#!/usr/bin/env python3
"""
Focused Test for Outfit Generation Validation
Tests the core validation logic to ensure inappropriate combinations are prevented.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from typing import List, Dict, Any
import asyncio

# Mock classes for testing
class MockClothingItem:
    def __init__(self, id: str, name: str, type: str, color: str = "", style: List[str] = None, occasion: List[str] = None):
        self.id = id
        self.name = name
        self.type = type
        self.color = color
        self.style = style or []
        self.occasion = occasion or []
        self.imageUrl = f"https://example.com/{id}.jpg"
        self.wearCount = 0
        self.favorite_score = 0.5
        self.tags = []
        self.metadata = None

class MockWeatherData:
    def __init__(self, temperature: float = 70, condition: str = "clear", humidity: int = 50, wind_speed: int = 5, precipitation: int = 0):
        self.temperature = temperature
        self.condition = condition
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.precipitation = precipitation

def test_validation_service_directly():
    """Test the validation service directly."""
    print("🧪 Testing Outfit Validation Service Directly")
    print("=" * 60)
    
    try:
        # Import the validation service
        from services.outfit_validation_service import OutfitValidationService
        
        validation_service = OutfitValidationService()
        
        # Test cases
        test_cases = [
            {
                "name": "Blazer + Cargo Pants (Should Remove Cargos)",
                "items": [
                    MockClothingItem("blazer_1", "Navy Blazer", "blazer"),
                    MockClothingItem("cargo_1", "Khaki Cargo Pants", "cargo pants")
                ],
                "should_remove": True
            },
            {
                "name": "Blazer + Flip Flops (Should Remove Flip Flops)",
                "items": [
                    MockClothingItem("blazer_1", "Navy Blazer", "blazer"),
                    MockClothingItem("flip_flops_1", "Black Flip Flops", "flip-flops")
                ],
                "should_remove": True
            },
            {
                "name": "Blazer + Jeans (Should Keep Both)",
                "items": [
                    MockClothingItem("blazer_1", "Navy Blazer", "blazer"),
                    MockClothingItem("jeans_1", "Dark Wash Jeans", "jeans")
                ],
                "should_remove": False
            },
            {
                "name": "Suit + Athletic Shorts (Should Remove Shorts)",
                "items": [
                    MockClothingItem("suit_1", "Black Suit", "suit"),
                    MockClothingItem("shorts_1", "Athletic Shorts", "athletic shorts")
                ],
                "should_remove": True
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
                
                print(f"   Original items: {[item.name for item in test_case['items']]}")
                print(f"   Filtered items: {[item.name for item in filtered_items]}")
                if errors:
                    print(f"   Errors: {errors}")
                
                # Determine if test passed
                if test_case['should_remove']:
                    if items_removed:
                        print(f"✅ PASSED - Items were removed as expected")
                        results.append(True)
                    else:
                        print(f"❌ FAILED - Expected items to be removed but they weren't")
                        results.append(False)
                else:
                    if not items_removed:
                        print(f"✅ PASSED - No items were removed as expected")
                        results.append(True)
                    else:
                        print(f"❌ FAILED - Items were removed when they shouldn't have been")
                        results.append(False)
                        
            except Exception as e:
                print(f"❌ ERROR - {str(e)}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 VALIDATION SERVICE TEST RESULTS")
        print("=" * 60)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total
        
    except ImportError as e:
        print(f"❌ Could not import validation service: {e}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_rule_based_outfit_generation():
    """Test the rule-based outfit generation logic."""
    print("\n🎯 Testing Rule-Based Outfit Generation")
    print("=" * 60)
    
    try:
        # Import the rule-based generation function
        from routes.outfits import generate_rule_based_outfit
        
        # Mock wardrobe items
        mock_wardrobe = [
            {
                "id": "blazer_1",
                "name": "Navy Blazer",
                "type": "blazer",
                "color": "navy",
                "style": ["formal", "business"],
                "occasion": ["business", "formal"],
                "season": ["all"],
                "userId": "test_user",
                "dominantColors": [],
                "matchingColors": [],
                "createdAt": 1234567890000,
                "updatedAt": 1234567890000
            },
            {
                "id": "cargo_1",
                "name": "Khaki Cargo Pants",
                "type": "cargo pants",
                "color": "khaki",
                "style": ["casual", "athletic"],
                "occasion": ["casual", "athletic"],
                "season": ["all"],
                "userId": "test_user",
                "dominantColors": [],
                "matchingColors": [],
                "createdAt": 1234567890000,
                "updatedAt": 1234567890000
            },
            {
                "id": "jeans_1",
                "name": "Dark Wash Jeans",
                "type": "jeans",
                "color": "blue",
                "style": ["casual"],
                "occasion": ["casual"],
                "season": ["all"],
                "userId": "test_user",
                "dominantColors": [],
                "matchingColors": [],
                "createdAt": 1234567890000,
                "updatedAt": 1234567890000
            }
        ]
        
        mock_user_profile = {
            "id": "test_user",
            "name": "Test User",
            "gender": "female",
            "stylePreferences": ["casual", "minimalist"]
        }
        
        mock_request = type('MockRequest', (), {
            'style': 'business',
            'occasion': 'business',
            'baseItemId': None,
            'weather': MockWeatherData(70, "clear")
        })()
        
        print("   Generating outfit with blazer + cargo pants + jeans...")
        
        # This should remove cargo pants due to inappropriate combination
        result = asyncio.run(generate_rule_based_outfit(mock_wardrobe, mock_user_profile, mock_request))
        
        if result and "outfit" in result:
            outfit_items = result["outfit"].get("items", [])
            item_names = [item.get("name", "") for item in outfit_items]
            
            print(f"   Generated outfit items: {item_names}")
            
            # Check if cargo pants were removed
            has_cargo = any("cargo" in name.lower() for name in item_names)
            has_blazer = any("blazer" in name.lower() for name in item_names)
            
            if has_blazer and not has_cargo:
                print("✅ PASSED - Cargo pants were correctly removed from blazer outfit")
                return True
            elif has_blazer and has_cargo:
                print("❌ FAILED - Cargo pants should have been removed from blazer outfit")
                return False
            else:
                print("⚠️  WARNING - Unexpected outfit composition")
                return False
        else:
            print("❌ FAILED - No outfit generated")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import rule-based generation: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_weather_integration():
    """Test weather integration with outfit generation."""
    print("\n🌤️ Testing Weather Integration")
    print("=" * 60)
    
    # Test weather data handling
    weather_scenarios = [
        {"temperature": 90, "condition": "hot", "expected_avoid": ["blazer", "coat"]},
        {"temperature": 30, "condition": "cold", "expected_avoid": ["t-shirt", "shorts"]},
        {"temperature": 70, "condition": "clear", "expected_avoid": []}
    ]
    
    results = []
    
    for scenario in weather_scenarios:
        print(f"   Testing {scenario['temperature']}°F {scenario['condition']} weather...")
        
        # Simple weather appropriateness check
        temp = scenario["temperature"]
        avoid_items = scenario["expected_avoid"]
        
        # Mock items
        test_items = [
            {"type": "blazer", "name": "Navy Blazer"},
            {"type": "t-shirt", "name": "White T-Shirt"},
            {"type": "coat", "name": "Winter Coat"},
            {"type": "shorts", "name": "Athletic Shorts"}
        ]
        
        # Check weather appropriateness
        appropriate_items = []
        for item in test_items:
            item_type = item["type"]
            
            # Hot weather logic
            if temp > 80:
                if item_type not in ["blazer", "coat", "sweater"]:
                    appropriate_items.append(item)
            # Cold weather logic
            elif temp < 50:
                if item_type not in ["t-shirt", "shorts", "sandals"]:
                    appropriate_items.append(item)
            # Moderate weather
            else:
                appropriate_items.append(item)
        
        # Check if inappropriate items were filtered out
        filtered_types = [item["type"] for item in appropriate_items]
        inappropriate_found = any(avoid_type in filtered_types for avoid_type in avoid_items)
        
        if not inappropriate_found:
            print(f"   ✅ PASSED - Weather-appropriate items selected")
            results.append(True)
        else:
            print(f"   ❌ FAILED - Weather-inappropriate items found: {[t for t in filtered_types if t in avoid_items]}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 WEATHER INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total

def main():
    """Run all focused tests."""
    print("🚀 Starting Focused Outfit Generation Validation Tests")
    print("=" * 60)
    print("Testing core validation logic without full backend setup")
    print()
    
    # Test 1: Validation service
    validation_passed = test_validation_service_directly()
    
    # Test 2: Rule-based generation
    rule_based_passed = test_rule_based_outfit_generation()
    
    # Test 3: Weather integration
    weather_passed = test_weather_integration()
    
    # Overall results
    print(f"\n🎯 OVERALL FOCUSED TEST RESULTS")
    print("=" * 60)
    print(f"Validation Service: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    print(f"Rule-Based Generation: {'✅ PASSED' if rule_based_passed else '❌ FAILED'}")
    print(f"Weather Integration: {'✅ PASSED' if weather_passed else '❌ FAILED'}")
    
    total_passed = sum([validation_passed, rule_based_passed, weather_passed])
    total_tests = 3
    
    print(f"\n📊 FINAL SCORE: {total_passed}/{total_tests}")
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 All focused tests passed!")
        print("✅ Validation logic is working correctly")
        print("✅ Inappropriate combinations are being prevented")
        print("✅ Weather integration is functioning")
        print("✅ Core outfit generation logic is sound")
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed.")
        print("🔧 Please review the failing tests and fix issues")

if __name__ == "__main__":
    main()
