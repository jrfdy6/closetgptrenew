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

async def check_wardrobe_items():
    """Check if the user's actual wardrobe items are in the database"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your user ID
    
    print(f"Checking wardrobe items for user: {user_id}")
    
    # Query wardrobe collection
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_query = wardrobe_ref.where('userId', '==', user_id)
    
    item_docs = wardrobe_query.stream()
    
    items = []
    for doc in item_docs:
        item_data = doc.to_dict()
        items.append({
            'id': doc.id,
            'name': item_data.get('name', 'Unknown'),
            'type': item_data.get('type', 'Unknown'),
            'brand': item_data.get('brand', 'Unknown'),
            'color': item_data.get('color', 'Unknown')
        })
    
    print(f"\nFound {len(items)} wardrobe items:")
    
    if items:
        for i, item in enumerate(items[:10], 1):  # Show first 10
            print(f"  {i}. {item['name']} ({item['type']}) - {item['brand']} - {item['color']}")
        
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more items")
        
        # Show item types breakdown
        type_counts = {}
        for item in items:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        print(f"\nItem types breakdown:")
        for item_type, count in sorted(type_counts.items()):
            print(f"  {item_type}: {count} items")
    else:
        print("  No wardrobe items found for this user")
        
        # Check if there are any items for other users
        print("\nChecking for items from other users...")
        all_items = wardrobe_ref.stream()
        other_users = set()
        
        for doc in all_items:
            item_data = doc.to_dict()
            other_user = item_data.get('userId')
            if other_user and other_user != user_id:
                other_users.add(other_user)
        
        if other_users:
            print(f"Found items from {len(other_users)} other users:")
            for other_user in list(other_users)[:5]:  # Show first 5
                print(f"  {other_user}")
        else:
            print("No wardrobe items found in the entire database")

if __name__ == "__main__":
    asyncio.run(check_wardrobe_items()) 