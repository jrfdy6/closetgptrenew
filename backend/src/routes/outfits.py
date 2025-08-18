"""
Outfit management endpoints (GET operations only).
Gradually restoring Firebase functionality while maintaining reliability.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["outfits"])
security = HTTPBearer()

# Firebase imports with graceful fallback
try:
    from ..config.firebase import db, firebase_initialized
    from ..auth.auth_service import get_current_user_optional
    from ..custom_types.profile import UserProfile
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase modules imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Firebase import failed: {e}")
    FIREBASE_AVAILABLE = False
    db = None
    firebase_initialized = False
    # Create a mock get_current_user_optional function
    def get_current_user_optional():
        return None
except Exception as e:
    logger.error(f"❌ Firebase import error: {e}")
    FIREBASE_AVAILABLE = False
    db = None
    firebase_initialized = False
    # Create a mock get_current_user_optional function
    def get_current_user_optional():
        return None

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

@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {
        "status": "healthy", 
        "router": "outfits", 
        "message": "Outfits router is working!",
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits router."""
    logger.info("🔍 DEBUG: Outfits debug endpoint called")
    return {
        "status": "debug",
        "router": "outfits",
        "message": "Outfits router debug endpoint working",
        "timestamp": datetime.now().isoformat(),
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/", response_model=List[OutfitResponse])
async def get_outfits():
    """Get all outfits for the current user."""
    logger.info("🔍 DEBUG: Get outfits endpoint called")
    
    try:
        # Check Firebase availability
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase modules not available, returning mock data")
            return await get_mock_outfits()
        
        if not firebase_initialized:
            logger.warning("Firebase not initialized, returning mock data")
            return await get_mock_outfits()
        
        # TEMPORARILY DISABLED AUTH - for testing endpoint loading
        # if not current_user:
        #     logger.warning("No user authenticated, returning mock data")
        #     return await get_mock_outfits()
        
        logger.info("Firebase available and initialized, attempting to fetch real data")
        
        # Try to fetch real outfits from Firebase
        try:
            outfits_ref = db.collection('outfits')
            # TEMPORARILY DISABLED USER FILTERING - for testing
            # if current_user and hasattr(current_user, 'id') and current_user.id:
            #     # Filter by user if authenticated
            #     outfits_ref = outfits_ref.where('user_id', '==', current_user.id)
            #     logger.info(f"Filtering outfits for user: {current_user.id}")
            # else:
            #     logger.info("No user ID, fetching all outfits")
            
            logger.info("Fetching all outfits from database (no user filter)")
            
            outfits_docs = outfits_ref.stream()
            outfits = []
            
            for doc in outfits_docs:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfits.append(outfit_data)
            
            if outfits:
                logger.info(f"Found {len(outfits)} real outfits from database")
                return outfits
            else:
                logger.info("No outfits found in database, returning mock data")
                return await get_mock_outfits()
                
        except Exception as firebase_error:
            logger.error(f"Firebase query failed: {firebase_error}")
            logger.warning("Falling back to mock data due to Firebase error")
            return await get_mock_outfits()
        
    except Exception as e:
        logger.error(f"Error getting outfits: {e}")
        # Fallback to mock data on error
        logger.warning("Falling back to mock data due to error")
        return await get_mock_outfits()

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    
    try:
        # Check Firebase availability
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("Firebase not available, returning mock data")
            outfits = await get_mock_outfits()
            for outfit in outfits:
                if outfit["id"] == outfit_id:
                    return outfit
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        # Try to fetch real outfit from Firebase
        try:
            outfit_doc = db.collection('outfits').document(outfit_id).get()
            if outfit_doc.exists:
                outfit_data = outfit_doc.to_dict()
                outfit_data['id'] = outfit_id
                logger.info(f"Successfully retrieved outfit {outfit_id} from database")
                return outfit_data
            else:
                logger.warning(f"Outfit {outfit_id} not found in database")
                raise HTTPException(status_code=404, detail="Outfit not found")
                
        except Exception as firebase_error:
            logger.error(f"Firebase query failed: {firebase_error}")
            logger.warning("Falling back to mock data due to Firebase error")
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