#!/usr/bin/env python3
"""
Regression Tests for Fallback System and Healing Context

This test suite ensures:
1. Healing context structure remains consistent
2. Fallback strategies are properly triggered
3. Expected fixes are attempted when errors occur
4. No regression in fallback functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService
from src.services.outfit_fallback_service import OutfitFallbackService
from src.services.dynamic_healing_context import DynamicHealingContext, ErrorType, FixType
from src.custom_types.wardrobe import ClothingItem, ClothingType, Color
from src.custom_types.profile import UserProfile
from src.custom_types.weather import WeatherData
import time

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
        self.dominantColors = kwargs.get('dominantColors', [Color(name="blue", hex="#0000FF")])
        self.matchingColors = kwargs.get('matchingColors', [Color(name="white", hex="#FFFFFF")])
        
        # Add required attributes that the outfit service expects
        self.imageUrl = kwargs.get('imageUrl', 'https://example.com/test-image.jpg')
        self.imageUrls = kwargs.get('imageUrls', ['https://example.com/test-image.jpg'])
        self.description = kwargs.get('description', f'Test {name}')
        self.brand = kwargs.get('brand', 'Test Brand')
        self.price = kwargs.get('price', 50.0)
        self.size = kwargs.get('size', 'M')
        self.fit = kwargs.get('fit', 'regular')
        self.fabric = kwargs.get('fabric', 'cotton')
        self.pattern = kwargs.get('pattern', 'solid')
        self.formality = kwargs.get('formality', 'casual')
        self.silhouette = kwargs.get('silhouette', 'regular')
        self.layer = kwargs.get('layer', 1)
        self.minTemp = kwargs.get('minTemp', 60)
        self.maxTemp = kwargs.get('maxTemp', 80)
        self.createdAt = kwargs.get('createdAt', int(time.time()))
        self.updatedAt = kwargs.get('updatedAt', int(time.time()))
        
        # Add all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_test_wardrobe():
    """Create a test wardrobe with various items."""
    return [
        MockClothingItem(
            id="shirt1", name="White T-Shirt", type="shirt", category="top", 
            userId="test_user", material="cotton", style=["casual", "minimalist"]
        ),
        MockClothingItem(
            id="pants1", name="Blue Jeans", type="pants", category="bottom", 
            userId="test_user", material="denim", style=["casual", "classic"]
        ),
        MockClothingItem(
            id="shoes1", name="Sneakers", type="shoes", category="shoes", 
            userId="test_user", material="canvas", style=["casual", "athletic"]
        ),
        MockClothingItem(
            id="sweater1", name="Wool Sweater", type="sweater", category="top", 
            userId="test_user", material="wool", style=["classic", "warm"]
        ),
        MockClothingItem(
            id="jacket1", name="Leather Jacket", type="jacket", category="outerwear", 
            userId="test_user", material="leather", style=["edgy", "classic"]
        )
    ]

def create_test_user_profile():
    """Create a test user profile."""
    return UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual", "classic"],
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    )

class TestFallbackRegression:
    """Regression tests for the fallback system."""
    
    @pytest.fixture
    def outfit_service(self):
        """Create outfit service instance."""
        return OutfitService()
    
    @pytest.fixture
    def fallback_service(self):
        """Create fallback service instance."""
        return OutfitFallbackService()
    
    @pytest.fixture
    def test_wardrobe(self):
        """Create test wardrobe."""
        return create_test_wardrobe()
    
    @pytest.fixture
    def test_user_profile(self):
        """Create test user profile."""
        return create_test_user_profile()
    
    @pytest.fixture
    def test_weather(self):
        """Create test weather data."""
        return WeatherData(temperature=75, condition="sunny", location="test", humidity=50)

    def test_healing_context_structure_is_complete(self, outfit_service, test_wardrobe, test_user_profile, test_weather):
        """Test that healing context has all required fields and proper structure."""
        print("🧪 Testing Healing Context Structure Completeness")
        
        # Generate outfit using real pipeline
        result = asyncio.run(outfit_service.generate_outfit(
            occasion="casual",
            weather=test_weather,
            wardrobe=test_wardrobe,
            user_profile=test_user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="casual"
        ))
        
        # Extract healing context from metadata
        healing_log = result.metadata.get("healing_log", {})
        healing_context = healing_log.get("healing_context", {})
        
        print(f"🔍 Healing log keys: {list(healing_log.keys())}")
        print(f"🔍 Healing context keys: {list(healing_context.keys())}")
        print(f"🔍 Full metadata keys: {list(result.metadata.keys())}")
        
        # Validate that healing_log exists in metadata (even if empty)
        assert "healing_log" in result.metadata, "❌ healing_log missing from metadata"
        
        # Validate that healing_context exists in healing_log
        assert "healing_context" in healing_log, "❌ healing_context missing from healing_log"
        
        # Validate structure - healing context should have these fields (even if empty)
        assert "errors_seen" in healing_context, "❌ errors_seen missing from healing context"
        assert "rules_triggered" in healing_context, "❌ rules_triggered missing from healing context"
        assert "items_removed" in healing_context, "❌ items_removed missing from healing context"
        assert "fixes_attempted" in healing_context, "❌ fixes_attempted missing from healing context"
        assert "healing_pass" in healing_context, "❌ healing_pass missing from healing context"
        assert "learning_history" in healing_context, "❌ learning_history missing from healing context"
        
        # Validate data types
        assert isinstance(healing_context["errors_seen"], list), "❌ errors_seen should be a list"
        assert isinstance(healing_context["rules_triggered"], dict), "❌ rules_triggered should be a dict"
        assert isinstance(healing_context["items_removed"], list), "❌ items_removed should be a list"
        assert isinstance(healing_context["fixes_attempted"], list), "❌ fixes_attempted should be a list"
        assert isinstance(healing_context["healing_pass"], int), "❌ healing_pass should be an int"
        assert isinstance(healing_context["learning_history"], list), "❌ learning_history should be a list"
        
        # Validate error records structure (if any exist)
        if healing_context["errors_seen"]:
            error_record = healing_context["errors_seen"][0]
            assert isinstance(error_record, dict), "❌ Error records should be dictionaries"
            assert "error_type" in error_record, "❌ Error records missing error_type"
            assert "details" in error_record, "❌ Error records missing details"
            assert "pass_number" in error_record, "❌ Error records missing pass_number"
            assert "timestamp" in error_record, "❌ Error records missing timestamp"
        
        # Validate fix records structure (if any exist)
        if healing_context["fixes_attempted"]:
            fix_record = healing_context["fixes_attempted"][0]
            assert isinstance(fix_record, dict), "❌ Fix records should be dictionaries"
            assert "fix_type" in fix_record, "❌ Fix records missing fix_type"
            assert "success" in fix_record, "❌ Fix records missing success"
            assert "pass_number" in fix_record, "❌ Fix records missing pass_number"
            assert "timestamp" in fix_record, "❌ Fix records missing timestamp"
        
        print("✅ Healing context structure validation passed")

    def test_weather_fix_expected_when_weather_error_occurs(self, fallback_service):
        """Test that weather fixes are attempted when weather errors occur."""
        print("🧪 Testing Weather Fix Triggering")
        
        # Create test items with weather-inappropriate items
        test_items = [
            MockClothingItem(
                id="wool_sweater", name="Wool Sweater", type="sweater", category="top", 
                userId="test_user", material="wool", style=["warm"]
            ),
            MockClothingItem(
                id="cotton_tshirt", name="Cotton T-Shirt", type="shirt", category="top", 
                userId="test_user", material="cotton", style=["casual"]
            )
        ]
        
        context = {
            'user_profile': {'id': 'test_user'},
            'occasion': 'casual',
            'weather': {'temperature_f': 85, 'condition': 'sunny'},  # Hot weather
            'style_preferences': ['casual']
        }
        
        healing_context = DynamicHealingContext(context)
        
        # Mock the weather replacement method
        with patch.object(fallback_service, '_find_weather_appropriate_replacement') as mock_find:
            mock_find.return_value = test_items[1]  # Return cotton t-shirt as replacement
            
            # Run weather fix
            fixed_items, fixes_applied = asyncio.run(fallback_service._fix_weather_issues(
                test_items, context, healing_context
            ))
            
            # Check that weather fix was attempted
            weather_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.WEATHER_FIX]
            assert len(weather_fixes) > 0, "❌ Weather fix should be attempted when weather error occurs"
            
            # Check that weather error was logged
            weather_errors = [e for e in healing_context.errors_seen if e.error_type == ErrorType.WEATHER_MISMATCH]
            assert len(weather_errors) > 0, "❌ Weather error should be logged"
            
            print("✅ Weather fix triggering validation passed")

    def test_duplicate_fix_expected_when_duplicates_occur(self, fallback_service):
        """Test that duplicate fixes are attempted when duplicate items occur."""
        print("🧪 Testing Duplicate Fix Triggering")
        
        # Create test items with duplicates
        test_items = [
            MockClothingItem(
                id="pants1", name="Blue Jeans", type="pants", category="bottom", 
                userId="test_user", material="denim"
            ),
            MockClothingItem(
                id="pants2", name="Black Pants", type="pants", category="bottom", 
                userId="test_user", material="cotton"
            ),
            MockClothingItem(
                id="shirt1", name="White T-Shirt", type="shirt", category="top", 
                userId="test_user", material="cotton"
            )
        ]
        
        context = {
            'user_profile': {'id': 'test_user'},
            'occasion': 'casual',
            'weather': {'temperature_f': 75, 'condition': 'sunny'},
            'style_preferences': ['casual']
        }
        
        healing_context = DynamicHealingContext(context)
        
        # Mock the alternatives method
        with patch.object(fallback_service, '_find_alternatives_for_category') as mock_find:
            mock_find.return_value = [test_items[2]]  # Return shirt as alternative
            
            # Run duplicate fix
            fixed_items, fixes_applied = asyncio.run(fallback_service._fix_duplicate_items(
                test_items, context, healing_context
            ))
            
            # Check that duplicate fix was attempted
            duplicate_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.DUPLICATE_FIX]
            assert len(duplicate_fixes) > 0, "❌ Duplicate fix should be attempted when duplicates occur"
            
            # Check that duplicate error was logged
            duplicate_errors = [e for e in healing_context.errors_seen if e.error_type == ErrorType.DUPLICATE_ITEMS]
            assert len(duplicate_errors) > 0, "❌ Duplicate error should be logged"
            
            # Check that items were removed
            assert len(healing_context.items_removed) > 0, "❌ Items should be removed when fixing duplicates"
            
            print("✅ Duplicate fix triggering validation passed")

    def test_no_fix_attempted_when_no_error_occurs(self, fallback_service):
        """Test that no fixes are attempted when no errors occur."""
        print("🧪 Testing No Fix When No Error")
        
        # Create test items with no issues
        test_items = [
            MockClothingItem(
                id="shirt1", name="Cotton T-Shirt", type="shirt", category="top", 
                userId="test_user", material="cotton"
            ),
            MockClothingItem(
                id="pants1", name="Blue Jeans", type="pants", category="bottom", 
                userId="test_user", material="denim"
            )
        ]
        
        context = {
            'user_profile': {'id': 'test_user'},
            'occasion': 'casual',
            'weather': {'temperature_f': 75, 'condition': 'sunny'},
            'style_preferences': ['casual']
        }
        
        healing_context = DynamicHealingContext(context)
        
        # Run weather fix (should not find any issues)
        fixed_items, fixes_applied = asyncio.run(fallback_service._fix_weather_issues(
            test_items, context, healing_context
        ))
        
        # Check that no weather fixes were attempted
        weather_fixes = [f for f in healing_context.fixes_attempted if f.fix_type == FixType.WEATHER_FIX]
        assert len(weather_fixes) == 0, "❌ No weather fix should be attempted when no weather issues exist"
        
        # Check that no weather errors were logged
        weather_errors = [e for e in healing_context.errors_seen if e.error_type == ErrorType.WEATHER_MISMATCH]
        assert len(weather_errors) == 0, "❌ No weather error should be logged when no weather issues exist"
        
        print("✅ No fix when no error validation passed")

    def test_healing_context_persistence_across_passes(self, fallback_service):
        """Test that healing context persists information across multiple healing passes."""
        print("🧪 Testing Healing Context Persistence")
        
        context = {
            'user_profile': {'id': 'test_user'},
            'occasion': 'casual',
            'weather': {'temperature_f': 85, 'condition': 'sunny'},
            'style_preferences': ['casual']
        }
        
        healing_context = DynamicHealingContext(context)
        
        # Simulate first pass
        healing_context.add_error_seen(
            ErrorType.WEATHER_MISMATCH,
            "Test error pass 1",
            item_ids=["item1"]
        )
        healing_context.add_fix_attempted(
            FixType.WEATHER_FIX,
            success=True,
            details={"pass": 1}
        )
        
        # Increment pass
        healing_context.increment_pass()
        
        # Simulate second pass
        healing_context.add_error_seen(
            ErrorType.DUPLICATE_ITEMS,
            "Test error pass 2",
            item_ids=["item2"]
        )
        healing_context.add_fix_attempted(
            FixType.DUPLICATE_FIX,
            success=False,
            details={"pass": 2}
        )
        
        # Validate persistence
        assert len(healing_context.errors_seen) == 2, "❌ Errors should persist across passes"
        assert len(healing_context.fixes_attempted) == 2, "❌ Fixes should persist across passes"
        assert healing_context.healing_pass == 2, "❌ Pass counter should increment"
        
        # Validate pass numbers
        pass1_errors = [e for e in healing_context.errors_seen if e.pass_number == 1]
        pass2_errors = [e for e in healing_context.errors_seen if e.pass_number == 2]
        assert len(pass1_errors) == 1, "❌ Pass 1 errors should be preserved"
        assert len(pass2_errors) == 1, "❌ Pass 2 errors should be recorded"
        
        print("✅ Healing context persistence validation passed")

    def test_healing_context_serialization(self, fallback_service):
        """Test that healing context can be properly serialized to dict."""
        print("🧪 Testing Healing Context Serialization")
        
        context = {
            'user_profile': {'id': 'test_user'},
            'occasion': 'casual',
            'weather': {'temperature_f': 75, 'condition': 'sunny'},
            'style_preferences': ['casual']
        }
        
        healing_context = DynamicHealingContext(context)
        
        # Add some test data
        healing_context.add_error_seen(
            ErrorType.WEATHER_MISMATCH,
            "Test error",
            item_ids=["item1"]
        )
        healing_context.add_fix_attempted(
            FixType.WEATHER_FIX,
            success=True,
            details={"test": "data"}
        )
        
        # Serialize to dict
        serialized = healing_context.get_state()
        
        # Validate serialization
        assert isinstance(serialized, dict), "❌ Serialized context should be a dict"
        assert "session_id" in serialized, "❌ Session ID should be serialized"
        assert "errors_seen" in serialized, "❌ Errors should be serialized"
        assert "fixes_attempted" in serialized, "❌ Fixes should be serialized"
        assert "healing_pass" in serialized, "❌ Pass counter should be serialized"
        
        # Validate error serialization
        errors = serialized["errors_seen"]
        assert isinstance(errors, list), "❌ Serialized errors should be a list"
        if errors:
            error = errors[0]
            assert "error_type" in error, "❌ Serialized error should have error_type"
            assert "details" in error, "❌ Serialized error should have details"
            assert "pass_number" in error, "❌ Serialized error should have pass_number"
        
        # Validate fix serialization
        fixes = serialized["fixes_attempted"]
        assert isinstance(fixes, list), "❌ Serialized fixes should be a list"
        if fixes:
            fix = fixes[0]
            assert "fix_type" in fix, "❌ Serialized fix should have fix_type"
            assert "success" in fix, "❌ Serialized fix should have success"
            assert "pass_number" in fix, "❌ Serialized fix should have pass_number"
        
        print("✅ Healing context serialization validation passed")

def run_regression_tests():
    """Run all regression tests."""
    print("🚀 Starting Fallback System Regression Tests")
    print("=" * 60)
    
    # Create test instance
    test_suite = TestFallbackRegression()
    
    # Run tests
    tests = [
        test_suite.test_healing_context_structure_is_complete,
        test_suite.test_weather_fix_expected_when_weather_error_occurs,
        test_suite.test_duplicate_fix_expected_when_duplicates_occur,
        test_suite.test_no_fix_attempted_when_no_error_occurs,
        test_suite.test_healing_context_persistence_across_passes,
        test_suite.test_healing_context_serialization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} passed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed: {str(e)}")
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All regression tests passed!")
        return True
    else:
        print("⚠️ Some regression tests failed!")
        return False

if __name__ == "__main__":
    success = run_regression_tests()
    sys.exit(0 if success else 1) 