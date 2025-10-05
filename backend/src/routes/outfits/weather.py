"""
Weather-related functions for outfit generation and management.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def check_item_weather_appropriateness(item: Dict[str, Any], weather_data: Dict[str, Any]) -> bool:
    """Check if an item is appropriate for the current weather conditions."""
    try:
        temperature = float((weather_data.get('temperature', 70) if weather_data else 70))
        condition = str(weather_data.get('condition', '') if weather_data else '').lower()
        
        item_type = str(item.get('type', '') if item else '').lower()
        item_name = str(item.get('name', '') if item else '').lower()
        
        # Get material from metadata if available
        material = ""
        metadata = (item.get('metadata', {}) if item else {})
        if isinstance(metadata, dict):
            visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
            if isinstance(visual_attrs, dict):
                material = str(visual_attrs.get('material', '') if visual_attrs else '').lower()
        
        # Hot weather checks (85°F+)
        if temperature >= 85:
            exclude_materials = ['wool', 'fleece', 'thick', 'heavy', 'winter', 'cashmere']
            exclude_types = ['coat', 'jacket', 'sweater', 'hoodie', 'thermal']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
        
        # Cold weather checks (40°F and below)
        elif temperature <= 40:
            exclude_materials = ['linen', 'light cotton', 'mesh', 'silk']
            exclude_types = ['tank top', 'sleeveless', 'shorts', 'sandals']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
        
        # Rain/storm checks
        if ('rain' in condition or 'storm' in condition or 'thunderstorm' in condition or 
        (weather_data.get('precipitation', 0) if weather_data else 0) > 50):
            delicate_materials = ['silk', 'suede', 'velvet', 'linen']
            if material and any(mat in material for mat in delicate_materials):
                return False
        
        return True
        
    except Exception as e:
        logger.warning(f"Error checking weather appropriateness: {e}")
        return True  # Default to appropriate if check fails


def attach_weather_context_to_items(items: List, weather_data: Dict[str, Any]) -> List:
    """Attach weather context and appropriateness analysis to each item."""
    try:
        if not weather_data or not items:
            return items
            
        temp = (weather_data.get('temperature', 70) if weather_data else 70)
        condition = (weather_data.get('condition', 'clear') if weather_data else 'clear').lower()
        precipitation = (weather_data.get('precipitation', 0) if weather_data else 0)
        
        enhanced_items = []
        for item in items:
            # Handle both dict and Pydantic ClothingItem objects
            if hasattr(item, 'dict'):  # Pydantic object
                enhanced_item = item.dict()
                item_type = getattr(item, 'type', '').lower()
                item_name = getattr(item, 'name', '').lower()
                material = ""
                metadata = getattr(item, 'metadata', {})
                if hasattr(metadata, 'dict'):  # Pydantic metadata
                    metadata = metadata.dict()
                if isinstance(metadata, dict):
                    visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                    if isinstance(visual_attrs, dict):
                        material = str(visual_attrs.get('material', '') if visual_attrs else '').lower()
                color = getattr(item, 'color', '').title()
            else:  # Dictionary
                enhanced_item = item.copy()
                item_type = str(item.get('type', '') if item else '').lower()
                item_name = str(item.get('name', '') if item else '').lower()
                material = ""
                metadata = (item.get('metadata', {}) if item else {})
                if isinstance(metadata, dict):
                    visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                    if isinstance(visual_attrs, dict):
                        material = str(visual_attrs.get('material', '') if visual_attrs else '').lower()
                color = (item.get('color', '') if item else '').title()
            
            # Temperature appropriateness analysis
            temp_appropriateness = "excellent"
            temp_note = ""
                
            if temp >= 85:  # Very hot weather
                if any(heavy in item_name for heavy in ['heavy', 'winter', 'thick', 'wool', 'fleece', 'thermal']):
                    temp_appropriateness = "too warm"
                    temp_note = f"may be too warm for {temp}°F weather"
                elif 'shorts' in item_type or 'tank' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"perfect for {temp}°F hot weather"
                elif 'cotton' in material or 'linen' in material:
                    temp_appropriateness = "excellent"
                    temp_note = f"breathable fabric ideal for {temp}°F weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"suitable for {temp}°F warm weather"
                        
            elif temp >= 75:  # Warm weather
                if 'shorts' in item_type or 'tank' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"comfortable for {temp}°F warm weather"
                elif any(heavy in item_name for heavy in ['heavy', 'winter', 'thick']):
                    temp_appropriateness = "borderline"
                    temp_note = f"may be warm for {temp}°F weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"appropriate for {temp}°F warm weather"
                        
            elif temp >= 65:  # Mild weather
                temp_appropriateness = "excellent"
                temp_note = f"ideal for {temp}°F mild weather"
                    
            elif temp >= 55:  # Cool weather
                if 'shorts' in item_type:
                    temp_appropriateness = "borderline"
                    temp_note = f"may be cool for {temp}°F weather"
                elif 'sweater' in item_type or 'jacket' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"perfect for {temp}°F cool weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"suitable for {temp}°F cool weather"
                        
            else:  # Cold weather
                if any(cool in item_type for cool in ['shorts', 'tank', 'sleeveless']):
                    temp_appropriateness = "inappropriate"
                    temp_note = f"inadequate for {temp}°F cold weather"
                elif any(warm in item_name for warm in ['heavy', 'winter', 'wool', 'fleece']):
                    temp_appropriateness = "excellent"
                    temp_note = f"ideal for {temp}°F cold weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"appropriate for {temp}°F cold weather"
            
            # Fabric and condition analysis
            fabric_note = ""
            if 'rain' in condition or precipitation > 50:
                if any(delicate in material for delicate in ['silk', 'suede', 'velvet', 'linen']):
                    fabric_note = f"Note: {material} fabric may not be ideal for wet conditions"
                elif any(water_resistant in material for water_resistant in ['nylon', 'polyester', 'gore-tex']):
                    fabric_note = f"Excellent: {material} provides good water resistance"
                    
            # Style and occasion analysis
            style_note = ""
            if item_type in ['dress', 'blazer', 'suit']:
                style_note = "professional and versatile"
            elif item_type in ['jeans', 'denim']:
                style_note = "casual and comfortable"
            elif item_type in ['sweater', 'cardigan']:
                style_note = "cozy and layered"
            elif item_type in ['shirt', 'blouse']:
                style_note = "classic and adaptable"
            
            # Attach weather context
            enhanced_item['weather_context'] = {
                'temperature_appropriateness': temp_appropriateness,
                'temperature_note': temp_note,
                'fabric_note': fabric_note,
                'style_note': style_note,
                'color': color,
                'overall_suitability': temp_appropriateness
            }
            
            enhanced_items.append(enhanced_item)
            
        return enhanced_items
        
    except Exception as e:
        logger.warning(f"Error attaching weather context to items: {e}")
        return items


# Note: Additional weather functions like generate_weather_aware_fallback_reasoning 
# and validate_weather_outfit_combinations will be extracted in a separate step
# to keep this file manageable.
