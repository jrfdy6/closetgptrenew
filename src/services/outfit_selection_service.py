"""
Outfit Selection Service
Smart selection and item categorization logic.
"""

from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile

class OutfitSelectionService:
    def __init__(self):
        pass
        
    def _safe_temperature_convert(self, temperature) -> float:
        """Safely convert temperature to float to prevent string vs float comparison errors."""
        if isinstance(temperature, str):
            try:
                return float(temperature)
            except (ValueError, TypeError):
                return 70.0
        elif temperature is None:
            return 70.0
        else:
            return float(temperature)
            
    def smart_selection_phase(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Phase 3: Select best-fit items using priority, style match, and harmony rules."""
        if not filtered_wardrobe:
            return []
        
        # For now, select the first 3-4 items as a simple implementation
        # In a full implementation, this would use sophisticated selection logic
        target_count = context.get("target_counts", {}).get("min_items", 3)
        
        selected_items = filtered_wardrobe[:target_count]
        
        # Ensure we have at least 2 items
        if len(selected_items) < 2:
            selected_items = filtered_wardrobe[:2] if len(filtered_wardrobe) >= 2 else filtered_wardrobe
        
        return selected_items
        
    def select_core_items(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select core items for the outfit."""
        # For now, select first few items
        return filtered_wardrobe[:3] if len(filtered_wardrobe) >= 3 else filtered_wardrobe
        
    def get_item_categories(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Get items categorized by type."""
        categories = {}
        for item in items:
            item_type = item.type.lower()
            if item_type not in categories:
                categories[item_type] = []
            categories[item_type].append(item)
        return categories
