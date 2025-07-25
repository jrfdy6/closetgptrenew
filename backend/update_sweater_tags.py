#!/usr/bin/env python3
"""
Script to update the Abercrombie & Fitch sweater item tags.
This item is incorrectly tagged as 'long' but should be 'short' sleeve.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Initialize Firebase
if not firebase_admin._apps:
    # Load service account key
    service_account_path = "service-account-key.json"
    if os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    else:
        print("❌ service-account-key.json not found. Please ensure it's in the backend directory.")
        exit(1)

db = firestore.client()

def update_sweater_tags():
    """Update the Abercrombie & Fitch sweater item tags."""
    
    # Find the specific item by name
    wardrobe_ref = db.collection('wardrobe')
    query = wardrobe_ref.where('name', '==', 'A loose, long, textured, ribbed sweater by Abercrombie & Fitch')
    
    docs = query.stream()
    items = list(docs)
    
    if not items:
        print("❌ Item not found: 'A loose, long, textured, ribbed sweater by Abercrombie & Fitch'")
        print("🔍 Searching for similar items...")
        
        # Try a broader search
        query = wardrobe_ref.where('name', '>=', 'Abercrombie').where('name', '<=', 'Abercrombie\uf8ff')
        docs = query.stream()
        items = list(docs)
        
        if not items:
            print("❌ No Abercrombie & Fitch items found")
            return
        
        print(f"📋 Found {len(items)} Abercrombie & Fitch items:")
        for item in items:
            print(f"  - {item.get('name')}")
        return
    
    item = items[0]
    item_id = item.id
    item_data = item.to_dict()
    
    print(f"✅ Found item: {item_data.get('name')}")
    print(f"📋 Current tags: {item_data.get('tags', [])}")
    print(f"📋 Current style: {item_data.get('style', [])}")
    print(f"📋 Current metadata: {item_data.get('metadata', {})}")
    
    # Update the item with correct tags
    updates = {
        'name': 'A loose, short, textured, ribbed sweater by Abercrombie & Fitch',  # Change 'long' to 'short'
        'tags': ['short sleeve', 'ribbed', 'textured', 'sweater', 'casual'],  # Add short sleeve tag
        'style': ['Casual', 'Short Sleeve', 'Ribbed', 'Textured'],  # Update style tags
        'metadata.visualAttributes.sleeveLength': 'Short',  # Set sleeve length
        'metadata.visualAttributes.wearLayer': 'Outer',  # This is an outer layer, not meant to be layered under
        'metadata.visualAttributes.fit': 'loose',
        'metadata.visualAttributes.textureStyle': 'ribbed',
        'metadata.visualAttributes.pattern': 'textured',
        'metadata.naturalDescription': 'A loose, short-sleeve, ribbed sweater from Abercrombie & Fitch. This is an outer layer item that should not be worn under long-sleeve shirts.',
        'updatedAt': firestore.SERVER_TIMESTAMP
    }
    
    try:
        wardrobe_ref.document(item_id).update(updates)
        print("✅ Successfully updated item tags!")
        print("📋 New name: A loose, short, textured, ribbed sweater by Abercrombie & Fitch")
        print("📋 New tags: ['short sleeve', 'ribbed', 'textured', 'sweater', 'casual']")
        print("📋 New style: ['Casual', 'Short Sleeve', 'Ribbed', 'Textured']")
        print("📋 Sleeve length: Short")
        print("📋 Wear layer: Outer (not meant for layering under long sleeves)")
        
    except Exception as e:
        print(f"❌ Error updating item: {e}")

if __name__ == "__main__":
    print("🔧 Updating Abercrombie & Fitch sweater tags...")
    update_sweater_tags()
    print("✅ Script completed!") 