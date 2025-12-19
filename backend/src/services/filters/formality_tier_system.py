#!/usr/bin/env python3
"""
Formality Tier System for Progressive Outfit Filtering
======================================================

This module implements a comprehensive tier-based filtering system for occasions
that require specific formality levels. The system progressively falls back to
more relaxed tiers if strict tiers don't have enough items or all items are
recently worn.

Architecture:
- Tier 1 (Strict Formal): Suits, blazers, dress shoes
- Tier 2 (Smart Casual): Button-ups, chinos, loafers
- Tier 3 (Creative Casual): Stylish but relaxed items
- Tier 4 (Relaxed): Clean jeans, sneakers
- Tier 5 (Athletic): Gym wear, athletic shoes

Usage:
    tier_system = FormalityTierSystem()
    if tier_system.should_apply_tier_filter(occasion):
        filtered_wardrobe, tier_used = tier_system.apply_progressive_filter(
            wardrobe, occasion, style, recently_used_item_ids
        )
"""

import logging
from enum import Enum
from typing import List, Set, Dict, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FormalityTier(Enum):
    """Formality tiers for progressive filtering"""
    TIER_1_STRICT_FORMAL = "strict_formal"      # Suits, blazers, dress shoes
    TIER_2_SMART_CASUAL = "smart_casual"        # Button-ups, chinos, loafers
    TIER_3_CREATIVE_CASUAL = "creative_casual"  # Stylish but relaxed
    TIER_4_RELAXED = "relaxed"                  # Jeans, sneakers (clean)
    TIER_5_ATHLETIC = "athletic"                # Gym wear, athletic shoes


@dataclass
class TierRequirements:
    """Requirements for each tier"""
    min_items: int = 3  # Minimum items needed to use this tier
    min_fresh_items: int = 2  # Minimum non-recently-worn items


@dataclass
class OccasionTierConfig:
    """Configuration for occasion-specific tier filtering"""
    occasion: str
    primary_tier: FormalityTier
    allowed_tiers: List[FormalityTier]
    style_overrides: Dict[str, FormalityTier]  # Style-specific tier adjustments
    requirements: TierRequirements


# ═══════════════════════════════════════════════════════════════════════
# TIER KEYWORD DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

TIER_1_KEYWORDS = {
    'tops': [
        'blazer', 'suit jacket', 'dress shirt', 'button-up shirt', 'oxford shirt',
        'formal shirt', 'tuxedo shirt', 'dress blouse', 'silk blouse',
        'formal top', 'business shirt', 'professional shirt'
    ],
    'bottoms': [
        'dress pants', 'suit pants', 'dress trousers', 'wool trousers',
        'formal skirt', 'pencil skirt', 'a-line skirt', 'dress skirt',
        'slacks', 'formal pants', 'business pants'
    ],
    'shoes': [
        'oxford shoes', 'dress shoes', 'loafers', 'heels', 'pumps',
        'derby shoes', 'monk strap', 'dress boots', 'formal shoes',
        'leather shoes', 'patent leather'
    ],
    'outerwear': [
        'overcoat', 'peacoat', 'trench coat', 'wool coat',
        'formal coat', 'dress coat'
    ],
    'dresses': [
        'cocktail dress', 'formal dress', 'business dress', 'sheath dress',
        'pencil dress', 'a-line dress'
    ]
}

TIER_2_KEYWORDS = {
    'tops': [
        'button-up', 'collared shirt', 'polo shirt', 'smart sweater',
        'cashmere sweater', 'merino sweater', 'blazer casual',
        'smart casual shirt', 'chambray shirt', 'linen shirt'
    ],
    'bottoms': [
        'chinos', 'khakis', 'dark jeans', 'tailored pants',
        'midi skirt', 'knee-length skirt', 'smart casual pants',
        'tailored shorts', 'bermuda shorts'
    ],
    'shoes': [
        'loafers', 'chelsea boots', 'dress sneakers', 'ankle boots',
        'leather sneakers', 'minimalist sneakers', 'smart casual shoes',
        'suede shoes', 'monk strap casual'
    ],
    'outerwear': [
        'blazer', 'sports coat', 'cardigan', 'smart jacket',
        'unstructured blazer', 'knit blazer'
    ],
    'dresses': [
        'midi dress', 'wrap dress', 'shirt dress', 'smart casual dress',
        'day dress'
    ]
}

TIER_3_KEYWORDS = {
    'tops': [
        't-shirt plain', 'henley', 'sweater', 'turtleneck',
        'smart casual top', 'blouse casual', 'knit top',
        'crew neck', 'v-neck', 'casual shirt'
    ],
    'bottoms': [
        'jeans clean', 'colored chinos', 'casual pants',
        'skirt casual', 'culottes', 'wide-leg pants',
        'relaxed pants', 'casual trousers'
    ],
    'shoes': [
        'clean sneakers', 'canvas shoes', 'casual boots',
        'flats', 'sandals dressy', 'espadrilles',
        'white sneakers', 'leather sneakers'
    ],
    'outerwear': [
        'denim jacket', 'bomber jacket', 'utility jacket',
        'casual blazer', 'field jacket'
    ],
    'dresses': [
        'casual dress', 'sundress', 'maxi dress', 'knit dress',
        't-shirt dress', 'jersey dress'
    ]
}

# Blocked keywords (too casual for any formal tier)
TIER_BLOCKED_KEYWORDS = [
    # Athletic
    'athletic', 'gym', 'workout', 'training', 'sport', 'running',
    'basketball', 'football', 'soccer', 'tennis', 'track',
    # Very casual
    'sweatpants', 'joggers', 'sweatshirt', 'hoodie graphic',
    'tank top', 'crop top', 'ripped', 'distressed', 'torn',
    'graphic tee', 'band tee', 'logo tee',
    # Footwear
    'flip-flop', 'slide', 'crocs', 'slipper', 'athletic shoes',
    'running shoes', 'gym shoes', 'basketball shoes',
    # CRITICAL: Block casual items for interviews
    't-shirt', 'tshirt', 'tee shirt', 'denim shorts', 'jean shorts',
    'cargo shorts', 'athletic shorts', 'running shorts'
]


# ═══════════════════════════════════════════════════════════════════════
# OCCASION CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════

OCCASION_TIER_CONFIGS = {
    # ─────────────────────────────────────────────────────────────────
    # TIER 1: STRICT FORMALITY OCCASIONS
    # ─────────────────────────────────────────────────────────────────
    'interview': OccasionTierConfig(
        occasion='interview',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL  # Only for creative industries
        ],
        style_overrides={
            'light academia': FormalityTier.TIER_2_SMART_CASUAL,
            'dark academia': FormalityTier.TIER_2_SMART_CASUAL,
            'creative': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'artistic': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'tech': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'business': OccasionTierConfig(
        occasion='business',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL
        ],
        style_overrides={
            'business casual': FormalityTier.TIER_2_SMART_CASUAL,
            'smart casual': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'work': OccasionTierConfig(
        occasion='work',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL
        ],
        style_overrides={
            'business casual': FormalityTier.TIER_2_SMART_CASUAL,
            'smart casual': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_2_SMART_CASUAL,
            'tech': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'professional': OccasionTierConfig(
        occasion='professional',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL
        ],
        style_overrides={
            'business casual': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'formal': OccasionTierConfig(
        occasion='formal',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[FormalityTier.TIER_1_STRICT_FORMAL],  # No fallback
        style_overrides={},
        requirements=TierRequirements(min_items=4, min_fresh_items=3)
    ),
    
    'black-tie': OccasionTierConfig(
        occasion='black-tie',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[FormalityTier.TIER_1_STRICT_FORMAL],
        style_overrides={},
        requirements=TierRequirements(min_items=4, min_fresh_items=3)
    ),
    
    'gala': OccasionTierConfig(
        occasion='gala',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[FormalityTier.TIER_1_STRICT_FORMAL],
        style_overrides={},
        requirements=TierRequirements(min_items=4, min_fresh_items=3)
    ),
    
    'wedding': OccasionTierConfig(
        occasion='wedding',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL  # For casual weddings
        ],
        style_overrides={
            'garden party': FormalityTier.TIER_2_SMART_CASUAL,
            'beach wedding': FormalityTier.TIER_2_SMART_CASUAL,
            'cocktail': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=4, min_fresh_items=3)
    ),
    
    'wedding-guest': OccasionTierConfig(
        occasion='wedding-guest',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL
        ],
        style_overrides={
            'garden party': FormalityTier.TIER_2_SMART_CASUAL,
            'beach': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=4, min_fresh_items=3)
    ),
    
    'funeral': OccasionTierConfig(
        occasion='funeral',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[FormalityTier.TIER_1_STRICT_FORMAL],
        style_overrides={},
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # TIER 2: CONTEXT-AWARE FORMALITY
    # ─────────────────────────────────────────────────────────────────
    'cocktail': OccasionTierConfig(
        occasion='cocktail',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL
        ],
        style_overrides={
            'glamorous': FormalityTier.TIER_1_STRICT_FORMAL,
            'elegant': FormalityTier.TIER_1_STRICT_FORMAL,
            'edgy': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'creative': FormalityTier.TIER_3_CREATIVE_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'date-night': OccasionTierConfig(
        occasion='date-night',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_1_STRICT_FORMAL  # For fancy dates
        ],
        style_overrides={
            'romantic': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'elegant': FormalityTier.TIER_1_STRICT_FORMAL,
            'glamorous': FormalityTier.TIER_1_STRICT_FORMAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'date': OccasionTierConfig(
        occasion='date',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_1_STRICT_FORMAL
        ],
        style_overrides={
            'romantic': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'elegant': FormalityTier.TIER_1_STRICT_FORMAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'conference': OccasionTierConfig(
        occasion='conference',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL
        ],
        style_overrides={
            'tech': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'creative': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'corporate': FormalityTier.TIER_1_STRICT_FORMAL,
            'business': FormalityTier.TIER_1_STRICT_FORMAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'presentation': OccasionTierConfig(
        occasion='presentation',
        primary_tier=FormalityTier.TIER_1_STRICT_FORMAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL
        ],
        style_overrides={
            'tech': FormalityTier.TIER_2_SMART_CASUAL,
            'creative': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'meeting': OccasionTierConfig(
        occasion='meeting',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL
        ],
        style_overrides={
            'corporate': FormalityTier.TIER_1_STRICT_FORMAL,
            'tech': FormalityTier.TIER_3_CREATIVE_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'brunch': OccasionTierConfig(
        occasion='brunch',
        primary_tier=FormalityTier.TIER_3_CREATIVE_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_4_RELAXED
        ],
        style_overrides={
            'chic': FormalityTier.TIER_2_SMART_CASUAL,
            'casual': FormalityTier.TIER_4_RELAXED,
            'elegant': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=1)
    ),
    
    'dinner': OccasionTierConfig(
        occasion='dinner',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL
        ],
        style_overrides={
            'elegant': FormalityTier.TIER_1_STRICT_FORMAL,
            'casual': FormalityTier.TIER_3_CREATIVE_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    'night-out': OccasionTierConfig(
        occasion='night-out',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_1_STRICT_FORMAL
        ],
        style_overrides={
            'glamorous': FormalityTier.TIER_1_STRICT_FORMAL,
            'edgy': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'casual': FormalityTier.TIER_3_CREATIVE_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # TIER 3: STYLE-DRIVEN OCCASIONS
    # ─────────────────────────────────────────────────────────────────
    'museum': OccasionTierConfig(
        occasion='museum',
        primary_tier=FormalityTier.TIER_3_CREATIVE_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_4_RELAXED
        ],
        style_overrides={
            'artistic': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'minimalist': FormalityTier.TIER_2_SMART_CASUAL,
            'elegant': FormalityTier.TIER_2_SMART_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=1)
    ),
    
    'art-gallery': OccasionTierConfig(
        occasion='art-gallery',
        primary_tier=FormalityTier.TIER_3_CREATIVE_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL,
            FormalityTier.TIER_4_RELAXED
        ],
        style_overrides={
            'artistic': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'avant-garde': FormalityTier.TIER_3_CREATIVE_CASUAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=1)
    ),
    
    'theater': OccasionTierConfig(
        occasion='theater',
        primary_tier=FormalityTier.TIER_2_SMART_CASUAL,
        allowed_tiers=[
            FormalityTier.TIER_1_STRICT_FORMAL,
            FormalityTier.TIER_2_SMART_CASUAL,
            FormalityTier.TIER_3_CREATIVE_CASUAL
        ],
        style_overrides={
            'elegant': FormalityTier.TIER_1_STRICT_FORMAL,
            'casual': FormalityTier.TIER_3_CREATIVE_CASUAL,
            'glamorous': FormalityTier.TIER_1_STRICT_FORMAL,
        },
        requirements=TierRequirements(min_items=3, min_fresh_items=2)
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# MAIN TIER SYSTEM CLASS
# ═══════════════════════════════════════════════════════════════════════

class FormalityTierSystem:
    """
    Progressive tier filtering system for occasions with formality requirements.
    
    Strategy:
    1. Determine target tier based on occasion + style
    2. Try primary tier first
    3. If insufficient items or all recently worn, fallback to next tier
    4. Continue until sufficient items found or all tiers exhausted
    
    Example:
        >>> tier_system = FormalityTierSystem()
        >>> if tier_system.should_apply_tier_filter('interview'):
        ...     filtered, tier = tier_system.apply_progressive_filter(
        ...         wardrobe, 'interview', 'light academia', recently_used_ids
        ...     )
    """
    
    def __init__(self):
        self.configs = OCCASION_TIER_CONFIGS
        self.tier_keywords = {
            FormalityTier.TIER_1_STRICT_FORMAL: TIER_1_KEYWORDS,
            FormalityTier.TIER_2_SMART_CASUAL: TIER_2_KEYWORDS,
            FormalityTier.TIER_3_CREATIVE_CASUAL: TIER_3_KEYWORDS,
        }
        self.blocked_keywords = TIER_BLOCKED_KEYWORDS
    
    def should_apply_tier_filter(self, occasion: str) -> bool:
        """Check if occasion requires tier filtering"""
        return occasion.lower() in self.configs
    
    def get_target_tier(self, occasion: str, style: str) -> FormalityTier:
        """Determine target tier based on occasion and style"""
        config = self.configs.get(occasion.lower())
        if not config:
            return FormalityTier.TIER_3_CREATIVE_CASUAL  # Default
        
        # Check for style override
        style_lower = (style or '').lower()
        if style_lower in config.style_overrides:
            return config.style_overrides[style_lower]
        
        return config.primary_tier
    
    def apply_progressive_filter(
        self,
        wardrobe: List[Any],
        occasion: str,
        style: str,
        recently_used_item_ids: Set[str],
        safe_get_item_attr_func: callable,
        occasion_fallbacks: Optional[Dict[str, List[str]]] = None
    ) -> Tuple[List[Any], FormalityTier]:
        """
        Apply progressive tier filtering with fallback.
        
        Args:
            wardrobe: List of wardrobe items
            occasion: Occasion name
            style: Style name
            recently_used_item_ids: Set of recently worn item IDs
            safe_get_item_attr_func: Function to safely get item attributes
            occasion_fallbacks: Optional dict of occasion fallbacks for semantic matching
        
        Returns:
            (filtered_wardrobe, tier_used)
        """
        config = self.configs.get(occasion.lower())
        if not config:
            logger.info(f"⚠️ No tier config for occasion '{occasion}', returning full wardrobe")
            return wardrobe, FormalityTier.TIER_3_CREATIVE_CASUAL
        
        target_tier = self.get_target_tier(occasion, style)
        logger.info(f"🎯 TIER SYSTEM: {occasion.upper()} + {style} → Target tier: {target_tier.value}")
        
        # Try each allowed tier in order
        for tier in config.allowed_tiers:
            logger.info(f"📊 Trying TIER: {tier.value}")
            
            filtered_items = self._filter_by_tier(
                wardrobe, 
                tier, 
                safe_get_item_attr_func,
                occasion=occasion,
                occasion_fallbacks=occasion_fallbacks
            )
            fresh_items = [
                item for item in filtered_items
                if safe_get_item_attr_func(item, 'id', '') not in recently_used_item_ids
            ]
            
            logger.info(f"   {len(filtered_items)} total items, {len(fresh_items)} fresh")
            
            # Check if tier has sufficient items
            if len(fresh_items) >= config.requirements.min_fresh_items:
                logger.info(f"✅ Using TIER {tier.value} - sufficient fresh items")
                return filtered_items, tier
            elif len(filtered_items) >= config.requirements.min_items:
                logger.info(f"⚠️ Using TIER {tier.value} - sufficient items but some recently worn")
                return filtered_items, tier
            else:
                logger.warning(f"⚠️ TIER {tier.value} insufficient - trying next tier")
        
        # Last resort: return best available tier
        logger.error(f"🚨 All tiers insufficient - using best available items")
        return wardrobe, target_tier
    
    def _filter_by_tier(
        self,
        wardrobe: List[Any],
        tier: FormalityTier,
        safe_get_item_attr_func: callable,
        occasion: Optional[str] = None,
        occasion_fallbacks: Optional[Dict[str, List[str]]] = None
    ) -> List[Any]:
        """
        Filter wardrobe items by formality tier with intelligent keyword matching
        and occasion compatibility checking.
        
        Args:
            wardrobe: List of wardrobe items
            tier: Formality tier to filter by
            safe_get_item_attr_func: Function to safely get item attributes
            occasion: Target occasion (e.g., "interview")
            occasion_fallbacks: Dict of occasion fallbacks for semantic matching
        
        Returns:
            List of items matching the tier and occasion
        """
        # EXTREME DEBUG LOGGING
        import sys
        print(f"\n{'='*80}", flush=True)
        print(f"🔍 _filter_by_tier CALLED", flush=True)
        print(f"   Tier: {tier.value}", flush=True)
        print(f"   Occasion: {occasion}", flush=True)
        print(f"   Wardrobe size: {len(wardrobe)}", flush=True)
        print(f"   Blocked keywords count: {len(self.blocked_keywords)}", flush=True)
        print(f"   First 5 blocked keywords: {self.blocked_keywords[:5]}", flush=True)
        print(f"{'='*80}\n", flush=True)
        sys.stdout.flush()
        
        keywords = self.tier_keywords.get(tier, {})
        if not keywords:
            # No keywords for this tier, return all
            print(f"⚠️ NO KEYWORDS for tier {tier.value}, returning all items", flush=True)
            sys.stdout.flush()
            return wardrobe
        
        filtered = []
        blocked_count = 0
        for item in wardrobe:
            item_name = safe_get_item_attr_func(item, 'name', '').lower()
            item_type = str(safe_get_item_attr_func(item, 'type', '')).lower()
            
            # EXTREME DEBUG: Log every item
            print(f"🔍 Checking item: '{item_name}' (type: '{item_type}')", flush=True)
            sys.stdout.flush()
            
            # First, check if item is blocked (too casual)
            is_blocked = any(blocked in item_name or blocked in item_type for blocked in self.blocked_keywords)
            
            print(f"   is_blocked check result: {is_blocked}", flush=True)
            sys.stdout.flush()
            
            if is_blocked:
                # Find which keyword blocked it
                blocking_keyword = next((kw for kw in self.blocked_keywords if kw in item_name or kw in item_type), None)
                print(f"   🚫 BLOCKED: '{item_name}' (keyword: '{blocking_keyword}')", flush=True)
                sys.stdout.flush()
                logger.info(f"   🚫 BLOCKED: '{item_name}' (keyword: '{blocking_keyword}')")
                blocked_count += 1
                continue
            
            # Check if item matches tier keywords with INTELLIGENT MATCHING
            matches_tier = False
            for category, category_keywords in keywords.items():
                for keyword in category_keywords:
                    # Split keyword into words for flexible matching
                    keyword_words = keyword.split()
                    
                    if len(keyword_words) > 1:
                        # Multi-word keyword (e.g., "pencil dress", "dress shirt", "oxford shoes")
                        # Check if ALL words from keyword appear in item name/type (order-independent)
                        # This matches:
                        #   - "pencil dress" → "Dress pencil Mustard Yellow" ✅
                        #   - "dress shirt" → "Shirt dress blue" ✅
                        #   - "oxford shoes" → "Shoes oxford brown" ✅
                        if all(word in item_name or word in item_type for word in keyword_words):
                            matches_tier = True
                            break
                    else:
                        # Single-word keyword: use simple substring match
                        if keyword in item_name or keyword in item_type:
                            matches_tier = True
                            break
                
                if matches_tier:
                    break
            
            # Also check metadata for formality level
            if not matches_tier:  # Only check metadata if keyword match failed
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        formal_level = (visual_attrs.get('formalLevel') or '').lower()
                        
                        if tier == FormalityTier.TIER_1_STRICT_FORMAL:
                            if formal_level in ['formal', 'business', 'professional', 'dress']:
                                matches_tier = True
                        elif tier == FormalityTier.TIER_2_SMART_CASUAL:
                            if formal_level in ['smart casual', 'business casual', 'semi-formal']:
                                matches_tier = True
                        elif tier == FormalityTier.TIER_3_CREATIVE_CASUAL:
                            if formal_level in ['casual', 'smart casual', 'creative']:
                                matches_tier = True
            
            # CRITICAL: Check occasion compatibility (with fallbacks)
            # This ensures items tagged with "business" or "formal" can be used for "interview"
            if matches_tier and occasion and occasion_fallbacks:
                item_occasions = safe_get_item_attr_func(item, 'occasion', [])
                if isinstance(item_occasions, str):
                    item_occasions = [item_occasions]
                
                item_occasions_lower = [occ.lower() for occ in item_occasions]
                occasion_lower = occasion.lower()
                
                # Check if item matches target occasion OR fallback occasions
                occasion_match = False
                
                # Direct match
                if occasion_lower in item_occasions_lower:
                    occasion_match = True
                # Fallback match
                elif occasion_lower in occasion_fallbacks:
                    fallback_occasions = [fb.lower() for fb in occasion_fallbacks[occasion_lower]]
                    if any(fallback in item_occasions_lower for fallback in fallback_occasions):
                        occasion_match = True
                
                # If occasion checking is enabled but item doesn't match, skip it
                if not occasion_match:
                    logger.debug(f"   ❌ {item_name}: tier match but occasion mismatch (has {item_occasions_lower}, need {occasion_lower} or {occasion_fallbacks.get(occasion_lower, [])})")
                    continue
                else:
                    logger.debug(f"   ✅ {item_name}: tier + occasion match")
            
            if matches_tier:
                print(f"   ✅ ADDED: '{item_name}' (tier: {tier.value})", flush=True)
                sys.stdout.flush()
                logger.info(f"   ✅ ADDED: '{item_name}' (tier: {tier.value})")
                filtered.append(item)
            else:
                print(f"   ❌ REJECTED: '{item_name}' (no tier match)", flush=True)
                sys.stdout.flush()
                logger.info(f"   ❌ REJECTED: '{item_name}' (no tier match)")
        
        print(f"\n{'='*80}", flush=True)
        print(f"📊 TIER FILTER RESULT:", flush=True)
        print(f"   Total items: {len(wardrobe)}", flush=True)
        print(f"   Blocked: {blocked_count}", flush=True)
        print(f"   Passed: {len(filtered)}", flush=True)
        print(f"{'='*80}\n", flush=True)
        sys.stdout.flush()
        logger.info(f"📊 TIER FILTER RESULT: {len(filtered)}/{len(wardrobe)} items passed, {blocked_count} blocked")
        return filtered
    
    def get_tier_description(self, tier: FormalityTier) -> str:
        """Get human-readable description of tier"""
        descriptions = {
            FormalityTier.TIER_1_STRICT_FORMAL: "Strict Formal (suits, blazers, dress shoes)",
            FormalityTier.TIER_2_SMART_CASUAL: "Smart Casual (button-ups, chinos, loafers)",
            FormalityTier.TIER_3_CREATIVE_CASUAL: "Creative Casual (stylish but relaxed)",
            FormalityTier.TIER_4_RELAXED: "Relaxed (clean jeans, sneakers)",
            FormalityTier.TIER_5_ATHLETIC: "Athletic (gym wear)",
        }
        return descriptions.get(tier, "Unknown tier")

