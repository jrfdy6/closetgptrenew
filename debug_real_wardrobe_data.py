#!/usr/bin/env python3
"""
Debug script to connect to Firebase and see what data is actually in the wardrobe
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_wardrobe_data():
    """Connect to Firebase and examine real wardrobe data"""
    
    print("🔍 DEBUGGING REAL WARDROBE DATA")
    print("=" * 50)
    
    try:
        # Import Firebase configuration
        from src.config.firebase import db, firebase_initialized
        
        if not firebase_initialized or db is None:
            print("❌ Firebase not initialized")
            return
        
        print("✅ Firebase connected successfully")
        
        # Query wardrobe collection
        print("\n📦 Querying wardrobe collection...")
        
        # Get all wardrobe items (limit to first 10 for debugging)
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.limit(10).stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        print(f"✅ Found {len(items)} wardrobe items")
        
        if not items:
            print("❌ No wardrobe items found")
            return
        
        # Analyze the first few items
        print("\n🔍 ANALYZING FIRST 3 ITEMS:")
        print("=" * 50)
        
        for i, item in enumerate(items[:3]):
            print(f"\n📋 ITEM {i+1}: {item.get('id', 'NO_ID')}")
            print(f"   Name: {item.get('name', 'NO_NAME')}")
            print(f"   Type: {item.get('type', 'NO_TYPE')}")
            print(f"   Color: {item.get('color', 'NO_COLOR')}")
            print(f"   Style: {item.get('style', 'NO_STYLE')}")
            print(f"   Occasion: {item.get('occasion', 'NO_OCCASION')}")
            print(f"   Season: {item.get('season', 'NO_SEASON')}")
            print(f"   Brand: {item.get('brand', 'NO_BRAND')}")
            print(f"   Material: {item.get('material', 'NO_MATERIAL')}")
            
            # Check metadata
            metadata = item.get('metadata', {})
            print(f"   Metadata: {json.dumps(metadata, indent=2) if metadata else 'NO_METADATA'}")
            
            print("-" * 30)
        
        # Analyze all items for patterns
        print(f"\n📊 ANALYSIS OF ALL {len(items)} ITEMS:")
        print("=" * 50)
        
        # Count by type
        type_counts = {}
        occasion_counts = {}
        style_counts = {}
        
        for item in items:
            # Count types
            item_type = item.get('type', 'unknown')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            # Count occasions
            occasions = item.get('occasion', [])
            if isinstance(occasions, list):
                for occasion in occasions:
                    occasion_counts[occasion] = occasion_counts.get(occasion, 0) + 1
            elif occasions:
                occasion_counts[occasions] = occasion_counts.get(occasions, 0) + 1
            
            # Count styles
            styles = item.get('style', [])
            if isinstance(styles, list):
                for style in styles:
                    style_counts[style] = style_counts.get(style, 0) + 1
            elif styles:
                style_counts[styles] = style_counts.get(styles, 0) + 1
        
        print(f"📈 ITEM TYPES:")
        for item_type, count in sorted(type_counts.items()):
            print(f"   {item_type}: {count}")
        
        print(f"\n📈 OCCASIONS:")
        for occasion, count in sorted(occasion_counts.items()):
            print(f"   {occasion}: {count}")
        
        print(f"\n📈 STYLES:")
        for style, count in sorted(style_counts.items()):
            print(f"   {style}: {count}")
        
        # Check for missing data
        print(f"\n🚨 MISSING DATA ANALYSIS:")
        print("=" * 50)
        
        missing_fields = {
            'name': 0,
            'type': 0,
            'color': 0,
            'style': 0,
            'occasion': 0,
            'season': 0,
            'brand': 0,
            'material': 0
        }
        
        for item in items:
            for field in missing_fields:
                if not item.get(field):
                    missing_fields[field] += 1
        
        for field, missing_count in missing_fields.items():
            percentage = (missing_count / len(items)) * 100
            print(f"   {field}: {missing_count}/{len(items)} missing ({percentage:.1f}%)")
        
        print(f"\n✅ ANALYSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_wardrobe_data()
