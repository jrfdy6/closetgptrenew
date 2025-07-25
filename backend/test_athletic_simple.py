#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Import the services without Firebase
from services.outfit_service import OutfitService
from types.weather import WeatherData
from types.profile import UserProfile
from types.wardrobe import ClothingItem, ClothingType, Color
from types.outfit_rules import get_weather_rule

def test_athletic_filtering():
    """Test that athletic filtering works correctly for 70°F weather."""
    print("🧪 Testing athletic filtering for 70°F weather...")
    
    # Create outfit service (without Firebase initialization)
    outfit_service = OutfitService()
    
    # Create sample wardrobe items
    wardrobe = [
        ClothingItem(
            id="sweater-1",
            name="Cable knit sweater",
            type=ClothingType.SWEATER,
            style=["casual", "preppy"],
            occasion=["casual", "business casual"],
            dominantColors=[{"name": "gray", "hex": "#808080"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            color="gray",
            season=["winter", "fall"],
            tags=["warm", "cozy"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="shirt-1",
            name="Cotton t-shirt",
            type=ClothingType.SHIRT,
            style=["casual", "athletic"],
            occasion=["casual", "athletic", "gym"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            color="white",
            season=["all"],
            tags=["comfortable", "breathable"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="pants-1",
            name="Dress pants",
            type=ClothingType.PANTS,
            style=["formal", "business"],
            occasion=["formal", "business"],
            dominantColors=[{"name": "black", "hex": "#000000"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            color="black",
            season=["all"],
            tags=["formal", "professional"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="shorts-1",
            name="Athletic shorts",
            type=ClothingType.SHORTS,
            style=["athletic", "sporty"],
            occasion=["athletic", "gym", "casual"],
            dominantColors=[{"name": "black", "hex": "#000000"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            color="black",
            season=["summer", "spring"],
            tags=["athletic", "comfortable"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="shoes-1",
            name="Dress shoes",
            type=ClothingType.SHOES,
            style=["formal", "business"],
            occasion=["formal", "business"],
            dominantColors=[{"name": "black", "hex": "#000000"}],
            matchingColors=[{"name": "brown", "hex": "#8B4513"}],
            color="black",
            season=["all"],
            tags=["formal", "professional"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="sneakers-1",
            name="Running sneakers",
            type=ClothingType.SNEAKERS,
            style=["athletic", "sporty"],
            occasion=["athletic", "gym", "casual"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            color="white",
            season=["all"],
            tags=["athletic", "comfortable"],
            userId="test-user",
            imageUrl="test.jpg",
            createdAt=1640995200,
            updatedAt=1640995200
        )
    ]
    
    # Create test data
    weather = WeatherData(temperature=70.0, condition='sunny', humidity=50)
    user_profile = UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        gender="male",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual", "classic"],
        budget="medium",
        favoriteBrands=["Nike", "Adidas"],
        createdAt=1640995200,
        updatedAt=1640995200
    )
    
    # Test 1: Check temperature filtering
    print("\n🔍 Test 1: Testing temperature filtering...")
    weather_rule = get_weather_rule(weather.temperature)
    print(f"✅ Weather rule: {weather_rule.required_layers} layers required")
    print(f"   Temperature range: {weather_rule.min_temperature}-{weather_rule.max_temperature}°F")
    
    # Test temperature filtering on tops
    top_items = [item for item in wardrobe if item.type in [ClothingType.SHIRT, ClothingType.SWEATER]]
    print(f"✅ Available top items: {[item.name for item in top_items]}")
    
    filtered_tops = outfit_service._filter_items_by_temperature(top_items, weather_rule, "Athletic / Gym")
    print(f"✅ Top items after temperature filtering: {[item.name for item in filtered_tops]}")
    
    # Test 2: Check occasion filtering
    print("\n🔍 Test 2: Testing occasion filtering...")
    all_items = wardrobe.copy()
    filtered_items = outfit_service._filter_items_for_occasion_and_style(all_items, "Athletic / Gym", "Preppy")
    print(f"✅ Items after occasion filtering: {[item.name for item in filtered_items]}")
    
    # Test 3: Test outfit composition
    print("\n🔍 Test 3: Testing outfit composition...")
    selected_items = outfit_service._compose_outfit_with_limits(
        wardrobe=wardrobe,
        occasion="Athletic / Gym",
        style="Preppy",
        mood_rule=None,
        user_profile=user_profile,
        layering_rule=weather_rule,
        trendingStyles=[],
        likedOutfits=[],
        baseItem=None
    )
    print(f"✅ Composition result: {len(selected_items)} items selected")
    for item in selected_items:
        print(f"   - {item.name} ({item.type})")
    
    # Test 4: Verify athletic requirements
    print("\n🔍 Test 4: Verifying athletic requirements...")
    
    # Check for forbidden items
    sweater_items = [item for item in selected_items if item.type == ClothingType.SWEATER]
    dress_pants_items = [item for item in selected_items if item.type == ClothingType.PANTS]
    dress_shoes_items = [item for item in selected_items if item.type == ClothingType.SHOES]
    
    if sweater_items:
        print(f"❌ ERROR: Found sweater in athletic outfit: {[item.name for item in sweater_items]}")
        return False
    else:
        print("✅ SUCCESS: No sweaters selected for athletic outfit")
    
    if dress_pants_items:
        print(f"⚠️  WARNING: Found dress pants in athletic outfit: {[item.name for item in dress_pants_items]}")
    else:
        print("✅ SUCCESS: No dress pants selected for athletic outfit")
    
    if dress_shoes_items:
        print(f"⚠️  WARNING: Found dress shoes in athletic outfit: {[item.name for item in dress_shoes_items]}")
    else:
        print("✅ SUCCESS: No dress shoes selected for athletic outfit")
    
    # Check for preferred items
    shorts_items = [item for item in selected_items if item.type == ClothingType.SHORTS]
    sneakers_items = [item for item in selected_items if item.type == ClothingType.SNEAKERS]
    
    if shorts_items:
        print(f"✅ SUCCESS: Found shorts in athletic outfit: {[item.name for item in shorts_items]}")
    else:
        print("⚠️  WARNING: No shorts selected for athletic outfit")
    
    if sneakers_items:
        print(f"✅ SUCCESS: Found sneakers in athletic outfit: {[item.name for item in sneakers_items]}")
    else:
        print("⚠️  WARNING: No sneakers selected for athletic outfit")
    
    return True

if __name__ == "__main__":
    test_athletic_filtering() 