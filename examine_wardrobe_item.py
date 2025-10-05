#!/usr/bin/env python3
"""
Examine a single wardrobe item to see all available fields
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def examine_wardrobe_item():
    """Connect to Firebase and examine a single wardrobe item"""
    
    print("🔍 EXAMINING WARDROBE ITEM STRUCTURE")
    print("=" * 60)
    
    try:
        # Import Firebase configuration
        from src.config.firebase import db, firebase_initialized
        
        if not firebase_initialized or db is None:
            print("❌ Firebase not initialized")
            return
        
        print("✅ Firebase connected successfully")
        
        # Query wardrobe collection for one item
        print("\n📦 Getting one wardrobe item...")
        
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.limit(1).stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        if not items:
            print("❌ No wardrobe items found")
            return
        
        item = items[0]
        
        print(f"✅ Found wardrobe item: {item.get('id', 'NO_ID')}")
        print("\n📋 ALL FIELDS IN WARDROBE ITEM:")
        print("=" * 60)
        
        # Show all fields with their values
        for key, value in sorted(item.items()):
            if isinstance(value, dict):
                print(f"📁 {key}: (object)")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        print(f"   📁 {sub_key}: (nested object)")
                        for nested_key, nested_value in sub_value.items():
                            print(f"      🔹 {nested_key}: {nested_value}")
                    else:
                        print(f"   🔹 {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"📋 {key}: {value} (list with {len(value)} items)")
            else:
                print(f"🔹 {key}: {value}")
        
        print(f"\n📊 FIELD SUMMARY:")
        print("=" * 60)
        print(f"Total fields: {len(item)}")
        
        # Count field types
        field_types = {}
        for key, value in item.items():
            value_type = type(value).__name__
            if value_type not in field_types:
                field_types[value_type] = []
            field_types[value_type].append(key)
        
        for field_type, fields in field_types.items():
            print(f"{field_type}: {fields}")
        
        # Check for specific fields we care about
        print(f"\n🎯 KEY FIELDS FOR OUTFIT GENERATION:")
        print("=" * 60)
        
        key_fields = ['name', 'type', 'color', 'style', 'occasion', 'season', 'brand', 'material']
        for field in key_fields:
            value = item.get(field, 'NOT_FOUND')
            print(f"{field}: {value}")
        
        # Check metadata structure
        metadata = item.get('metadata', {})
        print(f"\n📁 METADATA STRUCTURE:")
        print("=" * 60)
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, dict):
                    print(f"📁 {key}: (object with {len(value)} fields)")
                    for sub_key, sub_value in value.items():
                        print(f"   🔹 {sub_key}: {sub_value}")
                else:
                    print(f"🔹 {key}: {value}")
        else:
            print("No metadata found")
        
        print(f"\n✅ EXAMINATION COMPLETE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_wardrobe_item()

