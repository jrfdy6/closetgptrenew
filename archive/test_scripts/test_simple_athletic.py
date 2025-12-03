#!/usr/bin/env python3
"""
Simple test to verify the hard filter + soft scoring system works
"""

import requests
import json

def test_athletic_outfit():
    """Test athletic outfit generation with the new system"""
    
    # Test data
    test_data = {
        "occasion": "Athletic",
        "style": "Classic", 
        "mood": "Bold",
        "weather": {
            "temperature": 70,
            "condition": "sunny"
        },
        "wardrobe": [
            {
                "id": "test1",
                "name": "A slim, long, solid, smooth button up by Polo Ralph Lauren",
                "type": "shirt",
                "color": "Olive Green",
                "occasion": [],
                "style": [],
                "mood": []
            },
            {
                "id": "test2", 
                "name": "A solid, smooth toe shoes by SUICOKE",
                "type": "shoes",
                "color": "Black",
                "occasion": [],
                "style": [],
                "mood": []
            },
            {
                "id": "test3",
                "name": "A slim, solid, smooth slim fit pants by Dockers", 
                "type": "pants",
                "color": "Olive",
                "occasion": [],
                "style": [],
                "mood": []
            },
            {
                "id": "test4",
                "name": "Nike Athletic Tank Top",
                "type": "shirt", 
                "color": "White",
                "occasion": [],
                "style": [],
                "mood": []
            },
            {
                "id": "test5",
                "name": "Nike Running Shorts",
                "type": "shorts",
                "color": "Black", 
                "occasion": [],
                "style": [],
                "mood": []
            },
            {
                "id": "test6",
                "name": "Nike Sneakers",
                "type": "shoes",
                "color": "White",
                "occasion": [],
                "style": [],
                "mood": []
            }
        ],
        "user_profile": {
            "bodyType": "Athletic",
            "height": "Average",
            "weight": "Average", 
            "gender": "Male",
            "skinTone": "Medium",
            "stylePreferences": {}
        },
        "likedOutfits": []
    }
    
    try:
        print("🧪 Testing athletic outfit generation...")
        print(f"📊 Test wardrobe: {len(test_data['wardrobe'])} items")
        print(f"🎯 Request: Athletic + Classic + Bold")
        
        # Make request to robust generator
        response = requests.post(
            "https://closetgpt-backend-production.up.railway.app/api/outfits/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Outfit generated!")
            print(f"📦 Items: {len(result.get('items', []))}")
            
            for i, item in enumerate(result.get('items', [])):
                print(f"  {i+1}. {item.get('name', 'Unknown')}")
            
            # Check if we got athletic items
            item_names = [item.get('name', '').lower() for item in result.get('items', [])]
            athletic_indicators = ['tank', 'athletic', 'sport', 'gym', 'workout', 'running', 'sneaker', 'shorts']
            business_indicators = ['button', 'dress', 'oxford', 'formal', 'suit']
            
            athletic_count = sum(1 for name in item_names if any(indicator in name for indicator in athletic_indicators))
            business_count = sum(1 for name in item_names if any(indicator in name for indicator in business_indicators))
            
            print(f"🏃‍♂️ Athletic items: {athletic_count}")
            print(f"👔 Business items: {business_count}")
            
            if athletic_count > business_count:
                print("🎉 SUCCESS: More athletic items than business items!")
            else:
                print("⚠️ ISSUE: Still getting business items for athletic occasion")
                
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_athletic_outfit()

