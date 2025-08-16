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
    """Analyze an image using GPT-4 Vision API."""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Read the image file and convert to base64
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            base64_image = f"data:image/jpeg;base64,{image_data}"
        
        # Call OpenAI API for image analysis
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this clothing item and provide the following information in JSON format:
{
    "type": "One of: shirt, pants, shorts, dress, skirt, jacket, sweater, shoes, accessory, other",
    "subType": "More specific type (e.g., 't-shirt', 'jeans', 'denim shorts', 'sundress')",
    "dominantColors": [
        {
            "name": "Color name",
            "hex": "Hex color code",
            "rgb": [R, G, B]
        }
    ],
    "matchingColors": [
        {
            "name": "Color name",
            "hex": "Hex color code",
            "rgb": [R, G, B]
        }
    ],
    "style": ["Array of style tags like: Casual, Formal, Sporty, etc."],
    "brand": "Brand name if visible (optional)",
    "season": ["Array of applicable seasons: spring, summer, fall, winter"],
    "occasion": ["Array of occasions like: Casual, Formal, Business, etc."],
    "metadata": {
        "basicMetadata": {
            "width": "Image width in pixels",
            "height": "Image height in pixels",
            "orientation": "EXIF orientation tag",
            "dateTaken": "When the image was captured",
            "deviceModel": "Camera/device model",
            "gps": "Latitude & longitude if available",
            "flashUsed": "Whether flash was on"
        },
        "visualAttributes": {
            "material": "Cotton, denim, leather, etc.",
            "pattern": "Solid, striped, polka dots, etc.",
            "textureStyle": "Smooth, ribbed, fuzzy, etc.",
            "fabricWeight": "Light, medium, heavy",
            "fit": "Loose, slim, oversized",
            "silhouette": "A-line, boxy, tapered",
            "length": "Cropped, mid-length, maxi",
            "genderTarget": "Men's, women's, unisex",
            "sleeveLength": "Sleeveless, short, long",
            "hangerPresent": "Boolean indicating if hanger is visible",
            "backgroundRemoved": "Boolean indicating if background is removed",
            "wearLayer": "Inner, outer, base",
            "formalLevel": "Casual, semi-formal, formal",
            "temperatureCompatibility": {
                "minTemp": "Minimum temperature in Fahrenheit",
                "maxTemp": "Maximum temperature in Fahrenheit",
                "recommendedLayers": ["Array of recommended layer types"],
                "materialPreferences": ["Array of preferred materials for this temperature range"]
            },
            "materialCompatibility": {
                "compatibleMaterials": ["Array of materials that work well with this item"],
                "weatherAppropriate": {
                    "spring": ["Array of appropriate materials"],
                    "summer": ["Array of appropriate materials"],
                    "fall": ["Array of appropriate materials"],
                    "winter": ["Array of appropriate materials"]
                }
            },
            "bodyTypeCompatibility": {
                "hourglass": {
                    "recommendedFits": ["Array of recommended fits"],
                    "styleRecommendations": ["Array of style recommendations"]
                },
                "pear": {
                    "recommendedFits": ["Array of recommended fits"],
                    "styleRecommendations": ["Array of style recommendations"]
                },
                "apple": {
                    "recommendedFits": ["Array of recommended fits"],
                    "styleRecommendations": ["Array of style recommendations"]
                },
                "rectangle": {
                    "recommendedFits": ["Array of recommended fits"],
                    "styleRecommendations": ["Array of style recommendations"]
                },
                "inverted_triangle": {
                    "recommendedFits": ["Array of recommended fits"],
                    "styleRecommendations": ["Array of style recommendations"]
                }
            },
            "skinToneCompatibility": {
                "warm": {
                    "compatibleColors": ["Array of compatible colors"],
                    "recommendedColorPalette": ["Array of recommended colors"]
                },
                "cool": {
                    "compatibleColors": ["Array of compatible colors"],
                    "recommendedColorPalette": ["Array of recommended colors"]
                },
                "neutral": {
                    "compatibleColors": ["Array of compatible colors"],
                    "recommendedColorPalette": ["Array of recommended colors"]
                }
            }
        },
        "itemMetadata": {
            "priceEstimate": "Estimated price range",
            "careInstructions": "Wash cold, dry clean, etc.",
            "tags": ["Any additional user-defined metadata"],
            "outfitScoring": {
                "baseScore": "Base score for the item",
                "pieceCountScore": "Score based on piece count",
                "colorHarmonyScore": "Score for color harmony",
                "materialCompatibilityScore": "Score for material compatibility",
                "patternMixingScore": "Score for pattern mixing",
                "pairabilityScore": "Score for how well it pairs with other items",
                "formalityConsistencyScore": "Score for formality consistency",
                "totalScore": "Total outfit score"
            }
        }
    }
}

IMPORTANT RULES:
1. If the item is shorts (any length above the knee), set type to "shorts" and use an appropriate subType (e.g., "denim shorts", "athletic shorts", "bermuda shorts")
2. Do NOT classify shorts as "pants" with a subtype of "shorts"
3. All fields must be present in the response, even if empty
4. For example:
- dominantColors must be an array (can be empty)
- matchingColors must be an array (can be empty)
- style must be an array (can be empty)
- season must be an array (can be empty)
- occasion must be an array (can be empty)
- metadata fields should be null if information is not available
5. For temperature compatibility:
   - Freezing (<32°F): 3 layers (shirt, sweater, jacket)
   - Cold (32-50°F): 2 layers (shirt, sweater)
   - Chilly (50-65°F): 1 layer (shirt)
   - Mild (65-75°F): 1 layer (shirt)
   - Warm (75-85°F): 1 layer (shirt)
   - Hot (>85°F): 1 layer (shirt)
6. For material compatibility:
   - Consider weather-appropriate materials for each season
   - Include compatible material combinations
7. For body type compatibility:
   - Consider the item's fit and style for each body type
   - Provide specific recommendations for each body type
8. For skin tone compatibility:
   - Consider the item's colors and how they work with different skin tones
   - Provide specific color recommendations for each skin tone

Please ensure the response is valid JSON with all fields present.
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": { "url": base64_image }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        # Parse the response content
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code block if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Log the raw response for debugging
        logger.info(f"Raw API response: {content}")
        
        # Validate and parse the JSON
        try:
            # First try to parse the content directly
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Ensure all required fields are present
            required_fields = {
                "type": "other",
                "subType": "Unnamed Item",
                "dominantColors": [],
                "matchingColors": [],
                "style": [],
                "brand": "",
                "season": [],
                "occasion": [],
                "metadata": {
                    "basicMetadata": {},
                    "visualAttributes": {
                        "temperatureCompatibility": {
                            "minTemp": 32,
                            "maxTemp": 75,
                            "recommendedLayers": [],
                            "materialPreferences": []
                        },
                        "materialCompatibility": {
                            "compatibleMaterials": [],
                            "weatherAppropriate": {
                                "spring": [],
                                "summer": [],
                                "fall": [],
                                "winter": []
                            }
                        },
                        "bodyTypeCompatibility": {
                            "hourglass": {"recommendedFits": [], "styleRecommendations": []},
                            "pear": {"recommendedFits": [], "styleRecommendations": []},
                            "apple": {"recommendedFits": [], "styleRecommendations": []},
                            "rectangle": {"recommendedFits": [], "styleRecommendations": []},
                            "inverted_triangle": {"recommendedFits": [], "styleRecommendations": []}
                        },
                        "skinToneCompatibility": {
                            "warm": {"compatibleColors": [], "recommendedColorPalette": []},
                            "cool": {"compatibleColors": [], "recommendedColorPalette": []},
                            "neutral": {"compatibleColors": [], "recommendedColorPalette": []}
                        }
                    },
                    "itemMetadata": {
                        "tags": [],
                        "outfitScoring": {
                            "baseScore": 0,
                            "pieceCountScore": 0,
                            "colorHarmonyScore": 0,
                            "materialCompatibilityScore": 0,
                            "patternMixingScore": 0,
                            "pairabilityScore": 0,
                            "formalityConsistencyScore": 0,
                            "totalScore": 0
                        }
                    }
                }
            }
            
            # Merge the response with default values
            for key, default_value in required_fields.items():
                if key not in analysis:
                    analysis[key] = default_value
                elif isinstance(default_value, dict):
                    for subkey, subdefault in default_value.items():
                        if subkey not in analysis[key]:
                            analysis[key][subkey] = subdefault
                        elif isinstance(subdefault, dict):
                            for subsubkey, subsubdefault in subdefault.items():
                                if subsubkey not in analysis[key][subkey]:
                                    analysis[key][subkey][subsubkey] = subsubdefault
            
            # Generate a descriptive name for the item
            name_parts = []
            if analysis["type"] != "other":
                name_parts.append(analysis["type"].title())
            if analysis["subType"] and analysis["subType"] != "Unnamed Item":
                name_parts.append(analysis["subType"])
            if analysis["dominantColors"]:
                name_parts.append(analysis["dominantColors"][0]["name"])
            if analysis["brand"]:
                name_parts.append(f"by {analysis['brand']}")
            
            analysis["name"] = " ".join(name_parts) if name_parts else "Unnamed Item"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            logger.error(f"Raw content: {content}")
            raise ValueError("Failed to parse analysis response")
            
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise ValueError(f"Failed to analyze image: {str(e)}") 