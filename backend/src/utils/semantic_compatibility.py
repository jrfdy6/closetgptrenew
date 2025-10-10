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
    req = requested_style.lower().replace(' ', '_')  # Normalize spaces to underscores
    # exact or contained
    if req in [s.lower().replace(' ', '_') for s in item_styles]:
        return True
    # check group compatibility
    compat_set = set(STYLE_COMPATIBILITY.get(req, []))
    for it in item_styles:
        if it.lower().replace(' ', '_') in compat_set:
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
        'confident': ['confident', 'bold', 'statement', 'vibrant', 'expressive'],
        'relaxed': ['relaxed', 'calm', 'laidback', 'casual', 'neutral'],
        'calm': ['calm', 'relaxed', 'peaceful', 'serene', 'neutral'],
        'professional': ['professional', 'polished', 'sophisticated', 'elegant', 'refined'],
        'polished': ['polished', 'professional', 'sophisticated', 'elegant', 'refined'],
        'romantic': ['romantic', 'soft', 'elegant', 'feminine', 'delicate'],
        'soft': ['soft', 'romantic', 'gentle', 'delicate', 'feminine'],
        'casual': ['casual', 'relaxed', 'comfortable', 'easy', 'neutral'],
        'neutral': ['neutral', 'casual', 'relaxed', 'calm', 'balanced'],
        # extend as needed
    }
    if rm in [m.lower() for m in item_moods]:
        return True
    allowed = set(MOOD_COMPAT.get(rm, []))
    return any(m.lower() in allowed for m in item_moods)


def occasion_matches(requested_occasion: Optional[str], item_occasions: List[str]) -> bool:
    """Check if item occasions match the requested occasion with semantic compatibility."""
    import logging
    logger = logging.getLogger(__name__)
    
    # DEPLOYMENT CHECK: This log confirms we're running the latest code
    logger.warning(f"🚀 OCCASION_MATCHES CALLED - VERSION: 2025-10-10-v3 - requested='{requested_occasion}', items={item_occasions}")
    
    if not requested_occasion:
        return True
    
    ro = requested_occasion.lower().replace(' ', '_')  # Normalize spaces to underscores
    
    # Log what we're matching
    logger.info(f"🔍 SEMANTIC MATCH: requested='{requested_occasion}' (normalized='{ro}'), item_occasions={item_occasions}")
    
    # Direct match check
    normalized_item_occasions = [o.lower().replace(' ', '_') for o in item_occasions]
    if ro in normalized_item_occasions:
        logger.info(f"✅ SEMANTIC: Direct match found: '{ro}' in {normalized_item_occasions}")
        return True
    
    # Fallback compatibility check
    FALLBACKS: Dict[str, List[str]] = {
        'athletic': ['casual', 'everyday', 'sport', 'athletic', 'workout'],
        'casual': ['everyday', 'casual', 'relaxed', 'weekend'],
        'business': ['business', 'business_casual', 'formal', 'smart_casual'],
        'formal': ['formal', 'business', 'elegant', 'sophisticated'],
        'everyday': ['everyday', 'casual', 'relaxed', 'comfortable'],
        'weekend': ['weekend', 'casual', 'relaxed', 'everyday'],
        'work': ['work', 'business', 'business_casual', 'professional'],
        'professional': ['professional', 'business', 'business_casual', 'work'],
    }
    fallback = set(FALLBACKS.get(ro, []))
    logger.info(f"🔍 SEMANTIC: fallback set for '{ro}' = {fallback}")
    
    for o in item_occasions:
        normalized_o = o.lower().replace(' ', '_')
        if normalized_o in fallback:
            logger.info(f"✅ SEMANTIC: Fallback match! '{o}' (normalized='{normalized_o}') matches '{requested_occasion}'")
            return True
    
    logger.warning(f"❌ SEMANTIC: NO MATCH - '{requested_occasion}' not compatible with {item_occasions}")
    return False
