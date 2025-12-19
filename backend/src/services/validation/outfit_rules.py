#!/usr/bin/env python3
"""
Outfit Composition Rules
========================

Core rules for outfit composition, including the canonical invariant gate.
"""

import logging
from typing import Any, Tuple, List

logger = logging.getLogger(__name__)


def can_add_category(
    category: str,
    categories_filled: dict,
    selected_items: list,
    item: Any = None,
    is_shirt_func: callable = None,
) -> Tuple[bool, str]:
    """
    Canonical invariant gate for outfit composition.
    
    Enforces three core invariants:
    1. No duplicate dresses
    2. Dress ↔ Tops/Bottoms bidirectional exclusion
    3. No two shirts
    
    Args:
        category: Category to check ('dress', 'tops', 'bottoms', etc.)
        categories_filled: Dict tracking which categories are already in outfit
        selected_items: List of items already selected
        item: Optional item object (needed for shirt duplicate check)
        is_shirt_func: Function to check if an item is a shirt
    
    Returns:
        (can_add: bool, reason: str)
    """
    
    # 👗 INVARIANT 1: No duplicate dresses
    if category == 'dress' and categories_filled.get('dress'):
        return False, "duplicate dress"
    
    # 👗 INVARIANT 2: Dress ↔ Tops/Bottoms (bidirectional)
    if category == 'dress':
        if categories_filled.get('bottoms'):
            return False, "bottoms already exist"
        if categories_filled.get('tops'):
            return False, "tops already exist"
    
    if category in ('tops', 'bottoms'):
        if categories_filled.get('dress'):
            return False, "dress already exists"
    
    # 👕 INVARIANT 3: No two shirts
    if category == 'tops' and item is not None and is_shirt_func is not None:
        if is_shirt_func(item):
            has_shirt = any(is_shirt_func(i) for i in selected_items)
            if has_shirt:
                return False, "shirt already exists"
    
    # ✅ Outerwear, accessories, others are allowed
    return True, ""


def check_inappropriate_combination(item1: Any, item2: Any) -> bool:
    """
    Check if two items form an inappropriate combination.
    
    Returns:
        True if combination is inappropriate, False otherwise
    """
    # For now, allow all combinations
    # This can be expanded with specific rules as needed
    return False


def get_essential_requirements(occasion: str, style: str, has_dress: bool) -> dict:
    """
    Get essential categories based on context.
    
    Returns:
        Dict with 'required', 'preferred', and 'optional' category lists
    """
    occasion_lower = (occasion or "").lower()
    style_lower = (style or "").lower()
    
    # If dress exists, it replaces tops + bottoms
    if has_dress:
        return {
            'required': ['shoes'],  # Only shoes required with dress
            'preferred': ['outerwear'],  # Outerwear nice to have
            'optional': []
        }
    
    # Context-specific rules for non-dress outfits
    if occasion_lower == 'loungewear' or style_lower in ['loungewear', 'minimal', 'casual']:
        return {
            'required': ['tops', 'shoes'],  # Bottoms optional for lounge/minimal
            'preferred': ['bottoms'],
            'optional': ['outerwear']
        }
    elif occasion_lower in ['gym', 'workout', 'athletic']:
        return {
            'required': ['tops', 'bottoms', 'shoes'],  # All required for gym
            'preferred': [],
            'optional': ['outerwear']
        }
    else:
        # Default: tops + bottoms + shoes required
        return {
            'required': ['tops', 'bottoms', 'shoes'],
            'preferred': [],
            'optional': ['outerwear', 'accessories']
        }

