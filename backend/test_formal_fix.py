#!/usr/bin/env python3
"""
Test script to verify Formal + Old Money + warm weather filtering fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.types.wardrobe import ClothingItem, ClothingType
from src.types.profile import UserProfile
from src.types.weather import WeatherData
from src.services.outfit_service import OutfitService

def test_formal_old_money_fix():
    """Test that Formal + Old Money + 74.7°F weather doesn't produce multiple tops."""
    
    # Create test wardrobe with problematic items
    wardrobe = [
        ClothingItem(
            id="dress-shirt",
            name="A slim, long, solid, smooth dress shirt",
            type=ClothingType.DRESS_SHIRT,
            color="white",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            tags=["formal", "business", "dress"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="polo",
            name="A slim, short, striped, smooth polo shirt by Van Heusen",
            type=ClothingType.SHIRT,
            color="blue",
            season=["spring", "summer"],
            imageUrl="test.jpg",
            style=["casual", "business casual"],
            occasion=["casual", "business casual"],
            dominantColors=[{"name": "blue", "hex": "#0000FF"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["casual", "polo"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="button-down",
            name="A loose, short, striped, smooth short sleeve button down by Croft & Barrow",
            type=ClothingType.SHIRT,
            color="blue",
            season=["spring", "summer"],
            imageUrl="test.jpg",
            style=["casual", "business casual"],
            occasion=["casual", "business casual"],
            dominantColors=[{"name": "blue", "hex": "#0000FF"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["casual", "button down"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="dress-pants",
            name="A slim, solid, smooth dress pants",
            type=ClothingType.PANTS,
            color="black",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business"],
            dominantColors=[{"name": "black", "hex": "#000000"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["formal", "business", "dress"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="oxford",
            name="A slim, brogue, smooth oxford shoes",
            type=ClothingType.DRESS_SHOES,
            color="brown",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business"],
            dominantColors=[{"name": "brown", "hex": "#8B4513"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            tags=["formal", "business", "oxford"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        )
    ]
    
    # Create test user profile
    user_profile = UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["old money", "formal"],
        occasionPreferences=["formal", "business"],
        colorPreferences=["white", "black", "navy"],
        brandPreferences=["Brooks Brothers"],
        budget="high",
        createdAt=1640995200,
        updatedAt=1640995200
    )
    
    # Create test weather (74.7°F - warm weather)
    weather = WeatherData(
        temperature=74.7,
        condition="sunny",
        humidity=60,
        windSpeed=5,
        location="Test City"
    )
    
    # Create outfit service
    service = OutfitService()
    
    print("🧪 Testing Formal + Old Money + 74.7°F weather filtering...")
    
    # Test refined pipeline
    result = service._generate_outfit_refined_pipeline(
        occasion="Formal",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="Old Money",
        mood="relaxed"
    )
    
    if result.get("success", False) and "items" in result:
        selected_items = result["items"]
        print(f"✅ Refined pipeline successful: {len(selected_items)} items selected")
        
        # Check for multiple tops
        tops = [item for item in selected_items if item.type in [ClothingType.SHIRT, ClothingType.DRESS_SHIRT]]
        if len(tops) > 1:
            print(f"❌ ERROR: Multiple tops selected: {len(tops)} tops")
            for top in tops:
                print(f"   - {top.name} ({top.type})")
            return False
        else:
            print(f"✅ SUCCESS: Only {len(tops)} top selected")
        
        # Check for casual items in formal outfit
        casual_items = [item for item in selected_items if "polo" in item.name.lower()]
        if casual_items:
            print(f"❌ ERROR: Casual items in formal outfit: {[item.name for item in casual_items]}")
            return False
        else:
            print("✅ SUCCESS: No casual items in formal outfit")
        
        # Check for duplicate items
        item_ids = [item.id for item in selected_items]
        unique_ids = list(set(item_ids))
        if len(item_ids) != len(unique_ids):
            print("❌ ERROR: Duplicate items detected")
            return False
        else:
            print("✅ SUCCESS: No duplicate items")
        
        print(f"\n📋 Selected items:")
        for item in selected_items:
            print(f"   - {item.name} ({item.type}) [Style: {item.style}]")
        
        return True
    else:
        print(f"❌ Refined pipeline failed: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_formal_old_money_fix()
    if success:
        print("\n🎉 All tests passed! Formal + Old Money filtering is working correctly.")
    else:
        print("\n❌ Tests failed. Issues remain.")
        sys.exit(1) 