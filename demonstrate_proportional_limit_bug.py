#!/usr/bin/env python3
"""
Demonstrate how the proportional limit calculation can allow 2+ jackets.
"""

def calculate_proportional_limit(base_limit, total_base_limit, remaining_items_needed):
    """The exact formula from the code."""
    proportional_limit = max(
        base_limit,  # At least the base limit
        int((base_limit / total_base_limit) * remaining_items_needed * 1.5)  # Proportional scaling
    )
    return proportional_limit

print("🔍 Demonstrating Proportional Limit Bug")
print("="*80)
print("This shows how the formula can allow multiple jackets.\n")

# Scenario from the generated outfit (5 items total)
print("📊 SCENARIO: Business + Classic + Bold (5-item target)")
print("-"*80)

# Base limits for 5-item outfit
base_category_limits = {
    "tops": 1,
    "bottoms": 1,
    "shoes": 1,
    "outerwear": 1,
    "accessories": 1
}
total_base_limit = sum(base_category_limits.values())  # = 5

print(f"Base limits: {base_category_limits}")
print(f"Total base limit: {total_base_limit}\n")

# Simulate selection process
print("🔄 SELECTION PROCESS:")
print("-"*80)

selected_items = []
category_counts = {"tops": 0, "bottoms": 0, "shoes": 0, "outerwear": 0, "accessories": 0}

# Selection order (as might happen in reality)
selection_sequence = [
    ("Button-down shirt", "tops"),
    ("Dress pants", "bottoms"),
    ("Oxford shoes", "shoes"),
    ("Dark Teal Jacket", "outerwear"),  # FIRST jacket
    ("Charcoal Jacket", "outerwear"),   # SECOND jacket - WHY IS THIS ALLOWED?
]

for i, (item_name, category) in enumerate(selection_sequence):
    target_count = 5
    remaining_items_needed = target_count - len(selected_items)
    current_count = category_counts[category]
    base_limit = base_category_limits[category]
    
    # Calculate proportional limit
    proportional_limit = calculate_proportional_limit(
        base_limit, 
        total_base_limit, 
        remaining_items_needed
    )
    
    # Check if we can add this item
    can_add = current_count < proportional_limit
    
    print(f"\nStep {i+1}: Trying to add '{item_name}' ({category})")
    print(f"  Current progress: {len(selected_items)}/{target_count} items")
    print(f"  Remaining needed: {remaining_items_needed}")
    print(f"  Current {category} count: {current_count}")
    print(f"  Base limit for {category}: {base_limit}")
    print(f"  Proportional limit formula:")
    print(f"    max({base_limit}, int(({base_limit}/{total_base_limit}) * {remaining_items_needed} * 1.5))")
    print(f"    = max({base_limit}, int({base_limit/total_base_limit:.2f} * {remaining_items_needed} * 1.5))")
    print(f"    = max({base_limit}, int({(base_limit/total_base_limit) * remaining_items_needed * 1.5:.2f}))")
    print(f"    = max({base_limit}, {int((base_limit/total_base_limit) * remaining_items_needed * 1.5)})")
    print(f"    = {proportional_limit}")
    print(f"  Check: {current_count} < {proportional_limit}? {can_add}")
    
    if can_add:
        selected_items.append(item_name)
        category_counts[category] += 1
        print(f"  ✅ ADDED {item_name}")
    else:
        print(f"  ❌ REJECTED {item_name} (limit reached)")

print("\n" + "="*80)
print("📊 FINAL RESULT:")
print("="*80)
print(f"Total items: {len(selected_items)}")
print(f"Category counts: {category_counts}")
print(f"Outerwear items: {category_counts['outerwear']}")
print()

if category_counts['outerwear'] > 1:
    print("🐛 BUG CONFIRMED: Multiple jackets were allowed!")
    print("\n💡 ROOT CAUSE:")
    print("   The proportional_limit calculation uses a formula that can")
    print("   exceed the base_limit when remaining_items_needed is high.")
    print("   This allows 2+ items in categories that should only have 1.")
else:
    print("✅ No bug - only 1 jacket allowed")

print("\n" + "="*80)
print("🔧 RECOMMENDED FIX:")
print("="*80)
print("1. Add HARD LIMITS for critical categories (outerwear, tops, bottoms, shoes)")
print("2. Never allow proportional_limit to exceed base_limit for these categories")
print("3. OR: Add explicit check: 'if category == outerwear and current_count >= 1: skip'")
print("="*80)

