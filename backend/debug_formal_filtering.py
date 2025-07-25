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

async def debug_formal_filtering():
    """Debug why formal items are being filtered out."""
    
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
    
    # Check how many items have formal attributes
    formal_keywords = ['formal', 'business', 'dress', 'professional', 'elegant']
    items_with_formal_attrs = []
    
    for item in wardrobe:
        has_formal_occasion = False
        if item.occasion:
            item_occasions = [occ.lower() for occ in item.occasion]
            for item_occ in item_occasions:
                if any(keyword in item_occ for keyword in formal_keywords):
                    has_formal_occasion = True
                    break
        
        has_formal_style = False
        if item.style:
            item_styles = [s.lower() for s in item.style]
            if any(keyword in ' '.join(item_styles) for keyword in formal_keywords):
                has_formal_style = True
        
        has_formal_tags = False
        if hasattr(item, 'tags') and item.tags:
            item_tags = [tag.lower() for tag in item.tags]
            if any(keyword in ' '.join(item_tags) for keyword in formal_keywords):
                has_formal_tags = True
        
        if has_formal_occasion or has_formal_style or has_formal_tags:
            items_with_formal_attrs.append({
                'item': item,
                'has_formal_occasion': has_formal_occasion,
                'has_formal_style': has_formal_style,
                'has_formal_tags': has_formal_tags
            })
    
    print(f"Items with formal attributes: {len(items_with_formal_attrs)}")
    
    # Show some examples
    print("\nExamples of items with formal attributes:")
    for i, item_info in enumerate(items_with_formal_attrs[:5]):
        item = item_info['item']
        print(f"  {i+1}. {item.name} ({item.type})")
        print(f"     Occasion: {item.occasion}")
        print(f"     Style: {item.style}")
        print(f"     Tags: {getattr(item, 'tags', [])}")
        print(f"     Formal attrs: occasion={item_info['has_formal_occasion']}, style={item_info['has_formal_style']}, tags={item_info['has_formal_tags']}")
        print()
    
    # Now test the actual filtering
    print("Testing actual filtering...")
    
    # Apply weather filtering first
    weather_filtered = outfit_service._filter_by_weather_strict(wardrobe, weather)
    print(f"After weather filtering: {len(weather_filtered)} items")
    
    # Apply occasion filtering
    occasion_filtered = outfit_service._filter_by_occasion_strict(weather_filtered, occasion)
    print(f"After occasion filtering: {len(occasion_filtered)} items")
    
    # Show what was filtered out
    filtered_out = [item for item in weather_filtered if item not in occasion_filtered]
    print(f"Items filtered out by occasion: {len(filtered_out)}")
    
    print("\nItems filtered out by occasion filtering:")
    for i, item in enumerate(filtered_out[:10]):
        print(f"  {i+1}. {item.name} ({item.type})")
        print(f"     Occasion: {item.occasion}")
        print(f"     Style: {item.style}")
        print(f"     Tags: {getattr(item, 'tags', [])}")
        print()
    
    # Check if any formal items were filtered out
    formal_items_filtered_out = [item for item in filtered_out if item in [info['item'] for info in items_with_formal_attrs]]
    print(f"Formal items filtered out: {len(formal_items_filtered_out)}")
    
    if formal_items_filtered_out:
        print("\nFormal items that were filtered out:")
        for item in formal_items_filtered_out:
            print(f"  - {item.name} ({item.type})")

if __name__ == "__main__":
    asyncio.run(debug_formal_filtering()) 