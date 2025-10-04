from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import uuid

router = APIRouter(prefix="/api/outfit-new")

@router.get("/")
async def get_outfits():
    """Get outfits endpoint"""
    return {"message": "Minimal outfit router is working!", "status": "success"}

@router.post("/generate")
async def generate_outfit(request: Dict[str, Any]):
    """Generate outfit with minimal validation"""
    print(f"🔍 DEBUG: Minimal outfit generation called")
    print(f"🔍 DEBUG: Request data: {request}")
    
    # Simple mock response
    mock_outfit = {
        "id": str(uuid.uuid4()),
        "name": f"Minimal {(request.get('style', 'Casual') if request else 'Casual')} Outfit",
        "occasion": (request.get("occasion", "casual") if request else "casual"),
        "style": (request.get("style", "casual") if request else "casual"),
        "mood": (request.get("mood", "confident") if request else "confident"),
        "confidence": 85.0,
        "items": [
            {
                "id": "minimal-item-1",
                "name": "Minimal Shirt",
                "type": "shirt",
                "color": "blue",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "minimal-item-2", 
                "name": "Minimal Pants",
                "type": "pants",
                "color": "black",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "minimal-item-3",
                "name": "Minimal Shoes", 
                "type": "shoes",
                "color": "white",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            }
        ],
        "reasoning": "Minimal mock outfit for testing endpoint connectivity",
        "createdAt": int(time.time()),
        "userId": (request.get("user_profile", {}) if request else {}).get("id", "unknown")
    }
    
    print(f"✅ DEBUG: Minimal outfit generated successfully")
    return mock_outfit
