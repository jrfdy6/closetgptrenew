"""
Minimal wardrobe router for testing - no complex imports
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile

router = APIRouter(tags=["wardrobe-simple"])

@router.get("/")
async def get_wardrobe_items_simple(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Simple wardrobe items endpoint for testing."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return {
            "success": True,
            "items": [],
            "count": 0,
            "user_id": current_user.id,
            "message": "Simple wardrobe endpoint working"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/test")
async def test_wardrobe_simple() -> Dict[str, Any]:
    """Test endpoint that doesn't require authentication."""
    return {
        "success": True,
        "message": "Simple wardrobe router is working",
        "timestamp": "2024-01-01T00:00:00Z"
    }
