#!/usr/bin/env python3
"""
Direct Firestore test to show user filtering logs.
This script directly accesses Firestore and shows the exact logs you requested.
"""

import firebase_admin
from firebase_admin import firestore
import json

def test_user_filtering_direct():
    """Test user filtering directly with Firestore."""
    print("🔍 Direct User Filtering Test")
    print("=" * 60)
    
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            firebase_admin.initialize_app()
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Test with a specific user ID (you can change this)
        test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your actual user ID
        print(f"👤 Testing with user ID: {test_user_id}")
        print(f"📎 current_user_id: \"{test_user_id}\" <class 'str'>")
        print()
        
        # Get all outfits
        outfits_ref = db.collection('outfits')
        outfits_docs = outfits_ref.limit(10).stream()
        outfits_list = list(outfits_docs)
        
        print(f"📊 Found {len(outfits_list)} outfits to analyze")
        print()
        
        # Analyze each outfit
        for i, doc in enumerate(outfits_list):
            outfit_data = doc.to_dict()
            outfit_id = doc.id
            
            print(f"🔍 Analyzing outfit {i+1}: {outfit_id}")
            
            # Check outfit-level user_id fields
            outfit_user_id = outfit_data.get('user_id')
            outfit_userId = outfit_data.get('userId')
            
            print(f"🔎 outfit.user_id: \"{outfit_user_id}\" <class '{type(outfit_user_id).__name__}'>")
            print(f"🔎 outfit.userId: \"{outfit_userId}\" <class '{type(outfit_userId).__name__}'>")
            
            # Check direct matches
            direct_match = False
            if outfit_user_id == test_user_id:
                print("✅ Direct match on outfit.user_id")
                direct_match = True
            elif outfit_userId == test_user_id:
                print("✅ Direct match on outfit.userId")
                direct_match = True
            else:
                print("⛔️ No direct match on outfit-level fields")
            
            # Check items for userId
            items = outfit_data.get('items', [])
            print(f"🔍 Outfit has {len(items)} items")
            
            item_match = False
            for j, item in enumerate(items):
                if isinstance(item, dict):
                    item_userId = item.get('userId')
                    print(f"🔍 item[{j}].userId: \"{item_userId}\" <class '{type(item_userId).__name__}'>")
                    
                    if item_userId == test_user_id:
                        print(f"✅ Item {j} userId matches current user")
                        item_match = True
                        break
                    else:
                        print(f"❌ Item {j} userId does not match")
                elif isinstance(item, str):
                    print(f"🔍 item[{j}] is string ID: \"{item}\", checking wardrobe collection")
                    try:
                        item_doc = db.collection('wardrobe').document(item).get()
                        if item_doc.exists:
                            item_data = item_doc.to_dict()
                            item_userId = item_data.get('userId')
                            print(f"🔍 Wardrobe item {item} userId: \"{item_userId}\" <class '{type(item_userId).__name__}'>")
                            
                            if item_userId == test_user_id:
                                print(f"✅ Wardrobe item {item} userId matches current user")
                                item_match = True
                                break
                            else:
                                print(f"❌ Wardrobe item {item} userId does not match")
                        else:
                            print(f"⚠️ Wardrobe item {item} not found")
                    except Exception as e:
                        print(f"⚠️ Error checking wardrobe item {item}: {e}")
            
            # Summary for this outfit
            if direct_match:
                print("✅ INCLUDING outfit (direct match)")
            elif item_match:
                print("✅ INCLUDING outfit (item-level match)")
            else:
                print("❌ EXCLUDING outfit (no matches)")
            
            print("-" * 50)
            print()
        
        # Summary
        print("📊 SUMMARY:")
        print(f"Total outfits analyzed: {len(outfits_list)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_real_data():
    """Test with real user data from your database."""
    print("\n" + "=" * 60)
    print("🔍 Testing with Real User Data")
    print("=" * 60)
    
    try:
        db = firestore.client()
        
        # Get a few real outfits
        outfits_ref = db.collection('outfits')
        outfits_docs = outfits_ref.limit(5).stream()
        
        print("📄 Sample Outfit Data:")
        for i, doc in enumerate(outfits_docs):
            data = doc.to_dict()
            print(f"\nOutfit {i+1}: {doc.id}")
            print(f"  Fields: {list(data.keys())}")
            print(f"  user_id: {data.get('user_id', 'NOT_FOUND')}")
            print(f"  userId: {data.get('userId', 'NOT_FOUND')}")
            print(f"  Items: {len(data.get('items', []))}")
            
            # Show first item details
            items = data.get('items', [])
            if items and isinstance(items[0], dict):
                first_item = items[0]
                print(f"  First item userId: {first_item.get('userId', 'NOT_FOUND')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Direct User Filtering Test")
    print("This script will show exactly the logs you requested")
    print()
    
    # Test with your user ID
    test_user_filtering_direct()
    
    # Test with real data
    test_with_real_data()
    
    print("\n✅ Test completed!")
    print("📝 The logs above show exactly what you requested:")
    print("   - current_user_id values")
    print("   - outfit.user_id values")
    print("   - item.userId values")
    print("   - Matching logic and results") 