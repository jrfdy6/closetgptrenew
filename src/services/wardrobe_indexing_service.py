"""
Wardrobe Indexing Service
=========================

This service handles the creation and management of Firestore indexes for wardrobe items
to enable fast, scalable queries for outfit generation and fallback strategies.
"""

from typing import List, Dict, Any, Optional
from ..config.firebase import db
from ..custom_types.wardrobe import ClothingItem
import time
import logging

logger = logging.getLogger(__name__)

class WardrobeIndexingService:
    def __init__(self):
        self.db = db
        self.wardrobe_collection = self.db.collection('wardrobe')
        
        # Define the indexed fields for fast queries
        self.indexed_fields = {
            'category': 'string',           # top, bottom, outerwear, shoes, accessory
            'seasonality': 'array',         # ["summer", "spring", "fall", "winter"]
            'material': 'string',           # cotton, wool, fleece, silk, etc.
            'color': 'string',              # Primary color
            'fit': 'string',                # loose, fitted, oversized, etc.
            'style_tags': 'array',          # ["grunge", "old_money", "minimalist"]
            'formality': 'string',          # casual, semi-formal, formal
            'occasions': 'array',           # ["date", "office", "gym", "party"]
            'temperature_range': 'array',   # [min_temp, max_temp]
            'body_type_compatibility': 'array',  # ["athletic", "curvy", "petite"]
            'skin_tone_compatibility': 'array',  # ["warm", "cool", "neutral"]
            'quality_score': 'number',      # 0.0 to 1.0
            'pairability_score': 'number',  # 0.0 to 1.0
            'last_worn': 'timestamp',       # Last time item was worn
            'wear_count': 'number',         # Number of times worn
            'favorite': 'boolean',          # User marked as favorite
            'userId': 'string',             # User ID for security
            'createdAt': 'timestamp',       # Item creation time
            'updatedAt': 'timestamp'        # Last update time
        }
        
        # Composite indexes for complex queries
        self.composite_indexes = [
            # Basic category + seasonality queries
            ['userId', 'category', 'seasonality'],
            ['userId', 'category', 'formality'],
            ['userId', 'category', 'occasions'],
            
            # Weather-based queries
            ['userId', 'category', 'temperature_range'],
            ['userId', 'category', 'material'],
            
            # Style-based queries
            ['userId', 'category', 'style_tags'],
            ['userId', 'category', 'fit'],
            
            # Performance-based queries
            ['userId', 'category', 'quality_score'],
            ['userId', 'category', 'pairability_score'],
            ['userId', 'category', 'favorite'],
            
            # Complex multi-field queries
            ['userId', 'category', 'seasonality', 'formality'],
            ['userId', 'category', 'occasions', 'style_tags'],
            ['userId', 'category', 'temperature_range', 'material'],
            ['userId', 'category', 'body_type_compatibility', 'skin_tone_compatibility'],
            
            # Time-based queries
            ['userId', 'category', 'last_worn'],
            ['userId', 'category', 'wear_count'],
            
            # Advanced outfit generation queries
            ['userId', 'category', 'seasonality', 'occasions', 'formality'],
            ['userId', 'category', 'temperature_range', 'material', 'style_tags'],
            ['userId', 'category', 'quality_score', 'pairability_score', 'favorite']
        ]

    async def create_indexes_for_wardrobe_item(self, item: ClothingItem) -> Dict[str, Any]:
        """
        Create indexed fields for a wardrobe item to enable fast queries.
        
        Args:
            item: The ClothingItem to index
            
        Returns:
            Dictionary containing the indexed data
        """
        try:
            # Extract and normalize indexed fields from the item
            indexed_data = {
                'userId': item.userId,
                'category': self._determine_category(item.type),
                'seasonality': self._normalize_seasonality(item.season),
                'material': self._extract_material(item),
                'color': self._extract_primary_color(item),
                'fit': self._extract_fit(item),
                'style_tags': self._extract_style_tags(item),
                'formality': self._determine_formality(item),
                'occasions': self._normalize_occasions(item.occasion),
                'temperature_range': self._calculate_temperature_range(item),
                'body_type_compatibility': self._determine_body_type_compatibility(item),
                'skin_tone_compatibility': self._determine_skin_tone_compatibility(item),
                'quality_score': self._calculate_quality_score(item),
                'pairability_score': self._calculate_pairability_score(item),
                'last_worn': item.lastWorn if hasattr(item, 'lastWorn') else None,
                'wear_count': item.wearCount if hasattr(item, 'wearCount') else 0,
                'favorite': item.favorite if hasattr(item, 'favorite') else False,
                'createdAt': item.createdAt,
                'updatedAt': item.updatedAt,
                
                # Keep original fields for compatibility
                'id': item.id,
                'name': item.name,
                'type': item.type,
                'imageUrl': item.imageUrl,
                'tags': item.tags,
                'dominantColors': item.dominantColors,
                'matchingColors': item.matchingColors,
                'style': item.style,
                'occasion': item.occasion
            }
            
            return indexed_data
            
        except Exception as e:
            logger.error(f"Error creating indexes for item {item.id}: {e}")
            return {}

    async def update_wardrobe_item_indexes(self, item_id: str, item: ClothingItem) -> bool:
        """
        Update the indexed fields for an existing wardrobe item.
        
        Args:
            item_id: The ID of the item to update
            item: The updated ClothingItem
            
        Returns:
            True if successful, False otherwise
        """
        try:
            indexed_data = await self.create_indexes_for_wardrobe_item(item)
            if not indexed_data:
                return False
            
            # Update the document with new indexed fields
            doc_ref = self.wardrobe_collection.document(item_id)
            doc_ref.update(indexed_data)
            
            logger.info(f"Successfully updated indexes for item {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating indexes for item {item_id}: {e}")
            return False

    async def batch_update_wardrobe_indexes(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """
        Batch update indexes for multiple wardrobe items.
        
        Args:
            items: List of ClothingItem objects to index
            
        Returns:
            Dictionary with results of the batch operation
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Use Firestore batch writes for efficiency
            batch = self.db.batch()
            
            for item in items:
                try:
                    indexed_data = await self.create_indexes_for_wardrobe_item(item)
                    if indexed_data:
                        doc_ref = self.wardrobe_collection.document(item.id)
                        batch.update(doc_ref, indexed_data)
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to create indexes for item {item.id}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error processing item {item.id}: {str(e)}")
            
            # Commit the batch
            if results['successful'] > 0:
                batch.commit()
                logger.info(f"Batch updated {results['successful']} items, {results['failed']} failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch update: {e}")
            results['errors'].append(f"Batch operation failed: {str(e)}")
            return results

    # Helper methods for extracting and normalizing indexed data
    def _determine_category(self, item_type: str) -> str:
        """Determine the category of an item based on its type."""
        category_mapping = {
            'top': ['shirt', 't-shirt', 'blouse', 'sweater', 'hoodie', 'tank-top'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'leggings'],
            'outerwear': ['jacket', 'coat', 'blazer', 'cardigan'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'flats', 'heels'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'bag', 'hat']
        }
        
        for category, types in category_mapping.items():
            if item_type.lower() in types:
                return category
        
        return 'other'

    def _normalize_seasonality(self, seasons: List[str]) -> List[str]:
        """Normalize season data to standard format."""
        if not seasons:
            return ['all']
        
        normalized = []
        season_mapping = {
            'spring': 'spring',
            'summer': 'summer', 
            'fall': 'fall',
            'autumn': 'fall',
            'winter': 'winter',
            'all': 'all'
        }
        
        for season in seasons:
            normalized_season = season_mapping.get(season.lower(), 'all')
            if normalized_season not in normalized:
                normalized.append(normalized_season)
        
        return normalized if normalized else ['all']

    def _extract_material(self, item: ClothingItem) -> str:
        """Extract the primary material from an item."""
        if hasattr(item, 'metadata') and item.metadata:
            material = getattr(item.metadata, 'material', None)
            if material:
                return material.lower()
        
        # Fallback to tags
        if item.tags:
            material_keywords = ['cotton', 'wool', 'silk', 'linen', 'polyester', 'denim', 'leather', 'suede']
            for tag in item.tags:
                if tag.lower() in material_keywords:
                    return tag.lower()
        
        return 'unknown'

    def _extract_primary_color(self, item: ClothingItem) -> str:
        """Extract the primary color from an item."""
        if item.dominantColors:
            return item.dominantColors[0].name.lower()
        elif hasattr(item, 'color'):
            return item.color.lower()
        else:
            return 'unknown'

    def _extract_fit(self, item: ClothingItem) -> str:
        """Extract the fit information from an item."""
        if hasattr(item, 'metadata') and item.metadata:
            fit = getattr(item.metadata, 'fit', None)
            if fit:
                return fit.lower()
        
        # Fallback to tags
        if item.tags:
            fit_keywords = ['loose', 'fitted', 'oversized', 'slim', 'relaxed']
            for tag in item.tags:
                if tag.lower() in fit_keywords:
                    return tag.lower()
        
        return 'regular'

    def _extract_style_tags(self, item: ClothingItem) -> List[str]:
        """Extract style tags from an item."""
        style_tags = []
        
        # From style field
        if item.style:
            style_tags.extend(item.style)
        
        # From tags field
        if item.tags:
            style_keywords = ['grunge', 'old_money', 'minimalist', 'bohemian', 'streetwear', 
                            'vintage', 'modern', 'classic', 'trendy', 'elegant']
            for tag in item.tags:
                if tag.lower() in style_keywords:
                    style_tags.append(tag.lower())
        
        return list(set(style_tags))  # Remove duplicates

    def _determine_formality(self, item: ClothingItem) -> str:
        """Determine the formality level of an item."""
        formal_keywords = ['formal', 'business', 'elegant', 'suit', 'blazer', 'dress']
        casual_keywords = ['casual', 'streetwear', 'athletic', 'gym', 'sporty']
        
        # Check item type
        if item.type.lower() in ['suit', 'blazer', 'dress']:
            return 'formal'
        
        # Check style tags
        if item.style:
            for style in item.style:
                if style.lower() in formal_keywords:
                    return 'formal'
                elif style.lower() in casual_keywords:
                    return 'casual'
        
        # Check tags
        if item.tags:
            for tag in item.tags:
                if tag.lower() in formal_keywords:
                    return 'formal'
                elif tag.lower() in casual_keywords:
                    return 'casual'
        
        return 'semi-formal'

    def _normalize_occasions(self, occasions: List[str]) -> List[str]:
        """Normalize occasion data to standard format."""
        if not occasions:
            return ['casual']
        
        normalized = []
        occasion_mapping = {
            'casual': 'casual',
            'formal': 'formal',
            'business': 'office',
            'work': 'office',
            'office': 'office',
            'party': 'party',
            'date': 'date',
            'gym': 'gym',
            'workout': 'gym',
            'athletic': 'gym',
            'sport': 'athletic',
            'sports': 'athletic'
        }
        
        for occasion in occasions:
            normalized_occasion = occasion_mapping.get(occasion.lower(), occasion.lower())
            if normalized_occasion not in normalized:
                normalized.append(normalized_occasion)
        
        return normalized if normalized else ['casual']

    def _calculate_temperature_range(self, item: ClothingItem) -> List[float]:
        """Calculate the temperature range suitable for an item."""
        # Default temperature ranges based on season
        season_temps = {
            'summer': [70, 100],
            'spring': [50, 75],
            'fall': [45, 70],
            'winter': [20, 55]
        }
        
        if item.season:
            # Calculate average temperature range based on seasons
            min_temp = 100
            max_temp = 0
            season_count = 0
            
            for season in item.season:
                if season.lower() in season_temps:
                    min_temp = min(min_temp, season_temps[season.lower()][0])
                    max_temp = max(max_temp, season_temps[season.lower()][1])
                    season_count += 1
            
            if season_count > 0:
                return [min_temp, max_temp]
        
        # Fallback to material-based temperature
        material = self._extract_material(item)
        if material in ['wool', 'fleece', 'cashmere']:
            return [20, 60]  # Cold weather
        elif material in ['cotton', 'linen']:
            return [50, 90]  # Moderate weather
        else:
            return [40, 80]  # Default range

    def _determine_body_type_compatibility(self, item: ClothingItem) -> List[str]:
        """Determine body type compatibility for an item."""
        # This would be based on item characteristics and user feedback
        # For now, return all body types as compatible
        return ['athletic', 'curvy', 'petite', 'plus-size', 'tall', 'short']

    def _determine_skin_tone_compatibility(self, item: ClothingItem) -> List[str]:
        """Determine skin tone compatibility for an item."""
        # This would be based on color analysis
        # For now, return all skin tones as compatible
        return ['warm', 'cool', 'neutral']

    def _calculate_quality_score(self, item: ClothingItem) -> float:
        """Calculate a quality score for an item."""
        score = 0.5  # Base score
        
        # Material quality
        material = self._extract_material(item)
        material_scores = {
            'silk': 0.9,
            'cashmere': 0.9,
            'wool': 0.8,
            'cotton': 0.7,
            'linen': 0.7,
            'polyester': 0.5
        }
        score += material_scores.get(material, 0.5) * 0.3
        
        # Brand quality (if available)
        if hasattr(item, 'brand') and item.brand:
            # This would be based on a brand quality database
            score += 0.1
        
        return min(score, 1.0)

    def _calculate_pairability_score(self, item: ClothingItem) -> float:
        """Calculate a pairability score for an item."""
        score = 0.5  # Base score
        
        # Color pairability
        if item.dominantColors:
            # Neutral colors are more pairable
            neutral_colors = ['black', 'white', 'gray', 'beige', 'navy']
            if item.dominantColors[0].name.lower() in neutral_colors:
                score += 0.2
        
        # Style versatility
        if item.style and len(item.style) > 1:
            score += 0.1
        
        # Occasion versatility
        if item.occasion and len(item.occasion) > 1:
            score += 0.1
        
        return min(score, 1.0)

    async def get_indexed_wardrobe_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about indexed wardrobe items for a user.
        
        Args:
            user_id: The user ID to get stats for
            
        Returns:
            Dictionary with wardrobe statistics
        """
        try:
            stats = {
                'total_items': 0,
                'categories': {},
                'materials': {},
                'colors': {},
                'formality_levels': {},
                'indexed_items': 0,
                'non_indexed_items': 0
            }
            
            # Query wardrobe items
            query = self.wardrobe_collection.where('userId', '==', user_id)
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict()
                stats['total_items'] += 1
                
                # Check if item is properly indexed
                if 'category' in data and 'material' in data:
                    stats['indexed_items'] += 1
                    
                    # Category stats
                    category = data.get('category', 'unknown')
                    stats['categories'][category] = stats['categories'].get(category, 0) + 1
                    
                    # Material stats
                    material = data.get('material', 'unknown')
                    stats['materials'][material] = stats['materials'].get(material, 0) + 1
                    
                    # Color stats
                    color = data.get('color', 'unknown')
                    stats['colors'][color] = stats['colors'].get(color, 0) + 1
                    
                    # Formality stats
                    formality = data.get('formality', 'unknown')
                    stats['formality_levels'][formality] = stats['formality_levels'].get(formality, 0) + 1
                else:
                    stats['non_indexed_items'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting wardrobe stats for user {user_id}: {e}")
            return {}

    def get_required_firestore_indexes(self) -> List[str]:
        """
        Get a list of required Firestore indexes for manual creation.
        
        Returns:
            List of index definitions for Firebase Console
        """
        indexes = []
        
        for index_fields in self.composite_indexes:
            index_def = {
                'collection': 'wardrobe',
                'fields': index_fields,
                'queryScope': 'COLLECTION'
            }
            indexes.append(index_def)
        
        return indexes 