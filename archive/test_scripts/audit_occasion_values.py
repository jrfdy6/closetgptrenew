#!/usr/bin/env python3
"""
Audit what occasion/style VALUES are assigned to items.
Identifies items that SHOULD be business-suitable but are tagged with wrong occasions.
"""

import os
import json
from collections import defaultdict, Counter
import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore_client():
    """Initialize and return Firestore client."""
    if not firebase_admin._apps:
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    return firestore.client()

def audit_occasion_values(user_id: str = "dANqjiI0CKgaitxzYtw1bhtvQrG3"):
    """Audit what occasion values are assigned and identify misclassifications."""
    
    print("🔍 Auditing Occasion/Style VALUES...")
    print(f"👤 User ID: {user_id}\n")
    
    db = get_firestore_client()
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    items = list(wardrobe_ref.stream())
    
    print(f"📊 Total items: {len(items)}\n")
    
    # Track all occasions and styles
    all_occasions = Counter()
    all_styles = Counter()
    
    # Business-appropriate keywords
    business_occasions = ['business', 'formal', 'office', 'work', 'professional', 
                         'semi-formal', 'business casual', 'smart casual']
    casual_occasions = ['casual', 'beach', 'vacation', 'brunch', 'dinner', 'everyday',
                       'sport', 'sports', 'athletic', 'loungewear']
    
    # Item types that should typically be business-appropriate
    business_item_types = {
        'dress shirt': ['button up', 'dress shirt', 'oxford', 'formal shirt'],
        'dress pants': ['dress pants', 'trousers', 'slacks', 'suit pants'],
        'blazer/jacket': ['blazer', 'suit jacket', 'sport coat'],
        'dress shoes': ['oxford', 'derby', 'loafer', 'monk strap', 'dress shoe'],
        'accessories': ['tie', 'bow tie', 'pocket square', 'dress belt']
    }
    
    # Categorize items
    misclassified = []
    correctly_classified = []
    
    for doc in items:
        data = doc.to_dict()
        item_id = doc.id
        item_name = data.get('name', 'Unknown')
        item_type = data.get('type', '').lower()
        
        occasions = data.get('occasion', [])
        styles = data.get('style', [])
        
        if not isinstance(occasions, list):
            occasions = []
        if not isinstance(styles, list):
            styles = []
        
        # Count all occasions/styles
        for occ in occasions:
            all_occasions[occ.lower() if isinstance(occ, str) else str(occ)] += 1
        for sty in styles:
            all_styles[sty.lower() if isinstance(sty, str) else str(sty)] += 1
        
        # Determine if this item SHOULD be business-appropriate
        should_be_business = False
        business_category = None
        
        for category, keywords in business_item_types.items():
            if any(keyword in item_name.lower() or keyword in item_type for keyword in keywords):
                should_be_business = True
                business_category = category
                break
        
        if should_be_business:
            # Check if it has any business-appropriate occasions
            has_business_occasion = any(occ.lower() in business_occasions for occ in occasions if isinstance(occ, str))
            has_only_casual = all(occ.lower() in casual_occasions for occ in occasions if isinstance(occ, str)) and len(occasions) > 0
            
            item_info = {
                'id': item_id,
                'name': item_name[:70],
                'type': item_type,
                'category': business_category,
                'occasions': occasions,
                'styles': styles
            }
            
            if has_only_casual or not has_business_occasion:
                item_info['issue'] = 'Only casual occasions, missing business tags'
                misclassified.append(item_info)
            else:
                correctly_classified.append(item_info)
    
    # Print statistics
    print("=" * 90)
    print("📊 OCCASION DISTRIBUTION (All Items)")
    print("=" * 90)
    print(f"{'Occasion':<30} {'Count':>10}")
    print("-" * 90)
    for occ, count in all_occasions.most_common(20):
        print(f"{occ:<30} {count:>10}")
    
    print("\n" + "=" * 90)
    print("🎨 STYLE DISTRIBUTION (All Items)")
    print("=" * 90)
    print(f"{'Style':<30} {'Count':>10}")
    print("-" * 90)
    for sty, count in all_styles.most_common(20):
        print(f"{sty:<30} {count:>10}")
    
    # Business items analysis
    print("\n" + "=" * 90)
    print("🎯 BUSINESS-APPROPRIATE ITEMS ANALYSIS")
    print("=" * 90)
    total_business_items = len(misclassified) + len(correctly_classified)
    print(f"Total business-appropriate items: {total_business_items}")
    print(f"✅ Correctly tagged: {len(correctly_classified)} ({len(correctly_classified)/total_business_items*100:.1f}%)")
    print(f"❌ Misclassified (casual only): {len(misclassified)} ({len(misclassified)/total_business_items*100:.1f}%)")
    
    # Show misclassified items
    print("\n" + "=" * 90)
    print("❌ MISCLASSIFIED ITEMS (Should be business, tagged as casual)")
    print("=" * 90)
    
    # Group by category
    by_category = defaultdict(list)
    for item in misclassified:
        by_category[item['category']].append(item)
    
    for category, items in sorted(by_category.items()):
        print(f"\n📁 {category.upper()} ({len(items)} items)")
        print("-" * 90)
        for item in items[:10]:  # Show first 10 per category
            print(f"  • {item['name']}")
            print(f"    Occasions: {', '.join(item['occasions'][:5])}")
            if len(item['occasions']) > 5:
                print(f"    ... +{len(item['occasions'])-5} more")
            print()
        if len(items) > 10:
            print(f"  ... and {len(items)-10} more {category} items\n")
    
    # Save report
    report = {
        'summary': {
            'total_items': len(items),
            'total_business_items': total_business_items,
            'correctly_classified': len(correctly_classified),
            'misclassified': len(misclassified)
        },
        'occasion_distribution': dict(all_occasions),
        'style_distribution': dict(all_styles),
        'misclassified_items': misclassified
    }
    
    with open('occasion_values_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("=" * 90)
    print("✅ Detailed report saved to: occasion_values_audit_report.json")
    print("=" * 90)
    
    # Recommendations
    print("\n" + "=" * 90)
    print("💡 KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 90)
    print(f"1. {len(misclassified)} business-appropriate items are ONLY tagged with casual occasions")
    print(f"2. These items need to be re-tagged with: business, formal, office, work, etc.")
    print(f"3. The AI metadata extraction may be too casual-biased")
    print(f"4. Recommendation: Update backfill script to add business occasions based on item type")
    print()

if __name__ == "__main__":
    audit_occasion_values()

