#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def test_firestore_query():
    """Test the Firestore query directly."""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Testing Firestore query for user ID: {user_id}")
    
    # Query wardrobe collection
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    docs = wardrobe_ref.stream()
    
    doc_count = 0
    valid_items = 0
    invalid_items = 0
    
    for doc in docs:
        doc_count += 1
        item_data = doc.to_dict()
        
        print(f"\nDocument {doc_count}: {doc.id}")
        print(f"  Keys: {list(item_data.keys())}")
        print(f"  Type: {item_data.get('type', 'N/A')}")
        print(f"  UserId: {item_data.get('userId', 'N/A')}")
        print(f"  Name: {item_data.get('name', 'N/A')}")
        print(f"  Color: {item_data.get('color', 'N/A')}")
        
        # Check if required fields are present
        required_fields = ['id', 'name', 'type', 'color', 'season', 'imageUrl', 'tags', 'userId', 'dominantColors', 'matchingColors', 'occasion', 'createdAt', 'updatedAt']
        missing_fields = []
        
        for field in required_fields:
            if field not in item_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  Missing fields: {missing_fields}")
            invalid_items += 1
        else:
            print(f"  ✓ All required fields present")
            valid_items += 1
    
    print(f"\nSummary:")
    print(f"  Total documents: {doc_count}")
    print(f"  Valid items: {valid_items}")
    print(f"  Invalid items: {invalid_items}")
    
    # Also check total items in collection
    all_docs = db.collection('wardrobe').stream()
    total_in_collection = 0
    for doc in all_docs:
        total_in_collection += 1
    
    print(f"  Total items in wardrobe collection: {total_in_collection}")

if __name__ == "__main__":
    test_firestore_query() 