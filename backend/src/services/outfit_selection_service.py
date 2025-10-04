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
        
        # Get base item from context
        base_item = (context.get("base_item") if context else None)
        selected_items = []
        
        # Always include the base item if provided
        if base_item:
#             print(f"🎯 Including base item in selection: {base_item.name} ({base_item.type})")
            selected_items.append(base_item)
        
        # For now, select additional items from filtered wardrobe
        # In a full implementation, this would use sophisticated selection logic
        target_count = (context.get("target_counts", {}) if context else {}).get("min_items", 3)
        
        # Add additional items, excluding the base item if it's already in filtered_wardrobe
        additional_items_needed = target_count - len(selected_items)
        additional_items = []
        
        for item in filtered_wardrobe:
            if len(additional_items) >= additional_items_needed:
                break
            # Skip if this item is the same as the base item (already included)
            if base_item and item.id == base_item.id:
                continue
            additional_items.append(item)
        
        selected_items.extend(additional_items)
        
        # Ensure we have at least 2 items
        if len(selected_items) < 2:
            # Add more items if needed
            for item in filtered_wardrobe:
                if len(selected_items) >= 2:
                    break
                if base_item and item.id == base_item.id:
                    continue
                if item not in selected_items:
                    selected_items.append(item)
        
#         print(f"🎯 Final selection: {len(selected_items)} items")
        for i, item in enumerate(selected_items):
#             print(f"  {i+1}. {item.name} ({item.type})")
        
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
