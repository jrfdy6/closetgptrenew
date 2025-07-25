#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_service import OutfitService
from src.custom_types.wardrobe import ClothingItem, Color
from src.custom_types.profile import UserProfile
from src.custom_types.weather import WeatherData
# from src.custom_types.metadata import Metadata, ColorAnalysis

async def test_outfit_generation_fix():
    """Test if the Color object bug fix works"""
    
    print("🧪 Testing outfit generation fix...")
    
    # Create a test outfit service
    outfit_service = OutfitService()
    
    # Create test wardrobe items with Color objects
    test_wardrobe = []
    
    # Create test colors
    blue_color = Color(name="blue", hex="#0000FF", rgb=[0, 0, 255])
    red_color = Color(name="red", hex="#FF0000", rgb=[255, 0, 0])
    white_color = Color(name="white", hex="#FFFFFF", rgb=[255, 255, 255])
    
    # Create test items
    test_item1 = ClothingItem(
        id="test_item_1",
        name="Test Blue Shirt",
        type="shirt",
        color="blue",
        season=["spring", "summer"],
        style=["casual"],
        imageUrl="https://example.com/test1.jpg",
        tags=["casual", "cotton"],
        dominantColors=[blue_color],
        matchingColors=[white_color],
        occasion=["casual"],
        createdAt=int(asyncio.get_event_loop().time()),
        updatedAt=int(asyncio.get_event_loop().time()),
        userId="test_user"
    )
    
    test_item2 = ClothingItem(
        id="test_item_2",
        name="Test Red Pants",
        type="pants",
        color="red",
        season=["spring", "summer"],
        style=["casual"],
        imageUrl="https://example.com/test2.jpg",
        tags=["casual", "cotton"],
        dominantColors=[red_color],
        matchingColors=[white_color],
        occasion=["casual"],
        createdAt=int(asyncio.get_event_loop().time()),
        updatedAt=int(asyncio.get_event_loop().time()),
        userId="test_user"
    )
    
    test_wardrobe = [test_item1, test_item2]
    
    # Create test user profile
    user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        bodyType="average",
        skinTone="neutral",
        measurements={},
        stylePreferences=[],
        colorPalette={
            "primary": ["blue", "red"],
            "secondary": ["white"],
            "accent": [],
            "neutral": [],
            "avoid": []
        },
        stylePersonality={
            "classic": 0.5,
            "modern": 0.5,
            "creative": 0.5,
            "minimal": 0.5,
            "bold": 0.5
        },
        materialPreferences={
            "preferred": ["cotton"],
            "avoid": []
        },
        preferredBrands=[],
        createdAt=int(asyncio.get_event_loop().time()),
        updatedAt=int(asyncio.get_event_loop().time())
    )
    
    # Create test weather
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=50.0
    )
    
    try:
        print("🔄 Attempting to generate outfit...")
        
        # Try to generate an outfit
        result = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=test_wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        )
        
        print("✅ Outfit generation successful!")
        print(f"   Outfit name: {result.name}")
        print(f"   Items count: {len(result.items)}")
        print(f"   Was successful: {result.wasSuccessful}")
        
        if result.items:
            print("   Items:")
            for item in result.items:
                if isinstance(item, str):
                    print(f"     - {item} (ID)")
                else:
                    print(f"     - {item.name} ({item.type})")
        else:
            print("   ⚠️  No items selected")
            
    except Exception as e:
        print(f"❌ Outfit generation failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_outfit_generation_fix())
    if success:
        print("\n🎉 Color object bug fix test PASSED!")
    else:
        print("\n💥 Color object bug fix test FAILED!") 