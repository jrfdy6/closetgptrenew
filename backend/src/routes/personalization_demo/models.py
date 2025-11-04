"""
Personalization Demo Models
==========================

Pydantic models for the personalization demo system.
Reuses models from the main outfit generator with personalization enhancements.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Reuse models from main outfit generator
from ..outfits.models import OutfitRequest, OutfitResponse

class PersonalizationDemoRequest(BaseModel):
    """Enhanced request model for personalization demo with generation mode selection."""
    occasion: str
    style: str
    mood: str
    weather: Optional[Dict[str, Any]] = None
    wardrobe: Optional[List[Dict[str, Any]]] = None
    user_profile: Optional[Dict[str, Any]] = None
    baseItemId: Optional[str] = None
    generation_mode: str = "simple-minimal"  # "simple-minimal" or "robust"

class PersonalizationDemoResponse(BaseModel):
    """Enhanced response model for personalization demo with generation details."""
    id: str
    name: str
    items: List[Dict[str, Any]]
    style: str
    occasion: str
    mood: str
    weather: Dict[str, Any]
    confidence_score: float
    personalization_score: Optional[float] = None
    personalization_applied: bool = False
    user_interactions: int = 0
    data_source: str = "personalization_demo"
    generation_mode: str
    generation_strategy: str
    metadata: Dict[str, Any]
    outfitAnalysis: Optional[Dict[str, Any]] = None  # Add detailed outfit analysis

class PersonalizationStatusResponse(BaseModel):
    """Personalization status response model."""
    user_id: str
    personalization_enabled: bool
    has_existing_data: bool
    total_interactions: int
    min_interactions_required: int
    ready_for_personalization: bool
    preferred_colors: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    favorite_items_count: int
    most_worn_items_count: int
    data_source: str
    system_parameters: Dict[str, Any]
    available_generation_modes: List[str]
