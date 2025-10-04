from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import uuid

router = APIRouter(prefix="/api/outfit")

@(router.get("/") if router else None)
async def get_outfits():
    """Simple test endpoint to verify outfit router loads"""
    return {"message": "Simple outfit router is working!", "status": "success"}

@(router.get("/{outfit_id}") if router else None)
async def get_outfit(outfit_id: str):
    """Simple test endpoint to get outfit by ID"""
    return {"message": f"Getting outfit {outfit_id}", "outfit_id": outfit_id}

@router.post("/generate")
async def generate_outfit(request: Dict[str, Any]):
    print(f"🔍 DEBUG: Simple outfit generation called")
    print(f"🔍 DEBUG: Request data: {request}")
    
    # Simple mock response
    mock_outfit = {
        "id": str(uuid.uuid4()),
        "name": f"Simple Mock Outfit",
        "occasion": (request.get("occasion", "casual") if request else "casual"),
        "style": (request.get("style", "casual") if request else "casual"),
        "mood": (request.get("mood", "confident") if request else "confident"),
        "confidence": 85.0,
        "items": [
            {
                "id": "mock-item-1",
                "name": "Mock Shirt",
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
                "id": "mock-item-2", 
                "name": "Mock Pants",
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
                "id": "mock-item-3",
                "name": "Mock Shoes", 
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
        "reasoning": "Simple mock outfit for testing endpoint connectivity",
        "createdAt": int(time.time()),
        "userId": (request.get("user_profile", {}) if request else {}).get("id", "unknown")
    }
    
    print(f"✅ DEBUG: Simple mock outfit generated successfully")
    return mock_outfit
