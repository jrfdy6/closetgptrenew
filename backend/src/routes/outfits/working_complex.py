"""
Working complex outfits router - adding complexity incrementally.
All imports are verified to work individually.
"""

import logging
import time
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["outfits-working-complex"]
)

# Import all the working components
from .models import OutfitRequest, OutfitResponse
from .utils import log_generation_strategy
from src.auth.auth_service import get_current_user, get_current_user_id

# Import services with error handling
try:
    from src.services.outfits.generation_service import OutfitGenerationService
    GENERATION_SERVICE_AVAILABLE = True
    logger.info("✅ Generation service imported successfully")
except ImportError as e:
    logger.error(f"❌ Generation service import failed: {e}")
    GENERATION_SERVICE_AVAILABLE = False
    OutfitGenerationService = None

try:
    from src.services.outfits.simple_service import SimpleOutfitService
    SIMPLE_SERVICE_AVAILABLE = True
    logger.info("✅ Simple service imported successfully")
except ImportError as e:
    logger.error(f"❌ Simple service import failed: {e}")
    SIMPLE_SERVICE_AVAILABLE = False
    SimpleOutfitService = None

try:
    from .rule_engine import generate_rule_based_outfit, generate_fallback_outfit
    RULE_ENGINE_AVAILABLE = True
    logger.info("✅ Rule engine imported successfully")
except ImportError as e:
    logger.error(f"❌ Rule engine import failed: {e}")
    RULE_ENGINE_AVAILABLE = False
    generate_rule_based_outfit = None
    generate_fallback_outfit = None

@router.get("/health")
async def working_complex_health():
    """Health check for working complex outfits router."""
    return {
        "status": "ok",
        "service": "outfits-working-complex",
        "message": "Working complex outfits router is operational",
        "services": {
            "generation_service": GENERATION_SERVICE_AVAILABLE,
            "simple_service": SIMPLE_SERVICE_AVAILABLE,
            "rule_engine": RULE_ENGINE_AVAILABLE
        }
    }

@router.post("/test-generate")
async def test_outfit_generation(
    req: OutfitRequest
):
    """
    Test outfit generation without authentication for debugging.
    """
    start_time = time.time()
    
    if not (GENERATION_SERVICE_AVAILABLE or SIMPLE_SERVICE_AVAILABLE or RULE_ENGINE_AVAILABLE):
        return {
            "status": "error",
            "message": "No outfit generation services are available",
            "services": {
                "generation_service": GENERATION_SERVICE_AVAILABLE,
                "simple_service": SIMPLE_SERVICE_AVAILABLE,
                "rule_engine": RULE_ENGINE_AVAILABLE
            }
        }
    
    # Initialize services based on availability
    generation_service = OutfitGenerationService() if GENERATION_SERVICE_AVAILABLE else None
    simple_service = SimpleOutfitService() if SIMPLE_SERVICE_AVAILABLE else None
    
    # Try robust generation first
    if generation_service:
        try:
            outfit_response = await generation_service.generate_outfit_logic(req, "test-user")
            
            # Check if this is a debug response indicating robust service failure
            if outfit_response.get('metadata', {}).get('generation_strategy') == 'robust_debug':
                logger.warning(f"⚠️ Robust service failed, falling back to rule-based: {outfit_response.get('reasoning', 'Unknown error')}")
                raise Exception(f"Robust service debug mode: {outfit_response.get('reasoning', 'Unknown error')}")
            
            logger.info(f"✅ Test robust outfit generation successful")
            return {
                "status": "success",
                "strategy": "robust",
                "outfit": outfit_response,
                "generation_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Test robust generation failed, trying rule-based: {e}")
            
            # Fallback to rule-based generation
            if RULE_ENGINE_AVAILABLE:
                try:
                    user_profile = {}
                    outfit_response = await generate_rule_based_outfit(req.resolved_wardrobe, user_profile, req)
                    logger.info(f"✅ Test rule-based outfit generation successful")
                    return {
                        "status": "success",
                        "strategy": "rule_based",
                        "outfit": outfit_response,
                        "generation_time": time.time() - start_time
                    }
                    
                except Exception as rule_error:
                    logger.warning(f"⚠️ Test rule-based generation failed, trying simple: {rule_error}")
                    
                    # Final fallback to simple generation
                    if simple_service:
                        try:
                            outfit_response = await simple_service.generate_simple_outfit(req, "test-user")
                            logger.info(f"✅ Test simple outfit generation successful")
                            return {
                                "status": "success",
                                "strategy": "simple",
                                "outfit": outfit_response,
                                "generation_time": time.time() - start_time
                            }
                            
                        except Exception as simple_error:
                            logger.error(f"❌ Test simple generation failed: {simple_error}")
                            return {
                                "status": "error",
                                "message": f"All generation methods failed: {str(simple_error)}",
                                "generation_time": time.time() - start_time
                            }
                    else:
                        return {
                            "status": "error",
                            "message": "No generation services available",
                            "generation_time": time.time() - start_time
                        }
            else:
                return {
                    "status": "error",
                    "message": "No generation services available",
                    "generation_time": time.time() - start_time
                }
    else:
        return {
            "status": "error",
            "message": "Complex outfit generation service not available",
            "generation_time": time.time() - start_time
        }

@router.post("/generate")
async def working_complex_generate_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Working complex outfit generation with verified imports and 4-tier fallback strategy.
    """
    start_time = time.time()
    
    if not (GENERATION_SERVICE_AVAILABLE or SIMPLE_SERVICE_AVAILABLE or RULE_ENGINE_AVAILABLE):
        raise HTTPException(
            status_code=500,
            detail="No outfit generation services are available. Please check backend logs."
        )
    
    # Initialize services based on availability
    generation_service = OutfitGenerationService() if GENERATION_SERVICE_AVAILABLE else None
    simple_service = SimpleOutfitService() if SIMPLE_SERVICE_AVAILABLE else None
    
    # Try robust generation first
    if generation_service:
        try:
            outfit_response = await generation_service.generate_outfit_logic(req, current_user_id)
            logger.info(f"✅ Robust outfit generation successful")
            
        except Exception as e:
            logger.warning(f"⚠️ Robust generation failed, falling back to rule-based: {e}")
            
            # Fallback to rule-based generation
            if RULE_ENGINE_AVAILABLE:
                try:
                    user_profile = {}  # TODO: Get actual user profile
                    outfit_response = await generate_rule_based_outfit(req.resolved_wardrobe, user_profile, req)
                    logger.info(f"✅ Rule-based outfit generation successful")
                    
                except Exception as rule_error:
                    logger.warning(f"⚠️ Rule-based generation failed, trying simple fallback: {rule_error}")
                    
                    # Final fallback to simple generation
                    if simple_service:
                        try:
                            outfit_response = await simple_service.generate_simple_outfit(req, current_user_id)
                            logger.info(f"✅ Simple outfit generation successful")
                            
                        except Exception as simple_error:
                            logger.error(f"❌ All generation methods failed: {simple_error}")
                            raise HTTPException(
                                status_code=500,
                                detail=f"Outfit generation failed: {str(simple_error)}"
                            )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="No outfit generation services available"
                        )
            else:
                # Try simple service directly
                if simple_service:
                    try:
                        outfit_response = await simple_service.generate_simple_outfit(req, current_user_id)
                        logger.info(f"✅ Simple outfit generation successful")
                    except Exception as simple_error:
                        logger.error(f"❌ Simple generation failed: {simple_error}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Outfit generation failed: {str(simple_error)}"
                        )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="No outfit generation services available"
                    )
    else:
        raise HTTPException(
            status_code=500,
            detail="Complex outfit generation service not available"
        )
    
    # Log generation strategy
    log_generation_strategy(
        outfit_response, 
        current_user_id, 
        generation_time=time.time() - start_time
    )
    
    return outfit_response

logger.info("✅ Working complex outfits router created successfully")
