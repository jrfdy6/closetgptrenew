"""
Working authentication routes for ClosetGPT.
Follows the exact pattern used by working wardrobe.py and outfits.py
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import time
# Firebase imports moved inside functions to prevent import-time crashes
# from firebase_admin import auth
# from firebase_admin import firestore
# from ..config.firebase import db, firebase_initialized
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
        
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
        except ImportError as e:
            logger.warning(f"Firebase import failed: {e}")
            return {
                "user_id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "avatar_url": None,
                "created_at": current_user.createdAt,
                "updated_at": current_user.updatedAt
            }
        
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
        logger.info(f"🔍 DEBUG: Profile data retrieved from Firestore: user_id={current_user.id}, fields_count={len(user_data.keys()) if user_data else 0}")
        
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
        logger.info(f"🔍 DEBUG: Profile data received: fields_count={len(profile_data.keys()) if profile_data else 0}, user_id={current_user.id}")
        
        # Import Firebase inside function to prevent import-time crashes
        from ..config.firebase import db, firebase_initialized
        
        # Check if Firebase is available
        if not firebase_initialized:
            logger.warning("Firebase not available, cannot update profile")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase service not available"
            )
        
        user_ref = db.collection('users').document(current_user.id)
        
        # Prepare update data with all profile fields
        frontend_updated_at = ((profile_data.get('updated_at') if profile_data else None) if profile_data else None) or profile_data.get('updatedAt')
        current_time = int(time.time())
        final_updated_at = frontend_updated_at or current_time
        
        # Also check for createdAt/created_at
        frontend_created_at = ((profile_data.get('created_at') if profile_data else None) if profile_data else None) or profile_data.get('createdAt')
        final_created_at = frontend_created_at or current_time
        
        logger.info(f"🔍 DEBUG: Timestamp handling - frontend_updated_at: {frontend_updated_at}, current_time: {current_time}, final_updated_at: {final_updated_at}")
        logger.info(f"🔍 DEBUG: Profile data keys: {list(profile_data.keys())}")
        logger.info(f"🔍 DEBUG: measurements in profile_data: {'measurements' in profile_data}, value: {profile_data.get('measurements')}")
        logger.info(f"🔍 DEBUG: stylePreferences in profile_data: {'stylePreferences' in profile_data}, value: {profile_data.get('stylePreferences')}")
        
        update_data = {
            'name': (profile_data.get('name') if profile_data else None),
            'email': (profile_data.get('email') if profile_data else None),
            'created_at': final_created_at,  # Use frontend timestamp if available
            'updated_at': final_updated_at  # Use frontend timestamp if available
        }
        
        # Add all the detailed profile fields if they exist
        if 'gender' in profile_data:
            update_data['gender'] = profile_data['gender']
        if 'measurements' in profile_data:
            update_data['measurements'] = profile_data['measurements']
            logger.info(f"✅ DEBUG: Added measurements to update_data")
        if 'stylePreferences' in profile_data:
            update_data['stylePreferences'] = profile_data['stylePreferences']
            logger.info(f"✅ DEBUG: Added stylePreferences to update_data: {profile_data['stylePreferences']}")
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
        if 'stylePersona' in profile_data:
            update_data['stylePersona'] = profile_data['stylePersona']
        if 'height' in profile_data:
            update_data['height'] = profile_data['height']
        if 'weight' in profile_data:
            update_data['weight'] = profile_data['weight']
        if 'heightFeetInches' in profile_data:
            update_data['heightFeetInches'] = profile_data['heightFeetInches']
        
        # Use set() instead of update() to create the document if it doesn't exist
        user_ref.set(update_data, merge=True)
        
        logger.info(f"✅ User profile updated successfully: {current_user.id}")
        logger.info(f"🔍 DEBUG: Updated profile data: user_id={current_user.id}, fields_updated={len(update_data.keys()) if update_data else 0}")
        logger.info(f"🔍 DEBUG: Fields in update_data: {list(update_data.keys())}")
        logger.info(f"🔍 DEBUG: Has measurements: {'measurements' in update_data}, Has stylePreferences: {'stylePreferences' in update_data}")
        
        # Return the updated profile data
        return update_data
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
