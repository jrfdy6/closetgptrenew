"""
Pydantic models for outfit generation and management.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, field_validator


class OutfitRequest(BaseModel):
    """Request model for outfit generation."""
    style: str
    mood: str
    occasion: str
    description: Optional[str] = None
    baseItem: Optional[Dict[str, Any]] = None
    baseItemId: Optional[str] = None  # Add baseItemId field to track user-selected base item
    wardrobe: Optional[List[Dict[str, Any]]] = []  # Add wardrobe field
    wardrobeItems: Optional[List[Dict[str, Any]]] = []  # Alternative wardrobe field name
    wardrobeCount: Optional[int] = 0  # Add wardrobeCount field
    wardrobeType: Optional[str] = "object"  # Add wardrobeType field
    weather: Optional[Dict[str, Any]] = None  # Add weather field
    
    # Additional fields from SmartWeatherOutfitGenerator
    user_profile: Optional[Dict[str, Any]] = None
    likedOutfits: Optional[List[Dict[str, Any]]] = []
    trendingStyles: Optional[List[Dict[str, Any]]] = []
    preferences: Optional[Dict[str, Any]] = None
    
    @property
    def resolved_wardrobe(self) -> List[Dict[str, Any]]:
        """Get wardrobe items, handling both wardrobe and wardrobeItems formats"""
        return self.wardrobe or self.wardrobeItems or []


class CreateOutfitRequest(BaseModel):
    """Request model for outfit creation."""
    name: str
    occasion: str
    style: str
    description: Optional[str] = None
    items: List[Dict[str, Any]]
    createdAt: Optional[int] = None


class OutfitResponse(BaseModel):
    """Response model for outfits."""
    id: str
    name: str
    style: Optional[str] = None
    mood: Optional[str] = None
    items: Optional[List[dict]] = None
    occasion: Optional[str] = None
    confidence_score: Optional[float] = None  # Keep this field but allow None values
    reasoning: Optional[str] = None
    createdAt: Optional[datetime] = None
    user_id: Optional[str] = None
    generated_at: Optional[str] = None
    wearCount: Optional[int] = 0
    lastWorn: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None  # Include generation_strategy and other metadata

    @field_validator("createdAt", mode="before")
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
