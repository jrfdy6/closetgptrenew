#!/usr/bin/env python3
"""
Simple Firestore connectivity test.
This script tests basic Firestore operations without complex dependencies.
"""

import firebase_admin
from firebase_admin import firestore
import json

def test_firestore_connectivity():
    """Test basic Firestore connectivity."""
    print("🔍 Testing Firestore connectivity...")
    
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            firebase_admin.initialize_app()
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Test basic collection access
        print("🔍 Testing outfits collection access...")
        outfits_ref = db.collection('outfits')
        print("✅ Outfits collection reference created")
        
        # Test getting a few documents
        print("🔍 Testing document retrieval...")
        docs = outfits_ref.limit(3).stream()
        docs_list = list(docs)
        print(f"✅ Retrieved {len(docs_list)} documents")
        
        # Show sample data
        for i, doc in enumerate(docs_list):
            data = doc.to_dict()
            print(f"📄 Document {i+1}: {doc.id}")
            print(f"   - Fields: {list(data.keys())}")
            print(f"   - user_id: {data.get('user_id', 'NOT_FOUND')}")
            print(f"   - userId: {data.get('userId', 'NOT_FOUND')}")
            print(f"   - Items count: {len(data.get('items', []))}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_wardrobe_collection():
    """Test wardrobe collection access."""
    print("\n🔍 Testing wardrobe collection...")
    
    try:
        db = firestore.client()
        wardrobe_ref = db.collection('wardrobe')
        
        # Test getting a few wardrobe items
        docs = wardrobe_ref.limit(3).stream()
        docs_list = list(docs)
        print(f"✅ Retrieved {len(docs_list)} wardrobe items")
        
        # Show sample data
        for i, doc in enumerate(docs_list):
            data = doc.to_dict()
            print(f"👕 Wardrobe Item {i+1}: {doc.id}")
            print(f"   - Fields: {list(data.keys())}")
            print(f"   - userId: {data.get('userId', 'NOT_FOUND')}")
            print(f"   - Type: {data.get('type', 'NOT_FOUND')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Firestore Connectivity Test")
    print("=" * 50)
    
    # Test outfits collection
    outfits_success = test_firestore_connectivity()
    
    # Test wardrobe collection
    wardrobe_success = test_wardrobe_collection()
    
    print("=" * 50)
    if outfits_success and wardrobe_success:
        print("✅ All tests passed! Firestore is working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\n📝 Next steps:")
    print("1. If tests pass, the issue is in the backend route logic")
    print("2. If tests fail, there's a Firestore connectivity issue")
    print("3. Check Firebase credentials and project configuration") 