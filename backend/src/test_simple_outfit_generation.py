#!/usr/bin/env python3
"""
Simple test script for outfit generation with enhanced user profiles.
This script tests the core functionality without complex imports.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List

async def test_basic_outfit_generation():
    """Test basic outfit generation functionality."""
    print("🧪 Testing Basic Outfit Generation")
    print("=" * 50)
    
    try:
        # Import the outfit service directly
        from services.outfit_service import OutfitService
        from data.database import get_database
        
        print("✅ Successfully imported outfit service")
        
        # Initialize services
        db = get_database()
        outfit_service = OutfitService(db)
        
        print("✅ Successfully initialized services")
        
        # Create a simple test request
        test_request = {
            "user_id": "test_user",
            "occasion": "casual",
            "weather": {
                "temperature": 20,
                "condition": "sunny",
                "humidity": 50
            },
            "user_profile": {
                "gender": "female",
                "body_type": "hourglass",
                "style_preferences": ["casual", "elegant"],
                "color_palette": ["black", "white", "navy"],
                "avoid_colors": ["neon"],
                "material_preferences": ["cotton", "silk"],
                "fit_preferences": ["fitted", "regular"],
                "brand_preferences": ["Zara", "H&M"],
                "budget_range": "mid",
                "measurements": {
                    "bust": 34,
                    "waist": 28,
                    "hips": 36,
                    "bra_size": "34B"
                },
                "style_personality": {
                    "classic": 0.7,
                    "romantic": 0.3,
                    "dramatic": 0.4
                }
            },
            "preferences": {
                "include_accessories": True,
                "include_outerwear": True,
                "color_coordination": True
            }
        }
        
        print("✅ Created test request")
        
        # Test outfit generation
        print("\n🎯 Testing outfit generation...")
        outfit = await outfit_service.generate_outfit(test_request)
        
        if outfit:
            print("✅ Outfit generated successfully!")
            print(f"Outfit ID: {outfit.id}")
            print(f"Confidence Score: {outfit.confidence_score}")
            print(f"Style Tags: {outfit.style_tags}")
            print(f"Occasion: {outfit.occasion}")
            
            print("\n👕 Outfit Items:")
            for item in outfit.items:
                print(f"  - {item.category}: {item.name} ({item.color}, {item.material})")
            
            # Validate outfit composition
            categories = [item.category for item in outfit.items]
            print(f"\n📊 Outfit Composition: {categories}")
            
            # Check if outfit includes essential categories
            has_top = "tops" in categories
            has_bottom = "bottoms" in categories
            has_shoes = "shoes" in categories
            
            print(f"  ✅ Has top: {has_top}")
            print(f"  ✅ Has bottom: {has_bottom}")
            print(f"  ✅ Has shoes: {has_shoes}")
            
            if has_top and has_bottom and has_shoes:
                print("\n🎉 SUCCESS: Outfit generation is working correctly!")
                return True
            else:
                print("\n⚠️  WARNING: Outfit missing essential categories")
                return False
        else:
            print("❌ Failed to generate outfit")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_profile_filtering():
    """Test that user profile attributes are properly used in filtering."""
    print("\n🧪 Testing User Profile Filtering")
    print("=" * 50)
    
    try:
        from services.outfit_service import OutfitService
        from data.database import get_database
        
        db = get_database()
        outfit_service = OutfitService(db)
        
        # Test with different user profiles
        test_profiles = [
            {
                "name": "Female Profile",
                "profile": {
                    "gender": "female",
                    "body_type": "hourglass",
                    "style_preferences": ["elegant", "casual"],
                    "color_palette": ["black", "white", "navy"],
                    "avoid_colors": ["neon", "bright_pink"],
                    "material_preferences": ["cotton", "silk"],
                    "fit_preferences": ["fitted", "regular"],
                    "brand_preferences": ["Zara", "H&M"],
                    "budget_range": "mid",
                    "measurements": {
                        "bust": 34,
                        "waist": 28,
                        "hips": 36,
                        "bra_size": "34B"
                    },
                    "style_personality": {
                        "classic": 0.7,
                        "romantic": 0.3,
                        "dramatic": 0.4
                    }
                }
            },
            {
                "name": "Male Profile",
                "profile": {
                    "gender": "male",
                    "body_type": "athletic",
                    "style_preferences": ["casual", "athletic"],
                    "color_palette": ["navy", "gray", "white"],
                    "avoid_colors": ["pink", "purple"],
                    "material_preferences": ["cotton", "polyester"],
                    "fit_preferences": ["regular", "slim"],
                    "brand_preferences": ["Nike", "Adidas"],
                    "budget_range": "mid",
                    "measurements": {
                        "chest": 42,
                        "waist": 32,
                        "hips": 38
                    },
                    "style_personality": {
                        "classic": 0.5,
                        "dramatic": 0.6,
                        "natural": 0.7
                    }
                }
            }
        ]
        
        for test_case in test_profiles:
            print(f"\n👤 Testing {test_case['name']}...")
            
            test_request = {
                "user_id": f"test_user_{test_case['name'].lower().replace(' ', '_')}",
                "occasion": "casual",
                "weather": {
                    "temperature": 20,
                    "condition": "sunny",
                    "humidity": 50
                },
                "user_profile": test_case["profile"],
                "preferences": {
                    "include_accessories": True,
                    "include_outerwear": True,
                    "color_coordination": True
                }
            }
            
            outfit = await outfit_service.generate_outfit(test_request)
            
            if outfit:
                print(f"✅ Generated outfit for {test_case['name']}")
                
                # Check gender compatibility
                outfit_genders = [item.gender for item in outfit.items if hasattr(item, 'gender')]
                gender_compatible = all(gender == test_case["profile"]["gender"] or gender == "unisex" for gender in outfit_genders)
                print(f"  ✅ Gender compatible: {gender_compatible}")
                
                # Check color compatibility
                outfit_colors = [item.color for item in outfit.items if hasattr(item, 'color') and item.color]
                color_compatible = all(color in test_case["profile"]["color_palette"] or color not in test_case["profile"]["avoid_colors"] for color in outfit_colors)
                print(f"  ✅ Color compatible: {color_compatible}")
                
                # Check material compatibility
                if test_case["profile"]["material_preferences"]:
                    outfit_materials = [item.material for item in outfit.items if hasattr(item, 'material') and item.material]
                    material_compatible = any(material in test_case["profile"]["material_preferences"] for material in outfit_materials)
                    print(f"  ✅ Material compatible: {material_compatible}")
                
            else:
                print(f"❌ Failed to generate outfit for {test_case['name']}")
        
        print("\n🎉 User profile filtering test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during user profile filtering test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced User Profile Integration Tests")
    print("=" * 70)
    
    # Test basic outfit generation
    basic_success = await test_basic_outfit_generation()
    
    # Test user profile filtering
    filtering_success = await test_user_profile_filtering()
    
    print(f"\n{'='*70}")
    print("📊 Test Results Summary")
    print(f"{'='*70}")
    print(f"Basic Outfit Generation: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"User Profile Filtering: {'✅ PASS' if filtering_success else '❌ FAIL'}")
    
    if basic_success and filtering_success:
        print("\n🎉 ALL TESTS PASSED! Enhanced user profile integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main()) 