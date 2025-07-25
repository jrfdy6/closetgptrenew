#!/usr/bin/env python3
"""
Test script to demonstrate the new layering approach with core category mapping
and subtype/tags for outfit generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.types.wardrobe import ClothingType, CoreCategory, LayerLevel, WarmthFactor
from backend.src.utils.layering import (
    get_core_category, get_layer_level, get_warmth_factor, 
    can_layer, get_max_layers, get_layering_rule,
    validate_layering_compatibility, get_layering_suggestions
)

def test_core_category_mapping():
    """Test core category mapping for different clothing types."""
    print("=== Testing Core Category Mapping ===")
    
    test_cases = [
        # Tops
        (ClothingType.SHIRT, "shirt"),
        (ClothingType.T_SHIRT, "t-shirt"),
        (ClothingType.BLOUSE, "blouse"),
        (ClothingType.SWEATER, "sweater"),
        (ClothingType.HOODIE, "hoodie"),
        (ClothingType.CARDIGAN, "cardigan"),
        
        # Bottoms
        (ClothingType.PANTS, "pants"),
        (ClothingType.JEANS, "jeans"),
        (ClothingType.SHORTS, "shorts"),
        (ClothingType.SKIRT, "skirt"),
        
        # Dresses
        (ClothingType.DRESS, "dress"),
        (ClothingType.SUNDRESS, "sundress"),
        
        # Outerwear
        (ClothingType.JACKET, "jacket"),
        (ClothingType.BLAZER, "blazer"),
        (ClothingType.COAT, "coat"),
        
        # Shoes
        (ClothingType.SHOES, "shoes"),
        (ClothingType.SNEAKERS, "sneakers"),
        (ClothingType.BOOTS, "boots"),
        
        # Accessories
        (ClothingType.ACCESSORY, "accessory"),
        (ClothingType.HAT, "hat"),
        (ClothingType.SCARF, "scarf"),
    ]
    
    for clothing_type, name in test_cases:
        category = get_core_category(clothing_type)
        print(f"{name:15} -> {category.value}")
    
    print()

def test_layer_level_mapping():
    """Test layer level mapping for different clothing types."""
    print("=== Testing Layer Level Mapping ===")
    
    test_cases = [
        # Base layers
        (ClothingType.T_SHIRT, "t-shirt"),
        (ClothingType.TANK_TOP, "tank top"),
        
        # Inner layers
        (ClothingType.SHIRT, "shirt"),
        (ClothingType.BLOUSE, "blouse"),
        
        # Middle layers
        (ClothingType.SWEATER, "sweater"),
        (ClothingType.CARDIGAN, "cardigan"),
        
        # Outer layers
        (ClothingType.JACKET, "jacket"),
        (ClothingType.COAT, "coat"),
    ]
    
    for clothing_type, name in test_cases:
        layer_level = get_layer_level(clothing_type)
        print(f"{name:15} -> {layer_level.value}")
    
    print()

def test_warmth_factor_mapping():
    """Test warmth factor mapping for different clothing types."""
    print("=== Testing Warmth Factor Mapping ===")
    
    test_cases = [
        # Light items
        (ClothingType.T_SHIRT, "t-shirt"),
        (ClothingType.SHORTS, "shorts"),
        (ClothingType.SANDALS, "sandals"),
        
        # Medium items
        (ClothingType.SHIRT, "shirt"),
        (ClothingType.PANTS, "pants"),
        (ClothingType.SWEATER, "sweater"),
        
        # Heavy items
        (ClothingType.JACKET, "jacket"),
        (ClothingType.COAT, "coat"),
    ]
    
    for clothing_type, name in test_cases:
        warmth_factor = get_warmth_factor(clothing_type)
        print(f"{name:15} -> {warmth_factor.value}")
    
    print()

def test_layering_capabilities():
    """Test layering capabilities for different clothing types."""
    print("=== Testing Layering Capabilities ===")
    
    test_cases = [
        (ClothingType.T_SHIRT, "t-shirt"),
        (ClothingType.SHIRT, "shirt"),
        (ClothingType.SWEATER, "sweater"),
        (ClothingType.JACKET, "jacket"),
        (ClothingType.PANTS, "pants"),
        (ClothingType.SHOES, "shoes"),
    ]
    
    for clothing_type, name in test_cases:
        can_layer_item = can_layer(clothing_type)
        max_layers = get_max_layers(clothing_type)
        print(f"{name:15} -> Can layer: {can_layer_item}, Max layers: {max_layers}")
    
    print()

def test_temperature_based_layering():
    """Test temperature-based layering rules."""
    print("=== Testing Temperature-Based Layering ===")
    
    temperatures = [20, 40, 60, 70, 80, 90]
    
    for temp in temperatures:
        rule = get_layering_rule(temp)
        print(f"{temp}°F: {rule['min_layers']}-{rule['max_layers']} layers, "
              f"preferred warmth: {[w.value for w in rule['preferred_warmth']]}")
        print(f"  Notes: {rule['notes']}")
    
    print()

def test_layering_validation():
    """Test layering validation for different outfits."""
    print("=== Testing Layering Validation ===")
    
    # Test case 1: Cold weather outfit
    cold_outfit = [
        {"type": "t-shirt"},
        {"type": "sweater"},
        {"type": "jacket"},
        {"type": "pants"},
        {"type": "boots"}
    ]
    
    validation = validate_layering_compatibility(cold_outfit, 30)
    print(f"Cold weather outfit (30°F):")
    print(f"  Valid: {validation['is_valid']}")
    print(f"  Errors: {validation['errors']}")
    print(f"  Warnings: {validation['warnings']}")
    
    # Test case 2: Hot weather outfit
    hot_outfit = [
        {"type": "t-shirt"},
        {"type": "shorts"},
        {"type": "sandals"}
    ]
    
    validation = validate_layering_compatibility(hot_outfit, 85)
    print(f"\nHot weather outfit (85°F):")
    print(f"  Valid: {validation['is_valid']}")
    print(f"  Errors: {validation['errors']}")
    print(f"  Warnings: {validation['warnings']}")
    
    # Test case 3: Inappropriate outfit for weather
    inappropriate_outfit = [
        {"type": "t-shirt"},
        {"type": "shorts"},
        {"type": "sandals"}
    ]
    
    validation = validate_layering_compatibility(inappropriate_outfit, 20)
    print(f"\nInappropriate outfit (20°F):")
    print(f"  Valid: {validation['is_valid']}")
    print(f"  Errors: {validation['errors']}")
    print(f"  Warnings: {validation['warnings']}")
    
    print()

def test_layering_suggestions():
    """Test layering suggestions for different outfits."""
    print("=== Testing Layering Suggestions ===")
    
    # Test case 1: Insufficient layers for cold weather
    insufficient_outfit = [
        {"type": "t-shirt"},
        {"type": "pants"},
        {"type": "shoes"}
    ]
    
    suggestions = get_layering_suggestions(insufficient_outfit, 25)
    print(f"Outfit with insufficient layers (25°F):")
    print(f"  Suggestions: {suggestions}")
    
    # Test case 2: Missing required categories
    incomplete_outfit = [
        {"type": "pants"},
        {"type": "shoes"}
    ]
    
    suggestions = get_layering_suggestions(incomplete_outfit, 70)
    print(f"\nIncomplete outfit (70°F):")
    print(f"  Suggestions: {suggestions}")
    
    print()

def test_comprehensive_outfit_example():
    """Test a comprehensive outfit example with the new layering approach."""
    print("=== Comprehensive Outfit Example ===")
    
    # Example: Winter outfit with proper layering
    winter_outfit = [
        {"type": "t-shirt", "name": "Cotton T-shirt"},
        {"type": "sweater", "name": "Wool Sweater"},
        {"type": "jacket", "name": "Winter Jacket"},
        {"type": "pants", "name": "Warm Pants"},
        {"type": "boots", "name": "Winter Boots"},
        {"type": "scarf", "name": "Warm Scarf"}
    ]
    
    print("Winter Outfit Analysis:")
    print("Items:")
    for item in winter_outfit:
        clothing_type = ClothingType(item["type"])
        category = get_core_category(clothing_type)
        layer_level = get_layer_level(clothing_type)
        warmth_factor = get_warmth_factor(clothing_type)
        can_layer_item = can_layer(clothing_type)
        
        print(f"  {item['name']:20} | Category: {category.value:10} | "
              f"Layer: {layer_level.value:8} | Warmth: {warmth_factor.value:8} | "
              f"Can layer: {can_layer_item}")
    
    # Validate the outfit
    validation = validate_layering_compatibility(winter_outfit, 25)
    print(f"\nValidation (25°F):")
    print(f"  Valid: {validation['is_valid']}")
    print(f"  Errors: {validation['errors']}")
    print(f"  Warnings: {validation['warnings']}")
    
    # Get suggestions
    suggestions = get_layering_suggestions(winter_outfit, 25)
    print(f"  Suggestions: {suggestions}")
    
    print()

def main():
    """Run all tests."""
    print("Testing New Layering Approach with Core Category Mapping")
    print("=" * 60)
    print()
    
    test_core_category_mapping()
    test_layer_level_mapping()
    test_warmth_factor_mapping()
    test_layering_capabilities()
    test_temperature_based_layering()
    test_layering_validation()
    test_layering_suggestions()
    test_comprehensive_outfit_example()
    
    print("All tests completed!")

if __name__ == "__main__":
    main() 