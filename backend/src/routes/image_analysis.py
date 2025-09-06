from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image
try:
    import pillow_heif
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    print("⚠️ pillow_heif not available - HEIC image support disabled")
import tempfile
import mimetypes
import base64
import json
from typing import List, Optional
from datetime import datetime

# Debug imports with try/except blocks
try:
    from ..services.openai_service import analyze_image_with_gpt4
    print("✅ Successfully imported openai_service")
except Exception as e:
    print(f"❌ Failed import: openai_service - {e}")
    analyze_image_with_gpt4 = None

try:
    from ..services.simple_image_analysis_service import simple_analyzer
    print("✅ Successfully imported simple_image_analysis_service")
except Exception as e:
    print(f"❌ Failed import: simple_image_analysis_service - {e}")
    simple_analyzer = None

try:
    from ..utils.image_processing import process_image_for_analysis
    print("✅ Successfully imported utils.image_processing")
except Exception as e:
    print(f"❌ Failed import: utils.image_processing - {e}")
    process_image_for_analysis = None

try:
    from ..core.logging import get_logger
    print("✅ Successfully imported core.logging")
except Exception as e:
    print(f"❌ Failed import: core.logging - {e}")
    get_logger = None

try:
    from ..models.analytics_event import AnalyticsEvent
    print("✅ Successfully imported models.analytics_event")
except Exception as e:
    print(f"❌ Failed import: models.analytics_event - {e}")
    AnalyticsEvent = None

try:
    from ..services.analytics_service import log_analytics_event
    print("✅ Successfully imported services.analytics_service")
except Exception as e:
    print(f"❌ Failed import: services.analytics_service - {e}")
    log_analytics_event = None
# Import auth dependency
try:
    from src.auth.auth_service import get_current_user_id
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logger.warning("Auth service not available, analysis will be anonymous")

# Set up logging with fallback
if get_logger:
    logger = get_logger("image_analysis")
else:
    import logging
    logger = logging.getLogger("image_analysis")
    print("⚠️ Using fallback logging due to import failure")

# Load environment variables
load_dotenv()

router = APIRouter(tags=["image-analysis"])

class AnalyzeImagePayload(BaseModel):
    image_url: Optional[str] = None
    image: Optional[dict] = None

def convert_to_jpeg(image_url: str) -> str:
    """Convert image to JPEG format for analysis"""
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Check if it's a HEIC image
            if image_url.lower().endswith('.heic'):
                if HEIC_SUPPORT:
                    try:
                        heif_file = pillow_heif.read_heif(response.content)
                        image = Image.frombytes(
                            heif_file.mode,
                            heif_file.size,
                            heif_file.data,
                            "raw",
                        )
                        image.save(temp_file.name, "JPEG")
                    except Exception as e:
                        print(f"Failed to convert HEIC: {str(e)}")
                        # Fallback: save as is
                        temp_file.write(response.content)
                else:
                    print("HEIC image detected but pillow_heif not available - saving as is")
                    temp_file.write(response.content)
            else:
                # For other formats, try to convert to JPEG
                try:
                    image = Image.open(BytesIO(response.content))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(temp_file.name, "JPEG")
                except Exception as e:
                    print(f"Failed to convert image: {str(e)}")
                    # Fallback: save as is
                    temp_file.write(response.content)
            
            return temp_file.name
            
    except Exception as e:
        print(f"Error converting image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Enhanced image analysis using both GPT-4 Vision and CLIP style analysis
    """
    try:
        # Create a temporary file to store the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Convert HEIC to JPEG if necessary
        if file.filename.lower().endswith('.heic'):
            if HEIC_SUPPORT:
                try:
                    heif_file = pillow_heif.read_heif(temp_file_path)
                    image = Image.frombytes(
                        heif_file.mode,
                        heif_file.size,
                        heif_file.data,
                        "raw",
                    )
                    # Create a new temporary file for the JPEG
                    jpeg_path = temp_file_path.replace('.heic', '.jpg')
                    image.save(jpeg_path, "JPEG")
                    # Update the path to use the JPEG file
                    os.unlink(temp_file_path)
                    temp_file_path = jpeg_path
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Failed to convert HEIC image: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="HEIC images not supported - pillow_heif dependency missing")

        # Process the image for analysis
        if process_image_for_analysis:
            processed_image = process_image_for_analysis(temp_file_path)
        else:
            print("⚠️ process_image_for_analysis not available, using original image")
            processed_image = temp_file_path
        
        # Use enhanced analysis (GPT-4 + CLIP)
        print("Starting enhanced analysis with GPT-4 Vision and CLIP")
        if simple_analyzer:
            analysis = await simple_analyzer.analyze_clothing_item(processed_image)
        else:
            print("⚠️ simple_analyzer not available, using fallback analysis")
            analysis = {
                "name": "Analysis Failed - Service Unavailable",
                "type": "clothing",
                "subType": "unknown",
                "dominantColors": [{"name": "unknown", "hex": "#000000"}],
                "matchingColors": [{"name": "unknown", "hex": "#000000"}],
                "style": ["casual"],
                "season": ["all-season"],
                "occasion": ["everyday"],
                "metadata": {
                    "visualAttributes": {
                        "material": "unknown",
                        "pattern": "unknown",
                        "fit": "unknown",
                        "sleeveLength": "unknown"
                    }
                }
            }
        
        # Log analytics event
        if AnalyticsEvent and log_analytics_event:
            try:
                analytics_event = AnalyticsEvent(
                    user_id=current_user_id,
                    event_type="image_analyzed",
                    metadata={
                        "analysis_type": "enhanced",
                        "file_type": file.content_type,
                        "file_size": len(content),
                        "has_clothing_detected": bool(analysis.get("clothing_type")),
                        "confidence_score": analysis.get("confidence_score", 0)
                    }
                )
                log_analytics_event(analytics_event)
            except Exception as analytics_error:
                print(f"⚠️ Analytics logging failed: {analytics_error}")
        else:
            print("⚠️ Analytics not available, skipping event logging")
        
        # Clean up temporary files
        os.unlink(temp_file_path)
        if processed_image != temp_file_path:
            try:
                os.unlink(processed_image)
            except:
                pass
        
        return {"analysis": analysis}
    except Exception as e:
        # Clean up temporary files in case of error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        if 'processed_image' in locals() and processed_image != temp_file_path:
            try:
                os.unlink(processed_image)
            except:
                pass
        
        # Log error analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="image_analysis_error",
            metadata={
                "analysis_type": "enhanced",
                "error": str(e),
                "error_type": type(e).__name__,
                "file_type": file.content_type if 'file' in locals() else "unknown"
            }
        )
        log_analytics_event(analytics_event)
        
        print(f"Enhanced analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image")
async def analyze_single_image(
    payload: AnalyzeImagePayload,
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Enhanced single image analysis using GPT-4 Vision + CLIP
    """
    try:
        # Try to resolve image URL from different payload formats
        image_url = payload.image_url
        if not image_url and payload.image and "url" in payload.image:
            image_url = payload.image["url"]
        
        if not image_url:
            print("❌ No image URL provided in request")
            raise HTTPException(status_code=400, detail="Image URL is required")
        
        print(f"🔍 Processing image URL: {image_url[:100]}...")
        print(f"🔍 Image URL type: {'data URL' if image_url.startswith('data:') else 'regular URL'}")
        
        # Handle both data URLs and regular URLs
        if image_url.startswith('data:'):
            # Handle base64 data URL
            print("Processing base64 data URL")
            import base64
            
            # Extract the base64 data from the data URL
            header, data = image_url.split(',', 1)
            image_data = base64.b64decode(data)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
        else:
            # Handle regular URL (Firebase Storage, S3, etc.)
            print(f"Processing regular URL: {image_url}")
            try:
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                print(f"Successfully downloaded image from URL, size: {len(response.content)} bytes")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
            except Exception as download_error:
                print(f"Failed to download image from URL: {str(download_error)}")
                raise HTTPException(status_code=400, detail=f"Failed to download image: {str(download_error)}")
        
        try:
            # Use direct GPT-4 Vision analysis for better name generation
            print(f"🔍 Starting AI analysis for image at: {temp_path}")
            print(f"🔍 Image file exists: {os.path.exists(temp_path)}")
            print(f"🔍 Image file size: {os.path.getsize(temp_path)} bytes")
            
            try:
                if analyze_image_with_gpt4:
                    analysis = await analyze_image_with_gpt4(temp_path)
                    print(f"✅ AI analysis completed successfully")
                    print(f"🔍 Full analysis result: {analysis}")
                    print(f"🔍 Generated name: {analysis.get('name', 'No name')}")
                    print(f"🔍 Analysis type: {analysis.get('type', 'No type')}")
                    print(f"🔍 Analysis subType: {analysis.get('subType', 'No subType')}")
                else:
                    print("⚠️ analyze_image_with_gpt4 not available, using fallback")
                    raise Exception("GPT-4 service not available")
            except Exception as gpt_error:
                print(f"❌ GPT-4 analysis failed: {gpt_error}")
                print(f"❌ GPT-4 error type: {type(gpt_error).__name__}")
                import traceback
                print(f"❌ GPT-4 traceback: {traceback.format_exc()}")
                
                # Fallback to basic analysis
                analysis = {
                    "name": "Analysis Failed",
                    "type": "clothing",
                    "subType": "unknown",
                    "dominantColors": [{"name": "unknown", "hex": "#000000"}],
                    "matchingColors": [{"name": "unknown", "hex": "#000000"}],
                    "style": ["casual"],
                    "season": ["all-season"],
                    "occasion": ["everyday"],
                    "metadata": {
                        "visualAttributes": {
                            "material": "unknown",
                            "pattern": "unknown",
                            "fit": "unknown",
                            "sleeveLength": "unknown"
                        }
                    },
                    "error": str(gpt_error)
                }
                print(f"🔍 Using fallback analysis: {analysis}")
            
            # Map AI analysis to wardrobe item schema
            normalized_analysis = {
                "name": analysis.get("name", "Unknown Item"),
                "type": analysis.get("type", "clothing"),
                "subType": analysis.get("subType", ""),
                "clothing_type": analysis.get("type", "clothing"),  # Map type to clothing_type
                "color": analysis.get("dominantColors", [{}])[0].get("name", "unknown") if analysis.get("dominantColors") else "unknown",
                "primary_color": analysis.get("dominantColors", [{}])[0].get("name", "unknown") if analysis.get("dominantColors") else "unknown",
                "dominantColors": analysis.get("dominantColors", []),
                "matchingColors": analysis.get("matchingColors", []),
                "style": analysis.get("style", []),
                "season": analysis.get("season", []),
                "occasion": analysis.get("occasion", []),
                "brand": analysis.get("brand", ""),
                "material": analysis.get("metadata", {}).get("visualAttributes", {}).get("material", "unknown"),
                "fit": analysis.get("metadata", {}).get("visualAttributes", {}).get("fit", "unknown"),
                "sleeveLength": analysis.get("metadata", {}).get("visualAttributes", {}).get("sleeveLength", "unknown"),
                "pattern": analysis.get("metadata", {}).get("visualAttributes", {}).get("pattern", "unknown"),
                "gender": analysis.get("metadata", {}).get("visualAttributes", {}).get("genderTarget", "unisex"),
                "formalLevel": analysis.get("metadata", {}).get("visualAttributes", {}).get("formalLevel", "casual")
            }
            
            print(f"🔍 Mapped analysis for wardrobe: {normalized_analysis}")
            
            # Log analytics event
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                event_type="single_image_analyzed",
                metadata={
                    "analysis_type": "gpt4_vision_direct",
                    "image_url": image_url,
                    "file_size": len(response.content),
                    "has_clothing_detected": bool(analysis.get("type")),
                    "confidence_score": 0.85
                }
            )
            log_analytics_event(analytics_event)
            
            return {"analysis": normalized_analysis}
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"❌ Error in analyze_single_image: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Log error analytics event (simplified)
        try:
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                event_type="single_image_analysis_error",
                metadata={
                    "analysis_type": "enhanced",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "image_url": image.get("url", "") if 'image' in locals() else ""
                }
            )
            log_analytics_event(analytics_event)
        except Exception as analytics_error:
            print(f"⚠️ Analytics logging failed: {analytics_error}")
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image-legacy")
async def analyze_single_image_legacy(
    image: dict,
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Legacy single image analysis using only GPT-4 Vision
    """
    try:
        image_url = image.get("url")
        if not image_url:
            raise HTTPException(status_code=400, detail="Image URL is required")
        
        # Download image to temporary file
        response = requests.get(image_url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Use legacy analysis (GPT-4 only)
            analysis = await analyze_image_with_gpt4(temp_path)
            
            # Log analytics event
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                event_type="single_image_analyzed",
                metadata={
                    "analysis_type": "legacy",
                    "image_url": image_url,
                    "file_size": len(response.content),
                    "has_clothing_detected": bool(analysis.get("clothing_type")),
                    "confidence_score": analysis.get("confidence_score", 0)
                }
            )
            log_analytics_event(analytics_event)
            
            return {"analysis": analysis}
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        # Log error analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="single_image_analysis_error",
            metadata={
                "analysis_type": "legacy",
                "error": str(e),
                "error_type": type(e).__name__,
                "image_url": image.get("url", "") if 'image' in locals() else ""
            }
        )
        log_analytics_event(analytics_event)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image-clip-only")
async def analyze_single_image_clip_only(
    image: dict,
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Simple image analysis using GPT-4 Vision only
    """
    try:
        image_url = image.get("url")
        if not image_url:
            raise HTTPException(status_code=400, detail="Image URL is required")
        
        # Download image to temporary file
        response = requests.get(image_url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Use simple analysis (GPT-4 Vision only)
            analysis = await simple_analyzer.analyze_clothing_item(temp_path)
            
            # Log analytics event
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                event_type="single_image_analyzed",
                metadata={
                    "analysis_type": "gpt4_vision_only",
                    "image_url": image_url,
                    "file_size": len(response.content),
                    "confidence_score": analysis.get("metadata", {}).get("confidence", 0)
                }
            )
            log_analytics_event(analytics_event)
            
            return {"analysis": analysis}
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        # Log error analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="single_image_analysis_error",
            metadata={
                "analysis_type": "gpt4_vision_only",
                "error": str(e),
                "error_type": type(e).__name__,
                "image_url": image.get("url", "") if 'image' in locals() else ""
            }
        )
        log_analytics_event(analytics_event)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-batch")
async def analyze_batch_images(
    images: List[dict],
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Enhanced batch image analysis using GPT-4 Vision + CLIP
    """
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        results = []
        successful_count = 0
        error_count = 0
        
        for i, image_data in enumerate(images):
            try:
                image_url = image_data.get("url")
                if not image_url:
                    continue
                
                # Download image to temporary file
                response = requests.get(image_url)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                try:
                    # Use enhanced analysis (GPT-4 + CLIP)
                    analysis = await simple_analyzer.analyze_clothing_item(temp_path)
                    results.append({
                        "index": i,
                        "url": image_url,
                        "analysis": analysis,
                        "status": "success"
                    })
                    successful_count += 1
                finally:
                    # Clean up temporary file
                    os.unlink(temp_path)
                    
            except Exception as e:
                results.append({
                    "index": i,
                    "url": image_data.get("url", ""),
                    "error": str(e),
                    "status": "error"
                })
                error_count += 1
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="batch_images_analyzed",
            metadata={
                "analysis_type": "enhanced",
                "total_images": len(images),
                "successful_count": successful_count,
                "error_count": error_count,
                "success_rate": successful_count / len(images) if images else 0
            }
        )
        log_analytics_event(analytics_event)
        
        return {
            "results": results,
            "summary": {
                "total": len(images),
                "successful": successful_count,
                "errors": error_count
            }
        }
        
    except Exception as e:
        # Log error analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="batch_image_analysis_error",
            metadata={
                "analysis_type": "enhanced",
                "error": str(e),
                "error_type": type(e).__name__,
                "total_images": len(images) if 'images' in locals() else 0
            }
        )
        log_analytics_event(analytics_event)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-batch-legacy")
async def analyze_batch_images_legacy(
    images: List[dict],
    current_user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """
    Legacy batch image analysis using only GPT-4 Vision
    """
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        results = []
        successful_count = 0
        error_count = 0
        
        for i, image_data in enumerate(images):
            try:
                image_url = image_data.get("url")
                if not image_url:
                    continue
                
                # Download image to temporary file
                response = requests.get(image_url)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                try:
                    # Use legacy analysis (GPT-4 only)
                    analysis = await analyze_image_with_gpt4(temp_path)
                    results.append({
                        "index": i,
                        "url": image_url,
                        "analysis": analysis,
                        "status": "success"
                    })
                    successful_count += 1
                finally:
                    # Clean up temporary file
                    os.unlink(temp_path)
                    
            except Exception as e:
                results.append({
                    "index": i,
                    "url": image_data.get("url", ""),
                    "error": str(e),
                    "status": "error"
                })
                error_count += 1
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="batch_images_analyzed",
            metadata={
                "analysis_type": "legacy",
                "total_images": len(images),
                "successful_count": successful_count,
                "error_count": error_count,
                "success_rate": successful_count / len(images) if images else 0
            }
        )
        log_analytics_event(analytics_event)
        
        return {
            "results": results,
            "summary": {
                "total": len(images),
                "successful": successful_count,
                "errors": error_count
            }
        }
        
    except Exception as e:
        # Log error analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="batch_image_analysis_error",
            metadata={
                "analysis_type": "legacy",
                "error": str(e),
                "error_type": type(e).__name__,
                "total_images": len(images) if 'images' in locals() else 0
            }
        )
        log_analytics_event(analytics_event)
        
        raise HTTPException(status_code=500, detail=str(e)) 