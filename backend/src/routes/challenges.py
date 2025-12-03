"""
Challenges API Routes
Endpoints for managing and interacting with gamification challenges
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.challenge_service import challenge_service

router = APIRouter(prefix="/challenges", tags=["challenges"])
logger = logging.getLogger(__name__)


@router.get("/available")
async def get_available_challenges(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get challenges available to start
    
    Returns featured and always-available challenges that user hasn't started
    """
    try:
        challenges = await challenge_service.get_available_challenges(current_user.id)
        
        return {
            "success": True,
            "data": {
                "challenges": challenges,
                "count": len(challenges)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting available challenges: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get available challenges")


@router.get("/active")
async def get_active_challenges(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's currently active challenges with progress
    """
    try:
        challenges = await challenge_service.get_active_challenges(current_user.id)
        
        return {
            "success": True,
            "data": {
                "challenges": challenges,
                "count": len(challenges)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting active challenges: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get active challenges")


@router.post("/{challenge_id}/start")
async def start_challenge(
    challenge_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a new challenge for the user
    
    Args:
        challenge_id: ID of the challenge to start
    """
    try:
        result = await challenge_service.start_challenge(current_user.id, challenge_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to start challenge'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting challenge: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start challenge")


@router.get("/history")
async def get_challenge_history(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's completed challenges history
    """
    try:
        completed_ref = challenge_service.db.collection('user_challenges')\
            .document(current_user.id)\
            .collection('completed')
        
        history = []
        for doc in completed_ref.stream():
            challenge_data = doc.to_dict()
            history.append(challenge_data)
        
        # Sort by completion date (most recent first)
        history.sort(key=lambda x: x.get('completed_at', datetime.min), reverse=True)
        
        return {
            "success": True,
            "data": {
                "challenges": history,
                "count": len(history)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting challenge history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get challenge history")


@router.get("/{challenge_id}/progress")
async def get_challenge_progress(
    challenge_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed progress for a specific active challenge
    """
    try:
        active_ref = challenge_service.db.collection('user_challenges')\
            .document(current_user.id)\
            .collection('active')\
            .document(challenge_id)
        
        doc = active_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Challenge not found or not active")
        
        challenge_data = doc.to_dict()
        
        # Add challenge definition details
        from ..custom_types.gamification import CHALLENGE_CATALOG
        challenge_def = CHALLENGE_CATALOG.get(challenge_id)
        if challenge_def:
            challenge_data['title'] = challenge_def.title
            challenge_data['description'] = challenge_def.description
            challenge_data['rewards'] = challenge_def.rewards
        
        return {
            "success": True,
            "data": challenge_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting challenge progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get challenge progress")


@router.post("/expire-old")
async def expire_old_challenges(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check and expire challenges past their expiration date
    """
    try:
        expired_count = await challenge_service.expire_old_challenges(current_user.id)
        
        return {
            "success": True,
            "message": f"Expired {expired_count} challenges"
        }
        
    except Exception as e:
        logger.error(f"Error expiring challenges: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to expire challenges")


@router.get("/catalog")
async def get_challenge_catalog() -> Dict[str, Any]:
    """
    Get the complete challenge catalog (all available challenge types)
    """
    try:
        from ..custom_types.gamification import CHALLENGE_CATALOG
        
        catalog = []
        for challenge_id, challenge_def in CHALLENGE_CATALOG.items():
            catalog.append({
                "challenge_id": challenge_id,
                "title": challenge_def.title,
                "description": challenge_def.description,
                "type": challenge_def.type.value,
                "rewards": challenge_def.rewards,
                "cadence": challenge_def.cadence,
                "featured": challenge_def.featured,
                "icon": challenge_def.icon
            })
        
        return {
            "success": True,
            "data": {
                "challenges": catalog,
                "count": len(catalog)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting challenge catalog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get challenge catalog")


# Export router
__all__ = ['router']

