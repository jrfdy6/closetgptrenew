#!/usr/bin/env python3
"""
Debug Comprehensive Wardrobe

Test the comprehensive wardrobe directly to understand why it fails.
"""

import sys
sys.path.append('backend/src')

def test_comprehensive_wardrobe():
    """Test the comprehensive wardrobe directly"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    # Comprehensive wardrobe from the stress test
    comprehensive_wardrobe = [
        {
            'id': 'shirt_white_formal',
            'name': 'Classic White Button-Down Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Brooks Brothers',
            'occasion': ['business', 'formal'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'clean'],
            'temperature_range': [50, 80],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': True,
            'usage_count': 25,
            'wearCount': 20
        },
        {
            'id': 'shirt_blue_business',
            'name': 'Navy Blue Business Shirt',
            'type': 'shirt',
            'color': 'Navy Blue',
            'brand': 'Hugo Boss',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['professional', 'classic'],
            'mood': ['professional', 'serious'],
            'temperature_range': [45, 75],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 15,
            'wearCount': 12
        },
        {
            'id': 'shirt_polo_white',
            'name': 'White Polo Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Ralph Lauren',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'preppy'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [60, 90],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': True,
            'usage_count': 30,
            'wearCount': 25
        },
        {
            'id': 'shirt_tshirt_gray',
            'name': 'Light Gray Cotton T-Shirt',
            'type': 'shirt',
            'color': 'Gray',
            'brand': 'Uniqlo',
            'occasion': ['casual', 'everyday', 'athletic'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'minimalist'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [65, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 35,
            'wearCount': 30
        },
        {
            'id': 'shirt_athletic_moisture',
            'name': 'Moisture-Wicking Athletic Shirt',
            'type': 'shirt',
            'color': 'Black',
            'brand': 'Under Armour',
            'occasion': ['athletic', 'casual'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['athletic', 'sporty'],
            'mood': ['active', 'energetic'],
            'temperature_range': [60, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 15,
            'wearCount': 12
        },
        {
            'id': 'sweater_cashmere',
            'name': 'Cashmere Sweater',
            'type': 'sweater',
            'color': 'Gray',
            'brand': 'Brunello Cucinelli',
            'occasion': ['business', 'casual', 'formal'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'elegant', 'luxury'],
            'mood': ['sophisticated', 'warm'],
            'temperature_range': [30, 60],
            'weather_conditions': ['clear', 'cloudy', 'cold'],
            'favorite': True,
            'usage_count': 8,
            'wearCount': 6
        }
    ]
    
    print("🔍 TESTING COMPREHENSIVE WARDROBE")
    print("=" * 60)
    
    # Preprocess the wardrobe
    print("🔄 PREPROCESSING COMPREHENSIVE WARDROBE:")
    processed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(comprehensive_wardrobe)
    
    print(f"✅ Processed {len(processed_wardrobe)} items")
    
    # Show the processed items
    for i, item in enumerate(processed_wardrobe, 1):
        print(f"\\n📋 ITEM {i}: {item['name']}")
        print(f"   Type: {item['type']}")
        print(f"   Occasion: {item.get('occasion', [])}")
        print(f"   Style: {item.get('style', [])}")
        print(f"   Mood: {item.get('mood', [])}")
        print(f"   Tags: {item.get('tags', [])}")
    
    # Test the outfit generation API on Railway
    print(f"\\n🚀 TESTING OUTFIT GENERATION API ON RAILWAY:")
    
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
        "wardrobe": processed_wardrobe,
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
            "https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate",
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
    test_comprehensive_wardrobe()



