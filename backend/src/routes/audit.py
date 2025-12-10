"""
Wardrobe Audit API Routes
ROI-focused audit that helps users understand wardrobe utilization.
Access is gated by subscription plan (FREE/PRO/PREMIUM).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/audit", tags=["audit"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_audit_status(
    season_id: str = "current",
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the Wardrobe Audit state for the current user.
    Shows different levels of detail based on subscription plan:
    - FREE: Item counts only (no dollar values)
    - PRO: Includes WUR (Wardrobe Utilization Rate)
    - PREMIUM: Full audit including donation manifest and estimated waste
    """
    try:
        user_id = current_user.id
        logger.info(f"📊 Audit status requested for user {user_id}")
        
        try:
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit system is currently unavailable."
            )
        
        audit_state = await addiction_service.get_user_audit_state(user_id, season_id)
        
        if audit_state.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=audit_state["error"]
            )
        
        logger.info(f"✅ Audit status retrieved for user {user_id}")
        
        return {
            "success": True,
            "audit": audit_state
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit status for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit status"
        )


@router.get("/donation-manifest")
async def get_donation_manifest(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the donation manifest for PREMIUM users.
    Requires PREMIUM subscription; returns empty list for other plans.
    """
    try:
        user_id = current_user.id
        
        try:
            from ..config.firebase import db
            from ..services.addiction_service import addiction_service
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit system is currently unavailable."
            )
        
        # Check subscription
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        plan = user_data.get('subscription_plan', 'FREE')
        
        if plan != 'PREMIUM':
            return {
                "success": False,
                "error": "Donation manifest requires PREMIUM subscription",
                "plan": plan,
                "manifest": []
            }
        
        # Get worn items
        from google.cloud.firestore_v1 import FieldFilter
        outfit_history_query = db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', user_id))
        worn_item_ids = set()
        
        for doc in outfit_history_query.stream():
            entry = doc.to_dict()
            items = entry.get('items', [])
            for item in items:
                if isinstance(item, dict):
                    worn_item_ids.add(item.get('id'))
                elif isinstance(item, str):
                    worn_item_ids.add(item)
        
        # Generate manifest
        manifest = await addiction_service.generate_donation_manifest(user_id, list(worn_item_ids))
        
        logger.info(f"✅ Generated donation manifest for user {user_id}: {len(manifest)} items")
        
        return {
            "success": True,
            "plan": plan,
            "manifest": manifest,
            "count": len(manifest),
            "message": f"Found {len(manifest)} items ready for donation to reclaim closet space"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting donation manifest for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve donation manifest"
        )

