"""
Simple outfit generation service for fallback scenarios.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from ...routes.outfits.models import OutfitRequest, OutfitResponse

logger = logging.getLogger(__name__)


class SimpleOutfitService:
    """Simple outfit generation service for fallback scenarios."""
    
    def __init__(self):
        self.logger = logger
    
    async def generate_simple_outfit(self, req: OutfitRequest, user_id: str) -> Dict[str, Any]:
        """
        Generate a simple outfit using basic logic and fallback strategies.
        This is used when the robust service fails or is unavailable.
        """
        logger.info(f"🔄 Using simple outfit generation for user: {user_id}")
        
        # Get wardrobe items
        wardrobe_items = req.resolved_wardrobe
        
        if not wardrobe_items:
            logger.warning("⚠️ No wardrobe items available for simple generation")
            return self._create_empty_outfit(req, user_id)
        
        # Simple outfit generation logic
        selected_items = []
        
        # Try to find at least one item of each basic category
        categories = ['top', 'bottom', 'shoes']
        
        for category in categories:
            # Find items that match this category
            category_items = [
                item for item in wardrobe_items 
                if self._item_matches_category(item, category)
            ]
            
            if category_items:
                # Select the first item from this category
                selected_items.append(category_items[0])
                logger.info(f"✅ Selected {category}: {category_items[0].get('name', 'Unknown')}")
        
        # If we still don't have enough items, add more from wardrobe
        if len(selected_items) < 3:
            remaining_items = [item for item in wardrobe_items if item not in selected_items]
            needed = 3 - len(selected_items)
            selected_items.extend(remaining_items[:needed])
        
        # Create outfit response
        outfit = {
            'id': str(uuid4()),
            'name': f"Simple {req.style} outfit",
            'style': req.style,
            'mood': req.mood,
            'occasion': req.occasion,
            'items': selected_items,
            'confidence_score': 0.6,  # Lower confidence for simple generation
            'reasoning': f"Simple outfit generated with {len(selected_items)} items from your wardrobe",
            'createdAt': datetime.now(),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'wearCount': 0,
            'lastWorn': None,
            'metadata': {
                'generation_strategy': 'simple_fallback',
                'generation_time': datetime.now().timestamp(),
                'wardrobe_size': len(wardrobe_items),
                'items_selected': len(selected_items)
            }
        }
        
        logger.info(f"✅ Simple outfit generated with {len(selected_items)} items")
        return outfit
    
    def _item_matches_category(self, item: Dict[str, Any], category: str) -> bool:
        """Check if an item matches a basic category."""
        if not item:
            return False
        
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
        
        category_mappings = {
            'top': ['shirt', 'blouse', 't-shirt', 'tank', 'sweater', 'hoodie', 'top'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'trousers', 'bottom'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats']
        }
        
        if category in category_mappings:
            return any(cat in item_type or cat in item_name for cat in category_mappings[category])
        
        return False
    
    def _create_empty_outfit(self, req: OutfitRequest, user_id: str) -> Dict[str, Any]:
        """Create an empty outfit when no wardrobe items are available."""
        return {
            'id': str(uuid4()),
            'name': f"Empty {req.style} outfit",
            'style': req.style,
            'mood': req.mood,
            'occasion': req.occasion,
            'items': [],
            'confidence_score': 0.0,
            'reasoning': "No wardrobe items available for outfit generation",
            'createdAt': datetime.now(),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'wearCount': 0,
            'lastWorn': None,
            'metadata': {
                'generation_strategy': 'empty_fallback',
                'generation_time': datetime.now().timestamp(),
                'wardrobe_size': 0,
                'items_selected': 0
            }
        }
