#!/usr/bin/env python3
"""
Outfit Generation Constants
============================

Core constants and configuration for outfit generation.
Extracted from robust_outfit_generation_service.py for better maintainability.
"""

from enum import Enum


class GenerationStrategy(Enum):
    """Outfit generation strategies with fallback order"""
    COHESIVE_COMPOSITION = "cohesive_composition"
    BODY_TYPE_OPTIMIZED = "body_type_optimized"
    STYLE_PROFILE_MATCHED = "style_profile_matched"
    WEATHER_ADAPTED = "weather_adapted"
    FALLBACK_SIMPLE = "fallback_simple"
    EMERGENCY_DEFAULT = "emergency_default"


# Dynamic category limits based on occasion and style
BASE_CATEGORY_LIMITS = {
    "tops": 2,
    "bottoms": 1,
    "shoes": 1,
    "outerwear": 1,
    "accessories": 2,
    "dress": 1  # Only one dress allowed
}

# Item count constraints
MAX_ITEMS = 8  # Maximum items in an outfit
MIN_ITEMS = 3  # Minimum items in an outfit

# Inappropriate combinations to prevent
INAPPROPRIATE_COMBINATIONS = {
    ("blazer", "shorts"): "Blazers should not be paired with shorts",
    ("formal_shoes", "casual_bottoms"): "Formal shoes should not be paired with casual bottoms",
    ("high_heels", "athletic_wear"): "High heels should not be paired with athletic wear",
    ("tie", "t_shirt"): "Ties should not be worn with t-shirts",
    ("suit", "sneakers"): "Suits should not be paired with sneakers",
    ("dress", "tops"): "Dresses should not be paired with tops",
    ("dress", "bottoms"): "Dresses should not be paired with bottoms",
}

# Style profile compatibility rules
STYLE_COMPATIBILITY = {
    "formal": ["business_casual", "smart_casual"],
    "casual": ["smart_casual", "athleisure", "streetwear"],
    "athletic": ["athleisure", "casual"],
    "business_casual": ["formal", "smart_casual"],
    "streetwear": ["casual", "athleisure"],
    "minimalist": ["modern", "scandinavian", "contemporary"],
    "bohemian": ["casual", "festival", "artistic"],
    "preppy": ["classic", "ivy-league", "collegiate"],
}

# Generation strategy order (fallback sequence)
GENERATION_STRATEGY_ORDER = [
    GenerationStrategy.COHESIVE_COMPOSITION,
    GenerationStrategy.BODY_TYPE_OPTIMIZED,
    GenerationStrategy.STYLE_PROFILE_MATCHED,
    GenerationStrategy.WEATHER_ADAPTED,
    GenerationStrategy.FALLBACK_SIMPLE,
    GenerationStrategy.EMERGENCY_DEFAULT
]

# Category mappings
CATEGORY_ALIASES = {
    "shirt": "tops",
    "t-shirt": "tops",
    "t_shirt": "tops",
    "blouse": "tops",
    "top": "tops",
    "sweater": "tops",
    "cardigan": "tops",
    "hoodie": "tops",
    "jacket": "outerwear",
    "coat": "outerwear",
    "blazer": "outerwear",
    "pant": "bottoms",
    "pants": "bottoms",
    "jeans": "bottoms",
    "trousers": "bottoms",
    "shorts": "bottoms",
    "skirt": "bottoms",
    "shoe": "shoes",
    "boot": "shoes",
    "boots": "shoes",
    "sneaker": "shoes",
    "sneakers": "shoes",
    "sandal": "shoes",
    "sandals": "shoes",
    "heel": "shoes",
    "heels": "shoes",
    "accessory": "accessories",
    "bag": "accessories",
    "hat": "accessories",
    "scarf": "accessories",
    "belt": "accessories",
    "jewelry": "accessories",
    "watch": "accessories",
    "sunglasses": "accessories",
}

# Essential categories for different occasions
ESSENTIAL_CATEGORIES_BY_OCCASION = {
    "default": ["tops", "bottoms", "shoes"],
    "formal": ["tops", "bottoms", "shoes", "outerwear"],
    "business": ["tops", "bottoms", "shoes"],
    "interview": ["tops", "bottoms", "shoes"],
    "casual": ["tops", "shoes"],  # Bottoms optional for some casual looks
    "party": ["tops", "shoes"],  # Dress can replace tops+bottoms
    "date": ["tops", "shoes"],
    "gym": ["tops", "bottoms", "shoes"],
    "athletic": ["tops", "bottoms", "shoes"],
    "loungewear": ["tops", "shoes"],  # Bottoms optional
    "beach": ["tops", "shoes"],  # Swimwear context
}

# Weather-based layering requirements
LAYERING_REQUIREMENTS = {
    "cold": {"min_layers": 2, "requires_outerwear": True},
    "cool": {"min_layers": 1, "requires_outerwear": False},
    "mild": {"min_layers": 1, "requires_outerwear": False},
    "warm": {"min_layers": 1, "requires_outerwear": False},
    "hot": {"min_layers": 1, "requires_outerwear": False},
}

# Temperature thresholds (Fahrenheit)
TEMPERATURE_THRESHOLDS = {
    "hot": 85,
    "warm": 70,
    "mild": 60,
    "cool": 50,
    "cold": 40,
    "very_cold": 32,
}

# Formality levels
FORMALITY_LEVELS = {
    "very_formal": 5,
    "formal": 4,
    "business_casual": 3,
    "smart_casual": 2,
    "casual": 1,
    "athletic": 0,
}

# Occasion formality mapping
OCCASION_FORMALITY = {
    "interview": 5,
    "business": 5,
    "formal": 5,
    "black-tie": 5,
    "gala": 5,
    "wedding": 4,
    "cocktail": 4,
    "date-night": 3,
    "dinner": 3,
    "brunch": 2,
    "casual": 1,
    "party": 2,
    "gym": 0,
    "athletic": 0,
    "loungewear": 0,
}

