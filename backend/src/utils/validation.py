from typing import Optional, Dict, List, Any, Union
from unidecode import unidecode
import re
from difflib import SequenceMatcher
from ..custom_types.wardrobe import ClothingType, ClothingItem
import time
import json
import traceback
import logging
import uuid

# Set up logging
logger = logging.getLogger(__name__)

# Maximum lengths for strings
MAX_TYPE_LENGTH = 32
MAX_SUBTYPE_LENGTH = 64

# Canonical type mappings with synonyms
TYPE_MAPPINGS: Dict[str, List[str]] = {
    "shirt": [
        "t-shirt", "tee", "tshirt", "tee shirt", "v neck", "v-neck", "vneck", 
        "tank top", "polo", "blouse", "button down", "button-down", "button up",
        "button-up", "oxford", "dress shirt", "casual shirt", "formal shirt"
    ],
    "pants": [
        "jeans", "trousers", "slacks", "chinos", "khakis", "leggings", "joggers",
        "cargo pants", "dress pants", "formal pants", "casual pants", "shorts",
        "bermuda shorts", "capri pants", "culottes", "palazzo pants"
    ],
    "dress": [
        "gown", "frock", "sundress", "cocktail dress", "maxi", "mini",
        "evening dress", "formal dress", "casual dress", "party dress",
        "shift dress", "a-line dress", "bodycon dress", "wrap dress"
    ],
    "skirt": [
        "mini skirt", "maxi skirt", "pleated", "a-line", "pencil skirt",
        "midi skirt", "circle skirt", "wrap skirt", "denim skirt", "leather skirt"
    ],
    "jacket": [
        "denim", "blazer", "bomber", "parka", "windbreaker", "coat", "raincoat",
        "leather jacket", "suit jacket", "sports jacket", "cardigan", "sweater jacket",
        "puffer jacket", "down jacket", "fleece jacket", "vest", "waistcoat"
    ],
    "sweater": [
        "sweatshirt", "hoodie", "cardigan", "pullover", "jumper",
        "turtleneck", "mock neck", "crew neck", "v-neck sweater",
        "cable knit", "fisherman sweater", "chunky knit", "cashmere"
    ],
    "shoes": [
        "sneakers", "boots", "loafers", "sandals", "heels", "flats", "pumps",
        "oxfords", "derby", "mules", "espadrilles", "moccasins", "slip-ons",
        "ankle boots", "knee-high boots", "chelsea boots", "running shoes",
        "athletic shoes", "trainers", "stilettos", "wedges", "platforms"
    ],
    "accessory": [
        "bag", "purse", "scarf", "hat", "belt", "jewelry", "watch",
        "sunglasses", "gloves", "mittens", "socks", "tights", "stockings",
        "handbag", "backpack", "tote", "clutch", "necklace", "bracelet",
        "earrings", "ring", "tie", "bow tie", "pocket square", "cufflinks"
    ],
    "other": []
}

# Additional subtype mappings for common variations
SUBTYPE_MAPPINGS: Dict[str, List[str]] = {
    "shirt": [
        "v-neck", "crew neck", "turtle neck", "mock neck", "polo",
        "button-down", "button-up", "oxford", "dress", "casual"
    ],
    "pants": [
        "skinny", "straight", "bootcut", "wide leg", "flared",
        "cargo", "dress", "casual", "formal", "denim", "leather"
    ],
    "dress": [
        "maxi", "mini", "midi", "a-line", "bodycon", "shift",
        "wrap", "cocktail", "evening", "casual", "formal"
    ],
    "skirt": [
        "mini", "maxi", "midi", "a-line", "pencil", "pleated",
        "circle", "wrap", "denim", "leather"
    ],
    "jacket": [
        "denim", "leather", "bomber", "blazer", "parka", "windbreaker",
        "rain", "puffer", "down", "fleece", "vest"
    ],
    "sweater": [
        "v-neck", "crew neck", "turtle neck", "mock neck", "cardigan",
        "pullover", "hoodie", "cable knit", "chunky", "cashmere"
    ],
    "shoes": [
        "sneakers", "boots", "loafers", "sandals", "heels", "flats",
        "pumps", "oxfords", "derby", "mules", "espadrilles"
    ]
}

def normalize_string(input_str: Optional[str]) -> str:
    """Normalize a string by converting to lowercase, removing special characters, etc."""
    if not input_str:
        return ""
    
    # Convert to lowercase and normalize unicode
    normalized = unidecode(input_str.lower().strip())
    
    # Remove special characters but keep spaces and hyphens
    normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
    
    # Collapse multiple spaces and hyphens
    normalized = re.sub(r'[\s-]+', ' ', normalized)
    
    return normalized

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings using SequenceMatcher."""
    return SequenceMatcher(None, str1, str2).ratio()

def find_closest_match(input_str: str, options: List[str], threshold: float = 0.8) -> Optional[str]:
    """Find the closest match from a list of options using string similarity."""
    if not input_str or not options:
        return None
    
    normalized_input = normalize_string(input_str)
    best_match = None
    best_score = threshold
    
    for option in options:
        normalized_option = normalize_string(option)
        score = calculate_similarity(normalized_input, normalized_option)
        
        if score > best_score:
            best_score = score
            best_match = option
    
    return best_match

def normalize_clothing_type(item_type: str, sub_type: Optional[str] = None) -> ClothingType:
    """
    Normalize clothing type with special handling for shorts and shoes.
    """
    if not item_type:
        logger.warning("Empty type string, defaulting to OTHER")
        return ClothingType.OTHER

    # Handle ClothingType enum format (e.g., "ClothingType.SHIRT" -> "shirt")
    if 'clothingtype.' in item_type.lower():
        enum_value = item_type.split('.')[-1].lower()
        # Map enum values to valid ClothingType enum values
        enum_mappings = {
            'shirt': ClothingType.SHIRT,
            'pants': ClothingType.PANTS, 
            'shoes': ClothingType.SHOES,
            'jacket': ClothingType.JACKET,
            'dress': ClothingType.DRESS,
            'sweater': ClothingType.SWEATER,
            'blouse': ClothingType.BLOUSE,
            'hoodie': ClothingType.HOODIE,
            'polo': ClothingType.POLO,
            'jeans': ClothingType.JEANS,
            'shorts': ClothingType.SHORTS,
            'skirt': ClothingType.SKIRT,
            'boots': ClothingType.BOOTS,
            'sneakers': ClothingType.SNEAKERS,
            'heels': ClothingType.HEELS,
            'blazer': ClothingType.BLAZER,
            'coat': ClothingType.COAT,
            'accessory': ClothingType.ACCESSORY,
            'other': ClothingType.OTHER
        }
        if enum_value in enum_mappings:
            return enum_mappings[enum_value]
        else:
            logger.warning(f"Unknown enum value {enum_value}, defaulting to OTHER")
            return ClothingType.OTHER

    # Convert to lowercase for case-insensitive matching
    type_lower = item_type.lower()
    sub_type_lower = sub_type.lower() if sub_type else None

    # Special case for shorts - check both type and subtype
    if (type_lower == "pants" and sub_type_lower == "shorts") or \
       (type_lower == "shorts") or \
       (sub_type_lower == "shorts"):
        return ClothingType.SHORTS

    # Special case for shoes - always return SHOES type regardless of subtype
    if type_lower == "shoes" or type_lower == "boots" or type_lower == "sneakers" or type_lower == "sandals":
        return ClothingType.SHOES

    # Map common variations to standard types with improved mapping
    type_mapping: Dict[str, ClothingType] = {
        # Shirts
        "shirt": ClothingType.SHIRT,
        "dress_shirt": ClothingType.DRESS_SHIRT,
        "t-shirt": ClothingType.T_SHIRT,
        "tshirt": ClothingType.T_SHIRT,
        "blouse": ClothingType.BLOUSE,
        "tank_top": ClothingType.TANK_TOP,
        "tank": ClothingType.TANK_TOP,
        "crop_top": ClothingType.CROP_TOP,
        "crop": ClothingType.CROP_TOP,
        "polo": ClothingType.POLO,
        "top": ClothingType.SHIRT,
        
        # Bottoms
        "pants": ClothingType.PANTS,
        "trousers": ClothingType.PANTS,
        "jeans": ClothingType.JEANS,
        "chinos": ClothingType.CHINOS,
        "slacks": ClothingType.SLACKS,
        "joggers": ClothingType.JOGGERS,
        "sweatpants": ClothingType.SWEATPANTS,
        "shorts": ClothingType.SHORTS,
        "skirt": ClothingType.SKIRT,
        "mini_skirt": ClothingType.MINI_SKIRT,
        "midi_skirt": ClothingType.MIDI_SKIRT,
        "maxi_skirt": ClothingType.MAXI_SKIRT,
        "pencil_skirt": ClothingType.PENCIL_SKIRT,
        
        # Dresses
        "dress": ClothingType.DRESS,
        "gown": ClothingType.DRESS,
        "sundress": ClothingType.SUNDRESS,
        "cocktail_dress": ClothingType.COCKTAIL_DRESS,
        "maxi_dress": ClothingType.MAXI_DRESS,
        "mini_dress": ClothingType.MINI_DRESS,
        
        # Outerwear
        "jacket": ClothingType.JACKET,
        "coat": ClothingType.COAT,
        "blazer": ClothingType.BLAZER,
        "vest": ClothingType.VEST,
        "sweater": ClothingType.SWEATER,
        "jumper": ClothingType.SWEATER,
        "hoodie": ClothingType.HOODIE,
        "cardigan": ClothingType.CARDIGAN,
        
        # Shoes
        "shoes": ClothingType.SHOES,
        "dress_shoes": ClothingType.DRESS_SHOES,
        "loafers": ClothingType.LOAFERS,
        "sneakers": ClothingType.SNEAKERS,
        "boots": ClothingType.BOOTS,
        "sandals": ClothingType.SANDALS,
        "heels": ClothingType.HEELS,
        "flats": ClothingType.FLATS,
        
        # Accessories
        "accessory": ClothingType.ACCESSORY,
        "jewelry": ClothingType.JEWELRY,
        "bag": ClothingType.BAG,
        "hat": ClothingType.HAT,
        "scarf": ClothingType.SCARF,
        "belt": ClothingType.BELT,
        "watch": ClothingType.WATCH,
        "other": ClothingType.OTHER
    }

    # Try to find a match in the mapping
    for key, value in type_mapping.items():
        if key in type_lower:
            return value

    # If no match found, try to match against enum values
    try:
        return ClothingType(type_lower)
    except ValueError:
        logger.warning(f"Could not normalize type '{item_type}', defaulting to OTHER")
        return ClothingType.OTHER

def normalize_subtype(sub_type: Optional[str]) -> Optional[str]:
    """
    Normalize clothing subtype.
    """
    if not sub_type:
        return None

    # Remove special characters and normalize
    normalized = ''.join(c for c in str(sub_type) if c.isalnum() or c.isspace() or c == '-')
    return normalized.strip()

def validate_clothing_item(item: Dict[str, Any]) -> ClothingItem:
    """
    Validate and normalize a clothing item.
    """
    # Normalize type and subtype
    item_type = normalize_clothing_type(((item.get('type', '') if item else '') if item else ''), item.get('subType'))
    sub_type = normalize_subtype((item.get('subType') if item else None))

    # Update the item with normalized values
    item['type'] = item_type
    item['subType'] = sub_type

    # Create and validate ClothingItem
    try:
        return ClothingItem(**item)
    except Exception as e:
        logger.error(f"Error validating clothing item: {str(e)}")
        raise ValueError(f"Invalid clothing item: {str(e)}")

def validate_outfit_requirements(outfit: ClothingItem) -> bool:
    """
    Validate that an outfit meets all requirements.
    """
    # Check for required pieces using core categories
    from .layering import get_core_category
    
    top_items = [item for item in outfit.items if get_core_category(item.type) == CoreCategory.TOP]
    bottom_items = [item for item in outfit.items if get_core_category(item.type) == CoreCategory.BOTTOM]
    dress_items = [item for item in outfit.items if get_core_category(item.type) == CoreCategory.DRESS]
    
    has_top = len(top_items) > 0
    has_bottom = len(bottom_items) > 0
    has_dress = len(dress_items) > 0
    has_mixed_bottoms = any(item.type == ClothingType.PANTS for item in outfit.items) and any(item.type == ClothingType.SHORTS for item in outfit.items)

    # Get style and season from metadata
    style = outfit.(metadata.get('style', '') if metadata else '').lower() if outfit.metadata else ''
    season = outfit.(metadata.get('season', '') if metadata else '').lower() if outfit.metadata else ''
    occasion = outfit.(metadata.get('occasion', '') if metadata else '').lower() if outfit.metadata else ''
    
    # Special handling for vacation outfits
    if occasion == 'vacation':
        # Vacation outfits can be more flexible
        if not (has_top or has_bottom):  # Allow single-piece outfits like dresses
            logger.warning("Vacation outfit should have at least one piece")
            return False
        
        # Allow mixing of casual pieces
        if has_mixed_bottoms:
            logger.info("Vacation outfit can mix pants and shorts")
            return True
        
        # Vacation-specific piece count
        piece_count = len(outfit.items)
        if piece_count < 1 or piece_count > 5:  # More flexible piece count for vacation
            logger.warning(f"Vacation outfit should have 1-5 pieces, got {piece_count}")
            return False
        
        return True

    # Regular outfit validation
    if has_dress:
        # If we have a dress, we don't need separate top and bottom
        if not has_dress:
            logger.warning("Outfit with dress should have at least one dress")
            return False
    else:
        # If no dress, we need both top and bottom
        if not has_top:
            logger.warning("Outfit missing a top (shirt, sweater, jacket, etc.)")
            return False

        if not has_bottom:
            logger.warning("Outfit missing pants, shorts, or skirt")
            return False

    if has_mixed_bottoms:
        logger.warning("Outfit cannot mix pants and shorts")
        return False

    # Define piece count ranges based on style and season
    piece_count = len(outfit.items)
    min_pieces = 2
    max_pieces = 6
    
    # Adjust for summer styles
    if season == 'summer' or 'summer' in style:
        min_pieces = 2
        max_pieces = 4
    
    # Adjust for winter styles
    if season == 'winter' or 'winter' in style:
        min_pieces = 3
        max_pieces = 6
    
    # Adjust for specific styles
    if 'minimalist' in style:
        min_pieces = 2
        max_pieces = 4
    elif 'layered' in style:
        min_pieces = 4
        max_pieces = 6
    
    # Check piece count
    if piece_count < min_pieces or piece_count > max_pieces:
        logger.warning(f"Outfit must have {min_pieces}-{max_pieces} pieces for {style} style in {season} season, got {piece_count}")
        return False

    return True

def is_clothing_item(item: Any) -> bool:
    """Type guard to check if an object is a valid clothing item."""
    try:
        validate_clothing_item(item)
        return True
    except Exception:
        return False 
