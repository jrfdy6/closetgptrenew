#!/usr/bin/env python3
"""
Cohesive Outfit Composition Service
Focuses on creating harmonious, well-coordinated outfits rather than just matching criteria
"""

import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.custom_types.wardrobe import ClothingItem
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

logger = logging.getLogger(__name__)

class OutfitStyle(Enum):
    CASUAL = "casual"
    BUSINESS_CASUAL = "business_casual"
    FORMAL = "formal"
    SMART_CASUAL = "smart_casual"
    WEEKEND = "weekend"

class ColorHarmony(Enum):
    MONOCHROMATIC = "monochromatic"  # Same color family
    ANALOGOUS = "analogous"          # Adjacent colors
    COMPLEMENTARY = "complementary"  # Opposite colors
    TRIADIC = "triadic"             # Three evenly spaced colors
    NEUTRAL = "neutral"             # Black, white, gray, beige

@dataclass
class OutfitComposition:
    base_piece: ClothingItem
    complementary_pieces: List[ClothingItem]
    total_items: int
    color_harmony: ColorHarmony
    style_consistency: float
    occasion_appropriateness: float
    weather_appropriateness: float

class CohesiveOutfitCompositionService:
    def __init__(self):
        self.color_harmony_map = {
            # Neutral colors that work with everything
            "neutral": ["black", "white", "gray", "beige", "navy", "charcoal", "ivory", "cream"],
            
            # Warm color families
            "warm": ["red", "orange", "yellow", "burgundy", "maroon", "coral", "peach", "gold"],
            
            # Cool color families  
            "cool": ["blue", "green", "purple", "teal", "mint", "sage", "lavender", "indigo"],
            
            # Earth tones
            "earth": ["brown", "tan", "olive", "khaki", "rust", "terracotta", "moss", "camel"]
        }
        
        # Style consistency rules
        self.style_formality_levels = {
            "formal": 5,
            "business": 4,
            "business_casual": 3,
            "smart_casual": 2.5,
            "casual": 2,
            "weekend": 1.5,
            "athletic": 1
        }
        
        # Item formality mapping
        self.item_formality = {
            # Formal items
            "suit": 5, "blazer": 4.5, "dress_shirt": 4.5, "dress_pants": 4.5, "oxford": 4.5, "loafers": 4,
            
            # Business items
            "dress_shirt": 4, "chinos": 3.5, "button_up": 3.5, "dress_shoes": 4,
            
            # Casual items
            "t-shirt": 1.5, "jeans": 2, "sneakers": 1.5, "shorts": 1.5, "hoodie": 1.5,
            
            # Weekend items
            "polo": 2.5, "khakis": 3, "boat_shoes": 2.5, "henley": 2
        }

    async def create_cohesive_outfit(
        self,
        wardrobe: List[ClothingItem],
        occasion: str,
        style: str,
        mood: str,
        weather: WeatherData,
        user_profile: UserProfile,
        max_items: int = 4
    ) -> OutfitComposition:
        """
        Create a cohesive outfit by selecting a base piece and building around it harmoniously.
        """
        logger.info(f"🎨 Creating cohesive outfit for {occasion} {style} occasion")
        
        # Step 1: Filter wardrobe for occasion and weather appropriateness
        appropriate_items = self._filter_appropriate_items(wardrobe, occasion, style, weather)
        logger.info(f"📋 {len(appropriate_items)} appropriate items from {len(wardrobe)} total")
        
        if len(appropriate_items) < 2:
            logger.warning("⚠️ Insufficient appropriate items for cohesive outfit")
            return self._create_fallback_outfit(appropriate_items)
        
        # Step 2: Select base piece (usually bottom or dress)
        base_piece = self._select_base_piece(appropriate_items, occasion, style)
        logger.info(f"🎯 Selected base piece: {base_piece.name} ({base_piece.type})")
        
        # Step 3: Build color harmony around base piece
        color_palette = self._determine_color_palette(base_piece, appropriate_items)
        logger.info(f"🎨 Color palette: {color_palette}")
        
        # Step 4: Select complementary pieces that work with base
        complementary_pieces = self._select_complementary_pieces(
            appropriate_items, base_piece, color_palette, occasion, style, max_items - 1
        )
        
        # Step 5: Ensure style consistency and occasion appropriateness
        final_pieces = self._ensure_style_consistency(
            [base_piece] + complementary_pieces, occasion, style
        )
        
        # Step 6: Calculate composition metrics
        composition = OutfitComposition(
            base_piece=base_piece,
            complementary_pieces=final_pieces[1:],  # Exclude base piece
            total_items=len(final_pieces),
            color_harmony=self._assess_color_harmony(final_pieces),
            style_consistency=self._calculate_style_consistency(final_pieces, style),
            occasion_appropriateness=self._calculate_occasion_appropriateness(final_pieces, occasion),
            weather_appropriateness=self._calculate_weather_appropriateness(final_pieces, weather)
        )
        
        logger.info(f"✅ Created cohesive outfit: {composition.total_items} items, "
                   f"{composition.color_harmony.value} harmony, "
                   f"{composition.style_consistency:.1f} style consistency")
        
        return composition

    def _filter_appropriate_items(
        self,
        wardrobe: List[ClothingItem],
        occasion: str,
        style: str,
        weather: WeatherData
    ) -> List[ClothingItem]:
        """Filter wardrobe items for occasion, style, and weather appropriateness."""
        appropriate = []
        
        for item in wardrobe:
            # Check occasion appropriateness
            if not self._is_occasion_appropriate(item, occasion):
                continue
                
            # Check weather appropriateness
            if not self._is_weather_appropriate(item, weather):
                continue
                
            # Check style appropriateness
            if not self._is_style_appropriate(item, style):
                continue
                
            appropriate.append(item)
        
        return appropriate

    def _select_base_piece(
        self,
        items: List[ClothingItem],
        occasion: str,
        style: str
    ) -> ClothingItem:
        """Select the foundation piece of the outfit (usually bottom or dress)."""
        
        # Priority order for base pieces based on occasion
        base_priorities = {
            "formal": ["dress", "suit", "dress_pants", "skirt"],
            "business": ["dress", "dress_pants", "skirt", "chinos"],
            "business_casual": ["dress", "dress_pants", "chinos", "jeans"],
            "casual": ["jeans", "pants", "shorts", "dress"],
            "weekend": ["jeans", "shorts", "pants", "dress"]
        }
        
        # Get items by priority for this occasion
        occasion_priority = base_priorities.get(occasion.lower(), ["pants", "jeans", "dress"])
        
        for priority_type in occasion_priority:
            for item in items:
                if self._item_matches_type(item, priority_type):
                    return item
        
        # Fallback: return first appropriate item
        return items[0]

    def _determine_color_palette(
        self,
        base_piece: ClothingItem,
        available_items: List[ClothingItem]
    ) -> List[str]:
        """Determine a harmonious color palette based on the base piece."""
        base_color = base_piece.color.lower()
        
        # Start with base color
        palette = [base_color]
        
        # Add neutral colors that work with everything
        neutrals = ["black", "white", "navy", "gray", "beige"]
        
        # If base color is neutral, add one accent color
        if base_color in neutrals:
            # Find a complementary accent color from available items
            for item in available_items:
                if item.color.lower() not in neutrals and item.id != base_piece.id:
                    palette.append(item.color.lower())
                    break
        else:
            # If base color is not neutral, add neutral colors
            for neutral in neutrals:
                if len(palette) < 3:  # Limit to 3 colors max
                    palette.append(neutral)
        
        return palette[:3]  # Maximum 3 colors for harmony

    def _select_complementary_pieces(
        self,
        available_items: List[ClothingItem],
        base_piece: ClothingItem,
        color_palette: List[str],
        occasion: str,
        style: str,
        max_complementary: int
    ) -> List[ClothingItem]:
        """Select pieces that complement the base piece harmoniously."""
        complementary = []
        used_items = {base_piece.id}
        
        # Determine what types of items we need
        needed_types = self._determine_needed_types(base_piece, occasion, style)
        
        for item_type, priority in needed_types.items():
            if len(complementary) >= max_complementary:
                break
                
            # Find best item of this type
            best_item = self._find_best_item_for_type(
                available_items, item_type, color_palette, used_items
            )
            
            if best_item:
                complementary.append(best_item)
                used_items.add(best_item.id)
        
        return complementary

    def _determine_needed_types(
        self,
        base_piece: ClothingItem,
        occasion: str,
        style: str
    ) -> Dict[str, int]:
        """Determine what types of items are needed to complete the outfit."""
        base_type = base_piece.type.lower()
        needed = {}
        
        # Always need a top
        if base_type in ["pants", "jeans", "shorts", "skirt"]:
            needed["top"] = 10  # High priority
            
            # Add layering piece for cooler weather or formal occasions
            if occasion.lower() in ["formal", "business"] or style.lower() in ["formal", "business_casual"]:
                needed["layer"] = 8  # High priority
            else:
                needed["layer"] = 5  # Medium priority
        
        # Always need shoes
        needed["shoes"] = 10  # High priority
        
        # Add accessories for formal occasions
        if occasion.lower() in ["formal", "business"]:
            needed["accessory"] = 6  # Medium priority
        
        return needed

    def _find_best_item_for_type(
        self,
        items: List[ClothingItem],
        item_type: str,
        color_palette: List[str],
        used_items: set
    ) -> Optional[ClothingItem]:
        """Find the best item of a specific type that fits the color palette."""
        candidates = []
        
        for item in items:
            if item.id in used_items:
                continue
                
            # Check if item matches the type we're looking for
            if not self._item_matches_category(item, item_type):
                continue
            
            # Calculate compatibility score
            score = self._calculate_item_compatibility(item, color_palette, item_type)
            candidates.append((item, score))
        
        if not candidates:
            return None
        
        # Return the highest scoring item
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _calculate_item_compatibility(
        self,
        item: ClothingItem,
        color_palette: List[str],
        target_type: str
    ) -> float:
        """Calculate how well an item fits the outfit composition."""
        score = 0.0
        
        # Color compatibility (40% of score)
        item_color = item.color.lower()
        if item_color in color_palette:
            score += 40
        elif self._colors_are_harmonious(item_color, color_palette):
            score += 30
        
        # Type compatibility (30% of score)
        if self._item_matches_category(item, target_type):
            score += 30
        
        # Style compatibility (20% of score)
        if hasattr(item, 'style') and item.style:
            # Add style matching logic here
            score += 20
        
        # Occasion compatibility (10% of score)
        if hasattr(item, 'occasion') and item.occasion:
            # Add occasion matching logic here
            score += 10
        
        return score

    def _ensure_style_consistency(
        self,
        pieces: List[ClothingItem],
        occasion: str,
        style: str
    ) -> List[ClothingItem]:
        """Ensure all pieces work together stylistically."""
        if len(pieces) <= 2:
            return pieces
        
        # Calculate formality levels for all pieces
        formality_scores = []
        for piece in pieces:
            score = self._get_item_formality_score(piece)
            formality_scores.append(score)
        
        # If formality scores vary too much, remove the most inconsistent piece
        if len(formality_scores) > 2:
            avg_formality = sum(formality_scores) / len(formality_scores)
            max_deviation = max(abs(score - avg_formality) for score in formality_scores)
            
            if max_deviation > 1.5:  # Too much variation
                # Find and remove the most inconsistent piece
                worst_index = max(range(len(formality_scores)), 
                                key=lambda i: abs(formality_scores[i] - avg_formality))
                pieces.pop(worst_index)
        
        return pieces

    def _assess_color_harmony(self, pieces: List[ClothingItem]) -> ColorHarmony:
        """Assess the color harmony of the outfit."""
        colors = [piece.color.lower() for piece in pieces]
        unique_colors = list(set(colors))
        
        if len(unique_colors) == 1:
            return ColorHarmony.MONOCHROMATIC
        elif len(unique_colors) <= 2:
            return ColorHarmony.NEUTRAL
        elif len(unique_colors) == 3:
            return ColorHarmony.TRIADIC
        else:
            return ColorHarmony.ANALOGOUS

    def _calculate_style_consistency(self, pieces: List[ClothingItem], target_style: str) -> float:
        """Calculate how consistent the style is across all pieces."""
        if not pieces:
            return 0.0
        
        formality_scores = [self._get_item_formality_score(piece) for piece in pieces]
        target_formality = self.style_formality_levels.get(target_style.lower(), 2.5)
        
        # Calculate deviation from target formality
        deviations = [abs(score - target_formality) for score in formality_scores]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Convert to 0-1 scale (lower deviation = higher consistency)
        consistency = max(0, 1 - (avg_deviation / 2))  # Assuming max deviation of 2
        return consistency

    def _calculate_occasion_appropriateness(self, pieces: List[ClothingItem], occasion: str) -> float:
        """Calculate how appropriate the outfit is for the occasion."""
        appropriate_count = 0
        for piece in pieces:
            if self._is_occasion_appropriate(piece, occasion):
                appropriate_count += 1
        
        return appropriate_count / len(pieces) if pieces else 0.0

    def _calculate_weather_appropriateness(self, pieces: List[ClothingItem], weather: WeatherData) -> float:
        """Calculate how appropriate the outfit is for the weather."""
        appropriate_count = 0
        for piece in pieces:
            if self._is_weather_appropriate(piece, weather):
                appropriate_count += 1
        
        return appropriate_count / len(pieces) if pieces else 0.0

    # Helper methods
    def _is_occasion_appropriate(self, item: ClothingItem, occasion: str) -> bool:
        """Check if an item is appropriate for the occasion."""
        if not hasattr(item, 'occasion') or not item.occasion:
            return True  # Assume appropriate if no occasion specified
        
        item_occasions = [occ.lower() for occ in item.occasion] if isinstance(item.occasion, list) else [item.occasion.lower()]
        return occasion.lower() in item_occasions or 'all' in item_occasions

    def _is_weather_appropriate(self, item: ClothingItem, weather: WeatherData) -> bool:
        """Check if an item is appropriate for the weather."""
        temp = getattr(weather, 'temperature', 70)
        
        # Simple weather appropriateness based on item type
        item_type = item.type.lower()
        
        if temp < 60:  # Cold weather
            return item_type not in ['shorts', 'sandals', 'tank_top']
        elif temp > 80:  # Hot weather
            return item_type not in ['jacket', 'sweater', 'hoodie', 'boots']
        else:  # Moderate weather
            return True

    def _is_style_appropriate(self, item: ClothingItem, style: str) -> bool:
        """Check if an item is appropriate for the style."""
        if not hasattr(item, 'style') or not item.style:
            return True  # Assume appropriate if no style specified
        
        item_styles = [s.lower() for s in item.style] if isinstance(item.style, list) else [item.style.lower()]
        return style.lower() in item_styles or 'all' in item_styles

    def _item_matches_type(self, item: ClothingItem, target_type: str) -> bool:
        """Check if an item matches a specific type."""
        item_type = item.type.lower()
        return target_type.lower() in item_type or item_type in target_type.lower()

    def _item_matches_category(self, item: ClothingItem, category: str) -> bool:
        """Check if an item matches a clothing category."""
        item_type = item.type.lower()
        
        category_mappings = {
            "top": ["shirt", "t-shirt", "blouse", "sweater", "tank", "polo", "henley"],
            "bottom": ["pants", "jeans", "shorts", "skirt"],
            "shoes": ["shoes", "sneakers", "boots", "sandals", "heels"],
            "layer": ["jacket", "blazer", "sweater", "hoodie", "cardigan"],
            "accessory": ["belt", "watch", "scarf", "hat", "bag"]
        }
        
        if category in category_mappings:
            return any(cat_type in item_type for cat_type in category_mappings[category])
        
        return False

    def _colors_are_harmonious(self, color1: str, color_palette: List[str]) -> bool:
        """Check if a color harmonizes with a palette."""
        # Simple harmony check - could be enhanced with color theory
        neutrals = ["black", "white", "gray", "beige", "navy"]
        return color1 in neutrals or any(c in neutrals for c in color_palette)

    def _get_item_formality_score(self, item: ClothingItem) -> float:
        """Get the formality score for an item."""
        item_type = item.type.lower()
        
        # Check exact matches first
        if item_type in self.item_formality:
            return self.item_formality[item_type]
        
        # Check partial matches
        for item_key, score in self.item_formality.items():
            if item_key in item_type or item_type in item_key:
                return score
        
        # Default to medium formality
        return 2.5

    def _create_fallback_outfit(self, items: List[ClothingItem]) -> OutfitComposition:
        """Create a minimal fallback outfit when there are insufficient items."""
        if not items:
            return OutfitComposition(
                base_piece=None,
                complementary_pieces=[],
                total_items=0,
                color_harmony=ColorHarmony.NEUTRAL,
                style_consistency=0.0,
                occasion_appropriateness=0.0,
                weather_appropriateness=0.0
            )
        
        return OutfitComposition(
            base_piece=items[0],
            complementary_pieces=items[1:2],  # Take up to 1 more item
            total_items=min(len(items), 2),
            color_harmony=ColorHarmony.NEUTRAL,
            style_consistency=0.5,
            occasion_appropriateness=0.5,
            weather_appropriateness=0.5
        )
