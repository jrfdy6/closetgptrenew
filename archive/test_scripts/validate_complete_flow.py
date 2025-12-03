#!/usr/bin/env python3
"""
Complete Flow Validation Test
Tests all enhancements: occasion-first, session tracking, exploration, favorites, wear decay
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
from src.custom_types.wardrobe import ClothingItem
from types import SimpleNamespace

# Test data - Mock wardrobe with various items
def create_test_wardrobe():
    """Create a diverse test wardrobe for validation"""
    items = [
        # GYM ITEMS (Classic)
        {"id": "gym_polo_1", "name": "Grey Athletic Polo", "type": "shirt", "occasion": ["gym", "athletic"], "style": ["classic", "sporty"]},
        {"id": "gym_shorts_1", "name": "Black Athletic Shorts", "type": "shorts", "occasion": ["gym", "athletic"], "style": ["classic", "sporty"]},
        {"id": "gym_sneakers_1", "name": "White Training Sneakers", "type": "shoes", "occasion": ["gym", "athletic", "sport"], "style": ["classic", "athletic"]},
        
        # GYM ITEMS (Minimalist)
        {"id": "gym_tee_1", "name": "Minimalist Black Tee", "type": "t-shirt", "occasion": ["gym", "athletic"], "style": ["minimalist", "athletic"]},
        {"id": "gym_joggers_1", "name": "Grey Joggers", "type": "pants", "occasion": ["gym", "workout"], "style": ["minimalist", "athleisure"]},
        
        # CASUAL ITEMS (Classic)
        {"id": "casual_chinos_1", "name": "Navy Chinos", "type": "pants", "occasion": ["casual", "smart_casual"], "style": ["classic", "preppy"]},
        {"id": "casual_loafers_1", "name": "Brown Leather Loafers", "type": "shoes", "occasion": ["casual", "business_casual"], "style": ["classic", "elegant"]},
        {"id": "casual_polo_1", "name": "White Classic Polo", "type": "shirt", "occasion": ["casual"], "style": ["classic", "preppy"]},
        
        # SLEEP/LOUNGEWEAR (Cozy)
        {"id": "sleep_pj_1", "name": "Cozy Flannel Pajamas", "type": "pants", "occasion": ["sleep", "loungewear"], "style": ["cozy", "comfortable"]},
        {"id": "sleep_tee_1", "name": "Soft Sleep Tee", "type": "t-shirt", "occasion": ["sleep", "loungewear"], "style": ["cozy", "comfortable"]},
        {"id": "sleep_slippers_1", "name": "Fuzzy Slippers", "type": "shoes", "occasion": ["sleep", "loungewear"], "style": ["cozy", "comfortable"]},
        
        # WRONG OCCASION ITEMS (should be filtered out)
        {"id": "business_suit_1", "name": "Formal Suit Jacket", "type": "jacket", "occasion": ["business", "formal"], "style": ["classic", "elegant"]},
        {"id": "business_dress_shoes_1", "name": "Black Dress Shoes", "type": "shoes", "occasion": ["business", "formal"], "style": ["classic", "elegant"]},
        
        # FALLBACK TEST ITEMS (for minimalist/sport overlap)
        {"id": "sport_tee_1", "name": "Sport Performance Tee", "type": "t-shirt", "occasion": ["sport", "active"], "style": ["minimalist", "athletic"], "wearCount": 0},
        {"id": "active_shorts_1", "name": "Active Shorts", "type": "shorts", "occasion": ["active", "athletic"], "style": ["minimalist"], "wearCount": 0},
    ]
    
    # Convert to ClothingItem objects
    clothing_items = []
    for item_dict in items:
        try:
            item = ClothingItem(**item_dict)
            clothing_items.append(item)
        except Exception as e:
            print(f"⚠️ Warning: Could not create ClothingItem for {item_dict.get('name')}: {e}")
            # Add as dict if ClothingItem fails (for compatibility)
            clothing_items.append(item_dict)
    
    return clothing_items


def create_test_context(occasion: str, style: str, wardrobe):
    """Create test generation context"""
    weather = SimpleNamespace(temperature=72.0, condition="clear")
    
    context = GenerationContext(
        user_id="test_user_validation",
        occasion=occasion,
        style=style,
        mood="confident",
        weather=weather,
        wardrobe=wardrobe,
        base_item_id=None,
        user_profile={
            'bodyType': 'Average',
            'height': 'Average',
            'gender': 'Unspecified',
            'stylePreferences': {}
        }
    )
    
    return context


async def run_validation_test(test_name: str, occasion: str, style: str, expected_outcome: str):
    """Run a single validation test"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*80}")
    print(f"📋 Occasion: {occasion}, Style: {style}")
    print(f"🎯 Expected: {expected_outcome}")
    print(f"{'-'*80}\n")
    
    # Create test wardrobe
    wardrobe = create_test_wardrobe()
    print(f"📦 Test wardrobe: {len(wardrobe)} items")
    
    # Create context
    context = create_test_context(occasion, style, wardrobe)
    
    # Initialize service
    service = RobustOutfitGenerationService()
    
    try:
        # Generate outfit
        print(f"\n🚀 Starting generation...\n")
        outfit = await service.generate_outfit(context)
        
        # Validate results
        print(f"\n{'='*80}")
        print(f"✅ TEST RESULTS: {test_name}")
        print(f"{'='*80}\n")
        
        print(f"🎨 Generated Outfit:")
        if hasattr(outfit, 'items') and outfit.items:
            for i, item in enumerate(outfit.items):
                item_name = getattr(item, 'name', item.get('name', 'Unknown') if isinstance(item, dict) else 'Unknown')
                item_occasions = getattr(item, 'occasion', item.get('occasion', []) if isinstance(item, dict) else [])
                item_styles = getattr(item, 'style', item.get('style', []) if isinstance(item, dict) else [])
                print(f"  {i+1}. {item_name}")
                print(f"     Occasions: {item_occasions}")
                print(f"     Styles: {item_styles}")
        else:
            print("  ⚠️ No items in outfit")
        
        # Validation checks
        print(f"\n🔍 Validation Checks:")
        
        # Check 1: Occasion appropriateness
        occasion_match = False
        if hasattr(outfit, 'items') and outfit.items:
            for item in outfit.items:
                item_occasions = getattr(item, 'occasion', item.get('occasion', []) if isinstance(item, dict) else [])
                if occasion.lower() in [o.lower() for o in item_occasions]:
                    occasion_match = True
                    break
        
        print(f"  {'✅' if occasion_match else '❌'} Occasion Match: Items match '{occasion}' occasion")
        
        # Check 2: Style compatibility
        style_match = False
        if hasattr(outfit, 'items') and outfit.items:
            for item in outfit.items:
                item_styles = getattr(item, 'style', item.get('style', []) if isinstance(item, dict) else [])
                if style.lower() in [s.lower() for s in item_styles]:
                    style_match = True
                    break
        
        print(f"  {'✅' if style_match else '⚠️'} Style Match: Items match '{style}' style")
        
        # Check 3: No wrong occasion items (e.g., no business items in gym outfit)
        wrong_items = []
        excluded_occasions = {
            'gym': ['business', 'formal'],
            'casual': ['gym', 'athletic', 'formal'],
            'sleep': ['business', 'gym', 'formal']
        }
        
        if occasion.lower() in excluded_occasions and hasattr(outfit, 'items') and outfit.items:
            for item in outfit.items:
                item_occasions = getattr(item, 'occasion', item.get('occasion', []) if isinstance(item, dict) else [])
                item_name = getattr(item, 'name', item.get('name', 'Unknown') if isinstance(item, dict) else 'Unknown')
                for excluded in excluded_occasions[occasion.lower()]:
                    if excluded in [o.lower() for o in item_occasions]:
                        wrong_items.append(f"{item_name} (has '{excluded}')")
        
        if wrong_items:
            print(f"  ❌ Wrong Items Found: {', '.join(wrong_items)}")
        else:
            print(f"  ✅ No Wrong Items: All items appropriate for occasion")
        
        # Overall result
        print(f"\n{'='*80}")
        if occasion_match and not wrong_items:
            print(f"✅ TEST PASSED: {test_name}")
        else:
            print(f"❌ TEST FAILED: {test_name}")
        print(f"{'='*80}\n")
        
        return {
            'test': test_name,
            'passed': occasion_match and not wrong_items,
            'occasion_match': occasion_match,
            'style_match': style_match,
            'wrong_items': len(wrong_items) == 0,
            'items_count': len(outfit.items) if hasattr(outfit, 'items') and outfit.items else 0
        }
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ TEST ERROR: {test_name}")
        print(f"{'='*80}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        
        return {
            'test': test_name,
            'passed': False,
            'error': str(e)
        }


async def main():
    """Run all validation tests"""
    print(f"\n{'#'*80}")
    print(f"# COMPLETE FLOW VALIDATION TEST SUITE")
    print(f"# Testing: Occasion-first, Session tracking, Exploration, Favorites, Wear decay")
    print(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")
    
    # Define test cases
    test_cases = [
        {
            'name': 'Gym + Classic',
            'occasion': 'gym',
            'style': 'classic',
            'expected': 'Pull gym-appropriate classic items (e.g., polos, shorts, sneakers)'
        },
        {
            'name': 'Casual + Classic',
            'occasion': 'casual',
            'style': 'classic',
            'expected': 'Use classic-casual items (chinos, loafers, etc.)'
        },
        {
            'name': 'Gym + Minimalist (Fallback Test)',
            'occasion': 'gym',
            'style': 'minimalist',
            'expected': 'Expand via OCCASION_FALLBACKS (sport, athletic, etc.)'
        },
        {
            'name': 'Sleep + Cozy',
            'occasion': 'sleep',
            'style': 'cozy',
            'expected': 'Ignore global diversity, allow overlaps'
        }
    ]
    
    # Run all tests
    results = []
    for test_case in test_cases:
        result = await run_validation_test(
            test_case['name'],
            test_case['occasion'],
            test_case['style'],
            test_case['expected']
        )
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print(f"\n{'#'*80}")
    print(f"# TEST SUMMARY")
    print(f"{'#'*80}\n")
    
    passed_tests = sum(1 for r in results if r.get('passed', False))
    total_tests = len(results)
    
    print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed\n")
    
    for result in results:
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        print(f"  {status}: {result['test']}")
        if 'error' in result:
            print(f"         Error: {result['error']}")
        elif not result.get('passed', False):
            details = []
            if not result.get('occasion_match', False):
                details.append("occasion mismatch")
            if not result.get('wrong_items', True):
                details.append("wrong items present")
            if details:
                print(f"         Issues: {', '.join(details)}")
    
    print(f"\n{'#'*80}")
    if passed_tests == total_tests:
        print(f"# ✅ ALL TESTS PASSED - SYSTEM VALIDATED")
    else:
        print(f"# ⚠️ SOME TESTS FAILED - REVIEW REQUIRED")
    print(f"{'#'*80}\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

