#!/usr/bin/env python3
"""
Lightweight Outfits Routes - No External Dependencies
====================================================

This module provides personalized outfit generation using lightweight
embeddings without requiring external APIs or databases.

New Endpoints:
- POST /api/outfits-lightweight/generate-personalized - Generate personalized outfits
- POST /api/outfits-lightweight/interaction - Record user interactions
- GET /api/outfits-lightweight/personalization-status - Get personalization status
- GET /api/outfits-lightweight/analytics - Get recommendation analytics
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services.lightweight_outfit_generation import LightweightOutfitGeneration, LightweightOutfitResult
from ..services.lightweight_embedding_service import UserInteraction
from ..custom_types.outfit_rules import OutfitRequest, OutfitResponse
from ..auth.auth_service import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize lightweight embedding service
lightweight_service = LightweightOutfitGeneration()

# Pydantic models for new endpoints
class InteractionRequest(BaseModel):
    outfit_id: Optional[str] = None
    item_id: Optional[str] = None
    interaction_type: str  # view, like, wear, dislike
    rating: Optional[float] = None

class PersonalizationStatusResponse(BaseModel):
    user_id: str
    personalization_enabled: bool
    has_user_embedding: bool
    total_interactions: int
    recommended_strategy: str
    personalization_score: float
    confidence: float
    system_parameters: Dict[str, Any]

class AnalyticsResponse(BaseModel):
    embedding_service: Dict[str, Any]
    personalization_enabled: bool
    fallback_enabled: bool
    max_personalized_outfits: int
    recommendation_parameters: Dict[str, Any]

@router.post("/generate-personalized", response_model=OutfitResponse)
async def generate_lightweight_personalized_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate personalized outfit using lightweight embeddings.
    
    This endpoint provides personalized outfit generation without external dependencies:
    - Lightweight hash-based embeddings
    - In-memory storage with JSON persistence
    - Cosine similarity using pure Python
    - Continuous learning from user interactions
    """
    start_time = time.time()
    
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        logger.info(f"🎯 Generating lightweight personalized outfit for user {user_id}")
        
        # Create generation context
        generation_context = {
            "occasion": req.occasion,
            "style": req.style,
            "mood": req.mood,
            "weather": req.weather.dict() if req.weather else {},
            "user_profile": {"id": user_id, "name": "User"},
            "base_item_id": req.baseItemId
        }
        
        # Import the existing outfit generation function
        from .outfits import generate_outfit_logic
        
        # Generate personalized outfits
        personalized_result = await lightweight_service.generate_personalized_outfits(
            user_id=user_id,
            base_outfit_generation_func=lambda: generate_outfit_logic(req, user_id),
            generation_context=generation_context,
            user_wardrobe=req.wardrobe
        )
        
        # Convert to standard outfit response format
        if personalized_result.outfits:
            # Use the first personalized outfit as the main result
            main_outfit = personalized_result.outfits[0]
            
            # Create outfit response
            outfit_response = {
                "id": main_outfit.get("id", f"lightweight_{int(time.time())}"),
                "name": main_outfit.get("name", "Lightweight Personalized Outfit"),
                "items": main_outfit.get("items", []),
                "style": req.style,
                "occasion": req.occasion,
                "mood": req.mood,
                "weather": req.weather.dict() if req.weather else {},
                "confidence": personalized_result.confidence,
                "metadata": {
                    **main_outfit.get("metadata", {}),
                    "personalization_applied": personalized_result.personalization_applied,
                    "strategy_used": personalized_result.strategy_used,
                    "personalization_score": personalized_result.personalization_score,
                    "generation_time": time.time() - start_time,
                    "total_personalized_outfits": len(personalized_result.outfits),
                    "lightweight_embeddings": True
                }
            }
            
            logger.info(f"✅ Generated lightweight personalized outfit using {personalized_result.strategy_used} strategy")
            return OutfitResponse(**outfit_response)
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate lightweight personalized outfit"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lightweight personalized outfit generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lightweight personalized outfit generation failed: {str(e)}"
        )

@router.post("/interaction")
async def record_lightweight_interaction(
    interaction: InteractionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Record user interaction with an outfit or item for learning.
    
    This endpoint captures user behavior to improve recommendations:
    - Outfit/item views, likes, wears, dislikes
    - Rating information
    - Timestamp and context
    """
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Validate interaction
        if not interaction.outfit_id and not interaction.item_id:
            raise HTTPException(
                status_code=400, 
                detail="Either outfit_id or item_id must be provided"
            )
        
        if interaction.interaction_type not in ["view", "like", "wear", "dislike"]:
            raise HTTPException(
                status_code=400,
                detail="interaction_type must be one of: view, like, wear, dislike"
            )
        
        # Record interaction
        if interaction.outfit_id:
            success = await lightweight_service.record_outfit_interaction(
                user_id=user_id,
                outfit_id=interaction.outfit_id,
                interaction_type=interaction.interaction_type,
                rating=interaction.rating
            )
        else:
            success = await lightweight_service.record_item_interaction(
                user_id=user_id,
                item_id=interaction.item_id,
                interaction_type=interaction.interaction_type,
                rating=interaction.rating
            )
        
        if success:
            return {
                "success": True,
                "message": f"Recorded {interaction.interaction_type} interaction",
                "user_id": user_id,
                "timestamp": time.time(),
                "lightweight_embeddings": True
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to record interaction"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record interaction: {str(e)}"
        )

@router.get("/personalization-status", response_model=PersonalizationStatusResponse)
async def get_lightweight_personalization_status(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get personalization status and analytics for the current user.
    
    Returns information about:
    - User embedding status
    - Interaction history
    - Recommendation strategy
    - Personalization parameters
    """
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Get personalization status
        status = lightweight_service.get_personalization_status(user_id)
        
        return PersonalizationStatusResponse(**status)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get personalization status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization status: {str(e)}"
        )

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_lightweight_recommendation_analytics(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get overall recommendation system analytics.
    
    Returns system-wide statistics about:
    - Embedding service performance
    - User engagement metrics
    - Recommendation parameters
    - System health
    """
    try:
        # Validate user (admin only in production)
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get system analytics
        analytics = lightweight_service.get_system_analytics()
        
        return AnalyticsResponse(**analytics)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.post("/update-personalization-settings")
async def update_lightweight_personalization_settings(
    settings: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update personalization settings (admin only).
    
    Allows updating:
    - Personalization enable/disable
    - Recommendation parameters
    - Learning rates
    - Exploration rates
    """
    try:
        # Validate user (admin only in production)
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Update settings
        lightweight_service.update_personalization_settings(**settings)
        
        return {
            "success": True,
            "message": "Lightweight personalization settings updated",
            "updated_settings": settings,
            "lightweight_embeddings": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update settings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update settings: {str(e)}"
        )

@router.get("/health")
async def lightweight_embeddings_health_check():
    """Health check for the lightweight embeddings system"""
    try:
        analytics = lightweight_service.get_system_analytics()
        
        return {
            "status": "healthy",
            "personalization_enabled": analytics["personalization_enabled"],
            "total_users": analytics["embedding_service"]["total_users"],
            "total_interactions": analytics["embedding_service"]["total_interactions"],
            "lightweight_embeddings": True,
            "no_external_dependencies": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Lightweight embeddings health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "lightweight_embeddings": True,
            "timestamp": time.time()
        }
