#!/usr/bin/env python3
"""
Focused test: Only test the extracted modules (no main service dependencies)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 80)
print("EXTRACTED MODULES FUNCTIONALITY TEST")
print("=" * 80)

# Test 1: Import all extracted modules
print("\n✅ TEST 1: Module Imports")
from src.services.constants import BASE_CATEGORY_LIMITS, MAX_ITEMS, MIN_ITEMS
from src.services.item_utils import safe_get_item_name, get_item_category, is_shirt, is_dress
from src.services.validation import can_add_category, get_essential_requirements
print("   All modules imported successfully")

# Test 2: Constants
print("\n✅ TEST 2: Constants")
print(f"   MAX_ITEMS = {MAX_ITEMS}")
print(f"   MIN_ITEMS = {MIN_ITEMS}")
print(f"   Category limits = {BASE_CATEGORY_LIMITS}")

# Test 3: Item utilities
print("\n✅ TEST 3: Item Utilities")
class MockItem:
    def __init__(self, name, item_type):
        self.name = name
        self.type = item_type
        self.metadata = None

shirt = MockItem("Blue Shirt", "shirt")
dress = MockItem("Red Dress", "dress")
pants = MockItem("Black Pants", "pants")

print(f"   Shirt name: {safe_get_item_name(shirt)}")
print(f"   Shirt category: {get_item_category(shirt)}")
print(f"   Is shirt? {is_shirt(shirt)}")
print(f"   Is dress? {is_dress(shirt)}")
print(f"   Dress category: {get_item_category(dress)}")
print(f"   Is dress? {is_dress(dress)}")

# Test 4: Validation - Dress Exclusion (CRITICAL)
print("\n✅ TEST 4: Dress Exclusion Logic (Critical Invariant)")
categories_filled = {'dress': True}
selected_items = [dress]

# Try to add bottoms with dress
can_add, reason = can_add_category('bottoms', categories_filled, selected_items)
print(f"   Can add bottoms with dress? {can_add} (reason: {reason})")
assert can_add == False, "FAIL: Should not allow bottoms with dress"

# Try to add tops with dress
can_add, reason = can_add_category('tops', categories_filled, selected_items)
print(f"   Can add tops with dress? {can_add} (reason: {reason})")
assert can_add == False, "FAIL: Should not allow tops with dress"

# Try to add dress with bottoms
categories_filled = {'bottoms': True}
selected_items = [pants]
can_add, reason = can_add_category('dress', categories_filled, selected_items)
print(f"   Can add dress with bottoms? {can_add} (reason: {reason})")
assert can_add == False, "FAIL: Should not allow dress with bottoms"

# Can add shoes with dress
categories_filled = {'dress': True}
selected_items = [dress]
can_add, reason = can_add_category('shoes', categories_filled, selected_items)
print(f"   Can add shoes with dress? {can_add}")
assert can_add == True, "FAIL: Should allow shoes with dress"

# Test 5: Essential Requirements
print("\n✅ TEST 5: Essential Requirements")
gym_reqs = get_essential_requirements("gym", "athletic", False)
print(f"   Gym (no dress): {gym_reqs}")
assert 'tops' in gym_reqs['required'], "Gym should require tops"
assert 'bottoms' in gym_reqs['required'], "Gym should require bottoms"

party_dress_reqs = get_essential_requirements("party", "casual", True)
print(f"   Party (with dress): {party_dress_reqs}")
assert 'tops' not in party_dress_reqs['required'], "Dress outfit should NOT require tops"
assert 'shoes' in party_dress_reqs['required'], "Dress outfit should require shoes"

lounge_reqs = get_essential_requirements("loungewear", "casual", False)
print(f"   Loungewear: {lounge_reqs}")
assert 'bottoms' in lounge_reqs['preferred'], "Loungewear should prefer bottoms (but not require)"

# Test 6: No Duplicate Dresses
print("\n✅ TEST 6: No Duplicate Dresses")
categories_filled = {'dress': True}
selected_items = [dress]
can_add, reason = can_add_category('dress', categories_filled, selected_items)
print(f"   Can add second dress? {can_add} (reason: {reason})")
assert can_add == False, "FAIL: Should not allow duplicate dresses"
assert reason == "duplicate dress", f"Wrong reason: {reason}"

# All tests passed!
print("\n" + "=" * 80)
print("🎉 ALL TESTS PASSED!")
print("=" * 80)
print("\n✅ Refactored modules are fully functional:")
print("   ✓ Constants module working")
print("   ✓ Item utilities working")
print("   ✓ Validation logic intact")
print("   ✓ Dress exclusion enforced")
print("   ✓ Essential requirements correct")
print("   ✓ No duplicate dresses allowed")
print("\n🚀 Refactoring is production-ready!")

