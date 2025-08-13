"""
Minimal authentication routes for ClosetGPT.
Just the profile endpoint with minimal dependencies.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

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
        
        # For now, just return a test user ID to test the route
        # We'll add Firebase verification later
        if token == "test":
            return "test-user-id"
        
        # Mock user ID for testing
        return "mock-user-123"
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Token processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token processing failed"
        )

@router.get("/profile")
async def get_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Getting profile for user: {current_user_id}")
        
        # Return mock profile data for testing
        profile_data = {
            "user_id": current_user_id,
            "email": "test@example.com",
            "name": "Test User",
            "avatar_url": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        logger.info(f"🔍 DEBUG: Profile data returned: {profile_data}")
        return profile_data
        
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
        
        # Return success for testing
        return {
            "user_id": current_user_id,
            "email": profile_data.get('email'),
            "name": profile_data.get('name'),
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
