"""
Admin endpoint to initialize wardrobe counts for existing users.
Temporary endpoint - can be removed after migration is complete.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..custom_types.profile import UserProfile
from ..auth.auth_service import get_current_user
from ..config.firebase import db, firebase_initialized

router = APIRouter(tags=["wardrobe-admin"])
logger = logging.getLogger(__name__)


@router.post("/initialize-my-wardrobe-count")
async def initialize_my_wardrobe_count(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Initialize wardrobeItemCount for the current user.
    Counts their actual wardrobe items and sets the cached count.
    """
    try:
        if not firebase_initialized:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        user_id = current_user.id
        logger.info(f"🔧 Initializing wardrobeItemCount for user: {user_id}")
        
        # Count their wardrobe items
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        items = list(wardrobe_ref.stream())
        item_count = len(items)
        
        logger.info(f"📦 Found {item_count} items for user {user_id}")
        
        # Update the user profile with the count
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'wardrobeItemCount': item_count
        })
        
        logger.info(f"✅ Set wardrobeItemCount to {item_count} for user {user_id}")
        
        return {
            "success": True,
            "message": f"Initialized wardrobeItemCount to {item_count}",
            "userId": user_id,
            "wardrobeItemCount": item_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing wardrobe count: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize wardrobe count: {str(e)}"
        )
