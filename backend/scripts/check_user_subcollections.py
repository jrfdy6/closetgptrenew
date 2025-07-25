#!/usr/bin/env python3
"""
Check for wardrobe items stored as subcollections under user documents.
This is the correct structure where each user has their own wardrobe subcollection.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def check_user_subcollections():
    """Check for users and their wardrobe subcollections."""
    print("🔍 Checking User Subcollections")
    print("=" * 60)
    
    # First, check if there's a users collection
    try:
        users = list(db.collection('users').stream())
        print(f"Found {len(users)} users in 'users' collection")
        
        if len(users) > 0:
            for i, user in enumerate(users):
                user_data = user.to_dict()
                user_id = user.id
                print(f"\n👤 User {i+1}: {user_id}")
                print(f"  Data: {list(user_data.keys())}")
                
                # Check for wardrobe subcollection
                try:
                    wardrobe_items = list(user.reference.collection('wardrobe').stream())
                    print(f"  Wardrobe items: {len(wardrobe_items)}")
                    
                    if len(wardrobe_items) > 0:
                        print(f"  Sample items:")
                        for j, item in enumerate(wardrobe_items[:3]):
                            item_data = item.to_dict()
                            name = item_data.get('name', 'No name')
                            item_type = item_data.get('type', 'No type')
                            print(f"    {j+1}. {name} ({item_type})")
                        
                        if len(wardrobe_items) > 3:
                            print(f"    ... and {len(wardrobe_items) - 3} more")
                    
                except Exception as e:
                    print(f"  ❌ Error checking wardrobe: {e}")
                
                # Check for other possible subcollections
                try:
                    subcollections = list(user.reference.collections())
                    if subcollections:
                        print(f"  Other subcollections: {[col.id for col in subcollections]}")
                except Exception as e:
                    print(f"  ❌ Error checking subcollections: {e}")
                    
        else:
            print("No users found in 'users' collection")
            
    except Exception as e:
        print(f"❌ Error accessing 'users' collection: {e}")

def check_alternative_user_collections():
    """Check for users in alternative collection names."""
    print(f"\n🔍 Checking Alternative User Collections:")
    print("=" * 60)
    
    # Check for alternative user collection names
    user_collections = ['user', 'accounts', 'profiles', 'auth']
    
    for collection_name in user_collections:
        try:
            users = list(db.collection(collection_name).stream())
            if len(users) > 0:
                print(f"✅ Found {len(users)} users in '{collection_name}' collection")
                
                for i, user in enumerate(users[:3]):  # Show first 3
                    user_data = user.to_dict()
                    user_id = user.id
                    print(f"  User {i+1}: {user_id}")
                    
                    # Check for wardrobe subcollection
                    try:
                        wardrobe_items = list(user.reference.collection('wardrobe').stream())
                        print(f"    Wardrobe items: {len(wardrobe_items)}")
                        
                        if len(wardrobe_items) > 0:
                            # Show sample
                            sample = wardrobe_items[0].to_dict()
                            print(f"    Sample: {sample.get('name', 'No name')}")
                            
                    except Exception as e:
                        print(f"    ❌ Error checking wardrobe: {e}")
                        
            else:
                print(f"❌ '{collection_name}': No users found")
                
        except Exception as e:
            print(f"❌ '{collection_name}': Collection doesn't exist")

def check_clothingItems_for_users():
    """Check if clothingItems collection has user IDs that we can use to find users."""
    print(f"\n🔍 Checking clothingItems for User IDs:")
    print("=" * 60)
    
    try:
        clothing_items = list(db.collection('clothingItems').stream())
        print(f"Found {len(clothing_items)} clothing items")
        
        if len(clothing_items) > 0:
            # Extract unique user IDs
            user_ids = set()
            for item in clothing_items:
                item_data = item.to_dict()
                if 'userId' in item_data:
                    user_ids.add(item_data['userId'])
            
            print(f"Found {len(user_ids)} unique user IDs:")
            for user_id in user_ids:
                print(f"  - {user_id}")
                
                # Try to find this user in the users collection
                try:
                    user_doc = db.collection('users').document(user_id).get()
                    if user_doc.exists:
                        print(f"    ✅ User found in 'users' collection")
                        user_data = user_doc.to_dict()
                        print(f"    User data: {list(user_data.keys())}")
                        
                        # Check for wardrobe subcollection
                        try:
                            wardrobe_items = list(user_doc.reference.collection('wardrobe').stream())
                            print(f"    Wardrobe items: {len(wardrobe_items)}")
                            
                            if len(wardrobe_items) > 0:
                                print(f"    Sample items:")
                                for i, item in enumerate(wardrobe_items[:3]):
                                    item_data = item.to_dict()
                                    name = item_data.get('name', 'No name')
                                    item_type = item_data.get('type', 'No type')
                                    print(f"      {i+1}. {name} ({item_type})")
                                    
                        except Exception as e:
                            print(f"    ❌ Error checking wardrobe subcollection: {e}")
                    else:
                        print(f"    ❌ User not found in 'users' collection")
                        
                except Exception as e:
                    print(f"    ❌ Error checking user: {e}")
                    
    except Exception as e:
        print(f"❌ Error checking clothingItems: {e}")

def check_all_collections_for_users():
    """Check all collections for documents that might be users."""
    print(f"\n🔍 Checking All Collections for User Documents:")
    print("=" * 60)
    
    try:
        collections = db.collections()
        for collection in collections:
            try:
                docs = list(collection.limit(5).stream())
                if len(docs) > 0:
                    # Check if any documents look like users (have email, displayName, etc.)
                    user_like_docs = []
                    for doc in docs:
                        data = doc.to_dict()
                        user_fields = ['email', 'displayName', 'uid', 'photoURL', 'emailVerified']
                        if any(field in data for field in user_fields):
                            user_like_docs.append(doc)
                    
                    if user_like_docs:
                        print(f"📁 {collection.id}: Found {len(user_like_docs)} user-like documents")
                        for doc in user_like_docs:
                            data = doc.to_dict()
                            print(f"  User: {doc.id}")
                            print(f"    Fields: {list(data.keys())}")
                            
                            # Check for wardrobe subcollection
                            try:
                                wardrobe_items = list(doc.reference.collection('wardrobe').stream())
                                print(f"    Wardrobe items: {len(wardrobe_items)}")
                                
                                if len(wardrobe_items) > 0:
                                    print(f"    Sample items:")
                                    for i, item in enumerate(wardrobe_items[:2]):
                                        item_data = item.to_dict()
                                        name = item_data.get('name', 'No name')
                                        print(f"      {i+1}. {name}")
                                        
                            except Exception as e:
                                print(f"    ❌ Error checking wardrobe: {e}")
                                
            except Exception as e:
                print(f"❌ Error checking {collection.id}: {e}")
                
    except Exception as e:
        print(f"❌ Error listing collections: {e}")

if __name__ == "__main__":
    check_user_subcollections()
    check_alternative_user_collections()
    check_clothingItems_for_users()
    check_all_collections_for_users()
    
    print(f"\n💡 Summary:")
    print("=" * 30)
    print("This script checks for:")
    print("1. Users in the 'users' collection")
    print("2. Wardrobe subcollections under each user")
    print("3. Alternative user collection names")
    print("4. User IDs from clothingItems")
    print("5. User-like documents in all collections")
    print("6. The correct nested structure for your data") 