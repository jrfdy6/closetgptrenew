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

async def test_interview_outfit():
    """Test generating an interview outfit to see if it picks 4-7 items."""
    
    # Initialize services
    outfit_service = OutfitService()
    
    # Test data - using real user with 114 wardrobe items
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # john's user ID
    occasion = "interview"
    weather = WeatherData(
        temperature=20.0,
        condition="sunny",
        humidity=50.0,
        wind_speed=5.0
    )
    
    # Get user profile
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        print(f"No user profile found for {user_id}")
        return
    
    user_data = user_doc.to_dict()
    user_profile = UserProfile(**user_data)
    print(f"Using user: {user_profile.name} ({user_profile.email})")
    
    # Get wardrobe
    docs = db.collection('wardrobe').where('userId', '==', user_id).stream()
    wardrobe = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        wardrobe.append(ClothingItem(**item_data))
    
    if not wardrobe:
        print("No wardrobe found")
        return
    
    print(f"Total wardrobe items: {len(wardrobe)}")
    
    # Generate outfit
    print(f"\nGenerating outfit for: {occasion}")
    print("=" * 50)
    
    try:
        outfit = await outfit_service.generate_outfit(
            occasion=occasion,
            weather=weather,
            wardrobe=wardrobe,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            outfitHistory=[]
        )
        
        print(f"\nGenerated outfit with {len(outfit.items)} items:")
        print("-" * 30)
        
        for i, item in enumerate(outfit.items, 1):
            print(f"{i}. {item.name} ({item.type})")
            if hasattr(item, 'occasion') and item.occasion:
                print(f"   Occasions: {item.occasion}")
            if hasattr(item, 'style') and item.style:
                print(f"   Styles: {item.style}")
            print()
        
        print(f"Outfit description: {outfit.description}")
        print(f"Style notes: {outfit.styleNotes}")
        
        # Check if we met the target counts
        target_counts = outfit_service._get_target_item_counts(occasion)
        min_items = target_counts["min_items"]
        max_items = target_counts["max_items"]
        
        print(f"\nTarget: {min_items}-{max_items} items")
        print(f"Actual: {len(outfit.items)} items")
        
        if len(outfit.items) >= min_items and len(outfit.items) <= max_items:
            print("✅ SUCCESS: Outfit meets target item count!")
        else:
            print("❌ FAILURE: Outfit does not meet target item count")
        
    except Exception as e:
        print(f"Error generating outfit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_interview_outfit()) 