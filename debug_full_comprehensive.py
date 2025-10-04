#!/usr/bin/env python3
"""
Debug Full Comprehensive Wardrobe

Test the full comprehensive wardrobe with a casual scenario to understand the filtering issue.
"""

import sys
sys.path.append('backend/src')

def test_full_comprehensive_wardrobe():
    """Test the full comprehensive wardrobe with casual scenario"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    # Full comprehensive wardrobe (24 items)
    comprehensive_wardrobe = [
        # BUSINESS/FORMAL ITEMS
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
            'id': 'blazer_navy',
            'name': 'Navy Blue Blazer',
            'type': 'jacket',
            'color': 'Navy Blue',
            'brand': 'Calvin Klein',
            'occasion': ['business', 'formal', 'party'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['classic', 'professional', 'elegant'],
            'mood': ['professional', 'sophisticated'],
            'temperature_range': [40, 70],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': True,
            'usage_count': 8,
            'wearCount': 6
        },
        {
            'id': 'pants_dress_black',
            'name': 'Black Dress Pants',
            'type': 'pants',
            'color': 'Black',
            'brand': 'Hugo Boss',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'temperature_range': [40, 75],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 18,
            'wearCount': 15
        },
        {
            'id': 'pants_dress_gray',
            'name': 'Charcoal Gray Dress Pants',
            'type': 'pants',
            'color': 'Gray',
            'brand': 'Brooks Brothers',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['professional', 'classic'],
            'mood': ['professional', 'serious'],
            'temperature_range': [40, 75],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 12,
            'wearCount': 10
        },
        {
            'id': 'shoes_oxford_brown',
            'name': 'Brown Oxford Dress Shoes',
            'type': 'shoes',
            'color': 'Brown',
            'brand': 'Cole Haan',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'temperature_range': [30, 80],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': True,
            'usage_count': 20,
            'wearCount': 18
        },
        {
            'id': 'shoes_oxford_black',
            'name': 'Black Oxford Dress Shoes',
            'type': 'shoes',
            'color': 'Black',
            'brand': 'Allen Edmonds',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'temperature_range': [30, 80],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 15,
            'wearCount': 12
        },
        
        # CASUAL ITEMS
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
            'id': 'shirt_tshirt_white',
            'name': 'White Cotton T-Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Uniqlo',
            'occasion': ['casual', 'everyday', 'athletic'],
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
            'id': 'jeans_dark_blue',
            'name': 'Dark Blue Denim Jeans',
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
            'id': 'jeans_light_blue',
            'name': 'Light Blue Denim Jeans',
            'type': 'pants',
            'color': 'Light Blue',
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'relaxed'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [60, 90],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 25,
            'wearCount': 20
        },
        {
            'id': 'shorts_khaki',
            'name': 'Khaki Shorts',
            'type': 'shorts',
            'color': 'Khaki',
            'brand': 'J.Crew',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer'],
            'style': ['casual', 'preppy'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [70, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 20,
            'wearCount': 18
        },
        {
            'id': 'shoes_sneakers_white',
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
        },
        {
            'id': 'shoes_sneakers_black',
            'name': 'Black Sneakers',
            'type': 'shoes',
            'color': 'Black',
            'brand': 'Adidas',
            'occasion': ['casual', 'athletic', 'everyday'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['casual', 'athletic'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [45, 85],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 30,
            'wearCount': 25
        },
        
        # ATHLETIC ITEMS
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
            'id': 'shorts_athletic',
            'name': 'Athletic Running Shorts',
            'type': 'shorts',
            'color': 'Navy',
            'brand': 'Nike',
            'occasion': ['athletic'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['athletic', 'sporty'],
            'mood': ['active', 'energetic'],
            'temperature_range': [65, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 10,
            'wearCount': 8
        },
        {
            'id': 'shoes_running',
            'name': 'Running Shoes',
            'type': 'shoes',
            'color': 'Blue',
            'brand': 'Brooks',
            'occasion': ['athletic'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['athletic', 'sporty'],
            'mood': ['active', 'energetic'],
            'temperature_range': [40, 90],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': False,
            'usage_count': 12,
            'wearCount': 10
        },
        
        # WINTER ITEMS
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
        },
        {
            'id': 'jacket_winter',
            'name': 'Winter Jacket',
            'type': 'jacket',
            'color': 'Black',
            'brand': 'Canada Goose',
            'occasion': ['casual', 'everyday'],
            'season': ['winter'],
            'style': ['practical', 'warm'],
            'mood': ['warm', 'protective'],
            'temperature_range': [10, 45],
            'weather_conditions': ['cold', 'snow', 'wind'],
            'favorite': False,
            'usage_count': 5,
            'wearCount': 4
        },
        {
            'id': 'boots_winter',
            'name': 'Winter Boots',
            'type': 'shoes',
            'color': 'Brown',
            'brand': 'Sorel',
            'occasion': ['casual', 'everyday'],
            'season': ['winter'],
            'style': ['practical', 'warm'],
            'mood': ['warm', 'protective'],
            'temperature_range': [10, 45],
            'weather_conditions': ['cold', 'snow', 'rain'],
            'favorite': False,
            'usage_count': 3,
            'wearCount': 2
        },
        
        # SUMMER ITEMS
        {
            'id': 'shirt_linen_white',
            'name': 'White Linen Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Eileen Fisher',
            'occasion': ['casual', 'business'],
            'season': ['summer'],
            'style': ['casual', 'light'],
            'mood': ['light', 'breathable'],
            'temperature_range': [75, 95],
            'weather_conditions': ['clear', 'sunny', 'hot'],
            'favorite': True,
            'usage_count': 12,
            'wearCount': 10
        },
        {
            'id': 'shorts_linen',
            'name': 'Linen Shorts',
            'type': 'shorts',
            'color': 'Beige',
            'brand': 'J.Crew',
            'occasion': ['casual', 'everyday'],
            'season': ['summer'],
            'style': ['casual', 'light'],
            'mood': ['light', 'breathable'],
            'temperature_range': [75, 95],
            'weather_conditions': ['clear', 'sunny', 'hot'],
            'favorite': False,
            'usage_count': 8,
            'wearCount': 6
        },
        {
            'id': 'shoes_sandals',
            'name': 'Leather Sandals',
            'type': 'shoes',
            'color': 'Brown',
            'brand': 'Birkenstock',
            'occasion': ['casual', 'everyday'],
            'season': ['summer'],
            'style': ['casual', 'comfortable'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [70, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': False,
            'usage_count': 6,
            'wearCount': 5
        }
    ]
    
    print("🔍 TESTING FULL COMPREHENSIVE WARDROBE")
    print("=" * 60)
    
    # Preprocess the wardrobe
    print("🔄 PREPROCESSING FULL COMPREHENSIVE WARDROBE:")
    processed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(comprehensive_wardrobe)
    
    print(f"✅ Processed {len(processed_wardrobe)} items")
    
    # Count items by type
    type_counts = {}
    for item in processed_wardrobe:
        item_type = item['type']
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
    
    print(f"\\n📊 ITEM TYPE BREAKDOWN:")
    for item_type, count in type_counts.items():
        print(f"   {item_type}: {count} items")
    
    # Test the outfit generation API on Railway
    print(f"\\n🚀 TESTING CASUAL SCENARIO:")
    
    import requests
    import json
    
    # Test casual scenario
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
    test_full_comprehensive_wardrobe()



