from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from pydantic import validator
from .style_engine import StyleAttributes, Fit, Silhouette, Material, Neckline, Detail, Accessory
import re
import time

class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"

class ClothingType(str, Enum):
    SHIRT = "shirt"
    DRESS_SHIRT = "dress_shirt"
    PANTS = "pants"
    SHORTS = "shorts"
    SKIRT = "skirt"
    DRESS = "dress"
    JACKET = "jacket"
    SWEATER = "sweater"
    SHOES = "shoes"
    DRESS_SHOES = "dress_shoes"
    LOAFERS = "loafers"
    SNEAKERS = "sneakers"
    ACCESSORY = "accessory"
    OTHER = "other"
    # Additional types for better categorization
    T_SHIRT = "t-shirt"
    BLOUSE = "blouse"
    TANK_TOP = "tank_top"
    CROP_TOP = "crop_top"
    POLO = "polo"
    HOODIE = "hoodie"
    CARDIGAN = "cardigan"
    BLAZER = "blazer"
    COAT = "coat"
    VEST = "vest"
    JEANS = "jeans"
    CHINOS = "chinos"
    SLACKS = "slacks"
    JOGGERS = "joggers"
    SWEATPANTS = "sweatpants"
    MINI_SKIRT = "mini_skirt"
    MIDI_SKIRT = "midi_skirt"
    MAXI_SKIRT = "maxi_skirt"
    PENCIL_SKIRT = "pencil_skirt"
    SUNDRESS = "sundress"
    COCKTAIL_DRESS = "cocktail_dress"
    MAXI_DRESS = "maxi_dress"
    MINI_DRESS = "mini_dress"
    BOOTS = "boots"
    SANDALS = "sandals"
    HEELS = "heels"
    FLATS = "flats"
    HAT = "hat"
    SCARF = "scarf"
    BELT = "belt"
    JEWELRY = "jewelry"
    BAG = "bag"
    WATCH = "watch"

class StyleType(str, Enum):
    CASUAL = "Casual"
    FORMAL = "Formal"
    SPORTS = "Sports"
    TRENDY = "Trendy"
    VINTAGE = "Vintage"
    STATEMENT = "Statement"
    SMART_CASUAL = "Smart Casual"
    BUSINESS = "Business"
    LUXURY = "Luxury"
    STREETWEAR = "Streetwear"
    MINIMALIST = "Minimalist"
    BOHEMIAN = "Bohemian"
    CLASSIC = "Classic"
    ELEGANT = "Elegant"
    ATHLETIC = "Athletic"
    PREPPY = "Preppy"
    GOTHIC = "Gothic"
    PUNK = "Punk"
    HIPSTER = "Hipster"
    RETRO = "Retro"

# Alias StyleType as StyleTag for compatibility
StyleTag = StyleType

class StyleSubtype(str, Enum):
    # --- CASUAL ---
    EVERYDAY = "Everyday"
    RELAXED = "Relaxed"
    COMFY = "Comfy"
    LOUNGEWEAR = "Loungewear"
    WEEKEND = "Weekend"
    DENIM_CASUAL = "Denim Casual"
    SUMMER_CASUAL = "Summer Casual"

    # --- FORMAL ---
    BLACK_TIE = "Black Tie"
    COCKTAIL = "Cocktail"
    EVENING_GOWN = "Evening Gown"
    TUXEDO = "Tuxedo"
    BRIDAL = "Bridal"
    GALA = "Gala"

    # --- SPORTS / ATHLETIC ---
    ACTIVEWEAR = "Activewear"
    GYM_WEAR = "Gym Wear"
    RUNNING = "Running"
    CYCLING = "Cycling"
    SWIMWEAR = "Swimwear"
    TENNISCORE = "Tenniscore"
    ATHLEISURE = "Athleisure"

    # --- TRENDY ---
    Y2K = "Y2K"
    FUTURISTIC = "Futuristic"
    COTTAGECORE = "Cottagecore"
    COASTAL_GRANDMA = "Coastal Grandma"
    GENDER_FLUID = "Gender Fluid"
    ECLECTIC = "Eclectic"
    CLEAN_GIRL = "Clean Girl"
    DARK_ACADEMIA = "Dark Academia"
    LIGHT_ACADEMIA = "Light Academia"

    # --- VINTAGE / RETRO ---
    SEVENTIES = "70s"
    EIGHTIES = "80s"
    NINETIES = "90s"
    MOD = "Mod"
    PINUP = "Pinup"
    OLD_MONEY = "Old Money"
    VINTAGE_CHANEL = "Vintage Chanel"

    # --- STATEMENT / ARTISTIC ---
    COLORBLOCK = "Colorblock"
    MAXIMALIST = "Maximalist"
    PRINT_ON_PRINT = "Print on Print"
    ART_POP = "Art Pop"
    BOLD_GRAPHICS = "Bold Graphics"
    AVANT_GARDE = "Avant-Garde"

    # --- SMART CASUAL / BUSINESS ---
    BUSINESS_CASUAL = "Business Casual"
    OFFICE_CHIC = "Office Chic"
    MONOCHROME_MINIMAL = "Monochrome Minimal"
    CLEAN_LINES = "Clean Lines"
    URBAN_PROFESSIONAL = "Urban Professional"

    # --- LUXURY / ELEGANT ---
    DESIGNER = "Designer"
    HIGH_FASHION = "High Fashion"
    SOPHISTICATED = "Sophisticated"
    FRENCH_GIRL = "French Girl"
    RED_CARPET = "Red Carpet"

    # --- STREETWEAR ---
    SKATE = "Skate"
    URBAN = "Urban"
    TECHWEAR = "Techwear"
    HYPEBEAST = "Hypebeast"
    GRUNGE = "Grunge"
    WORKWEAR = "Workwear"
    MILITARY = "Military Inspired"

    # --- BOHEMIAN ---
    FESTIVAL = "Festival"
    FOLK = "Folk"
    LAYERED = "Layered"
    ETHNIC_INFLUENCE = "Ethnic Influence"
    EARTH_TONES = "Earth Tones"

    # --- SUBCULTURE / NICHE ---
    PREPPY = "Preppy"
    GOTHIC = "Gothic"
    PUNK = "Punk"
    HIPSTER = "Hipster"
    EMO = "Emo"
    SCENE = "Scene"
    ALT = "Alt"

    # --- CLASSIC / MINIMALIST ---
    CLASSIC_CHIC = "Classic Chic"
    TIMELESS = "Timeless"
    JAPANESE_MINIMALISM = "Japanese Minimalism"
    SCANDI = "Scandinavian Minimalism"
    MONOCHROME = "Monochrome"
    MODERN_BASIC = "Modern Basic"

class Color(BaseModel):
    name: str
    hex: str
    rgb: List[int] = Field(default_factory=lambda: [0, 0, 0])

    @classmethod
    def from_string(cls, color_name: str) -> "Color":
        """Create a Color instance from a string name."""
        # Normalize color name to snake_case
        normalized_name = color_name.lower().replace(' ', '_')
        # Generate a default hex value based on the color name
        # This is a simple mapping, you might want to use a more sophisticated color mapping
        hex_value = "#000000"  # Default black
        rgb_value = [0, 0, 0]  # Default black RGB
        return cls(name=normalized_name, hex=hex_value, rgb=rgb_value)

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TemperatureRange(str, Enum):
    VERY_COLD = "very_cold"
    COLD = "cold"
    COOL = "cool"
    MILD = "mild"
    WARM = "warm"
    HOT = "hot"
    VERY_HOT = "very_hot"

class Material(str, Enum):
    COTTON = "cotton"
    WOOL = "wool"
    SILK = "silk"
    LINEN = "linen"
    DENIM = "denim"
    LEATHER = "leather"
    SYNTHETIC = "synthetic"
    KNIT = "knit"
    FLEECE = "fleece"
    OTHER = "other"

class LayerLevel(str, Enum):
    BASE = "base"
    INNER = "inner"
    MIDDLE = "middle"
    OUTER = "outer"

class WarmthFactor(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"

class CoreCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"

class BodyType(str, Enum):
    HOURGLASS = "hourglass"
    PEAR = "pear"
    APPLE = "apple"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

class SkinTone(str, Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"

class TemperatureCompatibility(BaseModel):
    minTemp: float
    maxTemp: float
    recommendedLayers: List[str]
    materialPreferences: List[Material]

    @field_validator('minTemp', 'maxTemp', mode='before')
    def parse_temperature_strings(cls, v, info):
        """Parse temperature strings with degree symbols to float values."""
        if isinstance(v, str):
            # Remove degree symbols and units, extract just the number
            # Match numbers (including decimals) followed by optional degree symbol and units
            match = re.search(r'(-?\d+(?:\.\d+)?)', v)
            if match:
                return float(match.group(1))
            else:
                # If no number found, return a default value
                return 20.0  # Default to 20°C/68°F
        return v

class MaterialCompatibility(BaseModel):
    compatibleMaterials: List[Material]
    weatherAppropriate: Dict[str, List[Material]]

class BodyTypeCompatibility(BaseModel):
    recommendedFits: Optional[Dict[BodyType, List[str]]] = None
    styleRecommendations: Optional[Dict[BodyType, List[str]]] = None

class SkinToneCompatibility(BaseModel):
    compatibleColors: Optional[Dict[SkinTone, List[str]]] = None
    recommendedPalettes: Optional[Dict[SkinTone, List[str]]] = None

class OutfitScoring(BaseModel):
    versatility: float = Field(ge=0, le=10)
    seasonality: float = Field(ge=0, le=10)
    formality: float = Field(ge=0, le=10)
    trendiness: float = Field(ge=0, le=10)
    quality: float = Field(ge=0, le=10)

class VisualAttributes(BaseModel):
    material: Optional[str] = None
    pattern: Optional[str] = None
    textureStyle: Optional[str] = None
    fabricWeight: Optional[str] = None
    fit: Optional[str] = None
    silhouette: Optional[str] = None
    length: Optional[str] = None
    genderTarget: Optional[str] = None
    sleeveLength: Optional[str] = None
    neckline: Optional[str] = None  # "collar", "crew", "v-neck", "polo", "button-down", etc.
    hangerPresent: Optional[bool] = None
    backgroundRemoved: Optional[bool] = None
    wearLayer: Optional[str] = None
    formalLevel: Optional[str] = None
    waistbandType: Optional[str] = None  # "belt_loops", "elastic", "drawstring", "elastic_drawstring", "button_zip", "none"
    # New layering properties
    layerLevel: Optional[LayerLevel] = None
    warmthFactor: Optional[WarmthFactor] = None
    coreCategory: Optional[CoreCategory] = None
    canLayer: Optional[bool] = None
    maxLayers: Optional[int] = None
    temperatureCompatibility: Optional[TemperatureCompatibility] = None
    materialCompatibility: Optional[MaterialCompatibility] = None
    bodyTypeCompatibility: Optional[Dict[str, Any]] = None  # Allow dict for complex nested structures
    skinToneCompatibility: Optional[Dict[str, Any]] = None  # Allow dict for complex nested structures
    outfitScoring: Optional[Dict[str, Any]] = None  # Allow dict for complex nested structures

    model_config = ConfigDict(
        extra='allow',  # Allow extra fields from Firestore
        arbitrary_types_allowed=True
    )

class ItemMetadata(BaseModel):
    priceEstimate: Optional[str] = None
    careInstructions: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        extra='allow',  # Allow extra fields from Firestore
        arbitrary_types_allowed=True
    )

class BasicMetadata(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    orientation: Optional[str] = None
    dateTaken: Optional[str] = None
    deviceModel: Optional[str] = None
    gps: Optional[str] = None
    flashUsed: Optional[bool] = None

    model_config = ConfigDict(
        extra='allow',  # Allow extra fields like imageHash
        arbitrary_types_allowed=True
    )

class ColorAnalysis(BaseModel):
    dominant: List[Color] = Field(default_factory=list)
    matching: List[Color] = Field(default_factory=list)

    @field_validator('dominant', 'matching', mode='before')
    def convert_strings_to_colors(cls, v, info):
        if isinstance(v, list):
            return [Color.from_string(c) if isinstance(c, str) else c for c in v]
        return v

    model_config = ConfigDict(
        extra='allow',  # Allow extra color fields
        arbitrary_types_allowed=True
    )

class Metadata(BaseModel):
    analysisTimestamp: Optional[int] = None  # Made optional for backwards compatibility
    originalType: Optional[str] = None  # Made optional for backwards compatibility  
    originalSubType: Optional[str] = None
    styleTags: List[str] = Field(default_factory=list)
    occasionTags: List[str] = Field(default_factory=list)
    brand: Optional[str] = None
    imageHash: Optional[str] = None
    colorAnalysis: Optional[ColorAnalysis] = None  # Make optional to prevent validation failure
    basicMetadata: Optional[BasicMetadata] = None
    visualAttributes: Optional[VisualAttributes] = None
    itemMetadata: Optional[ItemMetadata] = None
    naturalDescription: Optional[str] = None
    normalized: Optional[Dict[str, Any]] = None  # Add normalized field
    temperatureCompatibility: Optional[TemperatureCompatibility] = None
    materialCompatibility: Optional[MaterialCompatibility] = None
    bodyTypeCompatibility: Optional[BodyTypeCompatibility] = None
    skinToneCompatibility: Optional[SkinToneCompatibility] = None
    outfitScoring: Optional[OutfitScoring] = None

    @field_validator('colorAnalysis', mode='before')
    def convert_color_analysis(cls, v, info):
        if isinstance(v, dict):
            if 'dominant' in v:
                v['dominant'] = [
                    Color.from_string(c) if isinstance(c, str) else c
                    for c in v['dominant']
                ]
            if 'matching' in v:
                v['matching'] = [
                    Color.from_string(c) if isinstance(c, str) else c
                    for c in v['matching']
                ]
        return v

    model_config = ConfigDict(
        extra='allow',  # Allow extra fields from Firestore
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "analysisTimestamp": 1234567890,
                "originalType": "jacket",
                "originalSubType": "denim",
                "styleTags": ["casual", "streetwear"],
                "occasionTags": ["daily", "casual"],
                "brand": "",
                "imageHash": "abc123",
                "colorAnalysis": {
                    "dominant": ["blue", "navy"],
                    "matching": ["white", "gray"]
                },
                "basicMetadata": {
                    "width": 800,
                    "height": 600,
                    "orientation": "portrait",
                    "dateTaken": "2024-03-20T12:00:00Z",
                    "deviceModel": "iPhone 12",
                    "gps": "37.7749,-122.4194",
                    "flashUsed": False
                },
                "visualAttributes": {
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "fit": "regular",
                    "length": "regular",
                    "sleeveLength": "",
                    "genderTarget": "unisex",
                    "textureStyle": "denim",
                    "backgroundRemoved": False,
                    "silhouette": "regular",
                    "hangerPresent": False,
                    "wearLayer": "outer",
                    "material": "denim",
                    "fabricWeight": "medium"
                },
                "itemMetadata": {
                    "careInstructions": "Machine wash cold",
                    "tags": ["denim", "jacket"],
                    "priceEstimate": "89.99"
                },
                "naturalDescription": "A classic blue denim jacket"
            }
        }
    )

class ClothingItem(BaseModel):
    id: str
    name: str
    type: ClothingType
    color: str
    season: List[str]
    imageUrl: Optional[str] = "https://placeholder.com/image.jpg"
    tags: List[str] = Field(default_factory=list)
    style: List[str] = Field(default_factory=list)
    userId: Optional[str] = "unknown-user"
    dominantColors: List[Color] = Field(default_factory=list)
    matchingColors: List[Color] = Field(default_factory=list)
    occasion: List[str] = Field(default_factory=list)
    brand: Optional[str] = None
    size: Optional[str] = None  # Add missing size field
    material: Optional[str] = None  # Add missing material field
    createdAt: Optional[int] = Field(default_factory=lambda: int(time.time() * 1000))
    updatedAt: Optional[int] = Field(default_factory=lambda: int(time.time() * 1000))
    subType: Optional[str] = None
    colorName: Optional[str] = None
    backgroundRemoved: Optional[bool] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None  # Accept any dict - don't validate nested structure
    
    # Usage tracking fields for wardrobe diversity
    wearCount: Optional[int] = 0
    lastWorn: Optional[float] = 0.0
    favorite_score: Optional[float] = 0.0
    seasonal_score: Optional[float] = 1.0  # Add seasonal_score field for testing
    quality_score: Optional[float] = 0.5  # Add quality_score field for validation
    pairability_score: Optional[float] = 0.5  # Add pairability_score field for validation

    @field_validator('style', mode='before')
    def convert_style_to_list(cls, v, info):
        """Convert single string style to list if needed."""
        if isinstance(v, str):
            return [v]
        return v

    @field_validator('createdAt', 'updatedAt', mode='before')
    def convert_datetime_to_int(cls, v, info):
        """Convert Firestore DatetimeWithNanoseconds to integer timestamp."""
        if hasattr(v, 'timestamp'):
            # Handle DatetimeWithNanoseconds from Firestore
            return int(v.timestamp() * 1000)  # Convert to milliseconds
        elif isinstance(v, str):
            # Handle string timestamps
            try:
                return int(v)
            except ValueError:
                return v
        elif isinstance(v, float):
            # Handle float timestamps (like 1752706214.171391)
            return int(v)
        return v

    @field_validator('dominantColors', 'matchingColors', mode='before')
    def convert_colors(cls, v, info):
        """Convert color data to proper Color objects."""
        if not isinstance(v, list):
            return []
        
        converted_colors = []
        for color in v:
            if isinstance(color, dict):
                # Handle color objects with name, hex, rgb
                if 'name' in color:
                    converted_colors.append(Color(
                        name=(color.get('name', 'Unknown') if color else 'Unknown'),
                        hex=(color.get('hex', '#000000') if color else '#000000'),
                        rgb=(color.get('rgb', [0, 0, 0]) if color else [0, 0, 0])
                    ))
                else:
                    # Handle simple color strings
                    converted_colors.append(Color.from_string(str(color)))
            elif isinstance(color, str):
                # Handle string colors
                converted_colors.append(Color.from_string(color))
            else:
                # Skip invalid colors
                continue
        
        return converted_colors

    @field_validator('metadata', mode='before')
    def convert_metadata_colors(cls, v, info):
        """Convert metadata color strings to Color objects."""
        if not v:
            return v
        
        # Handle material name case conversion and validation
        if 'visualAttributes' in v:
            va = v['visualAttributes']
            if va and 'materialCompatibility' in va:
                mc = va['materialCompatibility']
                if mc and 'compatibleMaterials' in mc:
                    mc['compatibleMaterials'] = [
                        cls._normalize_material(mat) if isinstance(mat, str) else mat 
                        for mat in mc['compatibleMaterials']
                    ]
                if mc and 'weatherAppropriate' in mc:
                    for season in mc['weatherAppropriate']:
                        if mc['weatherAppropriate'][season]:
                            mc['weatherAppropriate'][season] = [
                                cls._normalize_material(mat) if isinstance(mat, str) else mat 
                                for mat in mc['weatherAppropriate'][season]
                            ]
            
            if va and 'temperatureCompatibility' in va:
                tc = va['temperatureCompatibility']
                if tc and 'materialPreferences' in tc:
                    tc['materialPreferences'] = [
                        cls._normalize_material(mat) if isinstance(mat, str) else mat 
                        for mat in tc['materialPreferences']
                    ]

            # Handle missing required fields in bodyTypeCompatibility
            if va and 'bodyTypeCompatibility' in va:
                btc = va['bodyTypeCompatibility']
                if btc:
                    if 'recommendedFits' not in btc or btc['recommendedFits'] is None:
                        btc['recommendedFits'] = {}
                    if 'styleRecommendations' not in btc or btc['styleRecommendations'] is None:
                        btc['styleRecommendations'] = {}

            # Handle missing required fields in skinToneCompatibility
            if va and 'skinToneCompatibility' in va:
                stc = va['skinToneCompatibility']
                if stc:
                    if 'compatibleColors' not in stc or stc['compatibleColors'] is None:
                        stc['compatibleColors'] = {}
                    if 'recommendedPalettes' not in stc or stc['recommendedPalettes'] is None:
                        stc['recommendedPalettes'] = {}

        # Convert color strings to Color objects
        if 'colorAnalysis' in v:
            ca = v['colorAnalysis']
            if ca and 'dominant' in ca and isinstance(ca['dominant'], list):
                ca['dominant'] = [
                    Color.from_string(color) if isinstance(color, str) else color
                    for color in ca['dominant']
                ]
            if ca and 'matching' in ca and isinstance(ca['matching'], list):
                ca['matching'] = [
                    Color.from_string(color) if isinstance(color, str) else color
                    for color in ca['matching']
                ]
        
        return v

    @staticmethod
    def _normalize_material(material: str) -> str:
        """Normalize material names to valid enum values."""
        if not isinstance(material, str):
            return material
        
        material_lower = material.lower().strip()
        
        # Handle special cases
        if material_lower in ['n/a', 'na', 'none', 'unknown']:
            return 'other'
        
        # Handle compound materials
        if 'leather' in material_lower:
            return 'leather'
        if 'cotton' in material_lower:
            return 'cotton'
        if 'wool' in material_lower:
            return 'wool'
        if 'silk' in material_lower:
            return 'silk'
        if 'linen' in material_lower:
            return 'linen'
        if 'denim' in material_lower:
            return 'denim'
        if 'synthetic' in material_lower or 'polyester' in material_lower or 'nylon' in material_lower:
            return 'synthetic'
        if 'knit' in material_lower:
            return 'knit'
        if 'fleece' in material_lower:
            return 'fleece'
        
        # If it's already a valid enum value, return it
        valid_materials = ['cotton', 'wool', 'silk', 'linen', 'denim', 'leather', 'synthetic', 'knit', 'fleece', 'other']
        if material_lower in valid_materials:
            return material_lower
        
        # Default to 'other' for unrecognized materials
        return 'other'

    def get_style_compatibility(self, other_item: 'ClothingItem') -> float:
        """Calculate style compatibility score between two items."""
        score = 0.0
        total_factors = 0

        # Color harmony
        if self.metadata and other_item.metadata:
            color_harmony = analyze_color_harmony(
                self.metadata.colorAnalysis.dominant,
                other_item.metadata.colorAnalysis.dominant
            )
            score += color_harmony
            total_factors += 1

        # Style tag overlap
        common_styles = set(self.style) & set(other_item.style)
        style_score = len(common_styles) / max(len(self.style), len(other_item.style)) if self.style and other_item.style else 0
        score += style_score
        total_factors += 1

        # Occasion compatibility
        common_occasions = set(self.occasion) & set(other_item.occasion)
        occasion_score = len(common_occasions) / max(len(self.occasion), len(other_item.occasion)) if self.occasion and other_item.occasion else 0
        score += occasion_score
        total_factors += 1

        # Season overlap
        common_seasons = set(self.season) & set(other_item.season)
        season_score = len(common_seasons) / max(len(self.season), len(other_item.season)) if self.season and other_item.season else 0
        score += season_score
        total_factors += 1

        return score / total_factors if total_factors > 0 else 0.0

    model_config = ConfigDict(arbitrary_types_allowed=True)

class Outfit(BaseModel):
    id: str
    name: str
    description: str
    items: List[ClothingItem]
    occasion: str
    season: str
    style: str
    styleTags: List[str] = Field(default_factory=list)
    colorHarmony: str
    styleNotes: str
    createdAt: int
    updatedAt: int
    metadata: Optional[Dict[str, Any]] = None

class GeneratedOutfit(Outfit):
    """A generated outfit with additional metadata."""
    pass

# Export types for use in other backend modules
__all__ = [
    'Season',
    'ClothingType',
    'StyleType',
    'StyleTag',
    'StyleSubtype',
    'Color',
    'VisualAttributes',
    'ItemMetadata',
    'BasicMetadata',
    'ColorAnalysis',
    'Metadata',
    'ClothingItem',
    'Outfit',
    'GeneratedOutfit',
    'TemperatureRange',
    'Material',
    'BodyType',
    'SkinTone',
    'TemperatureCompatibility',
    'MaterialCompatibility',
    'BodyTypeCompatibility',
    'SkinToneCompatibility',
    'OutfitScoring',
    'LayerLevel',
    'WarmthFactor',
    'CoreCategory'
] 