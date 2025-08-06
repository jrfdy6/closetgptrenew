from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

@router.get("/")
async def get_wardrobe_items() -> Dict[str, Any]:
    """Get user's wardrobe items - minimal version"""
    try:
        print("DEBUG: Getting wardrobe items (minimal)")
        
        # Return a simple response for now
        return {
            "success": True,
            "items": [],
            "count": 0,
            "message": "Wardrobe endpoint is working (minimal version)",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"DEBUG: Error in minimal wardrobe endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving wardrobe items: {str(e)}"
        )

@router.post("/")
async def add_wardrobe_item(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add item to wardrobe - minimal version"""
    try:
        print(f"DEBUG: Adding wardrobe item (minimal)")
        
        return {
            "success": True,
            "message": "Item added successfully (minimal version)",
            "item_id": "test-id",
            "item": item_data
        }
    except Exception as e:
        print(f"DEBUG: Error adding wardrobe item (minimal): {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add item"
        )

@router.get("/test")
async def test_wardrobe_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify router is working"""
    return {
        "message": "Wardrobe minimal router is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    } 