"""
Constants Package
=================

This package contains all constants, configuration, and keyword definitions
for outfit generation.

Modules:
- outfit_constants: Core outfit generation constants
- keywords: Occasion, style, and item type keywords
"""

from .outfit_constants import (
    GenerationStrategy,
    BASE_CATEGORY_LIMITS,
    MAX_ITEMS,
    MIN_ITEMS,
    INAPPROPRIATE_COMBINATIONS,
    STYLE_COMPATIBILITY,
    GENERATION_STRATEGY_ORDER,
    CATEGORY_ALIASES,
    ESSENTIAL_CATEGORIES_BY_OCCASION,
    LAYERING_REQUIREMENTS,
    TEMPERATURE_THRESHOLDS,
    FORMALITY_LEVELS,
    OCCASION_FORMALITY,
)

from .keywords import (
    OCCASION_KEYWORDS,
    STYLE_KEYWORDS,
    ITEM_TYPE_KEYWORDS,
    FORMALITY_KEYWORDS,
    WEATHER_KEYWORDS,
    COLOR_FAMILIES,
    PATTERN_KEYWORDS,
    MATERIAL_KEYWORDS,
    SEASON_KEYWORDS,
)

__all__ = [
    # outfit_constants
    "GenerationStrategy",
    "BASE_CATEGORY_LIMITS",
    "MAX_ITEMS",
    "MIN_ITEMS",
    "INAPPROPRIATE_COMBINATIONS",
    "STYLE_COMPATIBILITY",
    "GENERATION_STRATEGY_ORDER",
    "CATEGORY_ALIASES",
    "ESSENTIAL_CATEGORIES_BY_OCCASION",
    "LAYERING_REQUIREMENTS",
    "TEMPERATURE_THRESHOLDS",
    "FORMALITY_LEVELS",
    "OCCASION_FORMALITY",
    # keywords
    "OCCASION_KEYWORDS",
    "STYLE_KEYWORDS",
    "ITEM_TYPE_KEYWORDS",
    "FORMALITY_KEYWORDS",
    "WEATHER_KEYWORDS",
    "COLOR_FAMILIES",
    "PATTERN_KEYWORDS",
    "MATERIAL_KEYWORDS",
    "SEASON_KEYWORDS",
]

