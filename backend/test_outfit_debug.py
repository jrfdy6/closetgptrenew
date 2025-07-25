#!/usr/bin/env python3

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_outfit_generation():
    """Test outfit generation to debug the issues."""
    print("🧪 Testing outfit generation...")
    
    # Test payload
    payload = {
        "occasion": "Casual",
        "mood": "confident",
        "style": "Casual Cool",
        "weather": {
            "temperature": 75,
            "condition": "sunny",
            "humidity": 60,
            "location": "default",
            "wind_speed": 5,
            "precipitation": 0
        },
        "wardrobe": [
            {
                "id": "test-shirt-1",
                "name": "Blue T-Shirt",
                "type": "shirt",
                "style": ["casual"],
                "occasion": ["casual"],
                "dominantColors": [{"name": "blue", "hex": "#0000FF"}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
                "color": "blue",
                "season": ["all"],
                "tags": ["casual"],
                "userId": "test-user",
                "imageUrl": "https://example.com/blue-tshirt.jpg",
                "createdAt": 1640995200,
                "updatedAt": 1640995200
            },
            {
                "id": "test-pants-1",
                "name": "Black Jeans",
                "type": "pants",
                "style": ["casual"],
                "occasion": ["casual"],
                "dominantColors": [{"name": "black", "hex": "#000000"}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
                "color": "black",
                "season": ["all"],
                "tags": ["casual"],
                "userId": "test-user",
                "imageUrl": "https://example.com/black-jeans.jpg",
                "createdAt": 1640995200,
                "updatedAt": 1640995200
            }
        ],
        "user_profile": {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "bodyType": "athletic",
            "skinTone": "medium",
            "stylePreferences": ["casual"],
            "budget": "medium",
            "createdAt": 1640995200,
            "updatedAt": 1640995200
        },
        "likedOutfits": [],
        "trendingStyles": []
    }
    
    try:
        print("Sending request to backend...")
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Outfit generation worked!")
            print(f"Generated outfit ID: {result.get('id', 'N/A')}")
            print(f"Outfit name: {result.get('name', 'N/A')}")
            print(f"Outfit mood: {result.get('mood', 'N/A')}")
            print(f"Outfit style: {result.get('style', 'N/A')}")
            print(f"Number of items: {len(result.get('items', []))}")
            
            # Check items
            items = result.get('items', [])
            if items:
                print("Items in outfit:")
                for item in items:
                    print(f"  - {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
                    print(f"    Image URL: {item.get('imageUrl', 'No image')}")
            else:
                print("❌ No items in outfit!")
            
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = test_outfit_generation()
    if success:
        print("\n🎉 Outfit generation test PASSED!")
    else:
        print("\n💥 Outfit generation test FAILED!") 