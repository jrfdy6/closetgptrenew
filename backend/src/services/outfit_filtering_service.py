"""
Outfit Filtering Service
Handles all filtering logic for outfit generation including weather, occasion, style, and mood filtering.
"""

from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
from ..custom_types.weather import WeatherData
from ..custom_types.outfit_rules import get_occasion_rule, get_mood_rule


class OutfitFilteringService:
    """Handles all filtering operations for outfit generation."""
    
    def __init__(self):
        pass
    
    def apply_strict_filtering(self, wardrobe, context):
        # print(f"🔍 DEBUG: _apply_strict_filtering - Starting with {len(wardrobe)} items")
        filtered = wardrobe[:]
        
        # Weather filtering
        before = len(filtered)
        filtered = self._filter_by_weather_strict(filtered, context["weather"])
        after = len(filtered)
        # print(f"🔍 DEBUG: _apply_strict_filtering - After weather filtering: {after} items (removed {before - after})")
        
        # Occasion filtering
        before = len(filtered)
        filtered = self._filter_by_occasion_strict(filtered, context["occasion"])
        after = len(filtered)
        # print(f"🔍 DEBUG: _apply_strict_filtering - After occasion filtering: {after} items (removed {before - after})")
        
        # Style filtering
        before = len(filtered)
        filtered = self._filter_by_style_strict(filtered, context.get("style") if context else None, context.get("style_matrix", {}) if context else {})
        after = len(filtered)
        # print(f"🔍 DEBUG: _apply_strict_filtering - After style filtering: {after} items (removed {before - after})")
        
        # Preferences filtering
        before = len(filtered)
        filtered = self._filter_by_personal_preferences(filtered, context.get("user_profile") if context else None)
        after = len(filtered)
        # print(f"🔍 DEBUG: _apply_strict_filtering - After preferences filtering: {after} items (removed {before - after})")
        
        # Mood filtering
        before = len(filtered)
        filtered = self._filter_by_mood_strict(filtered, context.get("mood_rule") if context else None, context.get("base_item") if context else None)
        after = len(filtered)
        # print(f"🔍 DEBUG: _apply_strict_filtering - After mood filtering: {after} items (removed {before - after})")
        
        return filtered
    
    def apply_light_filtering(self, wardrobe, context):
        """Light filtering - basic weather and occasion filtering."""
        # print(f"🔍 DEBUG: apply_light_filtering - Starting with {len(wardrobe)} items")
        filtered = wardrobe[:]
        
        # Basic weather filtering
        before = len(filtered)
        filtered = self._filter_by_weather_strict(filtered, context["weather"])
        after = len(filtered)
        # print(f"🔍 DEBUG: apply_light_filtering - After weather filtering: {after} items (removed {before - after})")
        
        # Basic occasion filtering to prevent obviously inappropriate items
        before = len(filtered)
        filtered = self._filter_by_occasion_light(filtered, context.get("occasion", "") if context else "")
        after = len(filtered)
        # print(f"🔍 DEBUG: apply_light_filtering - After occasion filtering: {after} items (removed {before - after})")
        
        return filtered
    
    def _filter_by_occasion_light(self, items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Light occasion filtering to remove obviously inappropriate items."""
        if not items or not occasion:
            return items
            
        occasion_lower = occasion.lower()
        filtered_items = []
        
        for item in items:
            item_name = item.name.lower()
            item_type = item.type.lower()
            
            # Skip obviously inappropriate items for formal occasions
            if any(formal_term in occasion_lower for formal_term in ['formal', 'business', 'interview']):
                # Block casual/athletic items for formal occasions
                if any(inappropriate in item_name or inappropriate in item_type for inappropriate in [
                    'sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs',  # Casual shoes
                    'jersey', 'basketball', 'sport', 'tank', 'tank top',  # Athletic wear
                    'biker', 'leather jacket', 'hoodie', 'sweatpants', 'joggers'  # Casual outerwear
                ]):
                    continue
            
            # Skip obviously inappropriate items for party occasions
            elif any(party_term in occasion_lower for party_term in ['party', 'night out', 'club']):
                # Block formal/work items for party occasions
                if any(inappropriate in item_name or inappropriate in item_type for inappropriate in [
                    'suit', 'dress pants', 'oxford', 'loafers',  # Too formal
                    'athletic', 'gym', 'jersey', 'basketball', 'sport',  # Too athletic
                    'sweatpants', 'joggers', 'lounge', 'pajama',  # Too casual
                    'work', 'business', 'professional'  # Too work-like
                ]):
                    continue
            
            # Skip obviously inappropriate items for date occasions
            elif any(date_term in occasion_lower for date_term in ['date', 'romantic']):
                # Block athletic/casual items for date occasions
                if any(inappropriate in item_name or inappropriate in item_type for inappropriate in [
                    'athletic', 'gym', 'jersey', 'basketball', 'sport',  # Too athletic
                    'lounge', 'pajama', 'sleep',  # Too casual
                    'work', 'business', 'professional',  # Too work-like
                    'swim', 'beach', 'bikini'  # Too beachy
                ]):
                    continue
            
            # Skip obviously inappropriate items for athletic occasions
            elif any(athletic_term in occasion_lower for athletic_term in ['athletic', 'gym', 'workout', 'sport']):
                # Block formal items for athletic occasions
                if any(inappropriate in item_name or inappropriate in item_type for inappropriate in [
                    'blazer', 'suit', 'dress pants', 'dress shirt', 'oxford', 'loafers', 'heels',  # Too formal
                    'formal', 'business', 'professional', 'dress', 'suit jacket', 'sport coat'  # Too formal
                ]):
                    continue
            
            # Skip obviously inappropriate items for loungewear occasions
            elif 'loungewear' in occasion_lower:
                # Block formal/structured items for loungewear
                if any(inappropriate in item_name or inappropriate in item_type for inappropriate in [
                    'blazer', 'suit', 'dress pants', 'oxford', 'heels', 'loafers',  # Too formal
                    'athletic', 'gym', 'jersey', 'basketball', 'sport',  # Too athletic
                    'work', 'business', 'professional',  # Too work-like
                    'jeans', 'denim'  # Too structured
                ]):
                    continue
            
            filtered_items.append(item)
        
        return filtered_items
    
    def _filter_by_weather_strict(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Filter items based on weather conditions with temperature conversion."""
        if not items:
            return items
            
        # Ensure temperature is a float
        temperature = weather.temperature
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        filtered_items = []
        
        for item in items:
            if self._is_weather_appropriate(item, weather, temperature):
                filtered_items.append(item)
        
        return filtered_items
    
    def _is_weather_appropriate(self, item: ClothingItem, weather: WeatherData, temperature: float) -> bool:
        """Enhanced weather appropriateness check with comprehensive temperature and condition logic."""
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        # Get item attributes
        item_type = item.type.lower()
        item_name = item.name.lower()
        material = ""
        if item.metadata and item.metadata.visualAttributes and item.metadata.visualAttributes.material:
            material = item.metadata.visualAttributes.material.lower() if item.metadata.visualAttributes.material else ""
        
        # Enhanced temperature-based filtering
        if temperature >= 85:  # Very hot weather (85°F+)
            # Exclude heavy/warm items
            exclude_materials = ['wool', 'fleece', 'thick', 'heavy', 'winter', 'cashmere', 'fur']
            exclude_types = ['coat', 'jacket', 'sweater', 'hoodie', 'thermal', 'long pants', 'jeans']
            exclude_keywords = ['warm', 'insulated', 'padded', 'quilted']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
            if any(keyword in item_name for keyword in exclude_keywords):
                return False
                
        elif temperature >= 75:  # Warm weather (75-84°F)
            # Exclude winter items but allow light layers
            exclude_materials = ['wool', 'fleece', 'heavy', 'winter', 'thermal']
            exclude_types = ['coat', 'heavy jacket', 'winter sweater', 'thermal']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
                
        elif temperature <= 40:  # Very cold weather (40°F and below)
            # Exclude summer items and prefer warm items
            exclude_materials = ['linen', 'light cotton', 'mesh', 'silk']
            exclude_types = ['tank top', 'sleeveless', 'shorts', 'sandals', 'flip flops']
            exclude_keywords = ['summer', 'beach', 'swimwear']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
            if any(keyword in item_name for keyword in exclude_keywords):
                return False
                
        elif temperature <= 65:  # Cool weather (41-65°F) - Extended range to catch 67°F scenario
            # Exclude obvious summer items that are inappropriate for cool weather
            exclude_materials = ['linen', 'light cotton', 'mesh']
            exclude_types = ['tank top', 'sleeveless', 'shorts', 'sandals']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
        
        # Weather condition-based filtering
        condition = weather.condition.lower()
        
        # Rainy weather considerations
        if 'rain' in condition or weather.precipitation > 50:
            # Prefer water-resistant materials and avoid delicate fabrics
            delicate_materials = ['silk', 'suede', 'velvet', 'linen']
            if material and any(mat in material for mat in delicate_materials):
                return False
                
        # Windy weather considerations
        if 'wind' in condition or weather.wind_speed > 15:
            # Avoid items that might be problematic in wind
            avoid_types = ['skirt', 'dress', 'loose', 'flowing']
            if any(avoid_type in item_type or avoid_type in item_name for avoid_type in avoid_types):
                # Still allow but with lower priority (handled in scoring)
                pass
        
        return True
    
    def _filter_by_occasion_strict(self, items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Filter items based on occasion requirements."""
        if not items:
            return items
            
        occasion_lower = occasion.lower()
        
        # Apply specific occasion filters
        if 'athletic' in occasion_lower or 'gym' in occasion_lower:
            return self._filter_for_athletic(items)
        elif 'formal' in occasion_lower or 'business' in occasion_lower:
            return self._filter_for_formal(items)
        elif 'party' in occasion_lower:
            return self._filter_for_party(items)
        elif 'casual' in occasion_lower:
            return self._filter_for_casual(items)
        # Add more occasion-specific filters as needed
        
        return items
    
    def _filter_for_athletic(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Filter items for athletic occasions."""
        athletic_items = []
        for item in items:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Include athletic items
            if any(keyword in item_type or keyword in item_name 
                   for keyword in ['shirt', 'pants', 'shorts', 'sneakers', 'athletic', 'sports']):
                athletic_items.append(item)
            # Include casual items that work for athletic activities
            elif any(keyword in item_type or keyword in item_name 
                    for keyword in ['t-shirt', 'jeans', 'shoes']):
                athletic_items.append(item)
        
        return athletic_items
    
    def _filter_for_formal(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Filter items for formal occasions."""
        formal_items = []
        for item in items:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Include formal items
            if any(keyword in item_type or keyword in item_name 
                   for keyword in ['shirt', 'pants', 'dress', 'blazer', 'suit', 'formal']):
                formal_items.append(item)
            # Include business casual items
            elif any(keyword in item_type or keyword in item_name 
                    for keyword in ['polo', 'khakis', 'dress shoes']):
                formal_items.append(item)
        
        return formal_items
    
    def _filter_for_party(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Filter items for party occasions."""
        party_items = []
        for item in items:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Include party-appropriate items
            if any(keyword in item_type or keyword in item_name 
                   for keyword in ['dress', 'shirt', 'pants', 'shoes', 'accessory']):
                party_items.append(item)
        
        return party_items
    
    def _filter_for_casual(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Filter items for casual occasions."""
        casual_items = []
        for item in items:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Include casual items
            if any(keyword in item_type or keyword in item_name 
                   for keyword in ['t-shirt', 'jeans', 'shorts', 'sneakers', 'casual']):
                casual_items.append(item)
        
        return casual_items
    
    def _filter_by_style_strict(self, items: List[ClothingItem], style: str, style_matrix: Dict[str, Any]) -> List[ClothingItem]:
        """Filter items based on style requirements."""
        if not items or not style:
            return items
            
        style_lower = style.lower()
        filtered_items = []
        
        for item in items:
            if self._item_matches_style(item, style_lower):
                filtered_items.append(item)
        
        return filtered_items
    
    def _item_matches_style(self, item: ClothingItem, style: str) -> bool:
        """
        Check if item matches the specified style.
        METADATA-FIRST FILTERING: Uses structured data as primary filter, names only as tertiary helper.
        """
        style_lower = style.lower()
        
        # ═══════════════════════════════════════════════════════════════════════
        # PRIMARY FILTER: Use structured metadata (style[], type, brand)
        # ═══════════════════════════════════════════════════════════════════════
        
        # 1. Check style[] field from AI analysis (PRIMARY)
        item_styles = [s.lower() for s in getattr(item, 'style', [])]
        if item_styles and style_lower in item_styles:
            return True  # Item explicitly tagged for this style
        
        # 2. Check item type (SECONDARY - more reliable than names)
        item_type = item.type.lower()
        if self._is_type_suitable_for_style(item_type, style_lower):
            return True
        
        # 3. Check brand (SECONDARY - reliable for certain styles)
        item_brand = getattr(item, 'brand', '').lower()
        if item_brand and self._is_brand_suitable_for_style(item_brand, style_lower):
            return True
        
        # ═══════════════════════════════════════════════════════════════════════
        # TERTIARY FILTER: Use item names only as fallback helper (LAST RESORT)
        # ═══════════════════════════════════════════════════════════════════════
        
        item_name = item.name.lower()
        if self._is_name_obviously_unsuitable_for_style(item_name, style_lower):
            return False
        
        # ═══════════════════════════════════════════════════════════════════════
        # DEFAULT: Allow items (let scoring system handle preferences)
        # ═══════════════════════════════════════════════════════════════════════
        
        return True  # Conservative approach - allow items, let scoring decide
    
    def _is_type_suitable_for_style(self, item_type: str, style_lower: str) -> bool:
        """Check if item type is suitable for style (SECONDARY filter)"""
        style_type_mappings = {
            'casual': ['shirt', 'pants', 'shoes', 'jeans', 'sneakers', 'hoodie', 'sweatshirt'],
            'formal': ['shirt', 'pants', 'shoes', 'dress', 'blazer', 'suit', 'heels', 'loafers'],
            'athletic': ['shirt', 'pants', 'shorts', 'shoes', 'sneakers', 'tank', 'hoodie'],
            'streetwear': ['hoodie', 'sneakers', 'jeans', 'shirt', 'pants'],
            'vintage': ['shirt', 'pants', 'dress', 'shoes', 'jacket'],
            'modern': ['shirt', 'pants', 'dress', 'shoes', 'jacket']
        }
        
        suitable_types = style_type_mappings.get(style_lower, [])
        return item_type in suitable_types
    
    def _is_brand_suitable_for_style(self, item_brand: str, style_lower: str) -> bool:
        """Check if brand is suitable for style (SECONDARY filter)"""
        style_brand_mappings = {
            'athletic': ['nike', 'adidas', 'puma', 'under armour', 'reebok', 'new balance'],
            'formal': ['brooks brothers', 'ralph lauren', 'hugo boss', 'calvin klein', 'tommy hilfiger'],
            'streetwear': ['supreme', 'off-white', 'yeezy', 'nike', 'adidas'],
            'vintage': ['levis', 'champion', 'nike', 'adidas'],
            'modern': ['everlane', 'allbirds', 'reformation', 'outdoor voices']
        }
        
        suitable_brands = style_brand_mappings.get(style_lower, [])
        return any(brand in item_brand for brand in suitable_brands)
    
    def _is_name_obviously_unsuitable_for_style(self, item_name: str, style_lower: str) -> bool:
        """
        Check if item name is obviously unsuitable for style (TERTIARY filter only).
        This is the ONLY place where names are used for filtering, and only for obvious mismatches.
        """
        unsuitable_terms = {
            'athletic': ['dress shoes', 'suit', 'blazer', 'heels', 'oxford', 'loafers'],
            'formal': ['tank top', 'flip flops', 'sweatpants', 'basketball shoes'],
            'casual': ['tuxedo', 'evening gown', 'wedding dress'],
            'streetwear': ['business suit', 'formal dress', 'dress shoes']
        }
        
        terms_to_check = unsuitable_terms.get(style_lower, [])
        return any(term in item_name for term in terms_to_check)
    
    def _filter_by_personal_preferences(self, items: List[ClothingItem], user_profile: UserProfile) -> List[ClothingItem]:
        """Filter items based on user preferences."""
        if not items:
            return items
            
        filtered_items = []
        
        for item in items:
            if self._check_gender_compatibility(item, user_profile.gender):
                if self._check_color_palette_compatibility(item, user_profile.color_palette):
                    if self._check_material_preferences(item, user_profile.material_preferences):
                        filtered_items.append(item)
        
        return filtered_items
    
    def _check_gender_compatibility(self, item: ClothingItem, gender: Optional[str]) -> bool:
        """Check if item is compatible with user's gender preference."""
        if not gender:
            return True
        
        # Add gender compatibility logic here
        return True
    
    def _check_color_palette_compatibility(self, item: ClothingItem, color_palette: Optional[Dict[str, List[str]]]) -> bool:
        """Check if item colors are compatible with user's color palette."""
        if not color_palette:
            return True
        
        # Add color compatibility logic here
        return True
    
    def _check_material_preferences(self, item: ClothingItem, material_preferences: Optional[Dict[str, List[str]]]) -> bool:
        """Check if item materials match user's preferences."""
        if not material_preferences:
            return True
        
        # Add material preference logic here
        return True
    
    def _filter_by_mood_strict(self, items: List[ClothingItem], mood_rule, base_item: Optional[ClothingItem] = None) -> List[ClothingItem]:
        """Filter items based on mood requirements."""
        if not items or not mood_rule:
            return items
        
        # Add mood filtering logic here
        return items
    
    def _filter_recently_used_items(self, items: List[ClothingItem], outfit_history: List[Dict], days: int = 7) -> List[ClothingItem]:
        """Filter out recently used items for wardrobe diversity."""
        # For now, return all items
        return items
    
    def deduplicate_shoes(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Deduplicate shoes - ensure only one shoe in the final outfit."""
        shoes = []
        other_items = []
        
        for item in items:
            if 'shoe' in item.type.lower() or 'sneaker' in item.type.lower():
                shoes.append(item)
            else:
                other_items.append(item)
        
        # Keep only the first shoe
        if shoes:
            other_items.append(shoes[0])
        
        return other_items
    
    def deduplicate_by_category(self, items: List[ClothingItem], context: Dict[str, Any] = None) -> List[ClothingItem]:
        """Deduplicate items by category to avoid too many similar items."""
        categories = {}
        
        for item in items:
            category = self._get_item_category(item)
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Keep only the first item from each category
        deduplicated_items = []
        for category, category_items in categories.items():
            deduplicated_items.append(category_items[0])
        
        return deduplicated_items
    
    def _get_item_category(self, item: ClothingItem) -> str:
        """Get the category of an item."""
        item_type = item.type.lower()
        
        if any(keyword in item_type for keyword in ['shirt', 'top', 'blouse']):
            return 'top'
        elif any(keyword in item_type for keyword in ['pants', 'jeans', 'shorts', 'skirt']):
            return 'bottom'
        elif any(keyword in item_type for keyword in ['shoe', 'sneaker', 'boot']):
            return 'shoes'
        elif any(keyword in item_type for keyword in ['jacket', 'coat', 'sweater', 'cardigan']):
            return 'outerwear'
        elif any(keyword in item_type for keyword in ['accessory', 'jewelry', 'bag']):
            return 'accessory'
        else:
            return 'other'
    
    def filter_items_by_temperature(self, items: List[ClothingItem], temperature: float, occasion: str = None) -> List[ClothingItem]:
        """Filter items based on temperature with proper conversion."""
        if not items:
            return items
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        filtered_items = []
        
        for item in items:
            if self._is_temperature_appropriate(item, temperature, occasion):
                filtered_items.append(item)
        
        return filtered_items
    
    def _is_temperature_appropriate(self, item: ClothingItem, temperature: float, occasion: str = None) -> bool:
        """Check if item is appropriate for the given temperature."""
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        # Get material from metadata if available
        material = ""
        if item.metadata and item.metadata.visualAttributes and item.metadata.visualAttributes.material:
            material = item.metadata.visualAttributes.material.lower() if item.metadata.visualAttributes.material else ""
        
        # Hot weather (80°F+)
        if temperature >= 85:  # Hot weather
            # Remove heavy winter items
            winter_materials = ['wool', 'fleece', 'thick', 'heavy']
            if material and any(mat in material for mat in winter_materials):
                return False
        
        # Warm weather (75-84°F)
        elif temperature >= 75:  # Warm weather
            # Allow most items, but prefer lighter materials
            pass
        
        # Mild weather (65-74°F)
        elif temperature >= 65:  # Mild weather
            # Allow most items
            pass
        
        # Cool weather (50-64°F)
        elif temperature >= 50:  # Cool weather
            # Prefer slightly warmer items
            pass
        
        # Cold weather (<50°F)
        else:  # Cold weather
            # Remove obvious summer items
            summer_materials = ['linen', 'light cotton']
            if material and any(mat in material for mat in summer_materials):
                return False
        
        return True 