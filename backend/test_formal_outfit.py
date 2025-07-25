#!/usr/bin/env python3

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_service import OutfitService
from src.config.firebase import db
from src.types.profile import UserProfile
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
import asyncio

async def test_formal_outfit():
    """Test generating a formal outfit to see if it picks 4-7 items."""
    
    # Initialize services
    outfit_service = OutfitService()
    
    # Test data - using real user with 114 wardrobe items
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # john's user ID
    occasion = "formal"
    weather = WeatherData(
        temperature=20.0,
        condition="sunny",
        humidity=50.0,
        wind_speed=5.0
    )
    
    # Get user profile
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        print("User not found")
        return
    
    user_data = user_doc.to_dict()
    user_profile = UserProfile(
        id=user_id,
        name=user_data.get('name', 'Unknown'),
        email=user_data.get('email', ''),
        bodyType=user_data.get('bodyType', 'average'),
        skinTone=user_data.get('skinTone', 'medium'),
        createdAt=user_data.get('createdAt', int(time.time())),
        updatedAt=user_data.get('updatedAt', int(time.time()))
    )
    
    # Get wardrobe
    wardrobe_docs = db.collection('wardrobe').where('userId', '==', user_id).stream()
    wardrobe = []
    for doc in wardrobe_docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        wardrobe.append(ClothingItem(**item_data))
    
    print(f"Using user: {user_data.get('name', 'Unknown')} ({user_data.get('email', 'No email')})")
    print(f"Total wardrobe items: {len(wardrobe)}")
    print()
    print(f"Generating outfit for: {occasion}")
    print("=" * 50)
    
    # Test the specific pipeline step by step
    try:
        print("Testing _gather_input_context...")
        context = outfit_service._gather_input_context(
            occasion=occasion,
            weather=weather,
            user_profile=user_profile,
            style=None,
            mood=None,
            trendingStyles=[],
            likedOutfits=[],
            baseItem=None,
            outfit_history=[]
        )
        print("✅ _gather_input_context passed")
        
        print("Testing _apply_strict_filtering...")
        filtered_items = outfit_service._apply_strict_filtering(wardrobe, context)
        print(f"✅ _apply_strict_filtering passed: {len(filtered_items)} items")
        
        print("Testing _smart_selection_phase...")
        selected_items = outfit_service._smart_selection_phase(filtered_items, context)
        print(f"✅ _smart_selection_phase passed: {len(selected_items)} items")
        
        # Show the selected items
        print("\nSelected items:")
        for i, item in enumerate(selected_items, 1):
            print(f"{i}. {item.name} ({item.type})")
        
        # Check if we meet the target
        target_counts = context["target_counts"]
        min_items = target_counts["min_items"]
        max_items = target_counts["max_items"]
        
        print(f"\nTarget: {min_items}-{max_items} items")
        print(f"Actual: {len(selected_items)} items")
        
        if min_items <= len(selected_items) <= max_items:
            print("✅ SUCCESS: Outfit meets target item count")
        else:
            print("❌ FAILURE: Outfit does not meet target item count")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_formal_outfit()) 