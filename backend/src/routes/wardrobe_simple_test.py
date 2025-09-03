"""
Minimal wardrobe router for testing - no complex imports
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from firebase_admin import firestore
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe-simple"])

# Initialize Firestore
try:
    db = firestore.client()
except Exception as e:
    print(f"Warning: Could not initialize Firestore: {e}")
    db = None

@router.get("/")
async def get_wardrobe_items_simple(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Simple wardrobe items endpoint that actually fetches real data."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Query Firestore for user's wardrobe items
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "user_id": current_user.id,
            "message": f"Retrieved {len(items)} wardrobe items"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/wardrobe-stats")
async def get_wardrobe_stats_simple(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Simple wardrobe stats endpoint for dashboard."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Query Firestore for user's wardrobe items
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
        items = []
        categories = {}
        colors = {}
        
        for doc in docs:
            item_data = doc.to_dict()
            items.append(item_data)
            
            # Count by category
            item_type = item_data.get('type', 'unknown')
            categories[item_type] = categories.get(item_type, 0) + 1
            
            # Count by color
            item_color = item_data.get('color', 'unknown')
            colors[item_color] = colors.get(item_color, 0) + 1
        
        stats = {
            "total_items": len(items),
            "categories": categories,
            "colors": colors,
            "user_id": current_user.id
        }
        
        return {
            "success": True,
            "data": stats,
            "message": f"Wardrobe statistics retrieved successfully ({len(items)} items found)"
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
