#!/usr/bin/env python3
"""
Test script for the upgraded duplicate fixing strategy with dynamic healing context.

This script tests:
1. Duplicate detection and logging
2. Dynamic exclusions from healing context
3. Fix tracking and success/failure logging
4. Integration with the overall fallback system
"""

import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_fallback_service import OutfitFallbackService
from src.services.dynamic_healing_context import DynamicHealingContext, ErrorType, FixType
from src.types.wardrobe import ClothingItem

class MockClothingItem:
    """Mock clothing item for testing."""
    def __init__(self, id: str, name: str, type: str, category: str, userId: str, **kwargs):
        self.id = id
        self.name = name
        self.type = type
        self.category = category
        self.userId = userId
        self.material = kwargs.get('material', 'cotton')
        self.color = kwargs.get('color', 'blue')
        self.style = kwargs.get('style', ['casual'])
        self.occasion = kwargs.get('occasion', ['casual'])
        self.quality_score = kwargs.get('quality_score', 7.0)
        self.pairability_score = kwargs.get('pairability_score', 7.0)
        self.seasonality = kwargs.get('seasonality', ['spring', 'summer', 'fall', 'winter'])
        self.metadata = kwargs.get('metadata', {})
        
        # Add all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

async def test_duplicate_fixing_strategy():
    """Test the upgraded duplicate fixing strategy."""
    print("🧪 Testing Duplicate Fixing Strategy with Dynamic Healing Context")
    print("=" * 70)
    
    # Create test items with duplicates
    test_items = [
        MockClothingItem(
            id="pants1", name="Blue Jeans", type="pants", category="bottom", 
            userId="test_user", material="denim", quality_score=8.0
        ),
        MockClothingItem(
            id="pants2", name="Black Pants", type="pants", category="bottom", 
            userId="test_user", material="cotton", quality_score=7.5
        ),
        MockClothingItem(
            id="shirt1", name="White T-Shirt", type="shirt", category="top", 
            userId="test_user", material="cotton", quality_score=7.0
        ),
        MockClothingItem(
            id="shoes1", name="Sneakers", type="shoes", category="shoes", 
            userId="test_user", material="canvas", quality_score=8.5
        )
    ]
    
    # Create replacement items for the duplicate pants
    replacement_items = [
        MockClothingItem(
            id="shorts1", name="Khaki Shorts", type="shorts", category="bottom", 
            userId="test_user", material="cotton", quality_score=7.0
        ),
        MockClothingItem(
            id="skirt1", name="Denim Skirt", type="skirt", category="bottom", 
            userId="test_user", material="denim", quality_score=7.5
        )
    ]
    
    # Create context
    context = {
        'user_profile': {'id': 'test_user'},
        'occasion': 'casual',
        'weather': {'temperature_f': 75, 'condition': 'sunny'},
        'style_preferences': ['casual', 'comfortable']
    }
    
    # Create healing context
    healing_context = DynamicHealingContext(context)
    
    # Create fallback service
    fallback_service = OutfitFallbackService()
    
    # Mock the wardrobe collection
    mock_collection = Mock()
    fallback_service.wardrobe_collection = mock_collection
    
    # Mock the _find_alternatives_for_category method to return our replacement items
    async def mock_find_alternatives(category, exclude_item, context, healing_context):
        if category == "bottom":
            return replacement_items
        return []
    
    fallback_service._find_alternatives_for_category = mock_find_alternatives
    
    print("📋 Test Setup:")
    print(f"   - Original items: {[item.name for item in test_items]}")
    print(f"   - Duplicate category: bottom (2 pants)")
    print(f"   - Replacement items: {[item.name for item in replacement_items]}")
    print()
    
    # Test the duplicate fixing strategy
    print("🔧 Running Duplicate Fix Strategy...")
    fixed_items, fixes_applied = await fallback_service._fix_duplicate_items(
        test_items, context, healing_context
    )
    
    print("\n📊 Results:")
    print(f"   - Fixed items: {[item.name for item in fixed_items]}")
    print(f"   - Fixes applied: {len(fixes_applied)}")
    
    for fix in fixes_applied:
        print(f"   - Fix type: {fix['type']}")
        print(f"   - Category: {fix['category']}")
        print(f"   - Kept item: {fix['kept_item']}")
        print(f"   - Replaced items: {fix['replaced_items']}")
        print(f"   - Replacement items: {fix['replacement_items']}")
    
    print("\n🔍 Healing Context State:")
    print(f"   - Errors seen: {len(healing_context.errors_seen)}")
    print(f"   - Items removed: {len(healing_context.items_removed)}")
    print(f"   - Rules triggered: {len(healing_context.rules_triggered)}")
    print(f"   - Fixes attempted: {len(healing_context.fixes_attempted)}")
    
    # Print detailed healing context information
    print("\n📝 Detailed Healing Context:")
    
    for error in healing_context.errors_seen:
        print(f"   Error: {error.error_type.value} - {error.details}")
        print(f"     Pass: {error.pass_number}, Items: {error.item_ids}")
    
    for rule_name, triggers in healing_context.rules_triggered.items():
        for trigger in triggers:
            print(f"   Rule: {rule_name} - {trigger.reason}")
            print(f"     Pass: {trigger.pass_number}, Context: {trigger.context}")
    
    for fix in healing_context.fixes_attempted:
        print(f"   Fix: {fix.fix_type.value} - {'Success' if fix.success else 'Failed'}")
        print(f"     Pass: {fix.pass_number}, Details: {fix.details}")
    
    # Validation checks
    print("\n✅ Validation Checks:")
    
    # Check 1: Duplicate was detected and logged
    duplicate_errors = [e for e in healing_context.errors_seen if e.error_type == ErrorType.DUPLICATE_ITEMS]
    assert len(duplicate_errors) > 0, "❌ Duplicate error should be logged"
    print("   ✅ Duplicate error logged")
    
    # Check 2: Rule was triggered
    assert 'duplicate_detection' in healing_context.rules_triggered, "❌ Duplicate detection rule should be triggered"
    print("   ✅ Duplicate detection rule triggered")
    
    # Check 3: Items were removed from context
    assert len(healing_context.items_removed) > 0, "❌ Items should be removed from healing context"
    print("   ✅ Items removed from healing context")
    
    # Check 4: Fix was attempted and logged
    duplicate_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.DUPLICATE_FIX]
    assert len(duplicate_fixes) > 0, "❌ Duplicate fix should be attempted"
    print("   ✅ Duplicate fix attempted and logged")
    
    # Check 5: No duplicates in final outfit
    categories = {}
    for item in fixed_items:
        category = item.category
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    duplicates_found = any(len(items) > 1 for items in categories.values())
    assert not duplicates_found, "❌ Final outfit should not contain duplicates"
    print("   ✅ No duplicates in final outfit")
    
    # Check 6: Replacement items were used if all originals are removed
    replacement_names = [item.name for item in replacement_items]
    final_names = [item.name for item in fixed_items]
    original_names = [item.name for item in test_items if item.category == 'bottom']
    originals_in_final = any(name in final_names for name in original_names)
    replacements_used = any(name in final_names for name in replacement_names)
    if not originals_in_final:
        assert replacements_used, "❌ Replacement items should be used if all originals are removed"
        print("   ✅ Replacement items used when all originals are removed")
    else:
        print("   ✅ Best original kept as expected")
    
    print("\n🎉 All validation checks passed!")
    
    # Test the healing context state
    print("\n📈 Healing Context Summary:")
    state = healing_context.get_state()
    print(f"   - Session ID: {state['session_id']}")
    print(f"   - Healing pass: {state['healing_pass']}")
    print(f"   - Total learning events: {len(state['learning_history'])}")
    
    return True

async def test_duplicate_fixing_with_no_replacements():
    """Test duplicate fixing when no replacements are available."""
    print("\n🧪 Testing Duplicate Fixing with No Replacements Available")
    print("=" * 70)
    
    # Create test items with duplicates
    test_items = [
        MockClothingItem(
            id="sweater1", name="Wool Sweater", type="sweater", category="top", 
            userId="test_user", material="wool", quality_score=8.0
        ),
        MockClothingItem(
            id="sweater2", name="Cashmere Sweater", type="sweater", category="top", 
            userId="test_user", material="cashmere", quality_score=9.0
        )
    ]
    
    # Create context
    context = {
        'user_profile': {'id': 'test_user'},
        'occasion': 'casual',
        'weather': {'temperature_f': 75, 'condition': 'sunny'},
        'style_preferences': ['casual', 'comfortable']
    }
    
    # Create healing context
    healing_context = DynamicHealingContext(context)
    
    # Create fallback service
    fallback_service = OutfitFallbackService()
    
    # Mock the _find_alternatives_for_category method to return no replacements
    async def mock_find_alternatives_no_replacements(category, exclude_item, context, healing_context):
        return []  # No replacements available
    
    fallback_service._find_alternatives_for_category = mock_find_alternatives_no_replacements
    
    print("📋 Test Setup:")
    print(f"   - Original items: {[item.name for item in test_items]}")
    print(f"   - Duplicate category: top (2 sweaters)")
    print(f"   - No replacement items available")
    print()
    
    # Test the duplicate fixing strategy
    print("🔧 Running Duplicate Fix Strategy (No Replacements)...")
    fixed_items, fixes_applied = await fallback_service._fix_duplicate_items(
        test_items, context, healing_context
    )
    
    print("\n📊 Results:")
    print(f"   - Fixed items: {[item.name for item in fixed_items]}")
    print(f"   - Fixes applied: {len(fixes_applied)}")
    
    # Check that the fix was attempted but failed
    duplicate_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.DUPLICATE_FIX]
    if duplicate_fixes:
        latest_fix = duplicate_fixes[-1]
        print(f"   - Fix success: {latest_fix.success}")
        print(f"   - Fix details: {latest_fix.details}")
    
    # Validation checks
    print("\n✅ Validation Checks:")
    
    # Check 1: Fix was attempted but failed
    failed_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.DUPLICATE_FIX and not f.success]
    assert len(failed_fixes) > 0, "❌ Failed fix should be logged"
    print("   ✅ Failed fix logged")
    
    # Check 2: Items were still removed from context
    assert len(healing_context.items_removed) > 0, "❌ Items should be removed even when fix fails"
    print("   ✅ Items removed from healing context")
    
    print("\n🎉 All validation checks passed!")
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Duplicate Fixing Strategy Tests")
    print("=" * 70)
    
    try:
        # Test 1: Successful duplicate fixing
        await test_duplicate_fixing_strategy()
        
        # Test 2: Duplicate fixing with no replacements
        await test_duplicate_fixing_with_no_replacements()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main()) 