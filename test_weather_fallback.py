#!/usr/bin/env python3
"""
Test Script for Weather Fallback Strategy with Dynamic Healing Context

This script tests the complete weather fallback flow:
1. Force a weather validation failure
2. Confirm fallback activation
3. Check Firestore query filtering
4. Inspect final output and healing log
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_fallback_service import OutfitFallbackService
from services.dynamic_healing_context import DynamicHealingContext, ErrorType
from models.clothing_item import ClothingItem
from data.database import Database

class WeatherFallbackTester:
    def __init__(self):
        self.fallback_service = OutfitFallbackService()
        self.db = Database()
        
    def create_test_wardrobe(self) -> List[ClothingItem]:
        """Create a test wardrobe with weather-inappropriate items."""
        return [
            ClothingItem(
                id="wool_sweater_01",
                name="Wool Sweater",
                category="top",
                subcategory="sweater",
                material="wool",
                color="navy",
                style="classic",
                season="winter",
                occasion="casual",
                user_id="test_user"
            ),
            ClothingItem(
                id="fleece_jacket_01", 
                name="Fleece Jacket",
                category="outerwear",
                subcategory="jacket",
                material="fleece",
                color="black",
                style="casual",
                season="winter",
                occasion="casual",
                user_id="test_user"
            ),
            ClothingItem(
                id="cotton_tshirt_01",
                name="Cotton T-Shirt",
                category="top",
                subcategory="tshirt",
                material="cotton",
                color="white",
                style="casual",
                season="summer",
                occasion="casual",
                user_id="test_user"
            )
        ]
    
    def create_hot_weather_context(self) -> Dict[str, Any]:
        """Create a hot weather context that will trigger weather validation failures."""
        return {
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
    
    async def test_weather_validation_failure(self):
        """Step 1: Force a weather validation failure"""
        print("🧪 Step 1: Testing Weather Validation Failure")
        print("=" * 50)
        
        # Create test data
        test_wardrobe = self.create_test_wardrobe()
        hot_context = self.create_hot_weather_context()
        
        # Create an outfit with weather-inappropriate items
        problematic_outfit = [
            test_wardrobe[0],  # wool sweater (too hot)
            test_wardrobe[1],  # fleece jacket (too hot)
        ]
        
        # Simulate validation errors
        validation_errors = [
            "Weather mismatch: wool sweater inappropriate for 85°F",
            "Weather mismatch: fleece jacket inappropriate for 85°F"
        ]
        
        print(f"❄️ Problematic outfit items:")
        for item in problematic_outfit:
            print(f"   - {item.name} ({item.material}) - ID: {item.id}")
        
        print(f"🔥 Weather context: {hot_context['temperature_f']}°F")
        print(f"❌ Validation errors: {len(validation_errors)}")
        
        return problematic_outfit, validation_errors, hot_context
    
    async def test_fallback_activation(self, failed_outfit, validation_errors, context):
        """Step 2: Confirm fallback kicks in"""
        print("\n🛠 Step 2: Testing Fallback Activation")
        print("=" * 50)
        
        # Initialize healing context
        healing_context = DynamicHealingContext()
        
        # Run the fallback system
        print("🔄 Running fallback system...")
        fixed_outfit, remaining_errors, healing_log = await self.fallback_service.heal_outfit_with_fallbacks(
            failed_outfit, validation_errors, context
        )
        
        print(f"✅ Fallback completed")
        print(f"📊 Results:")
        print(f"   - Original items: {len(failed_outfit)}")
        print(f"   - Fixed items: {len(fixed_outfit)}")
        print(f"   - Remaining errors: {len(remaining_errors)}")
        
        return fixed_outfit, remaining_errors, healing_log
    
    def inspect_healing_context(self, healing_log):
        """Step 3: Inspect the healing context for proper logging"""
        print("\n🔍 Step 3: Inspecting Healing Context")
        print("=" * 50)
        
        healing_context = healing_log.get('healing_context', {})
        
        print("📋 Healing Context Analysis:")
        print(f"   - Errors seen: {healing_context.get('errors_seen', [])}")
        print(f"   - Items removed: {healing_context.get('items_removed', [])}")
        print(f"   - Rules triggered: {json.dumps(healing_context.get('rules_triggered', {}), indent=6)}")
        print(f"   - Fixes attempted: {healing_context.get('fixes_attempted', [])}")
        print(f"   - Healing pass: {healing_context.get('healing_pass', 'N/A')}")
        
        # Check for specific weather-related entries
        errors_seen = healing_context.get('errors_seen', [])
        items_removed = healing_context.get('items_removed', [])
        rules_triggered = healing_context.get('rules_triggered', {})
        
        # Validation checks
        checks = {
            "Weather errors logged": "weather_mismatch" in errors_seen,
            "Wool sweater removed": "wool_sweater_01" in items_removed,
            "Fleece jacket removed": "fleece_jacket_01" in items_removed,
            "Weather rules triggered": "weather" in rules_triggered,
            "Weather fix attempted": "fix_weather_issues" in healing_context.get('fixes_attempted', [])
        }
        
        print("\n✅ Validation Checklist:")
        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {check}")
        
        return all(checks.values())
    
    def inspect_final_outfit(self, fixed_outfit, original_outfit):
        """Step 4: Inspect the final outfit for weather appropriateness"""
        print("\n👕 Step 4: Inspecting Final Outfit")
        print("=" * 50)
        
        print("📊 Outfit Comparison:")
        print("   Original (problematic):")
        for item in original_outfit:
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
            return False
        else:
            print("✅ All items are weather-appropriate")
            return True
    
    async def run_complete_test(self):
        """Run the complete weather fallback test"""
        print("🚀 Starting Weather Fallback Test")
        print("=" * 60)
        
        try:
            # Step 1: Force weather validation failure
            failed_outfit, validation_errors, context = await self.test_weather_validation_failure()
            
            # Step 2: Test fallback activation
            fixed_outfit, remaining_errors, healing_log = await self.test_fallback_activation(
                failed_outfit, validation_errors, context
            )
            
            # Step 3: Inspect healing context
            context_valid = self.inspect_healing_context(healing_log)
            
            # Step 4: Inspect final outfit
            outfit_valid = self.inspect_final_outfit(fixed_outfit, failed_outfit)
            
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
    tester = WeatherFallbackTester()
    success = await tester.run_complete_test()
    
    if success:
        print("\n✨ Weather fallback strategy is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Weather fallback strategy needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 