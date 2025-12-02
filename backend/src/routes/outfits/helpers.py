"""
Helper functions for outfit generation.
Utility functions for item categorization, caching, and outfit manipulation.
"""

import logging
import hashlib
import random
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import get_item_category from scoring module (already extracted there)
from .scoring import get_item_category

# Import weather functions
from .weather import check_item_weather_appropriateness


def is_layer_item(item_type: str) -> bool:
    """Check if item type is a layering item."""
    item_type_lower = item_type.lower()
    layer_types = [
        "shirt", "t-shirt", "blouse", "sweater", "jacket", "coat", "blazer", "cardigan", "hoodie",
        "dress shirt", "button up", "button-up", "oxford", "dress-shirt", "polo"
    ]
    return any(layer_type in item_type_lower for layer_type in layer_types)


def _generate_wardrobe_hash(wardrobe_items: List[Dict[str, Any]]) -> str:
    """Generate a hash of wardrobe item IDs for cache invalidation."""
    if not wardrobe_items:
        return "empty"
    
    # Extract item IDs and sort for consistent hashing
    item_ids = sorted([str(item.get('id', '')) for item in wardrobe_items if item.get('id')])
    if not item_ids:
        return "no_ids"
    
    # Create hash from sorted IDs
    hash_string = ','.join(item_ids)
    return hashlib.md5(hash_string.encode()).hexdigest()[:12]


def _generate_outfit_cache_key(
    user_id: str,
    occasion: str,
    style: str,
    mood: str,
    weather: Optional[Dict[str, Any]],
    baseItemId: Optional[str],
    wardrobe_items: List[Dict[str, Any]]
) -> str:
    """Generate cache key for outfit generation request."""
    # Round temperature to 5°F increments for better cache hits
    temp = 70  # Default
    if weather and isinstance(weather, dict):
        temp = weather.get('temperature', 70)
    elif weather:
        temp = getattr(weather, 'temperature', 70)
    
    temp_rounded = int(round(temp / 5) * 5)
    
    # Generate wardrobe hash for auto-invalidation
    wardrobe_hash = _generate_wardrobe_hash(wardrobe_items)
    
    # Build cache key
    base_item_part = baseItemId or 'none'
    key_parts = [
        user_id,
        occasion.lower(),
        style.lower(),
        mood.lower(),
        str(temp_rounded),
        base_item_part,
        wardrobe_hash
    ]
    
    cache_key = ':'.join(key_parts)
    return f"outfit:{cache_key}"


async def _validate_cached_outfit(
    cached_outfit: Dict[str, Any],
    user_id: str,
    current_wardrobe_items: List[Dict[str, Any]]
) -> bool:
    """Validate that all items in cached outfit still exist in user's wardrobe."""
    if not cached_outfit or not cached_outfit.get('items'):
        return False
    
    # Create set of current wardrobe item IDs for fast lookup
    current_item_ids = {item.get('id') for item in current_wardrobe_items if item.get('id')}
    
    # Check if all cached outfit items still exist
    for item in cached_outfit['items']:
        item_id = item.get('id') if isinstance(item, dict) else getattr(item, 'id', None)
        if not item_id or item_id not in current_item_ids:
            logger.info(f"⚠️ Cache validation failed: Item {item_id} no longer in wardrobe")
            return False
    
    return True


def ensure_base_item_included(outfit: Dict[str, Any], base_item_id: Optional[str], wardrobe_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure base item is included in the outfit if specified, with weather appropriateness check."""
    if not base_item_id:
        return outfit
    
    logger.info(f"🎯 Ensuring base item {base_item_id} is included in outfit")
    
    # Find base item in wardrobe
    base_item = next((item for item in wardrobe_items if item.get('id') == base_item_id), None)
    
    if not base_item:
        logger.warning(f"⚠️ Base item {base_item_id} not found in wardrobe")
        return outfit
    
    # Check weather appropriateness of base item
    weather_data = (outfit.get('weather_data') if outfit else None)
    if weather_data:
        is_weather_appropriate = check_item_weather_appropriateness(base_item, weather_data)
        if not is_weather_appropriate:
            logger.warning(f"⚠️ Base item {(base_item.get('name', 'unnamed') if base_item else 'unnamed')} may not be weather-appropriate")
            # Add weather warning to outfit reasoning
            current_reasoning = (outfit.get('reasoning', '') if outfit else '')
            
            # Generate specific warning based on weather conditions
            temp = (weather_data.get('temperature', 70) if weather_data else 70)
            condition = (weather_data.get('condition', '') if weather_data else '').lower()
            item_name = (base_item.get('name', 'item') if base_item else 'item')
            
            # Get item details for specific warnings
            item_type = (base_item.get('type', '') if base_item else '').lower()
            metadata = (base_item.get('metadata', {}) if base_item else {})
            material = ""
            color = ""
            if isinstance(metadata, dict):
                visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                if isinstance(visual_attrs, dict):
                    material = (visual_attrs.get('material', '') if visual_attrs else '').lower()
                    color = (visual_attrs.get('color', '') if visual_attrs else '').lower()
            
            # Generate specific warning
            if temp >= 85 and any(mat in material for mat in ['wool', 'fleece', 'down', 'heavy']):
                weather_warning = f"\n\nNote: Your selected {item_name} may cause overheating in {temp}°F {condition} weather, but we've included it as requested."
            elif temp <= 40 and any(type_check in item_type for type_check in ['swimwear', 'tank', 'shorts']):
                weather_warning = f"\n\nNote: Your selected {item_name} may not provide adequate warmth for {temp}°F {condition} conditions, but we've included it as requested."
            elif ('rain' in condition or 'storm' in condition) and any(mat in material for mat in ['silk', 'suede', 'velvet']):
                weather_warning = f"\n\nNote: Your selected {item_name} may be damaged by {condition} conditions, but we've included it as requested."
            elif ('rain' in condition or 'storm' in condition) and 'white' in color:
                weather_warning = f"\n\nNote: Your selected {item_name} may be prone to staining in {condition} conditions - consider care when wearing, but we've included it as requested."
            else:
                weather_warning = f"\n\nNote: Your selected {item_name} may not be ideal for current weather conditions ({temp}°F, {condition}), but we've included it as requested."
            
            outfit['reasoning'] = current_reasoning + weather_warning
    
    # Ensure items array exists
    if 'items' not in outfit:
        outfit['items'] = []
    
    # Remove any existing base item to prevent duplicates
    outfit['items'] = [item for item in outfit['items'] if item.get('id') != base_item_id]
    
    # Insert base item at the beginning
    outfit['items'].insert(0, base_item)
    
    logger.info(f"✅ Base item {(base_item.get('name', 'unnamed') if base_item else 'unnamed')} guaranteed in outfit")
    return outfit


def _pick_any_item_safe(wardrobe: List[Dict[str, Any]], category: str, occasion: str) -> Dict[str, Any]:
    """Pick any item safely with occasion-aware filtering to prevent validation failures."""
    # Map category to item types
    category_types = {
        'tops': ['shirt', 'blouse', 't-shirt', 'top', 'tank', 'sweater', 'hoodie', 'sweatshirt'],
        'bottoms': ['pants', 'jeans', 'shorts', 'skirt', 'bottom', 'leggings', 'joggers', 'sweatpants'],
        'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'athletic shoes'],
        'outerwear': ['jacket', 'outerwear', 'blazer', 'cardigan', 'hoodie', 'zip-up', 'track jacket']
    }
    
    # Get candidates for this category
    candidates = [item for item in wardrobe if item.get('type', '').lower() in (category_types.get(category, []) if category_types else [])]
    
    # Apply occasion-aware filtering
    occasion_lower = occasion.lower()
    
    if 'athletic' in occasion_lower or 'gym' in occasion_lower or 'workout' in occasion_lower:
        # For athletic occasions, prefer athletic items
        if category == 'shoes':
            candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['sneaker', 'athletic', 'sport', 'gym', 'workout'])]
        elif category == 'tops':
            candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['athletic', 'sport', 'gym', 'workout', 'jersey', 'tank'])]
        elif category == 'bottoms':
            candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['athletic', 'sport', 'gym', 'workout', 'shorts', 'joggers'])]
        elif category == 'outerwear':
            # Exclude formal jackets for athletic occasions
            candidates = [item for item in candidates if not any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['blazer', 'suit', 'dress', 'formal'])]
    
    elif 'business' in occasion_lower or 'formal' in occasion_lower or 'interview' in occasion_lower:
        # For formal occasions, prefer formal items
        if category == 'shoes':
            candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress shoe', 'oxford', 'loafer', 'derby', 'wingtip', 'brogue'])]
        elif category == 'tops':
            candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress shirt', 'button down', 'button-up', 'blazer', 'suit jacket'])]
        elif category == 'bottoms':
            candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress pant', 'suit pant', 'trouser', 'slack', 'formal pant'])]
        elif category == 'outerwear':
            candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['blazer', 'suit jacket', 'sport coat'])]
    
    # If no candidates after filtering, fall back to any item in wardrobe
    if not candidates:
        logger.warning(f"🚨 EMERGENCY FILTER: No {category} candidates for {occasion}, using any item from wardrobe")
        return random.choice(wardrobe) if wardrobe else None
    
    return random.choice(candidates)


def _force_minimum_outfit(suitable_items: List[Dict[str, Any]], occasion: str, style: str) -> List[Dict[str, Any]]:
    """Force creation of a minimum viable outfit when validation fails but suitable items exist."""
    logger.info(f"🔧 FORCE MINIMUM: Creating outfit from {len(suitable_items)} suitable items")
    
    minimum_outfit = []
    essential_categories = ["tops", "bottoms", "shoes"]
    
    # Try to get one item from each essential category
    for category in essential_categories:
        category_items = [item for item in suitable_items if item.get('type', '').lower() == category]
        if category_items:
            # Take the first item from this category
            minimum_outfit.append(category_items[0])
            logger.info(f"🔧 FORCE MINIMUM: Added {category}: {category_items[0].get('name', 'Unknown')}")
        else:
            logger.warning(f"⚠️ FORCE MINIMUM: No {category} found in suitable items")
    
    # If we still don't have enough items, add any remaining suitable items
    while len(minimum_outfit) < 3 and len(minimum_outfit) < len(suitable_items):
        remaining_items = [item for item in suitable_items if item not in minimum_outfit]
        if remaining_items:
            minimum_outfit.append(remaining_items[0])
            logger.info(f"🔧 FORCE MINIMUM: Added additional item: {remaining_items[0].get('name', 'Unknown')}")
        else:
            break
    
    logger.info(f"🔧 FORCE MINIMUM: Created outfit with {len(minimum_outfit)} items")
    return minimum_outfit


def _select_priority_item(items: List[Dict[str, Any]], occasion: str, style: str, category: str) -> Dict[str, Any]:
    """Select the highest priority item for the given occasion and category."""
    if not items:
        return None
    
    occasion_lower = occasion.lower()
    
    # Score items based on priority for formal occasions
    scored_items = []
    for item in items:
        score = 50.0  # Base score
        item_name = (item.get('name', '') if item else '').lower()
        item_type = (item.get('type', '') if item else '').lower()
        
        # COMPREHENSIVE: Occasion-based prioritization for ALL occasions
        # FORMAL OCCASIONS (Business, Formal, Interview)
        if any(formal_term in occasion_lower for formal_term in ['formal', 'business', 'interview']):
            # Prioritize formal shoes (dress shoes, oxfords, loafers)
            if category == 'shoes' and any(formal_shoe in item_name or formal_shoe in item_type for formal_shoe in [
                'dress shoe', 'oxford', 'loafer', 'derby', 'wingtip', 'brogue', 'dress boot'
            ]):
                score += 100.0  # MASSIVE priority for formal shoes
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal shoes: {item_name}")
            
            # Prioritize formal tops (dress shirts, blazers)
            elif category in ['tops', 'outerwear'] and any(formal_top in item_name or formal_top in item_type for formal_top in [
                'dress shirt', 'button down', 'button-up', 'blazer', 'suit jacket', 'sport coat'
            ]):
                score += 80.0  # High priority for formal tops
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal tops: {item_name}")
            
            # Prioritize formal bottoms (dress pants, suit pants)
            elif category == 'bottoms' and any(formal_bottom in item_name or formal_bottom in item_type for formal_bottom in [
                'dress pant', 'suit pant', 'trouser', 'slack', 'formal pant'
            ]):
                score += 70.0  # High priority for formal bottoms
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal bottoms: {item_name}")
            
            # Penalize casual items on formal occasions
            elif any(casual_term in item_name or casual_term in item_type for casual_term in [
                'sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs',
                't-shirt', 'tank', 'jersey', 'basketball', 'sport', 'hoodie', 'sweatpants'
            ]):
                score -= 50.0  # Heavy penalty for casual items
                logger.info(f"🎯 FALLBACK FORMAL PENALTY: Penalizing casual item: {item_name}")
        
        # ATHLETIC OCCASIONS (Athletic, Gym, Workout, Sport)
        elif any(athletic_term in occasion_lower for athletic_term in ['athletic', 'gym', 'workout', 'sport']):
            # Prioritize athletic items
            if any(athletic_term in item_name or athletic_term in item_type for athletic_term in [
                'sneaker', 'athletic', 'sport', 'gym', 'workout', 'jersey', 'tank', 'shorts'
            ]):
                score += 60.0  # High priority for athletic items
                logger.info(f"🎯 FALLBACK ATHLETIC: Boosting athletic item: {item_name}")
            
            # Penalize formal items on athletic occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'blazer', 'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 40.0  # Penalty for formal items
                logger.info(f"🎯 FALLBACK ATHLETIC PENALTY: Penalizing formal item: {item_name}")
        
        # PARTY OCCASIONS (Party, Night Out, Club)
        elif any(party_term in occasion_lower for party_term in ['party', 'night out', 'club']):
            # Prioritize stylish/trendy items
            if any(party_term in item_name or party_term in item_type for party_term in [
                'party', 'dress', 'blouse', 'top', 'heels', 'boot', 'jacket', 'blazer'
            ]):
                score += 50.0  # High priority for party items
                logger.info(f"🎯 FALLBACK PARTY: Boosting party item: {item_name}")
            
            # Penalize work/athletic items on party occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'work', 'business', 'professional', 'athletic', 'gym', 'sport', 'sweatpants'
            ]):
                score -= 30.0  # Penalty for inappropriate items
                logger.info(f"🎯 FALLBACK PARTY PENALTY: Penalizing inappropriate item: {item_name}")
        
        # DATE OCCASIONS (Date, Romantic)
        elif any(date_term in occasion_lower for date_term in ['date', 'romantic']):
            # Prioritize elegant/romantic items
            if any(date_term in item_name or date_term in item_type for date_term in [
                'dress', 'blouse', 'button down', 'blazer', 'jacket', 'heels', 'boot'
            ]):
                score += 45.0  # High priority for date items
                logger.info(f"🎯 FALLBACK DATE: Boosting date item: {item_name}")
            
            # Penalize athletic/casual items on date occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'athletic', 'gym', 'sport', 'sweatpants', 'hoodie', 'sneaker', 'canvas'
            ]):
                score -= 35.0  # Penalty for inappropriate items
                logger.info(f"🎯 FALLBACK DATE PENALTY: Penalizing inappropriate item: {item_name}")
        
        # WEEKEND OCCASIONS (Weekend, Casual)
        elif any(weekend_term in occasion_lower for weekend_term in ['weekend', 'casual']):
            # Prioritize casual/comfortable items
            if any(weekend_term in item_name or weekend_term in item_type for weekend_term in [
                'casual', 'jeans', 'sneaker', 't-shirt', 'sweater', 'hoodie', 'jacket'
            ]):
                score += 40.0  # High priority for weekend items
                logger.info(f"🎯 FALLBACK WEEKEND: Boosting weekend item: {item_name}")
            
            # Penalize formal items on weekend occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 25.0  # Penalty for formal items
                logger.info(f"🎯 FALLBACK WEEKEND PENALTY: Penalizing formal item: {item_name}")
        
        # LOUNGEWEAR OCCASIONS (Loungewear, Relaxed)
        elif any(lounge_term in occasion_lower for lounge_term in ['loungewear', 'relaxed', 'lounge']):
            # Prioritize comfortable/loungewear items
            if any(lounge_term in item_name or lounge_term in item_type for lounge_term in [
                'sweat', 'hoodie', 't-shirt', 'jogger', 'lounge', 'pajama', 'comfortable', 'soft'
            ]):
                score += 50.0  # High priority for loungewear items
                logger.info(f"🎯 FALLBACK LOUNGE: Boosting loungewear item: {item_name}")
            
            # Penalize formal items on loungewear occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'suit', 'dress', 'blazer', 'oxford', 'heels', 'dress pant'
            ]):
                score -= 40.0  # Penalty for formal items
                logger.info(f"🎯 FALLBACK LOUNGE PENALTY: Penalizing formal item: {item_name}")
        
        scored_items.append((item, score))
    
    # Sort by score (highest first) and return top item
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    if scored_items:
        top_item = scored_items[0][0]
        top_score = scored_items[0][1]
        logger.info(f"🎯 FALLBACK PRIORITY: Selected {top_item.get('name', 'Unknown')} with score {top_score:.1f}")
        return top_item
    
    # Fallback: return first item if scoring failed
    return items[0] if items else None

