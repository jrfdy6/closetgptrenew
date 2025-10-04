#!/usr/bin/env python3
"""
Comprehensive Stress Test for Outfit Generation System

Tests 100+ scenarios across multiple dimensions:
- Weather conditions (10°F to 95°F)
- Occasions (business, casual, formal, party, athletic, etc.)
- Styles (classic, casual, trendy, elegant, etc.)
- Moods (professional, relaxed, bold, etc.)
- Edge cases (missing data, extreme values, etc.)
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add backend to path for imports
sys.path.append('backend/src')

def test_outfit_generation_comprehensive():
    """Comprehensive stress test with 100+ scenarios"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Comprehensive wardrobe with diverse items
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
    
    # Preprocess the comprehensive wardrobe
    print("🔄 PREPROCESSING: Converting comprehensive wardrobe")
    preprocessed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(comprehensive_wardrobe)
    print(f"✅ PREPROCESSING SUCCESSFUL: {len(preprocessed_wardrobe)} items")
    
    # Define test scenarios across multiple dimensions
    temperatures = [10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95]
    occasions = ['business', 'casual', 'formal', 'party', 'athletic', 'everyday']
    styles = ['classic', 'casual', 'trendy', 'elegant', 'professional', 'relaxed']
    moods = ['professional', 'relaxed', 'bold', 'comfortable', 'sophisticated', 'energetic']
    weather_conditions = ['clear', 'cloudy', 'sunny', 'rainy', 'snowy', 'windy', 'hot', 'cold']
    
    # Generate comprehensive test scenarios
    test_scenarios = []
    
    # 1. TEMPERATURE STRESS TEST (12 scenarios)
    print("🌡️ GENERATING TEMPERATURE STRESS TEST...")
    for temp in temperatures:
        test_scenarios.append({
            'name': f'Temperature {temp}°F Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': temp, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'temperature'
        })
    
    # 2. OCCASION STRESS TEST (6 scenarios)
    print("🎭 GENERATING OCCASION STRESS TEST...")
    for occasion in occasions:
        test_scenarios.append({
            'name': f'{occasion.title()} Occasion Test',
            'occasion': occasion,
            'style': 'classic',
            'mood': 'professional',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'occasion'
        })
    
    # 3. STYLE STRESS TEST (6 scenarios)
    print("🎨 GENERATING STYLE STRESS TEST...")
    for style in styles:
        test_scenarios.append({
            'name': f'{style.title()} Style Test',
            'occasion': 'casual',
            'style': style,
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'style'
        })
    
    # 4. MOOD STRESS TEST (6 scenarios)
    print("😊 GENERATING MOOD STRESS TEST...")
    for mood in moods:
        test_scenarios.append({
            'name': f'{mood.title()} Mood Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': mood,
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'mood'
        })
    
    # 5. WEATHER CONDITION STRESS TEST (8 scenarios)
    print("🌤️ GENERATING WEATHER CONDITION STRESS TEST...")
    for condition in weather_conditions:
        temp = 85 if condition == 'hot' else 35 if condition == 'cold' else 70
        test_scenarios.append({
            'name': f'{condition.title()} Weather Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': temp, 'condition': condition},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'weather'
        })
    
    # 6. COMBINATION STRESS TEST (30 scenarios)
    print("🔄 GENERATING COMBINATION STRESS TEST...")
    combination_scenarios = [
        # Business combinations
        {'occasion': 'business', 'style': 'classic', 'temp': 65, 'condition': 'cloudy'},
        {'occasion': 'business', 'style': 'professional', 'temp': 75, 'condition': 'clear'},
        {'occasion': 'business', 'style': 'elegant', 'temp': 55, 'condition': 'rainy'},
        
        # Formal combinations
        {'occasion': 'formal', 'style': 'elegant', 'temp': 60, 'condition': 'clear'},
        {'occasion': 'formal', 'style': 'classic', 'temp': 50, 'condition': 'cloudy'},
        {'occasion': 'formal', 'style': 'professional', 'temp': 45, 'condition': 'cold'},
        
        # Casual combinations
        {'occasion': 'casual', 'style': 'casual', 'temp': 80, 'condition': 'sunny'},
        {'occasion': 'casual', 'style': 'relaxed', 'temp': 75, 'condition': 'clear'},
        {'occasion': 'casual', 'style': 'trendy', 'temp': 85, 'condition': 'hot'},
        
        # Athletic combinations
        {'occasion': 'athletic', 'style': 'sporty', 'temp': 70, 'condition': 'clear'},
        {'occasion': 'athletic', 'style': 'athletic', 'temp': 80, 'condition': 'sunny'},
        {'occasion': 'athletic', 'style': 'active', 'temp': 65, 'condition': 'cloudy'},
        
        # Party combinations
        {'occasion': 'party', 'style': 'elegant', 'temp': 65, 'condition': 'clear'},
        {'occasion': 'party', 'style': 'trendy', 'temp': 70, 'condition': 'clear'},
        {'occasion': 'party', 'style': 'bold', 'temp': 60, 'condition': 'cloudy'},
        
        # Everyday combinations
        {'occasion': 'everyday', 'style': 'casual', 'temp': 72, 'condition': 'clear'},
        {'occasion': 'everyday', 'style': 'comfortable', 'temp': 68, 'condition': 'cloudy'},
        {'occasion': 'everyday', 'style': 'relaxed', 'temp': 76, 'condition': 'sunny'},
        
        # Extreme weather combinations
        {'occasion': 'casual', 'style': 'casual', 'temp': 95, 'condition': 'hot'},
        {'occasion': 'casual', 'style': 'casual', 'temp': 15, 'condition': 'cold'},
        {'occasion': 'business', 'style': 'professional', 'temp': 90, 'condition': 'hot'},
        {'occasion': 'formal', 'style': 'elegant', 'temp': 20, 'condition': 'cold'},
        
        # Edge case combinations
        {'occasion': 'business', 'style': 'casual', 'temp': 70, 'condition': 'clear'},  # Mixed occasion/style
        {'occasion': 'casual', 'style': 'formal', 'temp': 70, 'condition': 'clear'},   # Contradictory
        {'occasion': 'athletic', 'style': 'elegant', 'temp': 70, 'condition': 'clear'}, # Mismatch
        {'occasion': 'party', 'style': 'professional', 'temp': 70, 'condition': 'clear'}, # Mixed
        {'occasion': 'formal', 'style': 'athletic', 'temp': 70, 'condition': 'clear'}, # Contradictory
        {'occasion': 'everyday', 'style': 'trendy', 'temp': 70, 'condition': 'clear'}, # Mixed
        {'occasion': 'casual', 'style': 'sophisticated', 'temp': 70, 'condition': 'clear'}, # Mixed
        {'occasion': 'business', 'style': 'relaxed', 'temp': 70, 'condition': 'clear'}, # Mixed
        {'occasion': 'athletic', 'style': 'casual', 'temp': 70, 'condition': 'clear'}, # Compatible
        {'occasion': 'party', 'style': 'casual', 'temp': 70, 'condition': 'clear'}   # Compatible
    ]
    
    for i, combo in enumerate(combination_scenarios):
        test_scenarios.append({
            'name': f'Combo {i+1}: {combo["occasion"].title()} + {combo["style"].title()} + {combo["temp"]}°F',
            'occasion': combo['occasion'],
            'style': combo['style'],
            'mood': 'comfortable',
            'weather': {'temperature': combo['temp'], 'condition': combo['condition']},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'category': 'combination'
        })
    
    # 7. EDGE CASE STRESS TEST (20 scenarios)
    print("⚠️ GENERATING EDGE CASE STRESS TEST...")
    edge_cases = [
        # Missing data scenarios
        {'name': 'Missing Weather Data', 'weather': None},
        {'name': 'Missing User Profile', 'user_profile': None},
        {'name': 'Empty Occasion', 'occasion': ''},
        {'name': 'Empty Style', 'style': ''},
        {'name': 'Empty Mood', 'mood': ''},
        
        # Invalid data scenarios
        {'name': 'Invalid Temperature (-50°F)', 'weather': {'temperature': -50, 'condition': 'clear'}},
        {'name': 'Invalid Temperature (150°F)', 'weather': {'temperature': 150, 'condition': 'clear'}},
        {'name': 'Unknown Occasion', 'occasion': 'unknown_occasion'},
        {'name': 'Unknown Style', 'style': 'unknown_style'},
        {'name': 'Unknown Mood', 'mood': 'unknown_mood'},
        
        # Extreme combinations
        {'name': 'Business + Athletic + Hot', 'occasion': 'business', 'style': 'athletic', 'weather': {'temperature': 90, 'condition': 'hot'}},
        {'name': 'Formal + Casual + Cold', 'occasion': 'formal', 'style': 'casual', 'weather': {'temperature': 10, 'condition': 'cold'}},
        {'name': 'Party + Professional + Rain', 'occasion': 'party', 'style': 'professional', 'weather': {'temperature': 60, 'condition': 'rainy'}},
        {'name': 'Athletic + Elegant + Snow', 'occasion': 'athletic', 'style': 'elegant', 'weather': {'temperature': 25, 'condition': 'snowy'}},
        
        # Boundary conditions
        {'name': 'Boundary Hot (74°F)', 'weather': {'temperature': 74, 'condition': 'clear'}},
        {'name': 'Boundary Hot (76°F)', 'weather': {'temperature': 76, 'condition': 'clear'}},
        {'name': 'Boundary Cold (44°F)', 'weather': {'temperature': 44, 'condition': 'clear'}},
        {'name': 'Boundary Cold (46°F)', 'weather': {'temperature': 46, 'condition': 'clear'}},
        
        # Special characters
        {'name': 'Special Chars in Occasion', 'occasion': 'busi-ness!'},
        {'name': 'Numbers in Style', 'style': 'style123'}
    ]
    
    for edge_case in edge_cases:
        # Set defaults for edge cases
        test_scenarios.append({
            'name': edge_case['name'],
            'occasion': edge_case.get('occasion', 'casual'),
            'style': edge_case.get('style', 'casual'),
            'mood': edge_case.get('mood', 'comfortable'),
            'weather': edge_case.get('weather', {'temperature': 70, 'condition': 'clear'}),
            'user_profile': edge_case.get('user_profile', {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}),
            'category': 'edge_case'
        })
    
    # 8. USER PROFILE STRESS TEST (12 scenarios)
    print("👤 GENERATING USER PROFILE STRESS TEST...")
    user_profiles = [
        {'bodyType': 'Petite', 'height': 'Short', 'weight': 'Light'},
        {'bodyType': 'Tall', 'height': 'Tall', 'weight': 'Heavy'},
        {'bodyType': 'Athletic', 'height': 'Average', 'weight': 'Average'},
        {'bodyType': 'Curvy', 'height': 'Average', 'weight': 'Heavy'},
        {'skinTone': 'Fair', 'height': 'Average', 'weight': 'Average'},
        {'skinTone': 'Dark', 'height': 'Average', 'weight': 'Average'},
        {'gender': 'Male', 'height': 'Average', 'weight': 'Average'},
        {'gender': 'Female', 'height': 'Average', 'weight': 'Average'},
        {'height': 'Very Short', 'weight': 'Very Light'},
        {'height': 'Very Tall', 'weight': 'Very Heavy'},
        {'weight': 'Underweight', 'height': 'Average'},
        {'weight': 'Overweight', 'height': 'Average'}
    ]
    
    for i, profile in enumerate(user_profiles):
        # Fill in missing fields with defaults
        full_profile = {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}
        full_profile.update(profile)
        
        test_scenarios.append({
            'name': f'User Profile {i+1}: {list(profile.keys())[0].title()} = {list(profile.values())[0]}',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': full_profile,
            'category': 'user_profile'
        })
    
    print(f"✅ GENERATED {len(test_scenarios)} COMPREHENSIVE TEST SCENARIOS")
    print(f"📊 Categories: Temperature({len(temperatures)}), Occasion({len(occasions)}), Style({len(styles)}), Mood({len(moods)}), Weather({len(weather_conditions)}), Combination({len(combination_scenarios)}), Edge Cases({len(edge_cases)}), User Profiles({len(user_profiles)})")
    
    # Run the comprehensive test
    print("\\n🚀 STARTING COMPREHENSIVE STRESS TEST")
    print("=" * 100)
    
    results = []
    start_time = datetime.now()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n🧪 SCENARIO {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"📋 Category: {scenario['category'].upper()}")
        print(f"📋 Config: {scenario['occasion']} + {scenario['style']} + {scenario['mood']}")
        if scenario['weather']:
            print(f"📋 Weather: {scenario['weather']['temperature']}°F, {scenario['weather']['condition']}")
        else:
            print(f"📋 Weather: None")
        
        data = {
            'occasion': scenario['occasion'],
            'style': scenario['style'],
            'mood': scenario['mood'],
            'weather': scenario['weather'],
            'wardrobe': preprocessed_wardrobe,
            'user_profile': scenario['user_profile']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                outfit_items = result.get('items', [])
                strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
                
                print(f"✅ SUCCESS")
                print(f"   Strategy: {strategy}")
                print(f"   Items: {len(outfit_items)}")
                
                # Show generated outfit
                for j, item in enumerate(outfit_items, 1):
                    print(f"   {j}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                results.append({
                    'scenario': scenario['name'],
                    'category': scenario['category'],
                    'success': True,
                    'strategy': strategy,
                    'items_count': len(outfit_items),
                    'outfit_items': outfit_items,
                    'error': None
                })
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
                results.append({
                    'scenario': scenario['name'],
                    'category': scenario['category'],
                    'success': False,
                    'strategy': None,
                    'items_count': 0,
                    'outfit_items': [],
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'scenario': scenario['name'],
                'category': scenario['category'],
                'success': False,
                'strategy': None,
                'items_count': 0,
                'outfit_items': [],
                'error': str(e)
            })
        
        # Add small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Comprehensive analysis
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\\n" + "=" * 100)
    print("📊 COMPREHENSIVE STRESS TEST RESULTS")
    print("=" * 100)
    
    total_tests = len(results)
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"⏱️  Test Duration: {duration}")
    print(f"📊 Total Scenarios: {total_tests}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"📈 Success Rate: {len(successful_tests)/total_tests*100:.1f}%")
    
    # Category analysis
    print(f"\\n📊 CATEGORY BREAKDOWN:")
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0}
        categories[cat]['total'] += 1
        if result['success']:
            categories[cat]['success'] += 1
    
    for category, stats in categories.items():
        success_rate = stats['success'] / stats['total'] * 100
        print(f"   {category.title()}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Strategy analysis
    print(f"\\n🎯 STRATEGY DISTRIBUTION:")
    strategies = {}
    for result in successful_tests:
        strategy = result['strategy']
        strategies[strategy] = strategies.get(strategy, 0) + 1
    
    for strategy, count in sorted(strategies.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(successful_tests) * 100
        print(f"   {strategy}: {count} ({percentage:.1f}%)")
    
    # Failure analysis
    if failed_tests:
        print(f"\\n❌ FAILURE ANALYSIS:")
        error_types = {}
        for result in failed_tests:
            error = result['error']
            error_type = error.split(':')[0] if ':' in error else error[:50]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {error_type}: {count} failures")
        
        print(f"\\n🔍 DETAILED FAILURES:")
        for result in failed_tests[:10]:  # Show first 10 failures
            print(f"   • {result['scenario']} ({result['category']}): {result['error']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"stress_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'duration_seconds': duration.total_seconds(),
            'total_tests': total_tests,
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests)/total_tests*100,
            'categories': categories,
            'strategies': strategies,
            'error_types': error_types if failed_tests else {},
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\\n💾 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    test_outfit_generation_comprehensive()



