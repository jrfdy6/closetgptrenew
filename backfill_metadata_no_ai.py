"""
Backfill Wardrobe Metadata WITHOUT AI API Calls
================================================

Intelligently infers missing metadata from:
- Item name (e.g., "long sleeve shirt" → sleeveLength: "Long")
- Item type (e.g., "jacket" → wearLayer: "Outer")
- Existing metadata fields
- Pattern recognition in names

NO OpenAI API calls = NO cost!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
import time
from typing import Dict, Any, List

# Initialize Firestore
db = firestore.Client()

# User ID to backfill
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

# Inference rules
LAYER_INFERENCE = {
    'jacket': 'Outer',
    'coat': 'Outer',
    'blazer': 'Outer',
    'cardigan': 'Outer',
    'hoodie': 'Outer',
    'sweater': 'Mid',
    'shirt': 'Mid',
    'blouse': 'Mid',
    't-shirt': 'Inner',
    'tank': 'Inner',
    'camisole': 'Inner',
    'undershirt': 'Base',
    'pants': 'Bottom',
    'jeans': 'Bottom',
    'shorts': 'Bottom',
    'skirt': 'Bottom',
    'dress': 'Bottom',
    'shoes': 'Footwear',
    'sneakers': 'Footwear',
    'boots': 'Footwear',
    'sandals': 'Footwear',
    'belt': 'Accessory',
    'scarf': 'Accessory',
    'hat': 'Accessory',
    'bag': 'Accessory',
}

SLEEVE_KEYWORDS = {
    'sleeveless': 'Sleeveless',
    'tank': 'Sleeveless',
    'short sleeve': 'Short',
    'short-sleeve': 'Short',
    'short': 'Short',
    'long sleeve': 'Long',
    'long-sleeve': 'Long',
    'long': 'Long',
    '3/4 sleeve': '3/4',
    'three quarter': '3/4',
}

FIT_KEYWORDS = {
    'slim': 'slim',
    'fitted': 'fitted',
    'tight': 'fitted',
    'skinny': 'fitted',
    'loose': 'loose',
    'relaxed': 'relaxed',
    'oversized': 'oversized',
    'baggy': 'oversized',
    'regular': 'regular',
}

FORMALITY_KEYWORDS = {
    'formal': 'Formal',
    'dress': 'Business Casual',
    'suit': 'Formal',
    'tuxedo': 'Formal',
    'business': 'Business Casual',
    'casual': 'Casual',
    'athletic': 'Casual',
    'sport': 'Casual',
}

PATTERN_KEYWORDS = {
    'striped': 'striped',
    'stripe': 'striped',
    'checkered': 'checkered',
    'check': 'checkered',
    'plaid': 'plaid',
    'floral': 'floral',
    'solid': 'solid',
    'plain': 'solid',
    'graphic': 'graphic',
    'print': 'graphic',
    'polka dot': 'polka dot',
    'leopard': 'leopard',
    'zebra': 'zebra',
}


def infer_wear_layer(item_type: str, item_name: str) -> str:
    """Infer wearLayer from item type and name."""
    item_type_lower = item_type.lower()
    item_name_lower = item_name.lower()
    
    # Check type first
    for type_keyword, layer in LAYER_INFERENCE.items():
        if type_keyword in item_type_lower:
            return layer
    
    # Check name
    for type_keyword, layer in LAYER_INFERENCE.items():
        if type_keyword in item_name_lower:
            return layer
    
    # Default
    return 'Mid'


def infer_sleeve_length(item_name: str, item_type: str, wear_layer: str) -> str:
    """Infer sleeveLength from item name and type."""
    item_name_lower = item_name.lower()
    item_type_lower = item_type.lower()
    
    # Non-sleeved items
    if wear_layer in ['Bottom', 'Footwear', 'Accessory']:
        return 'None'
    
    # Check for sleeve keywords in name
    for keyword, sleeve in SLEEVE_KEYWORDS.items():
        if keyword in item_name_lower:
            return sleeve
    
    # Defaults based on type
    if any(word in item_type_lower for word in ['t-shirt', 'tank', 'camisole']):
        return 'Short'
    elif any(word in item_type_lower for word in ['jacket', 'coat', 'blazer']):
        return 'Long'
    elif 'sweater' in item_type_lower:
        return 'Long'  # Most sweaters are long-sleeve
    elif 'shirt' in item_type_lower or 'blouse' in item_type_lower:
        return 'Long'  # Most dress shirts are long-sleeve
    
    return 'Unknown'


def infer_fit(item_name: str) -> str:
    """Infer fit from item name."""
    item_name_lower = item_name.lower()
    
    for keyword, fit in FIT_KEYWORDS.items():
        if keyword in item_name_lower:
            return fit
    
    return 'regular'


def infer_formality(item_name: str, item_type: str, occasions: List[str]) -> str:
    """Infer formalLevel from name, type, and occasions."""
    item_name_lower = item_name.lower()
    item_type_lower = item_type.lower()
    occasions_lower = [o.lower() for o in occasions]
    
    # Check occasions first
    if any(occ in occasions_lower for occ in ['formal', 'wedding', 'interview']):
        return 'Formal'
    if any(occ in occasions_lower for occ in ['business', 'conference']):
        return 'Business Casual'
    if any(occ in occasions_lower for occ in ['casual', 'beach', 'athletic']):
        return 'Casual'
    
    # Check name and type
    for keyword, formality in FORMALITY_KEYWORDS.items():
        if keyword in item_name_lower or keyword in item_type_lower:
            return formality
    
    return 'Casual'


def infer_pattern(item_name: str) -> str:
    """Infer pattern from item name."""
    item_name_lower = item_name.lower()
    
    for keyword, pattern in PATTERN_KEYWORDS.items():
        if keyword in item_name_lower:
            return pattern
    
    return 'solid'


def infer_fabric_weight(item_type: str, seasons: List[str]) -> str:
    """Infer fabricWeight from type and seasons."""
    item_type_lower = item_type.lower()
    seasons_lower = [s.lower() for s in seasons]
    
    # Heavy items
    if any(word in item_type_lower for word in ['coat', 'parka', 'winter jacket']):
        return 'Heavy'
    
    # Light items
    if any(word in item_type_lower for word in ['tank', 't-shirt', 'shorts']):
        return 'Light'
    
    # Check seasons
    if 'winter' in seasons_lower and 'summer' not in seasons_lower:
        return 'Heavy'
    if 'summer' in seasons_lower and 'winter' not in seasons_lower:
        return 'Light'
    
    return 'Medium'


def infer_gender(item_name: str, occasions: List[str]) -> str:
    """Infer gender from name and occasions."""
    item_name_lower = item_name.lower()
    
    if any(word in item_name_lower for word in ['mens', 'men\'s', 'male']):
        return 'male'
    if any(word in item_name_lower for word in ['womens', 'women\'s', 'female', 'dress', 'blouse', 'skirt']):
        return 'female'
    
    return 'unisex'


def generate_normalized_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    """Generate normalized metadata from existing arrays."""
    normalized = {
        'occasion': [o.lower() for o in item.get('occasion', [])],
        'style': [s.lower() for s in item.get('style', [])],
        'mood': [m.lower() for m in item.get('mood', [])],
        'season': [s.lower() for s in item.get('season', [])],
        'normalized_at': time.strftime("%Y-%m-%dT%H:%M:%S"),
        'normalized_version': '1.0'
    }
    return normalized


def backfill_item(item: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Backfill missing metadata for a single item."""
    item_id = item.get('id', item.get('_doc_id', 'unknown'))
    item_name = item.get('name', 'Unknown')
    item_type = item.get('type', 'unknown')
    
    updates = {}
    fields_added = []
    
    # Get existing metadata or create it
    metadata = item.get('metadata', {})
    if not metadata:
        metadata = {
            'analysisTimestamp': int(time.time() * 1000),
            'originalType': item_type,
            'styleTags': item.get('style', []),
            'occasionTags': item.get('occasion', []),
            'colorAnalysis': {'dominant': [], 'matching': []}
        }
        updates['metadata'] = metadata
    
    # Get visualAttributes or create it
    visual_attrs = metadata.get('visualAttributes', {})
    if not visual_attrs:
        visual_attrs = {}
    
    # Infer missing fields
    if not visual_attrs.get('wearLayer'):
        visual_attrs['wearLayer'] = infer_wear_layer(item_type, item_name)
        fields_added.append('wearLayer')
    
    if not visual_attrs.get('sleeveLength'):
        wear_layer = visual_attrs.get('wearLayer', 'Mid')
        visual_attrs['sleeveLength'] = infer_sleeve_length(item_name, item_type, wear_layer)
        fields_added.append('sleeveLength')
    
    if not visual_attrs.get('fit'):
        visual_attrs['fit'] = infer_fit(item_name)
        fields_added.append('fit')
    
    if not visual_attrs.get('pattern'):
        visual_attrs['pattern'] = infer_pattern(item_name)
        fields_added.append('pattern')
    
    if not visual_attrs.get('formalLevel'):
        visual_attrs['formalLevel'] = infer_formality(item_name, item_type, item.get('occasion', []))
        fields_added.append('formalLevel')
    
    if not visual_attrs.get('fabricWeight'):
        visual_attrs['fabricWeight'] = infer_fabric_weight(item_type, item.get('season', []))
        fields_added.append('fabricWeight')
    
    if not visual_attrs.get('textureStyle'):
        visual_attrs['textureStyle'] = 'smooth'  # Default
        fields_added.append('textureStyle')
    
    if not visual_attrs.get('silhouette'):
        visual_attrs['silhouette'] = 'regular'
        fields_added.append('silhouette')
    
    if not visual_attrs.get('length'):
        visual_attrs['length'] = 'regular'
        fields_added.append('length')
    
    if not visual_attrs.get('genderTarget'):
        visual_attrs['genderTarget'] = 'Unisex'
        fields_added.append('genderTarget')
    
    if not visual_attrs.get('material'):
        visual_attrs['material'] = 'cotton'
        fields_added.append('material')
    
    # Update metadata with visual_attrs
    metadata['visualAttributes'] = visual_attrs
    updates['metadata.visualAttributes'] = visual_attrs
    
    # Generate normalized metadata
    if not metadata.get('normalized'):
        normalized = generate_normalized_metadata(item)
        metadata['normalized'] = normalized
        updates['metadata.normalized'] = normalized
        fields_added.append('normalized')
    
    # ROOT-level fields
    if not item.get('gender'):
        updates['gender'] = infer_gender(item_name, item.get('occasion', []))
        fields_added.append('gender')
    
    if not item.get('mood'):
        updates['mood'] = ['casual']  # Default
        fields_added.append('mood')
    
    if 'backgroundRemoved' not in item:
        updates['backgroundRemoved'] = False
        fields_added.append('backgroundRemoved')
    
    return {
        'item_id': item_id,
        'item_name': item_name[:50],
        'doc_id': item.get('_doc_id'),
        'fields_added': fields_added,
        'updates': updates,
        'update_count': len(fields_added)
    }


def run_backfill(dry_run: bool = True, limit: int = None):
    """Run the backfill process."""
    
    print("\n" + "="*80)
    print(f"WARDROBE METADATA BACKFILL {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("="*80)
    print(f"User ID: {USER_ID}")
    print(f"Mode: {'DRY RUN - No changes will be made' if dry_run else 'LIVE - Will update Firestore'}")
    if limit:
        print(f"Limit: {limit} items")
    print()
    
    # Get all wardrobe items
    print("📦 Fetching wardrobe items...")
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID)
    if limit:
        wardrobe_ref = wardrobe_ref.limit(limit)
    
    docs = wardrobe_ref.stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['_doc_id'] = doc.id
        items.append(item_data)
    
    print(f"✅ Retrieved {len(items)} items\n")
    
    # Process each item
    results = []
    items_updated = 0
    total_fields_added = 0
    
    print("🔄 Processing items...")
    print("-" * 80)
    
    for i, item in enumerate(items, 1):
        result = backfill_item(item, dry_run)
        
        if result['update_count'] > 0:
            items_updated += 1
            total_fields_added += result['update_count']
            
            # Show progress
            print(f"{i:3}/{len(items)} | {result['item_name']:50} | +{result['update_count']} fields")
            print(f"        Added: {', '.join(result['fields_added'][:5])}{'...' if len(result['fields_added']) > 5 else ''}")
            
            # Actually update Firestore if not dry run
            if not dry_run:
                try:
                    doc_ref = db.collection('wardrobe').document(result['doc_id'])
                    doc_ref.update(result['updates'])
                    print(f"        ✅ Updated in Firestore")
                except Exception as e:
                    print(f"        ❌ Error updating: {e}")
            
            results.append(result)
        else:
            # Item already complete
            if i % 10 == 0:  # Show progress every 10 items
                print(f"{i:3}/{len(items)} | Already complete items...")
    
    # Summary
    print("\n" + "="*80)
    print("BACKFILL SUMMARY")
    print("="*80)
    print(f"Total Items Processed: {len(items)}")
    print(f"Items Updated: {items_updated}")
    print(f"Items Already Complete: {len(items) - items_updated}")
    print(f"Total Fields Added: {total_fields_added}")
    print(f"Avg Fields per Item: {total_fields_added/items_updated if items_updated > 0 else 0:.1f}")
    
    if dry_run:
        print(f"\n⚠️  DRY RUN MODE - No changes were made to Firestore")
        print(f"Run with --live flag to actually update items")
    else:
        print(f"\n✅ LIVE MODE - {items_updated} items updated in Firestore!")
    
    # Field breakdown
    print(f"\n📊 Fields Added Breakdown:")
    field_counts = defaultdict(int)
    for result in results:
        for field in result['fields_added']:
            field_counts[field] += 1
    
    for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {field:30} : {count:3} items")
    
    print("="*80)
    
    return {
        'total_items': len(items),
        'items_updated': items_updated,
        'total_fields_added': total_fields_added,
        'field_breakdown': dict(field_counts)
    }


if __name__ == "__main__":
    from collections import defaultdict
    
    # Check for --live flag
    dry_run = '--live' not in sys.argv
    
    # Check for --limit flag
    limit = None
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--limit='):
            limit = int(arg.split('=')[1])
    
    if not dry_run:
        print("\n⚠️  WARNING: Running in LIVE mode!")
        print("This will update Firestore directly.")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    try:
        results = run_backfill(dry_run=dry_run, limit=limit)
        
        # Save results
        import json
        output_file = f"backfill_results_{'dry_run' if dry_run else 'live'}_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

