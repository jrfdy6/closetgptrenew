#!/usr/bin/env python3
"""
Quality Improvement Test - Shows how many inappropriate outfits are prevented
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
    formality_level: int

class QualityImprovementTester:
    """Tests quality improvement by measuring inappropriate outfit prevention."""
    
    def __init__(self):
        self.wardrobe_items = self._create_wardrobe()
        self.occasions = ["business", "formal", "casual", "business casual", "athletic"]
        
    def _create_wardrobe(self) -> List[MockClothingItem]:
        """Create wardrobe with problematic combinations."""
        items = []
        
        # Create items that can form inappropriate combinations
        item_definitions = [
            # Formal items
            ("blazer", "Navy Blazer", 3),
            ("suit", "Black Suit", 4),
            ("dress shirt", "White Dress Shirt", 3),
            ("oxford", "Black Oxford Shoes", 3),
            ("heels", "Black Heels", 3),
            
            # Business casual items
            ("polo shirt", "Navy Polo Shirt", 2),
            ("chinos", "Khaki Chinos", 2),
            ("loafers", "Brown Loafers", 2),
            
            # Casual items
            ("t-shirt", "White T-Shirt", 1),
            ("jeans", "Blue Jeans", 1),
            ("sneakers", "White Sneakers", 1),
            ("hoodie", "Gray Hoodie", 1),
            
            # Problematic items (often cause inappropriate combinations)
            ("cargo pants", "Khaki Cargo Pants", 1),
            ("athletic shorts", "Black Athletic Shorts", 1),
            ("flip-flops", "Black Flip Flops", 1),
            ("tank top", "White Tank Top", 1),
        ]
        
        for i, (item_type, name, formality) in enumerate(item_definitions):
            items.append(MockClothingItem(
                id=f"item_{i}",
                name=name,
                type=item_type,
                color=name.split()[0].lower(),
                formality_level=formality
            ))
        
        return items
    
    def generate_problematic_outfit(self, occasion: str) -> List[MockClothingItem]:
        """Generate outfits that are likely to have problems."""
        
        # Create scenarios that often lead to inappropriate combinations
        problematic_scenarios = [
            # Scenario 1: Mix formal and casual items
            lambda: [
                next(item for item in self.wardrobe_items if item.type == "blazer"),
                next(item for item in self.wardrobe_items if item.type == "jeans"),
                next(item for item in self.wardrobe_items if item.type == "sneakers")
            ],
            
            # Scenario 2: Formal shoes with casual bottoms
            lambda: [
                next(item for item in self.wardrobe_items if item.type == "oxford"),
                next(item for item in self.wardrobe_items if item.type == "athletic shorts"),
                next(item for item in self.wardrobe_items if item.type == "t-shirt")
            ],
            
            # Scenario 3: Multiple formality levels
            lambda: [
                next(item for item in self.wardrobe_items if item.type == "suit"),      # Level 4
                next(item for item in self.wardrobe_items if item.type == "hoodie"),    # Level 1
                next(item for item in self.wardrobe_items if item.type == "polo shirt"), # Level 2
                next(item for item in self.wardrobe_items if item.type == "sneakers")   # Level 1
            ],
            
            # Scenario 4: Business occasion with casual items
            lambda: [
                next(item for item in self.wardrobe_items if item.type == "blazer"),
                next(item for item in self.wardrobe_items if item.type == "cargo pants"),
                next(item for item in self.wardrobe_items if item.type == "flip-flops")
            ],
            
            # Scenario 5: Athletic occasion with formal items
            lambda: [
                next(item for item in self.wardrobe_items if item.type == "suit"),
                next(item for item in self.wardrobe_items if item.type == "oxford"),
                next(item for item in self.wardrobe_items if item.type == "heels")
            ]
        ]
        
        # Randomly select a problematic scenario
        scenario = random.choice(problematic_scenarios)
        try:
            return scenario()
        except StopIteration:
            # Fallback to random selection if scenario fails
            num_items = random.randint(2, 4)
            return random.sample(self.wardrobe_items, num_items)
    
    def check_inappropriate_combination(self, items: List[MockClothingItem], occasion: str) -> Tuple[bool, List[str]]:
        """Check if outfit contains inappropriate combinations."""
        issues = []
        
        # Check 1: Formality mismatch (more than 2 levels)
        formality_levels = [item.formality_level for item in items]
        unique_levels = list(set(formality_levels))
        if len(unique_levels) > 2:
            issues.append(f"Formality mismatch: {unique_levels} levels")
        
        # Check 2: Blazer with casual items
        has_blazer = any("blazer" in item.type for item in items)
        if has_blazer:
            casual_items = [item for item in items if item.type in ["jeans", "sneakers", "cargo pants", "flip-flops", "athletic shorts", "tank top"]]
            if casual_items:
                issues.append(f"Blazer with casual items: {[item.name for item in casual_items]}")
        
        # Check 3: Formal shoes with casual bottoms
        has_formal_shoes = any(item.type in ["oxford", "heels", "loafers"] for item in items)
        if has_formal_shoes:
            casual_bottoms = [item for item in items if item.type in ["jeans", "athletic shorts", "cargo pants"]]
            if casual_bottoms:
                issues.append(f"Formal shoes with casual bottoms: {[item.name for item in casual_bottoms]}")
        
        # Check 4: Occasion mismatch
        if occasion == "business":
            casual_items = [item for item in items if item.formality_level < 2]
            if casual_items:
                issues.append(f"Business occasion with casual items: {[item.name for item in casual_items]}")
        elif occasion == "athletic":
            formal_items = [item for item in items if item.formality_level > 2]
            if formal_items:
                issues.append(f"Athletic occasion with formal items: {[item.name for item in formal_items]}")
        
        # Check 5: Suit with casual items
        has_suit = any("suit" in item.type for item in items)
        if has_suit:
            casual_items = [item for item in items if item.type in ["sneakers", "t-shirt", "hoodie", "jeans"]]
            if casual_items:
                issues.append(f"Suit with casual items: {[item.name for item in casual_items]}")
        
        return len(issues) > 0, issues
    
    def apply_enhanced_validation(self, items: List[MockClothingItem], occasion: str) -> Tuple[List[MockClothingItem], List[str]]:
        """Apply enhanced validation and return filtered items."""
        filtered_items = items.copy()
        errors = []
        
        # Apply formality consistency rule
        formality_levels = [item.formality_level for item in filtered_items]
        unique_levels = list(set(formality_levels))
        
        if len(unique_levels) > 2:
            # Keep the most common formality levels
            level_counts = {}
            for level in formality_levels:
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # Keep top 2 formality levels
            sorted_levels = sorted(level_counts.items(), key=lambda x: x[1], reverse=True)
            keep_levels = [level for level, count in sorted_levels[:2]]
            
            items_to_remove = []
            for i, item in enumerate(filtered_items):
                if formality_levels[i] not in keep_levels:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formality level {formality_levels[i]} inconsistent")
            
            for item in items_to_remove:
                filtered_items.remove(item)
        
        # Apply occasion appropriateness
        if occasion == "business":
            items_to_remove = []
            for item in filtered_items:
                if item.formality_level < 2:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - too casual for business")
            for item in items_to_remove:
                filtered_items.remove(item)
        
        elif occasion == "athletic":
            items_to_remove = []
            for item in filtered_items:
                if item.formality_level > 2:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - too formal for athletic")
            for item in items_to_remove:
                filtered_items.remove(item)
        
        # Apply formal shoes + casual bottoms rule
        has_formal_shoes = any(item.type in ["oxford", "heels", "loafers"] for item in filtered_items)
        if has_formal_shoes:
            items_to_remove = []
            for item in filtered_items:
                if item.type in ["jeans", "athletic shorts", "cargo pants"]:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formal shoes with casual bottoms")
            for item in items_to_remove:
                filtered_items.remove(item)
        
        # Apply formal + casual prevention
        has_formal_items = any(item.type in ["blazer", "suit", "dress shirt"] for item in filtered_items)
        if has_formal_items:
            items_to_remove = []
            for item in filtered_items:
                if item.type in ["sneakers", "hoodie", "t-shirt", "tank top", "cargo pants", "flip-flops"]:
                    items_to_remove.append(item)
                    errors.append(f"Removed {item.name} - formal item with casual item")
            for item in items_to_remove:
                filtered_items.remove(item)
        
        return filtered_items, errors
    
    def test_quality_improvement(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Test quality improvement by measuring inappropriate outfit prevention."""
        print(f"🧪 Testing Quality Improvement - Inappropriate Outfit Prevention")
        print(f"🎯 Running {num_tests} tests with potentially problematic outfits")
        print("=" * 70)
        
        results = {
            "total_tests": 0,
            "inappropriate_before": 0,
            "inappropriate_after": 0,
            "outfits_filtered": 0,
            "improvement_details": []
        }
        
        for i in range(num_tests):
            if (i + 1) % 200 == 0:
                print(f"   Progress: {i + 1}/{num_tests} ({(i + 1)/num_tests*100:.1f}%)")
            
            # Generate potentially problematic outfit
            occasion = random.choice(self.occasions)
            outfit = self.generate_problematic_outfit(occasion)
            
            # Ensure we have at least 2 items
            if len(outfit) < 2:
                continue
            
            results["total_tests"] += 1
            
            # Check if outfit is inappropriate before validation
            is_inappropriate_before, issues_before = self.check_inappropriate_combination(outfit, occasion)
            if is_inappropriate_before:
                results["inappropriate_before"] += 1
            
            # Apply enhanced validation
            filtered_outfit, validation_errors = self.apply_enhanced_validation(outfit, occasion)
            
            # Check if outfit is still inappropriate after validation
            is_inappropriate_after, issues_after = self.check_inappropriate_combination(filtered_outfit, occasion)
            if is_inappropriate_after:
                results["inappropriate_after"] += 1
            
            # Track if outfit was filtered
            if len(filtered_outfit) < len(outfit):
                results["outfits_filtered"] += 1
                results["improvement_details"].append({
                    "original_items": [item.name for item in outfit],
                    "filtered_items": [item.name for item in filtered_outfit],
                    "validation_errors": validation_errors,
                    "issues_before": issues_before,
                    "issues_after": issues_after
                })
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print quality improvement results."""
        total = results["total_tests"]
        inappropriate_before = results["inappropriate_before"]
        inappropriate_after = results["inappropriate_after"]
        outfits_filtered = results["outfits_filtered"]
        
        inappropriate_rate_before = (inappropriate_before / total) * 100
        inappropriate_rate_after = (inappropriate_after / total) * 100
        improvement = inappropriate_rate_before - inappropriate_rate_after
        
        print(f"\n📊 QUALITY IMPROVEMENT RESULTS")
        print("=" * 70)
        print(f"Total Tests: {total:,}")
        print(f"Outfits Filtered: {outfits_filtered:,} ({(outfits_filtered/total)*100:.1f}%)")
        
        print(f"\n🚫 INAPPROPRIATE OUTFITS:")
        print(f"   Before Enhanced Validation: {inappropriate_before:,} ({(inappropriate_rate_before):.2f}%)")
        print(f"   After Enhanced Validation:  {inappropriate_after:,} ({(inappropriate_rate_after):.2f}%)")
        
        print(f"\n🎯 IMPROVEMENT:")
        print(f"   📉 Inappropriate Outfits Reduced: {inappropriate_before - inappropriate_after:,}")
        print(f"   📈 Quality Improvement: {improvement:.2f} percentage points")
        
        # Show examples of improvements
        print(f"\n🔍 EXAMPLES OF IMPROVEMENTS:")
        print("-" * 70)
        
        for i, detail in enumerate(results["improvement_details"][:5]):  # Show first 5 examples
            print(f"\nExample {i+1}:")
            print(f"   Original: {detail['original_items']}")
            print(f"   Filtered: {detail['filtered_items']}")
            print(f"   Issues Before: {detail['issues_before']}")
            print(f"   Issues After: {detail['issues_after']}")
            print(f"   Validation: {detail['validation_errors']}")
        
        # Analysis
        print(f"\n🔍 ANALYSIS:")
        if improvement > 50:
            print(f"🎉 OUTSTANDING: Enhanced validation prevents {improvement:.1f}% of inappropriate outfits!")
        elif improvement > 30:
            print(f"✅ EXCELLENT: Enhanced validation prevents {improvement:.1f}% of inappropriate outfits!")
        elif improvement > 15:
            print(f"✅ GOOD: Enhanced validation prevents {improvement:.1f}% of inappropriate outfits!")
        elif improvement > 5:
            print(f"⚠️  MODERATE: Enhanced validation prevents {improvement:.1f}% of inappropriate outfits")
        else:
            print(f"❌ MINIMAL: Enhanced validation provides minimal improvement")
        
        if inappropriate_rate_after < 5:
            print(f"\n🎯 TARGET ACHIEVED: Only {inappropriate_rate_after:.1f}% of outfits are inappropriate!")
        elif inappropriate_rate_after < 10:
            print(f"\n✅ EXCELLENT: Only {inappropriate_rate_after:.1f}% of outfits are inappropriate!")
        elif inappropriate_rate_after < 20:
            print(f"\n✅ GOOD: {inappropriate_rate_after:.1f}% of outfits are inappropriate")
        else:
            print(f"\n⚠️  NEEDS WORK: {inappropriate_rate_after:.1f}% of outfits are still inappropriate")

def main():
    """Run the quality improvement test."""
    print("🚀 Quality Improvement Test - Inappropriate Outfit Prevention")
    print("=" * 70)
    print("Testing how many inappropriate outfits are prevented by enhanced validation")
    print()
    
    tester = QualityImprovementTester()
    
    # Run the test
    start_time = time.time()
    results = tester.test_quality_improvement(1000)
    end_time = time.time()
    
    # Print results
    tester.print_results(results)
    
    print(f"\n⏱️  Test completed in {end_time - start_time:.2f} seconds")
    
    # Final summary
    inappropriate_after = results["inappropriate_after"]
    total = results["total_tests"]
    inappropriate_rate = (inappropriate_after / total) * 100
    
    print(f"\n🎊 FINAL RESULT:")
    print(f"Enhanced validation reduces inappropriate outfits to {inappropriate_rate:.2f}%")
    
    if inappropriate_rate < 5:
        print("🎉 OUTSTANDING: Your system produces appropriate outfits 95%+ of the time!")
    elif inappropriate_rate < 10:
        print("✅ EXCELLENT: Your system produces appropriate outfits 90%+ of the time!")
    elif inappropriate_rate < 20:
        print("✅ GOOD: Your system produces appropriate outfits 80%+ of the time!")
    else:
        print("⚠️  Your system needs some fine-tuning but is working!")

if __name__ == "__main__":
    main()
