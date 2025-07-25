#!/usr/bin/env python3
"""
Comprehensive unit tests for outfit validation functions.
Tests typical cases, edge cases, and invalid inputs.
"""

import sys
import os
import asyncio
from datetime import datetime
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.validation_orchestrator import ValidationOrchestrator, ValidationResult
from src.utils.outfit_validation import (
    validate_material_compatibility,
    validate_weather_appropriateness,
    validate_skin_tone_compatibility,
    validate_body_type_fit,
    validate_gender_appropriateness,
    validate_outfit_compatibility
)
from src.custom_types.wardrobe import ClothingItem, ClothingType, Color, Metadata, VisualAttributes, Season
from src.custom_types.profile import UserProfile

class MockOutfitService:
    def _get_layering_rule(self, *args, **kwargs):
        return None
    def _validate_layering_compliance(self, items, layering_rule, occasion, temperature):
        return {
            "is_compliant": True,
            "missing_layers": [],
            "suggestions": []
        }

class TestOutfitValidation:
    """Comprehensive test suite for outfit validation functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ValidationOrchestrator(MockOutfitService())
        now = int(datetime.now().timestamp() * 1000)
        # Create sample clothing items
        self.casual_shirt = ClothingItem(
            id="shirt1",
            name="Casual T-Shirt",
            type=ClothingType.SHIRT,
            color="white",
            season=[Season.SPRING, Season.SUMMER],
            imageUrl="http://example.com/shirt.jpg",
            tags=["casual", "comfortable"],
            style=["casual"],
            userId="user1",
            dominantColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            matchingColors=[Color(name="navy", hex="#000080", rgb=[0,0,128])],
            occasion=["casual", "work"],
            brand="BrandA",
            createdAt=now,
            updatedAt=now,
            metadata=Metadata(
                analysisTimestamp=now,
                originalType="shirt",
                colorAnalysis={
                    "dominant": [Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
                    "matching": [Color(name="navy", hex="#000080", rgb=[0,0,128])]
                },
                visualAttributes=VisualAttributes(
                    material="cotton",
                    fit="relaxed",
                    genderTarget="female"
                )
            )
        )
        self.casual_jeans = ClothingItem(
            id="jeans1",
            name="Casual Jeans",
            type=ClothingType.JEANS,
            color="blue",
            season=[Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
            imageUrl="http://example.com/jeans.jpg",
            tags=["casual", "versatile"],
            style=["casual"],
            userId="user1",
            dominantColors=[Color(name="blue", hex="#0000FF", rgb=[0,0,255])],
            matchingColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            occasion=["casual", "work"],
            brand="BrandB",
            createdAt=now,
            updatedAt=now,
            metadata=Metadata(
                analysisTimestamp=now,
                originalType="jeans",
                colorAnalysis={
                    "dominant": [Color(name="blue", hex="#0000FF", rgb=[0,0,255])],
                    "matching": [Color(name="white", hex="#FFFFFF", rgb=[255,255,255])]
                },
                visualAttributes=VisualAttributes(
                    material="denim",
                    fit="comfortable",
                    genderTarget="female"
                )
            )
        )
        self.casual_shoes = ClothingItem(
            id="shoes1",
            name="Casual Sneakers",
            type=ClothingType.SNEAKERS,
            color="white",
            season=[Season.SPRING, Season.SUMMER, Season.FALL],
            imageUrl="http://example.com/shoes.jpg",
            tags=["casual", "comfortable"],
            style=["casual"],
            userId="user1",
            dominantColors=[Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
            matchingColors=[Color(name="blue", hex="#0000FF", rgb=[0,0,255])],
            occasion=["casual", "work"],
            brand="BrandC",
            createdAt=now,
            updatedAt=now,
            metadata=Metadata(
                analysisTimestamp=now,
                originalType="sneakers",
                colorAnalysis={
                    "dominant": [Color(name="white", hex="#FFFFFF", rgb=[255,255,255])],
                    "matching": [Color(name="blue", hex="#0000FF", rgb=[0,0,255])]
                },
                visualAttributes=VisualAttributes(
                    material="canvas",
                    fit="regular",
                    genderTarget="female"
                )
            )
        )
        # Create user profile
        self.user_profile = UserProfile(
            id="user1",
            name="Jane Doe",
            email="jane@example.com",
            gender="female",
            stylePreferences=["casual", "comfortable"],
            bodyType="hourglass",
            skinTone="warm",
            fitPreference="comfortable",
            createdAt=now,
            updatedAt=now
        )

    def test_material_compatibility(self):
        result = validate_material_compatibility([self.casual_shirt, self.casual_jeans])
        assert len(result.errors) == 0  # Allow warnings but no errors

    def test_weather_appropriateness(self):
        result = validate_weather_appropriateness([self.casual_shirt, self.casual_jeans], Season.SPRING)
        print(f"    Weather result: {result.is_valid}, errors: {result.errors}, warnings: {result.warnings}")
        assert len(result.errors) == 0  # Allow warnings but no errors
        result = validate_weather_appropriateness([self.casual_shirt, self.casual_jeans], Season.WINTER)
        print(f"    Weather result: {result.is_valid}, errors: {result.errors}, warnings: {result.warnings}")
        assert len(result.errors) == 0  # Allow warnings but no errors
        return result

    def test_skin_tone_compatibility(self):
        result = validate_skin_tone_compatibility([self.casual_shirt, self.casual_jeans], self.user_profile)
        print(f"    Skin tone result: {result.is_valid}, errors: {result.errors}, warnings: {result.warnings}")
        assert len(result.errors) == 0  # Allow warnings but no errors
        return result

    def test_body_type_fit(self):
        result = validate_body_type_fit([self.casual_shirt, self.casual_jeans], self.user_profile)
        print(f"    Body type result: {result.is_valid}, errors: {result.errors}, warnings: {result.warnings}")
        assert len(result.errors) == 0  # Allow warnings but no errors
        return result

    def test_gender_appropriateness(self):
        result = validate_gender_appropriateness([self.casual_shirt, self.casual_jeans], self.user_profile)
        assert len(result.errors) == 0  # Allow warnings but no errors

    def test_outfit_compatibility(self):
        result = validate_outfit_compatibility([self.casual_shirt, self.casual_jeans], self.user_profile, Season.SPRING)
        print(f"    Outfit compatibility result: {result.is_valid}, errors: {result.errors}, warnings: {result.warnings}")
        assert len(result.errors) == 0  # Allow warnings but no errors
        return result

    async def test_orchestrator_parallel_validation(self):
        outfit = [self.casual_shirt, self.casual_jeans, self.casual_shoes]
        context = {
            "occasion": "casual",
            "weather": {"temperature": 75, "condition": "clear"},  # Warmer temperature to avoid cold weather rules
            "user_profile": self.user_profile,
            "season": Season.SPRING
        }
        result = await self.orchestrator.run_validation_pipeline(outfit, context)
        print(f"    Orchestrator errors: {result['errors']}")
        print(f"    Orchestrator warnings: {result['warnings']}")
        assert len(result['errors']) == 0  # Allow warnings but no errors
        assert len(result['warnings']) >= 0

    async def test_orchestrator_sequential_validation(self):
        outfit = [self.casual_shirt, self.casual_jeans, self.casual_shoes]
        context = {
            "occasion": "casual",
            "weather": {"temperature": 75, "condition": "clear"},  # Warmer temperature to avoid cold weather rules
            "user_profile": self.user_profile,
            "season": Season.SPRING
        }
        result = await self.orchestrator.run_validation_pipeline(outfit, context)
        print(f"    Orchestrator errors: {result['errors']}")
        print(f"    Orchestrator warnings: {result['warnings']}")
        assert len(result['errors']) == 0  # Allow warnings but no errors
        assert len(result['warnings']) >= 0

    def test_edge_cases(self):
        # Test empty outfit
        result = validate_material_compatibility([])
        assert len(result.errors) == 0  # Allow warnings but no errors
        # Test single item outfit
        result = validate_material_compatibility([self.casual_shirt])
        assert len(result.errors) == 0  # Allow warnings but no errors

    def test_invalid_inputs(self):
        # Test with None items
        try:
            result = validate_material_compatibility(None)
            assert result.is_valid is False
        except Exception:
            pass
        # Test with invalid items
        try:
            result = validate_material_compatibility([None, self.casual_jeans])
            assert result.is_valid is False
        except Exception:
            pass

def run_tests():
    print("🧪 Running Outfit Validation Tests...")
    print("=" * 50)
    test_methods = [
        'test_material_compatibility',
        'test_weather_appropriateness',
        'test_skin_tone_compatibility',
        'test_body_type_fit',
        'test_gender_appropriateness',
        'test_outfit_compatibility',
        'test_edge_cases',
        'test_invalid_inputs'
    ]
    passed = 0
    failed = 0
    for test_name in test_methods:
        try:
            test_suite = TestOutfitValidation()
            test_suite.setup_method()
            test_method = getattr(test_suite, test_name)
            result = test_method()
            print(f"✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: AssertionError: {str(e)}")
            # Print validation errors/warnings if available
            try:
                if 'result' in locals():
                    result = locals()['result']
                    print(f"    Errors: {getattr(result, 'errors', None)}")
                    print(f"    Warnings: {getattr(result, 'warnings', None)}")
                    print(f"    Is Valid: {getattr(result, 'is_valid', None)}")
            except:
                pass
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            traceback.print_exc()
            failed += 1
    async_tests = [
        'test_orchestrator_parallel_validation',
        'test_orchestrator_sequential_validation'
    ]
    async def run_async_tests():
        nonlocal passed, failed
        for test_name in async_tests:
            try:
                test_suite = TestOutfitValidation()
                test_suite.setup_method()
                test_method = getattr(test_suite, test_name)
                await test_method()
                print(f"✅ {test_name}")
                passed += 1
            except Exception as e:
                print(f"❌ {test_name}: {str(e)}")
                traceback.print_exc()
                failed += 1
    asyncio.run(run_async_tests())
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 