from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
from datetime import datetime
from pydantic import validator
from .profile import UserProfile
from .weather import WeatherData
import uuid
import time
from .style_types import StyleType

class OutfitPiece(BaseModel):
    itemId: str
    name: str
    type: str
    reason: str
    dominantColors: List[str]
    style: List[str]
    occasion: List[str]
    imageUrl: str

class OutfitContext(BaseModel):
    wardrobe: List[ClothingItem]
    weather: WeatherData
    occasion: str
    user_profile: UserProfile
    season: Optional[Season] = None
    baseItem: Optional[ClothingItem] = None
    likedOutfits: List[str] = []
    trendingStyles: List[str] = []
    style_profile: Optional[Dict[str, Any]] = None

    @field_validator('wardrobe', mode='before')
    def convert_wardrobe_colors(cls, v, info):
        if not isinstance(v, list):
            return v
        
        converted_items = []
        for item in v:
            if isinstance(item, dict):
                # Create a copy of the item to avoid modifying the original
                item_copy = item.copy()
                
                # Handle colorAnalysis in metadata
                if 'metadata' in item_copy and 'colorAnalysis' in item_copy['metadata']:
                    color_analysis = item_copy['metadata']['colorAnalysis']
                    
                    # Convert dominant colors
                    if 'dominant' in color_analysis:
                        color_analysis['dominant'] = [
                            {"name": color, "hex": "#000000", "rgb": [0, 0, 0]} 
                            if isinstance(color, str) else color 
                            for color in color_analysis['dominant']
                        ]
                    
                    # Convert matching colors
                    if 'matching' in color_analysis:
                        color_analysis['matching'] = [
                            {"name": color, "hex": "#000000", "rgb": [0, 0, 0]} 
                            if isinstance(color, str) else color 
                            for color in color_analysis['matching']
                        ]
                
                converted_items.append(item_copy)
            else:
                converted_items.append(item)
        
        return converted_items

    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

# ===== NEW TYPES FOR OUTFIT SERVICE =====

class OutfitItem(BaseModel):
    """Simplified outfit item for the outfit service - matches actual Firebase data"""
    id: str
    name: str
    userId: str  # This matches the actual data
    subType: str  # This is what the data actually has (not category)
    type: str  # This is what the data actually has
    color: str
    imageUrl: Optional[str] = None
    style: List[str]  # This is a list in the actual data
    occasion: List[str]  # This is a list in the actual data
    dominantColors: Optional[List[Dict[str, Any]]] = None
    matchingColors: Optional[List[Dict[str, Any]]] = None
    wearCount: Optional[int] = 0
    favorite_score: Optional[float] = 0.0
    brand: Optional[str] = None
    season: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    lastWorn: Optional[float] = 0.0
    createdAt: Optional[int] = None
    updatedAt: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Legacy field mappings for backward compatibility
    category: Optional[str] = None  # Map to subType
    imageUrl: Optional[str] = None  # Keep for compatibility
    
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields

class OutfitCreate(BaseModel):
    """Data model for creating a new outfit"""
    name: str
    occasion: str
    style: str
    mood: Optional[str] = None
    items: List[OutfitItem]
    confidenceScore: Optional[float] = None
    reasoning: Optional[str] = None

class OutfitUpdate(BaseModel):
    """Data model for updating an existing outfit"""
    name: Optional[str] = None
    occasion: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    items: Optional[List[OutfitItem]] = None
    confidenceScore: Optional[float] = None
    reasoning: Optional[str] = None

class OutfitFilters(BaseModel):
    """Filters for querying outfits"""
    occasion: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class OutfitResponse(BaseModel):
    """Response model for outfit data"""
    id: str
    name: str
    occasion: str
    style: str
    mood: Optional[str] = None
    items: List[OutfitItem]
    confidenceScore: Optional[float] = None
    reasoning: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    user_id: str
    isFavorite: Optional[bool] = False
    wearCount: Optional[int] = 0
    lastWorn: Optional[datetime] = None

    @field_validator("createdAt", "updatedAt", "lastWorn", mode="before")
    @classmethod
    def normalize_datetime(cls, v):
        if isinstance(v, str):
            # Fix double timezone issue: "2025-08-27T21:10:11.828353+00:00Z" → "2025-08-27T21:10:11.828353+00:00"
            if "+00:00Z" in v:
                v = v.replace("+00:00Z", "+00:00")
            elif v.endswith("Z") and "+00:00" not in v:
                # Convert "2025-08-27T21:10:11.828353Z" → "2025-08-27T21:10:11.828353+00:00"
                v = v.replace("Z", "+00:00")
        return v

# ===== FLEXIBLE OUTFIT MODEL FOR EXISTING DATA =====

class Outfit(BaseModel):
    """Flexible outfit model that can handle existing data structure"""
    id: str
    name: str
    occasion: str
    style: str
    mood: Optional[str] = None
    items: List[OutfitItem]
    user_id: str  # Use underscore to match database field
    createdAt: Optional[Union[datetime, int]] = None
    updatedAt: Optional[Union[datetime, int]] = None
    
    @field_validator("createdAt", "updatedAt", "lastWorn", mode="before")
    @classmethod
    def normalize_datetime(cls, v):
        if isinstance(v, str):
            # Fix double timezone issue: "2025-08-27T21:10:11.828353+00:00Z" → "2025-08-27T21:10:11.828353+00:00"
            if "+00:00Z" in v:
                v = v.replace("+00:00Z", "+00:00")
            elif v.endswith("Z") and "+00:00" not in v:
                # Convert "2025-08-27T21:10:11.828353Z" → "2025-08-27T21:10:11.828353+00:00"
                v = v.replace("Z", "+00:00")
        return v
    
    # Additional fields that exist in the actual data
    description: Optional[str] = None
    season: Optional[str] = None
    styleTags: Optional[List[str]] = None
    colorHarmony: Optional[str] = None
    styleNotes: Optional[str] = None
    explanation: Optional[str] = None
    pieces: Optional[List[Any]] = None  # Some outfits have 'pieces' instead of 'items'
    validation_details: Optional[Dict[str, Any]] = None
    wardrobe_snapshot: Optional[Dict[str, Any]] = None
    system_context: Optional[Dict[str, Any]] = None
    user_session_context: Optional[Dict[str, Any]] = None
    generation_method: Optional[str] = None
    wasSuccessful: Optional[bool] = None
    baseItemId: Optional[str] = None
    validationErrors: Optional[List[str]] = None
    userFeedback: Optional[Dict[str, Any]] = None
    generation_trace: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Legacy fields for backward compatibility
    isFavorite: Optional[bool] = False
    wearCount: Optional[int] = 0
    lastWorn: Optional[Union[datetime, int]] = None
    confidenceScore: Optional[float] = None
    reasoning: Optional[str] = None
    
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields

# ===== EXISTING TYPES CONTINUE =====

class OutfitGeneratedOutfit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    items: List[Union[str, ClothingItem]]  # Allow either strings (IDs) or full ClothingItem objects
    explanation: str
    reasoning: str  # Add missing reasoning field
    pieces: List[OutfitPiece]
    styleTags: List[str]
    colorHarmony: str
    styleNotes: str
    occasion: str
    season: str
    style: str
    mood: str = "Neutral"  # Default mood
    createdAt: int = Field(default_factory=lambda: int(time.time()))
    updatedAt: int = Field(default_factory=lambda: int(time.time()))
    metadata: Optional[Dict[str, Any]] = None
    # Add missing fields that are being added during generation
    wasSuccessful: Optional[bool] = True
    baseItemId: Optional[str] = None
    validationErrors: Optional[List[str]] = []
    confidence: Optional[float] = 0.0
    userFeedback: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # 🚀 NEW: Add user_id field for filtering
    weather: Optional[Dict[str, Any]] = None  # 🚀 NEW: Add weather field for outfit context
    
    # 🚀 NEW: Comprehensive Pipeline Tracing Fields
    generation_trace: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Step-by-step pipeline execution trace")
    validation_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Detailed validation errors and fixes")
    wardrobe_snapshot: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Wardrobe state at generation time")
    system_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="System version, config, and context")
    user_session_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User session and feedback history")
    generation_method: Optional[str] = Field(default="primary", description="Method used: primary, fallback, firestore_repair, etc.")

class OutfitGenerationRequest(BaseModel):
    occasion: str
    weather: WeatherData
    wardrobe: List[ClothingItem]
    user_profile: UserProfile
    likedOutfits: List[str]
    trendingStyles: List[str]
    preferences: Optional[Dict[str, Any]] = None
    outfitHistory: Optional[List[Dict[str, Any]]] = None
    randomSeed: Optional[float] = None
    season: Optional[str] = None
    style: Optional[str] = None
    baseItemId: Optional[str] = None  # Changed from baseItem to baseItemId

    @field_validator('wardrobe', mode='before')
    def validate_wardrobe_items(cls, v, info):
        if not isinstance(v, list):
            return v
        
        validated_items = []
        for item in v:
            if isinstance(item, dict):
                # Normalize type to match ClothingType enum values
                if 'type' in item and isinstance(item['type'], str):
                    from src.services.robust_hydrator import normalize_item_type_to_enum
                    item['type'] = normalize_item_type_to_enum(item['type'], item.get('name', ''))
                validated_items.append(ClothingItem(**item))
            else:
                validated_items.append(item)
        return validated_items

    @property
    def user_id(self) -> str:
        return self.user_profile.id

# Export types for use in other backend modules
__all__ = [
    'OutfitContext',
    'OutfitGeneratedOutfit',
    'OutfitPiece',
    'OutfitGenerationRequest',
    'WeatherData',
    'Outfit'
] 
