"""
Simple outfit history router for testing - minimal imports
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/outfit-history", tags=["outfit-history-simple"])

@router.get("/today")
async def get_todays_outfit_simple(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Simple today's outfit endpoint for testing."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return {
            "success": True,
            "todaysOutfit": None,
            "hasOutfitToday": False,
            "message": "Simple today's outfit endpoint working - no outfit worn today"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/")
async def get_outfit_history_simple(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Simple outfit history endpoint for testing."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return {
            "success": True,
            "data": [],
            "count": 0,
            "user_id": current_user.id,
            "message": "Simple outfit history endpoint working"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/test")
async def test_outfit_history_simple() -> Dict[str, Any]:
    """Test endpoint that doesn't require authentication."""
    return {
        "success": True,
        "message": "Simple outfit history router is working",
        "timestamp": "2024-01-01T00:00:00Z"
    }
