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

async def debug_real_outfit_generation():
    """Debug outfit generation with real wardrobe data"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Debugging real outfit generation for user: {user_id}")
    
    # Get user's wardrobe
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_docs = wardrobe_ref.where('userId', '==', user_id).stream()
    
    wardrobe_items = []
    for doc in wardrobe_docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        try:
            # Convert to ClothingItem object
            item = ClothingItem(**item_data)
            wardrobe_items.append(item)
        except Exception as e:
            print(f"⚠️  Error converting item {doc.id}: {e}")
            continue
    
    print(f"📊 Loaded {len(wardrobe_items)} wardrobe items")
    
    if len(wardrobe_items) == 0:
        print("❌ No wardrobe items found!")
        return
    
    # Get user profile
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        print("❌ User profile not found!")
        return
    
    user_data = user_doc.to_dict()
    try:
        user_profile = UserProfile(**user_data)
    except Exception as e:
        print(f"⚠️  Error converting user profile: {e}")
        # Create a basic profile
        user_profile = UserProfile(
            id=user_id,
            name=user_data.get('name', 'User'),
            email=user_data.get('email', 'user@example.com'),
            bodyType=user_data.get('bodyType', 'average'),
            skinTone=user_data.get('skinTone', 'neutral'),
            measurements=user_data.get('measurements', {}),
            stylePreferences=user_data.get('stylePreferences', []),
            colorPalette=user_data.get('colorPalette', {
                "primary": [], "secondary": [], "accent": [], "neutral": [], "avoid": []
            }),
            stylePersonality=user_data.get('stylePersonality', {
                "classic": 0.5, "modern": 0.5, "creative": 0.5, "minimal": 0.5, "bold": 0.5
            }),
            materialPreferences=user_data.get('materialPreferences', {
                "preferred": [], "avoid": []
            }),
            preferredBrands=user_data.get('preferredBrands', []),
            createdAt=user_data.get('createdAt', int(datetime.now().timestamp())),
            updatedAt=user_data.get('updatedAt', int(datetime.now().timestamp()))
        )
    
    # Create test weather
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=50.0
    )
    
    # Create outfit service
    outfit_service = OutfitService()
    
    print(f"\n🧪 Testing outfit generation with real data:")
    print(f"   - Wardrobe items: {len(wardrobe_items)}")
    print(f"   - User: {user_profile.name}")
    print(f"   - Weather: {weather.temperature}°F, {weather.condition}")
    
    # Analyze wardrobe categories
    categories = {}
    for item in wardrobe_items:
        item_type = item.type.lower()
        if item_type not in categories:
            categories[item_type] = 0
        categories[item_type] += 1
    
    print(f"\n📋 Wardrobe breakdown:")
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count} items")
    
    # Test outfit generation
    try:
        print(f"\n🔄 Generating outfit...")
        
        result = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=wardrobe_items,
            user_profile=user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        )
        
        print(f"\n📊 Generation Results:")
        print(f"   - Outfit name: {result.name}")
        print(f"   - Items count: {len(result.items)}")
        print(f"   - Was successful: {result.wasSuccessful}")
        print(f"   - Validation errors: {len(result.validationErrors) if result.validationErrors else 0}")
        
        if result.validationErrors:
            print(f"   - Errors: {result.validationErrors}")
        
        if result.items:
            print(f"   - Items selected:")
            for item in result.items:
                if isinstance(item, str):
                    print(f"     * {item} (ID)")
                else:
                    print(f"     * {item.name} ({item.type})")
        else:
            print(f"   ⚠️  No items selected!")
            
        # Check generation trace for debugging
        if hasattr(result, 'metadata') and result.metadata and 'generation_trace' in result.metadata:
            trace = result.metadata['generation_trace']
            print(f"\n🔍 Generation trace ({len(trace)} steps):")
            for i, step in enumerate(trace[:10]):  # Show first 10 steps
                step_type = step.get('step', 'Unknown')
                method = step.get('method', 'Unknown')
                print(f"   {i+1}. {step_type} - {method}")
            if len(trace) > 10:
                print(f"   ... and {len(trace) - 10} more steps")
        
    except Exception as e:
        print(f"❌ Outfit generation failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_real_outfit_generation()) 