"""
Gamification API Routes
Endpoints for XP, levels, badges, and gamification state
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.gamification_service import gamification_service
from ..services.ai_fit_score_service import ai_fit_score_service
from ..services.cpw_service import cpw_service

router = APIRouter(prefix="/gamification", tags=["gamification"])
logger = logging.getLogger(__name__)


@router.post("/initialize")
async def initialize_gamification(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Initialize gamification fields for current user
    Call this once to set up gamification for existing users
    """
    try:
        from ..config.firebase import db
        
        user_ref = db.collection('users').document(current_user.id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        
        # Add gamification fields if missing
        updates = {}
        if 'xp' not in user_data:
            updates['xp'] = 0
        if 'level' not in user_data:
            updates['level'] = 1
        if 'ai_fit_score' not in user_data:
            updates['ai_fit_score'] = 0.0
        if 'badges' not in user_data:
            updates['badges'] = []
        if 'current_challenges' not in user_data:
            updates['current_challenges'] = {}
        if 'spending_ranges' not in user_data:
            updates['spending_ranges'] = {
                "annual_total": "unknown",
                "shoes": "unknown",
                "jackets": "unknown",
                "pants": "unknown",
                "tops": "unknown",
                "dresses": "unknown",
                "activewear": "unknown",
                "accessories": "unknown"
            }
        
        if updates:
            user_ref.update(updates)
            logger.info(f"✅ Initialized gamification for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Gamification initialized",
            "fields_added": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing gamification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initialize gamification")


@router.get("/profile")
async def get_gamification_profile(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's complete gamification profile
    
    Returns:
        XP, level, badges, AI Fit Score, active challenges
    """
    try:
        state = await gamification_service.get_user_gamification_state(current_user.id)
        
        if not state:
            # Try to initialize if not found
            from ..config.firebase import db
            user_ref = db.collection('users').document(current_user.id)
            user_ref.update({
                'xp': 0,
                'level': 1,
                'ai_fit_score': 0.0,
                'badges': [],
                'current_challenges': {}
            }, merge=True)
            
            # Retry getting state
            state = await gamification_service.get_user_gamification_state(current_user.id)
            
            if not state:
                raise HTTPException(status_code=404, detail="Gamification state not found")
        
        return {
            "success": True,
            "data": state.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gamification profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get gamification profile")


@router.get("/stats")
async def get_gamification_stats(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed gamification statistics
    
    Returns comprehensive dashboard data including:
    - XP and level info
    - AI Fit Score with breakdown
    - CPW average and trend
    - Active challenges
    """
    try:
        # Get level info
        level_info = gamification_service.get_level_info(current_user.xp or 0)
        
        # Get AI Fit Score explanation
        ai_fit_explanation = await ai_fit_score_service.get_score_explanation(current_user.id)
        
        # Get CPW stats
        cpw_average = await cpw_service.calculate_wardrobe_average_cpw(current_user.id)
        cpw_trend = await cpw_service.calculate_cpw_trend(current_user.id, days=30)
        
        # Get active challenges
        from ..services.challenge_service import challenge_service
        active_challenges = await challenge_service.get_active_challenges(current_user.id)
        
        return {
            "success": True,
            "data": {
                "xp": current_user.xp or 0,
                "level": level_info.dict(),
                "ai_fit_score": ai_fit_explanation,
                "cpw": {
                    "average": cpw_average,
                    "trend": cpw_trend
                },
                "badges": current_user.badges or [],
                "active_challenges": active_challenges,
                "active_challenges_count": len(active_challenges)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting gamification stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get gamification stats")


@router.post("/award-xp")
async def award_xp_manually(
    amount: int,
    reason: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manually award XP (typically called internally, not by frontend)
    
    Args:
        amount: XP amount to award
        reason: Reason for XP award
    """
    try:
        result = await gamification_service.award_xp(
            user_id=current_user.id,
            amount=amount,
            reason=reason
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error awarding XP: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to award XP")


@router.get("/badges")
async def get_user_badges(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's earned badges with details
    """
    try:
        from ..custom_types.gamification import BADGE_DEFINITIONS, BadgeType
        
        badges = current_user.badges or []
        
        badge_details = []
        for badge_id in badges:
            try:
                badge_info = BADGE_DEFINITIONS.get(BadgeType(badge_id))
                if badge_info:
                    badge_details.append(badge_info.dict())
            except:
                logger.warning(f"Badge {badge_id} not found in definitions")
        
        # Check for new badges that can be unlocked
        newly_unlocked = await gamification_service.check_badge_unlock_conditions(current_user.id)
        
        return {
            "success": True,
            "data": {
                "badges": badge_details,
                "count": len(badge_details),
                "newly_unlocked": newly_unlocked
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting badges: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get badges")


@router.get("/ai-fit-score")
async def get_ai_fit_score_details(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed AI Fit Score breakdown
    """
    try:
        explanation = await ai_fit_score_service.get_score_explanation(current_user.id)
        
        return {
            "success": True,
            "data": explanation
        }
        
    except Exception as e:
        logger.error(f"Error getting AI Fit Score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get AI Fit Score")


@router.get("/cpw-summary")
async def get_cpw_summary(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get CPW summary and trends
    """
    try:
        average_cpw = await cpw_service.calculate_wardrobe_average_cpw(current_user.id)
        trend_30d = await cpw_service.calculate_cpw_trend(current_user.id, days=30)
        trend_7d = await cpw_service.calculate_cpw_trend(current_user.id, days=7)
        
        return {
            "success": True,
            "data": {
                "average_cpw": average_cpw,
                "trend_30_days": trend_30d,
                "trend_7_days": trend_7d
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting CPW summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get CPW summary")


@router.post("/recalculate-cpw")
async def recalculate_user_cpw(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Recalculate CPW for all user's items
    """
    try:
        count = await cpw_service.recalculate_all_cpw_for_user(current_user.id)
        
        return {
            "success": True,
            "message": f"Recalculated CPW for {count} items"
        }
        
    except Exception as e:
        logger.error(f"Error recalculating CPW: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to recalculate CPW")


@router.post("/cold-start-check")
async def check_cold_start_progress(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check Cold Start Quest progress (called after item upload)
    """
    try:
        # Get wardrobe count
        from ..config.firebase import db
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', current_user.id)
        wardrobe_count = len(list(wardrobe_ref.stream()))
        
        # Check progress
        from ..services.challenge_service import challenge_service
        milestone_result = await challenge_service.check_cold_start_progress(
            user_id=current_user.id,
            wardrobe_count=wardrobe_count
        )
        
        if milestone_result:
            return {
                "success": True,
                "milestone_reached": True,
                "data": milestone_result
            }
        else:
            return {
                "success": True,
                "milestone_reached": False,
                "current_count": wardrobe_count
            }
        
    except Exception as e:
        logger.error(f"Error checking Cold Start progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check Cold Start progress")


@router.get("/gws")
async def get_global_wardrobe_score(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get Global Wardrobe Score with component breakdown
    """
    try:
        from ..services.gws_service import gws_service
        
        breakdown = await gws_service.get_gws_breakdown(current_user.id)
        
        return {
            "success": True,
            "data": breakdown
        }
        
    except Exception as e:
        logger.error(f"Error getting GWS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get GWS")


@router.get("/utilization")
async def get_wardrobe_utilization(
    days: int = 30,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get wardrobe utilization metrics
    """
    try:
        from ..services.utilization_service import utilization_service
        
        utilization = await utilization_service.calculate_utilization_percentage(
            user_id=current_user.id,
            days=days
        )
        
        return {
            "success": True,
            "data": utilization
        }
        
    except Exception as e:
        logger.error(f"Error getting utilization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get utilization")


# Export router
__all__ = ['router']

