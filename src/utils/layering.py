from typing import Dict, List, Optional, Tuple
from ..custom_types.wardrobe import ClothingType, CoreCategory, LayerLevel, WarmthFactor

# Enhanced color compatibility for different skin tones
SKIN_TONE_COLOR_COMPATIBILITY: Dict[str, Dict[str, List[str]]] = {
    'warm': {
        'flattering_colors': ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red', 'orange', 'yellow', 'brown'],
        'avoid_colors': ['cool_blue', 'silver', 'cool_pink', 'purple'],
        'neutral_colors': ['cream', 'beige', 'warm_white', 'camel', 'tan']
    },
    'cool': {
        'flattering_colors': ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald', 'teal', 'navy'],
        'avoid_colors': ['orange', 'yellow', 'warm_red', 'gold'],
        'neutral_colors': ['white', 'cool_gray', 'navy', 'charcoal']
    },
    'neutral': {
        'flattering_colors': ['navy', 'gray', 'white', 'black', 'beige', 'mauve', 'rose', 'sage'],
        'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
        'neutral_colors': ['white', 'black', 'gray', 'beige', 'navy']
    },
    'olive': {
        'flattering_colors': ['olive', 'sage', 'mauve', 'rose', 'camel', 'brown', 'cream'],
        'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
        'neutral_colors': ['cream', 'beige', 'warm_white', 'camel', 'tan']
    },
    'deep': {
        'flattering_colors': ['deep_red', 'purple', 'emerald', 'navy', 'gold', 'cream', 'white'],
        'avoid_colors': ['pastel_pink', 'light_yellow', 'mint'],
        'neutral_colors': ['white', 'cream', 'beige', 'navy', 'charcoal']
    },
    'medium': {
        'flattering_colors': ['blue', 'green', 'purple', 'pink', 'coral', 'navy', 'gray'],
        'avoid_colors': ['neon_colors', 'very_pale_pastels'],
        'neutral_colors': ['white', 'black', 'gray', 'beige', 'navy']
    },
    'fair': {
        'flattering_colors': ['navy', 'gray', 'rose', 'sage', 'cream', 'soft_pink'],
        'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
        'neutral_colors': ['white', 'cream', 'beige', 'navy', 'charcoal']
    }
}

# Body type layering recommendations
BODY_TYPE_LAYERING_RECOMMENDATIONS: Dict[str, Dict[str, List[str]]] = {
    'hourglass': {
        'flattering_layers': ['fitted_tops', 'belted_waist', 'structured_jackets', 'wrap_styles'],
        'avoid_layers': ['boxy_shapes', 'oversized_tops', 'baggy_layers'],
        'layer_priorities': ['define_waist', 'balance_proportions', 'show_curves']
    },
    'pear': {
        'flattering_layers': ['fitted_tops', 'structured_jackets', 'longer_tops', 'dark_bottoms'],
        'avoid_layers': ['short_tops', 'light_bottoms', 'tight_bottoms'],
        'layer_priorities': ['draw_attention_up', 'balance_lower_body', 'create_length']
    },
    'apple': {
        'flattering_layers': ['longer_tops', 'structured_jackets', 'dark_colors', 'v_necks'],
        'avoid_layers': ['crop_tops', 'tight_tops', 'short_jackets'],
        'layer_priorities': ['create_length', 'define_waist', 'draw_attention_down']
    },
    'rectangle': {
        'flattering_layers': ['layered_looks', 'belts', 'structured_pieces', 'textured_layers'],
        'avoid_layers': ['boxy_shapes', 'single_layer_looks'],
        'layer_priorities': ['create_curves', 'add_dimension', 'define_waist']
    },
    'inverted_triangle': {
        'flattering_layers': ['darker_tops', 'lighter_bottoms', 'v_necks', 'longer_tops'],
        'avoid_layers': ['wide_shoulders', 'bright_tops', 'short_jackets'],
        'layer_priorities': ['balance_shoulders', 'draw_attention_down', 'create_waist']
    },
    'athletic': {
        'flattering_layers': ['fitted_pieces', 'structured_layers', 'textured_fabrics', 'belts'],
        'avoid_layers': ['baggy_layers', 'oversized_pieces'],
        'layer_priorities': ['create_curves', 'add_dimension', 'define_shape']
    },
    'curvy': {
        'flattering_layers': ['fitted_tops', 'structured_jackets', 'wrap_styles', 'belted_waist'],
        'avoid_layers': ['boxy_shapes', 'oversized_pieces', 'baggy_layers'],
        'layer_priorities': ['define_waist', 'show_curves', 'balance_proportions']
    }
}

# Style preference layering patterns
STYLE_PREFERENCE_LAYERING: Dict[str, Dict[str, List[str]]] = {
    'minimalist': {
        'layer_approach': ['clean_lines', 'monochromatic', 'simple_layers', 'structured_pieces'],
        'preferred_layers': ['blazer', 'sweater', 'structured_jacket'],
        'avoid_layers': ['busy_patterns', 'multiple_accessories', 'complex_layering']
    },
    'bohemian': {
        'layer_approach': ['flowy_layers', 'textured_fabrics', 'mixed_patterns', 'natural_materials'],
        'preferred_layers': ['cardigan', 'vest', 'flowy_jacket', 'scarf'],
        'avoid_layers': ['structured_blazers', 'formal_coats']
    },
    'streetwear': {
        'layer_approach': ['oversized_layers', 'sporty_pieces', 'mixed_styles', 'bold_statements'],
        'preferred_layers': ['hoodie', 'oversized_jacket', 'vest', 'sports_jacket'],
        'avoid_layers': ['formal_blazers', 'structured_coats']
    },
    'classic': {
        'layer_approach': ['timeless_layers', 'structured_pieces', 'quality_fabrics', 'refined_looks'],
        'preferred_layers': ['blazer', 'structured_jacket', 'cardigan', 'coat'],
        'avoid_layers': ['trendy_pieces', 'oversized_layers', 'casual_layers']
    },
    'romantic': {
        'layer_approach': ['soft_layers', 'flowy_fabrics', 'feminine_details', 'delicate_layers'],
        'preferred_layers': ['cardigan', 'flowy_jacket', 'scarf', 'vest'],
        'avoid_layers': ['structured_blazers', 'sporty_jackets']
    },
    'edgy': {
        'layer_approach': ['bold_layers', 'contrasting_pieces', 'mixed_materials', 'statement_layers'],
        'preferred_layers': ['leather_jacket', 'structured_blazer', 'vest', 'bold_jacket'],
        'avoid_layers': ['soft_layers', 'delicate_pieces']
    },
    'casual': {
        'layer_approach': ['comfortable_layers', 'easy_pieces', 'practical_layers', 'relaxed_fits'],
        'preferred_layers': ['hoodie', 'cardigan', 'casual_jacket', 'vest'],
        'avoid_layers': ['formal_blazers', 'structured_coats']
    },
    'formal': {
        'layer_approach': ['structured_layers', 'quality_fabrics', 'refined_details', 'professional_looks'],
        'preferred_layers': ['blazer', 'structured_jacket', 'coat', 'vest'],
        'avoid_layers': ['casual_layers', 'sporty_pieces']
    }
}

# Core category mapping for layering logic
CORE_CATEGORY_MAPPING: Dict[ClothingType, CoreCategory] = {
    # Tops
    ClothingType.SHIRT: CoreCategory.TOP,
    ClothingType.DRESS_SHIRT: CoreCategory.TOP,
    ClothingType.T_SHIRT: CoreCategory.TOP,
    ClothingType.BLOUSE: CoreCategory.TOP,
    ClothingType.TANK_TOP: CoreCategory.TOP,
    ClothingType.CROP_TOP: CoreCategory.TOP,
    ClothingType.POLO: CoreCategory.TOP,
    ClothingType.SWEATER: CoreCategory.TOP,
    ClothingType.HOODIE: CoreCategory.TOP,
    ClothingType.CARDIGAN: CoreCategory.TOP,
    
    # Bottoms
    ClothingType.PANTS: CoreCategory.BOTTOM,
    ClothingType.SHORTS: CoreCategory.BOTTOM,
    ClothingType.JEANS: CoreCategory.BOTTOM,
    ClothingType.CHINOS: CoreCategory.BOTTOM,
    ClothingType.SLACKS: CoreCategory.BOTTOM,
    ClothingType.JOGGERS: CoreCategory.BOTTOM,
    ClothingType.SWEATPANTS: CoreCategory.BOTTOM,
    ClothingType.SKIRT: CoreCategory.BOTTOM,
    ClothingType.MINI_SKIRT: CoreCategory.BOTTOM,
    ClothingType.MIDI_SKIRT: CoreCategory.BOTTOM,
    ClothingType.MAXI_SKIRT: CoreCategory.BOTTOM,
    ClothingType.PENCIL_SKIRT: CoreCategory.BOTTOM,
    
    # Dresses
    ClothingType.DRESS: CoreCategory.DRESS,
    ClothingType.SUNDRESS: CoreCategory.DRESS,
    ClothingType.COCKTAIL_DRESS: CoreCategory.DRESS,
    ClothingType.MAXI_DRESS: CoreCategory.DRESS,
    ClothingType.MINI_DRESS: CoreCategory.DRESS,
    
    # Outerwear
    ClothingType.JACKET: CoreCategory.OUTERWEAR,
    ClothingType.BLAZER: CoreCategory.OUTERWEAR,
    ClothingType.COAT: CoreCategory.OUTERWEAR,
    ClothingType.VEST: CoreCategory.OUTERWEAR,
    
    # Shoes
    ClothingType.SHOES: CoreCategory.SHOES,
    ClothingType.DRESS_SHOES: CoreCategory.SHOES,
    ClothingType.LOAFERS: CoreCategory.SHOES,
    ClothingType.SNEAKERS: CoreCategory.SHOES,
    ClothingType.BOOTS: CoreCategory.SHOES,
    ClothingType.SANDALS: CoreCategory.SHOES,
    ClothingType.HEELS: CoreCategory.SHOES,
    ClothingType.FLATS: CoreCategory.SHOES,
    
    # Accessories
    ClothingType.ACCESSORY: CoreCategory.ACCESSORY,
    ClothingType.HAT: CoreCategory.ACCESSORY,
    ClothingType.SCARF: CoreCategory.ACCESSORY,
    ClothingType.BELT: CoreCategory.ACCESSORY,
    ClothingType.JEWELRY: CoreCategory.ACCESSORY,
    ClothingType.BAG: CoreCategory.ACCESSORY,
    ClothingType.WATCH: CoreCategory.ACCESSORY,
    
    # Other
    ClothingType.OTHER: CoreCategory.ACCESSORY
}

# Layer level mapping for layering logic
LAYER_LEVEL_MAPPING: Dict[ClothingType, LayerLevel] = {
    # Base/Inner layers
    ClothingType.T_SHIRT: LayerLevel.BASE,
    ClothingType.TANK_TOP: LayerLevel.BASE,
    ClothingType.CROP_TOP: LayerLevel.BASE,
    
    # Inner layers
    ClothingType.SHIRT: LayerLevel.INNER,
    ClothingType.DRESS_SHIRT: LayerLevel.INNER,
    ClothingType.BLOUSE: LayerLevel.INNER,
    ClothingType.POLO: LayerLevel.INNER,
    
    # Middle layers
    ClothingType.SWEATER: LayerLevel.MIDDLE,
    ClothingType.HOODIE: LayerLevel.MIDDLE,
    ClothingType.CARDIGAN: LayerLevel.MIDDLE,
    ClothingType.VEST: LayerLevel.MIDDLE,
    
    # Outer layers
    ClothingType.JACKET: LayerLevel.OUTER,
    ClothingType.BLAZER: LayerLevel.OUTER,
    ClothingType.COAT: LayerLevel.OUTER,
    
    # Non-layering items
    ClothingType.PANTS: LayerLevel.BASE,
    ClothingType.SHORTS: LayerLevel.BASE,
    ClothingType.JEANS: LayerLevel.BASE,
    ClothingType.CHINOS: LayerLevel.BASE,
    ClothingType.SLACKS: LayerLevel.BASE,
    ClothingType.JOGGERS: LayerLevel.BASE,
    ClothingType.SWEATPANTS: LayerLevel.BASE,
    ClothingType.SKIRT: LayerLevel.BASE,
    ClothingType.MINI_SKIRT: LayerLevel.BASE,
    ClothingType.MIDI_SKIRT: LayerLevel.BASE,
    ClothingType.MAXI_SKIRT: LayerLevel.BASE,
    ClothingType.PENCIL_SKIRT: LayerLevel.BASE,
    ClothingType.DRESS: LayerLevel.BASE,
    ClothingType.SUNDRESS: LayerLevel.BASE,
    ClothingType.COCKTAIL_DRESS: LayerLevel.BASE,
    ClothingType.MAXI_DRESS: LayerLevel.BASE,
    ClothingType.MINI_DRESS: LayerLevel.BASE,
    ClothingType.SHOES: LayerLevel.BASE,
    ClothingType.DRESS_SHOES: LayerLevel.BASE,
    ClothingType.LOAFERS: LayerLevel.BASE,
    ClothingType.SNEAKERS: LayerLevel.BASE,
    ClothingType.BOOTS: LayerLevel.BASE,
    ClothingType.SANDALS: LayerLevel.BASE,
    ClothingType.HEELS: LayerLevel.BASE,
    ClothingType.FLATS: LayerLevel.BASE,
    ClothingType.ACCESSORY: LayerLevel.BASE,
    ClothingType.HAT: LayerLevel.BASE,
    ClothingType.SCARF: LayerLevel.BASE,
    ClothingType.BELT: LayerLevel.BASE,
    ClothingType.JEWELRY: LayerLevel.BASE,
    ClothingType.BAG: LayerLevel.BASE,
    ClothingType.WATCH: LayerLevel.BASE,
    ClothingType.OTHER: LayerLevel.BASE
}

# Warmth factor mapping for temperature-based layering
WARMTH_FACTOR_MAPPING: Dict[ClothingType, WarmthFactor] = {
    # Light items
    ClothingType.T_SHIRT: WarmthFactor.LIGHT,
    ClothingType.TANK_TOP: WarmthFactor.LIGHT,
    ClothingType.CROP_TOP: WarmthFactor.LIGHT,
    ClothingType.BLOUSE: WarmthFactor.LIGHT,
    ClothingType.POLO: WarmthFactor.LIGHT,
    ClothingType.SHORTS: WarmthFactor.LIGHT,
    ClothingType.MINI_SKIRT: WarmthFactor.LIGHT,
    ClothingType.SUNDRESS: WarmthFactor.LIGHT,
    ClothingType.MINI_DRESS: WarmthFactor.LIGHT,
    ClothingType.SANDALS: WarmthFactor.LIGHT,
    ClothingType.FLATS: WarmthFactor.LIGHT,
    ClothingType.ACCESSORY: WarmthFactor.LIGHT,
    ClothingType.HAT: WarmthFactor.LIGHT,
    ClothingType.BELT: WarmthFactor.LIGHT,
    ClothingType.JEWELRY: WarmthFactor.LIGHT,
    ClothingType.WATCH: WarmthFactor.LIGHT,
    
    # Medium items
    ClothingType.SHIRT: WarmthFactor.MEDIUM,
    ClothingType.DRESS_SHIRT: WarmthFactor.MEDIUM,
    ClothingType.PANTS: WarmthFactor.MEDIUM,
    ClothingType.JEANS: WarmthFactor.MEDIUM,
    ClothingType.CHINOS: WarmthFactor.MEDIUM,
    ClothingType.SLACKS: WarmthFactor.MEDIUM,
    ClothingType.JOGGERS: WarmthFactor.MEDIUM,
    ClothingType.SWEATPANTS: WarmthFactor.MEDIUM,
    ClothingType.SKIRT: WarmthFactor.MEDIUM,
    ClothingType.MIDI_SKIRT: WarmthFactor.MEDIUM,
    ClothingType.MAXI_SKIRT: WarmthFactor.MEDIUM,
    ClothingType.PENCIL_SKIRT: WarmthFactor.MEDIUM,
    ClothingType.DRESS: WarmthFactor.MEDIUM,
    ClothingType.COCKTAIL_DRESS: WarmthFactor.MEDIUM,
    ClothingType.MAXI_DRESS: WarmthFactor.MEDIUM,
    ClothingType.SWEATER: WarmthFactor.MEDIUM,
    ClothingType.HOODIE: WarmthFactor.MEDIUM,
    ClothingType.CARDIGAN: WarmthFactor.MEDIUM,
    ClothingType.VEST: WarmthFactor.MEDIUM,
    ClothingType.SHOES: WarmthFactor.MEDIUM,
    ClothingType.DRESS_SHOES: WarmthFactor.MEDIUM,
    ClothingType.LOAFERS: WarmthFactor.MEDIUM,
    ClothingType.SNEAKERS: WarmthFactor.MEDIUM,
    ClothingType.BOOTS: WarmthFactor.MEDIUM,
    ClothingType.HEELS: WarmthFactor.MEDIUM,
    ClothingType.SCARF: WarmthFactor.MEDIUM,
    ClothingType.BAG: WarmthFactor.MEDIUM,
    
    # Heavy items
    ClothingType.JACKET: WarmthFactor.HEAVY,
    ClothingType.BLAZER: WarmthFactor.HEAVY,
    ClothingType.COAT: WarmthFactor.HEAVY,
    ClothingType.OTHER: WarmthFactor.MEDIUM
}

# Can layer mapping - which items can be layered
CAN_LAYER_MAPPING: Dict[ClothingType, bool] = {
    # Items that can be layered
    ClothingType.SHIRT: True,
    ClothingType.DRESS_SHIRT: True,
    ClothingType.T_SHIRT: True,
    ClothingType.BLOUSE: True,
    ClothingType.TANK_TOP: True,
    ClothingType.CROP_TOP: True,
    ClothingType.POLO: True,
    ClothingType.SWEATER: True,
    ClothingType.HOODIE: True,
    ClothingType.CARDIGAN: True,
    ClothingType.JACKET: True,
    ClothingType.BLAZER: True,
    ClothingType.COAT: True,
    ClothingType.VEST: True,
    ClothingType.SCARF: True,
    
    # Items that cannot be layered
    ClothingType.PANTS: False,
    ClothingType.SHORTS: False,
    ClothingType.JEANS: False,
    ClothingType.CHINOS: False,
    ClothingType.SLACKS: False,
    ClothingType.JOGGERS: False,
    ClothingType.SWEATPANTS: False,
    ClothingType.SKIRT: False,
    ClothingType.MINI_SKIRT: False,
    ClothingType.MIDI_SKIRT: False,
    ClothingType.MAXI_SKIRT: False,
    ClothingType.PENCIL_SKIRT: False,
    ClothingType.DRESS: False,
    ClothingType.SUNDRESS: False,
    ClothingType.COCKTAIL_DRESS: False,
    ClothingType.MAXI_DRESS: False,
    ClothingType.MINI_DRESS: False,
    ClothingType.SHOES: False,
    ClothingType.DRESS_SHOES: False,
    ClothingType.LOAFERS: False,
    ClothingType.SNEAKERS: False,
    ClothingType.BOOTS: False,
    ClothingType.SANDALS: False,
    ClothingType.HEELS: False,
    ClothingType.FLATS: False,
    ClothingType.ACCESSORY: False,
    ClothingType.HAT: False,
    ClothingType.BELT: False,
    ClothingType.JEWELRY: False,
    ClothingType.BAG: False,
    ClothingType.WATCH: False,
    ClothingType.OTHER: False
}

# Maximum layers mapping - how many layers an item can support
MAX_LAYERS_MAPPING: Dict[ClothingType, int] = {
    # Items that can support multiple layers
    ClothingType.JACKET: 4,
    ClothingType.COAT: 4,
    ClothingType.BLAZER: 3,
    ClothingType.CARDIGAN: 3,
    ClothingType.VEST: 3,
    ClothingType.SWEATER: 2,
    ClothingType.HOODIE: 2,
    ClothingType.SHIRT: 2,
    ClothingType.DRESS_SHIRT: 2,
    ClothingType.BLOUSE: 2,
    ClothingType.POLO: 2,
    ClothingType.T_SHIRT: 1,
    ClothingType.TANK_TOP: 1,
    ClothingType.CROP_TOP: 1,
    
    # Non-layering items
    ClothingType.PANTS: 1,
    ClothingType.SHORTS: 1,
    ClothingType.JEANS: 1,
    ClothingType.CHINOS: 1,
    ClothingType.SLACKS: 1,
    ClothingType.JOGGERS: 1,
    ClothingType.SWEATPANTS: 1,
    ClothingType.SKIRT: 1,
    ClothingType.MINI_SKIRT: 1,
    ClothingType.MIDI_SKIRT: 1,
    ClothingType.MAXI_SKIRT: 1,
    ClothingType.PENCIL_SKIRT: 1,
    ClothingType.DRESS: 1,
    ClothingType.SUNDRESS: 1,
    ClothingType.COCKTAIL_DRESS: 1,
    ClothingType.MAXI_DRESS: 1,
    ClothingType.MINI_DRESS: 1,
    ClothingType.SHOES: 1,
    ClothingType.DRESS_SHOES: 1,
    ClothingType.LOAFERS: 1,
    ClothingType.SNEAKERS: 1,
    ClothingType.BOOTS: 1,
    ClothingType.SANDALS: 1,
    ClothingType.HEELS: 1,
    ClothingType.FLATS: 1,
    ClothingType.ACCESSORY: 1,
    ClothingType.HAT: 1,
    ClothingType.SCARF: 1,
    ClothingType.BELT: 1,
    ClothingType.JEWELRY: 1,
    ClothingType.BAG: 1,
    ClothingType.WATCH: 1,
    ClothingType.OTHER: 1
}

# Utility functions for layering logic
def get_core_category(clothing_type: ClothingType) -> CoreCategory:
    """Get the core category for a clothing type."""
    return CORE_CATEGORY_MAPPING.get(clothing_type, CoreCategory.ACCESSORY)

def get_layer_level(clothing_type: ClothingType) -> LayerLevel:
    """Get the layer level for a clothing type."""
    return LAYER_LEVEL_MAPPING.get(clothing_type, LayerLevel.BASE)

def get_warmth_factor(clothing_type: ClothingType) -> WarmthFactor:
    """Get the warmth factor for a clothing type."""
    return WARMTH_FACTOR_MAPPING.get(clothing_type, WarmthFactor.MEDIUM)

def can_layer(clothing_type: ClothingType) -> bool:
    """Check if a clothing type can be layered."""
    return CAN_LAYER_MAPPING.get(clothing_type, False)

def get_max_layers(clothing_type: ClothingType) -> int:
    """Get the maximum number of layers for a clothing type."""
    return MAX_LAYERS_MAPPING.get(clothing_type, 1)

# Temperature-based layering rules
def get_layering_rule(temperature: float) -> Dict:
    """Get the appropriate layering rule based on temperature."""
    if temperature < 32:
        return {
            "min_layers": 3,
            "max_layers": 5,
            "required_categories": [CoreCategory.TOP, CoreCategory.OUTERWEAR],
            "preferred_warmth": [WarmthFactor.MEDIUM, WarmthFactor.HEAVY],
            "notes": "Heavy layering required with thermal base layer"
        }
    elif temperature < 50:
        return {
            "min_layers": 2,
            "max_layers": 4,
            "required_categories": [CoreCategory.TOP],
            "preferred_warmth": [WarmthFactor.MEDIUM, WarmthFactor.HEAVY],
            "notes": "Medium layering with warm materials"
        }
    elif temperature < 65:
        return {
            "min_layers": 1,
            "max_layers": 3,
            "required_categories": [CoreCategory.TOP],
            "preferred_warmth": [WarmthFactor.LIGHT, WarmthFactor.MEDIUM],
            "notes": "Light layering with breathable materials"
        }
    elif temperature < 75:
        return {
            "min_layers": 1,
            "max_layers": 2,
            "required_categories": [CoreCategory.TOP],
            "preferred_warmth": [WarmthFactor.LIGHT, WarmthFactor.MEDIUM],
            "notes": "Single layer with light materials"
        }
    elif temperature < 85:
        return {
            "min_layers": 1,
            "max_layers": 2,
            "required_categories": [CoreCategory.TOP],
            "preferred_warmth": [WarmthFactor.LIGHT],
            "notes": "Light, breathable single layer"
        }
    else:
        return {
            "min_layers": 1,
            "max_layers": 1,
            "required_categories": [CoreCategory.TOP],
            "preferred_warmth": [WarmthFactor.LIGHT],
            "notes": "Minimal, breathable clothing"
        }

# Validate layering compatibility
def validate_layering_compatibility(
    items: List[Dict],
    temperature: float
) -> Dict:
    """Validate layering compatibility for a set of items."""
    rule = get_layering_rule(temperature)
    errors = []
    warnings = []
    
    # Count layers by category
    layers_by_category = {}
    layers_by_level = {}
    
    for item in items:
        item_type = ClothingType(item.get("type", "other"))
        category = get_core_category(item_type)
        layer_level = get_layer_level(item_type)
        warmth_factor = get_warmth_factor(item_type)
        
        layers_by_category[category] = layers_by_category.get(category, 0) + 1
        layers_by_level[layer_level] = layers_by_level.get(layer_level, 0) + 1
        
        # Check warmth appropriateness
        if warmth_factor not in rule["preferred_warmth"]:
            warnings.append(f"{item_type.value} may be too {warmth_factor.value} for {temperature}°F weather")
    
    # Check minimum layers
    total_layers = sum(1 for item in items if can_layer(ClothingType(item.get("type", "other"))))
    if total_layers < rule["min_layers"]:
        errors.append(f"Insufficient layering for {temperature}°F weather. Need at least {rule['min_layers']} layers.")
    
    # Check maximum layers
    if total_layers > rule["max_layers"]:
        warnings.append(f"Too many layers for {temperature}°F weather. Consider removing some items.")
    
    # Check required categories
    for category in rule["required_categories"]:
        if category not in layers_by_category:
            errors.append(f"Missing required category: {category.value}")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0
    }

# Get layering suggestions
def get_layering_suggestions(
    items: List[Dict],
    temperature: float
) -> List[str]:
    """Get layering suggestions for a set of items."""
    rule = get_layering_rule(temperature)
    suggestions = []
    
    current_layers = sum(1 for item in items if can_layer(ClothingType(item.get("type", "other"))))
    current_categories = set(get_core_category(ClothingType(item.get("type", "other"))) for item in items)
    
    if current_layers < rule["min_layers"]:
        suggestions.append(f"Add {rule['min_layers'] - current_layers} more layer(s) for {temperature}°F weather")
    
    for category in rule["required_categories"]:
        if category not in current_categories:
            suggestions.append(f"Add a {category.value} item for complete outfit")
    
    return suggestions

def get_skin_tone_color_recommendations(skin_tone: str) -> Dict[str, List[str]]:
    """Get color recommendations based on skin tone."""
    return SKIN_TONE_COLOR_COMPATIBILITY.get(skin_tone.lower(), {
        'flattering_colors': [],
        'avoid_colors': [],
        'neutral_colors': []
    })

def get_body_type_layering_recommendations(body_type: str) -> Dict[str, List[str]]:
    """Get layering recommendations based on body type."""
    return BODY_TYPE_LAYERING_RECOMMENDATIONS.get(body_type.lower(), {
        'flattering_layers': [],
        'avoid_layers': [],
        'layer_priorities': []
    })

def get_style_preference_layering(style_preference: str) -> Dict[str, List[str]]:
    """Get layering approach based on style preference."""
    return STYLE_PREFERENCE_LAYERING.get(style_preference.lower(), {
        'layer_approach': [],
        'preferred_layers': [],
        'avoid_layers': []
    })

def validate_color_skin_tone_compatibility(item_color: str, skin_tone: str) -> Dict[str, any]:
    """Validate if an item's color is compatible with the user's skin tone."""
    if not skin_tone or not item_color:
        return {'compatible': True, 'score': 0.5, 'reason': 'Missing skin tone or color information'}
    
    recommendations = get_skin_tone_color_recommendations(skin_tone)
    color_lower = item_color.lower()
    
    # Check if color is flattering
    if color_lower in recommendations['flattering_colors']:
        return {'compatible': True, 'score': 1.0, 'reason': f'{item_color} is flattering for {skin_tone} skin tone'}
    
    # Check if color should be avoided
    if color_lower in recommendations['avoid_colors']:
        return {'compatible': False, 'score': 0.0, 'reason': f'{item_color} may not be ideal for {skin_tone} skin tone'}
    
    # Check if color is neutral
    if color_lower in recommendations['neutral_colors']:
        return {'compatible': True, 'score': 0.8, 'reason': f'{item_color} is a neutral color for {skin_tone} skin tone'}
    
    # Default to moderate compatibility
    return {'compatible': True, 'score': 0.6, 'reason': f'{item_color} has moderate compatibility with {skin_tone} skin tone'}

def validate_body_type_layering_compatibility(items: List[Dict], body_type: str) -> Dict[str, any]:
    """Validate if layering approach is compatible with body type."""
    if not body_type:
        return {'compatible': True, 'score': 0.5, 'warnings': [], 'suggestions': []}
    
    recommendations = get_body_type_layering_recommendations(body_type)
    warnings = []
    suggestions = []
    score = 1.0
    
    # Analyze the layering approach
    top_items = [item for item in items if get_core_category(item.get('type', '')) == CoreCategory.TOP]
    outerwear_items = [item for item in items if get_core_category(item.get('type', '')) == CoreCategory.OUTERWEAR]
    
    # Check for body type specific recommendations
    if body_type.lower() == 'pear':
        if len(top_items) == 0:
            warnings.append("Pear body types benefit from fitted tops to balance proportions")
            score -= 0.2
        if len(outerwear_items) == 0:
            suggestions.append("Consider adding a structured jacket to draw attention upward")
    
    elif body_type.lower() == 'apple':
        if any('crop' in item.get('type', '').lower() for item in top_items):
            warnings.append("Crop tops may not be ideal for apple body types")
            score -= 0.3
        if len(outerwear_items) == 0:
            suggestions.append("Consider adding a longer jacket to create length")
    
    elif body_type.lower() == 'rectangle':
        if len(items) < 3:
            suggestions.append("Rectangle body types benefit from layered looks to create curves")
            score -= 0.1
    
    elif body_type.lower() == 'hourglass':
        if len(top_items) == 0:
            warnings.append("Hourglass body types benefit from fitted tops to show curves")
            score -= 0.2
    
    return {
        'compatible': score > 0.5,
        'score': max(0.0, score),
        'warnings': warnings,
        'suggestions': suggestions
    }

def validate_style_preference_compatibility(items: List[Dict], style_preferences: List[str]) -> Dict[str, any]:
    """Validate if layering approach matches style preferences."""
    if not style_preferences:
        return {'compatible': True, 'score': 0.5, 'warnings': [], 'suggestions': []}
    
    warnings = []
    suggestions = []
    score = 1.0
    
    for style in style_preferences:
        style_rec = get_style_preference_layering(style)
        
        # Check if items match preferred layers
        item_types = [item.get('type', '').lower() for item in items]
        preferred_layers = [layer.lower() for layer in style_rec['preferred_layers']]
        
        # Calculate how many preferred layers are present
        matching_layers = sum(1 for layer in preferred_layers if any(layer in item_type for item_type in item_types))
        
        if matching_layers == 0:
            warnings.append(f"No preferred {style} layering pieces found")
            score -= 0.2
        elif matching_layers < 2:
            suggestions.append(f"Consider adding more {style} layering pieces")
            score -= 0.1
    
    return {
        'compatible': score > 0.5,
        'score': max(0.0, score),
        'warnings': warnings,
        'suggestions': suggestions
    }

def get_personalized_layering_suggestions(
    items: List[Dict],
    temperature: float,
    skin_tone: Optional[str] = None,
    body_type: Optional[str] = None,
    style_preferences: Optional[List[str]] = None
) -> Dict[str, any]:
    """Get personalized layering suggestions considering all personal factors."""
    suggestions = []
    warnings = []
    recommendations = []
    
    # Basic temperature-based suggestions
    temp_suggestions = get_layering_suggestions(items, temperature)
    suggestions.extend(temp_suggestions)
    
    # Skin tone color suggestions
    if skin_tone:
        color_rec = get_skin_tone_color_recommendations(skin_tone)
        if color_rec['flattering_colors']:
            recommendations.append(f"Consider colors like {', '.join(color_rec['flattering_colors'][:3])} for your {skin_tone} skin tone")
    
    # Body type suggestions
    if body_type:
        body_rec = get_body_type_layering_recommendations(body_type)
        if body_rec['layer_priorities']:
            recommendations.append(f"For your {body_type} body type, focus on: {', '.join(body_rec['layer_priorities'][:2])}")
    
    # Style preference suggestions
    if style_preferences:
        for style in style_preferences[:2]:  # Limit to top 2 preferences
            style_rec = get_style_preference_layering(style)
            if style_rec['preferred_layers']:
                recommendations.append(f"For {style} style, try: {', '.join(style_rec['preferred_layers'][:2])}")
    
    return {
        'suggestions': suggestions,
        'warnings': warnings,
        'recommendations': recommendations,
        'temperature_based': temp_suggestions,
        'personalized': recommendations
    }

def calculate_personalized_layering_score(
    items: List[Dict],
    temperature: float,
    skin_tone: Optional[str] = None,
    body_type: Optional[str] = None,
    style_preferences: Optional[List[str]] = None
) -> float:
    """Calculate a personalized layering score considering all factors."""
    base_score = 0.5
    
    # Temperature compatibility (30% weight)
    temp_validation = validate_layering_compatibility(items, temperature)
    base_score += temp_validation.get('score', 0.5) * 0.3
    
    # Skin tone compatibility (20% weight)
    if skin_tone:
        color_scores = []
        for item in items:
            color = item.get('color', '')
            if color:
                color_validation = validate_color_skin_tone_compatibility(color, skin_tone)
                color_scores.append(color_validation['score'])
        
        if color_scores:
            avg_color_score = sum(color_scores) / len(color_scores)
            base_score += avg_color_score * 0.2
    
    # Body type compatibility (25% weight)
    if body_type:
        body_validation = validate_body_type_layering_compatibility(items, body_type)
        base_score += body_validation['score'] * 0.25
    
    # Style preference compatibility (25% weight)
    if style_preferences:
        style_validation = validate_style_preference_compatibility(items, style_preferences)
        base_score += style_validation['score'] * 0.25
    
    return min(1.0, max(0.0, base_score))

def get_enhanced_layering_validation(
    items: List[Dict],
    temperature: float,
    user_profile: Optional[Dict] = None
) -> Dict[str, any]:
    """Comprehensive layering validation with personal factors."""
    if not user_profile:
        return validate_layering_compatibility(items, temperature)
    
    skin_tone = getattr(user_profile, 'skinTone', None) or getattr(getattr(user_profile, 'measurements', {}), 'skinTone', None)
    body_type = getattr(user_profile, 'bodyType', None) or getattr(getattr(user_profile, 'measurements', {}), 'bodyType', None)
    style_preferences = getattr(user_profile, 'stylePreferences', [])
    
    # Get all validation results
    temp_validation = validate_layering_compatibility(items, temperature)
    color_validation = validate_color_skin_tone_compatibility('', skin_tone) if skin_tone else {'compatible': True, 'score': 0.5}
    body_validation = validate_body_type_layering_compatibility(items, body_type) if body_type else {'compatible': True, 'score': 0.5}
    style_validation = validate_style_preference_compatibility(items, style_preferences) if style_preferences else {'compatible': True, 'score': 0.5}
    
    # Calculate overall score
    overall_score = calculate_personalized_layering_score(
        items, temperature, skin_tone, body_type, style_preferences
    )
    
    # Combine all suggestions and warnings
    all_suggestions = []
    all_warnings = []
    
    if temp_validation.get('suggestions'):
        all_suggestions.extend(temp_validation['suggestions'])
    
    if body_validation.get('suggestions'):
        all_suggestions.extend(body_validation['suggestions'])
    
    if style_validation.get('suggestions'):
        all_suggestions.extend(style_validation['suggestions'])
    
    if body_validation.get('warnings'):
        all_warnings.extend(body_validation['warnings'])
    
    if style_validation.get('warnings'):
        all_warnings.extend(style_validation['warnings'])
    
    return {
        'is_valid': overall_score > 0.6,
        'overall_score': overall_score,
        'temperature_score': temp_validation.get('score', 0.5),
        'color_score': color_validation.get('score', 0.5),
        'body_type_score': body_validation.get('score', 0.5),
        'style_score': style_validation.get('score', 0.5),
        'suggestions': all_suggestions,
        'warnings': all_warnings,
        'personalized_recommendations': get_personalized_layering_suggestions(
            items, temperature, skin_tone, body_type, style_preferences
        )
    } 