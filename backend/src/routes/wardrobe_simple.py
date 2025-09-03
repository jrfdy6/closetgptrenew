from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from firebase_admin import firestore
import uuid
import time
from datetime import datetime

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

# Initialize Firestore conditionally
try:
    db = firestore.client()
    print("DEBUG: Firebase client initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize Firebase client: {e}")
    db = None

# Simple mock user for testing
class MockUser:
    def __init__(self, user_id: str):
        self.id = user_id

def get_current_user_mock():
    """Mock authentication for testing"""
    return MockUser("test-user-id")

@router.get("/test")
async def test_wardrobe_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify router is working"""
    return {
        "message": "Wardrobe router is working!",
        "timestamp": datetime.now().isoformat(),
        "firebase_available": db is not None
    }

@router.get("/")
async def get_wardrobe_items() -> Dict[str, Any]:
    """Get user's wardrobe items - simplified version"""
    try:
        print("DEBUG: Getting wardrobe items (simplified)")
        
        # Get wardrobe items from Firestore using flat collection structure
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.where('userId', '==', 'test-user-id').stream()
        
        items = []
        errors = []
        
        for doc in docs:
            try:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                
                # Ensure required fields exist
                if 'name' not in item_data:
                    item_data['name'] = 'Unknown Item'
                if 'type' not in item_data:
                    item_data['type'] = 'unknown'
                if 'color' not in item_data:
                    item_data['color'] = 'unknown'
                if 'style' not in item_data:
                    item_data['style'] = []
                if 'occasion' not in item_data:
                    item_data['occasion'] = []
                if 'season' not in item_data:
                    item_data['season'] = ['all']
                if 'tags' not in item_data:
                    item_data['tags'] = []
                if 'dominantColors' not in item_data:
                    item_data['dominantColors'] = []
                if 'matchingColors' not in item_data:
                    item_data['matchingColors'] = []
                if 'imageUrl' not in item_data:
                    item_data['imageUrl'] = ''
                if 'metadata' not in item_data:
                    item_data['metadata'] = {}
                if 'favorite' not in item_data:
                    item_data['favorite'] = False
                if 'wearCount' not in item_data:
                    item_data['wearCount'] = 0
                if 'lastWorn' not in item_data:
                    item_data['lastWorn'] = None
                
                # Handle timestamp conversion
                try:
                    if 'createdAt' in item_data:
                        if isinstance(item_data['createdAt'], str):
                            item_data['createdAt'] = int(datetime.fromisoformat(item_data['createdAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['createdAt'], 'timestamp'):
                            item_data['createdAt'] = int(item_data['createdAt'].timestamp())
                    else:
                        item_data['createdAt'] = int(datetime.now().timestamp())
                except Exception as e:
                    print(f"DEBUG: Error converting createdAt for item {doc.id}: {e}")
                    item_data['createdAt'] = int(datetime.now().timestamp())
                
                try:
                    if 'updatedAt' in item_data:
                        if isinstance(item_data['updatedAt'], str):
                            item_data['updatedAt'] = int(datetime.fromisoformat(item_data['updatedAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['updatedAt'], 'timestamp'):
                            item_data['updatedAt'] = int(item_data['updatedAt'].timestamp())
                    else:
                        item_data['updatedAt'] = int(datetime.now().timestamp())
                except Exception as e:
                    print(f"DEBUG: Error converting updatedAt for item {doc.id}: {e}")
                    item_data['updatedAt'] = int(datetime.now().timestamp())
                
                items.append(item_data)
                print(f"DEBUG: Successfully processed item {doc.id}")
                
            except Exception as e:
                print(f"DEBUG: Error processing wardrobe item {doc.id}: {e}")
                errors.append(f"Failed to process item {doc.id}: {str(e)}")
        
        # Sort items by creation date (newest first)
        items.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        print(f"DEBUG: Retrieved {len(items)} wardrobe items")
        if errors:
            print(f"DEBUG: Encountered {len(errors)} errors while processing items")
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "errors": errors if errors else None
        }
    except Exception as e:
        print(f"DEBUG: Error getting wardrobe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving wardrobe items: {str(e)}"
        )

@router.post("/")
async def add_wardrobe_item(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add item to wardrobe - simplified version"""
    try:
        print(f"DEBUG: Adding wardrobe item")
        
        # Validate required fields
        required_fields = ['name', 'type', 'color']
        for field in required_fields:
            if field not in item_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create item ID
        item_id = str(uuid.uuid4())
        
        # Prepare item data
        wardrobe_item = {
            "id": item_id,
            "userId": "test-user-id",
            "name": item_data["name"],
            "type": item_data["type"],
            "color": item_data["color"],
            "style": item_data.get("style", []),
            "occasion": item_data.get("occasion", []),
            "season": item_data.get("season", ["all"]),
            "imageUrl": item_data.get("imageUrl", ""),
            "dominantColors": [{"name": item_data["color"], "hex": "#000000", "rgb": [0, 0, 0]}],
            "matchingColors": [],
            "tags": item_data.get("tags", []),
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "metadata": {
                "analysisTimestamp": int(time.time()),
                "originalType": item_data["type"],
                "styleTags": item_data.get("style", []),
                "occasionTags": item_data.get("occasion", []),
                "colorAnalysis": {
                    "dominant": [item_data["color"]],
                    "matching": []
                },
                "visualAttributes": {
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "fit": "regular",
                    "material": "cotton",
                    "fabricWeight": "medium"
                },
                "itemMetadata": {
                    "tags": item_data.get("tags", []),
                    "careInstructions": "Check care label"
                }
            },
            "favorite": False,
            "wearCount": 0,
            "lastWorn": None
        }
        
        # Save to Firestore
        doc_ref = db.collection('wardrobe').document(item_id)
        doc_ref.set(wardrobe_item)
        
        print(f"DEBUG: Successfully added item with ID: {item_id}")
        
        return {
            "success": True,
            "message": "Item added successfully",
            "item_id": item_id,
            "item": wardrobe_item
        }
    except Exception as e:
        print(f"DEBUG: Error adding wardrobe item: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add item"
        )

@router.get("/top-worn-items")
async def get_top_worn_items(limit: int = 5):
    """Get top worn items from the wardrobe"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get all wardrobe items
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        # Sort by wear count (assuming wear_count field exists)
        items_with_wear_count = []
        for item in items:
            wear_count = item.get('wear_count', 0)
            items_with_wear_count.append({
                'id': item.get('id'),
                'name': item.get('name', 'Unknown Item'),
                'type': item.get('type', 'unknown'),
                'image_url': item.get('image_url', '/placeholder.jpg'),
                'wear_count': wear_count,
                'is_favorite': item.get('is_favorite', False)
            })
        
        # Sort by wear count descending and take top items
        top_items = sorted(items_with_wear_count, key=lambda x: x['wear_count'], reverse=True)[:limit]
        
        return {
            "success": True,
            "top_worn_items": top_items,
            "count": len(top_items),
            "total_items": len(items),
            "message": "Top worn items retrieved successfully"
        }
        
    except Exception as e:
        print(f"DEBUG: Error getting top worn items: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get top worn items"
        ) 