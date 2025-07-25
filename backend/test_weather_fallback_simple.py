#!/usr/bin/env python3
"""
Simple Test for Weather Fallback Strategy with Dynamic Healing Context

This script tests the weather fallback functionality without complex imports.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock ClothingItem for testing
class MockClothingItem:
    def __init__(self, id, name, category, material, **kwargs):
        self.id = id
        self.name = name
        self.category = category
        self.material = material
        self.type = category  # Add type attribute for compatibility
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Add userId attribute for fallback logic compatibility
        if hasattr(self, 'user_id'):
            self.userId = self.user_id

async def test_weather_fallback():
    """Test the weather fallback strategy with dynamic healing context"""
    
    print("🧪 Testing Weather Fallback with Dynamic Healing Context")
    print("=" * 60)
    
    try:
        # Import the services
        from src.services.dynamic_healing_context import DynamicHealingContext
        from src.services.outfit_fallback_service import OutfitFallbackService
        
        # Create test data
        print("📋 Creating test data...")
        
        # Create problematic outfit with weather-inappropriate items
        problematic_outfit = [
            MockClothingItem(
                id="wool_sweater_01",
                name="Wool Sweater",
                category="top",
                material="wool",
                type="sweater",
                color="navy",
                style="classic",
                season="winter",
                occasion="casual",
                user_id="test_user"
            ),
            MockClothingItem(
                id="fleece_jacket_01",
                name="Fleece Jacket", 
                category="outerwear",
                material="fleece",
                type="jacket",
                color="black",
                style="casual",
                season="winter",
                occasion="casual",
                user_id="test_user"
            )
        ]
        
        # Create a weather-appropriate replacement item
        cotton_tshirt = MockClothingItem(
            id="cotton_tshirt_01",
            name="Cotton T-Shirt",
            category="top",
            material="cotton",
            type="t-shirt",
            color="white",
            style="casual",
            season="summer",
            occasion="casual",
            user_id="test_user"
        )
        
        # Monkeypatch the fallback service's _query_by_weather_conditions method
        async def mock_query_by_weather_conditions(self, user_id, category, temperature, weather_condition, healing_context=None, limit=10):
            print(f"[DEBUG] mock_query_by_weather_conditions called with: user_id={user_id}, category={category}, temperature={temperature}, weather_condition={weather_condition}")
            print(f"[DEBUG] Returning cotton_tshirt: {cotton_tshirt.name} ({cotton_tshirt.material})")
            return [cotton_tshirt]
        
        # Patch the method
        OutfitFallbackService._query_by_weather_conditions = mock_query_by_weather_conditions
        
        # Create hot weather context
        hot_context = {
            "occasion": "casual",
            "style": "old money",
            "temperature_f": 85,
            "weather": {
                "temperature_f": 85,
                "condition": "sunny",
                "humidity": 60
            },
            "season": "summer",
            "user_id": "test_user"
        }
        
        # Create validation errors
        validation_errors = [
            "Weather mismatch: wool sweater inappropriate for 85°F",
            "Weather mismatch: fleece jacket inappropriate for 85°F"
        ]
        
        print(f"❄️ Problematic outfit items:")
        for item in problematic_outfit:
            print(f"   - {item.name} ({item.material}) - ID: {item.id}")
        
        print(f"🔥 Weather context: {hot_context['temperature_f']}°F")
        print(f"❌ Validation errors: {len(validation_errors)}")
        
        # Initialize services
        print("\n🛠 Initializing fallback service...")
        fallback_service = OutfitFallbackService()
        
        # Run the fallback system
        print("🔄 Running fallback system...")
        fixed_outfit, remaining_errors, healing_log = await fallback_service.heal_outfit_with_fallbacks(
            problematic_outfit, validation_errors, hot_context
        )
        
        print(f"✅ Fallback completed")
        print(f"📊 Results:")
        print(f"   - Original items: {len(problematic_outfit)}")
        print(f"   - Fixed items: {len(fixed_outfit)}")
        print(f"   - Remaining errors: {len(remaining_errors)}")
        print(f"   - Strategy used: {healing_log.get('strategy_used', 'unknown')}")
        
        # Inspect healing context
        print("\n🔍 Inspecting Healing Context:")
        healing_context = healing_log.get('healing_context', {})
        
        print("📋 Healing Context Analysis:")
        print(f"   - Errors seen: {healing_context.get('errors_seen', [])}")
        print(f"   - Items removed: {healing_context.get('items_removed', [])}")
        print(f"   - Rules triggered: {json.dumps(healing_context.get('rules_triggered', {}), indent=6)}")
        print(f"   - Fixes attempted: {healing_context.get('fixes_attempted', [])}")
        print(f"   - Healing pass: {healing_context.get('healing_pass', 'N/A')}")
        
        # Check for specific weather-related entries with proper structure handling
        errors_seen = healing_context.get('errors_seen', [])
        items_removed = healing_context.get('items_removed', [])
        rules_triggered = healing_context.get('rules_triggered', {})
        fixes_attempted = healing_context.get('fixes_attempted', [])
        
        # Helper functions for cleaner validation
        def healing_context_has_error(context, error_type):
            return any(e.get('error_type') == error_type for e in context.get('errors_seen', []))
        
        def healing_context_triggered_rule(context, rule_type):
            return rule_type in context.get('rules_triggered', {})
        
        def healing_context_has_fix_attempt(context, fix_type):
            return any(fix_type in str(fix).lower() for fix in context.get('fixes_attempted', []))
        
        # Validation checks with proper structure handling
        checks = {
            "Weather errors logged": healing_context_has_error(healing_context, "weather_mismatch"),
            "Wool sweater removed": "wool_sweater_01" in items_removed,
            "Fleece jacket removed": "fleece_jacket_01" in items_removed,
            "Weather rules triggered": healing_context_triggered_rule(healing_context, "weather"),
            "Weather fix attempted": healing_context_has_fix_attempt(healing_context, "weather")
        }
        
        print("\n✅ Validation Checklist:")
        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {check}")
        
        context_valid = all(checks.values())
        
        # Inspect final outfit
        print("\n👕 Inspecting Final Outfit:")
        print("   Original (problematic):")
        for item in problematic_outfit:
            print(f"     - {item.name} ({item.material})")
        
        print("   Fixed (weather-appropriate):")
        for item in fixed_outfit:
            print(f"     - {item.name} ({item.material})")
        
        # Check if weather-inappropriate materials are still present
        hot_materials = ["wool", "fleece", "leather", "suede"]
        inappropriate_items = [
            item for item in fixed_outfit 
            if item.material.lower() in hot_materials
        ]
        
        if inappropriate_items:
            print(f"❌ WARNING: Weather-inappropriate items still present:")
            for item in inappropriate_items:
                print(f"     - {item.name} ({item.material})")
            outfit_valid = False
        else:
            print("✅ All items are weather-appropriate")
            outfit_valid = True
        
        # Final results
        print("\n🎯 Final Test Results")
        print("=" * 60)
        print(f"✅ Context logging: {'PASS' if context_valid else 'FAIL'}")
        print(f"✅ Outfit appropriateness: {'PASS' if outfit_valid else 'FAIL'}")
        print(f"✅ Remaining errors: {len(remaining_errors)} (should be 0)")
        
        if context_valid and outfit_valid and len(remaining_errors) == 0:
            print("\n🎉 ALL TESTS PASSED! Weather fallback with dynamic healing context is working correctly.")
            return True
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            return False
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    success = await test_weather_fallback()
    
    if success:
        print("\n✨ Weather fallback strategy is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Weather fallback strategy needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 