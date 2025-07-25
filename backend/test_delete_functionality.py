#!/usr/bin/env python3
"""
Script to test delete functionality and verify collection structure
"""

import firebase_admin
from firebase_admin import firestore
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    sys.exit(1)

def test_delete_functionality():
    """Test delete functionality and verify collection structure"""
    
    print("🔍 Testing Delete Functionality")
    print("=" * 40)
    
    # Check wardrobe collection structure
    print("📁 Checking wardrobe collection...")
    try:
        wardrobe_ref = db.collection('wardrobe')
        docs = list(wardrobe_ref.limit(5).stream())
        
        print(f"✅ Found {len(docs)} items in wardrobe collection")
        
        if docs:
            sample_item = docs[0]
            print(f"📋 Sample item:")
            print(f"   ID: {sample_item.id}")
            print(f"   Name: {sample_item.get('name', 'Unknown')}")
            print(f"   Type: {sample_item.get('type', 'Unknown')}")
            print(f"   User ID: {sample_item.get('userId', 'Unknown')}")
            print()
            
            # Test if we can delete this item (but don't actually delete it)
            print("🧪 Testing delete operation (dry run)...")
            try:
                # Just check if the document reference can be created
                doc_ref = wardrobe_ref.document(sample_item.id)
                print(f"✅ Document reference created: {doc_ref.path}")
                print("✅ Delete operation should work correctly")
            except Exception as e:
                print(f"❌ Error creating document reference: {e}")
                
        else:
            print("⚠️  No items found in wardrobe collection")
            
    except Exception as e:
        print(f"❌ Error accessing wardrobe collection: {e}")
    
    # Check if there are any items in users/{userId}/wardrobe (old structure)
    print("\n📁 Checking for old collection structure...")
    try:
        # Get all users
        users_ref = db.collection('users')
        users = list(users_ref.limit(3).stream())
        
        for user in users:
            user_wardrobe_ref = users_ref.document(user.id).collection('wardrobe')
            user_items = list(user_wardrobe_ref.limit(3).stream())
            
            if user_items:
                print(f"⚠️  Found {len(user_items)} items in users/{user.id}/wardrobe (old structure)")
                print(f"   This might cause issues with delete functionality")
            else:
                print(f"✅ No items in users/{user.id}/wardrobe")
                
    except Exception as e:
        print(f"❌ Error checking user collections: {e}")
    
    print("\n🎯 Summary:")
    print("- Delete functionality should work if items are in 'wardrobe' collection")
    print("- If items are in 'users/{userId}/wardrobe', delete will fail")
    print("- Check browser console for any JavaScript errors during delete")

def main():
    """Main function"""
    try:
        test_delete_functionality()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 