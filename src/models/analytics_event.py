from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ItemInteractionType(str, Enum):
    VIEW = "view"
    EDIT = "edit"
    SELECT = "select"
    OUTFIT_GENERATED = "outfit_generated"
    BASE_ITEM_USED = "base_item_used"
    FEEDBACK_RECEIVED = "feedback_received"
    FAVORITE_TOGGLE = "favorite_toggle"

class AnalyticsEvent(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID (if available)")
    event_type: str = Field(..., description="Type of event, e.g. 'sign_in', 'outfit_generated', 'error'")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp (UTC)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")
    
    # Item-specific analytics fields (for item tracking)
    item_id: Optional[str] = Field(None, description="ID of the clothing item (for item analytics)")
    interaction_type: Optional[ItemInteractionType] = Field(None, description="Type of item interaction")
    outfit_id: Optional[str] = Field(None, description="ID of the outfit (for outfit-related events)")
    was_base_item: Optional[bool] = Field(None, description="Whether item was used as base item")
    feedback_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating given to outfit containing this item")
    feedback_type: Optional[str] = Field(None, description="Type of feedback (like, dislike, issue)")
    
    # Favorite scoring fields
    favorite_score: Optional[float] = Field(None, description="Calculated favorite score for the item")
    outfit_usage_score: Optional[float] = Field(None, description="Score based on outfit usage")
    feedback_score: Optional[float] = Field(None, description="Score based on user feedback")
    interaction_score: Optional[float] = Field(None, description="Score based on user interactions")
    style_preference_score: Optional[float] = Field(None, description="Score based on style preferences")
    base_item_score: Optional[float] = Field(None, description="Score based on base item usage") 