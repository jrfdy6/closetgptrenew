from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import datetime

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    gender: Optional[str] = None
    
    # Basic preferences
    preferences: Dict[str, List[str]] = Field(default_factory=lambda: {
        "style": [],
        "colors": [],
        "occasions": []
    })
    
    # Detailed measurements
    measurements: Dict[str, Any] = Field(default_factory=lambda: {
        "height": 0,
        "weight": 0,
        "bodyType": "",
        "skinTone": None,
        "heightFeetInches": "",
        "topSize": "",
        "bottomSize": "",
        "shoeSize": "",
        "dressSize": "",
        "jeanWaist": "",
        "braSize": "",
        "inseam": "",
        "waist": "",
        "chest": "",
        "shoulderWidth": 0,
        "waistWidth": 0,
        "hipWidth": 0,
        "armLength": 0,
        "neckCircumference": 0,
        "thighCircumference": 0,
        "calfCircumference": 0
    })
    
    # Style preferences
    stylePreferences: List[str] = Field(default_factory=list)
    bodyType: str
    skinTone: Optional[str] = None
    fitPreference: Optional[str] = None
    
    # Size preferences
    sizePreference: Optional[str] = None
    
    # Color preferences
    colorPalette: Optional[Dict[str, List[str]]] = Field(default_factory=lambda: {
        "primary": [],
        "secondary": [],
        "accent": [],
        "neutral": [],
        "avoid": []
    })
    
    # Style personality scores (0-1)
    stylePersonality: Optional[Dict[str, float]] = Field(default_factory=lambda: {
        "classic": 0.5,
        "modern": 0.5,
        "creative": 0.5,
        "minimal": 0.5,
        "bold": 0.5
    })
    
    # Material preferences
    materialPreferences: Optional[Dict[str, List[str]]] = Field(default_factory=lambda: {
        "preferred": [],
        "avoid": [],
        "seasonal": {
            "spring": [],
            "summer": [],
            "fall": [],
            "winter": []
        }
    })
    
    # Fit preferences
    fitPreferences: Optional[Dict[str, str]] = Field(default_factory=lambda: {
        "tops": "regular",
        "bottoms": "regular",
        "dresses": "regular"
    })
    
    # Comfort levels (0-1)
    comfortLevel: Optional[Dict[str, float]] = Field(default_factory=lambda: {
        "tight": 0.5,
        "loose": 0.5,
        "structured": 0.5,
        "relaxed": 0.5
    })
    
    # Brand preferences
    preferredBrands: Optional[List[str]] = Field(default_factory=list)
    
    # Budget preference
    budget: Optional[str] = None
    
    # Timestamps
    createdAt: int
    updatedAt: int

    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    @field_validator('preferences', mode='before')
    def validate_preferences(cls, v, info):
        if v is None:
            return {"style": [], "colors": [], "occasions": []}
        return v

    @field_validator('measurements', mode='before')
    def validate_measurements(cls, v, info):
        if v is None:
            return {
                "height": 0,
                "weight": 0,
                "bodyType": "",
                "skinTone": None,
                "heightFeetInches": "",
                "topSize": "",
                "bottomSize": "",
                "shoeSize": "",
                "dressSize": "",
                "jeanWaist": "",
                "braSize": "",
                "inseam": "",
                "waist": "",
                "chest": "",
                "shoulderWidth": 0,
                "waistWidth": 0,
                "hipWidth": 0,
                "armLength": 0,
                "neckCircumference": 0,
                "thighCircumference": 0,
                "calfCircumference": 0
            }
        return v

    @field_validator('stylePreferences', mode='before')
    def validate_style_preferences(cls, v, info):
        if v is None:
            return []
        return v

    @field_validator('colorPalette', mode='before')
    def validate_color_palette(cls, v, info):
        if v is None:
            return {
                "primary": [],
                "secondary": [],
                "accent": [],
                "neutral": [],
                "avoid": []
            }
        return v

    @field_validator('stylePersonality', mode='before')
    def validate_style_personality(cls, v, info):
        if v is None:
            return {
                "classic": 0.5,
                "modern": 0.5,
                "creative": 0.5,
                "minimal": 0.5,
                "bold": 0.5
            }
        return v

    @field_validator('materialPreferences', mode='before')
    def validate_material_preferences(cls, v, info):
        if v is None:
            return {
                "preferred": [],
                "avoid": [],
                "seasonal": {
                    "spring": [],
                    "summer": [],
                    "fall": [],
                    "winter": []
                }
            }
        return v

    @field_validator('fitPreferences', mode='before')
    def validate_fit_preferences(cls, v, info):
        if v is None:
            return {
                "tops": "regular",
                "bottoms": "regular",
                "dresses": "regular"
            }
        return v

    @field_validator('comfortLevel', mode='before')
    def validate_comfort_level(cls, v, info):
        if v is None:
            return {
                "tight": 0.5,
                "loose": 0.5,
                "structured": 0.5,
                "relaxed": 0.5
            }
        return v

    @field_validator('preferredBrands', mode='before')
    def validate_preferred_brands(cls, v, info):
        if v is None:
            return []
        return v

    @field_validator('createdAt', 'updatedAt', mode='before')
    def convert_datetime_to_int(cls, v, info):
        """Convert Firestore datetime objects to integers."""
        if hasattr(v, 'timestamp'):
            # Handle DatetimeWithNanoseconds objects
            return int(v.timestamp() * 1000)  # Convert to milliseconds
        elif isinstance(v, str):
            # Handle string timestamps
            try:
                dt = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
                return int(dt.timestamp() * 1000)
            except:
                return v
        return v

# Export types for use in other backend modules
__all__ = ['UserProfile'] 