#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def debug_outfit_fields():
    """Check what fields are missing from outfits"""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Test user ID from auth service
    
    print(f"Checking outfit fields for user: {user_id}")
    
    # Query outfits collection
    outfits_ref = db.collection('outfits')
    outfits_query = outfits_ref.where('user_id', '==', user_id)
    
    outfit_docs = outfits_query.stream()
    
    required_fields = ['name', 'style', 'mood', 'items', 'occasion', 'confidence_score', 'reasoning', 'createdAt']
    
    for i, doc in enumerate(outfit_docs):
        outfit_data = doc.to_dict()
        print(f"\n--- Outfit {i+1}: {outfit_data.get('name', 'Unknown')} ---")
        
        missing_fields = []
        for field in required_fields:
            if field not in outfit_data:
                missing_fields.append(field)
            else:
                value = outfit_data[field]
                if field == 'items':
                    print(f"  {field}: {len(value) if isinstance(value, list) else 'NOT A LIST'} items")
                elif field == 'confidence_score':
                    print(f"  {field}: {value} (type: {type(value).__name__})")
                else:
                    print(f"  {field}: {value}")
        
        if missing_fields:
            print(f"  ❌ MISSING FIELDS: {missing_fields}")
        else:
            print(f"  ✅ All required fields present")

if __name__ == "__main__":
    asyncio.run(debug_outfit_fields()) 