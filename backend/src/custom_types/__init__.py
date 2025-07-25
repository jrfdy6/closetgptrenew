# This file makes the types directory a Python package
from .profile import UserProfile
from .outfit import WeatherData, OutfitContext, OutfitGeneratedOutfit, OutfitPiece
from .wardrobe import (
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
from .weather import WeatherData

__all__ = [
    'UserProfile',
    'WeatherData',
    'OutfitContext',
    'OutfitGeneratedOutfit',
    'OutfitPiece',
    'ClothingItem',
    'ClothingType',
    'Season',
    'StyleTag',
    'Color',
    'VisualAttributes',
    'ItemMetadata',
    'BasicMetadata',
    'ColorAnalysis',
    'Metadata',
    'Outfit',
    'WardrobeGeneratedOutfit'
] 