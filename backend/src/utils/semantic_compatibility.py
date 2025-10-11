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
    # Mood compatibility - Expanded for better matching
    MOOD_COMPAT: Dict[str, List[str]] = {
        'bold': ['bold', 'confident', 'statement', 'vibrant', 'expressive', 'strong', 'striking', 'eye-catching'],
        'confident': ['confident', 'bold', 'statement', 'vibrant', 'expressive', 'strong', 'assertive'],
        'relaxed': ['relaxed', 'calm', 'laidback', 'casual', 'neutral', 'comfortable', 'easy'],
        'calm': ['calm', 'relaxed', 'peaceful', 'serene', 'neutral', 'tranquil'],
        'professional': ['professional', 'polished', 'sophisticated', 'elegant', 'refined', 'business-like'],
        'polished': ['polished', 'professional', 'sophisticated', 'elegant', 'refined', 'sleek'],
        'romantic': ['romantic', 'soft', 'elegant', 'feminine', 'delicate', 'graceful'],
        'soft': ['soft', 'romantic', 'gentle', 'delicate', 'feminine', 'subtle'],
        'casual': ['casual', 'relaxed', 'comfortable', 'easy', 'neutral', 'laid-back'],
        'neutral': ['neutral', 'casual', 'relaxed', 'calm', 'balanced', 'versatile'],
        'comfortable': ['comfortable', 'relaxed', 'casual', 'easy', 'cozy'],
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
    logger.warning(f"🚀 OCCASION_MATCHES CALLED - VERSION: 2025-10-11-COMPREHENSIVE - requested='{requested_occasion}', items={item_occasions}")
    
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
    
    # Comprehensive Fallback Compatibility - Expanded for all major occasions
    FALLBACKS: Dict[str, List[str]] = {
        # === PROFESSIONAL & WORK OCCASIONS ===
        'business': [
            'business', 'business_casual', 'formal', 'work', 'office', 'professional',
            'smart_casual', 'brunch', 'dinner', 'date',
            'conference', 'interview', 'meeting',
            'semi-formal', 'semi_formal'
        ],
        'business_casual': [
            'business_casual', 'business', 'work', 'office', 'professional',
            'smart_casual', 'smart casual',
            'brunch', 'dinner', 'lunch', 'date',
            'conference', 'meeting', 'interview'
        ],
        'work': ['work', 'business', 'business_casual', 'professional', 'office', 'meeting'],
        'office': ['office', 'work', 'business', 'business_casual', 'professional'],
        'professional': ['professional', 'business', 'business_casual', 'work', 'office', 'formal'],
        'interview': ['interview', 'business', 'professional', 'formal', 'business_casual'],
        'conference': ['conference', 'business', 'professional', 'meeting', 'work'],
        'meeting': ['meeting', 'business', 'business_casual', 'professional', 'work', 'conference'],
        
        # === FORMAL & SPECIAL EVENTS ===
        'formal': [
            'formal', 'wedding', 'gala', 'ball', 'opera',
            'business', 'black_tie', 'white_tie',
            'cocktail', 'evening', 'ceremony',
            'graduation', 'semi-formal', 'semi_formal'
        ],
        'semi_formal': ['semi_formal', 'semi-formal', 'formal', 'business', 'wedding', 'cocktail'],
        'wedding': [
            'wedding', 'formal', 'semi-formal', 'semi_formal',
            'cocktail', 'evening', 'reception',
            'garden_party', 'celebration', 'party', 'date'
        ],
        'funeral': [
            'funeral', 'formal', 'semi-formal', 'semi_formal',
            'business', 'professional', 'ceremony',
            'memorial', 'church', 'religious'
        ],
        'gala': ['gala', 'formal', 'black_tie', 'evening', 'ball', 'cocktail'],
        'cocktail': ['cocktail', 'semi-formal', 'semi_formal', 'evening', 'party', 'date', 'dinner'],
        'evening': ['evening', 'dinner', 'date', 'cocktail', 'night_out', 'formal'],
        
        # === CASUAL & EVERYDAY ===
        'casual': [
            'casual', 'everyday', 'weekend', 'relaxed', 'comfortable',
            'brunch', 'dinner', 'lunch',
            'outdoor', 'indoor', 'errands', 'shopping',
            'date', 'travel', 'vacation'
        ],
        'everyday': ['everyday', 'casual', 'relaxed', 'comfortable', 'weekend'],
        'weekend': ['weekend', 'casual', 'relaxed', 'everyday', 'brunch', 'lunch'],
        'relaxed': ['relaxed', 'casual', 'everyday', 'comfortable', 'weekend'],
        'comfortable': ['comfortable', 'casual', 'relaxed', 'everyday', 'loungewear'],
        
        # === SMART CASUAL ===
        'smart_casual': [
            'smart_casual', 'smart casual', 'business_casual', 'business casual',
            'business', 'brunch', 'dinner', 'date',
            'casual', 'semi-formal', 'semi_formal'
        ],
        
        # === SOCIAL OCCASIONS ===
        'brunch': [
            'brunch', 'casual', 'smart_casual', 'smart casual',
            'business_casual', 'business casual',
            'dinner', 'lunch', 'breakfast',
            'date', 'social', 'gathering', 'weekend'
        ],
        'dinner': [
            'dinner', 'date', 'evening', 'night_out',
            'casual', 'smart_casual', 'smart casual',
            'business_casual', 'business casual',
            'brunch', 'lunch', 'cocktail', 'social', 'gathering'
        ],
        'lunch': [
            'lunch', 'brunch', 'casual', 'everyday',
            'business_casual', 'work', 'date'
        ],
        'date': [
            'date', 'dinner', 'brunch', 'lunch',
            'evening', 'night_out', 'cocktail',
            'casual', 'smart_casual', 'smart casual',
            'business_casual', 'business casual'
        ],
        'party': [
            'party', 'celebration', 'cocktail', 'evening',
            'casual', 'date', 'night_out', 'social'
        ],
        'night_out': ['night_out', 'evening', 'date', 'dinner', 'cocktail', 'party', 'bar'],
        
        # === VACATION & LEISURE ===
        'beach': [
            'beach', 'vacation', 'resort', 'tropical',
            'casual', 'relaxed', 'outdoor', 'poolside',
            'summer', 'warm_weather'
        ],
        'vacation': [
            'vacation', 'beach', 'resort', 'tropical',
            'casual', 'relaxed', 'comfortable',
            'outdoor', 'sightseeing', 'travel',
            'dinner', 'brunch'
        ],
        'travel': ['travel', 'vacation', 'casual', 'comfortable', 'airplane', 'sightseeing'],
        'resort': ['resort', 'vacation', 'beach', 'tropical', 'poolside', 'casual'],
        'tropical': ['tropical', 'beach', 'vacation', 'resort', 'summer', 'casual'],
        'outdoor': ['outdoor', 'casual', 'hiking', 'camping', 'adventure', 'active'],
        
        # === ATHLETIC & ACTIVE ===
        'athletic': ['athletic', 'sport', 'sports', 'workout', 'gym', 'active', 'casual'],
        'sport': ['sport', 'sports', 'athletic', 'active', 'workout', 'gym', 'casual'],
        'sports': ['sports', 'sport', 'athletic', 'active', 'workout', 'casual'],
        'workout': ['workout', 'gym', 'exercise', 'fitness', 'athletic', 'sport', 'active'],
        'gym': ['gym', 'workout', 'exercise', 'fitness', 'athletic', 'active'],
        'active': ['active', 'athletic', 'sport', 'workout', 'outdoor', 'casual'],
        'athleisure': ['athleisure', 'athletic', 'casual', 'comfortable', 'sporty'],
        
        # === SEASONAL & THEMED ===
        'summer': ['summer', 'beach', 'vacation', 'outdoor', 'casual', 'tropical'],
        'winter': ['winter', 'cold_weather', 'cozy', 'indoor', 'casual'],
        'indoor': ['indoor', 'casual', 'comfortable', 'everyday', 'home'],
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
