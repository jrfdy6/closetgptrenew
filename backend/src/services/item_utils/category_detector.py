#!/usr/bin/env python3
"""
Category Detector
=================

Detects the category of clothing items (tops, bottoms, dress, shoes, outerwear, accessories).
Uses metadata-first approach with fallback to keyword matching.
"""

import logging
from typing import Any
from .safe_accessors import safe_get_item_name, safe_get_item_attr, safe_get

logger = logging.getLogger(__name__)


def get_item_category(item: Any) -> str:
    """
    Get category for an item - METADATA-FIRST approach.
    
    Returns one of: 'tops', 'bottoms', 'dress', 'shoes', 'outerwear', 'accessories', 'other'
    """
    item_type = getattr(item, 'type', '')
    item_name = getattr(item, 'name', 'Unknown')
    
    # METADATA CHECK: Use coreCategory from metadata if available (most accurate!)
    item_name_lower = safe_get_item_name(item).lower()
    raw_item_type = getattr(item, 'type', '')
    item_type_lower = ''
    if hasattr(raw_item_type, 'value'):
        item_type_lower = raw_item_type.value.lower()
    elif hasattr(raw_item_type, 'name'):
        item_type_lower = raw_item_type.name.lower()
    else:
        item_type_lower = str(raw_item_type).lower()
    
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                core_category = (visual_attrs.get('coreCategory') or '').lower()
                if core_category:
                    # Map coreCategory values to our category system
                    core_category_map = {
                        'top': 'tops',
                        'tops': 'tops',
                        'shirt': 'tops',
                        'bottom': 'bottoms',
                        'bottoms': 'bottoms',
                        'pants': 'bottoms',
                        'shorts': 'bottoms',
                        'shoe': 'shoes',
                        'shoes': 'shoes',
                        'footwear': 'shoes',
                        'outerwear': 'outerwear',
                        'jacket': 'outerwear',
                        'accessory': 'accessories',
                        'accessories': 'accessories'
                    }
                    if core_category in core_category_map:
                        category = core_category_map[core_category]
                        if category == 'tops' and any(keyword in item_type_lower or keyword in item_name_lower for keyword in ['blazer', 'jacket', 'coat']):
                            category = 'outerwear'
                        elif category == 'bottoms' and item_type_lower in ['sweater', 'shirt', 'top', 't-shirt', 't_shirt', 'hoodie', 'cardigan']:
                            logger.debug(
                                f"🏷️ CATEGORY (metadata override): '{item_name[:50]}' coreCategory='{core_category}' "
                                f"but type='{item_type_lower}' → treating as 'tops'"
                            )
                            category = 'tops'
                        logger.debug(f"🏷️ CATEGORY (metadata): '{item_name[:50]}' coreCategory='{core_category}' → '{category}'")
                        return category
    
    # Fallback to type-based detection
    # Handle enum types (e.g., ClothingType.SHIRT)
    item_type = item_type_lower
    
    # Handle ClothingType enum format (e.g., "ClothingType.SHIRT" -> "shirt")
    if 'clothingtype.' in item_type:
        item_type = item_type.split('.')[-1]
    
    # Map item types to categories
    category_map = {
        'shirt': 'tops',
        't-shirt': 'tops', 
        'blouse': 'tops',
        'sweater': 'tops',  # Pullover sweaters worn as tops
        'tank': 'tops',
        'polo': 'tops',
        'pants': 'bottoms',
        'jeans': 'bottoms',
        'shorts': 'bottoms',
        'skirt': 'bottoms',
        'dress': 'dress',  # Dresses are standalone - replace both top and bottom
        'romper': 'dress',  # Rompers treated like dresses
        'jumpsuit': 'dress',  # Jumpsuits treated like dresses
        'shoes': 'shoes',
        'sneakers': 'shoes',
        'boots': 'shoes',
        'heels': 'shoes',
        'jacket': 'outerwear',
        'blazer': 'outerwear',
        'coat': 'outerwear',
        'cardigan': 'outerwear',  # Cardigans are layers, can be worn over dresses
        'hoodie': 'outerwear'
    }
    
    category = safe_get(category_map, item_type, 'other')
    
    # If category is 'other', try fuzzy keyword matching
    if category == 'other':
        # Check for dress keywords (highest priority - must come before tops/bottoms)
        dress_keywords = ['dress', 'romper', 'jumpsuit', 'maxi', 'midi dress', 'mini dress']
        if any(kw in item_type or kw in item_name for kw in dress_keywords):
            category = 'dress'
            logger.debug(f"👗 KEYWORD MATCH: '{item_name[:50]}' → 'dress'")
        
        # Check for tops keywords
        elif any(kw in item_type or kw in item_name for kw in ['shirt', 't-shirt', 't_shirt', 'blouse', 'tank', 'polo', 'sweater', 'tee']):
            category = 'tops'
            logger.debug(f"👔 KEYWORD MATCH: '{item_name[:50]}' → 'tops'")
        
        # Check for bottoms keywords
        elif any(kw in item_type or kw in item_name for kw in ['pants', 'jeans', 'shorts', 'skirt', 'trouser', 'denim']):
            category = 'bottoms'
            logger.debug(f"👖 KEYWORD MATCH: '{item_name[:50]}' → 'bottoms'")
        
        # Check for shoes keywords
        elif any(kw in item_type or kw in item_name for kw in ['shoes', 'sneakers', 'boots', 'heels', 'sandals', 'loafers', 'flats']):
            category = 'shoes'
            logger.debug(f"👟 KEYWORD MATCH: '{item_name[:50]}' → 'shoes'")
        
        # Check for outerwear keywords
        elif any(kw in item_type or kw in item_name for kw in ['jacket', 'coat', 'blazer', 'cardigan', 'hoodie']):
            category = 'outerwear'
            logger.debug(f"🧥 KEYWORD MATCH: '{item_name[:50]}' → 'outerwear'")
    
    # Special handling: Check if a "sweater" is actually a layering piece (cardigan, open-front, etc.)
    if category == 'tops':
        layering_keywords = ['cardigan', 'open front', 'open-front', 'button-up sweater', 
                             'zip sweater', 'kimono', 'duster', 'wrap sweater', 'shrug']
        if any(kw in item_name for kw in layering_keywords):
            category = 'outerwear'
            logger.debug(f"🧥 RECLASSIFIED '{item_name[:50]}' from tops → outerwear (layering piece)")
    
    # 🔍 DIAGNOSTIC LOGGING - Track category assignment for debugging
    logger.debug(f"🏷️ CATEGORY (type-based): '{item_name[:50]}' type='{item_type}' → category='{category}'")
    
    return category

