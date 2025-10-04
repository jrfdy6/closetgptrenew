"""
Minimal authentication routes for ClosetGPT.
Just the profile endpoint with Firebase authentication.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth
import concurrent.futures
import datetime

from ..config.firebase import db
from ..custom_types.profile import UserProfile

# HTTP Bearer scheme for token extraction
security = HTTPBearer()

logger = logging.getLogger("auth_minimal")

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from Firebase ID token."""
    try:
        logger.info("🔍 DEBUG: ===== STARTING AUTHENTICATION PROCESS =====")
        token = credentials.credentials
        logger.info(f"🔍 DEBUG: Received token length: {len(token)}")
        
        # Handle test token for development
        if token == "test":
            logger.info("🔍 DEBUG: Using test token")
            return "test-user-id"
        
        # Verify Firebase JWT token
        logger.info("🔍 DEBUG: Verifying Firebase token...")
        
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
        
        user_id: str = (decoded_token.get("uid") if decoded_token else None)
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current user as UserProfile object for compatibility with existing routes."""
    try:
        logger.info("🔍 DEBUG: ===== STARTING get_current_user PROCESS =====")
        token = credentials.credentials
        logger.info(f"🔍 DEBUG: Received token length: {len(token)}")
        
        # Handle test token for development
        if token == "test":
            logger.info("🔍 DEBUG: Using test token for get_current_user")
            return UserProfile(
                id="test-user-id",
                name="Test User",
                email="test@example.com",
                gender=None,
                bodyType="average",
                createdAt=int(datetime.datetime.now().timestamp() * 1000),
                updatedAt=int(datetime.datetime.now().timestamp() * 1000)
            )
        
        # Verify Firebase JWT token
        logger.info("🔍 DEBUG: Verifying Firebase token for get_current_user...")
        
        # Use a timeout for the Firebase verification
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(firebase_auth.verify_id_token, token)
            try:
                decoded_token = future.result(timeout=30.0)
                logger.info("🔍 DEBUG: Firebase verification completed successfully for get_current_user!")
            except concurrent.futures.TimeoutError:
                logger.error("🔍 DEBUG: Firebase token verification timed out after 30 seconds")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification timed out"
                )
        
        user_id: str = (decoded_token.get("uid") if decoded_token else None)
        email: str = (decoded_token.get("email", "") if decoded_token else "")
        name: str = (decoded_token.get("name", email) if decoded_token else email)
        
        if user_id is None:
            logger.error("🔍 DEBUG: No user_id found in decoded token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        logger.info(f"🔍 DEBUG: Token verification successful for get_current_user, user_id: {user_id}")
        
        # Create UserProfile object
        return UserProfile(
            id=user_id,
            name=name,
            email=email,
            gender=None,
            bodyType="average",
            createdAt=int(datetime.datetime.now().timestamp() * 1000),
            updatedAt=int(datetime.datetime.now().timestamp() * 1000)
        )
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Firebase token verification failed in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

@router.get("/profile")
async def get_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Getting profile for user: {current_user_id}")
        
        # Query Firestore for real user data
        user_doc = db.collection('users').document(current_user_id).get()
        
        if not user_doc.exists:
            logger.info(f"🔍 DEBUG: No profile found for user: {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        logger.info(f"🔍 DEBUG: Profile data retrieved from Firestore: {user_data}")
        
        return {
            "user_id": current_user_id,
            "email": (user_data.get('email') if user_data else None),
            "name": (user_data.get('name') if user_data else None),
            "avatar_url": (user_data.get('avatar_url') if user_data else None),
            "created_at": (user_data.get('created_at') if user_data else None),
            "updated_at": (user_data.get('updated_at') if user_data else None)
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
            'name': (profile_data.get('name') if profile_data else None),
            'email': (profile_data.get('email') if profile_data else None),
            'updated_at': firebase_admin.firestore.SERVER_TIMESTAMP
        }
        
        user_ref.update(update_data)
        
        logger.info(f"User profile updated successfully: {current_user_id}")
        
        return {
            "user_id": current_user_id,
            "email": (profile_data.get('email') if profile_data else None),
            "name": (profile_data.get('name') if profile_data else None),
            "updated_at": "now"
        }
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
