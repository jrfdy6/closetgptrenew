"""
Validation Package
==================

Outfit validation and composition rules.

Modules:
- outfit_rules: Core outfit composition rules
- deduplication: Item deduplication utilities
"""

from .outfit_rules import (
    can_add_category,
    check_inappropriate_combination,
    get_essential_requirements,
)

from .deduplication import (
    deduplicate_items,
)

__all__ = [
    # outfit_rules
    "can_add_category",
    "check_inappropriate_combination",
    "get_essential_requirements",
    # deduplication
    "deduplicate_items",
]

