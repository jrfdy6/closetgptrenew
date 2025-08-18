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
    """Get all outfits for the current user - Hybrid approach with Firebase fallback."""
    logger.info("🔍 DEBUG: Get outfits endpoint called - Hybrid mode")
    
    # Check Firebase availability first
    if FIREBASE_AVAILABLE and firebase_initialized:
        logger.info("🔥 Firebase available - attempting to fetch real data")
        try:
            # Try to get current user (optional for now)
            # current_user = await get_current_user_optional()
            # if current_user:
            #     user_id = current_user.uid
            #     logger.info(f"Fetching outfits for user: {user_id}")
            # else:
            #     logger.warning("No authenticated user, using mock data")
            #     return await get_mock_outfits()
            
            # TEMPORARILY: Use mock user ID for testing
            user_id = "test-user-123"
            logger.info(f"Using test user ID: {user_id}")
            
            # Query Firebase for user's outfits
            outfits_ref = db.collection('outfits')
            query = outfits_ref.where('user_id', '==', user_id).limit(50)
            outfits_docs = query.stream()
            
            outfits = []
            for doc in outfits_docs:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfits.append(outfit_data)
            
            if outfits:
                logger.info(f"✅ Successfully retrieved {len(outfits)} outfits from Firebase")
                return outfits
            else:
                logger.info("📝 No outfits found in Firebase, falling back to mock data")
                return await get_mock_outfits()
                
        except Exception as firebase_error:
            logger.error(f"❌ Firebase query failed: {firebase_error}")
            logger.info("🔄 Falling back to mock data due to Firebase error")
            return await get_mock_outfits()
    else:
        logger.warning("⚠️ Firebase not available, using mock data")
        return await get_mock_outfits()
    
    # Final fallback (should never reach here)
    logger.error("🚨 Unexpected fallback path reached")
    return await get_mock_outfits()

@router.get("", response_model=List[OutfitResponse])
async def get_outfits_no_trailing():
    """Get all outfits for the current user (no trailing slash) - Hybrid approach."""
    logger.info("🔍 DEBUG: Get outfits endpoint called (no trailing slash) - Hybrid mode")
    
    # Use the same hybrid logic as the trailing slash version
    if FIREBASE_AVAILABLE and firebase_initialized:
        logger.info("🔥 Firebase available - attempting to fetch real data")
        try:
            # TEMPORARILY: Use mock user ID for testing
            user_id = "test-user-123"
            logger.info(f"Using test user ID: {user_id}")
            
            # Query Firebase for user's outfits
            outfits_ref = db.collection('outfits')
            query = outfits_ref.where('user_id', '==', user_id).limit(50)
            outfits_docs = query.stream()
            
            outfits = []
            for doc in outfits_docs:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfits.append(outfit_data)
            
            if outfits:
                logger.info(f"✅ Successfully retrieved {len(outfits)} outfits from Firebase")
                return outfits
            else:
                logger.info("📝 No outfits found in Firebase, falling back to mock data")
                return await get_mock_outfits()
                
        except Exception as firebase_error:
            logger.error(f"❌ Firebase query failed: {firebase_error}")
            logger.info("🔄 Falling back to mock data due to Firebase error")
            return await get_mock_outfits()
    else:
        logger.warning("⚠️ Firebase not available, using mock data")
        return await get_mock_outfits()
    
    # Final fallback (should never reach here)
    logger.error("🚨 Unexpected fallback path reached")
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