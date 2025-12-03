#!/usr/bin/env python3
"""
Audit wardrobe items for missing occasion and style metadata.
Focuses specifically on items that are likely suitable for business/formal occasions.
"""

import os
import json
from collections import defaultdict
import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore_client():
    """Initialize and return Firestore client."""
    if not firebase_admin._apps:
        # Initialize Firebase Admin SDK
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # Use default credentials
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

def audit_occasion_style_metadata(user_id: str = "dANqjiI0CKgaitxzYtw1bhtvQrG3"):
    """Audit wardrobe items for missing occasion and style data."""
    
    print("🔍 Starting Occasion/Style Metadata Audit...")
    print(f"👤 User ID: {user_id}\n")
    
    db = get_firestore_client()
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    items = list(wardrobe_ref.stream())
    
    print(f"📊 Total wardrobe items: {len(items)}\n")
    
    # Statistics
    stats = {
        'total_items': len(items),
        'missing_occasions': 0,
        'missing_styles': 0,
        'missing_both': 0,
        'has_both': 0,
        'empty_occasion_array': 0,
        'empty_style_array': 0,
    }
    
    # Categorize by item type
    by_type = defaultdict(lambda: {
        'total': 0,
        'missing_occasions': 0,
        'missing_styles': 0,
        'missing_both': 0,
        'items': []
    })
    
    # Items that SHOULD have business/formal occasions
    business_suitable_types = [
        'dress shirt', 'button up', 'blazer', 'jacket', 'suit jacket',
        'dress pants', 'trousers', 'slacks', 'dress shoes', 'oxford',
        'derby', 'loafer', 'belt', 'tie', 'pocket square'
    ]
    
    potentially_fixable = []
    
    for doc in items:
        data = doc.to_dict()
        item_id = doc.id
        item_name = data.get('name', 'Unknown')
        item_type = data.get('type', '').lower()
        
        # Check for occasions
        occasions = data.get('occasion', [])
        if not isinstance(occasions, list):
            occasions = []
        
        # Check for styles
        styles = data.get('style', [])
        if not isinstance(styles, list):
            styles = []
        
        has_occasions = len(occasions) > 0
        has_styles = len(styles) > 0
        
        # Update stats
        if not has_occasions:
            stats['missing_occasions'] += 1
            stats['empty_occasion_array'] += 1
        if not has_styles:
            stats['missing_styles'] += 1
            stats['empty_style_array'] += 1
        if not has_occasions and not has_styles:
            stats['missing_both'] += 1
        if has_occasions and has_styles:
            stats['has_both'] += 1
        
        # Categorize by type
        by_type[item_type]['total'] += 1
        if not has_occasions:
            by_type[item_type]['missing_occasions'] += 1
        if not has_styles:
            by_type[item_type]['missing_styles'] += 1
        if not has_occasions and not has_styles:
            by_type[item_type]['missing_both'] += 1
        
        # Check if this is a business-suitable item missing metadata
        is_business_suitable = any(btype in item_name.lower() or btype in item_type for btype in business_suitable_types)
        
        if is_business_suitable and (not has_occasions or not has_styles):
            item_info = {
                'id': item_id,
                'name': item_name,
                'type': item_type,
                'occasions': occasions,
                'styles': styles,
                'missing': []
            }
            if not has_occasions:
                item_info['missing'].append('occasions')
            if not has_styles:
                item_info['missing'].append('styles')
            
            potentially_fixable.append(item_info)
            by_type[item_type]['items'].append(item_info)
    
    # Print summary
    print("=" * 80)
    print("📊 OVERALL STATISTICS")
    print("=" * 80)
    print(f"Total items: {stats['total_items']}")
    print(f"Items with BOTH occasion + style: {stats['has_both']} ({stats['has_both']/stats['total_items']*100:.1f}%)")
    print(f"Items missing occasions: {stats['missing_occasions']} ({stats['missing_occasions']/stats['total_items']*100:.1f}%)")
    print(f"Items missing styles: {stats['missing_styles']} ({stats['missing_styles']/stats['total_items']*100:.1f}%)")
    print(f"Items missing BOTH: {stats['missing_both']} ({stats['missing_both']/stats['total_items']*100:.1f}%)")
    print()
    
    # Print breakdown by type
    print("=" * 80)
    print("📋 BREAKDOWN BY ITEM TYPE")
    print("=" * 80)
    
    sorted_types = sorted(by_type.items(), key=lambda x: x[1]['missing_both'], reverse=True)
    
    for item_type, type_stats in sorted_types[:20]:  # Top 20 types
        if type_stats['total'] > 0:
            missing_pct = (type_stats['missing_both'] / type_stats['total']) * 100
            print(f"\n{item_type.upper()} ({type_stats['total']} items)")
            print(f"  Missing occasions: {type_stats['missing_occasions']}")
            print(f"  Missing styles: {type_stats['missing_styles']}")
            print(f"  Missing BOTH: {type_stats['missing_both']} ({missing_pct:.1f}%)")
    
    # Print business-suitable items missing metadata
    print("\n" + "=" * 80)
    print("🎯 BUSINESS-SUITABLE ITEMS MISSING METADATA")
    print("=" * 80)
    print(f"Found {len(potentially_fixable)} business-suitable items with missing metadata:\n")
    
    for item in potentially_fixable[:30]:  # Show first 30
        missing_str = " + ".join(item['missing'])
        print(f"❌ {item['name'][:60]}")
        print(f"   Type: {item['type']}")
        print(f"   Missing: {missing_str}")
        print(f"   Current occasions: {item['occasions']}")
        print(f"   Current styles: {item['styles']}")
        print()
    
    if len(potentially_fixable) > 30:
        print(f"... and {len(potentially_fixable) - 30} more items\n")
    
    # Save detailed report
    report = {
        'summary': stats,
        'by_type': {k: {
            'total': v['total'],
            'missing_occasions': v['missing_occasions'],
            'missing_styles': v['missing_styles'],
            'missing_both': v['missing_both']
        } for k, v in by_type.items()},
        'business_suitable_items': potentially_fixable
    }
    
    report_file = 'occasion_style_audit_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("=" * 80)
    print(f"✅ Detailed report saved to: {report_file}")
    print("=" * 80)
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print(f"1. {len(potentially_fixable)} business-suitable items need metadata fixes")
    print(f"2. Run backfill with enhanced type-based inference")
    print(f"3. Focus on these types: dress shirt, button up, jacket, dress pants, shoes")
    print(f"4. After backfill, semantic matching should improve significantly")
    print()

if __name__ == "__main__":
    audit_occasion_style_metadata()
