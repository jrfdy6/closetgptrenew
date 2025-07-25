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

async def debug_layering_validation():
    """Debug the layering validation issue for 69.2°F"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Debugging layering validation for user: {user_id}")
    print(f"🌡️  Temperature: 69.2°F")
    
    # Create outfit service
    outfit_service = OutfitService()
    
    # Get layering rule for 69.2°F
    layering_rule = outfit_service._get_layering_rule(69.2)
    print(f"\n📋 Layering Rule for 69.2°F:")
    print(f"   - Temperature range: {layering_rule.min_temperature}°F - {layering_rule.max_temperature}°F")
    print(f"   - Required layers: {layering_rule.required_layers}")
    print(f"   - Layer types: {[lt.value for lt in layering_rule.layer_types]}")
    print(f"   - Material preferences: {layering_rule.material_preferences}")
    print(f"   - Notes: {layering_rule.notes}")
    
    # Get user profile
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        print("❌ User profile not found")
        return
    
    user_data = user_doc.to_dict()
    # Fix preferences format to match UserProfile model
    preferences = user_data.get('preferences', {})
    if 'formality' in preferences and isinstance(preferences['formality'], str):
        preferences['formality'] = [preferences['formality']]
    if 'budget' in preferences and isinstance(preferences['budget'], str):
        preferences['budget'] = [preferences['budget']]
    
    user_profile = UserProfile(
        id=user_id,
        name=user_data.get('name', ''),
        email=user_data.get('email', ''),
        gender=user_data.get('gender'),
        preferences=preferences,
        measurements=user_data.get('measurements', {}),
        stylePreferences=user_data.get('stylePreferences', []),
        bodyType=user_data.get('bodyType', ''),
        skinTone=user_data.get('skinTone'),
        createdAt=user_data.get('createdAt', 0),
        updatedAt=user_data.get('updatedAt', 0)
    )
    
    # Get wardrobe items
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_docs = wardrobe_ref.where('userId', '==', user_id).stream()
    
    wardrobe_items = []
    for doc in wardrobe_docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        try:
            item = ClothingItem(**item_data)
            wardrobe_items.append(item)
        except Exception as e:
            print(f"⚠️  Skipping item {doc.id}: {e}")
    
    print(f"\n👕 Wardrobe items: {len(wardrobe_items)}")
    
    # Create weather data
    weather = WeatherData(
        temperature=69.2,
        condition="sunny",
        humidity=50,
        wind_speed=5
    )
    
    # Test outfit generation
    print(f"\n🔄 Testing outfit generation...")
    
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
                
        # Test layering validation specifically
        print(f"\n🔍 Testing layering validation specifically:")
        layering_validation = outfit_service._validate_layering_compliance(result.items, layering_rule)
        print(f"   - Is compliant: {layering_validation['is_compliant']}")
        print(f"   - Layer count: {layering_validation['layer_count']}")
        print(f"   - Missing layers: {layering_validation['missing_layers']}")
        print(f"   - Suggestions: {layering_validation['suggestions']}")
        
        # Check what types of items we have
        item_types = [item.type.value if hasattr(item.type, 'value') else str(item.type) for item in result.items]
        print(f"   - Item types: {item_types}")
        
        # Check which items count as layers
        layer_types = [lt.value for lt in layering_rule.layer_types]
        layer_items = []
        for item in result.items:
            item_type_str = item.type.value if hasattr(item.type, 'value') else str(item.type)
            if item_type_str in layer_types:
                layer_items.append(item.name)
        
        print(f"   - Items that count as layers: {layer_items}")
        
    else:
        print(f"   ⚠️  No items selected!")

if __name__ == "__main__":
    asyncio.run(debug_layering_validation()) 