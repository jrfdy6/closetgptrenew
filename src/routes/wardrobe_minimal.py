from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from firebase_admin import firestore
import uuid
import time
from datetime import datetime

# Simplified imports to avoid dependency issues
try:
    from src.custom_types.wardrobe import ClothingItem, ClothingType, Color
    from src.custom_types.profile import UserProfile
    from src.auth.auth_service import get_current_user
except ImportError:
    # Fallback for when running as module
    try:
        from custom_types.wardrobe import ClothingItem, ClothingType, Color
        from custom_types.profile import UserProfile
        from auth.auth_service import get_current_user
    except ImportError:
        # Minimal fallback - create basic types
        from typing import TypedDict, Optional
        
        class ClothingItem(TypedDict):
            id: str
            name: str
            type: str
            color: str
            userId: str
            createdAt: int
            updatedAt: int
        
        class UserProfile(TypedDict):
            id: str
            name: str
            email: str
        
        def get_current_user():
            # Placeholder for now
            return UserProfile(id="test_user", name="Test User", email="test@example.com")

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

# Initialize Firestore conditionally
try:
    db = firestore.client()
except Exception as e:
    print(f"Warning: Could not initialize Firestore: {e}")
    db = None

@router.get("/")
async def get_wardrobe_items(current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """Get all wardrobe items for the current user."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        # Get items from Firestore
        items_ref = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = items_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            # Transform backend data to match frontend expectations
            transformed_item = {
                "id": doc.id,
                "name": item_data.get('name', 'Unknown Item'),
                "type": item_data.get('category', 'unknown'),  # Map category to type
                "color": item_data.get('color', 'unknown'),
                "imageUrl": item_data.get('image_url', '/placeholder.png'),  # Map image_url to imageUrl
                "wearCount": item_data.get('wear_count', 0),  # Map wear_count to wearCount
                "favorite": item_data.get('favorite', False),
                "style": item_data.get('style', []),
                "season": item_data.get('season', []),
                "occasion": item_data.get('occasion', []),
                "lastWorn": item_data.get('last_worn'),  # Map last_worn to lastWorn
                "userId": current_user.id,
                "createdAt": item_data.get('created_at'),  # Map created_at to createdAt
                "updatedAt": item_data.get('updated_at'),  # Map updated_at to updatedAt
            }
            items.append(transformed_item)
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "user_id": current_user.id
        }
        
    except Exception as e:
        print(f"Error getting wardrobe items: {e}")
        return {"success": False, "error": str(e)}

@router.post("/add")
async def add_wardrobe_item(
    item_data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Add a new wardrobe item for the current user."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        # Validate required fields
        required_fields = ['name', 'type', 'color']
        for field in required_fields:
            if field not in item_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create item ID
        item_id = str(uuid.uuid4())
        current_time = int(time.time())
        
        # Prepare item data for backend storage
        wardrobe_item = {
            "id": item_id,
            "userId": current_user.id,
            "name": item_data["name"],
            "category": item_data["type"],  # Map type to category
            "color": item_data["color"],
            "style": item_data.get("style", []),
            "occasion": item_data.get("occasion", []),
            "season": item_data.get("season", ["all"]),
            "image_url": item_data.get("imageUrl", ""),  # Map imageUrl to image_url
            "wear_count": item_data.get("wearCount", 0),  # Map wearCount to wear_count
            "favorite": item_data.get("favorite", False),
            "last_worn": item_data.get("lastWorn"),  # Map lastWorn to last_worn
            "created_at": current_time,
            "updated_at": current_time,
        }
        
        # Save to Firestore
        db.collection('wardrobe').document(item_id).set(wardrobe_item)
        
        return {
            "success": True,
            "message": "Item added successfully",
            "item_id": item_id,
            "item": wardrobe_item
        }
        
    except Exception as e:
        print(f"Error adding wardrobe item: {e}")
        return {"success": False, "error": str(e)}

@router.get("/{item_id}")
async def get_wardrobe_item(
    item_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific wardrobe item by ID."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        doc = db.collection('wardrobe').document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = doc.to_dict()
        if item_data.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"success": True, "item": item_data}
        
    except Exception as e:
        print(f"Error getting wardrobe item: {e}")
        return {"success": False, "error": str(e)}

@router.put("/{item_id}")
async def update_wardrobe_item(
    item_id: str,
    updates: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a wardrobe item."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        # Check if item exists and belongs to user
        doc = db.collection('wardrobe').document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = doc.to_dict()
        if item_data.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update the item
        updates['updated_at'] = int(time.time())
        db.collection('wardrobe').document(item_id).update(updates)
        
        return {"success": True, "message": "Item updated successfully"}
        
    except Exception as e:
        print(f"Error updating wardrobe item: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/{item_id}")
async def delete_wardrobe_item(
    item_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a wardrobe item."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        # Check if item exists and belongs to user
        doc = db.collection('wardrobe').document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = doc.to_dict()
        if item_data.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the item
        db.collection('wardrobe').document(item_id).delete()
        
        return {"success": True, "message": "Item deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting wardrobe item: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{item_id}/increment-wear")
async def increment_wear_count(
    item_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Increment the wear count for a wardrobe item."""
    try:
        if not db:
            return {"success": False, "error": "Database not available"}
        
        # Check if item exists and belongs to user
        doc = db.collection('wardrobe').document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = doc.to_dict()
        if item_data.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update wear count and last worn
        current_time = int(time.time())
        updates = {
            'wear_count': item_data.get('wear_count', 0) + 1,
            'last_worn': current_time,
            'updated_at': current_time
        }
        
        db.collection('wardrobe').document(item_id).update(updates)
        
        return {"success": True, "message": "Wear count incremented", "new_wear_count": updates['wear_count']}
        
    except Exception as e:
        print(f"Error incrementing wear count: {e}")
        return {"success": False, "error": str(e)} 