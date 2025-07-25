#!/usr/bin/env python3
"""
Simplified Autonomous Outfit Testing Framework
Generates outfits, analyzes them for issues, and automatically fixes logic until quality standards are met.
"""

import asyncio
import random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock classes for testing
class MockClothingItem:
    def __init__(self, id, name, type, style=None, occasion=None):
        self.id = id
        self.name = name
        self.type = type
        self.style = style or []
        self.occasion = occasion or []
        self.dominantColors = []
        self.imageUrl = ""

class MockWeatherData:
    def __init__(self, temperature=20, condition="sunny"):
        self.temperature = temperature
        self.condition = condition

class MockUserProfile:
    def __init__(self, id="test", name="Test User"):
        self.id = id
        self.name = name

class MockOutfitPiece:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class MockOutfit:
    def __init__(self, pieces):
        self.pieces = pieces

class OutfitAnalyzer:
    """Analyzes outfits for common issues and quality problems."""
    
    def __init__(self):
        self.issues_found = []
    
    def analyze_outfit(self, outfit, occasion):
        """Analyze an outfit for common issues."""
        issues = []
        
        # Get item types
        item_types = [piece.type.lower() for piece in outfit.pieces]
        item_names = [piece.name.lower() for piece in outfit.pieces]
        
        # Check for missing essential items
        if "shirt" not in item_types and "blouse" not in item_types:
            issues.append("MISSING_SHIRT")
        
        if "pants" not in item_types and "shorts" not in item_types and "skirt" not in item_types:
            issues.append("MISSING_BOTTOMS")
        
        if "shoes" not in item_types:
            issues.append("MISSING_SHOES")
        
        # Check for duplicate item types
        type_counts = {}
        for item_type in item_types:
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        for item_type, count in type_counts.items():
            if count > 1:
                issues.append(f"DUPLICATE_{item_type.upper()}")
        
        # Check for inappropriate items based on occasion
        occasion_lower = occasion.lower()
        
        if "work" in occasion_lower or "business" in occasion_lower or "office" in occasion_lower:
            if any("shorts" in name for name in item_names):
                issues.append("INAPPROPRIATE_SHORTS_FOR_WORK")
            if any("casual" in name for name in item_names):
                issues.append("INAPPROPRIATE_CASUAL_FOR_WORK")
        
        elif "school" in occasion_lower:
            if any("dress pants" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_SCHOOL")
            if any("dress shirt" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_SCHOOL")
        
        elif "athletic" in occasion_lower or "gym" in occasion_lower:
            if any("dress pants" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_ATHLETIC")
            if any("dress shirt" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_ATHLETIC")
        
        elif "airport" in occasion_lower:
            if any("dress pants" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_AIRPORT")
            if any("formal" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_AIRPORT")
        
        elif "festival" in occasion_lower:
            if any("dress pants" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_FESTIVAL")
            if any("formal" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_FESTIVAL")
        
        elif "gala" in occasion_lower:
            if any("shorts" in name for name in item_names):
                issues.append("INAPPROPRIATE_CASUAL_FOR_GALA")
            if any("t-shirt" in name for name in item_names):
                issues.append("INAPPROPRIATE_CASUAL_FOR_GALA")
        
        elif "errands" in occasion_lower:
            if any("dress pants" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_ERRANDS")
            if any("dress shirt" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_ERRANDS")
            if any("formal" in name for name in item_names):
                issues.append("INAPPROPRIATE_FORMAL_FOR_ERRANDS")
        
        # Check for poor item balance
        if len(item_types) < 3:
            issues.append("TOO_FEW_ITEMS")
        
        if len(item_types) > 6:
            issues.append("TOO_MANY_ITEMS")
        
        # Check for missing shoes when needed
        if "shoes" not in item_types and occasion_lower not in ["beach", "swimming"]:
            issues.append("MISSING_SHOES")
        
        return issues

class LogicFixer:
    """Automatically fixes outfit generation logic based on issues found."""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_logic(self, issues, occasion):
        """Apply fixes to the outfit generation logic based on issues found."""
        fixes = []
        
        for issue in issues:
            if issue == "MISSING_SHIRT":
                fixes.append("IMPROVE_SHIRT_SELECTION")
            
            elif issue == "MISSING_BOTTOMS":
                fixes.append("IMPROVE_BOTTOMS_SELECTION")
            
            elif issue == "MISSING_SHOES":
                fixes.append("IMPROVE_SHOE_SELECTION")
            
            elif issue.startswith("DUPLICATE_"):
                fixes.append("PREVENT_DUPLICATE_ITEMS")
            
            elif issue == "INAPPROPRIATE_SHORTS_FOR_WORK":
                fixes.append("FILTER_SHORTS_FROM_WORK")
            
            elif issue == "INAPPROPRIATE_CASUAL_FOR_WORK":
                fixes.append("FILTER_CASUAL_FROM_WORK")
            
            elif issue == "INAPPROPRIATE_FORMAL_FOR_SCHOOL":
                fixes.append("FILTER_FORMAL_FROM_SCHOOL")
            
            elif issue == "INAPPROPRIATE_FORMAL_FOR_ATHLETIC":
                fixes.append("FILTER_FORMAL_FROM_ATHLETIC")
            
            elif issue == "INAPPROPRIATE_FORMAL_FOR_AIRPORT":
                fixes.append("FILTER_FORMAL_FROM_AIRPORT")
            
            elif issue == "INAPPROPRIATE_FORMAL_FOR_FESTIVAL":
                fixes.append("FILTER_FORMAL_FROM_FESTIVAL")
            
            elif issue == "INAPPROPRIATE_CASUAL_FOR_GALA":
                fixes.append("FILTER_CASUAL_FROM_GALA")
            
            elif issue == "INAPPROPRIATE_FORMAL_FOR_ERRANDS":
                fixes.append("FILTER_FORMAL_FROM_ERRANDS")
        
        return list(set(fixes))  # Remove duplicates

class MockWardrobeGenerator:
    """Generates a realistic mock wardrobe for testing."""
    
    def generate_mock_wardrobe(self):
        """Generate a diverse mock wardrobe for testing."""
        wardrobe = []
        
        # Shirts
        shirts = [
            "Blue Dress Shirt", "White T-Shirt", "Black Button-Down", "Polo Shirt",
            "Casual Blouse", "Formal Blouse", "Athletic Jersey", "Hoodie",
            "Sweater", "Tank Top", "Dress Shirt", "Casual Shirt"
        ]
        
        # Pants
        pants = [
            "Black Dress Pants", "Blue Jeans", "Khaki Pants", "Athletic Shorts",
            "Casual Shorts", "Bermuda Shorts", "Dress Pants", "Sweatpants",
            "Leggings", "Skirt", "Formal Pants", "Casual Pants"
        ]
        
        # Shoes
        shoes = [
            "Black Oxford Shoes", "White Sneakers", "Brown Loafers", "Athletic Shoes",
            "Dress Shoes", "Sandals", "Boots", "Heels", "Casual Shoes",
            "Formal Shoes", "Running Shoes", "Work Shoes"
        ]
        
        # Accessories
        accessories = [
            "Black Belt", "Silver Watch", "Gold Necklace", "Leather Belt",
            "Casual Belt", "Formal Belt", "Bracelet", "Ring", "Earrings"
        ]
        
        # Jackets
        jackets = [
            "Black Blazer", "Casual Jacket", "Formal Jacket", "Athletic Jacket",
            "Winter Coat", "Light Jacket", "Suit Jacket", "Cardigan"
        ]
        
        # Combine all items
        all_items = shirts + pants + shoes + accessories + jackets
        
        for i, name in enumerate(all_items):
            item_type = self._determine_item_type(name)
            wardrobe.append(MockClothingItem(
                id=f"item_{i}",
                name=name,
                type=item_type
            ))
        
        return wardrobe
    
    def _determine_item_type(self, name):
        """Determine item type based on name."""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ["shirt", "blouse", "polo", "jersey", "hoodie", "sweater", "tank"]):
            return "shirt"
        elif any(word in name_lower for word in ["pants", "jeans", "shorts", "sweatpants", "leggings", "skirt"]):
            return "pants"
        elif any(word in name_lower for word in ["shoes", "sneakers", "loafers", "sandals", "boots", "heels"]):
            return "shoes"
        elif any(word in name_lower for word in ["belt", "watch", "necklace", "bracelet", "ring", "earrings"]):
            return "accessory"
        elif any(word in name_lower for word in ["jacket", "blazer", "coat", "cardigan"]):
            return "jacket"
        else:
            return "accessory"

class MockOutfitGenerator:
    """Mock outfit generator that simulates the real outfit generation service."""
    
    def __init__(self):
        self.wardrobe_generator = MockWardrobeGenerator()
        self.applied_fixes = set()  # Track applied fixes
    
    async def generate_outfit(self, wardrobe, occasion, style, mood):
        """Generate a mock outfit based on occasion, style, and mood."""
        # Simulate outfit generation logic with improved filtering
        pieces = []
        
        # Filter wardrobe based on occasion and applied fixes
        filtered_wardrobe = self._filter_wardrobe_for_occasion(wardrobe, occasion)
        
        # Always try to include essential items
        essential_items = ["shirt", "pants", "shoes"]
        
        for item_type in essential_items:
            available_items = [item for item in filtered_wardrobe if item.type.lower() == item_type]
            if available_items:
                selected_item = random.choice(available_items)
                pieces.append(MockOutfitPiece(selected_item.name, selected_item.type))
        
        # Add some accessories if available
        accessory_items = [item for item in filtered_wardrobe if item.type.lower() == "accessory"]
        if accessory_items and len(pieces) < 5:
            selected_accessory = random.choice(accessory_items)
            pieces.append(MockOutfitPiece(selected_accessory.name, selected_accessory.type))
        
        # Add jacket if available and appropriate
        jacket_items = [item for item in filtered_wardrobe if item.type.lower() == "jacket"]
        if jacket_items and len(pieces) < 5:
            selected_jacket = random.choice(jacket_items)
            pieces.append(MockOutfitPiece(selected_jacket.name, selected_jacket.type))
        
        return MockOutfit(pieces)
    
    def _filter_wardrobe_for_occasion(self, wardrobe, occasion):
        """Filter wardrobe based on occasion and applied fixes."""
        occasion_lower = occasion.lower()
        filtered_wardrobe = wardrobe.copy()
        
        # Apply occasion-specific filtering based on applied fixes
        if "FILTER_FORMAL_FROM_AIRPORT" in self.applied_fixes and "airport" in occasion_lower:
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["dress", "formal", "suit"])]
        
        if "FILTER_FORMAL_FROM_FESTIVAL" in self.applied_fixes and "festival" in occasion_lower:
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["dress", "formal", "suit"])]
        
        if "FILTER_FORMAL_FROM_SCHOOL" in self.applied_fixes and "school" in occasion_lower:
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["dress", "formal"])]
        
        if "FILTER_FORMAL_FROM_ATHLETIC" in self.applied_fixes and ("athletic" in occasion_lower or "gym" in occasion_lower):
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["dress", "formal"])]
        
        if "FILTER_CASUAL_FROM_WORK" in self.applied_fixes and ("work" in occasion_lower or "business" in occasion_lower or "office" in occasion_lower):
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["casual", "t-shirt", "hoodie"])]
        
        if "FILTER_SHORTS_FROM_WORK" in self.applied_fixes and ("work" in occasion_lower or "business" in occasion_lower or "office" in occasion_lower):
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["shorts"])]
        
        if "FILTER_CASUAL_FROM_GALA" in self.applied_fixes and "gala" in occasion_lower:
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["casual", "t-shirt", "shorts"])]
        
        if "FILTER_FORMAL_FROM_ERRANDS" in self.applied_fixes and "errands" in occasion_lower:
            filtered_wardrobe = [item for item in filtered_wardrobe 
                               if not any(word in item.name.lower() for word in ["dress", "formal", "suit"])]
        
        # Ensure we have at least some items for each type
        if not filtered_wardrobe:
            return wardrobe  # Fallback to original wardrobe if filtering is too aggressive
        
        return filtered_wardrobe
    
    def apply_fix(self, fix):
        """Apply a fix to the outfit generation logic."""
        self.applied_fixes.add(fix)

class AutonomousOutfitTester:
    """Main autonomous testing system."""
    
    def __init__(self):
        self.outfit_generator = MockOutfitGenerator()
        self.analyzer = OutfitAnalyzer()
        self.fixer = LogicFixer()
        self.wardrobe_generator = MockWardrobeGenerator()
        
        # Test occasions
        self.occasions = [
            "Work", "School", "Athletic", "Airport", "Festival", "Gala",
            "Casual", "Formal", "Business", "Party", "Interview", "Beach", "Errands"
        ]
        
        # Random styles and moods
        self.styles = [
            "Casual", "Formal", "Athletic", "Business", "Artsy", "Dark Academia",
            "Coastal Chic", "Techwear", "Vintage", "Minimalist", "Bohemian"
        ]
        
        self.moods = [
            "Relaxed", "Energetic", "Confident", "Creative", "Professional",
            "Playful", "Serious", "Adventurous", "Calm", "Excited"
        ]
        
        # Quality standards
        self.quality_standards = {
            "max_issues_per_outfit": 0,
            "consecutive_passing_outfits": 100,
            "max_test_iterations": 500
        }
    
    async def run_autonomous_testing(self):
        """Run the autonomous testing process."""
        print("🤖 Starting Autonomous Outfit Testing")
        print("=" * 60)
        
        consecutive_passes = 0
        total_iterations = 0
        fixes_applied = []
        
        while consecutive_passes < self.quality_standards["consecutive_passing_outfits"] and \
              total_iterations < self.quality_standards["max_test_iterations"]:
            
            total_iterations += 1
            print(f"\n🔄 Iteration {total_iterations}")
            
            # Generate mock wardrobe
            wardrobe = self.wardrobe_generator.generate_mock_wardrobe()
            
            # Select random occasion
            occasion = random.choice(self.occasions)
            
            # Select random style and mood
            style = random.choice(self.styles)
            mood = random.choice(self.moods)
            
            # Generate outfit
            try:
                outfit = await self.outfit_generator.generate_outfit(wardrobe, occasion, style, mood)
                
                # Analyze outfit
                issues = self.analyzer.analyze_outfit(outfit, occasion)
                
                print(f"📋 Occasion: {occasion}")
                print(f"🎨 Style: {style}")
                print(f"😊 Mood: {mood}")
                print(f"👕 Items: {[piece.name for piece in outfit.pieces]}")
                print(f"🔍 Issues found: {issues}")
                
                if not issues:
                    consecutive_passes += 1
                    print(f"✅ PASS! Consecutive passes: {consecutive_passes}")
                else:
                    consecutive_passes = 0
                    print(f"❌ FAIL! Resetting consecutive passes")
                    
                    # Apply fixes
                    fixes = self.fixer.fix_logic(issues, occasion)
                    if fixes:
                        print(f"🔧 Applying fixes: {fixes}")
                        fixes_applied.extend(fixes)
                        # Apply fixes to the outfit generator
                        for fix in fixes:
                            self.outfit_generator.apply_fix(fix)
                
            except Exception as e:
                print(f"💥 Error generating outfit: {e}")
                consecutive_passes = 0
            
            # Progress update
            if total_iterations % 10 == 0:
                print(f"\n📊 Progress: {total_iterations} iterations, {consecutive_passes} consecutive passes")
        
        # Final results
        print(f"\n🎯 Testing Complete!")
        print(f"📈 Total iterations: {total_iterations}")
        print(f"✅ Consecutive passes achieved: {consecutive_passes}")
        print(f"🔧 Fixes applied: {list(set(fixes_applied))}")
        
        if consecutive_passes >= self.quality_standards["consecutive_passing_outfits"]:
            print("🎉 SUCCESS: Quality standards met!")
        else:
            print("⚠️  WARNING: Quality standards not met within iteration limit")
        
        return {
            "success": consecutive_passes >= self.quality_standards["consecutive_passing_outfits"],
            "iterations": total_iterations,
            "consecutive_passes": consecutive_passes,
            "fixes_applied": list(set(fixes_applied))
        }

async def main():
    """Main function to run the autonomous testing."""
    tester = AutonomousOutfitTester()
    results = await tester.run_autonomous_testing()
    return results

if __name__ == "__main__":
    asyncio.run(main()) 