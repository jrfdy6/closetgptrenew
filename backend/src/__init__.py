# This file makes the src directory a Python package
# Wrap all imports in try-catch to prevent silent failures during app startup

import logging
logger = logging.getLogger(__name__)

# Safe import function
def safe_import(module_name: str, item_name: str = None):
    """Safely import a module or item, returning None if import fails"""
    try:
        if item_name:
            module = __import__(module_name, fromlist=[item_name])
            return getattr(module, item_name)
        else:
            return __import__(module_name)
    except Exception as e:
        logger.warning(f"Failed to import {module_name}{'.' + item_name if item_name else ''}: {e}")
        return None

# Safe imports with fallbacks
try:
    from .custom_types.profile import UserProfile
    # UserProfile imported
except Exception as e:
    logger.error(f"Failed to import UserProfile: {e}")
    UserProfile = None

try:
    from .custom_types.outfit import WeatherData, OutfitContext, OutfitGeneratedOutfit, OutfitPiece
    # Outfit types imported
except Exception as e:
    logger.error(f"Failed to import outfit types: {e}")
    WeatherData = None
    OutfitContext = None
    OutfitGeneratedOutfit = None
    OutfitPiece = None

try:
    from .custom_types.wardrobe import (
        ClothingType,
        Season,
        StyleTag,
        Color,
        VisualAttributes,
        ItemMetadata,
        BasicMetadata,
        ColorAnalysis,
        Metadata,
        ClothingItem,
        Outfit,
        GeneratedOutfit as WardrobeGeneratedOutfit
    )
    # Wardrobe types imported
except Exception as e:
    logger.error(f"Failed to import wardrobe types: {e}")
    # Set all to None if import fails
    ClothingType = None
    Season = None
    StyleTag = None
    Color = None
    VisualAttributes = None
    ItemMetadata = None
    BasicMetadata = None
    ColorAnalysis = None
    Metadata = None
    ClothingItem = None
    Outfit = None
    WardrobeGeneratedOutfit = None

# Only include successfully imported items in __all__
__all__ = []
if UserProfile:
    __all__.append('UserProfile')
if WeatherData:
    __all__.extend(['WeatherData', 'OutfitContext', 'OutfitGeneratedOutfit', 'OutfitPiece'])
if ClothingType:
    __all__.extend([
        'ClothingType', 'Season', 'StyleTag', 'Color', 'VisualAttributes',
        'ItemMetadata', 'BasicMetadata', 'ColorAnalysis', 'Metadata',
        'ClothingItem', 'Outfit', 'WardrobeGeneratedOutfit'
    ])

# Package imports complete 