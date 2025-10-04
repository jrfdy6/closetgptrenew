#!/usr/bin/env python3
"""
Wardrobe Preprocessor: Convert Complex Metadata to System Format

This service converts your 28-field complex wardrobe metadata into the format
that the robust outfit generation system expects, enabling sophisticated
personalization without breaking the core system.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WardrobePreprocessor:
    """
    Preprocesses complex wardrobe metadata for the outfit generation system
    
    Converts your 28-field complex metadata into the 9-field format that
    the system expects, while preserving sophisticated personalization data.
    """
    
    def __init__(self):
        self.logger = logger
    
    def preprocess_wardrobe(self, complex_wardrobe: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert complex wardrobe metadata to system format
        
        Args:
            complex_wardrobe: List of wardrobe items with 28 metadata fields
            
        Returns:
            List of wardrobe items in 9-field system format with enhanced data
        """
        self.logger.info(f"🔄 PREPROCESSING: Converting {len(complex_wardrobe)} complex wardrobe items")
        
        processed_items = []
        
        for item in complex_wardrobe:
            try:
                processed_item = self._preprocess_item(item)
                processed_items.append(processed_item)
                self.logger.debug(f"✅ Processed: {processed_item.get('name', 'Unknown')}")
            except Exception as e:
                self.logger.error(f"❌ Failed to process item: {e}")
                # Add fallback item to prevent complete failure
                processed_items.append(self._create_fallback_item(item))
        
        self.logger.info(f"✅ PREPROCESSING COMPLETE: {len(processed_items)} items processed")
        return processed_items
    
    def _preprocess_item(self, complex_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a single complex wardrobe item
        
        Args:
            complex_item: Item with 28 metadata fields
            
        Returns:
            Item in 9-field system format with enhanced data
        """
        # Handle None items
        if complex_item is None:
            self.logger.warning("⚠️ Received None item in _preprocess_item, returning fallback")
            return {
                'id': 'fallback',
                'name': 'Fallback Item',
                'type': 'unknown',
                'color': 'Unknown',
                'imageUrl': 'https://example.com/placeholder.jpg',
                'userId': 'test_user',
                'occasion': ['casual'],
                'style': ['casual'],
                'tags': ['fallback']
            }
        
        # Extract core fields (required)
        processed = {
            'id': complex_item.get('id', 'unknown'),
            'name': complex_item.get('name', 'Unknown Item'),
            'type': complex_item.get('type', 'unknown'),
            'color': complex_item.get('color', 'Unknown'),
            'imageUrl': complex_item.get('imageUrl', 'https://example.com/placeholder.jpg'),
            'userId': complex_item.get('userId', 'test_user'),
        }
        
        # Process occasion field (enhanced with complex metadata)
        processed['occasion'] = self._enhance_occasion_field(complex_item)
        
        # Process style field (enhanced with complex metadata)
        processed['style'] = self._enhance_style_field(complex_item)
        
        # Process tags field (enhanced with complex metadata)
        processed['tags'] = self._enhance_tags_field(complex_item)
        
        # Preserve mood field (critical for mood filtering)
        processed['mood'] = self._preserve_mood_field(complex_item)
        
        # Add sophisticated metadata as custom fields for future use
        processed['_complex_metadata'] = self._extract_complex_metadata(complex_item)
        
        return processed
    
    def _enhance_occasion_field(self, complex_item: Dict[str, Any]) -> List[str]:
        """
        Enhance occasion field with complex metadata analysis
        
        Uses brand, season, mood, and usage data to create more sophisticated
        occasion recommendations.
        """
        base_occasions = complex_item.get('occasion', [])
        if isinstance(base_occasions, str):
            base_occasions = base_occasions.split()
        
        # Conservative occasion enhancement - don't over-enhance
        enhanced_occasions = base_occasions.copy()
        
        # Only add occasions if they make logical sense
        brand = complex_item.get('brand', '').lower()
        season = complex_item.get('season', [])
        if isinstance(season, str):
            season = season.split()
        mood = complex_item.get('mood', [])
        if isinstance(mood, str):
            mood = mood.split()
        
        # Conservative brand-based enhancement
        if any(b in brand for b in ['brooks', 'hugo', 'calvin', 'ralph']) and 'formal' not in enhanced_occasions:
            enhanced_occasions.append('formal')
        
        # Conservative usage-based enhancement (only for truly versatile items)
        usage_count = complex_item.get('usage_count', 0)
        wear_count = complex_item.get('wearCount', 0)
        total_usage = usage_count + wear_count
        
        # Only add 'everyday' if item is truly versatile (high usage + casual style)
        if total_usage > 15 and 'casual' in enhanced_occasions and 'everyday' not in enhanced_occasions:
            enhanced_occasions.append('everyday')
        
        # DON'T add 'party' to winter items - this was causing issues
        # DON'T add broad occasions that don't make sense
        
        return list(set(enhanced_occasions))  # Remove duplicates
    
    def _enhance_style_field(self, complex_item: Dict[str, Any]) -> List[str]:
        """
        Enhance style field with complex metadata analysis
        
        Uses brand, mood, season, and usage data to create more sophisticated
        style recommendations.
        """
        base_styles = complex_item.get('style', [])
        if isinstance(base_styles, str):
            base_styles = base_styles.split()
        
        enhanced_styles = base_styles.copy()
        
        # Conservative style enhancement - avoid contradictory styles
        brand = complex_item.get('brand', '').lower()
        mood = complex_item.get('mood', [])
        if isinstance(mood, str):
            mood = mood.split()
        season = complex_item.get('season', [])
        if isinstance(season, str):
            season = season.split()
        
        # Conservative brand-based enhancement
        if 'abercrombie' in brand and 'preppy' not in enhanced_styles:
            enhanced_styles.append('preppy')
        elif 'brooks' in brand and 'professional' not in enhanced_styles:
            enhanced_styles.append('professional')
        elif 'levi' in brand and 'vintage' not in enhanced_styles:
            enhanced_styles.append('vintage')
        
        # Conservative mood-based enhancement
        if 'professional' in mood and 'business' not in enhanced_styles:
            enhanced_styles.append('business')
        if 'relaxed' in mood and 'comfortable' not in enhanced_styles:
            enhanced_styles.append('comfortable')
        
        # Conservative season-based enhancement
        if 'winter' in season and 'layered' not in enhanced_styles:
            enhanced_styles.append('layered')
        if 'summer' in season and 'light' not in enhanced_styles:
            enhanced_styles.append('light')
        
        # DON'T add contradictory styles like 'formal' + 'casual'
        # DON'T add 'cozy' to all winter items
        
        return list(set(enhanced_styles))  # Remove duplicates
    
    def _enhance_tags_field(self, complex_item: Dict[str, Any]) -> List[str]:
        """
        Enhance tags field with complex metadata analysis
        
        Combines original tags with sophisticated metadata-derived tags.
        """
        base_tags = complex_item.get('tags', [])
        if isinstance(base_tags, str):
            base_tags = base_tags.split()
        
        enhanced_tags = base_tags.copy()
        
        # Add sophisticated tags based on complex metadata
        brand = complex_item.get('brand', '').lower()
        if brand:
            enhanced_tags.append(f'brand_{brand.replace(" ", "_")}')
        
        # Usage-based tags
        usage_count = complex_item.get('usage_count', 0)
        wear_count = complex_item.get('wearCount', 0)
        total_usage = usage_count + wear_count
        
        if total_usage > 15:
            enhanced_tags.append('highly_worn')
        elif total_usage == 0:
            enhanced_tags.append('never_worn')
        
        # Favorite status
        if complex_item.get('favorite', False):
            enhanced_tags.append('favorite')
        
        # Season tags
        season = complex_item.get('season', [])
        if isinstance(season, str):
            season = season.split()
        
        for s in season:
            enhanced_tags.append(f'season_{s}')
        
        # Mood tags
        mood = complex_item.get('mood', [])
        if isinstance(mood, str):
            mood = mood.split()
        
        for m in mood:
            enhanced_tags.append(f'mood_{m}')
        
        return list(set(enhanced_tags))  # Remove duplicates
    
    def _preserve_mood_field(self, complex_item: Dict[str, Any]) -> List[str]:
        """
        Preserve mood field from complex metadata
        
        Args:
            complex_item: Item with complex metadata
            
        Returns:
            List of mood values
        """
        mood = complex_item.get('mood', [])
        
        # Handle both string and list formats
        if isinstance(mood, str):
            if mood.strip():
                mood = mood.split()
            else:
                mood = []
        
        # Ensure it's a list
        if not isinstance(mood, list):
            mood = []
        
        # Remove empty strings and duplicates
        mood = list(set([m.strip() for m in mood if m.strip()]))
        
        return mood
    
    def _extract_complex_metadata(self, complex_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and preserve complex metadata for future sophisticated features
        
        Returns a dictionary with all the complex metadata fields that aren't
        directly used in the current system but could be used for future
        sophisticated personalization.
        """
        return {
            'brand': complex_item.get('brand', ''),
            'season': complex_item.get('season', []),
            'mood': complex_item.get('mood', []),
            'gender': complex_item.get('gender', ''),
            'matchingColors': complex_item.get('matchingColors', []),
            'dominantColors': complex_item.get('dominantColors', []),
            'colorName': complex_item.get('colorName', ''),
            'subType': complex_item.get('subType', ''),
            'bodyTypeCompatibility': complex_item.get('bodyTypeCompatibility', []),
            'weatherCompatibility': complex_item.get('weatherCompatibility', []),
            'favorite': complex_item.get('favorite', False),
            'usage_count': complex_item.get('usage_count', 0),
            'wearCount': complex_item.get('wearCount', 0),
            'lastWorn': complex_item.get('lastWorn', None),
            'last_used_at': complex_item.get('last_used_at', None),
            'createdAt': complex_item.get('createdAt', None),
            'updatedAt': complex_item.get('updatedAt', None),
            'backgroundRemoved': complex_item.get('backgroundRemoved', False),
            'metadata': complex_item.get('metadata', {})
        }
    
    def _create_fallback_item(self, complex_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback item if preprocessing fails
        
        Ensures the system always has a working item to prevent complete failure.
        """
        return {
            'id': complex_item.get('id', 'fallback'),
            'name': complex_item.get('name', 'Fallback Item'),
            'type': complex_item.get('type', 'unknown'),
            'color': complex_item.get('color', 'Unknown'),
            'imageUrl': complex_item.get('imageUrl', ''),
            'userId': complex_item.get('userId', 'unknown'),
            'occasion': ['casual', 'everyday'],
            'style': ['casual'],
            'tags': ['fallback'],
            '_complex_metadata': {}
        }

# Global preprocessor instance
wardrobe_preprocessor = WardrobePreprocessor()