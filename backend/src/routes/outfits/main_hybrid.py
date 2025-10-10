"""
Main Hybrid Outfit Generation Router
====================================

This router integrates the proven personalization demo hybrid system
into the main app's /api/outfits endpoints. It provides both simple-minimal
and robust generation modes using the modular architecture that's already
working in the personalization demo.

Based on the successful personalization demo implementation.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.auth_utils import extract_uid_from_request
from src.auth.auth_service import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["outfits-main-hybrid"]
)

# Security
security = HTTPBearer(auto_error=False)

# Import the proven personalization service with fallback
try:
    from src.routes.personalization_demo.personalization_service import PersonalizationService
    from src.routes.personalization_demo.models import (
        PersonalizationDemoRequest,
        PersonalizationDemoResponse
    )
    PERSONALIZATION_SERVICE_AVAILABLE = True
    logger.info("✅ Personalization service imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import personalization service: {e}")
    PERSONALIZATION_SERVICE_AVAILABLE = False
    
    # Create fallback classes
    class PersonalizationDemoRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PersonalizationDemoResponse:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PersonalizationService:
        async def generate_personalized_outfit(self, request):
            return PersonalizationDemoResponse(
                id="fallback",
                name="Fallback Outfit",
                items=[],
                reasoning="Service unavailable - using fallback"
            )

# Initialize personalization service
if PERSONALIZATION_SERVICE_AVAILABLE:
    personalization_service = PersonalizationService()
else:
    personalization_service = None

@router.get("/health")
async def health_check():
    """Health check for the main hybrid outfit generation system"""
    try:
        return {
            "status": "healthy",
            "main_outfit_generation_enabled": True,
            "available_generation_modes": ["simple-minimal", "robust"],
            "uses_hybrid_architecture": True,
            "personalization_service_available": PERSONALIZATION_SERVICE_AVAILABLE,
            "integration_status": "migrated_from_demo",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Main outfit generation health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "main_outfit_generation_enabled": False
        }

@router.post("/debug-filter")
async def debug_outfit_filtering(
    request: dict,
    req: Request,
    semantic: bool = False
):
    """Debug endpoint to see why items are being filtered out during outfit generation."""
    try:
        if not PERSONALIZATION_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Debug service is currently unavailable"
            )
        
        # Extract user ID using robust authentication, with fallback for testing
        try:
            current_user_id = extract_uid_from_request(req)
        except HTTPException as auth_error:
            # For debug purposes, allow test mode with a fallback user ID
            logger.warning(f"🔍 DEBUG: Authentication failed, using test mode: {auth_error.detail}")
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Use real user for debug
        
        logger.info(f"🔍 DEBUG FILTER: Request from user: {current_user_id}")
        logger.info(f"🔍 DEBUG FILTER: Request data: {request}")
        
        # TEMPORARY: Auto-fetch wardrobe if empty
        wardrobe_items = request.get("wardrobe", [])
        if len(wardrobe_items) == 0:
            logger.info(f"🔍 DEBUG FILTER: Wardrobe empty, fetching from Firebase...")
            try:
                from src.config.firebase import db
                docs = db.collection('wardrobe').where('userId', '==', current_user_id).stream()
                wardrobe_items = [doc.to_dict() for doc in docs]
                logger.info(f"✅ DEBUG FILTER: Fetched {len(wardrobe_items)} items from Firebase")
            except Exception as e:
                logger.error(f"❌ DEBUG FILTER: Failed to fetch wardrobe: {e}")
        
        # Create debug request
        demo_request = PersonalizationDemoRequest(
            occasion=request.get("occasion", "casual"),
            style=request.get("style", "casual"),
            mood=request.get("mood", "comfortable"),
            weather=request.get("weather"),
            wardrobe=wardrobe_items,
            user_profile=request.get("user_profile"),
            baseItemId=request.get("baseItemId"),
            generation_mode="debug"  # Special debug mode
        )
        
        # Get debug analysis from personalization service
        debug_result = await personalization_service.debug_outfit_filtering(
            demo_request,
            current_user_id,
            semantic_filtering=semantic
        )
        
        logger.info(f"✅ DEBUG FILTER: Analysis complete (semantic={semantic})")
        
        # Use enhanced debug output format
        try:
            from src.utils.enhanced_debug_output import format_final_debug_response
            
            enhanced_response = format_final_debug_response(
                outfits=[],  # No outfits generated in debug mode
                debug_analysis=debug_result.get('debug_analysis', []),
                semantic_mode=semantic,
                requested_style=demo_request.style,
                requested_occasion=demo_request.occasion,
                requested_mood=demo_request.mood,
                debug_output=debug_result.get('debug_output')
            )
            
            return {
                "success": True,
                **enhanced_response,
                "filters_applied": {
                    "occasion": demo_request.occasion,
                    "style": demo_request.style,
                    "mood": demo_request.mood,
                    "weather": demo_request.weather,
                    "semantic_mode": semantic
                },
                "timestamp": time.time(),
                "user_id": current_user_id
            }
        except ImportError:
            # Fallback to original format if enhanced output not available
            return {
                "success": True,
                "debug_analysis": debug_result,
                "filters_applied": {
                    "occasion": demo_request.occasion,
                    "style": demo_request.style,
                    "mood": demo_request.mood,
                    "weather": demo_request.weather,
                    "semantic_mode": semantic
                },
                "timestamp": time.time(),
                "user_id": current_user_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ DEBUG FILTER: Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug analysis failed: {str(e)}"
        )

@router.post("/generate")
async def generate_outfit(
    request: dict,
    req: Request
):
    """
    Main outfit generation endpoint with hybrid architecture.
    
    Supports both simple-minimal and robust generation modes.
    Uses the proven personalization demo system under the hood.
    """
    try:
        if not PERSONALIZATION_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Outfit generation service is currently unavailable"
            )
        
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        logger.info(f"🎯 Main outfit generation request from user: {current_user_id}")
        logger.info(f"📋 Request data: {request}")
        
        # Extract generation mode from request, default to robust
        generation_mode = request.get("generation_mode", "robust")
        
        # Convert request to personalization demo format
        demo_request = PersonalizationDemoRequest(
            occasion=request.get("occasion", "casual"),
            style=request.get("style", "casual"),
            mood=request.get("mood", "comfortable"),
            weather=request.get("weather"),  # Changed from weather_data to weather
            wardrobe=request.get("wardrobe", []),  # CRITICAL: Pass wardrobe data
            user_profile=request.get("user_profile"),
            baseItemId=request.get("baseItemId"),
            generation_mode=generation_mode
        )
        
        # Generate outfit using the proven personalization service
        result = await personalization_service.generate_personalized_outfit(
            demo_request,
            current_user_id
        )
        
        logger.info(f"✅ Main outfit generation successful with mode: {generation_mode}")
        
        # Convert response to main app format
        # Set validation metadata based on actual outfit quality
        result_metadata = result.metadata if hasattr(result, 'metadata') else {}
        if isinstance(result_metadata, dict):
            # Get the actual items from the result
            result_items = result.items if hasattr(result, 'items') else []
            item_count = len(result_items)
            
            # Validation checks:
            # - Minimum 3 items required for a complete outfit
            # - Must have essential categories (tops, bottoms, shoes)
            min_items_met = item_count >= 3
            
            # Check for essential categories
            has_top = False
            has_bottom = False
            has_shoes = False
            for item in result_items:
                item_type = str(getattr(item, 'type', '')).lower()
                if 'shirt' in item_type or 'top' in item_type or 'blouse' in item_type:
                    has_top = True
                elif 'pants' in item_type or 'bottom' in item_type or 'skirt' in item_type or 'shorts' in item_type:
                    has_bottom = True
                elif 'shoe' in item_type:
                    has_shoes = True
            
            essential_categories_met = has_top and has_bottom and has_shoes
            
            # Overall validation: passed if minimum items AND essential categories
            validation_passed = min_items_met and essential_categories_met
            
            # Set validation flags based on actual checks
            result_metadata['validation_applied'] = True  # We always apply validation
            result_metadata['occasion_requirements_met'] = validation_passed
            result_metadata['deduplication_applied'] = True  # Always applied in robust service
            
            # Add debug info
            if not validation_passed:
                logger.warning(f"⚠️ VALIDATION FAILED: items={item_count}, min_items_met={min_items_met}, "
                             f"has_top={has_top}, has_bottom={has_bottom}, has_shoes={has_shoes}")
                result_metadata['validation_failure_reason'] = {
                    'item_count': item_count,
                    'min_items_met': min_items_met,
                    'essential_categories_met': essential_categories_met,
                    'has_top': has_top,
                    'has_bottom': has_bottom,
                    'has_shoes': has_shoes
                }
        
        return {
            "success": True,
            "id": result.id if hasattr(result, 'id') else f"outfit_{int(time.time())}",
            "name": result.name if hasattr(result, 'name') else f"{request.get('style', 'Unknown')} {request.get('occasion', 'Outfit')}",
            "items": result.items if hasattr(result, 'items') else [],
            "style": result.style if hasattr(result, 'style') else request.get('style', 'unknown'),
            "occasion": result.occasion if hasattr(result, 'occasion') else request.get('occasion', 'unknown'),
            "mood": result.mood if hasattr(result, 'mood') else request.get('mood', 'unknown'),
            "weather": result.weather if hasattr(result, 'weather') else {},
            "confidence_score": result.confidence_score if hasattr(result, 'confidence_score') else 0.8,
            "personalization_score": result.personalization_score if hasattr(result, 'personalization_score') else None,
            "personalization_applied": result.personalization_applied if hasattr(result, 'personalization_applied') else True,
            "generation_mode": generation_mode,
            "generation_strategy": result.generation_strategy if hasattr(result, 'generation_strategy') else "hybrid",
            "data_source": result.data_source if hasattr(result, 'data_source') else "main_hybrid",
            "metadata": result_metadata,
            "timestamp": time.time(),
            "user_id": current_user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Main outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outfit generation failed: {str(e)}"
        )

@router.post("/generate-simple")
async def generate_simple_outfit(
    request: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Simple outfit generation endpoint - forces simple-minimal mode.
    
    Convenience endpoint for clients that specifically want simple generation.
    """
    try:
        # Force simple-minimal mode
        request["generation_mode"] = "simple-minimal"
        
        # Use the main generate endpoint
        return await generate_outfit(request, current_user_id)
        
    except Exception as e:
        logger.error(f"❌ Simple outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple outfit generation failed: {str(e)}"
        )

@router.post("/generate-robust")
async def generate_robust_outfit(
    request: dict,
    req: Request
):
    """
    Robust outfit generation endpoint - forces robust mode.
    
    Convenience endpoint for clients that specifically want robust generation.
    """
    try:
        # Force robust mode
        request["generation_mode"] = "robust"
        
        # Use the main generate endpoint
        return await generate_outfit(request, req)
        
    except Exception as e:
        logger.error(f"❌ Robust outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robust outfit generation failed: {str(e)}"
        )

@router.get("/debug-user")
async def debug_user_info(
    req: Request
):
    """
    Debug endpoint to check user authentication and service availability.
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        return {
            "user_id": current_user_id,
            "personalization_service_available": PERSONALIZATION_SERVICE_AVAILABLE,
            "timestamp": time.time(),
            "status": "debug_info_retrieved"
        }
    except Exception as e:
        logger.error(f"❌ Debug user info failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug info retrieval failed: {str(e)}"
        )

@router.get("/status")
async def generation_status():
    """
    Get the current status of the outfit generation system.
    """
    try:
        return {
            "system_status": "operational",
            "generation_modes": ["simple-minimal", "robust"],
            "personalization_enabled": True,
            "hybrid_architecture": True,
            "service_availability": {
                "personalization_service": PERSONALIZATION_SERVICE_AVAILABLE,
                "main_endpoints": True
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {
            "system_status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("")
async def get_outfits(
    req: Request,
    limit: int = 50,
    offset: int = 0
):
    """
    Get outfit history for the authenticated user.
    
    This endpoint fetches previously generated outfits from the outfit history.
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        logger.info(f"📋 Fetching outfits for user: {current_user_id} (limit={limit}, offset={offset})")
        
        # Import Firebase
        from src.config.firebase import db
        
        # Query outfit history collection using Firestore index
        query = db.collection('outfit_history')\
            .where('userId', '==', current_user_id)\
            .order_by('createdAt', direction='DESCENDING')\
            .limit(limit)
        
        if offset > 0:
            # Get the last document from the previous page for pagination
            prev_query = db.collection('outfit_history')\
                .where('userId', '==', current_user_id)\
                .order_by('createdAt', direction='DESCENDING')\
                .limit(offset)
            prev_docs = list(prev_query.stream())
            if prev_docs:
                query = query.start_after(prev_docs[-1])
        
        # Fetch outfits
        docs = query.stream()
        outfits = []
        
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append(outfit_data)
        
        logger.info(f"✅ Retrieved {len(outfits)} outfits for user {current_user_id}")
        
        return {
            "success": True,
            "outfits": outfits,
            "count": len(outfits),
            "limit": limit,
            "offset": offset,
            "user_id": current_user_id,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch outfits: {str(e)}"
        )
