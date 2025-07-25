#!/usr/bin/env python3
import requests
import json

def test_item_selection_debug():
    """Test outfit generation with debug output to see why no items are selected."""
    
    # Simple test payload with minimal data
    payload = {
        "occasion": "Wedding Guest",
        "mood": "confident", 
        "style": "Casual Cool",
        "description": "",
        "wardrobe": [
            {
                "id": "test-item-1",
                "name": "Test Wedding Shirt",
                "type": "shirt",
                "color": "White",
                "season": ["spring", "summer"],
                "imageUrl": "https://example.com/test.jpg",
                "tags": ["Wedding Guest", "Formal"],
                "style": ["Casual Cool", "Classic"],
                "userId": "test-user",
                "dominantColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "occasion": ["Wedding Guest", "Formal", "Casual"],
                "createdAt": 1750326000,
                "updatedAt": 1750326000,
                "subType": None,
                "brand": None,
                "colorName": "White",
                "metadata": {
                    "visualAttributes": {
                        "material": "cotton",
                        "pattern": None,
                        "textureStyle": None,
                        "fabricWeight": None,
                        "fit": None,
                        "silhouette": None,
                        "length": None,
                        "genderTarget": None,
                        "sleeveLength": None,
                        "hangerPresent": None,
                        "backgroundRemoved": None,
                        "wearLayer": None,
                        "formalLevel": None
                    },
                    "itemMetadata": {
                        "priceEstimate": None,
                        "careInstructions": None,
                        "tags": ["Wedding Guest", "Formal"]
                    },
                    "colorAnalysis": {
                        "dominant": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                        "matching": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}]
                    },
                    "originalType": "shirt",
                    "analysisTimestamp": 1750326000,
                    "naturalDescription": None
                }
            }
        ],
        "weather": {
            "temperature": 70,
            "condition": "sunny",
            "humidity": 50,
            "wind_speed": 5,
            "location": "New York"
        },
        "user_profile": {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "gender": "male",
            "preferences": {
                "style": ["Casual Cool"],
                "colors": ["White", "Black"],
                "occasions": ["Wedding Guest"]
            },
            "measurements": {
                "height": 70,
                "weight": 160,
                "bodyType": "athletic",
                "skinTone": "warm"
            },
            "stylePreferences": ["Casual Cool"],
            "bodyType": "athletic",
            "skinTone": "warm",
            "fitPreference": None,
            "createdAt": 1750326000,
            "updatedAt": 1750326000
        },
        "likedOutfits": [],
        "trendingStyles": []
    }
    
    print("🧪 Testing item selection with debug output...")
    print(f"📦 Sending {len(payload['wardrobe'])} wardrobe items")
    print(f"🎯 Occasion: {payload['occasion']}")
    print(f"🎨 Style: {payload['style']}")
    
    try:
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Outfit generation worked!")
            print(f"🎯 Generated outfit ID: {data.get('id')}")
            print(f"👕 Outfit name: {data.get('name')}")
            print(f"📋 Number of items selected: {len(data.get('items', []))}")
            print(f"🎨 Color harmony: {data.get('colorHarmony')}")
            print(f"📝 Style notes: {data.get('styleNotes')}")
            
            if len(data.get('items', [])) == 0:
                print("\n⚠️  No items were selected - this suggests an issue with the selection logic")
                print("🔍 Check the backend logs for debug output about item selection")
            else:
                print(f"\n✅ Items selected successfully!")
                for i, item in enumerate(data.get('items', [])):
                    print(f"  {i+1}. {item.get('name')} ({item.get('type')})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_item_selection_debug() 