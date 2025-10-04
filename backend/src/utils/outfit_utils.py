"""
Utility functions for outfit generation to eliminate code duplication.
"""

from typing import Any, Dict, List
from ..custom_types.wardrobe import ClothingItem


def get_color_name(color: Any) -> str:
    """
    Extract color name from color object.
    
    Args:
        color: Color object that may be a dict, object with .name attribute, or string
        
    Returns:
        str: Color name as string
    """
    if hasattr(color, 'name'):
        return color.name
    elif isinstance(color, dict) and 'name' in color:
        return color['name']
    elif isinstance(color, str):
        return color
    else:
        return str(color)


def athletic_sort_key(item: ClothingItem, preferences: List[str]) -> int:
    """
    Sort items by athletic preferences.
    
    Args:
        item: Clothing item to sort
        preferences: List of preferred item types in order of preference
        
    Returns:
        int: Sort key (lower = higher priority)
    """
    item_type = item.type.lower()
    for preferred_type in preferences:
        if preferred_type in item_type:
            return preferences.index(preferred_type)
    return len(preferences)  # Put non-preferred items last


def check_body_type_compatibility(item: ClothingItem, body_type: str) -> bool:
    """
    Check if an item is compatible with the user's body type.
    
    Args:
        item: Clothing item to check
        body_type: User's body type
        
    Returns:
        bool: True if compatible, False otherwise
    """
    if not body_type or body_type == "average":
        return True  # Default to compatible if no specific body type
    
    # Get body type compatibility from item metadata
    if hasattr(item, 'metadata') and item.metadata:
        metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
        
        # Check visual attributes for body type compatibility
        if 'visualAttributes' in metadata:
            visual_attrs = metadata['visualAttributes']
            # Add null check for visual_attrs
            if visual_attrs is not None and 'bodyTypeCompatibility' in visual_attrs:
                body_comp = visual_attrs['bodyTypeCompatibility']
                if isinstance(body_comp, dict):
                    # Check if the body type is in the recommended fits
                    recommended_fits = (body_comp.get('recommendedFits', {}) if body_comp else {})
                    if body_type in recommended_fits:
                        return True
                    
                    # Check if the body type is in the style recommendations
                    style_recs = (body_comp.get('styleRecommendations', {}) if body_comp else {})
                    if body_type in style_recs:
                        return True
    
    # Default to compatible if no specific compatibility data
    return True


def check_skin_tone_compatibility(item: ClothingItem, skin_tone: str) -> bool:
    """
    Check if an item is compatible with the user's skin tone.
    
    Args:
        item: Clothing item to check
        skin_tone: User's skin tone
        
    Returns:
        bool: True if compatible, False otherwise
    """
    if not skin_tone:
        return True  # Default to compatible if no specific skin tone
    
    # Get skin tone compatibility from item metadata
    if hasattr(item, 'metadata') and item.metadata:
        metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
        
        # Check visual attributes for skin tone compatibility
        if 'visualAttributes' in metadata:
            visual_attrs = metadata['visualAttributes']
            # Add null check for visual_attrs
            if visual_attrs is not None and 'skinToneCompatibility' in visual_attrs:
                skin_comp = visual_attrs['skinToneCompatibility']
                if isinstance(skin_comp, dict):
                    # Check if the skin tone is in the compatible colors
                    compatible_colors = (skin_comp.get('compatibleColors', {}) if skin_comp else {})
                    if skin_tone in compatible_colors:
                        return True
                    
                    # Check if the skin tone is in the recommended palettes
                    recommended_palettes = (skin_comp.get('recommendedPalettes', {}) if skin_comp else {})
                    if skin_tone in recommended_palettes:
                        return True
    
    # Default to compatible if no specific compatibility data
    return True


def extract_color_names(colors: List[Any]) -> List[str]:
    """
    Extract color names from a list of color objects.
    
    Args:
        colors: List of color objects
        
    Returns:
        List[str]: List of color names
    """
    return [get_color_name(color) for color in colors]


def get_item_category(item: ClothingItem) -> str:
    """
    Get the category of a clothing item based on its type.
    
    Args:
        item: Clothing item
        
    Returns:
        str: Category (top, bottom, shoes, accessory, outerwear)
    """
    item_type = item.type.lower()
    
    # Define category mappings
    category_mappings = {
        'top': ['shirt', 't-shirt', 'blouse', 'sweater', 'polo', 'tank top'],
        'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'leggings'],
        'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'flats', 'heels'],
        'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'bag', 'hat'],
        'outerwear': ['jacket', 'coat', 'blazer', 'cardigan', 'hoodie']
    }
    
    # Check each category
    for category, types in category_mappings.items():
        if any(t in item_type for t in types):
            return category
    
    # Default to 'accessory' if no specific category found
    return 'accessory' 