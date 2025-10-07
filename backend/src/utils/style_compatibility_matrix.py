# backend/src/utils/style_compatibility_matrix.py
# Canonical Style Compatibility Matrix for Python backend
# All keys and values are normalized to lowercase for consistent matching

from typing import Dict, List, Optional

# Canonical Style Compatibility Matrix
STYLE_COMPATIBILITY: Dict[str, List[str]] = {
    # Core Professional Styles
    "classic": ["classic", "casual", "smart casual", "business casual", "traditional", "preppy", "minimalist", "balanced"],
    "business": ["business", "business casual", "business_casual", "professional", "smart casual", "smart_casual", "classic", "formal"],
    "business_casual": ["business_casual", "business casual", "business", "smart casual", "smart_casual", "classic", "casual", "preppy"],
    "formal": ["formal", "elegant", "semi-formal", "business", "classic"],
    "professional": ["professional", "business", "business casual", "business_casual", "smart casual", "smart_casual", "classic", "formal"],
    "smart_casual": ["smart_casual", "smart casual", "business_casual", "business casual", "business", "professional", "classic", "casual"],
    
    # Casual & Everyday Styles
    "casual": ["casual", "classic", "streetwear", "athleisure", "relaxed", "everyday", "casual_cool", "business_casual"],
    "casual_cool": ["casual_cool", "casual", "streetwear", "minimalist", "modern"],
    "relaxed": ["relaxed", "casual", "everyday", "coastal_grandma", "coastal_chic"],
    "everyday": ["everyday", "casual", "relaxed", "balanced", "minimalist"],
    
    # Athletic & Active Styles
    "athletic": ["athletic", "sporty", "active", "workout", "athleisure", "techwear"],
    "athleisure": ["athleisure", "athletic", "sporty", "casual", "techwear"],
    "sporty": ["sporty", "athletic", "athleisure", "active", "workout"],
    
    # Street & Urban Styles
    "streetwear": ["streetwear", "urban", "edgy", "trendy", "casual", "grunge"],
    "urban": ["urban", "streetwear", "edgy", "modern", "techwear"],
    "edgy": ["edgy", "streetwear", "grunge", "urban", "avant_garde"],
    "grunge": ["grunge", "edgy", "streetwear", "casual"],
    
    # Vintage & Retro Styles
    "vintage": ["vintage", "retro", "classic", "timeless", "old_money", "dark_academia"],
    "retro": ["retro", "vintage", "y2k", "classic"],
    "timeless": ["timeless", "classic", "vintage", "old_money", "minimalist"],
    
    # Modern & Contemporary Styles
    "modern": ["modern", "contemporary", "trendy", "fashion-forward", "minimalist", "casual_cool"],
    "contemporary": ["contemporary", "modern", "minimalist", "balanced"],
    "trendy": ["trendy", "modern", "streetwear", "y2k"],
    "fashion_forward": ["fashion_forward", "modern", "avant_garde", "artsy"],
    
    # Minimalist & Clean Styles
    "minimalist": ["minimalist", "simple", "clean", "basic", "classic", "modern", "balanced"],
    "simple": ["simple", "minimalist", "clean", "basic"],
    "clean": ["clean", "minimalist", "simple", "modern"],
    "basic": ["basic", "minimalist", "simple", "casual"],
    
    # Bohemian & Artistic Styles
    "bohemian": ["bohemian", "boho", "eclectic", "artistic", "romantic", "cottagecore"],
    "boho": ["boho", "bohemian", "eclectic", "romantic", "coastal_grandma"],
    "eclectic": ["eclectic", "bohemian", "boho", "artsy", "romantic"],
    "artistic": ["artistic", "eclectic", "artsy", "avant_garde", "bohemian"],
    "artsy": ["artsy", "artistic", "avant_garde", "eclectic", "creative"],
    
    # Preppy & Traditional Styles
    "preppy": ["preppy", "classic", "traditional", "polished", "old_money", "business_casual"],
    "traditional": ["traditional", "classic", "preppy", "old_money", "vintage"],
    "polished": ["polished", "preppy", "classic", "formal", "business"],
    
    # Specialized Styles
    "old_money": ["old_money", "preppy", "classic", "traditional", "polished", "vintage"],
    "dark_academia": ["dark_academia", "vintage", "classic", "academic", "traditional"],
    "y2k": ["y2k", "retro", "trendy", "edgy", "streetwear"],
    "techwear": ["techwear", "athletic", "athleisure", "urban", "modern"],
    "androgynous": ["androgynous", "minimalist", "modern", "classic", "balanced"],
    
    # Coastal & Relaxed Styles
    "coastal_grandma": ["coastal_grandma", "coastal_chic", "relaxed", "boho", "romantic"],
    "coastal_chic": ["coastal_chic", "coastal_grandma", "relaxed", "romantic", "casual"],
    
    # Balanced & Versatile Styles
    "balanced": ["balanced", "classic", "minimalist", "modern", "casual", "business_casual"],
    
    # Avant-garde & Experimental Styles
    "avant_garde": ["avant_garde", "artsy", "edgy", "experimental", "fashion_forward"],
    "experimental": ["experimental", "avant_garde", "artsy", "creative"],
    "creative": ["creative", "artsy", "avant_garde", "eclectic"],
    
    # Romantic & Feminine Styles
    "romantic": ["romantic", "bohemian", "boho", "cottagecore", "coastal_grandma", "coastal_chic"],
    "cottagecore": ["cottagecore", "romantic", "bohemian", "vintage", "coastal_grandma"],
    
    # Elegant & Sophisticated Styles
    "elegant": ["elegant", "formal", "classic", "romantic", "sophisticated"],
    "sophisticated": ["sophisticated", "elegant", "classic", "formal", "old_money"],
    
    # Professional & Work Styles (duplicate removed - see line 14)
    
    # Workout & Active Styles
    "workout": ["workout", "athletic", "sporty", "athleisure", "active"],
    "active": ["active", "athletic", "sporty", "workout", "athleisure"],
    
    # Academic & Intellectual Styles
    "academic": ["academic", "dark_academia", "classic", "traditional", "intellectual"],
    "intellectual": ["intellectual", "academic", "classic", "dark_academia", "minimalist"],
    
    # Nautical & Maritime Styles
    "nautical": ["nautical", "preppy", "coastal_chic", "classic", "casual"],
    "maritime": ["maritime", "nautical", "coastal_chic", "preppy"],
    
    # Alternative & Subculture Styles
    "alternative": ["alternative", "grunge", "edgy", "streetwear", "punk"],
    "punk": ["punk", "edgy", "grunge", "alternative", "streetwear"],
    
    # Seasonal & Themed Styles
    "summer": ["summer", "casual", "coastal_chic", "romantic", "bohemian"],
    "winter": ["winter", "classic", "dark_academia", "minimalist", "cozy"],
    "cozy": ["cozy", "winter", "casual", "relaxed", "cottagecore"],
    
    # Gender-neutral & Inclusive Styles
    "unisex": ["unisex", "minimalist", "classic", "modern", "androgynous"],
    "gender_neutral": ["gender_neutral", "unisex", "minimalist", "androgynous", "modern"],
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
