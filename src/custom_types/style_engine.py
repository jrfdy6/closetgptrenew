from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from enum import Enum

class Fit(str, Enum):
    RELAXED = "relaxed"
    TAILORED = "tailored"
    FITTED = "fitted"
    OVERSIZED = "oversized"
    LOOSE = "loose"
    SKINNY = "skinny"
    REGULAR = "regular"
    ATHLETIC = "athletic"
    STRUCTURED = "structured"

class Silhouette(str, Enum):
    A_LINE = "a_line"
    HOURGLASS = "hourglass"
    RECTANGULAR = "rectangular"
    TRIANGULAR = "triangular"
    OVERSIZED = "oversized"
    FITTED = "fitted"
    FLOWING = "flowing"
    STRUCTURED = "structured"
    MINIMAL = "minimal"
    VOLUMINOUS = "voluminous"

class Material(str, Enum):
    # Natural Fibers
    COTTON = "cotton"
    WOOL = "wool"
    SILK = "silk"
    LINEN = "linen"
    LEATHER = "leather"
    DENIM = "denim"
    CORDUROY = "corduroy"
    TWILL = "twill"
    TWEED = "tweed"
    CASHMERE = "cashmere"
    SATIN = "satin"
    
    # Synthetic Fibers
    POLYESTER = "polyester"
    NYLON = "nylon"
    SPANDEX = "spandex"
    RAYON = "rayon"
    ACRYLIC = "acrylic"
    VISCOSE = "viscose"
    
    # Blends
    COTTON_BLEND = "cotton_blend"
    WOOL_BLEND = "wool_blend"
    POLYESTER_BLEND = "polyester_blend"
    DOWN = "down"
    FLEECE = "fleece"
    
    # Special Materials
    WATERPROOF = "waterproof"
    RUBBER = "rubber"
    THERMAL = "thermal"
    GORE_TEX = "gore_tex"
    TECHNICAL = "technical"
    MIXED_MEDIA = "mixed_media"
    TEXTURED = "textured"
    UNCONVENTIONAL = "unconventional"

class Neckline(str, Enum):
    ROUND = "round"
    V_NECK = "v_neck"
    CREW = "crew"
    TURTLENECK = "turtleneck"
    SCOOP = "scoop"
    BOAT = "boat"
    COLLAR = "collar"
    PLUNGE = "plunge"
    OFF_SHOULDER = "off_shoulder"
    HALTER = "halter"
    SWEETHEART = "sweetheart"
    SQUARE = "square"

class Detail(str, Enum):
    POCKETS = "pockets"
    BUTTONS = "buttons"
    ZIPPERS = "zippers"
    PATCHES = "patches"
    EMBROIDERY = "embroidery"
    PLEATS = "pleats"
    RUFFLES = "ruffles"
    LACE = "lace"
    FRINGE = "fringe"
    BEADS = "beads"
    SEQUINS = "sequins"
    ELBOW_PATCHES = "elbow_patches"
    PATCHWORK = "patchwork"
    DISTRESSED = "distressed"
    FRAYED = "frayed"

class Accessory(str, Enum):
    BELT = "belt"
    SCARF = "scarf"
    HAT = "hat"
    GLOVES = "gloves"
    SUNGLASSES = "sunglasses"
    WATCH = "watch"
    SPORTS_WATCH = "sports_watch"
    NECKLACE = "necklace"
    EARRINGS = "earrings"
    BRACELET = "bracelet"
    RING = "ring"
    BAG = "bag"
    SATCHEL = "satchel"
    BACKPACK = "backpack"
    TIE = "tie"
    BOW_TIE = "bow_tie"
    POCKET_SQUARE = "pocket_square"

class StyleAttributes(BaseModel):
    fit: Optional[Fit] = None
    silhouette: Optional[Silhouette] = None
    materials: List[Material] = Field(default_factory=list)
    necklines: List[Neckline] = Field(default_factory=list)
    details: List[Detail] = Field(default_factory=list)
    accessories: List[Accessory] = Field(default_factory=list)
    color_palette: List[str] = Field(default_factory=list)
    layers: Optional[int] = None

class StyleDefinition(BaseModel):
    name: str
    description: str
    attributes: StyleAttributes
    compatible_styles: List[str] = Field(default_factory=list)
    incompatible_styles: List[str] = Field(default_factory=list)
    seasonal_preferences: List[str] = Field(default_factory=list)
    occasion_suitability: List[str] = Field(default_factory=list)

# Example style definitions
STYLE_DEFINITIONS = {
    "dark_academia": StyleDefinition(
        name="Dark Academia",
        description="A sophisticated, intellectual aesthetic with dark, muted colors and vintage-inspired elements",
        attributes=StyleAttributes(
            fit=Fit.TAILORED,
            silhouette=Silhouette.STRUCTURED,
            materials=[Material.TWEED, Material.WOOL, Material.CORDUROY, Material.LEATHER],
            necklines=[Neckline.COLLAR, Neckline.TURTLENECK],
            details=[Detail.ELBOW_PATCHES, Detail.PATCHES],
            accessories=[Accessory.SATCHEL, Accessory.SUNGLASSES, Accessory.TIE],
            color_palette=["navy", "burgundy", "forest_green", "brown", "cream"],
            layers=2
        ),
        compatible_styles=["classic", "vintage", "preppy"],
        incompatible_styles=["streetwear", "sporty"],
        seasonal_preferences=["fall", "winter"],
        occasion_suitability=["academic", "professional", "formal"]
    ),
    
    "minimalist": StyleDefinition(
        name="Minimalist",
        description="Clean, simple, and focused on quality over quantity with neutral colors and timeless pieces",
        attributes=StyleAttributes(
            fit=Fit.REGULAR,
            silhouette=Silhouette.MINIMAL,
            materials=[Material.COTTON, Material.LINEN, Material.WOOL],
            necklines=[Neckline.CREW, Neckline.ROUND, Neckline.V_NECK],
            details=[Detail.POCKETS, Detail.BUTTONS],
            accessories=[Accessory.WATCH, Accessory.BAG],
            color_palette=["white", "black", "gray", "beige", "navy"],
            layers=1
        ),
        compatible_styles=["classic", "modern", "scandinavian"],
        incompatible_styles=["maximalist", "bohemian"],
        seasonal_preferences=["all"],
        occasion_suitability=["casual", "business_casual", "professional"]
    )
}

def get_style_definition(style_name: str) -> Optional[StyleDefinition]:
    """Get the style definition for a given style name."""
    return STYLE_DEFINITIONS.get(style_name.lower())

def get_compatible_styles(style_name: str) -> List[str]:
    """Get a list of styles that are compatible with the given style."""
    style_def = get_style_definition(style_name)
    if style_def:
        return style_def.compatible_styles
    return []

def get_incompatible_styles(style_name: str) -> List[str]:
    """Get a list of styles that are incompatible with the given style."""
    style_def = get_style_definition(style_name)
    if style_def:
        return style_def.incompatible_styles
    return []

def validate_style_combination(styles: List[str]) -> bool:
    """Validate if a combination of styles is compatible."""
    for style in styles:
        style_def = get_style_definition(style)
        if not style_def:
            continue
        
        # Check if any of the other styles are in the incompatible list
        for other_style in styles:
            if other_style != style and other_style in style_def.incompatible_styles:
                return False
    return True

def get_style_attributes(style_name: str) -> Optional[StyleAttributes]:
    """Get the style attributes for a given style name."""
    style_def = get_style_definition(style_name)
    if style_def:
        return style_def.attributes
    return None 