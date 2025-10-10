"""
Wardrobe Metadata Audit Script
===============================

Analyzes all wardrobe items to identify missing metadata fields.
Generates comprehensive report showing:
- Which fields are missing
- How many items are affected
- Priority for backfilling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
from collections import defaultdict
import json

# Initialize Firestore
db = firestore.Client()

# User ID to audit
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

# Critical fields for metadata compatibility system
CRITICAL_FIELDS = {
    'root': {
        'bodyTypeCompatibility': 'Body type analyzer (Analyzer #1)',
        'weatherCompatibility': 'Weather analyzer (Analyzer #3)',
        'gender': 'Gender filtering',
        'backgroundRemoved': 'Image quality check',
        'mood': 'Mood filtering',
    },
    'metadata': {
        'visualAttributes': 'ALL compatibility scoring',
        'naturalDescription': 'Semantic insights',
        'normalized': 'Consistent filtering',
    },
    'metadata.visualAttributes': {
        'wearLayer': 'CRITICAL: Layer positioning',
        'sleeveLength': 'CRITICAL: Sleeve validation',
        'textureStyle': 'Pattern/texture mixing',
        'fabricWeight': 'Temperature matching',
        'fit': 'Fit/silhouette balance',
        'silhouette': 'Proportion harmony',
        'pattern': 'Pattern mixing',
        'formalLevel': 'Formality matching',
        'material': 'Material analysis',
        'length': 'Length compatibility',
        'genderTarget': 'Gender targeting',
        'hangerPresent': 'Image metadata',
        'backgroundRemoved': 'Image quality',
    }
}


def check_field_exists(item, field_path):
    """Check if a nested field exists in item."""
    parts = field_path.split('.')
    current = item
    
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return False
            current = current[part]
        else:
            return False
    
    # Check if value is not None and not empty
    if current is None:
        return False
    if isinstance(current, (list, dict, str)) and not current:
        return False
    
    return True


def audit_wardrobe():
    """Audit all wardrobe items for missing metadata."""
    
    print("\n" + "="*80)
    print("WARDROBE METADATA AUDIT")
    print("="*80)
    print(f"User ID: {USER_ID}\n")
    
    # Get all wardrobe items
    print("📦 Fetching wardrobe items from Firestore...")
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID)
    docs = wardrobe_ref.stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['_doc_id'] = doc.id
        items.append(item_data)
    
    print(f"✅ Retrieved {len(items)} items\n")
    
    if not items:
        print("❌ No items found!")
        return
    
    # Track missing fields
    missing_stats = defaultdict(int)
    items_missing = defaultdict(list)
    
    # Check each item
    for item in items:
        item_id = item.get('id', item.get('_doc_id', 'unknown'))
        item_name = item.get('name', 'Unknown')[:50]
        
        # Check ROOT fields
        for field, description in CRITICAL_FIELDS['root'].items():
            if not check_field_exists(item, field):
                missing_stats[f'root.{field}'] += 1
                items_missing[f'root.{field}'].append(f"{item_id[:15]}... - {item_name}")
        
        # Check metadata exists
        if 'metadata' not in item or not item['metadata']:
            missing_stats['metadata'] += 1
            items_missing['metadata'].append(f"{item_id[:15]}... - {item_name}")
            continue
        
        # Check metadata-level fields
        for field, description in CRITICAL_FIELDS['metadata'].items():
            if not check_field_exists(item, f'metadata.{field}'):
                missing_stats[f'metadata.{field}'] += 1
                items_missing[f'metadata.{field}'].append(f"{item_id[:15]}... - {item_name}")
        
        # Check visualAttributes fields
        if check_field_exists(item, 'metadata.visualAttributes'):
            for field, description in CRITICAL_FIELDS['metadata.visualAttributes'].items():
                if not check_field_exists(item, f'metadata.visualAttributes.{field}'):
                    missing_stats[f'metadata.visualAttributes.{field}'] += 1
                    items_missing[f'metadata.visualAttributes.{field}'].append(f"{item_id[:15]}... - {item_name}")
    
    # Generate Report
    print("="*80)
    print("MISSING METADATA REPORT")
    print("="*80)
    
    total_items = len(items)
    
    # Summary Statistics
    print(f"\n📊 Summary Statistics:")
    print(f"Total Items: {total_items}")
    
    items_with_complete_metadata = sum(
        1 for item in items 
        if check_field_exists(item, 'metadata.visualAttributes.wearLayer') and
           check_field_exists(item, 'metadata.visualAttributes.sleeveLength')
    )
    
    print(f"Items with CRITICAL metadata (wearLayer + sleeveLength): {items_with_complete_metadata}")
    print(f"Items MISSING critical metadata: {total_items - items_with_complete_metadata}")
    print(f"Completion Rate: {(items_with_complete_metadata/total_items)*100:.1f}%")
    
    # Critical Missing Fields
    print(f"\n🚨 CRITICAL Fields (Required for Layer Compatibility):")
    print(f"-" * 80)
    
    critical_missing = [
        ('metadata.visualAttributes.wearLayer', 'Layer positioning'),
        ('metadata.visualAttributes.sleeveLength', 'Sleeve validation'),
    ]
    
    for field, description in critical_missing:
        count = missing_stats.get(field, 0)
        pct = (count / total_items) * 100
        status = "✅" if count == 0 else "❌"
        print(f"{status} {description:30} Missing: {count:3}/{total_items} ({pct:5.1f}%)")
    
    # High Priority Missing Fields
    print(f"\n⚠️  HIGH PRIORITY Fields (Required for Full Compatibility):")
    print(f"-" * 80)
    
    high_priority = [
        ('metadata.visualAttributes.pattern', 'Pattern mixing'),
        ('metadata.visualAttributes.fit', 'Fit balance'),
        ('metadata.visualAttributes.formalLevel', 'Formality matching'),
        ('metadata.visualAttributes.textureStyle', 'Texture mixing'),
        ('metadata.visualAttributes.fabricWeight', 'Temperature matching'),
    ]
    
    for field, description in high_priority:
        count = missing_stats.get(field, 0)
        pct = (count / total_items) * 100
        status = "✅" if count == 0 else "⚠️"
        print(f"{status} {description:30} Missing: {count:3}/{total_items} ({pct:5.1f}%)")
    
    # Medium Priority Fields
    print(f"\n📋 MEDIUM PRIORITY Fields (Useful for Enhanced Scoring):")
    print(f"-" * 80)
    
    medium_priority = [
        ('root.bodyTypeCompatibility', 'Body type scoring'),
        ('root.weatherCompatibility', 'Weather scoring'),
        ('metadata.naturalDescription', 'Semantic insights'),
        ('metadata.normalized', 'Filtering consistency'),
        ('root.mood', 'Mood filtering'),
        ('root.gender', 'Gender filtering'),
    ]
    
    for field, description in medium_priority:
        count = missing_stats.get(field, 0)
        pct = (count / total_items) * 100
        status = "✅" if count == 0 else "📝"
        print(f"{status} {description:30} Missing: {count:3}/{total_items} ({pct:5.1f}%)")
    
    # Low Priority Fields
    print(f"\n💡 LOW PRIORITY Fields (Nice to Have):")
    print(f"-" * 80)
    
    low_priority = [
        ('metadata.visualAttributes.silhouette', 'Silhouette detail'),
        ('metadata.visualAttributes.length', 'Length detail'),
        ('metadata.visualAttributes.genderTarget', 'Gender target'),
        ('metadata.visualAttributes.hangerPresent', 'Image metadata'),
        ('root.backgroundRemoved', 'Image quality'),
    ]
    
    for field, description in low_priority:
        count = missing_stats.get(field, 0)
        pct = (count / total_items) * 100
        status = "✅" if count == 0 else "💡"
        print(f"{status} {description:30} Missing: {count:3}/{total_items} ({pct:5.1f}%)")
    
    # Items with NO metadata at all
    print(f"\n" + "="*80)
    no_metadata = sum(1 for item in items if 'metadata' not in item or not item['metadata'])
    no_visual_attrs = sum(
        1 for item in items 
        if not check_field_exists(item, 'metadata.visualAttributes')
    )
    
    print(f"📊 Metadata Completeness:")
    print(f"  Items with NO metadata object: {no_metadata}/{total_items}")
    print(f"  Items with NO visualAttributes: {no_visual_attrs}/{total_items}")
    print(f"  Items with COMPLETE visualAttributes: {total_items - no_visual_attrs}/{total_items}")
    
    # Backfill Priority
    print(f"\n" + "="*80)
    print("🔧 BACKFILL RECOMMENDATIONS:")
    print("="*80)
    
    if items_with_complete_metadata == total_items:
        print("✅ All items have complete metadata! No backfill needed.")
    elif items_with_complete_metadata > total_items * 0.8:
        print(f"✅ Good coverage ({items_with_complete_metadata}/{total_items} items)")
        print(f"📝 Consider backfilling {total_items - items_with_complete_metadata} items for 100% coverage")
    elif items_with_complete_metadata > total_items * 0.5:
        print(f"⚠️  Moderate coverage ({items_with_complete_metadata}/{total_items} items)")
        print(f"📝 Recommend backfilling {total_items - items_with_complete_metadata} items")
    else:
        print(f"🚨 LOW coverage ({items_with_complete_metadata}/{total_items} items)")
        print(f"🔧 URGENT: Backfill {total_items - items_with_complete_metadata} items to unlock full system")
    
    print(f"\nPriority 1 (CRITICAL): Backfill wearLayer + sleeveLength")
    print(f"Priority 2 (HIGH): Backfill pattern + fit + formalLevel")
    print(f"Priority 3 (MEDIUM): Backfill bodyTypeCompatibility + weatherCompatibility")
    
    # Sample items missing critical fields
    if missing_stats.get('metadata.visualAttributes.wearLayer', 0) > 0:
        print(f"\n📋 Sample Items Missing wearLayer (first 5):")
        for item_desc in items_missing['metadata.visualAttributes.wearLayer'][:5]:
            print(f"  - {item_desc}")
    
    # Export detailed report
    report = {
        'total_items': total_items,
        'items_with_critical_metadata': items_with_complete_metadata,
        'completion_rate': (items_with_complete_metadata/total_items)*100,
        'missing_fields_summary': dict(missing_stats),
        'backfill_needed': total_items - items_with_complete_metadata
    }
    
    with open('wardrobe_metadata_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: wardrobe_metadata_audit_report.json")
    print("="*80)


if __name__ == "__main__":
    try:
        audit_wardrobe()
    except Exception as e:
        print(f"\n❌ Error running audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

