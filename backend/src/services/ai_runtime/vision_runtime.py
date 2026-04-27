from __future__ import annotations

import base64
import json
import logging
import mimetypes
from pathlib import Path

from .runtime_config import build_openai_client, get_openai_vision_model

logger = logging.getLogger(__name__)

VISION_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["shirt", "pants", "shorts", "dress", "skirt", "jacket", "sweater", "shoes", "accessory", "other"]},
        "subType": {"type": "string"},
        "dominantColors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "hex": {"type": "string"},
                    "rgb": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["name", "hex", "rgb"],
            },
        },
        "matchingColors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "hex": {"type": "string"},
                    "rgb": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["name", "hex", "rgb"],
            },
        },
        "style": {"type": "array", "items": {"type": "string"}},
        "occasion": {"type": "array", "items": {"type": "string"}},
        "mood": {"type": "array", "items": {"type": "string"}},
        "season": {"type": "array", "items": {"type": "string", "enum": ["spring", "summer", "fall", "winter"]}},
        "brand": {"type": "string"},
        "name": {"type": "string"},
        "canonical": {
            "type": "object",
            "properties": {
                "style": {"type": "array", "items": {"type": "string"}},
                "occasion": {"type": "array", "items": {"type": "string"}},
                "mood": {"type": "array", "items": {"type": "string"}},
            },
        },
        "confidence": {
            "type": "object",
            "properties": {
                "style": {"type": "number", "minimum": 0, "maximum": 1},
                "occasion": {"type": "number", "minimum": 0, "maximum": 1},
                "mood": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
        "bodyTypeCompatibility": {
            "type": "array",
            "items": {"type": "string", "enum": ["Rectangle", "Hourglass", "Triangle", "Inverted Triangle", "Apple", "Oval"]},
        },
        "weatherCompatibility": {
            "type": "array",
            "items": {"type": "string"},
        },
        "gender": {"type": "string", "enum": ["male", "female", "unisex"]},
        "backgroundRemoved": {"type": "boolean"},
        "metadata": {
            "type": "object",
            "properties": {
                "visualAttributes": {
                    "type": "object",
                    "properties": {
                        "wearLayer": {"type": "string", "enum": ["Base", "Inner", "Mid", "Outer", "Bottom", "Footwear", "Accessory"]},
                        "sleeveLength": {"type": "string", "enum": ["Sleeveless", "Short", "3/4", "Long", "None"]},
                        "material": {"type": "string"},
                        "pattern": {"type": "string"},
                        "textureStyle": {"type": "string"},
                        "fabricWeight": {"type": "string", "enum": ["Light", "Medium", "Heavy"]},
                        "fit": {"type": "string", "enum": ["fitted", "slim", "regular", "relaxed", "loose", "oversized"]},
                        "silhouette": {"type": "string"},
                        "length": {"type": "string"},
                        "neckline": {"type": "string"},
                        "transparency": {"type": "string", "enum": ["opaque", "semi-sheer", "sheer", "textured-opaque"]},
                        "collarType": {"type": "string"},
                        "embellishments": {"type": "string", "enum": ["none", "minimal", "moderate", "heavy"]},
                        "printSpecificity": {"type": "string"},
                        "formalLevel": {"type": "string", "enum": ["Casual", "Smart Casual", "Business Casual", "Semi-Formal", "Formal"]},
                        "genderTarget": {"type": "string", "enum": ["Men", "Women", "Unisex"]},
                        "backgroundRemoved": {"type": "boolean"},
                        "hangerPresent": {"type": "boolean"},
                        "waistbandType": {"type": "string", "enum": ["belt_loops", "elastic", "drawstring", "elastic_drawstring", "button_zip", "none"]},
                        "rise": {"type": "string"},
                        "legOpening": {"type": "string"},
                        "heelHeight": {"type": "string"},
                        "statementLevel": {"type": "integer", "minimum": 0, "maximum": 10},
                    },
                    "required": ["wearLayer", "sleeveLength", "material", "pattern", "fit", "formalLevel", "neckline", "transparency", "embellishments", "printSpecificity"],
                },
                "naturalDescription": {"type": "string"},
            },
        },
    },
    "required": ["type", "subType", "dominantColors", "style", "occasion", "mood", "season", "metadata"],
}

SYSTEM_PROMPT = (
    "You are a professional fashion metadata extractor. Analyze clothing items in images and provide "
    "detailed, accurate information. IMPORTANT: Only analyze images that contain clothing items. "
    "If the image does not contain a clear clothing item, set type to 'other' and provide what you can detect. "
    "Be specific and detailed in your analysis. Always respond with valid JSON matching the provided schema."
)

USER_PROMPT = """Analyze the clothing image and return comprehensive JSON with ALL visualAttributes fields.

CRITICAL FIELDS (Required for outfit compatibility):
- wearLayer: Classify as Base/Inner/Mid/Outer/Bottom/Footwear/Accessory
  * Base: Underwear, undershirts
  * Inner: T-shirts, basic tops worn as first layer
  * Mid: Shirts, sweaters that can layer
  * Outer: Jackets, coats, cardigans
  * Bottom: Pants, shorts, skirts
  * Footwear: Shoes, boots, sandals
  * Accessory: Belts, scarves, hats

- sleeveLength: Sleeveless/Short/3/4/Long/None (critical for layering compatibility!)

- fit: fitted/slim/regular/relaxed/loose/oversized

- formalLevel: Casual/Smart Casual/Business Casual/Semi-Formal/Formal

ADDITIONAL VISUALATTRIBUTES (Required):
- pattern: solid/striped/checkered/plaid/floral/geometric/textured/etc.
- textureStyle: smooth/ribbed/cable knit/textured/silky/rough/etc.
- fabricWeight: Light/Medium/Heavy
- silhouette: structured/flowy/boxy/fitted/etc.
- length: short/mid-length/long/cropped/etc.
- neckline: FOR TOPS ONLY - crew/v-neck/scoop/turtleneck/collar/henley/tank/halter/off-shoulder/cowl/boat/square/sweetheart/none (use 'none' for bottoms/shoes/accessories)
- transparency: opaque/semi-sheer/sheer/textured-opaque (affects layering needs and modesty)
- collarType: FOR SHIRTS/TOPS - button-down/spread/point/band/mandarin/camp/shawl/peter-pan/none (more specific than neckline)
- embellishments: none/minimal/moderate/heavy (sequins, beading, graphics, patches, etc.)
- printSpecificity: none/logo/text/graphic/abstract/geometric/floral/animal (more specific than pattern)
- genderTarget: Men/Women/Unisex
- material: cotton/wool/silk/polyester/denim/etc.
- backgroundRemoved: true/false (is background removed?)
- hangerPresent: true/false (is item on a hanger?)
- waistbandType: FOR PANTS/SHORTS ONLY - Analyze waistband closure type:
  * belt_loops: Traditional pants with belt loops (dress pants, jeans, chinos)
  * elastic: Full elastic waistband (sweatpants, some athletic wear)
  * drawstring: Drawstring closure (joggers, some shorts)
  * elastic_drawstring: Combination of elastic + drawstring (athletic pants, loungewear)
  * button_zip: Button/zipper only without belt loops (some formal pants)
  * none: Not applicable (for non-bottom items like tops, dresses, etc.)
- rise: FOR PANTS/SHORTS/SKIRTS - high-rise/mid-rise/low-rise/none (how high it sits on waist)
- legOpening: FOR PANTS ONLY - straight/tapered/wide/flared/bootcut/skinny/none (leg shape at ankle)
- heelHeight: FOR SHOES ONLY - flat/low/mid/high/very-high/platform/none (heel measurement)
- statementLevel: Rate 0-10 how eye-catching the item is:
  * 0-2: Basic wardrobe staple (plain white tee, basic jeans)
  * 3-5: Moderate personality (patterned shirt, colored pants)
  * 6-8: Statement piece (bold print, unique design)
  * 9-10: Showstopper (sequins, dramatic silhouette)

ROOT-LEVEL FIELDS (Also required):
- bodyTypeCompatibility: Array of body types this flatters (Rectangle/Hourglass/Triangle/Inverted Triangle/Apple/Oval)
- weatherCompatibility: Array of weather conditions (Hot/Warm/Cool/Cold/Summer/Fall/Winter/Spring)
- gender: male/female/unisex
- backgroundRemoved: true/false (detect if background is removed in image)

ALSO INCLUDE:
- naturalDescription: 1-2 sentence description with styling notes (e.g., "A loose, short-sleeve sweater. Should not be worn under long-sleeve shirts.")
- type, subType, dominantColors (with hex codes!), matchingColors (with hex codes!), style[], occasion[], mood[], season[], brand

EXAMPLE OUTPUT:
{
  "type": "sweater",
  "subType": "cardigan",
  "dominantColors": [{"name": "Beige", "hex": "#D9C8A9", "rgb": [217, 200, 169]}],
  "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
  "style": ["Casual", "Preppy"],
  "occasion": ["Beach", "Casual", "Brunch"],
  "mood": ["Relaxed"],
  "season": ["fall", "winter"],
  "brand": "Abercrombie & Fitch",
  "bodyTypeCompatibility": ["Rectangle", "Apple"],
  "weatherCompatibility": ["Hot", "Warm", "Fall", "Winter"],
  "gender": "male",
  "backgroundRemoved": false,
  "metadata": {
    "visualAttributes": {
      "wearLayer": "Outer",
      "sleeveLength": "Short",
      "material": "Cotton",
      "pattern": "textured",
      "textureStyle": "ribbed",
      "fabricWeight": "Medium",
      "fit": "loose",
      "silhouette": "Boxy",
      "length": "Mid-length",
      "neckline": "crew",
      "transparency": "opaque",
      "collarType": "none",
      "embellishments": "minimal",
      "printSpecificity": "none",
      "formalLevel": "Casual",
      "genderTarget": "Unisex",
      "backgroundRemoved": false,
      "hangerPresent": true,
      "waistbandType": "none",
      "rise": "none",
      "legOpening": "none",
      "heelHeight": "none",
      "statementLevel": 4
    },
    "naturalDescription": "A loose, short-sleeve, ribbed sweater. This is an outer layer item that should not be worn under long-sleeve shirts."
  }
}

Return comprehensive, complete JSON with ALL fields for professional wardrobe management!"""


def _build_data_uri(image_bytes: bytes, *, image_path: str | None = None) -> str:
    mime_type = mimetypes.guess_type(image_path or "")[0] or "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _generate_item_name(analysis: dict) -> str:
    name_parts: list[str] = []
    clothing_type = analysis.get("type", "")
    if clothing_type and clothing_type not in {"other", "object", "unknown"}:
        name_parts.append(str(clothing_type).title())
    elif clothing_type == "object":
        if analysis.get("subType"):
            name_parts.append(str(analysis["subType"]).title())
        else:
            name_parts.append("Clothing Item")

    if analysis.get("subType") and analysis["subType"] not in {"unknown", "null"}:
        name_parts.append(str(analysis["subType"]))

    dominant_colors = analysis.get("dominantColors") or []
    if dominant_colors:
        first_color = dominant_colors[0]
        if isinstance(first_color, dict):
            color_name = first_color.get("name", "")
            if color_name and color_name not in {"unknown", "null"}:
                name_parts.append(str(color_name).title())

    brand = analysis.get("brand")
    if brand and brand not in {"unknown", "null"}:
        name_parts.append(f"by {brand}")

    if not name_parts:
        styles = analysis.get("style") or []
        occasions = analysis.get("occasion") or []
        if styles:
            name_parts.append(str(styles[0]).title())
        elif occasions:
            name_parts.append(str(occasions[0]).title())
        else:
            name_parts.append("Clothing Item")

    return " ".join(name_parts)


def _parse_analysis_content(content: str) -> dict:
    try:
        analysis = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Failed to parse analysis response") from exc
    analysis["name"] = _generate_item_name(analysis)
    return analysis


def _run_vision_request(image_reference: str) -> dict:
    client = build_openai_client()
    logger.info("Calling OpenAI vision runtime")
    response = client.chat.completions.create(
        model=get_openai_vision_model(),
        response_format={"type": "json_schema", "json_schema": {"name": "clothing_analysis", "schema": VISION_SCHEMA}},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_reference}},
                    {"type": "text", "text": USER_PROMPT},
                ],
            },
        ],
        max_tokens=3000,
        temperature=0.1,
    )
    content = response.choices[0].message.content
    logger.info(f"Raw vision runtime response: {content}")
    return _parse_analysis_content(content)


async def analyze_image_path_with_openai_vision(image_path: str) -> dict:
    try:
        image_bytes = Path(image_path).read_bytes()
        return _run_vision_request(_build_data_uri(image_bytes, image_path=image_path))
    except Exception as exc:
        logger.error(f"Error analyzing image path with vision runtime: {exc}")
        raise ValueError(f"Failed to analyze image: {exc}") from exc


async def analyze_image_url_with_openai_vision(image_url: str) -> dict:
    try:
        return _run_vision_request(image_url)
    except Exception as exc:
        logger.error(f"Error analyzing image URL with vision runtime: {exc}")
        raise ValueError(f"Failed to analyze image: {exc}") from exc
