#!/usr/bin/env python3
"""
Test Firebase connection using environment variables
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

def test_firebase_env():
    """Test Firebase connection using environment variables"""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            print("✅ Firebase already initialized")
            return True
            
        print("🔍 Testing Firebase with environment variables...")
        
        # Check for required environment variables
        required_vars = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY", 
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID",
            "FIREBASE_CLIENT_X509_CERT_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print(f"❌ Missing Firebase environment variables: {missing_vars}")
            return False
        
        print("✅ All required environment variables found")
        
        # Create credentials from environment variables
        firebase_creds = {
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", ""),
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ["FIREBASE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
        }
        
        print("🔍 Initializing Firebase with environment credentials...")
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
        
        # Test Firestore connection
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Test a simple query
        collections = list(db.collections())
        print(f"📁 Collections found: {[col.id for col in collections]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firebase with environment variables: {e}")
        return False

def create_test_data():
    """Create test data if Firebase is working"""
    try:
        db = firestore.client()
        
        # Create test user
        users_ref = db.collection('users')
        test_user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        user_ref = users_ref.add(test_user_data)
        user_id = user_ref[1].id
        print(f"✅ Created test user: {user_id}")
        
        # Create test wardrobe item
        wardrobe_ref = db.collection('wardrobe')
        test_item_data = {
            'name': 'Test T-Shirt',
            'type': 'shirt',
            'color': 'white',
            'userId': user_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        item_ref = wardrobe_ref.add(test_item_data)
        print(f"✅ Created test wardrobe item: {item_ref[1].id}")
        
        # Create test outfit
        outfits_ref = db.collection('outfits')
        test_outfit_data = {
            'name': 'Test Outfit',
            'userId': user_id,
            'items': [item_ref[1].id],
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        outfit_ref = outfits_ref.add(test_outfit_data)
        print(f"✅ Created test outfit: {outfit_ref[1].id}")
        
        return user_id
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing Firebase with environment variables...")
    
    if test_firebase_env():
        print("\n✅ Firebase connection successful!")
        
        # Try to create test data
        test_user_id = create_test_data()
        if test_user_id:
            print(f"✅ Test user ID: {test_user_id}")
            print("🎉 Firebase is working! You can now test the API endpoints.")
        else:
            print("❌ Failed to create test data")
    else:
        print("\n❌ Firebase connection failed!")
        print("💡 Make sure to set the Firebase environment variables in Railway")
        sys.exit(1) 