"""
Shuffle Route - Random outfit generation ("Dress Me" feature)
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import random
import logging

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.gamification_service import gamification_service

router = APIRouter(prefix="/shuffle", tags=["shuffle"])
logger = logging.getLogger(__name__)


@router.post("/")
async def generate_shuffle_outfit(
    occasion: Optional[str] = "casual",
    weather: Optional[Dict[str, Any]] = None,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a random outfit using existing robust outfit generation
    
    The "Dress Me" shuffle feature that provides instant outfit suggestions
    """
    try:
        logger.info(f"🎲 Generating shuffle outfit for user {current_user.id}")
        
        # Import the robust outfit generation service
        try:
            from ..services.robust_outfit_generation_service import RobustOutfitGenerationService
            generation_service = RobustOutfitGenerationService()
        except ImportError:
            # Fallback to regular outfit service
            from ..services.outfits.generation_service import OutfitGenerationService
            generation_service = OutfitGenerationService()
        
        # Prepare request with random seed for variety
        request_data = {
            "occasion": occasion or "casual",
            "random_seed": random.randint(0, 1000000),
            "num_outfits": 1
        }
        
        # Add weather if provided
        if weather:
            request_data["weather"] = weather
        
        # Generate outfit
        try:
            # Try the robust service method
            if hasattr(generation_service, 'generate_outfit'):
                outfit = await generation_service.generate_outfit(
                    user_id=current_user.id,
                    **request_data
                )
            else:
                # Use alternative method
                outfit = await generation_service.generate_personalized_outfit(
                    user_id=current_user.id,
                    occasion=occasion or "casual",
                    weather=weather
                )
        except Exception as gen_error:
            logger.error(f"Error generating outfit: {gen_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate shuffle outfit")
        
        # Award small XP for using shuffle
        xp_result = await gamification_service.award_xp(
            user_id=current_user.id,
            amount=2,
            reason="shuffle_used",
            metadata={"occasion": occasion}
        )
        
        logger.info(f"✅ Generated shuffle outfit and awarded 2 XP to user {current_user.id}")
        
        return {
            "success": True,
            "outfit": outfit,
            "xp_earned": 2,
            "level_up": xp_result.get('level_up', False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in shuffle endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Shuffle generation failed: {str(e)}")


@router.post("/quick")
async def generate_quick_shuffle(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Quick shuffle without any parameters - fastest option
    Uses current weather and casual occasion
    """
    try:
        return await generate_shuffle_outfit(
            occasion="casual",
            weather=None,
            current_user=current_user
        )
    except Exception as e:
        logger.error(f"Error in quick shuffle: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Quick shuffle failed")


# Export router
__all__ = ['router']

