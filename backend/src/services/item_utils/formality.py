#!/usr/bin/env python3
"""
Formality Level Detection
=========================

Functions to determine formality levels of items and contexts.
"""

import logging
from typing import Optional, Any
from .safe_accessors import safe_get_item_type, safe_get_item_name

logger = logging.getLogger(__name__)


def get_item_formality_level(item: Any) -> Optional[int]:
    """
    Get item's formality level.
    
    Returns:
        0 = casual
        1 = smart casual
        2 = business casual
        3 = formal
        4 = black tie
    """
    # Check metadata first
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                formal_level = (visual_attrs.get('formalLevel') or '').lower()
                if 'black tie' in formal_level or 'formal event' in formal_level:
                    return 4
                elif 'formal' in formal_level or 'business formal' in formal_level:
                    return 3
                elif 'business casual' in formal_level or 'smart' in formal_level:
                    return 2
                elif 'smart casual' in formal_level:
                    return 1
                elif 'casual' in formal_level:
                    return 0
    
    # Fallback: infer from item type and name
    item_type = str(safe_get_item_type(item)).lower()
    item_name = safe_get_item_name(item).lower()
    
    # Formal items (3-4)
    if any(kw in item_type or kw in item_name for kw in ['tuxedo', 'gown', 'bow tie', 'cufflink']):
        return 4
    elif any(kw in item_type or kw in item_name for kw in ['suit', 'blazer', 'dress shirt', 'tie', 'oxford', 'loafer']):
        return 3
    # Business casual (2)
    elif any(kw in item_type or kw in item_name for kw in ['chino', 'khaki', 'dress pant', 'polo', 'cardigan', 'derby']):
        return 2
    # Smart casual (1)
    elif any(kw in item_type or kw in item_name for kw in ['dark jean', 'button', 'sweater', 'boot']):
        return 1
    # Casual (0)
    else:
        return 0


def get_context_formality_level(occasion: str, style: str) -> Optional[int]:
    """
    Get target formality level from occasion and style.
    
    Returns:
        0 = casual
        1 = smart casual
        2 = business casual
        3 = formal
        4 = black tie
    """
    occasion_lower = (occasion or '').lower()
    style_lower = (style or '').lower()
    
    # Occasion-based formality (highest priority)
    if any(kw in occasion_lower for kw in ['gala', 'black tie', 'wedding formal']):
        return 4
    elif any(kw in occasion_lower for kw in ['interview', 'business', 'formal', 'conference']):
        return 3
    elif any(kw in occasion_lower for kw in ['business casual', 'date', 'brunch']):
        return 2
    elif any(kw in occasion_lower for kw in ['smart casual', 'weekend']):
        return 1
    
    # Style-based formality (if occasion is neutral)
    if any(kw in style_lower for kw in ['formal', 'classic', 'preppy', 'old money']):
        return 3
    elif any(kw in style_lower for kw in ['business casual', 'urban professional']):
        return 2
    elif any(kw in style_lower for kw in ['smart', 'minimalist']):
        return 1
    else:
        return 0

