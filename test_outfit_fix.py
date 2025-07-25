#!/usr/bin/env python3
import requests
import json

def test_outfit_generation():
    """Test outfit generation with the fixed to_dict_recursive function."""
    
    # Test payload with occasion, style, and mood selected
    payload = {
        "occasion": "Wedding Guest",
        "mood": "confident", 
        "style": "Casual Cool",
        "description": "",
        "gender": "male",
        "wardrobe": [
            {
                "id": "test-item-1",
                "name": "Test Shirt",
                "type": "shirt",
                "color": "White",
                "season": ["spring", "summer"],
                "imageUrl": "https://example.com/test.jpg",
                "tags": ["Casual"],
                "style": ["Classic", "Casual"],
                "userId": "test-user",
                "dominantColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "occasion": ["Casual", "Brunch"],
                "createdAt": 1750151680958,
                "updatedAt": 1750202836,
                "subType": "t-shirt",
                "backgroundRemoved": False,
                "metadata": {
                    "originalType": "shirt",
                    "analysisTimestamp": 1750151680958,
                    "colorAnalysis": {
                        "dominant": [{"hex": "#FFFFFF", "name": "White", "rgb": [255, 255, 255]}],
                        "matching": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}]
                    },
                    "visualAttributes": {
                        "material": "Cotton",
                        "pattern": "Solid",
                        "textureStyle": "Smooth",
                        "fabricWeight": "Light",
                        "fit": "Regular",
                        "formalLevel": "Casual"
                    }
                }
            }
        ],
        "user_profile": {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "gender": "male",
            "age": 25,
            "height": 175,
            "weight": 70,
            "bodyType": "average",
            "stylePreferences": ["Casual", "Classic"],
            "colorPreferences": ["Blue", "White"],
            "brandPreferences": ["Nike", "Adidas"],
            "budget": "medium",
            "location": "New York",
            "climate": "temperate",
            "createdAt": 1750151680958,
            "updatedAt": 1750151680958
        },
        "weather": {
            "temperature": 22.0,
            "condition": "sunny",
            "humidity": 60,
            "wind_speed": 10,
            "location": "New York"
        },
        "likedOutfits": [],
        "trendingStyles": [],
        "preferences": {},
        "outfitHistory": [],
        "randomSeed": 0.5,
        "season": "spring",
        "baseItem": None
    }
    
    try:
        print("Testing outfit generation with occasion, style, and mood...")
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
            print(f"Number of items: {len(result.get('items', []))}")
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
        print("\n🎉 The to_dict_recursive fix is working! You can now use outfit generation with occasion, style, and mood selected.")
    else:
        print("\n💥 There's still an issue with the outfit generation.") 