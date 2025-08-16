from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging
from typing import List, Dict, Tuple
from ..services.style_analysis_service import style_analyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/style-analysis", tags=["Style Analysis"])

@router.post("/analyze")
async def analyze_style(file: UploadFile = File(...)):
    """
    Analyze a clothing item image and return ranked style matches using CLIP embeddings
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Analyze style
        style_matches = style_analyzer.analyze_style(image)
        
        return {
            "success": True,
            "style_matches": style_matches,
            "top_match": style_matches[0] if style_matches else None
        }
        
    except Exception as e:
        logger.error(f"Error in style analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")

@router.post("/top-styles")
async def get_top_styles(file: UploadFile = File(...), top_k: int = 5):
    """
    Get top-k style matches for a clothing item image
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate top_k parameter
        if top_k < 1 or top_k > 20:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get top styles
        top_styles = style_analyzer.get_top_styles(image, top_k)
        
        return {
            "success": True,
            "top_styles": top_styles,
            "top_k": top_k
        }
        
    except Exception as e:
        logger.error(f"Error getting top styles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get top styles: {str(e)}")

@router.post("/style-confidence")
async def get_style_confidence(file: UploadFile = File(...), style_name: str = None):
    """
    Get confidence score for a specific style
    """
    try:
        if not style_name:
            raise HTTPException(status_code=400, detail="style_name parameter is required")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get style confidence
        confidence = style_analyzer.get_style_confidence(image, style_name)
        
        return {
            "success": True,
            "style_name": style_name,
            "confidence": confidence
        }
        
    except Exception as e:
        logger.error(f"Error getting style confidence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get style confidence: {str(e)}")

@router.post("/style-breakdown")
async def get_style_breakdown(file: UploadFile = File(...)):
    """
    Get confidence scores for all supported styles
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get style breakdown
        breakdown = style_analyzer.get_style_breakdown(image)
        
        # Sort by confidence (highest first)
        sorted_breakdown = dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "success": True,
            "style_breakdown": sorted_breakdown,
            "top_style": list(sorted_breakdown.keys())[0] if sorted_breakdown else None
        }
        
    except Exception as e:
        logger.error(f"Error getting style breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get style breakdown: {str(e)}")

@router.get("/supported-styles")
async def get_supported_styles():
    """
    Get list of all supported style types
    """
    try:
        supported_styles = list(style_analyzer.style_prompts.keys())
        return {
            "success": True,
            "supported_styles": supported_styles,
            "count": len(supported_styles)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported styles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported styles: {str(e)}") 