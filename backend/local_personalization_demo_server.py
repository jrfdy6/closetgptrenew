#!/usr/bin/env python3
"""
Local personalization demo test server.
This runs a minimal FastAPI server locally to test the personalization demo functionality.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError as e:
    print(f"❌ FastAPI not available: {e}")
    print("💡 Run: python setup_local_test_env.py")
    FASTAPI_AVAILABLE = False

# Pydantic models for the personalization demo
class OutfitGenerationRequest(BaseModel):
    occasion: str = "business"
    style: str = "professional"
    mood: str = "confident"
    weather: Optional[Dict[str, Any]] = None
    generation_mode: str = "robust"  # or "simple-minimal"
    user_id: str = "test-user-123"

class OutfitItem(BaseModel):
    id: str
    name: str
    type: str
    color: str
    style: str
    occasion: str
    imageUrl: Optional[str] = None

class OutfitResponse(BaseModel):
    id: str
    name: str
    items: List[OutfitItem]
    style: str
    occasion: str
    mood: str
    confidence_score: float
    personalization_score: float
    personalization_applied: bool
    user_interactions: int
    data_source: str
    generation_mode: str
    generation_strategy: str
    metadata: Dict[str, Any]

class PersonalizationStatusResponse(BaseModel):
    user_id: str
    personalization_enabled: bool
    has_existing_data: bool
    total_interactions: int
    min_interactions_required: int
    ready_for_personalization: bool
    preferred_colors: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    favorite_items_count: int
    most_worn_items_count: int
    data_source: str

# Mock data for testing
MOCK_WARDROBE_ITEMS = [
    {
        "id": "item-1",
        "name": "Navy Blue Blazer",
        "type": "outerwear",
        "color": "navy",
        "style": "professional",
        "occasion": "business",
        "imageUrl": "https://via.placeholder.com/200x200/000080/FFFFFF?text=Navy+Blazer"
    },
    {
        "id": "item-2",
        "name": "White Dress Shirt",
        "type": "top",
        "color": "white",
        "style": "professional",
        "occasion": "business",
        "imageUrl": "https://via.placeholder.com/200x200/FFFFFF/000000?text=White+Shirt"
    },
    {
        "id": "item-3",
        "name": "Black Dress Pants",
        "type": "bottom",
        "color": "black",
        "style": "professional",
        "occasion": "business",
        "imageUrl": "https://via.placeholder.com/200x200/000000/FFFFFF?text=Black+Pants"
    },
    {
        "id": "item-4",
        "name": "Brown Leather Shoes",
        "type": "shoes",
        "color": "brown",
        "style": "professional",
        "occasion": "business",
        "imageUrl": "https://via.placeholder.com/200x200/8B4513/FFFFFF?text=Brown+Shoes"
    },
    {
        "id": "item-5",
        "name": "Casual Blue Jeans",
        "type": "bottom",
        "color": "blue",
        "style": "casual",
        "occasion": "casual",
        "imageUrl": "https://via.placeholder.com/200x200/4169E1/FFFFFF?text=Blue+Jeans"
    },
    {
        "id": "item-6",
        "name": "White T-Shirt",
        "type": "top",
        "color": "white",
        "style": "casual",
        "occasion": "casual",
        "imageUrl": "https://via.placeholder.com/200x200/FFFFFF/000000?text=White+T-Shirt"
    }
]

def create_mock_outfit(request: OutfitGenerationRequest) -> OutfitResponse:
    """Create a mock outfit based on the request."""
    
    # Filter items based on occasion and style
    suitable_items = [
        item for item in MOCK_WARDROBE_ITEMS
        if request.occasion.lower() in item["occasion"].lower() and 
           request.style.lower() in item["style"].lower()
    ]
    
    # If no suitable items, use fallback items
    if not suitable_items:
        suitable_items = MOCK_WARDROBE_ITEMS[:4]  # Use first 4 items as fallback
    
    # Create outfit items
    outfit_items = []
    for i, item in enumerate(suitable_items[:4]):  # Limit to 4 items
        outfit_items.append(OutfitItem(
            id=item["id"],
            name=item["name"],
            type=item["type"],
            color=item["color"],
            style=item["style"],
            occasion=item["occasion"],
            imageUrl=item["imageUrl"]
        ))
    
    # Determine generation strategy based on mode
    if request.generation_mode == "robust":
        generation_strategy = "robust_personalization"
        confidence_score = 0.92
        personalization_score = 0.88
    else:
        generation_strategy = "simple_minimal"
        confidence_score = 0.75
        personalization_score = 0.65
    
    return OutfitResponse(
        id=f"outfit-{request.generation_mode}-{int(datetime.now().timestamp())}",
        name=f"{request.style.title()} {request.occasion.title()} Outfit",
        items=outfit_items,
        style=request.style,
        occasion=request.occasion,
        mood=request.mood,
        confidence_score=confidence_score,
        personalization_score=personalization_score,
        personalization_applied=True,
        user_interactions=15,
        data_source="local_test_mock",
        generation_mode=request.generation_mode,
        generation_strategy=generation_strategy,
        metadata={
            "generation_time": 0.3,
            "personalization_enabled": True,
            "user_id": request.user_id,
            "uses_simple_architecture": request.generation_mode == "simple-minimal",
            "test_mode": True,
            "wardrobe_size": len(suitable_items),
            "timestamp": datetime.now().isoformat()
        }
    )

def get_personalization_status(user_id: str) -> PersonalizationStatusResponse:
    """Get personalization status for a user."""
    return PersonalizationStatusResponse(
        user_id=user_id,
        personalization_enabled=True,
        has_existing_data=True,
        total_interactions=15,
        min_interactions_required=3,
        ready_for_personalization=True,
        preferred_colors=["navy", "white", "black", "brown"],
        preferred_styles=["professional", "casual"],
        preferred_occasions=["business", "casual"],
        favorite_items_count=4,
        most_worn_items_count=6,
        data_source="local_test_mock"
    )

if FASTAPI_AVAILABLE:
    # Create FastAPI app
    app = FastAPI(
        title="Personalization Demo - Local Test Server",
        description="Local test server for personalization demo functionality",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Personalization Demo - Local Test Server",
            "status": "running",
            "endpoints": [
                "/health",
                "/api/personalization-demo/health",
                "/api/personalization-demo/generate",
                "/api/personalization-demo/personalization-status",
                "/api/personalization-demo/user-preferences",
                "/api/personalization-demo/analytics"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "personalization_demo_enabled": True,
            "available_generation_modes": ["simple-minimal", "robust"],
            "uses_local_testing": True,
            "timestamp": datetime.now().isoformat()
        }
    
    # Personalization demo endpoints
    @app.get("/api/personalization-demo/health")
    async def personalization_health():
        return {
            "status": "healthy",
            "personalization_demo_enabled": True,
            "available_generation_modes": ["simple-minimal", "robust"],
            "uses_local_testing": True,
            "integration_status": "local_test_server",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.post("/api/personalization-demo/generate", response_model=OutfitResponse)
    async def generate_personalized_outfit(request: OutfitGenerationRequest):
        """Generate a personalized outfit using the specified generation mode."""
        try:
            print(f"🎯 Generating outfit: {request.generation_mode} mode for {request.occasion} {request.style}")
            
            # Create mock outfit
            outfit = create_mock_outfit(request)
            
            print(f"✅ Generated outfit with {len(outfit.items)} items")
            print(f"   Confidence: {outfit.confidence_score}")
            print(f"   Personalization: {outfit.personalization_score}")
            
            return outfit
            
        except Exception as e:
            print(f"❌ Error generating outfit: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/personalization-demo/personalization-status", response_model=PersonalizationStatusResponse)
    async def get_personalization_status_endpoint(user_id: str = "test-user-123"):
        """Get personalization status for the user."""
        return get_personalization_status(user_id)
    
    @app.get("/api/personalization-demo/user-preferences")
    async def get_user_preferences(user_id: str = "test-user-123"):
        """Get user preferences."""
        return {
            "user_id": user_id,
            "preferences": {
                "preferred_colors": ["navy", "white", "black", "brown"],
                "preferred_styles": ["professional", "casual"],
                "preferred_occasions": ["business", "casual"],
                "disliked_colors": ["neon", "bright"],
                "disliked_styles": ["gothic", "punk"]
            },
            "existing_data": {
                "favorite_items": ["item-1", "item-2", "item-3", "item-4"],
                "most_worn_items": ["item-1", "item-2", "item-5", "item-6"],
                "total_interactions": 15,
                "last_updated": datetime.now().isoformat(),
                "data_source": "local_test_mock"
            },
            "stats": {
                "total_interactions": 15,
                "ready_for_personalization": True,
                "favorite_items_count": 4,
                "most_worn_items_count": 4
            },
            "uses_existing_data": True,
            "generation_modes_available": ["simple-minimal", "robust"]
        }
    
    @app.get("/api/personalization-demo/analytics")
    async def get_analytics():
        """Get system analytics."""
        return {
            "system_stats": {
                "uses_local_testing": True,
                "available_generation_modes": ["simple-minimal", "robust"],
                "uses_existing_data": True,
                "data_sources": ["local_test_mock"],
                "modular_services": ["mock_outfit_generator"],
                "no_duplicate_storage": True,
                "firebase_integration": False
            },
            "integration_benefits": [
                "Local testing environment",
                "Supports both generation modes",
                "Easy to debug and maintain",
                "Consistent with existing patterns",
                "Enhanced debugging capabilities",
                "No external dependencies"
            ],
            "migration_readiness": {
                "architecture_compatible": True,
                "service_reuse": False,
                "data_compatibility": True,
                "ready_for_main_app": True
            },
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Run the local test server."""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Please run: python setup_local_test_env.py")
        return
    
    print("🚀 Starting Personalization Demo - Local Test Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("🎯 Personalization demo: http://localhost:8000/api/personalization-demo/health")
    print("\n💡 Test both generation modes:")
    print("   - Simple-minimal: POST /api/personalization-demo/generate with generation_mode='simple-minimal'")
    print("   - Robust: POST /api/personalization-demo/generate with generation_mode='robust'")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
