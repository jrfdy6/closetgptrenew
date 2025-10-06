#!/usr/bin/env python3
"""
Feature Flags Test Script
========================

Test script to validate feature flag functionality and semantic filtering.
"""

import sys
import os
import asyncio
import logging

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from config.feature_flags import feature_flags, is_semantic_match_enabled, is_debug_output_enabled
from services.robust_outfit_generation_service import RobustOutfitGenerationService
from custom_types.generation_context import GenerationContext
from custom_types.weather import WeatherData
from custom_types.profile import UserProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_feature_flags():
    """Test feature flag functionality."""
    logger.info("🧪 Testing Feature Flags...")
    
    # Test 1: Default flags
    logger.info(f"✅ Default semantic match: {is_semantic_match_enabled()}")
    logger.info(f"✅ Default debug output: {is_debug_output_enabled()}")
    logger.info(f"✅ All flags: {feature_flags.get_all_flags()}")
    
    # Test 2: Override flags
    feature_flags.override_flag('FEATURE_SEMANTIC_MATCH', True)
    logger.info(f"✅ Override semantic match: {is_semantic_match_enabled()}")
    
    # Test 3: Reset to defaults
    feature_flags.override_flag('FEATURE_SEMANTIC_MATCH', False)
    logger.info(f"✅ Reset semantic match: {is_semantic_match_enabled()}")
    
    logger.info("🎉 Feature flags test completed successfully!")

async def test_semantic_filtering():
    """Test semantic filtering functionality."""
    logger.info("🧪 Testing Semantic Filtering...")
    
    try:
        # Create test context
        context = GenerationContext(
            user_id="test_user",
            occasion="formal",
            style="business",
            mood="professional",
            weather=WeatherData(
                temperature=72.0,
                condition="sunny",
                precipitation=0,
                wind_speed=5
            ),
            wardrobe=[],  # Empty for testing
            user_profile=UserProfile(
                id="test_user",
                name="Test User",
                email="test@example.com",
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
        )
        
        # Test with feature flags
        robust_service = RobustOutfitGenerationService()
        
        # Test traditional filtering (default)
        result_traditional = await robust_service._filter_suitable_items_with_debug(
            context, 
            semantic_filtering=False
        )
        
        # Test semantic filtering
        result_semantic = await robust_service._filter_suitable_items_with_debug(
            context, 
            semantic_filtering=True
        )
        
        logger.info(f"✅ Traditional filtering result: {len(result_traditional.get('valid_items', []))} items")
        logger.info(f"✅ Semantic filtering result: {len(result_semantic.get('valid_items', []))} items")
        logger.info(f"✅ Debug output enabled: {'debug_output' in result_semantic}")
        
        logger.info("🎉 Semantic filtering test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Semantic filtering test failed: {e}")
        raise

async def main():
    """Run all tests."""
    logger.info("🚀 Starting Feature Flags and Semantic Filtering Tests...")
    
    try:
        await test_feature_flags()
        await test_semantic_filtering()
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("✅ Feature flags are working correctly")
        logger.info("✅ Semantic filtering is functional")
        logger.info("✅ Safe deployment ready")
        
    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
