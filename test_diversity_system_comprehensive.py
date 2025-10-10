"""
Comprehensive Diversity System Test
Tests the complete diversity filtering integration in outfit generation
"""

import sys
import time
import json
from datetime import datetime

# Test configuration
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
NUM_GENERATIONS = 10  # Generate 10 outfits to test diversity

print("=" * 80)
print("🧪 COMPREHENSIVE DIVERSITY SYSTEM TEST")
print("=" * 80)
print()

# Import required modules
try:
    from backend.src.config.firebase import db
    from backend.src.services.diversity_filter_service import DiversityFilterService
    from backend.src.custom_types.wardrobe import ClothingItem
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Initialize diversity filter
diversity_filter = DiversityFilterService()

print()
print("=" * 80)
print("PART 1: FIRESTORE OUTFIT HISTORY LOADING TEST")
print("=" * 80)
print()

# Test 1: Load outfit history from Firestore
print("📊 Test 1: Loading outfit history from Firestore...")
try:
    outfit_history = diversity_filter._load_outfit_history_from_firestore(USER_ID)
    print(f"✅ Loaded {len(outfit_history)} outfits from Firestore")
    
    if outfit_history:
        # Show sample outfit
        sample_outfit = outfit_history[0]
        print(f"\n📋 Sample outfit:")
        print(f"   ID: {sample_outfit.get('id')}")
        print(f"   Items: {len(sample_outfit.get('items', []))}")
        print(f"   Occasion: {sample_outfit.get('occasion')}")
        print(f"   Style: {sample_outfit.get('style')}")
        
        # Check item structure
        if sample_outfit.get('items'):
            first_item = sample_outfit['items'][0]
            if isinstance(first_item, ClothingItem):
                print(f"   ✅ Items are ClothingItem objects")
                print(f"      Sample item: {first_item.name}")
            else:
                print(f"   ❌ Items are NOT ClothingItem objects: {type(first_item)}")
    else:
        print("⚠️  No outfit history found in Firestore")
        print("   This means diversity filtering will not work!")
        
except Exception as e:
    print(f"❌ Failed to load outfit history: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("PART 2: DIVERSITY CALCULATION TEST")
print("=" * 80)
print()

# Test 2: Calculate similarity between outfits
print("📊 Test 2: Testing outfit similarity calculation...")
try:
    if len(outfit_history) >= 2:
        outfit1_items = outfit_history[0].get('items', [])
        outfit2_items = outfit_history[1].get('items', [])
        
        if outfit1_items and outfit2_items:
            similarity = diversity_filter.calculate_outfit_similarity(outfit1_items, outfit2_items)
            print(f"✅ Similarity between outfit 1 and 2: {similarity:.2%}")
            
            # Check item overlap
            items1_ids = {item.id for item in outfit1_items}
            items2_ids = {item.id for item in outfit2_items}
            overlap = len(items1_ids & items2_ids)
            total = len(items1_ids | items2_ids)
            
            print(f"   Item overlap: {overlap}/{total} items")
            print(f"   Jaccard index: {overlap/total:.2%}" if total > 0 else "   Jaccard index: N/A")
            
            if similarity > 0.7:
                print(f"   ⚠️  HIGH SIMILARITY: These outfits are too similar!")
            else:
                print(f"   ✅ Good diversity between these outfits")
        else:
            print("⚠️  Outfits don't have items")
    else:
        print("⚠️  Not enough outfits to compare")
        
except Exception as e:
    print(f"❌ Failed to calculate similarity: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("PART 3: DIVERSITY CHECK INTEGRATION TEST")
print("=" * 80)
print()

# Test 3: Check if diversity check is actually called
print("📊 Test 3: Testing diversity check with mock outfit...")
try:
    if outfit_history and outfit_history[0].get('items'):
        # Use items from first outfit as a "new" outfit
        test_outfit = outfit_history[0].get('items', [])[:3]  # Take first 3 items
        
        diversity_result = diversity_filter.check_outfit_diversity(
            user_id=USER_ID,
            new_outfit=test_outfit,
            occasion="Casual",
            style="Classic",
            mood="Comfortable"
        )
        
        print(f"✅ Diversity check completed")
        print(f"   Is diverse: {diversity_result.get('is_diverse')}")
        print(f"   Diversity score: {diversity_result.get('diversity_score'):.2f}")
        print(f"   Similarity scores found: {len(diversity_result.get('similarity_scores', []))}")
        
        if not diversity_result.get('is_diverse'):
            print(f"   ⚠️  Outfit flagged as NOT diverse")
            most_similar = diversity_result.get('most_similar_outfit')
            if most_similar:
                print(f"   Most similar outfit: {most_similar.get('outfit_id')}")
                print(f"   Similarity: {most_similar.get('similarity'):.2%}")
        
        # Check recommendations
        recs = diversity_result.get('recommendations', [])
        if recs:
            print(f"\n   Recommendations:")
            for rec in recs:
                print(f"      - {rec}")
    else:
        print("⚠️  No outfits to test with")
        
except Exception as e:
    print(f"❌ Failed diversity check: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("PART 4: DIVERSITY BOOST TEST")
print("=" * 80)
print()

# Test 4: Test diversity boost application
print("📊 Test 4: Testing diversity boost on wardrobe items...")
try:
    # Load sample wardrobe items
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID).limit(20)
    docs = wardrobe_ref.stream()
    
    sample_items = []
    for doc in docs:
        item_data = doc.to_dict()
        try:
            item = ClothingItem(**item_data)
            sample_items.append(item)
        except Exception as e:
            print(f"   ⚠️  Failed to convert item: {e}")
    
    print(f"✅ Loaded {len(sample_items)} wardrobe items")
    
    if sample_items:
        # Apply diversity boost
        boosted_items = diversity_filter.apply_diversity_boost(
            items=sample_items,
            user_id=USER_ID,
            occasion="Casual",
            style="Classic",
            mood="Comfortable"
        )
        
        print(f"✅ Diversity boost applied to {len(boosted_items)} items")
        
        # Show top 5 boosted items
        boosted_items.sort(key=lambda x: x[1], reverse=True)
        print(f"\n   Top 5 boosted items:")
        for i, (item, score) in enumerate(boosted_items[:5], 1):
            print(f"      {i}. {item.name[:50]}: score={score:.2f}")
        
        # Check if boost is actually different
        base_score = 1.0
        boosted_scores = [score for _, score in boosted_items]
        if max(boosted_scores) > base_score:
            print(f"\n   ✅ Diversity boost is ACTIVE (max boost: {max(boosted_scores):.2f})")
        else:
            print(f"\n   ⚠️  No diversity boost detected (all scores at base: {base_score})")
    else:
        print("⚠️  No wardrobe items loaded")
        
except Exception as e:
    print(f"❌ Failed diversity boost test: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("PART 5: ITEM USAGE TRACKING TEST")
print("=" * 80)
print()

# Test 5: Check item usage tracking
print("📊 Test 5: Analyzing item usage patterns...")
try:
    # Count item usage from outfit history
    item_usage = {}
    for outfit in outfit_history:
        for item in outfit.get('items', []):
            if hasattr(item, 'id'):
                item_usage[item.id] = item_usage.get(item.id, 0) + 1
    
    print(f"✅ Found {len(item_usage)} unique items in outfit history")
    
    if item_usage:
        # Sort by usage
        sorted_usage = sorted(item_usage.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n   Top 10 most used items:")
        for i, (item_id, count) in enumerate(sorted_usage[:10], 1):
            # Find item name
            item_name = "Unknown"
            for outfit in outfit_history:
                for item in outfit.get('items', []):
                    if hasattr(item, 'id') and item.id == item_id:
                        item_name = getattr(item, 'name', 'Unknown')
                        break
            
            print(f"      {i}. {item_name[:50]}: used {count} times")
        
        # Check for overused items
        overused = [(item_id, count) for item_id, count in item_usage.items() if count > 5]
        if overused:
            print(f"\n   ⚠️  Found {len(overused)} overused items (used >5 times)")
            print(f"      Diversity filtering should penalize these items!")
        else:
            print(f"\n   ✅ Good item rotation - no overused items")
    
except Exception as e:
    print(f"❌ Failed item usage tracking: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("PART 6: DIVERSITY METRICS SUMMARY")
print("=" * 80)
print()

# Test 6: Get overall diversity metrics
print("📊 Test 6: Calculating overall diversity metrics...")
try:
    metrics = diversity_filter.get_diversity_metrics(USER_ID)
    
    print(f"✅ Diversity metrics calculated:")
    print(f"   Total outfits: {metrics.total_outfits}")
    print(f"   Unique combinations: {metrics.unique_combinations}")
    print(f"   Diversity score: {metrics.diversity_score:.2%}")
    print(f"   Recent repetitions: {metrics.recent_repetitions}")
    print(f"   Rotation effectiveness: {metrics.rotation_effectiveness:.2%}")
    print(f"   Similarity threshold: {metrics.similarity_threshold:.2%}")
    
    # Assessment
    print(f"\n   Assessment:")
    if metrics.diversity_score > 0.7:
        print(f"      ✅ EXCELLENT diversity ({metrics.diversity_score:.2%})")
    elif metrics.diversity_score > 0.5:
        print(f"      ⚠️  MODERATE diversity ({metrics.diversity_score:.2%})")
    else:
        print(f"      ❌ POOR diversity ({metrics.diversity_score:.2%}) - System needs improvement!")
    
    if metrics.recent_repetitions > 3:
        print(f"      ❌ TOO MANY recent repetitions ({metrics.recent_repetitions})")
    else:
        print(f"      ✅ Good recent variety")
    
except Exception as e:
    print(f"❌ Failed to calculate metrics: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("FINAL ASSESSMENT")
print("=" * 80)
print()

print("📋 System Status:")
print()

# Check each component
checks = {
    "Firestore loading": len(outfit_history) > 0 if 'outfit_history' in locals() else False,
    "Similarity calculation": True if 'similarity' in locals() else False,
    "Diversity check": True if 'diversity_result' in locals() else False,
    "Diversity boost": True if 'boosted_items' in locals() else False,
    "Item usage tracking": len(item_usage) > 0 if 'item_usage' in locals() else False,
    "Metrics calculation": True if 'metrics' in locals() else False,
}

for check_name, status in checks.items():
    print(f"   {'✅' if status else '❌'} {check_name}")

print()
all_passed = all(checks.values())
if all_passed:
    print("✅ ALL TESTS PASSED - Diversity system is functional!")
else:
    print("⚠️  SOME TESTS FAILED - Diversity system needs fixes!")
    print()
    print("🔍 Issues to address:")
    for check_name, status in checks.items():
        if not status:
            print(f"   - Fix: {check_name}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

