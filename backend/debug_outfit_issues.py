#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_outfit_generation_debug():
    """Test outfit generation to debug the specific issues."""
    print("🔍 Testing outfit generation to debug issues...")
    
    # Test payload with actual weather data (81°F) and athletic occasion
    payload = {
        "occasion": "Athletic / Gym",
        "mood": "energetic",
        "style": "Athleisure",
        "description": "Test outfit for debugging",
        "wardrobe": [
            {
                "id": "228mfgpco9lmby5t9mx",
                "name": "A slim, long, solid, smooth dress shirt",
                "type": "shirt",
                "color": "Ivory",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2Fded2ca7e-d804-4dbc-aac9-7bb9ed96d05a.jpg?alt=media&token=699b97ee-4f82-40b2-9a32-aa83822a8baf",
                "tags": ["formal", "business"],
                "style": ["Classic", "Business", "Preppy", "Business Casual", "Old Money", "Formal"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "Ivory", "hex": "#FFFFF0", "rgb": [255, 255, 240]}],
                "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "occasion": ["Business", "Wedding", "Formal", "Funeral"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "dress shirt",
                "brand": "Unknown",
                "colorName": "Ivory",
                "backgroundRemoved": False
            },
            {
                "id": "dress-pants-1",
                "name": "Dress Pants",
                "type": "pants",
                "color": "Black",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://example.com/dress-pants.jpg",
                "tags": ["formal", "business", "dress"],
                "style": ["Classic", "Business", "Formal", "Professional"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "matchingColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "occasion": ["Business", "Formal", "Wedding", "Interview"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "dress pants",
                "brand": "Unknown",
                "colorName": "Black",
                "backgroundRemoved": False
            },
            {
                "id": "725fbe51-72d3-467c-a395-b06169bc05c5",
                "name": "White Leather Sneakers",
                "type": "sneakers",
                "color": "white",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
                "tags": ["sneakers", "white", "minimalist", "leather"],
                "style": ["Minimalist", "Classic", "Casual"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}, {"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                "occasion": ["casual", "daily", "weekend", "errands"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "low_top",
                "brand": "Common Projects",
                "colorName": "white",
                "backgroundRemoved": True
            },
            {
                "id": "11nmpo4r5dkjmby60vj0",
                "name": "A loose, solid, smooth casual shorts",
                "type": "shorts",
                "color": "Navy Blue",
                "season": ["spring", "summer"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F8479caf9-f533-460b-b8c1-d0ddbc858c63.jpg?alt=media&token=03fd34cb-8d22-41fe-b639-aabfda5ad8f7",
                "tags": ["Casual"],
                "style": ["Urban", "Techwear", "Casual", "Streetwear", "Athleisure", "Sporty"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "Navy Blue", "hex": "#000080", "rgb": [0, 0, 128]}],
                "matchingColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "occasion": ["Beach", "Vacation", "Casual", "Brunch", "Dinner"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "casual shorts",
                "brand": None,
                "colorName": "Navy Blue",
                "backgroundRemoved": False
            },
            # Add more appropriate athletic items
            {
                "id": "athletic-shirt-1",
                "name": "Cotton Athletic T-Shirt",
                "type": "shirt",
                "color": "White",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://example.com/athletic-shirt.jpg",
                "tags": ["athletic", "comfortable", "cotton"],
                "style": ["Athleisure", "Sporty", "Casual"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "occasion": ["Athletic", "Gym", "Casual", "Workout"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "t-shirt",
                "brand": "Nike",
                "colorName": "White",
                "backgroundRemoved": False
            },
            {
                "id": "athletic-shorts-1",
                "name": "Athletic Running Shorts",
                "type": "shorts",
                "color": "Black",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://example.com/athletic-shorts.jpg",
                "tags": ["athletic", "running", "comfortable"],
                "style": ["Athleisure", "Sporty", "Athletic"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "matchingColors": [{"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "occasion": ["Athletic", "Gym", "Running", "Workout"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "athletic shorts",
                "brand": "Adidas",
                "colorName": "Black",
                "backgroundRemoved": False
            },
            {
                "id": "running-shoes-1",
                "name": "Running Sneakers",
                "type": "sneakers",
                "color": "Gray",
                "season": ["spring", "summer", "fall", "winter"],
                "imageUrl": "https://example.com/running-shoes.jpg",
                "tags": ["athletic", "running", "comfortable"],
                "style": ["Athleisure", "Sporty", "Athletic"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [{"name": "Gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "matchingColors": [{"name": "Black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "occasion": ["Athletic", "Gym", "Running", "Workout"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "subType": "running shoes",
                "brand": "Nike",
                "colorName": "Gray",
                "backgroundRemoved": False
            }
        ],
        "weather": {
            "temperature": 81,  # Actual temperature instead of 70
            "condition": "sunny",
            "location": "test",
            "humidity": 50,
            "wind_speed": 5,
            "precipitation": 0
        },
        "user_profile": {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "preferences": {
                "style": ["casual", "athletic"],
                "colors": ["blue", "white", "black"],
                "occasions": ["casual", "athletic"]
            },
            "measurements": {
                "height": 70,
                "weight": 150,
                "bodyType": "athletic",
                "skinTone": "medium"
            },
            "stylePreferences": ["casual", "athletic"],
            "bodyType": "athletic",
            "skinTone": "medium",
            "createdAt": 1640995200,
            "updatedAt": 1640995200
        },
        "likedOutfits": [],
        "trendingStyles": []
    }
    
    print(f"🌡️  Weather temperature: {payload['weather']['temperature']}°F")
    print(f"🎯 Occasion: {payload['occasion']}")
    print(f"👕 Wardrobe items: {len(payload['wardrobe'])}")
    
    # Analyze wardrobe items for occasion compatibility
    print(f"\n🔍 ANALYZING WARDROBE ITEMS FOR OCCASION COMPATIBILITY:")
    print(f"Requested occasion: '{payload['occasion']}'")
    
    athletic_keywords = ['athletic', 'gym', 'workout', 'running', 'sport']
    for item in payload['wardrobe']:
        item_occasions = [occ.lower() for occ in item['occasion']]
        has_athletic_occasion = any(keyword in ' '.join(item_occasions) for keyword in athletic_keywords)
        
        print(f"  📋 {item['name']} ({item['type']})")
        print(f"     Occasions: {item['occasion']}")
        print(f"     Has athletic occasion: {'✅ YES' if has_athletic_occasion else '❌ NO'}")
        print(f"     Style: {item['style']}")
        print(f"     Tags: {item['tags']}")
        print()
    
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
            print(f"🌡️  Weather mentioned: {data.get('description', '')}")
            
            # Check for duplicate items
            items = data.get('items', [])
            item_names = [item.get('name', '') for item in items]
            unique_names = list(set(item_names))
            
            print(f"📋 Number of items selected: {len(items)}")
            print(f"📋 Number of unique item names: {len(unique_names)}")
            
            if len(items) != len(unique_names):
                print("⚠️  WARNING: Duplicate items detected!")
                from collections import Counter
                name_counts = Counter(item_names)
                duplicates = {name: count for name, count in name_counts.items() if count > 1}
                print(f"🔄 Duplicate items: {duplicates}")
            else:
                print("✅ No duplicate items detected")
            
            print(f"\n📝 SELECTED ITEMS ANALYSIS:")
            for i, item in enumerate(items):
                print(f"  {i+1}. {item.get('name')} ({item.get('type')})")
                
                # Check if this is the problematic dress shirt
                if "dress shirt" in item.get('name', '').lower():
                    print(f"     ⚠️  PROBLEMATIC ITEM DETECTED!")
                    print(f"     ❌ This is a dress shirt selected for athletic wear")
                    print(f"     🔍 Let's analyze why this was chosen...")
                    
                    # Find the original wardrobe item
                    original_item = None
                    for wardrobe_item in payload['wardrobe']:
                        if wardrobe_item['id'] == item.get('id'):
                            original_item = wardrobe_item
                            break
                    
                    if original_item:
                        print(f"     📋 Original item details:")
                        print(f"        Occasions: {original_item['occasion']}")
                        print(f"        Style: {original_item['style']}")
                        print(f"        Tags: {original_item['tags']}")
                        print(f"        SubType: {original_item.get('subType', 'N/A')}")
                        
                        # Check if it has any athletic-related attributes
                        has_athletic_style = any('athletic' in style.lower() for style in original_item['style'])
                        has_athletic_tags = any('athletic' in tag.lower() for tag in original_item['tags'])
                        has_athletic_occasion = any('athletic' in occ.lower() or 'gym' in occ.lower() for occ in original_item['occasion'])
                        
                        print(f"        Has athletic style: {'✅ YES' if has_athletic_style else '❌ NO'}")
                        print(f"        Has athletic tags: {'✅ YES' if has_athletic_tags else '❌ NO'}")
                        print(f"        Has athletic occasion: {'✅ YES' if has_athletic_occasion else '❌ NO'}")
                        
                        if not any([has_athletic_style, has_athletic_tags, has_athletic_occasion]):
                            print(f"     🚨 CONCLUSION: This item has NO athletic attributes!")
                            print(f"     🚨 It should have been filtered out by occasion filtering!")
                            print(f"     🚨 This indicates a BUG in the backend filtering logic!")
                
                # Check if this is the "White Leather Sneakers" item
                if "White Leather Sneakers" in item.get('name', ''):
                    print(f"     ⚠️  This is the 'White Leather Sneakers' item - type: {item.get('type')}")
                    if item.get('type') != 'sneakers':
                        print(f"     ❌ ERROR: Type mismatch! Expected 'sneakers', got '{item.get('type')}'")
            
            # Check for inappropriate items for athletic wear
            inappropriate_items = []
            for item in items:
                item_name = item.get('name', '').lower()
                item_type = item.get('type', '').lower()
                if any(term in item_name for term in ['dress shirt', 'dress pants', 'formal', 'business', 'slacks']) or \
                   any(term in item_type for term in ['dress_shirt', 'dress_pants', 'formal']):
                    inappropriate_items.append(item.get('name'))
            
            if inappropriate_items:
                print(f"\n⚠️  WARNING: Inappropriate items for athletic wear: {inappropriate_items}")
                print(f"🔍 This confirms the filtering logic is not working correctly!")
            else:
                print("✅ All items are appropriate for athletic wear")
            
            # Check temperature filtering
            sweater_items = [item for item in items if 'sweater' in item.get('type', '').lower()]
            if sweater_items and payload['weather']['temperature'] >= 75:
                print(f"⚠️  WARNING: Sweaters selected for warm weather ({payload['weather']['temperature']}°F): {[item.get('name') for item in sweater_items]}")
            else:
                print("✅ Temperature filtering working correctly")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_outfit_generation_debug() 