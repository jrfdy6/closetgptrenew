from fastapi import APIRouter

router = APIRouter(prefix="/api/outfit", tags=["outfit"])

@router.get("/")
async def get_outfits():
    """Get outfits endpoint"""
    return {"message": "Outfit router is working!", "status": "success"}

@router.post("/generate")
async def generate_outfit(request: dict):
    """Generate outfit with minimal validation"""
    print(f"🔍 DEBUG: Outfit generation called")
    print(f"🔍 DEBUG: Request data: {request}")
    
    # Simple mock response
    mock_outfit = {
        "id": "outfit-test-123",
        "name": f"Test {request.get('style', 'Casual')} Outfit",
        "occasion": request.get("occasion", "casual"),
        "style": request.get("style", "casual"),
        "mood": request.get("mood", "confident"),
        "confidence": 85.0,
        "items": [
            {
                "id": "test-item-1",
                "name": "Test Shirt",
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
                "id": "test-item-2", 
                "name": "Test Pants",
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
                "id": "test-item-3",
                "name": "Test Shoes", 
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
        "reasoning": "Test mock outfit for testing endpoint connectivity",
        "createdAt": 1758580800,
        "userId": request.get("user_profile", {}).get("id", "unknown")
    }
    
    print(f"✅ DEBUG: Test outfit generated successfully")
    return mock_outfit
