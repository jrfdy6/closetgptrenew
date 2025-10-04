#!/usr/bin/env python3
"""
Debug System Regression After Mood Fix

Test simple scenarios to understand why the system broke after fixing mood filtering.
"""

import sys
sys.path.append('backend/src')

def test_simple_scenario():
    """Test a simple scenario that should work"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    # Simple wardrobe that should work
    simple_wardrobe = [
        {
            'id': 'shirt_white',
            'name': 'White Cotton T-Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Uniqlo',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'minimalist'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [65, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': True,
            'usage_count': 40,
            'wearCount': 35
        },
        {
            'id': 'pants_jeans',
            'name': 'Dark Blue Jeans',
            'type': 'pants',
            'color': 'Dark Blue',
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['casual', 'classic'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [50, 85],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': True,
            'usage_count': 45,
            'wearCount': 40
        },
        {
            'id': 'shoes_sneakers',
            'name': 'White Sneakers',
            'type': 'shoes',
            'color': 'White',
            'brand': 'Nike',
            'occasion': ['casual', 'athletic', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'athletic'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [50, 90],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': True,
            'usage_count': 50,
            'wearCount': 45
        }
    ]
    
    print("🔍 TESTING SIMPLE SCENARIO")
    print("=" * 60)
    
    # Preprocess the wardrobe
    print("🔄 PREPROCESSING WARDROBE:")
    processed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(simple_wardrobe)
    
    print(f"✅ Processed {len(processed_wardrobe)} items")
    
    # Show the processed items
    for i, item in enumerate(processed_wardrobe, 1):
        print(f"\\n📋 ITEM {i}: {item['name']}")
        print(f"   Type: {item['type']}")
        print(f"   Occasion: {item.get('occasion', [])}")
        print(f"   Style: {item.get('style', [])}")
        print(f"   Mood: {item.get('mood', [])}")
        print(f"   Tags: {item.get('tags', [])}")
    
    # Test the outfit generation API
    print(f"\\n🚀 TESTING OUTFIT GENERATION API:")
    
    import requests
    import json
    
    # Test simple casual scenario
    test_request = {
        "occasion": "casual",
        "style": "casual", 
        "mood": "comfortable",
        "weather": {
            "temperature": 70,
            "condition": "clear"
        },
        "wardrobe_items": processed_wardrobe,
        "user_profile": {
            "body_type": "average",
            "skin_tone": "medium",
            "gender": "male",
            "height": "average",
            "weight": "average"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:3001/api/outfits/generate",
            json=test_request,
            headers={"Authorization": "Bearer test"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Strategy: {result.get('metadata', {}).get('generation_strategy', 'unknown')}")
            print(f"   Items: {len(result.get('items', []))}")
            for item in result.get('items', []):
                print(f"     - {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
                
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
    
    return processed_wardrobe

if __name__ == "__main__":
    test_simple_scenario()



