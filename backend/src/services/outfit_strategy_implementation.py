"""
Outfit Strategy Implementation
==============================

Implements the logic for each outfit composition strategy.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from .outfit_strategy_selector import OutfitStrategy

logger = logging.getLogger(__name__)


class StrategyImplementation:
    """Implements outfit composition strategies"""
    
    @staticmethod
    def apply_strategy(
        strategy: OutfitStrategy,
        sorted_items: List[Tuple[str, Dict]],
        categories_filled: Dict[str, bool],
        target_items: int,
        context: Any,
        base_item_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply the selected strategy to item selection.
        
        Returns:
            Dict with:
            - selection_adjustments: Dict[item_id, score_adjustment]
            - selection_rules: Dict with strategy-specific selection rules
            - strategy_metadata: Info about what strategy is doing
        """
        
        logger.info(f"🎨 APPLYING STRATEGY: {strategy.value.upper().replace('_', ' ')}")
        
        if strategy == OutfitStrategy.TRADITIONAL:
            return StrategyImplementation._traditional_strategy(sorted_items, target_items)
        
        elif strategy == OutfitStrategy.HIGH_LOW:
            return StrategyImplementation._high_low_strategy(sorted_items, target_items, context, base_item_id)
        
        elif strategy == OutfitStrategy.LAYERING_CONTRAST:
            return StrategyImplementation._layering_contrast_strategy(sorted_items, target_items, context)
        
        elif strategy == OutfitStrategy.STATEMENT_PIECE:
            return StrategyImplementation._statement_piece_strategy(sorted_items, target_items, base_item_id)
        
        elif strategy == OutfitStrategy.GRADUATED:
            return StrategyImplementation._graduated_strategy(sorted_items, target_items, context)
        
        elif strategy == OutfitStrategy.MONOCHROME:
            return StrategyImplementation._monochrome_strategy(sorted_items, target_items, context)
        
        elif strategy == OutfitStrategy.COLOR_POP:
            return StrategyImplementation._color_pop_strategy(sorted_items, target_items, context, base_item_id)
        
        elif strategy == OutfitStrategy.TEXTURE_PLAY:
            return StrategyImplementation._texture_play_strategy(sorted_items, target_items)
        
        elif strategy == OutfitStrategy.PROPORTIONS:
            return StrategyImplementation._proportions_strategy(sorted_items, target_items, context)
        
        elif strategy == OutfitStrategy.ERA_BLEND:
            return StrategyImplementation._era_blend_strategy(sorted_items, target_items)
        
        else:
            # Fallback to traditional
            logger.warning(f"⚠️ Unknown strategy, falling back to traditional")
            return StrategyImplementation._traditional_strategy(sorted_items, target_items)
    
    # ═══════════════════════════════════════════════════════════════════════
    # STRATEGY IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def _traditional_strategy(sorted_items, target_items):
        """Traditional: Pick highest scored items"""
        return {
            'selection_adjustments': {},  # No adjustments, use natural scores
            'selection_rules': {
                'method': 'top_scores',
                'description': 'Select highest scored items naturally'
            },
            'strategy_metadata': {
                'name': 'Traditional Match',
                'description': 'All items match your target style and formality'
            }
        }
    
    @staticmethod
    def _high_low_strategy(sorted_items, target_items, context, base_item_id):
        """High-Low: Boost items that create formality contrast"""
        adjustments = {}
        
        # Find items with formality contrast
        # Boost formal items AND casual items, penalize middle-formality items
        for item_id, score_data in sorted_items:
            if item_id == base_item_id:
                continue  # Skip base item
            
            item = score_data['item']
            formality = StrategyImplementation._get_item_formality(item)
            
            if formality in [0, 4]:  # Very casual or very formal
                adjustments[item_id] = 0.3  # Boost extremes
            elif formality in [1, 3]:  # Somewhat formal/casual
                adjustments[item_id] = 0.1  # Slight boost
            else:  # Middle formality
                adjustments[item_id] = -0.1  # Slight penalty
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'contrast_boost',
                'boost_extremes': True
            },
            'strategy_metadata': {
                'name': 'High-Low Mix',
                'description': 'Mixing dressy and casual pieces for modern sophistication'
            }
        }
    
    @staticmethod
    def _layering_contrast_strategy(sorted_items, target_items, context):
        """Layering Contrast: Ensure different formality in layers"""
        adjustments = {}
        
        # Boost items that would create good layering contrast
        # Base layer (casual) + Mid layer (moderate) + Outer layer (formal)
        for item_id, score_data in sorted_items:
            item = score_data['item']
            layer = StrategyImplementation._get_item_layer(item)
            formality = StrategyImplementation._get_item_formality(item)
            
            # Prefer casual base layers, moderate mid layers, formal outer layers
            if layer == 'base' and formality <= 1:
                adjustments[item_id] = 0.2
            elif layer == 'mid' and formality == 2:
                adjustments[item_id] = 0.2
            elif layer == 'outerwear' and formality >= 2:
                adjustments[item_id] = 0.2
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'layer_contrast',
                'target_pattern': 'casual_base_formal_outer'
            },
            'strategy_metadata': {
                'name': 'Layering Contrast',
                'description': 'Contrasting formality levels through layering'
            }
        }
    
    @staticmethod
    def _statement_piece_strategy(sorted_items, target_items, base_item_id):
        """Statement Piece: One bold item, rest neutral"""
        adjustments = {}
        
        # Find the highest-scored non-base item as statement piece
        statement_item_id = None
        max_score = -999
        
        for item_id, score_data in sorted_items:
            if item_id == base_item_id:
                continue
            if score_data['composite_score'] > max_score:
                max_score = score_data['composite_score']
                statement_item_id = item_id
        
        # Boost statement piece, penalize other high-scoring items
        for item_id, score_data in sorted_items:
            if item_id == base_item_id:
                continue
            elif item_id == statement_item_id:
                adjustments[item_id] = 0.5  # Huge boost for statement
            elif score_data['composite_score'] > 2.0:  # Other high scorers
                adjustments[item_id] = -0.3  # Penalize to make room for statement
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'statement_piece',
                'statement_item': statement_item_id
            },
            'strategy_metadata': {
                'name': 'Statement Piece',
                'description': 'One standout item with supporting neutral pieces'
            }
        }
    
    @staticmethod
    def _graduated_strategy(sorted_items, target_items, context):
        """Graduated: Smooth formality progression"""
        adjustments = {}
        
        # Boost items that create a formality ladder (0→1→2→3)
        # Categorize items by formality
        by_formality = {0: [], 1: [], 2: [], 3: [], 4: []}
        
        for item_id, score_data in sorted_items:
            item = score_data['item']
            formality = StrategyImplementation._get_item_formality(item)
            by_formality[formality].append(item_id)
        
        # Boost one item from each formality level (if available)
        for formality_level, item_ids in by_formality.items():
            if item_ids and len(item_ids) > 0:
                # Boost first item from this formality level
                adjustments[item_ids[0]] = 0.2
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'graduated',
                'target_progression': True
            },
            'strategy_metadata': {
                'name': 'Graduated Formality',
                'description': 'Smooth formality progression across pieces'
            }
        }
    
    @staticmethod
    def _monochrome_strategy(sorted_items, target_items, context):
        """Monochrome: Prioritize color harmony"""
        adjustments = {}
        
        # Find dominant color in top-scored items
        color_counts = {}
        for item_id, score_data in sorted_items[:10]:  # Check top 10
            item = score_data['item']
            color = StrategyImplementation._get_item_color(item)
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Pick most common color as theme
        theme_color = max(color_counts, key=color_counts.get) if color_counts else None
        
        if theme_color:
            logger.info(f"   🎨 MONOCHROME: Theme color = {theme_color}")
            # Boost items matching theme color
            for item_id, score_data in sorted_items:
                item = score_data['item']
                item_color = StrategyImplementation._get_item_color(item)
                if item_color == theme_color or StrategyImplementation._colors_are_compatible(item_color, theme_color):
                    adjustments[item_id] = 0.3
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'monochrome',
                'theme_color': theme_color
            },
            'strategy_metadata': {
                'name': 'Monochrome Focus',
                'description': f'Cohesive {theme_color} color story' if theme_color else 'Cohesive color story'
            }
        }
    
    @staticmethod
    def _color_pop_strategy(sorted_items, target_items, context, base_item_id):
        """Color Pop: Neutral base + ONE bright accent"""
        adjustments = {}
        
        # Find one bright/bold colored item
        bright_item_id = None
        for item_id, score_data in sorted_items:
            if item_id == base_item_id:
                continue
            item = score_data['item']
            color = StrategyImplementation._get_item_color(item).lower()
            if color in ['red', 'yellow', 'orange', 'bright blue', 'pink', 'purple', 'green']:
                bright_item_id = item_id
                break
        
        if bright_item_id:
            # Boost the pop color item, boost neutral items, penalize other bright items
            for item_id, score_data in sorted_items:
                if item_id == base_item_id:
                    continue
                item = score_data['item']
                color = StrategyImplementation._get_item_color(item).lower()
                
                if item_id == bright_item_id:
                    adjustments[item_id] = 0.5  # Huge boost for THE pop
                elif color in ['black', 'white', 'gray', 'grey', 'navy', 'beige', 'tan', 'brown']:
                    adjustments[item_id] = 0.2  # Boost neutrals
                else:
                    adjustments[item_id] = -0.3  # Penalize other colors
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'color_pop',
                'pop_item': bright_item_id
            },
            'strategy_metadata': {
                'name': 'Color Pop',
                'description': 'Neutral foundation with one vibrant accent piece'
            }
        }
    
    @staticmethod
    def _texture_play_strategy(sorted_items, target_items):
        """Texture Play: Mix smooth + textured + patterned"""
        adjustments = {}
        
        # Categorize items by texture
        textures = {'smooth': [], 'textured': [], 'patterned': []}
        
        for item_id, score_data in sorted_items:
            item = score_data['item']
            texture = StrategyImplementation._get_item_texture(item)
            if texture in textures:
                textures[texture].append(item_id)
        
        # Boost one from each texture category
        for texture_type, item_ids in textures.items():
            if item_ids:
                adjustments[item_ids[0]] = 0.2  # Boost first from each category
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'texture_mix',
                'target_variety': True
            },
            'strategy_metadata': {
                'name': 'Texture Play',
                'description': 'Mixing smooth, textured, and patterned fabrics for visual interest'
            }
        }
    
    @staticmethod
    def _proportions_strategy(sorted_items, target_items, context):
        """Proportions: Balance fitted + loose silhouettes"""
        adjustments = {}
        
        # Categorize by fit
        fits = {'fitted': [], 'loose': [], 'regular': []}
        
        for item_id, score_data in sorted_items:
            item = score_data['item']
            fit = StrategyImplementation._get_item_fit(item)
            if fit in fits:
                fits[fit].append(item_id)
        
        # Apply fashion rule: fitted top + loose bottom OR loose top + fitted bottom
        # Boost items that create this balance
        for item_id, score_data in sorted_items:
            item = score_data['item']
            category = StrategyImplementation._get_item_category(item)
            fit = StrategyImplementation._get_item_fit(item)
            
            # Boost fitted tops
            if category == 'tops' and fit == 'fitted':
                adjustments[item_id] = 0.15
            # Boost loose bottoms (pairs with fitted tops)
            elif category == 'bottoms' and fit == 'loose':
                adjustments[item_id] = 0.15
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'proportions',
                'target_balance': 'fitted_loose'
            },
            'strategy_metadata': {
                'name': 'Proportions Balance',
                'description': 'Balancing fitted and loose silhouettes for flattering proportions'
            }
        }
    
    @staticmethod
    def _era_blend_strategy(sorted_items, target_items):
        """Era Blend: Mix vintage + modern"""
        adjustments = {}
        
        # Boost items that blend eras
        vintage_count = 0
        modern_count = 0
        
        for item_id, score_data in sorted_items:
            item = score_data['item']
            is_vintage = StrategyImplementation._is_vintage_item(item)
            
            if is_vintage and vintage_count < target_items // 2:
                adjustments[item_id] = 0.2
                vintage_count += 1
            elif not is_vintage and modern_count < target_items // 2:
                adjustments[item_id] = 0.1
                modern_count += 1
        
        return {
            'selection_adjustments': adjustments,
            'selection_rules': {
                'method': 'era_blend',
                'target_mix': 'vintage_modern'
            },
            'strategy_metadata': {
                'name': 'Era Blend',
                'description': 'Blending vintage classics with modern pieces'
            }
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def _get_item_formality(item) -> int:
        """Get item formality level (0-4)"""
        # Check metadata
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    if 'formal' in formal_level and 'business' not in formal_level:
                        return 3
                    elif 'business' in formal_level:
                        return 2
                    elif 'casual' in formal_level:
                        return 0
        
        # Fallback to type
        item_type = str(getattr(item, 'type', '')).lower()
        item_name = str(getattr(item, 'name', '')).lower()
        
        if any(kw in item_type or kw in item_name for kw in ['suit', 'blazer', 'dress shirt', 'oxford']):
            return 3
        elif any(kw in item_type or kw in item_name for kw in ['chino', 'polo', 'cardigan']):
            return 2
        elif any(kw in item_type or kw in item_name for kw in ['button', 'sweater', 'boot']):
            return 1
        else:
            return 0
    
    @staticmethod
    def _get_item_layer(item) -> str:
        """Get item layer (base, mid, outerwear)"""
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    wear_layer = (visual_attrs.get('wearLayer') or '').lower()
                    if wear_layer:
                        return wear_layer
        
        # Fallback
        item_type = str(getattr(item, 'type', '')).lower()
        if 'jacket' in item_type or 'coat' in item_type:
            return 'outerwear'
        elif 'sweater' in item_type or 'cardigan' in item_type:
            return 'mid'
        else:
            return 'base'
    
    @staticmethod
    def _get_item_color(item) -> str:
        """Get item color"""
        if hasattr(item, 'color'):
            return str(item.color)
        elif isinstance(item, dict):
            return item.get('color', 'unknown')
        return 'unknown'
    
    @staticmethod
    def _get_item_texture(item) -> str:
        """Get item texture (smooth, textured, patterned)"""
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    pattern = (visual_attrs.get('pattern') or '').lower()
                    texture = (visual_attrs.get('textureStyle') or '').lower()
                    
                    if pattern and pattern not in ['solid', 'none']:
                        return 'patterned'
                    elif 'textured' in texture or 'ribbed' in texture or 'knit' in texture:
                        return 'textured'
                    else:
                        return 'smooth'
        
        # Fallback to name
        name = str(getattr(item, 'name', '')).lower()
        if any(kw in name for kw in ['striped', 'plaid', 'floral', 'print']):
            return 'patterned'
        elif any(kw in name for kw in ['knit', 'cable', 'ribbed', 'textured']):
            return 'textured'
        else:
            return 'smooth'
    
    @staticmethod
    def _get_item_fit(item) -> str:
        """Get item fit (fitted, loose, regular)"""
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    fit = (visual_attrs.get('fit') or '').lower()
                    if fit:
                        return fit
        
        # Fallback
        name = str(getattr(item, 'name', '')).lower()
        if any(kw in name for kw in ['slim', 'fitted', 'tight', 'skinny']):
            return 'fitted'
        elif any(kw in name for kw in ['loose', 'relaxed', 'oversized', 'baggy']):
            return 'loose'
        else:
            return 'regular'
    
    @staticmethod
    def _get_item_category(item) -> str:
        """Get item category"""
        item_type = str(getattr(item, 'type', '')).lower()
        
        if any(kw in item_type for kw in ['shirt', 'top', 'blouse', 'sweater', 'hoodie']):
            return 'tops'
        elif any(kw in item_type for kw in ['pants', 'jeans', 'shorts', 'skirt']):
            return 'bottoms'
        elif any(kw in item_type for kw in ['shoes', 'boot', 'sneaker']):
            return 'shoes'
        elif any(kw in item_type for kw in ['jacket', 'coat', 'blazer']):
            return 'outerwear'
        else:
            return 'other'
    
    @staticmethod
    def _is_vintage_item(item) -> bool:
        """Check if item is vintage/retro"""
        name = str(getattr(item, 'name', '')).lower()
        style = getattr(item, 'style', [])
        if isinstance(style, str):
            style = [style]
        style_lower = [s.lower() for s in style]
        
        return (any(kw in name for kw in ['vintage', 'retro', 'classic']) or
                any(kw in style_lower for kw in ['vintage', 'retro', 'classic', 'old money']))
    
    @staticmethod
    def _colors_are_compatible(color1: str, color2: str) -> bool:
        """Check if two colors work together in monochrome scheme"""
        color1_lower = color1.lower()
        color2_lower = color2.lower()
        
        # Same color family
        if color1_lower == color2_lower:
            return True
        
        # Neutral compatibility
        neutrals = ['black', 'white', 'gray', 'grey', 'navy', 'beige', 'tan', 'brown']
        if color1_lower in neutrals and color2_lower in neutrals:
            return True
        
        # Earth tones
        earth_tones = ['brown', 'tan', 'beige', 'olive', 'khaki']
        if color1_lower in earth_tones and color2_lower in earth_tones:
            return True
        
        return False

