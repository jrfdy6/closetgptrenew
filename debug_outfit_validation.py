#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# Initialize Firebase
cred = credentials.Certificate('service-account-key.json')
firebase_admin.initialize_app(cred)

async def debug_outfit_validation():
    """Debug outfit validation issues."""
    outfit_id = '005222b7-d95e-45d4-8a9c-e0704372d606'
    
    print(f"Debugging outfit validation for ID: {outfit_id}")
    
    try:
        # Get the document directly from Firestore
        db = firestore.client()
        doc = db.collection('outfits').document(outfit_id).get()
        
        if not doc.exists:
            print(f"❌ Document {outfit_id} does not exist in Firestore")
            return
        
        print(f"✅ Document {outfit_id} exists in Firestore")
        
        # Get the raw data
        outfit_data = doc.to_dict()
        outfit_data['id'] = doc.id
        
        print(f"Raw data keys: {list(outfit_data.keys())}")
        print(f"Items count: {len(outfit_data.get('items', []))}")
        print(f"Has mood field: {'mood' in outfit_data}")
        print(f"Mood value: {outfit_data.get('mood', 'NOT_FOUND')}")
        
        # Check items structure
        items = outfit_data.get('items', [])
        if items:
            print(f"\nFirst item structure:")
            first_item = items[0]
            print(f"  Type: {type(first_item)}")
            if isinstance(first_item, dict):
                print(f"  Keys: {list(first_item.keys())}")
                print(f"  Has 'id': {'id' in first_item}")
                print(f"  Has 'name': {'name' in first_item}")
                print(f"  Has 'type': {'type' in first_item}")
            else:
                print(f"  Value: {first_item}")
        
        # Try to import and test the Pydantic model
        try:
            from types.outfit import OutfitGeneratedOutfit
            print(f"\nTesting OutfitGeneratedOutfit validation...")
            
            # Try to create the model
            outfit_model = OutfitGeneratedOutfit(**outfit_data)
            print(f"✅ OutfitGeneratedOutfit validation successful!")
            print(f"   - Name: {outfit_model.name}")
            print(f"   - Style: {outfit_model.style}")
            print(f"   - Mood: {outfit_model.mood}")
            print(f"   - Items: {len(outfit_model.items)}")
            
        except Exception as e:
            print(f"❌ OutfitGeneratedOutfit validation failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_outfit_validation()) 