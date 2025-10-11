"""
Semantic Compatibility Utilities
Handles semantic matching for style, mood, and occasion compatibility
"""

from typing import List, Optional, Dict, Set
from .style_compatibility_matrix import STYLE_COMPATIBILITY


# ============================================================================
# MOOD COMPATIBILITY MATRIX (Module-level for bidirectional enforcement)
# ============================================================================

MOOD_COMPAT: Dict[str, List[str]] = {
    "active": ["active", "adventurous", "dynamic", "energetic", "outdoorsy"],
    "adaptable": ["adaptable", "versatile"],
    "adventurous": [
        "active", "adventurous", "bold", "daring", "outdoorsy",
        "rugged"
    ],
    "aesthetic": ["aesthetic", "artistic"],
    "ageless": ["ageless", "timeless"],
    "all-purpose": ["all-purpose", "versatile"],
    "alternative": [
        "alternative", "different", "edgy", "individual", "unconventional",
        "unique"
    ],
    "animated": ["animated", "lively"],
    "artistic": [
        "aesthetic", "artistic", "bohemian", "creative", "eclectic",
        "expressive", "imaginative"
    ],
    "assertive": ["assertive", "confident"],
    "attention-grabbing": ["attention-grabbing", "statement"],
    "authoritative": ["authoritative", "powerful"],
    "balanced": [
        "balanced", "composed", "harmonious", "moderate", "neutral",
        "versatile"
    ],
    "basic": ["basic", "minimal", "simple"],
    "bohemian": ["artistic", "bohemian", "eclectic"],
    "bold": [
        "adventurous", "bold", "confident", "daring", "dramatic",
        "edgy", "expressive", "eye-catching", "fierce", "powerful",
        "rebellious", "statement", "striking", "strong", "vibrant"
    ],
    "bright": ["bright", "fresh", "vibrant"],
    "business-like": ["business-like", "professional"],
    "calm": [
        "calm", "gentle", "neutral", "peaceful", "relaxed",
        "serene", "soothing", "tranquil"
    ],
    "casual": [
        "casual", "chill", "comfortable", "easy", "easygoing",
        "effortless", "everyday", "informal", "laid-back", "neutral",
        "relaxed"
    ],
    "cheerful": ["cheerful", "fun", "playful"],
    "chic": [
        "chic", "elegant", "fashionable", "polished", "sophisticated",
        "stylish", "trendy"
    ],
    "chill": [
        "casual", "chill", "cool", "easygoing", "laid-back",
        "relaxed"
    ],
    "classic": [
        "classic", "elegant", "enduring", "refined", "timeless",
        "traditional"
    ],
    "classy": [
        "classy", "distinguished", "elegant", "refined", "sophisticated",
        "tasteful"
    ],
    "clean": [
        "clean", "crisp", "fresh", "minimal", "minimalist",
        "neat", "simple", "sleek"
    ],
    "colorful": ["colorful", "vibrant"],
    "comfortable": [
        "casual", "comfortable", "cozy", "easy", "easygoing",
        "everyday", "functional", "relaxed", "soft"
    ],
    "commanding": ["commanding", "powerful"],
    "composed": ["balanced", "composed", "serene"],
    "confident": [
        "assertive", "bold", "confident", "expressive", "poised",
        "powerful", "self-assured", "statement", "strong", "vibrant"
    ],
    "contemporary": ["contemporary", "current", "fresh", "modern", "up-to-date"],
    "cool": ["chill", "cool"],
    "corporate": ["corporate", "professional"],
    "cozy": [
        "comfortable", "cozy", "homey", "inviting", "snug",
        "soft", "warm"
    ],
    "creative": [
        "artistic", "creative", "expressive", "imaginative", "innovative",
        "original", "unique"
    ],
    "crisp": [
        "clean", "crisp", "fresh", "neat", "polished",
        "sharp"
    ],
    "cultured": ["cultured", "refined", "sophisticated"],
    "current": ["contemporary", "current", "modern"],
    "daring": [
        "adventurous", "bold", "daring", "edgy", "fearless",
        "fierce", "rebellious"
    ],
    "defiant": ["defiant", "rebellious"],
    "delicate": [
        "delicate", "feminine", "fragile", "gentle", "romantic",
        "soft", "subtle"
    ],
    "different": ["alternative", "different", "unconventional"],
    "distinctive": ["distinctive", "individual", "unique"],
    "distinguished": ["classy", "distinguished", "refined"],
    "diverse": ["diverse", "eclectic"],
    "dramatic": [
        "bold", "dramatic", "eye-catching", "fierce", "statement",
        "striking", "theatrical"
    ],
    "dreamy": [
        "dreamy", "ethereal", "imaginative", "romantic", "soft",
        "whimsical"
    ],
    "durable": ["durable", "rugged"],
    "dynamic": [
        "active", "dynamic", "energetic", "powerful", "spirited",
        "vigorous"
    ],
    "easy": [
        "casual", "comfortable", "easy", "effortless", "relaxed",
        "simple"
    ],
    "easygoing": [
        "casual", "chill", "comfortable", "easygoing", "laid-back",
        "relaxed"
    ],
    "eclectic": [
        "artistic", "bohemian", "diverse", "eclectic", "mixed",
        "varied"
    ],
    "edgy": [
        "alternative", "bold", "daring", "edgy", "fierce",
        "rebellious", "unconventional"
    ],
    "efficient": ["efficient", "functional", "practical"],
    "effortless": [
        "casual", "easy", "effortless", "natural", "simple",
        "uncomplicated"
    ],
    "elegant": [
        "chic", "classic", "classy", "elegant", "feminine",
        "graceful", "luxurious", "polished", "professional", "refined",
        "romantic", "sophisticated", "timeless"
    ],
    "enduring": ["classic", "enduring", "timeless"],
    "energetic": [
        "active", "dynamic", "energetic", "enthusiastic", "lively",
        "spirited", "vibrant"
    ],
    "enjoyable": ["enjoyable", "fun"],
    "entertaining": ["entertaining", "fun"],
    "enthusiastic": ["energetic", "enthusiastic", "spirited"],
    "essential": ["essential", "minimal"],
    "eternal": ["eternal", "timeless"],
    "ethereal": ["dreamy", "ethereal"],
    "everyday": [
        "casual", "comfortable", "everyday", "functional", "practical",
        "relaxed"
    ],
    "expressive": [
        "artistic", "bold", "confident", "creative", "expressive",
        "individual", "unique"
    ],
    "eye-catching": ["bold", "dramatic", "eye-catching", "statement", "striking"],
    "fashionable": ["chic", "fashionable"],
    "fearless": ["daring", "fearless"],
    "feminine": [
        "delicate", "elegant", "feminine", "graceful", "pretty",
        "romantic", "soft"
    ],
    "fierce": [
        "bold", "daring", "dramatic", "edgy", "fierce",
        "powerful", "strong"
    ],
    "flexible": ["flexible", "versatile"],
    "fluid": ["fluid", "graceful"],
    "formal": ["formal", "professional"],
    "fragile": ["delicate", "fragile"],
    "fresh": [
        "bright", "clean", "contemporary", "crisp", "fresh",
        "modern", "new", "vibrant"
    ],
    "fun": [
        "cheerful", "enjoyable", "entertaining", "fun", "lively",
        "playful", "whimsical"
    ],
    "functional": [
        "comfortable", "efficient", "everyday", "functional", "practical",
        "purposeful", "utilitarian"
    ],
    "gentle": ["calm", "delicate", "gentle", "soft"],
    "graceful": [
        "elegant", "feminine", "fluid", "graceful", "poised",
        "refined", "romantic"
    ],
    "harmonious": ["balanced", "harmonious", "peaceful"],
    "homey": ["cozy", "homey"],
    "imaginative": ["artistic", "creative", "dreamy", "imaginative", "whimsical"],
    "impressive": ["impressive", "striking"],
    "individual": [
        "alternative", "distinctive", "expressive", "individual", "original",
        "personal", "unconventional", "unique"
    ],
    "informal": ["casual", "informal"],
    "innovative": ["creative", "innovative"],
    "inviting": ["cozy", "inviting"],
    "laid-back": ["casual", "chill", "easygoing", "laid-back"],
    "laidback": ["laidback", "relaxed"],
    "lavish": ["lavish", "luxurious"],
    "lighthearted": ["lighthearted", "playful"],
    "lively": [
        "animated", "energetic", "fun", "lively", "spirited",
        "vibrant", "vivacious"
    ],
    "luxurious": [
        "elegant", "lavish", "luxurious", "opulent", "rich",
        "sophisticated"
    ],
    "masculine": ["masculine", "rugged"],
    "minimal": [
        "basic", "clean", "essential", "minimal", "minimalist",
        "simple", "understated"
    ],
    "minimalist": [
        "clean", "minimal", "minimalist", "refined", "simple",
        "understated"
    ],
    "mixed": ["eclectic", "mixed"],
    "moderate": ["balanced", "moderate"],
    "modern": [
        "contemporary", "current", "fresh", "modern", "sleek",
        "trendy", "updated"
    ],
    "modest": ["modest", "understated"],
    "multifunctional": ["multifunctional", "versatile"],
    "muted": ["muted", "soft", "subtle"],
    "natural": ["effortless", "natural"],
    "nature-loving": ["nature-loving", "outdoorsy"],
    "neat": ["clean", "crisp", "neat"],
    "neutral": [
        "balanced", "calm", "casual", "neutral", "relaxed",
        "understated", "versatile"
    ],
    "new": ["fresh", "new"],
    "nonconformist": ["nonconformist", "rebellious"],
    "nontraditional": ["nontraditional", "unconventional"],
    "one-of-a-kind": ["one-of-a-kind", "unique"],
    "opulent": ["luxurious", "opulent"],
    "original": ["creative", "individual", "original", "unique"],
    "outdoorsy": [
        "active", "adventurous", "nature-loving", "outdoorsy", "practical",
        "rugged"
    ],
    "passionate": ["passionate", "spirited"],
    "peaceful": [
        "calm", "harmonious", "peaceful", "quiet", "serene",
        "tranquil"
    ],
    "personal": ["individual", "personal"],
    "placid": ["placid", "serene"],
    "playful": [
        "cheerful", "fun", "lighthearted", "playful", "spirited",
        "whimsical"
    ],
    "poised": ["confident", "graceful", "poised"],
    "polished": [
        "chic", "crisp", "elegant", "polished", "professional",
        "put-together", "refined", "sharp", "sleek", "sophisticated"
    ],
    "powerful": [
        "authoritative", "bold", "commanding", "confident", "dynamic",
        "fierce", "powerful", "strong"
    ],
    "practical": [
        "efficient", "everyday", "functional", "outdoorsy", "practical",
        "sensible", "utilitarian"
    ],
    "pretty": ["feminine", "pretty"],
    "professional": [
        "business-like", "corporate", "elegant", "formal", "polished",
        "professional", "refined", "sophisticated"
    ],
    "purposeful": ["functional", "purposeful"],
    "put-together": ["polished", "put-together"],
    "quiet": ["peaceful", "quiet", "understated"],
    "quirky": ["quirky", "whimsical"],
    "rebellious": [
        "bold", "daring", "defiant", "edgy", "nonconformist",
        "rebellious"
    ],
    "refined": [
        "classic", "classy", "cultured", "distinguished", "elegant",
        "graceful", "minimalist", "polished", "professional", "refined",
        "sleek", "sophisticated", "subtle", "tasteful", "understated"
    ],
    "relaxed": [
        "calm", "casual", "chill", "comfortable", "easy",
        "easygoing", "everyday", "laidback", "neutral", "relaxed"
    ],
    "remarkable": ["remarkable", "striking"],
    "rich": ["luxurious", "rich"],
    "romantic": [
        "delicate", "dreamy", "elegant", "feminine", "graceful",
        "romantic", "soft", "whimsical"
    ],
    "rugged": [
        "adventurous", "durable", "masculine", "outdoorsy", "rugged",
        "sturdy", "tough"
    ],
    "self-assured": ["confident", "self-assured"],
    "sensible": ["practical", "sensible"],
    "serene": [
        "calm", "composed", "peaceful", "placid", "serene",
        "tranquil"
    ],
    "sharp": ["crisp", "polished", "sharp"],
    "simple": [
        "basic", "clean", "easy", "effortless", "minimal",
        "minimalist", "simple", "straightforward", "uncomplicated"
    ],
    "sleek": [
        "clean", "modern", "polished", "refined", "sleek",
        "smooth", "streamlined"
    ],
    "smooth": ["sleek", "smooth"],
    "snug": ["cozy", "snug"],
    "soft": [
        "comfortable", "cozy", "delicate", "dreamy", "feminine",
        "gentle", "muted", "romantic", "soft", "subtle",
        "tender"
    ],
    "soothing": ["calm", "soothing"],
    "sophisticated": [
        "chic", "classy", "cultured", "elegant", "luxurious",
        "polished", "professional", "refined", "sophisticated"
    ],
    "special": ["special", "unique"],
    "spirited": [
        "dynamic", "energetic", "enthusiastic", "lively", "passionate",
        "playful", "spirited", "vivacious"
    ],
    "statement": [
        "attention-grabbing", "bold", "confident", "dramatic", "eye-catching",
        "statement", "striking"
    ],
    "straightforward": ["simple", "straightforward"],
    "streamlined": ["sleek", "streamlined"],
    "striking": [
        "bold", "dramatic", "eye-catching", "impressive", "remarkable",
        "statement", "striking"
    ],
    "strong": ["bold", "confident", "fierce", "powerful", "strong"],
    "sturdy": ["rugged", "sturdy"],
    "stylish": ["chic", "stylish"],
    "subtle": [
        "delicate", "muted", "refined", "soft", "subtle",
        "understated"
    ],
    "tasteful": ["classy", "refined", "tasteful"],
    "tender": ["soft", "tender"],
    "theatrical": ["dramatic", "theatrical"],
    "timeless": [
        "ageless", "classic", "elegant", "enduring", "eternal",
        "timeless", "traditional"
    ],
    "tough": ["rugged", "tough"],
    "traditional": ["classic", "timeless", "traditional"],
    "tranquil": ["calm", "peaceful", "serene", "tranquil"],
    "trendy": ["chic", "modern", "trendy"],
    "uncomplicated": ["effortless", "simple", "uncomplicated"],
    "unconventional": [
        "alternative", "different", "edgy", "individual", "nontraditional",
        "unconventional", "unique"
    ],
    "understated": [
        "minimal", "minimalist", "modest", "neutral", "quiet",
        "refined", "subtle", "understated"
    ],
    "unique": [
        "alternative", "creative", "distinctive", "expressive", "individual",
        "one-of-a-kind", "original", "special", "unconventional", "unique"
    ],
    "up-to-date": ["contemporary", "up-to-date"],
    "updated": ["modern", "updated"],
    "utilitarian": ["functional", "practical", "utilitarian"],
    "varied": ["eclectic", "varied"],
    "versatile": [
        "adaptable", "all-purpose", "balanced", "flexible", "multifunctional",
        "neutral", "versatile"
    ],
    "vibrant": [
        "bold", "bright", "colorful", "confident", "energetic",
        "fresh", "lively", "vibrant", "vivid"
    ],
    "vigorous": ["dynamic", "vigorous"],
    "vivacious": ["lively", "spirited", "vivacious"],
    "vivid": ["vibrant", "vivid"],
    "warm": ["cozy", "warm"],
    "whimsical": [
        "dreamy", "fun", "imaginative", "playful", "quirky",
        "romantic", "whimsical"
    ],
}


# ============================================================================
# OCCASION FALLBACKS MATRIX (Module-level for bidirectional enforcement)
# ============================================================================

OCCASION_FALLBACKS: Dict[str, List[str]] = {
    "active": [
        "active", "athletic", "casual", "gym", "outdoor",
        "sport", "sports", "workout"
    ],
    "adventure": ["adventure", "outdoor"],
    "airplane": ["airplane", "travel"],
    "athleisure": ["athleisure", "athletic", "casual", "comfortable", "sporty"],
    "athletic": [
        "active", "athleisure", "athletic", "casual", "gym",
        "sport", "sports", "workout"
    ],
    "ball": ["ball", "formal", "gala"],
    "bar": ["bar", "night_out"],
    "beach": [
        "beach", "casual", "outdoor", "poolside", "relaxed",
        "resort", "summer", "tropical", "vacation", "warm_weather"
    ],
    "black_tie": ["black_tie", "formal", "gala"],
    "breakfast": ["breakfast", "brunch"],
    "brunch": [
        "breakfast", "brunch", "business", "business casual", "business_casual",
        "casual", "date", "dinner", "gathering", "lunch",
        "smart casual", "smart_casual", "social", "vacation", "weekend"
    ],
    "business": [
        "brunch", "business", "business_casual", "conference", "date",
        "dinner", "formal", "funeral", "interview", "meeting",
        "office", "professional", "semi-formal", "semi_formal", "smart_casual",
        "work"
    ],
    "business casual": ["brunch", "business casual", "date", "dinner", "smart_casual"],
    "business_casual": [
        "brunch", "business", "business_casual", "conference", "date",
        "dinner", "interview", "lunch", "meeting", "office",
        "professional", "smart casual", "smart_casual", "work"
    ],
    "camping": ["camping", "outdoor"],
    "casual": [
        "active", "athleisure", "athletic", "beach", "brunch",
        "casual", "comfortable", "date", "dinner", "errands",
        "everyday", "indoor", "lunch", "outdoor", "party",
        "relaxed", "resort", "shopping", "smart_casual", "sport",
        "sports", "summer", "travel", "tropical", "vacation",
        "weekend", "winter"
    ],
    "celebration": ["celebration", "party", "wedding"],
    "ceremony": ["ceremony", "formal", "funeral"],
    "church": ["church", "funeral"],
    "cocktail": [
        "cocktail", "date", "dinner", "evening", "formal",
        "gala", "night_out", "party", "semi-formal", "semi_formal",
        "wedding"
    ],
    "cold_weather": ["cold_weather", "winter"],
    "comfortable": [
        "athleisure", "casual", "comfortable", "everyday", "indoor",
        "loungewear", "relaxed", "travel", "vacation"
    ],
    "conference": [
        "business", "business_casual", "conference", "meeting", "professional",
        "work"
    ],
    "cozy": ["cozy", "winter"],
    "date": [
        "brunch", "business", "business casual", "business_casual", "casual",
        "cocktail", "date", "dinner", "evening", "lunch",
        "night_out", "party", "smart casual", "smart_casual", "wedding"
    ],
    "dinner": [
        "brunch", "business", "business casual", "business_casual", "casual",
        "cocktail", "date", "dinner", "evening", "gathering",
        "lunch", "night_out", "smart casual", "smart_casual", "social",
        "vacation"
    ],
    "errands": ["casual", "errands"],
    "evening": [
        "cocktail", "date", "dinner", "evening", "formal",
        "gala", "night_out", "party", "wedding"
    ],
    "everyday": [
        "casual", "comfortable", "everyday", "indoor", "lunch",
        "relaxed", "weekend"
    ],
    "exercise": ["exercise", "gym", "workout"],
    "fitness": ["fitness", "gym", "workout"],
    "formal": [
        "ball", "black_tie", "business", "ceremony", "cocktail",
        "evening", "formal", "funeral", "gala", "graduation",
        "interview", "opera", "professional", "semi-formal", "semi_formal",
        "wedding", "white_tie"
    ],
    "funeral": [
        "business", "ceremony", "church", "formal", "funeral",
        "memorial", "professional", "religious", "semi-formal", "semi_formal"
    ],
    "gala": [
        "ball", "black_tie", "cocktail", "evening", "formal",
        "gala"
    ],
    "garden_party": ["garden_party", "wedding"],
    "gathering": ["brunch", "dinner", "gathering"],
    "graduation": ["formal", "graduation"],
    "gym": [
        "active", "athletic", "exercise", "fitness", "gym",
        "sport", "workout"
    ],
    "hiking": ["hiking", "outdoor"],
    "home": ["home", "indoor"],
    "indoor": [
        "casual", "comfortable", "everyday", "home", "indoor",
        "winter"
    ],
    "interview": ["business", "business_casual", "formal", "interview", "professional"],
    "loungewear": ["comfortable", "loungewear"],
    "lunch": [
        "brunch", "business_casual", "casual", "date", "dinner",
        "everyday", "lunch", "weekend", "work"
    ],
    "meeting": [
        "business", "business_casual", "conference", "meeting", "professional",
        "work"
    ],
    "memorial": ["funeral", "memorial"],
    "night_out": [
        "bar", "cocktail", "date", "dinner", "evening",
        "night_out", "party"
    ],
    "office": ["business", "business_casual", "office", "professional", "work"],
    "opera": ["formal", "opera"],
    "outdoor": [
        "active", "adventure", "beach", "camping", "casual",
        "hiking", "outdoor", "summer", "vacation"
    ],
    "party": [
        "casual", "celebration", "cocktail", "date", "evening",
        "night_out", "party", "social", "wedding"
    ],
    "poolside": ["beach", "poolside", "resort"],
    "professional": [
        "business", "business_casual", "conference", "formal", "funeral",
        "interview", "meeting", "office", "professional", "work"
    ],
    "reception": ["reception", "wedding"],
    "relaxed": [
        "beach", "casual", "comfortable", "everyday", "relaxed",
        "vacation", "weekend"
    ],
    "religious": ["funeral", "religious"],
    "resort": [
        "beach", "casual", "poolside", "resort", "tropical",
        "vacation"
    ],
    "semi-formal": [
        "business", "cocktail", "formal", "funeral", "semi-formal",
        "semi_formal", "smart_casual", "wedding"
    ],
    "semi_formal": [
        "business", "cocktail", "formal", "funeral", "semi-formal",
        "semi_formal", "smart_casual", "wedding"
    ],
    "shopping": ["casual", "shopping"],
    "sightseeing": ["sightseeing", "travel", "vacation"],
    "smart casual": [
        "brunch", "business_casual", "date", "dinner", "smart casual",
        "smart_casual"
    ],
    "smart_casual": [
        "brunch", "business", "business casual", "business_casual", "casual",
        "date", "dinner", "semi-formal", "semi_formal", "smart casual",
        "smart_casual"
    ],
    "social": ["brunch", "dinner", "party", "social"],
    "sport": [
        "active", "athletic", "casual", "gym", "sport",
        "sports", "workout"
    ],
    "sports": [
        "active", "athletic", "casual", "sport", "sports",
        "workout"
    ],
    "sporty": ["athleisure", "sporty"],
    "summer": [
        "beach", "casual", "outdoor", "summer", "tropical",
        "vacation"
    ],
    "travel": [
        "airplane", "casual", "comfortable", "sightseeing", "travel",
        "vacation"
    ],
    "tropical": [
        "beach", "casual", "resort", "summer", "tropical",
        "vacation"
    ],
    "vacation": [
        "beach", "brunch", "casual", "comfortable", "dinner",
        "outdoor", "relaxed", "resort", "sightseeing", "summer",
        "travel", "tropical", "vacation"
    ],
    "warm_weather": ["beach", "warm_weather"],
    "wedding": [
        "celebration", "cocktail", "date", "evening", "formal",
        "garden_party", "party", "reception", "semi-formal", "semi_formal",
        "wedding"
    ],
    "weekend": [
        "brunch", "casual", "everyday", "lunch", "relaxed",
        "weekend"
    ],
    "white_tie": ["formal", "white_tie"],
    "winter": ["casual", "cold_weather", "cozy", "indoor", "winter"],
    "work": [
        "business", "business_casual", "conference", "lunch", "meeting",
        "office", "professional", "work"
    ],
    "workout": [
        "active", "athletic", "exercise", "fitness", "gym",
        "sport", "sports", "workout"
    ],
}


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
    
    # Direct match check
    if rm in [m.lower() for m in item_moods]:
        return True
    
    # Semantic compatibility check using module-level MOOD_COMPAT
    allowed = set(MOOD_COMPAT.get(rm, []))
    return any(m.lower() in allowed for m in item_moods)


def occasion_matches(requested_occasion: Optional[str], item_occasions: List[str]) -> bool:
    """Check if item occasions match the requested occasion with semantic compatibility."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Reduced logging to prevent Railway rate limit (500 logs/sec)
    # logger.warning(f"🚀 OCCASION_MATCHES CALLED - VERSION: 2025-10-11-COMPREHENSIVE - requested='{requested_occasion}', items={item_occasions}")
    
    if not requested_occasion:
        return True
    
    ro = requested_occasion.lower().replace(' ', '_')  # Normalize spaces to underscores
    
    # Logging disabled to prevent Railway rate limit (500 logs/sec)
    # logger.info(f"🔍 SEMANTIC MATCH: requested='{requested_occasion}' (normalized='{ro}'), item_occasions={item_occasions}")
    
    # Direct match check
    normalized_item_occasions = [o.lower().replace(' ', '_') for o in item_occasions]
    if ro in normalized_item_occasions:
        # logger.info(f"✅ SEMANTIC: Direct match found: '{ro}' in {normalized_item_occasions}")
        return True
    
    # Semantic fallback check using module-level OCCASION_FALLBACKS
    fallback = set(OCCASION_FALLBACKS.get(ro, []))
    # logger.info(f"🔍 SEMANTIC: fallback set for '{ro}' = {fallback}")
    
    for o in item_occasions:
        normalized_o = o.lower().replace(' ', '_')
        if normalized_o in fallback:
            # logger.info(f"✅ SEMANTIC: Fallback match! '{o}' (normalized='{normalized_o}') matches '{requested_occasion}'")
            return True
    
    # logger.warning(f"❌ SEMANTIC: NO MATCH - '{requested_occasion}' not compatible with {item_occasions}")
    return False
