#!/usr/bin/env python3
"""
Comprehensive Outfit Generation Simulation
Generates 1000 test outfit combinations to identify inappropriate outfits
and create rules to prevent them from happening again.
"""

import random
import json
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserProfile:
    id: str
    name: str
    gender: str
    age: int
    style_preferences: List[str]
    body_type: str
    favorite_colors: List[str]
    occupation: str
    lifestyle: str

@dataclass
class WardrobeItem:
    id: str
    name: str
    type: str
    color: str
    style: List[str]
    occasion: List[str]
    season: List[str]
    material: str
    formality_level: int  # 1=casual, 2=business casual, 3=formal, 4=very formal
    temperature_range: Tuple[int, int]
    gender: str
    age_range: Tuple[int, int]

@dataclass
class WeatherData:
    temperature: float
    condition: str
    humidity: int
    wind_speed: int
    precipitation: int

class ComprehensiveOutfitSimulator:
    """Simulates 1000 outfit generations to identify inappropriate combinations."""
    
    def __init__(self):
        self.inappropriate_outfits = []
        self.new_rules = []
        self.test_results = {
            "total_tests": 0,
            "inappropriate_found": 0,
            "success_rate": 0.0,
            "simulation_time": 0.0
        }
        
        # Define comprehensive test data
        self.user_profiles = self._generate_user_profiles()
        self.wardrobe_items = self._generate_wardrobe_items()
        self.occasions = self._generate_occasions()
        self.moods = self._generate_moods()
        self.weather_scenarios = self._generate_weather_scenarios()
        
        # Existing validation rules
        self.existing_rules = {
            "blazer_shorts": {
                "description": "Blazer + Shorts",
                "reason": "Blazers are formal wear and should not be paired with casual shorts",
                "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
                "keep_items": ["blazer", "suit jacket", "sport coat"]
            },
            "blazer_cargos": {
                "description": "Blazer + Cargo Pants",
                "reason": "Cargo pants are casual/athletic wear and should not be paired with formal blazers",
                "remove_items": ["cargo pants", "cargos", "cargo shorts", "cargo"],
                "keep_items": ["blazer", "suit jacket", "sport coat", "jacket"]
            },
            "blazer_flip_flops": {
                "description": "Blazer + Flip Flops",
                "reason": "Blazers are formal wear and should not be paired with flip flops",
                "remove_items": ["flip-flops", "flip flops", "slides", "thongs"],
                "keep_items": ["blazer", "suit jacket", "sport coat"]
            },
            "formal_shoes_shorts": {
                "description": "Formal Shoes + Shorts",
                "reason": "Formal shoes should not be worn with shorts",
                "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
                "keep_items": ["oxford", "loafers", "dress shoes", "heels", "pumps"]
            },
            "business_athletic": {
                "description": "Business Wear + Athletic Wear",
                "reason": "Business items should not be mixed with athletic wear",
                "remove_items": ["athletic shorts", "basketball shorts", "sweatpants", "athletic pants"],
                "keep_items": ["blazer", "suit", "dress shirt", "dress pants"]
            }
        }
    
    def _generate_user_profiles(self) -> List[UserProfile]:
        """Generate diverse user profiles for testing."""
        profiles = []
        
        genders = ["male", "female", "non-binary"]
        age_ranges = [(18, 25), (26, 35), (36, 45), (46, 55), (56, 65)]
        style_prefs = [
            ["casual", "minimalist"],
            ["formal", "professional"],
            ["bohemian", "eclectic"],
            ["athletic", "sporty"],
            ["vintage", "retro"],
            ["modern", "contemporary"],
            ["classic", "timeless"]
        ]
        body_types = ["rectangle", "pear", "apple", "hourglass", "inverted triangle"]
        occupations = ["student", "professional", "creative", "athlete", "entrepreneur", "teacher", "healthcare"]
        lifestyles = ["urban", "suburban", "rural", "traveler", "homebody", "social", "outdoor"]
        
        for i in range(100):
            gender = random.choice(genders)
            age_range = random.choice(age_ranges)
            age = random.randint(age_range[0], age_range[1])
            
            profiles.append(UserProfile(
                id=f"user_{i:03d}",
                name=f"User {i}",
                gender=gender,
                age=age,
                style_preferences=random.choice(style_prefs),
                body_type=random.choice(body_types),
                favorite_colors=random.sample(["black", "white", "navy", "gray", "red", "blue", "green", "brown", "pink", "purple"], 3),
                occupation=random.choice(occupations),
                lifestyle=random.choice(lifestyles)
            ))
        
        return profiles
    
    def _generate_wardrobe_items(self) -> List[WardrobeItem]:
        """Generate comprehensive wardrobe items for testing."""
        items = []
        
        # Define comprehensive item types with attributes
        item_definitions = [
            # Formal Items
            {"type": "blazer", "formality": 3, "styles": ["formal", "business"], "occasions": ["business", "formal"], "seasons": ["spring", "fall", "winter"], "temp_range": (50, 75)},
            {"type": "suit", "formality": 4, "styles": ["formal", "business"], "occasions": ["formal", "business"], "seasons": ["all"], "temp_range": (45, 80)},
            {"type": "dress shirt", "formality": 3, "styles": ["formal", "business"], "occasions": ["business", "formal"], "seasons": ["all"], "temp_range": (50, 85)},
            {"type": "dress pants", "formality": 3, "styles": ["formal", "business"], "occasions": ["business", "formal"], "seasons": ["all"], "temp_range": (45, 80)},
            {"type": "oxford", "formality": 3, "styles": ["formal", "business"], "occasions": ["business", "formal"], "seasons": ["all"], "temp_range": (40, 85)},
            {"type": "heels", "formality": 3, "styles": ["formal", "elegant"], "occasions": ["formal", "business"], "seasons": ["all"], "temp_range": (40, 85)},
            
            # Business Casual Items
            {"type": "polo shirt", "formality": 2, "styles": ["business casual", "preppy"], "occasions": ["business casual", "casual"], "seasons": ["spring", "summer"], "temp_range": (60, 90)},
            {"type": "chinos", "formality": 2, "styles": ["business casual", "preppy"], "occasions": ["business casual", "casual"], "seasons": ["all"], "temp_range": (50, 80)},
            {"type": "loafers", "formality": 2, "styles": ["business casual", "preppy"], "occasions": ["business casual", "casual"], "seasons": ["all"], "temp_range": (50, 85)},
            {"type": "cardigan", "formality": 2, "styles": ["business casual", "preppy"], "occasions": ["business casual", "casual"], "seasons": ["fall", "winter"], "temp_range": (45, 70)},
            
            # Casual Items
            {"type": "t-shirt", "formality": 1, "styles": ["casual", "athletic"], "occasions": ["casual", "athletic"], "seasons": ["spring", "summer"], "temp_range": (60, 95)},
            {"type": "jeans", "formality": 1, "styles": ["casual"], "occasions": ["casual"], "seasons": ["all"], "temp_range": (40, 75)},
            {"type": "sneakers", "formality": 1, "styles": ["casual", "athletic"], "occasions": ["casual", "athletic"], "seasons": ["all"], "temp_range": (40, 85)},
            {"type": "hoodie", "formality": 1, "styles": ["casual", "athletic"], "occasions": ["casual", "athletic"], "seasons": ["fall", "winter"], "temp_range": (30, 65)},
            
            # Athletic Items
            {"type": "athletic shorts", "formality": 1, "styles": ["athletic", "casual"], "occasions": ["athletic", "casual"], "seasons": ["spring", "summer"], "temp_range": (70, 95)},
            {"type": "athletic pants", "formality": 1, "styles": ["athletic"], "occasions": ["athletic"], "seasons": ["all"], "temp_range": (40, 80)},
            {"type": "tank top", "formality": 1, "styles": ["athletic", "casual"], "occasions": ["athletic", "casual"], "seasons": ["spring", "summer"], "temp_range": (70, 100)},
            
            # Problematic Items (should be filtered with formal items)
            {"type": "cargo pants", "formality": 1, "styles": ["casual", "athletic"], "occasions": ["casual", "athletic"], "seasons": ["all"], "temp_range": (50, 80)},
            {"type": "flip-flops", "formality": 1, "styles": ["casual", "beach"], "occasions": ["casual", "beach"], "seasons": ["spring", "summer"], "temp_range": (75, 100)},
            {"type": "slides", "formality": 1, "styles": ["casual", "athletic"], "occasions": ["casual", "athletic"], "seasons": ["spring", "summer"], "temp_range": (70, 95)},
            
            # Weather-specific items
            {"type": "winter coat", "formality": 2, "styles": ["formal", "warm"], "occasions": ["formal", "business"], "seasons": ["winter"], "temp_range": (20, 50)},
            {"type": "summer dress", "formality": 1, "styles": ["casual", "summer"], "occasions": ["casual"], "seasons": ["summer"], "temp_range": (70, 95)},
            {"type": "sandals", "formality": 1, "styles": ["casual", "summer"], "occasions": ["casual"], "seasons": ["spring", "summer"], "temp_range": (70, 95)},
            
            # Additional items for comprehensive testing
            {"type": "sweater", "formality": 2, "styles": ["casual", "business casual"], "occasions": ["casual", "business casual"], "seasons": ["fall", "winter"], "temp_range": (30, 70)},
            {"type": "skirt", "formality": 2, "styles": ["casual", "business casual"], "occasions": ["casual", "business casual"], "seasons": ["all"], "temp_range": (50, 80)},
            {"type": "boots", "formality": 2, "styles": ["casual", "business casual"], "occasions": ["casual", "business casual"], "seasons": ["fall", "winter"], "temp_range": (30, 70)},
            {"type": "dress", "formality": 3, "styles": ["formal", "elegant"], "occasions": ["formal", "business"], "seasons": ["all"], "temp_range": (50, 85)},
            {"type": "blouse", "formality": 2, "styles": ["business casual", "feminine"], "occasions": ["business casual", "casual"], "seasons": ["all"], "temp_range": (50, 85)},
        ]
        
        colors = ["black", "white", "navy", "gray", "blue", "red", "green", "brown", "pink", "purple", "yellow", "orange"]
        materials = ["cotton", "wool", "polyester", "silk", "denim", "leather", "synthetic", "linen", "cashmere"]
        
        for i, definition in enumerate(item_definitions):
            for color in colors[:3]:  # 3 colors per item type
                for material in materials[:2]:  # 2 materials per item type
                    items.append(WardrobeItem(
                        id=f"{definition['type']}_{color}_{i}",
                        name=f"{color.title()} {definition['type'].replace('_', ' ').title()}",
                        type=definition["type"],
                        color=color,
                        style=definition["styles"],
                        occasion=definition["occasions"],
                        season=definition["seasons"],
                        material=material,
                        formality_level=definition["formality"],
                        temperature_range=definition["temp_range"],
                        gender="unisex",
                        age_range=(18, 65)
                    ))
        
        return items
    
    def _generate_occasions(self) -> List[str]:
        """Generate comprehensive occasion types."""
        return [
            "business", "business casual", "formal", "casual", "athletic", "date night",
            "interview", "wedding", "funeral", "party", "gym", "beach", "travel",
            "presentation", "meeting", "lunch", "dinner", "brunch", "shopping",
            "outdoor activity", "concert", "theater", "museum", "church", "family gathering"
        ]
    
    def _generate_moods(self) -> List[str]:
        """Generate comprehensive mood types."""
        return [
            "confident", "relaxed", "professional", "casual", "elegant", "playful",
            "serious", "creative", "athletic", "romantic", "adventurous", "comfortable",
            "stylish", "minimalist", "bold", "conservative", "trendy", "classic",
            "energetic", "calm", "sophisticated", "youthful", "mature", "edgy"
        ]
    
    def _generate_weather_scenarios(self) -> List[WeatherData]:
        """Generate comprehensive weather scenarios."""
        scenarios = []
        
        # Temperature ranges
        temp_ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
        conditions = ["sunny", "cloudy", "rainy", "snowy", "windy", "foggy", "clear", "overcast"]
        
        for temp_range in temp_ranges:
            for condition in conditions:
                temp = random.randint(temp_range[0], temp_range[1])
                scenarios.append(WeatherData(
                    temperature=temp,
                    condition=condition,
                    humidity=random.randint(20, 90),
                    wind_speed=random.randint(0, 25),
                    precipitation=random.randint(0, 100) if condition in ["rainy", "snowy"] else 0
                ))
        
        return scenarios
    
    def simulate_outfit_generation(self, user_profile: UserProfile, occasion: str, mood: str, weather: WeatherData) -> Dict[str, Any]:
        """Simulate outfit generation and check for inappropriate combinations."""
        
        # Filter wardrobe items based on user profile and context
        suitable_items = []
        
        for item in self.wardrobe_items:
            # Basic filtering
            if (item.formality_level >= 2 and "formal" in occasion) or \
               (item.formality_level <= 2 and "casual" in occasion) or \
               (item.formality_level == 1 and "athletic" in occasion):
                
                # Weather filtering
                if weather.temperature >= item.temperature_range[0] and weather.temperature <= item.temperature_range[1]:
                    
                    # Occasion filtering
                    if any(occ in item.occasion for occ in [occasion]):
                        suitable_items.append(item)
        
        # If no suitable items found, use broader criteria
        if not suitable_items:
            for item in self.wardrobe_items:
                if weather.temperature >= item.temperature_range[0] and weather.temperature <= item.temperature_range[1]:
                    suitable_items.append(item)
        
        # Select 2-4 items for outfit
        if len(suitable_items) >= 2:
            num_items = random.randint(2, min(4, len(suitable_items)))
            selected_items = random.sample(suitable_items, num_items)
            
            # Apply existing validation rules
            filtered_items = self._apply_existing_rules(selected_items)
            
            return {
                "success": True,
                "outfit": {"items": filtered_items},
                "user_profile": user_profile,
                "occasion": occasion,
                "mood": mood,
                "weather": weather,
                "original_items": selected_items,
                "filtered": len(selected_items) != len(filtered_items)
            }
        else:
            return {
                "success": False,
                "outfit": {"items": []},
                "user_profile": user_profile,
                "occasion": occasion,
                "mood": mood,
                "weather": weather,
                "original_items": [],
                "filtered": False
            }
    
    def _apply_existing_rules(self, items: List[WardrobeItem]) -> List[WardrobeItem]:
        """Apply existing validation rules to filter out inappropriate combinations."""
        filtered_items = items.copy()
        
        for rule_name, rule in self.existing_rules.items():
            keep_items = rule.get("keep_items", [])
            remove_items = rule.get("remove_items", [])
            
            # Find items that should be kept (formal items)
            has_formal_items = False
            for item in filtered_items:
                item_type = item.type.lower()
                item_name = item.name.lower()
                
                # Check if this item should be kept
                should_keep = any(keep_type in item_type or keep_type in item_name for keep_type in keep_items)
                if should_keep:
                    has_formal_items = True
                    break
            
            # If we have formal items that should be kept, remove casual items
            if has_formal_items:
                items_to_remove = []
                for item in filtered_items:
                    item_type = item.type.lower()
                    item_name = item.name.lower()
                    
                    # Check if this item should be removed
                    should_remove = any(remove_type in item_type or remove_type in item_name for remove_type in remove_items)
                    
                    if should_remove:
                        items_to_remove.append(item)
                
                # Remove the inappropriate items
                for item in items_to_remove:
                    if item in filtered_items:
                        filtered_items.remove(item)
        
        return filtered_items
    
    def _check_inappropriate_combination(self, outfit_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if the outfit contains inappropriate combinations."""
        items = outfit_data["outfit"]["items"]
        issues = []
        
        if not items:
            return False, []
        
        # Check for various inappropriate combinations
        item_types = [item.type.lower() for item in items]
        item_names = [item.name.lower() for item in items]
        formality_levels = [item.formality_level for item in items]
        
        # Check for formality mismatches
        if len(set(formality_levels)) > 2:  # More than 2 different formality levels
            issues.append(f"Formality mismatch: levels {sorted(set(formality_levels))}")
        
        # Check for specific inappropriate combinations
        has_blazer = any("blazer" in item_type for item_type in item_types)
        has_suit = any("suit" in item_type for item_type in item_types)
        has_formal_shoes = any(item_type in ["oxford", "heels", "loafers"] for item_type in item_types)
        
        # Blazer/suit with casual items
        if has_blazer or has_suit:
            casual_items = [item_type for item_type in item_types if item_type in ["shorts", "athletic shorts", "cargo pants", "flip-flops", "slides", "tank top"]]
            if casual_items:
                issues.append(f"Formal item with casual items: {casual_items}")
        
        # Formal shoes with casual bottoms
        if has_formal_shoes:
            casual_bottoms = [item_type for item_type in item_types if item_type in ["shorts", "athletic shorts", "cargo pants"]]
            if casual_bottoms:
                issues.append(f"Formal shoes with casual bottoms: {casual_bottoms}")
        
        # Weather inappropriateness
        weather = outfit_data["weather"]
        for item in items:
            if weather.temperature > item.temperature_range[1]:
                issues.append(f"Weather too hot for {item.name} (temp: {weather.temperature}°F, max: {item.temperature_range[1]}°F)")
            elif weather.temperature < item.temperature_range[0]:
                issues.append(f"Weather too cold for {item.name} (temp: {weather.temperature}°F, min: {item.temperature_range[0]}°F)")
        
        # Occasion inappropriateness
        occasion = outfit_data["occasion"].lower()
        if "formal" in occasion or "business" in occasion:
            casual_items = [item_type for item_type in item_types if item_type in ["t-shirt", "shorts", "sneakers", "hoodie"]]
            if casual_items:
                issues.append(f"Occasion too formal for casual items: {casual_items}")
        elif "athletic" in occasion or "gym" in occasion:
            formal_items = [item_type for item_type in item_types if item_type in ["blazer", "suit", "dress shirt", "oxford", "heels"]]
            if formal_items:
                issues.append(f"Occasion too casual for formal items: {formal_items}")
        
        return len(issues) > 0, issues
    
    def run_comprehensive_simulation(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Run comprehensive simulation with 1000 outfit generations."""
        print(f"🚀 Starting Comprehensive Outfit Generation Simulation")
        print(f"🎯 Testing {num_tests} outfit combinations")
        print("=" * 80)
        
        start_time = time.time()
        
        for i in range(num_tests):
            if (i + 1) % 100 == 0:
                print(f"   Progress: {i + 1}/{num_tests} ({((i + 1)/num_tests)*100:.1f}%)")
            
            # Select random parameters
            user_profile = random.choice(self.user_profiles)
            occasion = random.choice(self.occasions)
            mood = random.choice(self.moods)
            weather = random.choice(self.weather_scenarios)
            
            # Generate outfit
            outfit_data = self.simulate_outfit_generation(user_profile, occasion, mood, weather)
            
            if outfit_data["success"]:
                # Check for inappropriate combinations
                is_inappropriate, issues = self._check_inappropriate_combination(outfit_data)
                
                if is_inappropriate:
                    self.inappropriate_outfits.append({
                        "outfit_data": outfit_data,
                        "issues": issues,
                        "test_number": i + 1
                    })
        
        end_time = time.time()
        
        # Calculate results
        self.test_results = {
            "total_tests": num_tests,
            "successful_generations": len([o for o in self.inappropriate_outfits if o["outfit_data"]["success"]]),
            "inappropriate_found": len(self.inappropriate_outfits),
            "success_rate": ((num_tests - len(self.inappropriate_outfits)) / num_tests) * 100,
            "simulation_time": end_time - start_time
        }
        
        return self.test_results
    
    def analyze_inappropriate_outfits(self) -> List[Dict[str, Any]]:
        """Analyze inappropriate outfits and create new rules."""
        print(f"\n🔍 Analyzing {len(self.inappropriate_outfits)} Inappropriate Outfits")
        print("=" * 80)
        
        # Group issues by type
        issue_patterns = {}
        
        for outfit in self.inappropriate_outfits:
            for issue in outfit["issues"]:
                # Categorize the issue
                if "Formal item with casual items" in issue:
                    category = "formal_casual_mismatch"
                elif "Formal shoes with casual bottoms" in issue:
                    category = "formal_shoes_casual_bottoms"
                elif "Formality mismatch" in issue:
                    category = "formality_mismatch"
                elif "Weather too" in issue:
                    category = "weather_inappropriate"
                elif "Occasion too" in issue:
                    category = "occasion_inappropriate"
                else:
                    category = "other"
                
                if category not in issue_patterns:
                    issue_patterns[category] = []
                issue_patterns[category].append(outfit)
        
        # Create new rules based on patterns
        new_rules = []
        
        for category, outfits in issue_patterns.items():
            if len(outfits) >= 5:  # Only create rules for patterns that occur 5+ times
                rule = self._create_rule_from_pattern(category, outfits)
                if rule:
                    new_rules.append(rule)
        
        self.new_rules = new_rules
        return new_rules
    
    def _create_rule_from_pattern(self, category: str, outfits: List[Dict]) -> Dict[str, Any]:
        """Create a new validation rule from a pattern of inappropriate outfits."""
        
        if category == "formal_casual_mismatch":
            return {
                "rule_name": f"enhanced_formal_casual_{len(self.new_rules)}",
                "description": "Enhanced Formal + Casual Prevention",
                "reason": "Formal items should not be paired with casual items",
                "remove_items": ["shorts", "athletic shorts", "cargo pants", "flip-flops", "slides", "tank top", "hoodie"],
                "keep_items": ["blazer", "suit", "dress shirt", "oxford", "heels", "dress pants"],
                "frequency": len(outfits),
                "category": category
            }
        
        elif category == "formal_shoes_casual_bottoms":
            return {
                "rule_name": f"enhanced_formal_shoes_{len(self.new_rules)}",
                "description": "Enhanced Formal Shoes + Casual Bottoms Prevention",
                "reason": "Formal shoes should not be worn with casual bottoms",
                "remove_items": ["shorts", "athletic shorts", "cargo pants", "athletic pants"],
                "keep_items": ["oxford", "loafers", "dress shoes", "heels", "pumps"],
                "frequency": len(outfits),
                "category": category
            }
        
        elif category == "formality_mismatch":
            return {
                "rule_name": f"formality_consistency_{len(self.new_rules)}",
                "description": "Formality Consistency Rule",
                "reason": "Outfit items should have consistent formality levels",
                "remove_items": [],  # This would be a more complex rule
                "keep_items": [],
                "frequency": len(outfits),
                "category": category,
                "complex_rule": True
            }
        
        elif category == "weather_inappropriate":
            return {
                "rule_name": f"weather_appropriateness_{len(self.new_rules)}",
                "description": "Weather Appropriateness Rule",
                "reason": "Items should be appropriate for the weather conditions",
                "remove_items": [],  # This would be weather-specific
                "keep_items": [],
                "frequency": len(outfits),
                "category": category,
                "weather_rule": True
            }
        
        elif category == "occasion_inappropriate":
            return {
                "rule_name": f"occasion_appropriateness_{len(self.new_rules)}",
                "description": "Occasion Appropriateness Rule",
                "reason": "Items should be appropriate for the occasion",
                "remove_items": [],  # This would be occasion-specific
                "keep_items": [],
                "frequency": len(outfits),
                "category": category,
                "occasion_rule": True
            }
        
        return None
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        
        report.append("# 🧪 Comprehensive Outfit Generation Test Report")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("## 📊 Test Summary")
        report.append(f"- **Total Tests**: {self.test_results['total_tests']:,}")
        report.append(f"- **Inappropriate Outfits Found**: {self.test_results['inappropriate_found']:,}")
        report.append(f"- **Success Rate**: {self.test_results['success_rate']:.2f}%")
        report.append(f"- **Simulation Time**: {self.test_results['simulation_time']:.2f} seconds")
        report.append("")
        
        # Inappropriate outfits analysis
        if self.inappropriate_outfits:
            report.append("## ❌ Inappropriate Outfits Found")
            report.append("")
            
            # Group by issue type
            issue_counts = {}
            for outfit in self.inappropriate_outfits:
                for issue in outfit["issues"]:
                    issue_type = issue.split(":")[0] if ":" in issue else issue
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            report.append("### Issue Frequency:")
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {issue_type}: {count} occurrences")
            report.append("")
            
            # Show examples
            report.append("### Example Inappropriate Outfits:")
            for i, outfit in enumerate(self.inappropriate_outfits[:10]):  # Show first 10
                report.append(f"\n#### Example {i+1}:")
                report.append(f"- **User**: {outfit['outfit_data']['user_profile'].name} ({outfit['outfit_data']['user_profile'].gender}, {outfit['outfit_data']['user_profile'].age}yo)")
                report.append(f"- **Occasion**: {outfit['outfit_data']['occasion']}")
                report.append(f"- **Mood**: {outfit['outfit_data']['mood']}")
                report.append(f"- **Weather**: {outfit['outfit_data']['weather'].temperature}°F, {outfit['outfit_data']['weather'].condition}")
                report.append(f"- **Items**: {[item.name for item in outfit['outfit_data']['outfit']['items']]}")
                report.append(f"- **Issues**: {outfit['issues']}")
        
        # New rules
        if self.new_rules:
            report.append("\n## 🆕 New Validation Rules Recommended")
            report.append("")
            
            for rule in self.new_rules:
                report.append(f"### {rule['description']}")
                report.append(f"- **Frequency**: {rule['frequency']} occurrences")
                report.append(f"- **Reason**: {rule['reason']}")
                if rule.get('remove_items'):
                    report.append(f"- **Remove Items**: {rule['remove_items']}")
                if rule.get('keep_items'):
                    report.append(f"- **Keep Items**: {rule['keep_items']}")
                report.append("")
        
        # Recommendations
        report.append("## 🎯 Recommendations")
        report.append("")
        
        if self.test_results['success_rate'] >= 99:
            report.append("✅ **Excellent Performance**: Success rate is 99%+ - system is working very well")
        elif self.test_results['success_rate'] >= 95:
            report.append("⚠️ **Good Performance**: Success rate is 95%+ - minor improvements needed")
        else:
            report.append("❌ **Needs Improvement**: Success rate below 95% - significant improvements needed")
        
        report.append("")
        report.append(f"### Action Items:")
        if self.new_rules:
            report.append(f"1. Implement {len(self.new_rules)} new validation rules")
        report.append(f"2. Review {self.test_results['inappropriate_found']} inappropriate outfit examples")
        report.append("3. Test new rules with additional simulations")
        report.append("4. Monitor production for similar issues")
        
        return "\n".join(report)
    
    def save_results(self, filename: str = "comprehensive_simulation_results.json"):
        """Save simulation results to JSON file."""
        results = {
            "test_results": self.test_results,
            "inappropriate_outfits": [
                {
                    "test_number": outfit["test_number"],
                    "user_profile": {
                        "id": outfit["outfit_data"]["user_profile"].id,
                        "gender": outfit["outfit_data"]["user_profile"].gender,
                        "age": outfit["outfit_data"]["user_profile"].age,
                        "style_preferences": outfit["outfit_data"]["user_profile"].style_preferences,
                        "occupation": outfit["outfit_data"]["user_profile"].occupation
                    },
                    "occasion": outfit["outfit_data"]["occasion"],
                    "mood": outfit["outfit_data"]["mood"],
                    "weather": {
                        "temperature": outfit["outfit_data"]["weather"].temperature,
                        "condition": outfit["outfit_data"]["weather"].condition
                    },
                    "items": [{"name": item.name, "type": item.type, "formality_level": item.formality_level} for item in outfit["outfit_data"]["outfit"]["items"]],
                    "issues": outfit["issues"]
                }
                for outfit in self.inappropriate_outfits
            ],
            "new_rules": self.new_rules,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results saved to {filename}")

def main():
    """Run the comprehensive simulation."""
    simulator = ComprehensiveOutfitSimulator()
    
    # Run simulation
    results = simulator.run_comprehensive_simulation(1000)
    
    # Analyze results
    new_rules = simulator.analyze_inappropriate_outfits()
    
    # Generate and print report
    report = simulator.generate_report()
    print(report)
    
    # Save results
    simulator.save_results()
    
    # Print summary
    print(f"\n🎉 SIMULATION COMPLETE!")
    print(f"📊 Success Rate: {results['success_rate']:.2f}%")
    print(f"❌ Inappropriate Outfits: {results['inappropriate_found']}")
    print(f"🆕 New Rules Recommended: {len(new_rules)}")
    
    if results['success_rate'] >= 99:
        print("✅ EXCELLENT: System is performing at 99%+ success rate!")
    elif results['success_rate'] >= 95:
        print("⚠️ GOOD: Minor improvements needed")
    else:
        print("❌ NEEDS WORK: Significant improvements required")

if __name__ == "__main__":
    main()
