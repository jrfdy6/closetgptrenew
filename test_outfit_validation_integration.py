#!/usr/bin/env python3
"""
Integration Test for Outfit Validation Improvements
Tests the actual validation functions we implemented.
"""

import asyncio
import sys
import os

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from custom_types.wardrobe import ClothingItem
from services.outfit_validation_service import OutfitValidationService

async def test_validation_rules():
    """Test the actual validation rules we implemented."""
    print("🧪 Testing Outfit Validation Rules")
    print("=" * 40)
    
    validation_service = OutfitValidationService()
    
    # Create test clothing items
    blazer = ClothingItem(
        id="blazer_1",
        name="Navy Blazer",
        type="blazer",
        color="navy",
        imageUrl="https://example.com/blazer.jpg",
        style=["formal", "business"],
        occasion=["business", "formal"],
        brand="Test Brand",
        wearCount=5,
        favorite_score=0.8,
        tags=["professional"],
        metadata={}
    )
    
    cargo_pants = ClothingItem(
        id="cargo_1",
        name="Khaki Cargo Pants", 
        type="cargo pants",
        color="khaki",
        imageUrl="https://example.com/cargos.jpg",
        style=["casual", "athletic"],
        occasion=["casual", "athletic"],
        brand="Test Brand",
        wearCount=3,
        favorite_score=0.6,
        tags=["utility"],
        metadata={}
    )
    
    jeans = ClothingItem(
        id="jeans_1",
        name="Dark Wash Jeans",
        type="jeans", 
        color="blue",
        imageUrl="https://example.com/jeans.jpg",
        style=["casual"],
        occasion=["casual"],
        brand="Test Brand",
        wearCount=10,
        favorite_score=0.9,
        tags=["denim"],
        metadata={}
    )
    
    flip_flops = ClothingItem(
        id="flip_flops_1",
        name="Black Flip Flops",
        type="flip-flops",
        color="black", 
        imageUrl="https://example.com/flipflops.jpg",
        style=["casual", "beach"],
        occasion=["casual", "beach"],
        brand="Test Brand",
        wearCount=8,
        favorite_score=0.7,
        tags=["comfortable"],
        metadata={}
    )
    
    # Test cases
    test_cases = [
        {
            "name": "Blazer + Cargo Pants (Should Remove Cargos)",
            "items": [blazer, cargo_pants],
            "expected_removal": True,
            "expected_remaining": ["blazer"]
        },
        {
            "name": "Blazer + Flip Flops (Should Remove Flip Flops)",
            "items": [blazer, flip_flops],
            "expected_removal": True,
            "expected_remaining": ["blazer"]
        },
        {
            "name": "Blazer + Jeans (Should Keep Both)",
            "items": [blazer, jeans],
            "expected_removal": False,
            "expected_remaining": ["blazer", "jeans"]
        },
        {
            "name": "Just Jeans (Should Keep)",
            "items": [jeans],
            "expected_removal": False,
            "expected_remaining": ["jeans"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        try:
            # Test the inappropriate combinations enforcement
            filtered_items, errors = validation_service._enforce_inappropriate_combinations(test_case['items'])
            
            # Check if items were removed
            items_removed = len(test_case['items']) > len(filtered_items)
            
            # Check remaining item types
            remaining_types = [item.type.lower() for item in filtered_items]
            
            # Determine if test passed
            if test_case['expected_removal']:
                if items_removed:
                    print(f"✅ PASSED - Items were removed as expected")
                    print(f"   Remaining: {remaining_types}")
                    if errors:
                        print(f"   Errors: {errors}")
                    results.append(True)
                else:
                    print(f"❌ FAILED - Expected items to be removed but they weren't")
                    print(f"   Remaining: {remaining_types}")
                    results.append(False)
            else:
                if not items_removed:
                    print(f"✅ PASSED - No items were removed as expected")
                    print(f"   Remaining: {remaining_types}")
                    results.append(True)
                else:
                    print(f"❌ FAILED - Items were removed when they shouldn't have been")
                    print(f"   Remaining: {remaining_types}")
                    if errors:
                        print(f"   Errors: {errors}")
                    results.append(False)
                    
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 VALIDATION TEST RESULTS")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All validation tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed - please review the validation logic")
    
    return passed == total

async def test_intelligent_naming():
    """Test the intelligent naming function."""
    print("\n🎨 Testing Intelligent Naming")
    print("=" * 40)
    
    # Import the naming function from routes
    try:
        from routes.outfits import generate_intelligent_outfit_name
        
        test_cases = [
            {
                "name": "Blazer + Jeans",
                "items": [
                    {"type": "blazer", "name": "Navy Blazer"},
                    {"type": "jeans", "name": "Dark Jeans"}
                ],
                "style": "casual",
                "mood": "confident",
                "occasion": "business",
                "expected_keywords": ["Smart Casual", "Business"]
            },
            {
                "name": "Dress Only",
                "items": [
                    {"type": "dress", "name": "Black Dress"}
                ],
                "style": "elegant",
                "mood": "confident", 
                "occasion": "formal",
                "expected_keywords": ["Effortless", "Formal"]
            },
            {
                "name": "Jeans + Sneakers",
                "items": [
                    {"type": "jeans", "name": "Blue Jeans"},
                    {"type": "sneakers", "name": "White Sneakers"}
                ],
                "style": "casual",
                "mood": "relaxed",
                "occasion": "casual",
                "expected_keywords": ["Relaxed", "Casual"]
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['name']}")
            
            try:
                outfit_name = await generate_intelligent_outfit_name(
                    test_case['items'],
                    test_case['style'],
                    test_case['mood'],
                    test_case['occasion']
                )
                
                print(f"   Generated: '{outfit_name}'")
                
                # Check if expected keywords are in the name
                name_lower = outfit_name.lower()
                keywords_found = [kw for kw in test_case['expected_keywords'] if kw.lower() in name_lower]
                
                if keywords_found:
                    print(f"✅ PASSED - Found keywords: {keywords_found}")
                    results.append(True)
                else:
                    print(f"❌ FAILED - Expected keywords: {test_case['expected_keywords']}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ ERROR - {str(e)}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 NAMING TEST RESULTS")
        print("=" * 40)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total
        
    except ImportError as e:
        print(f"❌ Could not import naming function: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Outfit Generation Integration Tests")
    print("=" * 50)
    
    # Test validation rules
    validation_passed = await test_validation_rules()
    
    # Test intelligent naming
    naming_passed = await test_intelligent_naming()
    
    # Overall results
    print(f"\n🎯 OVERALL TEST RESULTS")
    print("=" * 50)
    print(f"Validation Tests: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    print(f"Naming Tests: {'✅ PASSED' if naming_passed else '❌ FAILED'}")
    
    if validation_passed and naming_passed:
        print("\n🎉 All integration tests passed! The outfit generation improvements are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")

if __name__ == "__main__":
    asyncio.run(main())
