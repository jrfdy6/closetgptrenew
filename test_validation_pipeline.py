#!/usr/bin/env python3
"""
Test script for the Outfit Validation Pipeline
==============================================

This script demonstrates the validation pipeline in action with various
test cases to show how it catches inappropriate outfit combinations.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_validation_pipeline import validation_pipeline, ValidationContext

async def test_validation_pipeline():
    """Test the validation pipeline with various outfit scenarios"""
    
    print("🧪 Testing Outfit Validation Pipeline")
    print("=" * 50)
    
    # Test Case 1: Formal outfit with inappropriate items
    print("\n📋 Test Case 1: Formal outfit with sneakers and jersey")
    formal_outfit = {
        "items": [
            {"name": "Dress Shirt", "type": "shirt", "color": "white"},
            {"name": "Dress Pants", "type": "pants", "color": "black"},
            {"name": "Nike Sneakers", "type": "shoes", "color": "white"},
            {"name": "Basketball Jersey", "type": "top", "color": "red"}
        ]
    }
    
    formal_context = ValidationContext(
        occasion="Business Formal",
        style="Classic",
        mood="Professional",
        weather={"temperature": 72, "condition": "clear"},
        user_profile={"id": "test_user"},
        temperature=72.0
    )
    
    result = await validation_pipeline.validate_outfit(formal_outfit, formal_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 2: Hot weather with heavy clothing
    print("\n📋 Test Case 2: Hot weather with heavy winter coat")
    hot_weather_outfit = {
        "items": [
            {"name": "T-Shirt", "type": "shirt", "color": "blue"},
            {"name": "Shorts", "type": "bottoms", "color": "khaki"},
            {"name": "Winter Parka", "type": "coat", "material": "down", "color": "black"},
            {"name": "Sneakers", "type": "shoes", "color": "white"}
        ]
    }
    
    hot_context = ValidationContext(
        occasion="Casual",
        style="Casual",
        mood="Relaxed",
        weather={"temperature": 85, "condition": "sunny"},
        user_profile={"id": "test_user"},
        temperature=85.0
    )
    
    result = await validation_pipeline.validate_outfit(hot_weather_outfit, hot_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 3: Cold weather with shorts
    print("\n📋 Test Case 3: Cold weather with shorts")
    cold_weather_outfit = {
        "items": [
            {"name": "T-Shirt", "type": "shirt", "color": "white"},
            {"name": "Shorts", "type": "bottoms", "color": "blue"},
            {"name": "Sneakers", "type": "shoes", "color": "black"}
        ]
    }
    
    cold_context = ValidationContext(
        occasion="Casual",
        style="Casual",
        mood="Relaxed",
        weather={"temperature": 35, "condition": "cold"},
        user_profile={"id": "test_user"},
        temperature=35.0
    )
    
    result = await validation_pipeline.validate_outfit(cold_weather_outfit, cold_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 4: Perfect formal outfit
    print("\n📋 Test Case 4: Perfect formal outfit")
    perfect_formal_outfit = {
        "items": [
            {"name": "Dress Shirt", "type": "shirt", "color": "white"},
            {"name": "Dress Pants", "type": "pants", "color": "navy"},
            {"name": "Oxford Shoes", "type": "shoes", "color": "black"},
            {"name": "Blazer", "type": "jacket", "color": "navy"}
        ]
    }
    
    perfect_context = ValidationContext(
        occasion="Business Formal",
        style="Classic",
        mood="Professional",
        weather={"temperature": 70, "condition": "clear"},
        user_profile={"id": "test_user"},
        temperature=70.0
    )
    
    result = await validation_pipeline.validate_outfit(perfect_formal_outfit, perfect_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 5: Minimalist style with too many items
    print("\n📋 Test Case 5: Minimalist style with too many items")
    maximalist_minimalist_outfit = {
        "items": [
            {"name": "T-Shirt", "type": "shirt", "color": "white"},
            {"name": "Jeans", "type": "pants", "color": "blue"},
            {"name": "Sneakers", "type": "shoes", "color": "white"},
            {"name": "Watch", "type": "accessory", "color": "silver"},
            {"name": "Bracelet", "type": "accessory", "color": "gold"},
            {"name": "Necklace", "type": "accessory", "color": "silver"},
            {"name": "Hat", "type": "accessory", "color": "black"}
        ]
    }
    
    minimalist_context = ValidationContext(
        occasion="Casual",
        style="Minimalist",
        mood="Serene",
        weather={"temperature": 75, "condition": "clear"},
        user_profile={"id": "test_user"},
        temperature=75.0
    )
    
    result = await validation_pipeline.validate_outfit(maximalist_minimalist_outfit, minimalist_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Print validation statistics
    print("\n📊 Validation Statistics")
    print("=" * 30)
    stats = validation_pipeline.get_validation_stats()
    print(f"Total validations: {stats['total_validations']}")
    print(f"Failed validations: {stats['failed_validations']}")
    print(f"Success rate: {((stats['total_validations'] - stats['failed_validations']) / stats['total_validations'] * 100):.1f}%")
    print(f"Common failures: {stats['common_failures']}")

if __name__ == "__main__":
    asyncio.run(test_validation_pipeline())
