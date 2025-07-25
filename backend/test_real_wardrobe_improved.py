#!/usr/bin/env python3
"""
Improved autonomous tester for real wardrobe outfit generation
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

class ImprovedWardrobeTester:
    """Improved test with better analysis and handling."""
    
    def __init__(self):
        self.outfit_service = OutfitService()
        self.user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        self.consecutive_passes = 0
        self.total_tests = 0
        self.failure_patterns = {}  # Track failure patterns
        
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
    
    def normalize_item_type(self, item):
        """Normalize item types for consistent analysis."""
        type_lower = item.type.lower()
        name_lower = item.name.lower()
        
        # Normalize footwear types
        if any(footwear in type_lower or footwear in name_lower for footwear in [
            "shoes", "sneakers", "boots", "sandals", "flats", "heels", "oxford", "loafers", 
            "toe shoes", "footwear", "foot wear"
        ]):
            return "shoes"
        
        # Normalize top types
        if any(top in type_lower or top in name_lower for top in [
            "shirt", "t-shirt", "tshirt", "blouse", "sweater", "hoodie", "jacket", "coat",
            "top", "upper", "shirt"
        ]):
            return "shirt"
        
        # Normalize bottom types
        if any(bottom in type_lower or bottom in name_lower for bottom in [
            "pants", "trousers", "jeans", "shorts", "skirt", "leggings", "tracksuit",
            "bottom", "lower", "pants", "pleated skirt"
        ]):
            return "pants"
        
        # Normalize accessory types
        if any(accessory in type_lower or accessory in name_lower for accessory in [
            "belt", "watch", "jewelry", "necklace", "bracelet", "ring", "earrings",
            "accessory", "accessories", "belt"
        ]):
            return "accessory"
        
        # Normalize outerwear types
        if any(outerwear in type_lower or outerwear in name_lower for outerwear in [
            "jacket", "coat", "blazer", "suit jacket", "cardigan", "sweater",
            "outerwear", "jacket"
        ]):
            return "jacket"
        
        # Return original type if no normalization applies
        return type_lower
    
    def analyze_outfit_improved(self, outfit, occasion):
        """Improved outfit analysis with better logic."""
        issues = []
        if not outfit or not outfit.items:
            return ["NO_ITEMS"]
        
        # Use normalized types for better analysis
        normalized_types = [self.normalize_item_type(item) for item in outfit.items]
        item_names = [item.name.lower() for item in outfit.items]
        
        # Check for duplicates using normalized types
        type_counts = {}
        for item_type in normalized_types:
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        for item_type, count in type_counts.items():
            if count > 1:
                issues.append(f"DUPLICATE_{item_type.upper()}")
        
        # Check for missing essentials using normalized types
        if "shirt" not in normalized_types:
            issues.append("MISSING_SHIRT")
        if "pants" not in normalized_types:
            issues.append("MISSING_BOTTOMS")
        if "shoes" not in normalized_types:
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
        
        # Check for poor item balance
        if len(outfit.items) < 3:
            issues.append("TOO_FEW_ITEMS")
        if len(outfit.items) > 6:
            issues.append("TOO_MANY_ITEMS")
        
        return issues
    
    def track_failure_pattern(self, occasion, issues):
        """Track failure patterns to identify systemic issues."""
        if occasion not in self.failure_patterns:
            self.failure_patterns[occasion] = {}
        
        for issue in issues:
            if issue not in self.failure_patterns[occasion]:
                self.failure_patterns[occasion][issue] = 0
            self.failure_patterns[occasion][issue] += 1
    
    def get_wardrobe_stats(self, wardrobe):
        """Get statistics about the wardrobe to understand limitations."""
        type_counts = {}
        for item in wardrobe:
            normalized_type = self.normalize_item_type(item)
            type_counts[normalized_type] = type_counts.get(normalized_type, 0) + 1
        
        return type_counts
    
    async def run_improved_test(self, wardrobe):
        """Run the improved test with better analysis."""
        print("\n" + "="*60)
        print("IMPROVED AUTOMATIC OUTFIT TESTING")
        print("="*60)
        
        # Get wardrobe statistics
        wardrobe_stats = self.get_wardrobe_stats(wardrobe)
        print(f"📊 Wardrobe composition:")
        for item_type, count in sorted(wardrobe_stats.items()):
            print(f"  {item_type}: {count} items")
        
        test_occasions = ["Work", "Casual", "Athletic", "Party", "Formal", "Errands", "Brunch", "Airport", "Gala"]
        test_styles = ["Casual", "Formal", "Athletic"]
        test_moods = ["Relaxed", "Confident", "Energetic"]
        
        max_tests = 1000  # Prevent infinite loops
        consecutive_failures = 0
        
        while self.consecutive_passes < 100 and self.total_tests < max_tests:
            self.total_tests += 1
            occasion = random.choice(test_occasions)
            style = random.choice(test_styles)
            mood = random.choice(test_moods)
            
            print(f"\n🔄 Test {self.total_tests}")
            print(f"📋 {occasion} | 🎨 {style} | 😊 {mood}")
            print(f"📊 Passes: {self.consecutive_passes} | 🔧 Failures: {consecutive_failures}")
            
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
                        normalized_type = self.normalize_item_type(item)
                        print(f"  - {item.name} ({normalized_type})")
                    
                    # Analyze with improved logic
                    issues = self.analyze_outfit_improved(outfit, occasion)
                    
                    if not issues:
                        self.consecutive_passes += 1
                        consecutive_failures = 0
                        print(f"✅ PASS! ({self.consecutive_passes}/100)")
                        
                        if self.consecutive_passes == 100:
                            print("\n🎉 SUCCESS: 100 consecutive passes!")
                            print(f"📈 Total tests: {self.total_tests}")
                            return True
                    else:
                        print(f"❌ FAIL: {issues}")
                        self.consecutive_passes = 0
                        consecutive_failures += 1
                        
                        # Track failure patterns
                        self.track_failure_pattern(occasion, issues)
                        
                        # If we have too many consecutive failures, show analysis
                        if consecutive_failures >= 5:
                            print(f"\n⚠️  {consecutive_failures} consecutive failures. Analyzing patterns...")
                            self.show_failure_analysis()
                            consecutive_failures = 0  # Reset counter
                else:
                    print("❌ No outfit generated")
                    self.consecutive_passes = 0
                    consecutive_failures += 1
                    
            except Exception as e:
                print(f"💥 Error: {e}")
                self.consecutive_passes = 0
                consecutive_failures += 1
            
            # Progress update
            if self.total_tests % 10 == 0:
                success_rate = (self.consecutive_passes / self.total_tests) * 100
                print(f"\n📊 Progress: {self.total_tests} tests, {self.consecutive_passes} passes, {success_rate:.1f}% success")
        
        # Final analysis
        print(f"\n📊 Final Results:")
        print(f"  Total tests: {self.total_tests}")
        print(f"  Consecutive passes: {self.consecutive_passes}")
        print(f"  Success rate: {(self.consecutive_passes / self.total_tests) * 100:.1f}%")
        
        if self.failure_patterns:
            print(f"\n🔍 Failure Analysis:")
            self.show_failure_analysis()
        
        return self.consecutive_passes >= 100
    
    def show_failure_analysis(self):
        """Show analysis of failure patterns."""
        print("📊 Failure Patterns by Occasion:")
        for occasion, issues in self.failure_patterns.items():
            if issues:
                print(f"  {occasion}:")
                for issue, count in sorted(issues.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {issue}: {count} times")

async def main():
    """Main function."""
    tester = ImprovedWardrobeTester()
    wardrobe = await tester.get_user_wardrobe()
    
    if not wardrobe:
        print("No wardrobe items found!")
        return
    
    success = await tester.run_improved_test(wardrobe)
    
    if success:
        print("\n🎯 MISSION ACCOMPLISHED!")
    else:
        print("\n⚠️  Testing stopped - analysis complete")

if __name__ == "__main__":
    asyncio.run(main()) 