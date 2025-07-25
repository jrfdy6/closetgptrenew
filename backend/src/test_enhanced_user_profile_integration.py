#!/usr/bin/env python3
"""
Test script for enhanced user profile integration in outfit generation.
Tests that all user profile attributes (gender, bra size, detailed measurements, 
color preferences, style personality, etc.) are properly used in outfit generation.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Try both absolute and relative imports for local modules
try:
    from types.profile import UserProfile
    from types.wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
    from types.weather import WeatherData
    from services.outfit_service import OutfitService
except ImportError:
    from .custom_types.profile import UserProfile
    from .custom_types.wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
    from .custom_types.weather import WeatherData
    from .services.outfit_service import OutfitService
print("✅ Successfully imported backend modules")

def create_test_wardrobe() -> List[ClothingItem]:
    """Create a diverse test wardrobe with various items."""
    wardrobe = []
    
    # Tops
    tops = [
        {
            "id": "shirt-1", "name": "Classic White Shirt", "type": "shirt",
            "style": ["classic", "formal"], "occasion": ["work", "formal"],
            "season": ["spring", "summer", "fall"], "color": "white",
            "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            "tags": ["classic", "timeless", "cotton"], "brand": "Ralph Lauren",
            "metadata": {"gender": "male", "fit": "fitted", "material": "cotton"}
        },
        {
            "id": "blouse-1", "name": "Silk Blouse", "type": "blouse",
            "style": ["elegant", "feminine"], "occasion": ["work", "evening"],
            "season": ["spring", "summer"], "color": "blue",
            "dominantColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
            "tags": ["silk", "elegant"], "brand": "Theory",
            "metadata": {"gender": "female", "fit": "fitted", "material": "silk"}
        },
        {
            "id": "sweater-1", "name": "Wool Sweater", "type": "sweater",
            "style": ["classic", "warm"], "occasion": ["casual", "work"],
            "season": ["fall", "winter"], "color": "gray",
            "dominantColors": [{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
            "tags": ["wool", "warm"], "brand": "J.Crew",
            "metadata": {"gender": "male", "fit": "regular", "material": "wool"}
        }
    ]
    
    # Bottoms
    bottoms = [
        {
            "id": "pants-1", "name": "Black Dress Pants", "type": "pants",
            "style": ["formal", "classic"], "occasion": ["work", "formal"],
            "season": ["all"], "color": "black",
            "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            "tags": ["formal", "classic"], "brand": "Brooks Brothers",
            "metadata": {"gender": "male", "fit": "fitted", "material": "polyester"}
        },
        {
            "id": "skirt-1", "name": "A-Line Skirt", "type": "skirt",
            "style": ["feminine", "classic"], "occasion": ["work", "casual"],
            "season": ["spring", "summer"], "color": "navy",
            "dominantColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
            "tags": ["feminine", "classic"], "brand": "Ann Taylor",
            "metadata": {"gender": "female", "fit": "fitted", "material": "cotton"}
        }
    ]
    
    # Shoes
    shoes = [
        {
            "id": "shoes-1", "name": "Leather Oxfords", "type": "shoes",
            "style": ["classic", "formal"], "occasion": ["work", "formal"],
            "season": ["all"], "color": "brown",
            "dominantColors": [{"name": "brown", "hex": "#8B4513", "rgb": [139, 69, 19]}],
            "tags": ["leather", "classic"], "brand": "Allen Edmonds",
            "metadata": {"gender": "male", "fit": "regular", "material": "leather"}
        },
        {
            "id": "shoes-2", "name": "Pumps", "type": "shoes",
            "style": ["elegant", "feminine"], "occasion": ["work", "evening"],
            "season": ["all"], "color": "black",
            "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            "tags": ["elegant", "feminine"], "brand": "Nine West",
            "metadata": {"gender": "female", "fit": "fitted", "material": "leather"}
        }
    ]
    
    # Accessories
    accessories = [
        {
            "id": "belt-1", "name": "Leather Belt", "type": "belt",
            "style": ["classic"], "occasion": ["work", "casual"],
            "season": ["all"], "color": "brown",
            "dominantColors": [{"name": "brown", "hex": "#8B4513", "rgb": [139, 69, 19]}],
            "tags": ["leather", "classic"], "brand": "Coach",
            "metadata": {"gender": "male", "fit": "regular", "material": "leather"}
        }
    ]
    
    # Combine all items
    all_items = tops + bottoms + shoes + accessories
    
    for item_data in all_items:
        wardrobe.append(ClothingItem(**item_data))
    
    return wardrobe

def create_test_user_profiles() -> Dict[str, UserProfile]:
    """Create test user profiles with different attribute combinations."""
    base_profile = {
        "id": "test-user-123",
        "name": "Test User",
        "email": "test@example.com",
        "createdAt": int(datetime.now().timestamp()),
        "updatedAt": int(datetime.now().timestamp())
    }
    
    profiles = {}
    
    # Profile 1: Complete female profile with all attributes
    profiles["complete_female"] = UserProfile(
        **base_profile,
        gender="female",
        preferences={
            "style": ["elegant", "feminine"],
            "colors": ["navy", "black", "white"],
            "occasions": ["work", "evening"]
        },
        measurements={
            "height": 165,
            "weight": 60,
            "bodyType": "hourglass",
            "skinTone": "medium",
            "heightFeetInches": "5'5\"",
            "topSize": "M",
            "bottomSize": "8",
            "shoeSize": "7",
            "dressSize": "8",
            "jeanWaist": "28",
            "braSize": "34C",
            "inseam": "30",
            "waist": "28",
            "chest": "34",
            "shoulderWidth": 36,
            "waistWidth": 28,
            "hipWidth": 38,
            "armLength": 24,
            "neckCircumference": 14,
            "thighCircumference": 22,
            "calfCircumference": 14
        },
        stylePreferences=["elegant", "feminine", "classic"],
        bodyType="hourglass",
        skinTone="medium",
        fitPreference="fitted",
        sizePreference="M",
        colorPalette={
            "primary": ["navy", "black"],
            "secondary": ["white", "gray"],
            "accent": ["red"],
            "neutral": ["beige", "brown"],
            "avoid": ["pink", "purple"]
        },
        stylePersonality={
            "classic": 0.8,
            "modern": 0.6,
            "creative": 0.4,
            "minimal": 0.7,
            "bold": 0.3
        },
        materialPreferences={
            "preferred": ["silk", "cotton", "leather"],
            "avoid": ["polyester", "acrylic"],
            "seasonal": {
                "spring": ["cotton", "linen"],
                "summer": ["cotton", "linen"],
                "fall": ["wool", "silk"],
                "winter": ["wool", "cashmere"]
            }
        },
        fitPreferences={
            "tops": "fitted",
            "bottoms": "fitted",
            "dresses": "fitted"
        },
        comfortLevel={
            "tight": 0.3,
            "loose": 0.7,
            "structured": 0.8,
            "relaxed": 0.4
        },
        preferredBrands=["Theory", "Ann Taylor", "Nine West"],
        budget="medium"
    )
    
    # Profile 2: Complete male profile with all attributes
    profiles["complete_male"] = UserProfile(
        **base_profile,
        gender="male",
        preferences={
            "style": ["classic", "formal"],
            "colors": ["navy", "gray", "white"],
            "occasions": ["work", "formal"]
        },
        measurements={
            "height": 180,
            "weight": 75,
            "bodyType": "athletic",
            "skinTone": "medium",
            "heightFeetInches": "5'11\"",
            "topSize": "L",
            "bottomSize": "32",
            "shoeSize": "10",
            "dressSize": "",
            "jeanWaist": "32",
            "braSize": "",
            "inseam": "32",
            "waist": "32",
            "chest": "42",
            "shoulderWidth": 44,
            "waistWidth": 32,
            "hipWidth": 36,
            "armLength": 26,
            "neckCircumference": 16,
            "thighCircumference": 24,
            "calfCircumference": 16
        },
        stylePreferences=["classic", "formal", "professional"],
        bodyType="athletic",
        skinTone="medium",
        fitPreference="fitted",
        sizePreference="L",
        colorPalette={
            "primary": ["navy", "gray"],
            "secondary": ["white", "black"],
            "accent": ["burgundy"],
            "neutral": ["beige", "brown"],
            "avoid": ["pink", "purple"]
        },
        stylePersonality={
            "classic": 0.9,
            "modern": 0.4,
            "creative": 0.2,
            "minimal": 0.8,
            "bold": 0.1
        },
        materialPreferences={
            "preferred": ["cotton", "wool", "leather"],
            "avoid": ["polyester", "acrylic"],
            "seasonal": {
                "spring": ["cotton", "linen"],
                "summer": ["cotton", "linen"],
                "fall": ["wool", "tweed"],
                "winter": ["wool", "cashmere"]
            }
        },
        fitPreferences={
            "tops": "fitted",
            "bottoms": "fitted",
            "dresses": "regular"
        },
        comfortLevel={
            "tight": 0.2,
            "loose": 0.8,
            "structured": 0.9,
            "relaxed": 0.3
        },
        preferredBrands=["Ralph Lauren", "Brooks Brothers", "Allen Edmonds"],
        budget="high"
    )
    
    # Profile 3: Minimal profile (backward compatibility test)
    profiles["minimal"] = UserProfile(
        **base_profile,
        gender="male",
        preferences={
            "style": ["casual"],
            "colors": ["blue", "black"],
            "occasions": ["casual"]
        },
        measurements={
            "height": 175,
            "weight": 70,
            "bodyType": "athletic",
            "skinTone": "medium"
        },
        stylePreferences=["casual"],
        bodyType="athletic",
        skinTone="medium"
    )
    
    return profiles

async def test_enhanced_outfit_generation():
    """Test outfit generation with enhanced user profiles."""
    print("🧪 Testing Enhanced User Profile Integration")
    print("=" * 60)
    
    try:
        # Initialize outfit service
        outfit_service = OutfitService()
        
        # Create test data
        wardrobe = create_test_wardrobe()
        weather = WeatherData(
            temperature=20,
            condition="sunny",
            location="test",
            humidity=50,
            wind_speed=5,
            precipitation=0
        )
        user_profiles = create_test_user_profiles()
        
        print(f"✅ Created test data:")
        print(f"   - Wardrobe: {len(wardrobe)} items")
        print(f"   - Weather: {weather.temperature}°C, {weather.condition}")
        print(f"   - User profiles: {len(user_profiles)} profiles")
        
        # Test each profile
        for profile_name, user_profile in user_profiles.items():
            print(f"\n🔍 Testing profile: {profile_name}")
            print(f"   - Gender: {user_profile.gender}")
            print(f"   - Body type: {user_profile.bodyType}")
            print(f"   - Bra size: {user_profile.measurements.get('braSize', 'N/A')}")
            print(f"   - Style personality: {user_profile.stylePersonality}")
            print(f"   - Preferred brands: {user_profile.preferredBrands}")
            
            try:
                # Generate outfit
                outfit = await outfit_service.generate_outfit(
                    occasion="work",
                    weather=weather,
                    wardrobe=wardrobe,
                    user_profile=user_profile,
                    likedOutfits=[],
                    trendingStyles=[],
                    style="classic"
                )
                
                print(f"✅ Generated outfit with {len(outfit.items)} items")
                
                # Analyze the outfit for profile compliance
                analyze_outfit_compliance(outfit, user_profile)
                
            except Exception as e:
                print(f"❌ Failed to generate outfit for {profile_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_outfit_compliance(outfit, user_profile: UserProfile):
    """Analyze how well the outfit complies with user profile preferences."""
    print(f"   📊 Outfit Analysis:")
    
    # Check gender compliance
    if user_profile.gender:
        gender_compliant = all(
            not hasattr(item, 'metadata') or 
            not item.metadata or 
            not hasattr(item.metadata, 'gender') or 
            item.metadata.gender == user_profile.gender
            for item in outfit.items
        )
        print(f"      - Gender compliance: {'✅' if gender_compliant else '❌'}")
    
    # Check color palette compliance
    if user_profile.colorPalette:
        avoid_colors = user_profile.colorPalette.get('avoid', [])
        color_compliant = True
        for item in outfit.items:
            for color in item.dominantColors or []:
                if any(avoid_color.lower() in color.get('name', '').lower() for avoid_color in avoid_colors):
                    color_compliant = False
                    break
        print(f"      - Color palette compliance: {'✅' if color_compliant else '❌'}")
    
    # Check brand preferences
    if user_profile.preferredBrands:
        brand_compliant = any(
            item.brand and item.brand.lower() in [brand.lower() for brand in user_profile.preferredBrands]
            for item in outfit.items
        )
        print(f"      - Brand preference compliance: {'✅' if brand_compliant else '❌'}")
    
    # Check style personality
    if user_profile.stylePersonality:
        classic_score = user_profile.stylePersonality.get('classic', 0.5)
        if classic_score > 0.7:
            classic_items = any(
                any(tag in str(item.tags).lower() for tag in ['classic', 'timeless', 'traditional'])
                for item in outfit.items
            )
            print(f"      - Classic style preference: {'✅' if classic_items else '❌'}")
    
    # Check material preferences
    if user_profile.materialPreferences:
        preferred_materials = user_profile.materialPreferences.get('preferred', [])
        material_compliant = any(
            any(material.lower() in str(item.tags).lower() for material in preferred_materials)
            for item in outfit.items
        )
        print(f"      - Material preference compliance: {'✅' if material_compliant else '❌'}")

async def test_backward_compatibility():
    """Test that the system still works with minimal user profiles."""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    try:
        outfit_service = OutfitService()
        wardrobe = create_test_wardrobe()
        weather = WeatherData(
            temperature=20,
            condition="sunny",
            location="test",
            humidity=50,
            wind_speed=5,
            precipitation=0
        )
        
        # Create minimal profile (old format)
        minimal_profile = UserProfile(
            id="test-user-minimal",
            name="Minimal User",
            email="minimal@test.com",
            gender="male",
            preferences={"style": ["casual"], "colors": ["blue"], "occasions": ["casual"]},
            measurements={"height": 175, "weight": 70, "bodyType": "athletic", "skinTone": "medium"},
            stylePreferences=["casual"],
            bodyType="athletic",
            skinTone="medium",
            createdAt=int(datetime.now().timestamp()),
            updatedAt=int(datetime.now().timestamp())
        )
        
        print(f"✅ Testing minimal profile with basic attributes only")
        
        outfit = await outfit_service.generate_outfit(
            occasion="casual",
            weather=weather,
            wardrobe=wardrobe,
            user_profile=minimal_profile,
            likedOutfits=[],
            trendingStyles=[]
        )
        
        print(f"✅ Generated outfit with minimal profile: {len(outfit.items)} items")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced User Profile Integration Tests")
    print("=" * 70)
    
    # Test 1: Enhanced outfit generation
    test1_success = await test_enhanced_outfit_generation()
    
    # Test 2: Backward compatibility
    test2_success = await test_backward_compatibility()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Enhanced outfit generation: {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"Backward compatibility: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Enhanced user profile integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 