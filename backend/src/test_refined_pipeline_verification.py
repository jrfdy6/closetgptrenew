#!/usr/bin/env python3
"""
Test script to verify the refined outfit generation pipeline is working correctly.
This tests the 5-phase pipeline implementation.
"""

import sys
import os

from services.outfit_service import OutfitService
from models.clothing_item import ClothingItem
from models.user_profile import UserProfile
from models.weather_data import WeatherData
from models.color import Color
from typing import List, Dict, Any

def create_test_wardrobe() -> List[ClothingItem]:
    """Create a test wardrobe with various clothing items."""
    return [
        ClothingItem(
            id="1",
            name="White T-Shirt",
            type="t-shirt",
            style="casual",
            occasion=["casual", "athletic"],
            dominantColors=[Color(name="white", hex="#FFFFFF")],
            imageUrl="test1.jpg",
            attributes=["athletic", "comfortable", "breathable"]
        ),
        ClothingItem(
            id="2",
            name="Blue Jeans",
            type="jeans",
            style="casual",
            occasion=["casual", "everyday"],
            dominantColors=[Color(name="blue", hex="#000080")],
            imageUrl="test2.jpg",
            attributes=["comfortable", "versatile"]
        ),
        ClothingItem(
            id="3",
            name="Running Shoes",
            type="sneakers",
            style="athletic",
            occasion=["athletic", "casual"],
            dominantColors=[Color(name="black", hex="#000000")],
            imageUrl="test3.jpg",
            attributes=["athletic", "comfortable", "supportive"]
        ),
        ClothingItem(
            id="4",
            name="Dress Shirt",
            type="dress shirt",
            style="formal",
            occasion=["formal", "business"],
            dominantColors=[Color(name="white", hex="#FFFFFF")],
            imageUrl="test4.jpg",
            attributes=["formal", "professional", "elegant"]
        ),
        ClothingItem(
            id="5",
            name="Dress Pants",
            type="dress pants",
            style="formal",
            occasion=["formal", "business"],
            dominantColors=[Color(name="black", hex="#000000")],
            imageUrl="test5.jpg",
            attributes=["formal", "professional"]
        )
    ]

def create_test_user_profile() -> UserProfile:
    """Create a test user profile."""
    return UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual", "athletic"],
        sizePreferences=["M"],
        colorPreferences=["blue", "black", "white"]
    )

def create_test_weather() -> WeatherData:
    """Create test weather data."""
    return WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=60.0,
        windSpeed=5.0
    )

def test_refined_pipeline_phases():
    """Test each phase of the refined pipeline."""
    print("🧪 Testing Refined Outfit Generation Pipeline")
    print("=" * 50)
    
    # Initialize service
    service = OutfitService()
    
    # Create test data
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = create_test_weather()
    
    print(f"📦 Test wardrobe: {len(wardrobe)} items")
    print(f"👤 Test user: {user_profile.name}")
    print(f"🌤️  Test weather: {weather.temperature}°F, {weather.condition}")
    
    # Test different scenarios
    test_scenarios = [
        {
            "name": "Athletic/Gym Outfit",
            "occasion": "Athletic / Gym",
            "style": "athletic",
            "mood": "energetic"
        },
        {
            "name": "Casual Outfit",
            "occasion": "Everyday Casual",
            "style": "casual",
            "mood": "relaxed"
        },
        {
            "name": "Formal Outfit",
            "occasion": "Formal",
            "style": "formal",
            "mood": "elegant"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎯 Testing: {scenario['name']}")
        print("-" * 30)
        
        try:
            # Test the refined pipeline directly
            result = service._generate_outfit_refined_pipeline(
                occasion=scenario["occasion"],
                weather=weather,
                wardrobe=wardrobe,
                user_profile=user_profile,
                style=scenario["style"],
                mood=scenario["mood"]
            )
            
            if result["success"]:
                items = result["items"]
                print(f"✅ Pipeline SUCCESS: {len(items)} items selected")
                print(f"📋 Selected items:")
                for i, item in enumerate(items, 1):
                    print(f"   {i}. {item.name} ({item.type}) - {item.style}")
                
                # Test context gathering
                context = result.get("context", {})
                print(f"🔍 Context gathered:")
                print(f"   - Occasion rule: {context.get('occasion_rule', 'None')}")
                print(f"   - Target counts: {context.get('target_counts', 'None')}")
                print(f"   - Style matrix: {context.get('style_matrix', 'None')}")
                
            else:
                print(f"❌ Pipeline FAILED: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n🎉 Pipeline verification completed!")

def test_pipeline_phases_individually():
    """Test each phase of the pipeline individually."""
    print(f"\n🔬 Testing Individual Pipeline Phases")
    print("=" * 50)
    
    service = OutfitService()
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = create_test_weather()
    
    # Phase 1: Input Context Gathering
    print("📋 Phase 1: Input Context Gathering")
    context = service._gather_input_context(
        occasion="Athletic / Gym",
        weather=weather,
        user_profile=user_profile,
        style="athletic",
        mood="energetic",
        trendingStyles=[],
        likedOutfits=[],
        baseItem=None
    )
    print(f"   ✅ Context gathered with {len(context)} keys")
    print(f"   📊 Target counts: {context.get('target_counts', 'None')}")
    
    # Phase 2: Strict Filtering
    print("🔍 Phase 2: Strict Filtering")
    filtered_wardrobe = service._apply_strict_filtering(wardrobe, context)
    print(f"   ✅ Filtered from {len(wardrobe)} to {len(filtered_wardrobe)} items")
    print(f"   📋 Filtered items: {[item.name for item in filtered_wardrobe]}")
    
    # Phase 3: Smart Selection
    print("🎯 Phase 3: Smart Selection")
    selected_items = service._smart_selection_phase(filtered_wardrobe, context)
    print(f"   ✅ Selected {len(selected_items)} items")
    print(f"   📋 Selected items: {[item.name for item in selected_items]}")
    
    # Phase 4: Structural Integrity
    print("🏗️  Phase 4: Structural Integrity Check")
    structure_result = service._structural_integrity_check(selected_items, filtered_wardrobe, context)
    print(f"   ✅ Structure complete: {structure_result['is_complete']}")
    print(f"   📋 Missing categories: {structure_result.get('missing_categories', [])}")
    
    # Phase 5: Final Validation
    print("✅ Phase 5: Final Validation")
    validation_result = service._final_outfit_validation(selected_items, context)
    print(f"   ✅ Validation passed: {validation_result['is_valid']}")
    print(f"   ⚠️  Warnings: {len(validation_result.get('warnings', []))}")
    print(f"   ❌ Errors: {len(validation_result.get('errors', []))}")
    
    print(f"\n🎉 Individual phase testing completed!")

if __name__ == "__main__":
    test_refined_pipeline_phases()
    test_pipeline_phases_individually() 