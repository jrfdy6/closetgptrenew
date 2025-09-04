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
        
        # Define the JSON schema for structured response
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
                "brand": {"type": "string"},
                "season": {"type": "array", "items": {"type": "string", "enum": ["spring", "summer", "fall", "winter"]}},
                "occasion": {"type": "array", "items": {"type": "string"}},
                "name": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "visualAttributes": {
                            "type": "object",
                            "properties": {
                                "material": {"type": "string"},
                                "pattern": {"type": "string"},
                                "textureStyle": {"type": "string"},
                                "fabricWeight": {"type": "string"},
                                "fit": {"type": "string"},
                                "silhouette": {"type": "string"},
                                "length": {"type": "string"},
                                "genderTarget": {"type": "string"},
                                "sleeveLength": {"type": "string"},
                                "formalLevel": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "required": ["type", "subType", "dominantColors", "matchingColors", "style", "season", "occasion", "name", "metadata"]
        }

        # Call OpenAI API for image analysis with structured output
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_schema", "json_schema": {"name": "clothing_analysis", "schema": json_schema}},
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional fashion metadata extractor. Analyze clothing items in images and provide detailed, accurate information. Be specific and detailed in your analysis. Always respond with valid JSON matching the provided schema."
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
                            "text": """Analyze this clothing item image and provide detailed metadata. Be specific about:
- The exact type and subtype of clothing
- Accurate color analysis with proper hex codes
- Detailed style characteristics (not just "casual")
- Appropriate seasons and occasions
- Material, pattern, fit, and other visual attributes
- Brand if visible

Provide comprehensive, detailed analysis that would be useful for wardrobe management and outfit planning."""
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Log the raw response for debugging
        logger.info(f"Raw GPT-4 Vision response: {content}")
        print(f"🔍 Raw GPT-4 Vision response: {content}")
        
        # Parse the JSON response
        try:
            analysis = json.loads(content)
            logger.info(f"Parsed analysis: {analysis}")
            print(f"✅ Parsed analysis: {analysis}")
            
            # Generate a descriptive name for the item
            name_parts = []
            if analysis.get("type") and analysis["type"] != "other":
                name_parts.append(analysis["type"].title())
            if analysis.get("subType") and analysis["subType"]:
                name_parts.append(analysis["subType"])
            if analysis.get("dominantColors") and len(analysis["dominantColors"]) > 0:
                name_parts.append(analysis["dominantColors"][0]["name"])
            if analysis.get("brand") and analysis["brand"]:
                name_parts.append(f"by {analysis['brand']}")
            
            analysis["name"] = " ".join(name_parts) if name_parts else "Unnamed Item"
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Raw content: {content}")
            raise ValueError("Failed to parse analysis response")
            
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise ValueError(f"Failed to analyze image: {str(e)}")