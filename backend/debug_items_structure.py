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

async def debug_items_structure():
    """Check the detailed structure of items field"""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Test user ID from auth service
    
    print(f"Checking items structure for user: {user_id}")
    
    # Query outfits collection
    outfits_ref = db.collection('outfits')
    outfits_query = outfits_ref.where('user_id', '==', user_id)
    
    outfit_docs = outfits_query.stream()
    
    for i, doc in enumerate(outfit_docs, 1):
        outfit_data = doc.to_dict()
        print(f"\n--- Outfit {i}: {outfit_data.get('name', 'Unknown')} ---")
        
        items = outfit_data.get('items', [])
        print(f"  Items type: {type(items)}")
        print(f"  Items length: {len(items)}")
        
        if items:
            print("  Items content:")
            for j, item in enumerate(items):
                print(f"    Item {j}: {type(item)} = {item}")
                if isinstance(item, str):
                    print(f"      (This is a string ID, not a dictionary)")
                elif isinstance(item, dict):
                    print(f"      Keys: {list(item.keys())}")
        else:
            print("  No items")
        
        print(f"  Other fields: {list(outfit_data.keys())}")

if __name__ == "__main__":
    asyncio.run(debug_items_structure()) 