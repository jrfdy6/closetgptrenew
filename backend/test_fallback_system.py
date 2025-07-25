"""
Test script for the Self-Healing Outfit Fallback System
======================================================

This script demonstrates how the fallback system works and tests various scenarios.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.outfit_fallback_service import OutfitFallbackService
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
from src.types.profile import UserProfile
from src.types.outfit_rules import get_layering_rule
import time

async def test_fallback_system():
    """Test the complete fallback system with various scenarios."""
    
    print("🧪 Testing Self-Healing Outfit Fallback System")
    print("=" * 60)
    
    # Initialize the fallback service
    fallback_service = OutfitFallbackService()
    
    # Create test context
    context = {
        'occasion': 'casual',
        'weather': WeatherData(
            temperature=75.0,
            condition='sunny',
            humidity=60.0,
            wind_speed=5.0
        ),
        'user_profile': UserProfile(
            id='test-user-123',
            name='Test User',
            email='test@example.com',
            gender='male',
            bodyType='athletic',
            skinTone='medium',
            stylePreferences=['casual', 'minimalist'],
            colorPreferences=['blue', 'gray', 'white'],
            occasionPreferences=['casual', 'workout'],
            measurements={
                'height': 180,
                'weight': 75,
                'chest': 100,
                'waist': 80,
                'hips': 95
            }
        ),
        'style': 'casual',
        'mood': 'relaxed'
    }
    
    # Test Scenario 1: Duplicate items
    print("\n🔧 Test Scenario 1: Duplicate Items")
    print("-" * 40)
    
    duplicate_items = [
        ClothingItem(
            id='item1',
            name='Blue T-Shirt',
            type='t-shirt',
            color='blue',
            season=['spring', 'summer'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/blue-tshirt.jpg',
            tags=['cotton', 'comfortable'],
            dominantColors=[{'name': 'blue', 'hex': '#0000FF'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        ),
        ClothingItem(
            id='item2',
            name='Red T-Shirt',
            type='t-shirt',
            color='red',
            season=['spring', 'summer'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/red-tshirt.jpg',
            tags=['cotton', 'comfortable'],
            dominantColors=[{'name': 'red', 'hex': '#FF0000'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        )
    ]
    
    duplicate_errors = ["Duplicate items detected: two t-shirts"]
    
    healed_items, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
        duplicate_items, duplicate_errors, context
    )
    
    print(f"✅ Original items: {len(duplicate_items)}")
    print(f"✅ Healed items: {len(healed_items)}")
    print(f"✅ Remaining errors: {len(remaining_errors)}")
    print(f"✅ Healing strategy used: {healing_log.get('strategy_used')}")
    print(f"✅ Items fixed: {len(healing_log.get('items_fixed', []))}")
    print(f"✅ Items replaced: {len(healing_log.get('items_replaced', []))}")
    
    # Test Scenario 2: Weather inappropriate items
    print("\n🔧 Test Scenario 2: Weather Inappropriate Items")
    print("-" * 40)
    
    weather_inappropriate_items = [
        ClothingItem(
            id='item3',
            name='Wool Sweater',
            type='sweater',
            color='brown',
            season=['winter', 'fall'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/wool-sweater.jpg',
            tags=['wool', 'warm'],
            dominantColors=[{'name': 'brown', 'hex': '#8B4513'}],
            matchingColors=[{'name': 'beige', 'hex': '#F5F5DC'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        )
    ]
    
    weather_errors = ["Item not appropriate for hot weather: wool sweater"]
    
    healed_items, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
        weather_inappropriate_items, weather_errors, context
    )
    
    print(f"✅ Original items: {len(weather_inappropriate_items)}")
    print(f"✅ Healed items: {len(healed_items)}")
    print(f"✅ Remaining errors: {len(remaining_errors)}")
    print(f"✅ Healing strategy used: {healing_log.get('strategy_used')}")
    
    # Test Scenario 3: Style conflicts
    print("\n🔧 Test Scenario 3: Style Conflicts")
    print("-" * 40)
    
    style_conflict_items = [
        ClothingItem(
            id='item4',
            name='Formal Suit Jacket',
            type='jacket',
            color='black',
            season=['all'],
            style=['formal', 'business'],
            occasion=['formal', 'business'],
            imageUrl='https://example.com/suit-jacket.jpg',
            tags=['formal', 'professional'],
            dominantColors=[{'name': 'black', 'hex': '#000000'}],
            matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        )
    ]
    
    style_errors = ["Style conflict: formal jacket doesn't match casual style"]
    
    healed_items, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
        style_conflict_items, style_errors, context
    )
    
    print(f"✅ Original items: {len(style_conflict_items)}")
    print(f"✅ Healed items: {len(healed_items)}")
    print(f"✅ Remaining errors: {len(remaining_errors)}")
    print(f"✅ Healing strategy used: {healing_log.get('strategy_used')}")
    
    # Test Scenario 4: Multiple errors
    print("\n🔧 Test Scenario 4: Multiple Errors")
    print("-" * 40)
    
    multiple_error_items = [
        ClothingItem(
            id='item5',
            name='Winter Coat',
            type='coat',
            color='black',
            season=['winter'],
            style=['formal'],
            occasion=['formal'],
            imageUrl='https://example.com/winter-coat.jpg',
            tags=['warm', 'formal'],
            dominantColors=[{'name': 'black', 'hex': '#000000'}],
            matchingColors=[{'name': 'gray', 'hex': '#808080'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        ),
        ClothingItem(
            id='item6',
            name='Another Winter Coat',
            type='coat',
            color='brown',
            season=['winter'],
            style=['casual'],
            occasion=['casual'],
            imageUrl='https://example.com/another-coat.jpg',
            tags=['warm', 'casual'],
            dominantColors=[{'name': 'brown', 'hex': '#8B4513'}],
            matchingColors=[{'name': 'beige', 'hex': '#F5F5DC'}],
            createdAt=int(time.time()),
            updatedAt=int(time.time()),
            userId='test-user-123'
        )
    ]
    
    multiple_errors = [
        "Item not appropriate for hot weather: winter coat",
        "Duplicate items detected: two coats",
        "Style conflict: formal coat doesn't match casual style"
    ]
    
    healed_items, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
        multiple_error_items, multiple_errors, context
    )
    
    print(f"✅ Original items: {len(multiple_error_items)}")
    print(f"✅ Healed items: {len(healed_items)}")
    print(f"✅ Remaining errors: {len(remaining_errors)}")
    print(f"✅ Healing strategy used: {healing_log.get('strategy_used')}")
    print(f"✅ Total attempts made: {healing_log.get('attempts_made')}")
    
    # Test Scenario 5: Scratch generation
    print("\n🔧 Test Scenario 5: Scratch Generation")
    print("-" * 40)
    
    empty_items = []
    scratch_errors = ["No items selected", "Pipeline completely failed"]
    
    healed_items, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
        empty_items, scratch_errors, context
    )
    
    print(f"✅ Original items: {len(empty_items)}")
    print(f"✅ Healed items: {len(healed_items)}")
    print(f"✅ Remaining errors: {len(remaining_errors)}")
    print(f"✅ Healing strategy used: {healing_log.get('strategy_used')}")
    
    print("\n🎉 Fallback System Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fallback_system()) 