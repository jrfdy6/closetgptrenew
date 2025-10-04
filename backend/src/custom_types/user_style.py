from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from enum import Enum
from .wardrobe import ClothingType, StyleTag, Color
from .style_engine import StyleAttributes

class FeedbackType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"
    WEAR = "wear"
    SKIP = "skip"

class ItemUsage(BaseModel):
    item_id: str
    wear_count: int = 0
    last_worn: Optional[datetime] = None
    feedback_history: List[FeedbackType] = Field(default_factory=list)
    outfit_combinations: Dict[str, int] = Field(default_factory=dict)  # item_id -> count
    style_matches: Dict[str, int] = Field(default_factory=dict)  # style -> count

class StylePreference(BaseModel):
    style: str
    confidence: float = 0.0  # 0-1 scale
    last_updated: datetime = Field(default_factory=datetime.now)
    feedback_count: int = 0
    positive_feedback: int = 0

class ColorPreference(BaseModel):
    color: str
    confidence: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)
    feedback_count: int = 0
    positive_feedback: int = 0

class MaterialPreference(BaseModel):
    material: str
    confidence: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)
    feedback_count: int = 0
    positive_feedback: int = 0

class UserStyleProfile(BaseModel):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # Style preferences
    style_preferences: Dict[str, StylePreference] = Field(default_factory=dict)
    color_preferences: Dict[str, ColorPreference] = Field(default_factory=dict)
    material_preferences: Dict[str, MaterialPreference] = Field(default_factory=dict)
    
    # Item usage tracking
    item_usage: Dict[str, ItemUsage] = Field(default_factory=dict)
    
    # Outfit feedback
    outfit_feedback: Dict[str, FeedbackType] = Field(default_factory=dict)
    
    # Style evolution metrics
    favorite_combinations: Dict[str, int] = Field(default_factory=dict)  # style combination -> count
    seasonal_preferences: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # season -> {style -> confidence}
    occasion_preferences: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # occasion -> {style -> confidence}
    
    def update_item_usage(self, item_id: str, feedback: FeedbackType, outfit_id: Optional[str] = None):
        """Update item usage statistics and feedback."""
        if item_id not in self.item_usage:
            self.item_usage[item_id] = ItemUsage(item_id=item_id)
        
        usage = self.item_usage[item_id]
        usage.feedback_history.append(feedback)
        
        if feedback == FeedbackType.WEAR:
            usage.wear_count += 1
            usage.last_worn = datetime.now()
        
        if outfit_id:
            for other_item_id in (outfit_feedback.get(outfit_id, {}) if outfit_feedback else {}):
                if other_item_id != item_id:
                    usage.outfit_combinations[other_item_id] = (outfit_combinations.get(other_item_id, 0) if outfit_combinations else 0) + 1
    
    def update_style_preference(self, style: str, feedback: FeedbackType):
        """Update style preference based on feedback."""
        if style not in self.style_preferences:
            self.style_preferences[style] = StylePreference(style=style)
        
        pref = self.style_preferences[style]
        pref.feedback_count += 1
        if feedback == FeedbackType.LIKE:
            pref.positive_feedback += 1
        elif feedback == FeedbackType.DISLIKE:
            pref.positive_feedback = max(0, pref.positive_feedback - 1)
        
        pref.confidence = pref.positive_feedback / max(1, pref.feedback_count)
        pref.last_updated = datetime.now()
    
    def get_style_insights(self) -> Dict[str, Any]:
        """Generate style insights similar to Spotify Wrapped."""
        now = datetime.now()
        last_month = now.replace(month=now.month-1 if now.month > 1 else 12)
        
        # Most worn items
        most_worn = sorted(
            self.item_usage.values(),
            key=lambda x: x.wear_count,
            reverse=True
        )[:5]
        
        # Most successful style combinations
        top_combinations = sorted(
            self.favorite_combinations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Style evolution
        style_evolution = {
            style: pref.confidence
            for style, pref in self.style_preferences.items()
            if pref.last_updated > last_month
        }
        
        # Seasonal preferences
        current_season = self._get_current_season()
        seasonal_prefs = self.(seasonal_preferences.get(current_season, {}) if seasonal_preferences else {})
        
        return {
            "most_worn_items": [item.item_id for item in most_worn],
            "top_style_combinations": top_combinations,
            "style_evolution": style_evolution,
            "seasonal_preferences": seasonal_prefs,
            "confidence_scores": {
                "style": sum(p.confidence for p in self.style_preferences.values()) / max(1, len(self.style_preferences)),
                "color": sum(p.confidence for p in self.color_preferences.values()) / max(1, len(self.color_preferences)),
                "material": sum(p.confidence for p in self.material_preferences.values()) / max(1, len(self.material_preferences))
            }
        }
    
    def _get_current_season(self) -> str:
        """Determine current season based on date."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Generate personalized style recommendations."""
        # Get underutilized items
        underutilized = [
            item_id for item_id, usage in self.item_usage.items()
            if usage.wear_count < 3 and usage.last_worn is None
        ]
        
        # Get successful style combinations
        successful_combinations = {
            combo: count for combo, count in self.favorite_combinations.items()
            if count > 2
        }
        
        # Get style preferences with high confidence
        preferred_styles = {
            style: pref.confidence
            for style, pref in self.style_preferences.items()
            if pref.confidence > 0.7
        }
        
        return {
            "underutilized_items": underutilized,
            "successful_combinations": successful_combinations,
            "preferred_styles": preferred_styles,
            "suggested_experiments": self._generate_style_experiments()
        }
    
    def _generate_style_experiments(self) -> List[Dict[str, Any]]:
        """Generate style experiment suggestions based on user preferences."""
        experiments = []
        
        # Suggest combining preferred styles
        preferred_styles = [
            style for style, pref in self.style_preferences.items()
            if pref.confidence > 0.6
        ]
        
        for i, style1 in enumerate(preferred_styles):
            for style2 in preferred_styles[i+1:]:
                if f"{style1}+{style2}" not in self.favorite_combinations:
                    experiments.append({
                        "type": "style_combination",
                        "suggestion": f"Try combining {style1} with {style2}",
                        "confidence": (self.style_preferences[style1].confidence + 
                                    self.style_preferences[style2].confidence) / 2
                    })
        
        return experiments 