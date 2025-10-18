#!/usr/bin/env python3
"""
Complete Wardrobe Metadata Backfill
====================================

Fixes ALL wardrobe items to have proper metadata structure:
1. Restructures data from analysis object to metadata.visualAttributes
2. Adds missing fields (neckline, description, Phase 1 fields)
3. Ensures all metadata is in the correct location for frontend display
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
import time

db = firestore.Client()
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"


def generate_description(item, analysis, visual_attrs):
    """Generate a description from existing data."""
    # Try to get from various sources
    if visual_attrs.get('naturalDescription'):
        return visual_attrs['naturalDescription']
    
    fit = analysis.get('fit') or visual_attrs.get('fit', 'regular')
    material = analysis.get('material') or visual_attrs.get('material', 'cotton')
    item_type = item.get('type', 'item')
    color = item.get('color', '')
    sleeve = analysis.get('sleeveLength') or visual_attrs.get('sleeveLength', '')
    brand = item.get('brand', '')
    
    parts = []
    if fit and fit.lower() not in ['none', 'unknown']:
        parts.append(fit.lower())
    if material and material.lower() not in ['none', 'unknown']:
        parts.append(material.lower())
    parts.append(item_type)
    if color:
        parts.append(f"in {color.lower()}")
    if sleeve and sleeve.lower() not in ['none', 'unknown']:
        parts.append(f"with {sleeve.lower()} sleeves")
    if brand and brand != 'Unknown':
        parts.append(f"by {brand}")
    
    return "A " + " ".join(parts)


def infer_neckline(item):
    """Infer neckline from item type."""
    item_type = item.get('type', '').lower()
    subtype = item.get('subType', '').lower()
    name = item.get('name', '').lower()
    
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
    elif 't-shirt' in item_type or 't shirt' in subtype:
        return 'crew'
    elif 'dress' in item_type:
        return 'various'
    elif 'sweater' in item_type or 'hoodie' in item_type:
        return 'crew'
    elif 'blouse' in item_type or 'shirt' in item_type:
        return 'collar'
    elif 'tank' in item_type:
        return 'tank'
    else:
        return 'none'


def backfill_item(doc_id, item):
    """Backfill metadata for a single item."""
    item_name = item.get('name', 'Unknown')[:60]
    
    # Get existing data
    analysis = item.get('analysis', {})
    metadata = item.get('metadata', {})
    visual_attrs = metadata.get('visualAttributes', {})
    
    # Check if restructuring is needed
    needs_restructure = bool(analysis) and not visual_attrs
    needs_description = not metadata.get('naturalDescription')
    needs_neckline = not visual_attrs.get('neckline')
    
    if not (needs_restructure or needs_description or needs_neckline):
        return False, "Already complete"
    
    # Build complete visualAttributes
    if needs_restructure:
        # Extract ALL fields from analysis (flat structure)
        new_visual_attrs = {
            # Core fields from analysis
            'material': analysis.get('material', visual_attrs.get('material', 'cotton')),
            'pattern': analysis.get('pattern', visual_attrs.get('pattern', 'solid')),
            'fit': analysis.get('fit', visual_attrs.get('fit', 'regular')),
            'formalLevel': analysis.get('formalLevel', visual_attrs.get('formalLevel', 'Casual')),
            'sleeveLength': analysis.get('sleeveLength', visual_attrs.get('sleeveLength', 'unknown')),
            'fabricWeight': visual_attrs.get('fabricWeight', 'medium'),
            'silhouette': visual_attrs.get('silhouette', 'regular'),
            'genderTarget': analysis.get('gender', visual_attrs.get('genderTarget', 'Unisex')),
            # Critical layering fields
            'wearLayer': visual_attrs.get('wearLayer', 'Mid'),
            'textureStyle': visual_attrs.get('textureStyle', 'smooth'),
            'length': visual_attrs.get('length', 'regular'),
            # Phase 1 new fields
            'neckline': visual_attrs.get('neckline') or infer_neckline(item),
            'transparency': visual_attrs.get('transparency', 'opaque'),
            'collarType': visual_attrs.get('collarType', 'none'),
            'embellishments': visual_attrs.get('embellishments', 'none'),
            'printSpecificity': visual_attrs.get('printSpecificity', 'none'),
            'rise': visual_attrs.get('rise', 'none'),
            'legOpening': visual_attrs.get('legOpening', 'none'),
            'heelHeight': visual_attrs.get('heelHeight', 'none'),
            'statementLevel': visual_attrs.get('statementLevel', 3),
            # Additional
            'waistbandType': visual_attrs.get('waistbandType', 'none'),
            'backgroundRemoved': visual_attrs.get('backgroundRemoved', False),
            'hangerPresent': visual_attrs.get('hangerPresent', False),
        }
    else:
        new_visual_attrs = visual_attrs.copy()
        
        # Add missing neckline
        if needs_neckline:
            new_visual_attrs['neckline'] = infer_neckline(item)
    
    # Generate description if missing
    new_description = metadata.get('naturalDescription')
    if needs_description:
        new_description = generate_description(item, analysis, new_visual_attrs)
    
    # Update metadata
    updated_metadata = metadata.copy() if metadata else {}
    updated_metadata['visualAttributes'] = new_visual_attrs
    updated_metadata['naturalDescription'] = new_description
    
    # Keep existing metadata fields
    if 'colorAnalysis' in metadata:
        updated_metadata['colorAnalysis'] = metadata['colorAnalysis']
    if 'analysisTimestamp' in metadata:
        updated_metadata['analysisTimestamp'] = metadata['analysisTimestamp']
    
    # Update in Firestore
    db.collection('wardrobe').document(doc_id).update({'metadata': updated_metadata})
    
    actions = []
    if needs_restructure:
        actions.append("restructured from analysis")
    if needs_description:
        actions.append("added description")
    if needs_neckline:
        actions.append("added neckline")
    
    return True, ", ".join(actions)


def backfill_all():
    """Backfill all wardrobe items."""
    
    print("\n" + "="*80)
    print("COMPLETE WARDROBE METADATA BACKFILL")
    print("="*80)
    print()
    
    # Get all items
    print("📦 Fetching all wardrobe items...")
    docs = db.collection('wardrobe').where('userId', '==', USER_ID).stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['_doc_id'] = doc.id
        items.append((doc.id, item_data))
    
    total_items = len(items)
    print(f"✅ Found {total_items} items\n")
    
    # Statistics
    stats = {
        'total': total_items,
        'already_complete': 0,
        'fixed': 0,
        'errors': 0,
        'restructured': 0,
        'added_description': 0,
        'added_neckline': 0
    }
    
    # Process each item
    print("🔄 Processing items...\n")
    for idx, (doc_id, item) in enumerate(items, 1):
        item_name = item.get('name', 'Unknown')[:60]
        print(f"[{idx}/{total_items}] {item_name}", end="")
        
        try:
            updated, action = backfill_item(doc_id, item)
            
            if updated:
                stats['fixed'] += 1
                if 'restructured' in action:
                    stats['restructured'] += 1
                if 'description' in action:
                    stats['added_description'] += 1
                if 'neckline' in action:
                    stats['added_neckline'] += 1
                print(f" ✅ {action}")
            else:
                stats['already_complete'] += 1
                print(" ✓ OK")
            
            # Rate limiting
            time.sleep(0.05)
            
        except Exception as e:
            stats['errors'] += 1
            print(f" ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("BACKFILL SUMMARY")
    print("="*80)
    print(f"Total items processed:      {stats['total']}")
    print(f"Already complete:           {stats['already_complete']}")
    print(f"Items fixed:                {stats['fixed']}")
    print(f"  - Restructured:           {stats['restructured']}")
    print(f"  - Added description:      {stats['added_description']}")
    print(f"  - Added neckline:         {stats['added_neckline']}")
    print(f"Errors:                     {stats['errors']}")
    print("="*80)
    
    if stats['errors'] == 0 and stats['fixed'] > 0:
        print("\n✅ Backfill completed successfully!")
        print(f"   {stats['fixed']} items updated with proper metadata structure")
        print("\n🔄 NEXT STEP: Refresh your wardrobe page to see all metadata!")
    elif stats['errors'] == 0:
        print("\n✅ All items already had complete metadata!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")
    
    print("="*80)


if __name__ == "__main__":
    try:
        backfill_all()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

