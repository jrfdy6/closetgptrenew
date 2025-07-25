#!/usr/bin/env python3
"""
Debug script to test why shorts and sandals aren't being found for hot weather outfits
"""

import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.outfit_generation_service import OutfitGenerationService
from custom_types.wardrobe import ClothingItem, ClothingType, Color
from custom_types.weather import WeatherData
from custom_types.profile import UserProfile
import time

def create_test_wardrobe_with_shorts_and_sandals():
    """Create a test wardrobe that includes shorts and sandals."""
    now = int(time.time())
    return [
        ClothingItem(
            id="shorts1",
            name="Blue Shorts",
            type=ClothingType.SHORTS,
            color="blue",
            season=["summer", "spring"],
            imageUrl="test_shorts.jpg",
            tags=["casual", "summer"],
            style=["casual", "summer"],
            occasion=["casual", "beach", "hot weather"],
            dominantColors=[Color(name="blue", hex="#0000FF", rgb=[0, 0, 255])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])],
            userId="test_user",
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="sandals1", 
            name="Brown Sandals",
            type=ClothingType.SANDALS,
            color="brown",
            season=["summer", "spring"],
            imageUrl="test_sandals.jpg",
            tags=["casual", "summer"],
            style=["casual", "summer"],
            occasion=["casual", "beach", "hot weather"],
            dominantColors=[Color(name="brown", hex="#8B4513", rgb=[139, 69, 19])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])],
            userId="test_user",
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="shirt1",
            name="White T-Shirt",
            type=ClothingType.SHIRT,
            color="white", 
            season=["summer", "spring"],
            imageUrl="test_shirt.jpg",
            tags=["casual", "summer"],
            style=["casual", "summer"],
            occasion=["casual", "hot weather"],
            dominantColors=[Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])],
            matchingColors=[Color(name="black", hex="#000000", rgb=[0, 0, 0])],
            userId="test_user",
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="pants1",
            name="Black Pants",
            type=ClothingType.PANTS,
            color="black",
            season=["fall", "winter", "spring"],
            imageUrl="test_pants.jpg",
            tags=["casual", "formal"],
            style=["casual", "formal"],
            occasion=["casual", "formal"],
            dominantColors=[Color(name="black", hex="#000000", rgb=[0, 0, 0])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])],
            userId="test_user",
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="shoes1",
            name="Black Shoes",
            type=ClothingType.SHOES,
            color="black",
            season=["all"],
            imageUrl="test_shoes.jpg",
            tags=["casual", "formal"],
            style=["casual", "formal"],
            occasion=["casual", "formal"],
            dominantColors=[Color(name="black", hex="#000000", rgb=[0, 0, 0])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])],
            userId="test_user",
            createdAt=now,
            updatedAt=now
        )
    ]

async def debug_hot_weather_selection():
    """Debug the hot weather item selection process."""
    print("🔍 Debugging Hot Weather Item Selection")
    print("=" * 50)
    
    # Create test data
    wardrobe = create_test_wardrobe_with_shorts_and_sandals()
    weather = WeatherData(temperature=85, condition="sunny", location="test", humidity=60)
    user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        gender="male",
        bodyType="average",
        skinTone="medium",
        stylePreferences=["casual"],
        budget="medium",
        preferredBrands=["Nike"],
        createdAt=1640995200,
        updatedAt=1640995200
    )
    
    # Create service
    service = OutfitGenerationService()
    
    print("📋 Original Wardrobe Items:")
    for item in wardrobe:
        print(f"   - {item.name} (type: {item.type})")
    
    print("\n🔍 Step 1: Testing item type normalization")
    for item in wardrobe:
        normalized_type = service._normalize_item_type(item.type, item.name)
        print(f"   {item.name} ({item.type}) -> {normalized_type}")
    
    print("\n🔍 Step 2: Testing occasion filtering for 'hot weather'")
    filtered_items = service._select_appropriate_items(wardrobe, "hot weather", "casual")
    print(f"   Filtered items ({len(filtered_items)}):")
    for item in filtered_items:
        print(f"     - {item.name} ({item.type})")
    
    print("\n🔍 Step 3: Testing complete outfit generation")
    try:
        outfit = await service.generate_outfit(
            user_id="test_user",
            wardrobe=wardrobe,
            occasion="hot weather",
            weather=weather,
            user_profile=user_profile,
            style="casual"
        )
        
        print(f"   Generated outfit with {len(outfit.pieces)} pieces:")
        for piece in outfit.pieces:
            print(f"     - {piece.name} ({piece.type})")
        
        # Check if shorts and sandals were selected
        shorts_found = any("shorts" in piece.type.lower() or "shorts" in piece.name.lower() for piece in outfit.pieces)
        sandals_found = any("sandals" in piece.type.lower() or "sandals" in piece.name.lower() for piece in outfit.pieces)
        
        print(f"\n✅ Shorts found: {shorts_found}")
        print(f"✅ Sandals found: {sandals_found}")
        
        if not shorts_found:
            print("❌ PROBLEM: Shorts not found in outfit!")
        if not sandals_found:
            print("❌ PROBLEM: Sandals not found in outfit!")
            
    except Exception as e:
        print(f"❌ Error generating outfit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_hot_weather_selection()) 