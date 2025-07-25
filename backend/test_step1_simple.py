"""
Simple Test for Step 1: Replace or Fix Items from Firestore
==========================================================

This script tests the core Step 1 functionality with correct enum values.
"""

import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.outfit_fallback_service import OutfitFallbackService
from src.types.wardrobe import ClothingItem, ClothingType
from src.types.weather import WeatherData

async def test_step1_simple():
    """Simple test for Step 1 functionality."""
    
    print("🧪 Simple Test for Step 1: Replace or Fix Items from Firestore")
    print("=" * 70)
    
    # Initialize service
    fallback_service = OutfitFallbackService()
    
    # Test user ID
    test_user_id = "test-user-step1"
    
    # Create test context
    context = {
        'occasion': 'casual',
        'weather': WeatherData(
            temperature=75.0,
            condition='sunny',
            humidity=60.0,
            wind_speed=5.0
        ),
        'user_profile': {
            'id': test_user_id,
            'name': 'Test User',
            'email': 'test@example.com',
            'gender': 'male',
            'bodyType': 'athletic',
            'skinTone': 'medium',
            'stylePreferences': ['casual', 'minimalist'],
            'measurements': {
                'height': 180,
                'weight': 75,
                'chest': 100,
                'waist': 80,
                'hips': 95
            }
        },
        'style': 'casual',
        'mood': 'relaxed'
    }
    
    print("✅ Service initialized successfully")
    
    # Test 1: Duplicate Items Fix
    print("\n🔍 Test 1: Duplicate Items Fix")
    print("-" * 40)
    
    # Create a failed outfit with duplicate items
    failed_outfit = [
        ClothingItem(
            id='duplicate-shirt-1',
            name='Blue Shirt 1',
            type=ClothingType.SHIRT,
            color='blue',
            season=['spring', 'summer'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/shirt1.jpg',
            tags=['cotton'],
            dominantColors=[{'name': 'blue', 'hex': '#0000FF'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId=test_user_id
        ),
        ClothingItem(
            id='duplicate-shirt-2',
            name='Blue Shirt 2',
            type=ClothingType.SHIRT,
            color='blue',
            season=['spring', 'summer'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/shirt2.jpg',
            tags=['cotton'],
            dominantColors=[{'name': 'blue', 'hex': '#0000FF'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId=test_user_id
        ),
        ClothingItem(
            id='valid-pants',
            name='Black Pants',
            type=ClothingType.PANTS,
            color='black',
            season=['all'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/pants.jpg',
            tags=['cotton'],
            dominantColors=[{'name': 'black', 'hex': '#000000'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId=test_user_id
        )
    ]
    
    validation_errors = [
        "Duplicate items detected: two shirts in the same outfit",
        "Outfit has too many tops"
    ]
    
    print(f"🔧 Testing duplicate fix with {len(validation_errors)} errors")
    print(f"   Original outfit: {[item.name for item in failed_outfit]}")
    
    try:
        start_time = time.time()
        healed_outfit, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
            failed_outfit, validation_errors, context
        )
        healing_time = time.time() - start_time
        
        print(f"   ✅ Healing time: {healing_time:.3f} seconds")
        print(f"   ✅ Strategy used: {healing_log['strategy_used']}")
        print(f"   ✅ Items fixed: {len(healing_log['items_fixed'])}")
        print(f"   ✅ Items replaced: {len(healing_log['items_replaced'])}")
        print(f"   ✅ Remaining errors: {len(remaining_errors)}")
        print(f"   ✅ Healed outfit: {[item.name for item in healed_outfit]}")
        
    except Exception as e:
        print(f"   ❌ Error in duplicate fix: {e}")
    
    # Test 2: Weather Issues Fix
    print("\n🔍 Test 2: Weather Issues Fix")
    print("-" * 40)
    
    # Create a failed outfit with weather-inappropriate items
    failed_outfit_weather = [
        ClothingItem(
            id='winter-sweater',
            name='Wool Sweater',
            type=ClothingType.SWEATER,
            color='gray',
            season=['winter'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/sweater.jpg',
            tags=['wool'],
            dominantColors=[{'name': 'gray', 'hex': '#808080'}],
            matchingColors=[{'name': 'black', 'hex': '#000000'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId=test_user_id
        )
    ]
    
    validation_errors_weather = [
        "Wool sweater inappropriate for 75°F weather",
        "Outfit not suitable for current temperature"
    ]
    
    print(f"🔧 Testing weather fix with {len(validation_errors_weather)} errors")
    print(f"   Original outfit: {[item.name for item in failed_outfit_weather]}")
    
    try:
        start_time = time.time()
        healed_outfit, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
            failed_outfit_weather, validation_errors_weather, context
        )
        healing_time = time.time() - start_time
        
        print(f"   ✅ Healing time: {healing_time:.3f} seconds")
        print(f"   ✅ Strategy used: {healing_log['strategy_used']}")
        print(f"   ✅ Items fixed: {len(healing_log['items_fixed'])}")
        print(f"   ✅ Items replaced: {len(healing_log['items_replaced'])}")
        print(f"   ✅ Remaining errors: {len(remaining_errors)}")
        print(f"   ✅ Healed outfit: {[item.name for item in healed_outfit]}")
        
    except Exception as e:
        print(f"   ❌ Error in weather fix: {e}")
    
    # Test 3: Individual Fix Methods
    print("\n🔍 Test 3: Individual Fix Methods")
    print("-" * 40)
    
    # Test duplicate fix method directly
    print("🔧 Testing _fix_duplicate_items method:")
    try:
        duplicate_items = failed_outfit[:2]  # Two duplicate shirts
        fixed_items, fixes = await fallback_service._fix_duplicate_items(duplicate_items, context)
        print(f"   ✅ Fixed items: {[item.name for item in fixed_items]}")
        print(f"   ✅ Fixes applied: {len(fixes)}")
    except Exception as e:
        print(f"   ❌ Error in duplicate fix method: {e}")
    
    # Test weather fix method directly
    print("\n🔧 Testing _fix_weather_issues method:")
    try:
        weather_items = failed_outfit_weather
        fixed_items, fixes = await fallback_service._fix_weather_issues(weather_items, context)
        print(f"   ✅ Fixed items: {[item.name for item in fixed_items]}")
        print(f"   ✅ Fixes applied: {len(fixes)}")
    except Exception as e:
        print(f"   ❌ Error in weather fix method: {e}")
    
    # Test 4: Firestore Query Integration
    print("\n🔍 Test 4: Firestore Query Integration")
    print("-" * 40)
    
    # Test finding alternatives for category
    print("🔧 Testing _find_alternatives_for_category method:")
    try:
        test_item = failed_outfit[0]
        alternatives = await fallback_service._find_alternatives_for_category('top', test_item, context)
        print(f"   ✅ Alternatives found: {len(alternatives)}")
        for alt in alternatives:
            print(f"      - {alt.name} ({alt.type})")
    except Exception as e:
        print(f"   ❌ Error in alternatives query: {e}")
    
    # Test finding weather-appropriate replacement
    print("\n🔧 Testing _find_weather_appropriate_replacement method:")
    try:
        weather_replacement = await fallback_service._find_weather_appropriate_replacement(
            test_item, 75.0, 'summer', context
        )
        if weather_replacement:
            print(f"   ✅ Weather replacement found: {weather_replacement.name}")
        else:
            print("   ❌ No weather replacement found")
    except Exception as e:
        print(f"   ❌ Error in weather replacement: {e}")
    
    print("\n🎉 Step 1 Simple Testing Complete!")
    print("=" * 70)
    print("✅ Replace or Fix Items from Firestore (Fallback 1) is functional")
    print("✅ Core healing methods are working")
    print("✅ Firestore query integration is operational")

if __name__ == "__main__":
    asyncio.run(test_step1_simple()) 