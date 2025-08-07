#!/usr/bin/env python3

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_user_outfits(user_id: str):
    """Check what outfits exist in Firestore for a specific user."""
    
    # Initialize Firebase with service account key
    if not firebase_admin._apps:
        cred = credentials.Certificate('service-account-key.json')
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print(f"🔍 Checking outfits for user: {user_id}")
    print("=" * 50)
    
    # Get all outfits
    outfits_ref = db.collection('outfits')
    all_outfits = outfits_ref.stream()
    
    user_outfits = []
    other_outfits = []
    
    for doc in all_outfits:
        outfit_data = doc.to_dict()
        outfit_id = doc.id
        
        # Check if outfit has user_id field
        outfit_user_id = outfit_data.get('user_id')
        
        # Check items for userId
        items = outfit_data.get('items', [])
        user_items_count = 0
        total_items = len(items)
        
        for item in items:
            if isinstance(item, dict) and item.get('userId') == user_id:
                user_items_count += 1
            elif isinstance(item, str):
                # Check wardrobe collection
                try:
                    item_doc = db.collection('wardrobe').document(item).get()
                    if item_doc.exists:
                        item_data = item_doc.to_dict()
                        if item_data.get('userId') == user_id:
                            user_items_count += 1
                except Exception as e:
                    print(f"Error checking item {item}: {e}")
        
        outfit_info = {
            'id': outfit_id,
            'name': outfit_data.get('name', 'Unknown'),
            'user_id_field': outfit_user_id,
            'user_items': user_items_count,
            'total_items': total_items,
            'createdAt': outfit_data.get('createdAt'),
            'items': items
        }
        
        # Determine if this outfit belongs to the user
        belongs_to_user = False
        
        # Check if outfit has user_id field matching user
        if outfit_user_id == user_id:
            belongs_to_user = True
            print(f"✅ Outfit {outfit_id} has user_id field: {outfit_user_id}")
        
        # Check if all items belong to user
        elif user_items_count > 0 and user_items_count == total_items:
            belongs_to_user = True
            print(f"✅ Outfit {outfit_id} has all user items: {user_items_count}/{total_items}")
        
        # Check if most items belong to user (at least 50%)
        elif user_items_count > 0 and user_items_count >= total_items * 0.5:
            belongs_to_user = True
            print(f"⚠️  Outfit {outfit_id} has mostly user items: {user_items_count}/{total_items}")
        
        if belongs_to_user:
            user_outfits.append(outfit_info)
        else:
            other_outfits.append(outfit_info)
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY:")
    print(f"Total outfits in database: {len(user_outfits) + len(other_outfits)}")
    print(f"Outfits belonging to user {user_id}: {len(user_outfits)}")
    print(f"Other outfits: {len(other_outfits)}")
    
    print("\n" + "=" * 50)
    print(f"👤 YOUR OUTFITS:")
    for outfit in user_outfits:
        created_at = outfit['createdAt']
        if isinstance(created_at, (int, float)):
            created_at = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(created_at, str):
            created_at = created_at[:19]  # Truncate to first 19 chars
        
        print(f"  • {outfit['name']} (ID: {outfit['id']})")
        print(f"    - User ID field: {outfit['user_id_field']}")
        print(f"    - User items: {outfit['user_items']}/{outfit['total_items']}")
        print(f"    - Created: {created_at}")
        print()
    
    print("\n" + "=" * 50)
    print(f"🔍 OTHER OUTFITS (first 10):")
    for outfit in other_outfits[:10]:
        print(f"  • {outfit['name']} (ID: {outfit['id']})")
        print(f"    - User ID field: {outfit['user_id_field']}")
        print(f"    - User items: {outfit['user_items']}/{outfit['total_items']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_user_outfits.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    check_user_outfits(user_id) 