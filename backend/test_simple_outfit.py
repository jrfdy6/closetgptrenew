#!/usr/bin/env python3
"""Simple test to verify backend outfit generation works."""

import asyncio
import json
from src.services.outfit_service import OutfitService
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

async def test_simple_outfit():
    """Test basic outfit generation."""
    outfit_service = OutfitService()
    
    print("🧪 Simple Outfit Generation Test")
    print("=" * 40)
    
    # Create minimal test data
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=60,
        wind_speed=5
    )
    
    user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        gender="male",
        bodyType="athletic",
        body_type="athletic",
        skinTone="medium",
        skin_tone="medium",
        height=175,
        weight=70,
        age=25,
        createdAt=0,
        updatedAt=0
    )
    
    # Empty wardrobe to test fallback
    wardrobe = []
    
    print("📋 Test data:")
    print(f"  - Weather: {weather.temperature}°F, {weather.condition}")
    print(f"  - User: {user_profile.name}")
    print(f"  - Wardrobe: {len(wardrobe)} items")
    print(f"  - Occasion: casual")
    
    try:
        print("\n🎯 Generating outfit...")
        
        outfit = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"📋 Outfit details:")
        print(f"  - ID: {outfit.id}")
        print(f"  - Name: {outfit.name}")
        print(f"  - Items: {len(outfit.items)}")
        print(f"  - Success: {outfit.wasSuccessful}")
        
        if outfit.items:
            print(f"  - Selected items:")
            for item in outfit.items:
                print(f"    * {item.name} ({item.type})")
        else:
            print(f"  ❌ No items selected")
            
        return outfit.wasSuccessful
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_outfit())
    if result:
        print("\n✅ TEST PASSED: Backend outfit generation works!")
    else:
        print("\n❌ TEST FAILED: Backend has issues!") 