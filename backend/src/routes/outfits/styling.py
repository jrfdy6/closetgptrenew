"""
Style-related functions for outfit generation and management.
FULLY SYNCHRONIZED with frontend style list (35 styles total)
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Global exclusion debug list for tracking exclusions
exclusion_debug = []


def filter_items_by_style(items: List[Dict[str, Any]], style: str) -> List[Dict[str, Any]]:
    """Filter wardrobe items to only include those appropriate for the given style."""
    if not items or not style:
        return items
    
    style_lower = style.lower()
    
    # Define style-appropriate keywords for different styles - MATCHES FRONTEND EXACTLY
    style_filters = {
        # Academic & Intellectual (3 styles)
        'dark academia': {
            'include_keywords': ['dark', 'academia', 'academic', 'scholarly', 'vintage', 'tweed', 'plaid', 'corduroy', 'oxford', 'loafer', 'blazer', 'cardigan', 'turtleneck', 'cable knit', 'brown', 'burgundy', 'forest green', 'navy', 'beige', 'cream'],
            'exclude_keywords': ['neon', 'bright', 'athletic', 'sport', 'gym'],
            'preferred_types': ['blazer', 'cardigan', 'button-up', 'turtleneck', 'sweater', 'oxford shoes', 'loafers', 'trousers', 'pleated skirt', 'tweed jacket']
        },
        'light academia': {
            'include_keywords': ['light', 'academia', 'academic', 'scholarly', 'cream', 'beige', 'white', 'linen', 'oxford', 'loafer', 'blazer', 'cardigan', 'button-up', 'light colors', 'neutral', 'soft'],
            'exclude_keywords': ['neon', 'bright', 'athletic', 'sport', 'gym', 'dark colors'],
            'preferred_types': ['blazer', 'cardigan', 'button-up', 'linen shirt', 'sweater', 'oxford shoes', 'loafers', 'trousers', 'pleated skirt', 'light jacket']
        },
        'old money': {
            'include_keywords': ['old money', 'wealthy', 'luxury', 'classic', 'timeless', 'polo', 'cable knit', 'cashmere', 'tailored', 'golf', 'tennis', 'yacht', 'preppy', 'refined', 'elegant'],
            'exclude_keywords': ['trendy', 'fast fashion', 'athletic wear', 'gym'],
            'preferred_types': ['polo shirt', 'cable knit sweater', 'blazer', 'chinos', 'loafers', 'boat shoes', 'cashmere', 'tailored trousers']
        },
        
        # Trendy & Modern (4 styles)
        'y2k': {
            'include_keywords': ['y2k', '2000s', 'nostalgic', 'butterfly', 'low-rise', 'crop', 'mini', 'platform', 'chunky', 'metallic', 'velour', 'juicy', 'baby tee', 'rhinestone', 'pink'],
            'exclude_keywords': ['formal', 'business', 'traditional'],
            'preferred_types': ['crop top', 'low-rise jeans', 'mini skirt', 'platform shoes', 'baby tee', 'cargo pants', 'velour tracksuit']
        },
        'coastal grandmother': {
            'include_keywords': ['coastal', 'grandmother', 'linen', 'relaxed', 'effortless', 'neutral', 'beige', 'white', 'blue', 'oversized', 'breezy', 'casual', 'elegant', 'timeless'],
            'exclude_keywords': ['tight', 'formal', 'athletic', 'gym'],
            'preferred_types': ['linen shirt', 'wide-leg pants', 'oversized sweater', 'sandals', 'straw hat', 'loose dress']
        },
        'clean girl': {
            'include_keywords': ['clean girl', 'minimal', 'simple', 'fresh', 'neutral', 'slicked back', 'natural', 'effortless', 'polished', 'understated', 'basic', 'classic'],
            'exclude_keywords': ['busy', 'loud', 'flashy', 'maximalist'],
            'preferred_types': ['white tee', 'neutral sweater', 'straight jeans', 'sneakers', 'simple jewelry', 'basic pieces']
        },
        'cottagecore': {
            'include_keywords': ['cottagecore', 'cottage', 'pastoral', 'rustic', 'vintage', 'floral', 'lace', 'embroidered', 'prairie', 'gingham', 'pinafore', 'apron', 'smock', 'straw hat', 'wicker'],
            'exclude_keywords': ['modern', 'sleek', 'athletic', 'corporate'],
            'preferred_types': ['floral dress', 'pinafore', 'prairie dress', 'cardigan', 'blouse', 'midi skirt', 'apron', 'mary janes', 'clogs']
        },
        
        # Artistic & Creative (4 styles)
        'avant-garde': {
            'include_keywords': ['avant-garde', 'experimental', 'unconventional', 'artistic', 'architectural', 'sculptural', 'asymmetric', 'deconstructed', 'conceptual', 'innovative'],
            'exclude_keywords': ['basic', 'conventional', 'traditional', 'simple'],
            'preferred_types': ['sculptural pieces', 'asymmetric', 'deconstructed', 'architectural']
        },
        'artsy': {
            'include_keywords': ['artsy', 'artistic', 'creative', 'unique', 'asymmetric', 'statement', 'bold', 'colorful', 'patterned', 'mixed', 'layered', 'eclectic'],
            'exclude_keywords': ['basic', 'plain', 'corporate'],
            'preferred_types': ['statement piece', 'unique jacket', 'wide-leg pants', 'oversized', 'patterned', 'asymmetric']
        },
        'maximalist': {
            'include_keywords': ['maximalist', 'bold', 'colorful', 'patterns', 'mixed prints', 'layered', 'accessories', 'statement', 'more is more', 'eclectic', 'vibrant'],
            'exclude_keywords': ['minimal', 'simple', 'plain', 'understated'],
            'preferred_types': ['bold prints', 'statement jewelry', 'layered pieces', 'colorful', 'patterned']
        },
        'colorblock': {
            'include_keywords': ['colorblock', 'color blocking', 'bold colors', 'contrasting', 'geometric', 'blocks', 'primary colors', 'vibrant', 'modern'],
            'exclude_keywords': ['muted', 'neutral', 'monochrome', 'black and white'],
            'preferred_types': ['colorblock dress', 'contrasting pieces', 'bold colors', 'geometric patterns']
        },
        
        # Professional & Classic (4 styles)
        'business casual': {
            'include_keywords': ['business casual', 'professional', 'work', 'office', 'smart', 'polished', 'blazer', 'trousers', 'button-up', 'loafers'],
            'exclude_keywords': ['casual', 'athletic', 'sport', 'gym', 'too casual'],
            'preferred_types': ['blazer', 'dress pants', 'button-up', 'blouse', 'loafers', 'dress shoes', 'pencil skirt']
        },
        'classic': {
            'include_keywords': ['classic', 'timeless', 'traditional', 'elegant', 'sophisticated', 'refined', 'tailored', 'button', 'collared', 'oxford', 'loafer', 'chino', 'trouser'],
            'exclude_keywords': ['extremely casual', 'gym', 'workout', 'athletic wear'],
            'preferred_types': ['button-up', 'button-down', 'blazer', 'dress shirt', 'trousers', 'chinos', 'dress pants', 'oxford shoes', 'loafers', 'dress shoes']
        },
        'preppy': {
            'include_keywords': ['preppy', 'collegiate', 'classic', 'nautical', 'stripe', 'polo', 'button', 'khaki', 'blazer', 'sweater'],
            'exclude_keywords': ['grunge', 'edgy', 'distressed', 'athletic wear'],
            'preferred_types': ['polo shirt', 'button-down', 'blazer', 'sweater', 'cardigan', 'chinos', 'boat shoes', 'oxford shoes']
        },
        'urban professional': {
            'include_keywords': ['urban professional', 'modern professional', 'city', 'sleek', 'contemporary', 'polished', 'minimalist', 'tailored', 'sophisticated'],
            'exclude_keywords': ['casual', 'sloppy', 'athletic', 'gym'],
            'preferred_types': ['tailored blazer', 'modern dress', 'sleek pants', 'professional shoes', 'contemporary pieces']
        },
        
        # Urban & Street (4 styles)
        'streetwear': {
            'include_keywords': ['streetwear', 'urban', 'casual', 'trendy', 'oversized', 'graphic', 'sneaker', 'hoodie', 'jogger', 'bomber'],
            'exclude_keywords': ['formal', 'business', 'dressy', 'corporate'],
            'preferred_types': ['hoodie', 't-shirt', 'jeans', 'joggers', 'sneakers', 'bomber jacket']
        },
        'techwear': {
            'include_keywords': ['techwear', 'technical', 'functional', 'utility', 'tactical', 'waterproof', 'breathable', 'cargo', 'straps', 'black', 'futuristic'],
            'exclude_keywords': ['formal', 'dressy', 'delicate', 'vintage'],
            'preferred_types': ['technical jacket', 'cargo pants', 'utility vest', 'tactical boots', 'functional gear']
        },
        'grunge': {
            'include_keywords': ['grunge', 'flannel', 'plaid shirt', 'ripped', 'distressed', 'band tee', 'combat boots', 'oversized', 'layered', 'dark', 'worn', 'vintage tee'],
            'exclude_keywords': ['polished', 'refined', 'formal', 'preppy', 'corporate'],
            'preferred_types': ['flannel shirt', 'ripped jeans', 'band t-shirt', 'combat boots', 'oversized sweater', 'beanie']
        },
        'hipster': {
            'include_keywords': ['hipster', 'indie', 'vintage', 'retro', 'quirky', 'artisanal', 'beard', 'glasses', 'thrift', 'unique', 'alternative'],
            'exclude_keywords': ['mainstream', 'corporate', 'formal'],
            'preferred_types': ['vintage tee', 'flannel', 'skinny jeans', 'boots', 'beanie', 'vintage jacket']
        },
        
        # Feminine & Romantic (4 styles)
        'romantic': {
            'include_keywords': ['romantic', 'feminine', 'flowy', 'delicate', 'soft', 'lace', 'ruffle', 'floral', 'dress', 'skirt', 'pastel'],
            'exclude_keywords': ['harsh', 'masculine', 'athletic', 'gym', 'cargo'],
            'preferred_types': ['dress', 'skirt', 'blouse', 'heels', 'flats', 'cardigan']
        },
        'boho': {
            'include_keywords': ['boho', 'bohemian', 'flowy', 'free', 'ethnic', 'vintage', 'embroidered', 'fringe', 'maxi', 'loose', 'layered', 'natural'],
            'exclude_keywords': ['structured', 'formal', 'business', 'corporate'],
            'preferred_types': ['maxi dress', 'maxi skirt', 'loose top', 'sandals', 'boots', 'fringe']
        },
        'french girl': {
            'include_keywords': ['french girl', 'parisian', 'effortless', 'chic', 'simple', 'classic', 'striped', 'beret', 'trench', 'ballet flats', 'timeless'],
            'exclude_keywords': ['flashy', 'loud', 'overly trendy'],
            'preferred_types': ['striped shirt', 'trench coat', 'ballet flats', 'beret', 'simple dress', 'blazer']
        },
        'pinup': {
            'include_keywords': ['pinup', 'vintage', 'retro', '50s', 'polka dot', 'high waist', 'swing dress', 'rockabilly', 'pin curl', 'red lips', 'cat eye'],
            'exclude_keywords': ['modern', 'minimalist', 'athletic'],
            'preferred_types': ['swing dress', 'high-waisted', 'polka dot', 'vintage dress', 'retro shoes']
        },
        
        # Modern & Minimal (3 styles)
        'minimalist': {
            'include_keywords': ['minimalist', 'simple', 'clean', 'modern', 'sleek', 'neutral', 'monochrome', 'basic', 'plain', 'solid'],
            'exclude_keywords': ['busy', 'patterned', 'embellished', 'ornate', 'loud'],
            'preferred_types': ['basic tee', 'plain shirt', 'simple pants', 'solid color']
        },
        'modern': {
            'include_keywords': ['modern', 'contemporary', 'current', 'sleek', 'clean lines', 'minimalist', 'updated', 'fresh'],
            'exclude_keywords': ['vintage', 'outdated', 'retro', 'old-fashioned'],
            'preferred_types': ['contemporary pieces', 'modern cut', 'sleek design', 'updated classics']
        },
        'scandinavian': {
            'include_keywords': ['scandinavian', 'nordic', 'minimal', 'neutral', 'cozy', 'hygge', 'simple', 'functional', 'natural', 'muted colors'],
            'exclude_keywords': ['flashy', 'loud', 'maximalist', 'busy'],
            'preferred_types': ['neutral sweater', 'simple dress', 'minimal jewelry', 'cozy pieces']
        },
        
        # Alternative & Edgy (4 styles)
        'gothic': {
            'include_keywords': ['gothic', 'goth', 'dark', 'black', 'lace', 'velvet', 'corset', 'platform boots', 'choker', 'dark makeup'],
            'exclude_keywords': ['bright', 'pastel', 'preppy', 'corporate'],
            'preferred_types': ['black clothing', 'lace', 'velvet', 'platform boots', 'dark accessories', 'corset']
        },
        'punk': {
            'include_keywords': ['punk', 'studded', 'leather', 'spikes', 'chains', 'safety pins', 'plaid', 'tartan', 'combat boots', 'band', 'graphic', 'torn', 'ripped'],
            'exclude_keywords': ['preppy', 'formal', 'business', 'soft', 'delicate'],
            'preferred_types': ['leather jacket', 'band tee', 'ripped jeans', 'combat boots', 'studded belt', 'plaid pants']
        },
        'cyberpunk': {
            'include_keywords': ['cyberpunk', 'futuristic', 'neon', 'tech', 'metallic', 'holographic', 'led', 'cyber', 'dystopian', 'techwear'],
            'exclude_keywords': ['vintage', 'classic', 'traditional', 'natural'],
            'preferred_types': ['neon accents', 'metallic', 'tech accessories', 'futuristic pieces', 'holographic']
        },
        'edgy': {
            'include_keywords': ['edgy', 'bold', 'leather', 'studded', 'distressed', 'ripped', 'dark', 'black', 'rock', 'denim', 'boot'],
            'exclude_keywords': ['pastel', 'delicate', 'preppy', 'corporate'],
            'preferred_types': ['leather jacket', 'denim', 'boots', 'dark pants', 'black clothing']
        },
        
        # Seasonal & Lifestyle (5 styles)
        'coastal chic': {
            'include_keywords': ['coastal', 'beach', 'nautical', 'breezy', 'linen', 'white', 'blue', 'striped', 'relaxed', 'resort', 'summer'],
            'exclude_keywords': ['heavy', 'formal', 'athletic', 'gym'],
            'preferred_types': ['linen shirt', 'white dress', 'sandals', 'striped top', 'beach hat', 'lightweight']
        },
        'athleisure': {
            'include_keywords': ['athletic', 'sport', 'gym', 'track', 'jogger', 'sweat', 'hoodie', 'sneaker', 'running', 'workout', 'yoga', 'legging', 'active', 'performance'],
            'exclude_keywords': ['dress', 'formal', 'suit', 'blazer', 'business', 'oxford', 'heel', 'dress shirt', 'tie', 'formal pants'],
            'preferred_types': ['t-shirt', 'tank', 'hoodie', 'sweatshirt', 'joggers', 'leggings', 'sweatpants', 'sneakers', 'athletic shoes', 'track jacket']
        },
        'casual cool': {
            'include_keywords': ['casual', 'cool', 'relaxed', 'effortless', 'comfortable', 'everyday', 'laid-back', 'easy'],
            'exclude_keywords': ['formal', 'business', 'dressy', 'stuffy'],
            'preferred_types': ['jeans', 't-shirt', 'sneakers', 'casual jacket', 'comfortable pieces']
        },
        'loungewear': {
            'include_keywords': ['lounge', 'comfortable', 'cozy', 'soft', 'relaxed', 'home', 'pajama', 'sweatpant', 'oversized', 'comfy'],
            'exclude_keywords': ['formal', 'business', 'structured', 'tight'],
            'preferred_types': ['sweatpants', 'oversized hoodie', 'soft tee', 'cozy cardigan', 'slippers', 'joggers']
        },
        'workout': {
            'include_keywords': ['workout', 'gym', 'athletic', 'sport', 'fitness', 'training', 'exercise', 'performance', 'activewear', 'sports bra'],
            'exclude_keywords': ['formal', 'dressy', 'casual', 'street'],
            'preferred_types': ['sports bra', 'leggings', 'tank top', 'athletic shorts', 'training shoes', 'performance wear']
        }
    }
    
    # Get filter criteria for this style
    # If style not found, use permissive default that accepts most items
    if style_lower not in style_filters:
        logger.info(f"⚠️ Unknown style '{style}' in filter, using permissive default")
        # For unknown styles, be FULLY permissive - don't exclude anything
        # Let the scoring system handle appropriateness instead
        filter_criteria = {
            'include_keywords': [],  # Accept all by default
            'exclude_keywords': [],  # No exclusions for unknown styles (occasion will handle constraints)
            'preferred_types': []  # No type restrictions
        }
    else:
        filter_criteria = style_filters[style_lower]
    
    filtered_items = []
    for item in items:
        # Safety check: handle list, dict, and object formats
        if isinstance(item, list):
            # Skip if item is a list (shouldn't happen but safety check)
            continue
        elif isinstance(item, dict):
            item_name = str(item.get('name', '') if item else '').lower()
            item_type = str(item.get('type', '') if item else '').lower()
            item_description = str(item.get('description', '') if item else '').lower()
        else:
            # Handle object format
            item_name = str(getattr(item, 'name', '')).lower()
            item_type = str(getattr(item, 'type', '')).lower()
            item_description = str(getattr(item, 'description', '')).lower()
        
        # Combine all text fields for keyword matching
        all_text = f"{item_name} {item_type} {item_description}"
        
        # Check if item should be excluded
        should_exclude = any(exclude_word in all_text for exclude_word in filter_criteria['exclude_keywords'])
        if should_exclude:
            item_name_for_log = item_name if isinstance(item, dict) else getattr(item, 'name', 'unnamed')
            logger.info(f"🚫 Excluding {item_name_for_log} from {style} style (contains excluded keywords)")
            continue
        
        # Check if item should be included (preferred types or include keywords)
        has_include_match = (
            item_type in filter_criteria['preferred_types'] or
            any(include_word in all_text for include_word in filter_criteria['include_keywords'])
        )
        
        # Be permissive: include items unless they have explicit exclusions or fail to match for restrictive styles
        if has_include_match:
            # Item explicitly matches style criteria
            filtered_items.append(item)
            item_name_for_log = item_name if isinstance(item, dict) else str(getattr(item, 'name', 'unnamed'))
            logger.info(f"✅ Including {item_name_for_log} for {style} style (explicit match)")
        else:
            # For athleisure and workout, be more restrictive - only include items that explicitly match
            if style_lower in ['athleisure', 'workout']:
                item_name_for_log = item_name if isinstance(item, dict) else str(getattr(item, 'name', 'unnamed'))
                logger.info(f"⚠️ Skipping {item_name_for_log} for {style_lower} (not explicitly athletic)")
            else:
                # For other styles (including unknown styles), include items that don't explicitly conflict
                # This ensures we don't filter out too many items
                filtered_items.append(item)
                item_name_for_log = item_name if isinstance(item, dict) else str(getattr(item, 'name', 'unnamed'))
                logger.info(f"➕ Including {item_name_for_log} for {style} style (no conflicts, permissive)")
    
    logger.info(f"🎯 Style filtering for {style}: {len(filtered_items)}/{len(items)} items kept")
    return filtered_items


def get_hard_style_exclusions(style: str, item: Dict[str, Any], mood: str = None) -> Optional[str]:
    """Check if an item should be hard-excluded from a specific style."""
    item_name = str(item.get('name', '') if item else '').lower()
    item_type = str(item.get('type', '') if item else '').lower()
    item_description = str(item.get('description', '') if item else '').lower()
    item_material = str(item.get('material', '') if item else '').lower()
    
    # Combine all text for analysis
    item_text = f"{item_name} {item_type} {item_description} {item_material}"
    
    global exclusion_debug
    
    # Define hard exclusions for specific styles
    exclusion_rules = {
        'athleisure': {
            'formal_indicators': ['formal', 'business', 'dress pants', 'suit', 'blazer', 'dress shirt', 'tie', 'oxford', 'dress shoes', 'heels'],
            'formal_materials': ['wool suit', 'silk tie', 'dress wool'],
            'formal_types': ['dress shirt', 'dress pants', 'suit jacket', 'blazer', 'tie', 'dress shoes']
        },
        'workout': {
            'non_athletic': ['formal', 'business', 'dress', 'suit', 'blazer', 'casual', 'street'],
            'inappropriate_types': ['dress', 'suit', 'blazer', 'heels', 'dress shoes']
        },
        'business casual': {
            'too_casual': ['athletic', 'sport', 'gym', 'workout', 'jogger', 'sweatpants', 'hoodie'],
            'too_casual_types': ['hoodie', 'sweatshirt', 'joggers', 'sweatpants', 'sneakers']
        },
        'gothic': {
            'bright_indicators': ['bright', 'neon', 'pastel', 'pink', 'yellow', 'preppy'],
        },
        'punk': {
            'preppy_indicators': ['preppy', 'polo', 'business', 'formal', 'corporate'],
        }
    }
    
    if style not in exclusion_rules:
        return None
    
    rules = exclusion_rules[style]
    
    # Check for exclusion indicators
    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
        "style": style,
        "mood": mood,
        "item_text": item_text,
        "checking_indicators": list(rules.values())
    })
    
    for category, indicators in rules.items():
        for indicator in indicators:
            if indicator in item_text:
                # BOLD MOOD EXCEPTION: Allow cross-style blending for fashion-forward looks
                if mood and mood.lower() == 'bold':
                    exclusion_debug.append({
                        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                        "exclusion_bypassed": f"Bold mood allows {indicator} with {style}",
                        "matched_indicator": indicator,
                        "category": category,
                        "reason": "fashion-forward bold styling"
                    })
                    logger.info(f"🎨 BOLD EXCEPTION: Allowing {indicator} with {style} for bold fashion statement")
                    continue  # Skip exclusion for bold mood
                
                exclusion_debug.append({
                    "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                    "exclusion_reason": f"{indicator} inappropriate for {style}",
                    "matched_indicator": indicator,
                    "category": category
                })
                logger.info(f"🚫 EXCLUSION MATCH: {indicator} found in {item_text}")
                return f"{indicator} inappropriate for {style}"
    
    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
        "result": "no exclusion - item passes hard filter"
    })
    
    return None


def calculate_colorblock_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized colorblock scoring using actual color and pattern metadata.
    Uses AI-analyzed dominantColors, matchingColors, and pattern data.
    """
    score = 0
    
    # 1. CHECK PATTERN (most reliable indicator)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['geometric', 'color block', 'colorblock', 'blocks']:
            score += 30  # Highly appropriate - geometric/block patterns
            logger.debug(f"   ✅ COLORBLOCK: {item.get('name')} has geometric/block pattern (+30)")
        elif pattern == 'solid':
            score += 10  # Appropriate - solid colors work for colorblock
            logger.debug(f"   ✅ COLORBLOCK: {item.get('name')} has solid pattern (+10)")
        elif pattern in ['floral', 'paisley', 'damask', 'baroque', 'ornate']:
            score -= 25  # Highly inappropriate - too busy/decorative
            logger.debug(f"   ❌ COLORBLOCK: {item.get('name')} has busy pattern {pattern} (-25)")
    
    # 2. CHECK DOMINANT COLORS (for bold, contrasting colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors and len(dominant_colors) >= 2:
        # Multiple bold colors = potential colorblock piece
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Bold/primary colors that work well in colorblock
        bold_colors = ['red', 'blue', 'yellow', 'green', 'orange', 'purple', 'pink', 'cyan', 'magenta']
        bold_count = sum(1 for name in color_names if any(bold in name for bold in bold_colors))
        
        if bold_count >= 2:
            score += 25  # Multiple bold colors
            logger.debug(f"   ✅ COLORBLOCK: {item.get('name')} has {bold_count} bold colors (+25)")
        elif bold_count == 1:
            score += 15  # One bold color
            logger.debug(f"   ✅ COLORBLOCK: {item.get('name')} has 1 bold color (+15)")
    
    # 3. CHECK FOR MUTED/NEUTRAL (inappropriate for colorblock)
    item_color = item.get('color', '').lower()
    muted_keywords = ['beige', 'neutral', 'muted', 'gray', 'grey', 'taupe', 'khaki', 'ecru']
    if any(word in item_color for word in muted_keywords):
        score -= 15
        logger.debug(f"   ❌ COLORBLOCK: {item.get('name')} has muted/neutral color (-15)")
    
    # 4. CHECK FOR MONOCHROME (inappropriate for colorblock)
    if len(dominant_colors) == 1:
        single_color = dominant_colors[0]
        color_name = ''
        if isinstance(single_color, dict):
            color_name = single_color.get('name', '').lower()
        elif isinstance(single_color, str):
            color_name = single_color.lower()
        
        if any(word in color_name for word in ['black', 'white', 'grey', 'gray']):
            score -= 10
            logger.debug(f"   ❌ COLORBLOCK: {item.get('name')} is monochrome {color_name} (-10)")
    
    return score


def calculate_minimalist_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized minimalist scoring using pattern and color metadata.
    Minimalist = solid patterns, 1-2 neutral colors, clean lines.
    """
    score = 0
    
    # 1. CHECK PATTERN (critical for minimalist)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern == 'solid':
            score += 30  # Highly appropriate - solid is key to minimalism
            logger.debug(f"   ✅ MINIMALIST: {item.get('name')} has solid pattern (+30)")
        elif pattern in ['floral', 'paisley', 'graphic', 'busy', 'ornate', 'baroque', 'leopard', 'zebra']:
            score -= 30  # Highly inappropriate - too busy
            logger.debug(f"   ❌ MINIMALIST: {item.get('name')} has busy pattern {pattern} (-30)")
        elif pattern in ['striped', 'plaid', 'checkered']:
            score -= 15  # Moderate penalty - not minimalist
            logger.debug(f"   ⚠️ MINIMALIST: {item.get('name')} has pattern {pattern} (-15)")
    
    # 2. CHECK COLOR COUNT (minimalist = 1-2 colors max)
    dominant_colors = item.get('dominantColors', [])
    color_count = len(dominant_colors)
    
    if color_count <= 2:
        score += 20  # Good - minimalist uses few colors
        logger.debug(f"   ✅ MINIMALIST: {item.get('name')} has {color_count} colors (+20)")
    elif color_count >= 4:
        score -= 25  # Too many colors
        logger.debug(f"   ❌ MINIMALIST: {item.get('name')} has {color_count} colors (-25)")
    
    # 3. CHECK FOR NEUTRAL COLORS
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        neutral_colors = ['white', 'black', 'gray', 'grey', 'beige', 'cream', 'ivory', 'navy', 'taupe']
        neutral_count = sum(1 for name in color_names if any(neutral in name for neutral in neutral_colors))
        
        if neutral_count == len(color_names):
            score += 20  # All neutral - perfect for minimalist
            logger.debug(f"   ✅ MINIMALIST: {item.get('name')} has all neutral colors (+20)")
        
        # Penalty for loud colors
        loud_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime', 'electric']
        if any(loud in ' '.join(color_names) for loud in loud_colors):
            score -= 20
            logger.debug(f"   ❌ MINIMALIST: {item.get('name')} has loud colors (-20)")
    
    return score


def calculate_maximalist_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized maximalist scoring using pattern and color metadata.
    Maximalist = bold patterns, 3+ colors, more is more.
    """
    score = 0
    
    # 1. CHECK PATTERN (maximalist loves patterns)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['floral', 'paisley', 'graphic', 'mixed', 'busy', 'ornate', 'baroque', 'leopard', 'zebra', 'geometric']:
            score += 30  # Highly appropriate - bold patterns
            logger.debug(f"   ✅ MAXIMALIST: {item.get('name')} has bold pattern {pattern} (+30)")
        elif pattern == 'solid':
            score -= 20  # Inappropriate - too plain
            logger.debug(f"   ❌ MAXIMALIST: {item.get('name')} has solid pattern (-20)")
    
    # 2. CHECK COLOR COUNT (maximalist = 3+ colors)
    dominant_colors = item.get('dominantColors', [])
    color_count = len(dominant_colors)
    
    if color_count >= 4:
        score += 30  # Excellent - lots of colors
        logger.debug(f"   ✅ MAXIMALIST: {item.get('name')} has {color_count} colors (+30)")
    elif color_count == 3:
        score += 20  # Good - multiple colors
        logger.debug(f"   ✅ MAXIMALIST: {item.get('name')} has 3 colors (+20)")
    elif color_count <= 1:
        score -= 20  # Too monochrome
        logger.debug(f"   ❌ MAXIMALIST: {item.get('name')} has only {color_count} color(s) (-20)")
    
    # 3. CHECK FOR BOLD COLORS
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        bold_colors = ['red', 'blue', 'yellow', 'green', 'orange', 'purple', 'pink', 'magenta', 'cyan', 'bright']
        bold_count = sum(1 for name in color_names if any(bold in name for bold in bold_colors))
        
        if bold_count >= 2:
            score += 20  # Bold colors - perfect for maximalist
            logger.debug(f"   ✅ MAXIMALIST: {item.get('name')} has {bold_count} bold colors (+20)")
        
        # Check for all neutral (boring for maximalist)
        neutral_colors = ['white', 'black', 'gray', 'grey', 'beige', 'cream', 'taupe']
        if all(any(neutral in name for neutral in neutral_colors) for name in color_names):
            score -= 25  # All neutral - too boring
            logger.debug(f"   ❌ MAXIMALIST: {item.get('name')} is all neutral (-25)")
    
    return score


def calculate_gothic_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized gothic scoring using color and material metadata.
    Gothic = black dominant, dark colors, specific materials (lace, velvet).
    """
    score = 0
    
    # 1. CHECK FOR BLACK (critical for gothic)
    dominant_colors = item.get('dominantColors', [])
    has_black = False
    
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Check if black is present
        if any('black' in name for name in color_names):
            has_black = True
            score += 30  # Black is essential for gothic
            logger.debug(f"   ✅ GOTHIC: {item.get('name')} has black (+30)")
        
        # Check for dark colors (burgundy, dark purple, dark red)
        dark_colors = ['burgundy', 'wine', 'dark red', 'maroon', 'purple', 'dark purple', 'navy']
        dark_count = sum(1 for name in color_names if any(dark in name for dark in dark_colors))
        if dark_count > 0:
            score += 15  # Dark colors complement gothic
            logger.debug(f"   ✅ GOTHIC: {item.get('name')} has dark colors (+15)")
        
        # Penalty for bright/pastel colors
        bright_colors = ['pastel', 'pink', 'baby blue', 'mint', 'peach', 'yellow', 'bright', 'neon', 'lime']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 30  # Very inappropriate
            logger.debug(f"   ❌ GOTHIC: {item.get('name')} has bright/pastel colors (-30)")
    
    # 2. CHECK MATERIAL (lace, velvet, leather)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['lace', 'velvet', 'leather', 'silk']):
            score += 20  # Gothic materials
            logger.debug(f"   ✅ GOTHIC: {item.get('name')} has gothic material {material} (+20)")
    
    # 3. CHECK PATTERN (lace patterns are gothic)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['lace', 'mesh', 'fishnet']:
            score += 15  # Gothic patterns
            logger.debug(f"   ✅ GOTHIC: {item.get('name')} has gothic pattern {pattern} (+15)")
    
    # 4. If no black, significant penalty
    if not has_black and dominant_colors:
        score -= 20
        logger.debug(f"   ❌ GOTHIC: {item.get('name')} missing black color (-20)")
    
    return score


def calculate_monochrome_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized monochrome scoring using color metadata.
    Monochrome = single color family (especially black/white/gray).
    """
    score = 0
    
    # 1. CHECK COLOR COUNT (monochrome = 1 color family)
    dominant_colors = item.get('dominantColors', [])
    color_count = len(dominant_colors)
    
    if color_count == 1:
        score += 30  # Perfect - single color
        logger.debug(f"   ✅ MONOCHROME: {item.get('name')} has 1 color (+30)")
    elif color_count == 2:
        score += 10  # Acceptable - might be shades of same color
        logger.debug(f"   ✅ MONOCHROME: {item.get('name')} has 2 colors (+10)")
    elif color_count >= 4:
        score -= 30  # Too many colors
        logger.debug(f"   ❌ MONOCHROME: {item.get('name')} has {color_count} colors (-30)")
    
    # 2. CHECK FOR BLACK/WHITE/GRAY (classic monochrome)
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Check if all colors are black/white/gray
        bw_colors = ['black', 'white', 'gray', 'grey', 'charcoal', 'ivory', 'cream']
        if all(any(bw in name for bw in bw_colors) for name in color_names):
            score += 25  # Classic monochrome palette
            logger.debug(f"   ✅ MONOCHROME: {item.get('name')} is black/white/gray monochrome (+25)")
        
        # Check if all colors are from same family (all blues, all reds, etc.)
        color_families = [
            ['blue', 'navy', 'azure', 'cobalt', 'indigo'],
            ['red', 'burgundy', 'wine', 'maroon', 'crimson'],
            ['green', 'olive', 'forest', 'emerald', 'sage'],
            ['brown', 'tan', 'beige', 'camel', 'chocolate']
        ]
        
        for family in color_families:
            if all(any(f in name for f in family) for name in color_names):
                score += 20  # Single color family
                logger.debug(f"   ✅ MONOCHROME: {item.get('name')} is single color family (+20)")
                break
    
    # 3. CHECK PATTERN (solid is better for monochrome)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern == 'solid':
            score += 15  # Solid enhances monochrome
            logger.debug(f"   ✅ MONOCHROME: {item.get('name')} has solid pattern (+15)")
        elif pattern in ['mixed', 'colorful', 'rainbow']:
            score -= 20  # Contradicts monochrome
            logger.debug(f"   ❌ MONOCHROME: {item.get('name')} has colorful pattern (-20)")
    
    return score


def calculate_dark_academia_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized dark academia scoring using color, pattern, and material metadata.
    Dark Academia = dark colors (brown, burgundy, forest green), plaid/tweed patterns, wool materials.
    """
    score = 0
    
    # 1. CHECK FOR DARK COLORS
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Dark academia colors
        dark_academia_colors = ['brown', 'burgundy', 'wine', 'maroon', 'forest green', 'navy', 'beige', 'tan', 'olive', 'dark green']
        dark_count = sum(1 for name in color_names if any(dark in name for dark in dark_academia_colors))
        
        if dark_count >= 1:
            score += 25  # Has dark academia colors
            logger.debug(f"   ✅ DARK ACADEMIA: {item.get('name')} has {dark_count} dark academia colors (+25)")
        
        # Penalty for neon/bright colors
        bright_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime', 'electric', 'yellow']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 30
            logger.debug(f"   ❌ DARK ACADEMIA: {item.get('name')} has bright colors (-30)")
    
    # 2. CHECK PATTERN (plaid, tweed, corduroy)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['plaid', 'checkered', 'tartan', 'houndstooth']:
            score += 30  # Classic dark academia patterns
            logger.debug(f"   ✅ DARK ACADEMIA: {item.get('name')} has academia pattern {pattern} (+30)")
        elif pattern in ['striped', 'argyle']:
            score += 15  # Acceptable patterns
            logger.debug(f"   ✅ DARK ACADEMIA: {item.get('name')} has pattern {pattern} (+15)")
    
    # 3. CHECK MATERIAL (wool, tweed, corduroy)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['tweed', 'wool', 'corduroy', 'cable knit']):
            score += 20  # Academic materials
            logger.debug(f"   ✅ DARK ACADEMIA: {item.get('name')} has academic material {material} (+20)")
    
    return score


def calculate_light_academia_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized light academia scoring using color and material metadata.
    Light Academia = light colors (cream, beige, white, pastels), linen materials.
    """
    score = 0
    
    # 1. CHECK FOR LIGHT COLORS
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Light academia colors
        light_colors = ['cream', 'beige', 'white', 'ivory', 'light blue', 'pastel', 'pale', 'soft', 'blush', 'champagne']
        light_count = sum(1 for name in color_names if any(light in name for light in light_colors))
        
        if light_count >= 1:
            score += 25  # Has light academia colors
            logger.debug(f"   ✅ LIGHT ACADEMIA: {item.get('name')} has {light_count} light academia colors (+25)")
        
        # Penalty for dark colors
        dark_colors = ['black', 'dark', 'charcoal', 'navy']
        dark_count = sum(1 for name in color_names if any(dark in name for dark in dark_colors))
        if dark_count >= 2:
            score -= 25
            logger.debug(f"   ❌ LIGHT ACADEMIA: {item.get('name')} has too many dark colors (-25)")
        
        # Penalty for neon/bright colors
        bright_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime', 'electric']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 20
            logger.debug(f"   ❌ LIGHT ACADEMIA: {item.get('name')} has neon colors (-20)")
    
    # 2. CHECK MATERIAL (linen is key)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if 'linen' in material:
            score += 25  # Linen is quintessential light academia
            logger.debug(f"   ✅ LIGHT ACADEMIA: {item.get('name')} has linen material (+25)")
        elif any(m in material for m in ['cotton', 'silk', 'chiffon']):
            score += 10  # Light, airy materials
            logger.debug(f"   ✅ LIGHT ACADEMIA: {item.get('name')} has light material {material} (+10)")
    
    # 3. CHECK PATTERN (prefer simple/soft patterns)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['solid', 'subtle']:
            score += 10  # Clean, simple patterns
            logger.debug(f"   ✅ LIGHT ACADEMIA: {item.get('name')} has simple pattern (+10)")
    
    return score


def calculate_preppy_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized preppy scoring using pattern and color metadata.
    Preppy = stripes/plaid patterns, navy/white/khaki colors, classic cuts.
    """
    score = 0
    
    # 1. CHECK PATTERN (stripes and plaids are quintessential preppy)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['striped', 'stripes']:
            score += 30  # Stripes are very preppy
            logger.debug(f"   ✅ PREPPY: {item.get('name')} has striped pattern (+30)")
        elif pattern in ['plaid', 'checkered', 'gingham']:
            score += 25  # Plaid/gingham are preppy
            logger.debug(f"   ✅ PREPPY: {item.get('name')} has {pattern} pattern (+25)")
    
    # 2. CHECK FOR PREPPY COLORS
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Preppy colors
        preppy_colors = ['navy', 'white', 'khaki', 'pink', 'light blue', 'green', 'yellow', 'red']
        preppy_count = sum(1 for name in color_names if any(prep in name for prep in preppy_colors))
        
        if preppy_count >= 2:
            score += 20  # Multiple preppy colors
            logger.debug(f"   ✅ PREPPY: {item.get('name')} has {preppy_count} preppy colors (+20)")
        elif preppy_count == 1:
            score += 10
            logger.debug(f"   ✅ PREPPY: {item.get('name')} has 1 preppy color (+10)")
        
        # Penalty for grunge/edgy colors
        if any(word in ' '.join(color_names) for word in ['black', 'dark', 'charcoal']):
            score -= 15
            logger.debug(f"   ⚠️ PREPPY: {item.get('name')} has dark colors (-15)")
    
    return score


def calculate_cottagecore_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized cottagecore scoring using pattern and color metadata.
    Cottagecore = floral/gingham patterns, pastel/earth tones, natural materials.
    """
    score = 0
    
    # 1. CHECK PATTERN (floral is key to cottagecore)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['floral', 'flower']:
            score += 30  # Floral is essential cottagecore
            logger.debug(f"   ✅ COTTAGECORE: {item.get('name')} has floral pattern (+30)")
        elif pattern in ['gingham', 'checkered', 'small checks']:
            score += 25  # Gingham is very cottagecore
            logger.debug(f"   ✅ COTTAGECORE: {item.get('name')} has {pattern} pattern (+25)")
        elif pattern in ['embroidered', 'lace', 'eyelet']:
            score += 20  # Decorative cottage patterns
            logger.debug(f"   ✅ COTTAGECORE: {item.get('name')} has {pattern} pattern (+20)")
        elif pattern in ['geometric', 'graphic', 'modern']:
            score -= 20  # Too modern for cottagecore
            logger.debug(f"   ❌ COTTAGECORE: {item.get('name')} has modern pattern (-20)")
    
    # 2. CHECK COLORS (pastels and earth tones)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Cottagecore colors
        cottage_colors = ['pastel', 'pink', 'lavender', 'sage', 'mint', 'peach', 'cream', 'white', 'light blue', 'yellow', 'green']
        cottage_count = sum(1 for name in color_names if any(cottage in name for cottage in cottage_colors))
        
        if cottage_count >= 1:
            score += 20  # Has cottagecore colors
            logger.debug(f"   ✅ COTTAGECORE: {item.get('name')} has cottagecore colors (+20)")
    
    # 3. CHECK MATERIAL (natural fibers)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['cotton', 'linen', 'lace']):
            score += 15  # Natural, cottage materials
            logger.debug(f"   ✅ COTTAGECORE: {item.get('name')} has natural material {material} (+15)")
    
    return score


def calculate_romantic_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized romantic scoring using pattern, material, and color metadata.
    Romantic = floral/lace patterns, soft materials (silk, chiffon), pastel colors.
    """
    score = 0
    
    # 1. CHECK PATTERN (lace and floral are romantic)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['lace', 'mesh', 'eyelet']:
            score += 30  # Lace is quintessentially romantic
            logger.debug(f"   ✅ ROMANTIC: {item.get('name')} has lace pattern (+30)")
        elif pattern in ['floral', 'flower']:
            score += 25  # Floral is romantic
            logger.debug(f"   ✅ ROMANTIC: {item.get('name')} has floral pattern (+25)")
        elif pattern in ['ruffles', 'embroidered']:
            score += 20  # Feminine details
            logger.debug(f"   ✅ ROMANTIC: {item.get('name')} has {pattern} details (+20)")
    
    # 2. CHECK MATERIAL (soft, delicate materials)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['lace', 'silk', 'chiffon', 'satin', 'velvet']):
            score += 25  # Romantic materials
            logger.debug(f"   ✅ ROMANTIC: {item.get('name')} has romantic material {material} (+25)")
    
    # 3. CHECK COLORS (soft, pastel colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Romantic colors
        romantic_colors = ['pink', 'blush', 'pastel', 'lavender', 'cream', 'ivory', 'peach', 'rose', 'soft']
        romantic_count = sum(1 for name in color_names if any(rom in name for rom in romantic_colors))
        
        if romantic_count >= 1:
            score += 20  # Has romantic colors
            logger.debug(f"   ✅ ROMANTIC: {item.get('name')} has romantic colors (+20)")
    
    return score


def calculate_grunge_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized grunge scoring using pattern, texture, and color metadata.
    Grunge = plaid/flannel patterns, distressed texture, dark colors, oversized fit.
    """
    score = 0
    
    # 1. CHECK PATTERN (plaid/flannel is grunge)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['plaid', 'flannel', 'checkered', 'tartan']:
            score += 30  # Plaid/flannel is quintessential grunge
            logger.debug(f"   ✅ GRUNGE: {item.get('name')} has grunge pattern {pattern} (+30)")
    
    # 2. CHECK TEXTURE (distressed, worn, ripped)
    texture = item.get('metadata', {}).get('visualAttributes', {}).get('textureStyle', '').lower()
    if texture:
        if any(t in texture for t in ['distressed', 'ripped', 'worn', 'faded', 'vintage']):
            score += 25  # Distressed texture is grunge
            logger.debug(f"   ✅ GRUNGE: {item.get('name')} has distressed texture (+25)")
    
    # 3. CHECK FIT (oversized is grunge)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['oversized', 'loose', 'baggy']:
            score += 20  # Oversized fit is grunge
            logger.debug(f"   ✅ GRUNGE: {item.get('name')} has oversized fit (+20)")
    
    # 4. CHECK COLORS (dark, muted colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Grunge colors (dark, muted)
        grunge_colors = ['black', 'dark', 'gray', 'charcoal', 'brown', 'olive', 'burgundy']
        grunge_count = sum(1 for name in color_names if any(grunge in name for grunge in grunge_colors))
        
        if grunge_count >= 1:
            score += 15  # Has grunge colors
            logger.debug(f"   ✅ GRUNGE: {item.get('name')} has grunge colors (+15)")
        
        # Penalty for bright/preppy colors
        if any(word in ' '.join(color_names) for word in ['bright', 'neon', 'pastel', 'pink']):
            score -= 20
            logger.debug(f"   ❌ GRUNGE: {item.get('name')} has non-grunge colors (-20)")
    
    return score


def calculate_boho_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized boho scoring using pattern, fit, and color metadata.
    Boho = ethnic/embroidered patterns, flowy fit, earth tones.
    """
    score = 0
    
    # 1. CHECK PATTERN (ethnic, embroidered, paisley)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['ethnic', 'embroidered', 'paisley', 'tribal', 'bohemian']:
            score += 30  # Ethnic patterns are quintessential boho
            logger.debug(f"   ✅ BOHO: {item.get('name')} has boho pattern {pattern} (+30)")
        elif pattern in ['floral', 'printed', 'mixed']:
            score += 15  # Acceptable boho patterns
            logger.debug(f"   ✅ BOHO: {item.get('name')} has pattern {pattern} (+15)")
    
    # 2. CHECK FIT (flowy, loose is boho)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['flowy', 'loose', 'relaxed', 'oversized']:
            score += 20  # Flowy fit is boho
            logger.debug(f"   ✅ BOHO: {item.get('name')} has flowy fit (+20)")
        elif fit in ['tight', 'fitted', 'slim']:
            score -= 15  # Too structured for boho
            logger.debug(f"   ❌ BOHO: {item.get('name')} has structured fit (-15)")
    
    # 3. CHECK COLORS (earth tones, natural colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Boho colors (earth tones)
        boho_colors = ['brown', 'tan', 'beige', 'olive', 'rust', 'terracotta', 'sage', 'mustard', 'burgundy', 'cream']
        boho_count = sum(1 for name in color_names if any(boho in name for boho in boho_colors))
        
        if boho_count >= 1:
            score += 20  # Has boho colors
            logger.debug(f"   ✅ BOHO: {item.get('name')} has earth tone colors (+20)")
    
    # 4. CHECK MATERIAL (natural fibers)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['cotton', 'linen', 'hemp', 'natural']):
            score += 15  # Natural materials are boho
            logger.debug(f"   ✅ BOHO: {item.get('name')} has natural material {material} (+15)")
    
    return score


def calculate_business_casual_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized business casual scoring using formalLevel metadata.
    Business Casual = Business Casual or Smart Casual formalLevel, structured fits.
    """
    score = 0
    
    # 1. CHECK FORMAL LEVEL (most direct indicator)
    formal_level = item.get('metadata', {}).get('visualAttributes', {}).get('formalLevel', '').lower()
    if formal_level:
        if formal_level in ['business casual', 'business', 'smart casual']:
            score += 40  # Direct match for business casual
            logger.debug(f"   ✅ BUSINESS CASUAL: {item.get('name')} has formalLevel {formal_level} (+40)")
        elif formal_level == 'formal':
            score += 20  # Formal works but might be too dressy
            logger.debug(f"   ✅ BUSINESS CASUAL: {item.get('name')} has formal level (+20)")
        elif formal_level in ['casual', 'relaxed']:
            score -= 20  # Too casual
            logger.debug(f"   ❌ BUSINESS CASUAL: {item.get('name')} is too casual (-20)")
        elif formal_level in ['athletic', 'loungewear']:
            score -= 50  # Completely inappropriate
            logger.debug(f"   ❌ BUSINESS CASUAL: {item.get('name')} is athletic/loungewear (-50)")
    
    # 2. CHECK COLORS (professional colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Business casual colors
        professional_colors = ['navy', 'gray', 'grey', 'black', 'white', 'blue', 'khaki', 'beige', 'burgundy']
        professional_count = sum(1 for name in color_names if any(prof in name for prof in professional_colors))
        
        if professional_count >= 1:
            score += 15  # Has professional colors
            logger.debug(f"   ✅ BUSINESS CASUAL: {item.get('name')} has professional colors (+15)")
        
        # Penalty for too casual/loud colors
        casual_colors = ['neon', 'bright', 'hot pink', 'lime', 'fluorescent']
        if any(casual in ' '.join(color_names) for casual in casual_colors):
            score -= 25
            logger.debug(f"   ❌ BUSINESS CASUAL: {item.get('name')} has loud colors (-25)")
    
    # 3. CHECK FIT (structured is professional)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['tailored', 'fitted', 'structured']:
            score += 20  # Professional fit
            logger.debug(f"   ✅ BUSINESS CASUAL: {item.get('name')} has professional fit (+20)")
    
    return score


def calculate_scandinavian_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized scandinavian scoring using color and material metadata.
    Scandinavian = neutral/muted colors, wool/knit materials, minimal patterns.
    """
    score = 0
    
    # 1. CHECK COLORS (neutral, muted Nordic palette)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Scandinavian colors (neutral, muted)
        scandi_colors = ['white', 'cream', 'beige', 'gray', 'grey', 'black', 'navy', 'muted', 'soft', 'pale']
        scandi_count = sum(1 for name in color_names if any(scandi in name for scandi in scandi_colors))
        
        if scandi_count >= 1:
            score += 25  # Has Scandinavian colors
            logger.debug(f"   ✅ SCANDINAVIAN: {item.get('name')} has Nordic colors (+25)")
        
        # Penalty for loud/bright colors
        bright_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime', 'electric', 'vibrant']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 30
            logger.debug(f"   ❌ SCANDINAVIAN: {item.get('name')} has bright colors (-30)")
    
    # 2. CHECK MATERIAL (wool, knit are quintessential Scandinavian)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['wool', 'knit', 'cable knit', 'merino', 'cashmere']):
            score += 30  # Scandinavian materials
            logger.debug(f"   ✅ SCANDINAVIAN: {item.get('name')} has Nordic material {material} (+30)")
        elif any(m in material for m in ['cotton', 'linen']):
            score += 10  # Natural materials acceptable
            logger.debug(f"   ✅ SCANDINAVIAN: {item.get('name')} has natural material (+10)")
    
    # 3. CHECK PATTERN (simple/minimal preferred)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['solid', 'minimal', 'simple']:
            score += 20  # Simple is Scandinavian
            logger.debug(f"   ✅ SCANDINAVIAN: {item.get('name')} has minimal pattern (+20)")
        elif pattern in ['floral', 'busy', 'ornate', 'baroque', 'maximalist']:
            score -= 25  # Too busy for Scandinavian
            logger.debug(f"   ❌ SCANDINAVIAN: {item.get('name')} has busy pattern (-25)")
    
    return score


def calculate_old_money_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized old money scoring using material quality and classic colors.
    Old Money = quality materials (cashmere, silk, wool), classic colors, timeless fit.
    """
    score = 0
    
    # 1. CHECK MATERIAL QUALITY (luxury materials)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        # Premium materials
        if any(m in material for m in ['cashmere', 'silk', 'merino', 'wool', 'linen', 'leather']):
            score += 35  # Luxury materials
            logger.debug(f"   ✅ OLD MONEY: {item.get('name')} has quality material {material} (+35)")
        
        # Avoid cheap materials
        if any(m in material for m in ['polyester', 'acrylic', 'synthetic']):
            score -= 20  # Cheap materials
            logger.debug(f"   ❌ OLD MONEY: {item.get('name')} has cheap material (-20)")
    
    # 2. CHECK COLORS (classic, understated colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Old money colors (classic, timeless)
        classic_colors = ['navy', 'camel', 'cream', 'white', 'gray', 'grey', 'burgundy', 'forest green', 'khaki', 'tan']
        classic_count = sum(1 for name in color_names if any(classic in name for classic in classic_colors))
        
        if classic_count >= 1:
            score += 25  # Has classic colors
            logger.debug(f"   ✅ OLD MONEY: {item.get('name')} has classic colors (+25)")
        
        # Penalty for trendy/loud colors
        trendy_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime']
        if any(trendy in ' '.join(color_names) for trendy in trendy_colors):
            score -= 30  # Too flashy
            logger.debug(f"   ❌ OLD MONEY: {item.get('name')} has flashy colors (-30)")
    
    # 3. CHECK FORMAL LEVEL (smart casual to formal)
    formal_level = item.get('metadata', {}).get('visualAttributes', {}).get('formalLevel', '').lower()
    if formal_level:
        if formal_level in ['smart casual', 'business casual', 'formal', 'business']:
            score += 20  # Appropriate formality
            logger.debug(f"   ✅ OLD MONEY: {item.get('name')} has appropriate formality (+20)")
        elif formal_level in ['athletic', 'loungewear']:
            score -= 30  # Too casual
            logger.debug(f"   ❌ OLD MONEY: {item.get('name')} is too casual (-30)")
    
    # 4. CHECK FIT (tailored, quality fit)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['tailored', 'fitted', 'classic']:
            score += 15  # Quality fit
            logger.debug(f"   ✅ OLD MONEY: {item.get('name')} has tailored fit (+15)")
    
    return score


def calculate_clean_girl_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized clean girl scoring using pattern and color metadata.
    Clean Girl = solid patterns, neutral colors, smooth textures, minimal aesthetic.
    """
    score = 0
    
    # 1. CHECK PATTERN (solid/minimal is essential)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['solid', 'minimal', 'plain']:
            score += 30  # Essential for clean girl
            logger.debug(f"   ✅ CLEAN GIRL: {item.get('name')} has clean pattern (+30)")
        elif pattern in ['busy', 'loud', 'maximalist', 'graphic']:
            score -= 30  # Too busy
            logger.debug(f"   ❌ CLEAN GIRL: {item.get('name')} has busy pattern (-30)")
    
    # 2. CHECK COLORS (neutral, fresh colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Clean girl colors
        clean_colors = ['white', 'cream', 'beige', 'nude', 'soft', 'pastel', 'light', 'neutral']
        clean_count = sum(1 for name in color_names if any(clean in name for clean in clean_colors))
        
        if clean_count >= 1:
            score += 25  # Has clean girl colors
            logger.debug(f"   ✅ CLEAN GIRL: {item.get('name')} has clean colors (+25)")
        
        # Penalty for bold/dark colors
        bold_colors = ['neon', 'bright', 'dark', 'bold', 'gothic']
        if any(bold in ' '.join(color_names) for bold in bold_colors):
            score -= 20
            logger.debug(f"   ❌ CLEAN GIRL: {item.get('name')} has bold colors (-20)")
    
    # 3. CHECK TEXTURE (smooth is clean girl)
    texture = item.get('metadata', {}).get('visualAttributes', {}).get('textureStyle', '').lower()
    if texture:
        if texture in ['smooth', 'sleek', 'polished']:
            score += 15  # Clean texture
            logger.debug(f"   ✅ CLEAN GIRL: {item.get('name')} has smooth texture (+15)")
        elif texture in ['distressed', 'ripped', 'worn']:
            score -= 20  # Too rough
            logger.debug(f"   ❌ CLEAN GIRL: {item.get('name')} has distressed texture (-20)")
    
    return score


def calculate_punk_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized punk scoring using material, texture, and color metadata.
    Punk = leather, studded/distressed textures, black/dark colors.
    """
    score = 0
    
    # 1. CHECK MATERIAL (leather is quintessential punk)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if 'leather' in material:
            score += 30  # Leather is essential punk
            logger.debug(f"   ✅ PUNK: {item.get('name')} has leather material (+30)")
        elif 'denim' in material:
            score += 15  # Denim works for punk
            logger.debug(f"   ✅ PUNK: {item.get('name')} has denim material (+15)")
    
    # 2. CHECK TEXTURE (studded, distressed, ripped)
    texture = item.get('metadata', {}).get('visualAttributes', {}).get('textureStyle', '').lower()
    if texture:
        if any(t in texture for t in ['studded', 'spiked', 'chains']):
            score += 35  # Studded is very punk
            logger.debug(f"   ✅ PUNK: {item.get('name')} has punk texture {texture} (+35)")
        elif any(t in texture for t in ['distressed', 'ripped', 'torn', 'worn']):
            score += 25  # Distressed is punk
            logger.debug(f"   ✅ PUNK: {item.get('name')} has distressed texture (+25)")
    
    # 3. CHECK COLORS (black and dark)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        if any('black' in name for name in color_names):
            score += 20  # Black is punk
            logger.debug(f"   ✅ PUNK: {item.get('name')} has black color (+20)")
        
        # Penalty for soft/pastel colors
        soft_colors = ['pastel', 'soft', 'blush', 'baby', 'light pink']
        if any(soft in ' '.join(color_names) for soft in soft_colors):
            score -= 25
            logger.debug(f"   ❌ PUNK: {item.get('name')} has soft colors (-25)")
    
    return score


def calculate_edgy_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized edgy scoring using material, texture, and color metadata.
    Edgy = leather, dark colors, distressed textures.
    """
    score = 0
    
    # 1. CHECK MATERIAL (leather is edgy)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if 'leather' in material:
            score += 30  # Leather is very edgy
            logger.debug(f"   ✅ EDGY: {item.get('name')} has leather material (+30)")
        elif 'denim' in material:
            score += 15  # Denim can be edgy
            logger.debug(f"   ✅ EDGY: {item.get('name')} has denim material (+15)")
    
    # 2. CHECK TEXTURE (distressed, worn)
    texture = item.get('metadata', {}).get('visualAttributes', {}).get('textureStyle', '').lower()
    if texture:
        if any(t in texture for t in ['distressed', 'ripped', 'torn', 'worn']):
            score += 25  # Distressed is edgy
            logger.debug(f"   ✅ EDGY: {item.get('name')} has distressed texture (+25)")
    
    # 3. CHECK COLORS (dark, bold colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Edgy colors
        edgy_colors = ['black', 'dark', 'charcoal', 'burgundy', 'deep red']
        edgy_count = sum(1 for name in color_names if any(edgy in name for edgy in edgy_colors))
        
        if edgy_count >= 1:
            score += 20  # Has edgy colors
            logger.debug(f"   ✅ EDGY: {item.get('name')} has dark/edgy colors (+20)")
        
        # Penalty for soft/pastel colors
        soft_colors = ['pastel', 'soft', 'blush', 'baby', 'light pink', 'peach']
        if any(soft in ' '.join(color_names) for soft in soft_colors):
            score -= 25
            logger.debug(f"   ❌ EDGY: {item.get('name')} has soft colors (-25)")
    
    return score


def calculate_french_girl_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized french girl scoring using pattern, color, and fit metadata.
    French Girl = striped patterns, classic neutrals (navy, white, black), effortless fit.
    """
    score = 0
    
    # 1. CHECK PATTERN (stripes are iconic french girl)
    pattern = item.get('metadata', {}).get('visualAttributes', {}).get('pattern', '').lower()
    if pattern:
        if pattern in ['striped', 'stripes']:
            score += 30  # Stripes are quintessential French
            logger.debug(f"   ✅ FRENCH GIRL: {item.get('name')} has striped pattern (+30)")
        elif pattern in ['solid', 'minimal']:
            score += 15  # Simple patterns work
            logger.debug(f"   ✅ FRENCH GIRL: {item.get('name')} has simple pattern (+15)")
    
    # 2. CHECK COLORS (classic French palette)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # French girl colors
        french_colors = ['navy', 'white', 'black', 'red', 'beige', 'cream']
        french_count = sum(1 for name in color_names if any(french in name for french in french_colors))
        
        if french_count >= 1:
            score += 20  # Has French colors
            logger.debug(f"   ✅ FRENCH GIRL: {item.get('name')} has French palette colors (+20)")
        
        # Penalty for loud colors
        loud_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime']
        if any(loud in ' '.join(color_names) for loud in loud_colors):
            score -= 20
            logger.debug(f"   ❌ FRENCH GIRL: {item.get('name')} has loud colors (-20)")
    
    # 3. CHECK FIT (effortless, not too tight or baggy)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['tailored', 'fitted', 'classic', 'regular']:
            score += 15  # Effortless fit
            logger.debug(f"   ✅ FRENCH GIRL: {item.get('name')} has effortless fit (+15)")
    
    return score


def calculate_urban_professional_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized urban professional scoring using formalLevel and fit metadata.
    Urban Professional = Business Casual+ formality, modern/sleek fit, professional colors.
    """
    score = 0
    
    # 1. CHECK FORMAL LEVEL (similar to business casual)
    formal_level = item.get('metadata', {}).get('visualAttributes', {}).get('formalLevel', '').lower()
    if formal_level:
        if formal_level in ['business casual', 'business', 'smart casual', 'formal']:
            score += 35  # Professional formality
            logger.debug(f"   ✅ URBAN PROFESSIONAL: {item.get('name')} has formalLevel {formal_level} (+35)")
        elif formal_level in ['casual', 'relaxed']:
            score -= 20  # Too casual
            logger.debug(f"   ❌ URBAN PROFESSIONAL: {item.get('name')} is too casual (-20)")
        elif formal_level in ['athletic', 'loungewear']:
            score -= 40  # Very inappropriate
            logger.debug(f"   ❌ URBAN PROFESSIONAL: {item.get('name')} is athletic/loungewear (-40)")
    
    # 2. CHECK FIT (modern, tailored)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['tailored', 'fitted', 'structured', 'modern']:
            score += 25  # Modern professional fit
            logger.debug(f"   ✅ URBAN PROFESSIONAL: {item.get('name')} has modern fit (+25)")
    
    # 3. CHECK COLORS (sleek professional colors)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Urban professional colors
        professional_colors = ['black', 'navy', 'gray', 'grey', 'white', 'charcoal']
        professional_count = sum(1 for name in color_names if any(prof in name for prof in professional_colors))
        
        if professional_count >= 1:
            score += 20  # Has professional colors
            logger.debug(f"   ✅ URBAN PROFESSIONAL: {item.get('name')} has professional colors (+20)")
    
    return score


def calculate_techwear_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized techwear scoring using material and color metadata.
    Techwear = technical/synthetic materials, black dominant, functional design.
    """
    score = 0
    
    # 1. CHECK MATERIAL (technical fabrics)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if any(m in material for m in ['technical', 'synthetic', 'waterproof', 'nylon', 'polyester', 'gore-tex']):
            score += 35  # Technical materials are essential
            logger.debug(f"   ✅ TECHWEAR: {item.get('name')} has technical material {material} (+35)")
        elif any(m in material for m in ['cotton', 'linen', 'silk']):
            score -= 20  # Too natural for techwear
            logger.debug(f"   ❌ TECHWEAR: {item.get('name')} has natural material (-20)")
    
    # 2. CHECK COLORS (black is dominant in techwear)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Techwear is predominantly black
        if any('black' in name for name in color_names):
            score += 30  # Black is techwear
            logger.debug(f"   ✅ TECHWEAR: {item.get('name')} has black color (+30)")
        
        # Gray/charcoal also work
        if any(word in ' '.join(color_names) for word in ['gray', 'grey', 'charcoal']):
            score += 15  # Dark neutrals
            logger.debug(f"   ✅ TECHWEAR: {item.get('name')} has dark neutral (+15)")
        
        # Penalty for bright colors (except neon accents)
        bright_colors = ['pastel', 'soft', 'light', 'baby blue', 'pink']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 25
            logger.debug(f"   ❌ TECHWEAR: {item.get('name')} has soft colors (-25)")
    
    return score


def calculate_coastal_grandmother_metadata_score(item: Dict[str, Any]) -> int:
    """
    Optimized coastal grandmother scoring using material, color, and fit metadata.
    Coastal Grandmother = linen materials, neutral/beige/blue colors, relaxed fit.
    """
    score = 0
    
    # 1. CHECK MATERIAL (linen is essential)
    material = item.get('metadata', {}).get('visualAttributes', {}).get('material', '').lower()
    if material:
        if 'linen' in material:
            score += 35  # Linen is quintessential coastal grandmother
            logger.debug(f"   ✅ COASTAL GRANDMOTHER: {item.get('name')} has linen material (+35)")
        elif any(m in material for m in ['cotton', 'silk']):
            score += 10  # Light natural materials
            logger.debug(f"   ✅ COASTAL GRANDMOTHER: {item.get('name')} has natural material (+10)")
    
    # 2. CHECK COLORS (neutral, beige, white, blue)
    dominant_colors = item.get('dominantColors', [])
    if dominant_colors:
        color_names = []
        for c in dominant_colors:
            if isinstance(c, dict):
                color_names.append(c.get('name', '').lower())
            elif isinstance(c, str):
                color_names.append(c.lower())
        
        # Coastal grandmother colors
        coastal_colors = ['beige', 'white', 'cream', 'blue', 'navy', 'sand', 'neutral', 'ivory']
        coastal_count = sum(1 for name in color_names if any(coastal in name for coastal in coastal_colors))
        
        if coastal_count >= 1:
            score += 25  # Has coastal colors
            logger.debug(f"   ✅ COASTAL GRANDMOTHER: {item.get('name')} has coastal colors (+25)")
        
        # Penalty for bright/neon colors
        bright_colors = ['neon', 'bright', 'fluorescent', 'hot pink', 'lime']
        if any(bright in ' '.join(color_names) for bright in bright_colors):
            score -= 20
            logger.debug(f"   ❌ COASTAL GRANDMOTHER: {item.get('name')} has bright colors (-20)")
    
    # 3. CHECK FIT (relaxed, oversized)
    fit = item.get('metadata', {}).get('visualAttributes', {}).get('fit', '').lower()
    if fit:
        if fit in ['relaxed', 'oversized', 'loose', 'flowy']:
            score += 20  # Relaxed fit is coastal grandmother
            logger.debug(f"   ✅ COASTAL GRANDMOTHER: {item.get('name')} has relaxed fit (+20)")
        elif fit in ['tight', 'fitted', 'slim']:
            score -= 15  # Too structured
            logger.debug(f"   ❌ COASTAL GRANDMOTHER: {item.get('name')} has fitted look (-15)")
    
    return score


def calculate_style_appropriateness_score(style: str, item: Dict[str, Any], occasion: str = None, mood: str = None) -> int:
    """Calculate style appropriateness score with heavy penalties for mismatches."""
    
    # OPTIMIZATION: Use metadata-based scoring for styles with objective criteria
    style_lower = style.lower()
    
    # Map styles to their metadata scoring functions (Phases 1-4)
    metadata_scorers = {
        # Phase 1: Color-based styles
        'colorblock': calculate_colorblock_metadata_score,
        'minimalist': calculate_minimalist_metadata_score,
        'maximalist': calculate_maximalist_metadata_score,
        'gothic': calculate_gothic_metadata_score,
        'monochrome': calculate_monochrome_metadata_score,
        # Phase 2: Academia & Pattern-heavy styles
        'dark academia': calculate_dark_academia_metadata_score,
        'light academia': calculate_light_academia_metadata_score,
        'preppy': calculate_preppy_metadata_score,
        'cottagecore': calculate_cottagecore_metadata_score,
        'romantic': calculate_romantic_metadata_score,
        'grunge': calculate_grunge_metadata_score,
        'boho': calculate_boho_metadata_score,
        # Phase 3: Formality & Quality styles
        'business casual': calculate_business_casual_metadata_score,
        'scandinavian': calculate_scandinavian_metadata_score,
        'old money': calculate_old_money_metadata_score,
        # Phase 4: Urban & Modern styles
        'clean girl': calculate_clean_girl_metadata_score,
        'punk': calculate_punk_metadata_score,
        'edgy': calculate_edgy_metadata_score,
        'french girl': calculate_french_girl_metadata_score,
        'urban professional': calculate_urban_professional_metadata_score,
        'techwear': calculate_techwear_metadata_score,
        'coastal grandmother': calculate_coastal_grandmother_metadata_score,
    }
    
    if style_lower in metadata_scorers:
        metadata_score = metadata_scorers[style_lower](item)
        # If we got a strong metadata signal (positive or negative), use it
        if metadata_score != 0:
            logger.debug(f"   🎨 Using metadata-based {style_lower} score: {metadata_score}")
            # Still do text fallback but weight metadata heavily
            text_score = 0
            item_text = f"{item.get('name', '')} {item.get('description', '')}".lower()
            
            # Text-based bonuses (additive with metadata) - style specific
            if style_lower == 'colorblock':
                if any(word in item_text for word in ['colorblock', 'color blocking', 'bold colors', 'geometric']):
                    text_score += 20
                if any(word in item_text for word in ['monochrome', 'boring', 'plain', 'dull']):
                    text_score -= 15
            elif style_lower == 'minimalist':
                if any(word in item_text for word in ['minimalist', 'minimal', 'clean', 'simple']):
                    text_score += 15
                if any(word in item_text for word in ['maximalist', 'busy', 'ornate']):
                    text_score -= 15
            elif style_lower == 'maximalist':
                if any(word in item_text for word in ['maximalist', 'bold', 'statement', 'eclectic']):
                    text_score += 15
                if any(word in item_text for word in ['minimalist', 'plain', 'simple']):
                    text_score -= 15
            elif style_lower == 'gothic':
                if any(word in item_text for word in ['gothic', 'goth', 'dark', 'victorian']):
                    text_score += 15
                if any(word in item_text for word in ['preppy', 'bright', 'cheerful']):
                    text_score -= 15
            elif style_lower == 'monochrome':
                if any(word in item_text for word in ['monochrome', 'black and white', 'single color']):
                    text_score += 15
                if any(word in item_text for word in ['colorful', 'multicolor', 'rainbow']):
                    text_score -= 15
            # Phase 2 styles
            elif style_lower == 'dark academia':
                if any(word in item_text for word in ['dark academia', 'academic', 'scholarly', 'tweed']):
                    text_score += 15
            elif style_lower == 'light academia':
                if any(word in item_text for word in ['light academia', 'academic', 'linen', 'airy']):
                    text_score += 15
            elif style_lower == 'preppy':
                if any(word in item_text for word in ['preppy', 'collegiate', 'polo', 'nautical']):
                    text_score += 15
            elif style_lower == 'cottagecore':
                if any(word in item_text for word in ['cottagecore', 'cottage', 'pastoral', 'prairie']):
                    text_score += 15
            elif style_lower == 'romantic':
                if any(word in item_text for word in ['romantic', 'feminine', 'delicate', 'flowy']):
                    text_score += 15
            elif style_lower == 'grunge':
                if any(word in item_text for word in ['grunge', 'flannel', 'distressed', 'ripped']):
                    text_score += 15
            elif style_lower == 'boho':
                if any(word in item_text for word in ['boho', 'bohemian', 'ethnic', 'flowy']):
                    text_score += 15
            # Phase 3 styles
            elif style_lower == 'business casual':
                if any(word in item_text for word in ['business casual', 'professional', 'office', 'work']):
                    text_score += 15
            elif style_lower == 'scandinavian':
                if any(word in item_text for word in ['scandinavian', 'nordic', 'hygge', 'minimal']):
                    text_score += 15
            elif style_lower == 'old money':
                if any(word in item_text for word in ['old money', 'luxury', 'classic', 'timeless']):
                    text_score += 15
            # Phase 4 styles
            elif style_lower == 'clean girl':
                if any(word in item_text for word in ['clean girl', 'minimal', 'fresh', 'natural']):
                    text_score += 15
            elif style_lower == 'punk':
                if any(word in item_text for word in ['punk', 'studded', 'leather', 'chains']):
                    text_score += 15
            elif style_lower == 'edgy':
                if any(word in item_text for word in ['edgy', 'bold', 'leather', 'rock']):
                    text_score += 15
            elif style_lower == 'french girl':
                if any(word in item_text for word in ['french girl', 'parisian', 'chic', 'effortless']):
                    text_score += 15
            elif style_lower == 'urban professional':
                if any(word in item_text for word in ['urban professional', 'modern professional', 'city']):
                    text_score += 15
            elif style_lower == 'techwear':
                if any(word in item_text for word in ['techwear', 'technical', 'functional', 'utility']):
                    text_score += 15
            elif style_lower == 'coastal grandmother':
                if any(word in item_text for word in ['coastal grandmother', 'linen', 'breezy']):
                    text_score += 15
            
            total = metadata_score + text_score
            logger.debug(f"   🎨 Final {style_lower} score: {total} (metadata: {metadata_score}, text: {text_score})")
            return max(total, -50)  # Cap at -50 to prevent over-penalization
    
    # Standard text-based scoring for all other styles
    item_name = str(item.get('name', '') if item else '').lower()
    item_type = str(item.get('type', '') if item else '').lower()
    item_description = str(item.get('description', '') if item else '').lower()
    item_material = str(item.get('material', '') if item else '').lower()
    
    item_text = f"{item_name} {item_type} {item_description} {item_material}"
    
    # Define style-specific scoring - MATCHES FRONTEND EXACTLY (35 styles)
    style_scoring = {
        # Academic & Intellectual (3 styles)
        'dark academia': {
            'highly_appropriate': ['dark', 'academia', 'academic', 'scholarly', 'vintage', 'tweed', 'plaid', 'corduroy', 'blazer', 'cardigan', 'turtleneck', 'oxford', 'loafer'],
            'appropriate': ['button-up', 'sweater', 'trousers', 'brown', 'burgundy', 'forest green', 'navy', 'beige', 'pleated', 'cable knit', 'wool'],
            'inappropriate': ['neon', 'bright colors', 'overly casual', 'graphic tee'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'joggers', 'sweatpants', 'tank top']
        },
        'light academia': {
            'highly_appropriate': ['light', 'academia', 'academic', 'scholarly', 'cream', 'beige', 'white', 'linen', 'blazer', 'cardigan', 'oxford', 'loafer'],
            'appropriate': ['button-up', 'sweater', 'trousers', 'light colors', 'neutral', 'soft', 'pleated', 'airy'],
            'inappropriate': ['dark colors', 'neon', 'bright', 'overly casual'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'joggers', 'sweatpants']
        },
        'old money': {
            'highly_appropriate': ['old money', 'wealthy', 'luxury', 'classic', 'timeless', 'polo', 'cable knit', 'cashmere', 'tailored', 'refined', 'elegant'],
            'appropriate': ['golf', 'tennis', 'yacht', 'preppy', 'blazer', 'loafers', 'chinos', 'quality'],
            'inappropriate': ['trendy', 'fast fashion', 'loud', 'flashy'],
            'highly_inappropriate': ['athletic wear', 'gym', 'workout', 'cheap', 'disposable']
        },
        
        # Trendy & Modern (4 styles)
        'y2k': {
            'highly_appropriate': ['y2k', '2000s', 'nostalgic', 'butterfly', 'low-rise', 'crop', 'mini', 'platform', 'chunky', 'metallic', 'velour', 'rhinestone'],
            'appropriate': ['baby tee', 'cargo', 'denim', 'pink', 'juicy', 'tracksuit', 'sparkle'],
            'inappropriate': ['formal', 'business', 'traditional', 'conservative'],
            'highly_inappropriate': ['suit', 'blazer', 'professional', 'corporate']
        },
        'coastal grandmother': {
            'highly_appropriate': ['coastal', 'grandmother', 'linen', 'relaxed', 'effortless', 'neutral', 'beige', 'white', 'blue', 'oversized', 'breezy'],
            'appropriate': ['casual', 'elegant', 'timeless', 'comfortable', 'natural'],
            'inappropriate': ['tight', 'formal', 'structured'],
            'highly_inappropriate': ['athletic', 'gym', 'workout', 'flashy']
        },
        'clean girl': {
            'highly_appropriate': ['clean girl', 'minimal', 'simple', 'fresh', 'neutral', 'natural', 'effortless', 'polished', 'understated', 'basic'],
            'appropriate': ['white', 'beige', 'classic', 'sleek', 'modern'],
            'inappropriate': ['busy', 'loud', 'flashy', 'maximalist', 'bold'],
            'highly_inappropriate': ['gothic', 'punk', 'grunge', 'distressed']
        },
        'cottagecore': {
            'highly_appropriate': ['cottagecore', 'cottage', 'pastoral', 'rustic', 'vintage', 'floral', 'lace', 'embroidered', 'prairie', 'gingham', 'pinafore'],
            'appropriate': ['dress', 'skirt', 'cardigan', 'blouse', 'apron', 'smock', 'straw', 'wicker', 'mary janes', 'clogs'],
            'inappropriate': ['modern', 'sleek', 'minimalist'],
            'highly_inappropriate': ['athletic', 'corporate', 'business', 'suit', 'tech']
        },
        
        # Artistic & Creative (4 styles)
        'avant-garde': {
            'highly_appropriate': ['avant-garde', 'experimental', 'unconventional', 'artistic', 'architectural', 'sculptural', 'asymmetric', 'deconstructed', 'conceptual'],
            'appropriate': ['innovative', 'unique', 'bold', 'creative', 'statement'],
            'inappropriate': ['basic', 'conventional', 'traditional'],
            'highly_inappropriate': ['boring', 'plain', 'conservative', 'mainstream']
        },
        'artsy': {
            'highly_appropriate': ['artsy', 'artistic', 'creative', 'unique', 'asymmetric', 'avant-garde', 'statement', 'bold', 'eclectic'],
            'appropriate': ['colorful', 'patterned', 'mixed', 'layered', 'oversized', 'wide-leg', 'unusual'],
            'inappropriate': ['basic', 'plain', 'simple', 'conservative'],
            'highly_inappropriate': ['corporate', 'business casual', 'traditional suit']
        },
        'maximalist': {
            'highly_appropriate': ['maximalist', 'bold', 'colorful', 'patterns', 'mixed prints', 'layered', 'statement', 'more is more', 'eclectic', 'vibrant'],
            'appropriate': ['accessories', 'jewelry', 'embellished', 'decorative'],
            'inappropriate': ['minimal', 'simple', 'plain'],
            'highly_inappropriate': ['understated', 'boring', 'monochrome', 'basic']
        },
        'colorblock': {
            'highly_appropriate': ['colorblock', 'color blocking', 'bold colors', 'contrasting', 'geometric', 'blocks', 'primary colors', 'vibrant'],
            'appropriate': ['modern', 'graphic', 'striking'],
            'inappropriate': ['muted', 'neutral', 'monochrome'],
            'highly_inappropriate': ['black and white only', 'beige', 'boring']
        },
        
        # Professional & Classic (4 styles)
        'business casual': {
            'highly_appropriate': ['business casual', 'professional', 'work', 'office', 'smart', 'polished', 'blazer', 'trousers', 'button-up'],
            'appropriate': ['loafers', 'dress shoes', 'blouse', 'collared', 'structured'],
            'inappropriate': ['casual', 'athletic', 'distressed'],
            'highly_inappropriate': ['gym', 'workout', 'hoodie', 'sweatshirt', 'joggers', 'sneakers', 't-shirt']
        },
        'classic': {
            'highly_appropriate': ['classic', 'timeless', 'traditional', 'elegant', 'sophisticated', 'refined', 'tailored', 'well-fitted'],
            'appropriate': ['button-up', 'button-down', 'collared', 'blazer', 'trousers', 'chinos', 'oxford', 'loafers', 'simple', 'clean', 'structured', 'neutral'],
            'inappropriate': ['distressed', 'ripped', 'overly casual', 'worn', 'graphic tee'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'joggers', 'sweatpants', 'hoodie', 'overly trendy']
        },
        'preppy': {
            'highly_appropriate': ['preppy', 'collegiate', 'classic', 'nautical', 'striped', 'polo', 'button-down', 'khaki'],
            'appropriate': ['blazer', 'sweater', 'cardigan', 'chinos', 'boat shoes', 'oxford', 'clean', 'crisp'],
            'inappropriate': ['grunge', 'edgy', 'distressed'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'goth', 'punk', 'overly casual']
        },
        'urban professional': {
            'highly_appropriate': ['urban professional', 'modern professional', 'city', 'sleek', 'contemporary', 'polished', 'minimalist', 'tailored', 'sophisticated'],
            'appropriate': ['structured', 'quality', 'well-fitted', 'modern'],
            'inappropriate': ['casual', 'sloppy', 'outdated'],
            'highly_inappropriate': ['athletic', 'gym', 'workout', 'loungewear']
        },
        
        # Urban & Street (4 styles)
        'streetwear': {
            'highly_appropriate': ['streetwear', 'urban', 'casual', 'trendy', 'oversized', 'graphic', 'sneakers', 'hoodie'],
            'appropriate': ['t-shirt', 'jeans', 'joggers', 'bomber', 'track', 'athletic', 'logo'],
            'inappropriate': ['formal', 'business', 'dressy', 'traditional'],
            'highly_inappropriate': ['suit', 'blazer', 'dress pants', 'dress shoes', 'heels', 'corporate']
        },
        'techwear': {
            'highly_appropriate': ['techwear', 'technical', 'functional', 'utility', 'tactical', 'waterproof', 'breathable', 'cargo', 'futuristic'],
            'appropriate': ['black', 'straps', 'zippers', 'performance', 'modern'],
            'inappropriate': ['formal', 'dressy', 'delicate'],
            'highly_inappropriate': ['vintage', 'retro', 'romantic', 'flowy']
        },
        'grunge': {
            'highly_appropriate': ['grunge', 'flannel', 'plaid shirt', 'ripped', 'distressed', 'band tee', 'combat boots', 'oversized', 'layered', 'worn'],
            'appropriate': ['dark', 'vintage tee', 'denim', 'casual', 'beanie', 'converse'],
            'inappropriate': ['polished', 'refined', 'preppy', 'neat'],
            'highly_inappropriate': ['formal', 'corporate', 'business', 'elegant', 'sophisticated']
        },
        'hipster': {
            'highly_appropriate': ['hipster', 'indie', 'vintage', 'retro', 'quirky', 'artisanal', 'unique', 'alternative', 'thrift'],
            'appropriate': ['flannel', 'skinny jeans', 'boots', 'beanie', 'glasses', 'beard'],
            'inappropriate': ['mainstream', 'corporate', 'basic'],
            'highly_inappropriate': ['formal', 'business', 'conventional']
        },
        
        # Feminine & Romantic (4 styles)
        'romantic': {
            'highly_appropriate': ['romantic', 'feminine', 'flowy', 'delicate', 'soft', 'lace', 'ruffles', 'floral'],
            'appropriate': ['dress', 'skirt', 'blouse', 'pastel', 'chiffon', 'silk', 'satin', 'elegant'],
            'inappropriate': ['harsh', 'structured', 'masculine'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'cargo', 'combat', 'utilitarian']
        },
        'boho': {
            'highly_appropriate': ['boho', 'bohemian', 'flowy', 'free', 'ethnic', 'vintage', 'embroidered', 'fringe', 'maxi', 'loose', 'layered'],
            'appropriate': ['natural', 'earthy', 'sandals', 'boots', 'casual'],
            'inappropriate': ['structured', 'formal', 'business'],
            'highly_inappropriate': ['athletic', 'sport', 'corporate', 'suit', 'blazer']
        },
        'french girl': {
            'highly_appropriate': ['french girl', 'parisian', 'effortless', 'chic', 'simple', 'classic', 'striped', 'beret', 'trench', 'ballet flats'],
            'appropriate': ['timeless', 'elegant', 'minimal', 'quality'],
            'inappropriate': ['flashy', 'loud', 'overly trendy', 'maximalist'],
            'highly_inappropriate': ['athletic', 'gym', 'workout', 'tacky']
        },
        'pinup': {
            'highly_appropriate': ['pinup', 'vintage', 'retro', '50s', 'polka dot', 'high waist', 'swing dress', 'rockabilly'],
            'appropriate': ['red lips', 'cat eye', 'pin curl', 'vintage style', 'feminine'],
            'inappropriate': ['modern', 'minimalist', 'athletic'],
            'highly_inappropriate': ['grunge', 'punk', 'goth', 'techwear']
        },
        
        # Modern & Minimal (3 styles)
        'minimalist': {
            'highly_appropriate': ['minimalist', 'simple', 'clean', 'modern', 'sleek', 'neutral', 'monochrome', 'streamlined'],
            'appropriate': ['solid', 'plain', 'basic', 'understated', 'refined', 'tailored'],
            'inappropriate': ['busy', 'patterned', 'embellished', 'ornate'],
            'highly_inappropriate': ['loud', 'graphic', 'overly decorative', 'bohemian', 'maximalist']
        },
        'modern': {
            'highly_appropriate': ['modern', 'contemporary', 'current', 'sleek', 'clean lines', 'minimalist', 'updated', 'fresh'],
            'appropriate': ['stylish', 'trendy', 'fashionable', 'sophisticated'],
            'inappropriate': ['vintage', 'outdated', 'retro'],
            'highly_inappropriate': ['old-fashioned', 'dated', 'archaic']
        },
        'scandinavian': {
            'highly_appropriate': ['scandinavian', 'nordic', 'minimal', 'neutral', 'cozy', 'hygge', 'simple', 'functional', 'natural'],
            'appropriate': ['muted colors', 'wool', 'knitwear', 'clean'],
            'inappropriate': ['flashy', 'loud', 'maximalist', 'busy'],
            'highly_inappropriate': ['neon', 'bright colors', 'excessive decoration']
        },
        
        # Alternative & Edgy (4 styles)
        'gothic': {
            'highly_appropriate': ['gothic', 'goth', 'dark', 'black', 'lace', 'velvet', 'corset', 'platform boots', 'choker'],
            'appropriate': ['dark makeup', 'silver', 'dramatic', 'Victorian'],
            'inappropriate': ['bright', 'pastel', 'preppy'],
            'highly_inappropriate': ['corporate', 'business', 'clean girl', 'coastal']
        },
        'punk': {
            'highly_appropriate': ['punk', 'studded', 'leather', 'spikes', 'chains', 'safety pins', 'plaid', 'tartan', 'combat boots', 'band', 'ripped'],
            'appropriate': ['graphic', 'torn', 'black', 'dark', 'diy', 'patches'],
            'inappropriate': ['preppy', 'soft', 'pastel', 'delicate'],
            'highly_inappropriate': ['formal', 'business', 'corporate', 'conservative', 'traditional']
        },
        'cyberpunk': {
            'highly_appropriate': ['cyberpunk', 'futuristic', 'neon', 'tech', 'metallic', 'holographic', 'led', 'cyber', 'dystopian'],
            'appropriate': ['techwear', 'black', 'electric', 'urban'],
            'inappropriate': ['vintage', 'classic', 'traditional'],
            'highly_inappropriate': ['natural', 'organic', 'cottagecore', 'boho']
        },
        'edgy': {
            'highly_appropriate': ['edgy', 'bold', 'leather', 'studded', 'distressed', 'ripped', 'dark', 'black', 'rock'],
            'appropriate': ['denim', 'boots', 'chain', 'zipper', 'asymmetric', 'moto'],
            'inappropriate': ['pastel', 'soft', 'delicate', 'preppy'],
            'highly_inappropriate': ['romantic', 'frilly', 'lace', 'overly feminine', 'corporate']
        },
        
        # Seasonal & Lifestyle (5 styles)
        'coastal chic': {
            'highly_appropriate': ['coastal', 'beach', 'nautical', 'breezy', 'linen', 'white', 'blue', 'striped', 'relaxed', 'resort'],
            'appropriate': ['summer', 'sandals', 'lightweight', 'fresh'],
            'inappropriate': ['heavy', 'formal', 'structured'],
            'highly_inappropriate': ['athletic', 'gym', 'workout', 'gothic']
        },
        'athleisure': {
            'highly_appropriate': ['athletic', 'sport', 'performance', 'moisture-wicking', 'breathable', 'activewear', 'gym', 'workout', 'running', 'yoga'],
            'appropriate': ['comfortable', 'stretchy', 'casual', 'relaxed', 'cotton', 'polyester'],
            'inappropriate': ['formal', 'business', 'dressy', 'structured'],
            'highly_inappropriate': ['suit', 'blazer', 'dress pants', 'dress shirt', 'tie', 'oxford', 'formal pants', 'dress shoes', 'heels']
        },
        'casual cool': {
            'highly_appropriate': ['casual', 'cool', 'relaxed', 'effortless', 'comfortable', 'everyday', 'laid-back', 'easy'],
            'appropriate': ['jeans', 't-shirt', 'sneakers', 'simple', 'accessible'],
            'inappropriate': ['formal', 'business', 'dressy'],
            'highly_inappropriate': ['suit', 'tie', 'dress pants', 'very formal']
        },
        'loungewear': {
            'highly_appropriate': ['lounge', 'comfortable', 'cozy', 'soft', 'relaxed', 'home', 'pajama', 'sweatpant', 'oversized', 'comfy'],
            'appropriate': ['fleece', 'cotton', 'jersey', 'easy', 'casual'],
            'inappropriate': ['formal', 'business', 'structured', 'tight'],
            'highly_inappropriate': ['suit', 'blazer', 'heels', 'dress shoes', 'formal wear']
        },
        'workout': {
            'highly_appropriate': ['workout', 'gym', 'athletic', 'sport', 'fitness', 'training', 'exercise', 'performance', 'activewear', 'sports bra'],
            'appropriate': ['leggings', 'shorts', 'tank', 'moisture-wicking', 'breathable'],
            'inappropriate': ['formal', 'dressy', 'casual street wear'],
            'highly_inappropriate': ['suit', 'dress', 'heels', 'business attire']
        }
    }
    
    # If style not in our scoring dict, use permissive default scoring
    if style.lower() not in style_scoring:
        logger.info(f"⚠️ Unknown style '{style}', using permissive default scoring")
        # Return moderate positive score for unknown styles to be inclusive
        # Give bonus points for common versatile attributes
        default_score = 10  # Base score for unknown styles
        
        # Add points for versatile attributes that work with most styles
        versatile_keywords = ['versatile', 'classic', 'comfortable', 'casual', 'simple', 'clean', 'neutral']
        for keyword in versatile_keywords:
            if keyword in item_text:
                default_score += 5
        
        # Subtract points only for extremely inappropriate items (athletic gear for formal occasions)
        extreme_negatives = ['gym', 'workout', 'athletic', 'sweatpants', 'extremely casual']
        for negative in extreme_negatives:
            if negative in item_text and style.lower() in ['formal', 'business', 'elegant']:
                default_score -= 10
        
        return max(default_score, 5)  # Ensure at least a small positive score
    
    scoring = style_scoring[style.lower()]
    total_score = 0
    
    # Check for highly appropriate indicators (+30 points)
    for indicator in (scoring.get('highly_appropriate', []) if scoring else []):
        if indicator in item_text:
            total_score += 30
            
    # Check for appropriate indicators (+15 points)
    for indicator in (scoring.get('appropriate', []) if scoring else []):
        if indicator in item_text:
            total_score += 15
            
    # Check for inappropriate indicators (-25 points)
    for indicator in (scoring.get('inappropriate', []) if scoring else []):
        if indicator in item_text:
            total_score -= 25
            
    # Check for highly inappropriate indicators (-50 points)
    for indicator in (scoring.get('highly_inappropriate', []) if scoring else []):
        if indicator in item_text:
            total_score -= 50
    
    # If no matches found, give a small positive score to be inclusive
    if total_score == 0:
        total_score = 5  # Small positive score for neutral items
    
    # OCCASION-BASED OVERRIDE: Handle conflicting occasion/style combinations
    # For certain occasions, override style restrictions to ensure functional outfits
    if occasion:
        occasion_lower = occasion.lower()
        
        # GYM/WORKOUT occasions REQUIRE athletic wear, override style penalties
        if occasion_lower in ['gym', 'workout', 'exercise', 'fitness', 'training', 'yoga', 'running']:
            athletic_keywords = ['athletic', 'sport', 'gym', 'workout', 'performance', 'moisture-wicking', 'breathable', 'activewear', 'running', 'yoga', 'training']
            is_athletic_item = any(keyword in item_text for keyword in athletic_keywords)
            
            if is_athletic_item:
                # Athletic items get BONUS points for gym occasions, even if style doesn't match
                logger.info(f"🏋️ Occasion override: Athletic item gets bonus for {occasion_lower} occasion (style={style})")
                total_score = max(total_score, 20)  # Ensure at least 20 points for athletic items during gym occasions
                total_score += 30  # Add significant bonus
        
        # FORMAL occasions REQUIRE formal wear
        elif occasion_lower in ['wedding', 'gala', 'black tie', 'formal event', 'cocktail']:
            formal_keywords = ['formal', 'dress', 'suit', 'blazer', 'elegant', 'gown', 'tuxedo', 'cocktail dress']
            is_formal_item = any(keyword in item_text for keyword in formal_keywords)
            
            if is_formal_item:
                logger.info(f"👔 Occasion override: Formal item gets bonus for {occasion_lower} occasion")
                total_score = max(total_score, 15)
                total_score += 25
        
        # BEACH/SWIM occasions
        elif occasion_lower in ['beach', 'pool', 'swim', 'swimming', 'poolside']:
            beach_keywords = ['swimsuit', 'bikini', 'swim', 'beach', 'shorts', 'sandals', 'flip-flops', 'cover-up']
            is_beach_item = any(keyword in item_text for keyword in beach_keywords)
            
            if is_beach_item:
                logger.info(f"🏖️ Occasion override: Beach item gets bonus for {occasion_lower} occasion")
                total_score = max(total_score, 15)
                total_score += 25
    
    # MOOD-BASED SCORING: Adjust scores based on mood to influence outfit vibe
    if mood:
        mood_lower = mood.lower()
        
        # ROMANTIC MOOD: Prefer soft, elegant, refined pieces (gender-neutral)
        if mood_lower == 'romantic':
            # Universal romantic keywords that work for both genders
            romantic_keywords = [
                'romantic', 'soft', 'delicate', 'flowy', 'elegant', 'refined', 'sophisticated',
                'silk', 'chiffon', 'satin', 'cashmere', 'velvet',  # Elegant materials
                'pastel', 'cream', 'rose', 'lavender', 'soft blue', 'soft pink',  # Soft colors
                'floral', 'lace', 'embroidery',  # Delicate details
                'tailored', 'fitted', 'draped'  # Refined fits
            ]
            has_romantic = any(keyword in item_text for keyword in romantic_keywords)
            
            # Gender-specific romantic items (boost if item matches user's typical items)
            # Note: These are checked but don't penalize if missing (works for both genders)
            feminine_romantic = ['dress', 'skirt', 'blouse']
            masculine_romantic = ['button-up', 'dress shirt', 'blazer', 'suit']
            has_feminine_romantic = any(keyword in item_text for keyword in feminine_romantic)
            has_masculine_romantic = any(keyword in item_text for keyword in masculine_romantic)
            
            harsh_keywords = ['harsh', 'rigid', 'athletic', 'sport', 'cargo', 'utility', 'tactical', 'military']
            has_harsh = any(keyword in item_text for keyword in harsh_keywords)
            
            if has_romantic:
                logger.info(f"💕 Romantic mood: Boosting romantic item")
                total_score += 15
            # Additional boost for gender-appropriate romantic items (if present)
            if has_feminine_romantic or has_masculine_romantic:
                logger.info(f"💕 Romantic mood: Additional boost for romantic item type")
                total_score += 5
            if has_harsh:
                logger.info(f"💕 Romantic mood: Penalizing harsh item")
                total_score -= 10
        
        # PLAYFUL MOOD: Prefer bright colors, fun patterns, casual, energetic pieces
        elif mood_lower == 'playful':
            playful_keywords = ['playful', 'fun', 'bright', 'colorful', 'graphic', 'pattern', 'print', 'casual', 'relaxed', 'quirky', 'unique', 'statement', 'bold color', 'vibrant']
            has_playful = any(keyword in item_text for keyword in playful_keywords)
            
            serious_keywords = ['formal', 'business', 'conservative', 'muted', 'plain', 'boring']
            has_serious = any(keyword in item_text for keyword in serious_keywords)
            
            if has_playful:
                logger.info(f"🎨 Playful mood: Boosting fun item")
                total_score += 15
            if has_serious:
                logger.info(f"🎨 Playful mood: Penalizing serious item")
                total_score -= 10
        
        # SERENE MOOD: Prefer muted tones, comfortable, simple, calming pieces
        elif mood_lower == 'serene':
            serene_keywords = ['serene', 'calm', 'peaceful', 'comfortable', 'soft', 'muted', 'neutral', 'beige', 'cream', 'white', 'gray', 'simple', 'minimal', 'relaxed', 'cozy', 'natural']
            has_serene = any(keyword in item_text for keyword in serene_keywords)
            
            chaotic_keywords = ['loud', 'busy', 'flashy', 'neon', 'bright', 'bold pattern', 'maximalist']
            has_chaotic = any(keyword in item_text for keyword in chaotic_keywords)
            
            if has_serene:
                logger.info(f"🧘 Serene mood: Boosting calming item")
                total_score += 15
            if has_chaotic:
                logger.info(f"🧘 Serene mood: Penalizing chaotic item")
                total_score -= 10
        
        # DYNAMIC MOOD: Prefer bold colors, statement pieces, energetic, attention-grabbing looks
        elif mood_lower == 'dynamic':
            dynamic_keywords = ['dynamic', 'bold', 'statement', 'striking', 'vibrant', 'energetic', 'dramatic', 'eye-catching', 'standout', 'colorful', 'bright', 'strong', 'powerful']
            has_dynamic = any(keyword in item_text for keyword in dynamic_keywords)
            
            boring_keywords = ['plain', 'boring', 'basic', 'muted', 'understated', 'subtle']
            has_boring = any(keyword in item_text for keyword in boring_keywords)
            
            if has_dynamic:
                logger.info(f"⚡ Dynamic mood: Boosting bold item")
                total_score += 15
            if has_boring:
                logger.info(f"⚡ Dynamic mood: Penalizing plain item")
                total_score -= 10
        
        # BOLD MOOD: Prefer daring, unconventional, fashion-forward pieces (already handled in exclusions)
        # Additional scoring for bold items
        elif mood_lower == 'bold':
            bold_keywords = ['bold', 'daring', 'unconventional', 'edgy', 'statement', 'dramatic', 'unique', 'avant-garde', 'fashion-forward', 'striking']
            has_bold = any(keyword in item_text for keyword in bold_keywords)
            
            safe_keywords = ['safe', 'basic', 'conventional', 'traditional', 'conservative']
            has_safe = any(keyword in item_text for keyword in safe_keywords)
            
            if has_bold:
                logger.info(f"🔥 Bold mood: Boosting daring item")
                total_score += 15
            if has_safe:
                logger.info(f"🔥 Bold mood: Penalizing safe item")
                total_score -= 8
        
        # SUBTLE MOOD: Prefer understated, neutral, minimal, refined pieces
        elif mood_lower == 'subtle':
            subtle_keywords = ['subtle', 'understated', 'minimal', 'simple', 'refined', 'elegant', 'neutral', 'muted', 'soft', 'quiet', 'timeless', 'classic', 'clean']
            has_subtle = any(keyword in item_text for keyword in subtle_keywords)
            
            loud_keywords = ['loud', 'flashy', 'bold', 'bright', 'neon', 'statement', 'attention-grabbing', 'maximalist']
            has_loud = any(keyword in item_text for keyword in loud_keywords)
            
            if has_subtle:
                logger.info(f"🤫 Subtle mood: Boosting understated item")
                total_score += 15
            if has_loud:
                logger.info(f"🤫 Subtle mood: Penalizing loud item")
                total_score -= 10
    
    return total_score

