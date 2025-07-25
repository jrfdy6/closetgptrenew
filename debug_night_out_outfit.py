#!/usr/bin/env python3
"""
Debug script to test Night Out outfit generation and see why tops are missing
"""

import requests
import json

# Backend API endpoint
API_BASE_URL = "http://localhost:3001"

def create_test_wardrobe_with_tops():
    """Create test wardrobe data with various tops."""
    base_fields = {
        "tags": [],
        "userId": "test-user",
        "matchingColors": [],
        "createdAt": 1704067200,
        "updatedAt": 1704067200
    }
    
    return [
        # TOPS - Multiple options
        {
            "id": "test-shirt-1",
            "name": "A slim, solid, smooth t-shirt",
            "type": "shirt",
            "color": "black",
            "style": ["streetwear", "casual"],
            "occasion": ["casual", "night out", "streetwear"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/tshirt.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 90},
                {"name": "dark gray", "hex": "#333333", "percentage": 10}
            ],
            **base_fields
        },
        {
            "id": "test-shirt-2",
            "name": "A solid, smooth hoodie",
            "type": "sweater",
            "color": "navy",
            "style": ["streetwear", "casual"],
            "occasion": ["casual", "night out", "streetwear"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/hoodie.jpg",
            "dominantColors": [
                {"name": "navy", "hex": "#000080", "percentage": 85},
                {"name": "blue", "hex": "#0000FF", "percentage": 15}
            ],
            **base_fields
        },
        {
            "id": "test-shirt-3",
            "name": "A slim, solid, smooth polo shirt",
            "type": "shirt",
            "color": "white",
            "style": ["streetwear", "smart casual"],
            "occasion": ["casual", "night out", "smart casual"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/polo.jpg",
            "dominantColors": [
                {"name": "white", "hex": "#FFFFFF", "percentage": 95},
                {"name": "light gray", "hex": "#F5F5F5", "percentage": 5}
            ],
            **base_fields
        },
        # BOTTOMS
        {
            "id": "test-pants-1",
            "name": "A slim, solid, smooth dress pants",
            "type": "pants",
            "color": "black",
            "style": ["streetwear", "smart casual"],
            "occasion": ["casual", "night out", "streetwear"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/pants.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "percentage": 90},
                {"name": "dark gray", "hex": "#333333", "percentage": 10}
            ],
            **base_fields
        },
        # Shoes
        {
            "id": "test-shoes-1",
            "name": "A slim, solid, smooth high top sneakers",
            "type": "sneakers",
            "color": "white",
            "style": ["streetwear", "casual"],
            "occasion": ["casual", "night out", "streetwear"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/sneakers.jpg",
            "dominantColors": [
                {"name": "white", "hex": "#FFFFFF", "percentage": 90},
                {"name": "light gray", "hex": "#F5F5F5", "percentage": 10}
            ],
            **base_fields
        }
    ]

def test_night_out_outfit():
    """Test generating a Night Out outfit with detailed logging."""
    print("🧪 Testing Night Out outfit generation with detailed logging")
    print("=" * 60)
    
    try:
        # Create test data
        wardrobe = create_test_wardrobe_with_tops()
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
                "style": ["streetwear"],
                "colors": ["black", "white", "navy"],
                "occasions": ["night out", "casual"]
            },
            "stylePreferences": ["streetwear"],
            "fitPreference": "fitted",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
        
        # Create weather data
        weather_data = {
            "temperature": 83.2,
            "condition": "clear",
            "humidity": 60,
            "windSpeed": 5
        }
        
        # Create request payload
        payload = {
            "occasion": "Night Out",
            "weather": weather_data,
            "wardrobe": wardrobe,
            "user_profile": user_profile,
            "likedOutfits": [],
            "trendingStyles": [],
            "outfitHistory": [],
            "style": "Streetwear",
            "mood": "relaxed"
        }
        
        print(f"\n🚀 Sending request to generate Night Out outfit...")
        print(f"   - Occasion: Night Out")
        print(f"   - Style: Streetwear")
        print(f"   - Mood: relaxed")
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
            
            # Check if top is present
            tops = [piece for piece in pieces if piece.get('type') in ['shirt', 't-shirt', 'polo', 'hoodie', 'sweater']]
            if tops:
                print(f"\n✅ TOP FOUND: {len(tops)} top(s) in outfit")
                for top in tops:
                    print(f"   - {top.get('name')} ({top.get('type')})")
            else:
                print(f"\n❌ NO TOP FOUND: Outfit missing shirt/top!")
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
    test_night_out_outfit() 