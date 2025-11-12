"""
Working authentication routes for Easy Outfit App.
Follows the exact pattern used by working wardrobe.py and outfits.py
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import time
from firebase_admin import auth
from firebase_admin import firestore

# Use the same import pattern as working routers
from ..config.firebase import db, firebase_initialized
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

# HTTP Bearer scheme for token extraction
security = HTTPBearer()

logger = logging.getLogger("auth_working")

router = APIRouter(tags=["authentication"])

@router.get("/profile")
async def get_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Getting profile for user: {current_user.id}")
        
        # Check if Firebase is available (same pattern as outfits.py)
        if not firebase_initialized:
            logger.warning("Firebase not available, returning user profile from token")
            return {
                "user_id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "avatar_url": None,
                "created_at": current_user.createdAt,
                "updated_at": current_user.updatedAt
            }
        
        # Query Firestore for real user data (same pattern as wardrobe.py)
        user_doc = db.collection('users').document(current_user.id).get()
        
        if not user_doc.exists:
            logger.info(f"🔍 DEBUG: No Firestore profile found for user: {current_user.id}")
            # Return profile from token data (same fallback as outfits.py)
            return {
                "user_id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "avatar_url": None,
                "created_at": current_user.createdAt,
                "updated_at": current_user.updatedAt
            }
        
        user_data = user_doc.to_dict()
        logger.info(f"🔍 DEBUG: Profile data retrieved from Firestore: {user_data}")
        
        return {
            "user_id": current_user.id,
            "email": user_data.get('email', current_user.email),
            "name": user_data.get('name', current_user.name),
            "avatar_url": user_data.get('avatar_url'),
            "created_at": user_data.get('created_at', current_user.createdAt),
            "updated_at": user_data.get('updated_at', current_user.updatedAt)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Updating profile for user: {current_user.id}")
        
        # Check if Firebase is available
        if not firebase_initialized:
            logger.warning("Firebase not available, cannot update profile")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase service not available"
            )
        
        user_ref = db.collection('users').document(current_user.id)
        
        update_data = {
            'name': profile_data.get('name'),
            'email': profile_data.get('email'),
            'updated_at': int(time.time())  # Use timestamp like wardrobe.py
        }
        
        user_ref.update(update_data)
        
        logger.info(f"User profile updated successfully: {current_user.id}")
        
        return {
            "user_id": current_user.id,
            "email": profile_data.get('email'),
            "name": profile_data.get('name'),
            "updated_at": update_data['updated_at']
        }
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
