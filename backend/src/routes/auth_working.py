"""
Working authentication routes for ClosetGPT.
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
        
        # Return the full user profile data instead of just basic fields
        # This includes measurements, style preferences, and all other profile data
        return user_data
        
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
        logger.info(f"🔍 DEBUG: Profile data received: {profile_data}")
        
        # Check if Firebase is available
        if not firebase_initialized:
            logger.warning("Firebase not available, cannot update profile")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase service not available"
            )
        
        user_ref = db.collection('users').document(current_user.id)
        
        # Prepare update data with all profile fields
        update_data = {
            'name': profile_data.get('name'),
            'email': profile_data.get('email'),
            'updated_at': int(time.time())  # Use timestamp like wardrobe.py
        }
        
        # Add all the detailed profile fields if they exist
        if 'gender' in profile_data:
            update_data['gender'] = profile_data['gender']
        if 'measurements' in profile_data:
            update_data['measurements'] = profile_data['measurements']
        if 'stylePreferences' in profile_data:
            update_data['stylePreferences'] = profile_data['stylePreferences']
        if 'preferences' in profile_data:
            update_data['preferences'] = profile_data['preferences']
        if 'bodyType' in profile_data:
            update_data['bodyType'] = profile_data['bodyType']
        if 'skinTone' in profile_data:
            update_data['skinTone'] = profile_data['skinTone']
        if 'fitPreference' in profile_data:
            update_data['fitPreference'] = profile_data['fitPreference']
        if 'sizePreference' in profile_data:
            update_data['sizePreference'] = profile_data['sizePreference']
        if 'colorPalette' in profile_data:
            update_data['colorPalette'] = profile_data['colorPalette']
        if 'stylePersonality' in profile_data:
            update_data['stylePersonality'] = profile_data['stylePersonality']
        if 'materialPreferences' in profile_data:
            update_data['materialPreferences'] = profile_data['materialPreferences']
        if 'fitPreferences' in profile_data:
            update_data['fitPreferences'] = profile_data['fitPreferences']
        if 'comfortLevel' in profile_data:
            update_data['comfortLevel'] = profile_data['comfortLevel']
        if 'preferredBrands' in profile_data:
            update_data['preferredBrands'] = profile_data['preferredBrands']
        if 'budget' in profile_data:
            update_data['budget'] = profile_data['budget']
        if 'avatar_url' in profile_data:
            update_data['avatar_url'] = profile_data['avatar_url']
        
        # Use set() instead of update() to create the document if it doesn't exist
        user_ref.set(update_data, merge=True)
        
        logger.info(f"User profile updated successfully: {current_user.id}")
        logger.info(f"🔍 DEBUG: Updated profile data: {update_data}")
        
        # Return the updated profile data
        return update_data
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
