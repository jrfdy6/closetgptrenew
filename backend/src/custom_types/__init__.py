# This file makes the types directory a Python package
# Removed automatic imports to prevent circular dependencies
# Import specific classes as needed in individual modules

__all__ = [
    # Profile types
    'UserProfile',
    # Weather types  
    'WeatherData',
    # Outfit types
    'OutfitContext',
    'OutfitGeneratedOutfit', 
    'OutfitPiece',
    # Wardrobe types
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