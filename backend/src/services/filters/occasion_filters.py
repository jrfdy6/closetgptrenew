#!/usr/bin/env python3
"""
Occasion-Specific Filters for Outfit Generation
================================================

This module contains hard filters for different occasions (gym, formal, loungewear, etc.).
Each filter blocks inappropriate items for specific occasions.

The filters are organized by occasion type and can be called independently or through
the main dispatcher.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OccasionFilters:
    """
    Occasion-specific hard filters for outfit generation.
    
    Each filter method returns True if the item is ALLOWED, False if BLOCKED.
    """
    
    def __init__(self, safe_get_item_name_func: callable, safe_get_item_attr_func: callable):
        """
        Initialize with helper functions from the main service.
        
        Args:
            safe_get_item_name_func: Function to safely get item name
            safe_get_item_attr_func: Function to safely get item attributes
        """
        self.safe_get_item_name = safe_get_item_name_func
        self.safe_get_item_attr = safe_get_item_attr_func
    
    def apply_hard_filter(self, item: Any, occasion: str, style: str) -> bool:
        """
        Main dispatcher for occasion-specific hard filters.
        
        Args:
            item: Clothing item to filter
            occasion: Occasion name
            style: Style name
        
        Returns:
            True if item is allowed, False if blocked
        """
        occasion_lower = occasion.lower()
        style_lower = (style or '').lower()
        
        # Dispatch to appropriate filter
        if occasion_lower in ['gym', 'athletic', 'workout']:
            return self.filter_gym(item, style_lower)
        elif occasion_lower in ['formal', 'black-tie', 'gala']:
            return self.filter_formal(item, style_lower)
        elif occasion_lower in ['loungewear', 'home', 'sleep', 'relax']:
            return self.filter_loungewear(item, style_lower)
        elif occasion_lower in ['party', 'date', 'night out', 'club', 'dinner']:
            return self.filter_party_date(item, style_lower)
        
        # Style-specific filters
        if style_lower in ['old money', 'urban professional']:
            if not self.filter_old_money_style(item):
                return False
        
        # Basic fallback constraints
        return self._basic_hard_constraints(item, occasion_lower)
    
    # ═══════════════════════════════════════════════════════════════════════
    # GYM / ATHLETIC FILTER
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_gym(self, item: Any, style: str) -> bool:
        """
        Filter for gym/athletic occasions.
        Blocks formal/structured items, allows athletic wear.
        """
        item_name = self.safe_get_item_name(item).lower()
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()
        else:
            item_type = str(raw_type).lower()
        
        # PANTS CHECK: Block formal pants, allow athletic pants
        if item_type in ['pants', 'jeans', 'trousers', 'bottoms'] and 'short' not in item_name:
            # Check metadata first
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    waistband_type = (visual_attrs.get('waistbandType') or '').lower()
                    material = (visual_attrs.get('material') or '').lower()
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    
                    # Waistband check
                    if waistband_type in ['button_zip', 'belt_loops']:
                        logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - formal waistband")
                        return False
                    elif waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
                        logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic waistband")
                        return True
                    
                    # Material check
                    if material in ['denim', 'wool', 'cotton twill', 'linen', 'cashmere', 'silk']:
                        logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - formal material")
                        return False
                    elif material in ['polyester', 'mesh', 'performance', 'synthetic', 'nylon', 'spandex']:
                        logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic material")
                        return True
                    
                    # Formal level check
                    if formal_level in ['formal', 'business', 'dress', 'professional']:
                        logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - formal level")
                        return False
                    elif formal_level in ['athletic', 'sport']:
                        logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic level")
                        return True
            
            # Check occasion tags
            item_occasions = getattr(item, 'occasion', [])
            item_occasions_lower = [occ.lower() for occ in item_occasions] if item_occasions else []
            if item_occasions_lower:
                if any(occ in item_occasions_lower for occ in ['business', 'formal', 'professional', 'work']):
                    logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - formal occasion tag")
                    return False
                elif any(occ in item_occasions_lower for occ in ['athletic', 'gym', 'workout', 'sport', 'running']):
                    logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic occasion tag")
                    return True
            
            # Shorts are usually OK
            if item_type in ['shorts', 'athletic_shorts']:
                return True
            
            # Fallback: Check name for athletic keywords
            athletic_keywords = [
                'jogger', 'joggers', 'sweatpants', 'sweat pants', 'track pants',
                'athletic pants', 'workout pants', 'gym pants', 'training pants',
                'legging', 'leggings', 'yoga pants', 'running pants'
            ]
            
            if any(kw in item_name for kw in athletic_keywords):
                logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic keyword")
                return True
            
            # Block generic/formal pants
            generic_blocks = ['pants', 'pant', 'trouser', 'trousers', 'chino', 'chinos', 'jean', 'jeans', 'slack', 'slacks']
            if any(block in item_name for block in generic_blocks):
                logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - generic/formal pants")
                return False
            
            # Ambiguous - block to be safe
            logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - no explicit athletic indicators")
            return False
        
        # TOPS CHECK: Block collared/formal tops
        if item_type in ['shirt', 'top', 'sweater', 'hoodie', 'jacket', 'outerwear', 'dress_shirt', 't-shirt', 't_shirt', 'polo', 'blouse']:
            # Check metadata for collar/formal indicators
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    neckline = (visual_attrs.get('neckline') or '').lower()
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    
                    if 'collar' in neckline or 'polo' in neckline or 'button' in neckline:
                        logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - collar detected")
                        return False
                    
                    if formal_level in ['formal', 'business', 'dress', 'professional']:
                        logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - formal level")
                        return False
                    elif formal_level in ['athletic', 'sport']:
                        logger.info(f"✅ GYM: ALLOWED {item_name[:40]} - athletic level")
                        return True
            
            # Check for collar/casual features in name
            casual_top_blocks = [
                'sweater', 'cardigan', 'pullover', 'turtleneck', 'henley', 'flannel',
                'cable knit', 'cable-knit', 'casual shirt', 'dress shirt', 'button up',
                'button down', 'button-up', 'button-down', 'polo shirt', 'polo'
            ]
            
            athletic_qualifiers = ['athletic', 'gym', 'workout', 'training', 'sport', 'performance']
            
            is_casual_top = any(kw in item_name for kw in casual_top_blocks)
            has_athletic_qualifier = any(kw in item_name for kw in athletic_qualifiers)
            
            if is_casual_top and not has_athletic_qualifier:
                logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - casual top without athletic qualifier")
                return False
        
        # SHOES CHECK: Block non-athletic shoes
        if item_type in ['shoes', 'boots', 'footwear'] or 'shoe' in item_type:
            non_athletic_keywords = [
                'oxford', 'loafer', 'derby', 'monk', 'dress shoe', 'dress',
                'heel', 'heels', 'pump', 'formal', 'brogue', 'wingtip',
                'slide', 'slides', 'sandal', 'sandals', 'flip-flop', 'flip flop',
                'boat shoe', 'moccasin', 'ballet flat', 'slipper'
            ]
            
            if any(kw in item_name for kw in non_athletic_keywords):
                logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - non-athletic shoe")
                return False
            
            # Check for athletic shoes
            athletic_shoe_keywords = [
                'sneaker', 'sneakers', 'athletic', 'running', 'training', 'sport', 'gym',
                'basketball', 'tennis', 'cross-trainer', 'workout', 'performance', 'trainer'
            ]
            
            if any(kw in item_name or kw in item_type for kw in athletic_shoe_keywords):
                logger.debug(f"✅ GYM: ALLOWED {item_name[:40]} - athletic shoe")
                return True
            else:
                logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - must be explicitly athletic")
                return False
        
        # Block formal items
        gym_blocks = [
            'suit', 'tuxedo', 'blazer', 'sport coat', 'tie', 'bow tie',
            'leather jacket', 'biker jacket', 'peacoat', 'trench',
            'suspenders', 'cufflinks', 'pocket square', 'belt', 'watch',
            'bracelet', 'necklace', 'ring', 'chain'
        ]
        
        for block in gym_blocks:
            if block in item_type or block in item_name:
                logger.info(f"🚫 GYM: BLOCKED {item_name[:40]} - matched '{block}'")
                return False
        
        logger.debug(f"✅ GYM: PASSED {item_name[:40]}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # FORMAL FILTER
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_formal(self, item: Any, style: str) -> bool:
        """
        Filter for formal occasions (weddings, galas, black-tie).
        Blocks athletic/casual items, allows formal wear.
        """
        item_name = self.safe_get_item_name(item).lower()
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()
        else:
            item_type = str(raw_type).lower()
        
        logger.info(f"👔 FORMAL FILTER ACTIVE")
        
        # Block athletic/gym wear
        athletic_blocks = [
            'sneakers', 'athletic', 'gym', 'workout', 'training', 'sport', 'running',
            'sweatpants', 'joggers', 'track pants', 'leggings', 'yoga pants',
            'hoodie', 'sweatshirt', 'tank top', 'crop top', 'basketball shorts',
            'jersey', 'athletic shorts'
        ]
        
        if any(block in item_name or block in item_type for block in athletic_blocks):
            logger.info(f"🚫 FORMAL: BLOCKED {item_name[:40]} - athletic item")
            return False
        
        # Check metadata for athletic/casual formalLevel
        if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                formal_level = (visual_attrs.get('formalLevel') or '').lower()
                if formal_level in ['athletic', 'sport']:
                    logger.info(f"🚫 FORMAL: BLOCKED {item_name[:40]} - athletic level")
                    return False
        
        logger.debug(f"✅ FORMAL: PASSED {item_name[:40]}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # LOUNGEWEAR FILTER
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_loungewear(self, item: Any, style: str) -> bool:
        """
        Filter for loungewear/home occasions.
        Blocks formal/structured items, allows relaxed wear.
        """
        item_name = self.safe_get_item_name(item).lower()
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()
        else:
            item_type = str(raw_type).lower()
        
        logger.info(f"🏠 LOUNGEWEAR FILTER ACTIVE")
        
        # Block formal wear
        formal_blocks = [
            'suit', 'tuxedo', 'blazer', 'sport coat', 'tie', 'bow tie',
            'dress shirt', 'oxford shoes', 'heels', 'pumps',
            'dress pants', 'slacks', 'pencil skirt'
        ]
        
        if any(block in item_name or block in item_type for block in formal_blocks):
            logger.info(f"🚫 LOUNGEWEAR: BLOCKED {item_name[:40]} - formal item")
            return False
        
        # Check metadata for formal formalLevel
        if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                formal_level = (visual_attrs.get('formalLevel') or '').lower()
                if formal_level in ['formal', 'business', 'professional']:
                    logger.info(f"🚫 LOUNGEWEAR: BLOCKED {item_name[:40]} - formal level")
                    return False
        
        # For bottoms, enforce relaxed/drawstring requirement
        if item_type in ['bottoms', 'pants', 'trousers', 'shorts', 'leggings', 'jeans', 'chinos']:
            # Block structured bottoms
            structured_blocks = [
                'jean', 'denim', 'chino', 'trouser', 'dress pant', 'dress trouser',
                'slack', 'suit pant', 'crease', 'pleated trouser', 'khaki', 'gabardine'
            ]
            
            if any(block in item_name for block in structured_blocks):
                logger.info(f"🚫 LOUNGEWEAR: BLOCKED {item_name[:40]} - structured bottom")
                return False
            
            # Check for relaxed features
            relaxed_markers = [
                'drawstring', 'elastic waist', 'jogger', 'joggers', 'sweatpant', 'sweat pant',
                'track pant', 'lounge', 'relaxed fit', 'pajama', 'pj', 'knit pant',
                'wide-leg', 'wide leg', 'palazzo', 'pull-on', 'pull on', 'loose'
            ]
            
            has_relaxed_feature = any(marker in item_name for marker in relaxed_markers)
            
            if not has_relaxed_feature:
                # Check metadata
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        waistband_type = (visual_attrs.get('waistbandType') or '').lower()
                        if waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
                            has_relaxed_feature = True
                
                if not has_relaxed_feature:
                    logger.info(f"🚫 LOUNGEWEAR: BLOCKED {item_name[:40]} - no relaxed features")
                    return False
        
        logger.debug(f"✅ LOUNGEWEAR: PASSED {item_name[:40]}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # PARTY / DATE FILTER
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_party_date(self, item: Any, style: str) -> bool:
        """
        Filter for party/date/night out occasions.
        Blocks athletic/overly casual items.
        """
        item_name = self.safe_get_item_name(item).lower()
        
        # Block gym/athletic wear
        athletic_blocks = [
            'athletic', 'gym', 'workout', 'training', 'sport shorts',
            'sweatpants', 'joggers', 'yoga pants', 'leggings with athletic',
            'hoodie', 'sweatshirt', 'basketball shorts', 'running shoes'
        ]
        
        if any(block in item_name for block in athletic_blocks):
            logger.warning(f"🚫 PARTY/DATE: BLOCKED {item_name[:40]} - athletic item")
            return False
        
        # Block overly casual items
        too_casual_blocks = [
            'crocs', 'flip-flop', 'slide sandal', 'slide', 'slides', 'slipper',
            'graphic tee', 'band tee', 'pajama', 'sleepwear'
        ]
        
        if any(block in item_name for block in too_casual_blocks):
            logger.warning(f"🚫 PARTY/DATE: BLOCKED {item_name[:40]} - too casual")
            return False
        
        logger.debug(f"✅ PARTY/DATE: PASSED {item_name[:40]}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # STYLE-SPECIFIC FILTERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_old_money_style(self, item: Any) -> bool:
        """
        Filter for old money / urban professional style.
        Blocks athletic/overly casual items.
        """
        item_name = self.safe_get_item_name(item).lower()
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()
        else:
            item_type = str(raw_type).lower()
        
        logger.info(f"🏛️ OLD MONEY STYLE FILTER ACTIVE")
        
        casual_blocks = [
            'athletic', 'gym', 'workout', 'training', 'sport', 'sports jersey',
            'jersey', 'basketball', 'football', 'baseball', 'soccer',
            'sweatshort', 'sweat short', 'sweatpant', 'sweat pant', 'jogger',
            'hoodie', 'graphic tee', 'band tee', 'denim short', 'cargo short',
            'crocs', 'sneaker', 'slides', 'flip-flop', 'flip flop'
        ]
        
        if any(block in item_name for block in casual_blocks):
            logger.info(f"🚫 OLD MONEY: BLOCKED {item_name[:40]} - too casual")
            return False
        
        if item_type in ['sweatshirt', 'hoodie', 'athletic wear', 'gym wear']:
            logger.info(f"🚫 OLD MONEY: BLOCKED type '{item_type}'")
            return False
        
        # Check metadata
        if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
            visual_attrs = item.metadata.get('visualAttributes', {})
            if isinstance(visual_attrs, dict):
                formal_level = (visual_attrs.get('formalLevel') or '').lower()
                if formal_level in ['athletic', 'sport', 'casual']:
                    logger.info(f"🚫 OLD MONEY: BLOCKED {item_name[:40]} - formal level={formal_level}")
                    return False
        
        logger.debug(f"✅ OLD MONEY: PASSED {item_name[:40]}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # BASIC CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _basic_hard_constraints(self, item: Any, occasion_lower: str) -> bool:
        """Basic hard constraints that apply to all occasions"""
        item_name = self.safe_get_item_name(item).lower()
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()
        else:
            item_type = str(raw_type).lower()
        
        # Basic constraints
        if item_type == 'tuxedo' and occasion_lower in ['athletic', 'gym', 'workout']:
            return False
        if item_type == 'evening_gown' and occasion_lower in ['athletic', 'gym', 'workout']:
            return False
        if 'bikini' in item_name and occasion_lower in ['business', 'interview', 'work']:
            return False
        if 'swimwear' in item_name and occasion_lower in ['business', 'interview', 'work']:
            return False
        if 'pajama' in item_name and occasion_lower not in ['home', 'loungewear', 'sleep']:
            return False
        if 'sleepwear' in item_name and occasion_lower not in ['home', 'loungewear', 'sleep']:
            return False
        
        return True

