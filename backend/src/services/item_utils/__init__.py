"""
Item Utils Package
==================

Utility functions for working with clothing items.

Modules:
- safe_accessors: Safe attribute access for items
- category_detector: Detect item categories
- item_type_checkers: Check specific item types
- formality: Formality level detection
"""

from .safe_accessors import (
    safe_get_item_type,
    safe_get_item_name,
    safe_get_item_attr,
    safe_get,
    safe_item_access,
)

from .category_detector import (
    get_item_category,
)

from .item_type_checkers import (
    is_shirt,
    is_turtleneck,
    is_collared,
    is_sweater_vest,
    is_tank_top,
    get_sleeve_length,
    is_dress,
    is_formal_item,
    is_casual_item,
    is_athletic_item,
)

from .formality import (
    get_item_formality_level,
    get_context_formality_level,
)

__all__ = [
    # safe_accessors
    "safe_get_item_type",
    "safe_get_item_name",
    "safe_get_item_attr",
    "safe_get",
    "safe_item_access",
    # category_detector
    "get_item_category",
    # item_type_checkers
    "is_shirt",
    "is_turtleneck",
    "is_collared",
    "is_sweater_vest",
    "is_tank_top",
    "get_sleeve_length",
    "is_dress",
    "is_formal_item",
    "is_casual_item",
    "is_athletic_item",
    # formality
    "get_item_formality_level",
    "get_context_formality_level",
]

