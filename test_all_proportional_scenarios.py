#!/usr/bin/env python3
"""
Test all scenarios where proportional limit might allow 2+ jackets.
"""

def calculate_proportional_limit(base_limit, total_base_limit, remaining_items_needed):
    """The exact formula from the code."""
    proportional_limit = max(
        base_limit,
        int((base_limit / total_base_limit) * remaining_items_needed * 1.5)
    )
    return proportional_limit

print("🔍 Testing All Proportional Limit Scenarios")
print("="*80)
print("Finding scenarios where 2+ jackets could be selected.\n")

# Test different target counts
for target_count in range(3, 9):
    print(f"\n{'='*80}")
    print(f"TARGET COUNT: {target_count} items")
    print(f"{'='*80}")
    
    # Determine base limits based on target count
    if target_count <= 3:
        base_limits = {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1}
    elif target_count == 4:
        base_limits = {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1}
    elif target_count == 5:
        base_limits = {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1, "accessories": 1}
    elif target_count >= 6:
        base_limits = {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1, "accessories": 2, "sweater": 1}
    
    total_base_limit = sum(base_limits.values())
    outerwear_base_limit = base_limits.get("outerwear", 0)
    
    print(f"Base limits: {base_limits}")
    print(f"Total base limit: {total_base_limit}")
    print(f"Outerwear base limit: {outerwear_base_limit}\n")
    
    # Simulate at different points in selection
    bug_found = False
    
    for items_selected in range(0, target_count + 1):
        remaining = target_count - items_selected
        
        # Assume we already have 1 jacket
        current_outerwear_count = 1
        
        # Calculate what the limit would be for the SECOND jacket
        proportional_limit = calculate_proportional_limit(
            outerwear_base_limit,
            total_base_limit,
            remaining
        )
        
        # Would a second jacket be allowed?
        would_allow_second = current_outerwear_count < proportional_limit
        
        if would_allow_second:
            print(f"  ⚠️  At {items_selected}/{target_count} items selected:")
            print(f"      Remaining needed: {remaining}")
            print(f"      Formula: max({outerwear_base_limit}, int(({outerwear_base_limit}/{total_base_limit}) * {remaining} * 1.5))")
            print(f"      = max({outerwear_base_limit}, {int((outerwear_base_limit/total_base_limit) * remaining * 1.5)})")
            print(f"      = {proportional_limit}")
            print(f"      Current outerwear: {current_outerwear_count}")
            print(f"      Check: {current_outerwear_count} < {proportional_limit}? TRUE")
            print(f"      🐛 BUG: SECOND JACKET WOULD BE ALLOWED!")
            bug_found = True
    
    if not bug_found:
        print(f"  ✅ No bug scenario found for target={target_count}")

print("\n" + "="*80)
print("🎯 ALTERNATIVE BUG HYPOTHESIS")
print("="*80)
print("\nIf the formula doesn't allow 2 jackets, the bug might be:")
print("1. Jackets are NOT being categorized as 'outerwear'")
print("2. One jacket is categorized as 'outerwear', the other as something else")
print("3. The category_counts dict is not being tracked properly")
print("4. There's a different code path that bypasses this check")
print("\nLet's check what category jackets are actually assigned...")

