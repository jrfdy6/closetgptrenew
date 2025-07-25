#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Get the absolute path to the backend directory
BACKEND_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BACKEND_DIR / 'service-account-key.json'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def test_firestore_data():
    """Test the Firestore data directly."""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Testing Firestore data for user ID: {user_id}")
    
    # Query wardrobe collection for the specific user
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    docs = list(wardrobe_ref.stream())
    
    print(f"Found {len(docs)} documents for user {user_id}")
    
    # Check all documents in collection
    all_docs = list(db.collection('wardrobe').stream())
    print(f"Total documents in wardrobe collection: {len(all_docs)}")
    
    # Check user IDs
    user_ids = set()
    for doc in all_docs:
        data = doc.to_dict()
        if 'userId' in data:
            user_ids.add(data['userId'])
    
    print(f"User IDs found: {user_ids}")
    
    # Show details of first few documents for the user
    print(f"\nDetails of documents for user {user_id}:")
    for i, doc in enumerate(docs[:5]):  # Show first 5
        data = doc.to_dict()
        print(f"\nDocument {i+1}: {doc.id}")
        print(f"  Type: {data.get('type', 'N/A')}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Color: {data.get('color', 'N/A')}")
        print(f"  UserId: {data.get('userId', 'N/A')}")
        print(f"  Keys: {list(data.keys())}")
        
        # Check required fields
        required_fields = ['id', 'name', 'type', 'color', 'season', 'imageUrl', 'tags', 'userId', 'dominantColors', 'matchingColors', 'occasion', 'createdAt', 'updatedAt']
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  Missing fields: {missing_fields}")
        else:
            print(f"  ✓ All required fields present")

if __name__ == "__main__":
    test_firestore_data() 