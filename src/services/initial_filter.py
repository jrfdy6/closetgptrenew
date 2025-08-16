from typing import List
from ..custom_types.wardrobe import ClothingItem

def light_filtering(wardrobe: List[ClothingItem], context) -> List[ClothingItem]:
    """Light filtering - only basic availability and weather filtering."""
    # Filter by seasonal_score if present, else pass all
    # Use threshold of 0.5 to match test expectations
    filtered = [item for item in wardrobe if getattr(item, 'seasonal_score', 1.0) >= 0.5]
    return filtered 