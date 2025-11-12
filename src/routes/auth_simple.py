"""
Simplified authentication routes for Easy Outfit App.
Just the profile endpoint to avoid import issues.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth
import concurrent.futures

from ..config.firebase import db

# HTTP Bearer scheme for token extraction
security = HTTPBearer()

logger = logging.getLogger("auth_simple")

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from Firebase ID token."""
    try:
        logger.info("🔍 DEBUG: ===== STARTING AUTHENTICATION PROCESS =====")
        token = credentials.credentials
        logger.info(f"🔍 DEBUG: Received token length: {len(token)}")
        
        # Use a timeout for the Firebase verification
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(firebase_auth.verify_id_token, token)
            try:
                decoded_token = future.result(timeout=30.0)
                logger.info("🔍 DEBUG: Firebase verification completed successfully!")
            except concurrent.futures.TimeoutError:
                logger.error("🔍 DEBUG: Firebase token verification timed out after 30 seconds")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification timed out"
                )
        
        user_id: str = decoded_token.get("uid")
        if user_id is None:
            logger.error("🔍 DEBUG: No user_id found in decoded token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        logger.info(f"🔍 DEBUG: Token verification successful, user_id: {user_id}")
        return user_id
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

@router.get("/profile")
async def get_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Getting profile for user: {current_user_id}")
        
        user_doc = db.collection('users').document(current_user_id).get()
        
        if not user_doc.exists:
            logger.info(f"🔍 DEBUG: No profile found for user: {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        logger.info(f"🔍 DEBUG: Profile data retrieved: {user_data}")
        
        return {
            "user_id": current_user_id,
            "email": user_data.get('email'),
            "name": user_data.get('name'),
            "avatar_url": user_data.get('avatar_url'),
            "created_at": user_data.get('created_at'),
            "updated_at": user_data.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Updating profile for user: {current_user_id}")
        
        user_ref = db.collection('users').document(current_user_id)
        
        update_data = {
            'name': profile_data.get('name'),
            'email': profile_data.get('email'),
            'updated_at': firebase_admin.firestore.SERVER_TIMESTAMP
        }
        
        user_ref.update(update_data)
        
        logger.info(f"User profile updated successfully: {current_user_id}")
        
        return {
            "user_id": current_user_id,
            "email": profile_data.get('email'),
            "name": profile_data.get('name'),
            "updated_at": "now"
        }
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
