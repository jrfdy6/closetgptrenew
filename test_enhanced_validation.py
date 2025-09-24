#!/usr/bin/env python3
"""
Test script for Enhanced Validation Rules
========================================

This script tests the enhanced validation rules to ensure they catch
inappropriate outfit combinations and provide helpful suggestions.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_validation_pipeline import validation_pipeline, ValidationContext

async def test_enhanced_validation_rules():
    """Test the enhanced validation rules with various scenarios"""
    
    print("🧪 Testing Enhanced Validation Rules")
    print("=" * 60)
    
    # Test Case 1: Formal outfit with sneakers (should fail with explicit blacklist)
    print("\n📋 Test Case 1: Formal outfit with sneakers (BLACKLIST TEST)")
    formal_outfit = {
        "items": [
            {"name": "Dress Shirt", "type": "shirt", "color": "white"},
            {"name": "Dress Pants", "type": "pants", "color": "black"},
            {"name": "Nike Sneakers", "type": "shoes", "color": "white"},
            {"name": "Blazer", "type": "jacket", "color": "navy"}
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
    
    # Test Case 2: Hot weather with heavy coat (should fail at 75°F threshold)
    print("\n📋 Test Case 2: Hot weather with heavy coat (75°F THRESHOLD TEST)")
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
        weather={"temperature": 78, "condition": "sunny"},  # Above 75°F threshold
        user_profile={"id": "test_user"},
        temperature=78.0
    )
    
    result = await validation_pipeline.validate_outfit(hot_weather_outfit, hot_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 3: Minimalist style with too many items (should fail)
    print("\n📋 Test Case 3: Minimalist style with too many items (STYLE RULES TEST)")
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
    
    # Test Case 4: Perfect formal outfit (should pass with positive reinforcement)
    print("\n📋 Test Case 4: Perfect formal outfit (POSITIVE REINFORCEMENT TEST)")
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
    
    # Test Case 5: Borderline temperature with lightweight blazer (should allow)
    print("\n📋 Test Case 5: Borderline temperature with lightweight blazer (GRADUATED THRESHOLDS TEST)")
    borderline_outfit = {
        "items": [
            {"name": "Button-Up Shirt", "type": "shirt", "color": "light blue"},
            {"name": "Chinos", "type": "pants", "color": "khaki"},
            {"name": "Lightweight Blazer", "type": "jacket", "material": "cotton", "color": "beige"},
            {"name": "Loafers", "type": "shoes", "color": "brown"}
        ]
    }
    
    borderline_context = ValidationContext(
        occasion="Business Casual",
        style="Classic",
        mood="Professional",
        weather={"temperature": 73, "condition": "clear"},  # Just above 75°F threshold
        user_profile={"id": "test_user"},
        temperature=73.0
    )
    
    result = await validation_pipeline.validate_outfit(borderline_outfit, borderline_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")
    
    # Test Case 6: Maximalist style with too few items (should fail)
    print("\n📋 Test Case 6: Maximalist style with too few items (STYLE RULES TEST)")
    minimal_maximalist_outfit = {
        "items": [
            {"name": "T-Shirt", "type": "shirt", "color": "white"},
            {"name": "Jeans", "type": "pants", "color": "blue"},
            {"name": "Sneakers", "type": "shoes", "color": "white"}
        ]
    }
    
    maximalist_context = ValidationContext(
        occasion="Casual",
        style="Maximalist",
        mood="Bold",
        weather={"temperature": 75, "condition": "clear"},
        user_profile={"id": "test_user"},
        temperature=75.0
    )
    
    result = await validation_pipeline.validate_outfit(minimal_maximalist_outfit, maximalist_context)
    print(f"✅ Valid: {result.valid}")
    print(f"❌ Errors: {result.errors}")
    print(f"⚠️ Warnings: {result.warnings}")
    print(f"💡 Suggestions: {result.suggestions}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_validation_rules())
