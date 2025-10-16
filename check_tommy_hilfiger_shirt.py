#!/usr/bin/env python3
"""
Check Tommy Hilfiger shirt in Firestore
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.config.firebase import db
import json

# User ID from logs
user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

print(f"🔍 Searching for Tommy Hilfiger shirt in wardrobe for user {user_id}...")

# Get wardrobe items
wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
items = wardrobe_ref.stream()

tommy_items = []

for item_doc in items:
    item_data = item_doc.to_dict()
    name = (item_data.get('name') or '').lower()
    brand = (item_data.get('brand') or '').lower()
    
    # Look for Tommy Hilfiger items
    if 'tommy hilfiger' in name or 'tommy hilfiger' in brand or 'tommy' in brand:
        tommy_items.append(item_data)

print(f"\n✅ Found {len(tommy_items)} Tommy Hilfiger items\n")

# Print details
for idx, item in enumerate(tommy_items):
    print(f"{'='*80}")
    print(f"Item {idx+1}: {item.get('name', 'Unknown')}")
    print(f"{'='*80}")
    print(f"ID: {item.get('id', 'No ID')}")
    print(f"Name: {item.get('name', 'No name')}")
    print(f"Type: {item.get('type', 'No type')}")
    print(f"Color: {item.get('color', 'No color')}")
    print(f"Brand: {item.get('brand', 'No brand')}")
    print(f"Occasion: {item.get('occasion', [])}")
    print(f"Style: {item.get('style', [])}")
    print(f"Tags: {item.get('tags', [])}")
    
    # Check metadata
    metadata = item.get('metadata', {})
    if metadata:
        print(f"\n📦 METADATA:")
        print(f"  Visual Attributes: {metadata.get('visualAttributes', 'None')}")
        print(f"  Basic Metadata: {metadata.get('basicMetadata', 'None')}")
        print(f"  Item Metadata: {metadata.get('itemMetadata', 'None')}")
        
        # Check for collar info
        visual_attrs = metadata.get('visualAttributes', {})
        if visual_attrs:
            print(f"\n  🔍 Visual Attributes Detail:")
            print(f"    - neckline: {visual_attrs.get('neckline', 'Not set')}")
            print(f"    - sleeveLength: {visual_attrs.get('sleeveLength', 'Not set')}")
            print(f"    - fit: {visual_attrs.get('fit', 'Not set')}")
            print(f"    - pattern: {visual_attrs.get('pattern', 'Not set')}")
            print(f"    - formality: {visual_attrs.get('formality', 'Not set')}")
    else:
        print(f"\n⚠️ NO METADATA")
    
    print(f"\n")

print(f"\n{'='*80}")
print(f"SUMMARY: Found {len(tommy_items)} Tommy Hilfiger item(s)")
print(f"{'='*80}\n")

