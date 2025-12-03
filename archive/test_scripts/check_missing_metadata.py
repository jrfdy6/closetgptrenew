#!/usr/bin/env python3
"""
Check how many wardrobe items are missing metadata (pattern, material, fit)
"""

from google.cloud import firestore
import sys
sys.path.insert(0, 'backend')

db = firestore.Client()
user_id = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'

print("=" * 80)
print("METADATA COMPLETENESS ANALYSIS")
print("=" * 80)
print()

# Get all items
items = list(db.collection('wardrobe').where('userId', '==', user_id).stream())
total_items = len(items)

print(f"Total items in wardrobe: {total_items}")
print()

# Statistics
stats = {
    'has_metadata': 0,
    'no_metadata': 0,
    'has_visual_attributes': 0,
    'no_visual_attributes': 0,
    'has_pattern': 0,
    'has_material': 0,
    'has_fit': 0,
    'complete_metadata': 0  # Has pattern AND material AND fit
}

# Categories breakdown
category_stats = {}

# Examples
items_with_metadata = []
items_without_metadata = []

for item_doc in items:
    data = item_doc.to_dict()
    item_id = item_doc.id
    name = data.get('name', 'Unknown')
    item_type = data.get('type', 'unknown')
    
    # Track category
    if item_type not in category_stats:
        category_stats[item_type] = {
            'total': 0,
            'has_metadata': 0,
            'missing_metadata': 0
        }
    category_stats[item_type]['total'] += 1
    
    # Check metadata
    metadata = data.get('metadata')
    
    if metadata:
        stats['has_metadata'] += 1
        category_stats[item_type]['has_metadata'] += 1
        
        # Check visualAttributes
        visual_attrs = metadata.get('visualAttributes')
        
        if visual_attrs:
            stats['has_visual_attributes'] += 1
            
            # Check individual fields
            pattern = visual_attrs.get('pattern')
            material = visual_attrs.get('material')
            fit = visual_attrs.get('fit')
            
            if pattern:
                stats['has_pattern'] += 1
            if material:
                stats['has_material'] += 1
            if fit:
                stats['has_fit'] += 1
            
            if pattern and material and fit:
                stats['complete_metadata'] += 1
                if len(items_with_metadata) < 3:
                    items_with_metadata.append({
                        'name': name,
                        'type': item_type,
                        'pattern': pattern,
                        'material': material,
                        'fit': fit
                    })
            else:
                if len(items_without_metadata) < 3:
                    items_without_metadata.append({
                        'name': name,
                        'type': item_type,
                        'pattern': pattern,
                        'material': material,
                        'fit': fit
                    })
        else:
            stats['no_visual_attributes'] += 1
            category_stats[item_type]['missing_metadata'] += 1
            if len(items_without_metadata) < 3:
                items_without_metadata.append({
                    'name': name,
                    'type': item_type,
                    'pattern': None,
                    'material': None,
                    'fit': None
                })
    else:
        stats['no_metadata'] += 1
        stats['no_visual_attributes'] += 1
        category_stats[item_type]['missing_metadata'] += 1
        if len(items_without_metadata) < 3:
            items_without_metadata.append({
                'name': name,
                'type': item_type,
                'pattern': None,
                'material': None,
                'fit': None
            })

# Print results
print("OVERALL STATISTICS:")
print("-" * 80)
print(f"✅ Items with metadata object:        {stats['has_metadata']:>3} ({stats['has_metadata']/total_items*100:.1f}%)")
print(f"❌ Items without metadata object:     {stats['no_metadata']:>3} ({stats['no_metadata']/total_items*100:.1f}%)")
print()
print(f"✅ Items with visualAttributes:       {stats['has_visual_attributes']:>3} ({stats['has_visual_attributes']/total_items*100:.1f}%)")
print(f"❌ Items without visualAttributes:    {stats['no_visual_attributes']:>3} ({stats['no_visual_attributes']/total_items*100:.1f}%)")
print()
print(f"📊 Items with pattern data:           {stats['has_pattern']:>3} ({stats['has_pattern']/total_items*100:.1f}%)")
print(f"📊 Items with material data:          {stats['has_material']:>3} ({stats['has_material']/total_items*100:.1f}%)")
print(f"📊 Items with fit data:               {stats['has_fit']:>3} ({stats['has_fit']/total_items*100:.1f}%)")
print()
print(f"🎯 Items with COMPLETE metadata:      {stats['complete_metadata']:>3} ({stats['complete_metadata']/total_items*100:.1f}%)")
print(f"   (has pattern AND material AND fit)")
print()

print("BREAKDOWN BY CATEGORY:")
print("-" * 80)
for category, cat_stats in sorted(category_stats.items()):
    pct = (cat_stats['has_metadata'] / cat_stats['total'] * 100) if cat_stats['total'] > 0 else 0
    print(f"{category:20} | Total: {cat_stats['total']:>3} | With metadata: {cat_stats['has_metadata']:>3} ({pct:>5.1f}%) | Missing: {cat_stats['missing_metadata']:>3}")

print()
print("EXAMPLES OF ITEMS WITH COMPLETE METADATA:")
print("-" * 80)
for item in items_with_metadata[:3]:
    print(f"✅ {item['name'][:50]}")
    print(f"   Type: {item['type']}")
    print(f"   Pattern: {item['pattern']}, Material: {item['material']}, Fit: {item['fit']}")
    print()

print("EXAMPLES OF ITEMS WITHOUT METADATA:")
print("-" * 80)
for item in items_without_metadata[:3]:
    print(f"❌ {item['name'][:50]}")
    print(f"   Type: {item['type']}")
    print(f"   Pattern: {item['pattern']}, Material: {item['material']}, Fit: {item['fit']}")
    print()

print("=" * 80)
print("RECOMMENDATION:")
if stats['complete_metadata'] / total_items < 0.5:
    print("⚠️  Less than 50% of items have complete metadata")
    print("    Run metadata backfill to enable pattern/material/fit scoring")
elif stats['complete_metadata'] / total_items < 0.8:
    print("⚠️  Metadata coverage is incomplete")
    print("    Consider backfilling for better t-shirt variety")
else:
    print("✅ Good metadata coverage!")
    print("   Pattern/material/fit scoring should work well")
print("=" * 80)

