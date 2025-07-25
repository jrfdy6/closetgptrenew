#!/usr/bin/env python3
"""
Script to find and fix items with test-shirt.jpg URLs in the database
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

def fix_test_shirt_urls():
    """Find and fix items with test-shirt.jpg URLs"""
    
    print("🔍 Searching for items with test-shirt.jpg URLs...")
    
    # Check all collections
    collections = ['wardrobe', 'clothingItems', 'outfits', 'trends']
    
    total_fixed = 0
    
    for collection_name in collections:
        print(f"📁 Checking collection: {collection_name}")
        
        try:
            collection_ref = db.collection(collection_name)
            docs = collection_ref.stream()
            
            for doc in docs:
                data = doc.to_dict()
                image_url = data.get('imageUrl', '')
                
                if 'test-shirt.jpg' in image_url or 'example.com' in image_url:
                    print(f"❌ Found item with problematic URL: {doc.id}")
                    print(f"   Name: {data.get('name', 'Unknown')}")
                    print(f"   Type: {data.get('type', 'Unknown')}")
                    print(f"   Current URL: {image_url}")
                    
                    # Create a better placeholder URL based on item type
                    item_type = data.get('type', 'clothing').lower()
                    if 'shirt' in item_type or 'shirt' in data.get('name', '').lower():
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Shirt"
                    elif 'pants' in item_type or 'pants' in data.get('name', '').lower():
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Pants"
                    elif 'shoes' in item_type or 'shoes' in data.get('name', '').lower():
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Shoes"
                    elif 'sweater' in item_type or 'sweater' in data.get('name', '').lower():
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Sweater"
                    elif 'accessory' in item_type or 'belt' in data.get('name', '').lower():
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Accessory"
                    else:
                        placeholder_url = "https://via.placeholder.com/400x600/CCCCCC/666666?text=Clothing"
                    
                    # Update the document
                    try:
                        doc_ref = collection_ref.document(doc.id)
                        doc_ref.update({
                            'imageUrl': placeholder_url
                        })
                        print(f"✅ Fixed: {data.get('name', 'Unknown')} - Set placeholder image")
                        total_fixed += 1
                    except Exception as e:
                        print(f"❌ Error fixing {data.get('name', 'Unknown')}: {e}")
                    
                    print()
                    
        except Exception as e:
            print(f"❌ Error reading collection {collection_name}: {e}")
    
    print(f"🎉 Successfully fixed {total_fixed} items!")
    
    if total_fixed == 0:
        print("✅ No items with test-shirt.jpg or example.com URLs found!")
        print("The issue might be in browser cache or frontend code.")

def main():
    """Main function"""
    print("🔧 Test Shirt URL Fixer")
    print("=" * 40)
    
    try:
        fix_test_shirt_urls()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 