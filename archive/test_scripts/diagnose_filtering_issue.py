"""
Diagnose Filtering Issue - Check what items pass for specific combinations
"""

import sys
from collections import defaultdict

USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

# Test combinations that user reports as repetitive
TEST_COMBINATIONS = [
    ("Casual", "Classic", "Comfortable"),
    ("Athletic", "Sporty", "Energetic"),
    ("Business", "Professional", "Confident"),
]

print("=" * 80)
print("🔍 FILTERING DIAGNOSTIC TOOL")
print("=" * 80)
print()

try:
    from backend.src.config.firebase import db
    from backend.src.custom_types.wardrobe import ClothingItem
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()
print("📊 Loading wardrobe from Firestore...")
try:
    docs = db.collection('wardrobe').where('userId', '==', USER_ID).stream()
    wardrobe_items = []
    
    for doc in docs:
        item_data = doc.to_dict()
        wardrobe_items.append(item_data)
    
    print(f"✅ Loaded {len(wardrobe_items)} wardrobe items")
except Exception as e:
    print(f"❌ Failed to load wardrobe: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("TESTING EACH COMBINATION")
print("=" * 80)

for occasion, style, mood in TEST_COMBINATIONS:
    print()
    print(f"🎯 Testing: {occasion} / {style} / {mood}")
    print("-" * 80)
    
    passed_items = []
    rejected_items = []
    
    for item in wardrobe_items:
        # Get normalized metadata (prioritize normalized fields)
        metadata = item.get('metadata', {})
        normalized = metadata.get('normalized', {})
        
        # Get occasion, style, mood from normalized or fallback to raw
        if normalized:
            item_occasions = normalized.get('occasion', [])
            item_styles = normalized.get('style', [])
            item_moods = normalized.get('mood', [])
        else:
            item_occasions = item.get('occasion', [])
            item_styles = item.get('style', [])
            item_moods = item.get('mood', [])
        
        # Ensure lists and lowercase
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions.lower()]
        else:
            item_occasions = [str(o).lower() for o in item_occasions]
        
        if isinstance(item_styles, str):
            item_styles = [item_styles.lower()]
        else:
            item_styles = [str(s).lower() for s in item_styles]
        
        if isinstance(item_moods, str):
            item_moods = [item_moods.lower()]
        else:
            item_moods = [str(m).lower() for m in item_moods]
        
        # Check filters
        context_occasion = occasion.lower()
        context_style = style.lower()
        context_mood = mood.lower()
        
        ok_occ = any(s == context_occasion for s in item_occasions)
        ok_style = any(s == context_style for s in item_styles)
        ok_mood = len(item_moods) == 0 or any(m == context_mood for m in item_moods)
        
        # STRICT FILTERING: Requires occasion AND style
        if ok_occ and ok_style:
            passed_items.append({
                'name': item.get('name', 'Unknown'),
                'type': item.get('type', 'unknown'),
                'occasions': item_occasions,
                'styles': item_styles,
                'moods': item_moods
            })
        else:
            reasons = []
            if not ok_occ:
                reasons.append(f"occasion (has: {item_occasions})")
            if not ok_style:
                reasons.append(f"style (has: {item_styles})")
            
            rejected_items.append({
                'name': item.get('name', 'Unknown'),
                'type': item.get('type', 'unknown'),
                'reasons': reasons
            })
    
    # Summary
    print(f"\n   ✅ PASSED: {len(passed_items)} items")
    print(f"   ❌ REJECTED: {len(rejected_items)} items")
    
    # Show passed items by type
    if passed_items:
        types_count = defaultdict(int)
        for item in passed_items:
            types_count[item['type']] += 1
        
        print(f"\n   📦 Passed items by type:")
        for item_type, count in sorted(types_count.items()):
            print(f"      {item_type}: {count}")
        
        # Show first 5 passed items
        print(f"\n   📋 Sample passed items:")
        for i, item in enumerate(passed_items[:5], 1):
            print(f"      {i}. {item['name'][:50]} ({item['type']})")
    else:
        print(f"\n   ⚠️  NO ITEMS PASSED! This combination will fail!")
    
    # Show why items were rejected (top reasons)
    if rejected_items:
        all_reasons = []
        for item in rejected_items:
            all_reasons.extend(item['reasons'])
        
        reason_counts = defaultdict(int)
        for reason in all_reasons:
            reason_counts[reason] += 1
        
        print(f"\n   📊 Top rejection reasons:")
        for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {count} items: {reason}")

print()
print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print()
print("💡 RECOMMENDATIONS:")
print()
print("If any combination has <10 passed items:")
print("   → Filtering is TOO STRICT")
print("   → You'll see the same outfits repeatedly")
print("   → Solution: Relax filtering OR add more metadata to items")
print()
print("If passed items are always the same:")
print("   → Diversity boost needs stronger penalty for repeated items")
print("   → Check Railway logs for diversity scores")

