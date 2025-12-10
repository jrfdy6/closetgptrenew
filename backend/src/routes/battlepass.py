"""
Battle Pass API Routes
Handles seasonal progression and rewards
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/battlepass", tags=["battlepass"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_battle_pass_status(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's current Battle Pass level, XP progress, and unlocked rewards"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Battle Pass system is currently unavailable."
            )
        
        bp_state = await addiction_service.get_user_battle_pass_state(user_id)
        
        if bp_state.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=bp_state["error"]
            )
        
        return {
            "success": True,
            "season_id": bp_state.get("season_id", "S1_ECO_ENGINEERING"),
            "current_level": bp_state.get("current_level", 1),
            "current_xp": bp_state.get("current_xp", 0),
            "premium_unlocked": bp_state.get("premium_unlocked", False),
            "claimed_rewards": bp_state.get("claimed_rewards", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting battle pass status for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve battle pass status"
        )


@router.post("/claim")
async def claim_battle_pass_reward(
    reward_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Claim a battle pass reward"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Battle Pass system is currently unavailable."
            )
        
        result = await addiction_service.claim_battle_pass_reward(user_id, reward_id)
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "reward_id": reward_id,
            "reward_data": result.get("reward_data", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming battle pass reward for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to claim battle pass reward"
        )


@router.post("/unlock-premium")
async def unlock_premium_battle_pass(
    method: str = "streak",
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Unlock Premium Battle Pass via 30-day streak or purchase"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Battle Pass system is currently unavailable."
            )
        
        result = await addiction_service.unlock_premium_battle_pass(user_id, method=method)
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "method": method,
            "premium_unlocked": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking premium battle pass for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock premium battle pass"
        )

