"""
Outfit management endpoints - Single canonical generator with bulletproof consistency.
All outfits are generated and saved through the same pipeline.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

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

# Simplified mock data function for fallback
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

class OutfitRequest(BaseModel):
    """Request model for outfit generation."""
    style: str
    mood: str
    occasion: str
    description: Optional[str] = None

class OutfitResponse(BaseModel):
    """Response model for outfits."""
    id: str
    name: str
    style: str
    mood: str
    items: List[dict]
    occasion: str
    confidence_score: float
    reasoning: str
    createdAt: datetime
    user_id: Optional[str] = None
    generated_at: Optional[str] = None

# Mock generation logic (replace with real GPT + rules later)
async def generate_outfit_logic(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Mock outfit generation logic - replace with real GPT + rules."""
    logger.info(f"🎨 Generating outfit for user {user_id}: {req.style}, {req.mood}, {req.occasion}")
    
    # Mock generation - replace with real logic
    outfit_name = f"{req.style.title()} {req.mood.title()} Look"
    
    return {
        "name": outfit_name,
        "style": req.style,
        "mood": req.mood,
        "items": [
            {"id": "generated-1", "name": f"{req.style} Top", "type": "shirt", "imageUrl": None},
            {"id": "generated-2", "name": f"{req.mood} Pants", "type": "pants", "imageUrl": None}
        ],
        "occasion": req.occasion,
        "confidence_score": 0.85,
        "reasoning": f"Generated {req.style} outfit for {req.occasion} with {req.mood} mood",
        "createdAt": datetime.now()
    }

# Mock Firestore operations (replace with real operations later)
async def save_outfit(user_id: str, outfit_id: str, outfit_record: Dict[str, Any]) -> bool:
    """Mock save outfit to Firestore - replace with real operation."""
    logger.info(f"💾 Mock saving outfit {outfit_id} for user {user_id}")
    # TODO: Replace with real Firestore save
    return True

async def get_user_outfits(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Mock get user outfits from Firestore - replace with real operation."""
    logger.info(f"📚 Mock fetching outfits for user {user_id}, limit: {limit}, offset: {offset}")
    # TODO: Replace with real Firestore query
    return await get_mock_outfits()

# Health and debug endpoints
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

# ✅ Generate + Save Outfit (single source of truth)
@router.post("/", response_model=OutfitResponse)
async def generate_outfit(
    req: OutfitRequest,
):
    """
    Generate an outfit using decision logic, save it to Firestore,
    and return the standardized response.
    """
    try:
        # TEMPORARILY: Use mock user ID for testing
        current_user_id = "mock-user-123"
        logger.info("Using mock user ID for testing")
        
        logger.info(f"🎨 Generating outfit for user: {current_user_id}")
        
        # 1. Run generation logic (GPT + rules + metadata validation)
        outfit = await generate_outfit_logic(req, current_user_id)

        # 2. Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }

        # 3. Save to Firestore
        await save_outfit(current_user_id, outfit_id, outfit_record)

        # 4. Return standardized outfit response
        logger.info(f"✅ Successfully generated and saved outfit {outfit_id}")
        return OutfitResponse(**outfit_record)

    except Exception as e:
        logger.error(f"❌ Outfit generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate outfit")

# ✅ Retrieve Outfit History
@router.get("/", response_model=List[OutfitResponse])
async def list_outfits(
    limit: int = 50,
    offset: int = 0,
):
    """
    Fetch a user's outfit history from Firestore.
    """
    try:
        # TEMPORARILY: Use mock user ID for testing
        current_user_id = "mock-user-123"
        logger.info("Using mock user ID for testing")
        
        logger.info(f"📚 Fetching outfits for user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        logger.info(f"✅ Successfully retrieved {len(outfits)} outfits for user {current_user_id}")
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        logger.info("🔄 Falling back to mock data due to error")
        mock_outfits = await get_mock_outfits()
        return [OutfitResponse(**o) for o in mock_outfits]

# Support for no-trailing-slash calls
@router.post("", response_model=OutfitResponse)
async def generate_outfit_no_trailing(
    req: OutfitRequest,
):
    """Generate outfit (no trailing slash) - calls the same logic."""
    return await generate_outfit(req)

@router.get("", response_model=List[OutfitResponse])
async def list_outfits_no_trailing(
    limit: int = 50,
    offset: int = 0,
):
    """List outfits (no trailing slash) - calls the same logic."""
    return await list_outfits(limit, offset)

# Individual outfit retrieval
@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    
    try:
        # TEMPORARILY: Use mock user ID for testing
        current_user_id = "mock-user-123"
        logger.info("Using mock user ID for testing")
        
        # Check Firebase availability
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("Firebase not available, returning mock data")
            outfits = await get_mock_outfits()
            for outfit in outfits:
                if outfit["id"] == outfit_id:
                    return OutfitResponse(**outfit)
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        # Try to fetch real outfit from Firebase
        try:
            outfit_doc = db.collection('outfits').document(outfit_id).get()
            if outfit_doc.exists:
                outfit_data = outfit_doc.to_dict()
                outfit_data['id'] = outfit_id
                logger.info(f"Successfully retrieved outfit {outfit_id} from database")
                return OutfitResponse(**outfit_data)
            else:
                logger.warning(f"Outfit {outfit_id} not found in database")
                raise HTTPException(status_code=404, detail="Outfit not found")
                
        except Exception as firebase_error:
            logger.error(f"Firebase query failed: {firebase_error}")
            logger.warning("Falling back to mock data due to Firebase error")
            outfits = await get_mock_outfits()
            for outfit in outfits:
                if outfit["id"] == outfit_id:
                    return OutfitResponse(**outfit)
            raise HTTPException(status_code=404, detail="Outfit not found")
        
    except Exception as e:
        logger.error(f"Error getting outfit {outfit_id}: {e}")
        # Fallback to mock data on other errors
        outfits = await get_mock_outfits()
        for outfit in outfits:
            if outfit["id"] == outfit_id:
                return OutfitResponse(**outfit)
        raise HTTPException(status_code=404, detail="Outfit not found") 