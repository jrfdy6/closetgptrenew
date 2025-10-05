"""
Core outfit generation logic.
"""

import logging
from typing import Dict, List, Any, Optional
from .weather import check_item_weather_appropriateness

logger = logging.getLogger(__name__)


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
            condition = str(weather_data.get('condition', '') if weather_data else '').lower()
            item_name = (base_item.get('name', 'item') if base_item else 'item')
            
            # Get item details for specific warnings
            item_type = str(base_item.get('type', '') if base_item else '').lower()
            metadata = (base_item.get('metadata', {}) if base_item else {})
            material = ""
            color = ""
            if isinstance(metadata, dict):
                visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                if isinstance(visual_attrs, dict):
                    material = str(visual_attrs.get('material', '') if visual_attrs else '').lower()
                    color = str(visual_attrs.get('color', '') if visual_attrs else '').lower()
            
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


# Note: The main generate_outfit_logic function is very large (500+ lines) and will be extracted 
# in a separate step to keep this file manageable. It includes the core outfit generation 
# logic with robust service integration, validation, and fallback strategies.
