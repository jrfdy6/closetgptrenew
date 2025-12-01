"""
Data Privacy Controls Routes
Handles user data privacy settings and controls
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from ..auth.auth_service import get_current_user_id
from ..config.firebase import db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["data-privacy"])


class PrivacySettings(BaseModel):
    share_analytics: bool = False
    share_style_data: bool = False
    allow_data_collection: bool = True
    allow_personalization: bool = True
    data_retention_days: Optional[int] = None  # None = default retention


@router.get("/privacy-settings")
async def get_privacy_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get user's privacy settings"""
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict() or {}
            privacy = user_data.get('privacy', {})
            
            return {
                'share_analytics': privacy.get('share_analytics', False),
                'share_style_data': privacy.get('share_style_data', False),
                'allow_data_collection': privacy.get('allow_data_collection', True),
                'allow_personalization': privacy.get('allow_personalization', True),
                'data_retention_days': privacy.get('data_retention_days'),
                'last_updated': privacy.get('last_updated')
            }
        else:
            # Return defaults
            return {
                'share_analytics': False,
                'share_style_data': False,
                'allow_data_collection': True,
                'allow_personalization': True,
                'data_retention_days': None,
                'last_updated': None
            }
    except Exception as e:
        logger.error(f"Error fetching privacy settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch privacy settings: {str(e)}")


@router.post("/privacy-settings")
async def update_privacy_settings(
    settings: PrivacySettings,
    user_id: str = Depends(get_current_user_id)
):
    """Update user's privacy settings"""
    try:
        from datetime import datetime, timezone
        
        user_ref = db.collection('users').document(user_id)
        
        privacy_data = {
            'share_analytics': settings.share_analytics,
            'share_style_data': settings.share_style_data,
            'allow_data_collection': settings.allow_data_collection,
            'allow_personalization': settings.allow_personalization,
            'data_retention_days': settings.data_retention_days,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        user_ref.set({
            'privacy': privacy_data
        }, merge=True)
        
        logger.info(f"Updated privacy settings for user {user_id}")
        
        return {
            'success': True,
            'message': 'Privacy settings updated successfully',
            'settings': privacy_data
        }
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update privacy settings: {str(e)}")


@router.delete("/privacy-data")
async def delete_user_data(
    data_type: Optional[str] = None,  # 'all', 'outfits', 'wardrobe', 'analytics'
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete user data based on privacy settings.
    
    data_type: 'all' deletes everything, specific types delete only that data
    """
    try:
        from datetime import datetime, timezone
        
        deleted = []
        
        if data_type is None or data_type == 'all':
            # Delete outfit history
            outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
            outfit_count = 0
            for doc in outfits_ref.stream():
                doc.reference.delete()
                outfit_count += 1
            deleted.append(f'{outfit_count} outfit history entries')
            
            # Delete wardrobe items
            wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
            wardrobe_count = 0
            for doc in wardrobe_ref.stream():
                doc.reference.delete()
                wardrobe_count += 1
            deleted.append(f'{wardrobe_count} wardrobe items')
            
            # Delete analytics data
            analytics_ref = db.collection('user_analytics').where('user_id', '==', user_id)
            analytics_count = 0
            for doc in analytics_ref.stream():
                doc.reference.delete()
                analytics_count += 1
            deleted.append(f'{analytics_count} analytics entries')
            
        elif data_type == 'outfits':
            outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
            outfit_count = 0
            for doc in outfits_ref.stream():
                doc.reference.delete()
                outfit_count += 1
            deleted.append(f'{outfit_count} outfit history entries')
            
        elif data_type == 'wardrobe':
            wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
            wardrobe_count = 0
            for doc in wardrobe_ref.stream():
                doc.reference.delete()
                wardrobe_count += 1
            deleted.append(f'{wardrobe_count} wardrobe items')
            
        elif data_type == 'analytics':
            analytics_ref = db.collection('user_analytics').where('user_id', '==', user_id)
            analytics_count = 0
            for doc in analytics_ref.stream():
                doc.reference.delete()
                analytics_count += 1
            deleted.append(f'{analytics_count} analytics entries')
        
        logger.info(f"Deleted data for user {user_id}: {', '.join(deleted)}")
        
        return {
            'success': True,
            'message': 'Data deleted successfully',
            'deleted': deleted
        }
    except Exception as e:
        logger.error(f"Error deleting user data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")


@router.get("/privacy-summary")
async def get_privacy_summary(
    user_id: str = Depends(get_current_user_id)
):
    """Get summary of user's data and privacy status"""
    try:
        # Count user's data
        outfits_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        outfit_count = sum(1 for _ in outfits_ref.stream())
        
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        wardrobe_count = sum(1 for _ in wardrobe_ref.stream())
        
        analytics_ref = db.collection('user_analytics').where('user_id', '==', user_id)
        analytics_count = sum(1 for _ in analytics_ref.stream())
        
        # Get privacy settings
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        privacy = {}
        if user_doc.exists:
            user_data = user_doc.to_dict() or {}
            privacy = user_data.get('privacy', {})
        
        return {
            'data_summary': {
                'outfits': outfit_count,
                'wardrobe_items': wardrobe_count,
                'analytics_entries': analytics_count,
                'total': outfit_count + wardrobe_count + analytics_count
            },
            'privacy_settings': {
                'share_analytics': privacy.get('share_analytics', False),
                'share_style_data': privacy.get('share_style_data', False),
                'allow_data_collection': privacy.get('allow_data_collection', True),
                'allow_personalization': privacy.get('allow_personalization', True)
            },
            'data_retention': privacy.get('data_retention_days'),
            'last_updated': privacy.get('last_updated')
        }
    except Exception as e:
        logger.error(f"Error fetching privacy summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch privacy summary: {str(e)}")

