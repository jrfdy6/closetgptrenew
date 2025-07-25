#!/usr/bin/env python3
"""
Script to find any items with test-shirt.jpg in any collection
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

def find_test_shirt():
    """Find any items with test-shirt.jpg in any collection"""
    
    print("🔍 Searching for items with test-shirt.jpg in all collections...")
    
    # Get all collections
    collections = db.collections()
    
    test_shirt_items = []
    
    for collection in collections:
        collection_name = collection.id
        print(f"📁 Checking collection: {collection_name}")
        
        try:
            docs = collection.stream()
            for doc in docs:
                data = doc.to_dict()
                
                # Check if the item has an imageUrl that contains test-shirt.jpg
                image_url = data.get('imageUrl', '')
                if 'test-shirt.jpg' in image_url:
                    test_shirt_items.append({
                        'collection': collection_name,
                        'id': doc.id,
                        'name': data.get('name', 'Unknown'),
                        'imageUrl': image_url,
                        'userId': data.get('userId', 'Unknown'),
                        'type': data.get('type', 'Unknown')
                    })
        except Exception as e:
            print(f"❌ Error reading collection {collection_name}: {e}")
    
    print(f"\n📊 Found {len(test_shirt_items)} items with test-shirt.jpg")
    
    if not test_shirt_items:
        print("✅ No items with test-shirt.jpg found!")
        return
    
    # Display the items
    print("\n📋 Items with test-shirt.jpg:")
    for i, item in enumerate(test_shirt_items, 1):
        print(f"{i}. {item['name']} (ID: {item['id']})")
        print(f"   Collection: {item['collection']}")
        print(f"   Type: {item['type']}")
        print(f"   ImageUrl: {item['imageUrl']}")
        print(f"   User: {item['userId']}")
        print()
    
    # Ask if user wants to fix these items
    response = input(f"❓ Do you want to fix these {len(test_shirt_items)} items by setting placeholder images? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Fix cancelled.")
        return
    
    # Fix the items by setting placeholder images
    print("\n🔧 Fixing items...")
    fixed_count = 0
    
    for item in test_shirt_items:
        try:
            collection_ref = db.collection(item['collection'])
            doc_ref = collection_ref.document(item['id'])
            
            # Set a placeholder image based on item type
            placeholder_url = f"https://via.placeholder.com/400x600/CCCCCC/666666?text={item['type'].title()}"
            
            doc_ref.update({
                'imageUrl': placeholder_url
            })
            
            fixed_count += 1
            print(f"✅ Fixed: {item['name']} (ID: {item['id']}) in {item['collection']} - Set placeholder image")
        except Exception as e:
            print(f"❌ Error fixing {item['name']} (ID: {item['id']}) in {item['collection']}: {e}")
    
    print(f"\n🎉 Successfully fixed {fixed_count} out of {len(test_shirt_items)} items!")

def main():
    """Main function"""
    print("🔍 Test Shirt Finder")
    print("=" * 40)
    
    try:
        find_test_shirt()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 