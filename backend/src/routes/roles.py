"""
Internal Status / Roles API
Handles user status, perk visibility, and progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..custom_types.gamification import UserRole

router = APIRouter(prefix="/roles", tags=["roles"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_user_status(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current user status, active perks, and progress to next tier"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Roles system is currently unavailable."
            )
        
        addiction_state = await addiction_service.get_user_addiction_state(user_id)
        role_data = addiction_state.get('role', {})
        current_role_str = role_data.get('current_role', 'lurker')
        
        try:
            current_role = UserRole(current_role_str)
        except:
            current_role = UserRole.LURKER
        
        role_meta = {
            "lurker": {
                "title": "Closet Lurker",
                "icon": "👀",
                "color": "gray",
                "perks_desc": ["Basic App Access"]
            },
            "scout": {
                "title": "Style Scout",
                "icon": "🧭",
                "color": "blue",
                "perks_desc": ["1.2x Token Earnings", "+5% Gacha Luck"]
            },
            "trendsetter": {
                "title": "Trendsetter",
                "icon": "👑",
                "color": "gold",
                "perks_desc": ["1.5x Token Earnings", "Exclusive Gacha Pool", "Priority AI"]
            }
        }
        
        promotion_check = await addiction_service.check_for_promotion(user_id)
        
        return {
            "current_role": {
                "id": current_role.value,
                **role_meta.get(current_role.value, {})
            },
            "active_privileges": role_data.get('privileges', {}),
            "next_tier_progress": promotion_check.get('progress', None),
            "maintenance_status": role_data.get('role_decay_checks_remaining', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user status for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user status"
        )


@router.post("/check-promotion")
async def check_promotion(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Manually trigger a promotion check"""
    try:
        user_id = current_user.id
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Roles system is currently unavailable."
            )
        
        result = await addiction_service.check_for_promotion(user_id)
        
        return {
            "success": True,
            "promotion_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking promotion for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check promotion"
        )

