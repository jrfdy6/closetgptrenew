"""
Progressive outfits router - adding complexity incrementally.
"""

import logging
import time
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["outfits-progressive"]
)

# Test 1: Basic imports only (already working)
@router.get("/health")
async def outfits_health():
    """Health check for progressive outfits router."""
    return {
        "status": "ok",
        "service": "outfits-progressive",
        "message": "Progressive outfits router is working",
        "test_stage": "basic_imports"
    }

# Test 2: Add model imports
try:
    from .models import OutfitRequest, OutfitResponse
    MODELS_AVAILABLE = True
    logger.info("✅ Models imported successfully")
except ImportError as e:
    logger.error(f"❌ Models import failed: {e}")
    MODELS_AVAILABLE = False
    OutfitRequest = None
    OutfitResponse = None

# Test 3: Add auth imports
try:
    from ..auth.auth_service import get_current_user, get_current_user_id
    AUTH_AVAILABLE = True
    logger.info("✅ Auth imports successful")
except ImportError as e:
    logger.error(f"❌ Auth import failed: {e}")
    AUTH_AVAILABLE = False
    get_current_user = None
    get_current_user_id = None

# Test 4: Add utils imports
try:
    from .utils import log_generation_strategy
    UTILS_AVAILABLE = True
    logger.info("✅ Utils imported successfully")
except ImportError as e:
    logger.error(f"❌ Utils import failed: {e}")
    UTILS_AVAILABLE = False
    log_generation_strategy = None

@router.post("/generate")
async def progressive_generate_outfit(
    req: dict = None,  # Use dict instead of OutfitRequest for now
    current_user_id: str = "test-user"
):
    """Progressive outfit generation with incremental complexity."""
    
    # Test what's available
    availability = {
        "models": MODELS_AVAILABLE,
        "auth": AUTH_AVAILABLE,
        "utils": UTILS_AVAILABLE
    }
    
    # Basic response
    outfit_response = {
        "id": "progressive-outfit-1",
        "name": "Progressive Test Outfit",
        "style": "progressive",
        "mood": "confident",
        "occasion": "testing",
        "items": [],
        "confidence_score": 0.8,
        "reasoning": "Progressive generation test - checking import availability",
        "createdAt": time.time(),
        "user_id": current_user_id,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "wearCount": 0,
        "lastWorn": None,
        "metadata": {
            "generation_strategy": "progressive_test",
            "generation_time": time.time(),
            "availability": availability,
            "test_stage": "incremental_imports"
        }
    }
    
    # Try to log generation strategy if available
    if UTILS_AVAILABLE and log_generation_strategy:
        try:
            log_generation_strategy(outfit_response, current_user_id)
        except Exception as e:
            logger.warning(f"⚠️ Failed to log generation strategy: {e}")
    
    return outfit_response

logger.info("✅ Progressive outfits router created successfully")
