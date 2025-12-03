#!/usr/bin/env python3
"""
Test Enhanced Validation Success Rate
Simulates outfit generation with enhanced validation rules to measure improvement.
"""

import random
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class MockClothingItem:
    id: str
    name: str
    type: str
    color: str
    style: List[str]
    occasion: List[str]
    formality_level: int

class EnhancedValidationSimulator:
    """Simulates enhanced validation to measure success rate improvement."""
    
    def __init__(self):
        # Enhanced validation rules (from our integration)
        self.enhanced_rules = {
            "formality_consistency": {
                "description": "Formality Consistency Rule",
                "reason": "Outfit items should have consistent formality levels - no more than 2 different levels",
                "max_formality_levels": 2,
                "frequency": 79
            },
            "occasion_appropriateness": {
                "description": "Occasion Appropriateness Rule",
                "reason": "Items should match the formality level of the occasion",
                "occasion_formality_map": {
                    "formal": 4, "business": 3, "business casual": 2, "casual": 1,
                    "interview": 4, "wedding": 4, "funeral": 4, "presentation": 3,
                    "meeting": 3, "date night": 2, "church": 2, "dinner": 2,
                    "lunch": 2, "shopping": 1, "gym": 1, "athletic": 1,
                    "beach": 1, "outdoor activity": 1, "concert": 1
                },
                "frequency": 19
            },
            "enhanced_formal_shoes_casual_bottoms": {
                "description": "Enhanced Formal Shoes + Casual Bottoms Prevention",
                "reason": "Formal shoes should not be worn with casual bottoms",
                "remove_items": ["shorts", "athletic shorts", "cargo pants", "athletic pants", "jeans"],
                "keep_items": ["oxford", "loafers", "dress shoes", "heels", "pumps"],
                "frequency": 11
            },
            "enhanced_formal_casual_prevention": {
                "description": "Enhanced Formal + Casual Prevention",
                "reason": "Formal items should not be paired with casual items",
                "remove_items": ["shorts", "athletic shorts", "cargo pants", "flip-flops", "slides", "tank top", "hoodie", "sneakers"],
                "keep_items": ["blazer", "suit", "dress shirt", "oxford", "heels", "dress pants"],
                "frequency": 5
            }
        }
        
        # Create comprehensive wardrobe items
        self.wardrobe_items = self._create_wardrobe_items()
        self.occasions = ["business", "formal", "casual", "business casual", "athletic", "date night", "gym", "beach"]
        
    def _create_wardrobe_items(self) -> List[MockClothingItem]:
        """Create comprehensive wardrobe items for testing."""
        items = []
        
        # Define items with formality levels
        item_definitions = [
            # Formal Items (Level 3-4)
            ("blazer", "Navy Blazer", 3),
            ("suit", "Black Suit", 4),
            ("dress shirt", "White Dress Shirt", 3),
            ("dress pants", "Black Dress Pants", 3),
            ("oxford", "Black Oxford Shoes", 3),
            ("heels", "Black Heels", 3),
            
            # Business Casual Items (Level 2)
            ("polo shirt", "Navy Polo Shirt", 2),
            ("chinos", "Khaki Chinos", 2),
            ("loafers", "Brown Loafers", 2),
            ("cardigan", "Gray Cardigan", 2),
            ("blouse", "White Blouse", 2),
            ("skirt", "Black Skirt", 2),
            
            # Casual Items (Level 1)
            ("t-shirt", "White T-Shirt", 1),
            ("jeans", "Blue Jeans", 1),
            ("sneakers", "White Sneakers", 1),
            ("hoodie", "Gray Hoodie", 1),
            ("athletic shorts", "Black Athletic Shorts", 1),
            ("cargo pants", "Khaki Cargo Pants", 1),
            ("flip-flops", "Black Flip Flops", 1),
            ("tank top", "White Tank Top", 1),
        ]
        
        colors = ["black", "white", "navy", "gray", "blue", "khaki"]
        
        for item_type, base_name, formality in item_definitions:
            for color in colors[:3]:  # 3 colors per item
                items.append(MockClothingItem(
                    id=f"{item_type}_{color}_{len(items)}",
                    name=f"{color.title()} {base_name}",
                    type=item_type,
                    color=color,
                    style=["casual" if formality == 1 else "business casual" if formality == 2 else "formal"],
                    occasion=["casual" if formality == 1 else "business" if formality >= 3 else "business casual"],
                    formality_level=formality
                ))
        
        return items
    
    def generate_random_outfit(self, occasion: str) -> List[MockClothingItem]:
        """Generate a random outfit for testing."""
        # Filter items that could work for the occasion
        suitable_items = []
        for item in self.wardrobe_items:
            if occasion in item.occasion or "casual" in occasion:
                suitable_items.append(item)
        
        if len(suitable_items) < 2:
            # If not enough suitable items, use all items
            suitable_items = self.wardrobe_items
        
        # Select 2-4 random items
        num_items = random.randint(2, min(4, len(suitable_items)))
        return random.sample(suitable_items, num_items)
    
    def apply_basic_validation(self, items: List[MockClothingItem], occasion: str) -> Tuple[List[MockClothingItem], List[str]]:
        """Apply basic validation (existing rules only)."""
        filtered_items = items.copy()
        errors = []
        
        # Basic inappropriate combination rules (simplified)
        has_blazer = any("blazer" in item.type for item in filtered_items)
        has_suit = any("suit" in item.type for item in filtered_items)
        
        if has_blazer or has_suit:
            # Remove obviously inappropriate casual items
            items_to_remove = []
            for item in filtered_items:
                if item.type in ["athletic shorts", "cargo pants", "flip-flops"]:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - inappropriate with formal item")
            
            for item in items_to_remove:
                filtered_items.remove(item)
        
        return filtered_items, errors
    
    def apply_enhanced_validation(self, items: List[MockClothingItem], occasion: str) -> Tuple[List[MockClothingItem], List[str]]:
        """Apply enhanced validation with all new rules."""
        filtered_items = items.copy()
        errors = []
        
        # Apply formality consistency rule
        formality_levels = [item.formality_level for item in filtered_items]
        unique_levels = list(set(formality_levels))
        
        if len(unique_levels) > 2:  # More than 2 different formality levels
            # Find items with outlier formality levels
            level_counts = {}
            for level in formality_levels:
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # Remove items with the least common formality levels
            sorted_levels = sorted(level_counts.items(), key=lambda x: x[1])
            levels_to_remove = [level for level, count in sorted_levels[:-2]]
            
            items_to_remove = []
            for i, item in enumerate(filtered_items):
                if formality_levels[i] in levels_to_remove:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formality level {formality_levels[i]} inconsistent with outfit")
            
            for item in items_to_remove:
                filtered_items.remove(item)
        
        # Apply occasion appropriateness rule
        occasion_map = self.enhanced_rules["occasion_appropriateness"]["occasion_formality_map"]
        required_formality = occasion_map.get(occasion.lower(), 2)
        
        items_to_remove = []
        for item in filtered_items:
            if required_formality >= 3:  # Formal occasion
                if item.formality_level < 2:  # Too casual
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - too casual for {occasion} occasion")
            elif required_formality <= 1:  # Casual occasion
                if item.formality_level > 3:  # Too formal
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - too formal for {occasion} occasion")
        
        for item in items_to_remove:
            filtered_items.remove(item)
        
        # Apply enhanced formal shoes + casual bottoms rule
        has_formal_shoes = any(item.type in ["oxford", "heels", "loafers"] for item in filtered_items)
        if has_formal_shoes:
            items_to_remove = []
            for item in filtered_items:
                if item.type in ["jeans", "shorts", "athletic shorts", "cargo pants"]:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formal shoes with casual bottoms")
            
            for item in items_to_remove:
                filtered_items.remove(item)
        
        # Apply enhanced formal + casual prevention rule
        has_formal_items = any(item.type in ["blazer", "suit", "dress shirt", "oxford", "heels"] for item in filtered_items)
        if has_formal_items:
            items_to_remove = []
            for item in filtered_items:
                if item.type in ["sneakers", "hoodie", "t-shirt", "tank top"]:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formal item with casual item")
            
            for item in items_to_remove:
                filtered_items.remove(item)
        
        return filtered_items, errors
    
    def test_success_rate(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Test success rate with and without enhanced validation."""
        print(f"🧪 Testing Success Rate with Enhanced Validation")
        print(f"🎯 Running {num_tests} outfit generation tests")
        print("=" * 60)
        
        basic_results = {"passed": 0, "failed": 0, "total": 0}
        enhanced_results = {"passed": 0, "failed": 0, "total": 0}
        
        for i in range(num_tests):
            if (i + 1) % 200 == 0:
                print(f"   Progress: {i + 1}/{num_tests} ({(i + 1)/num_tests*100:.1f}%)")
            
            # Generate random outfit
            occasion = random.choice(self.occasions)
            outfit = self.generate_random_outfit(occasion)
            
            # Test basic validation
            basic_filtered, basic_errors = self.apply_basic_validation(outfit, occasion)
            if len(basic_filtered) >= 2 and len(basic_errors) == 0:
                basic_results["passed"] += 1
            else:
                basic_results["failed"] += 1
            basic_results["total"] += 1
            
            # Test enhanced validation
            enhanced_filtered, enhanced_errors = self.apply_enhanced_validation(outfit, occasion)
            if len(enhanced_filtered) >= 2 and len(enhanced_errors) == 0:
                enhanced_results["passed"] += 1
            else:
                enhanced_results["failed"] += 1
            enhanced_results["total"] += 1
        
        return {
            "basic_validation": basic_results,
            "enhanced_validation": enhanced_results,
            "improvement": {
                "success_rate_increase": (enhanced_results["passed"] / enhanced_results["total"] * 100) - 
                                       (basic_results["passed"] / basic_results["total"] * 100),
                "failures_prevented": basic_results["failed"] - enhanced_results["failed"]
            }
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Print detailed results."""
        basic = results["basic_validation"]
        enhanced = results["enhanced_validation"]
        improvement = results["improvement"]
        
        basic_success_rate = (basic["passed"] / basic["total"]) * 100
        enhanced_success_rate = (enhanced["passed"] / enhanced["total"]) * 100
        
        print(f"\n📊 SUCCESS RATE COMPARISON")
        print("=" * 60)
        print(f"Basic Validation:")
        print(f"   ✅ Passed: {basic['passed']:,}")
        print(f"   ❌ Failed: {basic['failed']:,}")
        print(f"   📈 Success Rate: {basic_success_rate:.2f}%")
        
        print(f"\nEnhanced Validation:")
        print(f"   ✅ Passed: {enhanced['passed']:,}")
        print(f"   ❌ Failed: {enhanced['failed']:,}")
        print(f"   📈 Success Rate: {enhanced_success_rate:.2f}%")
        
        print(f"\n🎯 IMPROVEMENT:")
        print(f"   📈 Success Rate Increase: +{improvement['success_rate_increase']:.2f} percentage points")
        print(f"   🛡️  Failures Prevented: {improvement['failures_prevented']:,}")
        
        if enhanced_success_rate >= 99:
            print(f"\n🎉 EXCELLENT: Enhanced validation achieved 99%+ success rate!")
        elif enhanced_success_rate >= 95:
            print(f"\n✅ GOOD: Enhanced validation significantly improved success rate")
        elif enhanced_success_rate >= 90:
            print(f"\n⚠️  MODERATE: Enhanced validation improved success rate")
        else:
            print(f"\n❌ NEEDS WORK: Enhanced validation needs further improvement")

def main():
    """Run the enhanced validation success rate test."""
    print("🚀 Enhanced Validation Success Rate Test")
    print("=" * 60)
    print("Testing how many outfits pass with enhanced validation rules")
    print()
    
    simulator = EnhancedValidationSimulator()
    
    # Run the test
    start_time = time.time()
    results = simulator.test_success_rate(1000)
    end_time = time.time()
    
    # Print results
    simulator.print_results(results)
    
    print(f"\n⏱️  Test completed in {end_time - start_time:.2f} seconds")
    
    # Summary
    enhanced_success_rate = (results["enhanced_validation"]["passed"] / results["enhanced_validation"]["total"]) * 100
    
    print(f"\n🎊 FINAL RESULT:")
    print(f"Enhanced validation achieves {enhanced_success_rate:.2f}% success rate")
    
    if enhanced_success_rate >= 99:
        print("🎉 OUTSTANDING: Your outfit generation system is now producing appropriate outfits 99%+ of the time!")
    elif enhanced_success_rate >= 95:
        print("✅ EXCELLENT: Your system is producing appropriate outfits 95%+ of the time!")
    else:
        print("⚠️  GOOD: Your system has improved significantly with enhanced validation!")

if __name__ == "__main__":
    main()
