#!/usr/bin/env python3
"""
Backfill Metadata for Single Item
==================================

Adds missing metadata fields (naturalDescription, neckline) to a specific item.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
import json

db = firestore.Client()

def backfill_item(item_id):
    """Backfill metadata for a specific item."""
    
    print(f"\n🔍 Fetching item: {item_id}")
    
    # Get the item
    doc_ref = db.collection('wardrobe').document(item_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Item not found: {item_id}")
        return
    
    item = doc.to_dict()
    print(f"✅ Found: {item.get('name', 'Unknown')}")
    
    # Check current metadata
    metadata = item.get('metadata', {})
    visual_attrs = metadata.get('visualAttributes', {})
    
    current_desc = metadata.get('naturalDescription')
    current_neckline = visual_attrs.get('neckline')
    
    print(f"\n📊 Current Metadata:")
    print(f"  naturalDescription: {current_desc or 'NULL'}")
    print(f"  neckline:           {current_neckline or 'MISSING'}")
    print(f"  material:           {visual_attrs.get('material', 'MISSING')}")
    print(f"  sleeveLength:       {visual_attrs.get('sleeveLength', 'MISSING')}")
    print(f"  fit:                {visual_attrs.get('fit', 'MISSING')}")
    
    # Generate missing fields
    updates_needed = {}
    
    if not current_desc:
        # Generate a basic description based on existing data
        item_type = item.get('type', 'item')
        color = item.get('color', '')
        brand = item.get('brand', '')
        material = visual_attrs.get('material', '')
        fit = visual_attrs.get('fit', '')
        sleeve = visual_attrs.get('sleeveLength', '')
        
        description_parts = []
        if fit and fit != 'none':
            description_parts.append(fit.lower())
        if material and material != 'none':
            description_parts.append(material.lower())
        description_parts.append(item_type)
        if sleeve and sleeve != 'none':
            description_parts.append(f"with {sleeve.lower()} sleeves")
        if brand:
            description_parts.append(f"by {brand}")
        
        generated_desc = "A " + " ".join(description_parts)
        
        updates_needed['description'] = generated_desc
        print(f"\n✨ Generated Description: {generated_desc}")
    
    if not current_neckline:
        # Infer neckline based on item type
        item_type = item.get('type', '').lower()
        subtype = item.get('subType', '').lower()
        
        if 't-shirt' in item_type or 't shirt' in subtype or 'tshirt' in item_type:
            inferred_neckline = 'crew'
        elif 'polo' in item_type:
            inferred_neckline = 'collar'
        elif 'dress' in item_type:
            inferred_neckline = 'various'
        elif 'sweater' in item_type or 'hoodie' in item_type:
            inferred_neckline = 'crew'
        elif 'blouse' in item_type:
            inferred_neckline = 'various'
        else:
            inferred_neckline = 'standard'
        
        updates_needed['neckline'] = inferred_neckline
        print(f"✨ Inferred Neckline: {inferred_neckline}")
    
    # Apply updates
    if updates_needed:
        print(f"\n🔄 Applying updates...")
        
        # Build update object
        update_obj = {}
        
        if 'description' in updates_needed:
            if 'metadata' not in update_obj:
                update_obj['metadata'] = metadata.copy()
            update_obj['metadata']['naturalDescription'] = updates_needed['description']
        
        if 'neckline' in updates_needed:
            if 'metadata' not in update_obj:
                update_obj['metadata'] = metadata.copy()
            if 'visualAttributes' not in update_obj['metadata']:
                update_obj['metadata']['visualAttributes'] = visual_attrs.copy()
            update_obj['metadata']['visualAttributes']['neckline'] = updates_needed['neckline']
        
        # Update in Firestore
        doc_ref.update(update_obj)
        
        print(f"✅ Updates saved to Firestore!")
        print(f"\n📋 Updated Fields:")
        for field, value in updates_needed.items():
            print(f"  {field}: {value}")
    else:
        print(f"\n✅ No updates needed - item already has complete metadata!")
    
    print(f"\n{'=' * 80}")
    print(f"✅ BACKFILL COMPLETE")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    # The specific item ID for "Shirt t-shirt White by Celine"
    item_id = "oq0k7mk82fmc1az8mn"
    
    print("=" * 80)
    print("BACKFILL SINGLE ITEM - Add Missing Metadata")
    print("=" * 80)
    
    try:
        backfill_item(item_id)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

