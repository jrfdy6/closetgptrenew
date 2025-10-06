"""
Semantic Compatibility Utilities
Handles semantic matching for style, mood, and occasion compatibility
"""

from typing import List, Optional, Dict, Set
from .style_compatibility_matrix import STYLE_COMPATIBILITY, style_matches as matrix_style_matches


def style_matches(requested_style: Optional[str], item_styles: List[str]) -> bool:
    """Check if item styles match the requested style with semantic compatibility."""
    # Use the comprehensive style matrix from the dedicated module
    return matrix_style_matches(requested_style, item_styles)


def mood_matches(requested_mood: Optional[str], item_moods: List[str]) -> bool:
    """Check if item moods match the requested mood with semantic compatibility."""
    if not requested_mood:
        return True
    if not item_moods:
        return True
    
    rm = requested_mood.lower()
    item_moods_lower = [m.lower() for m in item_moods]
    
    # Exact match
    if rm in item_moods_lower:
        return True
    
    # Mood compatibility matrix
    MOOD_COMPAT: Dict[str, List[str]] = {
        'bold': ['bold', 'confident', 'statement', 'vibrant', 'expressive'],
        'relaxed': ['relaxed', 'calm', 'laidback', 'casual', 'neutral'],
        'romantic': ['romantic', 'soft', 'elegant'],
    }
    
    allowed = set(MOOD_COMPAT.get(rm, []))
    return any(mood.lower() in allowed for mood in item_moods)


def occasion_matches(requested_occasion: Optional[str], item_occasions: List[str]) -> bool:
    """Check if item occasions match the requested occasion with semantic compatibility."""
    if not requested_occasion:
        return True
    
    ro = requested_occasion.lower()
    item_occasions_lower = [o.lower() for o in item_occasions]
    
    # Exact match
    if ro in item_occasions_lower:
        return True
    
    # Occasion fallback matrix
    FALLBACKS: Dict[str, List[str]] = {
        'athletic': ['casual', 'everyday', 'sport'],
        'casual': ['everyday', 'casual'],
        'business': ['business', 'business casual', 'formal', 'smart casual'],
    }
    
    fallback = set(FALLBACKS.get(ro, []))
    return any(occasion.lower() in fallback for occasion in item_occasions)
