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
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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

@router.post("/generate")
async def generate_outfit(
    request: dict,
    current_user_id: str = Depends(get_current_user_id)
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
        
        logger.info(f"🎯 Main outfit generation request from user: {current_user_id}")
        logger.info(f"📋 Request data: {request}")
        
        # Extract generation mode from request, default to robust
        generation_mode = request.get("generation_mode", "robust")
        
        # Convert request to personalization demo format
        demo_request = PersonalizationDemoRequest(
            occasion=request.get("occasion", "casual"),
            style=request.get("style", "casual"),
            mood=request.get("mood", "comfortable"),
            weather_data=request.get("weather_data"),
            user_preferences=request.get("user_preferences"),
            generation_mode=generation_mode,
            user_id=current_user_id
        )
        
        # Generate outfit using the proven personalization service
        result = await personalization_service.generate_personalized_outfit(
            demo_request,
            current_user_id
        )
        
        logger.info(f"✅ Main outfit generation successful with mode: {generation_mode}")
        
        # Convert response to main app format
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
            "metadata": result.metadata if hasattr(result, 'metadata') else {},
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
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Robust outfit generation endpoint - forces robust mode.
    
    Convenience endpoint for clients that specifically want robust generation.
    """
    try:
        # Force robust mode
        request["generation_mode"] = "robust"
        
        # Use the main generate endpoint
        return await generate_outfit(request, current_user_id)
        
    except Exception as e:
        logger.error(f"❌ Robust outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robust outfit generation failed: {str(e)}"
        )

@router.get("/debug-user")
async def debug_user_info(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Debug endpoint to check user authentication and service availability.
    """
    try:
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
