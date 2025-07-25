import asyncio
from src.services.outfit_service import OutfitService
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile
from src.custom_types.wardrobe import ClothingItem, ClothingType
import time

def create_test_wardrobe():
    now = int(time.time())
    return [
        ClothingItem(
            id="playful1",
            name="Green and white striped short sleeve button down",
            type=ClothingType.SHIRT,
            color="green",
            style=["casual", "trendy", "colorful"],
            occasion=["vacation"],
            season=["summer"],
            dominantColors=[{"name": "green", "hex": "#228B22"}, {"name": "white", "hex": "#FFFFFF"}],
            material="cotton",
            imageUrl="https://example.com/green-shirt.jpg",
            tags=["playful", "summer"],
            userId="test-user",
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="relaxed1",
            name="Grey striped polo shirt",
            type=ClothingType.SHIRT,
            color="grey",
            style=["casual", "comfortable", "minimal"],
            occasion=["vacation"],
            season=["summer"],
            dominantColors=[{"name": "grey", "hex": "#808080"}],
            material="cotton",
            imageUrl="https://example.com/grey-polo.jpg",
            tags=["relaxed", "summer"],
            userId="test-user",
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="pants1",
            name="Khaki pants",
            type=ClothingType.PANTS,
            color="khaki",
            style=["casual"],
            occasion=["vacation"],
            season=["summer"],
            dominantColors=[{"name": "khaki", "hex": "#C3B091"}],
            material="cotton",
            imageUrl="https://example.com/khaki-pants.jpg",
            tags=["casual", "summer"],
            userId="test-user",
            matchingColors=[{"name": "white", "hex": "#FFFFFF"}],
            createdAt=now,
            updatedAt=now
        ),
        ClothingItem(
            id="shoes1",
            name="White sneakers",
            type=ClothingType.SHOES,
            color="white",
            style=["casual"],
            occasion=["vacation"],
            season=["summer"],
            dominantColors=[{"name": "white", "hex": "#FFFFFF"}],
            material="leather",
            imageUrl="https://example.com/white-sneakers.jpg",
            tags=["casual", "summer"],
            userId="test-user",
            matchingColors=[{"name": "khaki", "hex": "#C3B091"}],
            createdAt=now,
            updatedAt=now
        ),
    ]

def create_test_user_profile():
    return UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual"],
        budget="medium",
        createdAt=1640995200,
        updatedAt=1640995200
    )

def create_test_weather():
    return WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=60,
        windSpeed=5,
        location="Test City"
    )

async def test_mood_filtering():
    outfit_service = OutfitService()
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = create_test_weather()

    for mood in ["playful", "relaxed"]:
        outfit = await outfit_service.generate_outfit(
            occasion="Vacation",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual",
            mood=mood
        )
        print(f"\nMood: {mood}")
        for item_id in outfit.items:
            item = next((i for i in wardrobe if i.id == item_id), None)
            if item:
                print(f"  - {item.name} ({item.color}, {item.style})")

if __name__ == "__main__":
    asyncio.run(test_mood_filtering()) 