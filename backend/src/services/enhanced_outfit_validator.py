#!/usr/bin/env python3
"""
Enhanced Outfit Validator - Integrated Thought Clarification System
================================================================

This validator uses integrated thought clarification to systematically prevent
inappropriate outfit combinations through multi-layered validation:

1. Pre-validation filtering (prevent bad items from entering)
2. Core validation (check inappropriate combinations) 
3. Occasion-specific validation (strict business/formal rules)
4. Formality consistency validation (ensure outfit coherence)
5. Robust error handling (no fallback to bad outfits)

The system prevents outfits like:
- Business occasion with shorts and casual shoes
- Formal jackets with athletic wear
- Inconsistent formality levels
- Weather-inappropriate combinations
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from .visual_harmony_validator import VisualHarmonyValidator, VisualHarmonyResult

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"    # Must fix - outfit completely inappropriate
    HIGH = "high"           # Should fix - major style violation
    MEDIUM = "medium"       # Consider fixing - minor style issue
    LOW = "low"            # Optional fix - style preference

class FormalityLevel(Enum):
    """Formality levels for consistency checking"""
    FORMAL = "formal"           # Suits, dress shoes, dress shirts
    BUSINESS_FORMAL = "business_formal"  # Business suits, dress shirts
    BUSINESS_CASUAL = "business_casual"  # Blazers, dress pants, loafers
    SMART_CASUAL = "smart_casual"       # Button-ups, chinos, clean sneakers
    CASUAL = "casual"          # T-shirts, jeans, sneakers
    ATHLETIC = "athletic"      # Athletic wear, gym clothes
    LOUNGEWEAR = "loungewear"  # Comfortable home wear

@dataclass
class ValidationResult:
    """Enhanced validation result with detailed feedback"""
    is_valid: bool
    severity: ValidationSeverity
    issues: List[str]
    suggestions: List[str]
    confidence_score: float
    filtered_items: List[Dict[str, Any]]
    validation_details: Dict[str, Any]

class EnhancedOutfitValidator:
    """
    Enhanced Outfit Validator with Integrated Thought Clarification
    
    This validator systematically prevents inappropriate outfit combinations
    through comprehensive multi-layered validation.
    """
    
    def __init__(self):
        # Initialize formality mapping
        self.formality_mapping = self._initialize_formality_mapping()
        
        # Initialize inappropriate combinations database
        self.inappropriate_combinations = self._initialize_inappropriate_combinations()
        
        # Initialize occasion-specific rules
        self.occasion_rules = self._initialize_occasion_rules()
        
        # Initialize style-specific rules
        self.style_rules = self._initialize_style_rules()
        
        # Initialize mood-specific rules
        self.mood_rules = self._initialize_mood_rules()
        
        # Initialize visual harmony validator
        self.visual_harmony_validator = VisualHarmonyValidator()
        
        # Initialize validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "inappropriate_combinations_prevented": 0,
            "visual_harmony_validations": 0
        }
    
    def _initialize_formality_mapping(self) -> Dict[str, FormalityLevel]:
        """Initialize formality level mapping for items"""
        return {
            # Formal items
            "suit": FormalityLevel.FORMAL,
            "tuxedo": FormalityLevel.FORMAL,
            "dress_shirt": FormalityLevel.BUSINESS_FORMAL,
            "dress_pants": FormalityLevel.BUSINESS_FORMAL,
            "dress_shoes": FormalityLevel.BUSINESS_FORMAL,
            "oxford": FormalityLevel.BUSINESS_FORMAL,
            "loafers": FormalityLevel.BUSINESS_CASUAL,
            "blazer": FormalityLevel.BUSINESS_CASUAL,
            "sport_coat": FormalityLevel.BUSINESS_CASUAL,
            
            # Business casual items
            "button_up": FormalityLevel.BUSINESS_CASUAL,
            "button_down": FormalityLevel.BUSINESS_CASUAL,
            "chinos": FormalityLevel.BUSINESS_CASUAL,
            "polo": FormalityLevel.SMART_CASUAL,
            
            # Casual items
            "t_shirt": FormalityLevel.CASUAL,
            "tank_top": FormalityLevel.CASUAL,
            "jeans": FormalityLevel.CASUAL,
            "sneakers": FormalityLevel.CASUAL,
            "hoodie": FormalityLevel.CASUAL,
            "sweatshirt": FormalityLevel.CASUAL,
            
            # Athletic items
            "athletic_shorts": FormalityLevel.ATHLETIC,
            "basketball_shorts": FormalityLevel.ATHLETIC,
            "athletic_pants": FormalityLevel.ATHLETIC,
            "athletic_shirt": FormalityLevel.ATHLETIC,
            "gym_shorts": FormalityLevel.ATHLETIC,
            "workout_pants": FormalityLevel.ATHLETIC,
            
            # Loungewear items
            "pajamas": FormalityLevel.LOUNGEWEAR,
            "lounge_pants": FormalityLevel.LOUNGEWEAR,
            "sweatpants": FormalityLevel.LOUNGEWEAR,
            "house_shoes": FormalityLevel.LOUNGEWEAR,
        }
    
    def _initialize_inappropriate_combinations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive inappropriate combinations database"""
        return {
            # CRITICAL: Business/Formal Occasion Violations
            "business_shorts": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Shorts with Business Occasion",
                "reason": "Shorts are never appropriate for business occasions",
                "trigger_items": ["shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts", "cargo_shorts"],
                "trigger_occasions": ["business", "interview", "formal", "professional"],
                "action": "remove_trigger_items"
            },
            
            "business_casual_shoes": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Casual Shoes with Business Occasion",
                "reason": "Business occasions require formal or business casual shoes",
                "trigger_items": ["sneakers", "athletic_shoes", "flip_flops", "sandals", "canvas_shoes"],
                "trigger_occasions": ["business", "interview", "formal", "professional"],
                "action": "remove_trigger_items"
            },
            
            "formal_jacket_casual_bottoms": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Formal Jacket with Casual Bottoms",
                "reason": "Formal jackets require formal or business casual bottoms",
                "trigger_items": ["shorts", "athletic_shorts", "basketball_shorts", "sweatpants", "athletic_pants"],
                "required_with": ["blazer", "suit_jacket", "sport_coat", "formal_jacket"],
                "action": "remove_trigger_items"
            },
            
            "business_athletic_mix": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Business Wear with Athletic Wear",
                "reason": "Business and athletic wear should not be mixed",
                "trigger_items": ["athletic_shorts", "basketball_shorts", "athletic_pants", "gym_shorts", "workout_pants"],
                "required_with": ["dress_shirt", "blazer", "suit_jacket", "business_shirt"],
                "action": "remove_trigger_items"
            },
            
            # HIGH: Formality Inconsistency
            "formality_mismatch": {
                "severity": ValidationSeverity.HIGH,
                "description": "Formality Level Mismatch",
                "reason": "Items should have consistent formality levels",
                "max_formality_gap": 2,  # Max gap between formality levels
                "action": "adjust_formality"
            },
            
            # MEDIUM: Style Consistency
            "style_inconsistency": {
                "severity": ValidationSeverity.MEDIUM,
                "description": "Style Inconsistency",
                "reason": "Items should have compatible styles",
                "action": "suggest_alternatives"
            }
        }
    
    def _initialize_occasion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize strict occasion-specific validation rules"""
        return {
            "business": {
                "required_formality": FormalityLevel.BUSINESS_CASUAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants"
                ],
                "required_items": ["dress_shirt", "button_up", "blazer", "dress_pants", "chinos"],
                "preferred_shoes": ["dress_shoes", "oxford", "loafers", "business_casual_shoes"],
                "min_formality": FormalityLevel.BUSINESS_CASUAL
            },
            
            "business_formal": {
                "required_formality": FormalityLevel.BUSINESS_FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["dress_shirt", "dress_pants", "dress_shoes", "blazer", "suit"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.BUSINESS_FORMAL
            },
            
            "interview": {
                "required_formality": FormalityLevel.BUSINESS_FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes"
                ],
                "required_items": ["dress_shirt", "dress_pants", "dress_shoes", "blazer", "suit"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.BUSINESS_FORMAL
            },
            
            "formal": {
                "required_formality": FormalityLevel.FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["suit", "dress_shirt", "dress_pants", "dress_shoes"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.FORMAL
            },
            
            "casual": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["casual_top", "casual_bottom", "casual_shoes"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "weekend": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "party": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal",
                    "athletic_shorts", "basketball_shorts", "gym_clothes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers", "boots"],
                "min_formality": FormalityLevel.CASUAL,
                "notes": "Party occasions allow casual wear including shorts and sneakers"
            },
            
            "date": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal",
                    "athletic_shorts", "basketball_shorts", "gym_clothes", "athletic_shoes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["loafers", "boots", "casual_shoes"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            # Additional comprehensive occasion rules for all frontend options
            "business_casual": {
                "required_formality": FormalityLevel.BUSINESS_CASUAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants"
                ],
                "required_items": ["dress_shirt", "button_up", "blazer", "dress_pants", "chinos"],
                "preferred_shoes": ["dress_shoes", "oxford", "loafers", "business_casual_shoes"],
                "min_formality": FormalityLevel.BUSINESS_CASUAL
            },
            
            "work": {
                "required_formality": FormalityLevel.BUSINESS_CASUAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants"
                ],
                "required_items": ["dress_shirt", "button_up", "dress_pants", "chinos"],
                "preferred_shoes": ["dress_shoes", "oxford", "loafers", "business_casual_shoes"],
                "min_formality": FormalityLevel.BUSINESS_CASUAL
            },
            
            "date_night": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "athletic_shorts", "basketball_shorts", "gym_clothes",
                    "athletic_shoes", "running_shoes", "workout_clothes"
                ],
                "required_items": ["stylish_top", "stylish_bottom"],
                "preferred_shoes": ["dress_shoes", "heels", "stylish_sneakers", "boots"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "first_date": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "athletic_shorts", "basketball_shorts", "gym_clothes",
                    "athletic_shoes", "running_shoes", "workout_clothes"
                ],
                "required_items": ["stylish_top", "stylish_bottom"],
                "preferred_shoes": ["dress_shoes", "heels", "stylish_sneakers", "boots"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "brunch": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "athletic_shorts", "basketball_shorts", "gym_clothes",
                    "athletic_shoes", "running_shoes", "workout_clothes"
                ],
                "required_items": ["stylish_top", "stylish_bottom"],
                "preferred_shoes": ["dress_shoes", "heels", "stylish_sneakers", "boots"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "wedding_guest": {
                "required_formality": FormalityLevel.BUSINESS_FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["dress_shirt", "dress_pants", "dress_shoes", "blazer", "suit"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.BUSINESS_FORMAL
            },
            
            "cocktail": {
                "required_formality": FormalityLevel.BUSINESS_FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["dress_shirt", "dress_pants", "dress_shoes", "blazer", "suit"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.BUSINESS_FORMAL
            },
            
            "night_out": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "athletic_shorts", "basketball_shorts", "gym_clothes",
                    "athletic_shoes", "running_shoes", "workout_clothes"
                ],
                "required_items": ["stylish_top", "stylish_bottom"],
                "preferred_shoes": ["dress_shoes", "heels", "stylish_sneakers", "boots"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "gala": {
                "required_formality": FormalityLevel.FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["suit", "dress_shirt", "dress_pants", "dress_shoes"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.FORMAL
            },
            
            "travel": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["comfortable_top", "comfortable_bottom"],
                "preferred_shoes": ["comfortable_shoes", "sneakers", "casual_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "airport": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["comfortable_top", "comfortable_bottom"],
                "preferred_shoes": ["comfortable_shoes", "sneakers", "casual_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "beach": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "blazer", "dress_shoes", "formal_clothes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sandals", "flip_flops", "casual_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "vacation": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["comfortable_top", "comfortable_bottom"],
                "preferred_shoes": ["comfortable_shoes", "sneakers", "casual_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "festival": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "blazer", "dress_shoes", "formal_clothes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sneakers", "boots", "casual_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "rainy_day": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["weather_appropriate_top", "weather_appropriate_bottom"],
                "preferred_shoes": ["waterproof_shoes", "boots", "sneakers"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "snow_day": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["warm_top", "warm_bottom"],
                "preferred_shoes": ["winter_boots", "warm_shoes"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "hot_weather": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["light_top", "light_bottom"],
                "preferred_shoes": ["breathable_shoes", "sandals", "sneakers"],
                "min_formality": FormalityLevel.CASUAL
            },
            
        }
    
    def _initialize_style_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive style-specific validation rules"""
        return {
            # Academic & Intellectual Styles
            "dark_academia": {
                "color_palette": ["brown", "black", "cream", "burgundy", "navy", "forest_green"],
                "preferred_items": ["blazer", "dress_shirt", "dress_pants", "oxford_shoes", "turtleneck", "corduroy"],
                "forbidden_items": ["athletic_shorts", "bright_colors", "casual_sneakers", "tank_tops"],
                "texture_preference": ["wool", "tweed", "corduroy", "leather"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["vintage_watch", "leather_belt", "reading_glasses"]
            },
            
            "light_academia": {
                "color_palette": ["cream", "beige", "white", "light_brown", "pastel_blue", "sage_green"],
                "preferred_items": ["cardigan", "blouse", "pleated_skirt", "loafers", "lightweight_blazer"],
                "forbidden_items": ["dark_colors", "athletic_wear", "heavy_boots"],
                "texture_preference": ["cotton", "linen", "lightweight_wool"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["delicate_jewelry", "light_scarf", "canvas_bag"]
            },
            
            "old_money": {
                "color_palette": ["navy", "cream", "camel", "white", "black", "gold_accent"],
                "preferred_items": ["blazer", "polo_shirt", "chinos", "loafers", "cashmere_sweater"],
                "forbidden_items": ["athletic_wear", "bright_colors", "casual_sneakers"],
                "texture_preference": ["cashmere", "silk", "quality_cotton", "leather"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["gold_watch", "leather_belt", "quality_bag"]
            },
            
            # Trendy & Modern Styles
            "y2k": {
                "color_palette": ["pink", "silver", "metallic", "bright_neon", "white", "black"],
                "preferred_items": ["crop_top", "low_rise_jeans", "platform_shoes", "metallic_accessories"],
                "forbidden_items": ["formal_wear", "conservative_items"],
                "texture_preference": ["metallic", "synthetic", "shiny"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["chunky_jewelry", "platform_shoes", "bright_accessories"]
            },
            
            "coastal_grandmother": {
                "color_palette": ["white", "beige", "navy", "stripes", "natural_tones"],
                "preferred_items": ["linen_pants", "striped_shirt", "canvas_shoes", "lightweight_cardigan"],
                "forbidden_items": ["athletic_wear", "heavy_boots", "dark_colors"],
                "texture_preference": ["linen", "cotton", "canvas"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["straw_hat", "canvas_bag", "simple_jewelry"]
            },
            
            "clean_girl": {
                "color_palette": ["white", "beige", "cream", "black", "neutral_tones"],
                "preferred_items": ["minimalist_top", "tailored_pants", "white_sneakers", "simple_dress"],
                "forbidden_items": ["busy_patterns", "bright_colors", "athletic_wear"],
                "texture_preference": ["cotton", "linen", "silk"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["minimal_jewelry", "simple_bag", "clean_shoes"]
            },
            
            "cottagecore": {
                "color_palette": ["earth_tones", "pastels", "floral_patterns", "cream", "sage_green"],
                "preferred_items": ["floral_dress", "knit_cardigan", "ankle_boots", "vintage_blouse"],
                "forbidden_items": ["athletic_wear", "urban_styles", "bright_neon"],
                "texture_preference": ["cotton", "knit", "floral_prints", "natural_fibers"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["floral_accessories", "vintage_jewelry", "natural_bag"]
            },
            
            # Artistic & Creative Styles
            "avant_garde": {
                "color_palette": ["bold_colors", "metallic", "black", "white", "unusual_combinations"],
                "preferred_items": ["statement_pieces", "unusual_cuts", "artistic_accessories"],
                "forbidden_items": ["basic_items", "conservative_styles"],
                "texture_preference": ["unusual_textures", "metallic", "experimental_materials"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["statement_jewelry", "artistic_bags", "unique_shoes"]
            },
            
            "artsy": {
                "color_palette": ["mixed_colors", "artistic_patterns", "earth_tones", "bold_accents"],
                "preferred_items": ["unique_pieces", "artistic_prints", "vintage_items", "handmade_accessories"],
                "forbidden_items": ["mass_produced_basics", "athletic_wear"],
                "texture_preference": ["mixed_textures", "natural_fibers", "artistic_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["handmade_jewelry", "artistic_bags", "unique_accessories"]
            },
            
            "maximalist": {
                "color_palette": ["all_colors", "bold_patterns", "mixed_prints", "bright_combinations"],
                "preferred_items": ["patterned_items", "bold_accessories", "colorful_pieces", "statement_items"],
                "forbidden_items": ["plain_basics", "minimal_items"],
                "texture_preference": ["mixed_textures", "bold_patterns", "varied_materials"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["bold_jewelry", "colorful_bags", "statement_shoes"]
            },
            
            "colorblock": {
                "color_palette": ["bold_solid_colors", "contrasting_combinations", "bright_blocks"],
                "preferred_items": ["solid_color_pieces", "geometric_cuts", "bold_combinations"],
                "forbidden_items": ["subtle_patterns", "neutral_combinations"],
                "texture_preference": ["smooth_surfaces", "solid_colors", "clean_lines"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["colorful_accessories", "bold_jewelry", "bright_bags"]
            },
            
            # Professional & Classic Styles
            "business_casual": {
                "color_palette": ["navy", "white", "gray", "black", "subtle_patterns"],
                "preferred_items": ["blazer", "dress_shirt", "dress_pants", "loafers", "polo_shirt"],
                "forbidden_items": ["athletic_wear", "casual_sneakers", "tank_tops"],
                "texture_preference": ["cotton", "wool", "quality_fabrics"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["professional_watch", "leather_belt", "quality_bag"]
            },
            
            "classic": {
                "color_palette": ["navy", "white", "black", "gray", "camel", "neutral_tones"],
                "preferred_items": ["blazer", "dress_shirt", "dress_pants", "oxford_shoes", "cashmere_sweater"],
                "forbidden_items": ["trendy_items", "athletic_wear", "casual_sneakers"],
                "texture_preference": ["wool", "cotton", "silk", "quality_fabrics"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["timeless_jewelry", "quality_bag", "classic_shoes"]
            },
            
            "preppy": {
                "color_palette": ["navy", "white", "pink", "green", "stripes", "pastels"],
                "preferred_items": ["polo_shirt", "chinos", "loafers", "blazer", "cable_knit_sweater"],
                "forbidden_items": ["athletic_wear", "casual_sneakers", "dark_colors"],
                "texture_preference": ["cotton", "wool", "quality_fabrics"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["leather_belt", "quality_bag", "classic_watch"]
            },
            
            "urban_professional": {
                "color_palette": ["black", "white", "gray", "navy", "modern_neutrals"],
                "preferred_items": ["modern_blazer", "dress_shirt", "tailored_pants", "dress_shoes"],
                "forbidden_items": ["casual_wear", "athletic_wear", "outdated_styles"],
                "texture_preference": ["modern_fabrics", "quality_materials", "sleek_finishes"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["modern_watch", "sleek_bag", "contemporary_jewelry"]
            },
            
            # Urban & Street Styles
            "streetwear": {
                "color_palette": ["black", "white", "gray", "bold_accents", "urban_colors"],
                "preferred_items": ["hoodie", "sneakers", "jeans", "graphic_tee", "baseball_cap"],
                "forbidden_items": ["formal_wear", "dress_shoes", "business_attire"],
                "texture_preference": ["cotton", "denim", "synthetic_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["baseball_cap", "sneakers", "urban_bag"]
            },
            
            "techwear": {
                "color_palette": ["black", "gray", "white", "tech_colors", "metallic_accents"],
                "preferred_items": ["tech_jacket", "cargo_pants", "tech_sneakers", "utility_vest"],
                "forbidden_items": ["formal_wear", "traditional_business_attire"],
                "texture_preference": ["synthetic_materials", "tech_fabrics", "waterproof_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["tech_accessories", "utility_bag", "modern_watch"]
            },
            
            "grunge": {
                "color_palette": ["black", "gray", "flannel_patterns", "dark_colors", "faded_tones"],
                "preferred_items": ["flannel_shirt", "ripped_jeans", "combat_boots", "band_tee"],
                "forbidden_items": ["formal_wear", "preppy_styles", "bright_colors"],
                "texture_preference": ["denim", "cotton", "worn_fabrics"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["chunky_jewelry", "combat_boots", "vintage_bag"]
            },
            
            "hipster": {
                "color_palette": ["earth_tones", "vintage_colors", "muted_tones", "retro_patterns"],
                "preferred_items": ["vintage_tee", "skinny_jeans", "vintage_sneakers", "thick_framed_glasses"],
                "forbidden_items": ["mainstream_trends", "formal_wear"],
                "texture_preference": ["vintage_fabrics", "retro_materials", "unique_textures"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["vintage_accessories", "retro_bag", "unique_jewelry"]
            },
            
            # Feminine & Romantic Styles
            "romantic": {
                "color_palette": ["pink", "white", "pastels", "floral_patterns", "soft_tones"],
                "preferred_items": ["floral_dress", "lace_top", "pearl_accessories", "delicate_jewelry"],
                "forbidden_items": ["athletic_wear", "dark_colors", "casual_sneakers"],
                "texture_preference": ["lace", "silk", "soft_fabrics", "delicate_materials"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["pearl_jewelry", "delicate_bag", "feminine_shoes"]
            },
            
            "boho": {
                "color_palette": ["earth_tones", "jewel_tones", "floral_patterns", "natural_colors"],
                "preferred_items": ["flowy_dress", "fringe_jacket", "ankle_boots", "layered_jewelry"],
                "forbidden_items": ["formal_wear", "athletic_wear", "structured_items"],
                "texture_preference": ["flowy_fabrics", "natural_fibers", "textured_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["layered_jewelry", "fringe_bag", "natural_accessories"]
            },
            
            "french_girl": {
                "color_palette": ["navy", "white", "black", "red", "stripes", "neutral_tones"],
                "preferred_items": ["striped_shirt", "high_waisted_jeans", "ballet_flat", "trench_coat"],
                "forbidden_items": ["athletic_wear", "casual_sneakers", "bright_colors"],
                "texture_preference": ["cotton", "linen", "quality_fabrics"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["delicate_jewelry", "classic_bag", "timeless_shoes"]
            },
            
            "pinup": {
                "color_palette": ["red", "black", "white", "polka_dots", "vintage_colors"],
                "preferred_items": ["circle_skirt", "peplum_top", "heels", "vintage_dress"],
                "forbidden_items": ["athletic_wear", "casual_sneakers", "modern_casual"],
                "texture_preference": ["retro_fabrics", "vintage_materials", "classic_textures"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["vintage_jewelry", "retro_bag", "classic_heels"]
            },
            
            # Modern & Minimal Styles
            "minimalist": {
                "color_palette": ["white", "black", "gray", "beige", "neutral_tones"],
                "preferred_items": ["simple_top", "tailored_pants", "white_sneakers", "basic_dress"],
                "forbidden_items": ["busy_patterns", "bright_colors", "excessive_accessories"],
                "texture_preference": ["cotton", "linen", "quality_basics"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["minimal_jewelry", "simple_bag", "clean_shoes"]
            },
            
            "modern": {
                "color_palette": ["black", "white", "gray", "modern_neutrals", "subtle_accents"],
                "preferred_items": ["contemporary_top", "modern_pants", "sleek_shoes", "structured_jacket"],
                "forbidden_items": ["outdated_styles", "athletic_wear", "casual_sneakers"],
                "texture_preference": ["modern_fabrics", "sleek_materials", "contemporary_finishes"],
                "formality_level": FormalityLevel.BUSINESS_CASUAL,
                "accessory_style": ["contemporary_jewelry", "modern_bag", "sleek_accessories"]
            },
            
            "scandinavian": {
                "color_palette": ["white", "black", "gray", "natural_tones", "muted_colors"],
                "preferred_items": ["oversized_sweater", "wide_leg_pants", "comfortable_shoes", "layered_pieces"],
                "forbidden_items": ["bright_colors", "athletic_wear", "formal_business_attire"],
                "texture_preference": ["wool", "cotton", "natural_fibers"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["natural_jewelry", "simple_bag", "comfortable_shoes"]
            },
            
            # Alternative & Edgy Styles
            "gothic": {
                "color_palette": ["black", "dark_colors", "red_accents", "purple", "silver"],
                "preferred_items": ["black_dress", "leather_jacket", "combat_boots", "dark_accessories"],
                "forbidden_items": ["bright_colors", "preppy_styles", "athletic_wear"],
                "texture_preference": ["leather", "velvet", "dark_fabrics"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["dark_jewelry", "gothic_accessories", "combat_boots"]
            },
            
            "punk": {
                "color_palette": ["black", "red", "white", "bold_accents", "contrasting_colors"],
                "preferred_items": ["band_tee", "ripped_jeans", "combat_boots", "studded_accessories"],
                "forbidden_items": ["formal_wear", "preppy_styles", "conservative_items"],
                "texture_preference": ["denim", "leather", "distressed_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["studded_jewelry", "combat_boots", "punk_accessories"]
            },
            
            "cyberpunk": {
                "color_palette": ["black", "neon_colors", "metallic", "electric_blue", "silver"],
                "preferred_items": ["tech_jacket", "futuristic_pants", "cyber_shoes", "LED_accessories"],
                "forbidden_items": ["traditional_formal_wear", "vintage_styles"],
                "texture_preference": ["synthetic_materials", "metallic_fabrics", "tech_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["tech_accessories", "futuristic_bag", "cyber_jewelry"]
            },
            
            "edgy": {
                "color_palette": ["black", "dark_colors", "bold_accents", "metallic", "contrasting_tones"],
                "preferred_items": ["leather_jacket", "dark_jeans", "boots", "statement_accessories"],
                "forbidden_items": ["preppy_styles", "bright_pastels", "athletic_wear"],
                "texture_preference": ["leather", "denim", "bold_materials"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["statement_jewelry", "bold_bag", "edgy_shoes"]
            },
            
            # Seasonal & Lifestyle Styles
            "coastal_chic": {
                "color_palette": ["white", "navy", "beige", "stripes", "ocean_tones"],
                "preferred_items": ["linen_dress", "striped_shirt", "canvas_shoes", "lightweight_cardigan"],
                "forbidden_items": ["heavy_winter_wear", "athletic_wear", "dark_colors"],
                "texture_preference": ["linen", "cotton", "lightweight_fabrics"],
                "formality_level": FormalityLevel.SMART_CASUAL,
                "accessory_style": ["straw_hat", "canvas_bag", "natural_jewelry"]
            },
            
            "athleisure": {
                "color_palette": ["black", "white", "gray", "athletic_colors", "performance_tones"],
                "preferred_items": ["athletic_tee", "yoga_pants", "sneakers", "sports_bra"],
                "forbidden_items": ["formal_wear", "dress_shoes", "business_attire"],
                "texture_preference": ["performance_fabrics", "moisture_wicking", "stretchy_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["athletic_accessories", "sports_bag", "performance_shoes"]
            },
            
            "casual_cool": {
                "color_palette": ["neutral_tones", "black", "white", "denim_blue", "subtle_accents"],
                "preferred_items": ["denim_jacket", "basic_tee", "sneakers", "comfortable_pants"],
                "forbidden_items": ["formal_wear", "athletic_wear", "bright_colors"],
                "texture_preference": ["cotton", "denim", "comfortable_fabrics"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["simple_jewelry", "casual_bag", "comfortable_shoes"]
            },
            
            "loungewear": {
                "color_palette": ["neutral_tones", "soft_colors", "comfortable_tones", "pastels"],
                "preferred_items": ["sweatpants", "hoodie", "slippers", "comfortable_tee"],
                "forbidden_items": ["formal_wear", "business_attire", "dress_shoes"],
                "texture_preference": ["soft_fabrics", "comfortable_materials", "cozy_textures"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["comfortable_accessories", "cozy_bag", "soft_shoes"]
            },
            
            "workout": {
                "color_palette": ["black", "white", "bright_colors", "athletic_tones", "performance_colors"],
                "preferred_items": ["athletic_shirt", "workout_pants", "athletic_shoes", "sports_bra"],
                "forbidden_items": ["formal_wear", "dress_shoes", "business_attire"],
                "texture_preference": ["performance_fabrics", "moisture_wicking", "stretchy_materials"],
                "formality_level": FormalityLevel.CASUAL,
                "accessory_style": ["athletic_accessories", "sports_bag", "performance_shoes"]
            }
        }
    
    def _initialize_mood_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive mood-specific validation rules"""
        return {
            "romantic": {
                "color_preference": ["soft_pastels", "pink", "white", "rose_gold", "delicate_tones"],
                "style_preference": ["feminine", "delicate", "flowing", "lace", "floral"],
                "forbidden_items": ["athletic_wear", "dark_colors", "casual_sneakers", "heavy_boots"],
                "preferred_items": ["floral_dress", "delicate_blouse", "pearl_accessories", "soft_fabrics"],
                "accessory_style": ["delicate_jewelry", "romantic_bag", "feminine_shoes"],
                "formality_tendency": "elevated"
            },
            
            "playful": {
                "color_preference": ["bright_colors", "fun_patterns", "cheerful_tones", "mixed_colors"],
                "style_preference": ["fun", "colorful", "patterned", "casual", "expressive"],
                "forbidden_items": ["formal_wear", "dark_colors", "conservative_styles"],
                "preferred_items": ["colorful_top", "fun_accessories", "patterned_items", "bright_shoes"],
                "accessory_style": ["colorful_jewelry", "fun_bag", "playful_shoes"],
                "formality_tendency": "relaxed"
            },
            
            "serene": {
                "color_preference": ["soft_tones", "neutral_colors", "calm_tones", "muted_pastels"],
                "style_preference": ["calm", "peaceful", "comfortable", "minimal", "soft"],
                "forbidden_items": ["bright_colors", "athletic_wear", "heavy_boots"],
                "preferred_items": ["soft_sweater", "comfortable_pants", "gentle_accessories", "calm_fabrics"],
                "accessory_style": ["simple_jewelry", "peaceful_bag", "comfortable_shoes"],
                "formality_tendency": "relaxed"
            },
            
            "dynamic": {
                "color_preference": ["bold_colors", "energetic_tones", "contrasting_colors", "vibrant_hues"],
                "style_preference": ["energetic", "bold", "active", "confident", "striking"],
                "forbidden_items": ["dull_colors", "passive_styles", "conservative_items"],
                "preferred_items": ["bold_top", "confident_accessories", "energetic_pieces", "striking_shoes"],
                "accessory_style": ["bold_jewelry", "confident_bag", "dynamic_shoes"],
                "formality_tendency": "confident"
            },
            
            "bold": {
                "color_preference": ["strong_colors", "black", "white", "bold_accents", "high_contrast"],
                "style_preference": ["confident", "striking", "strong", "assertive", "powerful"],
                "forbidden_items": ["timid_styles", "pastel_colors", "casual_sneakers"],
                "preferred_items": ["statement_piece", "bold_accessories", "confident_shoes", "strong_silhouette"],
                "accessory_style": ["statement_jewelry", "bold_bag", "powerful_shoes"],
                "formality_tendency": "confident"
            },
            
            "subtle": {
                "color_preference": ["neutral_tones", "muted_colors", "soft_tones", "understated_hues"],
                "style_preference": ["understated", "refined", "gentle", "sophisticated", "quiet"],
                "forbidden_items": ["bright_colors", "loud_patterns", "athletic_wear"],
                "preferred_items": ["refined_top", "quality_basics", "sophisticated_accessories", "understated_shoes"],
                "accessory_style": ["refined_jewelry", "quality_bag", "sophisticated_shoes"],
                "formality_tendency": "elevated"
            }
        }
    
    async def validate_outfit_comprehensive(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Comprehensive outfit validation using integrated thought clarification
        
        This is the main validation method that orchestrates all validation layers
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1
        
        logger.info(f"🔍 Starting comprehensive outfit validation with {len(items)} items")
        logger.info(f"📋 Context: {context.get('occasion', 'unknown')} - {context.get('style', 'unknown')}")
        
        try:
            # Step 1: Pre-validation filtering
            filtered_items, pre_validation_issues = await self._pre_validation_filtering(items, context)
            logger.info(f"✅ Pre-validation: {len(filtered_items)} items passed")
            
            # Step 2: Core inappropriate combinations check
            filtered_items, core_issues = await self._check_inappropriate_combinations(filtered_items, context)
            logger.info(f"✅ Core validation: {len(filtered_items)} items passed")
            
            # Step 3: Occasion-specific validation
            filtered_items, occasion_issues = await self._validate_occasion_specific(filtered_items, context)
            logger.info(f"✅ Occasion validation: {len(filtered_items)} items passed")
            
            # Step 4: Formality consistency validation
            formality_issues = await self._validate_formality_consistency(filtered_items, context)
            logger.info(f"✅ Formality validation completed")
            
            # Step 5: Visual harmony validation
            visual_harmony_result = await self._validate_visual_harmony(filtered_items, context)
            logger.info(f"✅ Visual harmony validation completed - Score: {visual_harmony_result.overall_harmony_score:.1f}/100")
            
            # Step 6: Style-specific validation
            style_issues = await self._validate_style_specific(filtered_items, context)
            logger.info(f"✅ Style validation completed - {len(style_issues)} issues found")
            
            # Step 7: Mood-specific validation
            mood_issues = await self._validate_mood_specific(filtered_items, context)
            logger.info(f"✅ Mood validation completed - {len(mood_issues)} issues found")
            
            # Step 8: Final validation assessment
            all_issues = pre_validation_issues + core_issues + occasion_issues + formality_issues + style_issues + mood_issues
            is_valid = len(all_issues) == 0 and len(filtered_items) >= 3
            
            # Calculate confidence score including visual harmony
            confidence_score = self._calculate_confidence_score(
                filtered_items, context, all_issues, visual_harmony_result.overall_harmony_score
            )
            
            # Determine severity
            severity = self._determine_severity(all_issues)
            
            # Generate suggestions (including visual harmony suggestions)
            suggestions = self._generate_suggestions(all_issues, context)
            if visual_harmony_result.suggestions:
                suggestions.extend(visual_harmony_result.suggestions)
            
            # Update statistics
            if is_valid:
                self.validation_stats["successful_validations"] += 1
            else:
                self.validation_stats["failed_validations"] += 1
            
            self.validation_stats["visual_harmony_validations"] += 1
            
            validation_time = time.time() - start_time
            logger.info(f"✅ Validation completed in {validation_time:.2f}s - Valid: {is_valid}")
            
            return ValidationResult(
                is_valid=is_valid,
                severity=severity,
                issues=all_issues,
                suggestions=suggestions,
                confidence_score=confidence_score,
                filtered_items=filtered_items,
                validation_details={
                    "validation_time": validation_time,
                    "pre_validation_issues": len(pre_validation_issues),
                    "core_issues": len(core_issues),
                    "occasion_issues": len(occasion_issues),
                    "formality_issues": len(formality_issues),
                    "style_issues": len(style_issues),
                    "mood_issues": len(mood_issues),
                    "visual_harmony_score": visual_harmony_result.overall_harmony_score,
                    "visual_harmony_type": visual_harmony_result.harmony_type,
                    "total_items_input": len(items),
                    "total_items_output": len(filtered_items)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Validation failed with exception: {e}")
            self.validation_stats["failed_validations"] += 1
            
            # Return critical failure - do not fall back to bad outfits
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                issues=[f"Validation system error: {str(e)}"],
                suggestions=["Contact support - validation system needs attention"],
                confidence_score=0.0,
                filtered_items=[],
                validation_details={"error": str(e)}
            )
    
    async def _pre_validation_filtering(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Pre-validation filtering to remove obviously inappropriate items"""
        filtered_items = []
        issues = []
        occasion = context.get('occasion', '').lower()
        
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            # Check for obviously inappropriate items for business occasions
            if occasion in ['business', 'interview', 'formal']:
                inappropriate_keywords = [
                    'shorts', 'athletic', 'basketball', 'gym', 'workout', 
                    'sweatpants', 'lounge', 'pajama', 'tank_top'
                ]
                
                if any(keyword in item_name or keyword in item_type for keyword in inappropriate_keywords):
                    issues.append(f"Removed {item.get('name', 'Unknown')} - inappropriate for {occasion}")
                    continue
            
            # Check for obviously inappropriate shoes for business occasions
            if occasion in ['business', 'interview', 'formal'] and item_type in ['shoes', 'footwear']:
                inappropriate_shoe_keywords = [
                    'sneaker', 'athletic', 'canvas', 'flip_flop', 'sandals'
                ]
                
                if any(keyword in item_name for keyword in inappropriate_shoe_keywords):
                    issues.append(f"Removed {item.get('name', 'Unknown')} - inappropriate shoes for {occasion}")
                    continue
            
            filtered_items.append(item)
        
        return filtered_items, issues
    
    async def _check_inappropriate_combinations(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Check for inappropriate combinations using comprehensive rules"""
        filtered_items = items.copy()
        issues = []
        occasion = context.get('occasion', '').lower()
        
        for rule_name, rule in self.inappropriate_combinations.items():
            severity = rule.get('severity', ValidationSeverity.MEDIUM)
            trigger_items = rule.get('trigger_items', [])
            trigger_occasions = rule.get('trigger_occasions', [])
            required_with = rule.get('required_with', [])
            
            # Check if rule applies to current occasion
            if trigger_occasions and occasion not in trigger_occasions:
                continue
            
            # Check if we have items that trigger this rule
            has_trigger_items = False
            has_required_with_items = False
            
            for item in filtered_items:
                item_name = item.get('name', '').lower()
                item_type = item.get('type', '').lower()
                
                # Check for trigger items
                if any(trigger in item_name or trigger in item_type for trigger in trigger_items):
                    has_trigger_items = True
                
                # Check for required_with items
                if required_with and any(required in item_name or required in item_type for required in required_with):
                    has_required_with_items = True
            
            # Apply rule if conditions are met
            if has_trigger_items and (not required_with or has_required_with_items):
                items_to_remove = []
                
                for item in filtered_items:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if any(trigger in item_name or trigger in item_type for trigger in trigger_items):
                        items_to_remove.append(item)
                        issues.append(f"Removed {item.get('name', 'Unknown')} - {rule['reason']}")
                        self.validation_stats["inappropriate_combinations_prevented"] += 1
                
                # Remove inappropriate items
                for item in items_to_remove:
                    if item in filtered_items:
                        filtered_items.remove(item)
        
        return filtered_items, issues
    
    async def _validate_occasion_specific(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate occasion-specific requirements"""
        filtered_items = items.copy()
        issues = []
        occasion = context.get('occasion', '').lower()
        
        # Handle occasion variations (e.g., "Business Formal" -> "business_formal")
        normalized_occasion = occasion.replace(' ', '_').replace('-', '_')
        
        # Try exact match first, then normalized match
        if occasion not in self.occasion_rules and normalized_occasion not in self.occasion_rules:
            return filtered_items, issues
        
        rule = self.occasion_rules.get(occasion) or self.occasion_rules.get(normalized_occasion)
        forbidden_items = rule.get('forbidden_items', [])
        required_items = rule.get('required_items', [])
        preferred_shoes = rule.get('preferred_shoes', [])
        min_formality = rule.get('min_formality', FormalityLevel.CASUAL)
        
        # Remove forbidden items
        items_to_remove = []
        for item in filtered_items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            if any(forbidden in item_name or forbidden in item_type for forbidden in forbidden_items):
                items_to_remove.append(item)
                issues.append(f"Removed {item.get('name', 'Unknown')} - forbidden for {occasion}")
        
        for item in items_to_remove:
            if item in filtered_items:
                filtered_items.remove(item)
        
        # Check for required items (warnings, not removals)
        has_required_items = False
        for item in filtered_items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            if any(required in item_name or required in item_type for required in required_items):
                has_required_items = True
                break
        
        if not has_required_items and required_items:
            issues.append(f"Warning: Missing recommended items for {occasion}: {', '.join(required_items)}")
        
        # Validate shoe appropriateness
        shoe_items = [item for item in filtered_items if item.get('type', '').lower() in ['shoes', 'footwear']]
        if shoe_items and preferred_shoes:
            for shoe in shoe_items:
                shoe_name = shoe.get('name', '').lower()
                if not any(preferred in shoe_name for preferred in preferred_shoes):
                    issues.append(f"Warning: {shoe.get('name', 'Unknown')} may not be ideal for {occasion}")
        
        return filtered_items, issues
    
    async def _validate_formality_consistency(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Validate formality consistency across outfit"""
        issues = []
        
        if len(items) < 2:
            return issues
        
        # Determine formality levels for each item
        item_formalities = []
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            formality = FormalityLevel.CASUAL  # default
            for keyword, level in self.formality_mapping.items():
                if keyword in item_name or keyword in item_type:
                    formality = level
                    break
            
            item_formalities.append(formality)
        
        # Check for formality consistency
        if len(set(item_formalities)) > 3:  # Too many different formality levels
            issues.append("Warning: Outfit has inconsistent formality levels")
        
        # Check for extreme formality mismatches
        formality_values = {level: i for i, level in enumerate(FormalityLevel)}
        formality_scores = [formality_values[level] for level in item_formalities]
        
        if max(formality_scores) - min(formality_scores) > 3:  # Too much formality gap
            issues.append("Warning: Outfit has extreme formality mismatches")
        
        return issues
    
    async def _validate_visual_harmony(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> VisualHarmonyResult:
        """Validate visual harmony using comprehensive fashion theory"""
        if not items:
            return VisualHarmonyResult(
                overall_harmony_score=0.0,
                color_harmony={"error": "No items to analyze"},
                texture_harmony={"error": "No items to analyze"},
                proportion_harmony={"error": "No items to analyze"},
                style_coherence={"error": "No items to analyze"},
                issues=["No items provided for visual harmony analysis"],
                suggestions=["Add items to analyze visual harmony"],
                harmony_type="unknown",
                confidence=0.0
            )
        
        try:
            style = context.get('style', 'casual')
            occasion = context.get('occasion', 'casual')
            
            # Use the visual harmony validator
            harmony_result = await self.visual_harmony_validator.validate_visual_harmony(
                items, style, occasion, context
            )
            
            logger.info(f"🎨 Visual harmony analysis: {harmony_result.overall_harmony_score:.1f}/100 - {harmony_result.harmony_type}")
            
            return harmony_result
            
        except Exception as e:
            logger.error(f"❌ Visual harmony validation failed: {e}")
            return VisualHarmonyResult(
                overall_harmony_score=0.0,
                color_harmony={"error": str(e)},
                texture_harmony={"error": str(e)},
                proportion_harmony={"error": str(e)},
                style_coherence={"error": str(e)},
                issues=[f"Visual harmony analysis failed: {str(e)}"],
                suggestions=["Contact support - visual harmony system needs attention"],
                harmony_type="unknown",
                confidence=0.0
            )
    
    def _calculate_confidence_score(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any], 
        issues: List[str],
        visual_harmony_score: float = 70.0
    ) -> float:
        """Calculate confidence score for the outfit including visual harmony"""
        base_score = 100.0
        
        # Deduct points for issues
        for issue in issues:
            if "Removed" in issue:
                base_score -= 15.0  # Item removal
            elif "Warning" in issue:
                base_score -= 5.0   # Warning
        
        # Bonus for appropriate item count
        if 3 <= len(items) <= 6:
            base_score += 10.0
        elif len(items) < 3:
            base_score -= 20.0
        
        # Bonus for occasion appropriateness
        occasion = context.get('occasion', '').lower()
        if occasion in ['business', 'interview', 'formal']:
            # Check if we have appropriate items for formal occasions
            has_formal_items = any(
                any(keyword in item.get('name', '').lower() or keyword in item.get('type', '').lower() 
                    for keyword in ['dress', 'formal', 'business', 'blazer'])
                for item in items
            )
            if has_formal_items:
                base_score += 10.0
        
        # Include visual harmony in confidence score (weighted 20%)
        harmony_contribution = visual_harmony_score * 0.2
        base_score = (base_score * 0.8) + harmony_contribution
        
        return max(0.0, min(100.0, base_score))
    
    def _determine_severity(self, issues: List[str]) -> ValidationSeverity:
        """Determine overall validation severity"""
        if not issues:
            return ValidationSeverity.LOW
        
        critical_count = sum(1 for issue in issues if "Removed" in issue and any(
            keyword in issue.lower() for keyword in ['business', 'formal', 'interview']
        ))
        
        if critical_count > 0:
            return ValidationSeverity.CRITICAL
        elif any("Removed" in issue for issue in issues):
            return ValidationSeverity.HIGH
        elif any("Warning" in issue for issue in issues):
            return ValidationSeverity.MEDIUM
        else:
            return ValidationSeverity.LOW
    
    def _generate_suggestions(self, issues: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate helpful suggestions based on issues"""
        suggestions = []
        occasion = context.get('occasion', '').lower()
        
        if not issues:
            suggestions.append("Outfit looks great! All validation checks passed.")
            return suggestions
        
        # Generate suggestions based on issues
        for issue in issues:
            if "shorts" in issue.lower() and occasion in ['business', 'interview', 'formal']:
                suggestions.append("Consider dress pants or chinos for professional occasions")
            elif "sneakers" in issue.lower() and occasion in ['business', 'interview', 'formal']:
                suggestions.append("Consider dress shoes or loafers for professional occasions")
            elif "athletic" in issue.lower():
                suggestions.append("Consider more formal alternatives for professional settings")
            elif "formality" in issue.lower():
                suggestions.append("Try to maintain consistent formality levels across all items")
        
        # General suggestions based on occasion
        if occasion in ['business', 'interview', 'formal']:
            suggestions.extend([
                "Ensure all items are professional and well-fitted",
                "Consider adding a blazer or dress shirt for formality",
                "Choose dress shoes over casual footwear"
            ])
        
        return suggestions
    
    async def _validate_style_specific(self, items: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Validate items against style-specific rules"""
        issues = []
        style = context.get('style', '').lower()
        
        if not style or style not in self.style_rules:
            return issues
        
        rule = self.style_rules[style]
        forbidden_items = rule.get('forbidden_items', [])
        preferred_items = rule.get('preferred_items', [])
        color_palette = rule.get('color_palette', [])
        texture_preference = rule.get('texture_preference', [])
        
        logger.info(f"🎨 Style validation for '{style}': Checking {len(items)} items")
        
        # Check for forbidden items
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            item_color = item.get('color', '').lower()
            
            # Check forbidden items
            for forbidden in forbidden_items:
                if forbidden.lower() in item_name or forbidden.lower() in item_type:
                    issues.append(f"Style '{style}' forbids {forbidden} items (found: {item_name})")
                    logger.warning(f"🚫 Style violation: {forbidden} not allowed for {style}")
            
            # Check color palette (if specified)
            if color_palette and item_color:
                color_match = any(color.lower() in item_color for color in color_palette)
                if not color_match and not any(neutral in item_color for neutral in ['black', 'white', 'gray', 'beige', 'navy']):
                    issues.append(f"Style '{style}' prefers colors from {color_palette} (found: {item_color})")
        
        # Check if we have preferred items
        has_preferred = any(
            any(preferred.lower() in item.get('name', '').lower() or preferred.lower() in item.get('type', '').lower() 
                for preferred in preferred_items)
            for item in items
        )
        
        if preferred_items and not has_preferred:
            issues.append(f"Style '{style}' would benefit from items like: {', '.join(preferred_items[:3])}")
        
        logger.info(f"🎨 Style validation completed: {len(issues)} issues found")
        return issues
    
    async def _validate_mood_specific(self, items: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Validate items against mood-specific rules"""
        issues = []
        mood = context.get('mood', '').lower()
        
        if not mood or mood not in self.mood_rules:
            return issues
        
        rule = self.mood_rules[mood]
        forbidden_items = rule.get('forbidden_items', [])
        preferred_items = rule.get('preferred_items', [])
        color_preference = rule.get('color_preference', [])
        style_preference = rule.get('style_preference', [])
        formality_tendency = rule.get('formality_tendency', 'neutral')
        
        logger.info(f"💭 Mood validation for '{mood}': Checking {len(items)} items")
        
        # Check for forbidden items based on mood
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            item_color = item.get('color', '').lower()
            
            # Check forbidden items
            for forbidden in forbidden_items:
                if forbidden.lower() in item_name or forbidden.lower() in item_type:
                    issues.append(f"Mood '{mood}' forbids {forbidden} items (found: {item_name})")
                    logger.warning(f"💭 Mood violation: {forbidden} not suitable for {mood} mood")
        
        # Check color preference (if specified)
        if color_preference:
            color_matches = 0
            for item in items:
                item_color = item.get('color', '').lower()
                if any(color.lower() in item_color for color in color_preference):
                    color_matches += 1
            
            if color_matches == 0:
                issues.append(f"Mood '{mood}' would be enhanced with colors from {color_preference[:3]}")
        
        # Check formality tendency
        if formality_tendency == 'elevated':
            casual_items = ['sneakers', 'jeans', 't-shirt', 'hoodie', 'sweatpants']
            has_casual = any(
                any(casual in item.get('name', '').lower() or casual in item.get('type', '').lower() 
                    for casual in casual_items)
                for item in items
            )
            if has_casual:
                issues.append(f"Mood '{mood}' suggests more elevated/formal pieces")
        
        elif formality_tendency == 'relaxed':
            formal_items = ['suit', 'blazer', 'dress_shoes', 'oxford', 'tie']
            has_formal = any(
                any(formal in item.get('name', '').lower() or formal in item.get('type', '').lower() 
                    for formal in formal_items)
                for item in items
            )
            if has_formal:
                issues.append(f"Mood '{mood}' suggests more relaxed/casual pieces")
        
        logger.info(f"💭 Mood validation completed: {len(issues)} issues found")
        return issues
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.validation_stats.copy()
