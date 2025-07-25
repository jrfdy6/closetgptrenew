#!/usr/bin/env python3
"""
Debug script to test why interview outfit generation is only returning 2 items.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService
from src.types.weather import WeatherData
from src.types.profile import UserProfile

async def debug_interview_outfit():
    """Debug interview outfit generation."""
    
    # Create outfit service
    outfit_service = OutfitService()
    
    print("🧪 Debugging interview outfit generation...")
    
    # Create test data
    weather = WeatherData(
        temperature=69.9,
        condition="sunny",
        location="default",
        humidity=50,
        wind_speed=5,
        precipitation=0
    )
    
    user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        preferences={},
        measurements={"skinTone": "medium"},
        stylePreferences=[],
        bodyType="athletic",
        createdAt="2024-01-01",
        updatedAt="2024-01-01"
    )
    
    # Get a sample wardrobe (you'll need to replace this with actual wardrobe data)
    print("📋 Getting sample wardrobe...")
    try:
        from src.config.firebase import db
        wardrobe_docs = db.collection("wardrobe").limit(20).stream()
        wardrobe = []
        for doc in wardrobe_docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            from src.types.wardrobe import ClothingItem
            clothing_item = ClothingItem(**item_data)
            wardrobe.append(clothing_item)
        
        print(f"📋 Found {len(wardrobe)} wardrobe items")
        
        # Test the layering rule
        layering_rule = outfit_service._get_layering_rule(weather.temperature)
        print(f"🌡️  Layering rule for {weather.temperature}°F:")
        print(f"   - Required layers: {layering_rule.required_layers}")
        print(f"   - Layer types: {layering_rule.layer_types}")
        print(f"   - Material preferences: {layering_rule.material_preferences}")
        
        # Test outfit generation
        print("\n🎯 Testing outfit generation for Interview...")
        result = await outfit_service.generate_outfit(
            occasion="Interview",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="Minimalist",
            mood="confident"
        )
        
        print(f"\n✅ Generated outfit:")
        print(f"   - Items: {len(result.items)}")
        for i, item in enumerate(result.items):
            print(f"   {i+1}. {item.name} ({item.type})")
        
        # Test the ensure_outfit_structure method directly
        print(f"\n🔧 Testing _ensure_outfit_structure directly...")
        test_items = result.items[:2] if len(result.items) >= 2 else result.items
        print(f"   - Starting with {len(test_items)} items: {[item.name for item in test_items]}")
        
        enhanced_items = outfit_service._ensure_outfit_structure(
            test_items, 
            wardrobe, 
            layering_rule, 
            "Interview", 
            "Minimalist", 
            weather.temperature
        )
        
        print(f"   - After _ensure_outfit_structure: {len(enhanced_items)} items")
        for i, item in enumerate(enhanced_items):
            print(f"   {i+1}. {item.name} ({item.type})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_interview_outfit()) 