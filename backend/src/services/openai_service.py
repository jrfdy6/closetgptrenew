import os
import base64
import json
import logging
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

async def analyze_image_with_gpt4(image_path: str) -> dict:
    """Analyze an image using GPT-4 Vision API with structured JSON output."""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Read the image file and convert to base64
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            base64_image = f"data:image/jpeg;base64,{image_data}"
        
        # Define the JSON schema for structured response with mood and canonical fields
        json_schema = {
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
                            "rgb": {"type": "array", "items": {"type": "integer"}}
                        },
                        "required": ["name", "hex", "rgb"]
                    }
                },
                "matchingColors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "hex": {"type": "string"},
                            "rgb": {"type": "array", "items": {"type": "integer"}}
                        },
                        "required": ["name", "hex", "rgb"]
                    }
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
                        "mood": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "confidence": {
                    "type": "object",
                    "properties": {
                        "style": {"type": "number", "minimum": 0, "maximum": 1},
                        "occasion": {"type": "number", "minimum": 0, "maximum": 1},
                        "mood": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "bodyTypeCompatibility": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["Rectangle", "Hourglass", "Triangle", "Inverted Triangle", "Apple", "Oval"]}
                },
                "weatherCompatibility": {
                    "type": "array", 
                    "items": {"type": "string"}
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
                                "formalLevel": {"type": "string", "enum": ["Casual", "Smart Casual", "Business Casual", "Semi-Formal", "Formal"]},
                                "genderTarget": {"type": "string", "enum": ["Men", "Women", "Unisex"]},
                                "backgroundRemoved": {"type": "boolean"},
                                "hangerPresent": {"type": "boolean"},
                                "waistbandType": {"type": "string", "enum": ["belt_loops", "elastic", "drawstring", "elastic_drawstring", "button_zip", "none"]}
                            },
                            "required": ["wearLayer", "sleeveLength", "material", "pattern", "fit", "formalLevel"]
                        },
                        "naturalDescription": {"type": "string"}
                    }
                }
            },
            "required": ["type", "subType", "dominantColors", "style", "occasion", "mood", "season", "metadata"]
        }

        # Call OpenAI API for image analysis with structured output
        try:
            logger.info("Calling OpenAI API with image analysis request...")
            logger.info(f"Image size: {len(base64_image)} characters")
            logger.info(f"API Key present: {bool(os.getenv('OPENAI_API_KEY'))}")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_schema", "json_schema": {"name": "clothing_analysis", "schema": json_schema}},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional fashion metadata extractor. Analyze clothing items in images and provide detailed, accurate information. IMPORTANT: Only analyze images that contain clothing items. If the image does not contain a clear clothing item, set type to 'other' and provide what you can detect. Be specific and detailed in your analysis. Always respond with valid JSON matching the provided schema."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_image}
                            },
                            {
                                "type": "text",
                                "text": """Analyze the clothing image and return comprehensive JSON with ALL visualAttributes fields.

CRITICAL FIELDS (Required for outfit compatibility):
- wearLayer: Classify as Base/Inner/Mid/Outer/Bottom/Footwear/Accessory
  * Base: Underwear, undershirts
  * Inner: T-shirts, basic tops worn as first layer
  * Mid: Shirts, sweaters that can layer
  * Outer: Jackets, coats, cardigans
  * Bottom: Pants, shorts, skirts
  * Footwear: Shoes, boots, sandals
  * Accessory: Belts, scarves, hats

- sleeveLength: Sleeveless/Short/3\/4/Long/None (critical for layering compatibility!)

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
                            }
                        ]
                    }
                ],
                max_tokens=3000,  # Increased for comprehensive metadata
                temperature=0.1
            )
            logger.info("OpenAI API call completed successfully")
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {str(api_error)}")
            logger.error(f"API Error type: {type(api_error).__name__}")
            raise ValueError(f"OpenAI API call failed: {str(api_error)}")
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Log the raw response for debugging
        logger.info(f"Raw GPT-4 Vision response: {content}")
        # print(f"🔍 Raw GPT-4 Vision response: {content}")
        
        # Parse the JSON response
        try:
            analysis = json.loads(content)
            logger.info(f"Parsed analysis: {analysis}")
            # print(f"✅ Parsed analysis: {analysis}")
            
            # Generate a descriptive name for the item
            name_parts = []
            
            # Handle clothing type - be more flexible with "object" or "other"
            clothing_type = (analysis.get("type", "") if analysis else "")
            if clothing_type and clothing_type not in ["other", "object", "unknown"]:
                name_parts.append(clothing_type.title())
            elif clothing_type == "object":
                # If GPT-4 returns "object", try to infer from other fields
                if analysis.get("subType"):
                    name_parts.append(analysis["subType"].title())
                else:
                    name_parts.append("Clothing Item")
            
            # Add subtype if available
            if analysis.get("subType") and analysis["subType"] not in ["unknown", "null"]:
                name_parts.append(analysis["subType"])
            
            # Add dominant color if available
            if analysis.get("dominantColors") and len(analysis["dominantColors"]) > 0:
                color = analysis["dominantColors"][0].get("name", "")
                if color and color not in ["unknown", "null"]:
                    name_parts.append(color.title())
            
            # Add brand if available
            if analysis.get("brand") and analysis["brand"] not in ["unknown", "null"]:
                name_parts.append(f"by {analysis['brand']}")
            
            # Fallback name generation
            if not name_parts:
                # Try to use style or occasion information
                if analysis.get("style") and len(analysis["style"]) > 0:
                    name_parts.append(analysis["style"][0].title())
                elif analysis.get("occasion") and len(analysis["occasion"]) > 0:
                    name_parts.append(analysis["occasion"][0].title())
                else:
                    name_parts.append("Clothing Item")
            
            analysis["name"] = " ".join(name_parts)
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Raw content: {content}")
            raise ValueError("Failed to parse analysis response")
            
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise ValueError(f"Failed to analyze image: {str(e)}")