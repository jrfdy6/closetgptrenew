#!/usr/bin/env python3
"""
Quick Firestore Wardrobe Data Checker
=====================================

This script will dump all wardrobe items with their user IDs
to help debug why only 1 item is showing instead of 114.
"""

import os
import sys
from pathlib import Path

# Add the backend src directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend" / "src"))

try:
    from src.config.firebase import db, firebase_initialized
    print("✅ Firebase config imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Firebase config: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def check_wardrobe_data():
    """Check all wardrobe items and their user IDs."""
    
    if not firebase_initialized or db is None:
        print("❌ Firebase not initialized. Cannot check data.")
        return False
    
    print("🔍 Checking wardrobe data...")
    
    try:
        # Get all wardrobe items
        docs = db.collection('wardrobe').stream()
        
        # Convert to list to count
        all_docs = list(docs)
        total_count = len(all_docs)
        
        print(f"📊 Total items in wardrobe collection: {total_count}")
        
        if total_count == 0:
            print("❌ No items found in wardrobe collection!")
            return False
        
        # Analyze user IDs
        user_counts = {}
        field_usage = {}
        
        for doc in all_docs:
            data = doc.to_dict()
            
            # Check all possible user ID fields
            user_id = None
            used_field = None
            
            for field_name in ['userId', 'uid', 'ownerId', 'user_id']:
                if field_name in data and data[field_name]:
                    user_id = data[field_name]
                    used_field = field_name
                    break
            
            if user_id:
                user_counts[user_id] = user_counts.get(user_id, 0) + 1
                field_usage[used_field] = field_usage.get(used_field, 0) + 1
            else:
                user_counts['NO_USER_ID'] = user_counts.get('NO_USER_ID', 0) + 1
        
        print(f"\n👥 User ID distribution:")
        for user_id, count in user_counts.items():
            print(f"  {user_id}: {count} items")
        
        print(f"\n🏷️  Field name usage:")
        for field_name, count in field_usage.items():
            print(f"  {field_name}: {count} items")
        
        # Show sample items
        print(f"\n📋 Sample items (first 5):")
        for i, doc in enumerate(all_docs[:5]):
            data = doc.to_dict()
            user_id = (data.get('userId') or 
                      data.get('uid') or 
                      data.get('ownerId') or 
                      data.get('user_id') or 
                      'NO_USER_ID')
            
            print(f"  {i+1}. ID: {doc.id}")
            print(f"     Name: {data.get('name', 'NO_NAME')}")
            print(f"     User: {user_id}")
            print(f"     Fields: {list(data.keys())}")
            print()
        
        # Check for your specific user ID
        your_user_id = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'
        your_items = user_counts.get(your_user_id, 0)
        
        print(f"🎯 Your user ID ({your_user_id}): {your_items} items")
        
        if your_items == 0:
            print("❌ No items found for your user ID!")
            print("💡 This explains why you only see 1 item - your items belong to a different user ID")
        elif your_items == 1:
            print("⚠️  Only 1 item found for your user ID")
            print("💡 This explains why you only see 1 item")
        else:
            print(f"✅ Found {your_items} items for your user ID")
            print("💡 The API should be returning all these items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking wardrobe data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Wardrobe Data Checker")
    print("=" * 50)
    
    success = check_wardrobe_data()
    
    if success:
        print("\n🎉 Data check completed successfully!")
    else:
        print("\n❌ Data check failed!")
    
    sys.exit(0 if success else 1)
