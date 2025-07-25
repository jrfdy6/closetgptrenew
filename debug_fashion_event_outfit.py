#!/usr/bin/env python3
"""
Debug script to generate a Fashion Event outfit and see detailed logging
"""

import requests
import json

# Backend API endpoint
API_BASE_URL = "http://localhost:3001"

def create_test_wardrobe_with_bottoms():
    """Create test wardrobe data with various bottoms."""
    base_fields = {
        "tags": [],
        "userId": "test-user",
        "matchingColors": [],
        "createdAt": 1704067200,  # 2024-01-01T00:00:00Z as Unix timestamp
        "updatedAt": 1704067200
    }
    
    return [
        # Tops
        {
            "id": "test-shirt-1",
            "name": "A slim, long, solid, smooth dress shirt",
            "type": "shirt",
            "color": "white",
            "style": ["business casual", "formal"],
            "occasion": ["work", "formal", "business"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/shirt.jpg",
            "dominantColors": [
                {"name": "white", "hex": "#FFFFFF", "percentage": 80},
                {"name": "light gray", "hex": "#F5F5F5", "percentage": 20}
            ],
            **base_fields
        },
        # BOTTOMS - Multiple options
        {
            "id": "test-pants-1",
            "name": "A slim, solid, smooth dress pants",
            "type": "pants",
            "color": "black",
            "style": ["business casual", "formal"],
            "occasion": ["work", "formal", "business", "fashion event"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/pants.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 90},
                {"name": "dark gray", "hex": "#333333", "percentage": 10}
            ],
            **base_fields
        },
        {
            "id": "test-pants-2",
            "name": "A solid, smooth chino pants",
            "type": "pants",
            "color": "navy",
            "style": ["business casual", "smart casual"],
            "occasion": ["work", "casual", "business casual", "fashion event"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/chinos.jpg",
            "dominantColors": [
                {"name": "navy", "hex": "#000080", "percentage": 85},
                {"name": "blue", "hex": "#0000FF", "percentage": 15}
            ],
            **base_fields
        },
        {
            "id": "test-skirt-1",
            "name": "A solid, smooth pencil skirt",
            "type": "skirt",
            "color": "black",
            "style": ["business casual", "formal"],
            "occasion": ["work", "formal", "business", "fashion event"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/skirt.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 95},
                {"name": "dark gray", "hex": "#333333", "percentage": 5}
            ],
            **base_fields
        },
        # Shoes
        {
            "id": "test-shoes-1",
            "name": "A solid, smooth dress shoes",
            "type": "shoes",
            "color": "black",
            "style": ["business casual", "formal"],
            "occasion": ["work", "formal", "business", "fashion event"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/shoes.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 90},
                {"name": "dark brown", "hex": "#654321", "percentage": 10}
            ],
            **base_fields
        },
        # Accessories
        {
            "id": "test-belt-1",
            "name": "A solid, smooth belt",
            "type": "accessory",
            "color": "black",
            "style": ["business casual", "formal"],
            "occasion": ["work", "formal", "business", "fashion event"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/belt.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 100}
            ],
            **base_fields
        }
    ]

def test_fashion_event_outfit():
    """Test generating a Fashion Event outfit with detailed logging."""
    print("🧪 Testing Fashion Event outfit generation with detailed logging")
    print("=" * 60)
    
    try:
        # Create test data
        wardrobe = create_test_wardrobe_with_bottoms()
        print(f"📦 Created test wardrobe with {len(wardrobe)} items:")
        for item in wardrobe:
            print(f"   - {item['name']} ({item['type']})")
        
        # Create user profile
        user_profile = {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "bodyType": "athletic",
            "skinTone": "medium",
            "height": 175,
            "weight": 70,
            "preferences": {
                "style": ["business casual"],
                "colors": ["black", "white", "navy"],
                "occasions": ["fashion event", "work"]
            },
            "stylePreferences": ["business casual"],
            "fitPreference": "fitted",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
        
        # Create weather data
        weather_data = {
            "temperature": 83.8,
            "condition": "sunny",
            "humidity": 60,
            "windSpeed": 5
        }
        
        # Create request payload
        payload = {
            "occasion": "Fashion Event",
            "weather": weather_data,
            "wardrobe": wardrobe,
            "user_profile": user_profile,
            "likedOutfits": [],
            "trendingStyles": [],
            "outfitHistory": [],
            "style": "Business Casual",
            "mood": "energetic"
        }
        
        print(f"\n🚀 Sending request to generate Fashion Event outfit...")
        print(f"   - Occasion: Fashion Event")
        print(f"   - Style: Business Casual")
        print(f"   - Mood: energetic")
        print(f"   - Temperature: {weather_data['temperature']}°F")
        
        # Make the API call
        response = requests.post(
            f"{API_BASE_URL}/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated outfit:")
            print(f"   - Outfit ID: {result.get('id', 'N/A')}")
            print(f"   - Items: {len(result.get('items', []))}")
            
            # Use 'pieces' instead of 'items' for detailed item information
            pieces = result.get('pieces', [])
            print(f"   - Pieces: {len(pieces)}")
            for i, piece in enumerate(pieces, 1):
                print(f"   {i}. {piece.get('name', 'N/A')} ({piece.get('type', 'N/A')})")
            
            # Check if bottom is present
            bottoms = [piece for piece in pieces if piece.get('type') in ['pants', 'jeans', 'shorts', 'skirt']]
            if bottoms:
                print(f"\n✅ BOTTOM FOUND: {len(bottoms)} bottom(s) in outfit")
                for bottom in bottoms:
                    print(f"   - {bottom.get('name')} ({bottom.get('type')})")
            else:
                print(f"\n❌ NO BOTTOM FOUND: Outfit missing pants/skirt!")
                print(f"   - Available pieces: {[piece.get('type') for piece in pieces]}")
            
            # Also check validation errors
            validation_errors = result.get('validationErrors', [])
            if validation_errors:
                print(f"\n⚠️  Validation Errors:")
                for error in validation_errors:
                    print(f"   - {error}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fashion_event_outfit() 