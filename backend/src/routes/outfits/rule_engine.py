"""
Rule-based outfit generation engine with sophisticated decision trees.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from src.routes.outfits.models import OutfitRequest
from src.routes.outfits.utils import log_generation_strategy

logger = logging.getLogger(__name__)

# Global debug data storage
debug_data = []
exclusion_debug = []


def debug_rule_engine(stage: str, wardrobe_items=None, suitable=None, categorized=None, scores=None, validated=None):
    """Debug logging for rule engine stages."""
    # Debug logging removed to reduce Railway rate limiting
    try:
        debug_info = {
            "stage": stage,
            "wardrobe_count": len(wardrobe_items) if wardrobe_items is not None else None,
            "suitable_count": len(suitable) if suitable is not None else None,
            "categorized_keys": list(categorized.keys()) if categorized else None,
            "scores_count": len(scores) if scores is not None else None,
            "validated_count": len(validated) if validated is not None else None,
        }
        debug_data.append(debug_info)
        # Removed: print("🔎 RULE ENGINE DEBUG:", debug_info)
        # Removed: logger.info(f"🔎 RULE ENGINE DEBUG: {debug_info}")
    except Exception as e:
        error_info = {"stage": stage, "error": str(e)}
        debug_data.append(error_info)
        # Keep only critical errors
        logger.error(f"⚠️ CRITICAL DEBUG ERROR: {e}")


async def generate_rule_based_outfit(wardrobe_items: List[Dict], user_profile: Dict, req: OutfitRequest) -> Dict[str, Any]:
    """Generate outfit using rule-based decision tree and user's wardrobe."""
    try:
        logger.info(f"🎯 Generating rule-based outfit with {len(wardrobe_items)} items")
        
        # Clear previous debug data
        global debug_data, exclusion_debug
        debug_data = []
        exclusion_debug = []
        
        # DEBUG: Start stage
        debug_rule_engine("start", wardrobe_items=wardrobe_items)
        # Reduced logging to prevent Railway rate limits
        logger.info(f"🔍 DEBUG: User profile keys: {list(user_profile.keys()) if user_profile else 'None'}")
        logger.info(f"🔍 DEBUG: Request: style={req.style}, occasion={req.occasion}, baseItemId={req.baseItemId}")
        
        # Rule-based outfit selection using sophisticated decision tree
        
        # ENHANCED: Sophisticated style preference filtering with scoring
        suitable_items = []
        item_scores = {}  # Track scores for each item
        
        # DEBUG: After initialization
        debug_rule_engine("after_init", suitable=suitable_items, scores=item_scores)
        
        # ENHANCED: Ensure all wardrobe items have required fields for ClothingItem validation
        for item in wardrobe_items:
            # Add missing required fields with default values
            if 'season' not in item:
                item['season'] = ['all']
            if 'tags' not in item:
                item['tags'] = []
            if 'style' not in item:
                item['style'] = 'casual'
            if 'occasion' not in item:
                item['occasion'] = 'casual'
            if 'color' not in item:
                item['color'] = ['neutral']
            if 'name' not in item:
                item['name'] = f"Item {item.get('id', 'unknown')}"
        
        # Style-based filtering with scoring
        for item in wardrobe_items:
            try:
                # Calculate style appropriateness score
                style_score = calculate_style_appropriateness_score(req.style, item)
                
                # Only include items with positive scores
                if style_score > 0:
                    suitable_items.append(item)
                    item_scores[item.get('id', 'unknown')] = style_score
                    
            except Exception as e:
                logger.warning(f"⚠️ Error processing item {item.get('id', 'unknown')}: {e}")
                continue
        
        # DEBUG: After style filtering
        debug_rule_engine("after_style_filtering", suitable=suitable_items, scores=item_scores)
        
        if not suitable_items:
            logger.warning("⚠️ No suitable items found after style filtering")
            return await generate_fallback_outfit(req, req.user_id if hasattr(req, 'user_id') else 'unknown')
        
        # Categorize items by type
        categorized_items = {
            'tops': [],
            'bottoms': [],
            'shoes': [],
            'outerwear': [],
            'accessories': []
        }
        
        for item in suitable_items:
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
            
            # Enhanced categorization logic
            if any(top in item_type or top in item_name for top in ['shirt', 'blouse', 'top', 't-shirt', 'tank', 'sweater', 'hoodie']):
                categorized_items['tops'].append(item)
            elif any(bottom in item_type or bottom in item_name for bottom in ['pants', 'jeans', 'shorts', 'skirt', 'trousers']):
                categorized_items['bottoms'].append(item)
            elif any(shoe in item_type or shoe in item_name for shoe in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']):
                categorized_items['shoes'].append(item)
            elif any(outer in item_type or outer in item_name for outer in ['jacket', 'blazer', 'coat', 'cardigan', 'sweater']):
                categorized_items['outerwear'].append(item)
            else:
                categorized_items['accessories'].append(item)
        
        # DEBUG: After categorization
        debug_rule_engine("after_categorization", categorized=categorized_items)
        
        # Select items for outfit
        selected_items = []
        
        # Select one item from each category
        for category, items in categorized_items.items():
            if items:
                # Sort by score and select the best item
                scored_items = [(item, item_scores.get(item.get('id', 'unknown'), 0)) for item in items]
                scored_items.sort(key=lambda x: x[1], reverse=True)
                selected_items.append(scored_items[0][0])
        
        # DEBUG: After item selection
        debug_rule_engine("after_selection", validated=selected_items)
        
        # Ensure base item is included if specified
        if req.baseItemId:
            base_item = next((item for item in wardrobe_items if item.get('id') == req.baseItemId), None)
            if base_item and base_item not in selected_items:
                selected_items.insert(0, base_item)
        
        # Create outfit response
        outfit = {
            'id': str(uuid4()),
            'name': f"Rule-based {req.style} outfit",
            'style': req.style,
            'mood': req.mood,
            'occasion': req.occasion,
            'items': selected_items,
            'confidence_score': 0.7,  # Good confidence for rule-based generation
            'reasoning': f"Rule-based outfit generated with {len(selected_items)} items using sophisticated decision tree",
            'createdAt': datetime.now(),
            'user_id': getattr(req, 'user_id', 'unknown'),
            'generated_at': datetime.now().isoformat(),
            'wearCount': 0,
            'lastWorn': None,
            'metadata': {
                'generation_strategy': 'rule_based',
                'generation_time': time.time(),
                'wardrobe_size': len(wardrobe_items),
                'items_selected': len(selected_items),
                'debug_data': debug_data
            }
        }
        
        logger.info(f"✅ Rule-based outfit generated with {len(selected_items)} items")
        return outfit
        
    except Exception as e:
        logger.error(f"❌ Rule-based generation failed: {e}")
        # Fallback to simple generation
        return await generate_fallback_outfit(req, getattr(req, 'user_id', 'unknown'))


async def generate_fallback_outfit(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Generate a simple fallback outfit when other methods fail."""
    try:
        logger.info(f"🔄 Generating fallback outfit for user: {user_id}")
        
        # Get wardrobe items
        wardrobe_items = req.resolved_wardrobe
        
        if not wardrobe_items:
            logger.warning("⚠️ No wardrobe items available for fallback generation")
            return {
                'id': str(uuid4()),
                'name': f"Fallback {req.style} outfit",
                'style': req.style,
                'mood': req.mood,
                'occasion': req.occasion,
                'items': [],
                'confidence_score': 0.3,
                'reasoning': "No wardrobe items available for outfit generation",
                'createdAt': datetime.now(),
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'wearCount': 0,
                'lastWorn': None,
                'metadata': {
                    'generation_strategy': 'fallback_empty',
                    'generation_time': time.time(),
                    'wardrobe_size': 0
                }
            }
        
        # Simple fallback: select first few items
        selected_items = wardrobe_items[:3]  # Take first 3 items
        
        # Generate weather-aware reasoning
        reasoning = generate_weather_aware_fallback_reasoning(req, selected_items)
        
        outfit = {
            'id': str(uuid4()),
            'name': f"Fallback {req.style} outfit",
            'style': req.style,
            'mood': req.mood,
            'occasion': req.occasion,
            'items': selected_items,
            'confidence_score': 0.4,  # Lower confidence for fallback
            'reasoning': reasoning,
            'createdAt': datetime.now(),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'wearCount': 0,
            'lastWorn': None,
            'metadata': {
                'generation_strategy': 'fallback_simple',
                'generation_time': time.time(),
                'wardrobe_size': len(wardrobe_items),
                'items_selected': len(selected_items)
            }
        }
        
        logger.info(f"✅ Fallback outfit generated with {len(selected_items)} items")
        return outfit
        
    except Exception as e:
        logger.error(f"❌ Fallback generation failed: {e}")
        # Last resort: return empty outfit
        return {
            'id': str(uuid4()),
            'name': f"Emergency {req.style} outfit",
            'style': req.style,
            'mood': req.mood,
            'occasion': req.occasion,
            'items': [],
            'confidence_score': 0.1,
            'reasoning': f"Emergency fallback - all generation methods failed: {str(e)}",
            'createdAt': datetime.now(),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'wearCount': 0,
            'lastWorn': None,
            'metadata': {
                'generation_strategy': 'emergency_fallback',
                'generation_time': time.time(),
                'error': str(e)
            }
        }


def generate_weather_aware_fallback_reasoning(req: OutfitRequest, selected_items: List[Dict]) -> str:
    """Generate weather-aware reasoning for fallback outfits."""
    try:
        weather = req.weather
        if not weather:
            return f"Fallback outfit with {len(selected_items)} items from your wardrobe"
        
        temp = weather.get('temperature', 70)
        condition = weather.get('condition', 'clear')
        
        reasoning_parts = [
            f"Fallback outfit with {len(selected_items)} items",
            f"selected for {temp}°F {condition} weather"
        ]
        
        # Add item-specific reasoning
        if selected_items:
            item_names = [item.get('name', 'item') for item in selected_items[:2]]
            if item_names:
                reasoning_parts.append(f"featuring {', '.join(item_names)}")
        
        return ", ".join(reasoning_parts)
        
    except Exception as e:
        logger.warning(f"⚠️ Error generating weather reasoning: {e}")
        return f"Fallback outfit with {len(selected_items)} items from your wardrobe"


def calculate_style_appropriateness_score(style: str, item: Dict[str, Any]) -> int:
    """Calculate style appropriateness score for an item."""
    try:
        if not item or not style:
            return 0
        
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
        item_style = (item.get('style', '') if item else '').lower()
        
        style_lower = style.lower()
        
        # Base score
        score = 0
        
        # Style matching
        if style_lower in item_style:
            score += 10
        if style_lower in item_type:
            score += 8
        if style_lower in item_name:
            score += 6
        
        # Occasion appropriateness
        occasion = (item.get('occasion', '') if item else '').lower()
        if occasion and occasion != 'casual':
            score += 5
        
        # Color scoring
        colors = item.get('color', [])
        if colors and isinstance(colors, list):
            score += 3
        
        # Brand/quality indicators
        brand = item.get('brand', '')
        if brand:
            score += 2
        
        return max(0, score)
        
    except Exception as e:
        logger.warning(f"⚠️ Error calculating style score: {e}")
        return 0
