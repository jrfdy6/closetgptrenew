#!/usr/bin/env python3
"""
Test script to verify refactoring didn't break functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 80)
print("REFACTORING FUNCTIONALITY TEST")
print("=" * 80)

# Test 1: Import all extracted modules
print("\n1️⃣ Testing module imports...")
try:
    from src.services.constants import (
        BASE_CATEGORY_LIMITS,
        MAX_ITEMS,
        MIN_ITEMS,
        INAPPROPRIATE_COMBINATIONS,
        STYLE_COMPATIBILITY,
    )
    print("   ✅ constants module imported")
    
    from src.services.item_utils import (
        safe_get_item_name,
        safe_get_item_type,
        get_item_category,
        is_shirt,
        is_dress,
        get_item_formality_level,
    )
    print("   ✅ item_utils module imported")
    
    from src.services.validation import (
        can_add_category,
        get_essential_requirements,
        deduplicate_items,
    )
    print("   ✅ validation module imported")
    
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test constants
print("\n2️⃣ Testing constants...")
try:
    assert MAX_ITEMS == 8, "MAX_ITEMS should be 8"
    assert MIN_ITEMS == 3, "MIN_ITEMS should be 3"
    assert 'tops' in BASE_CATEGORY_LIMITS, "BASE_CATEGORY_LIMITS should have 'tops'"
    assert BASE_CATEGORY_LIMITS['tops'] == 2, "tops limit should be 2"
    print(f"   ✅ MAX_ITEMS = {MAX_ITEMS}")
    print(f"   ✅ MIN_ITEMS = {MIN_ITEMS}")
    print(f"   ✅ BASE_CATEGORY_LIMITS = {BASE_CATEGORY_LIMITS}")
except AssertionError as e:
    print(f"   ❌ Constant test failed: {e}")
    sys.exit(1)

# Test 3: Test item_utils functions
print("\n3️⃣ Testing item_utils functions...")
try:
    # Create mock item
    class MockItem:
        def __init__(self):
            self.name = "Test Shirt"
            self.type = "shirt"
            self.metadata = None
    
    item = MockItem()
    
    # Test safe accessors
    name = safe_get_item_name(item)
    assert name == "Test Shirt", f"Expected 'Test Shirt', got '{name}'"
    print(f"   ✅ safe_get_item_name() = '{name}'")
    
    item_type = safe_get_item_type(item)
    assert item_type == "shirt", f"Expected 'shirt', got '{item_type}'"
    print(f"   ✅ safe_get_item_type() = '{item_type}'")
    
    # Test category detection
    category = get_item_category(item)
    assert category == "tops", f"Expected 'tops', got '{category}'"
    print(f"   ✅ get_item_category() = '{category}'")
    
    # Test type checkers
    is_shirt_result = is_shirt(item)
    assert is_shirt_result == True, f"Expected True, got {is_shirt_result}"
    print(f"   ✅ is_shirt() = {is_shirt_result}")
    
    is_dress_result = is_dress(item)
    assert is_dress_result == False, f"Expected False, got {is_dress_result}"
    print(f"   ✅ is_dress() = {is_dress_result}")
    
except Exception as e:
    print(f"   ❌ item_utils test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test validation functions
print("\n4️⃣ Testing validation functions...")
try:
    # Test can_add_category (canonical invariant gate)
    categories_filled = {}
    selected_items = []
    
    # Test 1: Can add tops to empty outfit
    can_add, reason = can_add_category('tops', categories_filled, selected_items)
    assert can_add == True, f"Should be able to add tops to empty outfit"
    print(f"   ✅ can_add_category('tops', empty) = {can_add}")
    
    # Test 2: Cannot add dress if bottoms exist
    categories_filled = {'bottoms': True}
    can_add, reason = can_add_category('dress', categories_filled, selected_items)
    assert can_add == False, f"Should NOT be able to add dress when bottoms exist"
    assert reason == "bottoms already exist", f"Expected 'bottoms already exist', got '{reason}'"
    print(f"   ✅ can_add_category('dress', with_bottoms) = {can_add} (reason: {reason})")
    
    # Test 3: Cannot add bottoms if dress exists
    categories_filled = {'dress': True}
    can_add, reason = can_add_category('bottoms', categories_filled, selected_items)
    assert can_add == False, f"Should NOT be able to add bottoms when dress exists"
    assert reason == "dress already exists", f"Expected 'dress already exists', got '{reason}'"
    print(f"   ✅ can_add_category('bottoms', with_dress) = {can_add} (reason: {reason})")
    
    # Test get_essential_requirements
    reqs = get_essential_requirements("gym", "athletic", False)
    assert 'required' in reqs, "Requirements should have 'required' key"
    assert 'tops' in reqs['required'], "Gym should require tops"
    assert 'bottoms' in reqs['required'], "Gym should require bottoms"
    assert 'shoes' in reqs['required'], "Gym should require shoes"
    print(f"   ✅ get_essential_requirements('gym') = {reqs}")
    
    # Test with dress
    reqs_dress = get_essential_requirements("party", "casual", True)
    assert 'shoes' in reqs_dress['required'], "Dress outfit should require shoes"
    assert 'tops' not in reqs_dress['required'], "Dress outfit should NOT require tops"
    print(f"   ✅ get_essential_requirements('party', has_dress=True) = {reqs_dress}")
    
except Exception as e:
    print(f"   ❌ Validation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test that main service can still import
print("\n5️⃣ Testing main service import...")
try:
    from src.services.robust_outfit_generation_service import RobustOutfitGenerationService
    print("   ✅ RobustOutfitGenerationService imported successfully")
    
    # Try to instantiate (this will test that all dependencies are resolved)
    service = RobustOutfitGenerationService()
    print("   ✅ RobustOutfitGenerationService instantiated successfully")
    
    # Check that service has the expected attributes
    assert hasattr(service, 'tier_system'), "Service should have tier_system"
    assert hasattr(service, 'occasion_filters'), "Service should have occasion_filters"
    print("   ✅ Service has tier_system and occasion_filters")
    
except Exception as e:
    print(f"   ❌ Main service test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test dress exclusion logic (critical invariant)
print("\n6️⃣ Testing dress exclusion logic...")
try:
    # Create mock items
    class MockDress:
        def __init__(self):
            self.name = "Test Dress"
            self.type = "dress"
            self.metadata = None
    
    class MockPants:
        def __init__(self):
            self.name = "Test Pants"
            self.type = "pants"
            self.metadata = None
    
    dress = MockDress()
    pants = MockPants()
    
    # Test that dress is detected
    assert is_dress(dress) == True, "Dress should be detected"
    assert get_item_category(dress) == "dress", "Dress category should be 'dress'"
    print("   ✅ Dress detection working")
    
    # Test that pants cannot be added with dress
    categories_filled = {'dress': True}
    selected_items = [dress]
    can_add, reason = can_add_category('bottoms', categories_filled, selected_items)
    assert can_add == False, "Should NOT be able to add pants with dress"
    print(f"   ✅ Dress exclusion working: {reason}")
    
    # Test that dress cannot be added with pants
    categories_filled = {'bottoms': True}
    selected_items = [pants]
    can_add, reason = can_add_category('dress', categories_filled, selected_items)
    assert can_add == False, "Should NOT be able to add dress with pants"
    print(f"   ✅ Bidirectional exclusion working: {reason}")
    
except Exception as e:
    print(f"   ❌ Dress exclusion test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# All tests passed!
print("\n" + "=" * 80)
print("🎉 ALL TESTS PASSED! Refactoring is functionally correct.")
print("=" * 80)
print("\n✅ Summary:")
print("   - All modules import correctly")
print("   - Constants are correct")
print("   - Item utilities work as expected")
print("   - Validation logic is intact")
print("   - Main service can be instantiated")
print("   - Dress exclusion invariants are enforced")
print("\n🚀 Ready for deployment!")

