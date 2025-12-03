#!/usr/bin/env python3
"""
Test the impact of semantic expansion on outfit filtering.
Compares traditional (exact match) vs semantic (expanded) filtering.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

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

def load_wardrobe(user_id: str = "dANqjiI0CKgaitxzYtw1bhtvQrG3"):
    """Load user's wardrobe items."""
    db = get_firestore_client()
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    items = []
    for doc in wardrobe_ref.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        items.append(data)
    return items

def traditional_occasion_match(requested: str, item_occasions: list) -> bool:
    """Traditional exact match filtering."""
    if not requested:
        return True
    if not item_occasions:
        return False
    ro = requested.lower().replace(' ', '_')
    return ro in [o.lower().replace(' ', '_') for o in item_occasions]

def semantic_occasion_match(requested: str, item_occasions: list) -> bool:
    """Semantic expanded filtering."""
    if not requested:
        return True
    if not item_occasions:
        return False
    
    ro = requested.lower().replace(' ', '_')
    normalized_items = [o.lower().replace(' ', '_') for o in item_occasions]
    
    # Direct match
    if ro in normalized_items:
        return True
    
    # Semantic fallbacks
    FALLBACKS = {
        'business': ['business', 'business_casual', 'formal', 'work', 'office', 
                    'smart_casual', 'brunch', 'dinner', 'date', 'conference', 
                    'interview', 'meeting', 'semi-formal', 'semi_formal'],
        'casual': ['casual', 'everyday', 'weekend', 'relaxed', 'brunch', 
                  'dinner', 'lunch', 'date', 'travel', 'vacation'],
        'formal': ['formal', 'wedding', 'gala', 'business', 'cocktail', 
                  'evening', 'ceremony', 'semi-formal', 'semi_formal'],
        'beach': ['beach', 'vacation', 'resort', 'tropical', 'casual', 
                 'outdoor', 'summer'],
    }
    
    fallback = set(FALLBACKS.get(ro, []))
    return any(o in fallback for o in normalized_items)

def test_filtering(items, occasion, mode='traditional'):
    """Test filtering with given mode."""
    passed = []
    rejected = []
    
    for item in items:
        occasions = item.get('occasion', [])
        if not isinstance(occasions, list):
            occasions = []
        
        if mode == 'traditional':
            matches = traditional_occasion_match(occasion, occasions)
        else:
            matches = semantic_occasion_match(occasion, occasions)
        
        if matches:
            passed.append(item)
        else:
            rejected.append(item)
    
    return passed, rejected

def analyze_differences(traditional_passed, semantic_passed, all_items):
    """Analyze what items became available with semantic matching."""
    trad_ids = {item['id'] for item in traditional_passed}
    sem_ids = {item['id'] for item in semantic_passed}
    
    newly_accepted = sem_ids - trad_ids
    newly_accepted_items = [item for item in all_items if item['id'] in newly_accepted]
    
    return newly_accepted_items

def run_comparison(user_id: str = "dANqjiI0CKgaitxzYtw1bhtvQrG3"):
    """Run comprehensive comparison."""
    print("🔍 Loading wardrobe...")
    items = load_wardrobe(user_id)
    print(f"✅ Loaded {len(items)} items\n")
    
    # Test scenarios
    scenarios = [
        ("Business", "business"),
        ("Casual", "casual"),
        ("Formal", "formal"),
        ("Beach", "beach"),
    ]
    
    results = {}
    
    for scenario_name, occasion in scenarios:
        print("=" * 80)
        print(f"📊 Testing: {scenario_name.upper()}")
        print("=" * 80)
        
        # Traditional filtering
        trad_passed, trad_rejected = test_filtering(items, occasion, 'traditional')
        trad_pass_rate = (len(trad_passed) / len(items)) * 100
        
        # Semantic filtering
        sem_passed, sem_rejected = test_filtering(items, occasion, 'semantic')
        sem_pass_rate = (len(sem_passed) / len(items)) * 100
        
        # Improvement
        improvement = sem_pass_rate - trad_pass_rate
        newly_accepted = analyze_differences(trad_passed, sem_passed, items)
        
        print(f"\n📈 Traditional (Exact Match):")
        print(f"   Passed: {len(trad_passed)}/{len(items)} ({trad_pass_rate:.1f}%)")
        
        print(f"\n📈 Semantic (Expanded):")
        print(f"   Passed: {len(sem_passed)}/{len(items)} ({sem_pass_rate:.1f}%)")
        
        print(f"\n💡 Improvement:")
        print(f"   +{len(newly_accepted)} items ({improvement:+.1f}% pass rate)")
        
        # Show examples of newly accepted items
        if newly_accepted:
            print(f"\n🎯 Examples of newly accepted items:")
            for item in newly_accepted[:5]:
                name = item.get('name', 'Unknown')[:60]
                occasions = item.get('occasion', [])
                print(f"   ✅ {name}")
                print(f"      Occasions: {', '.join(occasions[:5])}")
        
        print()
        
        results[scenario_name] = {
            'total_items': len(items),
            'traditional': {
                'passed': len(trad_passed),
                'pass_rate': trad_pass_rate
            },
            'semantic': {
                'passed': len(sem_passed),
                'pass_rate': sem_pass_rate
            },
            'improvement': {
                'additional_items': len(newly_accepted),
                'pass_rate_increase': improvement
            }
        }
    
    # Summary
    print("=" * 80)
    print("📊 OVERALL SUMMARY")
    print("=" * 80)
    
    total_improvement = sum(r['improvement']['pass_rate_increase'] for r in results.values()) / len(results)
    
    print(f"\nAverage pass rate improvement: {total_improvement:+.1f}%")
    print(f"\nDetailed Results:")
    
    for scenario, data in results.items():
        print(f"\n{scenario}:")
        print(f"  Traditional: {data['traditional']['pass_rate']:.1f}%")
        print(f"  Semantic:    {data['semantic']['pass_rate']:.1f}%")
        print(f"  Improvement: {data['improvement']['pass_rate_increase']:+.1f}% (+{data['improvement']['additional_items']} items)")
    
    # Save results
    with open('semantic_comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ Results saved to: semantic_comparison_results.json")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    print("🚀 Semantic Expansion Impact Test")
    print("=" * 80)
    print("This script compares traditional vs semantic filtering")
    print("to quantify the improvement from semantic expansion.\n")
    
    try:
        results = run_comparison()
        print("\n🎉 Test complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

