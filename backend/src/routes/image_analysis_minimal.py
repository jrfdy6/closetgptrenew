from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging
import tempfile
import os
import base64
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AnalyzeImagePayload(BaseModel):
    image_url: Optional[str] = None
    image: Optional[dict] = None

def normalize_analysis(analysis: dict) -> dict:
    """
    Normalize AI analysis results to match expected frontend fields
    """
    return {
        "name": analysis.get("name") or "Analyzed Item",
        "type": analysis.get("type") or "clothing",
        "clothing_type": analysis.get("type") or "clothing",  # For frontend compatibility
        "color": analysis.get("color") or "unknown",
        "primary_color": analysis.get("color") or "unknown",  # For frontend compatibility
        "style": analysis.get("style") or "casual",
        "occasion": analysis.get("occasion") or "everyday",
        "season": analysis.get("season") or "all-season",
        "material": analysis.get("material") or "unknown",
        "fit": analysis.get("fit") or "unknown",
        "sleeveLength": analysis.get("sleeveLength") or "unknown",
        "pattern": analysis.get("pattern") or "solid",
        "confidence": analysis.get("confidence", 0.5),
        "dominantColors": analysis.get("dominantColors", []),
        "matchingColors": analysis.get("matchingColors", []),
        "subType": analysis.get("subType") or "",
        "brand": analysis.get("brand") or "",
        "gender": analysis.get("gender") or "unisex"
    }

async def perform_clothing_analysis(image_path: str, image_url: str, file_size: int) -> Dict[str, Any]:
    """
    Perform real AI analysis using GPT-4 Vision
    """
    try:
        # Lazy import OpenAI
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        logger.info("Sending image to GPT-4 Vision for analysis...")
        
        # Create the analysis prompt
        prompt = """
        Analyze this clothing item image and provide detailed information in JSON format. 
        Focus on:
        - Clothing type (shirt, pants, dress, etc.)
        - Style (casual, formal, sporty, etc.)
        - Occasion (work, casual, party, etc.)
        - Season (spring, summer, fall, winter, all-season)
        - Dominant colors (extract 2-3 main colors with hex codes)
        - Material (cotton, polyester, wool, etc.)
        - Fit (loose, fitted, tight, etc.)
        - Sleeve length (long, short, sleeveless, etc.)
        - Pattern (solid, striped, floral, etc.)
        - Confidence level (0.0 to 1.0)
        
        Return ONLY valid JSON in this exact format:
        {
            "type": "string",
            "style": "string", 
            "occasion": "string",
            "season": "string",
            "dominantColors": [{"name": "string", "hex": "#hexcode"}],
            "matchingColors": [{"name": "string", "hex": "#hexcode"}],
            "material": "string",
            "fit": "string",
            "sleeveLength": "string",
            "pattern": "string",
            "confidence": 0.0
        }
        """
        
        # Call GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        # Extract the analysis result
        analysis_text = response.choices[0].message.content
        logger.info(f"GPT-4 Vision response: {analysis_text[:200]}...")
        
        # Parse JSON response
        import json
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse GPT-4 response as JSON: {e}")
            # Fallback to basic analysis
            analysis = {
                "type": "clothing",
                "style": "casual",
                "occasion": "everyday",
                "season": "all-season",
                "dominantColors": [{"name": "unknown", "hex": "#000000"}],
                "matchingColors": [{"name": "unknown", "hex": "#000000"}],
                "material": "unknown",
                "fit": "unknown",
                "sleeveLength": "unknown",
                "pattern": "unknown",
                "confidence": 0.5
            }
        
        # Add metadata
        analysis["fileSize"] = file_size
        analysis["imageUrl"] = image_url
        analysis["analysisMethod"] = "gpt4-vision"
        
        logger.info(f"AI analysis completed: {analysis.get('type', 'unknown')} - {analysis.get('style', 'unknown')}")
        return analysis
        
    except Exception as e:
        logger.error(f"AI analysis failed: {e}", exc_info=True)
        # Return fallback analysis
        return {
            "type": "clothing",
            "style": "casual",
            "occasion": "everyday",
            "season": "all-season",
            "dominantColors": [{"name": "unknown", "hex": "#000000"}],
            "matchingColors": [{"name": "unknown", "hex": "#000000"}],
            "material": "unknown",
            "fit": "unknown",
            "sleeveLength": "unknown",
            "pattern": "unknown",
            "confidence": 0.1,
            "fileSize": file_size,
            "imageUrl": image_url,
            "analysisMethod": "fallback",
            "error": str(e)
        }

router = APIRouter()

# Import auth dependency
try:
    from src.auth.auth_service import get_current_user_id
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logger.warning("Auth service not available, analysis will be anonymous")

@router.post("/analyze-image")
async def analyze_image(
    payload: AnalyzeImagePayload,
    user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """Minimal image analysis with lazy imports"""
    try:
        logger.info(f"Starting image analysis for user: {user_id}")
        
        # Try to resolve image URL from different payload formats
        image_url = payload.image_url
        
        if not image_url and payload.image and "url" in payload.image:
            image_url = payload.image["url"]
        
        if not image_url:
            logger.error("❌ No image URL provided in request")
            raise HTTPException(status_code=400, detail="No image URL provided")
        
        logger.info(f"✅ Received image for analysis: {image_url} (user: {user_id})")
        
        logger.info(f"Image URL: {image_url[:100]}...")
        
        # Lazy import heavy dependencies
        try:
            logger.info("Importing OpenAI...")
            from openai import OpenAI
            logger.info("OpenAI imported successfully")
        except ImportError as e:
            logger.error(f"OpenAI import failed: {e}")
            raise HTTPException(status_code=503, detail="AI analysis service not available")
        
        try:
            logger.info("Importing requests...")
            import requests
            logger.info("Requests imported successfully")
        except ImportError as e:
            logger.error(f"Requests import failed: {e}")
            raise HTTPException(status_code=503, detail="Image download service not available")
        
        # Download image
        try:
            logger.info("Downloading image...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            logger.info(f"Downloaded image, size: {len(response.content)} bytes")
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Real AI analysis using GPT-4 Vision
            logger.info("Performing GPT-4 Vision analysis...")
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            
            # Perform real AI analysis
            analysis = await perform_clothing_analysis(temp_path, image_url, file_size)
            
            # Normalize analysis results for frontend compatibility
            normalized_analysis = normalize_analysis(analysis)
            
            logger.info("GPT-4 Vision analysis completed successfully")
            return {"analysis": normalized_analysis}
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
                logger.info("Cleaned up temporary file")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze image")
