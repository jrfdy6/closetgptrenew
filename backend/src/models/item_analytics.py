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

class ItemAnalytics(BaseModel):
    item_id: str = Field(..., description="ID of the clothing item")
    user_id: str = Field(..., description="ID of the user")
    interaction_type: ItemInteractionType = Field(..., description="Type of interaction")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the interaction occurred")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context data")
    
    # For outfit generation tracking
    outfit_id: Optional[str] = Field(None, description="ID of the outfit if this was part of outfit generation")
    was_base_item: Optional[bool] = Field(None, description="Whether this item was used as a base item")
    
    # For feedback tracking
    feedback_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating given to outfit containing this item")
    feedback_type: Optional[str] = Field(None, description="Type of feedback (like, dislike, issue)")

class ItemFavoriteScore(BaseModel):
    item_id: str = Field(..., description="ID of the clothing item")
    user_id: str = Field(..., description="ID of the user")
    total_score: float = Field(..., description="Overall favorite score (0.0 to 1.0)")
    
    # Component scores
    outfit_usage_score: float = Field(0.0, description="Score based on how often item appears in outfits")
    feedback_score: float = Field(0.0, description="Score based on user feedback for outfits containing this item")
    interaction_score: float = Field(0.0, description="Score based on user interactions (views, edits, selects)")
    style_preference_score: float = Field(0.0, description="Score based on match with user's style preferences")
    base_item_score: float = Field(0.0, description="Score based on how often item is used as base item")
    
    # Usage statistics
    times_in_outfits: int = Field(0, description="Number of times item appeared in generated outfits")
    times_base_item: int = Field(0, description="Number of times item was used as base item")
    total_views: int = Field(0, description="Total number of times item was viewed")
    total_edits: int = Field(0, description="Total number of times item was edited")
    total_selects: int = Field(0, description="Total number of times item was selected")
    average_feedback_rating: float = Field(0.0, description="Average rating from feedback")
    
    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When the score was last calculated")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the score was first created")

class ItemUsageSummary(BaseModel):
    item_id: str
    user_id: str
    item_name: str
    item_type: str
    image_url: str
    
    # Usage counts
    outfit_appearances: int = 0
    base_item_uses: int = 0
    total_views: int = 0
    total_edits: int = 0
    total_selects: int = 0
    
    # Feedback data
    total_feedback: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    average_rating: float = 0.0
    
    # Style matching
    style_match_percentage: float = 0.0
    
    # Overall score
    favorite_score: float = 0.0
    rank: Optional[int] = None  # Rank among user's items 