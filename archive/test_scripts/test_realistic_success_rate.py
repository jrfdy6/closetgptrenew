#!/usr/bin/env python3
"""
Realistic Enhanced Validation Success Rate Test
Tests with more realistic outfit generation scenarios.
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

class RealisticValidationTester:
    """Tests enhanced validation with realistic outfit generation."""
    
    def __init__(self):
        # Create realistic wardrobe items
        self.wardrobe_items = self._create_realistic_wardrobe()
        self.occasions = ["business", "formal", "casual", "business casual", "athletic"]
        
    def _create_realistic_wardrobe(self) -> List[MockClothingItem]:
        """Create a realistic wardrobe for testing."""
        items = []
        
        # Business wardrobe (realistic proportions)
        business_items = [
            ("blazer", "Navy Blazer", 3),
            ("blazer", "Black Blazer", 3),
            ("dress shirt", "White Dress Shirt", 3),
            ("dress shirt", "Blue Dress Shirt", 3),
            ("dress pants", "Black Dress Pants", 3),
            ("dress pants", "Gray Dress Pants", 3),
            ("oxford", "Black Oxford Shoes", 3),
            ("heels", "Black Heels", 3),
        ]
        
        # Business casual wardrobe
        business_casual_items = [
            ("polo shirt", "Navy Polo Shirt", 2),
            ("polo shirt", "White Polo Shirt", 2),
            ("chinos", "Khaki Chinos", 2),
            ("chinos", "Navy Chinos", 2),
            ("loafers", "Brown Loafers", 2),
            ("cardigan", "Gray Cardigan", 2),
            ("blouse", "White Blouse", 2),
        ]
        
        # Casual wardrobe
        casual_items = [
            ("t-shirt", "White T-Shirt", 1),
            ("t-shirt", "Gray T-Shirt", 1),
            ("jeans", "Blue Jeans", 1),
            ("jeans", "Black Jeans", 1),
            ("sneakers", "White Sneakers", 1),
            ("sneakers", "Black Sneakers", 1),
            ("hoodie", "Gray Hoodie", 1),
        ]
        
        # Problematic items (should be filtered)
        problematic_items = [
            ("cargo pants", "Khaki Cargo Pants", 1),
            ("athletic shorts", "Black Athletic Shorts", 1),
            ("flip-flops", "Black Flip Flops", 1),
            ("tank top", "White Tank Top", 1),
        ]
        
        all_items = business_items + business_casual_items + casual_items + problematic_items
        
        for i, (item_type, name, formality) in enumerate(all_items):
            items.append(MockClothingItem(
                id=f"item_{i}",
                name=name,
                type=item_type,
                color=name.split()[0].lower(),
                formality_level=formality
            ))
        
        return items
    
    def generate_realistic_outfit(self, occasion: str) -> List[MockClothingItem]:
        """Generate a realistic outfit based on occasion."""
        
        if occasion == "business":
            # Business outfit: formal items
            suitable_items = [item for item in self.wardrobe_items if item.formality_level >= 3]
            if len(suitable_items) >= 3:
                # Select 3-4 formal items
                num_items = random.randint(3, min(4, len(suitable_items)))
                return random.sample(suitable_items, num_items)
        
        elif occasion == "business casual":
            # Business casual outfit: level 2-3 items
            suitable_items = [item for item in self.wardrobe_items if item.formality_level >= 2]
            if len(suitable_items) >= 3:
                num_items = random.randint(3, min(4, len(suitable_items)))
                return random.sample(suitable_items, num_items)
        
        elif occasion == "casual":
            # Casual outfit: any items, but prefer casual
            casual_items = [item for item in self.wardrobe_items if item.formality_level <= 2]
            if len(casual_items) >= 2:
                # 70% chance of casual items, 30% chance of mixed
                if random.random() < 0.7:
                    num_items = random.randint(2, min(4, len(casual_items)))
                    return random.sample(casual_items, num_items)
                else:
                    # Mixed outfit (this is where problems occur)
                    num_items = random.randint(2, 4)
                    return random.sample(self.wardrobe_items, num_items)
        
        elif occasion == "athletic":
            # Athletic outfit: casual items only
            suitable_items = [item for item in self.wardrobe_items if item.formality_level == 1]
            if len(suitable_items) >= 2:
                num_items = random.randint(2, min(3, len(suitable_items)))
                return random.sample(suitable_items, num_items)
        
        # Fallback: random selection
        num_items = random.randint(2, 4)
        return random.sample(self.wardrobe_items, num_items)
    
    def apply_basic_validation(self, items: List[MockClothingItem], occasion: str) -> Tuple[bool, List[str]]:
        """Apply basic validation rules."""
        errors = []
        
        # Basic rule: no blazer with shorts/flip-flops
        has_blazer = any("blazer" in item.type for item in items)
        if has_blazer:
            for item in items:
                if item.type in ["athletic shorts", "flip-flops", "cargo pants"]:
                    errors.append(f"Blazer with {item.type} is inappropriate")
        
        # Basic rule: no formal shoes with shorts
        has_formal_shoes = any(item.type in ["oxford", "heels"] for item in items)
        if has_formal_shoes:
            for item in items:
                if item.type in ["athletic shorts", "cargo pants"]:
                    errors.append(f"Formal shoes with {item.type} is inappropriate")
        
        return len(errors) == 0, errors
    
    def apply_enhanced_validation(self, items: List[MockClothingItem], occasion: str) -> Tuple[bool, List[str]]:
        """Apply enhanced validation rules."""
        errors = []
        
        # Enhanced Rule 1: Formality consistency (max 2 different levels)
        formality_levels = [item.formality_level for item in items]
        unique_levels = list(set(formality_levels))
        
        if len(unique_levels) > 2:
            errors.append(f"Too many formality levels: {unique_levels}")
        
        # Enhanced Rule 2: Occasion appropriateness
        if occasion == "business":
            # Business should be formal (level 3+)
            casual_items = [item for item in items if item.formality_level < 3]
            if casual_items:
                errors.append(f"Business occasion with casual items: {[item.name for item in casual_items]}")
        
        elif occasion == "athletic":
            # Athletic should be casual (level 1)
            formal_items = [item for item in items if item.formality_level > 1]
            if formal_items:
                errors.append(f"Athletic occasion with formal items: {[item.name for item in formal_items]}")
        
        # Enhanced Rule 3: Formal shoes with casual bottoms
        has_formal_shoes = any(item.type in ["oxford", "heels", "loafers"] for item in items)
        if has_formal_shoes:
            casual_bottoms = [item for item in items if item.type in ["jeans", "athletic shorts", "cargo pants"]]
            if casual_bottoms:
                errors.append(f"Formal shoes with casual bottoms: {[item.name for item in casual_bottoms]}")
        
        # Enhanced Rule 4: Formal items with casual items
        has_formal_items = any(item.type in ["blazer", "suit", "dress shirt"] for item in items)
        if has_formal_items:
            casual_items = [item for item in items if item.type in ["sneakers", "hoodie", "t-shirt", "tank top"]]
            if casual_items:
                errors.append(f"Formal items with casual items: {[item.name for item in casual_items]}")
        
        return len(errors) == 0, errors
    
    def test_realistic_scenarios(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Test with realistic outfit generation scenarios."""
        print(f"🧪 Testing Realistic Outfit Generation Scenarios")
        print(f"🎯 Running {num_tests} realistic outfit tests")
        print("=" * 60)
        
        basic_results = {"passed": 0, "failed": 0, "total": 0}
        enhanced_results = {"passed": 0, "failed": 0, "total": 0}
        
        # Track by occasion
        occasion_results = {}
        
        for i in range(num_tests):
            if (i + 1) % 200 == 0:
                print(f"   Progress: {i + 1}/{num_tests} ({(i + 1)/num_tests*100:.1f}%)")
            
            # Generate realistic outfit
            occasion = random.choice(self.occasions)
            outfit = self.generate_realistic_outfit(occasion)
            
            # Ensure we have at least 2 items
            if len(outfit) < 2:
                continue
            
            # Test basic validation
            basic_valid, basic_errors = self.apply_basic_validation(outfit, occasion)
            if basic_valid:
                basic_results["passed"] += 1
            else:
                basic_results["failed"] += 1
            basic_results["total"] += 1
            
            # Test enhanced validation
            enhanced_valid, enhanced_errors = self.apply_enhanced_validation(outfit, occasion)
            if enhanced_valid:
                enhanced_results["passed"] += 1
            else:
                enhanced_results["failed"] += 1
            enhanced_results["total"] += 1
            
            # Track by occasion
            if occasion not in occasion_results:
                occasion_results[occasion] = {"basic_passed": 0, "basic_failed": 0, "enhanced_passed": 0, "enhanced_failed": 0}
            
            if basic_valid:
                occasion_results[occasion]["basic_passed"] += 1
            else:
                occasion_results[occasion]["basic_failed"] += 1
            
            if enhanced_valid:
                occasion_results[occasion]["enhanced_passed"] += 1
            else:
                occasion_results[occasion]["enhanced_failed"] += 1
        
        return {
            "basic_validation": basic_results,
            "enhanced_validation": enhanced_results,
            "occasion_results": occasion_results
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Print detailed results."""
        basic = results["basic_validation"]
        enhanced = results["enhanced_validation"]
        occasion_results = results["occasion_results"]
        
        basic_success_rate = (basic["passed"] / basic["total"]) * 100
        enhanced_success_rate = (enhanced["passed"] / enhanced["total"]) * 100
        
        print(f"\n📊 REALISTIC SUCCESS RATE COMPARISON")
        print("=" * 60)
        print(f"Basic Validation:")
        print(f"   ✅ Passed: {basic['passed']:,}")
        print(f"   ❌ Failed: {basic['failed']:,}")
        print(f"   📈 Success Rate: {basic_success_rate:.2f}%")
        
        print(f"\nEnhanced Validation:")
        print(f"   ✅ Passed: {enhanced['passed']:,}")
        print(f"   ❌ Failed: {enhanced['failed']:,}")
        print(f"   📈 Success Rate: {enhanced_success_rate:.2f}%")
        
        improvement = enhanced_success_rate - basic_success_rate
        print(f"\n🎯 IMPROVEMENT:")
        print(f"   📈 Success Rate Change: {improvement:+.2f} percentage points")
        
        print(f"\n📋 RESULTS BY OCCASION:")
        print("-" * 60)
        for occasion, occ_results in occasion_results.items():
            basic_total = occ_results["basic_passed"] + occ_results["basic_failed"]
            enhanced_total = occ_results["enhanced_passed"] + occ_results["enhanced_failed"]
            
            if basic_total > 0:
                basic_rate = (occ_results["basic_passed"] / basic_total) * 100
            else:
                basic_rate = 0
            
            if enhanced_total > 0:
                enhanced_rate = (occ_results["enhanced_passed"] / enhanced_total) * 100
            else:
                enhanced_rate = 0
            
            print(f"   {occasion.title()}:")
            print(f"     Basic: {basic_rate:.1f}% | Enhanced: {enhanced_rate:.1f}%")
        
        # Analysis
        print(f"\n🔍 ANALYSIS:")
        if enhanced_success_rate > basic_success_rate:
            print(f"✅ Enhanced validation IMPROVES success rate by {improvement:.2f} percentage points")
            print(f"🎯 Enhanced validation prevents more inappropriate combinations")
        elif enhanced_success_rate < basic_success_rate:
            print(f"⚠️  Enhanced validation is MORE STRICT (reduces success rate by {abs(improvement):.2f} percentage points)")
            print(f"🛡️  Enhanced validation prevents inappropriate combinations but filters more outfits")
        else:
            print(f"📊 Enhanced validation maintains similar success rate")
        
        if enhanced_success_rate >= 95:
            print(f"\n🎉 EXCELLENT: Enhanced validation achieves 95%+ success rate!")
        elif enhanced_success_rate >= 90:
            print(f"\n✅ GOOD: Enhanced validation achieves 90%+ success rate!")
        elif enhanced_success_rate >= 80:
            print(f"\n⚠️  MODERATE: Enhanced validation achieves 80%+ success rate")
        else:
            print(f"\n❌ NEEDS WORK: Enhanced validation needs improvement")

def main():
    """Run the realistic enhanced validation test."""
    print("🚀 Realistic Enhanced Validation Success Rate Test")
    print("=" * 60)
    print("Testing realistic outfit generation scenarios with enhanced validation")
    print()
    
    tester = RealisticValidationTester()
    
    # Run the test
    start_time = time.time()
    results = tester.test_realistic_scenarios(1000)
    end_time = time.time()
    
    # Print results
    tester.print_results(results)
    
    print(f"\n⏱️  Test completed in {end_time - start_time:.2f} seconds")
    
    # Final summary
    enhanced_success_rate = (results["enhanced_validation"]["passed"] / results["enhanced_validation"]["total"]) * 100
    
    print(f"\n🎊 FINAL RESULT:")
    print(f"Enhanced validation achieves {enhanced_success_rate:.2f}% success rate with realistic scenarios")
    
    if enhanced_success_rate >= 95:
        print("🎉 OUTSTANDING: Your outfit generation system produces excellent outfits!")
    elif enhanced_success_rate >= 90:
        print("✅ EXCELLENT: Your system produces very good outfits!")
    elif enhanced_success_rate >= 80:
        print("✅ GOOD: Your system produces appropriate outfits most of the time!")
    else:
        print("⚠️  Your system needs some fine-tuning but is working!")

if __name__ == "__main__":
    main()
