"""
Personalization Demo Routes
==========================

FastAPI routes for the hybrid personalization demo system.
Provides both simple-minimal and robust generation modes using modular services.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends

from src.auth.auth_service import get_current_user_id
from .models import (
    PersonalizationDemoRequest, 
    PersonalizationDemoResponse, 
    PersonalizationStatusResponse
)
from .personalization_service import PersonalizationService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/personalization-demo",
    tags=["personalization-demo"]
)

# Initialize personalization service
personalization_service = PersonalizationService()

@router.get("/health")
async def health_check():
    """Health check for the personalization demo system"""
    try:
        return {
            "status": "healthy",
            "personalization_demo_enabled": True,
            "available_generation_modes": ["simple-minimal", "robust"],
            "uses_modular_services": True,
            "integration_status": "hybrid_refactored",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Personalization demo health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "personalization_demo_enabled": False,
            "timestamp": time.time()
        }

@router.get("/test")
async def test_endpoint():
    """Test endpoint for personalization demo"""
    return {
        "message": "Personalization demo router is working",
        "status": "success",
        "generation_modes": ["simple-minimal", "robust"],
        "uses_modular_architecture": True,
        "timestamp": time.time()
    }

@router.post("/generate", response_model=PersonalizationDemoResponse)
async def generate_personalized_outfit(
    req: PersonalizationDemoRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate personalized outfit using hybrid modular system
    
    This endpoint:
    1. Uses modular generation services (robust or simple-minimal)
    2. Applies personalization based on existing data
    3. Provides detailed generation metadata
    4. Supports both generation modes from the frontend
    """
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate generation mode
        if req.generation_mode not in ["simple-minimal", "robust"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid generation mode. Must be 'simple-minimal' or 'robust'"
            )
        
        logger.info(f"🎯 Generating personalized outfit using {req.generation_mode} mode for user {current_user_id}")
        
        # Generate personalized outfit
        response = await personalization_service.generate_personalized_outfit(req, current_user_id)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Personalized outfit generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Personalized outfit generation failed: {str(e)}"
        )

@router.get("/personalization-status", response_model=PersonalizationStatusResponse)
async def get_personalization_status(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get personalization status with generation mode information"""
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get personalization status
        status = await personalization_service.get_personalization_status(current_user_id)
        
        return PersonalizationStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get personalization status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization status: {str(e)}"
        )

@router.get("/user-preferences")
async def get_user_preferences(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get detailed user preferences from existing data"""
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get user preferences
        preference = await personalization_service.personalization_engine.get_user_preference_from_existing_data(current_user_id)
        
        return {
            "user_id": current_user_id,
            "preferences": {
                "preferred_colors": preference.preferred_colors,
                "preferred_styles": preference.preferred_styles,
                "preferred_occasions": preference.preferred_occasions,
                "disliked_colors": preference.disliked_colors,
                "disliked_styles": preference.disliked_styles
            },
            "existing_data": {
                "favorite_items": preference.favorite_items,
                "most_worn_items": preference.most_worn_items,
                "total_interactions": preference.total_interactions,
                "last_updated": preference.last_updated,
                "data_source": preference.data_source
            },
            "stats": {
                "total_interactions": preference.total_interactions,
                "ready_for_personalization": preference.total_interactions >= 3,
                "favorite_items_count": len(preference.favorite_items),
                "most_worn_items_count": len(preference.most_worn_items)
            },
            "uses_existing_data": True,
            "generation_modes_available": ["simple-minimal", "robust"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user preferences: {str(e)}"
        )

@router.get("/analytics")
async def get_personalization_analytics():
    """Get analytics about the hybrid personalization system"""
    try:
        return {
            "system_stats": {
                "uses_modular_architecture": True,
                "hybrid_refactoring": True,
                "available_generation_modes": ["simple-minimal", "robust"],
                "uses_existing_data": True,
                "data_sources": [
                    "wardrobe_favorites",
                    "wardrobe_wear_counts",
                    "outfit_favorites",
                    "outfit_wear_counts",
                    "user_style_profiles",
                    "item_analytics"
                ],
                "modular_services": [
                    "OutfitGenerationService",
                    "SimpleOutfitService", 
                    "RobustOutfitGenerationService"
                ],
                "no_duplicate_storage": True,
                "firebase_integration": True
            },
            "integration_benefits": [
                "Reuses modular services from main generator",
                "Maintains existing data personalization",
                "Supports both generation modes",
                "Easy migration to main app",
                "Consistent architecture",
                "Enhanced debugging capabilities"
            ],
            "migration_readiness": {
                "architecture_compatible": True,
                "service_reuse": True,
                "data_compatibility": True,
                "ready_for_main_app": True
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get personalization analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization analytics: {str(e)}"
        )
