#!/usr/bin/env python3
"""
Test the fixed outfit generation to verify it prevents duplicates and ensures essentials
"""

import asyncio
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.firebase import db
from src.services.outfit_service import OutfitService
from src.custom_types.wardrobe import ClothingItem
from src.custom_types.outfit import OutfitGeneratedOutfit
import random

class FixedOutfitTester:
    """Test the fixed outfit generation logic."""
    
    def __init__(self):
        self.outfit_service = OutfitService()
        self.user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
    async def get_user_wardrobe(self):
        """Get user's wardrobe."""
        try:
            print(f"Fetching wardrobe for user: {self.user_id}")
            wardrobe_ref = db.collection('wardrobe')
            wardrobe_query = wardrobe_ref.where('userId', '==', self.user_id)
            docs = wardrobe_query.stream()
            
            wardrobe = []
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                try:
                    clothing_item = ClothingItem(**item_data)
                    wardrobe.append(clothing_item)
                except Exception as e:
                    continue
            
            print(f"Found {len(wardrobe)} wardrobe items")
            return wardrobe
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def analyze_outfit(self, outfit, occasion):
        """Analyze outfit for issues."""
        issues = []
        if not outfit or not outfit.items:
            return ["NO_ITEMS"]
        
        item_types = [item.type.lower() for item in outfit.items]
        item_names = [item.name.lower() for item in outfit.items]
        
        # Check for duplicates
        type_counts = {}
        for item_type in item_types:
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        for item_type, count in type_counts.items():
            if count > 1:
                issues.append(f"DUPLICATE_{item_type.upper()}")
        
        # Check for missing essentials
        if "shirt" not in item_types:
            issues.append("MISSING_SHIRT")
        if "pants" not in item_types and "shorts" not in item_types and "skirt" not in item_types and "other" not in item_types:
            issues.append("MISSING_BOTTOMS")
        if "shoes" not in item_types:
            issues.append("MISSING_SHOES")
        
        # Check for inappropriate items
        occasion_lower = occasion.lower()
        if "work" in occasion_lower and any("shorts" in name for name in item_names):
            issues.append("INAPPROPRIATE_SHORTS_FOR_WORK")
        if "athletic" in occasion_lower and any("dress" in name for name in item_names):
            issues.append("INAPPROPRIATE_FORMAL_FOR_ATHLETIC")
        
        return issues
    
    async def test_fixed_generation(self, wardrobe):
        """Test the fixed outfit generation."""
        print("\n" + "="*60)
        print("TESTING FIXED OUTFIT GENERATION")
        print("="*60)
        
        test_occasions = ["Work", "Casual", "Athletic", "Party", "Formal", "Errands", "Brunch"]
        test_styles = ["Casual", "Formal", "Athletic"]
        test_moods = ["Relaxed", "Confident", "Energetic"]
        
        total_tests = 0
        passing_tests = 0
        
        for i in range(10):  # Test 10 outfits
            total_tests += 1
            occasion = random.choice(test_occasions)
            style = random.choice(test_styles)
            mood = random.choice(test_moods)
            
            print(f"\n🔄 Test {i+1}")
            print(f"📋 {occasion} | 🎨 {style} | 😊 {mood}")
            
            try:
                # Create mock data
                from src.custom_types.weather import WeatherData
                from src.custom_types.profile import UserProfile
                
                weather = WeatherData(temperature=70.0, condition="sunny", humidity=50.0, wind_speed=5.0)
                user_profile = UserProfile(
                    id=self.user_id, name="Test User", email="test@example.com",
                    bodyType="athletic", createdAt=int(time.time()), updatedAt=int(time.time())
                )
                
                # Generate outfit
                outfit = await self.outfit_service.generate_outfit(
                    occasion=occasion, weather=weather, wardrobe=wardrobe,
                    user_profile=user_profile, likedOutfits=[], trendingStyles=[],
                    style=style, mood=mood
                )
                
                if outfit and outfit.items:
                    print(f"👕 {len(outfit.items)} items:")
                    for item in outfit.items:
                        print(f"  - {item.name} ({item.type})")
                    
                    # Analyze
                    issues = self.analyze_outfit(outfit, occasion)
                    
                    if not issues:
                        passing_tests += 1
                        print(f"✅ PASS! ({passing_tests}/{total_tests})")
                    else:
                        print(f"❌ FAIL: {issues}")
                else:
                    print("❌ No outfit generated")
                    
            except Exception as e:
                print(f"💥 Error: {e}")
        
        success_rate = (passing_tests / total_tests) * 100
        print(f"\n📊 Final Results:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passing tests: {passing_tests}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 SUCCESS: Fixed outfit generation is working well!")
        else:
            print("⚠️  WARNING: Still some issues to address")

async def main():
    """Main function."""
    tester = FixedOutfitTester()
    wardrobe = await tester.get_user_wardrobe()
    
    if not wardrobe:
        print("No wardrobe items found!")
        return
    
    await tester.test_fixed_generation(wardrobe)

if __name__ == "__main__":
    asyncio.run(main()) 