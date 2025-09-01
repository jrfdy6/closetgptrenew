from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Set, Any, Union
from datetime import datetime
from enum import Enum
from .wardrobe import ClothingType, StyleTag, Color
from .style_engine import StyleAttributes

class BodyType(str, Enum):
    HOURGLASS = "hourglass"
    PEAR = "pear"
    APPLE = "apple"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"
    TRIANGLE = "triangle"

class ColorSeason(str, Enum):
    WARM_SPRING = "warm_spring"
    COOL_SPRING = "cool_spring"
    WARM_AUTUMN = "warm_autumn"
    COOL_AUTUMN = "cool_autumn"
    WARM_SUMMER = "warm_summer"
    COOL_SUMMER = "cool_summer"
    WARM_WINTER = "warm_winter"
    COOL_WINTER = "cool_winter"

class StyleAesthetic(str, Enum):
    CLASSIC = "classic"
    ROMANTIC = "romantic"
    MINIMALIST = "minimalist"
    BOHEMIAN = "bohemian"
    EDGY = "edgy"
    PREPPY = "preppy"
    STREETWEAR = "streetwear"
    ATHLETIC = "athletic"
    VINTAGE = "vintage"
    GRUNGE = "grunge"
    COMFORTABLE = "comfortable"
    SOPHISTICATED = "sophisticated"

class QuizQuestion(BaseModel):
    id: str
    question: str
    type: str  # "multiple_choice", "image_choice", "slider", "text"
    options: List[Dict[str, Any]]
    weight: float = 1.0
    category: str  # "aesthetic", "color", "fit", "lifestyle"

class QuizResult(BaseModel):
    user_id: str
    completed_at: Union[datetime, float] = Field(default_factory=datetime.now)
    aesthetic_scores: Dict[str, float] = Field(default_factory=dict)
    color_season: Optional[ColorSeason] = None
    body_type: Optional[BodyType] = None
    style_preferences: Dict[str, float] = Field(default_factory=dict)
    fit_preferences: Dict[str, float] = Field(default_factory=dict)
    lifestyle_factors: Dict[str, float] = Field(default_factory=dict)
    favorite_outfits: List[Dict[str, Any]] = Field(default_factory=list)
    style_formula: Optional[str] = None

    @field_validator('completed_at', mode='before')
    def convert_timestamp(cls, v, info):
        if isinstance(v, (int, float)):
            try:
                # Handle both seconds and milliseconds timestamps
                if v > 1e12:  # Likely milliseconds
                    timestamp_seconds = v / 1000.0
                else:
                    timestamp_seconds = v
                # Sanity check for reasonable timestamp range
                if 946684800 <= timestamp_seconds <= 4102444800:
                    return datetime.fromtimestamp(timestamp_seconds)
                else:
                    # Invalid timestamp, use current time
                    return datetime.utcnow()
            except (ValueError, OverflowError, OSError):
                # Conversion failed, use current time
                return datetime.utcnow()
        return v

class StyleFormula(BaseModel):
    primary_aesthetic: str
    secondary_aesthetic: Optional[str] = None
    color_season: ColorSeason
    body_type: BodyType
    fit_preferences: List[str]
    style_rules: List[str]
    avoid_patterns: List[str]
    signature_elements: List[str]

class StyleDiscoveryProfile(BaseModel):
    user_id: str
    created_at: Union[datetime, float] = Field(default_factory=datetime.now)
    last_updated: Union[datetime, float] = Field(default_factory=datetime.now)
    
    # Quiz results
    quiz_result: Optional[QuizResult] = None
    
    # Style formula
    style_formula: Optional[StyleFormula] = None
    
    # Visual references
    pinterest_boards: List[Dict[str, Any]] = Field(default_factory=list)
    instagram_saves: List[Dict[str, Any]] = Field(default_factory=list)
    selfie_analysis: Optional[Dict[str, Any]] = None
    
    # Style evolution
    style_evolution: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator('created_at', 'last_updated', mode='before')
    def convert_timestamp(cls, v, info):
        if isinstance(v, (int, float)):
            try:
                # Handle both seconds and milliseconds timestamps
                if v > 1e12:  # Likely milliseconds
                    timestamp_seconds = v / 1000.0
                else:
                    timestamp_seconds = v
                # Sanity check for reasonable timestamp range
                if 946684800 <= timestamp_seconds <= 4102444800:
                    return datetime.fromtimestamp(timestamp_seconds)
                else:
                    # Invalid timestamp, use current time
                    return datetime.utcnow()
            except (ValueError, OverflowError, OSError):
                # Conversion failed, use current time
                return datetime.utcnow()
        return v

    def generate_style_formula(self) -> StyleFormula:
        """Generate a personalized style formula based on quiz results and preferences."""
        if not self.quiz_result:
            raise ValueError("Quiz results not available")
        
        # Determine primary and secondary aesthetics
        aesthetics = sorted(
            self.quiz_result.aesthetic_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        primary_aesthetic = aesthetics[0][0]
        secondary_aesthetic = aesthetics[1][0] if len(aesthetics) > 1 and aesthetics[1][1] > 0.3 else None
        
        # Determine fit preferences based on body type and style preferences
        fit_preferences = self._determine_fit_preferences()
        
        # Generate style rules
        style_rules = self._generate_style_rules()
        
        # Determine patterns to avoid
        avoid_patterns = self._determine_avoid_patterns()
        
        # Identify signature elements
        signature_elements = self._identify_signature_elements()
        
        return StyleFormula(
            primary_aesthetic=primary_aesthetic,
            secondary_aesthetic=secondary_aesthetic,
            color_season=self.quiz_result.color_season,
            body_type=self.quiz_result.body_type,
            fit_preferences=fit_preferences,
            style_rules=style_rules,
            avoid_patterns=avoid_patterns,
            signature_elements=signature_elements
        )
    
    def _determine_fit_preferences(self) -> List[str]:
        """Determine optimal fit preferences based on body type and style preferences."""
        preferences = []
        
        if self.quiz_result.body_type == BodyType.HOURGLASS:
            preferences.extend([
                "high-rise bottoms",
                "fitted tops",
                "wrap dresses",
                "belted styles"
            ])
        elif self.quiz_result.body_type == BodyType.PEAR:
            preferences.extend([
                "A-line skirts",
                "bootcut jeans",
                "structured tops",
                "wide-leg pants"
            ])
        # Add more body type specific preferences...
        
        # Add style-specific preferences
        if "romantic" in self.quiz_result.aesthetic_scores:
            preferences.extend([
                "flowy fabrics",
                "soft draping",
                "feminine silhouettes"
            ])
        
        return list(set(preferences))
    
    def _generate_style_rules(self) -> List[str]:
        """Generate personalized style rules based on preferences and body type."""
        rules = []
        
        # Color season rules
        if self.quiz_result.color_season:
            rules.append(f"Stick to {self.quiz_result.color_season.value} color palette")
        
        # Body type rules
        if self.quiz_result.body_type:
            rules.append(f"Accentuate {self.quiz_result.body_type.value} figure")
        
        # Style preference rules
        for aesthetic, score in self.quiz_result.aesthetic_scores.items():
            if score > 0.7:
                rules.append(f"Embrace {aesthetic} elements")
        
        return rules
    
    def _determine_avoid_patterns(self) -> List[str]:
        """Determine patterns and styles to avoid based on body type and preferences."""
        avoid = []
        
        if self.quiz_result.body_type == BodyType.RECTANGLE:
            avoid.extend([
                "boxy silhouettes",
                "straight cuts",
                "horizontal stripes"
            ])
        elif self.quiz_result.body_type == BodyType.APPLE:
            avoid.extend([
                "tight waistbands",
                "crop tops",
                "horizontal stripes"
            ])
        
        return avoid
    
    def _identify_signature_elements(self) -> List[str]:
        """Identify signature style elements based on preferences and saved outfits."""
        signatures = []
        
        # Analyze Pinterest/Instagram saves
        for board in self.pinterest_boards:
            # Add common elements from saved outfits
            pass
        
        # Add style-specific signatures
        if "minimalist" in self.quiz_result.aesthetic_scores:
            signatures.extend([
                "clean lines",
                "neutral colors",
                "quality basics"
            ])
        
        return signatures
    
    def update_from_quiz(self, quiz_result: QuizResult):
        """Update profile with new quiz results."""
        self.quiz_result = quiz_result
        self.style_formula = self.generate_style_formula()
        self.last_updated = datetime.now()
        
        # Add to style evolution
        self.style_evolution.append({
            "timestamp": datetime.now(),
            "type": "quiz_completion",
            "data": quiz_result.dict()
        })
    
    def add_visual_reference(self, reference_type: str, data: Dict[str, Any]):
        """Add a visual reference (Pinterest/Instagram save or selfie)."""
        if reference_type == "pinterest":
            self.pinterest_boards.append(data)
        elif reference_type == "instagram":
            self.instagram_saves.append(data)
        elif reference_type == "selfie":
            self.selfie_analysis = data
        
        self.last_updated = datetime.now()
        
        # Add to style evolution
        self.style_evolution.append({
            "timestamp": datetime.now(),
            "type": f"visual_reference_{reference_type}",
            "data": data
        })
    
    def get_style_insights(self) -> Dict[str, Any]:
        """Get personalized style insights and recommendations."""
        if not self.style_formula:
            return {"error": "Style formula not generated"}
        
        return {
            "style_formula": self.style_formula.dict(),
            "aesthetic_breakdown": self.quiz_result.aesthetic_scores if self.quiz_result else {},
            "color_palette": self._get_color_palette(),
            "fit_guide": self._get_fit_guide(),
            "style_evolution": self.style_evolution[-5:] if self.style_evolution else []
        }
    
    def _get_color_palette(self) -> Dict[str, List[str]]:
        """Get recommended color palette based on color season."""
        if not self.quiz_result or not self.quiz_result.color_season:
            return {}
        
        # Define color palettes for each season
        color_palettes = {
            ColorSeason.WARM_SPRING: {
                "primary": ["coral", "peach", "warm yellow", "sage green"],
                "secondary": ["warm brown", "cream", "soft blue"],
                "accent": ["terracotta", "gold", "warm pink"]
            },
            # Add more color season palettes...
        }
        
        return color_palettes.get(self.quiz_result.color_season, {})
    
    def _get_fit_guide(self) -> Dict[str, List[str]]:
        """Get personalized fit guide based on body type and preferences."""
        if not self.quiz_result or not self.quiz_result.body_type:
            return {}
        
        # Define fit guides for each body type
        fit_guides = {
            BodyType.HOURGLASS: {
                "recommended": [
                    "fitted tops that highlight waist",
                    "high-waisted bottoms",
                    "wrap dresses",
                    "belted styles"
                ],
                "avoid": [
                    "boxy silhouettes",
                    "oversized tops",
                    "low-rise bottoms"
                ]
            },
            # Add more body type guides...
        }
        
        return fit_guides.get(self.quiz_result.body_type, {}) 