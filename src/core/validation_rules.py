"""
Dynamic validation rules store for Easy Outfit App
This module provides a simple in-memory store that can be updated live
and persists to Firestore for durability.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
from firebase_admin import firestore
from ..config import firebase  # Import Firebase config to initialize it
from .logging import get_logger

logger = logging.getLogger(__name__)

def classify_layer(item) -> str:
    """Classify a layer item as light, medium, or heavy based on its properties."""
    if not hasattr(item, 'type') or not item.type:
        return "unknown"
    
    item_type = item.type.lower()
    material = getattr(item, 'material', '').lower() if hasattr(item, 'material') else ''
    
    # Heavy layers
    heavy_indicators = ['coat', 'jacket', 'blazer', 'sweater', 'cardigan']
    if any(indicator in item_type for indicator in heavy_indicators):
        return "heavy_layer"
    
    # Medium layers
    medium_indicators = ['shirt', 'blouse', 't-shirt', 'tshirt', 'tee']
    if any(indicator in item_type for indicator in medium_indicators):
        return "medium_layer"
    
    # Light layers
    light_indicators = ['tank', 'camisole', 'undershirt', 'sleeveless']
    if any(indicator in item_type for indicator in light_indicators):
        return "light_layer"
    
    # Material-based classification
    heavy_materials = ['wool', 'fleece', 'cashmere', 'thick_cotton']
    if any(mat in material for mat in heavy_materials):
        return "heavy_layer"
    
    light_materials = ['silk', 'linen', 'thin_cotton']
    if any(mat in material for mat in light_materials):
        return "light_layer"
    
    return "medium_layer"

def get_temp_threshold_for_layer(layer_type: str) -> float:
    """Get the maximum temperature threshold for a layer type."""
    thresholds = {
        "heavy_layer": 45.0,  # Heavy layers too warm above 45°F
        "medium_layer": 75.0,  # Medium layers too warm above 75°F
        "light_layer": 85.0,   # Light layers too warm above 85°F
        "unknown": 70.0        # Default threshold
    }
    return thresholds.get(layer_type, 70.0)

def validate_layering(items, temperature: float, style: str) -> List[dict]:
    """
    Validate layering rules for an outfit.
    
    Args:
        items: List of clothing items
        temperature: Current temperature in Fahrenheit
        style: Target style for the outfit
        
    Returns:
        List of validation errors
    """
    errors = []

    # Ensure temperature is a float
    if isinstance(temperature, str):
        try:
            temperature = float(temperature)
        except (ValueError, TypeError):
            temperature = 70.0
    elif temperature is None:
        temperature = 70.0

    # Define layering styles that allow multiple layers
    layering_styles = ["y2k", "avant-garde", "streetwear", "grunge", "techwear"]
    allow_multiple_layers = style.lower() in layering_styles

    # Get layer items and classify them
    layer_items = [i for i in items if hasattr(i, 'category') and i.category == "layer"]
    if not layer_items:
        # If no explicit layer category, try to identify layers by type
        layer_types = ['shirt', 'sweater', 'jacket', 'coat', 'blazer', 'cardigan', 't-shirt', 'blouse']
        layer_items = [i for i in items if hasattr(i, 'type') and i.type.lower() in layer_types]
    
    heavy_layers = [i for i in layer_items if classify_layer(i) == "heavy_layer"]

    # Check each layer for temperature appropriateness
    for layer in layer_items:
        layer_type = classify_layer(layer)
        max_temp = get_temp_threshold_for_layer(layer_type)

        if temperature > max_temp:
            errors.append({
                "type": "layering_temp_violation",
                "item_id": getattr(layer, 'id', None),
                "reason": f"{getattr(layer, 'name', 'Unknown item')} is too warm for {temperature}°F"
            })

    # Check for too many heavy layers in warm weather
    if len(heavy_layers) > 1 and temperature > 35 and not allow_multiple_layers:
        errors.append({
            "type": "layering_heavy_conflict",
            "reason": "Too many heavy layers for the current weather."
        })

    # Check for multiple layers when style doesn't support it
    if len(layer_items) > 1 and not allow_multiple_layers:
        errors.append({
            "type": "layering_style_conflict",
            "reason": f"Style '{style}' doesn't support multiple layers."
        })

    return errors

class ValidationRuleStore:
    """Dynamic validation rules store that can be updated live."""
    
    def __init__(self):
        self.db = firestore.client()
        self.rules_collection = self.db.collection('validation_rules')
        self._rules_cache = {}
        self._last_loaded = 0
        self._cache_ttl = 60  # Cache for 60 seconds
        
    def _load_rules_from_firestore(self) -> Dict[str, Any]:
        """Load rules from Firestore."""
        try:
            rules_doc = self.rules_collection.document('current').get()
            if rules_doc.exists:
                return rules_doc.to_dict()
            else:
                # Initialize with default rules
                default_rules = self._get_default_rules()
                self._save_rules_to_firestore(default_rules)
                return default_rules
        except Exception as e:
            logger.error(f"Error loading rules from Firestore: {e}")
            return self._get_default_rules()
    
    def _save_rules_to_firestore(self, rules: Dict[str, Any]) -> None:
        """Save rules to Firestore."""
        try:
            self.rules_collection.document('current').set(rules)
            logger.info("Validation rules saved to Firestore")
        except Exception as e:
            logger.error(f"Error saving rules to Firestore: {e}")
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default validation rules."""
        return {
            "material_climate_rules": {
                "wool": {"max_temp_f": 75, "min_temp_f": 32},
                "fleece": {"max_temp_f": 70, "min_temp_f": 40},
                "leather": {"max_temp_f": 85, "min_temp_f": 45},
                "denim": {"max_temp_f": 90, "min_temp_f": 50},
                "cotton": {"max_temp_f": 95, "min_temp_f": 60},
                "linen": {"max_temp_f": 100, "min_temp_f": 70},
                "silk": {"max_temp_f": 85, "min_temp_f": 60}
            },
            "seasonal_rules": {
                "winter": {"months": [12, 1, 2], "min_temp_f": 32},
                "spring": {"months": [3, 4, 5], "min_temp_f": 45},
                "summer": {"months": [6, 7, 8], "min_temp_f": 70},
                "fall": {"months": [9, 10, 11], "min_temp_f": 50}
            },
            "occasion_rules": {
                "formal": {"min_items": 2, "requires_jacket": True},
                "casual": {"min_items": 1, "requires_jacket": False},
                "business": {"min_items": 2, "requires_jacket": True},
                "athletic": {"min_items": 1, "requires_jacket": False}
            },
            "layering_rules": {
                "max_layers": 4,
                "min_layers_cold": 2,
                "max_layers_hot": 1
            },
            "color_rules": {
                "max_colors": 4,
                "require_neutral_base": True,
                "allow_patterns": True
            },
            "metadata": {
                "version": "1.0.0",
                "last_updated": int(time.time()),
                "created_at": int(time.time())
            }
        }
    
    def get_rules(self) -> Dict[str, Any]:
        """Get current validation rules (with caching)."""
        current_time = time.time()
        
        # Check if cache is still valid
        if current_time - self._last_loaded < self._cache_ttl and self._rules_cache:
            return self._rules_cache.copy()
        
        # Load from Firestore
        rules = self._load_rules_from_firestore()
        self._rules_cache = rules.copy()
        self._last_loaded = current_time
        
        return rules
    
    def update_rule(self, rule_path: str, new_value: Any) -> bool:
        """
        Update a specific rule.
        
        Args:
            rule_path: Dot-separated path to the rule (e.g., "material_climate_rules.wool.max_temp_f")
            new_value: New value for the rule
            
        Returns:
            bool: True if update was successful
        """
        try:
            rules = self.get_rules()
            
            # Navigate to the rule path
            path_parts = rule_path.split('.')
            current = rules
            
            # Navigate to parent of target
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Update the value
            current[path_parts[-1]] = new_value
            
            # Update metadata
            rules['metadata']['last_updated'] = int(time.time())
            rules['metadata']['version'] = self._increment_version(rules['metadata']['version'])
            
            # Save to Firestore
            self._save_rules_to_firestore(rules)
            
            # Update cache
            self._rules_cache = rules.copy()
            self._last_loaded = time.time()
            
            logger.info(f"Updated rule {rule_path} to {new_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rule {rule_path}: {e}")
            return False
    
    def add_material_rule(self, material: str, max_temp: int, min_temp: int) -> bool:
        """Add a new material climate rule."""
        return self.update_rule(f"material_climate_rules.{material}", {
            "max_temp_f": max_temp,
            "min_temp_f": min_temp
        })
    
    def remove_material_rule(self, material: str) -> bool:
        """Remove a material climate rule."""
        try:
            rules = self.get_rules()
            if material in rules.get('material_climate_rules', {}):
                del rules['material_climate_rules'][material]
                rules['metadata']['last_updated'] = int(time.time())
                rules['metadata']['version'] = self._increment_version(rules['metadata']['version'])
                
                self._save_rules_to_firestore(rules)
                self._rules_cache = rules.copy()
                self._last_loaded = time.time()
                
                logger.info(f"Removed material rule for {material}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing material rule for {material}: {e}")
            return False
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version string (simple implementation)."""
        try:
            parts = current_version.split('.')
            if len(parts) >= 3:
                patch = int(parts[2]) + 1
                return f"{parts[0]}.{parts[1]}.{patch}"
            return f"{current_version}.1"
        except:
            return f"{current_version}.1"
    
    def get_rule_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of rule changes."""
        try:
            history_ref = self.rules_collection.document('history').collection('changes')
            changes = history_ref.order_by('timestamp', direction='DESCENDING').limit(limit).stream()
            
            history = []
            for change in changes:
                history.append(change.to_dict())
            
            return history
        except Exception as e:
            logger.error(f"Error getting rule history: {e}")
            return []
    
    def log_rule_change(self, rule_path: str, old_value: Any, new_value: Any, user_id: str = "system") -> None:
        """Log a rule change to the history collection."""
        try:
            change_doc = {
                "rule_path": rule_path,
                "old_value": old_value,
                "new_value": new_value,
                "user_id": user_id,
                "timestamp": int(time.time())
            }
            
            self.rules_collection.document('history').collection('changes').add(change_doc)
            logger.info(f"Logged rule change: {rule_path} from {old_value} to {new_value}")
        except Exception as e:
            logger.error(f"Error logging rule change: {e}")
    
    def generate_fixable_suggestion(self, error_type: str, error_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a fixable suggestion for a validation error.
        
        Args:
            error_type: Type of validation error
            error_details: Details about the error
            
        Returns:
            Optional fix suggestion with rule_type, path, and new_value
        """
        try:
            if error_type == "material_climate_mismatch":
                # Extract material and temperature from error
                material = error_details.get("material", "").lower()
                temperature = error_details.get("temperature", 70)
                
                # Ensure temperature is a float
                if isinstance(temperature, str):
                    try:
                        temperature = float(temperature)
                    except (ValueError, TypeError):
                        temperature = 70.0
                elif temperature is None:
                    temperature = 70.0
                
                if material and material in self.get_rules().get("material_climate_rules", {}):
                    current_rule = self.get_rules()["material_climate_rules"][material]
                    current_max = current_rule.get("max_temp_f", 85)
                    
                    # Suggest increasing max temperature if item is too hot for current temp
                    if temperature > current_max:
                        return {
                            "rule_type": "material_climate",
                            "rule_path": f"material_climate_rules.{material}.max_temp_f",
                            "current_value": current_max,
                            "suggested_value": min(temperature + 5, 100),  # Cap at 100°F
                            "reason": f"Increase {material} max temperature from {current_max}°F to accommodate {temperature}°F weather",
                            "fixable": True
                        }
                    
                    # Suggest decreasing min temperature if item is too cold for current temp
                    current_min = current_rule.get("min_temp_f", 50)
                    if temperature < current_min:
                        return {
                            "rule_type": "material_climate",
                            "rule_path": f"material_climate_rules.{material}.min_temp_f",
                            "current_value": current_min,
                            "suggested_value": max(temperature - 5, 20),  # Floor at 20°F
                            "reason": f"Decrease {material} min temperature from {current_min}°F to accommodate {temperature}°F weather",
                            "fixable": True
                        }
            
            elif error_type == "layering_compliance":
                # Suggest adjusting layering rules
                missing_layers = error_details.get("missing_layers", 0)
                temperature = error_details.get("temperature", 70)
                
                # Ensure temperature is a float
                if isinstance(temperature, str):
                    try:
                        temperature = float(temperature)
                    except (ValueError, TypeError):
                        temperature = 70.0
                elif temperature is None:
                    temperature = 70.0
                
                if missing_layers > 0:
                    return {
                        "rule_type": "layering",
                        "rule_path": "layering_rules.min_layers_cold",
                        "current_value": self.get_rules().get("layering_rules", {}).get("min_layers_cold", 2),
                        "suggested_value": max(1, missing_layers - 1),
                        "reason": f"Reduce minimum layers requirement for {temperature}°F weather",
                        "fixable": True
                    }
            
            elif error_type == "low_occasion_appropriateness":
                # Suggest adjusting occasion appropriateness threshold
                score = error_details.get("score", 0.5)
                occasion = error_details.get("occasion", "unknown")
                
                if score < 0.3:
                    return {
                        "rule_type": "occasion_threshold",
                        "rule_path": "occasion_appropriateness_threshold",
                        "current_value": 0.3,
                        "suggested_value": max(0.1, score - 0.1),
                        "reason": f"Lower occasion appropriateness threshold for '{occasion}' to accommodate current scoring",
                        "fixable": True
                    }
            
            elif error_type == "low_weather_appropriateness":
                # Suggest adjusting weather thresholds
                score = error_details.get("score", 0.5)
                temperature = error_details.get("temperature", 70)
                
                if score < 0.4:
                    return {
                        "rule_type": "weather_threshold",
                        "rule_path": "weather_appropriateness_threshold",
                        "current_value": 0.4,
                        "suggested_value": max(0.2, score - 0.1),
                        "reason": f"Lower weather appropriateness threshold to accommodate current scoring",
                        "fixable": True
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating fixable suggestion: {e}")
            return None
    
    def apply_fix(self, fix_suggestion: Dict[str, Any], user_id: str = "system") -> bool:
        """
        Apply a fix suggestion to the validation rules.
        
        Args:
            fix_suggestion: The fix suggestion from generate_fixable_suggestion
            user_id: ID of user applying the fix
            
        Returns:
            bool: True if fix was applied successfully
        """
        try:
            rule_path = fix_suggestion.get("rule_path")
            new_value = fix_suggestion.get("suggested_value")
            
            if not rule_path or new_value is None:
                logger.error("Invalid fix suggestion: missing rule_path or suggested_value")
                return False
            
            # Get current value for logging
            rules = self.get_rules()
            current_value = None
            
            # Navigate to current value
            path_parts = rule_path.split('.')
            current = rules
            for part in path_parts[:-1]:
                if part in current:
                    current = current[part]
                else:
                    break
            else:
                current_value = current.get(path_parts[-1])
            
            # Apply the fix
            success = self.update_rule(rule_path, new_value)
            
            if success:
                # Log the fix
                self.log_rule_change(
                    rule_path=rule_path,
                    old_value=current_value,
                    new_value=new_value,
                    user_id=user_id
                )
                
                logger.info(f"Applied fix: {rule_path} = {new_value} (was {current_value})")
                return True
            else:
                logger.error(f"Failed to apply fix: {rule_path} = {new_value}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying fix: {e}")
            return False

# Global instance
validation_rules = ValidationRuleStore()
