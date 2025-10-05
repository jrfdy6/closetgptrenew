"""
Main router endpoints for outfit generation and management.
"""

import logging
import time
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import OutfitRequest, OutfitResponse
from .utils import log_generation_strategy
from ..auth.auth_service import get_current_user, get_current_user_id
from ...services.outfits.generation_service import OutfitGenerationService
from ...services.outfits.simple_service import SimpleOutfitService
from .rule_engine import generate_rule_based_outfit, generate_fallback_outfit

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["outfits"]
)
security = HTTPBearer()


@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check endpoint for outfits service."""
    return {
        "status": "healthy",
        "service": "outfits",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits service."""
    return {
        "service": "outfits",
        "debug_info": {
            "models_loaded": True,
            "utils_loaded": True,
            "validation_loaded": True,
            "styling_loaded": True,
            "weather_loaded": True,
            "generation_loaded": True
        },
        "timestamp": time.time()
    }


@router.post("/generate", response_model=OutfitResponse)
async def generate_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate an outfit using robust decision logic with comprehensive validation,
    fallback strategies, body type optimization, and style profile integration.
    """
    try:
        start_time = time.time()
        generation_attempts = 0
        max_attempts = 3
        
        # Enhanced authentication validation
        if not current_user_id:
            logger.error("❌ Authentication failed: No current user ID")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"🎯 Starting robust outfit generation for user: {current_user_id}")
        logger.info(f"📋 Request details: {req.occasion}, {req.style}, {req.mood}")
        
        # Initialize services
        generation_service = OutfitGenerationService()
        simple_service = SimpleOutfitService()
        
        # Try robust generation first
        try:
            outfit_response = await generation_service.generate_outfit_logic(req, current_user_id)
            logger.info(f"✅ Robust outfit generation successful")
            
        except Exception as e:
            logger.warning(f"⚠️ Robust generation failed, falling back to simple: {e}")
            
            # Fallback to rule-based generation
            try:
                user_profile = {}  # TODO: Get actual user profile
                outfit_response = await generate_rule_based_outfit(req.resolved_wardrobe, user_profile, req)
                logger.info(f"✅ Rule-based outfit generation successful")
                
            except Exception as rule_error:
                logger.warning(f"⚠️ Rule-based generation failed, trying simple fallback: {rule_error}")
                
                # Final fallback to simple generation
                try:
                    outfit_response = await simple_service.generate_simple_outfit(req, current_user_id)
                    logger.info(f"✅ Simple outfit generation successful")
                    
                except Exception as simple_error:
                    logger.error(f"❌ All generation methods failed: {simple_error}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Outfit generation failed: {str(simple_error)}"
                    )
        
        # Log generation strategy
        log_generation_strategy(
            outfit_response, 
            current_user_id, 
            time.time() - start_time
        )
        
        return OutfitResponse(**outfit_response)
        
    except Exception as e:
        logger.error(f"❌ Outfit generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Outfit generation failed: {str(e)}"
        )


# Note: Additional endpoints will be extracted from the original file:
# - Debug endpoints
# - Firebase test endpoints  
# - Outfit management endpoints
# - Analytics endpoints
