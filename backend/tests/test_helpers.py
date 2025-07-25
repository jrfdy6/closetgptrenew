"""
Test helpers for creating valid test data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from custom_types.wardrobe import ClothingItem
from custom_types.weather import WeatherData
from custom_types.profile import UserProfile
from typing import List

def create_test_clothing_item(
    id: str = "test_item",
    name: str = "Test Item",
    type: str = "shirt",
    seasonal_score: float = 0.8
) -> ClothingItem:
    """Create a valid test ClothingItem with all required fields."""
    return ClothingItem(
        id=id,
        name=name,
        type=type,
        color="blue",
        season=["all"],  # Fix: season should be a list
        imageUrl="https://example.com/image.jpg",
        tags=["casual"],
        userId="test_user",
        dominantColors=[
            {"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}
        ],
        matchingColors=[
            {"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}
        ],
        occasion=["casual"],
        createdAt=1234567890,
        updatedAt=1234567890,
        seasonal_score=seasonal_score
    )

def create_test_weather_data(
    temperature: float = 70,
    condition: str = "clear"
) -> WeatherData:
    """Create a valid test WeatherData with all required fields."""
    return WeatherData(
        temperature=temperature,
        condition=condition,
        humidity=50
    )

def create_test_user_profile(
    user_id: str = "test_user"
) -> UserProfile:
    """Create a valid test UserProfile with all required fields."""
    return UserProfile(
        id=user_id,
        name="Test User",
        email="test@example.com",
        bodyType="average",
        skinTone="medium",
        stylePreferences=["casual"],
        occasionPreferences=["casual"],
        colorPreferences=["blue"]
    )

def create_test_wardrobe(count: int = 3) -> List[ClothingItem]:
    """Create a test wardrobe with the specified number of items."""
    items = []
    for i in range(count):
        item = create_test_clothing_item(
            id=f"item_{i}",
            name=f"Test Item {i}",
            type=["shirt", "pants", "shoes"][i % 3]
        )
        items.append(item)
    return items 