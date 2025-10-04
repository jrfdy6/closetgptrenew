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
from src.services.body_type_optimization_service import BodyTypeOptimizationService, BodyType

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
        self.body_type_service = BodyTypeOptimizationService()
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
        max_items: int = 6
    ) -> OutfitComposition:
        """
        Create a cohesive outfit by selecting a base piece and building around it harmoniously.
        """
        logger.info(f"🎨 Creating cohesive outfit for {occasion} {style} occasion")
        
        try:
            # Step 1: Filter wardrobe with graceful fallback for occasion and style
            appropriate_items = self._filter_appropriate_items_with_fallback(wardrobe, occasion, style, weather)
            logger.info(f"📋 {len(appropriate_items)} appropriate items from {len(wardrobe)} total")
            
            if len(appropriate_items) < 2:
                logger.warning("⚠️ Insufficient appropriate items even after fallback")
                return self._create_fallback_outfit(appropriate_items)
                
        except Exception as e:
            logger.error(f"❌ Error in graceful fallback filtering: {e}")
            # Emergency fallback: use first 10 weather-appropriate items
            emergency_items = []
            for item in wardrobe[:20]:  # Limit to first 20 items
                try:
                    if self._is_weather_appropriate(item, weather):
                        emergency_items.append(item)
                        if len(emergency_items) >= 10:
                            break
                except:
                    continue
            
            logger.info(f"🚨 Emergency fallback: using {len(emergency_items)} items")
            return self._create_fallback_outfit(emergency_items)
        
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
        
        # Step 5: Apply body type optimization for flattering silhouettes
        all_pieces = [base_piece] + complementary_pieces
        body_type = self._get_user_body_type(user_profile)
        
        if body_type:
            logger.info(f"🎯 Applying body type optimization for {body_type.value}")
            optimized_pieces = await self.body_type_service.optimize_outfit_for_body_type(
                all_pieces, body_type, user_profile
            )
            logger.info(f"✅ Body type optimization: {len(all_pieces)} → {len(optimized_pieces)} items")
        else:
            optimized_pieces = all_pieces
            logger.info("⚠️ No body type specified, skipping body type optimization")
        
        # Step 6: Ensure style consistency and occasion appropriateness
        final_pieces = self._ensure_style_consistency(
            optimized_pieces, occasion, style
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

    def _filter_appropriate_items_with_fallback(
        self,
        wardrobe: List[ClothingItem],
        occasion: str,
        style: str,
        weather: WeatherData
    ) -> List[ClothingItem]:
        """Filter wardrobe items with graceful fallback for occasion and style."""
        
        # Simplified fallback hierarchy to prevent timeout
        style_fallbacks = {
            "loungewear": ["athleisure", "casual"],
            "athleisure": ["loungewear", "casual"],
            "casual": ["weekend", "athleisure"],
            "business_casual": ["business", "casual"],
            "business": ["business_casual", "formal"],
            "formal": ["business", "business_casual"],
            "weekend": ["casual", "athleisure"],
            "evening": ["formal", "business"],
            "party": ["evening", "formal"],
            "date": ["business_casual", "casual"],
            "travel": ["casual", "athleisure"],
            "workout": ["athleisure", "loungewear"]
        }
        
        occasion_fallbacks = {
            "loungewear": ["athleisure", "casual"],
            "athleisure": ["loungewear", "casual"],
            "casual": ["weekend", "athleisure"],
            "business": ["business_casual", "formal"],
            "business_casual": ["business", "casual"],
            "formal": ["business", "evening"],
            "interview": ["business", "formal", "business_casual"],
            "weekend": ["casual", "athleisure"],
            "evening": ["formal", "business"],
            "party": ["evening", "formal"],
            "date": ["business_casual", "casual"],
            "travel": ["casual", "athleisure"],
            "workout": ["athleisure", "loungewear"]
        }
        
        # Try original occasion and style first
        appropriate_items = self._filter_appropriate_items(wardrobe, occasion, style, weather)
        
        if len(appropriate_items) >= 2:
            logger.info(f"✅ Found {len(appropriate_items)} items for {occasion} {style}")
            return appropriate_items
        
        # Try style fallbacks (limit to 2 attempts)
        style_fallback_list = (style_fallbacks.get(style.lower() if style_fallbacks else None), ["casual"])
        for fallback_style in style_fallback_list[:2]:  # Limit to 2 attempts
            if fallback_style == style.lower():
                continue  # Skip original style
                
            logger.info(f"🔄 Trying style fallback: {fallback_style}")
            fallback_items = self._filter_appropriate_items(wardrobe, occasion, fallback_style, weather)
            
            if len(fallback_items) >= 2:
                logger.info(f"✅ Found {len(fallback_items)} items with style fallback: {fallback_style}")
                return fallback_items
        
        # Try occasion fallbacks (limit to 2 attempts)
        occasion_fallback_list = (occasion_fallbacks.get(occasion.lower() if occasion_fallbacks else None), ["casual"])
        for fallback_occasion in occasion_fallback_list[:2]:  # Limit to 2 attempts
            if fallback_occasion == occasion.lower():
                continue  # Skip original occasion
                
            logger.info(f"🔄 Trying occasion fallback: {fallback_occasion}")
            fallback_items = self._filter_appropriate_items(wardrobe, fallback_occasion, style, weather)
            
            if len(fallback_items) >= 2:
                logger.info(f"✅ Found {len(fallback_items)} items with occasion fallback: {fallback_occasion}")
                return fallback_items
        
        # Try one combined fallback
        if occasion_fallback_list and style_fallback_list:
            fallback_occasion = occasion_fallback_list[0]
            fallback_style = style_fallback_list[0]
            
            if fallback_occasion != occasion.lower() or fallback_style != style.lower():
                logger.info(f"🔄 Trying combined fallback: {fallback_occasion} + {fallback_style}")
                fallback_items = self._filter_appropriate_items(wardrobe, fallback_occasion, fallback_style, weather)
                
                if len(fallback_items) >= 2:
                    logger.info(f"✅ Found {len(fallback_items)} items with combined fallback: {fallback_occasion} + {fallback_style}")
                    return fallback_items
        
        # Final fallback: any weather-appropriate items
        logger.info("🔄 Final fallback: any weather-appropriate items")
        final_items = []
        for item in wardrobe[:50]:  # Limit to first 50 items for performance
            if self._is_weather_appropriate(item, weather):
                final_items.append(item)
        
        logger.info(f"✅ Final fallback found {len(final_items)} weather-appropriate items")
        return final_items

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
            "interview": ["dress", "dress_pants", "suit", "skirt", "chinos"],
            "casual": ["jeans", "pants", "shorts", "dress"],
            "weekend": ["jeans", "shorts", "pants", "dress"]
        }
        
        # Get items by priority for this occasion
        occasion_priority = (base_priorities.get(occasion.lower() if base_priorities else None), ["pants", "jeans", "dress"])
        
        logger.info(f"🎯 Selecting base piece for {occasion} occasion")
        logger.info(f"   Priority types: {occasion_priority}")
        logger.info(f"   Available items: {[f'{item.name} ({item.type})' for item in items[:5]]}")
        
        for priority_type in occasion_priority:
            for item in items:
                if self._item_matches_type(item, priority_type):
                    logger.info(f"✅ Selected base piece: {item.name} ({item.type}) - matches {priority_type}")
                    return item
        
        # Fallback: look for any bottom item
        for item in items:
            if self._item_matches_category(item, "bottom"):
                logger.info(f"✅ Fallback base piece: {item.name} ({item.type}) - bottom category")
                return item
        
        # Final fallback: return first item
        logger.warning(f"⚠️ No suitable base piece found, using first item: {items[0].name} ({items[0].type})")
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
                available_items, item_type, color_palette, used_items, user_profile
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
        used_items: set,
        user_profile: Optional[UserProfile] = None
    ) -> Optional[ClothingItem]:
        """Find the best item of a specific type that fits the color palette."""
        candidates = []
        
        for item in items:
            if item.id in used_items:
                continue
                
            # Check if item matches the type we're looking for
            if not self._item_matches_category(item, item_type):
                continue
            
            # Calculate compatibility score with style profile integration
            score = self._calculate_item_compatibility(item, color_palette, item_type, user_profile)
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
        target_type: str,
        user_profile: Optional[UserProfile] = None
    ) -> float:
        """Calculate how well an item fits the outfit composition with style profile integration."""
        score = 0.0
        
        # Color compatibility (20% of score)
        item_color = item.color.lower()
        if item_color in color_palette:
            score += 20
        elif self._colors_are_harmonious(item_color, color_palette):
            score += 15
        
        # Enhanced color scoring with user preferences
        if user_profile and hasattr(user_profile, 'colorPalette'):
            color_palette_data = user_profile.colorPalette
            if color_palette_data:
                # Check against user's preferred colors
                preferred_colors = []
                if color_palette_data.get('primary'):
                    preferred_colors.extend([c.lower() for c in color_palette_data['primary']])
                if color_palette_data.get('secondary'):
                    preferred_colors.extend([c.lower() for c in color_palette_data['secondary']])
                if color_palette_data.get('accent'):
                    preferred_colors.extend([c.lower() for c in color_palette_data['accent']])
                
                if item_color in preferred_colors:
                    score += 10  # Bonus for user's preferred colors
                
                # Penalty for avoided colors
                if color_palette_data.get('avoid'):
                    avoided_colors = [c.lower() for c in color_palette_data['avoid']]
                    if item_color in avoided_colors:
                        score -= 20
        
        # Type compatibility (20% of score)
        if self._item_matches_category(item, target_type):
            score += 20
        
        # Enhanced style compatibility with user profile (20% of score)
        style_score = self._calculate_style_profile_compatibility(item, user_profile)
        score += style_score
        
        # Material preferences (10% of score)
        material_score = self._calculate_material_compatibility(item, user_profile)
        score += material_score
        
        # Brand preferences (5% of score)
        brand_score = self._calculate_brand_compatibility(item, user_profile)
        score += brand_score
        
        # Physical measurements compatibility (15% of score)
        measurements_score = self._calculate_measurements_compatibility(item, user_profile)
        score += measurements_score
        
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
        target_formality = self.(style_formality_levels.get(target_style.lower() if style_formality_levels else None), 2.5)
        
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

    def _get_user_body_type(self, user_profile: UserProfile) -> Optional[BodyType]:
        """Extract body type from user profile."""
        if not user_profile:
            return None
        
        # Check if user profile has body type information
        if hasattr(user_profile, 'body_type') and user_profile.body_type:
            try:
                return BodyType(user_profile.body_type.lower())
            except ValueError:
                logger.warning(f"Invalid body type in profile: {user_profile.body_type}")
        
        # Check if body type is in user preferences or metadata
        if hasattr(user_profile, 'preferences') and user_profile.preferences:
            if isinstance(user_profile.preferences, dict):
                body_type = user_profile.(preferences.get('body_type') if preferences else None)
                if body_type:
                    try:
                        return BodyType(body_type.lower())
                    except ValueError:
                        pass
        
        # Check if body type is in style preferences
        if hasattr(user_profile, 'style_preferences') and user_profile.style_preferences:
            if isinstance(user_profile.style_preferences, list):
                for preference in user_profile.style_preferences:
                    if isinstance(preference, dict) and 'body_type' in preference:
                        try:
                            return BodyType(preference['body_type'].lower())
                        except ValueError:
                            pass
        
        logger.info("No body type information found in user profile")
        return None

    def _calculate_style_profile_compatibility(self, item: ClothingItem, user_profile: Optional[UserProfile]) -> float:
        """Calculate style compatibility based on user's style profile."""
        if not user_profile:
            return 0.0
        
        score = 0.0
        
        # Check style personality scores
        if hasattr(user_profile, 'stylePersonality') and user_profile.stylePersonality:
            style_personality = user_profile.stylePersonality
            
            # Map item characteristics to style personality traits
            item_name = item.name.lower()
            item_type = item.type.lower()
            
            # Classic items (structured, traditional)
            if any(classic in item_name or classic in item_type for classic in 
                   ['blazer', 'oxford', 'pencil', 'sheath', 'classic', 'traditional']):
                score += (style_personality.get('classic', 0.5) if style_personality else 0.5) * 10
            
            # Modern items (contemporary, minimalist)
            elif any(modern in item_name or modern in item_type for modern in 
                     ['minimalist', 'contemporary', 'sleek', 'modern', 'geometric']):
                score += (style_personality.get('modern', 0.5) if style_personality else 0.5) * 10
            
            # Creative items (unique, artistic, bold)
            elif any(creative in item_name or creative in item_type for creative in 
                     ['artistic', 'unique', 'bold', 'statement', 'creative', 'patterned']):
                score += (style_personality.get('creative', 0.5) if style_personality else 0.5) * 10
            
            # Minimal items (simple, clean)
            elif any(minimal in item_name or minimal in item_type for minimal in 
                     ['simple', 'clean', 'basic', 'essential', 'minimal']):
                score += (style_personality.get('minimal', 0.5) if style_personality else 0.5) * 10
            
            # Bold items (eye-catching, dramatic)
            elif any(bold in item_name or bold in item_type for bold in 
                     ['dramatic', 'eye-catching', 'bold', 'vibrant', 'statement']):
                score += (style_personality.get('bold', 0.5) if style_personality else 0.5) * 10
        
        # Check style preferences
        if hasattr(user_profile, 'stylePreferences') and user_profile.stylePreferences:
            item_styles = item.style if hasattr(item, 'style') and item.style else []
            if isinstance(item_styles, list):
                for user_style in user_profile.stylePreferences:
                    if user_style.lower() in [s.lower() for s in item_styles]:
                        score += 15  # Strong match for user's preferred styles
        
        return min(score, 25)  # Cap at 25 points

    def _calculate_material_compatibility(self, item: ClothingItem, user_profile: Optional[UserProfile]) -> float:
        """Calculate material compatibility based on user preferences."""
        if not user_profile or not hasattr(user_profile, 'materialPreferences'):
            return 0.0
        
        material_prefs = user_profile.materialPreferences
        if not material_prefs:
            return 0.0
        
        score = 0.0
        
        # Check item material against preferences
        item_name = item.name.lower()
        item_type = item.type.lower()
        
        # Check preferred materials
        preferred_materials = (material_prefs.get('preferred', []) if material_prefs else [])
        for material in preferred_materials:
            if material.lower() in item_name or material.lower() in item_type:
                score += 10
        
        # Check avoided materials
        avoided_materials = (material_prefs.get('avoid', []) if material_prefs else [])
        for material in avoided_materials:
            if material.lower() in item_name or material.lower() in item_type:
                score -= 15
        
        return min(score, 15)  # Cap at 15 points

    def _calculate_brand_compatibility(self, item: ClothingItem, user_profile: Optional[UserProfile]) -> float:
        """Calculate brand compatibility based on user preferences."""
        if not user_profile or not hasattr(user_profile, 'preferredBrands'):
            return 0.0
        
        preferred_brands = user_profile.preferredBrands
        if not preferred_brands:
            return 0.0
        
        score = 0.0
        
        # Check if item brand matches user preferences
        if hasattr(item, 'brand') and item.brand:
            item_brand = item.brand.lower()
            for preferred_brand in preferred_brands:
                if preferred_brand.lower() in item_brand:
                    score += 10
        
        return min(score, 10)  # Cap at 10 points

    def _calculate_measurements_compatibility(self, item: ClothingItem, user_profile: Optional[UserProfile]) -> float:
        """Calculate compatibility based on physical measurements and sizing."""
        if not user_profile or not hasattr(user_profile, 'measurements'):
            return 0.0
        
        measurements = user_profile.measurements
        if not measurements:
            return 0.0
        
        score = 0.0
        
        # Height-based compatibility
        height = (measurements.get('height', 0) if measurements else 0)
        height_feet_inches = (measurements.get('heightFeetInches', '') if measurements else '')
        
        if height > 0 or height_feet_inches:
            # Convert height to inches for calculations
            height_inches = self._convert_height_to_inches(height, height_feet_inches)
            
            # Height-appropriate item selection
            item_name = item.name.lower()
            item_type = item.type.lower()
            
            # Petite considerations (under 5'4")
            if height_inches < 64:
                if any(petite in item_name for petite in ['petite', 'cropped', 'ankle']):
                    score += 8
                elif any(tall in item_name for tall in ['long', 'maxi', 'floor-length']):
                    score -= 5
            
            # Tall considerations (over 5'8")
            elif height_inches > 68:
                if any(tall in item_name for tall in ['tall', 'long', 'maxi', 'floor-length']):
                    score += 8
                elif any(petite in item_name for petite in ['petite', 'cropped', 'ankle']):
                    score -= 5
        
        # Weight-based compatibility
        weight = (measurements.get('weight', 0) if measurements else 0)
        plus_size = (measurements.get('plusSize', False) if measurements else False)
        
        if weight > 0 or plus_size:
            item_name = item.name.lower()
            
            # Plus-size considerations
            if plus_size or weight > 180:  # Approximate threshold
                if any(plus in item_name for plus in ['plus', 'curvy', 'extended']):
                    score += 8
                elif any(regular in item_name for regular in ['regular', 'standard']):
                    score += 5
        
        # Clothing size matching
        item_size = self._extract_item_size(item)
        if item_size:
            # Top size matching
            if item_type in ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket', 'blazer']:
                user_top_size = (measurements.get('topSize', '') if measurements else '')
                if user_top_size and self._sizes_match(item_size, user_top_size):
                    score += 10
            
            # Bottom size matching
            elif item_type in ['pants', 'jeans', 'shorts', 'skirt']:
                user_bottom_size = (measurements.get('bottomSize', '') if measurements else '')
                if user_bottom_size and self._sizes_match(item_size, user_bottom_size):
                    score += 10
            
            # Dress size matching
            elif item_type == 'dress':
                user_dress_size = (measurements.get('dressSize', '') if measurements else '')
                if user_dress_size and self._sizes_match(item_size, user_dress_size):
                    score += 10
            
            # Shoe size matching
            elif item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']:
                user_shoe_size = (measurements.get('shoeSize', '') if measurements else '')
                if user_shoe_size and self._shoe_sizes_match(item_size, user_shoe_size):
                    score += 10
        
        # Skin tone compatibility for colors
        skin_tone = (measurements.get('skinTone') if measurements else None)
        if skin_tone:
            color_compatibility = self._calculate_skin_tone_color_compatibility(item, skin_tone)
            score += color_compatibility
        
        return min(score, 10)  # Cap at 10 points

    def _convert_height_to_inches(self, height: int, height_feet_inches: str) -> int:
        """Convert height to inches for calculations."""
        if height > 0:
            return height
        
        if height_feet_inches:
            # Parse formats like "5'4"", "5'4", "5-4"
            import re
            match = re.search(r'(\d+)[\'-](\d+)', height_feet_inches)
            if match:
                feet = int(match.group(1))
                inches = int(match.group(2))
                return feet * 12 + inches
        
        return 0

    def _extract_item_size(self, item: ClothingItem) -> Optional[str]:
        """Extract size information from item name or metadata."""
        item_name = item.name.lower()
        
        # Common size patterns
        import re
        
        # Numeric sizes (4, 6, 8, 10, 12, 14, 16, etc.)
        numeric_match = re.search(r'\b(\d{1,2})\b', item_name)
        if numeric_match:
            return numeric_match.group(1)
        
        # Letter sizes (XS, S, M, L, XL, XXL)
        letter_match = re.search(r'\b([X]*[SL])\b', item_name.upper())
        if letter_match:
            return letter_match.group(1)
        
        # Shoe sizes (7, 7.5, 8, 8.5, etc.)
        shoe_match = re.search(r'\b(\d{1,2}(?:\.\d)?)\b', item_name)
        if shoe_match and item.type.lower() in ['shoes', 'sneakers', 'boots', 'sandals']:
            return shoe_match.group(1)
        
        return None

    def _sizes_match(self, item_size: str, user_size: str) -> bool:
        """Check if item size matches user size."""
        if not item_size or not user_size:
            return False
        
        # Exact match
        if item_size.lower() == user_size.lower():
            return True
        
        # Numeric size tolerance (±1 size)
        if item_size.isdigit() and user_size.isdigit():
            item_num = int(item_size)
            user_num = int(user_size)
            return abs(item_num - user_num) <= 1
        
        return False

    def _shoe_sizes_match(self, item_size: str, user_size: str) -> bool:
        """Check if shoe sizes match with tolerance."""
        if not item_size or not user_size:
            return False
        
        try:
            item_float = float(item_size)
            user_float = float(user_size)
            return abs(item_float - user_float) <= 0.5  # Half size tolerance
        except ValueError:
            return item_size.lower() == user_size.lower()

    def _calculate_skin_tone_color_compatibility(self, item: ClothingItem, skin_tone: str) -> float:
        """Calculate color compatibility with skin tone."""
        item_color = item.color.lower()
        skin_tone_lower = skin_tone.lower()
        
        # Warm skin tone colors
        if 'warm' in skin_tone_lower or 'olive' in skin_tone_lower:
            warm_colors = ['gold', 'yellow', 'orange', 'coral', 'peach', 'warm brown', 'olive']
            if any(warm in item_color for warm in warm_colors):
                return 5
        
        # Cool skin tone colors
        elif 'cool' in skin_tone_lower or 'pink' in skin_tone_lower:
            cool_colors = ['blue', 'purple', 'silver', 'pink', 'mint', 'cool gray']
            if any(cool in item_color for cool in cool_colors):
                return 5
        
        # Neutral skin tone - most colors work
        elif 'neutral' in skin_tone_lower:
            return 3  # Small bonus for any color
        
        return 0

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
