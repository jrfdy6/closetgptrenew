"""
Challenges API Routes
Endpoints for managing and interacting with gamification challenges
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.challenge_service import challenge_service

router = APIRouter(prefix="/challenges", tags=["challenges"])
logger = logging.getLogger(__name__)


@router.get("/debug-catalog")
async def debug_challenge_catalog():
    """Debug endpoint to check CHALLENGE_CATALOG"""
    from ..custom_types.gamification import CHALLENGE_CATALOG
    
    catalog_info = []
    for cid, challenge in CHALLENGE_CATALOG.items():
        catalog_info.append({
            "id": cid,
            "title": challenge.title,
            "featured": challenge.featured,
            "cadence": challenge.cadence
        })
    
    return {
        "success": True,
        "catalog_size": len(CHALLENGE_CATALOG),
        "challenges": catalog_info
    }


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
    """Read and materialize completed history outside the request event loop."""
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(_read_challenge_history, current_user.id)


def _read_challenge_history(user_id: str) -> Dict[str, Any]:
    """
    Get user's completed challenges history
    """
    try:
        completed_ref = challenge_service.db.collection('user_challenges')\
            .document(user_id)\
            .collection('completed')
        
        history = []
        for doc in completed_ref.stream():
            challenge_data = doc.to_dict()
            if challenge_data.get('status') != 'completed':
                continue
            from ..custom_types.gamification import CHALLENGE_CATALOG
            definition = CHALLENGE_CATALOG.get(challenge_data.get('challenge_id'))
            if definition:
                challenge_data.update(title=definition.title, description=definition.description,
                                      rewards=definition.rewards, icon=definition.icon)
            challenge_data['instance_id'] = challenge_data.get('instance_id') or doc.id
            history.append(challenge_data)
        
        # Sort by completion date (most recent first)
        from ..services.wear_projection import _ms
        history.sort(key=lambda x: _ms(x.get('completed_at')), reverse=True)
        
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
            from google.cloud.firestore_v1 import FieldFilter
            candidates = list(challenge_service.db.collection("user_challenges").document(current_user.id).collection("active").where(filter=FieldFilter("challenge_id", "==", challenge_id)).stream())
            candidates = [snapshot for snapshot in candidates if snapshot.to_dict().get("status") == "in_progress"]
            if not candidates:
                raise HTTPException(status_code=404, detail="Challenge not found or not active")
            doc = max(candidates, key=lambda snapshot: str(snapshot.to_dict().get("started_at", "")))
        challenge_data = doc.to_dict()
        
        # Add challenge definition details
        from ..custom_types.gamification import CHALLENGE_CATALOG
        challenge_def = CHALLENGE_CATALOG.get(challenge_data.get("challenge_id", challenge_id))
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
            try:
                catalog.append({
                    "challenge_id": challenge_id,
                    "title": challenge_def.title,
                    "description": challenge_def.description,
                    "type": challenge_def.type.value if hasattr(challenge_def.type, 'value') else str(challenge_def.type),
                    "rewards": challenge_def.rewards if isinstance(challenge_def.rewards, dict) else {},
                    "cadence": challenge_def.cadence,
                    "featured": challenge_def.featured,
                    "icon": challenge_def.icon
                })
            except Exception as item_error:
                logger.warning(f"Error processing challenge {challenge_id}: {item_error}")
                continue
        
        return {
            "success": True,
            "data": {
                "challenges": catalog,
                "count": len(catalog)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting challenge catalog: {e}", exc_info=True)
        # Return empty catalog instead of error
        return {
            "success": True,
            "data": {
                "challenges": [],
                "count": 0
            }
        }


# Export router
__all__ = ['router']

