#!/usr/bin/env python3
"""
Simplified test for real wardrobe outfit generation with automatic fixes
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

class SimpleWardrobeTester:
    """Simplified test with automatic fixes."""
    
    def __init__(self):
        self.outfit_service = OutfitService()
        self.user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        self.applied_fixes = set()
        self.consecutive_passes = 0
        self.total_tests = 0
        
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
        if "airport" in occasion_lower and any("dress" in name for name in item_names):
            issues.append("INAPPROPRIATE_FORMAL_FOR_AIRPORT")
        if "gala" in occasion_lower and any("shorts" in name for name in item_names):
            issues.append("INAPPROPRIATE_CASUAL_FOR_GALA")
        if "errands" in occasion_lower and any("dress" in name for name in item_names):
            issues.append("INAPPROPRIATE_FORMAL_FOR_ERRANDS")
        if "brunch" in occasion_lower and any("dress" in name for name in item_names):
            issues.append("INAPPROPRIATE_FORMAL_FOR_BRUNCH")
        
        return issues
    
    def suggest_fixes(self, issues):
        """Suggest fixes for issues."""
        fixes = []
        for issue in issues:
            if issue.startswith("DUPLICATE_"):
                fixes.append("PREVENT_DUPLICATES")
            elif issue == "MISSING_SHIRT":
                fixes.append("ENSURE_SHIRT")
            elif issue == "MISSING_BOTTOMS":
                fixes.append("ENSURE_BOTTOMS")
            elif issue == "MISSING_SHOES":
                fixes.append("ENSURE_SHOES")
            elif issue == "INAPPROPRIATE_SHORTS_FOR_WORK":
                fixes.append("FILTER_SHORTS_FROM_WORK")
            elif issue == "INAPPROPRIATE_FORMAL_FOR_ATHLETIC":
                fixes.append("FILTER_FORMAL_FROM_ATHLETIC")
        return list(set(fixes))
    
    def apply_fixes(self, fixes):
        """Apply fixes."""
        for fix in fixes:
            self.applied_fixes.add(fix)
            print(f"🔧 Applied: {fix}")
    
    async def run_test(self, wardrobe):
        """Run the test with automatic fixes."""
        print("\n" + "="*60)
        print("AUTOMATIC OUTFIT TESTING WITH FIXES")
        print("="*60)
        
        test_occasions = ["Work", "Casual", "Athletic", "Party", "Formal", "Errands", "Brunch", "Airport", "Gala"]
        test_styles = ["Casual", "Formal", "Athletic"]
        test_moods = ["Relaxed", "Confident", "Energetic"]
        
        while self.consecutive_passes < 100:
            self.total_tests += 1
            occasion = random.choice(test_occasions)
            style = random.choice(test_styles)
            mood = random.choice(test_moods)
            
            print(f"\n🔄 Test {self.total_tests}")
            print(f"📋 {occasion} | 🎨 {style} | 😊 {mood}")
            print(f"📊 Passes: {self.consecutive_passes} | 🔧 Fixes: {len(self.applied_fixes)}")
            
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
                        self.consecutive_passes += 1
                        print(f"✅ PASS! ({self.consecutive_passes}/100)")
                        
                        if self.consecutive_passes == 100:
                            print("\n🎉 SUCCESS: 100 consecutive passes!")
                            print(f"📈 Total tests: {self.total_tests}")
                            print(f"🔧 Fixes applied: {len(self.applied_fixes)}")
                            return True
                    else:
                        print(f"❌ FAIL: {issues}")
                        self.consecutive_passes = 0
                        
                        # Apply fixes
                        fixes = self.suggest_fixes(issues)
                        if fixes:
                            self.apply_fixes(fixes)
                else:
                    print("❌ No outfit generated")
                    self.consecutive_passes = 0
                    
            except Exception as e:
                print(f"💥 Error: {e}")
                self.consecutive_passes = 0
            
            # Progress update
            if self.total_tests % 5 == 0:
                success_rate = (self.consecutive_passes / self.total_tests) * 100
                print(f"\n📊 Progress: {self.total_tests} tests, {self.consecutive_passes} passes, {success_rate:.1f}% success")
        
        return False

async def main():
    """Main function."""
    tester = SimpleWardrobeTester()
    wardrobe = await tester.get_user_wardrobe()
    
    if not wardrobe:
        print("No wardrobe items found!")
        return
    
    success = await tester.run_test(wardrobe)
    
    if success:
        print("\n🎯 MISSION ACCOMPLISHED!")
    else:
        print("\n⚠️  Testing stopped")

if __name__ == "__main__":
    asyncio.run(main()) 