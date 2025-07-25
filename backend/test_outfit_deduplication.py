#!/usr/bin/env python3

import requests
import json
import time

def test_outfit_deduplication():
    """Test outfit generation to ensure no duplicate items are created."""
    
    # Create a test wardrobe with various items
    test_wardrobe = [
        {
            "id": "shirt-1",
            "name": "Blue Polo Shirt",
            "type": "shirt",
            "color": "blue",
            "season": ["spring", "summer"],
            "style": ["casual"],
            "occasion": ["casual"],
            "imageUrl": "https://example.com/shirt1.jpg",
            "tags": ["cotton"],
            "dominantColors": [{"name": "blue", "hex": "#0000FF"}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        },
        {
            "id": "shirt-2", 
            "name": "White Dress Shirt",
            "type": "shirt",
            "color": "white",
            "season": ["all"],
            "style": ["formal"],
            "occasion": ["business", "formal"],
            "imageUrl": "https://example.com/shirt2.jpg",
            "tags": ["cotton"],
            "dominantColors": [{"name": "white", "hex": "#FFFFFF"}],
            "matchingColors": [{"name": "black", "hex": "#000000"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        },
        {
            "id": "pants-1",
            "name": "Black Dress Pants",
            "type": "pants",
            "color": "black",
            "season": ["all"],
            "style": ["formal"],
            "occasion": ["business", "formal"],
            "imageUrl": "https://example.com/pants1.jpg",
            "tags": ["cotton"],
            "dominantColors": [{"name": "black", "hex": "#000000"}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        },
        {
            "id": "pants-2",
            "name": "Blue Jeans",
            "type": "pants",
            "color": "blue",
            "season": ["all"],
            "style": ["casual"],
            "occasion": ["casual"],
            "imageUrl": "https://example.com/pants2.jpg",
            "tags": ["denim"],
            "dominantColors": [{"name": "blue", "hex": "#0000FF"}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        },
        {
            "id": "shoes-1",
            "name": "Black Dress Shoes",
            "type": "shoes",
            "color": "black",
            "season": ["all"],
            "style": ["formal"],
            "occasion": ["business", "formal"],
            "imageUrl": "https://example.com/shoes1.jpg",
            "tags": ["leather"],
            "dominantColors": [{"name": "black", "hex": "#000000"}],
            "matchingColors": [{"name": "brown", "hex": "#8B4513"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        },
        {
            "id": "jacket-1",
            "name": "Blue Blazer",
            "type": "jacket",
            "color": "blue",
            "season": ["spring", "fall"],
            "style": ["business casual"],
            "occasion": ["business", "business casual"],
            "imageUrl": "https://example.com/jacket1.jpg",
            "tags": ["cotton"],
            "dominantColors": [{"name": "blue", "hex": "#0000FF"}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF"}],
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "userId": "test-user"
        }
    ]
    
    # Create test payload
    payload = {
        "occasion": "casual",
        "weather": {
            "temperature": 76.1,
            "condition": "Clear",
            "humidity": 60
        },
        "wardrobe": test_wardrobe,
        "user_profile": {
            "id": "test-user",
            "name": "Test User",
            "email": "test@example.com",
            "bodyType": "athletic",
            "createdAt": int(time.time()),
            "updatedAt": int(time.time())
        },
        "likedOutfits": [],
        "trendingStyles": []
    }
    
    try:
        print("🧪 Testing outfit generation with deduplication...")
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
                return False
            else:
                print("✅ No duplicate items detected")
            
            # Check for duplicate categories
            categories = []
            for item in items:
                item_type = item.get('type', '').lower()
                if 'shirt' in item_type or 'polo' in item_type:
                    categories.append('top')
                elif 'pants' in item_type or 'jeans' in item_type:
                    categories.append('bottom')
                elif 'shoes' in item_type or 'sneakers' in item_type:
                    categories.append('shoes')
                elif 'jacket' in item_type or 'coat' in item_type:
                    categories.append('layer')
                else:
                    categories.append('other')
            
            unique_categories = list(set(categories))
            if len(categories) != len(unique_categories):
                print("⚠️  WARNING: Duplicate categories detected!")
                from collections import Counter
                cat_counts = Counter(categories)
                duplicate_cats = {cat: count for cat, count in cat_counts.items() if count > 1}
                print(f"🔄 Duplicate categories: {duplicate_cats}")
                return False
            else:
                print("✅ No duplicate categories detected")
            
            print(f"\n📝 SELECTED ITEMS:")
            for i, item in enumerate(items, 1):
                print(f"   {i}. {item.get('name')} ({item.get('type')})")
            
            print(f"\n🎉 TEST PASSED: Outfit generation with deduplication working correctly!")
            return True
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_outfit_deduplication() 