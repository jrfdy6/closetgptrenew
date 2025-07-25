#!/usr/bin/env python3
"""Test script to verify outfit generation works with test data."""

import asyncio
import json
from src.services.outfit_service import OutfitService
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

async def test_outfit_generation():
    """Test outfit generation with a test user and wardrobe."""
    outfit_service = OutfitService()
    
    print("🧪 Testing Outfit Generation with Test Data")
    print("=" * 50)
    
    # Create test weather data
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=60,
        wind_speed=5
    )
    
    # Create test user profile
    user_profile = UserProfile(
        id="test_user_123",
        name="Test User",
        email="test@example.com",
        gender="female",
        bodyType="athletic",
        body_type="athletic",
        skinTone="medium",
        skin_tone="medium",
        height=165,
        weight=60,
        age=25,
        createdAt=0,
        updatedAt=0
    )
    
    # Create test wardrobe with basic items
    from src.custom_types.wardrobe import ClothingItem
    
    test_wardrobe = [
        ClothingItem(
            id="item_1",
            name="White T-Shirt",
            type="t-shirt",
            style=["casual"],
            occasion=["casual", "athletic"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            matchingColors=[{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
            color="white",
            season=["all"],
            imageUrl="test_tshirt.jpg",
            tags=["casual", "comfortable"],
            userId="test_user_123",
            createdAt=0,
            updatedAt=0,
            metadata={
                "analysisTimestamp": 0,
                "originalType": "t-shirt",
                "colorAnalysis": {
                    "dominantColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
                    "matchingColors": [{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "60",
                        "maxTemp": "85",
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["cotton"]
                    }
                }
            }
        ),
        ClothingItem(
            id="item_2",
            name="Blue Jeans",
            type="jeans",
            style=["casual"],
            occasion=["casual"],
            dominantColors=[{"name": "navy", "hex": "#000080", "r": 0, "g": 0, "b": 128}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            color="navy",
            season=["all"],
            imageUrl="test_jeans.jpg",
            tags=["casual", "denim"],
            userId="test_user_123",
            createdAt=0,
            updatedAt=0,
            metadata={
                "analysisTimestamp": 0,
                "originalType": "jeans",
                "colorAnalysis": {
                    "dominantColors": [{"name": "navy", "hex": "#000080", "r": 0, "g": 0, "b": 128}],
                    "matchingColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "50",
                        "maxTemp": "80",
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["cotton"]
                    }
                }
            }
        ),
        ClothingItem(
            id="item_3",
            name="White Sneakers",
            type="shoes",
            style=["casual"],
            occasion=["casual", "athletic"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            matchingColors=[{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
            color="white",
            season=["all"],
            imageUrl="test_sneakers.jpg",
            tags=["casual", "comfortable"],
            userId="test_user_123",
            createdAt=0,
            updatedAt=0,
            metadata={
                "analysisTimestamp": 0,
                "originalType": "shoes",
                "colorAnalysis": {
                    "dominantColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
                    "matchingColors": [{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "40",
                        "maxTemp": "90",
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["canvas"]
                    }
                }
            }
        )
    ]
    
    print("✅ Test data created successfully")
    print(f"   - Weather: {weather.temperature}°F, {weather.condition}")
    print(f"   - User: {user_profile.name}")
    print(f"   - Wardrobe: {len(test_wardrobe)} items")
    
    try:
        # Test outfit generation
        print("\n🔍 Testing outfit generation...")
        
        outfit = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=test_wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        )
        
        print(f"✅ Outfit generation successful!")
        print(f"   - Outfit ID: {outfit.id}")
        print(f"   - Outfit Name: {outfit.name}")
        print(f"   - Items Selected: {len(outfit.items)}")
        
        if outfit.items:
            print("   - Selected Items:")
            for item in outfit.items:
                print(f"     • {item.name} ({item.type})")
        else:
            print("   ⚠️  No items selected (this might indicate an issue)")
            
    except Exception as e:
        print(f"❌ Error during outfit generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Outfit generation test completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_outfit_generation()) 