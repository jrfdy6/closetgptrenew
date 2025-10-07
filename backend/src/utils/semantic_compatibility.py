"""
Semantic Compatibility Utilities
Handles semantic matching for style, mood, and occasion compatibility
"""

from typing import List, Optional, Dict, Set
from .style_compatibility_matrix import STYLE_COMPATIBILITY


def style_matches(requested_style: Optional[str], item_styles: List[str]) -> bool:
    """Check if item styles match the requested style with semantic compatibility."""
    if not requested_style:
        return True
    req = requested_style.lower()
    # exact or contained
    if req in [s.lower() for s in item_styles]:
        return True
    # check group compatibility
    compat_set = set(STYLE_COMPATIBILITY.get(req, []))
    for it in item_styles:
        if it.lower() in compat_set:
            return True
    return False


def mood_matches(requested_mood: Optional[str], item_moods: List[str]) -> bool:
    """Check if item moods match the requested mood with semantic compatibility."""
    if not requested_mood:
        return True  # optional filter by default
    if not item_moods or len(item_moods) == 0:
        return True  # treat missing mood as universal
    rm = requested_mood.lower()
    # small mood alias table
    MOOD_COMPAT: Dict[str, List[str]] = {
        'bold': ['bold', 'confident', 'statement', 'vibrant', 'expressive'],
        'relaxed': ['relaxed', 'calm', 'laidback', 'casual', 'neutral'],
        'romantic': ['romantic', 'soft', 'elegant'],
        # extend as needed
    }
    if rm in [m.lower() for m in item_moods]:
        return True
    allowed = set(MOOD_COMPAT.get(rm, []))
    return any(m.lower() in allowed for m in item_moods)


def occasion_matches(requested_occasion: Optional[str], item_occasions: List[str]) -> bool:
    """Check if item occasions match the requested occasion with semantic compatibility."""
    if not requested_occasion:
        return True
    ro = requested_occasion.lower()
    if ro in [o.lower() for o in item_occasions]:
        return True
    # optionally allow some fallbacks: e.g. athletic <-> casual?
    FALLBACKS: Dict[str, List[str]] = {
        'athletic': ['casual', 'everyday', 'sport'],
        'casual': ['everyday', 'casual'],
        'business': ['business', 'business casual', 'formal', 'smart casual'],
    }
    fallback = set(FALLBACKS.get(ro, []))
    return any(o.lower() in fallback for o in item_occasions)
