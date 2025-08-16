from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image
import pillow_heif
import tempfile
import mimetypes
import base64
import json
from typing import List
from datetime import datetime

from ..services.openai_service import analyze_image_with_gpt4
from ..services.simple_image_analysis_service import simple_analyzer
from ..utils.image_processing import process_image_for_analysis
from ..core.logging import get_logger
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event
from ..routes.auth import get_current_user_id

# Set up logging
logger = get_logger("image_analysis")

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api", tags=["image-analysis"])

class ImageAnalysisRequest(BaseModel):
    image: dict[str, str]

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
                    logger.warning(f"Failed to convert HEIC: {str(e)}")
                    # Fallback: save as is
                    temp_file.write(response.content)
            else:
                # For other formats, try to convert to JPEG
                try:
                    image = Image.open(BytesIO(response.content))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(temp_file.name, "JPEG")
                except Exception as e:
                    logger.warning(f"Failed to convert image: {str(e)}")
                    # Fallback: save as is
                    temp_file.write(response.content)
            
            return temp_file.name
            
    except Exception as e:
        logger.error(f"Error converting image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id)
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

        # Process the image for analysis
        processed_image = process_image_for_analysis(temp_file_path)
        
        # Use enhanced analysis (GPT-4 + CLIP)
        logger.info("Starting enhanced analysis with GPT-4 Vision and CLIP")
        analysis = await simple_analyzer.analyze_clothing_item(processed_image)
        
        # Log analytics event
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
        
        logger.error(f"Enhanced analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image")
async def analyze_single_image(
    image: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Enhanced single image analysis using GPT-4 Vision + CLIP
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
            # Use enhanced analysis (GPT-4 + CLIP)
            analysis = await simple_analyzer.analyze_clothing_item(temp_path)
            
            # Log analytics event
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                event_type="single_image_analyzed",
                metadata={
                    "analysis_type": "enhanced",
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
                "analysis_type": "enhanced",
                "error": str(e),
                "error_type": type(e).__name__,
                "image_url": image.get("url", "") if 'image' in locals() else ""
            }
        )
        log_analytics_event(analytics_event)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image-legacy")
async def analyze_single_image_legacy(
    image: dict,
    current_user_id: str = Depends(get_current_user_id)
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
    current_user_id: str = Depends(get_current_user_id)
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
    current_user_id: str = Depends(get_current_user_id)
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
    current_user_id: str = Depends(get_current_user_id)
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