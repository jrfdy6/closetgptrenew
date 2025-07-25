#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
from src.types.wardrobe import ClothingItem
from pydantic import ValidationError

# Get the absolute path to the backend directory
BACKEND_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BACKEND_DIR / 'service-account-key.json'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def test_clothing_item_validation():
    """Test ClothingItem validation with real data from Firestore."""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Testing ClothingItem validation for user ID: {user_id}")
    
    # Query wardrobe collection for the specific user
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    docs = list(wardrobe_ref.stream())
    
    print(f"Found {len(docs)} documents for user {user_id}")
    
    successful_parses = 0
    failed_parses = 0
    
    for i, doc in enumerate(docs):
        data = doc.to_dict()
        
        try:
            clothing_item = ClothingItem(**data)
            successful_parses += 1
            if i < 5:  # Show first 5 successful parses
                print(f"✓ Document {i+1}: {doc.id} - {data.get('type', 'N/A')} - {data.get('name', 'N/A')}")
        except ValidationError as e:
            failed_parses += 1
            if i < 5:  # Show first 5 failed parses
                print(f"✗ Document {i+1}: {doc.id} - {data.get('type', 'N/A')} - {data.get('name', 'N/A')}")
                print(f"  Validation error: {e}")
        except Exception as e:
            failed_parses += 1
            if i < 5:  # Show first 5 failed parses
                print(f"✗ Document {i+1}: {doc.id} - {data.get('type', 'N/A')} - {data.get('name', 'N/A')}")
                print(f"  Error: {e}")
    
    print(f"\nSummary:")
    print(f"  Total documents: {len(docs)}")
    print(f"  Successful parses: {successful_parses}")
    print(f"  Failed parses: {failed_parses}")

if __name__ == "__main__":
    test_clothing_item_validation() 