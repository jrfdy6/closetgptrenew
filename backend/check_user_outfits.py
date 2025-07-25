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

async def check_user_outfits():
    """Check outfits for the test user"""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Test user ID from auth service
    
    print(f"Checking outfits for user: {user_id}")
    
    # Query outfits collection
    outfits_ref = db.collection('outfits')
    outfits_query = outfits_ref.where('user_id', '==', user_id)
    
    outfit_docs = outfits_query.stream()
    
    outfits = []
    for doc in outfit_docs:
        outfit_data = doc.to_dict()
        outfits.append({
            'id': doc.id,
            'name': outfit_data.get('name', 'Unknown'),
            'occasion': outfit_data.get('occasion', 'Unknown'),
            'createdAt': outfit_data.get('createdAt', 'Unknown'),
            'items_count': len(outfit_data.get('items', []))
        })
    
    print(f"Found {len(outfits)} outfits:")
    for outfit in outfits:
        print(f"  - {outfit['name']} ({outfit['occasion']}) - {outfit['items_count']} items")
    
    if not outfits:
        print("No outfits found for this user.")
        print("This explains why you're only seeing test outfits in the frontend.")
        print("You need to generate some outfits first or check if you're using the correct user ID.")

if __name__ == "__main__":
    asyncio.run(check_user_outfits()) 