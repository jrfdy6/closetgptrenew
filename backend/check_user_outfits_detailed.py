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

async def check_user_outfits_detailed():
    """Check outfits for all users to find realistic outfit names"""
    
    users_to_check = ['test-user', 'test-user-123', 'test_user', 'default-user', 'test']
    
    for user_id in users_to_check:
        print(f"\n=== Checking outfits for user: {user_id} ===")
        
        # Query outfits collection
        outfits_ref = db.collection('outfits')
        outfits_query = outfits_ref.where('user_id', '==', user_id)
        
        outfit_docs = outfits_query.stream()
        
        outfit_count = 0
        realistic_outfits = []
        
        for doc in outfit_docs:
            outfit_data = doc.to_dict()
            outfit_count += 1
            
            name = outfit_data.get('name', 'Unknown')
            
            # Check if this looks like a realistic outfit name (not AI-generated)
            if not any(keyword in name.lower() for keyword in ['outfit', 'techwear', 'streetwear', 'grunge', 'avant-garde', 'bohemian']):
                realistic_outfits.append(name)
            
            # Show first 5 outfits
            if outfit_count <= 5:
                print(f"  {outfit_count}. {name}")
        
        print(f"  Total outfits: {outfit_count}")
        
        if realistic_outfits:
            print(f"  Realistic outfit names found: {realistic_outfits[:5]}")  # Show first 5
        else:
            print("  All outfits appear to be AI-generated/test outfits")

if __name__ == "__main__":
    asyncio.run(check_user_outfits_detailed()) 