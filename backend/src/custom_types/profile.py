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
        "calfCircumference": 0,
        "plusSize": False,
        "adaptiveNeeds": [],
        "mobilityConsiderations": [],
        "sensoryPreferences": []
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
    
    # Gamification fields
    xp: Optional[int] = 0
    level: Optional[int] = 1
    ai_fit_score: Optional[float] = 0.0
    badges: List[str] = Field(default_factory=list)
    current_challenges: Dict[str, Any] = Field(default_factory=dict)
    
    # Wardrobe tracking (cached for performance)
    wardrobeItemCount: Optional[int] = 0
    
    # Spending data for CPW calculations (8 categories)
    spending_ranges: Optional[Dict[str, str]] = Field(default_factory=lambda: {
        "tops": "unknown",
        "pants": "unknown",
        "shoes": "unknown",
        "jackets": "unknown",
        "dresses": "unknown",
        "accessories": "unknown",
        "undergarments": "unknown",
        "swimwear": "unknown"
    })
    
    # Location and timezone data (from weather API)
    location_data: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "timezone_offset": None,  # Seconds from UTC
        "timezone": None,  # IANA timezone (e.g., "America/New_York")
        "coordinates": None,  # {"lat": float, "lon": float}
        "country": None,
        "city_name": None,
        "last_location": None,
        "last_weather_fetch": None,
        "updated_at": None
    })
    
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

    @field_validator('badges', mode='before')
    def validate_badges(cls, v, info):
        """Validate badges list."""
        if v is None:
            return []
        return v

    @field_validator('current_challenges', mode='before')
    def validate_current_challenges(cls, v, info):
        """Validate current challenges dict."""
        if v is None:
            return {}
        return v

    @field_validator('spending_ranges', mode='before')
    def validate_spending_ranges(cls, v, info):
        """Validate spending ranges dict."""
        if v is None:
            return {
                "tops": "unknown",
                "pants": "unknown",
                "shoes": "unknown",
                "jackets": "unknown",
                "dresses": "unknown",
                "accessories": "unknown",
                "undergarments": "unknown",
                "swimwear": "unknown"
            }
        return v

    @field_validator('location_data', mode='before')
    def validate_location_data(cls, v, info):
        """Validate location data dict."""
        if v is None:
            return {
                "timezone_offset": None,
                "timezone": None,
                "coordinates": None,
                "country": None,
                "city_name": None,
                "last_location": None,
                "last_weather_fetch": None,
                "updated_at": None
            }
        return v

# Export types for use in other backend modules
__all__ = ['UserProfile'] 