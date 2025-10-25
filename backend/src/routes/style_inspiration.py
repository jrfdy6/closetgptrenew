"""
Style Inspiration API Routes
Provides personalized style recommendations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from ..services.style_inspiration_service import StyleInspirationService
from ..auth.auth_service import get_current_user_id
from ..config.firebase import db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["style-inspiration"])

# Initialize service
inspiration_service = StyleInspirationService()


class WeatherContext(BaseModel):
    """Weather context for recommendations"""
    temp_c: Optional[float] = None
    temperature: Optional[float] = None  # Alternative field name
    precip_mm: Optional[float] = 0.0
    precipitation: Optional[float] = 0.0  # Alternative field name
    wind_kph: Optional[float] = 0.0
    condition: Optional[str] = None


class InspirationRequest(BaseModel):
    """Request for style inspiration"""
    weather: Optional[WeatherContext] = None
    excluded_ids: Optional[List[str]] = None


@router.post("/get-inspiration")
async def get_style_inspiration(
    request: InspirationRequest = None,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get a single personalized style inspiration item
    
    Reads user's style profile and returns one recommended item
    based on their preferences and optional weather context.
    """
    try:
        # Fetch user profile from Firestore
        user_doc = db.collection('users').document(current_user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=404,
                detail="User profile not found. Please complete your profile first."
            )
        
        user_profile = user_doc.to_dict()
        
        # Prepare weather context
        weather = None
        if request and request.weather:
            weather = {
                'temp_c': request.weather.temp_c or request.weather.temperature,
                'precip_mm': request.weather.precip_mm or request.weather.precipitation,
                'wind_kph': request.weather.wind_kph or 0.0,
                'condition': request.weather.condition
            }
        
        # Get excluded IDs (items already shown)
        excluded_ids = request.excluded_ids if request else []
        
        # Get inspiration
        inspiration = inspiration_service.get_inspiration(
            user_profile=user_profile,
            weather=weather,
            excluded_ids=excluded_ids
        )
        
        if not inspiration:
            return {
                "success": False,
                "message": "No inspiration items available at this time",
                "inspiration": None
            }
        
        logger.info(f"✅ Generated inspiration for user {current_user_id}: {inspiration['title']}")
        
        return {
            "success": True,
            "message": "Inspiration generated successfully",
            "inspiration": inspiration
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating inspiration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate style inspiration: {str(e)}"
        )


@router.get("/catalog-stats")
async def get_catalog_stats() -> Dict[str, Any]:
    """Get statistics about the inspiration catalog (for debugging)"""
    try:
        catalog = inspiration_service.catalog
        
        # Gather stats
        total_items = len(catalog)
        categories = set()
        brands = set()
        price_range = [float('inf'), 0]
        
        for item in catalog:
            categories.update(item.get('categories', []))
            brands.add(item.get('brand', 'Unknown'))
            price = item.get('price_cents', 0)
            if price > 0:
                price_range[0] = min(price_range[0], price)
                price_range[1] = max(price_range[1], price)
        
        return {
            "success": True,
            "total_items": total_items,
            "categories": sorted(list(categories)),
            "brands": sorted(list(brands)),
            "price_range": {
                "min": f"${price_range[0] / 100:.2f}" if price_range[0] != float('inf') else "$0.00",
                "max": f"${price_range[1] / 100:.2f}"
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting catalog stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "success": True,
        "service": "style-inspiration",
        "catalog_loaded": len(inspiration_service.catalog) > 0,
        "catalog_size": len(inspiration_service.catalog)
    }

