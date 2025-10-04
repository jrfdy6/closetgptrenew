from typing import List
from ...custom_types.wardrobe import ClothingItem

def has_required_categories(items: List[ClothingItem]) -> bool:
    # Map item types to categories
    category_mapping = {
        "shirt": "top",
        "t-shirt": "top", 
        "blouse": "top",
        "sweater": "top",
        "jacket": "outerwear",
        "coat": "outerwear",
        "pants": "bottom",
        "jeans": "bottom",
        "shorts": "bottom",
        "skirt": "bottom",
        "dress": "dress",
        "shoes": "shoes",
        "sneakers": "shoes",
        "boots": "shoes",
        "accessory": "accessory",
        "bag": "accessory"
    }
    
    # Get categories from item types
    categories = []
    for item in items:
        item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
        category = (category_mapping.get(item_type, "other") if category_mapping else "other")
        categories.append(category)
    
    # Check for required categories: top, bottom, shoes
    required_categories = ['top', 'bottom', 'shoes']
    return all(cat in categories for cat in required_categories)

def has_min_items(items: List[ClothingItem], min_items: int = 3) -> bool:
    return len(items) >= min_items

def is_occasion_appropriate(items: List[ClothingItem], context) -> bool:
    # Dummy: always true for now
    return True

def meets_layer_count(items: List[ClothingItem], context) -> bool:
    # Dummy: always true for now
    return True 