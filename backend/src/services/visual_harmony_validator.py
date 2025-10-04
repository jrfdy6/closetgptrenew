#!/usr/bin/env python3
"""
Visual Harmony Validator - Comprehensive Fashion Harmony System
=============================================================

This validator implements comprehensive visual harmony principles including:
- Color theory and harmony (complementary, analogous, triadic, monochromatic)
- Texture and fabric harmony
- Proportion and balance validation
- Style coherence and aesthetic harmony
- Pattern and print coordination
- Seasonal color harmony
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)

class ColorHarmonyType(Enum):
    """Types of color harmony schemes"""
    MONOCHROMATIC = "monochromatic"    # Single color family
    ANALOGOUS = "analogous"           # Adjacent colors on color wheel
    COMPLEMENTARY = "complementary"   # Opposite colors on color wheel
    TRIADIC = "triadic"              # Three evenly spaced colors
    TETRADIC = "tetradic"            # Four colors forming rectangle
    SPLIT_COMPLEMENTARY = "split_complementary"  # Base color + two adjacent to complement
    NEUTRAL = "neutral"              # Neutrals with one accent color
    WARM = "warm"                    # Warm color palette
    COOL = "cool"                    # Cool color palette

class TextureHarmonyType(Enum):
    """Types of texture harmony"""
    SMOOTH = "smooth"                # All smooth textures
    TEXTURED = "textured"            # Mix of textures for interest
    CONTRASTING = "contrasting"      # Deliberate texture contrast
    LAYERED = "layered"              # Layered texture complexity

class ProportionType(Enum):
    """Types of proportion balance"""
    BALANCED = "balanced"            # Well-proportioned outfit
    VOLUME_TOP = "volume_top"        # Volume on top
    VOLUME_BOTTOM = "volume_bottom"  # Volume on bottom
    FITTED = "fitted"               # All fitted pieces
    OVERSIZED = "oversized"          # All oversized pieces

@dataclass
class ColorInfo:
    """Color information for harmony analysis"""
    name: str
    hex_value: Optional[str] = None
    rgb: Optional[Tuple[int, int, int]] = None
    hue: Optional[float] = None
    saturation: Optional[float] = None
    lightness: Optional[float] = None
    temperature: Optional[str] = None  # "warm" or "cool"
    category: Optional[str] = None    # "primary", "secondary", "neutral"

@dataclass
class VisualHarmonyResult:
    """Comprehensive visual harmony analysis result"""
    overall_harmony_score: float  # 0-100
    color_harmony: Dict[str, Any]
    texture_harmony: Dict[str, Any]
    proportion_harmony: Dict[str, Any]
    style_coherence: Dict[str, Any]
    issues: List[str]
    suggestions: List[str]
    harmony_type: str
    confidence: float

class VisualHarmonyValidator:
    """
    Comprehensive visual harmony validator using fashion theory principles
    """
    
    def __init__(self):
        # Initialize color database
        self.color_database = self._initialize_color_database()
        
        # Initialize texture database
        self.texture_database = self._initialize_texture_database()
        
        # Initialize style harmony rules
        self.style_harmony_rules = self._initialize_style_harmony_rules()
        
        # Initialize proportion rules
        self.proportion_rules = self._initialize_proportion_rules()
    
    def _initialize_color_database(self) -> Dict[str, ColorInfo]:
        """Initialize comprehensive color database with fashion theory"""
        return {
            # Primary Colors
            "red": ColorInfo("red", "#FF0000", (255, 0, 0), 0, 1.0, 0.5, "warm", "primary"),
            "blue": ColorInfo("blue", "#0000FF", (0, 0, 255), 240, 1.0, 0.5, "cool", "primary"),
            "yellow": ColorInfo("yellow", "#FFFF00", (255, 255, 0), 60, 1.0, 0.5, "warm", "primary"),
            
            # Secondary Colors
            "green": ColorInfo("green", "#00FF00", (0, 255, 0), 120, 1.0, 0.5, "cool", "secondary"),
            "orange": ColorInfo("orange", "#FFA500", (255, 165, 0), 30, 1.0, 0.5, "warm", "secondary"),
            "purple": ColorInfo("purple", "#800080", (128, 0, 128), 300, 1.0, 0.25, "cool", "secondary"),
            
            # Neutral Colors
            "black": ColorInfo("black", "#000000", (0, 0, 0), 0, 0, 0, "neutral", "neutral"),
            "white": ColorInfo("white", "#FFFFFF", (255, 255, 255), 0, 0, 1, "neutral", "neutral"),
            "gray": ColorInfo("gray", "#808080", (128, 128, 128), 0, 0, 0.5, "neutral", "neutral"),
            "brown": ColorInfo("brown", "#A52A2A", (165, 42, 42), 0, 0.6, 0.4, "warm", "neutral"),
            "beige": ColorInfo("beige", "#F5F5DC", (245, 245, 220), 60, 0.1, 0.9, "neutral", "neutral"),
            "navy": ColorInfo("navy", "#000080", (0, 0, 128), 240, 1.0, 0.25, "cool", "neutral"),
            "khaki": ColorInfo("khaki", "#F0E68C", (240, 230, 140), 54, 0.4, 0.7, "neutral", "neutral"),
            
            # Fashion Colors
            "burgundy": ColorInfo("burgundy", "#800020", (128, 0, 32), 340, 1.0, 0.25, "warm", "secondary"),
            "maroon": ColorInfo("maroon", "#800000", (128, 0, 0), 0, 1.0, 0.25, "warm", "secondary"),
            "olive": ColorInfo("olive", "#808000", (128, 128, 0), 60, 1.0, 0.5, "neutral", "secondary"),
            "sage": ColorInfo("sage", "#9CAF88", (156, 175, 136), 100, 0.2, 0.6, "cool", "secondary"),
            "charcoal": ColorInfo("charcoal", "#36454F", (54, 69, 79), 200, 0.2, 0.3, "cool", "neutral"),
            "ivory": ColorInfo("ivory", "#FFFFF0", (255, 255, 240), 60, 0.06, 0.97, "neutral", "neutral"),
            "cream": ColorInfo("cream", "#F5F5DC", (245, 245, 220), 60, 0.1, 0.9, "neutral", "neutral"),
            "tan": ColorInfo("tan", "#D2B48C", (210, 180, 140), 34, 0.33, 0.69, "warm", "neutral"),
            
            # Additional fashion colors
            "pink": ColorInfo("pink", "#FFC0CB", (255, 192, 203), 350, 0.25, 0.88, "warm", "secondary"),
            "coral": ColorInfo("coral", "#FF7F50", (255, 127, 80), 16, 1.0, 0.66, "warm", "secondary"),
            "teal": ColorInfo("teal", "#008080", (0, 128, 128), 180, 1.0, 0.5, "cool", "secondary"),
            "turquoise": ColorInfo("turquoise", "#40E0D0", (64, 224, 208), 174, 0.71, 0.56, "cool", "secondary"),
            "cobalt": ColorInfo("cobalt", "#0047AB", (0, 71, 171), 215, 1.0, 0.34, "cool", "secondary"),
            "emerald": ColorInfo("emerald", "#50C878", (80, 200, 120), 140, 0.6, 0.55, "cool", "secondary"),
            "gold": ColorInfo("gold", "#FFD700", (255, 215, 0), 51, 1.0, 0.5, "warm", "secondary"),
            "silver": ColorInfo("silver", "#C0C0C0", (192, 192, 192), 0, 0, 0.75, "neutral", "neutral"),
        }
    
    def _initialize_texture_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize texture database for harmony analysis"""
        return {
            "smooth": {
                "description": "Smooth, sleek textures",
                "examples": ["silk", "satin", "leather", "cotton", "polyester", "smooth"],
                "harmony_type": TextureHarmonyType.SMOOTH,
                "formality": "formal"
            },
            "textured": {
                "description": "Textured, interesting surfaces",
                "examples": ["knit", "ribbed", "cable", "tweed", "corduroy", "textured"],
                "harmony_type": TextureHarmonyType.TEXTURED,
                "formality": "casual"
            },
            "rough": {
                "description": "Rough, natural textures",
                "examples": ["denim", "canvas", "burlap", "rough", "distressed"],
                "harmony_type": TextureHarmonyType.CONTRASTING,
                "formality": "casual"
            },
            "soft": {
                "description": "Soft, comfortable textures",
                "examples": ["cashmere", "wool", "fleece", "soft", "cozy"],
                "harmony_type": TextureHarmonyType.LAYERED,
                "formality": "casual"
            },
            "shiny": {
                "description": "Shiny, reflective surfaces",
                "examples": ["metallic", "sequin", "patent", "shiny", "glossy"],
                "harmony_type": TextureHarmonyType.CONTRASTING,
                "formality": "formal"
            }
        }
    
    def _initialize_style_harmony_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize style harmony rules"""
        return {
            "minimalist": {
                "color_palette": ["neutral", "monochromatic"],
                "texture_preference": ["smooth", "soft"],
                "proportion_preference": ["balanced", "fitted"],
                "pattern_tolerance": "low",
                "accessory_limit": 2
            },
            "maximalist": {
                "color_palette": ["triadic", "complementary", "warm", "cool"],
                "texture_preference": ["textured", "contrasting", "layered"],
                "proportion_preference": ["volume_top", "volume_bottom"],
                "pattern_tolerance": "high",
                "accessory_limit": 5
            },
            "classic": {
                "color_palette": ["neutral", "analogous"],
                "texture_preference": ["smooth", "textured"],
                "proportion_preference": ["balanced"],
                "pattern_tolerance": "medium",
                "accessory_limit": 3
            },
            "edgy": {
                "color_palette": ["complementary", "cool"],
                "texture_preference": ["rough", "contrasting"],
                "proportion_preference": ["volume_top", "fitted"],
                "pattern_tolerance": "medium",
                "accessory_limit": 4
            },
            "bohemian": {
                "color_palette": ["warm", "analogous", "earth_tones"],
                "texture_preference": ["textured", "layered"],
                "proportion_preference": ["volume_bottom", "oversized"],
                "pattern_tolerance": "high",
                "accessory_limit": 6
            }
        }
    
    def _initialize_proportion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize proportion and balance rules"""
        return {
            "balanced": {
                "description": "Well-proportioned outfit with visual balance",
                "rules": [
                    "If top is loose, bottom should be fitted",
                    "If bottom is loose, top should be fitted",
                    "Avoid both loose top and bottom",
                    "Accessories should complement, not overwhelm"
                ],
                "score_boost": 20
            },
            "volume_top": {
                "description": "Volume and interest on top half",
                "rules": [
                    "Oversized top with fitted bottom",
                    "Statement pieces on top",
                    "Minimal bottom to balance",
                    "Good for pear-shaped bodies"
                ],
                "score_boost": 15
            },
            "volume_bottom": {
                "description": "Volume and interest on bottom half",
                "rules": [
                    "Fitted top with loose bottom",
                    "Statement pieces on bottom",
                    "Minimal top to balance",
                    "Good for apple-shaped bodies"
                ],
                "score_boost": 15
            }
        }
    
    async def validate_visual_harmony(
        self, 
        items: List[Dict[str, Any]], 
        style: str, 
        occasion: str,
        context: Dict[str, Any]
    ) -> VisualHarmonyResult:
        """
        Comprehensive visual harmony validation
        
        Analyzes:
        - Color harmony and color theory
        - Texture and fabric harmony
        - Proportion and balance
        - Style coherence
        - Pattern coordination
        - Overall aesthetic harmony
        """
        logger.info(f"🎨 Starting visual harmony validation for {len(items)} items")
        
        try:
            # Extract color information
            colors = self._extract_colors(items)
            
            # Analyze color harmony
            color_harmony = await self._analyze_color_harmony(colors)
            
            # Analyze texture harmony
            texture_harmony = await self._analyze_texture_harmony(items)
            
            # Analyze proportion harmony
            proportion_harmony = await self._analyze_proportion_harmony(items)
            
            # Analyze style coherence
            style_coherence = await self._analyze_style_coherence(items, style, occasion)
            
            # Calculate overall harmony score
            overall_score = self._calculate_overall_harmony_score(
                color_harmony, texture_harmony, proportion_harmony, style_coherence
            )
            
            # Generate issues and suggestions
            issues, suggestions = self._generate_harmony_feedback(
                color_harmony, texture_harmony, proportion_harmony, style_coherence, style
            )
            
            # Determine harmony type
            harmony_type = self._determine_harmony_type(color_harmony, style)
            
            # Calculate confidence
            confidence = self._calculate_confidence(items, color_harmony, style_coherence)
            
            logger.info(f"✅ Visual harmony validation completed - Score: {overall_score:.1f}/100")
            
            return VisualHarmonyResult(
                overall_harmony_score=overall_score,
                color_harmony=color_harmony,
                texture_harmony=texture_harmony,
                proportion_harmony=proportion_harmony,
                style_coherence=style_coherence,
                issues=issues,
                suggestions=suggestions,
                harmony_type=harmony_type,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ Visual harmony validation failed: {e}")
            return VisualHarmonyResult(
                overall_harmony_score=0.0,
                color_harmony={"error": str(e)},
                texture_harmony={"error": str(e)},
                proportion_harmony={"error": str(e)},
                style_coherence={"error": str(e)},
                issues=[f"Visual harmony analysis failed: {str(e)}"],
                suggestions=["Contact support - visual harmony system needs attention"],
                harmony_type="unknown",
                confidence=0.0
            )
    
    def _extract_colors(self, items: List[Dict[str, Any]]) -> List[ColorInfo]:
        """Extract color information from items"""
        colors = []
        
        for item in items:
            item_colors = (item.get('color', '') if item else '').lower().split()
            dominant_colors = (item.get('dominantColors', []) if item else [])
            
            # Use dominant colors if available, otherwise use item color
            if dominant_colors:
                for color_name in dominant_colors:
                    color_info = self._get_color_info(color_name)
                    if color_info:
                        colors.append(color_info)
            else:
                for color_name in item_colors:
                    color_info = self._get_color_info(color_name)
                    if color_info:
                        colors.append(color_info)
        
        return colors
    
    def _get_color_info(self, color_name: str) -> Optional[ColorInfo]:
        """Get color information from database"""
        # Normalize color name
        color_name = color_name.lower().strip()
        
        # Direct lookup
        if color_name in self.color_database:
            return self.color_database[color_name]
        
        # Fuzzy matching for common variations
        color_mappings = {
            "navy": "navy",
            "navy blue": "navy",
            "dark blue": "navy",
            "light blue": "blue",
            "sky blue": "blue",
            "royal blue": "blue",
            "dark red": "maroon",
            "light red": "red",
            "pink": "pink",
            "rose": "pink",
            "light green": "green",
            "dark green": "green",
            "forest green": "green",
            "olive green": "olive",
            "sage green": "sage",
            "light brown": "tan",
            "dark brown": "brown",
            "chocolate": "brown",
            "cream": "cream",
            "off white": "cream",
            "ivory": "ivory",
            "light gray": "gray",
            "dark gray": "charcoal",
            "charcoal": "charcoal",
            "silver": "silver",
            "gold": "gold",
            "metallic": "silver"
        }
        
        mapped_color = (color_mappings.get(color_name) if color_mappings else None)
        if mapped_color and mapped_color in self.color_database:
            return self.color_database[mapped_color]
        
        # Default to neutral if unknown
        return ColorInfo(color_name, category="unknown", temperature="neutral")
    
    async def _analyze_color_harmony(self, colors: List[ColorInfo]) -> Dict[str, Any]:
        """Analyze color harmony using color theory"""
        if len(colors) < 2:
            return {
                "harmony_type": "insufficient_colors",
                "score": 50,
                "analysis": "Not enough colors to analyze harmony"
            }
        
        # Count color categories
        neutrals = [c for c in colors if c.category == "neutral"]
        warm_colors = [c for c in colors if c.temperature == "warm"]
        cool_colors = [c for c in colors if c.temperature == "cool"]
        unique_colors = list(set([c.name for c in colors]))
        
        # Determine harmony type
        harmony_type = self._determine_color_harmony_type(colors)
        
        # Calculate harmony score
        score = self._calculate_color_harmony_score(colors, harmony_type)
        
        # Analyze color balance
        balance_analysis = self._analyze_color_balance(colors)
        
        return {
            "harmony_type": harmony_type.value,
            "score": score,
            "unique_colors": len(unique_colors),
            "neutrals": len(neutrals),
            "warm_colors": len(warm_colors),
            "cool_colors": len(cool_colors),
            "balance": balance_analysis,
            "color_palette": [c.name for c in colors]
        }
    
    def _determine_color_harmony_type(self, colors: List[ColorInfo]) -> ColorHarmonyType:
        """Determine the type of color harmony"""
        if len(colors) < 2:
            return ColorHarmonyType.NEUTRAL
        
        unique_colors = list(set([c.name for c in colors]))
        
        # Monochromatic - same color family
        if len(unique_colors) == 1:
            return ColorHarmonyType.MONOCHROMATIC
        
        # Neutral - mostly neutrals with one accent
        neutrals = [c for c in colors if c.category == "neutral"]
        if len(neutrals) >= len(colors) - 1:
            return ColorHarmonyType.NEUTRAL
        
        # Warm or Cool palette
        warm_colors = [c for c in colors if c.temperature == "warm"]
        cool_colors = [c for c in colors if c.temperature == "cool"]
        
        if len(warm_colors) >= len(colors) * 0.8:
            return ColorHarmonyType.WARM
        elif len(cool_colors) >= len(colors) * 0.8:
            return ColorHarmonyType.COOL
        
        # Analogous - adjacent colors (simplified)
        if len(unique_colors) <= 3:
            return ColorHarmonyType.ANALOGOUS
        
        # Complementary - opposite colors (simplified)
        if len(unique_colors) == 2:
            return ColorHarmonyType.COMPLEMENTARY
        
        # Default to analogous for multiple colors
        return ColorHarmonyType.ANALOGOUS
    
    def _calculate_color_harmony_score(self, colors: List[ColorInfo], harmony_type: ColorHarmonyType) -> float:
        """Calculate color harmony score"""
        base_score = 70  # Base score for having colors
        
        # Bonus for good harmony types
        harmony_bonuses = {
            ColorHarmonyType.MONOCHROMATIC: 20,
            ColorHarmonyType.NEUTRAL: 15,
            ColorHarmonyType.ANALOGOUS: 10,
            ColorHarmonyType.COMPLEMENTARY: 15,
            ColorHarmonyType.WARM: 5,
            ColorHarmonyType.COOL: 5,
            ColorHarmonyType.TRIADIC: 10
        }
        
        base_score += (harmony_bonuses.get(harmony_type, 0) if harmony_bonuses else 0)
        
        # Penalty for too many colors
        unique_colors = len(set([c.name for c in colors]))
        if unique_colors > 4:
            base_score -= (unique_colors - 4) * 5
        
        # Bonus for including neutrals
        neutrals = len([c for c in colors if c.category == "neutral"])
        if neutrals > 0:
            base_score += min(neutrals * 5, 15)
        
        return min(max(base_score, 0), 100)
    
    def _analyze_color_balance(self, colors: List[ColorInfo]) -> Dict[str, Any]:
        """Analyze color balance and distribution"""
        warm_colors = [c for c in colors if c.temperature == "warm"]
        cool_colors = [c for c in colors if c.temperature == "cool"]
        neutrals = [c for c in colors if c.category == "neutral"]
        
        return {
            "warm_cool_balance": len(warm_colors) / max(len(cool_colors), 1),
            "neutral_ratio": len(neutrals) / len(colors) if colors else 0,
            "is_balanced": abs(len(warm_colors) - len(cool_colors)) <= 1,
            "has_neutrals": len(neutrals) > 0
        }
    
    async def _analyze_texture_harmony(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze texture harmony"""
        textures = []
        
        for item in items:
            item_textures = self._identify_textures(item)
            textures.extend(item_textures)
        
        if not textures:
            return {
                "harmony_type": "unknown",
                "score": 50,
                "analysis": "No texture information available"
            }
        
        # Determine texture harmony type
        texture_types = set(textures)
        if len(texture_types) == 1:
            harmony_type = TextureHarmonyType.SMOOTH
        elif len(texture_types) <= 2:
            harmony_type = TextureHarmonyType.TEXTURED
        else:
            harmony_type = TextureHarmonyType.LAYERED
        
        # Calculate texture harmony score
        score = self._calculate_texture_harmony_score(textures, harmony_type)
        
        return {
            "harmony_type": harmony_type.value,
            "score": score,
            "textures": textures,
            "texture_count": len(texture_types),
            "analysis": f"Found {len(texture_types)} different texture types"
        }
    
    def _identify_textures(self, item: Dict[str, Any]) -> List[str]:
        """Identify textures in an item"""
        textures = []
        
        # Check material
        material = (item.get('material', '') if item else '').lower()
        if material:
            for texture_type, info in self.texture_database.items():
                if any(example in material for example in info['examples']):
                    textures.append(texture_type)
        
        # Check name for texture clues
        name = (item.get('name', '') if item else '').lower()
        for texture_type, info in self.texture_database.items():
            if any(example in name for example in info['examples']):
                textures.append(texture_type)
        
        # Default to smooth if no texture identified
        if not textures:
            textures.append('smooth')
        
        return textures
    
    def _calculate_texture_harmony_score(self, textures: List[str], harmony_type: TextureHarmonyType) -> float:
        """Calculate texture harmony score"""
        base_score = 70
        
        # Bonus for good texture harmony
        if harmony_type == TextureHarmonyType.TEXTURED:
            base_score += 15
        elif harmony_type == TextureHarmonyType.LAYERED:
            base_score += 10
        elif harmony_type == TextureHarmonyType.SMOOTH:
            base_score += 5
        
        # Penalty for too many different textures
        unique_textures = len(set(textures))
        if unique_textures > 4:
            base_score -= (unique_textures - 4) * 10
        
        return min(max(base_score, 0), 100)
    
    async def _analyze_proportion_harmony(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze proportion and balance"""
        proportions = self._identify_proportions(items)
        
        # Determine proportion type
        proportion_type = self._determine_proportion_type(proportions)
        
        # Calculate proportion score
        score = self._calculate_proportion_score(proportions, proportion_type)
        
        return {
            "proportion_type": proportion_type.value,
            "score": score,
            "analysis": proportions,
            "is_balanced": proportion_type == ProportionType.BALANCED
        }
    
    def _identify_proportions(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify proportions in outfit"""
        proportions = {
            "fitted_items": 0,
            "loose_items": 0,
            "oversized_items": 0,
            "top_items": 0,
            "bottom_items": 0,
            "accessory_items": 0
        }
        
        for item in items:
            item_type = (item.get('type', '') if item else '').lower()
            name = (item.get('name', '') if item else '').lower()
            
            # Count by type
            if item_type in ['shirt', 'top', 'blouse', 'sweater', 'jacket']:
                proportions["top_items"] += 1
            elif item_type in ['pants', 'shorts', 'skirt', 'jeans']:
                proportions["bottom_items"] += 1
            elif item_type in ['shoes', 'belt', 'bag', 'accessory']:
                proportions["accessory_items"] += 1
            
            # Count by fit
            if any(word in name for word in ['fitted', 'slim', 'skinny', 'tight']):
                proportions["fitted_items"] += 1
            elif any(word in name for word in ['loose', 'relaxed', 'comfortable']):
                proportions["loose_items"] += 1
            elif any(word in name for word in ['oversized', 'baggy', 'wide']):
                proportions["oversized_items"] += 1
        
        return proportions
    
    def _determine_proportion_type(self, proportions: Dict[str, Any]) -> ProportionType:
        """Determine proportion type"""
        fitted = proportions["fitted_items"]
        loose = proportions["loose_items"]
        oversized = proportions["oversized_items"]
        top_items = proportions["top_items"]
        bottom_items = proportions["bottom_items"]
        
        # Check for balance
        if abs(fitted - loose) <= 1 and oversized == 0:
            return ProportionType.BALANCED
        
        # Check for volume patterns
        if loose > fitted and top_items > bottom_items:
            return ProportionType.VOLUME_TOP
        elif loose > fitted and bottom_items > top_items:
            return ProportionType.VOLUME_BOTTOM
        
        # Check for all fitted
        if fitted > loose and fitted > oversized:
            return ProportionType.FITTED
        
        # Check for all oversized
        if oversized > fitted and oversized > loose:
            return ProportionType.OVERSIZED
        
        return ProportionType.BALANCED
    
    def _calculate_proportion_score(self, proportions: Dict[str, Any], proportion_type: ProportionType) -> float:
        """Calculate proportion score"""
        base_score = 70
        
        # Bonus for good proportion types
        proportion_bonuses = {
            ProportionType.BALANCED: 20,
            ProportionType.VOLUME_TOP: 15,
            ProportionType.VOLUME_BOTTOM: 15,
            ProportionType.FITTED: 10,
            ProportionType.OVERSIZED: 5
        }
        
        base_score += (proportion_bonuses.get(proportion_type, 0) if proportion_bonuses else 0)
        
        # Penalty for too many items of same type
        if proportions["top_items"] > 3:
            base_score -= 10
        if proportions["bottom_items"] > 2:
            base_score -= 15
        if proportions["accessory_items"] > 4:
            base_score -= 10
        
        return min(max(base_score, 0), 100)
    
    async def _analyze_style_coherence(self, items: List[Dict[str, Any]], style: str, occasion: str) -> Dict[str, Any]:
        """Analyze style coherence"""
        style_rules = style_harmony_rules.get(style.lower() if style_harmony_rules else None), {})
        
        if not style_rules:
            return {
                "score": 60,
                "analysis": "Style rules not defined",
                "coherence": "unknown"
            }
        
        # Analyze against style rules
        coherence_score = 0
        total_checks = 0
        
        # Check color palette
        colors = self._extract_colors(items)
        color_harmony = await self._analyze_color_harmony(colors)
        preferred_palettes = (style_rules.get("color_palette", []) if style_rules else [])
        
        if color_harmony["harmony_type"] in preferred_palettes:
            coherence_score += 25
        total_checks += 1
        
        # Check texture preference
        textures = []
        for item in items:
            textures.extend(self._identify_textures(item))
        preferred_textures = (style_rules.get("texture_preference", []) if style_rules else [])
        
        texture_match = any(texture in preferred_textures for texture in textures)
        if texture_match:
            coherence_score += 25
        total_checks += 1
        
        # Check proportion preference
        proportions = self._identify_proportions(items)
        proportion_type = self._determine_proportion_type(proportions)
        preferred_proportions = (style_rules.get("proportion_preference", []) if style_rules else [])
        
        if proportion_type.value in preferred_proportions:
            coherence_score += 25
        total_checks += 1
        
        # Check pattern tolerance
        patterns = self._count_patterns(items)
        pattern_tolerance = (style_rules.get("pattern_tolerance", "medium") if style_rules else "medium")
        
        if pattern_tolerance == "high" and patterns >= 2:
            coherence_score += 25
        elif pattern_tolerance == "medium" and patterns <= 2:
            coherence_score += 25
        elif pattern_tolerance == "low" and patterns <= 1:
            coherence_score += 25
        total_checks += 1
        
        final_score = coherence_score / max(total_checks, 1) * 100
        
        return {
            "score": final_score,
            "style": style,
            "coherence": "high" if final_score >= 75 else "medium" if final_score >= 50 else "low",
            "analysis": f"Style coherence: {final_score:.1f}%"
        }
    
    def _count_patterns(self, items: List[Dict[str, Any]]) -> int:
        """Count patterned items"""
        pattern_count = 0
        pattern_keywords = ['striped', 'polka', 'checkered', 'plaid', 'floral', 'print', 'pattern']
        
        for item in items:
            name = (item.get('name', '') if item else '').lower()
            if any(keyword in name for keyword in pattern_keywords):
                pattern_count += 1
        
        return pattern_count
    
    def _calculate_overall_harmony_score(
        self, 
        color_harmony: Dict[str, Any], 
        texture_harmony: Dict[str, Any], 
        proportion_harmony: Dict[str, Any], 
        style_coherence: Dict[str, Any]
    ) -> float:
        """Calculate overall visual harmony score"""
        # Weighted average of all harmony aspects
        weights = {
            "color": 0.35,      # Color harmony is most important
            "style": 0.25,      # Style coherence is very important
            "proportion": 0.25,  # Proportion balance is very important
            "texture": 0.15     # Texture harmony is important but less critical
        }
        
        overall_score = (
            (color_harmony.get("score", 50) if color_harmony else 50) * weights["color"] +
            (style_coherence.get("score", 50) if style_coherence else 50) * weights["style"] +
            (proportion_harmony.get("score", 50) if proportion_harmony else 50) * weights["proportion"] +
            (texture_harmony.get("score", 50) if texture_harmony else 50) * weights["texture"]
        )
        
        return min(max(overall_score, 0), 100)
    
    def _generate_harmony_feedback(
        self, 
        color_harmony: Dict[str, Any], 
        texture_harmony: Dict[str, Any], 
        proportion_harmony: Dict[str, Any], 
        style_coherence: Dict[str, Any],
        style: str
    ) -> Tuple[List[str], List[str]]:
        """Generate feedback and suggestions"""
        issues = []
        suggestions = []
        
        # Color harmony feedback
        if color_harmony.get("score", 0) < 60:
            issues.append("Color harmony needs improvement")
            suggestions.append("Consider using a more cohesive color palette")
        
        if color_harmony.get("unique_colors", 0) > 4:
            issues.append("Too many different colors")
            suggestions.append("Try reducing to 3-4 main colors for better harmony")
        
        # Texture harmony feedback
        if texture_harmony.get("score", 0) < 60:
            issues.append("Texture harmony could be improved")
            suggestions.append("Consider mixing textures more thoughtfully")
        
        # Proportion harmony feedback
        if proportion_harmony.get("score", 0) < 60:
            issues.append("Proportion balance needs attention")
            suggestions.append("Try balancing fitted and loose pieces")
        
        # Style coherence feedback
        if style_coherence.get("score", 0) < 60:
            issues.append(f"Style coherence with {style} could be better")
            suggestions.append(f"Consider items that better match {style} aesthetic")
        
        # General suggestions
        if not issues:
            suggestions.append("Great visual harmony! The outfit works well together")
        
        return issues, suggestions
    
    def _determine_harmony_type(self, color_harmony: Dict[str, Any], style: str) -> str:
        """Determine overall harmony type"""
        color_type = (color_harmony.get("harmony_type", "unknown") if color_harmony else "unknown")
        return f"{style}_{color_type}"
    
    def _calculate_confidence(self, items: List[Dict[str, Any]], color_harmony: Dict[str, Any], style_coherence: Dict[str, Any]) -> float:
        """Calculate confidence in the harmony analysis"""
        base_confidence = 0.8
        
        # Reduce confidence if we have limited color information
        if color_harmony.get("unique_colors", 0) < 2:
            base_confidence -= 0.2
        
        # Reduce confidence if style coherence is low
        if style_coherence.get("score", 50) < 50:
            base_confidence -= 0.1
        
        return max(min(base_confidence, 1.0), 0.0)
