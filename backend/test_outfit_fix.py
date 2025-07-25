#!/usr/bin/env python3
"""Test script to verify outfit generation fix works."""

import asyncio
import json
from src.services.outfit_service import OutfitService
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

async def test_outfit_generation_fix():
    """Test that outfit generation works with fallback logic."""
    outfit_service = OutfitService()
    
    print("🧪 Testing Outfit Generation Fix")
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
    
    # Create test wardrobe with limited items (like the real case)
    test_wardrobe = [
        {
            "id": "test_shoes_1",
            "name": "Black Sneakers",
            "type": "shoes",
            "subType": "sneakers",
            "style": ["Casual", "Athletic"],
            "occasion": ["Casual", "Athletic"],
            "dominantColors": [{"name": "Black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
            "matchingColors": [{"name": "White", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            "color": "Black",
            "brand": "Unknown",
            "updatedAt": 1750151681250,
            "weatherCompatibility": ["Spring", "Summer", "Fall"],
            "colorName": None,
            "userId": "test_user_123",
            "backgroundRemoved": False,
            "createdAt": 1750151681010,
            "gender": "male",
            "mood": ["Relaxed"],
            "season": ["fall", "spring", "summer"],
            "imageUrl": "test_shoes.jpg",
            "tags": ["Sporty", "Casual"],
            "metadata": {
                "analysisTimestamp": 0,
                "originalType": "shoes",
                "colorAnalysis": {
                    "dominantColors": [{"name": "Black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
                    "matchingColors": [{"name": "White", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}]
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
        },
        {
            "id": "test_jacket_1",
            "name": "Black Jacket",
            "type": "jacket",
            "subType": "ribbed sweater",
            "style": ["Business", "Casual", "Dark Academia"],
            "occasion": ["Business", "Casual", "Formal"],
            "dominantColors": [{"name": "Black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
            "matchingColors": [{"name": "White", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            "color": "Black",
            "brand": None,
            "updatedAt": 1750151681290,
            "weatherCompatibility": ["Cold", "Winter", "Fall"],
            "colorName": None,
            "userId": "test_user_123",
            "backgroundRemoved": False,
            "createdAt": 1750151681030,
            "gender": "male",
            "mood": ["Serious", "Professional"],
            "season": ["fall", "winter"],
            "imageUrl": "test_jacket.jpg",
            "tags": ["Formal", "Business"],
            "metadata": {
                "analysisTimestamp": 0,
                "originalType": "jacket",
                "colorAnalysis": {
                    "dominantColors": [{"name": "Black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
                    "matchingColors": [{"name": "White", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "32",
                        "maxTemp": "50",
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["wool"]
                    }
                }
            }
        }
    ]
    
    # Convert test wardrobe to ClothingItem objects
    from src.custom_types.wardrobe import ClothingItem
    clothing_items = []
    for item_data in test_wardrobe:
        item = ClothingItem(**item_data)
        clothing_items.append(item)
    
    print(f"📋 Test wardrobe: {len(clothing_items)} items")
    for item in clothing_items:
        print(f"  - {item.name} ({item.type})")
    
    print("\n🎯 Testing outfit generation for 'Fashion Event'...")
    
    try:
        # Generate outfit
        outfit = await outfit_service.generate_outfit(
            occasion="Fashion Event",
            weather=weather,
            wardrobe=clothing_items,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="Coastal Chic"
        )
        
        print(f"\n✅ Outfit generated successfully!")
        print(f"📋 Outfit details:")
        print(f"  - Name: {outfit.name}")
        print(f"  - Occasion: {outfit.occasion}")
        print(f"  - Style: {outfit.style}")
        print(f"  - Items: {len(outfit.items)}")
        
        if outfit.items:
            print(f"  - Selected items:")
            for item in outfit.items:
                print(f"    * {item.name} ({item.type})")
        else:
            print(f"  ❌ No items selected!")
            
        return len(outfit.items) > 0
        
    except Exception as e:
        print(f"❌ Error generating outfit: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_outfit_generation_fix())
    if result:
        print("\n✅ TEST PASSED: Outfit generation works with fallback logic!")
    else:
        print("\n❌ TEST FAILED: Outfit generation still returns zero items!") 