# backend/src/utils/style_compatibility_matrix.py
# Canonical Style Compatibility Matrix for Python backend
# All keys and values are normalized to lowercase for consistent matching
# VERSION: 2025-10-11-COMPREHENSIVE

from typing import Dict, List, Optional

# Canonical Style Compatibility Matrix
STYLE_COMPATIBILITY: Dict[str, List[str]] = {
    "academic": ["academic", "classic", "dark_academia", "intellectual", "traditional"],
    "active": ["active", "athleisure", "athletic", "sporty", "workout"],
    "alternative": ["alternative", "edgy", "grunge", "punk", "streetwear"],
    "androgynous": [
        "androgynous", "balanced", "classic", "gender_neutral", "minimalist",
        "modern", "unisex"
    ],
    "artistic": ["artistic", "artsy", "avant_garde", "bohemian", "eclectic"],
    "artsy": [
        "artistic", "artsy", "avant_garde", "creative", "eclectic",
        "experimental", "fashion_forward"
    ],
    "athleisure": [
        "active", "athleisure", "athletic", "casual", "sporty",
        "techwear", "workout"
    ],
    "athletic": [
        "active", "athleisure", "athletic", "sporty", "techwear",
        "workout"
    ],
    "avant_garde": [
        "artistic", "artsy", "avant_garde", "creative", "edgy",
        "experimental", "fashion_forward"
    ],
    "balanced": [
        "androgynous", "balanced", "business_casual", "casual", "classic",
        "contemporary", "everyday", "minimalist", "modern"
    ],
    "basic": ["basic", "casual", "minimalist", "simple"],
    "bohemian": [
        "artistic", "bohemian", "boho", "cottagecore", "eclectic",
        "romantic", "summer", "textured"
    ],
    "boho": ["bohemian", "boho", "coastal_grandma", "eclectic", "romantic"],
    "bold": [
        "bold", "classic", "edgy", "modern", "retro",
        "statement", "streetwear"
    ],
    "business": [
        "business", "business_casual", "classic", "formal", "polished",
        "professional", "smart_casual"
    ],
    "business_casual": [
        "balanced", "business", "business_casual", "casual", "classic",
        "preppy", "professional", "smart_casual"
    ],
    "casual": [
        "athleisure", "balanced", "basic", "business_casual", "casual",
        "casual_cool", "classic", "coastal_chic", "cozy", "everyday",
        "grunge", "nautical", "perforated", "relaxed", "smart_casual",
        "streetwear", "summer", "textured"
    ],
    "casual_cool": ["casual", "casual_cool", "minimalist", "modern", "streetwear"],
    "classic": [
        "academic", "androgynous", "balanced", "bold", "business",
        "business_casual", "casual", "classic", "dark_academia", "elegant",
        "formal", "geometric", "intellectual", "minimalist", "modern",
        "nautical", "old_money", "perforated", "polished", "preppy",
        "professional", "retro", "sleek", "smart_casual", "sophisticated",
        "statement", "textured", "timeless", "traditional", "unisex",
        "vintage", "winter"
    ],
    "clean": ["clean", "minimalist", "modern", "simple"],
    "coastal_chic": [
        "casual", "coastal_chic", "coastal_grandma", "maritime", "nautical",
        "relaxed", "romantic", "summer"
    ],
    "coastal_grandma": [
        "boho", "coastal_chic", "coastal_grandma", "cottagecore", "relaxed",
        "romantic"
    ],
    "contemporary": [
        "balanced", "contemporary", "geometric", "minimalist", "modern",
        "perforated", "sleek"
    ],
    "cottagecore": [
        "bohemian", "coastal_grandma", "cottagecore", "cozy", "romantic",
        "vintage"
    ],
    "cozy": ["casual", "cottagecore", "cozy", "relaxed", "winter"],
    "creative": ["artsy", "avant_garde", "creative", "eclectic", "experimental"],
    "dark_academia": [
        "academic", "classic", "dark_academia", "intellectual", "traditional",
        "vintage", "winter"
    ],
    "eclectic": [
        "artistic", "artsy", "bohemian", "boho", "creative",
        "eclectic", "romantic"
    ],
    "edgy": [
        "alternative", "avant_garde", "bold", "edgy", "experimental",
        "grunge", "punk", "statement", "streetwear", "urban",
        "y2k"
    ],
    "elegant": ["classic", "elegant", "formal", "romantic", "sophisticated"],
    "everyday": ["balanced", "casual", "everyday", "minimalist", "relaxed"],
    "experimental": [
        "artsy", "avant_garde", "creative", "edgy", "experimental",
        "modern"
    ],
    "fashion-forward": ["fashion-forward", "modern"],
    "fashion_forward": ["artsy", "avant_garde", "fashion_forward", "modern", "statement"],
    "formal": [
        "business", "classic", "elegant", "formal", "polished",
        "professional", "semi-formal", "sophisticated"
    ],
    "gender_neutral": ["androgynous", "gender_neutral", "minimalist", "modern", "unisex"],
    "geometric": [
        "classic", "contemporary", "geometric", "minimalist", "modern",
        "retro"
    ],
    "grunge": [
        "alternative", "casual", "edgy", "grunge", "punk",
        "streetwear"
    ],
    "intellectual": ["academic", "classic", "dark_academia", "intellectual", "minimalist"],
    "maritime": ["coastal_chic", "maritime", "nautical", "preppy"],
    "minimalist": [
        "androgynous", "balanced", "basic", "casual_cool", "classic",
        "clean", "contemporary", "everyday", "gender_neutral", "geometric",
        "intellectual", "minimalist", "modern", "simple", "sleek",
        "timeless", "unisex", "winter"
    ],
    "modern": [
        "androgynous", "balanced", "bold", "casual_cool", "classic",
        "clean", "contemporary", "experimental", "fashion-forward", "fashion_forward",
        "gender_neutral", "geometric", "minimalist", "modern", "perforated",
        "sleek", "statement", "techwear", "textured", "trendy",
        "unisex", "urban"
    ],
    "nautical": [
        "casual", "classic", "coastal_chic", "maritime", "nautical",
        "preppy"
    ],
    "old_money": [
        "classic", "old_money", "polished", "preppy", "sophisticated",
        "timeless", "traditional", "vintage"
    ],
    "perforated": ["casual", "classic", "contemporary", "modern", "perforated"],
    "polished": [
        "business", "classic", "formal", "old_money", "polished",
        "preppy", "sleek"
    ],
    "preppy": [
        "business_casual", "classic", "maritime", "nautical", "old_money",
        "polished", "preppy", "traditional"
    ],
    "professional": [
        "business", "business_casual", "classic", "formal", "professional",
        "smart_casual"
    ],
    "punk": ["alternative", "edgy", "grunge", "punk", "streetwear"],
    "relaxed": [
        "casual", "coastal_chic", "coastal_grandma", "cozy", "everyday",
        "relaxed"
    ],
    "retro": [
        "bold", "classic", "geometric", "retro", "vintage",
        "y2k"
    ],
    "romantic": [
        "bohemian", "boho", "coastal_chic", "coastal_grandma", "cottagecore",
        "eclectic", "elegant", "romantic", "summer"
    ],
    "semi-formal": ["formal", "semi-formal"],
    "simple": ["basic", "clean", "minimalist", "simple"],
    "sleek": [
        "classic", "contemporary", "minimalist", "modern", "polished",
        "sleek"
    ],
    "smart_casual": [
        "business", "business_casual", "casual", "classic", "professional",
        "smart_casual"
    ],
    "sophisticated": ["classic", "elegant", "formal", "old_money", "sophisticated"],
    "sporty": ["active", "athleisure", "athletic", "sporty", "workout"],
    "statement": [
        "bold", "classic", "edgy", "fashion_forward", "modern",
        "statement"
    ],
    "streetwear": [
        "alternative", "bold", "casual", "casual_cool", "edgy",
        "grunge", "punk", "streetwear", "trendy", "urban",
        "y2k"
    ],
    "summer": ["bohemian", "casual", "coastal_chic", "romantic", "summer"],
    "techwear": ["athleisure", "athletic", "modern", "techwear", "urban"],
    "textured": ["bohemian", "casual", "classic", "modern", "textured"],
    "timeless": ["classic", "minimalist", "old_money", "timeless", "vintage"],
    "traditional": [
        "academic", "classic", "dark_academia", "old_money", "preppy",
        "traditional", "vintage"
    ],
    "trendy": ["modern", "streetwear", "trendy", "y2k"],
    "unisex": [
        "androgynous", "classic", "gender_neutral", "minimalist", "modern",
        "unisex"
    ],
    "urban": ["edgy", "modern", "streetwear", "techwear", "urban"],
    "vintage": [
        "classic", "cottagecore", "dark_academia", "old_money", "retro",
        "timeless", "traditional", "vintage"
    ],
    "winter": ["classic", "cozy", "dark_academia", "minimalist", "winter"],
    "workout": ["active", "athleisure", "athletic", "sporty", "workout"],
    "y2k": ["edgy", "retro", "streetwear", "trendy", "y2k"],
}


def normalize_style(style: str) -> str:
    """Normalizes a style string to lowercase for consistent matching"""
    return style.strip().lower()


def normalize_styles(styles: List[str]) -> List[str]:
    """Normalizes a list of style strings"""
    return [normalize_style(style) for style in styles if style and style.strip()]


def get_compatible_styles(requested_style: str) -> List[str]:
    """Gets compatible styles for a given style"""
    normalized_style = normalize_style(requested_style)
    return STYLE_COMPATIBILITY.get(normalized_style, [])


def are_styles_compatible(style1: str, style2: str) -> bool:
    """Checks if two styles are compatible"""
    normalized_style1 = normalize_style(style1)
    normalized_style2 = normalize_style(style2)
    
    # Direct match
    if normalized_style1 == normalized_style2:
        return True
    
    # Check if style2 is in style1's compatibility list
    compatible_styles = get_compatible_styles(normalized_style1)
    return normalized_style2 in compatible_styles


def style_matches(requested_style: Optional[str], item_styles: List[str]) -> bool:
    """Checks if a requested style matches any of the item's styles"""
    if not requested_style:
        return True
    if not item_styles or len(item_styles) == 0:
        return True
    
    normalized_requested = normalize_style(requested_style)
    normalized_item_styles = normalize_styles(item_styles)
    
    # Direct match
    if normalized_requested in normalized_item_styles:
        return True
    
    # Check compatibility matrix
    compatible_styles = get_compatible_styles(normalized_requested)
    return any(item_style in compatible_styles for item_style in normalized_item_styles)


def get_all_styles() -> List[str]:
    """Gets all available styles in the compatibility matrix"""
    return list(STYLE_COMPATIBILITY.keys())


def export_normalized_style_matrix() -> Dict[str, List[str]]:
    """Exports the style compatibility matrix in a normalized format"""
    normalized = {}
    
    for key, values in STYLE_COMPATIBILITY.items():
        normalized_key = normalize_style(key)
        normalized_values = normalize_styles(values)
        normalized[normalized_key] = normalized_values
    
    return normalized


def validate_style_matrix() -> Dict[str, any]:
    """Validates that all styles in the matrix are properly normalized"""
    errors = []
    
    for key, values in STYLE_COMPATIBILITY.items():
        # Check if key is lowercase
        if key != key.lower():
            errors.append(f"Key '{key}' is not lowercase")
        
        # Check if values are lowercase
        for value in values:
            if value != value.lower():
                errors.append(f"Value '{value}' in key '{key}' is not lowercase")
        
        # Check if key is in its own compatibility list
        if key not in values:
            errors.append(f"Key '{key}' is not in its own compatibility list")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }
