#!/usr/bin/env python3
"""
Quick check of Firebase wardrobe metadata
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.config.firebase import db, firebase_initialized

def check_metadata():
    """Check actual metadata in Firebase wardrobe items"""
    
    if not firebase_initialized or db is None:
        print("❌ Firebase not initialized")
        return
    
    print("✅ Firebase initialized")
    
    # Get your user ID
    test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Checking wardrobe metadata for user: {test_user_id}")
    
    try:
        # Get a few wardrobe items
        docs = db.collection('wardrobe').where('userId', '==', test_user_id).limit(5).stream()
        
        items_checked = 0
        for doc in docs:
            item_data = doc.to_dict()
            items_checked += 1
            
            print(f"\n{'='*60}")
            print(f"Item {items_checked}: {item_data.get('name', 'Unknown')}")
            print(f"{'='*60}")
            print(f"Type: {item_data.get('type', 'N/A')}")
            print(f"Color: {item_data.get('color', 'N/A')}")
            
            # Check metadata fields
            occasion = item_data.get('occasion', [])
            style = item_data.get('style', [])
            mood = item_data.get('mood', [])
            
            print(f"\n📊 METADATA:")
            print(f"  Occasion: {occasion if occasion else '❌ EMPTY'}")
            print(f"  Style: {style if style else '❌ EMPTY'}")
            print(f"  Mood: {mood if mood else '❌ EMPTY'}")
            
            # Check if metadata object exists
            if 'metadata' in item_data:
                metadata = item_data['metadata']
                print(f"\n  Metadata object exists:")
                print(f"    - styleTags: {metadata.get('styleTags', '❌ MISSING')}")
                print(f"    - occasionTags: {metadata.get('occasionTags', '❌ MISSING')}")
            else:
                print(f"\n  ❌ No 'metadata' object found")
            
            if items_checked >= 5:
                break
        
        if items_checked == 0:
            print("❌ No items found for this user")
        else:
            print(f"\n{'='*60}")
            print(f"✅ Checked {items_checked} items")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_metadata()

