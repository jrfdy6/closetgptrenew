#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_service import OutfitService
from src.custom_types.wardrobe import ClothingItem
from src.custom_types.profile import UserProfile
from src.custom_types.weather import WeatherData

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def test_outfit_generation_after_fix():
    """Test outfit generation after the profile data structure fix"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🧪 Testing outfit generation after profile data fix for user: {user_id}")
    
    # Get user profile
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        print("❌ User profile not found")
        return
    
    user_data = user_doc.to_dict()
    print(f"📋 User profile loaded successfully")
    
    # Get user's wardrobe
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_items = wardrobe_ref.where('userId', '==', user_id).stream()
    
    wardrobe = []
    for item_doc in wardrobe_items:
        item_data = item_doc.to_dict()
        item_data['id'] = item_doc.id
        try:
            clothing_item = ClothingItem(**item_data)
            wardrobe.append(clothing_item)
        except Exception as e:
            print(f"⚠️ Warning: Could not create ClothingItem for {item_doc.id}: {e}")
            continue
    
    print(f"👕 Loaded {len(wardrobe)} wardrobe items")
    
    # Create test weather data
    weather = WeatherData(
        temperature=69.2,
        condition="partly_cloudy",
        humidity=60,
        wind_speed=5
    )
    
    # Create outfit service
    outfit_service = OutfitService()
    
    # Test outfit generation
    print("\n🎯 Testing outfit generation...")
    
    try:
        result = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=UserProfile(**user_data),
            likedOutfits=[],
            trendingStyles=[],
            style="casual",
            mood="relaxed"
        )
        
        print(f"✅ Outfit generation completed!")
        print(f"📋 Outfit name: {result.name}")
        print(f"👕 Items selected: {len(result.items)}")
        print(f"✅ Was successful: {result.wasSuccessful}")
        
        if result.validationErrors:
            print(f"⚠️ Validation errors: {result.validationErrors}")
        
        if result.items:
            print(f"👕 Selected items:")
            for item in result.items:
                if isinstance(item, ClothingItem):
                    print(f"  - {item.name} ({item.type})")
                else:
                    print(f"  - {item}")
        
    except Exception as e:
        print(f"❌ Outfit generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_outfit_generation_after_fix()) 