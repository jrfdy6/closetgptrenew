#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Initialize Firebase first
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Now import the services
from services.outfit_service import OutfitService
from types.weather import WeatherData
from types.profile import UserProfile
from types.wardrobe import ClothingItem, ClothingType

async def test_outfit_retrieval():
    outfit_service = OutfitService()
    
    # First, let's check if there are any existing outfits
    outfits_ref = db.collection('outfits')
    outfits_docs = outfits_ref.limit(5).stream()
    
    existing_outfits = []
    for doc in outfits_docs:
        outfit_data = doc.to_dict()
        outfit_data['id'] = doc.id
        existing_outfits.append(outfit_data)
        print(f"Found outfit: {doc.id} - {outfit_data.get('name', 'Unknown')}")
        print(f"  Items count: {len(outfit_data.get('items', []))}")
        print(f"  Was successful: {outfit_data.get('wasSuccessful', 'Unknown')}")
        print(f"  Validation errors: {outfit_data.get('validationErrors', [])}")
        print()
    
    if not existing_outfits:
        print("No existing outfits found")
        return
    
    # Test retrieval for each existing outfit
    for outfit_data in existing_outfits:
        outfit_id = outfit_data['id']
        print(f"Testing retrieval for outfit: {outfit_id}")
        
        try:
            retrieved_outfit = await outfit_service.get_outfit(outfit_id)
            if retrieved_outfit:
                print(f"✅ Successfully retrieved outfit: {retrieved_outfit.name}")
                print(f"   Items count: {len(retrieved_outfit.items)}")
                print(f"   Was successful: {retrieved_outfit.wasSuccessful}")
            else:
                print(f"❌ Failed to retrieve outfit: {outfit_id}")
        except Exception as e:
            print(f"❌ Error retrieving outfit {outfit_id}: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == '__main__':
    asyncio.run(test_outfit_retrieval()) 