#!/usr/bin/env python3
"""
Fix missing user document and check wardrobe subcollection access.
This will help restore access to the nested wardrobe data.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def analyze_clothing_items():
    """Analyze clothing items to understand the user structure."""
    print("🔍 Analyzing Clothing Items")
    print("=" * 50)
    
    try:
        clothing_items = list(db.collection('clothingItems').stream())
        print(f"Found {len(clothing_items)} clothing items")
        
        if len(clothing_items) > 0:
            # Group by user ID
            users_data = {}
            for item in clothing_items:
                item_data = item.to_dict()
                user_id = item_data.get('userId')
                
                if user_id not in users_data:
                    users_data[user_id] = {
                        'items': [],
                        'item_types': set(),
                        'created_dates': []
                    }
                
                users_data[user_id]['items'].append(item_data)
                users_data[user_id]['item_types'].add(item_data.get('type', 'unknown'))
                
                if 'createdAt' in item_data:
                    users_data[user_id]['created_dates'].append(item_data['createdAt'])
            
            print(f"Found {len(users_data)} unique users:")
            for user_id, data in users_data.items():
                print(f"\n👤 User: {user_id}")
                print(f"  Items: {len(data['items'])}")
                print(f"  Types: {list(data['item_types'])}")
                print(f"  Date range: {min(data['created_dates']) if data['created_dates'] else 'N/A'} to {max(data['created_dates']) if data['created_dates'] else 'N/A'}")
                
                # Show sample items
                print(f"  Sample items:")
                for i, item in enumerate(data['items'][:3]):
                    name = item.get('name', 'No name')
                    item_type = item.get('type', 'No type')
                    print(f"    {i+1}. {name} ({item_type})")
                
                return user_id, data
                
    except Exception as e:
        print(f"❌ Error analyzing clothing items: {e}")
        return None, None

def check_if_user_exists_in_auth():
    """Check if user exists in Firebase Auth (if accessible)."""
    print(f"\n🔐 Checking Firebase Auth:")
    print("=" * 50)
    
    try:
        # Try to get user from Auth (this might not work with service account)
        from firebase_admin import auth
        user_id = "QQRTxdxhZ0MPoW5lM3MI01cpYY72"
        
        try:
            user_record = auth.get_user(user_id)
            print(f"✅ User found in Firebase Auth:")
            print(f"  UID: {user_record.uid}")
            print(f"  Email: {user_record.email}")
            print(f"  Display Name: {user_record.display_name}")
            print(f"  Created: {user_record.user_metadata.creation_timestamp}")
            return user_record
        except Exception as e:
            print(f"❌ User not found in Auth: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing Firebase Auth: {e}")
        return None

def create_missing_user_document(user_id, user_data=None):
    """Create a missing user document based on clothing items data."""
    print(f"\n👤 Creating Missing User Document:")
    print("=" * 50)
    
    try:
        # Check if user document already exists
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            print(f"✅ User document already exists for {user_id}")
            return user_doc.to_dict()
        
        # Create basic user document
        user_document = {
            'id': user_id,
            'uid': user_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'wardrobeCount': len(user_data['items']) if user_data else 0,
            'itemTypes': list(user_data['item_types']) if user_data else [],
            'lastActive': firestore.SERVER_TIMESTAMP
        }
        
        # Add email if we have it from Auth
        auth_user = check_if_user_exists_in_auth()
        if auth_user and auth_user.email:
            user_document['email'] = auth_user.email
            user_document['displayName'] = auth_user.display_name
        
        # Create the user document
        user_ref.set(user_document)
        print(f"✅ Created user document for {user_id}")
        print(f"  Document data: {user_document}")
        
        return user_document
        
    except Exception as e:
        print(f"❌ Error creating user document: {e}")
        return None

def check_wardrobe_subcollection(user_id):
    """Check if wardrobe subcollection exists under the user."""
    print(f"\n👕 Checking Wardrobe Subcollection:")
    print("=" * 50)
    
    try:
        user_ref = db.collection('users').document(user_id)
        wardrobe_ref = user_ref.collection('wardrobe')
        
        # Check if wardrobe subcollection exists
        wardrobe_items = list(wardrobe_ref.stream())
        print(f"Found {len(wardrobe_items)} items in wardrobe subcollection")
        
        if len(wardrobe_items) > 0:
            print(f"Sample items:")
            for i, item in enumerate(wardrobe_items[:5]):
                item_data = item.to_dict()
                name = item_data.get('name', 'No name')
                item_type = item_data.get('type', 'No type')
                print(f"  {i+1}. {name} ({item_type})")
                
            return len(wardrobe_items)
        else:
            print("No items found in wardrobe subcollection")
            return 0
            
    except Exception as e:
        print(f"❌ Error checking wardrobe subcollection: {e}")
        return 0

def migrate_clothing_items_to_wardrobe(user_id):
    """Migrate clothing items from top-level collection to user's wardrobe subcollection."""
    print(f"\n🔄 Migrating Clothing Items to Wardrobe Subcollection:")
    print("=" * 50)
    
    try:
        # Get all clothing items for this user
        clothing_items = list(db.collection('clothingItems').where('userId', '==', user_id).stream())
        print(f"Found {len(clothing_items)} clothing items to migrate")
        
        if len(clothing_items) == 0:
            print("No clothing items found to migrate")
            return 0
        
        # Get wardrobe subcollection reference
        user_ref = db.collection('users').document(user_id)
        wardrobe_ref = user_ref.collection('wardrobe')
        
        migrated_count = 0
        for item in clothing_items:
            try:
                item_data = item.to_dict()
                item_id = item.id
                
                # Check if item already exists in wardrobe
                existing = wardrobe_ref.document(item_id).get()
                if existing.exists:
                    print(f"  ⚠️  Item {item_id} already exists in wardrobe, skipping")
                    continue
                
                # Add to wardrobe subcollection
                wardrobe_ref.document(item_id).set(item_data)
                print(f"  ✅ Migrated: {item_data.get('name', 'No name')}")
                migrated_count += 1
                
            except Exception as e:
                print(f"  ❌ Error migrating item {item.id}: {e}")
        
        print(f"\n✅ Successfully migrated {migrated_count} items to wardrobe subcollection")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return 0

if __name__ == "__main__":
    # Analyze existing data
    user_id, user_data = analyze_clothing_items()
    
    if user_id:
        # Create missing user document
        user_doc = create_missing_user_document(user_id, user_data)
        
        if user_doc:
            # Check wardrobe subcollection
            wardrobe_count = check_wardrobe_subcollection(user_id)
            
            # If no items in wardrobe subcollection, migrate them
            if wardrobe_count == 0:
                migrated = migrate_clothing_items_to_wardrobe(user_id)
                if migrated > 0:
                    # Check again after migration
                    final_count = check_wardrobe_subcollection(user_id)
                    print(f"\n🎉 Final wardrobe count: {final_count} items")
    
    print(f"\n💡 Summary:")
    print("=" * 30)
    print("This script:")
    print("1. Analyzes existing clothing items")
    print("2. Creates missing user document")
    print("3. Checks for wardrobe subcollection")
    print("4. Migrates items to correct structure")
    print("5. Restores access to nested wardrobe data") 