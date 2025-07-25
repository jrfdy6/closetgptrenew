#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def debug_outfit_items():
    """Debug the outfit items issue"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Debugging outfit items for user: {user_id}")
    
    # Get all outfits for this user
    outfits_ref = db.collection('outfits')
    user_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    
    for outfit_doc in user_outfits:
        outfit_data = outfit_doc.to_dict()
        outfit_id = outfit_doc.id
        
        print(f"\n📋 Outfit: {outfit_data.get('name', 'Unknown')} (ID: {outfit_id})")
        print(f"   Items type: {type(outfit_data.get('items', 'NOT_FOUND'))}")
        
        if 'items' in outfit_data:
            items = outfit_data['items']
            print(f"   Items length: {len(items) if isinstance(items, list) else 'NOT_LIST'}")
            
            if isinstance(items, list):
                print(f"   Items content:")
                for i, item in enumerate(items):
                    print(f"     {i+1}. Type: {type(item)}, Value: {item}")
                    
                    # If it's a string (item ID), check if it exists in wardrobe
                    if isinstance(item, str):
                        try:
                            item_doc = db.collection("wardrobe").document(item).get()
                            if item_doc.exists:
                                print(f"       ✅ Item exists in wardrobe")
                            else:
                                print(f"       ❌ Item NOT found in wardrobe")
                        except Exception as e:
                            print(f"       ❌ Error checking item: {e}")
        
        # Check if outfit has pieces (alternative item representation)
        if 'pieces' in outfit_data:
            pieces = outfit_data['pieces']
            print(f"   Pieces length: {len(pieces) if isinstance(pieces, list) else 'NOT_LIST'}")
            
            if isinstance(pieces, list) and pieces:
                print(f"   First piece: {pieces[0] if pieces else 'None'}")

if __name__ == "__main__":
    asyncio.run(debug_outfit_items()) 