#!/usr/bin/env python3
"""
Check for the correct user ID and Firebase Storage structure.
The data should be in user dANqjiI0CKgaitxzYtw1bhtvQrG3 and possibly in Storage.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app, storage
import json

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def check_correct_user():
    """Check for the correct user ID in Firestore."""
    print("🔍 Checking Correct User ID")
    print("=" * 50)
    
    correct_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Check if this user exists in users collection
    try:
        user_ref = db.collection('users').document(correct_user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            print(f"✅ User found: {correct_user_id}")
            print(f"  Data: {list(user_data.keys())}")
            print(f"  Email: {user_data.get('email', 'No email')}")
            print(f"  Display Name: {user_data.get('displayName', 'No name')}")
            
            # Check for wardrobe subcollection
            try:
                wardrobe_items = list(user_ref.collection('wardrobe').stream())
                print(f"  Wardrobe items: {len(wardrobe_items)}")
                
                if len(wardrobe_items) > 0:
                    print(f"  Sample items:")
                    for i, item in enumerate(wardrobe_items[:5]):
                        item_data = item.to_dict()
                        name = item_data.get('name', 'No name')
                        item_type = item_data.get('type', 'No type')
                        print(f"    {i+1}. {name} ({item_type})")
                        
                return len(wardrobe_items)
                
            except Exception as e:
                print(f"  ❌ Error checking wardrobe: {e}")
                return 0
        else:
            print(f"❌ User {correct_user_id} not found in users collection")
            return 0
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return 0

def check_firebase_auth_for_correct_user():
    """Check if the correct user exists in Firebase Auth."""
    print(f"\n🔐 Checking Firebase Auth for Correct User:")
    print("=" * 50)
    
    correct_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    try:
        from firebase_admin import auth
        
        try:
            user_record = auth.get_user(correct_user_id)
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

def check_firebase_storage():
    """Check Firebase Storage for wardrobe data."""
    print(f"\n📁 Checking Firebase Storage:")
    print("=" * 50)
    
    try:
        bucket = storage.bucket()
        print(f"✅ Storage bucket: {bucket.name}")
        
        # List all blobs (files) in the bucket
        blobs = list(bucket.list_blobs())
        print(f"Total files in storage: {len(blobs)}")
        
        # Look for user-specific folders
        user_folders = {}
        correct_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        for blob in blobs:
            path = blob.name
            if path.startswith('Users/'):
                parts = path.split('/')
                if len(parts) >= 2:
                    user_id = parts[1]
                    if user_id not in user_folders:
                        user_folders[user_id] = []
                    user_folders[user_id].append(path)
        
        print(f"Found {len(user_folders)} user folders in storage:")
        for user_id, files in user_folders.items():
            print(f"  User {user_id}: {len(files)} files")
            if user_id == correct_user_id:
                print(f"    ⭐ This is the correct user!")
                print(f"    Sample files:")
                for i, file_path in enumerate(files[:5]):
                    print(f"      {i+1}. {file_path}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
        
        # Check specifically for the correct user's wardrobe
        correct_user_files = [blob.name for blob in blobs if blob.name.startswith(f'Users/{correct_user_id}/')]
        print(f"\n📂 Files for correct user ({correct_user_id}): {len(correct_user_files)}")
        
        if correct_user_files:
            print("Sample files:")
            for i, file_path in enumerate(correct_user_files[:10]):
                print(f"  {i+1}. {file_path}")
            if len(correct_user_files) > 10:
                print(f"  ... and {len(correct_user_files) - 10} more")
        
        return correct_user_files
        
    except Exception as e:
        print(f"❌ Error accessing Firebase Storage: {e}")
        return []

def check_all_collections_for_correct_user():
    """Check all collections for documents with the correct user ID."""
    print(f"\n🔍 Checking All Collections for Correct User:")
    print("=" * 50)
    
    correct_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    try:
        collections = db.collections()
        for collection in collections:
            try:
                # Query for documents with this user ID
                docs = list(collection.where('userId', '==', correct_user_id).stream())
                if len(docs) > 0:
                    print(f"✅ {collection.id}: {len(docs)} documents for user {correct_user_id}")
                    
                    # Show sample documents
                    for i, doc in enumerate(docs[:3]):
                        data = doc.to_dict()
                        name = data.get('name', 'No name')
                        print(f"  {i+1}. {doc.id}: {name}")
                        
                else:
                    # Also check for user_id field
                    docs = list(collection.where('user_id', '==', correct_user_id).stream())
                    if len(docs) > 0:
                        print(f"✅ {collection.id}: {len(docs)} documents for user {correct_user_id} (user_id field)")
                        
            except Exception as e:
                # Collection might not have userId field
                pass
                
    except Exception as e:
        print(f"❌ Error checking collections: {e}")

def create_correct_user_document():
    """Create user document for the correct user if it doesn't exist."""
    print(f"\n👤 Creating Correct User Document:")
    print("=" * 50)
    
    correct_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    try:
        # Check if user document exists
        user_ref = db.collection('users').document(correct_user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            print(f"✅ User document already exists for {correct_user_id}")
            return user_doc.to_dict()
        
        # Get user info from Auth
        auth_user = check_firebase_auth_for_correct_user()
        
        # Create user document
        user_document = {
            'id': correct_user_id,
            'uid': correct_user_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'lastActive': firestore.SERVER_TIMESTAMP
        }
        
        if auth_user:
            user_document['email'] = auth_user.email
            user_document['displayName'] = auth_user.display_name
        
        # Create the user document
        user_ref.set(user_document)
        print(f"✅ Created user document for {correct_user_id}")
        
        return user_document
        
    except Exception as e:
        print(f"❌ Error creating user document: {e}")
        return None

if __name__ == "__main__":
    # Check for correct user in Firestore
    wardrobe_count = check_correct_user()
    
    # Check Firebase Auth
    auth_user = check_firebase_auth_for_correct_user()
    
    # Check Firebase Storage
    storage_files = check_firebase_storage()
    
    # Check all collections
    check_all_collections_for_correct_user()
    
    # Create user document if needed
    if wardrobe_count == 0:
        user_doc = create_correct_user_document()
    
    print(f"\n💡 Summary:")
    print("=" * 30)
    print("This script checks for:")
    print("1. Correct user ID in Firestore")
    print("2. User in Firebase Auth")
    print("3. Wardrobe data in Firebase Storage")
    print("4. User documents in all collections")
    print("5. The proper data structure you described") 