#!/usr/bin/env python3
"""
Simple Personalized Outfits Routes
==================================

This module adds simple personalization to your existing outfit generation
without replacing your current system.

New Endpoints:
- POST /api/outfits-simple/generate-personalized - Generate outfits with personalization
- POST /api/outfits-simple/interaction - Record user interactions
- GET /api/outfits-simple/personalization-status - Get personalization status
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Import services
from ..services.simple_personalization_integration import SimplePersonalizationIntegration, PersonalizedOutfitResult
from ..services.lightweight_embedding_service import UserInteraction

# Import types (with error handling)
try:
    from ..custom_types.outfit_rules import OutfitRequest, OutfitResponse
except ImportError as e:
    print(f"Failed to import outfit types: {e}")
    # Define minimal types for fallback
    class OutfitRequest:
        pass
    class OutfitResponse:
        pass

# Import auth (with error handling)
try:
    from ..auth.auth_service import get_current_user_id
except ImportError as e:
    print(f"Failed to import auth service: {e}")
    def get_current_user_id():
        return "test-user"

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize simple personalization service (with error handling)
try:
    personalization_service = SimplePersonalizationIntegration()
    logger.info("✅ Simple personalization service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize simple personalization service: {e}")
    # Create a minimal fallback service
    class FallbackPersonalizationService:
        def __init__(self):
            self.enable_personalization = False
        async def generate_outfit_with_personalization(self, *args, **kwargs):
            return PersonalizedOutfitResult(outfits=[], personalization_applied=False, confidence=0.0, metadata={"error": "Service unavailable"})
        async def record_user_interaction(self, *args, **kwargs):
            return False
        def get_personalization_status(self, user_id):
            return {"user_id": user_id, "personalization_enabled": False, "error": "Service unavailable"}
    
    personalization_service = FallbackPersonalizationService()
    logger.warning("⚠️ Using fallback personalization service")

# Pydantic models
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
    min_interactions_required: int
    ready_for_personalization: bool
    system_parameters: Dict[str, Any]

@router.post("/generate-personalized", response_model=OutfitResponse)
async def generate_simple_personalized_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate outfit using your existing system + add simple personalization.
    
    This endpoint:
    1. Uses your existing outfit generation (keeps all your validation)
    2. Adds personalization layer on top (if user has enough interactions)
    3. Falls back to existing system if personalization fails
    4. No external dependencies required
    """
    start_time = time.time()
    
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        logger.info(f"🎯 Generating simple personalized outfit for user {user_id}")
        
        # Create generation context
        generation_context = {
            "occasion": req.occasion,
            "style": req.style,
            "mood": req.mood,
            "weather": req.weather.dict() if req.weather else {},
            "user_profile": {"id": user_id, "name": "User"},
            "base_item_id": req.baseItemId
        }
        
        # Import your existing outfit generation function
        from .outfits import generate_outfit_logic
        
        # Create a wrapper function for your existing outfit generation
        async def existing_outfit_generation():
            return await generate_outfit_logic(req, user_id)
        
        # Generate outfit with personalization
        personalized_result = await personalization_service.generate_outfit_with_personalization(
            user_id=user_id,
            existing_outfit_generation_func=existing_outfit_generation,
            generation_context=generation_context,
            user_wardrobe=req.wardrobe
        )
        
        # Convert to standard outfit response format
        if personalized_result.outfits:
            # Use the first outfit as the main result
            main_outfit = personalized_result.outfits[0]
            
            # Create outfit response
            outfit_response = {
                "id": main_outfit.get("id", f"simple_personalized_{int(time.time())}"),
                "name": main_outfit.get("name", "Simple Personalized Outfit"),
                "items": main_outfit.get("items", []),
                "style": req.style,
                "occasion": req.occasion,
                "mood": req.mood,
                "weather": req.weather.dict() if req.weather else {},
                "confidence": personalized_result.confidence,
                "metadata": {
                    **main_outfit.get("metadata", {}),
                    "personalization_applied": personalized_result.personalization_applied,
                    "generation_time": time.time() - start_time,
                    "total_outfits_generated": len(personalized_result.outfits),
                    "simple_personalization": True,
                    "existing_system_used": True,
                    **personalized_result.metadata
                }
            }
            
            logger.info(f"✅ Generated simple personalized outfit (personalization: {personalized_result.personalization_applied})")
            return OutfitResponse(**outfit_response)
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate simple personalized outfit"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Simple personalized outfit generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Simple personalized outfit generation failed: {str(e)}"
        )

@router.post("/interaction")
async def record_simple_interaction(
    interaction: InteractionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Record user interaction for learning.
    
    This endpoint captures user behavior to improve recommendations:
    - Outfit/item views, likes, wears, dislikes
    - Rating information
    - Used for personalization learning
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
        success = await personalization_service.record_user_interaction(
            user_id=user_id,
            outfit_id=interaction.outfit_id,
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
                "simple_personalization": True
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
async def get_simple_personalization_status(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get personalization status for the current user.
    
    Returns information about:
    - Whether personalization is enabled
    - How many interactions the user has
    - Whether they're ready for personalization
    - System parameters
    """
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Get personalization status
        status = personalization_service.get_personalization_status(user_id)
        
        return PersonalizationStatusResponse(**status)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get personalization status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization status: {str(e)}"
        )

@router.get("/health")
async def simple_personalization_health_check():
    """Health check for the simple personalization system"""
    try:
        return {
            "status": "healthy",
            "personalization_enabled": personalization_service.enable_personalization,
            "min_interactions_required": personalization_service.min_interactions_for_personalization,
            "max_outfits": personalization_service.max_personalized_outfits,
            "simple_personalization": True,
            "no_external_dependencies": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Simple personalization health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "simple_personalization": True,
            "timestamp": time.time()
        }
