#!/usr/bin/env python3
"""
Debug Mood Filtering Inconsistency

Compare mood metadata between targeted test wardrobe and comprehensive wardrobe
to understand why mood filtering works in one but not the other.
"""

import sys
sys.path.append('backend/src')

def debug_mood_filtering():
    """Debug the mood filtering inconsistency"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    # TARGETED TEST WARDROBE (works - 66.7% success)
    targeted_wardrobe = [
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
    
    # COMPREHENSIVE TEST WARDROBE (fails - 0% success)
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
    
    print("🔍 DEBUGGING MOOD FILTERING INCONSISTENCY")
    print("=" * 80)
    
    # Preprocess both wardrobes
    print("🔄 PREPROCESSING TARGETED WARDROBE:")
    targeted_preprocessed = wardrobe_preprocessor.preprocess_wardrobe(targeted_wardrobe)
    
    print("🔄 PREPROCESSING COMPREHENSIVE WARDROBE:")
    comprehensive_preprocessed = wardrobe_preprocessor.preprocess_wardrobe(comprehensive_wardrobe)
    
    print(f"\\n📊 WARDROBE COMPARISON:")
    print(f"Targeted wardrobe: {len(targeted_preprocessed)} items")
    print(f"Comprehensive wardrobe: {len(comprehensive_preprocessed)} items")
    
    # Analyze mood data in both wardrobes
    print(f"\\n🎭 MOOD DATA ANALYSIS:")
    
    # Targeted wardrobe mood analysis
    print(f"\\n📋 TARGETED WARDROBE MOODS:")
    targeted_moods = set()
    for item in targeted_preprocessed:
        item_moods = item.get('mood', [])
        if isinstance(item_moods, str):
            item_moods = [item_moods]
        targeted_moods.update(item_moods)
        print(f"   {item['name']}: {item_moods}")
    
    # Comprehensive wardrobe mood analysis
    print(f"\\n📋 COMPREHENSIVE WARDROBE MOODS:")
    comprehensive_moods = set()
    for item in comprehensive_preprocessed:
        item_moods = item.get('mood', [])
        if isinstance(item_moods, str):
            item_moods = [item_moods]
        comprehensive_moods.update(item_moods)
        print(f"   {item['name']}: {item_moods}")
    
    # Compare mood coverage
    print(f"\\n🔍 MOOD COVERAGE COMPARISON:")
    print(f"Targeted wardrobe moods: {sorted(targeted_moods)}")
    print(f"Comprehensive wardrobe moods: {sorted(comprehensive_moods)}")
    
    # Test mood filtering logic
    print(f"\\n🧪 TESTING MOOD FILTERING LOGIC:")
    
    # Mood mappings from our fix
    mood_mappings = {
        'professional': ['serious', 'business', 'formal'],
        'relaxed': ['comfortable', 'casual', 'easy'],
        'bold': ['dramatic', 'striking', 'confident'],
        'comfortable': ['relaxed', 'easy', 'casual'],
        'sophisticated': ['elegant', 'refined', 'classic'],
        'energetic': ['active', 'dynamic', 'vibrant']
    }
    
    test_moods = ['professional', 'relaxed', 'bold', 'comfortable', 'sophisticated', 'energetic']
    
    for test_mood in test_moods:
        print(f"\\n🎯 Testing mood: '{test_mood}'")
        
        # Check targeted wardrobe
        targeted_matches = []
        for item in targeted_preprocessed:
            item_moods = item.get('mood', [])
            if isinstance(item_moods, str):
                item_moods = [item_moods]
            item_moods_lower = [m.lower() for m in item_moods]
            
            mood_compatible = False
            if test_mood.lower() in item_moods_lower:
                mood_compatible = True
            else:
                if test_mood.lower() in mood_mappings:
                    compatible_moods = mood_mappings[test_mood.lower()]
                    if any(compat_mood in item_moods_lower for compat_mood in compatible_moods):
                        mood_compatible = True
            
            if mood_compatible:
                targeted_matches.append(item['name'])
        
        # Check comprehensive wardrobe
        comprehensive_matches = []
        for item in comprehensive_preprocessed:
            item_moods = item.get('mood', [])
            if isinstance(item_moods, str):
                item_moods = [item_moods]
            item_moods_lower = [m.lower() for m in item_moods]
            
            mood_compatible = False
            if test_mood.lower() in item_moods_lower:
                mood_compatible = True
            else:
                if test_mood.lower() in mood_mappings:
                    compatible_moods = mood_mappings[test_mood.lower()]
                    if any(compat_mood in item_moods_lower for compat_mood in compatible_moods):
                        mood_compatible = True
            
            if mood_compatible:
                comprehensive_matches.append(item['name'])
        
        print(f"   Targeted matches: {len(targeted_matches)} - {targeted_matches}")
        print(f"   Comprehensive matches: {len(comprehensive_matches)} - {comprehensive_matches}")
        
        if len(comprehensive_matches) == 0 and len(targeted_matches) > 0:
            print(f"   🚨 ISSUE: Comprehensive wardrobe has NO matches for '{test_mood}' while targeted has {len(targeted_matches)}")
    
    # Check if comprehensive wardrobe has items with no mood data
    print(f"\\n⚠️ ITEMS WITH MISSING MOOD DATA:")
    for item in comprehensive_preprocessed:
        item_moods = item.get('mood', [])
        if not item_moods:
            print(f"   {item['name']}: NO MOOD DATA")
    
    return {
        'targeted_moods': sorted(targeted_moods),
        'comprehensive_moods': sorted(comprehensive_moods),
        'targeted_items': len(targeted_preprocessed),
        'comprehensive_items': len(comprehensive_preprocessed)
    }

if __name__ == "__main__":
    debug_mood_filtering()



