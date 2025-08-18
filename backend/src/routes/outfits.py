"""
Outfit management endpoints (GET operations only).
Outfit generation is handled by /api/outfit/generate.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Simplified imports to avoid runtime errors
# from ..config.firebase import db, firebase_initialized
# from ..auth.auth_service import get_current_user_optional
# from ..custom_types.profile import UserProfile

logger = logging.getLogger(__name__)
router = APIRouter(tags=["outfits"])
security = HTTPBearer()

# Simplified mock data function
async def get_mock_outfits() -> List[Dict[str, Any]]:
    """Return mock outfit data for testing."""
    return [
        {
            "id": "mock-outfit-1",
            "name": "Casual Summer Look",
            "style": "casual",
            "mood": "relaxed",
            "items": [
                {"id": "item-1", "name": "Blue T-Shirt", "type": "shirt", "imageUrl": None},
                {"id": "item-2", "name": "Jeans", "type": "pants", "imageUrl": None}
            ],
            "occasion": "casual",
            "confidence_score": 0.85,
            "reasoning": "Perfect for a relaxed summer day",
            "createdAt": datetime.now()
        },
        {
            "id": "mock-outfit-2",
            "name": "Business Casual",
            "style": "business",
            "mood": "professional",
            "items": [
                {"id": "item-3", "name": "White Button-Up", "type": "shirt", "imageUrl": None},
                {"id": "item-4", "name": "Khaki Pants", "type": "pants", "imageUrl": None}
            ],
            "occasion": "business",
            "confidence_score": 0.90,
            "reasoning": "Professional yet comfortable",
            "createdAt": datetime.now()
        }
    ]

class OutfitResponse(BaseModel):
    id: str
    name: str
    style: str
    mood: str
    items: List[dict]
    occasion: str
    confidence_score: float
    reasoning: str
    createdAt: datetime

class OutfitFeedback(BaseModel):
    outfit_id: str
    rating: int  # 1-5 scale
    feedback_type: str  # "like", "dislike", "comment"
    comment: Optional[str] = None

@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {"status": "healthy", "router": "outfits", "message": "Outfits router is working!"}

@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits router."""
    logger.info("🔍 DEBUG: Outfits debug endpoint called")
    return {
        "status": "debug",
        "router": "outfits",
        "message": "Outfits router debug endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/", response_model=List[OutfitResponse])
async def get_outfits():
    """Get all outfits for the current user."""
    logger.info("🔍 DEBUG: Get outfits endpoint called")
    try:
        # For now, just return mock data to get the endpoint working
        logger.info("Returning mock outfits data")
        return await get_mock_outfits()
        
    except Exception as e:
        logger.error(f"Error getting outfits: {e}")
        # Fallback to mock data on error
        return await get_mock_outfits()

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    try:
        # For now, just return mock data to get the endpoint working
        outfits = await get_mock_outfits()
        for outfit in outfits:
            if outfit["id"] == outfit_id:
                return outfit
        
        raise HTTPException(status_code=404, detail="Outfit not found")
        
    except Exception as e:
        logger.error(f"Error getting outfit {outfit_id}: {e}")
        # Fallback to mock data on other errors
        outfits = await get_mock_outfits()
        for outfit in outfits:
            if outfit["id"] == outfit_id:
                return outfit
        raise HTTPException(status_code=404, detail="Outfit not found")

@router.get("/test", response_model=List[OutfitResponse])
async def test_outfits():
    """Test endpoint for outfits."""
    logger.info("🔍 DEBUG: Test outfits endpoint called")
    return await get_mock_outfits() 