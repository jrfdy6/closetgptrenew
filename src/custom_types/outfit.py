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

class Outfit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    items: List[OutfitPiece]
    occasion: str
    season: str
    style: str
    styleTags: List[str]
    colorHarmony: str
    styleNotes: str
    createdAt: int = Field(default_factory=lambda: int(time.time()))
    updatedAt: int = Field(default_factory=lambda: int(time.time()))

class OutfitGeneratedOutfit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    items: List[Union[str, ClothingItem]]  # Allow either strings (IDs) or full ClothingItem objects
    explanation: str
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
    userFeedback: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # 🚀 NEW: Add user_id field for filtering
    flat_lay_status: Optional[str] = None
    flat_lay_url: Optional[str] = None
    flat_lay_error: Optional[str] = None
    flatLayStatus: Optional[str] = None
    flatLayUrl: Optional[str] = None
    flatLayError: Optional[str] = None
    flat_lay_status: Optional[str] = None
    flat_lay_url: Optional[str] = None
    flat_lay_error: Optional[str] = None
    
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
    baseItem: Optional[ClothingItem] = None

    @field_validator('wardrobe', mode='before')
    def validate_wardrobe_items(cls, v, info):
        if not isinstance(v, list):
            return v
        
        validated_items = []
        for item in v:
            if isinstance(item, dict):
                # Convert type to lowercase if it's a string
                if 'type' in item and isinstance(item['type'], str):
                    item['type'] = item['type'].lower()
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
