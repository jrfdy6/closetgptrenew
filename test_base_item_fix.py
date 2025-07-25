#!/usr/bin/env python3

import requests
import json
import time

def test_base_item_inclusion():
    """Test that base item is included in generated outfit."""
    now = int(time.time())
    # Test data matching the backend's required schema
    wardrobe_item = {
        "id": "006crwqcyyl7kmby62lrf",
        "name": "A loose, short, textured, ribbed sweater by Abercrombie & Fitch",
        "type": "sweater",
        "imageUrl": "https://example.com/sweater.jpg",
        "tags": ["casual", "warm"],
        "dominantColors": [{"name": "Blue", "hex": "#0000FF"}],
        "matchingColors": [{"name": "Gray", "hex": "#808080"}],
        "occasion": ["Casual", "Everyday"],
        "style": ["Casual", "Classic"],
        "color": "Blue",
        "season": ["summer"],
        "userId": "default-user",
        "createdAt": now,
        "updatedAt": now
    }
    payload = {
        "occasion": "Concert",
        "mood": "relaxed", 
        "style": "Classic",
        "description": "Test outfit with base item",
        "wardrobe": [wardrobe_item],
        "weather": {
            "temperature": 76.3,
            "condition": "Rain",
            "humidity": 89,
            "wind_speed": 1.34,
            "location": "Chillum",
            "precipitation": 3.26
        },
        "user_profile": {
            "id": "default-user",
            "name": "Test User",
            "email": "test@example.com",
            "stylePreferences": ["Classic", "Casual"],
            "bodyType": "athletic",
            "createdAt": now,
            "updatedAt": now
        },
        "likedOutfits": [],
        "trendingStyles": [],
        "baseItem": wardrobe_item
    }
    
    print("🧪 Testing base item inclusion in outfit generation...")
    print(f"📋 Base item: {payload['baseItem']['name']}")
    
    try:
        # Make request to outfit generation endpoint
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Outfit generated successfully!")
            print(f"🆔 Outfit ID: {result.get('id')}")
            print(f"📝 Name: {result.get('name')}")
            print(f"🎯 Occasion: {result.get('occasion')}")
            print(f"👕 Items count: {len(result.get('items', []))}")
            
            # Check if base item is in the outfit
            items = result.get('items', [])
            base_item_found = False
            
            print(f"\n🔍 Checking for base item in outfit items:")
            for i, item in enumerate(items):
                print(f"   {i+1}. {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
                if item.get('name') == payload['baseItem']['name']:
                    base_item_found = True
                    print(f"      ✅ BASE ITEM FOUND!")
            
            if base_item_found:
                print(f"\n🎉 SUCCESS: Base item is included in the generated outfit!")
                return True
            else:
                print(f"\n❌ FAILURE: Base item is NOT included in the generated outfit!")
                print(f"   Expected: {payload['baseItem']['name']}")
                return False
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_base_item_inclusion()
    if success:
        print("\n✅ Test PASSED - Base item is now properly included!")
    else:
        print("\n❌ Test FAILED - Base item is still missing!") 