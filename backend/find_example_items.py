#!/usr/bin/env python3
"""
Script to find items with example.com URLs in the wardrobe collection
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

def find_example_items():
    """Find items with example.com URLs in the wardrobe collection"""
    
    print("🔍 Searching for items with example.com URLs in wardrobe collection...")
    
    # Query all wardrobe items
    wardrobe_ref = db.collection('wardrobe')
    docs = wardrobe_ref.stream()
    
    example_items = []
    total_items = 0
    
    for doc in docs:
        total_items += 1
        data = doc.to_dict()
        
        # Check if the item has an imageUrl that contains example.com
        image_url = data.get('imageUrl', '')
        if 'example.com' in image_url:
            example_items.append({
                'id': doc.id,
                'name': data.get('name', 'Unknown'),
                'imageUrl': image_url,
                'userId': data.get('userId', 'Unknown'),
                'type': data.get('type', 'Unknown')
            })
    
    print(f"📊 Found {len(example_items)} items with example.com URLs out of {total_items} total items")
    
    if not example_items:
        print("✅ No items with example.com URLs found!")
        return
    
    # Display the items
    print("\n📋 Items with example.com URLs:")
    for i, item in enumerate(example_items, 1):
        print(f"{i}. {item['name']} (ID: {item['id']})")
        print(f"   Type: {item['type']}")
        print(f"   ImageUrl: {item['imageUrl']}")
        print(f"   User: {item['userId']}")
        print()
    
    # Ask if user wants to fix these items
    response = input(f"❓ Do you want to fix these {len(example_items)} items by setting placeholder images? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Fix cancelled.")
        return
    
    # Fix the items by setting placeholder images
    print("\n🔧 Fixing items...")
    fixed_count = 0
    
    for item in example_items:
        try:
            doc_ref = wardrobe_ref.document(item['id'])
            
            # Set a placeholder image based on item type
            placeholder_url = f"https://via.placeholder.com/400x600/CCCCCC/666666?text={item['type'].title()}"
            
            doc_ref.update({
                'imageUrl': placeholder_url
            })
            
            fixed_count += 1
            print(f"✅ Fixed: {item['name']} (ID: {item['id']}) - Set placeholder image")
        except Exception as e:
            print(f"❌ Error fixing {item['name']} (ID: {item['id']}): {e}")
    
    print(f"\n🎉 Successfully fixed {fixed_count} out of {len(example_items)} items!")

def main():
    """Main function"""
    print("🔍 Example.com URL Finder")
    print("=" * 40)
    
    try:
        find_example_items()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 