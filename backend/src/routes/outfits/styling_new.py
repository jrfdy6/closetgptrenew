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


def calculate_style_appropriateness_score(style: str, item: Dict[str, Any], occasion: str = None) -> int:
    """Calculate style appropriateness score with heavy penalties for mismatches."""
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
    
    return total_score

