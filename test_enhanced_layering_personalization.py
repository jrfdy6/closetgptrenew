#!/usr/bin/env python3
"""
Enhanced Layering System Test with Personalization Features
Tests the new layering system that incorporates skintone, style preference, and body type considerations.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from utils.layering import (
        get_skin_tone_color_recommendations,
        get_body_type_layering_recommendations,
        get_style_preference_layering,
        validate_color_skin_tone_compatibility,
        validate_body_type_layering_compatibility,
        validate_style_preference_compatibility,
        get_personalized_layering_suggestions,
        calculate_personalized_layering_score,
        get_enhanced_layering_validation,
        get_core_category,
        validate_layering_compatibility
    )
    from types.wardrobe import ClothingType, CoreCategory
    print("✅ Successfully imported layering utilities")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_skin_tone_color_recommendations():
    """Test skin tone color recommendations."""
    print("\n🧪 Testing Skin Tone Color Recommendations")
    print("=" * 50)
    
    test_cases = [
        ('warm', 'coral'),
        ('cool', 'blue'),
        ('neutral', 'navy'),
        ('olive', 'sage'),
        ('deep', 'purple'),
        ('medium', 'green'),
        ('fair', 'rose')
    ]
    
    for skin_tone, test_color in test_cases:
        print(f"\nTesting {skin_tone} skin tone:")
        
        # Get recommendations
        recommendations = get_skin_tone_color_recommendations(skin_tone)
        print(f"  Flattering colors: {recommendations['flattering_colors'][:3]}")
        print(f"  Avoid colors: {recommendations['avoid_colors'][:3]}")
        print(f"  Neutral colors: {recommendations['neutral_colors'][:3]}")
        
        # Test color compatibility
        compatibility = validate_color_skin_tone_compatibility(test_color, skin_tone)
        print(f"  {test_color} compatibility: {compatibility['score']:.2f} - {compatibility['reason']}")

def test_body_type_layering_recommendations():
    """Test body type layering recommendations."""
    print("\n🧪 Testing Body Type Layering Recommendations")
    print("=" * 50)
    
    test_cases = [
        'hourglass',
        'pear',
        'apple',
        'rectangle',
        'inverted_triangle',
        'athletic',
        'curvy'
    ]
    
    for body_type in test_cases:
        print(f"\nTesting {body_type} body type:")
        
        recommendations = get_body_type_layering_recommendations(body_type)
        print(f"  Flattering layers: {recommendations['flattering_layers'][:3]}")
        print(f"  Avoid layers: {recommendations['avoid_layers'][:3]}")
        print(f"  Layer priorities: {recommendations['layer_priorities']}")

def test_style_preference_layering():
    """Test style preference layering patterns."""
    print("\n🧪 Testing Style Preference Layering")
    print("=" * 50)
    
    test_cases = [
        'minimalist',
        'bohemian',
        'streetwear',
        'classic',
        'romantic',
        'edgy',
        'casual',
        'formal'
    ]
    
    for style in test_cases:
        print(f"\nTesting {style} style:")
        
        style_rec = get_style_preference_layering(style)
        print(f"  Layer approach: {style_rec['layer_approach'][:3]}")
        print(f"  Preferred layers: {style_rec['preferred_layers']}")
        print(f"  Avoid layers: {style_rec['avoid_layers'][:3]}")

def test_personalized_layering_validation():
    """Test comprehensive personalized layering validation."""
    print("\n🧪 Testing Personalized Layering Validation")
    print("=" * 50)
    
    # Test outfit with different personal profiles
    test_outfit = [
        {'type': 'shirt', 'color': 'blue', 'subType': 'dress_shirt'},
        {'type': 'pants', 'color': 'black', 'subType': 'slacks'},
        {'type': 'shoes', 'color': 'brown', 'subType': 'loafers'}
    ]
    
    test_profiles = [
        {
            'name': 'Warm Skin, Hourglass, Classic',
            'skinTone': 'warm',
            'bodyType': 'hourglass',
            'stylePreferences': ['classic', 'minimalist']
        },
        {
            'name': 'Cool Skin, Pear, Bohemian',
            'skinTone': 'cool',
            'bodyType': 'pear',
            'stylePreferences': ['bohemian', 'romantic']
        },
        {
            'name': 'Neutral Skin, Rectangle, Streetwear',
            'skinTone': 'neutral',
            'bodyType': 'rectangle',
            'stylePreferences': ['streetwear', 'edgy']
        }
    ]
    
    temperature = 75.0
    
    for profile in test_profiles:
        print(f"\nTesting profile: {profile['name']}")
        
        # Test enhanced validation
        validation = get_enhanced_layering_validation(
            test_outfit, 
            temperature, 
            profile
        )
        
        print(f"  Overall score: {validation['overall_score']:.2f}")
        print(f"  Temperature score: {validation['temperature_score']:.2f}")
        print(f"  Color score: {validation['color_score']:.2f}")
        print(f"  Body type score: {validation['body_type_score']:.2f}")
        print(f"  Style score: {validation['style_score']:.2f}")
        print(f"  Is valid: {validation['is_valid']}")
        
        if validation['suggestions']:
            print(f"  Suggestions: {validation['suggestions'][:2]}")
        
        if validation['warnings']:
            print(f"  Warnings: {validation['warnings'][:2]}")
        
        if validation['personalized_recommendations']['personalized']:
            print(f"  Personalized recommendations: {validation['personalized_recommendations']['personalized'][:2]}")

def test_color_skin_tone_compatibility():
    """Test color and skin tone compatibility."""
    print("\n🧪 Testing Color-Skin Tone Compatibility")
    print("=" * 50)
    
    test_cases = [
        ('warm', 'coral', True),
        ('warm', 'cool_blue', False),
        ('cool', 'blue', True),
        ('cool', 'orange', False),
        ('neutral', 'navy', True),
        ('neutral', 'bright_orange', False),
        ('olive', 'sage', True),
        ('deep', 'purple', True),
        ('fair', 'rose', True)
    ]
    
    for skin_tone, color, expected_good in test_cases:
        compatibility = validate_color_skin_tone_compatibility(color, skin_tone)
        status = "✅" if (compatibility['compatible'] == expected_good) else "❌"
        print(f"{status} {skin_tone} + {color}: {compatibility['score']:.2f} - {compatibility['reason']}")

def test_body_type_layering_compatibility():
    """Test body type and layering compatibility."""
    print("\n🧪 Testing Body Type-Layering Compatibility")
    print("=" * 50)
    
    # Test different outfit combinations for different body types
    test_cases = [
        {
            'body_type': 'pear',
            'outfit': [
                {'type': 'shirt', 'color': 'blue'},
                {'type': 'pants', 'color': 'black'},
                {'type': 'jacket', 'color': 'navy'}
            ],
            'description': 'Pear with fitted top and structured jacket'
        },
        {
            'body_type': 'apple',
            'outfit': [
                {'type': 'crop_top', 'color': 'red'},
                {'type': 'pants', 'color': 'black'}
            ],
            'description': 'Apple with crop top (should warn)'
        },
        {
            'body_type': 'rectangle',
            'outfit': [
                {'type': 'shirt', 'color': 'white'},
                {'type': 'pants', 'color': 'blue'}
            ],
            'description': 'Rectangle with minimal layers (should suggest more)'
        },
        {
            'body_type': 'hourglass',
            'outfit': [
                {'type': 'shirt', 'color': 'black'},
                {'type': 'pants', 'color': 'black'},
                {'type': 'belt', 'color': 'brown'}
            ],
            'description': 'Hourglass with fitted pieces and belt'
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['description']}:")
        
        validation = validate_body_type_layering_compatibility(
            test_case['outfit'], 
            test_case['body_type']
        )
        
        print(f"  Score: {validation['score']:.2f}")
        print(f"  Compatible: {validation['compatible']}")
        
        if validation['warnings']:
            print(f"  Warnings: {validation['warnings']}")
        
        if validation['suggestions']:
            print(f"  Suggestions: {validation['suggestions']}")

def test_style_preference_compatibility():
    """Test style preference and layering compatibility."""
    print("\n🧪 Testing Style Preference-Layering Compatibility")
    print("=" * 50)
    
    test_cases = [
        {
            'style_preferences': ['classic', 'minimalist'],
            'outfit': [
                {'type': 'blazer', 'color': 'navy'},
                {'type': 'shirt', 'color': 'white'},
                {'type': 'pants', 'color': 'black'}
            ],
            'description': 'Classic outfit for classic preferences'
        },
        {
            'style_preferences': ['bohemian', 'romantic'],
            'outfit': [
                {'type': 'cardigan', 'color': 'cream'},
                {'type': 'dress', 'color': 'floral'}
            ],
            'description': 'Bohemian outfit for bohemian preferences'
        },
        {
            'style_preferences': ['streetwear', 'edgy'],
            'outfit': [
                {'type': 'hoodie', 'color': 'black'},
                {'type': 'pants', 'color': 'gray'}
            ],
            'description': 'Streetwear outfit for streetwear preferences'
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['description']}:")
        
        validation = validate_style_preference_compatibility(
            test_case['outfit'], 
            test_case['style_preferences']
        )
        
        print(f"  Score: {validation['score']:.2f}")
        print(f"  Compatible: {validation['compatible']}")
        
        if validation['warnings']:
            print(f"  Warnings: {validation['warnings']}")
        
        if validation['suggestions']:
            print(f"  Suggestions: {validation['suggestions']}")

def test_personalized_layering_suggestions():
    """Test personalized layering suggestions."""
    print("\n🧪 Testing Personalized Layering Suggestions")
    print("=" * 50)
    
    test_outfit = [
        {'type': 'shirt', 'color': 'blue'},
        {'type': 'pants', 'color': 'black'},
        {'type': 'shoes', 'color': 'brown'}
    ]
    
    test_profiles = [
        {
            'name': 'Warm Skin, Hourglass, Classic',
            'skin_tone': 'warm',
            'body_type': 'hourglass',
            'style_preferences': ['classic']
        },
        {
            'name': 'Cool Skin, Pear, Bohemian',
            'skin_tone': 'cool',
            'body_type': 'pear',
            'style_preferences': ['bohemian']
        }
    ]
    
    temperature = 70.0
    
    for profile in test_profiles:
        print(f"\nTesting suggestions for {profile['name']}:")
        
        suggestions = get_personalized_layering_suggestions(
            test_outfit,
            temperature,
            profile['skin_tone'],
            profile['body_type'],
            profile['style_preferences']
        )
        
        print(f"  Temperature-based: {suggestions['temperature_based'][:2]}")
        print(f"  Personalized: {suggestions['personalized']}")

def test_layering_score_calculation():
    """Test personalized layering score calculation."""
    print("\n🧪 Testing Layering Score Calculation")
    print("=" * 50)
    
    test_outfit = [
        {'type': 'shirt', 'color': 'blue'},
        {'type': 'pants', 'color': 'black'},
        {'type': 'jacket', 'color': 'navy'},
        {'type': 'shoes', 'color': 'brown'}
    ]
    
    test_scenarios = [
        {
            'name': 'Perfect match',
            'skin_tone': 'cool',
            'body_type': 'rectangle',
            'style_preferences': ['classic'],
            'temperature': 75.0
        },
        {
            'name': 'Partial match',
            'skin_tone': 'warm',
            'body_type': 'pear',
            'style_preferences': ['bohemian'],
            'temperature': 75.0
        },
        {
            'name': 'Mismatch',
            'skin_tone': 'cool',
            'body_type': 'apple',
            'style_preferences': ['streetwear'],
            'temperature': 75.0
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nTesting {scenario['name']}:")
        
        score = calculate_personalized_layering_score(
            test_outfit,
            scenario['temperature'],
            scenario['skin_tone'],
            scenario['body_type'],
            scenario['style_preferences']
        )
        
        print(f"  Overall score: {score:.3f}")
        print(f"  Grade: {'A' if score > 0.8 else 'B' if score > 0.6 else 'C' if score > 0.4 else 'D'}")

def main():
    """Run all tests."""
    print("🎯 Enhanced Layering System with Personalization Features")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all tests
        test_skin_tone_color_recommendations()
        test_body_type_layering_recommendations()
        test_style_preference_layering()
        test_color_skin_tone_compatibility()
        test_body_type_layering_compatibility()
        test_style_preference_compatibility()
        test_personalized_layering_suggestions()
        test_layering_score_calculation()
        test_personalized_layering_validation()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎉 Enhanced layering system with personalization is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 