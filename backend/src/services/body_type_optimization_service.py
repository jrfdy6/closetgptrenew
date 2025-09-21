#!/usr/bin/env python3
"""
Body Type Optimization Service
Optimizes outfit selections for flattering silhouettes based on body type
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.custom_types.wardrobe import ClothingItem
from src.custom_types.profile import UserProfile

logger = logging.getLogger(__name__)

class BodyType(Enum):
    APPLE = "apple"           # Wider midsection, narrower shoulders/hips
    PEAR = "pear"            # Wider hips, narrower shoulders
    RECTANGLE = "rectangle"   # Straight figure, minimal curves
    HOURGLASS = "hourglass"   # Balanced shoulders/hips, defined waist
    INVERTED_TRIANGLE = "inverted_triangle"  # Broad shoulders, narrower hips
    DIAMOND = "diamond"       # Wider midsection, narrow shoulders/hips

@dataclass
class BodyTypeProfile:
    body_type: BodyType
    height: str  # "petite", "average", "tall"
    bust_size: str  # "small", "medium", "large"
    waist_emphasis: bool  # Whether to emphasize waist
    shoulder_emphasis: bool  # Whether to emphasize shoulders
    hip_emphasis: bool  # Whether to emphasize hips

class BodyTypeOptimizationService:
    def __init__(self):
        # Body type flattering rules
        self.flattering_rules = {
            BodyType.APPLE: {
                "silhouette": "structured, tailored",
                "emphasis": "shoulders_and_legs",
                "avoid": ["tight_midsection", "high_waisted", "belted_waist"],
                "prefer": ["v_neck", "structured_blazers", "straight_pants", "a_line_dresses"],
                "layering": "open_front_layers",
                "proportions": "balance_top_and_bottom"
            },
            BodyType.PEAR: {
                "silhouette": "balanced_top_bottom",
                "emphasis": "shoulders_and_waist",
                "avoid": ["tight_bottoms", "light_colors_bottom", "detailed_hips"],
                "prefer": ["structured_tops", "dark_bottoms", "belts", "shoulder_padding"],
                "layering": "fitted_tops_with_layers",
                "proportions": "emphasize_top_balance_bottom"
            },
            BodyType.RECTANGLE: {
                "silhouette": "create_curves",
                "emphasis": "waist_and_hips",
                "avoid": ["boxy_silhouettes", "straight_lines", "no_definition"],
                "prefer": ["belted_waists", "peplum_tops", "a_line_skirts", "layered_tops"],
                "layering": "create_definition",
                "proportions": "add_curves_and_definition"
            },
            BodyType.HOURGLASS: {
                "silhouette": "fitted_and_curved",
                "emphasis": "natural_waist",
                "avoid": ["boxy_fits", "oversized", "no_waist_definition"],
                "prefer": ["fitted_tops", "belted_waists", "pencil_skirts", "wrap_dresses"],
                "layering": "follow_natural_curves",
                "proportions": "accentuate_existing_curves"
            },
            BodyType.INVERTED_TRIANGLE: {
                "silhouette": "balance_shoulders",
                "emphasis": "hips_and_waist",
                "avoid": ["broad_shoulders", "padded_shoulders", "tight_tops"],
                "prefer": ["wide_leg_pants", "a_line_skirts", "v_neck", "hip_details"],
                "layering": "balance_shoulders",
                "proportions": "create_hip_width"
            },
            BodyType.DIAMOND: {
                "silhouette": "smooth_midsection",
                "emphasis": "shoulders_and_legs",
                "avoid": ["tight_midsection", "high_waisted", "belted_waist"],
                "prefer": ["v_neck", "structured_blazers", "straight_pants", "flowing_tops"],
                "layering": "open_front_layers",
                "proportions": "balance_top_and_bottom"
            }
        }
        
        # Item type flattering properties
        self.item_flattering_properties = {
            # Tops
            "v_neck": {"flatters": [BodyType.APPLE, BodyType.INVERTED_TRIANGLE], "creates": "elongation"},
            "crew_neck": {"flatters": [BodyType.PEAR, BodyType.RECTANGLE], "creates": "balance"},
            "wrap_top": {"flatters": [BodyType.HOURGLASS, BodyType.PEAR], "creates": "waist_emphasis"},
            "peplum": {"flatters": [BodyType.RECTANGLE, BodyType.PEAR], "creates": "hip_definition"},
            "structured_blazer": {"flatters": [BodyType.APPLE, BodyType.RECTANGLE], "creates": "structure"},
            
            # Bottoms
            "straight_pants": {"flatters": [BodyType.APPLE, BodyType.DIAMOND], "creates": "elongation"},
            "wide_leg_pants": {"flatters": [BodyType.INVERTED_TRIANGLE, BodyType.RECTANGLE], "creates": "balance"},
            "high_waisted": {"flatters": [BodyType.PEAR, BodyType.HOURGLASS], "creates": "waist_emphasis"},
            "a_line_skirt": {"flatters": [BodyType.PEAR, BodyType.RECTANGLE], "creates": "hip_definition"},
            "pencil_skirt": {"flatters": [BodyType.HOURGLASS, BodyType.RECTANGLE], "creates": "curve_accentuation"},
            
            # Dresses
            "wrap_dress": {"flatters": [BodyType.HOURGLASS, BodyType.PEAR], "creates": "waist_emphasis"},
            "a_line_dress": {"flatters": [BodyType.PEAR, BodyType.RECTANGLE], "creates": "hip_definition"},
            "shift_dress": {"flatters": [BodyType.RECTANGLE, BodyType.APPLE], "creates": "smooth_silhouette"},
            "belted_dress": {"flatters": [BodyType.HOURGLASS, BodyType.RECTANGLE], "creates": "waist_definition"},
            
            # Layers
            "cardigan": {"flatters": [BodyType.PEAR, BodyType.RECTANGLE], "creates": "soft_layering"},
            "blazer": {"flatters": [BodyType.APPLE, BodyType.RECTANGLE], "creates": "structure"},
            "vest": {"flatters": [BodyType.HOURGLASS, BodyType.RECTANGLE], "creates": "waist_emphasis"},
            "sweater": {"flatters": [BodyType.PEAR, BodyType.RECTANGLE], "creates": "soft_balance"}
        }

    async def optimize_outfit_for_body_type(
        self,
        items: List[ClothingItem],
        body_type: BodyType,
        user_profile: Optional[UserProfile] = None
    ) -> List[ClothingItem]:
        """
        Optimize outfit items for flattering body type silhouette.
        """
        if not items or not body_type:
            return items
        
        logger.info(f"🎯 Optimizing outfit for {body_type.value} body type")
        
        # Get body type rules
        rules = self.flattering_rules.get(body_type, {})
        if not rules:
            logger.warning(f"No rules found for body type: {body_type}")
            return items
        
        # Score each item based on body type flattering properties
        scored_items = []
        for item in items:
            score = self._calculate_body_type_score(item, body_type, rules)
            scored_items.append((item, score))
        
        # Sort by body type flattering score
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Select most flattering items while maintaining outfit functionality
        optimized_items = self._select_flattering_items(scored_items, body_type, rules)
        
        logger.info(f"✅ Optimized outfit: {len(items)} → {len(optimized_items)} items")
        return optimized_items

    def _calculate_body_type_score(
        self,
        item: ClothingItem,
        body_type: BodyType,
        rules: Dict[str, Any]
    ) -> float:
        """Calculate how flattering an item is for a specific body type."""
        score = 50.0  # Base score
        
        item_type = item.type.lower()
        item_name = item.name.lower()
        
        # Check against flattering rules
        preferred_items = rules.get("prefer", [])
        avoided_items = rules.get("avoid", [])
        
        # Increase score for preferred items
        for preferred in preferred_items:
            if self._item_matches_preference(item, preferred):
                score += 20
        
        # Decrease score for avoided items
        for avoided in avoided_items:
            if self._item_matches_preference(item, avoided):
                score -= 30
        
        # Check specific item type flattering properties
        for item_key, properties in self.item_flattering_properties.items():
            if self._item_matches_type(item, item_key):
                if body_type in properties["flatters"]:
                    score += 25
                else:
                    score -= 10
        
        # Consider item fit and structure
        score += self._assess_fit_flattery(item, body_type)
        
        return max(0, min(100, score))  # Clamp between 0-100

    def _item_matches_preference(self, item: ClothingItem, preference: str) -> bool:
        """Check if an item matches a body type preference."""
        item_type = item.type.lower()
        item_name = item.name.lower()
        
        preference_mappings = {
            "v_neck": ["v_neck", "v neck", "v-neck"],
            "structured_blazers": ["blazer", "jacket"],
            "straight_pants": ["straight", "pants", "trousers"],
            "a_line_dresses": ["a_line", "a-line", "a line"],
            "high_waisted": ["high_waist", "high waist", "high-waist"],
            "belted_waist": ["belt", "belted"],
            "wide_leg_pants": ["wide_leg", "wide leg", "wide-leg", "palazzo"],
            "pencil_skirt": ["pencil", "straight_skirt"],
            "wrap_dress": ["wrap", "wrap_dress"],
            "peplum": ["peplum"],
            "fitted_tops": ["fitted", "slim", "tailored"],
            "open_front_layers": ["cardigan", "open_front", "unbuttoned"]
        }
        
        if preference in preference_mappings:
            return any(keyword in item_type or keyword in item_name 
                      for keyword in preference_mappings[preference])
        
        return False

    def _item_matches_type(self, item: ClothingItem, item_key: str) -> bool:
        """Check if an item matches a specific type key."""
        item_type = item.type.lower()
        item_name = item.name.lower()
        
        type_mappings = {
            "v_neck": ["v_neck", "v neck", "v-neck"],
            "crew_neck": ["crew_neck", "crew neck", "crew-neck"],
            "wrap_top": ["wrap", "wrap_top"],
            "peplum": ["peplum"],
            "structured_blazer": ["blazer", "jacket"],
            "straight_pants": ["straight", "pants", "trousers"],
            "wide_leg_pants": ["wide_leg", "wide leg", "wide-leg", "palazzo"],
            "high_waisted": ["high_waist", "high waist", "high-waist"],
            "a_line_skirt": ["a_line", "a-line", "a line"],
            "pencil_skirt": ["pencil", "straight_skirt"],
            "wrap_dress": ["wrap", "wrap_dress"],
            "a_line_dress": ["a_line", "a-line", "a line"],
            "shift_dress": ["shift", "shift_dress"],
            "belted_dress": ["belted", "belted_dress"],
            "cardigan": ["cardigan"],
            "blazer": ["blazer"],
            "vest": ["vest"],
            "sweater": ["sweater"]
        }
        
        if item_key in type_mappings:
            return any(keyword in item_type or keyword in item_name 
                      for keyword in type_mappings[item_key])
        
        return False

    def _assess_fit_flattery(self, item: ClothingItem, body_type: BodyType) -> float:
        """Assess how flattering the fit of an item is for a body type."""
        score = 0.0
        
        # Check item description for fit keywords
        item_name = item.name.lower()
        item_type = item.type.lower()
        
        # Fit keywords and their body type preferences
        fit_preferences = {
            BodyType.APPLE: {
                "flattering": ["fitted", "tailored", "structured", "straight", "a_line"],
                "unflattering": ["tight", "clingy", "high_waist", "belted"]
            },
            BodyType.PEAR: {
                "flattering": ["fitted_top", "structured", "a_line", "wide_leg"],
                "unflattering": ["tight_bottom", "clingy_bottom", "light_bottom"]
            },
            BodyType.RECTANGLE: {
                "flattering": ["belted", "peplum", "fitted", "a_line", "layered"],
                "unflattering": ["boxy", "straight", "oversized", "no_definition"]
            },
            BodyType.HOURGLASS: {
                "flattering": ["fitted", "belted", "wrap", "tailored", "curved"],
                "unflattering": ["boxy", "oversized", "no_waist", "straight"]
            },
            BodyType.INVERTED_TRIANGLE: {
                "flattering": ["wide_leg", "a_line", "fitted_bottom", "v_neck"],
                "unflattering": ["broad_shoulder", "padded", "tight_top", "crew_neck"]
            },
            BodyType.DIAMOND: {
                "flattering": ["fitted", "tailored", "structured", "straight", "flowing"],
                "unflattering": ["tight", "clingy", "high_waist", "belted"]
            }
        }
        
        preferences = fit_preferences.get(body_type, {})
        flattering_keywords = preferences.get("flattering", [])
        unflattering_keywords = preferences.get("unflattering", [])
        
        # Check for flattering keywords
        for keyword in flattering_keywords:
            if keyword in item_name or keyword in item_type:
                score += 5
        
        # Check for unflattering keywords
        for keyword in unflattering_keywords:
            if keyword in item_name or keyword in item_type:
                score -= 10
        
        return score

    def _select_flattering_items(
        self,
        scored_items: List[Tuple[ClothingItem, float]],
        body_type: BodyType,
        rules: Dict[str, Any]
    ) -> List[ClothingItem]:
        """Select the most flattering items while maintaining outfit functionality."""
        if not scored_items:
            return []
        
        # Separate items by category
        categories = {
            "top": [],
            "bottom": [],
            "dress": [],
            "layer": [],
            "shoes": [],
            "accessory": []
        }
        
        for item, score in scored_items:
            category = self._categorize_item(item)
            if category in categories:
                categories[category].append((item, score))
        
        # Select best items from each category
        selected_items = []
        
        # Always need a base piece (bottom or dress)
        if categories["dress"]:
            # If we have dresses, select the best one
            best_dress = max(categories["dress"], key=lambda x: x[1])
            selected_items.append(best_dress[0])
        else:
            # Select best bottom
            if categories["bottom"]:
                best_bottom = max(categories["bottom"], key=lambda x: x[1])
                selected_items.append(best_bottom[0])
            
            # Select best top
            if categories["top"]:
                best_top = max(categories["top"], key=lambda x: x[1])
                selected_items.append(best_top[0])
        
        # Add layering piece if beneficial for body type
        if self._should_add_layer(body_type, rules):
            if categories["layer"]:
                best_layer = max(categories["layer"], key=lambda x: x[1])
                selected_items.append(best_layer[0])
        
        # Add shoes
        if categories["shoes"]:
            best_shoes = max(categories["shoes"], key=lambda x: x[1])
            selected_items.append(best_shoes[0])
        
        # Add accessories if beneficial
        if self._should_add_accessories(body_type, rules):
            if categories["accessory"]:
                best_accessory = max(categories["accessory"], key=lambda x: x[1])
                selected_items.append(best_accessory[0])
        
        return selected_items

    def _categorize_item(self, item: ClothingItem) -> str:
        """Categorize an item by type."""
        item_type = item.type.lower()
        
        if "dress" in item_type:
            return "dress"
        elif any(bottom in item_type for bottom in ["pants", "jeans", "shorts", "skirt"]):
            return "bottom"
        elif any(top in item_type for top in ["shirt", "t-shirt", "blouse", "top"]):
            return "top"
        elif any(layer in item_type for layer in ["jacket", "blazer", "sweater", "cardigan"]):
            return "layer"
        elif any(shoe in item_type for shoe in ["shoes", "sneakers", "boots", "sandals"]):
            return "shoes"
        else:
            return "accessory"

    def _should_add_layer(self, body_type: BodyType, rules: Dict[str, Any]) -> bool:
        """Determine if a layering piece would be flattering for the body type."""
        layering_strategy = rules.get("layering", "")
        
        if body_type in [BodyType.PEAR, BodyType.RECTANGLE]:
            return True  # Layers help balance proportions
        elif body_type in [BodyType.APPLE, BodyType.DIAMOND]:
            return layering_strategy == "open_front_layers"  # Only open layers
        elif body_type == BodyType.HOURGLASS:
            return True  # Layers can enhance curves
        elif body_type == BodyType.INVERTED_TRIANGLE:
            return layering_strategy == "balance_shoulders"  # Only if it balances shoulders
        
        return False

    def _should_add_accessories(self, body_type: BodyType, rules: Dict[str, Any]) -> bool:
        """Determine if accessories would be flattering for the body type."""
        emphasis = rules.get("emphasis", "")
        
        if "waist" in emphasis:
            return True  # Belts can help emphasize waist
        elif body_type in [BodyType.PEAR, BodyType.RECTANGLE]:
            return True  # Accessories can help create definition
        elif body_type == BodyType.HOURGLASS:
            return True  # Accessories can enhance natural curves
        
        return False

    def get_body_type_recommendations(self, body_type: BodyType) -> Dict[str, Any]:
        """Get specific recommendations for a body type."""
        rules = self.flattering_rules.get(body_type, {})
        
        return {
            "body_type": body_type.value,
            "silhouette_goal": rules.get("silhouette", ""),
            "emphasis_areas": rules.get("emphasis", ""),
            "preferred_items": rules.get("prefer", []),
            "items_to_avoid": rules.get("avoid", []),
            "layering_strategy": rules.get("layering", ""),
            "proportion_goal": rules.get("proportions", "")
        }
