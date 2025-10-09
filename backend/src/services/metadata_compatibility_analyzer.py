"""
Metadata Compatibility Analyzer
================================

Unified analyzer for all metadata-based compatibility checks.
Handles multiple compatibility dimensions using rich AI-analyzed metadata.

Compatibility Dimensions:
1. Layer Compatibility (30%) - Sleeve lengths, layer hierarchy
2. Pattern/Texture Mixing (20%) - Pattern overload, texture clashes
3. Fit/Silhouette Balance (20%) - Proportion balance
4. Formality Consistency (15%) - Formality level matching
5. Color Harmony (15%) - AI-analyzed color compatibility

Philosophy:
- Critical conflicts: 0.05 score (effectively blocked)
- Minor issues: Small penalties (-0.10 to -0.20)
- Good matches: Small bonuses (+0.10 to +0.20)
"""

import logging
from typing import Dict, List, Any, Optional
from ..custom_types.wardrobe import ClothingItem

logger = logging.getLogger(__name__)


def safe_get(obj, key, default=None):
    """Safely get attribute from object or dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class MetadataCompatibilityAnalyzer:
    """
    Unified analyzer for metadata-based compatibility checks.
    
    Replaces individual analyzers for layer, pattern, fit, formality, and color
    with a single unified system that scores all metadata-driven compatibility.
    """
    
    def __init__(self):
        # Import shared utilities
        from .outfit_selection_service import OutfitSelectionService
        self.layer_service = OutfitSelectionService()
        
        # Load compatibility rules from existing system
        try:
            from ..utils.pairability import FIT_COMPATIBILITY, SILHOUETTE_COMPATIBILITY, TEXTURE_COMPATIBILITY
            self.fit_rules = FIT_COMPATIBILITY
            self.silhouette_rules = SILHOUETTE_COMPATIBILITY
            self.texture_rules = TEXTURE_COMPATIBILITY
        except ImportError:
            logger.warning("⚠️ Pairability rules not found, using fallback")
            self.fit_rules = {
                "slim": ["relaxed", "structured", "slim"],
                "relaxed": ["slim", "oversized", "relaxed"],
                "oversized": ["relaxed", "oversized"],
            }
            self.silhouette_rules = {
                "structured": ["structured", "flowy", "boxy"],
                "flowy": ["structured", "flowy"],
                "boxy": ["structured", "boxy"],
            }
            self.texture_rules = {
                "smooth": ["smooth", "silky"],
                "rough": ["rough", "textured"],
                "sheer": ["smooth", "silky"],
            }
        
        # Formality level hierarchy (1=most casual, 5=most formal)
        self.formality_levels = {
            'Casual': 1,
            'Smart Casual': 2,
            'Business Casual': 3,
            'Semi-Formal': 4,
            'Formal': 5
        }
        
        # Pattern boldness classification (based on fashion theory)
        self.bold_patterns = [
            # Geometric/Graphic
            'graphic', 'geometric', 'checkerboard', 'checkered', 'striped', 'stripes',
            'plaid', 'houndstooth', 'harlequin', 'abstract',
            # Nature-inspired
            'leopard', 'tiger', 'zebra', 'snake', 'animal print',
            'floral', 'large floral', 'paisley', 'batik',
            # Cultural/Artistic
            'ethnic', 'art deco', 'damask', 'bohemian', 'toile',
            # Other notable
            'polka dot', 'polka dots', 'camouflage', 'camo', 'argyle'
        ]
        self.subtle_patterns = [
            'solid', 'textured', 'ribbed', 'cable knit', 'herringbone',
            'pinstripe', 'micro pattern', 'tone-on-tone'
        ]
        
        # Brand aesthetic mapping for style consistency
        self.brand_aesthetics = {
            # Minimalist/Basics
            'minimalist_basics': ['uniqlo', 'muji', 'cos', 'everlane', 'arket'],
            # Casual/Preppy
            'casual_preppy': ['abercrombie & fitch', 'abercrombie', 'hollister', 'j.crew', 'brooks brothers', 'vineyard vines'],
            # Modern/Minimalist
            'modern_minimalist': ['zara', 'h&m', 'mango', 'massimo dutti', 'reiss'],
            # Athletic/Sportswear
            'athletic': ['nike', 'adidas', 'puma', 'under armour', 'lululemon', 'gymshark', 'reebok'],
            # Streetwear
            'streetwear': ['supreme', 'off-white', 'stussy', 'bape', 'palace', 'kith'],
            # Luxury/Designer
            'luxury': ['gucci', 'prada', 'versace', 'dior', 'fendi', 'balenciaga'],
            # Contemporary/Designer
            'contemporary': ['acne studios', 'apc', 'our legacy', 'lemaire', 'maison margiela'],
            # Workwear/Heritage
            'workwear': ['carhartt', 'dickies', 'levis', 'wrangler', 'filson'],
            # Outdoor/Technical
            'outdoor': ['patagonia', 'north face', 'arc\'teryx', 'columbia', 'rei'],
            # Fast Fashion
            'fast_fashion': ['forever 21', 'fashion nova', 'shein', 'boohoo'],
            # Streetwear Luxury
            'streetwear_luxury': ['fear of god', 'yeezy', 'rick owens', 'rhude'],
            # Classic/Heritage
            'classic': ['ralph lauren', 'tommy hilfiger', 'hugo boss', 'calvin klein', 'lacoste']
        }
        
        # Brand aesthetic compatibility (which aesthetics mix well)
        self.aesthetic_compatibility = {
            'minimalist_basics': ['modern_minimalist', 'contemporary', 'casual_preppy'],
            'casual_preppy': ['minimalist_basics', 'classic'],
            'modern_minimalist': ['minimalist_basics', 'contemporary'],
            'athletic': ['streetwear', 'casual_preppy'],
            'streetwear': ['athletic', 'streetwear_luxury'],
            'luxury': ['contemporary', 'classic'],
            'contemporary': ['luxury', 'modern_minimalist', 'minimalist_basics'],
            'workwear': ['casual_preppy', 'streetwear'],
            'outdoor': ['athletic', 'workwear'],
            'streetwear_luxury': ['streetwear', 'luxury'],
            'classic': ['casual_preppy', 'luxury']
        }
    
    async def analyze_compatibility_scores(self, context, item_scores: Dict[str, Dict]) -> None:
        """
        Main entry point for unified metadata compatibility scoring.
        
        Args:
            context: GenerationContext with occasion, weather, base_item, etc.
            item_scores: Dict of item_id -> score_data (modified in place)
        """
        logger.info(f"🎨 METADATA COMPATIBILITY ANALYZER: Scoring {len(item_scores)} items across 6 dimensions (layer, pattern, fit, formality, color, brand)")
        
        # Collect all items for outfit-level checks
        all_items = [scores['item'] for scores in item_scores.values()]
        
        # Track critical conflicts for logging
        critical_conflicts = {
            'layer': [],
            'pattern': [],
            'fit': [],
            'formality': [],
            'color': []
        }
        
        for item_id, scores in item_scores.items():
            item = scores['item']
            
            # ═══════════════════════════════════════════════════════════
            # Score each compatibility dimension
            # ═══════════════════════════════════════════════════════════
            
            layer_score = await self._score_layer_compatibility(item, context)
            pattern_score = await self._score_pattern_texture(item, all_items)
            fit_score = await self._score_fit_balance(item, all_items)
            formality_score = await self._score_formality_consistency(item, all_items, context)
            color_score = await self._score_color_harmony(item, all_items)
            brand_score = await self._score_brand_consistency(item, all_items)
            
            # Track critical conflicts
            if layer_score < 0.1:
                critical_conflicts['layer'].append(self._safe_get_item_name(item))
            if pattern_score < 0.1:
                critical_conflicts['pattern'].append(self._safe_get_item_name(item))
            if fit_score < 0.15:
                critical_conflicts['fit'].append(self._safe_get_item_name(item))
            if formality_score < 0.2:
                critical_conflicts['formality'].append(self._safe_get_item_name(item))
            
            # ═══════════════════════════════════════════════════════════
            # Weighted composite of compatibility dimensions (6 sub-dimensions)
            # ═══════════════════════════════════════════════════════════
            
            compatibility_score = (
                layer_score * 0.28 +       # Most critical (hard blocks)
                pattern_score * 0.18 +     # Very visible conflicts
                fit_score * 0.18 +         # Important for aesthetics
                formality_score * 0.14 +   # Context-dependent
                color_score * 0.14 +       # AI pre-analyzed
                brand_score * 0.08         # Style consistency polish
            )
            
            # Store final score
            scores['compatibility_score'] = max(0.0, min(1.0, compatibility_score))
            
            # Store breakdown for debugging
            scores['_compatibility_breakdown'] = {
                'layer': layer_score,
                'pattern': pattern_score,
                'fit': fit_score,
                'formality': formality_score,
                'color': color_score,
                'brand': brand_score
            }
        
        logger.info(f"🎨 METADATA COMPATIBILITY ANALYZER: Completed scoring")
        
        # Log critical conflicts
        for dimension, items in critical_conflicts.items():
            if items:
                logger.warning(f"   ⚠️ {dimension.upper()}: {len(items)} items with critical conflicts")
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 1: Layer Compatibility (30% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_layer_compatibility(self, item: Any, context: Any) -> float:
        """
        Score layer compatibility using wearLayer and sleeveLength metadata.
        
        Critical: Short-sleeve outer over long-sleeve inner (0.05)
        Minor: Too many layers for temperature (-0.15)
        Bonus: Compatible with base item (+0.15)
        """
        layer_score = 1.0  # Base score (neutral)
        
        # Get item layer metadata
        item_layer = self.layer_service._get_item_layer(item)
        item_sleeve = self.layer_service._get_sleeve_length(item)
        
        # Get context data
        temp = safe_get(context, 'weather', {})
        if hasattr(temp, 'temperature'):
            temp = temp.temperature
        elif isinstance(temp, dict):
            temp = temp.get('temperature', 70.0)
        else:
            temp = 70.0
        
        base_item = safe_get(context, 'base_item', None)
        
        # ═══════════════════════════════════════════════════════════
        # CRITICAL CHECK: Sleeve Compatibility with Base Item
        # ═══════════════════════════════════════════════════════════
        if base_item:
            base_layer = self.layer_service._get_item_layer(base_item)
            base_sleeve = self.layer_service._get_sleeve_length(base_item)
            
            is_compatible = self._check_sleeve_compatibility(
                item_layer, item_sleeve,
                base_layer, base_sleeve
            )
            
            if not is_compatible:
                # CRITICAL CONFLICT: Heavy penalty (hard block via scoring)
                layer_score = 0.05
                logger.debug(f"   ❌ LAYER CRITICAL: {self._safe_get_item_name(item)} ({item_layer}, {item_sleeve}) conflicts with base ({base_layer}, {base_sleeve})")
            else:
                # Compatible: small bonus
                layer_score += 0.15
                logger.debug(f"   ✅ LAYER: {self._safe_get_item_name(item)} compatible with base")
        
        # ═══════════════════════════════════════════════════════════
        # MINOR CHECK: Temperature Appropriateness for Layer
        # ═══════════════════════════════════════════════════════════
        if layer_score > 0.05:  # Only if not critically blocked
            if temp < 50:  # Cold weather
                if item_layer == 'Outer':
                    layer_score += 0.20
                elif item_layer == 'Inner':
                    layer_score += 0.05
            elif temp > 75:  # Hot weather
                if item_layer in ['Outer', 'Mid']:
                    layer_score -= 0.15
                elif item_layer == 'Inner':
                    layer_score += 0.10
            else:  # Mild weather (50-75°F)
                if item_layer == 'Outer':
                    layer_score += 0.10
        
        return max(0.0, min(1.0, layer_score))
    
    def _check_sleeve_compatibility(
        self,
        item_layer: str, item_sleeve: str,
        base_layer: str, base_sleeve: str
    ) -> bool:
        """
        Check if sleeve lengths are compatible for layering.
        
        Checks BOTH directions:
        - If item would go OVER base (item is outer layer)
        - If base would go OVER item (base is outer layer)
        
        Rule: Outer sleeves must be >= Inner sleeves
        """
        # Only check layerable tops
        layerable_layers = ['Inner', 'Mid', 'Outer']
        if item_layer not in layerable_layers or base_layer not in layerable_layers:
            return True  # Not layerable tops, assume compatible
        
        layer_hierarchy = ['Base', 'Inner', 'Mid', 'Outer']
        try:
            item_pos = layer_hierarchy.index(item_layer) if item_layer in layer_hierarchy else 0
            base_pos = layer_hierarchy.index(base_layer) if base_layer in layer_hierarchy else 0
        except ValueError:
            return True
        
        sleeve_hierarchy = {
            'Sleeveless': 0,
            'None': 0,
            'Short': 1,
            '3/4': 2,
            'Long': 3,
            'Unknown': 1
        }
        
        item_sleeve_val = sleeve_hierarchy.get(item_sleeve, 1)
        base_sleeve_val = sleeve_hierarchy.get(base_sleeve, 1)
        
        # Check Direction 1: Would item go OVER base?
        if item_pos > base_pos:
            # Item is outer layer, base is inner layer
            # Item's sleeves must be >= base's sleeves
            return item_sleeve_val >= base_sleeve_val
        
        # Check Direction 2: Would base go OVER item?
        elif base_pos > item_pos:
            # Base is outer layer, item is inner layer  
            # Base's sleeves must be >= item's sleeves
            # Example: Base=Outer/Short, Item=Mid/Long → Short(1) >= Long(3)? NO → Conflict!
            return base_sleeve_val >= item_sleeve_val
        
        # Same layer level → No layering conflict
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 2: Pattern/Texture Mixing (20% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_pattern_texture(self, item: Any, all_items: List[Any]) -> float:
        """
        Score pattern and texture mixing.
        
        Critical: 3+ bold patterns in outfit (0.05)
        Minor: Mixed incompatible textures (-0.10)
        Bonus: Good texture pairing (+0.10)
        """
        pattern_score = 1.0
        
        # Get item's pattern and texture
        item_pattern = self._get_pattern(item)
        item_texture = self._get_texture(item)
        
        # Count bold patterns in outfit (including this item)
        bold_pattern_count = sum(
            1 for other in all_items 
            if self._get_pattern(other) in self.bold_patterns
        )
        
        # ═══════════════════════════════════════════════════════════
        # CRITICAL CHECK: Pattern Overload
        # ═══════════════════════════════════════════════════════════
        if bold_pattern_count >= 3:
            # Too many bold patterns = visual chaos
            if item_pattern in self.bold_patterns:
                pattern_score = 0.05  # CRITICAL: This item contributes to overload
                logger.debug(f"   ❌ PATTERN CRITICAL: {self._safe_get_item_name(item)} ({item_pattern}) - pattern overload ({bold_pattern_count} bold patterns)")
        elif bold_pattern_count == 2:
            # Two bold patterns is acceptable, slight penalty for third
            if item_pattern in self.bold_patterns:
                pattern_score -= 0.10
        elif bold_pattern_count == 1:
            # One bold pattern is good balance
            if item_pattern in self.bold_patterns:
                pattern_score += 0.10  # Bonus for single statement piece
        
        # ═══════════════════════════════════════════════════════════
        # MINOR CHECK: Texture Compatibility
        # ═══════════════════════════════════════════════════════════
        if item_texture and pattern_score > 0.05:
            compatible_count = 0
            incompatible_count = 0
            
            for other in all_items:
                if other == item:
                    continue
                
                other_texture = self._get_texture(other)
                if other_texture:
                    # Check compatibility using rules
                    compatible_textures = self.texture_rules.get(item_texture, [])
                    if other_texture in compatible_textures:
                        compatible_count += 1
                    else:
                        incompatible_count += 1
            
            # Penalty for incompatible textures
            if incompatible_count > 0:
                pattern_score -= (0.05 * incompatible_count)
                logger.debug(f"   ⚠️ TEXTURE: {self._safe_get_item_name(item)} has {incompatible_count} incompatible textures")
            elif compatible_count > 0:
                pattern_score += 0.05  # Small bonus for compatible textures
        
        return max(0.0, min(1.0, pattern_score))
    
    def _get_pattern(self, item: Any) -> str:
        """Extract pattern from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'pattern'):
                    return (visual_attrs.pattern or '').lower()
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    return (visual_attrs.get('pattern', '') or '').lower()
        return 'solid'  # Default to solid if unknown
    
    def _get_texture(self, item: Any) -> str:
        """Extract texture from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'textureStyle'):
                    return (visual_attrs.textureStyle or '').lower()
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    return (visual_attrs.get('textureStyle', '') or '').lower()
        return ''
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 3: Fit/Silhouette Balance (20% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_fit_balance(self, item: Any, all_items: List[Any]) -> float:
        """
        Score fit and silhouette balance.
        
        Philosophy:
        - REWARD balanced proportions (loose+fitted) with +0.20 bonus
        - ALLOW intentional monochrome looks (all-loose/all-fitted) with -0.15 minor penalty
        - RECOGNIZE quality indicators that make monochrome work
        - Never critically block fit combinations (artistic choice)
        """
        fit_score = 1.0  # Neutral baseline
        
        # Get item's fit and silhouette
        item_fit = self._get_fit(item)
        item_type = self._get_item_type(item).lower()
        
        # Categorize items as top or bottom
        is_top = any(t in item_type for t in ['shirt', 't-shirt', 'sweater', 'blouse', 'jacket', 'hoodie'])
        is_bottom = any(t in item_type for t in ['pants', 'jeans', 'shorts', 'skirt'])
        
        if not (is_top or is_bottom):
            return 1.0  # Not a top or bottom, neutral score
        
        # Count fit types in outfit (only tops and bottoms)
        tops_bottoms = [i for i in all_items if self._is_top_or_bottom(i)]
        loose_count = sum(1 for other in tops_bottoms if self._get_fit(other) in ['loose', 'relaxed', 'oversized'])
        fitted_count = sum(1 for other in tops_bottoms if self._get_fit(other) in ['fitted', 'slim', 'skinny'])
        total_tops_bottoms = len(tops_bottoms)
        
        # ═══════════════════════════════════════════════════════════
        # PRIMARY: REWARD Balanced Proportions
        # ═══════════════════════════════════════════════════════════
        if self._has_balanced_proportions(item, all_items, is_top, is_bottom):
            fit_score += 0.20  # BONUS for classic balanced proportions
            logger.debug(f"   ✅ FIT BONUS: {self._safe_get_item_name(item)} - balanced proportions (loose+fitted)")
            return max(0.0, min(1.0, fit_score))
        
        # ═══════════════════════════════════════════════════════════
        # SECONDARY: ALLOW Intentional Monochrome Looks
        # ═══════════════════════════════════════════════════════════
        if total_tops_bottoms >= 3:
            # Check for all-loose or all-fitted (intentional looks)
            if loose_count >= 3 and item_fit in ['loose', 'relaxed', 'oversized']:
                # All-loose: Streetwear/comfort aesthetic
                fit_score -= 0.15  # MINOR penalty (not critical)
                logger.debug(f"   ⚠️ FIT: {self._safe_get_item_name(item)} - intentional all-loose aesthetic")
                
                # Check for quality indicators that make it work
                if self._has_quality_indicators(all_items):
                    fit_score += 0.10  # Reduce penalty
                    logger.debug(f"   ✅ FIT: Quality indicators present, monochrome accepted")
                
            elif fitted_count >= 3 and item_fit in ['fitted', 'slim', 'skinny']:
                # All-fitted: Sleek/modern aesthetic
                fit_score -= 0.15  # MINOR penalty (not critical)
                logger.debug(f"   ⚠️ FIT: {self._safe_get_item_name(item)} - intentional all-fitted aesthetic")
                
                # Check for quality indicators
                if self._has_quality_indicators(all_items):
                    fit_score += 0.10  # Reduce penalty
                    logger.debug(f"   ✅ FIT: Quality indicators present, monochrome accepted")
        
        elif total_tops_bottoms == 2:
            # Two-piece outfit can also be valid monochrome
            if loose_count == 2 and item_fit in ['loose', 'relaxed', 'oversized']:
                fit_score -= 0.10  # Smaller penalty for 2-piece
                logger.debug(f"   ⚠️ FIT: Two-piece all-loose look")
                
                if self._has_quality_indicators(all_items):
                    fit_score += 0.08
            
            elif fitted_count == 2 and item_fit in ['fitted', 'slim', 'skinny']:
                fit_score -= 0.10
                logger.debug(f"   ⚠️ FIT: Two-piece all-fitted look")
                
                if self._has_quality_indicators(all_items):
                    fit_score += 0.08
        
        return max(0.0, min(1.0, fit_score))
    
    def _is_top_or_bottom(self, item: Any) -> bool:
        """Check if item is a top or bottom (for fit counting)."""
        item_type = self._get_item_type(item).lower()
        return (
            any(t in item_type for t in ['shirt', 't-shirt', 'sweater', 'blouse', 'jacket', 'hoodie']) or
            any(t in item_type for t in ['pants', 'jeans', 'shorts', 'skirt'])
        )
    
    def _has_balanced_proportions(self, item: Any, all_items: List[Any], is_top: bool, is_bottom: bool) -> bool:
        """Check if item creates balanced proportions with outfit."""
        item_fit = self._get_fit(item)
        
        # Check compatibility with tops/bottoms
        for other in all_items:
            if other == item:
                continue
            
            other_fit = self._get_fit(other)
            other_type = self._get_item_type(other).lower()
            other_is_top = any(t in other_type for t in ['shirt', 't-shirt', 'sweater', 'blouse', 'jacket'])
            other_is_bottom = any(t in other_type for t in ['pants', 'jeans', 'shorts', 'skirt'])
            
            # Classic balance: Loose top + fitted bottom OR Fitted top + loose bottom
            if is_top and other_is_bottom:
                compatible_fits = self.fit_rules.get(item_fit, [])
                if other_fit in compatible_fits:
                    return True
            elif is_bottom and other_is_top:
                compatible_fits = self.fit_rules.get(item_fit, [])
                if other_fit in compatible_fits:
                    return True
        
        return False
    
    def _has_quality_indicators(self, all_items: List[Any]) -> bool:
        """
        Check for quality indicators that make monochrome fits work.
        
        Indicators:
        - Premium brands
        - High-quality materials
        - Strategic accessories
        - Designer pieces
        """
        quality_score = 0
        
        for item in all_items:
            # Check for premium brands
            brand = self._get_brand(item).lower()
            premium_brands = [
                'fear of god', 'yeezy', 'balenciaga', 'rick owens',  # Oversized aesthetic
                'helmut lang', 'acne studios', 'celine', 'saint laurent',  # Fitted aesthetic
                'comme des garcons', 'yohji yamamoto', 'issey miyake'  # Artistic
            ]
            if any(pb in brand for pb in premium_brands):
                quality_score += 1
                logger.debug(f"   ✨ QUALITY: Premium brand detected ({brand})")
            
            # Check for high-quality materials
            material = self._get_material(item).lower()
            quality_materials = ['cashmere', 'silk', 'wool', 'leather', 'linen', 'merino']
            if any(qm in material for qm in quality_materials):
                quality_score += 0.5
                logger.debug(f"   ✨ QUALITY: Premium material detected ({material})")
            
            # Check for accessories (shows intentional styling)
            item_type = self._get_item_type(item).lower()
            if any(acc in item_type for acc in ['belt', 'scarf', 'hat', 'bag', 'watch']):
                quality_score += 0.5
                logger.debug(f"   ✨ QUALITY: Strategic accessory detected")
        
        # Threshold: 1+ quality indicators means intentional styling
        return quality_score >= 1.0
    
    def _get_brand(self, item: Any) -> str:
        """Extract brand from item."""
        if hasattr(item, 'brand'):
            return item.brand or ''
        elif isinstance(item, dict):
            return item.get('brand', '')
        return ''
    
    def _get_material(self, item: Any) -> str:
        """Extract material from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'material'):
                    return (visual_attrs.material or '').lower()
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    return (visual_attrs.get('material', '') or '').lower()
        return ''
    
    def _get_fit(self, item: Any) -> str:
        """Extract fit from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'fit'):
                    return (visual_attrs.fit or '').lower()
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    return (visual_attrs.get('fit', '') or '').lower()
        return 'regular'  # Default
    
    def _get_silhouette(self, item: Any) -> str:
        """Extract silhouette from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'silhouette'):
                    return (visual_attrs.silhouette or '').lower()
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    return (visual_attrs.get('silhouette', '') or '').lower()
        return ''
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 4: Formality Consistency (15% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_formality_consistency(self, item: Any, all_items: List[Any], context: Any) -> float:
        """
        Score formality consistency using formalLevel metadata.
        
        Critical: >2 level gap (Formal + Casual) (0.15)
        Minor: 1-2 level gap (-0.10)
        Bonus: Matches occasion formality (+0.10)
        """
        formality_score = 1.0
        
        # Get item's formality level
        item_formality = self._get_formality_level(item)
        item_formality_value = self.formality_levels.get(item_formality, 2)  # Default to Smart Casual
        
        # ═══════════════════════════════════════════════════════════
        # CRITICAL CHECK: Large Formality Gaps
        # ═══════════════════════════════════════════════════════════
        for other in all_items:
            if other == item:
                continue
            
            other_formality = self._get_formality_level(other)
            other_formality_value = self.formality_levels.get(other_formality, 2)
            
            gap = abs(item_formality_value - other_formality_value)
            
            if gap > 2:
                # CRITICAL: More than 2 levels apart (e.g., Formal + Casual)
                formality_score = 0.15
                logger.debug(f"   ❌ FORMALITY CRITICAL: {self._safe_get_item_name(item)} ({item_formality}) vs {self._safe_get_item_name(other)} ({other_formality}) - {gap} level gap")
                break
            elif gap == 2:
                # Minor: 2 levels apart (acceptable but not ideal)
                formality_score -= 0.10
        
        # ═══════════════════════════════════════════════════════════
        # BONUS CHECK: Matches Occasion Formality
        # ═══════════════════════════════════════════════════════════
        if formality_score > 0.2:  # Only if not critically blocked
            occasion = safe_get(context, 'occasion', '').lower()
            
            # Map occasions to expected formality
            occasion_formality = {
                'business': 'Business Casual',
                'formal': 'Formal',
                'interview': 'Formal',
                'wedding': 'Semi-Formal',
                'date': 'Smart Casual',
                'party': 'Smart Casual',
                'casual': 'Casual',
                'weekend': 'Casual',
                'athletic': 'Casual'
            }
            
            expected_formality = occasion_formality.get(occasion)
            if expected_formality and item_formality == expected_formality:
                formality_score += 0.10
                logger.debug(f"   ✅ FORMALITY: {self._safe_get_item_name(item)} ({item_formality}) matches {occasion} occasion")
        
        return max(0.0, min(1.0, formality_score))
    
    def _get_formality_level(self, item: Any) -> str:
        """Extract formality level from metadata."""
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'formalLevel'):
                    return visual_attrs.formalLevel or 'Smart Casual'
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    level = visual_attrs.get('formalLevel', 'Smart Casual')
                    return level if level else 'Smart Casual'
        
        # Fallback: infer from type (legacy support)
        return self._infer_formality_from_type(item)
    
    def _infer_formality_from_type(self, item: Any) -> str:
        """Infer formality from item type (fallback)."""
        item_name = self._safe_get_item_name(item).lower()
        item_type = self._get_item_type(item).lower()
        
        # Formal indicators
        if any(word in item_name or word in item_type for word in ['suit', 'blazer', 'dress shirt', 'dress pants', 'oxford', 'loafer', 'heels']):
            return 'Formal'
        
        # Business casual indicators
        if any(word in item_name or word in item_type for word in ['polo', 'chinos', 'cardigan', 'blouse']):
            return 'Business Casual'
        
        # Casual indicators
        if any(word in item_name or word in item_type for word in ['t-shirt', 'jeans', 'sneakers', 'hoodie']):
            return 'Casual'
        
        return 'Smart Casual'  # Default
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 5: Color Harmony (15% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_color_harmony(self, item: Any, all_items: List[Any]) -> float:
        """
        Score color harmony using AI-analyzed dominantColors and matchingColors.
        
        Bonuses: Item's color in another's matchingColors (+0.05 each, cap +0.15)
        Penalties: Clashing color combinations (-0.20 per clash)
        Neutral: No color data or unknown combinations (1.0)
        """
        color_score = 1.0
        
        # Get item's dominant and matching colors
        item_dominant = self._get_dominant_colors(item)
        item_matching = self._get_matching_colors(item)
        
        if not item_dominant:
            return 1.0  # No color data, neutral score
        
        # Color theory: Complementary colors that clash when used together
        # (Different from complementary colors that work well together)
        color_clashes = {
            'red': ['green', 'pink', 'orange'],  # Too warm together
            'green': ['red', 'pink'],
            'pink': ['red', 'green', 'orange'],
            'orange': ['red', 'pink', 'purple'],
            'purple': ['orange', 'yellow'],
            'yellow': ['purple'],
            'blue': ['brown'],  # Can clash in certain combinations
            'brown': ['blue', 'black']  # Brown + black is debated
        }
        
        # ═══════════════════════════════════════════════════════════
        # PENALTY CHECK: Clashing Color Combinations
        # ═══════════════════════════════════════════════════════════
        clash_penalty = 0.0
        
        for other in all_items:
            if other == item:
                continue
            
            other_dominant = self._get_dominant_colors(other)
            
            # Check for clashing combinations
            for item_color in item_dominant:
                item_color_lower = item_color.lower()
                for other_color in other_dominant:
                    other_color_lower = other_color.lower()
                    
                    # Check if these colors clash
                    if item_color_lower in color_clashes:
                        clash_list = color_clashes[item_color_lower]
                        if any(clash in other_color_lower for clash in clash_list):
                            clash_penalty += 0.20  # Penalty for clashing colors
                            logger.debug(f"   ❌ COLOR CLASH: {self._safe_get_item_name(item)} ({item_color}) clashes with ({other_color})")
        
        color_score -= clash_penalty
        
        # ═══════════════════════════════════════════════════════════
        # BONUS CHECK: AI-Analyzed Color Matches
        # ═══════════════════════════════════════════════════════════
        harmony_bonus = 0.0
        
        for other in all_items:
            if other == item:
                continue
            
            other_dominant = self._get_dominant_colors(other)
            
            # Check if other's dominant colors are in this item's matching colors
            for other_color in other_dominant:
                if other_color.lower() in [m.lower() for m in item_matching]:
                    harmony_bonus += 0.05  # Bonus for each AI-analyzed match
                    logger.debug(f"   ✅ COLOR MATCH: {self._safe_get_item_name(item)} - {other_color} in AI palette")
        
        color_score += min(harmony_bonus, 0.15)  # Cap bonus at +0.15
        
        return max(0.0, min(1.0, color_score))
    
    def _get_dominant_colors(self, item: Any) -> List[str]:
        """Extract dominant colors from metadata."""
        colors = []
        
        # Try dominantColors field
        if hasattr(item, 'dominantColors') and item.dominantColors:
            for color in item.dominantColors:
                if isinstance(color, dict):
                    name = color.get('name', '')
                    if name:
                        colors.append(name)
                elif hasattr(color, 'name'):
                    if color.name:
                        colors.append(color.name)
        
        # Fallback to color field
        if not colors and hasattr(item, 'color'):
            if isinstance(item.color, str) and item.color:
                colors.append(item.color)
        
        return colors
    
    def _get_matching_colors(self, item: Any) -> List[str]:
        """Extract matching colors from metadata."""
        colors = []
        
        if hasattr(item, 'matchingColors') and item.matchingColors:
            for color in item.matchingColors:
                if isinstance(color, dict):
                    name = color.get('name', '')
                    if name:
                        colors.append(name)
                elif hasattr(color, 'name'):
                    if color.name:
                        colors.append(color.name)
        
        return colors
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIMENSION 6: Brand Style Consistency (8% weight)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _score_brand_consistency(self, item: Any, all_items: List[Any]) -> float:
        """
        Score brand style consistency.
        
        Bonuses:
        - All items from same aesthetic group (+0.15)
        - Items from compatible aesthetics (+0.10)
        - Premium brand quality (+0.05)
        
        Neutral: No brand data or mixed brands (1.0)
        """
        brand_score = 1.0
        
        # Get item's brand
        item_brand = self._get_brand(item).lower()
        
        if not item_brand:
            return 1.0  # No brand data, neutral
        
        # Determine item's aesthetic group
        item_aesthetic = self._get_brand_aesthetic(item_brand)
        
        if not item_aesthetic:
            return 1.0  # Unknown brand, neutral
        
        # ═══════════════════════════════════════════════════════════
        # BONUS CHECK: Aesthetic Cohesion
        # ═══════════════════════════════════════════════════════════
        same_aesthetic_count = 0
        compatible_aesthetic_count = 0
        incompatible_count = 0
        
        for other in all_items:
            if other == item:
                continue
            
            other_brand = self._get_brand(other).lower()
            if not other_brand:
                continue  # Skip items without brands
            
            other_aesthetic = self._get_brand_aesthetic(other_brand)
            if not other_aesthetic:
                continue
            
            # Check aesthetic compatibility
            if other_aesthetic == item_aesthetic:
                same_aesthetic_count += 1  # Same aesthetic group
            elif item_aesthetic in self.aesthetic_compatibility:
                compatible_aesthetics = self.aesthetic_compatibility[item_aesthetic]
                if other_aesthetic in compatible_aesthetics:
                    compatible_aesthetic_count += 1  # Compatible aesthetics
                else:
                    incompatible_count += 1  # Incompatible aesthetics
        
        # Calculate aesthetic cohesion bonus
        if same_aesthetic_count >= 2:
            # All from same aesthetic (e.g., all Uniqlo, all Nike)
            brand_score += 0.15
            logger.debug(f"   ✅ BRAND: {self._safe_get_item_name(item)} - cohesive aesthetic ({item_aesthetic})")
        elif same_aesthetic_count == 1:
            brand_score += 0.10  # Two items from same aesthetic
        elif compatible_aesthetic_count > 0 and incompatible_count == 0:
            # All brands are compatible (e.g., Uniqlo + Zara)
            brand_score += 0.10
            logger.debug(f"   ✅ BRAND: {self._safe_get_item_name(item)} - compatible aesthetics")
        elif incompatible_count > 0:
            # Some incompatible brands (e.g., Athletic + Luxury)
            brand_score -= (0.05 * incompatible_count)  # Small penalty per conflict
            logger.debug(f"   ⚠️ BRAND: {self._safe_get_item_name(item)} - {incompatible_count} aesthetic conflicts")
        
        # ═══════════════════════════════════════════════════════════
        # SMALL BONUS: Premium Brand Quality
        # ═══════════════════════════════════════════════════════════
        if item_aesthetic in ['luxury', 'contemporary', 'streetwear_luxury']:
            brand_score += 0.05
            logger.debug(f"   ✨ BRAND: {self._safe_get_item_name(item)} - premium category")
        
        return max(0.0, min(1.0, brand_score))
    
    def _get_brand_aesthetic(self, brand: str) -> Optional[str]:
        """Get the aesthetic category for a brand."""
        brand_lower = brand.lower()
        
        for aesthetic, brands in self.brand_aesthetics.items():
            if any(b in brand_lower for b in brands):
                return aesthetic
        
        return None  # Unknown brand
    
    # ═══════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════
    
    def _safe_get_item_name(self, item: Any) -> str:
        """Safely get item name."""
        if hasattr(item, 'name'):
            return item.name or 'Unknown'
        elif isinstance(item, dict):
            return item.get('name', 'Unknown')
        return 'Unknown'
    
    def _get_item_type(self, item: Any) -> str:
        """Safely get item type."""
        if hasattr(item, 'type'):
            item_type = item.type
            if hasattr(item_type, 'value'):
                return item_type.value
            return str(item_type)
        elif isinstance(item, dict):
            return str(item.get('type', ''))
        return ''

