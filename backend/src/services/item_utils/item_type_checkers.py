#!/usr/bin/env python3
"""
Item Type Checkers
==================

Functions to check specific item types (shirt, turtleneck, collared, etc.).
"""

import logging
from typing import Any
from .safe_accessors import safe_get_item_name, safe_get_item_type

logger = logging.getLogger(__name__)


def is_shirt(item: Any) -> bool:
    """Check if item is a shirt (not a sweater, hoodie, or outerwear)."""
    item_type = str(safe_get_item_type(item)).lower()
    item_name = safe_get_item_name(item).lower()
    
    # Check metadata for coreCategory
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                core_category = (visual_attrs.get('coreCategory') or '').lower()
                if core_category in ['top', 'tops', 'shirt']:
                    # But exclude if it's actually outerwear
                    if any(kw in item_name for kw in ['jacket', 'coat', 'blazer']):
                        return False
                    # Exclude sweaters, hoodies, cardigans
                    if any(kw in item_name or kw in item_type for kw in ['sweater', 'hoodie', 'cardigan', 'vest']):
                        return False
                    return True
    
    # Check type and name
    shirt_keywords = ['shirt', 't-shirt', 't_shirt', 'blouse', 'polo', 'button-up', 'button up', 'dress shirt', 'oxford']
    if any(kw in item_type or kw in item_name for kw in shirt_keywords):
        # Exclude sweaters, hoodies, cardigans
        if any(kw in item_name or kw in item_type for kw in ['sweater', 'hoodie', 'cardigan', 'vest']):
            return False
        return True
    
    return False


def is_turtleneck(item: Any) -> bool:
    """Check if item is a turtleneck."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    # Check metadata
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                neckline = (visual_attrs.get('neckline') or '').lower()
                if 'turtleneck' in neckline or 'turtle' in neckline:
                    return True
    
    # Check name/type
    return 'turtleneck' in item_name or 'turtle' in item_name


def is_collared(item: Any) -> bool:
    """Check if item has a collar."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    # Check metadata
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                neckline = (visual_attrs.get('neckline') or '').lower()
                collar_type = (visual_attrs.get('collarType') or '').lower()
                if 'collar' in neckline or 'collar' in collar_type or 'polo' in neckline:
                    return True
    
    # Check name/type
    collar_keywords = ['collar', 'collared', 'polo', 'button-up', 'button up', 'dress shirt', 'oxford']
    return any(kw in item_name or kw in item_type for kw in collar_keywords)


def is_sweater_vest(item: Any) -> bool:
    """Check if item is a sweater vest (sleeveless sweater)."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    # Check metadata
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                if 'vest' in item_name and ('sweater' in item_name or 'sweater' in item_type):
                    return True
                if 'sleeveless' in sleeve_length and ('sweater' in item_name or 'sweater' in item_type):
                    return True
    
    # Check name/type
    return ('vest' in item_name and 'sweater' in item_name) or ('sweater vest' in item_name)


def is_tank_top(item: Any) -> bool:
    """Check if item is a tank top."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    # Check metadata
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                if 'sleeveless' in sleeve_length or 'tank' in sleeve_length:
                    return True
    
    # Check name/type
    tank_keywords = ['tank', 'tank top', 'cami', 'camisole', 'sleeveless']
    return any(kw in item_name or kw in item_type for kw in tank_keywords)


def get_sleeve_length(item: Any) -> str:
    """
    Get sleeve length from metadata or infer from name/type.
    
    Returns: 'sleeveless', 'short', 'three_quarter', 'long', 'unknown'
    """
    # Check metadata first
    if hasattr(item, 'metadata') and item.metadata:
        if isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                sleeve_length = visual_attrs.get('sleeveLength')
                if sleeve_length:
                    return str(sleeve_length).lower()
    
    # Fallback: infer from name/type
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    if any(kw in item_name for kw in ['sleeveless', 'tank', 'vest']):
        return 'sleeveless'
    elif any(kw in item_name for kw in ['short sleeve', 'short-sleeve', 't-shirt', 'polo']):
        return 'short'
    elif any(kw in item_name for kw in ['three quarter', '3/4', 'three-quarter']):
        return 'three_quarter'
    elif any(kw in item_name for kw in ['long sleeve', 'long-sleeve']):
        return 'long'
    
    return 'unknown'


def is_dress(item: Any) -> bool:
    """Check if item is a dress."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    dress_keywords = ['dress', 'gown', 'maxi', 'midi dress', 'mini dress', 'romper', 'jumpsuit']
    return any(kw in item_name or kw in item_type for kw in dress_keywords)


def is_formal_item(item: Any) -> bool:
    """Check if item is formal (suit, blazer, dress shoes, etc.)."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    formal_keywords = [
        'suit', 'tuxedo', 'blazer', 'dress shirt', 'dress shoes', 'oxford shoes',
        'loafers', 'heels', 'pumps', 'dress pants', 'slacks', 'tie', 'bow tie'
    ]
    return any(kw in item_name or kw in item_type for kw in formal_keywords)


def is_casual_item(item: Any) -> bool:
    """Check if item is casual (jeans, t-shirt, sneakers, etc.)."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    casual_keywords = [
        'jeans', 't-shirt', 'tee', 'sneakers', 'hoodie', 'sweatshirt',
        'shorts', 'tank top', 'sandals', 'flip-flops'
    ]
    return any(kw in item_name or kw in item_type for kw in casual_keywords)


def is_athletic_item(item: Any) -> bool:
    """Check if item is athletic wear."""
    item_name = safe_get_item_name(item).lower()
    item_type = str(safe_get_item_type(item)).lower()
    
    athletic_keywords = [
        'athletic', 'gym', 'workout', 'running', 'training', 'sport',
        'leggings', 'track pants', 'sports bra', 'athletic shoes'
    ]
    return any(kw in item_name or kw in item_type for kw in athletic_keywords)

