#!/usr/bin/env python3
"""
Test script for enhanced user profile integration with outfit generation.
This script tests that outfit generation properly uses all user profile attributes.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.outfit_service import OutfitService
from models.user_profile import UserProfile
from models.wardrobe_item import WardrobeItem
from data.database import get_database

async def create_test_wardrobe_items() -> List[WardrobeItem]:
    """Create test wardrobe items for testing."""
    items = []
    
    # Test tops
    tops = [
        {
            "id": "top1", "name": "White T-Shirt", "category": "tops", "subcategory": "t-shirts",
            "color": "white", "material": "cotton", "fit": "regular", "brand": "Nike",
            "gender": "female", "style_tags": ["casual", "basic"], "image_url": "test1.jpg"
        },
        {
            "id": "top2", "name": "Black Blouse", "category": "tops", "subcategory": "blouses",
            "color": "black", "material": "silk", "fit": "fitted", "brand": "Zara",
            "gender": "female", "style_tags": ["elegant", "professional"], "image_url": "test2.jpg"
        },
        {
            "id": "top3", "name": "Blue Sweater", "category": "tops", "subcategory": "sweaters",
            "color": "blue", "material": "wool", "fit": "oversized", "brand": "H&M",
            "gender": "female", "style_tags": ["cozy", "casual"], "image_url": "test3.jpg"
        }
    ]
    
    # Test bottoms
    bottoms = [
        {
            "id": "bottom1", "name": "Black Jeans", "category": "bottoms", "subcategory": "jeans",
            "color": "black", "material": "denim", "fit": "skinny", "brand": "Levi's",
            "gender": "female", "style_tags": ["casual", "versatile"], "image_url": "test4.jpg"
        },
        {
            "id": "bottom2", "name": "Gray Pants", "category": "bottoms", "subcategory": "pants",
            "color": "gray", "material": "cotton", "fit": "straight", "brand": "Uniqlo",
            "gender": "female", "style_tags": ["professional", "clean"], "image_url": "test5.jpg"
        },
        {
            "id": "bottom3", "name": "Blue Skirt", "category": "bottoms", "subcategory": "skirts",
            "color": "blue", "material": "cotton", "fit": "a-line", "brand": "Target",
            "gender": "female", "style_tags": ["feminine", "casual"], "image_url": "test6.jpg"
        }
    ]
    
    # Test outerwear
    outerwear = [
        {
            "id": "outer1", "name": "Black Jacket", "category": "outerwear", "subcategory": "jackets",
            "color": "black", "material": "leather", "fit": "fitted", "brand": "AllSaints",
            "gender": "female", "style_tags": ["edgy", "cool"], "image_url": "test7.jpg"
        }
    ]
    
    # Test shoes
    shoes = [
        {
            "id": "shoe1", "name": "White Sneakers", "category": "shoes", "subcategory": "sneakers",
            "color": "white", "material": "canvas", "fit": "regular", "brand": "Converse",
            "gender": "female", "style_tags": ["casual", "comfortable"], "image_url": "test8.jpg"
        }
    ]
    
    # Test accessories
    accessories = [
        {
            "id": "acc1", "name": "Gold Necklace", "category": "accessories", "subcategory": "necklaces",
            "color": "gold", "material": "metal", "fit": "regular", "brand": "Pandora",
            "gender": "female", "style_tags": ["elegant", "minimalist"], "image_url": "test9.jpg"
        }
    ]
    
    all_items = tops + bottoms + outerwear + shoes + accessories
    
    for item_data in all_items:
        item = WardrobeItem(
            id=item_data["id"],
            user_id="test_user",
            name=item_data["name"],
            category=item_data["category"],
            subcategory=item_data["subcategory"],
            color=item_data["color"],
            material=item_data["material"],
            fit=item_data["fit"],
            brand=item_data["brand"],
            gender=item_data["gender"],
            style_tags=item_data["style_tags"],
            image_url=item_data["image_url"],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        items.append(item)
    
    return items

def create_test_user_profiles() -> Dict[str, UserProfile]:
    """Create test user profiles with different levels of detail."""
    
    # Complete female profile with all attributes
    complete_female = UserProfile(
        user_id="test_user_female",
        gender="female",
        body_type="hourglass",
        height=165,
        weight=60,
        skin_tone="medium",
        hair_color="brown",
        eye_color="brown",
        age=28,
        location="New York",
        climate="temperate",
        style_preferences=["elegant", "casual", "minimalist"],
        color_palette=["black", "white", "navy", "gray"],
        avoid_colors=["neon", "bright_pink"],
        material_preferences=["cotton", "silk", "wool"],
        fit_preferences=["fitted", "regular"],
        brand_preferences=["Zara", "H&M", "Uniqlo"],
        budget_range="mid",
        occasion_preferences=["casual", "work", "date"],
        measurements={
            "bust": 34,
            "waist": 28,
            "hips": 36,
            "bra_size": "34B",
            "shoulder_width": 15,
            "arm_length": 24,
            "inseam": 30
        },
        style_personality={
            "classic": 0.7,
            "romantic": 0.3,
            "dramatic": 0.4,
            "natural": 0.6,
            "creative": 0.5
        },
        seasonal_preferences={
            "spring": ["pastels", "light_fabrics"],
            "summer": ["bright_colors", "linen"],
            "fall": ["earth_tones", "layers"],
            "winter": ["dark_colors", "warm_fabrics"]
        }
    )
    
    # Complete male profile
    complete_male = UserProfile(
        user_id="test_user_male",
        gender="male",
        body_type="athletic",
        height=180,
        weight=75,
        skin_tone="medium",
        hair_color="black",
        eye_color="brown",
        age=30,
        location="Los Angeles",
        climate="warm",
        style_preferences=["casual", "athletic", "modern"],
        color_palette=["navy", "gray", "white", "black"],
        avoid_colors=["pink", "purple"],
        material_preferences=["cotton", "polyester", "denim"],
        fit_preferences=["regular", "slim"],
        brand_preferences=["Nike", "Adidas", "Uniqlo"],
        budget_range="mid",
        occasion_preferences=["casual", "work", "gym"],
        measurements={
            "chest": 42,
            "waist": 32,
            "hips": 38,
            "shoulder_width": 18,
            "arm_length": 26,
            "inseam": 32
        },
        style_personality={
            "classic": 0.5,
            "romantic": 0.2,
            "dramatic": 0.6,
            "natural": 0.7,
            "creative": 0.3
        },
        seasonal_preferences={
            "spring": ["light_colors", "breathable_fabrics"],
            "summer": ["bright_colors", "moisture_wicking"],
            "fall": ["earth_tones", "layers"],
            "winter": ["dark_colors", "insulated_fabrics"]
        }
    )
    
    # Minimal profile with basic info only
    minimal_profile = UserProfile(
        user_id="test_user_minimal",
        gender="female",
        body_type="average",
        height=160,
        weight=55,
        skin_tone="light",
        hair_color="blonde",
        eye_color="blue",
        age=25,
        location="Chicago",
        climate="cold",
        style_preferences=["casual"],
        color_palette=["black", "white"],
        avoid_colors=[],
        material_preferences=[],
        fit_preferences=[],
        brand_preferences=[],
        budget_range="low",
        occasion_preferences=["casual"],
        measurements={},
        style_personality={},
        seasonal_preferences={}
    )
    
    return {
        "complete_female": complete_female,
        "complete_male": complete_male,
        "minimal": minimal_profile
    }

async def test_outfit_generation():
    """Test outfit generation with different user profiles."""
    print("🧪 Testing Enhanced User Profile Integration with Outfit Generation")
    print("=" * 70)
    
    # Initialize services
    db = get_database()
    outfit_service = OutfitService(db)
    
    # Create test wardrobe items
    print("\n📦 Creating test wardrobe items...")
    wardrobe_items = await create_test_wardrobe_items()
    print(f"✅ Created {len(wardrobe_items)} test items")
    
    # Create test user profiles
    print("\n👤 Creating test user profiles...")
    user_profiles = create_test_user_profiles()
    print(f"✅ Created {len(user_profiles)} test profiles")
    
    # Test each profile
    for profile_name, profile in user_profiles.items():
        print(f"\n{'='*50}")
        print(f"🧪 Testing Profile: {profile_name.upper()}")
        print(f"{'='*50}")
        
        print(f"Gender: {profile.gender}")
        print(f"Body Type: {profile.body_type}")
        print(f"Style Preferences: {profile.style_preferences}")
        print(f"Color Palette: {profile.color_palette}")
        print(f"Avoid Colors: {profile.avoid_colors}")
        print(f"Material Preferences: {profile.material_preferences}")
        print(f"Fit Preferences: {profile.fit_preferences}")
        print(f"Brand Preferences: {profile.brand_preferences}")
        print(f"Budget: {profile.budget_range}")
        
        if profile.measurements:
            print(f"Measurements: {profile.measurements}")
        
        if profile.style_personality:
            print(f"Style Personality: {profile.style_personality}")
        
        # Test outfit generation
        try:
            print(f"\n🎯 Generating outfit for {profile_name}...")
            
            # Create outfit request
            outfit_request = {
                "user_id": profile.user_id,
                "occasion": "casual",
                "weather": {
                    "temperature": 20,
                    "condition": "sunny",
                    "humidity": 50
                },
                "user_profile": profile.dict(),
                "preferences": {
                    "include_accessories": True,
                    "include_outerwear": True,
                    "color_coordination": True
                }
            }
            
            # Generate outfit
            outfit = await outfit_service.generate_outfit(outfit_request)
            
            if outfit:
                print("✅ Outfit generated successfully!")
                print(f"Outfit ID: {outfit.id}")
                print(f"Confidence Score: {outfit.confidence_score}")
                print(f"Style Tags: {outfit.style_tags}")
                print(f"Occasion: {outfit.occasion}")
                print(f"Weather: {outfit.weather}")
                
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
                
                # Check if outfit respects user preferences
                respects_gender = all(item.gender == profile.gender or item.gender == "unisex" for item in outfit.items)
                print(f"  ✅ Respects gender: {respects_gender}")
                
                # Check color compatibility
                outfit_colors = [item.color for item in outfit.items if item.color]
                color_compatible = all(color in profile.color_palette or color not in profile.avoid_colors for color in outfit_colors)
                print(f"  ✅ Color compatible: {color_compatible}")
                
                # Check material preferences
                if profile.material_preferences:
                    outfit_materials = [item.material for item in outfit.items if item.material]
                    material_compatible = any(material in profile.material_preferences for material in outfit_materials)
                    print(f"  ✅ Material compatible: {material_compatible}")
                
                # Check brand preferences
                if profile.brand_preferences:
                    outfit_brands = [item.brand for item in outfit.items if item.brand]
                    brand_compatible = any(brand in profile.brand_preferences for brand in outfit_brands)
                    print(f"  ✅ Brand compatible: {brand_compatible}")
                
            else:
                print("❌ Failed to generate outfit")
                
        except Exception as e:
            print(f"❌ Error generating outfit: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("🎉 Enhanced User Profile Integration Test Complete!")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(test_outfit_generation()) 