#!/usr/bin/env python3
"""
Safe Item Accessors
===================

Utility functions for safely accessing clothing item attributes.
Handles both ClothingItem objects and dict representations.
"""

from typing import Any, Optional


def safe_get_item_type(item: Any) -> str:
    """Safely get item type from either ClothingItem object or dict."""
    if hasattr(item, 'type'):
        return item.type
    elif isinstance(item, dict):
        return item.get('type', 'unknown')
    else:
        return 'unknown'


def safe_get_item_name(item: Any) -> str:
    """Safely get item name from either ClothingItem object or dict."""
    if hasattr(item, 'name'):
        return item.name
    elif isinstance(item, dict):
        return item.get('name', 'Unknown')
    else:
        return 'Unknown'


def safe_get_item_attr(item: Any, attr: str, default: Any = None) -> Any:
    """Safely get any attribute from either ClothingItem object or dict."""
    if hasattr(item, attr):
        return getattr(item, attr)
    elif isinstance(item, dict):
        return item.get(attr, default)
    else:
        return default


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get value from dict or object attribute."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    elif hasattr(obj, key):
        return getattr(obj, key, default)
    else:
        return default


def safe_item_access(item: Any, key: str, default: Any = None) -> Any:
    """Legacy alias for safe_get_item_attr."""
    return safe_get_item_attr(item, key, default)

