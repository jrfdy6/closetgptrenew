"""
Style-related functions for outfit generation and management.
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
    
    # Define style-appropriate keywords for different styles
    style_filters = {
        'athleisure': {
            'include_keywords': ['athletic', 'sport', 'gym', 'track', 'jogger', 'sweat', 'hoodie', 'sneaker', 'running', 'workout', 'yoga', 'legging', 'active', 'performance'],
            'exclude_keywords': ['dress', 'formal', 'suit', 'blazer', 'business', 'oxford', 'heel', 'dress shirt', 'tie', 'formal pants'],
            'preferred_types': ['t-shirt', 'tank', 'hoodie', 'sweatshirt', 'joggers', 'leggings', 'sweatpants', 'sneakers', 'athletic shoes', 'track jacket']
        },
        'casual': {
            'include_keywords': ['casual', 'everyday', 'comfortable', 'relaxed'],
            'exclude_keywords': ['formal', 'business', 'dressy', 'cocktail'],
            'preferred_types': ['t-shirt', 'jeans', 'shorts', 'sneakers', 'casual shoes']
        },
        'formal': {
            'include_keywords': ['formal', 'dress', 'business', 'professional', 'suit', 'blazer'],
            'exclude_keywords': ['casual', 'athletic', 'sport', 'gym', 'sweat'],
            'preferred_types': ['dress shirt', 'blazer', 'suit', 'dress pants', 'dress shoes', 'heels']
        },
        'business': {
            'include_keywords': ['business', 'professional', 'work', 'office', 'formal'],
            'exclude_keywords': ['casual', 'athletic', 'sport', 'gym', 'sweat'],
            'preferred_types': ['dress shirt', 'blazer', 'dress pants', 'dress shoes', 'blouse']
        },
        'classic': {
            'include_keywords': ['classic', 'timeless', 'traditional', 'elegant', 'sophisticated', 'refined', 'tailored', 'button', 'collared', 'oxford', 'loafer', 'chino', 'trouser'],
            'exclude_keywords': ['extremely casual', 'gym', 'workout', 'athletic wear'],
            'preferred_types': ['button-up', 'button-down', 'blazer', 'dress shirt', 'trousers', 'chinos', 'dress pants', 'oxford shoes', 'loafers', 'dress shoes']
        },
        'romantic': {
            'include_keywords': ['romantic', 'feminine', 'flowy', 'delicate', 'soft', 'lace', 'ruffle', 'floral', 'dress', 'skirt', 'pastel'],
            'exclude_keywords': ['harsh', 'masculine', 'athletic', 'gym', 'cargo'],
            'preferred_types': ['dress', 'skirt', 'blouse', 'heels', 'flats', 'cardigan']
        },
        'edgy': {
            'include_keywords': ['edgy', 'bold', 'leather', 'studded', 'distressed', 'ripped', 'dark', 'black', 'rock', 'denim', 'boot'],
            'exclude_keywords': ['pastel', 'delicate', 'preppy', 'corporate'],
            'preferred_types': ['leather jacket', 'denim', 'boots', 'dark pants', 'black clothing']
        },
        'bohemian': {
            'include_keywords': ['bohemian', 'boho', 'flowy', 'free', 'ethnic', 'vintage', 'embroidered', 'fringe', 'maxi', 'loose', 'layered', 'natural'],
            'exclude_keywords': ['structured', 'formal', 'business', 'corporate'],
            'preferred_types': ['maxi dress', 'maxi skirt', 'loose top', 'sandals', 'boots']
        },
        'preppy': {
            'include_keywords': ['preppy', 'collegiate', 'classic', 'nautical', 'stripe', 'polo', 'button', 'khaki', 'blazer', 'sweater'],
            'exclude_keywords': ['grunge', 'edgy', 'distressed', 'athletic wear'],
            'preferred_types': ['polo shirt', 'button-down', 'blazer', 'sweater', 'cardigan', 'chinos', 'boat shoes', 'oxford shoes']
        },
        'minimalist': {
            'include_keywords': ['minimalist', 'simple', 'clean', 'modern', 'sleek', 'neutral', 'monochrome', 'basic', 'plain', 'solid'],
            'exclude_keywords': ['busy', 'patterned', 'embellished', 'ornate', 'loud'],
            'preferred_types': ['basic tee', 'plain shirt', 'simple pants', 'solid color']
        },
        'vintage': {
            'include_keywords': ['vintage', 'retro', 'classic', 'antique', 'timeless', 'heritage', 'traditional', 'high-waist', 'midi', 'pleated'],
            'exclude_keywords': ['modern', 'contemporary', 'trendy', 'athletic', 'tech'],
            'preferred_types': ['high-waisted pants', 'midi skirt', 'button-up', 'pleated', 'vintage dress']
        },
        'streetwear': {
            'include_keywords': ['streetwear', 'urban', 'casual', 'trendy', 'oversized', 'graphic', 'sneaker', 'hoodie', 'jogger', 'bomber'],
            'exclude_keywords': ['formal', 'business', 'dressy', 'corporate'],
            'preferred_types': ['hoodie', 't-shirt', 'jeans', 'joggers', 'sneakers', 'bomber jacket']
        }
    }
    
    # Get filter criteria for this style
    # If style not found, use permissive default that accepts most items
    if style_lower not in style_filters:
        logger.info(f"⚠️ Unknown style '{style}' in filter, using permissive default")
        # For unknown styles, be very permissive - only exclude extreme athletic/gym wear for non-athletic styles
        filter_criteria = {
            'include_keywords': [],  # Accept all by default
            'exclude_keywords': ['gym', 'workout', 'athletic wear'] if style_lower not in ['athleisure', 'athletic'] else [],
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
            # For athleisure, be more restrictive - only include items that explicitly match
            if style_lower == 'athleisure':
                item_name_for_log = item_name if isinstance(item, dict) else str(getattr(item, 'name', 'unnamed'))
                logger.info(f"⚠️ Skipping {item_name_for_log} for athleisure (not explicitly athletic)")
            else:
                # For other styles (including unknown styles), include items that don't explicitly conflict
                # This ensures we don't filter out too many items for classic and other common styles
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
        'formal': {
            'casual_indicators': ['athletic', 'sport', 'gym', 'workout', 'jogger', 'sweat', 'hoodie', 'sneaker'],
            'casual_materials': ['jersey', 'fleece', 'athletic'],
            'casual_types': ['hoodie', 'sweatshirt', 'joggers', 'sweatpants', 'sneakers', 'athletic shoes']
        },
        'business': {
            'casual_indicators': ['athletic', 'sport', 'gym', 'workout', 'casual', 'distressed'],
            'casual_materials': ['jersey', 'fleece', 'athletic'],
            'casual_types': ['hoodie', 'sweatshirt', 'joggers', 'sneakers', 't-shirt']
        },
        'classic': {
            'athletic_indicators': ['athletic', 'sport', 'gym', 'workout', 'running', 'basketball'],
            'athletic_materials': ['jersey', 'fleece', 'athletic', 'mesh'],
            'athletic_types': ['sneakers', 'athletic shoes', 'running shoes', 'basketball shoes', 'joggers', 'sweatpants']
        }
    }
    
    # BRIDGE RULES: Allow cross-style combinations for specific occasion/style pairs
    bridge_rules = {
        ('classic', 'athletic'): {
            'allowed_athletic_items': ['sneakers', 'athletic shoes', 'polo shirt', 'chinos', 'joggers', 'athletic shorts'],
            'allowed_keywords': ['polo', 'chino', 'sneaker', 'athletic', 'sport', 'running', 'tennis']
        },
        ('athletic', 'classic'): {
            'allowed_classic_items': ['polo shirt', 'chinos', 'sneakers', 'athletic shoes', 'casual button-up'],
            'allowed_keywords': ['polo', 'chino', 'sneaker', 'classic', 'casual', 'button']
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
    
    # Check for bridge rules first (before standard exclusions)
    try:
        bridge_key = (style.lower(), 'athletic') if 'athletic' in item_text else None
        if not bridge_key:
            bridge_key = ('athletic', style.lower()) if style.lower() in ['classic', 'casual'] else None
        
        if bridge_key and bridge_key in bridge_rules:
            bridge_rule = bridge_rules[bridge_key]
            # Check if item matches bridge rule criteria
            for keyword in bridge_rule['allowed_keywords']:
                if keyword in item_text:
                    exclusion_debug.append({
                        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                        "bridge_rule_applied": f"{bridge_key[0]} + {bridge_key[1]} allows {keyword}",
                        "matched_keyword": keyword,
                        "reason": "cross-style bridge rule"
                    })
                    print(f"🌉 BRIDGE RULE: Allowing {keyword} for {bridge_key[0]} + {bridge_key[1]} combination")
                    return None  # Allow item through bridge rule
    except Exception as bridge_error:
        logger.warning(f"⚠️ Bridge rule error: {bridge_error}")
        # Continue with normal exclusion logic if bridge rules fail
    
    for category, indicators in rules.items():
        for indicator in indicators:
            if indicator in item_text:
                # BOLD MOOD EXCEPTION: Allow cross-style blending for fashion-forward looks
                if mood and mood.lower() == 'bold':
                    # Allow athletic items with Classic style for bold fashion statements
                    if style == 'classic' and category in ['athletic_indicators', 'athletic_materials', 'athletic_types']:
                        exclusion_debug.append({
                            "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                            "exclusion_bypassed": f"Bold mood allows {indicator} with {style}",
                            "matched_indicator": indicator,
                            "category": category,
                            "reason": "fashion-forward bold styling"
                        })
                        print(f"🎨 BOLD EXCEPTION: Allowing {indicator} with {style} for bold fashion statement")
                        continue  # Skip exclusion for bold mood
                    
                    # EXTENDED BOLD EXCEPTION: Allow cross-style items for any style combination
                    if category in ['casual_indicators', 'casual_materials', 'casual_types', 'formal_indicators', 'formal_materials', 'formal_types']:
                        exclusion_debug.append({
                            "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                            "exclusion_bypassed": f"Bold mood allows {indicator} with {style}",
                            "matched_indicator": indicator,
                            "category": category,
                            "reason": "bold mood cross-style blending"
                        })
                        print(f"🎨 BOLD EXCEPTION: Allowing {indicator} with {style} for bold cross-style blending")
                        continue  # Skip exclusion for bold mood
                
                exclusion_debug.append({
                    "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                    "exclusion_reason": f"{indicator} inappropriate for {style}",
                    "matched_indicator": indicator,
                    "category": category
                })
                print(f"🚫 EXCLUSION MATCH: {indicator} found in {item_text}")
                return f"{indicator} inappropriate for {style}"
    
    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
        "result": "no exclusion - item passes hard filter"
    })
    
    return None


def calculate_style_appropriateness_score(style: str, item: Dict[str, Any]) -> int:
    """Calculate style appropriateness score with heavy penalties for mismatches."""
    item_name = str(item.get('name', '') if item else '').lower()
    item_type = str(item.get('type', '') if item else '').lower()
    item_description = str(item.get('description', '') if item else '').lower()
    item_material = str(item.get('material', '') if item else '').lower()
    
    item_text = f"{item_name} {item_type} {item_description} {item_material}"
    
    # Define style-specific scoring
    style_scoring = {
        'athleisure': {
            'highly_appropriate': ['athletic', 'sport', 'performance', 'moisture-wicking', 'breathable', 'activewear', 'gym', 'workout', 'running', 'yoga'],
            'appropriate': ['comfortable', 'stretchy', 'casual', 'relaxed', 'cotton', 'polyester'],
            'inappropriate': ['formal', 'business', 'dressy', 'structured'],
            'highly_inappropriate': ['suit', 'blazer', 'dress pants', 'dress shirt', 'tie', 'oxford', 'formal pants', 'dress shoes', 'heels']
        },
        'formal': {
            'highly_appropriate': ['formal', 'business', 'professional', 'structured', 'tailored', 'dress', 'suit', 'blazer'],
            'appropriate': ['classic', 'elegant', 'refined', 'polished'],
            'inappropriate': ['casual', 'relaxed', 'distressed'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'hoodie', 'sweatshirt', 'joggers', 'sneakers']
        },
        'casual': {
            'highly_appropriate': ['casual', 'comfortable', 'relaxed', 'everyday', 'versatile'],
            'appropriate': ['cotton', 'denim', 'jersey', 'soft'],
            'inappropriate': ['formal', 'business', 'dressy'],
            'highly_inappropriate': ['suit', 'tie', 'dress pants', 'very formal']
        },
        'classic': {
            'highly_appropriate': ['classic', 'timeless', 'traditional', 'elegant', 'sophisticated', 'refined', 'tailored', 'well-fitted'],
            'appropriate': ['button-up', 'button-down', 'collared', 'blazer', 'trousers', 'chinos', 'oxford', 'loafers', 'simple', 'clean', 'structured', 'neutral'],
            'inappropriate': ['distressed', 'ripped', 'overly casual', 'worn', 'graphic tee'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'joggers', 'sweatpants', 'hoodie', 'overly trendy']
        },
        'business': {
            'highly_appropriate': ['business', 'professional', 'work', 'office', 'corporate', 'formal', 'executive'],
            'appropriate': ['blazer', 'suit', 'dress shirt', 'dress pants', 'dress shoes', 'blouse', 'pencil skirt', 'structured'],
            'inappropriate': ['casual', 'athletic', 'distressed'],
            'highly_inappropriate': ['gym', 'workout', 'hoodie', 'sweatshirt', 'joggers', 'sneakers', 't-shirt', 'tank top']
        },
        'romantic': {
            'highly_appropriate': ['romantic', 'feminine', 'flowy', 'delicate', 'soft', 'lace', 'ruffles', 'floral'],
            'appropriate': ['dress', 'skirt', 'blouse', 'pastel', 'chiffon', 'silk', 'satin', 'elegant'],
            'inappropriate': ['harsh', 'structured', 'masculine'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'cargo', 'combat', 'utilitarian']
        },
        'edgy': {
            'highly_appropriate': ['edgy', 'bold', 'leather', 'studded', 'distressed', 'ripped', 'dark', 'black', 'rock'],
            'appropriate': ['denim', 'boots', 'jacket', 'chain', 'zipper', 'asymmetric', 'moto'],
            'inappropriate': ['pastel', 'soft', 'delicate', 'preppy'],
            'highly_inappropriate': ['romantic', 'frilly', 'lace', 'overly feminine', 'corporate']
        },
        'bohemian': {
            'highly_appropriate': ['bohemian', 'boho', 'flowy', 'free-spirited', 'ethnic', 'vintage', 'embroidered', 'fringe'],
            'appropriate': ['maxi', 'dress', 'skirt', 'loose', 'casual', 'layered', 'natural', 'earthy'],
            'inappropriate': ['structured', 'formal', 'business'],
            'highly_inappropriate': ['athletic', 'sport', 'corporate', 'suit', 'blazer']
        },
        'preppy': {
            'highly_appropriate': ['preppy', 'collegiate', 'classic', 'nautical', 'striped', 'polo', 'button-down', 'khaki'],
            'appropriate': ['blazer', 'sweater', 'cardigan', 'chinos', 'boat shoes', 'oxford', 'clean', 'crisp'],
            'inappropriate': ['grunge', 'edgy', 'distressed'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'goth', 'punk', 'overly casual']
        },
        'minimalist': {
            'highly_appropriate': ['minimalist', 'simple', 'clean', 'modern', 'sleek', 'neutral', 'monochrome', 'streamlined'],
            'appropriate': ['solid', 'plain', 'basic', 'understated', 'refined', 'tailored'],
            'inappropriate': ['busy', 'patterned', 'embellished', 'ornate'],
            'highly_inappropriate': ['loud', 'graphic', 'overly decorative', 'bohemian', 'maximalist']
        },
        'vintage': {
            'highly_appropriate': ['vintage', 'retro', 'classic', 'antique', 'timeless', 'heritage', 'traditional'],
            'appropriate': ['high-waisted', 'midi', 'button-up', 'pleated', 'tweed', 'wool', 'leather'],
            'inappropriate': ['modern', 'contemporary', 'trendy'],
            'highly_inappropriate': ['athletic', 'sport', 'tech', 'performance', 'futuristic']
        },
        'streetwear': {
            'highly_appropriate': ['streetwear', 'urban', 'casual', 'trendy', 'oversized', 'graphic', 'sneakers', 'hoodie'],
            'appropriate': ['t-shirt', 'jeans', 'joggers', 'bomber', 'track', 'athletic', 'logo'],
            'inappropriate': ['formal', 'business', 'dressy', 'traditional'],
            'highly_inappropriate': ['suit', 'blazer', 'dress pants', 'dress shoes', 'heels', 'corporate']
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
    
    return total_score
