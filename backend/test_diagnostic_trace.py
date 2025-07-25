#!/usr/bin/env python3
"""
Test script to demonstrate diagnostic tracing functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
from src.types.profile import UserProfile
from src.types.weather import WeatherData
from src.config.firebase import db  # Import db directly

async def test_diagnostic_tracing():
    """Test the diagnostic tracing functionality by generating an outfit."""
    
    print("🚀 Testing Diagnostic Tracing System")
    print("=" * 50)
    
    # Firebase is already initialized in the config
    print("✅ Firebase initialized")
    
    # Create test data
    current_time = int(datetime.now().timestamp() * 1000)  # Convert to milliseconds
    user_profile = UserProfile(
        id="test_user_123",
        name="Test User",
        email="test@example.com",
        bodyType="average",
        skinTone="medium",
        stylePreferences=["casual", "comfortable"],
        preferences={
            "style": ["casual", "comfortable"],
            "colors": ["blue", "black", "white"],
            "occasions": ["casual", "work"]
        },
        measurements={
            "height": 170,
            "weight": 70,
            "bodyType": "average",
            "skinTone": "medium"
        },
        fitPreference="regular",
        createdAt=current_time,
        updatedAt=current_time
    )
    
    weather = WeatherData(
        temperature=72.0,
        condition="Clear",
        humidity=60,
        wind_speed=5.0,
        location="San Francisco, CA",
        precipitation=0.0
    )
    
    # Create test wardrobe items
    wardrobe = [
        ClothingItem(
            id="item_1",
            name="Blue T-Shirt",
            type=ClothingType.SHIRT,
            color="blue",
            season=[Season.SPRING.value, Season.SUMMER.value],
            imageUrl="https://example.com/blue-tshirt.jpg",
            tags=["casual", "work"],
            style=[StyleTag.CASUAL.value],
            userId="test_user_123",
            dominantColors=[Color(name="blue", hex="#0000FF", rgb=[0,0,255])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            occasion=["casual", "work"],
            brand="Test Brand",
            createdAt=current_time,
            updatedAt=current_time
        ),
        ClothingItem(
            id="item_2",
            name="Black Jeans",
            type=ClothingType.PANTS,
            color="black",
            season=[Season.SPRING.value, Season.SUMMER.value, Season.FALL.value, Season.WINTER.value],
            imageUrl="https://example.com/black-jeans.jpg",
            tags=["casual", "work"],
            style=[StyleTag.CASUAL.value],
            userId="test_user_123",
            dominantColors=[Color(name="black", hex="#000000", rgb=[0,0,0])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            occasion=["casual", "work"],
            brand="Test Brand",
            createdAt=current_time,
            updatedAt=current_time
        ),
        ClothingItem(
            id="item_3",
            name="White Sneakers",
            type=ClothingType.SNEAKERS,
            color="white",
            season=[Season.SPRING.value, Season.SUMMER.value, Season.FALL.value, Season.WINTER.value],
            imageUrl="https://example.com/white-sneakers.jpg",
            tags=["casual", "work"],
            style=[StyleTag.CASUAL.value],
            userId="test_user_123",
            dominantColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            matchingColors=[Color(name="black", hex="#000000", rgb=[0,0,0])],
            occasion=["casual", "work"],
            brand="Test Brand",
            createdAt=current_time,
            updatedAt=current_time
        )
    ]
    
    # Initialize outfit service
    outfit_service = OutfitService()
    
    print(f"📊 Test Data Created:")
    print(f"   - User: {user_profile.name} ({user_profile.id})")
    print(f"   - Weather: {weather.temperature}°F, {weather.condition}")
    print(f"   - Wardrobe: {len(wardrobe)} items")
    print(f"   - Occasion: casual")
    print()
    
    try:
        print("🔄 Generating outfit with diagnostic tracing...")
        print("-" * 50)
        
        # Generate outfit
        outfit = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        )
        
        print("✅ Outfit generated successfully!")
        print()
        
        # Display diagnostic information
        print("🔍 DIAGNOSTIC TRACE SUMMARY:")
        print("=" * 50)
        
        print(f"📋 Outfit ID: {outfit.id}")
        print(f"🎯 Generation Method: {getattr(outfit, 'generation_method', 'unknown')}")
        print(f"✅ Success: {outfit.wasSuccessful}")
        print(f"👕 Items: {len(outfit.items)}")
        print(f"🎨 Style: {outfit.style}")
        print(f"📅 Created: {datetime.fromtimestamp(outfit.createdAt)}")
        print()
        
        # Show generation trace
        if hasattr(outfit, 'generation_trace') and outfit.generation_trace:
            print("🔄 GENERATION TRACE:")
            print("-" * 30)
            for i, step in enumerate(outfit.generation_trace, 1):
                print(f"{i:2d}. {step.get('step', 'unknown')}")
                print(f"    Method: {step.get('method', 'unknown')}")
                if step.get('duration'):
                    print(f"    Duration: {step.get('duration'):.3f}s")
                if step.get('errors'):
                    print(f"    Errors: {step.get('errors')}")
                print()
        
        # Show validation details
        if hasattr(outfit, 'validation_details') and outfit.validation_details:
            print("⚠️  VALIDATION DETAILS:")
            print("-" * 30)
            errors = outfit.validation_details.get('errors', [])
            fixes = outfit.validation_details.get('fixes', [])
            
            if errors:
                print("❌ Errors:")
                for error in errors:
                    print(f"   - {error.get('reason', 'Unknown error')}")
                print()
            
            if fixes:
                print("🔧 Fixes Applied:")
                for fix in fixes:
                    print(f"   - {fix.get('method', 'Unknown method')}: {fix.get('original_error', 'Unknown error')}")
                print()
        
        # Show wardrobe snapshot
        if hasattr(outfit, 'wardrobe_snapshot') and outfit.wardrobe_snapshot:
            print("👔 WARDROBE SNAPSHOT:")
            print("-" * 30)
            snapshot = outfit.wardrobe_snapshot
            print(f"   Total Items: {snapshot.get('total_items', 0)}")
            print(f"   Categories: {snapshot.get('categories', {})}")
            
            gaps = snapshot.get('gaps', [])
            if gaps:
                print("   Gaps Detected:")
                for gap in gaps:
                    print(f"     - {gap.get('category', 'unknown')}: {gap.get('count', 0)} items ({gap.get('severity', 'unknown')} severity)")
            print()
        
        # Show system context
        if hasattr(outfit, 'system_context') and outfit.system_context:
            print("⚙️  SYSTEM CONTEXT:")
            print("-" * 30)
            context = outfit.system_context
            env = context.get('environment', {})
            config = context.get('config', {})
            
            print(f"   Python Version: {env.get('python_version', 'unknown')}")
            print(f"   Git Hash: {env.get('git_hash', 'unknown')[:8] if env.get('git_hash') else 'unknown'}")
            print(f"   Platform: {env.get('platform', 'unknown')}")
            print(f"   Session ID: {context.get('session_id', 'unknown')}")
            print(f"   Style Strictness: {config.get('style_strictness', 'unknown')}")
            print(f"   Fallback Enabled: {config.get('fallback_enabled', 'unknown')}")
            print()
        
        print("🎉 Diagnostic tracing test completed successfully!")
        print()
        print("💡 To view this trace in the frontend:")
        print("   1. Visit /analytics-test in your frontend")
        print("   2. Look for the outfit with ID:", outfit.id)
        print("   3. Click on it to see the full trace details")
        
    except Exception as e:
        print(f"❌ Error during outfit generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_diagnostic_tracing()) 