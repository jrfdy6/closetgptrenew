#!/usr/bin/env python3
"""
Test script to debug wardrobe parsing issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/src'))

import firebase_admin
from firebase_admin import credentials, firestore
from types.wardrobe import ClothingItem, ClothingType, Color
from pydantic import ValidationError

def test_wardrobe_parsing():
    """Test parsing wardrobe items from Firestore"""
    
    # Initialize Firebase Admin
    cred = credentials.Certificate("backend/service-account-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    # Get wardrobe items
    wardrobe_ref = db.collection('wardrobe')
    docs = wardrobe_ref.stream()
    
    successful_parses = 0
    failed_parses = 0
    
    for doc in docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        
        print(f"\n--- Testing item {doc.id} ---")
        print(f"Item name: {item_data.get('name', 'N/A')}")
        print(f"Item type: {item_data.get('type', 'N/A')}")
        print(f"Item color: {item_data.get('color', 'N/A')}")
        
        try:
            # Try to parse as ClothingItem
            clothing_item = ClothingItem(**item_data)
            print(f"✅ Successfully parsed item {doc.id}")
            successful_parses += 1
            
        except ValidationError as e:
            print(f"❌ Failed to parse item {doc.id}:")
            print(f"   Validation errors: {e.errors()}")
            failed_parses += 1
            
        except Exception as e:
            print(f"❌ Unexpected error parsing item {doc.id}: {e}")
            failed_parses += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Successful parses: {successful_parses}")
    print(f"Failed parses: {failed_parses}")
    print(f"Total items: {successful_parses + failed_parses}")

if __name__ == "__main__":
    test_wardrobe_parsing() 