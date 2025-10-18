#!/usr/bin/env python3
"""
Backfill Missing Metadata for All Items
========================================

Adds missing naturalDescription and neckline fields to ALL wardrobe items.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
import time

db = firestore.Client()
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

def generate_description(item, visual_attrs):
    """Generate a description based on existing metadata."""
    item_type = item.get('type', 'item')
    color = item.get('color', '')
    brand = item.get('brand', '')
    material = visual_attrs.get('material', '')
    fit = visual_attrs.get('fit', '')
    sleeve = visual_attrs.get('sleeveLength', '')
    pattern = visual_attrs.get('pattern', '')
    
    description_parts = []
    
    if fit and fit.lower() not in ['none', 'unknown', 'null']:
        description_parts.append(fit.lower())
    if pattern and pattern.lower() not in ['none', 'unknown', 'null', 'solid']:
        description_parts.append(pattern.lower())
    if material and material.lower() not in ['none', 'unknown', 'null']:
        description_parts.append(material.lower())
    
    description_parts.append(item_type)
    
    if color:
        description_parts.append(f"in {color.lower()}")
    if sleeve and sleeve.lower() not in ['none', 'unknown', 'null']:
        description_parts.append(f"with {sleeve.lower()} sleeves")
    if brand:
        description_parts.append(f"by {brand}")
    
    return "A " + " ".join(description_parts)


def infer_neckline(item):
    """Infer neckline based on item type."""
    item_type = item.get('type', '').lower()
    subtype = item.get('subType', '').lower()
    name = item.get('name', '').lower()
    
    # Check common neckline indicators
    if 'v-neck' in name or 'vneck' in name:
        return 'v-neck'
    elif 'crew' in name or 'crewneck' in name:
        return 'crew'
    elif 'scoop' in name:
        return 'scoop'
    elif 'turtleneck' in name or 'turtle' in name:
        return 'turtleneck'
    elif 'polo' in item_type or 'polo' in name:
        return 'collar'
    elif 't-shirt' in item_type or 't shirt' in subtype or 'tshirt' in item_type:
        return 'crew'
    elif 'dress' in item_type:
        return 'various'
    elif 'sweater' in item_type or 'hoodie' in item_type:
        return 'crew'
    elif 'blouse' in item_type or 'shirt' in item_type:
        return 'collar'
    elif 'tank' in item_type or 'cami' in item_type:
        return 'tank'
    else:
        return 'standard'


def backfill_all_items():
    """Backfill metadata for all items."""
    
    print("\n🔍 Fetching all wardrobe items...")
    
    # Get all items
    docs = db.collection('wardrobe').where('userId', '==', USER_ID).stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['_doc_id'] = doc.id
        items.append(item_data)
    
    total_items = len(items)
    print(f"✅ Found {total_items} items\n")
    
    # Statistics
    stats = {
        'total': total_items,
        'already_complete': 0,
        'updated_description': 0,
        'updated_neckline': 0,
        'updated_both': 0,
        'errors': 0
    }
    
    # Process each item
    for idx, item in enumerate(items, 1):
        item_id = item.get('_doc_id')
        item_name = item.get('name', 'Unknown')[:50]
        
        print(f"[{idx}/{total_items}] Processing: {item_name}")
        
        try:
            metadata = item.get('metadata', {})
            visual_attrs = metadata.get('visualAttributes', {})
            
            current_desc = metadata.get('naturalDescription')
            current_neckline = visual_attrs.get('neckline')
            
            updates_needed = {}
            
            # Check if description is missing or null
            if not current_desc or current_desc == 'null':
                description = generate_description(item, visual_attrs)
                updates_needed['description'] = description
            
            # Check if neckline is missing
            if not current_neckline:
                neckline = infer_neckline(item)
                updates_needed['neckline'] = neckline
            
            if updates_needed:
                # Build update object
                update_obj = {'metadata': metadata.copy()}
                
                if 'description' in updates_needed:
                    update_obj['metadata']['naturalDescription'] = updates_needed['description']
                    stats['updated_description'] += 1
                
                if 'neckline' in updates_needed:
                    if 'visualAttributes' not in update_obj['metadata']:
                        update_obj['metadata']['visualAttributes'] = visual_attrs.copy()
                    update_obj['metadata']['visualAttributes']['neckline'] = updates_needed['neckline']
                    stats['updated_neckline'] += 1
                
                if len(updates_needed) == 2:
                    stats['updated_both'] += 1
                
                # Update in Firestore
                doc_ref = db.collection('wardrobe').document(item_id)
                doc_ref.update(update_obj)
                
                print(f"  ✅ Updated: {', '.join(updates_needed.keys())}")
                
                # Rate limiting
                time.sleep(0.1)
            else:
                stats['already_complete'] += 1
                print(f"  ✓ Already complete")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['errors'] += 1
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("BACKFILL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total items processed:        {stats['total']}")
    print(f"Already had complete metadata: {stats['already_complete']}")
    print(f"Updated description:          {stats['updated_description']}")
    print(f"Updated neckline:             {stats['updated_neckline']}")
    print(f"Updated both:                 {stats['updated_both']}")
    print(f"Errors:                       {stats['errors']}")
    print(f"{'=' * 80}")
    
    if stats['errors'] == 0:
        print("\n✅ Backfill completed successfully!")
    else:
        print(f"\n⚠️  Backfill completed with {stats['errors']} errors")


if __name__ == "__main__":
    print("=" * 80)
    print("BACKFILL ALL ITEMS - Add Missing Metadata")
    print("=" * 80)
    print("\nThis will add missing naturalDescription and neckline fields")
    print("to ALL wardrobe items that don't have them.")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    
    try:
        backfill_all_items()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

