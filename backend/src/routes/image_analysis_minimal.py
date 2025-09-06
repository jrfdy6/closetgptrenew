from fastapi import APIRouter, HTTPException, Depends
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Import auth dependency
try:
    from src.services.auth_service import get_current_user_id
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logger.warning("Auth service not available, analysis will be anonymous")

@router.post("/analyze-image")
async def analyze_image(
    image: dict,
    user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """Minimal image analysis with lazy imports"""
    try:
        print(f"🔍 Starting image analysis for user: {user_id}")
        
        # Get image URL from request
        image_url = image.get("url")
        if not image_url:
            print("❌ No image URL provided")
            raise HTTPException(status_code=400, detail="Image URL is required")
        
        print(f"🔍 Image URL: {image_url[:100]}...")
        
        # Lazy import heavy dependencies
        try:
            print("🔍 Importing OpenAI...")
            from openai import OpenAI
            print("✅ OpenAI imported successfully")
        except ImportError as e:
            print(f"❌ OpenAI import failed: {e}")
            raise HTTPException(status_code=503, detail="AI analysis service not available")
        
        try:
            print("🔍 Importing requests...")
            import requests
            print("✅ Requests imported successfully")
        except ImportError as e:
            print(f"❌ Requests import failed: {e}")
            raise HTTPException(status_code=503, detail="Image download service not available")
        
        # Download image
        try:
            print("🔍 Downloading image...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            print(f"✅ Downloaded image, size: {len(response.content)} bytes")
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Simple analysis (just return basic info for now)
            print("🔍 Performing basic analysis...")
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            
            # Basic analysis result
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
                "confidence": 0.5,
                "fileSize": file_size,
                "imageUrl": image_url
            }
            
            print("✅ Analysis completed successfully")
            return {"analysis": analysis}
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
                print("✅ Cleaned up temporary file")
            except Exception as e:
                print(f"⚠️ Failed to clean up temp file: {e}")
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in analyze_image: {e}")
        logger.error(f"❌ Unexpected error in analyze_image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze image")
