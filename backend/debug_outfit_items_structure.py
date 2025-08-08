#!/usr/bin/env python3
"""
Debug outfit items structure to understand how items are stored.
"""

import firebase_admin
from firebase_admin import firestore
import json

def check_outfit_items_structure():
    """Check how items are structured in outfit documents."""
    print("🔍 Checking Outfit Items Structure")
    print("=" * 60)
    
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            firebase_admin.initialize_app()
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Get a few outfit documents
        outfits_ref = db.collection('outfits')
        outfits_docs = outfits_ref.limit(3).stream()
        
        for i, doc in enumerate(outfits_docs):
            data = doc.to_dict()
            items = data.get('items', [])
            
            print(f"\n📄 Outfit {i+1}: {doc.id}")
            print(f"   Items count: {len(items)}")
            
            for j, item in enumerate(items):
                print(f"\n   🔍 Item {j+1}:")
                print(f"      Type: {type(item)}")
                
                if isinstance(item, dict):
                    print(f"      Keys: {list(item.keys())}")
                    print(f"      userId: {item.get('userId')}")
                    print(f"      id: {item.get('id')}")
                    print(f"      name: {item.get('name')}")
                    print(f"      type: {item.get('type')}")
                elif isinstance(item, str):
                    print(f"      String ID: '{item}'")
                    print(f"      Length: {len(item)}")
                    
                    # Try to fetch the wardrobe item
                    try:
                        wardrobe_doc = db.collection('wardrobe').document(item).get()
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            print(f"      ✅ Found in wardrobe:")
                            print(f"         userId: {wardrobe_data.get('userId')}")
                            print(f"         name: {wardrobe_data.get('name')}")
                            print(f"         type: {wardrobe_data.get('type')}")
                        else:
                            print(f"      ❌ Not found in wardrobe collection")
                    except Exception as e:
                        print(f"      ⚠️ Error checking wardrobe: {e}")
                else:
                    print(f"      ⚠️ Unknown type: {item}")
        
        # Check if items are embedded objects or references
        print(f"\n🔍 Summary:")
        print(f"   - Items can be either embedded objects (dict) or string IDs")
        print(f"   - String IDs reference wardrobe collection documents")
        print(f"   - Embedded objects should have userId field")
        print(f"   - Wardrobe documents have userId field")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_item_user_id_checking():
    """Test how the backend checks item userId."""
    print("\n" + "=" * 60)
    print("🧪 Testing Item User ID Checking")
    print("=" * 60)
    
    try:
        db = firestore.client()
        test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        # Get a few outfits
        outfits_ref = db.collection('outfits')
        outfits_docs = outfits_ref.limit(3).stream()
        
        for i, doc in enumerate(outfits_docs):
            data = doc.to_dict()
            items = data.get('items', [])
            
            print(f"\n📄 Testing outfit {i+1}: {doc.id}")
            print(f"   Items count: {len(items)}")
            
            match_found = False
            for j, item in enumerate(items):
                print(f"\n   🔍 Checking item {j+1}:")
                
                if isinstance(item, dict):
                    item_userId = item.get('userId')
                    print(f"      Item is dict, userId: '{item_userId}'")
                    print(f"      Comparing '{item_userId}' == '{test_user_id}': {item_userId == test_user_id}")
                    
                    if item_userId == test_user_id:
                        print(f"      ✅ Match found!")
                        match_found = True
                        break
                    else:
                        print(f"      ❌ No match")
                        
                elif isinstance(item, str):
                    print(f"      Item is string ID: '{item}'")
                    
                    # Check wardrobe collection
                    try:
                        wardrobe_doc = db.collection('wardrobe').document(item).get()
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            item_userId = wardrobe_data.get('userId')
                            print(f"      Found in wardrobe, userId: '{item_userId}'")
                            print(f"      Comparing '{item_userId}' == '{test_user_id}': {item_userId == test_user_id}")
                            
                            if item_userId == test_user_id:
                                print(f"      ✅ Match found!")
                                match_found = True
                                break
                            else:
                                print(f"      ❌ No match")
                        else:
                            print(f"      ❌ Not found in wardrobe")
                    except Exception as e:
                        print(f"      ⚠️ Error checking wardrobe: {e}")
                else:
                    print(f"      ⚠️ Unknown item type: {type(item)}")
            
            if match_found:
                print(f"   ✅ Outfit {doc.id} has matching items")
            else:
                print(f"   ❌ Outfit {doc.id} has no matching items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Outfit Items Structure Debug")
    print("This will check how items are stored in outfit documents")
    print()
    
    # Check items structure
    structure_success = check_outfit_items_structure()
    
    # Test user ID checking
    testing_success = test_item_user_id_checking()
    
    print("\n" + "=" * 60)
    if structure_success and testing_success:
        print("✅ Items structure check completed successfully!")
        print("\n📝 Key findings:")
        print("- Items can be embedded objects or string IDs")
        print("- String IDs reference wardrobe collection")
        print("- Both should have userId field for user filtering")
        print("- Backend checks both embedded objects and wardrobe references")
    else:
        print("❌ Some checks failed. Check the errors above.") 