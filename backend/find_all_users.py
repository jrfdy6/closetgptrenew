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

async def find_all_users():
    """Find all users who have outfits in the database"""
    
    print("Searching for all users with outfits...")
    
    # Query outfits collection to get all unique user IDs
    outfits_ref = db.collection('outfits')
    outfit_docs = outfits_ref.stream()
    
    user_outfit_counts = {}
    
    for doc in outfit_docs:
        outfit_data = doc.to_dict()
        user_id = outfit_data.get('user_id')
        if user_id:
            if user_id not in user_outfit_counts:
                user_outfit_counts[user_id] = 0
            user_outfit_counts[user_id] += 1
    
    print(f"\nFound {len(user_outfit_counts)} users with outfits:")
    for user_id, count in user_outfit_counts.items():
        print(f"  User {user_id}: {count} outfits")
        
        # Show a sample outfit name for each user
        sample_outfit = outfits_ref.where('user_id', '==', user_id).limit(1).stream()
        for outfit_doc in sample_outfit:
            outfit_data = outfit_doc.to_dict()
            print(f"    Sample outfit: {outfit_data.get('name', 'Unknown')}")
            break

if __name__ == "__main__":
    asyncio.run(find_all_users()) 