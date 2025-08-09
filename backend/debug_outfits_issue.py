#!/usr/bin/env python3
"""
Debug script to check why outfits aren't showing up for the current user.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def debug_outfits_issue():
    """Debug why outfits aren't showing up for the current user."""
    print("🔍 Debugging Outfits Issue")
    print("=" * 60)
    
    # Get all outfits
    all_outfits = list(db.collection('outfits').stream())
    print(f"📊 Total outfits in database: {len(all_outfits)}")
    
    # Check for outfits with user_id field
    outfits_with_user_id = []
    outfits_with_userId = []
    outfits_with_no_user = []
    
    for doc in all_outfits:
        data = doc.to_dict()
        outfit_id = doc.id
        
        # Check for user_id field
        user_id = data.get('user_id')
        userId = data.get('userId')
        
        if user_id:
            outfits_with_user_id.append((outfit_id, user_id))
        elif userId:
            outfits_with_userId.append((outfit_id, userId))
        else:
            outfits_with_no_user.append(outfit_id)
    
    print(f"\n📊 Outfits with 'user_id' field: {len(outfits_with_user_id)}")
    for outfit_id, user_id in outfits_with_user_id[:5]:  # Show first 5
        print(f"  - {outfit_id}: {user_id}")
    
    print(f"\n📊 Outfits with 'userId' field: {len(outfits_with_userId)}")
    for outfit_id, userId in outfits_with_userId[:5]:  # Show first 5
        print(f"  - {outfit_id}: {userId}")
    
    print(f"\n📊 Outfits with no user field: {len(outfits_with_no_user)}")
    for outfit_id in outfits_with_no_user[:5]:  # Show first 5
        print(f"  - {outfit_id}")
    
    # Check for recent outfits (last 24 hours)
    print(f"\n🔍 Checking for recent outfits (last 24 hours)...")
    recent_outfits = []
    current_time = datetime.now()
    
    for doc in all_outfits:
        data = doc.to_dict()
        created_at = data.get('createdAt')
        
        if created_at:
            # Convert to datetime if it's a timestamp
            if isinstance(created_at, (int, float)):
                if created_at > 1000000000000:  # Milliseconds
                    created_dt = datetime.fromtimestamp(created_at / 1000)
                else:  # Seconds
                    created_dt = datetime.fromtimestamp(created_at)
            else:
                # Try to parse as string
                try:
                    created_dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                except:
                    continue
            
            # Check if it's within last 24 hours
            if (current_time - created_dt).days < 1:
                recent_outfits.append({
                    'id': doc.id,
                    'name': data.get('name', 'Unknown'),
                    'user_id': data.get('user_id'),
                    'userId': data.get('userId'),
                    'created_at': created_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'items_count': len(data.get('items', []))
                })
    
    print(f"\n📊 Recent outfits (last 24 hours): {len(recent_outfits)}")
    for outfit in recent_outfits:
        print(f"  - {outfit['name']} (ID: {outfit['id']})")
        print(f"    Created: {outfit['created_at']}")
        print(f"    User ID: {outfit['user_id'] or 'None'}")
        print(f"    UserId: {outfit['userId'] or 'None'}")
        print(f"    Items: {outfit['items_count']}")
        print()
    
    # Check for specific user IDs that might be in use
    print(f"\n🔍 Checking for common user IDs...")
    user_ids_found = set()
    for doc in all_outfits:
        data = doc.to_dict()
        if data.get('user_id'):
            user_ids_found.add(data['user_id'])
        if data.get('userId'):
            user_ids_found.add(data['userId'])
    
    print(f"📊 Unique user IDs found: {len(user_ids_found)}")
    for user_id in sorted(user_ids_found):
        print(f"  - {user_id}")
    
    # Check the test user ID specifically
    test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    test_user_outfits = []
    
    for doc in all_outfits:
        data = doc.to_dict()
        if data.get('user_id') == test_user_id or data.get('userId') == test_user_id:
            test_user_outfits.append({
                'id': doc.id,
                'name': data.get('name', 'Unknown'),
                'created_at': data.get('createdAt'),
                'items_count': len(data.get('items', []))
            })
    
    print(f"\n📊 Outfits for test user {test_user_id}: {len(test_user_outfits)}")
    for outfit in test_user_outfits:
        print(f"  - {outfit['name']} (ID: {outfit['id']})")
        print(f"    Created: {outfit['created_at']}")
        print(f"    Items: {outfit['items_count']}")

if __name__ == "__main__":
    debug_outfits_issue()
