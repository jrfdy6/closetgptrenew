#!/usr/bin/env python3
"""
Test Firebase connection and check for users/data
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore, auth

def test_firebase_connection():
    """Test Firebase connection and list users"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            
            # Check for service account key
            service_account_path = "service-account-key.json"
            if os.path.exists(service_account_path):
                print(f"✅ Found service account key: {service_account_path}")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                print("❌ No service account key found")
                return False
        else:
            print("✅ Firebase already initialized")
        
        # Test Firestore connection
        db = firestore.client()
        print("✅ Firestore client created")
        
        # List collections
        collections = db.collections()
        print(f"📁 Collections found: {[col.id for col in collections]}")
        
        # Check for users collection
        users_ref = db.collection('users')
        users = list(users_ref.limit(5).stream())
        print(f"👥 Users found: {len(users)}")
        for user in users:
            print(f"  - User ID: {user.id}")
            user_data = user.to_dict()
            print(f"    Email: {user_data.get('email', 'N/A')}")
            print(f"    Name: {user_data.get('name', 'N/A')}")
        
        # Check for wardrobe collection
        wardrobe_ref = db.collection('wardrobe')
        wardrobe_items = list(wardrobe_ref.limit(5).stream())
        print(f"👕 Wardrobe items found: {len(wardrobe_items)}")
        for item in wardrobe_items:
            print(f"  - Item ID: {item.id}")
            item_data = item.to_dict()
            print(f"    Name: {item_data.get('name', 'N/A')}")
            print(f"    Type: {item_data.get('type', 'N/A')}")
            print(f"    User ID: {item_data.get('userId', 'N/A')}")
        
        # Check for outfits collection
        outfits_ref = db.collection('outfits')
        outfits = list(outfits_ref.limit(5).stream())
        print(f"👗 Outfits found: {len(outfits)}")
        for outfit in outfits:
            print(f"  - Outfit ID: {outfit.id}")
            outfit_data = outfit.to_dict()
            print(f"    Name: {outfit_data.get('name', 'N/A')}")
            print(f"    User ID: {outfit_data.get('userId', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firebase connection: {e}")
        return False

def create_test_user():
    """Create a test user if none exist"""
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        users = list(users_ref.limit(1).stream())
        
        if not users:
            print("🔍 No users found, creating test user...")
            
            # Create test user
            test_user_data = {
                'email': 'test@example.com',
                'name': 'Test User',
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            # Add to users collection
            user_ref = users_ref.add(test_user_data)
            print(f"✅ Created test user with ID: {user_ref[1].id}")
            
            # Create test wardrobe item
            wardrobe_ref = db.collection('wardrobe')
            test_item_data = {
                'name': 'Test T-Shirt',
                'type': 'shirt',
                'color': 'white',
                'userId': user_ref[1].id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            item_ref = wardrobe_ref.add(test_item_data)
            print(f"✅ Created test wardrobe item with ID: {item_ref[1].id}")
            
            return user_ref[1].id
        else:
            print(f"✅ Found existing user: {users[0].id}")
            return users[0].id
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing Firebase connection...")
    
    if test_firebase_connection():
        print("\n✅ Firebase connection successful!")
        
        # Try to create test user
        test_user_id = create_test_user()
        if test_user_id:
            print(f"✅ Test user ID: {test_user_id}")
        else:
            print("❌ Failed to create test user")
    else:
        print("\n❌ Firebase connection failed!")
        sys.exit(1) 