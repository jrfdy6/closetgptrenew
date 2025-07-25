#!/usr/bin/env python3
"""
Test script to verify Gala + Old Money + warm weather filtering fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.types.wardrobe import ClothingItem, ClothingType
from src.types.profile import UserProfile
from src.types.weather import WeatherData
from src.services.outfit_service import OutfitService

def test_gala_old_money_fix():
    """Test that Gala + Old Money + 75.2°F weather produces appropriate formal outfits."""
    
    # Create test wardrobe with formal items
    wardrobe = [
        ClothingItem(
            id="dress-shirt",
            name="A slim, long, solid, smooth dress shirt by Reaction Kenneth Cole",
            type=ClothingType.DRESS_SHIRT,
            color="white",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business", "gala"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            tags=["formal", "business", "dress"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="short-shirt",
            name="A slim, short, solid, smooth shirt by Van Heusen",
            type=ClothingType.SHIRT,
            color="blue",
            season=["spring", "summer"],
            imageUrl="test.jpg",
            style=["casual", "business casual"],
            occasion=["casual", "business casual"],
            dominantColors=[{"name": "blue", "hex": "#0000FF"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["casual", "short sleeve"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="suit-pants",
            name="Navy Blue Suit Pants",
            type=ClothingType.PANTS,
            color="navy",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business", "gala"],
            dominantColors=[{"name": "navy", "hex": "#000080"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["formal", "business", "suit"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="blazer",
            name="Navy Blue Blazer",
            type=ClothingType.JACKET,
            color="navy",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business", "old money"],
            occasion=["formal", "business", "gala"],
            dominantColors=[{"name": "navy", "hex": "#000080"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["formal", "business", "blazer"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="dress-shoes",
            name="Black Oxford Dress Shoes",
            type=ClothingType.DRESS_SHOES,
            color="black",
            season=["all"],
            imageUrl="test.jpg",
            style=["formal", "business"],
            occasion=["formal", "business", "gala"],
            dominantColors=[{"name": "black", "hex": "#000000"}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            tags=["formal", "business", "oxford"],
            userId="test-user",
            createdAt=1640995200,
            updatedAt=1640995200
        ),
        ClothingItem(
            id="casual-shoes",
            name="A solid, smooth shoes",
            type=ClothingType.SHOES,
            color="brown",
            season=["all"],
            imageUrl="test.jpg",
            style=["casual"],
            occasion=["casual"],
            dominantColors=[{"name": "brown", "hex": "#8B4513"}],
            matchingColors=[{"name": "black", "hex": "#000000"}],
            tags=["casual", "shoes"],
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
        occasionPreferences=["formal", "gala"],
        colorPreferences=["navy", "black", "white"],
        brandPreferences=["Brooks Brothers"],
        budget="high",
        createdAt=1640995200,
        updatedAt=1640995200
    )
    
    # Create test weather (75.2°F - warm weather)
    weather = WeatherData(
        temperature=75.2,
        condition="sunny",
        humidity=60,
        windSpeed=5,
        location="Test City"
    )
    
    # Create outfit service
    service = OutfitService()
    
    print("🧪 Testing Gala + Old Money + 75.2°F weather filtering...")
    
    # Test refined pipeline
    result = service._generate_outfit_refined_pipeline(
        occasion="Gala",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="Old Money",
        mood="confident"
    )
    
    if result.get("success", False) and "items" in result:
        selected_items = result["items"]
        print(f"✅ Refined pipeline successful: {len(selected_items)} items selected")
        
        # Check for duplicate items
        item_ids = [item.id for item in selected_items]
        unique_ids = list(set(item_ids))
        if len(item_ids) != len(unique_ids):
            print("❌ ERROR: Duplicate items detected")
            return False
        else:
            print("✅ SUCCESS: No duplicate items")
        
        # Check for only one top
        tops = [item for item in selected_items if item.type in [ClothingType.SHIRT, ClothingType.DRESS_SHIRT]]
        if len(tops) > 1:
            print(f"❌ ERROR: Multiple tops selected: {len(tops)} tops")
            for top in tops:
                print(f"   - {top.name} ({top.type})")
            return False
        else:
            print(f"✅ SUCCESS: Only {len(tops)} top selected")
        
        # Check for no short-sleeve shirts in Gala
        short_sleeve = [item for item in selected_items if "short" in item.name.lower() and "sleeve" in item.name.lower()]
        if short_sleeve:
            print(f"❌ ERROR: Short-sleeve items in Gala outfit: {[item.name for item in short_sleeve]}")
            return False
        else:
            print("✅ SUCCESS: No short-sleeve items in Gala outfit")
        
        # Check for layer (blazer/jacket)
        layers = [item for item in selected_items if item.type in [ClothingType.JACKET]]
        if layers:
            print(f"✅ SUCCESS: Layer present: {[item.name for item in layers]}")
        else:
            print("⚠️  WARNING: No layer (blazer/jacket) in Gala outfit")
        
        # Check for dress shoes
        dress_shoes = [item for item in selected_items if item.type == ClothingType.DRESS_SHOES]
        if dress_shoes:
            print(f"✅ SUCCESS: Dress shoes selected: {[item.name for item in dress_shoes]}")
        else:
            print("⚠️  WARNING: No dress shoes in Gala outfit")
        
        print(f"\n📋 Selected items:")
        for item in selected_items:
            print(f"   - {item.name} ({item.type}) [Style: {item.style}]")
        
        return True
    else:
        print(f"❌ Refined pipeline failed: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_gala_old_money_fix()
    if success:
        print("\n🎉 All tests passed! Gala + Old Money filtering is working correctly.")
    else:
        print("\n❌ Tests failed. Issues remain.")
        sys.exit(1) 