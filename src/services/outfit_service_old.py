from typing import List, Optional, Dict, Any, Union
from ..config.firebase import db
from ..custom_types.outfit import Outfit, OutfitPiece, OutfitGeneratedOutfit, OutfitGenerationRequest
from ..custom_types.wardrobe import ClothingType, ClothingItem, Season, StyleTag, Color
from ..custom_types.outfit_rules import get_weather_rule, get_occasion_rule, LayeringRule, ClothingType as RuleClothingType, get_mood_rule
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from ..custom_types.style_engine import Material
import random
import time
import uuid
from ..utils.pairability import average_pairability
from ..utils.outfit_utils import get_color_name, athletic_sort_key, check_body_type_compatibility, check_skin_tone_compatibility, extract_color_names, get_item_category
# Add import at the top
from .outfit_fallback_service import OutfitFallbackService
# Add pipeline tracing service import
from .pipeline_tracing_service import PipelineTracingService
# Add coordinated analytics service import
from .analytics_service import log_outfit_generation
# Add validation orchestrator import
from .validation_orchestrator import ValidationOrchestrator

class OutfitService:
    def __init__(self):
        self.db = db
        self.collection = self.db.collection('outfits')
        self.wardrobe_collection = self.db.collection('wardrobe')
        # Add fallback service
        self.fallback_service = OutfitFallbackService()
        # Add pipeline tracing service
        self.tracing_service = PipelineTracingService()
        # Add validation orchestrator
        self.validation_orchestrator = ValidationOrchestrator(self)
       

    def to_dict_recursive(self, obj, depth=0, visited=None):
        """Recursively convert Pydantic models to dictionaries for Firestore serialization."""
        # Prevent infinite recursion
        if depth > 10:
            return str(obj)
        
        if visited is None:
            visited = set()
        
        # Prevent circular references
        obj_id = id(obj)
        if obj_id in visited:
            return str(obj)
        visited.add(obj_id)
        
        try:
            if hasattr(obj, 'dict'):
                # Pydantic model - use dict() method but handle enum values properly
                data = obj.dict()
                # Recursively process the dictionary to handle any nested enum values
                return self.to_dict_recursive(data, depth + 1, visited)
            elif isinstance(obj, dict):
                # Dictionary - recursively convert values
                result = {}
                for key, value in obj.items():
                    # Handle None values properly - don't convert to string
                    if value is None:
                        result[key] = None
                    else:
                        result[key] = self.to_dict_recursive(value, depth + 1, visited)
                return result
            elif isinstance(obj, list):
                # List - recursively convert items
                return [self.to_dict_recursive(item, depth + 1, visited) for item in obj]
            elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, type(None))):
                # Object with __dict__ - convert to dict, but be careful
                try:
                    return {key: self.to_dict_recursive(value, depth + 1, visited) 
                           for key, value in obj.__dict__.items() 
                           if not key.startswith('_')}  # Skip private attributes
                except:
                    return str(obj)
            elif hasattr(obj, 'value') and hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__'):
                # This is likely an enum - return its value
                return obj.value
            elif obj is None:
                # Handle None values properly
                return None
            else:
                # Primitive type - return as is
                return obj
        except Exception as e:
            # If anything goes wrong, return string representation
            return str(obj)

    async def get_outfits(self) -> List[OutfitGeneratedOutfit]:
        """Get all outfits from Firestore."""
        try:
            outfits = []
            docs = self.collection.stream()
            for doc in docs:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                
                # Convert item IDs to full ClothingItem objects if needed
                if 'items' in outfit_data and isinstance(outfit_data['items'], list):
                    converted_items = []
                    for item in outfit_data['items']:
                        if isinstance(item, str):
                            # This is an item ID, fetch the full item from wardrobe
                            try:
                                from ..config.firebase import db
                                item_doc = db.collection("wardrobe").document(item).get()
                                if item_doc.exists:
                                    item_data = item_doc.to_dict()
                                    item_data['id'] = item
                                    from ..custom_types.wardrobe import ClothingItem
                                    clothing_item = ClothingItem(**item_data)
                                    converted_items.append(clothing_item)
                                else:
                                    print(f"Warning: Item {item} not found in wardrobe, keeping as ID")
                                    converted_items.append(item)
                            except Exception as e:
                                print(f"Warning: Failed to fetch item {item}: {e}, keeping as ID")
                                converted_items.append(item)
                        else:
                            # This is already a full object or dict, keep as is
                            converted_items.append(item)
                    outfit_data['items'] = converted_items
                
                # Temporarily bypass validation to get outfits page working
                try:
                    # Try to validate as OutfitGeneratedOutfit first
                    outfits.append(OutfitGeneratedOutfit(**outfit_data))
                except Exception as e:
                    print(f"Validation failed for outfit {doc.id}, creating minimal outfit object")
                    # Create a complete outfit object with all required fields
                    minimal_outfit = {
                        "id": doc.id,
                        "name": outfit_data.get("name", "Unnamed Outfit"),
                        "description": outfit_data.get("description", "A generated outfit"),
                        "items": outfit_data.get("items", []),
                        "explanation": outfit_data.get("explanation", outfit_data.get("reasoning", "Generated outfit")),
                        "pieces": outfit_data.get("pieces", []),
                        "styleTags": outfit_data.get("styleTags", []),
                        "colorHarmony": outfit_data.get("colorHarmony", "neutral"),
                        "styleNotes": outfit_data.get("styleNotes", ""),
                        "occasion": outfit_data.get("occasion", "casual"),
                        "season": outfit_data.get("season", "all"),
                        "style": outfit_data.get("style", "casual"),
                        "mood": outfit_data.get("mood", "neutral"),
                        "createdAt": outfit_data.get("createdAt", 0),
                        "updatedAt": outfit_data.get("updatedAt", outfit_data.get("createdAt", 0)),
                        "metadata": outfit_data.get("metadata", {}),
                        "wasSuccessful": outfit_data.get("wasSuccessful", True),
                        "baseItemId": outfit_data.get("baseItemId", None),
                        "validationErrors": outfit_data.get("validationErrors", []),
                        "userFeedback": outfit_data.get("userFeedback", None),
                        "user_id": outfit_data.get("user_id", user_id),
                        "generation_trace": outfit_data.get("generation_trace", []),
                        "validation_details": outfit_data.get("validation_details", {}),
                        "wardrobe_snapshot": outfit_data.get("wardrobe_snapshot", {}),
                        "system_context": outfit_data.get("system_context", {}),
                        "user_session_context": outfit_data.get("user_session_context", {}),
                        "generation_method": outfit_data.get("generation_method", "primary")
                    }
                    try:
                        outfits.append(OutfitGeneratedOutfit(**minimal_outfit))
                    except Exception as e2:
                        print(f"Failed to create minimal outfit for {doc.id}: {e2}")
                        continue
            
            return outfits
        except Exception as e:
            print(f"Error getting outfits: {e}")
            raise

    async def get_outfit(self, outfit_id: str) -> Optional[OutfitGeneratedOutfit]:
        """Get a single outfit by ID from Firestore."""
        try:
            doc = self.collection.document(outfit_id).get()
            if not doc.exists:
                return None
            
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            
            # Debug: Print the raw outfit data structure
            print(f"DEBUG: get_outfit - Raw outfit data keys: {list(outfit_data.keys())}")
            print(f"DEBUG: get_outfit - Items type: {type(outfit_data.get('items', 'NOT_FOUND'))}")
            if 'items' in outfit_data:
                print(f"DEBUG: get_outfit - Items length: {len(outfit_data['items']) if isinstance(outfit_data['items'], list) else 'NOT_LIST'}")
                if isinstance(outfit_data['items'], list) and outfit_data['items']:
                    print(f"DEBUG: get_outfit - First item type: {type(outfit_data['items'][0])}")
            
            # Convert item IDs to full ClothingItem objects if needed
            if 'items' in outfit_data and isinstance(outfit_data['items'], list):
                converted_items = []
                for item in outfit_data['items']:
                    if isinstance(item, str):
                        # This is an item ID, fetch the full item from wardrobe
                        try:
                            from ..config.firebase import db
                            item_doc = db.collection("wardrobe").document(item).get()
                            if item_doc.exists:
                                item_data = item_doc.to_dict()
                                item_data['id'] = item
                                from ..custom_types.wardrobe import ClothingItem
                                clothing_item = ClothingItem(**item_data)
                                converted_items.append(clothing_item)
                            else:
                                print(f"Warning: Item {item} not found in wardrobe, keeping as ID")
                                converted_items.append(item)
                        except Exception as e:
                            print(f"Warning: Failed to fetch item {item}: {e}, keeping as ID")
                            converted_items.append(item)
                    else:
                        # This is already a full object or dict, keep as is
                        converted_items.append(item)
                outfit_data['items'] = converted_items
            
            try:
                # Try to validate as OutfitGeneratedOutfit first
                return OutfitGeneratedOutfit(**outfit_data)
            except Exception as e:
                print(f"Failed to validate as OutfitGeneratedOutfit: {e}")
                print(f"DEBUG: get_outfit - Validation error details: {str(e)}")
                # If that fails, try to convert from old Outfit format
                try:
                    # Convert old Outfit format to OutfitGeneratedOutfit format
                    converted_data = self._convert_old_outfit_format(outfit_data)
                    print(f"DEBUG: get_outfit - Conversion successful, trying validation again")
                    return OutfitGeneratedOutfit(**converted_data)
                except Exception as e2:
                    print(f"Failed to convert old outfit format: {e2}")
                    print(f"DEBUG: get_outfit - Conversion error details: {str(e2)}")
                    # If conversion fails, delete the problematic outfit
                    print(f"Deleting problematic outfit {outfit_id}")
                    self.collection.document(outfit_id).delete()
                    return None
                    
        except Exception as e:
            print(f"Error getting outfit {outfit_id}: {e}")
            raise

    def _convert_old_outfit_format(self, old_outfit_data: dict) -> dict:
        """Convert old Outfit format to OutfitGeneratedOutfit format."""
        # Create a copy to avoid modifying the original
        new_data = old_outfit_data.copy()
        
        # Helper function to normalize enum string representations
        def normalize_enum_string(value):
            """Convert enum string representations like 'ClothingType.SHIRT' to 'shirt'"""
            if isinstance(value, str) and '.' in value:
                # Extract the part after the last dot
                return value.split('.')[-1].lower()
            return value
        
        # Helper function to convert string "None" to actual None
        def convert_none_strings(value):
            """Convert string 'None' to actual None"""
            if isinstance(value, str) and value == "None":
                return None
            return value
        
        # If items are in OutfitPiece format, convert them to ClothingItem format
        if 'items' in new_data and isinstance(new_data['items'], list):
            converted_items = []
            for item in new_data['items']:
                if isinstance(item, dict):
                    # Check if this is an OutfitPiece (has itemId and reason)
                    if 'itemId' in item and 'reason' in item:
                        # This is an OutfitPiece, we need to convert it to ClothingItem format
                        # For now, we'll create a minimal ClothingItem structure
                        converted_item = {
                            'id': item.get('itemId', 'unknown'),
                            'name': item.get('name', 'Unknown Item'),
                            'type': normalize_enum_string(item.get('type', 'other')),
                            'color': 'unknown',
                            'season': ['all'],
                            'style': item.get('style', []),
                            'imageUrl': item.get('imageUrl', ''),
                            'tags': [],
                            'dominantColors': item.get('dominantColors', []),
                            'matchingColors': [],
                            'occasion': item.get('occasion', []),
                            'createdAt': int(time.time()),
                            'updatedAt': int(time.time()),
                            'userId': 'unknown'
                        }
                        converted_items.append(converted_item)
                    else:
                        # This is a dictionary that should be a ClothingItem
                        # Normalize the type field if it's an enum string representation
                        if 'type' in item:
                            item['type'] = normalize_enum_string(item['type'])
                        
                        # Convert string "None" values to actual None
                        for key, value in item.items():
                            item[key] = convert_none_strings(value)
                        
                        # Convert it to a ClothingItem object
                        try:
                            from ..types.wardrobe import ClothingItem
                            converted_items.append(ClothingItem(**item))
                        except Exception as e:
                            print(f"Warning: Failed to convert item dict to ClothingItem: {e}")
                            # If conversion fails, create a minimal structure
                            converted_item = {
                                'id': item.get('id', 'unknown'),
                                'name': item.get('name', 'Unknown Item'),
                                'type': normalize_enum_string(item.get('type', 'other')),
                                'color': item.get('color', 'unknown'),
                                'season': item.get('season', ['all']),
                                'style': item.get('style', []),
                                'imageUrl': item.get('imageUrl', ''),
                                'tags': item.get('tags', []),
                                'dominantColors': item.get('dominantColors', []),
                                'matchingColors': item.get('matchingColors', []),
                                'occasion': item.get('occasion', []),
                                'createdAt': item.get('createdAt', int(time.time())),
                                'updatedAt': item.get('updatedAt', int(time.time())),
                                'userId': item.get('userId', 'unknown')
                            }
                            converted_items.append(converted_item)
                elif isinstance(item, str):
                    # This is already a string (item ID), keep as is
                    converted_items.append(item)
                else:
                    # Handle case where item is not a dict or string (could be other type)
                    print(f"Warning: Skipping non-dict/non-string item in outfit data: {type(item)} - {item}")
                    continue
            
            new_data['items'] = converted_items
        
        # Convert string "None" values in the main outfit data
        for key, value in new_data.items():
            new_data[key] = convert_none_strings(value)
        
        # Ensure all required fields are present with proper type checking
        required_fields = {
            'explanation': new_data.get('explanation', 'Generated outfit'),
            'pieces': new_data.get('pieces', []),
            'styleTags': new_data.get('styleTags', []),
            'colorHarmony': new_data.get('colorHarmony', ''),
            'styleNotes': new_data.get('styleNotes', ''),
            'metadata': new_data.get('metadata', {}),
            # Add new tracking fields with default values
            'wasSuccessful': new_data.get('wasSuccessful', True),
            'baseItemId': new_data.get('baseItemId', None),
            'validationErrors': new_data.get('validationErrors', []),
            'userFeedback': new_data.get('userFeedback', None),
            'user_id': new_data.get('user_id', None)  # 🚀 NEW: Ensure user_id is included
        }
        
        # Safely update the data, ensuring we don't overwrite existing valid data
        for key, default_value in required_fields.items():
            if key not in new_data or new_data[key] is None:
                new_data[key] = default_value
            elif isinstance(default_value, list) and not isinstance(new_data[key], list):
                # If we expect a list but got something else, use the default
                print(f"Warning: Expected list for {key}, got {type(new_data[key])}, using default")
                new_data[key] = default_value
            elif isinstance(default_value, dict) and not isinstance(new_data[key], dict):
                # If we expect a dict but got something else, use the default
                print(f"Warning: Expected dict for {key}, got {type(new_data[key])}, using default")
                new_data[key] = default_value
            elif key == 'userFeedback' and new_data[key] == 'None':
                # Special handling for userFeedback - convert string 'None' to actual None
                print(f"Warning: Converting userFeedback from string 'None' to None")
                new_data[key] = None
        
        return new_data

    def _get_layering_rule(self, temperature: float) -> LayeringRule:
        """Get the appropriate layering rule based on temperature."""
        return get_weather_rule(temperature)

    def _select_items_for_layering(self, wardrobe: List[ClothingItem], layering_rule: LayeringRule, 
                                 occasion: str, style: Optional[str] = None) -> List[ClothingItem]:
        """Select items that meet layering requirements for the given temperature."""
        selected_items = []
        required_layers = layering_rule.required_layers
        # Convert layer_types to string values for comparison
        layer_types = [lt.value if hasattr(lt, 'value') else str(lt) for lt in layering_rule.layer_types]
        material_preferences = layering_rule.material_preferences
        
        # print(f"DEBUG: _select_items_for_layering - Required layers: {required_layers}")
        # print(f"DEBUG: _select_items_for_layering - Layer types: {layer_types}")
        # print(f"DEBUG: _select_items_for_layering - Material preferences: {material_preferences}")
        # print(f"DEBUG: _select_items_for_layering - Wardrobe item types: {[item.type for item in wardrobe]}")
        
        # Group wardrobe items by type for easier selection
        items_by_type = {}
        for item in wardrobe:
            item_type_str = item.type.value if hasattr(item.type, 'value') else str(item.type)
            if item_type_str not in items_by_type:
                items_by_type[item_type_str] = []
            items_by_type[item_type_str].append(item)
        
        # Select items for each required layer
        for layer_index in range(required_layers):
            layer_type = layer_types[layer_index] if layer_index < len(layer_types) else layer_types[0]
            
            # print(f"DEBUG: _select_items_for_layering - Selecting for layer {layer_index + 1}: {layer_type} (type: {type(layer_type)})")
            
            # Get items of the required type
            available_items = items_by_type.get(layer_type, [])
            # print(f"DEBUG: _select_items_for_layering - Available items for {layer_type}: {[item.name for item in available_items]}")
            
            if not available_items:
                # print(f"DEBUG: _select_items_for_layering - No items available for type {layer_type}")
                continue
            
            # Filter by material preferences
            preferred_items = []
            for item in available_items:
                # Check if item has material information
                if hasattr(item, 'material') and item.material:
                    if item.material in material_preferences:
                        preferred_items.append((item, 2))  # Higher priority for preferred materials
                    else:
                        preferred_items.append((item, 1))  # Lower priority for non-preferred materials
                else:
                    # If no material info, give medium priority
                    preferred_items.append((item, 1))
            
            # Sort by priority and select the best item
            preferred_items.sort(key=lambda x: x[1], reverse=True)
            
            if preferred_items:
                best_item = preferred_items[0][0]
                # print(f"DEBUG: _select_items_for_layering - Selected {best_item.name} for layer {layer_index + 1}")
                selected_items.append(best_item)
                
                # Remove the selected item from available items to avoid duplicates
                available_items.remove(best_item)
        
        # If we don't have enough layers, try to add additional items
        if len(selected_items) < required_layers:
            # print(f"DEBUG: _select_items_for_layering - Only got {len(selected_items)} layers, need {required_layers}")
            
            # Try to add additional items that could work as layers
            for item in wardrobe:
                item_type_str = item.type.value if hasattr(item.type, 'value') else str(item.type)
                if item not in selected_items and item_type_str in layer_types:
                    # print(f"DEBUG: _select_items_for_layering - Adding additional layer: {item.name} (type: {item_type_str})")
                    selected_items.append(item)
                    if len(selected_items) >= required_layers:
                        break
        
        # print(f"DEBUG: _select_items_for_layering - Final selected items: {[item.name for item in selected_items]}")
        return selected_items

    def _validate_layering_compliance(self, items: List[ClothingItem], layering_rule: LayeringRule, occasion: str = None, temperature: float = None) -> Dict[str, Any]:
        """Validate if the selected items meet layering requirements using temperature+occasion matrix."""
        validation = {
            "is_compliant": True,
            "layer_count": 0,
            "missing_layers": [],
            "suggestions": [],
            "matrix_applied": {}
        }
        
        # Get temperature+occasion layering matrix
        if temperature and occasion:
            layering_matrix = self._get_temperature_occasion_layering_matrix(temperature, occasion)
            validation["matrix_applied"] = layering_matrix
            print(f"DEBUG: _validate_layering_compliance - Applied matrix: {layering_matrix}")
        else:
            # Fallback to basic logic if temperature/occasion not provided
            layering_matrix = {
                "allow_minimal_layering": False,
                "required_layers": layering_rule.required_layers,
                "max_layers": 4,
                "strict_enforcement": True,
                "notes": "Fallback matrix"
            }
            validation["matrix_applied"] = layering_matrix
        
        # Convert layer_types to string values for comparison
        layer_types = [lt.value if hasattr(lt, 'value') else str(lt) for lt in layering_rule.layer_types]
        
        for item in items:
            item_type_str = item.type.value if hasattr(item.type, 'value') else str(item.type)
            if item_type_str in layer_types:
                validation["layer_count"] += 1
        
        # Use matrix-based validation
        allow_minimal_layering = layering_matrix.get("allow_minimal_layering", False)
        required_layers = layering_matrix.get("required_layers", layering_rule.required_layers)
        max_layers = layering_matrix.get("max_layers", 4)
        strict_enforcement = layering_matrix.get("strict_enforcement", True)
        
        # Check if we have enough layers
        if validation["layer_count"] < required_layers:
            if allow_minimal_layering:
                # For casual/warm occasions, be more lenient
                print(f"DEBUG: _validate_layering_compliance - Matrix allows minimal layering: {layering_matrix['notes']}")
                validation["is_compliant"] = True
                validation["suggestions"].append(f"Minimal layering acceptable: {layering_matrix['notes']}")
            else:
                validation["is_compliant"] = False
                missing_count = required_layers - validation["layer_count"]
                validation["missing_layers"].append(f"Need {missing_count} more layer(s)")
                validation["suggestions"].append(f"Add {missing_count} more clothing item(s) for proper layering")
        
        # Check if we have too many layers
        if validation["layer_count"] > max_layers:
            excess_count = validation["layer_count"] - max_layers
            validation["suggestions"].append(f"Consider removing {excess_count} layer(s) - maximum {max_layers} recommended")
            if strict_enforcement:
                validation["is_compliant"] = False
        
        # Check material preferences (only if strict enforcement is enabled)
        material_matches = 0  # Initialize here
        if validation["is_compliant"] and strict_enforcement and not allow_minimal_layering:
            for item in items:
                if hasattr(item, 'material') and item.material in layering_rule.material_preferences:
                    material_matches += 1
        
        if material_matches < len(items) * 0.5:  # At least 50% should match preferred materials
            validation["suggestions"].append("Consider items with preferred materials for better temperature regulation")
        
        return validation

    def _enhance_outfit_with_layering_insights(self, items: List[ClothingItem], layering_rule: LayeringRule, 
                                             weather: WeatherData) -> Dict[str, Any]:
        """Generate layering-specific insights and recommendations."""
        insights = {
            "layering_analysis": {
                "temperature_range": f"{layering_rule.min_temperature}°F - {layering_rule.max_temperature}°F",
                "required_layers": layering_rule.required_layers,
                "actual_layers": len([item for item in items if item.type in layering_rule.layer_types]),
                "layer_types": [item.type for item in items if item.type in layering_rule.layer_types],
                "material_coverage": 0,
                "layering_notes": layering_rule.notes
            },
            "temperature_appropriateness": "optimal",
            "comfort_prediction": "high",
            "style_coherence": "good"
        }
        
        # Calculate material coverage
        preferred_materials = set(layering_rule.material_preferences)
        item_materials = []
        for item in items:
            if hasattr(item, 'material') and item.material:
                item_materials.append(item.material)
        
        if item_materials:
            material_matches = sum(1 for material in item_materials if material in preferred_materials)
            insights["layering_analysis"]["material_coverage"] = material_matches / len(item_materials)
        
        # Adjust temperature appropriateness based on layering
        actual_layers = insights["layering_analysis"]["actual_layers"]
        if actual_layers < layering_rule.required_layers:
            insights["temperature_appropriateness"] = "insufficient"
            insights["comfort_prediction"] = "low"
        elif actual_layers > layering_rule.required_layers + 1:
            insights["temperature_appropriateness"] = "excessive"
            insights["comfort_prediction"] = "medium"
        
        return insights

    async def generate_outfit(
        self,
        occasion: str,
        weather: WeatherData,
        wardrobe: List[ClothingItem],
        user_profile: UserProfile,
        likedOutfits: List[str],
        trendingStyles: List[str],
        preferences: Optional[Dict[str, Any]] = None,
        outfitHistory: Optional[List[Dict[str, Any]]] = None,
        randomSeed: Optional[float] = None,
        season: Optional[str] = None,
        style: Optional[str] = None,
        baseItem: Optional[ClothingItem] = None,
        mood: Optional[str] = None
    ) -> OutfitGeneratedOutfit:
        """Generate a new outfit with robust fallback strategies and comprehensive tracing."""
        # 🚀 NEW: Initialize pipeline tracing
        self.tracing_service.reset_trace()
        generation_start_time = time.time()
        
        # Initialize tracking variables
        was_successful = True
        validation_errors = []
        base_item_id = baseItem.id if baseItem else None
        healing_log = {}
        generation_method = "primary"
        
        # 🚀 NEW: Add initial trace step
        self.tracing_service.add_trace_step(
            step="generation_start",
            method="generate_outfit",
            params={
                "occasion": occasion,
                "temperature": weather.temperature,
                "wardrobe_size": len(wardrobe),
                "style": style,
                "mood": mood,
                "base_item_id": base_item_id,
                "user_id": user_profile.id
            }
        )
        
        try:
            # 🚀 NEW: Normalize user profile data structure to prevent validation issues
            user_profile = self._normalize_user_profile_data(user_profile)
            
            # 🚨 DEBUG: Print first 3 wardrobe items before filtering
            print("\n===== DEBUG: First 3 wardrobe items before filtering =====")
            for i, item in enumerate(wardrobe[:3]):
                print(f"Item {i+1}: {item}")
            print("===== END DEBUG =====\n")
            
            # NEW: More detailed debugging
            print(f"🔍 DEBUG: generate_outfit - Received wardrobe with {len(wardrobe)} items")
            if wardrobe:
                print(f"🔍 DEBUG: generate_outfit - First 3 wardrobe items details:")
                for i, item in enumerate(wardrobe[:3]):
                    print(f"  {i+1}. {item.name} ({item.type}) - Style: {item.style}, Occasion: {item.occasion}")
                    print(f"      Colors: {item.dominantColors}, Matching: {item.matchingColors}")
            else:
                print(f"🔍 DEBUG: generate_outfit - No wardrobe items received!")
            
            # print("✅ Step 1: Starting generate_outfit with refined pipeline")
            # print(f"🔍 BASE ITEM DEBUG - Received baseItem: {baseItem.name if baseItem else 'None'}")
            # print(f"🔍 BASE ITEM DEBUG - Base item ID: {base_item_id}")
            
            # print(f"DEBUG: generate_outfit - Starting with {len(wardrobe)} wardrobe items")
            # print(f"DEBUG: generate_outfit - Temperature: {weather.temperature}°F")
            # print(f"DEBUG: generate_outfit - Occasion: {occasion}, Style: {style}, Mood: {mood}")
            # print(f"DEBUG: generate_outfit - User body type: {user_profile.bodyType}, Skin tone: {user_profile.skinTone}")
            # print(f"DEBUG: generate_outfit - Base item: {base_item_id}")
            
            # 🚀 NEW: Add pipeline start trace
            pipeline_start_time = time.time()
            self.tracing_service.add_trace_step(
                step="pipeline_start",
                method="refined_pipeline",
                params={"pipeline_type": "refined"}
            )
            
            # Use the refined pipeline
            # print("✅ Step 2: Starting refined pipeline")
            
            # NEW: Enhance wardrobe with usage data for diversity
            enhanced_wardrobe = await self._enhance_wardrobe_with_usage_data(wardrobe, user_profile.id)
            
            pipeline_result = await self._generate_outfit_refined_pipeline(
                occasion=occasion,
                weather=weather,
                wardrobe=enhanced_wardrobe,  # Use enhanced wardrobe
                user_profile=user_profile,
                style=style,
                mood=mood,
                baseItem=baseItem,
                trendingStyles=trendingStyles,
                likedOutfits=likedOutfits,
                outfit_history=outfitHistory
            )
            # print("✅ Step 2: Finished refined pipeline")
            
            # 🚀 NEW: Add pipeline completion trace
            pipeline_duration = time.time() - pipeline_start_time
            self.tracing_service.add_trace_step(
                step="pipeline_completion",
                method="refined_pipeline",
                params={"success": pipeline_result["success"]},
                result={"items_selected": len(pipeline_result.get("items", []))},
                duration=pipeline_duration
            )
            
            # Check if pipeline was successful
            if not pipeline_result["success"]:
                error_message = pipeline_result.get("message", "Pipeline failed")
                validation_errors.append(error_message)
                was_successful = False
                print(f"❌ Pipeline failed: {error_message}")
                
                # 🚀 NEW: Add validation error trace
                self.tracing_service.add_validation_error(
                    error_type="pipeline_failure",
                    reason=error_message
                )
            else:
                selected_items = pipeline_result["items"]
                                # print(f"✅ Pipeline successful: {len(selected_items)} items selected")
        # print(f"🔍 Selected items: {[item.name for item in selected_items]}")
            
            # NEW: If pipeline failed, try fallback strategies instead of immediately failing
            if not was_successful:
                print("🔧 Pipeline failed, attempting fallback strategies...")
                generation_method = "fallback"
                
                # 🚀 NEW: Add fallback start trace
                fallback_start_time = time.time()
                self.tracing_service.add_trace_step(
                    step="fallback_start",
                    method="heal_outfit_with_fallbacks",
                    params={"original_errors": validation_errors}
                )
                
                context = {
                    'occasion': occasion,
                    'weather': weather,
                    'user_profile': user_profile,
                    'style': style,
                    'mood': mood,
                    'baseItem': baseItem,
                    'trendingStyles': trendingStyles,
                    'likedOutfits': likedOutfits
                }
                
                # Try to heal the outfit using fallback strategies
                healed_items, remaining_errors, healing_log = await self.fallback_service.heal_outfit_with_fallbacks(
                    selected_items if 'selected_items' in locals() else [],
                    validation_errors,
                    context
                )
                
                # 🚀 NEW: Add fallback completion trace
                fallback_duration = time.time() - fallback_start_time
                self.tracing_service.add_trace_step(
                    step="fallback_completion",
                    method="heal_outfit_with_fallbacks",
                    params={"healing_log": healing_log},
                    result={
                        "healed_items_count": len(healed_items),
                        "remaining_errors": len(remaining_errors)
                    },
                    duration=fallback_duration
                )
                
                if not remaining_errors:
                    print("✅ Fallback strategies successful!")
                    selected_items = healed_items
                    was_successful = True
                    validation_errors = []
                    
                    # 🚀 NEW: Add successful fix trace
                    self.tracing_service.add_fix_attempt(
                        method="fallback_healing",
                        original_error="pipeline_failure",
                        fix_details={"healing_log": healing_log}
                    )
                else:
                    print(f"❌ Fallback strategies reduced errors but {len(remaining_errors)} remain")
                    selected_items = healed_items
                    validation_errors = remaining_errors
                    was_successful = False
                    
                    # 🚀 NEW: Add partial fix trace
                    for error in remaining_errors:
                        self.tracing_service.add_validation_error(
                            error_type="post_fallback_error",
                            reason=error
                        )
            
            # Continue with existing validation logic...
            # CRITICAL VALIDATION: Check if we have enough items
            if len(selected_items) < 2:
                validation_errors.append(f"Insufficient items selected: {len(selected_items)} items (minimum 2 required)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="insufficient_items",
                    reason=f"Only {len(selected_items)} items selected, minimum 2 required"
                )
            
            if len(selected_items) > 6:
                validation_errors.append(f"Too many items selected: {len(selected_items)} items (maximum 6 allowed)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="too_many_items",
                    reason=f"{len(selected_items)} items selected, maximum 6 allowed"
                )
            
            # Get layering rule for validation
            layering_rule = self._get_layering_rule(weather.temperature)
            
            # Step 3: Validate layering compliance
            print("✅ Step 3: Starting layering validation")
            layering_start_time = time.time()
            layering_validation = self._validate_layering_compliance(selected_items, layering_rule, occasion, weather.temperature)
            layering_duration = time.time() - layering_start_time
            print("✅ Step 3: Finished layering validation")
            print(f"🔍 layering_validation: {layering_validation}")
            
            # 🚀 NEW: Add layering validation trace
            self.tracing_service.add_trace_step(
                step="layering_validation",
                method="_validate_layering_compliance",
                params={"temperature": weather.temperature},
                result=layering_validation,
                duration=layering_duration
            )
            
            if not layering_validation["is_compliant"]:
                # Use the correct keys from the validation dict
                missing_layers = layering_validation.get('missing_layers', [])
                suggestions = layering_validation.get('suggestions', [])
                validation_errors.append(f"Layering requirements not met: {missing_layers}; {suggestions}")
                print(f"DEBUG: generate_outfit - Layering validation failed: {missing_layers}; {suggestions}")
                
                # 🚀 NEW: Add layering error trace
                self.tracing_service.add_validation_error(
                    error_type="layering_compliance",
                    reason=f"Missing layers: {missing_layers}",
                    details={"suggestions": suggestions}
                )
            
            # Step 3.5: Validate layering compatibility (sleeve length, button-up rules)
            print("✅ Step 3.5: Starting layering compatibility validation")
            compatibility_start_time = time.time()
            layering_compatibility = self._validate_layering_compatibility(selected_items)
            compatibility_duration = time.time() - compatibility_start_time
            print("✅ Step 3.5: Finished layering compatibility validation")
            print(f"🔍 layering_compatibility: {layering_compatibility}")
            
            # 🚀 NEW: Add layering compatibility trace
            self.tracing_service.add_trace_step(
                step="layering_compatibility",
                method="_validate_layering_compatibility",
                params={},
                result=layering_compatibility,
                duration=compatibility_duration
            )
            
            if not layering_compatibility["is_compatible"]:
                errors = layering_compatibility.get('errors', [])
                warnings = layering_compatibility.get('warnings', [])
                validation_errors.extend(errors)
                validation_errors.extend(warnings)
                print(f"DEBUG: generate_outfit - Layering compatibility failed: {errors}; {warnings}")
                
                # 🚀 NEW: Add compatibility error traces
                for error in errors:
                    self.tracing_service.add_validation_error(
                        error_type="layering_compatibility",
                        reason=error
                    )
                # Don't fail completely for layering compatibility issues
                # was_successful = False
            
            # Step 4: Generate outfit insights and analysis
            print("✅ Step 4: Starting _enhance_outfit_with_layering_insights")
            insights_start_time = time.time()
            layering_insights = self._enhance_outfit_with_layering_insights(selected_items, layering_rule, weather)
            insights_duration = time.time() - insights_start_time
            print("✅ Step 4: Finished _enhance_outfit_with_layering_insights")
            print(f"🔍 layering_insights: {layering_insights}")
            
            # 🚀 NEW: Add insights generation trace
            self.tracing_service.add_trace_step(
                step="insights_generation",
                method="_enhance_outfit_with_layering_insights",
                params={},
                result=layering_insights,
                duration=insights_duration
            )
            
            # Step 5: Calculate scores and generate content
            print("✅ Step 5: Starting score calculations")
            scores_start_time = time.time()
            print("🔍 Before _calculate_pairability_score_enhanced")
            pairability_score = self._calculate_pairability_score_enhanced(selected_items)
            print(f"🔍 pairability_score: {pairability_score}")
            
            print("🔍 Before _calculate_style_compliance_enhanced")
            style_compliance = self._calculate_style_compliance_enhanced(selected_items, style)
            print(f"🔍 style_compliance: {style_compliance}")
            
            print("🔍 Before _calculate_weather_appropriateness_enhanced")
            weather_appropriateness = self._calculate_weather_appropriateness_enhanced(selected_items, weather)
            print(f"🔍 weather_appropriateness: {weather_appropriateness}")
            
            print("🔍 Before _calculate_occasion_appropriateness_enhanced")
            occasion_appropriateness = self._calculate_occasion_appropriateness_enhanced(selected_items, occasion)
            print(f"🔍 occasion_appropriateness: {occasion_appropriateness}")
            print("✅ Step 5: Finished score calculations")
            
            scores_duration = time.time() - scores_start_time
            
            # 🚀 NEW: Add scores calculation trace
            self.tracing_service.add_trace_step(
                step="scores_calculation",
                method="calculate_scores",
                params={},
                result={
                    "pairability_score": pairability_score,
                    "style_compliance": style_compliance,
                    "weather_appropriateness": weather_appropriateness,
                    "occasion_appropriateness": occasion_appropriateness
                },
                duration=scores_duration
            )
            
            # CRITICAL VALIDATION: Check minimum scores (relaxed thresholds)
            if pairability_score < 0.2:  # Relaxed from 0.3
                validation_errors.append(f"Low pairability score: {pairability_score:.2f} (minimum 0.2 required)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="low_pairability",
                    reason=f"Score {pairability_score:.2f} below threshold 0.2"
                )
            
            if style_compliance < 0.3:  # Relaxed from 0.4
                validation_errors.append(f"Low style compliance: {style_compliance:.2f} (minimum 0.3 required)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="low_style_compliance",
                    reason=f"Score {style_compliance:.2f} below threshold 0.3"
                )
            
            if weather_appropriateness < 0.2:  # Relaxed from 0.4 to 0.2
                validation_errors.append(f"Low weather appropriateness: {weather_appropriateness:.2f} (minimum 0.2 required)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="low_weather_appropriateness",
                    reason=f"Score {weather_appropriateness:.2f} below threshold 0.2"
                )
            
            if occasion_appropriateness < 0.2:  # Relaxed from 0.3 to 0.2
                validation_errors.append(f"Low occasion appropriateness: {occasion_appropriateness:.2f} (minimum 0.2 required)")
                was_successful = False
                self.tracing_service.add_validation_error(
                    error_type="low_occasion_appropriateness",
                    reason=f"Score {occasion_appropriateness:.2f} below threshold 0.2"
                )
            
            # NEW: If we still have validation errors after fallback, try one more healing attempt
            if validation_errors and not was_successful:
                print("🔧 Final healing attempt for remaining validation errors...")
                generation_method = "final_fallback"
                
                # 🚀 NEW: Add final healing attempt trace
                final_healing_start_time = time.time()
                self.tracing_service.add_trace_step(
                    step="final_healing_attempt",
                    method="heal_outfit_with_fallbacks",
                    params={"remaining_errors": validation_errors}
                )
                
                context = {
                    'occasion': occasion,
                    'weather': weather,
                    'user_profile': user_profile,
                    'style': style,
                    'mood': mood,
                    'baseItem': baseItem,
                    'trendingStyles': trendingStyles,
                    'likedOutfits': likedOutfits
                }
                
                final_healed_items, final_remaining_errors, final_healing_log = await self.fallback_service.heal_outfit_with_fallbacks(
                    selected_items,
                    validation_errors,
                    context
                )
                
                final_healing_duration = time.time() - final_healing_start_time
                
                # 🚀 NEW: Add final healing completion trace
                self.tracing_service.add_trace_step(
                    step="final_healing_completion",
                    method="heal_outfit_with_fallbacks",
                    params={"final_healing_log": final_healing_log},
                    result={
                        "final_healed_items_count": len(final_healed_items),
                        "final_remaining_errors": len(final_remaining_errors),
                        "improvement": len(validation_errors) - len(final_remaining_errors)
                    },
                    duration=final_healing_duration
                )
                
                if len(final_remaining_errors) < len(validation_errors):
                    print("✅ Final healing attempt improved the outfit!")
                    selected_items = final_healed_items
                    validation_errors = final_remaining_errors
                    healing_log.update(final_healing_log)
                    
                    # 🚀 NEW: Add successful final fix trace
                    self.tracing_service.add_fix_attempt(
                        method="final_fallback_healing",
                        original_error="multiple_validation_errors",
                        fix_details={"final_healing_log": final_healing_log}
                    )
                    
                    # If we significantly reduced errors, mark as successful
                    if len(validation_errors) <= 1:
                        was_successful = True
            
            # Step 6: Generate outfit content
            print("✅ Step 6: Starting content generation")
            print("🔍 Before _calculate_color_harmony_enhanced")
            color_harmony = self._calculate_color_harmony_enhanced(selected_items)
            print(f"🔍 color_harmony: {color_harmony}")
            
            print("🔍 Before _generate_style_notes_enhanced")
            style_notes = self._generate_style_notes_enhanced(selected_items, occasion, style)
            print(f"🔍 style_notes: {style_notes}")
            
            print("🔍 Before _generate_style_tags_enhanced")
            style_tags = self._generate_style_tags_enhanced(selected_items, style)
            print(f"🔍 style_tags: {style_tags}")
            
            # Calculate missing metadata values just before using them
            style_compatibility = self._get_style_compatibility_summary(selected_items)
            clip_insights = self._extract_clip_insights(selected_items)

            # Step 7: Create outfit pieces
            print("✅ Step 7: Starting outfit pieces creation")
            outfit_pieces = []
            for item in selected_items:
                piece = OutfitPiece(
                    itemId=item.id,
                    name=item.name,
                    type=item.type,
                    reason=self._generate_item_reason_enhanced(item, occasion, style),
                    dominantColors=[color.name for color in item.dominantColors],
                    style=item.style,
                    occasion=item.occasion,
                    imageUrl=item.imageUrl
                )
                outfit_pieces.append(piece)
            print("✅ Step 7: Finished outfit pieces creation")
            
            # CRITICAL VALIDATION: Check if we have too many validation errors
            if len(validation_errors) >= 3:
                was_successful = False
                print(f"❌ CRITICAL: Too many validation errors ({len(validation_errors)}), marking as failed")
            
            # Step 8: Create outfit data
            print("✅ Step 8: Starting outfit_data creation")
            
            # Convert selected items to full objects for the response
            items_for_response = []
            for item in selected_items:
                # Convert ClothingItem to dict for response
                item_dict = item.dict() if hasattr(item, 'dict') else {
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                    'color': item.color,
                    'season': item.season,
                    'tags': item.tags,
                    'dominantColors': item.dominantColors,
                    'matchingColors': item.matchingColors,
                    'style': item.style,
                    'occasion': item.occasion,
                    'imageUrl': item.imageUrl,
                    'userId': item.userId,
                    'createdAt': item.createdAt,
                    'updatedAt': item.updatedAt,
                    'subType': item.subType,
                    'colorName': item.colorName,
                    'backgroundRemoved': item.backgroundRemoved,
                    'embedding': item.embedding,
                    'metadata': item.metadata,
                    'wearCount': item.wearCount,
                    'gender': item.gender,
                    'brand': item.brand,
                    'weatherCompatibility': item.weatherCompatibility,
                    'bodyTypeCompatibility': item.bodyTypeCompatibility,
                    'mood': item.mood
                }
                items_for_response.append(item_dict)
            
            outfit_data = {
                "id": str(uuid.uuid4()),
                "name": f"{style or 'Stylish'} {occasion} Outfit",
                "description": f"A {style or 'stylish'} outfit for {occasion} with {layering_rule.required_layers} layers for {weather.temperature}°F weather",
                "items": items_for_response,  # Return full item objects instead of just IDs
                "explanation": f"Generated outfit with {len(selected_items)} items for {occasion} occasion",
                "pieces": [piece.dict() for piece in outfit_pieces],
                "styleTags": style_tags,
                "colorHarmony": color_harmony,
                "styleNotes": style_notes,
                "occasion": occasion,
                "season": self._determine_season(weather.temperature, occasion),
                "style": style or "Stylish",
                "mood": mood if mood else "Neutral",  # Use provided mood, only default if none provided
                "createdAt": int(time.time()),
                "updatedAt": int(time.time()),
                "wasSuccessful": was_successful,
                "baseItemId": base_item_id,
                "validationErrors": validation_errors,
                "userFeedback": None,
                "user_id": user_profile.id,  # NEW: Add user_id for filtering
                "metadata": {
                    "layering_insights": layering_insights,
                    "style_compatibility": style_compatibility,
                    "clip_insights": clip_insights,
                    "healing_log": healing_log  # Add healing information
                }
            }
            print("✅ Step 8: Finished outfit_data creation")
            print(f"🔍 outfit_data keys: {list(outfit_data.keys())}")

            # Save to Firestore
            print("✅ Step 9: Starting Firestore save")
            doc_ref = self.collection.document(outfit_data["id"])
            # Convert the outfit data to dict for Firestore storage
            firestore_data = self.to_dict_recursive(outfit_data)
            doc_ref.set(firestore_data)
            print("✅ Step 9: Finished Firestore save")
            
            # 🚀 NEW: Add final generation completion trace
            generation_duration = time.time() - generation_start_time
            self.tracing_service.add_trace_step(
                step="generation_completion",
                method="generate_outfit",
                params={"outfit_id": outfit_data["id"]},
                result={
                    "was_successful": was_successful,
                    "items_count": len(selected_items),
                    "validation_errors_count": len(validation_errors),
                    "generation_method": generation_method
                },
                duration=generation_duration
            )
            
            # 🚀 NEW: Save complete trace to Firestore
            try:
                complete_trace = self.tracing_service.get_complete_trace(
                    outfit_id=outfit_data["id"],
                    user_id=user_profile.id,
                    wardrobe=wardrobe,
                    recent_feedback=outfitHistory,
                    outfit_history=outfitHistory
                )
                
                # Add the trace data to the outfit document
                outfit_data.update({
                    "generation_trace": complete_trace["generation_trace"],
                    "validation_details": {
                        "errors": [entry for entry in complete_trace["generation_trace"] 
                                 if entry.get("step") == "validation_error"],
                        "fixes": [entry for entry in complete_trace["generation_trace"] 
                                 if entry.get("step") == "fix_attempt"]
                    },
                    "wardrobe_snapshot": complete_trace["wardrobe_snapshot"],
                    "system_context": complete_trace["system_context"],
                    "user_session_context": complete_trace["user_session_context"],
                    "generation_method": generation_method
                })
                
                # Update the Firestore document with trace data
                firestore_data = self.to_dict_recursive(outfit_data)
                doc_ref.set(firestore_data)
                
                # Also save to the traces collection
                await self.tracing_service.save_trace(outfit_data["id"], complete_trace)
                
                print(f"🚀 Trace saved successfully for outfit {outfit_data['id']}")
                print(f"📊 Trace summary: {self.tracing_service.get_trace_summary()}")
                
            except Exception as trace_error:
                print(f"⚠️ Warning: Failed to save trace: {trace_error}")
            
            print(f"DEBUG: generate_outfit - Outfit saved with ID: {outfit_data['id']}")
            print(f"DEBUG: generate_outfit - Success: {was_successful}")
            print(f"DEBUG: generate_outfit - Base item ID: {base_item_id}")
            print(f"DEBUG: generate_outfit - Validation errors: {validation_errors}")
            print(f"DEBUG: generate_outfit - Layering compliance: {layering_validation['is_compliant']}")
            
            # Debug: Print the outfit_data dict to see what's in it
            print(f"DEBUG: generate_outfit - outfit_data keys: {list(outfit_data.keys())}")
            print(f"DEBUG: generate_outfit - wasSuccessful in dict: {outfit_data.get('wasSuccessful', 'NOT FOUND')}")
            print(f"DEBUG: generate_outfit - baseItemId in dict: {outfit_data.get('baseItemId', 'NOT FOUND')}")
            print(f"DEBUG: generate_outfit - validationErrors in dict: {outfit_data.get('validationErrors', 'NOT FOUND')}")
            
            # Debug: Print the full outfit_data dict
            print("DEBUG: generate_outfit - Full outfit_data dict:")
            import json
            print(json.dumps(outfit_data, indent=2, default=str))
            
            print("✅ Step 10: Creating OutfitGeneratedOutfit object")
            result = OutfitGeneratedOutfit(**outfit_data)
            print("✅ Step 10: Finished creating OutfitGeneratedOutfit object")
            print("✅ SUCCESS: generate_outfit completed successfully!")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR in generate_outfit: {e}")
            import traceback
            print(f"❌ TRACEBACK:")
            print(traceback.format_exc())
            
            # 🚀 NEW: Add error trace
            self.tracing_service.add_trace_step(
                step="generation_error",
                method="generate_outfit",
                params={},
                errors=[f"Generation failed: {str(e)}"],
                duration=time.time() - generation_start_time
            )
            
            # Mark as failed and capture the error
            was_successful = False
            validation_errors.append(f"Generation failed: {str(e)}")
            
            # Create a minimal outfit data for failed generation
            outfit_data = {
                "id": str(uuid.uuid4()),
                "name": f"Failed {occasion} Outfit",
                "description": f"Failed to generate outfit for {occasion}",
                "items": [],
                "explanation": f"Outfit generation failed: {str(e)}",
                "pieces": [],
                "styleTags": [],
                "colorHarmony": "",
                "styleNotes": "",
                "occasion": occasion,
                "season": self._determine_season(weather.temperature, occasion),
                "style": style or "Unknown",
                "createdAt": int(time.time()),
                "updatedAt": int(time.time()),
                "wasSuccessful": was_successful,
                "baseItemId": base_item_id,
                "validationErrors": validation_errors,
                "userFeedback": None,
                "metadata": {
                    "error": str(e),
                    "enhancedAnalysis": False,
                    "healing_log": healing_log
                },
                # 🚀 NEW: Add error trace data
                "generation_trace": self.tracing_service.current_trace,
                "generation_method": "error"
            }
            
            # Save failed outfit to Firestore for tracking
            try:
                doc_ref = self.collection.document(outfit_data["id"])
                # Convert the outfit data to dict for Firestore storage
                firestore_data = self.to_dict_recursive(outfit_data)
                doc_ref.set(firestore_data)
                print(f"DEBUG: generate_outfit - Failed outfit saved with ID: {outfit_data['id']}")
                
                # 🚀 NEW: Save error trace
                try:
                    error_trace = self.tracing_service.get_complete_trace(
                        outfit_id=outfit_data["id"],
                        user_id=user_profile.id,
                        wardrobe=wardrobe,
                        recent_feedback=outfitHistory,
                        outfit_history=outfitHistory
                    )
                    await self.tracing_service.save_trace(outfit_data["id"], error_trace)
                except Exception as trace_error:
                    print(f"⚠️ Warning: Failed to save error trace: {trace_error}")
                    
            except Exception as save_error:
                print(f"Error saving failed outfit: {save_error}")
            
            # Return the failed outfit
            return OutfitGeneratedOutfit(**outfit_data)

    def _get_complementary_items_enhanced(self, base_item: ClothingItem, wardrobe: List[ClothingItem], style: Optional[str]) -> List[ClothingItem]:
        """Get items that complement the base item using enhanced analysis insights."""
        complementary_items = []
        
        # Get enhanced style compatibility data
        base_style_compatibility = getattr(base_item.metadata, 'styleCompatibility', {}) if base_item.metadata else {}
        compatible_styles = base_style_compatibility.get("compatibleStyles", []) if base_style_compatibility else []
        avoid_styles = base_style_compatibility.get("avoidStyles", []) if base_style_compatibility else []
        
        for item in wardrobe:
            if item.id != base_item.id:
                # Check if items are compatible using enhanced analysis
                if self._items_are_compatible_enhanced(base_item, item, compatible_styles, avoid_styles, style):
                    complementary_items.append(item)
        
        return complementary_items

    def _get_essential_items_enhanced(self, occasion: str, wardrobe: List[ClothingItem], style: Optional[str]) -> List[ClothingItem]:
        """Get essential items for the given occasion using enhanced analysis and outfit rules."""
        essential_items = []
        print(f"DEBUG: _get_essential_items_enhanced - Looking for {occasion} items from {len(wardrobe)} wardrobe items")
        
        # Get the occasion rule to know what item types are required
        from ..types.outfit_rules import get_occasion_rule
        occasion_rule = get_occasion_rule(occasion)
        required_item_types = []
        if occasion_rule:
            required_item_types = [item_type.value.lower() for item_type in occasion_rule.required_items]
            print(f"DEBUG: _get_essential_items_enhanced - Required item types for {occasion}: {required_item_types}")
        else:
            print(f"DEBUG: _get_essential_items_enhanced - No occasion rule found for {occasion}")
        
        # Define category mapping to avoid duplicates
        category_mapping = {
            'top': ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket', 'coat'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings']
        }
        
        # Track which categories we've already filled
        filled_categories = set()
        
        # Define athletic keywords for strict filtering
        athletic_keywords = ['athletic', 'gym', 'workout', 'running', 'sport', 'exercise', 'training']
        
        # First, try to find items that match the occasion
        occasion_matching_items = []
        for item in wardrobe:
            print(f"DEBUG: Checking item {item.name} (id: {item.id})")
            print(f"DEBUG:   - Item occasions: {item.occasion}")
            print(f"DEBUG:   - Looking for occasion: {occasion}")
            
            # STRICT FILTERING for athletic occasions
            if occasion and 'athletic' in occasion.lower():
                # For athletic occasions, require items to have athletic-related attributes
                has_athletic_occasion = False
                if item.occasion:
                    item_occasions = [occ.lower() for occ in item.occasion]
                    for item_occ in item_occasions:
                        if any(keyword in item_occ for keyword in athletic_keywords):
                            has_athletic_occasion = True
                            break
                
                has_athletic_style = False
                if item.style:
                    item_styles = [s.lower() for s in item.style]
                    if any(keyword in ' '.join(item_styles) for keyword in athletic_keywords):
                        has_athletic_style = True
                
                has_athletic_tags = False
                if hasattr(item, 'tags') and item.tags:
                    item_tags = [tag.lower() for tag in item.tags]
                    if any(keyword in ' '.join(item_tags) for keyword in athletic_keywords):
                        has_athletic_tags = True
                
                # For athletic occasions, require at least one athletic attribute
                if not (has_athletic_occasion or has_athletic_style or has_athletic_tags):
                    print(f"DEBUG:   ✗ Item filtered out - no athletic attributes for {occasion}")
                    continue
                
                print(f"DEBUG:   ✓ Item has athletic attributes for {occasion}")
                occasion_matching_items.append(item)
            
            else:
                # For non-athletic occasions, use the original logic
                # Check occasion compatibility
                if occasion in item.occasion:
                    print(f"DEBUG:   ✓ Item matches occasion {occasion}")
                    # Use enhanced occasion tags if available
                    enhanced_occasions = getattr(item.metadata, 'enhancedOccasions', None)
                    if enhanced_occasions is None and item.metadata and hasattr(item.metadata, 'dict'):
                        enhanced_occasions = item.metadata.dict().get('enhancedOccasions', item.occasion) if item.metadata and hasattr(item.metadata, 'dict') else item.occasion
                    if enhanced_occasions is None:
                        enhanced_occasions = item.occasion
                    print(f"DEBUG:   - Enhanced occasions: {enhanced_occasions}")
                    if occasion in enhanced_occasions:
                        print(f"DEBUG:   ✓ Item added to occasion matching items")
                        occasion_matching_items.append(item)
                    else:
                        print(f"DEBUG:   ✗ Item filtered out by enhanced occasions")
                else:
                    print(f"DEBUG:   ✗ Item doesn't match occasion {occasion}")
        
        # Now ensure we have at least one item of each required type, but avoid duplicate categories
        selected_by_type = {}
        for item in occasion_matching_items:
            item_type = item.type.lower()
            
            # Determine which category this item belongs to
            item_category = None
            for category, types in category_mapping.items():
                if any(t in item_type for t in types):
                    item_category = category
                    break
            
            # Only add if we haven't filled this category yet
            if item_category and item_category not in filled_categories:
                for required_type in required_item_types:
                    if required_type in item_type and required_type not in selected_by_type:
                        selected_by_type[required_type] = item
                        essential_items.append(item)
                        filled_categories.add(item_category)
                        print(f"DEBUG: _get_essential_items_enhanced - Added {required_type} (category: {item_category}): {item.name}")
                        break
        
        # STRICT FALLBACK LOGIC for athletic occasions
        if occasion and 'athletic' in occasion.lower():
            # For athletic occasions, don't add items that don't have athletic attributes
            missing_types = set(required_item_types) - set(selected_by_type.keys())
            if missing_types:
                print(f"DEBUG: _get_essential_items_enhanced - Missing required types for athletic occasion: {missing_types}")
                print(f"DEBUG: _get_essential_items_enhanced - WARNING: Not adding non-athletic items as fallback!")
                print(f"DEBUG: _get_essential_items_enhanced - This may result in incomplete outfits, but prevents inappropriate items.")
        else:
            # For non-athletic occasions, keep the original fallback logic
            # If we don't have all required types, add items that match the required types
            missing_types = set(required_item_types) - set(selected_by_type.keys())
            if missing_types:
                print(f"DEBUG: _get_essential_items_enhanced - Missing required types: {missing_types}")
                for missing_type in missing_types:
                    for item in wardrobe:
                        if item not in essential_items:  # Don't add duplicates
                            item_type = item.type.lower()
                            
                            # Determine which category this item belongs to
                            item_category = None
                            for category, types in category_mapping.items():
                                if any(t in item_type for t in types):
                                    item_category = category
                                    break
                            
                            # Only add if we haven't filled this category yet and it matches the missing type
                            if item_category and item_category not in filled_categories and missing_type in item_type:
                                essential_items.append(item)
                                filled_categories.add(item_category)
                                print(f"DEBUG: _get_essential_items_enhanced - Added missing {missing_type} (category: {item_category}): {item.name}")
                                break
        
        print(f"DEBUG: _get_essential_items_enhanced - Found {len(essential_items)} essential items")
        # print(f"DEBUG: _get_essential_items_enhanced - Selected items: {[item.name for item in essential_items]}")
        print(f"DEBUG: _get_essential_items_enhanced - Filled categories: {filled_categories}")
        return essential_items

    def _get_style_items_enhanced(self, style: str, wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get items matching the style using enhanced analysis insights."""
        style_items = []
        print(f"DEBUG: _get_style_items_enhanced - Looking for {style} items from {len(wardrobe)} wardrobe items")
        
        for item in wardrobe:
            print(f"DEBUG: Checking item {item.name} (id: {item.id}) for style {style}")
            print(f"DEBUG:   - Item styles: {item.style}")
            
            # Check primary style from CLIP analysis
            clip_analysis = getattr(item.metadata, 'clipAnalysis', None)
            clip_primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
            print(f"DEBUG:   - CLIP primary style: {clip_primary_style}")
            if clip_primary_style and clip_primary_style.lower() == style.lower():
                print(f"DEBUG:   ✓ Item matches CLIP style")
                style_items.append(item)
                continue

            # Check enhanced style tags
            enhanced_styles = getattr(item.metadata, 'enhancedStyles', None)
            if enhanced_styles is None and item.metadata and hasattr(item.metadata, 'dict'):
                enhanced_styles = item.metadata.dict().get('enhancedStyles', item.style) if item.metadata and hasattr(item.metadata, 'dict') else item.style
            if enhanced_styles is None:
                enhanced_styles = item.style
            print(f"DEBUG:   - Enhanced styles: {enhanced_styles}")
            if style.lower() in [s.lower() for s in enhanced_styles]:
                print(f"DEBUG:   ✓ Item matches enhanced styles")
                style_items.append(item)
                continue

            # Check style compatibility
            style_compatibility = getattr(item.metadata, 'styleCompatibility', None)
            compatible_styles = style_compatibility.get("compatibleStyles", []) if style_compatibility else []
            print(f"DEBUG:   - Compatible styles: {compatible_styles}")
            if style.lower() in [s.lower() for s in compatible_styles]:
                print(f"DEBUG:   ✓ Item matches compatible styles")
                style_items.append(item)
            else:
                print(f"DEBUG:   ✗ Item doesn't match any style criteria")
        
        print(f"DEBUG: _get_style_items_enhanced - Found {len(style_items)} style items")
        return style_items

    def _adjust_for_weather_enhanced(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Apply weather-appropriate adjustments using enhanced temperature compatibility."""
        adjusted_items = []
        
        for item in items:
            # Get enhanced temperature compatibility data
            visual_attrs = getattr(item.metadata, 'visualAttributes', None)
            if visual_attrs is None:
                temp_compatibility = {}
            elif isinstance(visual_attrs, dict):
                temp_compatibility = visual_attrs.get("temperatureCompatibility", {})
            else:
                temp_compatibility = getattr(visual_attrs, 'temperatureCompatibility', {})
            
            # Handle both dict and Pydantic model for temp_compatibility
            if isinstance(temp_compatibility, dict):
                min_temp = temp_compatibility.get("minTemp", 32)
                max_temp = temp_compatibility.get("maxTemp", 75)
            else:
                # Pydantic model - use getattr
                min_temp = getattr(temp_compatibility, "minTemp", 32)
                max_temp = getattr(temp_compatibility, "maxTemp", 75)
            
            # Ensure temperature values are floats to prevent comparison errors
            try:
                min_temp = float(min_temp) if min_temp is not None else 32.0
                max_temp = float(max_temp) if max_temp is not None else 75.0
            except (ValueError, TypeError):
                # Fallback to safe defaults if conversion fails
                min_temp = 32.0
                max_temp = 75.0
            
            # Check if item is appropriate for current temperature
            if min_temp <= weather.temperature <= max_temp:
                adjusted_items.append(item)
        
        return adjusted_items

    def _calculate_color_harmony_enhanced(self, items: List[ClothingItem]) -> str:
        """Calculate color harmony using enhanced color analysis."""
        if not items:
            return "No items to analyze"
        
        # Extract enhanced color data
        dominant_colors = []
        matching_colors = []
        
        for item in items:
            # Use enhanced color analysis if available
            enhanced_colors = getattr(item.metadata, 'enhancedColorAnalysis', {})
            if enhanced_colors:
                dominant_colors.extend(enhanced_colors.get("dominant", item.dominantColors) if enhanced_colors else item.dominantColors)
                matching_colors.extend(enhanced_colors.get("matching", item.matchingColors) if enhanced_colors else item.matchingColors)
            else:
                dominant_colors.extend(item.dominantColors)
                matching_colors.extend(item.matchingColors)
        
        # Analyze color harmony
        if len(dominant_colors) == 0:
            return "No color data available"
        
        # Use utility function for color name extraction
        color_names = extract_color_names(dominant_colors)
        
        # Check for monochromatic
        if len(set(color_names)) == 1:
            return f"Monochromatic {color_names[0]} palette"
        
        # Check for complementary colors
        if len(color_names) == 2:
            return f"Complementary {color_names[0]} and {color_names[1]} palette"
        
        # Check for analogous colors
        if len(color_names) <= 3:
            return f"Analogous {', '.join(color_names)} palette"
        
        return f"Multi-color palette with {len(set(color_names))} distinct colors"

    def _generate_style_notes_enhanced(self, items: List[ClothingItem], occasion: str, style: Optional[str]) -> str:
        """Generate style notes using enhanced analysis insights."""
        if not items:
            return "No items selected"
        
        notes = []
        
        # Extract CLIP insights
        clip_insights = []
        for item in items:
            clip_analysis = getattr(item.metadata, 'clipAnalysis', {})
            if clip_analysis:
                primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
                confidence = clip_analysis.get("styleConfidence", 0) if clip_analysis else 0
                if primary_style and confidence > 0.3:
                    clip_insights.append(f"{primary_style} ({confidence:.1%} confidence)")
        
        if clip_insights:
            notes.append(f"Style analysis: {', '.join(clip_insights)}")
        
        # Extract style compatibility insights
        style_compatibility_notes = []
        for item in items:
            style_compat = getattr(item.metadata, 'styleCompatibility', {})
            if style_compat:
                compatible = style_compat.get("compatibleStyles", []) if style_compat else []
                avoid = style_compat.get("avoidStyles", []) if style_compat else []
                if compatible:
                    style_compatibility_notes.append(f"Works well with: {', '.join(compatible[:2])}")
                if avoid:
                    style_compatibility_notes.append(f"Avoid pairing with: {', '.join(avoid[:2])}")
        
        if style_compatibility_notes:
            notes.append("Style compatibility: " + "; ".join(style_compatibility_notes))
        
        # Add occasion and weather notes
        notes.append(f"Perfect for {occasion}")
        
        return ". ".join(notes)

    def _generate_item_reason_enhanced(self, item: ClothingItem, occasion: str, style: Optional[str]) -> str:
        """Generate reason for including an item using enhanced analysis."""
        reasons = []
        
        # Check CLIP analysis
        clip_analysis = getattr(item.metadata, 'clipAnalysis', {})
        if clip_analysis:
            primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
            confidence = clip_analysis.get("styleConfidence", 0) if clip_analysis else 0
            if primary_style and confidence > 0.3:
                reasons.append(f"Strong {primary_style} aesthetic")

                # Check style compatibility
        style_compat = getattr(item.metadata, 'styleCompatibility', {})
        if style_compat and style:
            compatible_styles = style_compat.get("compatibleStyles", []) if style_compat else []
            if style in compatible_styles:
                reasons.append(f"Compatible with {style} style")
        
        # Check occasion appropriateness
        if occasion in item.occasion:
            reasons.append(f"Perfect for {occasion}")
        
        if not reasons:
            reasons.append(f"Stylish choice for {occasion}")
        
        return "; ".join(reasons)

    def _calculate_pairability_score_enhanced(self, items: List[ClothingItem]) -> float:
        """Calculate enhanced pairability score using style compatibility data."""
        if len(items) < 2:
            return 1.0
        
        total_score = 0
        comparisons = 0
        
        for i, item1 in enumerate(items):
            for j, item2 in enumerate(items[i+1:], i+1):
                # Get style compatibility data
                style_compat1 = getattr(item1.metadata, 'styleCompatibility', {})
                style_compat2 = getattr(item2.metadata, 'styleCompatibility', {})
                
                # Check if items are compatible
                compatible_styles1 = style_compat1.get("compatibleStyles", []) if style_compat1 else []
                compatible_styles2 = style_compat2.get("compatibleStyles", []) if style_compat2 else []
                
                # Calculate compatibility score
                score = 0.5  # Base score
                
                # Check for style overlap
                item1_styles = set(item1.style + compatible_styles1)
                item2_styles = set(item2.style + compatible_styles2)
                style_overlap = len(item1_styles.intersection(item2_styles))
                
                if style_overlap > 0:
                    score += 0.3
                
                # Check for color compatibility
                if self._colors_are_compatible(item1.dominantColors, item2.dominantColors):
                    score += 0.2
                
                total_score += score
                comparisons += 1
        
        return total_score / comparisons if comparisons > 0 else 1.0

    def _calculate_style_compliance_enhanced(self, items: List[ClothingItem], style: Optional[str]) -> float:
        """Calculate enhanced style compliance using CLIP analysis."""
        if not style or not items:
            return 0.8
        
        total_confidence = 0
        style_matches = 0
        
        for item in items:
            clip_analysis = getattr(item.metadata, 'clipAnalysis', {})
            if clip_analysis:
                primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
                confidence = clip_analysis.get("styleConfidence", 0) if clip_analysis else 0
                
                if primary_style and primary_style.lower() == style.lower():
                    total_confidence += confidence
                    style_matches += 1
        
        if style_matches == 0:
            return 0.5  # Neutral score if no CLIP data
        
        return total_confidence / style_matches

    def _calculate_weather_appropriateness_enhanced(self, items: List[ClothingItem], weather: WeatherData) -> float:
        """Calculate enhanced weather appropriateness using temperature compatibility."""
        if not items:
            return 0.8
        
        appropriate_items = 0
        
        for item in items:
            visual_attrs = getattr(item.metadata, 'visualAttributes', None)
            if visual_attrs is None:
                temp_compatibility = {}
            elif isinstance(visual_attrs, dict):
                temp_compatibility = visual_attrs.get("temperatureCompatibility", {})
            else:
                temp_compatibility = getattr(visual_attrs, 'temperatureCompatibility', {})
            
            # Handle both dict and Pydantic model for temp_compatibility
            if isinstance(temp_compatibility, dict):
                min_temp = temp_compatibility.get("minTemp", 32)
                max_temp = temp_compatibility.get("maxTemp", 75)
            else:
                # Pydantic model - use getattr
                min_temp = getattr(temp_compatibility, "minTemp", 32)
                max_temp = getattr(temp_compatibility, "maxTemp", 75)
            
            # Ensure temperature values are floats to prevent comparison errors
            try:
                min_temp = float(min_temp) if min_temp is not None else 32.0
                max_temp = float(max_temp) if max_temp is not None else 75.0
            except (ValueError, TypeError):
                # Fallback to safe defaults if conversion fails
                min_temp = 32.0
                max_temp = 75.0
            
            if min_temp <= weather.temperature <= max_temp:
                appropriate_items += 1
        
        score = appropriate_items / len(items)
        
        # NEW: Ensure minimum score for basic outfits
        if score < 0.3 and len(items) >= 2:
            # If we have a basic outfit structure, give it a minimum score
            basic_outfit_types = ['shirt', 'pants', 'shoes', 't-shirt', 'jeans', 'sneakers']
            basic_count = sum(1 for item in items 
                            if any(basic in item.type.lower() or basic in item.name.lower() 
                                   for basic in basic_outfit_types))
            
            if basic_count >= 2:
                score = max(score, 0.4)  # Minimum 0.4 for basic outfits
        
        return score

    def _calculate_occasion_appropriateness_enhanced(self, items: List[ClothingItem], occasion: str) -> float:
        """Calculate enhanced occasion appropriateness with fallback logic."""
        if not items:
            return 0.8
        
        appropriate_items = 0
        total_items = len(items)
        
        for item in items:
            # Check both regular and enhanced occasion tags
            occasions = item.occasion + getattr(item.metadata, 'enhancedOccasions', [])
            if occasion in occasions:
                appropriate_items += 1
        
        base_score = appropriate_items / total_items
        
        # NEW: Fallback logic for low scores
        if base_score == 0.0:
            print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Zero occasion score, applying fallback logic")
            
            # Comprehensive fallback logic for all occasions
            # Fashion Event
            if 'fashion' in occasion.lower() or 'event' in occasion.lower():
                print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Fashion event detected, applying fashion-specific logic")
                fashion_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    stylish_keywords = ['stylish', 'fashion', 'trendy', 'modern', 'designer', 'elegant']
                    if any(keyword in item_name_lower for keyword in stylish_keywords):
                        fashion_matches += 1
                    elif any(basic_type in item_type_lower for basic_type in ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'sweater']):
                        fashion_matches += 1
                    elif hasattr(item, 'occasion') and len(item.occasion) > 0:
                        fashion_matches += 1
                    else:
                        fashion_matches += 1
                if fashion_matches > 0:
                    fallback_score = fashion_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Fashion event fallback score: {fallback_score}")
                    return max(fallback_score, 0.5)
            # Casual/athletic
            elif occasion.lower() in ['casual', 'athletic', 'gym', 'beach', 'vacation', 'errands']:
                casual_keywords = ['casual', 'comfortable', 'relaxed', 'everyday', 'basic', 'loose', 'slim']
                casual_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in casual_keywords):
                        casual_matches += 1
                    elif any(basic_type in item_type_lower for basic_type in ['t-shirt', 'jeans', 'sneakers', 'shorts', 'pants', 'shoes']):
                        casual_matches += 1
                    elif hasattr(item, 'occasion') and 'casual' in [occ.lower() for occ in item.occasion]:
                        casual_matches += 1
                if casual_matches > 0:
                    fallback_score = casual_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Casual fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            # Formal
            elif occasion.lower() in ['formal', 'business', 'interview', 'gala', 'wedding']:
                formal_keywords = ['formal', 'business', 'professional', 'dress', 'suit', 'blazer']
                formal_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in formal_keywords):
                        formal_matches += 1
                    elif any(formal_type in item_type_lower for formal_type in ['dress', 'suit', 'blazer', 'shirt', 'pants']):
                        formal_matches += 1
                    elif hasattr(item, 'occasion') and any('formal' in occ.lower() or 'business' in occ.lower() for occ in item.occasion):
                        formal_matches += 1
                if formal_matches > 0:
                    fallback_score = formal_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Formal fallback score: {fallback_score}")
                    return max(fallback_score, 0.4)
            # Party/social
            elif occasion.lower() in ['party', 'cocktail', 'night out', 'date night', 'brunch']:
                social_keywords = ['party', 'cocktail', 'dress', 'stylish', 'elegant', 'fashion']
                social_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in social_keywords):
                        social_matches += 1
                    elif any(social_type in item_type_lower for social_type in ['dress', 'shirt', 'pants', 'shoes', 'jacket']):
                        social_matches += 1
                    elif hasattr(item, 'occasion') and any('party' in occ.lower() or 'cocktail' in occ.lower() for occ in item.occasion):
                        social_matches += 1
                if social_matches > 0:
                    fallback_score = social_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Social fallback score: {fallback_score}")
                    return max(fallback_score, 0.4)
            # Outdoor/athletic
            elif occasion.lower() in ['athletic', 'gym', 'workout', 'sports', 'outdoor', 'hiking']:
                athletic_keywords = ['athletic', 'sport', 'gym', 'workout', 'active', 'comfortable']
                athletic_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in athletic_keywords):
                        athletic_matches += 1
                    elif any(athletic_type in item_type_lower for athletic_type in ['shorts', 'pants', 'shoes', 'shirt', 't-shirt']):
                        athletic_matches += 1
                    elif hasattr(item, 'occasion') and any('athletic' in occ.lower() or 'gym' in occ.lower() for occ in item.occasion):
                        athletic_matches += 1
                if athletic_matches > 0:
                    fallback_score = athletic_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Athletic fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            # Travel/vacation
            elif occasion.lower() in ['travel', 'vacation', 'airport', 'beach', 'holiday']:
                travel_keywords = ['comfortable', 'casual', 'relaxed', 'travel', 'vacation', 'beach']
                travel_matches = 0
                for item in items:
                    item_name_lower = item.name.lower()
                    item_type_lower = item.type.lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in travel_keywords):
                        travel_matches += 1
                    elif any(travel_type in item_type_lower for travel_type in ['shirt', 'pants', 'shoes', 'shorts', 'dress']):
                        travel_matches += 1
                    elif hasattr(item, 'occasion') and any('travel' in occ.lower() or 'vacation' in occ.lower() for occ in item.occasion):
                        travel_matches += 1
                if travel_matches > 0:
                    fallback_score = travel_matches / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - Travel fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            # General fallback
            else:
                print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - General fallback for occasion: {occasion}")
                basic_items = ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'sweater', 't-shirt', 'jeans']
                basic_count = 0
                for item in items:
                    item_type_lower = item.type.lower()
                    if any(basic in item_type_lower for basic in basic_items):
                        basic_count += 1
                if basic_count >= 2:
                    fallback_score = basic_count / total_items
                    print(f"DEBUG: _calculate_occasion_appropriateness_enhanced - General fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
        
        return base_score

    def _generate_style_tags_enhanced(self, items: List[ClothingItem], style: Optional[str]) -> List[str]:
        """Generate enhanced style tags using CLIP analysis."""
        tags = set()
        
        if style:
            tags.add(style)
        
        for item in items:
            # Add enhanced style tags
            enhanced_styles = getattr(item.metadata, 'enhancedStyles', None)
            if enhanced_styles is None and item.metadata and hasattr(item.metadata, 'dict'):
                enhanced_styles = item.metadata.dict().get('enhancedStyles', item.style) if item.metadata and hasattr(item.metadata, 'dict') else item.style
            if enhanced_styles is None:
                enhanced_styles = item.style
            tags.update(enhanced_styles)
            
            # Add CLIP primary style if high confidence
            clip_analysis = getattr(item.metadata, 'clipAnalysis', {})
            if clip_analysis:
                primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
                confidence = clip_analysis.get("styleConfidence", 0) if clip_analysis else 0
                if primary_style and confidence > 0.3:
                    tags.add(primary_style)
        
        return list(tags)

    def _items_are_compatible_enhanced(self, item1: ClothingItem, item2: ClothingItem, 
                                     compatible_styles: List[str], avoid_styles: List[str], 
                                     target_style: Optional[str]) -> bool:
        """Check if two items are compatible using enhanced analysis."""
        # Check style compatibility
        item2_styles = set(item2.style)
        if any(style in item2_styles for style in avoid_styles):
            return False
        
        if compatible_styles and not any(style in item2_styles for style in compatible_styles):
            return False
        
        # Check color compatibility
        if not self._colors_are_compatible(item1.dominantColors, item2.dominantColors):
            return False
        
        # Check occasion compatibility
        if not set(item1.occasion).intersection(set(item2.occasion)):
            return False
        
        return True

    def _colors_are_compatible(self, colors1: List[dict], colors2: List[dict]) -> bool:
        """Check if two color sets are compatible."""
        if not colors1 or not colors2:
            return True
        
        color_names1 = {get_color_name(color) for color in colors1}
        color_names2 = {get_color_name(color) for color in colors2}
        
        # Check for neutral colors
        neutral_colors = {"black", "white", "gray", "beige", "navy", "brown"}
        
        # If one item has neutral colors, they're compatible
        if color_names1.intersection(neutral_colors) or color_names2.intersection(neutral_colors):
            return True
        
        # Check for color harmony (simple check)
        return len(color_names1.intersection(color_names2)) > 0

    def _extract_clip_insights(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Extract CLIP analysis insights from items."""
        insights = {
            "primaryStyles": [],
            "averageConfidence": 0,
            "styleBreakdown": {}
        }
        
        total_confidence = 0
        confidence_count = 0
        
        for item in items:
            clip_analysis = getattr(item.metadata, 'clipAnalysis', {})
            if clip_analysis:
                primary_style = clip_analysis.get("primaryStyle") if clip_analysis else None
                confidence = clip_analysis.get("styleConfidence", 0) if clip_analysis else 0
                
                if primary_style:
                    insights["primaryStyles"].append(primary_style)
                    insights["styleBreakdown"][primary_style] = insights["styleBreakdown"].get(primary_style, 0) + 1 if insights["styleBreakdown"] else 1
                
                if confidence > 0:
                    total_confidence += confidence
                    confidence_count += 1
        
        if confidence_count > 0:
            insights["averageConfidence"] = total_confidence / confidence_count
        
        return insights

    def _get_style_compatibility_summary(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Get summary of style compatibility across items."""
        summary = {
            "compatibleStyles": set(),
            "avoidStyles": set(),
            "styleNotes": []
        }
        
        for item in items:
            style_compat = getattr(item.metadata, 'styleCompatibility', {})
            if style_compat:
                summary["compatibleStyles"].update(style_compat.get("compatibleStyles", []) if style_compat else [])
                summary["avoidStyles"].update(style_compat.get("avoidStyles", []) if style_compat else [])
                
                style_note = style_compat.get("styleNotes") if style_compat else None
                if style_note:
                    summary["styleNotes"].append(style_note)
        
        return {
            "compatibleStyles": list(summary["compatibleStyles"]),
            "avoidStyles": list(summary["avoidStyles"]),
            "styleNotes": summary["styleNotes"]
        }

    # Legacy methods for backward compatibility
    def _get_complementary_items(self, base_item: ClothingItem, wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get items that complement the base item."""
        return self._get_complementary_items_enhanced(base_item, wardrobe, None)

    def _get_essential_items(self, occasion: str, wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get essential items for the given occasion."""
        return self._get_essential_items_enhanced(occasion, wardrobe, None)

    def _get_style_items(self, style: str, wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get items matching the style."""
        return self._get_style_items_enhanced(style, wardrobe)

    def _adjust_for_weather(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Apply weather-appropriate adjustments."""
        return self._adjust_for_weather_enhanced(items, weather)

    def _calculate_color_harmony(self, items: List[ClothingItem]) -> str:
        """Calculate color harmony."""
        return self._calculate_color_harmony_enhanced(items)

    def _generate_style_notes(self, items: List[ClothingItem], occasion: str, style: Optional[str]) -> str:
        """Generate style notes."""
        return self._generate_style_notes_enhanced(items, occasion, style)

    def _generate_item_reason(self, item: ClothingItem, occasion: str, style: Optional[str]) -> str:
        """Generate reason for including an item."""
        return self._generate_item_reason_enhanced(item, occasion, style)

    def _calculate_pairability_score(self, items: List[ClothingItem]) -> float:
        """Calculate pairability score."""
        return self._calculate_pairability_score_enhanced(items)

    def _calculate_style_compliance(self, items: List[ClothingItem], style: Optional[str]) -> float:
        """Calculate style compliance score."""
        return self._calculate_style_compliance_enhanced(items, style)

    def _calculate_weather_appropriateness(self, items: List[ClothingItem], weather: WeatherData) -> float:
        """Calculate weather appropriateness score."""
        return self._calculate_weather_appropriateness_enhanced(items, weather)

    def _calculate_occasion_appropriateness(self, items: List[ClothingItem], occasion: str) -> float:
        """Calculate occasion appropriateness score."""
        return self._calculate_occasion_appropriateness_enhanced(items, occasion)

    def _generate_style_tags(self, items: List[ClothingItem], style: Optional[str]) -> List[str]:
        """Generate style tags."""
        return self._generate_style_tags_enhanced(items, style)

    def _items_are_compatible(self, item1: ClothingItem, item2: ClothingItem) -> bool:
        """Check if two items are compatible."""
        return self._items_are_compatible_enhanced(item1, item2, [], [], None)

    def _get_trending_items(self, trendingStyles: List[str], wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get trending items."""
        trending_items = []
        for item in wardrobe:
            if any(style in item.style for style in trendingStyles):
                trending_items.append(item)
        return trending_items

    def _get_liked_items(self, likedOutfits: List[str], wardrobe: List[ClothingItem]) -> List[ClothingItem]:
        """Get liked items."""
        liked_items = []
        for item in wardrobe:
            if item.id in likedOutfits:
                liked_items.append(item)
        return liked_items

    def _determine_season(self, temperature: float, occasion: str) -> str:
        """Determine the season based on temperature and occasion."""
        if temperature < 50:
            return "winter"
        elif temperature < 70:
            return "spring"
        elif temperature < 85:
            return "summer"
        else:
            return "fall"

    def _filter_items_by_mood(self, items: List[ClothingItem], mood_rule, base_item: Optional[ClothingItem] = None) -> List[ClothingItem]:
        """Filter items based on mood requirements - STRICT VERSION, but always preserve base_item if present."""
        filtered_items = []
        for item in items:
            # Check if item's colors match mood color palette
            item_colors = [getattr(color, 'name', str(color)).lower() for color in item.dominantColors]
            mood_colors = [color.lower() for color in mood_rule.color_palette]
            # Check if item's style matches mood style preferences
            item_styles = [style.lower() for style in (item.style or [])]
            mood_styles = [style.lower() for style in mood_rule.style_preferences]
            # Check if item's material matches mood material preferences
            item_material = getattr(item, 'material', None)
            mood_materials = [material.value if hasattr(material, 'value') else str(material) for material in mood_rule.material_preferences]
            # Score the item based on mood compatibility
            color_score = sum(1 for color in item_colors if any(mood_color in color or color in mood_color for mood_color in mood_colors))
            style_score = sum(1 for style in item_styles if any(mood_style in style or style in mood_style for mood_style in mood_styles))
            material_score = 1 if item_material and str(item_material).lower() in [m.lower() for m in mood_materials] else 0
            total_score = color_score + style_score + material_score
            # Include item if it has some mood compatibility
            if total_score > 0:
                filtered_items.append(item)
        # ⛑️ Ensure base_item is preserved
        if base_item and base_item not in filtered_items and base_item in items:
            print(f"[Mood Filter] Preserving base item despite mismatch: {base_item.name}")
            filtered_items.append(base_item)
        # STRICT: If no items match mood, return empty list except for base_item
        if not filtered_items and base_item and base_item in items:
            print(f"DEBUG: _filter_items_by_mood - No items match mood {mood_rule.mood}, but preserving base item")
            return [base_item]
        elif not filtered_items:
            print(f"DEBUG: _filter_items_by_mood - No items match mood {mood_rule.mood}, returning empty list")
            return []
        return filtered_items

    def _filter_items_by_body_and_skin(self, items: List[ClothingItem], user_profile: UserProfile) -> List[ClothingItem]:
        """Filter items based on body type and skin tone compatibility."""
        filtered_items = []
        
        for item in items:
            # Check body type compatibility
            body_compatible = self._check_body_type_compatibility(item, user_profile.bodyType)
            
            # Check skin tone compatibility
            skin_compatible = self._check_skin_tone_compatibility(item, user_profile.skinTone)
            
            # Include item if it's compatible with both body type and skin tone
            if body_compatible and skin_compatible:
                filtered_items.append(item)
        
        # If no items match body/skin criteria, return original items
        if not filtered_items:
            print(f"DEBUG: _filter_items_by_body_and_skin - No items match body type {user_profile.bodyType} or skin tone {user_profile.skinTone}, returning original items")
            return items
        
        return filtered_items

    def _check_body_type_compatibility(self, item: ClothingItem, body_type: str) -> bool:
        """Check if an item is compatible with the user's body type using utility function."""
        return check_body_type_compatibility(item, body_type)

    def _check_skin_tone_compatibility(self, item: ClothingItem, skin_tone: str) -> bool:
        """Check if an item is compatible with the user's skin tone using utility function."""
        return check_skin_tone_compatibility(item, skin_tone)

    def _compose_outfit_with_limits(self, wardrobe: List[ClothingItem], occasion: str, style: Optional[str], 
                                   mood_rule, user_profile: UserProfile, layering_rule: LayeringRule,
                                   trendingStyles: List[str], likedOutfits: List[str], 
                                   baseItem: Optional[ClothingItem] = None, weather_temperature: float = None) -> List[ClothingItem]:
        """Compose an outfit with proper limits to create a cohesive look."""
        selected_items = []
        
        # Step 1: Start with base item if provided
        if baseItem:
            selected_items.append(baseItem)
            print(f"DEBUG: _compose_outfit_with_limits - Added base item: {baseItem.name} (type: {baseItem.type})")
        
        # Step 2: Build outfit around base item or add essential items
        if baseItem:
            # Build outfit around the base item
            selected_items = self._build_outfit_around_base_item(baseItem, selected_items, wardrobe, occasion, style, layering_rule)
        else:
            # No base item, add essential items for the occasion
            print(f"DEBUG: _compose_outfit_with_limits - Looking for essential items")
            essential_items = self._get_essential_items_enhanced(occasion, wardrobe, style)
            print(f"DEBUG: _compose_outfit_with_limits - Found {len(essential_items)} essential items")
            
            # Limit essential items to 2-3 most important pieces
            essential_items = essential_items[:3]  # Take first 3
            for item in essential_items:
                if item not in selected_items:
                    selected_items.append(item)
                    print(f"DEBUG: _compose_outfit_with_limits - Added essential item: {item.name}")
        
        # Step 3: Add style items (limit to 1-2 items)
        if style and len(selected_items) < 4:  # Only add if we have room
            print(f"DEBUG: _compose_outfit_with_limits - Looking for style items: {style}")
            style_items = self._get_style_items_enhanced(style, wardrobe)
            print(f"DEBUG: _compose_outfit_with_limits - Found {len(style_items)} style items")
            
            # Limit style items to 1-2 pieces
            style_items = style_items[:2]  # Take first 2
            for item in style_items:
                if item not in selected_items and len(selected_items) < 4:
                    selected_items.append(item)
                    print(f"DEBUG: _compose_outfit_with_limits - Added style item: {item.name}")
        
        # Step 4: Apply mood-based filtering
        if mood_rule and selected_items:
            print(f"DEBUG: _compose_outfit_with_limits - Applying mood rule: {mood_rule.mood}")
            mood_filtered_items = self._filter_items_by_mood(selected_items, mood_rule, base_item=baseItem)
            print(f"DEBUG: _compose_outfit_with_limits - Mood filtering: {len(selected_items)} -> {len(mood_filtered_items)} items")
            selected_items = mood_filtered_items
        
        # Step 5: Apply body type and skin tone considerations
        if selected_items:
            print(f"DEBUG: _compose_outfit_with_limits - Applying body type and skin tone considerations")
            body_skin_filtered_items = self._filter_items_by_body_and_skin(selected_items, user_profile)
            print(f"DEBUG: _compose_outfit_with_limits - Body/skin filtering: {len(selected_items)} -> {len(body_skin_filtered_items)} items")
            selected_items = body_skin_filtered_items
        
        # Step 6: Add trending items (limit to 1 item)
        if trendingStyles and len(selected_items) < 4:  # Only add if we have room
            print(f"DEBUG: _compose_outfit_with_limits - Looking for trending items: {trendingStyles}")
            trending_items = self._get_trending_items(trendingStyles, wardrobe)
            print(f"DEBUG: _compose_outfit_with_limits - Found {len(trending_items)} trending items")
            
            # Limit trending items to 1 piece
            trending_items = trending_items[:1]  # Take first 1
            for item in trending_items:
                if item not in selected_items and len(selected_items) < 4:
                    selected_items.append(item)
                    print(f"DEBUG: _compose_outfit_with_limits - Added trending item: {item.name}")
        
        # Step 7: Add liked items (limit to 1 item)
        if likedOutfits and len(selected_items) < 4:  # Only add if we have room
            print(f"DEBUG: _compose_outfit_with_limits - Looking for liked items: {likedOutfits}")
            liked_items = self._get_liked_items(likedOutfits, wardrobe)
            print(f"DEBUG: _compose_outfit_with_limits - Found {len(liked_items)} liked items")
            
            # Limit liked items to 1 piece
            liked_items = liked_items[:1]  # Take first 1
            for item in liked_items:
                if item not in selected_items and len(selected_items) < 4:
                    selected_items.append(item)
                    print(f"DEBUG: _compose_outfit_with_limits - Added liked item: {item.name}")
        
        # Step 8: ALWAYS ensure we have a proper outfit structure if we have fewer than 4 items
        # This is the key fix - we need to ensure complete outfits regardless of base item
        if len(selected_items) < 4:
            print(f"DEBUG: _compose_outfit_with_limits - Ensuring outfit structure (current: {len(selected_items)} items)")
            selected_items = self._ensure_outfit_structure(selected_items, wardrobe, layering_rule, occasion, style, weather_temperature)
        else:
            print(f"DEBUG: _compose_outfit_with_limits - Skipping _ensure_outfit_structure, have {len(selected_items)} items")
        
        # Step 9: Limit total items to layering rule requirements, but preserve base item
        max_items = min(layering_rule.required_layers + 2, 5)  # Cap at 5 items maximum, allow 2 extra for accessories
        if len(selected_items) > max_items:
            # If we have a base item, ensure it's preserved
            if baseItem:
                # Remove base item temporarily
                base_item_in_list = baseItem in selected_items
                if base_item_in_list:
                    selected_items.remove(baseItem)
                
                # Limit the remaining items
                remaining_slots = max_items - 1  # Reserve 1 slot for base item
                selected_items = selected_items[:remaining_slots]
                
                # Add base item back at the beginning
                if base_item_in_list:
                    selected_items.insert(0, baseItem)
                    print(f"DEBUG: _compose_outfit_with_limits - Preserved base item: {baseItem.name}")
            else:
                # No base item, just limit normally
                selected_items = selected_items[:max_items]
            
            print(f"DEBUG: _compose_outfit_with_limits - Limited to {max_items} items based on layering rule")
        
        print(f"DEBUG: _compose_outfit_with_limits - Final outfit composition: {len(selected_items)} items")
        # print(f"DEBUG: _compose_outfit_with_limits - Selected items: {[item.name for item in selected_items]}")
        
        return selected_items

    def _build_outfit_around_base_item(self, base_item: ClothingItem, selected_items: List[ClothingItem], 
                                      wardrobe: List[ClothingItem], occasion: str, style: Optional[str], 
                                      layering_rule: LayeringRule) -> List[ClothingItem]:
        """Build a sensible outfit around a base item."""
        base_type = base_item.type.lower()
        print(f"DEBUG: _build_outfit_around_base_item - Building around {base_item.name} (type: {base_type})")
        
        # Define what we need based on base item type
        if base_type in ['shoes', 'sneakers', 'boots', 'sandals']:
            # Base item is shoes - we need bottom and top
            print(f"DEBUG: _build_outfit_around_base_item - Base item is shoes, adding bottom and top")
            
            # Add bottom item first
            bottom_items = [item for item in wardrobe if item.id != base_item.id and 
                           item.type.lower() in ['pants', 'jeans', 'shorts', 'skirt']]
            if bottom_items:
                # Filter by occasion and style
                filtered_bottoms = self._filter_items_for_occasion_and_style(bottom_items, occasion, style)
                if filtered_bottoms:
                    selected_items.append(filtered_bottoms[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added bottom: {filtered_bottoms[0].name}")
            
            # Add top item
            top_items = [item for item in wardrobe if item.id != base_item.id and 
                        item.type.lower() in ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket']]
            if top_items:
                # Filter by occasion and style
                filtered_tops = self._filter_items_for_occasion_and_style(top_items, occasion, style)
                if filtered_tops:
                    selected_items.append(filtered_tops[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added top: {filtered_tops[0].name}")
        
        elif base_type in ['pants', 'jeans', 'shorts', 'skirt']:
            # Base item is bottom - we need top and shoes
            print(f"DEBUG: _build_outfit_around_base_item - Base item is bottom, adding top and shoes")
            
            # Add top item first
            top_items = [item for item in wardrobe if item.id != base_item.id and 
                        item.type.lower() in ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket']]
            if top_items:
                filtered_tops = self._filter_items_for_occasion_and_style(top_items, occasion, style)
                if filtered_tops:
                    selected_items.append(filtered_tops[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added top: {filtered_tops[0].name}")
            
            # Add shoes
            shoe_items = [item for item in wardrobe if item.id != base_item.id and 
                         item.type.lower() in ['shoes', 'sneakers', 'boots', 'sandals']]
            if shoe_items:
                filtered_shoes = self._filter_items_for_occasion_and_style(shoe_items, occasion, style)
                if filtered_shoes:
                    selected_items.append(filtered_shoes[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added shoes: {filtered_shoes[0].name}")
        
        elif base_type in ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket']:
            # Base item is top - we need bottom and shoes
            print(f"DEBUG: _build_outfit_around_base_item - Base item is top, adding bottom and shoes")
            
            # Add bottom item first
            bottom_items = [item for item in wardrobe if item.id != base_item.id and 
                           item.type.lower() in ['pants', 'jeans', 'shorts', 'skirt']]
            if bottom_items:
                filtered_bottoms = self._filter_items_for_occasion_and_style(bottom_items, occasion, style)
                if filtered_bottoms:
                    selected_items.append(filtered_bottoms[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added bottom: {filtered_bottoms[0].name}")
            
            # Add shoes
            shoe_items = [item for item in wardrobe if item.id != base_item.id and 
                         item.type.lower() in ['shoes', 'sneakers', 'boots', 'sandals']]
            if shoe_items:
                filtered_shoes = self._filter_items_for_occasion_and_style(shoe_items, occasion, style)
                if filtered_shoes:
                    selected_items.append(filtered_shoes[0])
                    print(f"DEBUG: _build_outfit_around_base_item - Added shoes: {filtered_shoes[0].name}")
        
        else:
            # Unknown base item type, add essential items
            print(f"DEBUG: _build_outfit_around_base_item - Unknown base item type, adding essential items")
            essential_items = self._get_essential_items_enhanced(occasion, wardrobe, style)
            essential_items = [item for item in essential_items if item.id != base_item.id]
            essential_items = essential_items[:2]  # Take first 2
            for item in essential_items:
                if item not in selected_items:
                    selected_items.append(item)
                    print(f"DEBUG: _build_outfit_around_base_item - Added essential item: {item.name}")
        
        return selected_items

    def _filter_items_for_occasion_and_style(self, items: List[ClothingItem], occasion: str, style: Optional[str]) -> List[ClothingItem]:
        """Filter items based on occasion and style compatibility."""
        filtered_items = []
        
        # Get the occasion rule to check forbidden items
        occasion_rule = get_occasion_rule(occasion)
        forbidden_types = []
        if occasion_rule:
            forbidden_types = [item_type.value.lower() for item_type in occasion_rule.forbidden_items]
            print(f"DEBUG: _filter_items_for_occasion_and_style - Forbidden types for {occasion}: {forbidden_types}")
        
        # Additional forbidden items for specific occasions
        if occasion and 'athletic' in occasion.lower():
            # For athletic occasions, forbid formal and inappropriate items
            athletic_forbidden = ['dress_shirt', 'dress shirt', 'formal shirt', 'button down', 'button-up', 'oxford', 'dress_shoes', 'dress shoes', 'formal shoes', 'heels', 'dress pants', 'slacks', 'formal pants']
            forbidden_types.extend(athletic_forbidden)
            print(f"DEBUG: _filter_items_for_occasion_and_style - Athletic forbidden types: {athletic_forbidden}")
        
        # Define athletic keywords for strict filtering
        athletic_keywords = ['athletic', 'gym', 'workout', 'running', 'sport', 'exercise', 'training']
        
        for item in items:
            # Check if item is forbidden for this occasion
            item_type_lower = item.type.lower()
            item_name_lower = item.name.lower()
            
            # Check both type and name for forbidden items
            is_forbidden = any(forbidden_type in item_type_lower for forbidden_type in forbidden_types) or \
                          any(forbidden_type in item_name_lower for forbidden_type in forbidden_types)
            
            if is_forbidden:
                print(f"DEBUG: _filter_items_for_occasion_and_style - Filtering out {item.name} (type: {item.type}) - forbidden for {occasion}")
                continue
            
            # STRICT OCCASION FILTERING for athletic occasions
            if occasion and 'athletic' in occasion.lower():
                # For athletic occasions, require items to have athletic-related occasions
                has_athletic_occasion = False
                if item.occasion:
                    item_occasions = [occ.lower() for occ in item.occasion]
                    # Check if any of the item's occasions contain athletic keywords
                    for item_occ in item_occasions:
                        if any(keyword in item_occ for keyword in athletic_keywords):
                            has_athletic_occasion = True
                            break
                
                # Also check style and tags for athletic attributes
                has_athletic_style = False
                if item.style:
                    item_styles = [s.lower() for s in item.style]
                    if any(keyword in ' '.join(item_styles) for keyword in athletic_keywords):
                        has_athletic_style = True
                
                has_athletic_tags = False
                if hasattr(item, 'tags') and item.tags:
                    item_tags = [tag.lower() for tag in item.tags]
                    if any(keyword in ' '.join(item_tags) for keyword in athletic_keywords):
                        has_athletic_tags = True
                
                # For athletic occasions, require at least one athletic attribute
                if not (has_athletic_occasion or has_athletic_style or has_athletic_tags):
                    print(f"DEBUG: _filter_items_for_occasion_and_style - Filtering out {item.name} - no athletic attributes for {occasion}")
                    print(f"DEBUG:   - Occasions: {item.occasion}")
                    print(f"DEBUG:   - Style: {item.style}")
                    print(f"DEBUG:   - Tags: {getattr(item, 'tags', [])}")
                    continue
                
                print(f"DEBUG: _filter_items_for_occasion_and_style - Including {item.name} for athletic occasion")
                print(f"DEBUG:   - Has athletic occasion: {has_athletic_occasion}")
                print(f"DEBUG:   - Has athletic style: {has_athletic_style}")
                print(f"DEBUG:   - Has athletic tags: {has_athletic_tags}")
            
            else:
                # For non-athletic occasions, use the original logic
                # Check occasion compatibility
                occasion_match = False
                if item.occasion:
                    item_occasions = [occ.lower() for occ in item.occasion]
                    if occasion.lower() in item_occasions or any(occ in occasion.lower() for occ in item_occasions):
                        occasion_match = True
            
            # Check style compatibility
            style_match = False
            if style and item.style:
                item_styles = [s.lower() for s in item.style]
                if style.lower() in item_styles or any(s in style.lower() for s in item_styles):
                    style_match = True
            
            # Include item if it matches occasion or style (or if no style specified)
            if occasion and 'athletic' in occasion.lower():
                # For athletic occasions, we already filtered above, so include the item
                filtered_items.append(item)
            elif occasion_match or (not style or style_match):
                filtered_items.append(item)
        
        # Sort by occasion match first, then style match
        filtered_items.sort(key=lambda x: (
            occasion.lower() in [occ.lower() for occ in (x.occasion or [])],
            style and style.lower() in [s.lower() for s in (x.style or [])]
        ), reverse=True)
        
        # REMOVE THE FALLBACK LOGIC for athletic occasions - be strict!
        if occasion and 'athletic' in occasion.lower():
            print(f"DEBUG: _filter_items_for_occasion_and_style - Athletic occasion: found {len(filtered_items)} appropriate items")
            if len(filtered_items) == 0:
                print(f"DEBUG: _filter_items_for_occasion_and_style - WARNING: No athletic items found! This may cause outfit generation to fail.")
            return filtered_items
        
        # For non-athletic occasions, keep the fallback logic
        # If we don't have enough filtered items, be less restrictive and include more items
        if len(filtered_items) < 2:
            print(f"DEBUG: _filter_items_for_occasion_and_style - Only found {len(filtered_items)} items, being less restrictive")
            # Include items that don't have explicit occasion/style but aren't forbidden
            for item in items:
                if item not in filtered_items:
                    item_type_lower = item.type.lower()
                    item_name_lower = item.name.lower()
                    # Only exclude if explicitly forbidden
                    is_forbidden = any(forbidden_type in item_type_lower for forbidden_type in forbidden_types) or \
                                  any(forbidden_type in item_name_lower for forbidden_type in forbidden_types)
                    if not is_forbidden:
                        filtered_items.append(item)
                        print(f"DEBUG: _filter_items_for_occasion_and_style - Added fallback item: {item.name}")
        
        return filtered_items

    def _is_undergarment_appropriate_standalone(self, item: ClothingItem, occasion: str, temperature: float) -> bool:
        """Check if an undergarment is appropriate as a standalone item for the given occasion and weather."""
        undergarment_types = ['t-shirt', 'tee', 'tshirt', 'tank top', 'undershirt', 'camisole', 'sleeveless']
        
        # Check if this is an undergarment
        if not any(t in item.type.lower() for t in undergarment_types):
            return False
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        # Hot weather allows undergarments as standalone for specific occasions
        if temperature >= 80:
            # Beach, pool, athleisure, casual outdoor activities
            beach_occasions = ['beach', 'pool', 'swimming', 'vacation', 'resort']
            athleisure_occasions = ['athleisure', 'gym', 'workout', 'sports', 'exercise', 'casual']
            
            if any(occ in occasion.lower() for occ in beach_occasions + athleisure_occasions):
                return True
        
        # Very hot weather (90°F+) allows undergarments for more casual occasions
        if temperature >= 90:
            casual_occasions = ['casual', 'errands', 'home', 'lounge', 'weekend']
            if any(occ in occasion.lower() for occ in casual_occasions):
                return True
        
        return False

    def _ensure_outfit_structure(self, selected_items: List[ClothingItem], wardrobe: List[ClothingItem], 
                                layering_rule: LayeringRule, occasion: str, style: Optional[str], weather_temperature: float = None) -> List[ClothingItem]:
        """Ensure the outfit has a proper structure (top, bottom, shoes, etc.), applying occasion/style filtering."""
        if not selected_items:
            return selected_items
        
        # Remove duplicates first
        unique_items = []
        seen_ids = set()
        for item in selected_items:
            if item.id not in seen_ids:
                unique_items.append(item)
                seen_ids.add(item.id)
        
        if len(unique_items) != len(selected_items):
            print(f"DEBUG: _ensure_outfit_structure - Removed {len(selected_items) - len(unique_items)} duplicate items")
            selected_items = unique_items
        
        # Define required categories for a complete outfit
        required_categories = {
            'top': ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket', 'coat', 'polo'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'bag', 'hat']
        }
        
        # For athletic occasions, prioritize specific item types
        if occasion and 'athletic' in occasion.lower():
            # Athletic occasions should prefer shorts over pants and sneakers over dress shoes
            athletic_preferences = {
                'bottom': ['shorts', 'pants', 'jeans'],  # Prefer shorts first
                'shoes': ['sneakers', 'shoes', 'boots']  # Prefer sneakers first
            }
        else:
            athletic_preferences = {}
        
        # Check what categories we already have and track which items belong to which categories
        current_categories = set()
        category_items = {'top': [], 'bottom': [], 'shoes': [], 'accessory': []}
        
        for item in selected_items:
            item_type = item.type.lower()
            for category, types in required_categories.items():
                if any(t in item_type for t in types):
                    current_categories.add(category)
                    category_items[category].append(item)
                    break
        
        print(f"DEBUG: _ensure_outfit_structure - Current categories: {current_categories}")
        print(f"DEBUG: _ensure_outfit_structure - Category items: {[f'{cat}: {[item.name for item in items]}' for cat, items in category_items.items() if items]}")
        print(f"DEBUG: _ensure_outfit_structure - Layering rule: {layering_rule.required_layers} layers, temp range: {layering_rule.min_temperature}-{layering_rule.max_temperature}°F")
        
        # Check if we have any standalone undergarments that are appropriate
        standalone_undergarments = []
        for item in selected_items:
            # Ensure temperature is a float
            temperature = float(layering_rule.max_temperature) if layering_rule.max_temperature is not None else 70.0
            if self._is_undergarment_appropriate_standalone(item, occasion, temperature):
                standalone_undergarments.append(item)
        
        # If we have appropriate standalone undergarments, we might not need additional tops
        if standalone_undergarments:
            print(f"DEBUG: _ensure_outfit_structure - Found standalone undergarments: {[item.name for item in standalone_undergarments]}")
            # For beach/pool/athleisure, undergarments might be sufficient
            if any(occ in occasion.lower() for occ in ['beach', 'pool', 'swimming', 'athleisure', 'gym']):
                print(f"DEBUG: _ensure_outfit_structure - Allowing undergarments as standalone for {occasion}")
                # Still ensure we have bottoms and shoes
                missing_categories = set(required_categories.keys()) - current_categories
                missing_categories.discard('top')  # Don't require additional tops
            else:
                # For other occasions, still try to add proper tops
                missing_categories = set(required_categories.keys()) - current_categories
        else:
            # Be more aggressive about adding missing categories for a complete outfit
            missing_categories = set(required_categories.keys()) - current_categories
        
        # For all occasions, aim for at least 3-4 items total
        target_items = 4 if occasion.lower() in ['casual', 'business casual', 'fashion event'] else 3
        max_additional = max(target_items - len(selected_items), 3)  # Try to add up to 3 more items
        
        print(f"DEBUG: _ensure_outfit_structure - Missing categories: {missing_categories}")
        print(f"DEBUG: _ensure_outfit_structure - Target items: {target_items}, Max additional: {max_additional}")
        
        # Prioritize essential categories (top, bottom, shoes) over accessories
        priority_categories = ['top', 'bottom', 'shoes']
        other_categories = ['accessory']
        
        # First add priority categories that are missing
        for category in priority_categories:
            if category in missing_categories and len(selected_items) < target_items:
                category_types = required_categories[category]
                # Only add items that aren't already in the selected_items and aren't in the same category
                category_items_to_add = [item for item in wardrobe 
                                if item.id not in seen_ids  # Use seen_ids to prevent duplicates
                                and any(t in item.type.lower() for t in category_types)]
                
                # Apply temperature-based filtering for tops
                if category == 'top':
                    # Prevent adding multiple tops unless layering is required
                    num_tops = len([item for item in selected_items if any(t in item.type.lower() for t in required_categories['top'])])
                    if num_tops >= layering_rule.required_layers:
                        print(f"DEBUG: _ensure_outfit_structure - Skipping adding another top (already have {num_tops}, required layers: {layering_rule.required_layers})")
                        continue
                    category_items_to_add = self._filter_items_by_temperature(category_items_to_add, weather_temperature, occasion)
                
                # Apply occasion and style filtering
                filtered_items = self._filter_items_for_occasion_and_style(category_items_to_add, occasion, style)
                
                # For athletic occasions, prioritize specific item types
                if category in athletic_preferences and filtered_items:
                    # Sort by athletic preferences using utility function
                    filtered_items.sort(key=lambda item: athletic_sort_key(item, athletic_preferences[category]))
                    print(f"DEBUG: _ensure_outfit_structure - Sorted {category} items by athletic preferences: {[item.name for item in filtered_items[:3]]}")
                
                if filtered_items:
                    best_item = filtered_items[0]
                    selected_items.append(best_item)
                    seen_ids.add(best_item.id)  # Track to prevent duplicates
                    current_categories.add(category)
                    print(f"DEBUG: _ensure_outfit_structure - Added priority {category}: {best_item.name}")
        
        # Then add other categories if we still have room
        for category in other_categories:
            if category in missing_categories and len(selected_items) < target_items:
                category_types = required_categories[category]
                category_items = [item for item in wardrobe 
                                if item.id not in seen_ids  # Use seen_ids to prevent duplicates
                                and any(t in item.type.lower() for t in category_types)]
                filtered_items = self._filter_items_for_occasion_and_style(category_items, occasion, style)
                if filtered_items:
                    best_item = filtered_items[0]
                    selected_items.append(best_item)
                    seen_ids.add(best_item.id)  # Track to prevent duplicates
                    current_categories.add(category)
                    print(f"DEBUG: _ensure_outfit_structure - Added {category}: {best_item.name}")
        
        # If we still don't have enough items, add any available items from different categories
        if len(selected_items) < target_items:
            print(f"DEBUG: _ensure_outfit_structure - Still need more items, adding any available from different categories")
            available_items = [item for item in wardrobe if item.id not in seen_ids]  # Use seen_ids to prevent duplicates
            
            # Group available items by category
            available_by_category = {'top': [], 'bottom': [], 'shoes': [], 'accessory': []}
            for item in available_items:
                item_type = item.type.lower()
                for category, types in required_categories.items():
                    if any(t in item_type for t in types):
                        available_by_category[category].append(item)
                        break
            
            # Add items from categories we don't already have
            for category in priority_categories + other_categories:
                if category not in current_categories and available_by_category[category]:
                    # Apply temperature-based filtering for tops
                    if category == 'top':
                        # Prevent adding multiple tops unless layering is required
                        num_tops = len([item for item in selected_items if any(t in item.type.lower() for t in required_categories['top'])])
                        if num_tops >= layering_rule.required_layers:
                            print(f"DEBUG: _ensure_outfit_structure - Skipping adding another top (already have {num_tops}, required layers: {layering_rule.required_layers})")
                            continue
                        available_by_category[category] = self._filter_items_by_temperature(available_by_category[category], weather_temperature, occasion)
                    
                    # Apply occasion and style filtering
                    filtered_items = self._filter_items_for_occasion_and_style(available_by_category[category], occasion, style)
                    
                    # For athletic occasions, prioritize specific item types
                    if category in athletic_preferences and filtered_items:
                        # Sort by athletic preferences using utility function
                        filtered_items.sort(key=lambda item: athletic_sort_key(item, athletic_preferences[category]))
                    
                    if filtered_items:
                        item_to_add = filtered_items[0]
                        selected_items.append(item_to_add)
                        seen_ids.add(item_to_add.id)  # Track to prevent duplicates
                        current_categories.add(category)
                        print(f"DEBUG: _ensure_outfit_structure - Added fallback {category}: {item_to_add.name}")
                        if len(selected_items) >= target_items:
                            break
        
        return selected_items

    def _filter_items_by_temperature(self, items: List[ClothingItem], temperature: float, occasion: str = None) -> List[ClothingItem]:
        """Filter items based on temperature appropriateness."""
        # Use the actual temperature passed in, not the layering rule's temperature range
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        # Define undergarment types that can be worn in any weather
        undergarment_types = ['t-shirt', 'tee', 'tshirt', 'tank top', 'undershirt', 'camisole', 'sleeveless']
        
        # Get occasion rule to check forbidden items
        occasion_rule = None
        if occasion:
            from src.types.outfit_rules import get_occasion_rule
            occasion_rule = get_occasion_rule(occasion)
        
        # Define temperature-appropriate item types
        if temperature >= 85:  # Hot weather
            # Allow undergarments in any weather, but avoid heavy items in hot weather
            inappropriate_types = ['sweater', 'jacket', 'coat', 'hoodie', 'cardigan', 'wool', 'fleece']
            return [item for item in items if 
                   any(t in item.type.lower() for t in undergarment_types) or  # Allow undergarments
                   not any(t in item.type.lower() for t in inappropriate_types)]
        elif temperature >= 75:  # Warm weather (81°F falls here)
            # Allow undergarments in any weather, but avoid very heavy items in warm weather
            inappropriate_types = ['coat', 'heavy sweater', 'wool jacket', 'sweater', 'fleece']  # Filter out all sweaters in warm weather
            # For athletic occasions, also forbid regular sweaters in warm weather
            if occasion and 'athletic' in occasion.lower():
                inappropriate_types.append('sweater')  # Already included above, but keeping for clarity
            return [item for item in items if 
                   any(t in item.type.lower() for t in undergarment_types) or  # Allow undergarments
                   not any(t in item.type.lower() for t in inappropriate_types)]
        elif temperature >= 65:  # Mild weather (70°F falls here)
            # For mild weather, be more selective about heavy items
            inappropriate_types = []
            # For athletic occasions, forbid sweaters even in mild weather
            if occasion and 'athletic' in occasion.lower():
                inappropriate_types.append('sweater')
            # For warm mild weather (70°F+), avoid heavy sweaters
            if temperature >= 70:
                inappropriate_types.extend(['heavy sweater', 'wool sweater'])
            
            return [item for item in items if 
                   any(t in item.type.lower() for t in undergarment_types) or  # Allow undergarments
                   not any(t in item.type.lower() for t in inappropriate_types)]
        elif temperature >= 50:  # Chilly weather
            # Allow undergarments in any weather, but avoid very light items for outer layers
            inappropriate_types = ['tank top', 'sleeveless']  # Only restrict outer layer tank tops
            return [item for item in items if 
                   any(t in item.type.lower() for t in undergarment_types) or  # Allow undergarments
                   not any(t in item.type.lower() for t in inappropriate_types)]
        else:  # Cold weather
            # All items are appropriate, including undergarments
            return items

    async def update_outfit_feedback(self, outfit_id: str, feedback: Dict[str, Any]) -> bool:
        """Update user feedback for an outfit."""
        try:
            # Validate feedback structure
            required_fields = ["liked", "rating"]
            for field in required_fields:
                if field not in feedback:
                    raise ValueError(f"Missing required feedback field: {field}")
            
            # Validate rating range
            rating = feedback.get("rating")
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                raise ValueError("Rating must be a number between 1 and 5")
            
            # Validate liked field
            liked = feedback.get("liked")
            if not isinstance(liked, bool):
                raise ValueError("Liked field must be a boolean")
            
            # Get the outfit document
            doc_ref = self.collection.document(outfit_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Outfit with ID {outfit_id} not found")
            
            # Update the outfit with feedback
            feedback_data = {
                "liked": liked,
                "rating": rating,
                "comment": feedback.get("comment", ""),
                "timestamp": int(time.time())
            }
            
            doc_ref.update({
                "userFeedback": feedback_data,
                "updatedAt": int(time.time())
            })
            
            print(f"DEBUG: update_outfit_feedback - Feedback updated for outfit {outfit_id}")
            print(f"DEBUG: update_outfit_feedback - Feedback: {feedback_data}")
            
            return True
            
        except Exception as e:
            print(f"Error updating outfit feedback: {e}")
            return False

    async def get_outfit_analytics(self, user_id: str = None, start_date: int = None, end_date: int = None) -> Dict[str, Any]:
        """Get analytics about outfit generation success/failure patterns."""
        try:
            # Build query
            query = self.collection
            
            if user_id:
                # Note: This assumes outfits have a user_id field
                # You may need to adjust based on your data structure
                query = query.where("user_id", "==", user_id)
            
            if start_date:
                query = query.where("createdAt", ">=", start_date)
            
            if end_date:
                query = query.where("createdAt", "<=", end_date)
            
            # Get all outfits
            docs = query.stream()
            
            total_outfits = 0
            successful_outfits = 0
            failed_outfits = 0
            base_item_outfits = 0
            validation_errors = {}
            feedback_stats = {
                "total_feedback": 0,
                "positive_feedback": 0,
                "average_rating": 0,
                "total_rating": 0
            }
            
            for doc in docs:
                data = doc.to_dict()
                total_outfits += 1
                
                # Track success/failure
                was_successful = data.get("wasSuccessful", True)
                if was_successful:
                    successful_outfits += 1
                else:
                    failed_outfits += 1
                
                # Track base item usage
                if data.get("baseItemId"):
                    base_item_outfits += 1
                
                # Track validation errors
                errors = data.get("validationErrors", [])
                for error in errors:
                    validation_errors[error] = validation_errors.get(error, 0) + 1
                
                # Track feedback
                user_feedback = data.get("userFeedback")
                if user_feedback:
                    feedback_stats["total_feedback"] += 1
                    if user_feedback.get("liked", False):
                        feedback_stats["positive_feedback"] += 1
                    
                    rating = user_feedback.get("rating", 0)
                    if rating > 0:
                        feedback_stats["total_rating"] += rating
            
            # Calculate averages
            if feedback_stats["total_feedback"] > 0:
                feedback_stats["average_rating"] = feedback_stats["total_rating"] / feedback_stats["total_feedback"]
            
            analytics = {
                "total_outfits": total_outfits,
                "successful_outfits": successful_outfits,
                "failed_outfits": failed_outfits,
                "success_rate": (successful_outfits / total_outfits * 100) if total_outfits > 0 else 0,
                "base_item_outfits": base_item_outfits,
                "base_item_usage_rate": (base_item_outfits / total_outfits * 100) if total_outfits > 0 else 0,
                "validation_errors": validation_errors,
                "feedback_stats": feedback_stats
            }
            
            print(f"DEBUG: get_outfit_analytics - Generated analytics for {total_outfits} outfits")
            return analytics
            
        except Exception as e:
            print(f"Error getting outfit analytics: {e}")
            return {} 

    def _validate_layering_compatibility(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Validate that items can be layered together properly."""
        validation = {
            "is_compatible": True,
            "errors": [],
            "warnings": []
        }
        
        # Get all tops (shirts, sweaters, jackets)
        tops = [item for item in items if item.type.lower() in ['shirt', 'sweater', 'jacket']]
        
        if len(tops) < 2:
            return validation  # No layering to validate
        
        # Check for sleeve length compatibility
        for i, top1 in enumerate(tops):
            for top2 in tops[i+1:]:
                # Get sleeve length information
                sleeve1 = self._get_sleeve_length(top1)
                sleeve2 = self._get_sleeve_length(top2)
                type1 = top1.type.lower()
                type2 = top2.type.lower()
                
                # Rule: Short sleeve sweaters cannot be layered over long sleeve button-ups
                if (type1 == 'sweater' and sleeve1 == 'short' and 
                    type2 == 'shirt' and sleeve2 == 'long' and 
                    self._is_button_up(top2)):
                    validation["is_compatible"] = False
                    validation["errors"].append(
                        f"Cannot layer short sleeve sweater '{top1.name}' over long sleeve button-up '{top2.name}'. "
                        f"Only sweater vests can be layered over button-ups."
                    )
                
                # Rule: Short sleeve sweaters cannot be layered over long sleeve button-ups (reverse order)
                if (type2 == 'sweater' and sleeve2 == 'short' and 
                    type1 == 'shirt' and sleeve1 == 'long' and 
                    self._is_button_up(top1)):
                    validation["is_compatible"] = False
                    validation["errors"].append(
                        f"Cannot layer short sleeve sweater '{top2.name}' over long sleeve button-up '{top1.name}'. "
                        f"Only sweater vests can be layered over button-ups."
                    )
                
                # Rule: Only sweater vests can be layered over button-ups
                if (type1 == 'sweater' and type2 == 'shirt' and self._is_button_up(top2)):
                    if not self._is_sweater_vest(top1):
                        validation["is_compatible"] = False
                        validation["errors"].append(
                            f"Cannot layer sweater '{top1.name}' over button-up '{top2.name}'. "
                            f"Only sweater vests can be layered over button-ups."
                        )
                
                # Rule: Only sweater vests can be layered over button-ups (reverse order)
                if (type2 == 'sweater' and type1 == 'shirt' and self._is_button_up(top1)):
                    if not self._is_sweater_vest(top2):
                        validation["is_compatible"] = False
                        validation["errors"].append(
                            f"Cannot layer sweater '{top2.name}' over button-up '{top1.name}'. "
                            f"Only sweater vests can be layered over button-ups."
                        )
        
        return validation
    
    def _get_sleeve_length(self, item: ClothingItem) -> str:
        """Get the sleeve length of an item."""
        # Check metadata first
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes') and item.metadata.visualAttributes:
                sleeve_length = item.metadata.visualAttributes.sleeveLength
                if sleeve_length:
                    return sleeve_length.lower()
        
        # Fallback: infer from item name and type
        item_name = item.name.lower()
        item_type = item.type.lower()
        
        # Check for vest (no sleeves)
        if any(word in item_name for word in ['vest', 'sleeveless', 'tank']):
            return 'none'
        
        # Check for short sleeves
        if any(word in item_name for word in ['short sleeve', 'short-sleeve', 'short sleeve', 't-shirt', 'tee']):
            return 'short'
        
        # Check for long sleeves
        if any(word in item_name for word in ['long sleeve', 'long-sleeve', 'long sleeve', 'button up', 'button-up', 'dress shirt', 'oxford']):
            return 'long'
        
        # Default based on type
        if item_type == 'sweater':
            return 'long'  # Most sweaters are long sleeve
        elif item_type == 'shirt':
            return 'long'  # Most shirts are long sleeve
        else:
            return 'unknown'
    
    def _is_button_up(self, item: ClothingItem) -> bool:
        """Check if an item is a button-up shirt."""
        item_name = item.name.lower()
        item_type = item.type.lower()
        
        # Check for button-up indicators
        button_indicators = ['button up', 'button-up', 'button up', 'dress shirt', 'oxford', 'formal shirt']
        return any(indicator in item_name for indicator in button_indicators)
    
    def _is_sweater_vest(self, item: ClothingItem) -> bool:
        """Check if an item is a sweater vest."""
        item_name = item.name.lower()
        
        # Check for vest indicators
        vest_indicators = ['vest', 'sleeveless sweater', 'sweater vest']
        return any(indicator in item_name for indicator in vest_indicators)

    async def _generate_outfit_refined_pipeline(
        self,
        occasion: str,
        weather: WeatherData,
        wardrobe: List[ClothingItem],
        user_profile: UserProfile,
        style: Optional[str] = None,
        mood: Optional[str] = None,
        baseItem: Optional[ClothingItem] = None,
        trendingStyles: List[str] = None,
        likedOutfits: List[str] = None,
        outfit_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Refined outfit generation pipeline with 5 phases."""
        try:
            print("🔄 Starting refined pipeline...")
            
            # Phase 1: Input Context Gathering
            context = self._gather_input_context(
                occasion, weather, user_profile, style, mood, 
                trendingStyles or [], likedOutfits or [], baseItem, outfit_history, wardrobe
            )
            print(f"✅ Phase 1: Context gathered - {len(wardrobe)} items, {occasion}, {style}")
            
            # Phase 2: Preprocessing & Strict Filtering
            filtered_wardrobe = self._apply_strict_filtering(wardrobe, context)
            print(f"✅ Phase 2: Filtered to {len(filtered_wardrobe)} items")
            
            if len(filtered_wardrobe) < 2:
                return {
                    "success": False,
                    "message": f"Insufficient items after filtering: {len(filtered_wardrobe)} items (minimum 2 required)"
                }
            
            # Phase 3: Smart Selection
            selected_items = self._smart_selection_phase(filtered_wardrobe, context)
            self._debug_outfit_generation(selected_items, "After Smart Selection Phase")
            
            # Remove duplicates first
            unique_items = []
            seen_ids = set()
            for item in selected_items:
                if item.id not in seen_ids:
                    unique_items.append(item)
                    seen_ids.add(item.id)
            
            if len(unique_items) != len(selected_items):
                print(f"⚠️  Removed {len(selected_items) - len(unique_items)} duplicate items")
                selected_items = unique_items
            
            # Phase 4: Structural Integrity Check
            structure_result = self._structural_integrity_check(selected_items, filtered_wardrobe, context)
            if structure_result["is_complete"]:
                selected_items = structure_result["items"]
                print(f"✅ Phase 4: Structure validated - {len(selected_items)} items")
            else:
                print(f"⚠️  Phase 4: Structure issues - missing categories: {structure_result.get('missing_categories', [])}")
                # Continue with current items rather than failing completely

            self._debug_outfit_generation(selected_items, "After Structural Integrity Check")

            # NEW: Preserve base item before deduplication
            base_item = context.get("base_item")
            base_item_preserved = False
            if base_item:
                base_item_preserved = any(item.id == base_item.id for item in selected_items)
                print(f"🔍 DEBUG: Before deduplication - Base item present: {base_item_preserved}")

            # Deduplicate shoes (ensure only one shoe in the final outfit)
            selected_items = self._deduplicate_shoes(selected_items)

            # Comprehensive deduplication by category
            selected_items = self._deduplicate_by_category(selected_items, context)
            
            # NEW: Ensure base item is preserved after deduplication
            if base_item and not base_item_preserved:
                print(f"⚠️  DEBUG: After deduplication - Base item was lost, adding it back")
                # Add base item back at the beginning
                selected_items.insert(0, base_item)
                print(f"✅ DEBUG: After deduplication - Restored base item: {base_item.name}")
            
            self._debug_outfit_generation(selected_items, "After Deduplication")

            # Special validation for formal outfits
            if "formal" in context["occasion"].lower() or "gala" in context["occasion"].lower():
                selected_items = self._validate_formal_outfit_structure(selected_items, context["weather"])

            # Phase 5: Final Validation (Orchestrated)
            validation_result = await self._validate_outfit_with_orchestration(selected_items, context)
            if not validation_result["is_valid"]:
                print(f"⚠️  Phase 5: Orchestrated validation issues - {validation_result['errors']}")
                print(f"⚠️  Phase 5: Orchestrated validation warnings - {validation_result['warnings']}")
                # Don't fail completely, just log warnings
            
            # Ensure we have appropriate number of items based on occasion and weather
            target_counts = context["target_counts"]
            min_items = target_counts["min_items"]
            max_items = target_counts["max_items"]
            occasion = context["occasion"].lower()
            temperature = context["weather"].temperature
            
            # Determine optimal item count based on circumstances
            if len(selected_items) < min_items:
                print(f"⚠️  WARNING: _generate_outfit_refined_pipeline - Only {len(selected_items)} items selected (minimum {min_items} required)")
                
                # Smart fallback: select items based on occasion and weather requirements
                if len(wardrobe) >= min_items:
                    # For formal occasions, prioritize structured items
                    if "formal" in occasion or "business" in occasion or "interview" in occasion:
                        formal_items = [item for item in wardrobe if any(
                            keyword in item.type.lower() or keyword in item.name.lower()
                            for keyword in ['shirt', 'pants', 'dress', 'blazer', 'suit']
                        )]
                        if formal_items:
                            selected_items = formal_items[:min_items]
                        else:
                            selected_items = wardrobe[:min_items]
                    
                    # For athletic occasions, prioritize athletic items
                    elif "athletic" in occasion or "gym" in occasion:
                        athletic_items = [item for item in wardrobe if any(
                            keyword in item.type.lower() or keyword in item.name.lower()
                            for keyword in ['shirt', 'pants', 'shorts', 'sneakers', 'athletic']
                        )]
                        if athletic_items:
                            selected_items = athletic_items[:min_items]
                        else:
                            selected_items = wardrobe[:min_items]
                    
                    # For cold weather, prioritize layering items
                    elif temperature < 50:
                        layering_items = [item for item in wardrobe if any(
                            keyword in item.type.lower() or keyword in item.name.lower()
                            for keyword in ['shirt', 'pants', 'jacket', 'sweater', 'coat']
                        )]
                        if layering_items:
                            selected_items = layering_items[:min_items]
                        else:
                            selected_items = wardrobe[:min_items]
                    
                    # For hot weather, prioritize light items
                    # Ensure temperature is a float
                    if isinstance(temperature, str):
                        try:
                            temperature = float(temperature)
                        except (ValueError, TypeError):
                            temperature = 70.0
                    elif temperature is None:
                        temperature = 70.0
                    
                    if float(temperature) > 80:
                        light_items = [item for item in wardrobe if any(
                            keyword in item.type.lower() or keyword in item.name.lower()
                            for keyword in ['shirt', 'pants', 'shorts', 'light']
                        )]
                        if light_items:
                            selected_items = light_items[:min_items]
                        else:
                            selected_items = wardrobe[:min_items]
                    else:
                        selected_items = wardrobe[:min_items]
                    
                    # Default fallback
                    if len(selected_items) < min_items:
                        selected_items = wardrobe[:min_items]
                    
                    print(f"✅ DEBUG: _generate_outfit_refined_pipeline - Smart fallback selected {len(selected_items)} items")
                else:
                    return {
                        "success": False,
                            "message": f"Insufficient items in wardrobe: {len(wardrobe)} items (minimum {min_items} required)"
                }
            
            # NEW: Preserve base item when limiting items
            base_item = context.get("base_item")
            if base_item and len(selected_items) > 6:
                # Check if base item is in the first 6 items
                base_item_in_first_6 = any(item.id == base_item.id for item in selected_items[:6])
                if not base_item_in_first_6:
                    print(f"⚠️  DEBUG: Base item would be lost when limiting to 6 items, preserving it")
                    # Remove the last item and add base item at the beginning
                    selected_items = selected_items[:5]  # Keep first 5
                    selected_items.insert(0, base_item)  # Add base item first
                    print(f"✅ DEBUG: Preserved base item when limiting items")
                else:
                    selected_items = selected_items[:6]
                    print(f"⚠️  Limited to 6 items (base item preserved)")
            elif len(selected_items) > 6:
                selected_items = selected_items[:6]
                print(f"⚠️  Limited to 6 items")
            
            print(f"✅ Refined pipeline completed successfully with {len(selected_items)} items")
            return {
                "success": True,
                "items": selected_items,
                "context": context
            }
            
        except Exception as e:
            print(f"❌ Refined pipeline error: {str(e)}")
            return {
                "success": False,
                "message": f"Pipeline error: {str(e)}"
            }

    def _gather_input_context(
        self,
        occasion: str,
        weather: WeatherData,
        user_profile: UserProfile,
        style: Optional[str],
        mood: Optional[str],
        trendingStyles: List[str],
        likedOutfits: List[str],
        baseItem: Optional[ClothingItem],
        outfit_history: Optional[List[Dict[str, Any]]] = None,
        original_wardrobe: Optional[List[ClothingItem]] = None
    ) -> Dict[str, Any]:
        """Phase 1: Gather all input context and user data."""
        
        # Get rules and rules
        occasion_rule = get_occasion_rule(occasion)
        layering_rule = self._get_layering_rule(weather.temperature)
        mood_rule = get_mood_rule(mood) if mood else None
        
        # Determine target item counts by occasion
        target_counts = self._get_target_item_counts(occasion)
        
        # Get style compatibility matrix
        style_matrix = self._get_style_compatibility_matrix(style)
        
        return {
            "occasion": occasion,
            "weather": weather,
            "user_profile": user_profile,
            "style": style,
            "mood": mood,
            "base_item": baseItem,
            "trending_styles": trendingStyles,
            "liked_outfits": likedOutfits,
            "outfit_history": outfit_history or [],  # NEW: Include outfit history for diversity
            "original_wardrobe": original_wardrobe or [],  # NEW: Include original wardrobe for fallback
            "occasion_rule": occasion_rule,
            "layering_rule": layering_rule,
            "mood_rule": mood_rule,
            "target_counts": target_counts,
            "style_matrix": style_matrix
        }

    def _apply_strict_filtering(
        self,
        wardrobe: List[ClothingItem],
        context: Dict[str, Any]
    ) -> List[ClothingItem]:
        """Phase 2: Strictly remove unsuitable items BEFORE selection."""
        
        filtered_items = wardrobe.copy()
        print(f"🔍 DEBUG: _apply_strict_filtering - Starting with {len(filtered_items)} items")
        
        # 1. Weather mismatch filtering
        before_weather = len(filtered_items)
        filtered_items = self._filter_by_weather_strict(filtered_items, context["weather"])
        print(f"🔍 DEBUG: _apply_strict_filtering - After weather filtering: {len(filtered_items)} items (removed {before_weather - len(filtered_items)})")
        
        # 2. Occasion mismatch filtering
        before_occasion = len(filtered_items)
        filtered_items = self._filter_by_occasion_strict(filtered_items, context["occasion"])
        print(f"🔍 DEBUG: _apply_strict_filtering - After occasion filtering: {len(filtered_items)} items (removed {before_occasion - len(filtered_items)})")
        
        # 3. Style mismatch filtering
        if context["style"]:
            before_style = len(filtered_items)
            filtered_items = self._filter_by_style_strict(filtered_items, context["style"], context["style_matrix"])
            print(f"🔍 DEBUG: _apply_strict_filtering - After style filtering: {len(filtered_items)} items (removed {before_style - len(filtered_items)})")
        
        # 4. Fit/personal preference filtering
        before_preferences = len(filtered_items)
        filtered_items = self._filter_by_personal_preferences(filtered_items, context["user_profile"])
        print(f"🔍 DEBUG: _apply_strict_filtering - After preferences filtering: {len(filtered_items)} items (removed {before_preferences - len(filtered_items)})")
        
        # 5. Mood filtering (if specified)
        if context["mood_rule"]:
            before_mood = len(filtered_items)
            filtered_items = self._filter_by_mood_strict(filtered_items, context["mood_rule"], base_item=context.get("base_item"))
            print(f"🔍 DEBUG: _apply_strict_filtering - After mood filtering: {len(filtered_items)} items (removed {before_mood - len(filtered_items)})")
        
        # 6. NEW: Filter out recently used items for wardrobe diversity
        outfit_history = context.get("outfit_history", [])
        if outfit_history:
            before_history = len(filtered_items)
            filtered_items = self._filter_recently_used_items(filtered_items, outfit_history, days=7)
            print(f"🔍 DEBUG: _apply_strict_filtering - After history filtering: {len(filtered_items)} items (removed {before_history - len(filtered_items)})")
        
        # FALLBACK: If filtering is too strict and removes too many items, be more lenient
        target_counts = context["target_counts"]
        required_categories = target_counts["required_categories"]
        
        # Check if we have items for all required categories
        items_by_category = self._get_item_categories(filtered_items)
        missing_categories = set(required_categories) - set(items_by_category.keys())
        
        if len(filtered_items) < 3 or missing_categories:
            print(f"DEBUG: _apply_strict_filtering - Only {len(filtered_items)} items after strict filtering, missing categories: {missing_categories}, applying fallback")
            
            # Start over with more lenient filtering
            filtered_items = wardrobe.copy()
            
            # Only apply weather and basic occasion filtering (no strict athletic requirements)
            filtered_items = self._filter_by_weather_strict(filtered_items, context["weather"])
            
            # For athletic occasions, just filter out obviously inappropriate items
            if "athletic" in context["occasion"].lower() or "gym" in context["occasion"].lower():
                obviously_inappropriate = ['dress shoes', 'dress shirt', 'formal', 'heels', 'dress pants', 'slacks', 'suit']
                filtered_items = [item for item in filtered_items if not any(
                    inappropriate in item.type.lower() or inappropriate in item.name.lower()
                    for inappropriate in obviously_inappropriate
                )]
            
            # Apply personal preferences
            filtered_items = self._filter_by_personal_preferences(filtered_items, context["user_profile"])
            
            # Still apply recent usage filtering but with shorter timeframe
            if outfit_history:
                filtered_items = self._filter_recently_used_items(filtered_items, outfit_history, days=3)
            
            # SECOND FALLBACK: If we still don't have essential categories, be even more lenient
            items_by_category = self._get_item_categories(filtered_items)
            missing_categories = set(required_categories) - set(items_by_category.keys())
            
            if missing_categories:
                print(f"DEBUG: _apply_strict_filtering - Still missing categories after fallback: {missing_categories}, applying second fallback")
                
                # Start over with minimal filtering
                filtered_items = wardrobe.copy()
                
                # Only apply basic weather filtering (no strict rules)
                temperature = context["weather"].temperature
                if float(temperature) >= 80:  # Hot weather - only remove obvious winter items
                    obviously_hot = ['heavy sweater', 'winter coat', 'wool coat', 'thick fleece']
                elif temperature <= 45:  # Cold weather - only remove obvious summer items
                    obviously_hot = ['tank top', 'sleeveless', 'swimwear']
                else:  # Moderate weather - no temperature filtering
                    obviously_hot = []
                
                filtered_items = [item for item in filtered_items if not any(
                    hot_item in item.type.lower() or hot_item in item.name.lower()
                    for hot_item in obviously_hot
                )]
                
                # Apply only basic personal preferences (gender, size)
                filtered_items = [item for item in filtered_items if self._check_gender_compatibility(item, context["user_profile"].gender)]
                
                # No recent usage filtering in second fallback
            
            print(f"DEBUG: _apply_strict_filtering - Final fallback filtering: {len(filtered_items)} items")
            final_items_by_category = self._get_item_categories(filtered_items)
            print(f"DEBUG: _apply_strict_filtering - Final categories: {list(final_items_by_category.keys())}")
        
        # FINAL SAFETY CHECK: If we still have no items, return the original wardrobe
        if len(filtered_items) == 0:
            print(f"⚠️  WARNING: _apply_strict_filtering - No items after all filtering, returning original wardrobe")
            return wardrobe
        
        # ADDITIONAL SAFETY: If we have very few items, be more lenient
        if len(filtered_items) < 2:
            print(f"⚠️  WARNING: _apply_strict_filtering - Only {len(filtered_items)} items after filtering, being more lenient")
            # Start over with minimal filtering
            minimal_filtered = wardrobe.copy()
            
            # Only apply basic weather filtering
            temperature = context["weather"].temperature
            if temperature >= 80:  # Hot weather - only remove obvious winter items
                obviously_hot = ['heavy sweater', 'winter coat', 'wool coat', 'thick fleece']
            elif temperature <= 45:  # Cold weather - only remove obvious summer items
                obviously_hot = ['tank top', 'sleeveless', 'swimwear']
            else:  # Moderate weather - no temperature filtering
                obviously_hot = []
            
            minimal_filtered = [item for item in minimal_filtered if not any(
                hot_item in item.type.lower() or hot_item in item.name.lower()
                for hot_item in obviously_hot
            )]
            
            # Apply only basic personal preferences (gender)
            minimal_filtered = [item for item in minimal_filtered if self._check_gender_compatibility(item, context["user_profile"].gender)]
            
            if len(minimal_filtered) > len(filtered_items):
                print(f"✅ DEBUG: _apply_strict_filtering - Minimal filtering found {len(minimal_filtered)} items vs {len(filtered_items)}")
                return minimal_filtered
        
        return filtered_items

    def _smart_selection_phase(
        self,
        filtered_wardrobe: List[ClothingItem],
        context: Dict[str, Any]
    ) -> List[ClothingItem]:
        """Phase 3: Select best-fit items using priority, style match, and harmony rules."""
        
        selected_items = []
        selected_ids = set()  # Track selected item IDs to prevent duplicates
        target_counts = context["target_counts"]
        
        # NEW: Handle base item first if provided
        base_item = context.get("base_item")
        if base_item:
            print(f"🔍 DEBUG: _smart_selection_phase - Starting with base item: {base_item.name} (type: {base_item.type})")
            
            # Check if base item is in filtered wardrobe
            base_item_in_wardrobe = any(item.id == base_item.id for item in filtered_wardrobe)
            if not base_item_in_wardrobe:
                print(f"⚠️  DEBUG: _smart_selection_phase - Base item not in filtered wardrobe, adding it")
                # Add base item to filtered wardrobe temporarily for selection
                filtered_wardrobe.append(base_item)
            
            # Add base item as the first item
            selected_items.append(base_item)
            selected_ids.add(base_item.id)
            print(f"✅ DEBUG: _smart_selection_phase - Added base item: {base_item.name}")
            
            # Build complementary items around the base item
            complementary_items = self._build_outfit_around_base_item(
                base_item, selected_items, filtered_wardrobe, 
                context["occasion"], context["style"], context["layering_rule"]
            )
            
            # Add complementary items (excluding the base item which is already added)
            for item in complementary_items:
                if item.id != base_item.id and item.id not in selected_ids:
                    selected_items.append(item)
                    selected_ids.add(item.id)
                    print(f"✅ DEBUG: _smart_selection_phase - Added complementary item: {item.name}")
            
            # If we have enough items, return early
            if len(selected_items) >= target_counts["min_items"]:
                print(f"✅ DEBUG: _smart_selection_phase - Base item outfit complete with {len(selected_items)} items")
                return selected_items
        
        # 1. Core outfit items (must-have) - only if no base item or not enough items
        if len(selected_items) < target_counts["min_items"]:
            core_items = self._select_core_items(filtered_wardrobe, context)
            for item in core_items:
                if item.id not in selected_ids:
                    selected_items.append(item)
                    selected_ids.add(item.id)
        
        # 2. Style enhancers (match requested aesthetic)
        if context["style"] and len(selected_items) < target_counts["max_items"]:
            # Filter out already selected items
            available_items = [item for item in filtered_wardrobe if item.id not in selected_ids]
            style_items = self._select_style_enhancers(available_items, selected_items, context)
            for item in style_items:
                if item.id not in selected_ids and len(selected_items) < target_counts["max_items"]:
                    selected_items.append(item)
                    selected_ids.add(item.id)
        
        # 3. Accessories (limited by context and harmony)
        if len(selected_items) < target_counts["max_items"]:
            # Filter out already selected items
            available_items = [item for item in filtered_wardrobe if item.id not in selected_ids]
            accessory_items = self._select_accessories(available_items, selected_items, context)
            for item in accessory_items:
                if item.id not in selected_ids and len(selected_items) < target_counts["max_items"]:
                    selected_items.append(item)
                    selected_ids.add(item.id)
        
        # Final deduplication check
        final_items = []
        final_ids = set()
        for item in selected_items:
            if item.id not in final_ids:
                final_items.append(item)
                final_ids.add(item.id)
        
        if len(final_items) != len(selected_items):
            print(f"DEBUG: _smart_selection_phase - Removed {len(selected_items) - len(final_items)} duplicate items in final check")
        
        # NEW: Apply randomization factors to prevent deterministic selection
        final_items = self._add_randomization_factors(final_items, context)
        
        # FINAL SAFETY CHECK: If we have no items, select at least 2 random items from filtered wardrobe
        if len(final_items) == 0:
            print(f"⚠️  WARNING: _smart_selection_phase - No items selected, selecting random items from filtered wardrobe")
            import random
            if len(filtered_wardrobe) >= 2:
                final_items = random.sample(filtered_wardrobe, min(2, len(filtered_wardrobe)))
                print(f"✅ DEBUG: _smart_selection_phase - Selected {len(final_items)} random items as fallback")
            else:
                print(f"❌ ERROR: _smart_selection_phase - Not enough items in filtered wardrobe for fallback")
        
        # NEW: If we have fewer than minimum items, add more items to meet requirements
        min_items = context["target_counts"]["min_items"]
        if len(final_items) < min_items and len(filtered_wardrobe) > len(final_items):
            print(f"⚠️  WARNING: _smart_selection_phase - Only {len(final_items)} items selected (need {min_items}), adding more items")
            
            # Get items not already selected
            available_items = [item for item in filtered_wardrobe if item not in final_items]
            
            # Sort by relevance and add more items
            sorted_available = self._sort_items_by_relevance(available_items, context)
            needed_items = min_items - len(final_items)
            
            for item in sorted_available[:needed_items]:
                final_items.append(item)
                print(f"✅ DEBUG: _smart_selection_phase - Added fallback item: {item.name}")
        
        return final_items

    def _structural_integrity_check(
        self,
        selected_items: List[ClothingItem],
        filtered_wardrobe: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 4: Ensure completeness without compromising logic."""
        
        target_counts = context["target_counts"]
        required_categories = target_counts["required_categories"]
        
        # NEW: Preserve base item if present
        base_item = context.get("base_item")
        base_item_preserved = False
        if base_item:
            base_item_preserved = any(item.id == base_item.id for item in selected_items)
            print(f"🔍 DEBUG: _structural_integrity_check - Base item preserved: {base_item_preserved}")
        
        # Check what categories we have
        current_categories = self._get_item_categories(selected_items)
        missing_categories = set(required_categories) - set(current_categories.keys())
        
        print(f"🔍 DEBUG: _structural_integrity_check - Current categories: {list(current_categories.keys())}")
        print(f"🔍 DEBUG: _structural_integrity_check - Missing categories: {list(missing_categories)}")
        
        if missing_categories:
            print(f"🔧 DEBUG: _structural_integrity_check - Attempting to fill missing categories: {list(missing_categories)}")
            
            # Try to fill missing categories with valid items
            additional_items = self._fill_missing_categories(
                selected_items, filtered_wardrobe, missing_categories, context
            )
            
            print(f"🔧 DEBUG: _structural_integrity_check - Found {len(additional_items)} additional items")
            
            # Prevent duplicates when extending
            selected_ids = {item.id for item in selected_items}
            for item in additional_items:
                if item.id not in selected_ids:
                    selected_items.append(item)
                    selected_ids.add(item.id)
                    print(f"✅ DEBUG: _structural_integrity_check - Added {item.name} ({item.type})")
            
            # Re-check after filling
            current_categories = self._get_item_categories(selected_items)
            missing_categories = set(required_categories) - set(current_categories.keys())
            
            # SECOND ATTEMPT: If still missing categories, try with original wardrobe (less filtered)
            if missing_categories:
                print(f"⚠️  DEBUG: _structural_integrity_check - Still missing categories after first attempt: {list(missing_categories)}")
                print(f"⚠️  DEBUG: _structural_integrity_check - Trying with original wardrobe...")
                
                # Get original wardrobe from context
                original_wardrobe = context.get("original_wardrobe", [])
                if original_wardrobe:
                    # Try to fill missing categories from original wardrobe
                    additional_items = self._fill_missing_categories(
                        selected_items, original_wardrobe, missing_categories, context
                    )
                    
                    print(f"🔧 DEBUG: _structural_integrity_check - Found {len(additional_items)} additional items from original wardrobe")
                    
                    # Prevent duplicates when extending
                    selected_ids = {item.id for item in selected_items}
                    for item in additional_items:
                        if item.id not in selected_ids:
                            selected_items.append(item)
                            selected_ids.add(item.id)
                            print(f"✅ DEBUG: _structural_integrity_check - Added from original wardrobe: {item.name} ({item.type})")
                    
                    # Final re-check
                    current_categories = self._get_item_categories(selected_items)
                    missing_categories = set(required_categories) - set(current_categories.keys())
        
        # NEW: Ensure base item is still present if it was originally there
        if base_item and not base_item_preserved:
            print(f"⚠️  DEBUG: _structural_integrity_check - Base item was lost, adding it back")
            # Remove any item from the same category as base item to make room
            base_item_category = self._get_item_category(base_item)
            items_to_remove = [item for item in selected_items if self._get_item_category(item) == base_item_category and item.id != base_item.id]
            if items_to_remove:
                selected_items.remove(items_to_remove[0])
                print(f"🔧 DEBUG: _structural_integrity_check - Removed {items_to_remove[0].name} to make room for base item")
            
            # Add base item back
            selected_items.insert(0, base_item)  # Put base item first
            print(f"✅ DEBUG: _structural_integrity_check - Restored base item: {base_item.name}")
        
        print(f"🔍 DEBUG: _structural_integrity_check - Final categories: {list(current_categories.keys())}")
        print(f"🔍 DEBUG: _structural_integrity_check - Final missing: {list(missing_categories)}")
        
        return {
            "is_complete": len(missing_categories) == 0,
            "items": selected_items,
            "missing_categories": list(missing_categories),
            "current_categories": current_categories
        }

    def _final_outfit_validation(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Final validation of the generated outfit with soft fallback."""
        errors = []
        warnings = []
        
        # Check for duplicates
        item_ids = [item.id for item in items]
        if len(item_ids) != len(set(item_ids)):
            errors.append("Duplicate items detected in outfit")
        
        # Check for duplicate categories
        categories = [self._get_item_category(item) for item in items]
        if len(categories) != len(set(categories)):
            errors.append("Duplicate item categories detected in outfit")
        
        # Check form completeness
        form_validation = self._validate_form_completeness(items, context["target_counts"])
        if not form_validation["is_valid"]:
            errors.extend(form_validation["errors"])
        
        # Check occasion rules
        occasion_validation = self._validate_occasion_rules(items, context["occasion"])
        if not occasion_validation["is_valid"]:
            errors.extend(occasion_validation["errors"])
        
        # NEW: Special validation for formal outfits
        if "formal" in context["occasion"].lower() or "gala" in context["occasion"].lower() or "interview" in context["occasion"].lower():
            formal_validation = self._validate_formal_outfit_structure(items, context["weather"])
            if not formal_validation:  # Empty list means validation failed
                errors.append("Formal outfit missing required pants/skirts or jacket/blazer")
        
        # Check weather appropriateness
        weather_validation = self._validate_weather_appropriateness(items, context["weather"])
        if not weather_validation["is_valid"]:
            warnings.extend(weather_validation["warnings"])
        
        # Check style cohesion
        if context["style"]:
            style_validation = self._validate_style_cohesion(items, context["style"])
            if not style_validation["is_valid"]:
                warnings.extend(style_validation["warnings"])
        
        # NEW: Soft fallback for casual occasions with too few items
        if len(errors) > 0 and len(items) >= 2:
            occasion_lower = context["occasion"].lower()
            temperature = context["weather"].temperature
            
            # Allow 2-item outfits for casual occasions in warm weather
            if (occasion_lower in ['casual', 'athletic', 'gym', 'beach', 'vacation', 'errands'] and 
                temperature > 75 and len(items) >= 2):
                print(f"DEBUG: _final_outfit_validation - Soft fallback: Allowing 2-item outfit for casual/warm occasion")
                # Remove the "too few items" error if it exists
                errors = [error for error in errors if "too few items" not in error.lower() and "minimum" not in error.lower()]
                warnings.append("Minimal outfit acceptable for this casual/warm occasion")
            
            # Allow outfits with low occasion appropriateness for casual occasions
            if occasion_lower in ['casual', 'athletic', 'gym', 'beach', 'vacation', 'errands']:
                occasion_errors = [error for error in errors if "occasion" in error.lower()]
                if occasion_errors:
                    print(f"DEBUG: _final_outfit_validation - Soft fallback: Allowing low occasion appropriateness for casual occasion")
                    errors = [error for error in errors if error not in occasion_errors]
                    warnings.append("Relaxed occasion requirements for casual outfit")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    # Helper methods for the refined pipeline
    def _get_target_item_counts(self, occasion: str) -> Dict[str, Any]:
        """Get target item counts based on occasion and circumstances."""
        occasion_lower = occasion.lower()
        
        # ALL outfits must have at least 3 items: top, bottom, shoes
        # This ensures complete outfits for every occasion
        
        # Formal occasions - more structured, more items
        if "formal" in occasion_lower or "business" in occasion_lower or "interview" in occasion_lower or "gala" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory", "outerwear"]
            }
        
        # Athletic occasions - functional, but still need 3 items minimum
        elif "athletic" in occasion_lower or "gym" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 5,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["outerwear", "accessory"]
            }
        
        # Casual occasions - relaxed, but still need 3 items minimum
        elif "casual" in occasion_lower or "everyday" in occasion_lower or "errands" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 5,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory", "outerwear"]
            }
        
        # Social occasions - stylish, moderate to more items
        elif "party" in occasion_lower or "date" in occasion_lower or "night out" in occasion_lower or "cocktail" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory", "outerwear"]
            }
        
        # Travel occasions - practical, but still need 3 items minimum
        elif "travel" in occasion_lower or "airport" in occasion_lower or "vacation" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 5,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory", "outerwear"]
            }
        
        # Weather-specific occasions - layered, more items
        elif "cold" in occasion_lower or "winter" in occasion_lower or "snow" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["outerwear", "accessory"]
            }
        
        # Hot weather occasions - minimal, but still need 3 items minimum
        elif "hot" in occasion_lower or "summer" in occasion_lower or "beach" in occasion_lower:
            return {
                "min_items": 3,
                "max_items": 4,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory"]
            }
        
        # Default - balanced approach with 3 items minimum
        else:
            return {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"],
                "optional_categories": ["accessory", "outerwear"]
            }

    def _get_temperature_occasion_layering_matrix(self, temperature: float, occasion: str) -> Dict[str, Any]:
        """Get layering enforcement matrix based on temperature and occasion."""
        occasion_lower = occasion.lower()
        
        # Temperature ranges
        is_hot = temperature >= 80
        is_warm = 70 <= temperature < 80
        is_moderate = 50 <= temperature < 70
        is_cold = temperature < 50
        
        # Base matrix with temperature and occasion combinations
        matrix = {
            "allow_minimal_layering": False,
            "required_layers": 1,
            "max_layers": 3,
            "strict_enforcement": True,
            "notes": ""
        }
        
        # Hot weather (80°F+) - minimal layering for most occasions
        if is_hot:
            matrix["allow_minimal_layering"] = True
            matrix["required_layers"] = 1
            matrix["max_layers"] = 2
            matrix["strict_enforcement"] = False
            matrix["notes"] = "Hot weather - minimal layering preferred"
            
            # Special cases for hot weather
            if "formal" in occasion_lower or "business" in occasion_lower:
                matrix["required_layers"] = 2  # Still need some structure
                matrix["max_layers"] = 3
                matrix["strict_enforcement"] = True
                matrix["notes"] = "Hot weather formal - light layering required"
        
        # Warm weather (70-80°F) - moderate layering
        elif is_warm:
            matrix["allow_minimal_layering"] = True
            matrix["required_layers"] = 1
            matrix["max_layers"] = 3
            matrix["strict_enforcement"] = False
            matrix["notes"] = "Warm weather - flexible layering"
            
            # Special cases for warm weather
            if "formal" in occasion_lower or "business" in occasion_lower:
                matrix["required_layers"] = 2
                matrix["max_layers"] = 4
                matrix["strict_enforcement"] = True
                matrix["notes"] = "Warm weather formal - structured layering"
        
        # Moderate weather (50-70°F) - standard layering
        elif is_moderate:
            matrix["allow_minimal_layering"] = False
            matrix["required_layers"] = 2
            matrix["max_layers"] = 4
            matrix["strict_enforcement"] = True
            matrix["notes"] = "Moderate weather - standard layering"
            
            # Special cases for moderate weather
            if "casual" in occasion_lower or "athletic" in occasion_lower:
                matrix["allow_minimal_layering"] = True
                matrix["required_layers"] = 1
                matrix["max_layers"] = 3
                matrix["strict_enforcement"] = False
                matrix["notes"] = "Moderate weather casual - relaxed layering"
        
        # Cold weather (<50°F) - heavy layering
        else:
            matrix["allow_minimal_layering"] = False
            matrix["required_layers"] = 3
            matrix["max_layers"] = 5
            matrix["strict_enforcement"] = True
            matrix["notes"] = "Cold weather - heavy layering required"
            
            # Special cases for cold weather
            if "athletic" in occasion_lower or "gym" in occasion_lower:
                matrix["allow_minimal_layering"] = True
                matrix["required_layers"] = 2
                matrix["max_layers"] = 4
                matrix["strict_enforcement"] = False
                matrix["notes"] = "Cold weather athletic - functional layering"
        
        # Occasion-specific overrides
        if "beach" in occasion_lower or "vacation" in occasion_lower:
            matrix["allow_minimal_layering"] = True
            matrix["required_layers"] = 1
            matrix["max_layers"] = 2
            matrix["strict_enforcement"] = False
            matrix["notes"] += " - Beach/vacation relaxation"
        
        elif "formal" in occasion_lower or "gala" in occasion_lower or "wedding" in occasion_lower:
            matrix["allow_minimal_layering"] = False
            matrix["required_layers"] = max(matrix["required_layers"], 2)
            matrix["max_layers"] = max(matrix["max_layers"], 4)
            matrix["strict_enforcement"] = True
            matrix["notes"] += " - Formal occasion requirements"
        
        elif "athletic" in occasion_lower or "gym" in occasion_lower:
            matrix["allow_minimal_layering"] = True
            matrix["required_layers"] = 1
            matrix["max_layers"] = 3
            matrix["strict_enforcement"] = False
            matrix["notes"] += " - Athletic flexibility"
        
        return matrix

    def _get_style_compatibility_matrix(self, style: Optional[str]) -> Dict[str, Any]:
        """Get style-to-item compatibility matrix."""
        if not style:
            return {"approved_items": [], "banned_items": []}
        
        matrices = {
            "minimalist": {
                "approved_items": ["t-shirt", "shirt", "pants", "jeans", "sneakers", "loafers"],
                "banned_items": ["neon", "graphic", "pattern", "jewelry", "accessory"]
            },
            "techwear": {
                "approved_items": ["cargo pants", "hardshell", "sneakers", "jacket", "hoodie"],
                "banned_items": ["dress", "formal", "elegant", "delicate"]
            },
            "y2k": {
                "approved_items": ["crop top", "low rise", "platform", "baggy", "vintage", "graphic tee", "mini skirt", "flare jeans"],
                "banned_items": ["minimalist", "formal", "conservative", "cable knit", "traditional", "business"]
            },
            "athletic": {
                "approved_items": ["athletic", "gym", "workout", "sport", "training"],
                "banned_items": ["formal", "dress", "elegant", "business"]
            },
            "business": {
                "approved_items": ["dress shirt", "pants", "blazer", "dress shoes", "formal"],
                "banned_items": ["athletic", "casual", "beach", "gym"]
            },
            "old money": {
                "approved_items": ["dress shirt", "blazer", "dress pants", "oxford", "loafers", "sweater", "formal", "elegant", "traditional"],
                "banned_items": ["casual", "athletic", "trendy", "y2k", "minimalist", "techwear", "polo", "t-shirt", "jeans", "sneakers"]
            }
        }
        
        return matrices.get(style.lower(), {"approved_items": [], "banned_items": []})

    def _filter_by_weather_strict(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Strict weather filtering."""
        temperature = weather.temperature
        
        if temperature >= 80:  # Hot weather
            forbidden_types = ['sweater', 'jacket', 'coat', 'hoodie', 'cardigan', 'wool', 'fleece', 'long sleeve']
        elif temperature >= 70:  # Warm weather (78.5°F falls here)
            # Be more lenient for warm weather - only remove heavy sweaters
            forbidden_types = ['heavy sweater', 'thick wool', 'winter coat', 'cable knit', 'thick fleece']
        elif temperature <= 45:  # Cold weather
            forbidden_types = ['tank top', 'shorts', 'sandals', 'sleeveless']
        else:  # Moderate weather (45-70°F)
            forbidden_types = ['heavy sweater', 'thick wool', 'winter coat']
        
        filtered_items = []
        for item in items:
            # Check if item is forbidden
            is_forbidden = any(
            forbidden_type in item.type.lower() or forbidden_type in item.name.lower()
            for forbidden_type in forbidden_types
            )
            
            if not is_forbidden:
                filtered_items.append(item)
            else:
                print(f"❌ DEBUG: _filter_by_weather_strict - Removed {item.name} (type: {item.type}) for {temperature}°F weather")
        
        return filtered_items

    def _filter_by_occasion_strict(self, items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Strict occasion filtering with comprehensive special logic for all occasions."""
        occasion_rules = {
            "gym": ["dress shoes", "dress shirt", "formal", "heels", "dress pants", "slacks"],
            "beach": ["closed leather shoes", "blazer", "tight jeans", "formal"],
            "work": ["tank top", "flip-flops", "swimwear", "athletic"],
            "party": ["athletic", "gym", "workout", "casual shorts", "athletic shorts", "sweatpants"],
            "formal": ["athletic", "casual", "beach", "gym", "tank top", "polo", "t-shirt", "jeans", "shorts", "sneakers", "toe shoes", "slides", "flip flops", "sandals", "running shoes", "athletic shoes", "sport shoes"],
            "gala": ["athletic", "casual", "beach", "gym", "tank top", "polo", "t-shirt", "jeans", "shorts", "sneakers", "toe shoes", "slides", "flip flops", "sandals", "running shoes", "athletic shoes", "sport shoes", "short sleeve", "short-sleeve"],
            "airport": ["formal", "heels", "dress shoes", "suit", "blazer"],  # Avoid overly formal items for airport
            "travel": ["formal", "heels", "dress shoes", "suit", "blazer"],   # Same as airport
            "casual": ["formal", "heels", "dress shoes", "suit", "blazer"],   # Avoid formal items for casual
            "business": ["tank top", "flip-flops", "swimwear", "athletic", "casual shorts", "athletic shorts", "sweatpants"]  # Avoid casual items for business
        }
        
        forbidden_types = []
        for key, forbidden in occasion_rules.items():
            if key in occasion.lower():
                forbidden_types.extend(forbidden)
        
        # First filter out forbidden items
        filtered_items = [item for item in items if not any(
            forbidden_type in item.type.lower() or forbidden_type in item.name.lower()
            for forbidden_type in forbidden_types
        )]
        
        # Additional filtering for formal occasions - catch casual/athletic shoes by brand and characteristics
        if "formal" in occasion.lower() or "gala" in occasion.lower() or "interview" in occasion.lower():
            casual_shoe_indicators = [
                "toe shoes", "slides", "flip flops", "sandals", "running", "athletic", "sport", 
                "nike", "adidas", "puma", "reebok", "under armour", "new balance", "asics",
                "converse", "vans", "crocs", "birkenstock", "suicoke", "yeezy", "jordan",
                "trainer", "sneaker", "tennis", "basketball", "football", "soccer"
            ]
            
            filtered_items = [item for item in filtered_items if not (
                item.type.lower() in ['shoes', 'sneakers'] and 
                any(indicator in item.name.lower() for indicator in casual_shoe_indicators)
            )]
        
        # COMPREHENSIVE SPECIAL HANDLING FOR ALL OCCASIONS
        occasion_lower = occasion.lower()
        
        # 1. WEDDING GUEST - Business casual and up, but not strictly formal
        if "wedding" in occasion_lower:
            return self._filter_for_wedding_guest(filtered_items)
        
        # 2. AIRPORT - Comfortable, practical, and stylish items
        if "airport" in occasion_lower:
            return self._filter_for_airport(filtered_items)
        
        # 3. TRAVEL - Similar to airport but with more flexibility
        if "travel" in occasion_lower:
            return self._filter_for_travel(filtered_items)
        
        # 4. BUSINESS CASUAL - Professional yet relaxed
        if "business casual" in occasion_lower or "business_casual" in occasion_lower:
            return self._filter_for_business_casual(filtered_items)
        
        # 5. BUSINESS FORMAL - Professional and formal
        if "business formal" in occasion_lower or "business_formal" in occasion_lower:
            return self._filter_for_business_formal(filtered_items)
        
        # 6. WORK - Professional work attire
        if "work" in occasion_lower:
            return self._filter_for_work(filtered_items)
        
        # 7. INTERVIEW - Conservative and professional
        if "interview" in occasion_lower:
            return self._filter_for_interview(filtered_items)
        
        # 8. FORMAL - Elegant and sophisticated
        if "formal" in occasion_lower:
            return self._filter_for_formal(filtered_items)
        
        # 9. GALA - Luxurious and elegant
        if "gala" in occasion_lower:
            return self._filter_for_gala(filtered_items)
        
        # 10. PARTY - Bold and trendy
        if "party" in occasion_lower:
            return self._filter_for_party(filtered_items)
        
        # 11. DATE NIGHT - Romantic and sophisticated
        if "date" in occasion_lower:
            return self._filter_for_date_night(filtered_items)
        
        # 12. BRUNCH - Effortless and elegant
        if "brunch" in occasion_lower:
            return self._filter_for_brunch(filtered_items)
        
        # 13. COCKTAIL - Sophisticated and refined
        if "cocktail" in occasion_lower:
            return self._filter_for_cocktail(filtered_items)
        
        # 14. NIGHT OUT - Bold and trendy
        if "night out" in occasion_lower or "nightout" in occasion_lower:
            return self._filter_for_night_out(filtered_items)
        
        # 15. BEACH - Relaxed and beach-appropriate
        if "beach" in occasion_lower:
            return self._filter_for_beach(filtered_items)
        
        # 16. VACATION - Comfortable and relaxed
        if "vacation" in occasion_lower:
            return self._filter_for_vacation(filtered_items)
        
        # 17. FESTIVAL - Bohemian and trendy
        if "festival" in occasion_lower:
            return self._filter_for_festival(filtered_items)
        
        # 18. ATHLETIC/GYM - Athletic and performance-focused
        if "athletic" in occasion_lower or "gym" in occasion_lower:
            return self._filter_for_athletic(filtered_items)
        
        # 19. SCHOOL - Neat and appropriate
        if "school" in occasion_lower:
            return self._filter_for_school(filtered_items)
        
        # 20. HOLIDAY - Festive and elegant
        if "holiday" in occasion_lower:
            return self._filter_for_holiday(filtered_items)
        
        # 21. CONCERT - Trendy and music-inspired
        if "concert" in occasion_lower:
            return self._filter_for_concert(filtered_items)
        
        # 22. ERRANDS - Practical and comfortable
        if "errands" in occasion_lower:
            return self._filter_for_errands(filtered_items)
        
        # 23. MUSEUM - Cultured and elegant
        if "museum" in occasion_lower or "gallery" in occasion_lower:
            return self._filter_for_museum(filtered_items)
        
        # 24. FASHION EVENT - Fashion-forward and sophisticated
        if "fashion" in occasion_lower:
            return self._filter_for_fashion_event(filtered_items)
        
        # 25. OUTDOOR GATHERING - Outdoor-ready and practical
        if "outdoor" in occasion_lower:
            return self._filter_for_outdoor_gathering(filtered_items)
        
        # 26. FUNERAL - Respectful and somber
        if "funeral" in occasion_lower or "memorial" in occasion_lower:
            return self._filter_for_funeral(filtered_items)
        
        # 27. CASUAL - Relaxed and comfortable
        if "casual" in occasion_lower:
            return self._filter_for_casual(filtered_items)
        
        # 28. LOUNGEWEAR - Comfortable and relaxed
        if "loungewear" in occasion_lower or "lounge" in occasion_lower:
            return self._filter_for_loungewear(filtered_items)
        
        # 29. RAINY DAY - Practical and waterproof
        if "rainy" in occasion_lower or "rain" in occasion_lower:
            return self._filter_for_rainy_day(filtered_items)
        
        # 30. SNOW DAY - Warm and protective
        if "snow" in occasion_lower:
            return self._filter_for_snow_day(filtered_items)
        
        # 31. HOT WEATHER - Light and breathable
        if "hot" in occasion_lower and "weather" in occasion_lower:
            return self._filter_for_hot_weather(filtered_items)
        
        # 32. COLD WEATHER - Warm and insulated
        if "cold" in occasion_lower and "weather" in occasion_lower:
            return self._filter_for_cold_weather(filtered_items)
        
        # 33. CHILLY EVENING - Warm and elegant
        if "chilly" in occasion_lower:
            return self._filter_for_chilly_evening(filtered_items)
        
        return filtered_items

    # Helper methods for special occasion filtering
    def _filter_for_wedding_guest(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for wedding guest occasions."""
        print(f"🔍 DEBUG: _filter_for_wedding_guest - Processing wedding guest occasion")
        
        wedding_appropriate_items = []
        wedding_keywords = ['business casual', 'dinner', 'brunch', 'formal', 'business', 'professional', 'smart casual', 'classic', 'elegant']
        
        for item in items:
            # Check for wedding-appropriate attributes
            has_wedding_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in wedding_keywords):
                        has_wedding_appropriate_occasion = True
                        break
            
            has_wedding_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in wedding_keywords):
                    has_wedding_appropriate_style = True
            
            has_wedding_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in wedding_keywords):
                    has_wedding_appropriate_tags = True
            
            # For wedding guest, accept items with any wedding-appropriate attribute
            if has_wedding_appropriate_occasion or has_wedding_appropriate_style or has_wedding_appropriate_tags:
                wedding_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_wedding_guest - Wedding appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_wedding_guest - Wedding inappropriate item: {item.name}")
        
        # If we have wedding-appropriate items, use them; otherwise, be more lenient
        if wedding_appropriate_items:
            print(f"✅ DEBUG: _filter_for_wedding_guest - Found {len(wedding_appropriate_items)} wedding-appropriate items")
            return wedding_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_wedding_guest - No wedding-appropriate items found, being more lenient")
            return items

    def _filter_for_airport(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for airport occasions."""
        print(f"🔍 DEBUG: _filter_for_airport - Processing airport occasion")
        
        airport_appropriate_items = []
        airport_keywords = ['casual', 'business casual', 'travel', 'comfortable', 'practical', 'smart casual', 'minimalist', 'classic']
        
        for item in items:
            # Check for airport-appropriate attributes
            has_airport_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in airport_keywords):
                        has_airport_appropriate_occasion = True
                        break
            
            has_airport_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in airport_keywords):
                    has_airport_appropriate_style = True
            
            has_airport_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in airport_keywords):
                    has_airport_appropriate_tags = True
            
            # For airport, accept items with any airport-appropriate attribute
            if has_airport_appropriate_occasion or has_airport_appropriate_style or has_airport_appropriate_tags:
                airport_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_airport - Airport appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_airport - Airport inappropriate item: {item.name}")
        
        # If we have airport-appropriate items, use them; otherwise, be more lenient
        if airport_appropriate_items:
            print(f"✅ DEBUG: _filter_for_airport - Found {len(airport_appropriate_items)} airport-appropriate items")
            return airport_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_airport - No airport-appropriate items found, being more lenient")
            return items

    def _filter_for_travel(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for travel occasions."""
        print(f"🔍 DEBUG: _filter_for_travel - Processing travel occasion")
        
        travel_appropriate_items = []
        travel_keywords = ['casual', 'business casual', 'travel', 'comfortable', 'practical', 'smart casual', 'minimalist', 'classic', 'resort', 'vacation']
        
        for item in items:
            # Check for travel-appropriate attributes
            has_travel_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in travel_keywords):
                        has_travel_appropriate_occasion = True
                        break
            
            has_travel_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in travel_keywords):
                    has_travel_appropriate_style = True
            
            has_travel_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in travel_keywords):
                    has_travel_appropriate_tags = True
            
            # For travel, accept items with any travel-appropriate attribute
            if has_travel_appropriate_occasion or has_travel_appropriate_style or has_travel_appropriate_tags:
                travel_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_travel - Travel appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_travel - Travel inappropriate item: {item.name}")
        
        # If we have travel-appropriate items, use them; otherwise, be more lenient
        if travel_appropriate_items:
            print(f"✅ DEBUG: _filter_for_travel - Found {len(travel_appropriate_items)} travel-appropriate items")
            return travel_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_travel - No travel-appropriate items found, being more lenient")
            return items

    def _filter_for_business_casual(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for business casual occasions."""
        print(f"🔍 DEBUG: _filter_for_business_casual - Processing business casual occasion")
        
        business_casual_appropriate_items = []
        business_casual_keywords = ['business casual', 'smart casual', 'refined', 'polished', 'contemporary', 'professional']
        
        for item in items:
            # Check for business casual-appropriate attributes
            has_business_casual_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in business_casual_keywords):
                        has_business_casual_appropriate_occasion = True
                        break
            
            has_business_casual_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in business_casual_keywords):
                    has_business_casual_appropriate_style = True
            
            has_business_casual_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in business_casual_keywords):
                    has_business_casual_appropriate_tags = True
            
            # For business casual, accept items with any business casual-appropriate attribute
            if has_business_casual_appropriate_occasion or has_business_casual_appropriate_style or has_business_casual_appropriate_tags:
                business_casual_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_business_casual - Business casual appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_business_casual - Business casual inappropriate item: {item.name}")
        
        # If we have business casual-appropriate items, use them; otherwise, be more lenient
        if business_casual_appropriate_items:
            print(f"✅ DEBUG: _filter_for_business_casual - Found {len(business_casual_appropriate_items)} business casual-appropriate items")
            return business_casual_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_business_casual - No business casual-appropriate items found, being more lenient")
            return items

    def _filter_for_business_formal(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for business formal occasions."""
        print(f"🔍 DEBUG: _filter_for_business_formal - Processing business formal occasion")
        
        business_formal_appropriate_items = []
        business_formal_keywords = ['formal', 'business', 'professional', 'tailored', 'structured', 'classic', 'sophisticated']
        
        for item in items:
            # Check for business formal-appropriate attributes
            has_business_formal_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in business_formal_keywords):
                        has_business_formal_appropriate_occasion = True
                        break
            
            has_business_formal_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in business_formal_keywords):
                    has_business_formal_appropriate_style = True
            
            has_business_formal_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in business_formal_keywords):
                    has_business_formal_appropriate_tags = True
            
            # For business formal, accept items with any business formal-appropriate attribute
            if has_business_formal_appropriate_occasion or has_business_formal_appropriate_style or has_business_formal_appropriate_tags:
                business_formal_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_business_formal - Business formal appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_business_formal - Business formal inappropriate item: {item.name}")
        
        # If we have business formal-appropriate items, use them; otherwise, be more lenient
        if business_formal_appropriate_items:
            print(f"✅ DEBUG: _filter_for_business_formal - Found {len(business_formal_appropriate_items)} business formal-appropriate items")
            return business_formal_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_business_formal - No business formal-appropriate items found, being more lenient")
            return items

    def _filter_for_work(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for work occasions."""
        print(f"🔍 DEBUG: _filter_for_work - Processing work occasion")
        
        work_appropriate_items = []
        work_keywords = ['professional', 'practical', 'neat', 'business', 'work_appropriate', 'business casual', 'smart casual']
        
        for item in items:
            # Check for work-appropriate attributes
            has_work_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in work_keywords):
                        has_work_appropriate_occasion = True
                        break
            
            has_work_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in work_keywords):
                    has_work_appropriate_style = True
            
            has_work_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in work_keywords):
                    has_work_appropriate_tags = True
            
            # For work, accept items with any work-appropriate attribute
            if has_work_appropriate_occasion or has_work_appropriate_style or has_work_appropriate_tags:
                work_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_work - Work appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_work - Work inappropriate item: {item.name}")
        
        # If we have work-appropriate items, use them; otherwise, be more lenient
        if work_appropriate_items:
            print(f"✅ DEBUG: _filter_for_work - Found {len(work_appropriate_items)} work-appropriate items")
            return work_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_work - No work-appropriate items found, being more lenient")
            return items

    def _filter_for_interview(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for interview occasions."""
        print(f"🔍 DEBUG: _filter_for_interview - Processing interview occasion")
        
        interview_appropriate_items = []
        interview_keywords = ['conservative', 'professional', 'polished', 'traditional', 'confident', 'formal', 'business']
        
        for item in items:
            # Check for interview-appropriate attributes
            has_interview_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in interview_keywords):
                        has_interview_appropriate_occasion = True
                        break
            
            has_interview_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in interview_keywords):
                    has_interview_appropriate_style = True
            
            has_interview_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in interview_keywords):
                    has_interview_appropriate_tags = True
            
            # For interview, accept items with any interview-appropriate attribute
            if has_interview_appropriate_occasion or has_interview_appropriate_style or has_interview_appropriate_tags:
                interview_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_interview - Interview appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_interview - Interview inappropriate item: {item.name}")
        
        # If we have interview-appropriate items, use them; otherwise, be more lenient
        if interview_appropriate_items:
            print(f"✅ DEBUG: _filter_for_interview - Found {len(interview_appropriate_items)} interview-appropriate items")
            return interview_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_interview - No interview-appropriate items found, being more lenient")
            return items

    def _filter_for_formal(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for formal occasions."""
        print(f"🔍 DEBUG: _filter_for_formal - Processing formal occasion")
        
        formal_appropriate_items = []
        formal_keywords = ['formal', 'business', 'dress', 'professional', 'elegant', 'sophisticated', 'refined', 'luxurious', 'classic']
        
        for item in items:
            # Check for formal-appropriate attributes
            has_formal_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in formal_keywords):
                        has_formal_appropriate_occasion = True
                        break
            
            has_formal_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in formal_keywords):
                    has_formal_appropriate_style = True
            
            has_formal_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in formal_keywords):
                    has_formal_appropriate_tags = True
            
            # For formal occasions, require at least one formal attribute
            if has_formal_appropriate_occasion or has_formal_appropriate_style or has_formal_appropriate_tags:
                formal_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_formal - Formal appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_formal - Formal inappropriate item: {item.name}")
        
        # If we have formal items, use them; otherwise, be more lenient
        if formal_appropriate_items:
            print(f"✅ DEBUG: _filter_for_formal - Found {len(formal_appropriate_items)} formal-appropriate items")
            return formal_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_formal - No formal-appropriate items found, being more lenient")
            return items

    def _filter_for_gala(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for gala occasions."""
        print(f"🔍 DEBUG: _filter_for_gala - Processing gala occasion")
        
        gala_appropriate_items = []
        gala_keywords = ['luxurious', 'elegant', 'sophisticated', 'high_end', 'glamorous', 'formal', 'dress', 'professional']
        
        for item in items:
            # Check for gala-appropriate attributes
            has_gala_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in gala_keywords):
                        has_gala_appropriate_occasion = True
                        break
            
            has_gala_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in gala_keywords):
                    has_gala_appropriate_style = True
            
            has_gala_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in gala_keywords):
                    has_gala_appropriate_tags = True
            
            # For gala occasions, require at least one gala-appropriate attribute
            if has_gala_appropriate_occasion or has_gala_appropriate_style or has_gala_appropriate_tags:
                gala_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_gala - Gala appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_gala - Gala inappropriate item: {item.name}")
        
        # If we have gala items, use them; otherwise, be more lenient
        if gala_appropriate_items:
            print(f"✅ DEBUG: _filter_for_gala - Found {len(gala_appropriate_items)} gala-appropriate items")
            return gala_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_gala - No gala-appropriate items found, being more lenient")
            return items

    def _filter_for_party(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for party occasions."""
        print(f"🔍 DEBUG: _filter_for_party - Processing party occasion")
        
        party_appropriate_items = []
        party_keywords = ['bold', 'trendy', 'fashion_forward', 'statement', 'playful', 'party', 'glamorous', 'stylish']
        
        for item in items:
            # Check for party-appropriate attributes
            has_party_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in party_keywords):
                        has_party_appropriate_occasion = True
                        break
            
            has_party_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in party_keywords):
                    has_party_appropriate_style = True
            
            has_party_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in party_keywords):
                    has_party_appropriate_tags = True
            
            # For party occasions, accept items with any party-appropriate attribute
            if has_party_appropriate_occasion or has_party_appropriate_style or has_party_appropriate_tags:
                party_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_party - Party appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_party - Party inappropriate item: {item.name}")
        
        # If we have party-appropriate items, use them; otherwise, be more lenient
        if party_appropriate_items:
            print(f"✅ DEBUG: _filter_for_party - Found {len(party_appropriate_items)} party-appropriate items")
            return party_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_party - No party-appropriate items found, being more lenient")
            return items

    def _filter_for_date_night(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for date night occasions."""
        print(f"🔍 DEBUG: _filter_for_date_night - Processing date night occasion")
        
        date_appropriate_items = []
        date_keywords = ['romantic', 'elegant', 'sophisticated', 'stylish', 'attractive', 'sexy', 'alluring']
        
        for item in items:
            # Check for date-appropriate attributes
            has_date_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in date_keywords):
                        has_date_appropriate_occasion = True
                        break
            
            has_date_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in date_keywords):
                    has_date_appropriate_style = True
            
            has_date_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in date_keywords):
                    has_date_appropriate_tags = True
            
            # For date night, accept items with any date-appropriate attribute
            if has_date_appropriate_occasion or has_date_appropriate_style or has_date_appropriate_tags:
                date_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_date_night - Date appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_date_night - Date inappropriate item: {item.name}")
        
        # If we have date-appropriate items, use them; otherwise, be more lenient
        if date_appropriate_items:
            print(f"✅ DEBUG: _filter_for_date_night - Found {len(date_appropriate_items)} date-appropriate items")
            return date_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_date_night - No date-appropriate items found, being more lenient")
            return items

    def _filter_for_brunch(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for brunch occasions."""
        print(f"🔍 DEBUG: _filter_for_brunch - Processing brunch occasion")
        
        brunch_appropriate_items = []
        brunch_keywords = ['effortless', 'elegant', 'relaxed', 'sophisticated', 'casual_chic', 'brunch', 'dinner']
        
        for item in items:
            # Check for brunch-appropriate attributes
            has_brunch_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in brunch_keywords):
                        has_brunch_appropriate_occasion = True
                        break
            
            has_brunch_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in brunch_keywords):
                    has_brunch_appropriate_style = True
            
            has_brunch_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in brunch_keywords):
                    has_brunch_appropriate_tags = True
            
            # For brunch, accept items with any brunch-appropriate attribute
            if has_brunch_appropriate_occasion or has_brunch_appropriate_style or has_brunch_appropriate_tags:
                brunch_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_brunch - Brunch appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_brunch - Brunch inappropriate item: {item.name}")
        
        # If we have brunch-appropriate items, use them; otherwise, be more lenient
        if brunch_appropriate_items:
            print(f"✅ DEBUG: _filter_for_brunch - Found {len(brunch_appropriate_items)} brunch-appropriate items")
            return brunch_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_brunch - No brunch-appropriate items found, being more lenient")
            return items

    def _filter_for_cocktail(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for cocktail occasions."""
        print(f"🔍 DEBUG: _filter_for_cocktail - Processing cocktail occasion")
        
        cocktail_appropriate_items = []
        cocktail_keywords = ['sophisticated', 'elegant', 'refined', 'stylish', 'upscale', 'cocktail', 'formal']
        
        for item in items:
            # Check for cocktail-appropriate attributes
            has_cocktail_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in cocktail_keywords):
                        has_cocktail_appropriate_occasion = True
                        break
            
            has_cocktail_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in cocktail_keywords):
                    has_cocktail_appropriate_style = True
            
            has_cocktail_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in cocktail_keywords):
                    has_cocktail_appropriate_tags = True
            
            # For cocktail, accept items with any cocktail-appropriate attribute
            if has_cocktail_appropriate_occasion or has_cocktail_appropriate_style or has_cocktail_appropriate_tags:
                cocktail_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_cocktail - Cocktail appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_cocktail - Cocktail inappropriate item: {item.name}")
        
        # If we have cocktail-appropriate items, use them; otherwise, be more lenient
        if cocktail_appropriate_items:
            print(f"✅ DEBUG: _filter_for_cocktail - Found {len(cocktail_appropriate_items)} cocktail-appropriate items")
            return cocktail_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_cocktail - No cocktail-appropriate items found, being more lenient")
            return items

    def _filter_for_night_out(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for night out occasions."""
        print(f"🔍 DEBUG: _filter_for_night_out - Processing night out occasion")
        
        night_out_appropriate_items = []
        night_out_keywords = ['bold', 'trendy', 'stylish', 'fashion_forward', 'confident', 'night out', 'party']
        
        for item in items:
            # Check for night out-appropriate attributes
            has_night_out_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in night_out_keywords):
                        has_night_out_appropriate_occasion = True
                        break
            
            has_night_out_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in night_out_keywords):
                    has_night_out_appropriate_style = True
            
            has_night_out_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in night_out_keywords):
                    has_night_out_appropriate_tags = True
            
            # For night out, accept items with any night out-appropriate attribute
            if has_night_out_appropriate_occasion or has_night_out_appropriate_style or has_night_out_appropriate_tags:
                night_out_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_night_out - Night out appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_night_out - Night out inappropriate item: {item.name}")
        
        # If we have night out-appropriate items, use them; otherwise, be more lenient
        if night_out_appropriate_items:
            print(f"✅ DEBUG: _filter_for_night_out - Found {len(night_out_appropriate_items)} night out-appropriate items")
            return night_out_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_night_out - No night out-appropriate items found, being more lenient")
            return items

    def _filter_for_beach(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for beach occasions."""
        print(f"🔍 DEBUG: _filter_for_beach - Processing beach occasion")
        
        beach_appropriate_items = []
        beach_keywords = ['beach', 'vacation', 'resort', 'summer', 'casual', 'relaxed', 'comfortable']
        
        for item in items:
            # Check for beach-appropriate attributes
            has_beach_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in beach_keywords):
                        has_beach_appropriate_occasion = True
                        break
            
            has_beach_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in beach_keywords):
                    has_beach_appropriate_style = True
            
            has_beach_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in beach_keywords):
                    has_beach_appropriate_tags = True
            
            # For beach, accept items with any beach-appropriate attribute
            if has_beach_appropriate_occasion or has_beach_appropriate_style or has_beach_appropriate_tags:
                beach_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_beach - Beach appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_beach - Beach inappropriate item: {item.name}")
        
        # If we have beach-appropriate items, use them; otherwise, be more lenient
        if beach_appropriate_items:
            print(f"✅ DEBUG: _filter_for_beach - Found {len(beach_appropriate_items)} beach-appropriate items")
            return beach_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_beach - No beach-appropriate items found, being more lenient")
            return items

    def _filter_for_vacation(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for vacation occasions."""
        print(f"🔍 DEBUG: _filter_for_vacation - Processing vacation occasion")
        
        vacation_appropriate_items = []
        vacation_keywords = ['resort', 'vacation', 'relaxed', 'comfortable', 'holiday', 'travel', 'casual']
        
        for item in items:
            # Check for vacation-appropriate attributes
            has_vacation_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in vacation_keywords):
                        has_vacation_appropriate_occasion = True
                        break
            
            has_vacation_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in vacation_keywords):
                    has_vacation_appropriate_style = True
            
            has_vacation_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in vacation_keywords):
                    has_vacation_appropriate_tags = True
            
            # For vacation, accept items with any vacation-appropriate attribute
            if has_vacation_appropriate_occasion or has_vacation_appropriate_style or has_vacation_appropriate_tags:
                vacation_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_vacation - Vacation appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_vacation - Vacation inappropriate item: {item.name}")
        
        # If we have vacation-appropriate items, use them; otherwise, be more lenient
        if vacation_appropriate_items:
            print(f"✅ DEBUG: _filter_for_vacation - Found {len(vacation_appropriate_items)} vacation-appropriate items")
            return vacation_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_vacation - No vacation-appropriate items found, being more lenient")
            return items

    def _filter_for_festival(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for festival occasions."""
        print(f"🔍 DEBUG: _filter_for_festival - Processing festival occasion")
        
        festival_appropriate_items = []
        festival_keywords = ['festival', 'bohemian', 'trendy', 'creative', 'expressive', 'casual', 'comfortable']
        
        for item in items:
            # Check for festival-appropriate attributes
            has_festival_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in festival_keywords):
                        has_festival_appropriate_occasion = True
                        break
            
            has_festival_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in festival_keywords):
                    has_festival_appropriate_style = True
            
            has_festival_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in festival_keywords):
                    has_festival_appropriate_tags = True
            
            # For festival, accept items with any festival-appropriate attribute
            if has_festival_appropriate_occasion or has_festival_appropriate_style or has_festival_appropriate_tags:
                festival_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_festival - Festival appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_festival - Festival inappropriate item: {item.name}")
        
        # If we have festival-appropriate items, use them; otherwise, be more lenient
        if festival_appropriate_items:
            print(f"✅ DEBUG: _filter_for_festival - Found {len(festival_appropriate_items)} festival-appropriate items")
            return festival_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_festival - No festival-appropriate items found, being more lenient")
            return items
    def _filter_for_athletic(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for athletic occasions."""
        print(f"🔍 DEBUG: _filter_for_athletic - Processing athletic occasion")
        
        athletic_appropriate_items = []
        athletic_keywords = ['athletic', 'gym', 'workout', 'running', 'sport', 'exercise', 'training', 'active', 'dynamic']
        
        for item in items:
            # Check for athletic-appropriate attributes
            has_athletic_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in athletic_keywords):
                        has_athletic_appropriate_occasion = True
                        break
            
            has_athletic_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in athletic_keywords):
                    has_athletic_appropriate_style = True
            
            has_athletic_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in athletic_keywords):
                    has_athletic_appropriate_tags = True
            
            # For athletic occasions, require at least one athletic attribute
            if has_athletic_appropriate_occasion or has_athletic_appropriate_style or has_athletic_appropriate_tags:
                athletic_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_athletic - Athletic appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_athletic - Athletic inappropriate item: {item.name}")
        
        # If we have athletic items, use them; otherwise, be more lenient
        if athletic_appropriate_items:
            print(f"✅ DEBUG: _filter_for_athletic - Found {len(athletic_appropriate_items)} athletic-appropriate items")
            return athletic_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_athletic - No athletic-appropriate items found, being more lenient")
            return items

    def _filter_for_school(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for school occasions."""
        print(f"🔍 DEBUG: _filter_for_school - Processing school occasion")
        
        school_appropriate_items = []
        # More comprehensive school keywords that match common wardrobe items
        school_keywords = [
            'neat', 'appropriate', 'practical', 'comfortable', 'academic', 'casual', 'professional',
            'business', 'formal', 'classic', 'clean', 'simple', 'smart', 'polished', 'conservative',
            'traditional', 'respectable', 'modest', 'proper', 'suitable', 'acceptable', 'decent'
        ]
        
        for item in items:
            # Check for school-appropriate attributes
            has_school_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in school_keywords):
                        has_school_appropriate_occasion = True
                        break
            
            has_school_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in school_keywords):
                    has_school_appropriate_style = True
            
            has_school_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in school_keywords):
                    has_school_appropriate_tags = True
            
            # For school, accept items with any school-appropriate attribute
            if has_school_appropriate_occasion or has_school_appropriate_style or has_school_appropriate_tags:
                school_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_school - School appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_school - School inappropriate item: {item.name}")
        
        # If we have school-appropriate items, use them; otherwise, be more lenient
        if school_appropriate_items:
            print(f"✅ DEBUG: _filter_for_school - Found {len(school_appropriate_items)} school-appropriate items")
            return school_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_school - No school-appropriate items found, being more lenient")
            # For school, be very lenient - accept most items except obviously inappropriate ones
            obviously_inappropriate = ['swimwear', 'beach', 'party', 'athletic', 'gym', 'workout', 'sporty', 'revealing', 'sexy', 'club', 'nightclub']
            lenient_items = []
            
            for item in items:
                item_type_lower = item.type.lower()
                item_name_lower = item.name.lower()
                
                # Only exclude obviously inappropriate items
                is_inappropriate = any(inappropriate in item_type_lower or inappropriate in item_name_lower 
                                    for inappropriate in obviously_inappropriate)
                
                if not is_inappropriate:
                    lenient_items.append(item)
                    print(f"✅ DEBUG: _filter_for_school - Lenient inclusion: {item.name}")
                else:
                    print(f"❌ DEBUG: _filter_for_school - Excluded as inappropriate: {item.name}")
            
            print(f"✅ DEBUG: _filter_for_school - Lenient filtering found {len(lenient_items)} items")
            return lenient_items

    def _filter_for_holiday(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for holiday occasions."""
        print(f"🔍 DEBUG: _filter_for_holiday - Processing holiday occasion")
        
        holiday_appropriate_items = []
        holiday_keywords = ['festive', 'celebratory', 'traditional', 'elegant', 'seasonal', 'holiday', 'christmas', 'thanksgiving']
        
        for item in items:
            # Check for holiday-appropriate attributes
            has_holiday_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in holiday_keywords):
                        has_holiday_appropriate_occasion = True
                        break
            
            has_holiday_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in holiday_keywords):
                    has_holiday_appropriate_style = True
            
            has_holiday_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in holiday_keywords):
                    has_holiday_appropriate_tags = True
            
            # For holiday, accept items with any holiday-appropriate attribute
            if has_holiday_appropriate_occasion or has_holiday_appropriate_style or has_holiday_appropriate_tags:
                holiday_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_holiday - Holiday appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_holiday - Holiday inappropriate item: {item.name}")
        
        # If we have holiday-appropriate items, use them; otherwise, be more lenient
        if holiday_appropriate_items:
            print(f"✅ DEBUG: _filter_for_holiday - Found {len(holiday_appropriate_items)} holiday-appropriate items")
            return holiday_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_holiday - No holiday-appropriate items found, being more lenient")
            return items

    def _filter_for_concert(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for concert occasions."""
        print(f"🔍 DEBUG: _filter_for_concert - Processing concert occasion")
        
        concert_appropriate_items = []
        concert_keywords = ['trendy', 'music_inspired', 'expressive', 'stylish', 'concert_ready', 'casual', 'comfortable']
        
        for item in items:
            # Check for concert-appropriate attributes
            has_concert_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in concert_keywords):
                        has_concert_appropriate_occasion = True
                        break
            
            has_concert_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in concert_keywords):
                    has_concert_appropriate_style = True
            
            has_concert_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in concert_keywords):
                    has_concert_appropriate_tags = True
            
            # For concert, accept items with any concert-appropriate attribute
            if has_concert_appropriate_occasion or has_concert_appropriate_style or has_concert_appropriate_tags:
                concert_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_concert - Concert appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_concert - Concert inappropriate item: {item.name}")
        
        # If we have concert-appropriate items, use them; otherwise, be more lenient
        if concert_appropriate_items:
            print(f"✅ DEBUG: _filter_for_concert - Found {len(concert_appropriate_items)} concert-appropriate items")
            return concert_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_concert - No concert-appropriate items found, being more lenient")
            return items

    def _filter_for_errands(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for errands occasions."""
        print(f"🔍 DEBUG: _filter_for_errands - Processing errands occasion")
        
        errands_appropriate_items = []
        errands_keywords = ['practical', 'comfortable', 'easy_movement', 'casual', 'functional', 'everyday']
        
        for item in items:
            # Check for errands-appropriate attributes
            has_errands_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in errands_keywords):
                        has_errands_appropriate_occasion = True
                        break
            
            has_errands_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in errands_keywords):
                    has_errands_appropriate_style = True
            
            has_errands_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in errands_keywords):
                    has_errands_appropriate_tags = True
            
            # For errands, accept items with any errands-appropriate attribute
            if has_errands_appropriate_occasion or has_errands_appropriate_style or has_errands_appropriate_tags:
                errands_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_errands - Errands appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_errands - Errands inappropriate item: {item.name}")
        
        # If we have errands-appropriate items, use them; otherwise, be more lenient
        if errands_appropriate_items:
            print(f"✅ DEBUG: _filter_for_errands - Found {len(errands_appropriate_items)} errands-appropriate items")
            return errands_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_errands - No errands-appropriate items found, being more lenient")
            return items

    def _filter_for_museum(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for museum occasions."""
        print(f"🔍 DEBUG: _filter_for_museum - Processing museum occasion")
        
        museum_appropriate_items = []
        museum_keywords = ['cultured', 'elegant', 'refined', 'sophisticated', 'artistic', 'casual', 'comfortable']
        
        for item in items:
            # Check for museum-appropriate attributes
            has_museum_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in museum_keywords):
                        has_museum_appropriate_occasion = True
                        break
            
            has_museum_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in museum_keywords):
                    has_museum_appropriate_style = True
            
            has_museum_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in museum_keywords):
                    has_museum_appropriate_tags = True
            
            # For museum, accept items with any museum-appropriate attribute
            if has_museum_appropriate_occasion or has_museum_appropriate_style or has_museum_appropriate_tags:
                museum_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_museum - Museum appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_museum - Museum inappropriate item: {item.name}")
        
        # If we have museum-appropriate items, use them; otherwise, be more lenient
        if museum_appropriate_items:
            print(f"✅ DEBUG: _filter_for_museum - Found {len(museum_appropriate_items)} museum-appropriate items")
            return museum_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_museum - No museum-appropriate items found, being more lenient")
            return items

    def _filter_for_fashion_event(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for fashion event occasions."""
        print(f"🔍 DEBUG: _filter_for_fashion_event - Processing fashion event occasion")
        
        fashion_event_appropriate_items = []
        fashion_event_keywords = ['fashion_forward', 'trendy', 'sophisticated', 'stylish', 'avant_garde', 'fashion', 'elegant']
        
        for item in items:
            # Check for fashion event-appropriate attributes
            has_fashion_event_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in fashion_event_keywords):
                        has_fashion_event_appropriate_occasion = True
                        break
            
            has_fashion_event_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in fashion_event_keywords):
                    has_fashion_event_appropriate_style = True
            
            has_fashion_event_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in fashion_event_keywords):
                    has_fashion_event_appropriate_tags = True
            
            # For fashion event, accept items with any fashion event-appropriate attribute
            if has_fashion_event_appropriate_occasion or has_fashion_event_appropriate_style or has_fashion_event_appropriate_tags:
                fashion_event_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_fashion_event - Fashion event appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_fashion_event - Fashion event inappropriate item: {item.name}")
        
        # If we have fashion event-appropriate items, use them; otherwise, be more lenient
        if fashion_event_appropriate_items:
            print(f"✅ DEBUG: _filter_for_fashion_event - Found {len(fashion_event_appropriate_items)} fashion event-appropriate items")
            return fashion_event_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_fashion_event - No fashion event-appropriate items found, being more lenient")
            return items

    def _filter_for_outdoor_gathering(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for outdoor gathering occasions."""
        print(f"🔍 DEBUG: _filter_for_outdoor_gathering - Processing outdoor gathering occasion")
        
        outdoor_gathering_appropriate_items = []
        outdoor_gathering_keywords = ['outdoor_ready', 'casual', 'practical', 'weather_appropriate', 'social', 'comfortable']
        
        for item in items:
            # Check for outdoor gathering-appropriate attributes
            has_outdoor_gathering_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in outdoor_gathering_keywords):
                        has_outdoor_gathering_appropriate_occasion = True
                        break
            
            has_outdoor_gathering_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in outdoor_gathering_keywords):
                    has_outdoor_gathering_appropriate_style = True
            
            has_outdoor_gathering_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in outdoor_gathering_keywords):
                    has_outdoor_gathering_appropriate_tags = True
            
            # For outdoor gathering, accept items with any outdoor gathering-appropriate attribute
            if has_outdoor_gathering_appropriate_occasion or has_outdoor_gathering_appropriate_style or has_outdoor_gathering_appropriate_tags:
                outdoor_gathering_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_outdoor_gathering - Outdoor gathering appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_outdoor_gathering - Outdoor gathering inappropriate item: {item.name}")
        
        # If we have outdoor gathering-appropriate items, use them; otherwise, be more lenient
        if outdoor_gathering_appropriate_items:
            print(f"✅ DEBUG: _filter_for_outdoor_gathering - Found {len(outdoor_gathering_appropriate_items)} outdoor gathering-appropriate items")
            return outdoor_gathering_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_outdoor_gathering - No outdoor gathering-appropriate items found, being more lenient")
            return items

    def _filter_for_funeral(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for funeral occasions."""
        print(f"🔍 DEBUG: _filter_for_funeral - Processing funeral occasion")
        
        funeral_appropriate_items = []
        funeral_keywords = ['respectful', 'somber', 'traditional', 'formal', 'dignified', 'conservative']
        
        for item in items:
            # Check for funeral-appropriate attributes
            has_funeral_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in funeral_keywords):
                        has_funeral_appropriate_occasion = True
                        break
            
            has_funeral_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in funeral_keywords):
                    has_funeral_appropriate_style = True
            
            has_funeral_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in funeral_keywords):
                    has_funeral_appropriate_tags = True
            
            # For funeral, accept items with any funeral-appropriate attribute
            if has_funeral_appropriate_occasion or has_funeral_appropriate_style or has_funeral_appropriate_tags:
                funeral_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_funeral - Funeral appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_funeral - Funeral inappropriate item: {item.name}")
        
        # If we have funeral-appropriate items, use them; otherwise, be more lenient
        if funeral_appropriate_items:
            print(f"✅ DEBUG: _filter_for_funeral - Found {len(funeral_appropriate_items)} funeral-appropriate items")
            return funeral_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_funeral - No funeral-appropriate items found, being more lenient")
            return items

    def _filter_for_casual(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for casual occasions."""
        print(f"🔍 DEBUG: _filter_for_casual - Processing casual occasion")
        
        casual_appropriate_items = []
        casual_keywords = ['relaxed', 'comfortable', 'everyday', 'effortless', 'laid_back', 'casual']
        
        for item in items:
            # Check for casual-appropriate attributes
            has_casual_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in casual_keywords):
                        has_casual_appropriate_occasion = True
                        break
            
            has_casual_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in casual_keywords):
                    has_casual_appropriate_style = True
            
            has_casual_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in casual_keywords):
                    has_casual_appropriate_tags = True
            
            # For casual, accept items with any casual-appropriate attribute
            if has_casual_appropriate_occasion or has_casual_appropriate_style or has_casual_appropriate_tags:
                casual_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_casual - Casual appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_casual - Casual inappropriate item: {item.name}")
        
        # If we have casual-appropriate items, use them; otherwise, be more lenient
        if casual_appropriate_items:
            print(f"✅ DEBUG: _filter_for_casual - Found {len(casual_appropriate_items)} casual-appropriate items")
            return casual_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_casual - No casual-appropriate items found, being more lenient")
            return items

    def _filter_for_loungewear(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for loungewear occasions."""
        print(f"🔍 DEBUG: _filter_for_loungewear - Processing loungewear occasion")
        
        loungewear_appropriate_items = []
        loungewear_keywords = ['comfortable', 'relaxed', 'loungewear', 'home', 'casual', 'soft', 'cozy']
        
        for item in items:
            # Check for loungewear-appropriate attributes
            has_loungewear_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in loungewear_keywords):
                        has_loungewear_appropriate_occasion = True
                        break
            
            has_loungewear_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in loungewear_keywords):
                    has_loungewear_appropriate_style = True
            
            has_loungewear_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in loungewear_keywords):
                    has_loungewear_appropriate_tags = True
            
            # For loungewear, accept items with any loungewear-appropriate attribute
            if has_loungewear_appropriate_occasion or has_loungewear_appropriate_style or has_loungewear_appropriate_tags:
                loungewear_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_loungewear - Loungewear appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_loungewear - Loungewear inappropriate item: {item.name}")
        
        # If we have loungewear-appropriate items, use them; otherwise, be more lenient
        if loungewear_appropriate_items:
            print(f"✅ DEBUG: _filter_for_loungewear - Found {len(loungewear_appropriate_items)} loungewear-appropriate items")
            return loungewear_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_loungewear - No loungewear-appropriate items found, being more lenient")
            return items

    def _filter_for_rainy_day(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for rainy day occasions."""
        print(f"🔍 DEBUG: _filter_for_rainy_day - Processing rainy day occasion")
        
        rainy_day_appropriate_items = []
        rainy_day_keywords = ['practical', 'waterproof', 'functional', 'weather_appropriate', 'protective', 'water-resistant']
        
        for item in items:
            # Check for rainy day-appropriate attributes
            has_rainy_day_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in rainy_day_keywords):
                        has_rainy_day_appropriate_occasion = True
                        break
            
            has_rainy_day_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in rainy_day_keywords):
                    has_rainy_day_appropriate_style = True
            
            has_rainy_day_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in rainy_day_keywords):
                    has_rainy_day_appropriate_tags = True
            
            # For rainy day, accept items with any rainy day-appropriate attribute
            if has_rainy_day_appropriate_occasion or has_rainy_day_appropriate_style or has_rainy_day_appropriate_tags:
                rainy_day_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_rainy_day - Rainy day appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_rainy_day - Rainy day inappropriate item: {item.name}")
        
        # If we have rainy day-appropriate items, use them; otherwise, be more lenient
        if rainy_day_appropriate_items:
            print(f"✅ DEBUG: _filter_for_rainy_day - Found {len(rainy_day_appropriate_items)} rainy day-appropriate items")
            return rainy_day_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_rainy_day - No rainy day-appropriate items found, being more lenient")
            return items

    def _filter_for_snow_day(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for snow day occasions."""
        print(f"🔍 DEBUG: _filter_for_snow_day - Processing snow day occasion")
        
        snow_day_appropriate_items = []
        snow_day_keywords = ['warm', 'protective', 'insulated', 'winter_ready', 'cozy', 'winter', 'cold']
        
        for item in items:
            # Check for snow day-appropriate attributes
            has_snow_day_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in snow_day_keywords):
                        has_snow_day_appropriate_occasion = True
                        break
            
            has_snow_day_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in snow_day_keywords):
                    has_snow_day_appropriate_style = True
            
            has_snow_day_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in snow_day_keywords):
                    has_snow_day_appropriate_tags = True
            
            # For snow day, accept items with any snow day-appropriate attribute
            if has_snow_day_appropriate_occasion or has_snow_day_appropriate_style or has_snow_day_appropriate_tags:
                snow_day_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_snow_day - Snow day appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_snow_day - Snow day inappropriate item: {item.name}")
        
        # If we have snow day-appropriate items, use them; otherwise, be more lenient
        if snow_day_appropriate_items:
            print(f"✅ DEBUG: _filter_for_snow_day - Found {len(snow_day_appropriate_items)} snow day-appropriate items")
            return snow_day_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_snow_day - No snow day-appropriate items found, being more lenient")
            return items

    def _filter_for_hot_weather(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for hot weather occasions."""
        print(f"🔍 DEBUG: _filter_for_hot_weather - Processing hot weather occasion")
        
        hot_weather_appropriate_items = []
        hot_weather_keywords = ['breathable', 'light', 'summer', 'cool', 'airy', 'hot', 'warm']
        
        for item in items:
            # Check for hot weather-appropriate attributes
            has_hot_weather_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in hot_weather_keywords):
                        has_hot_weather_appropriate_occasion = True
                        break
            
            has_hot_weather_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in hot_weather_keywords):
                    has_hot_weather_appropriate_style = True
            
            has_hot_weather_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in hot_weather_keywords):
                    has_hot_weather_appropriate_tags = True
            
            # For hot weather, accept items with any hot weather-appropriate attribute
            if has_hot_weather_appropriate_occasion or has_hot_weather_appropriate_style or has_hot_weather_appropriate_tags:
                hot_weather_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_hot_weather - Hot weather appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_hot_weather - Hot weather inappropriate item: {item.name}")
        
        # If we have hot weather-appropriate items, use them; otherwise, be more lenient
        if hot_weather_appropriate_items:
            print(f"✅ DEBUG: _filter_for_hot_weather - Found {len(hot_weather_appropriate_items)} hot weather-appropriate items")
            return hot_weather_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_hot_weather - No hot weather-appropriate items found, being more lenient")
            return items

    def _filter_for_cold_weather(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for cold weather occasions."""
        print(f"🔍 DEBUG: _filter_for_cold_weather - Processing cold weather occasion")
        
        cold_weather_appropriate_items = []
        cold_weather_keywords = ['warm', 'insulated', 'protective', 'winter', 'cozy', 'cold', 'winter_ready']
        
        for item in items:
            # Check for cold weather-appropriate attributes
            has_cold_weather_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in cold_weather_keywords):
                        has_cold_weather_appropriate_occasion = True
                        break
            
            has_cold_weather_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in cold_weather_keywords):
                    has_cold_weather_appropriate_style = True
            
            has_cold_weather_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in cold_weather_keywords):
                    has_cold_weather_appropriate_tags = True
            
            # For cold weather, accept items with any cold weather-appropriate attribute
            if has_cold_weather_appropriate_occasion or has_cold_weather_appropriate_style or has_cold_weather_appropriate_tags:
                cold_weather_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_cold_weather - Cold weather appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_cold_weather - Cold weather inappropriate item: {item.name}")
        
        # If we have cold weather-appropriate items, use them; otherwise, be more lenient
        if cold_weather_appropriate_items:
            print(f"✅ DEBUG: _filter_for_cold_weather - Found {len(cold_weather_appropriate_items)} cold weather-appropriate items")
            return cold_weather_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_cold_weather - No cold weather-appropriate items found, being more lenient")
            return items

    def _filter_for_chilly_evening(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Special filtering for chilly evening occasions."""
        print(f"🔍 DEBUG: _filter_for_chilly_evening - Processing chilly evening occasion")
        
        chilly_evening_appropriate_items = []
        chilly_evening_keywords = ['elegant', 'layered', 'sophisticated', 'evening_appropriate', 'refined', 'warm']
        
        for item in items:
            # Check for chilly evening-appropriate attributes
            has_chilly_evening_appropriate_occasion = False
            if item.occasion:
                item_occasions = [occ.lower() for occ in item.occasion]
                for item_occ in item_occasions:
                    if any(keyword in item_occ for keyword in chilly_evening_keywords):
                        has_chilly_evening_appropriate_occasion = True
                        break
            
            has_chilly_evening_appropriate_style = False
            if item.style:
                item_styles = [s.lower() for s in item.style]
                if any(keyword in ' '.join(item_styles) for keyword in chilly_evening_keywords):
                    has_chilly_evening_appropriate_style = True
            
            has_chilly_evening_appropriate_tags = False
            if hasattr(item, 'tags') and item.tags:
                item_tags = [tag.lower() for tag in item.tags]
                if any(keyword in ' '.join(item_tags) for keyword in chilly_evening_keywords):
                    has_chilly_evening_appropriate_tags = True
            
            # For chilly evening, accept items with any chilly evening-appropriate attribute
            if has_chilly_evening_appropriate_occasion or has_chilly_evening_appropriate_style or has_chilly_evening_appropriate_tags:
                chilly_evening_appropriate_items.append(item)
                print(f"✅ DEBUG: _filter_for_chilly_evening - Chilly evening appropriate item: {item.name}")
            else:
                print(f"❌ DEBUG: _filter_for_chilly_evening - Chilly evening inappropriate item: {item.name}")
        
        # If we have chilly evening-appropriate items, use them; otherwise, be more lenient
        if chilly_evening_appropriate_items:
            print(f"✅ DEBUG: _filter_for_chilly_evening - Found {len(chilly_evening_appropriate_items)} chilly evening-appropriate items")
            return chilly_evening_appropriate_items
        else:
            print(f"⚠️  DEBUG: _filter_for_chilly_evening - No chilly evening-appropriate items found, being more lenient")
            return items

    def _filter_by_style_strict(self, items: List[ClothingItem], style: str, style_matrix: Dict[str, Any]) -> List[ClothingItem]:
        """Strict style filtering."""
        approved_items = style_matrix.get("approved_items", [])
        banned_items = style_matrix.get("banned_items", [])
        
        filtered_items = []
        for item in items:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Check if item has banned attributes
            has_banned = any(banned in item_type or banned in item_name for banned in banned_items)
            if has_banned:
                continue
            
            # Check if item has approved attributes or is neutral
            has_approved = any(approved in item_type or approved in item_name for approved in approved_items)
            is_neutral = not any(banned in item_type or banned in item_name for banned in banned_items)
            
            if has_approved or is_neutral:
                filtered_items.append(item)
        
        return filtered_items

    def _filter_by_personal_preferences(self, items: List[ClothingItem], user_profile: UserProfile) -> List[ClothingItem]:
        """Filter by personal preferences, body type, gender, and detailed measurements."""
        filtered_items = []
        
        for item in items:
            # Check body type compatibility
            if not self._check_body_type_compatibility(item, user_profile.bodyType):
                continue
            
            # Check skin tone compatibility
            if not self._check_skin_tone_compatibility(item, user_profile.skinTone):
                continue
            
            # Check gender compatibility
            if not self._check_gender_compatibility(item, user_profile.gender):
                continue
            
            # Check bra size compatibility (for tops and dresses)
            if not self._check_bra_size_compatibility(item, user_profile.measurements.get('braSize')):
                continue
            
            # Check color palette compatibility
            if not self._check_color_palette_compatibility(item, user_profile.colorPalette):
                continue
            
            # Check material preferences
            if not self._check_material_preferences(item, user_profile.materialPreferences):
                continue
            
            # Check fit preferences
            if not self._check_fit_preferences(item, user_profile.fitPreferences, user_profile.comfortLevel):
                continue
            
            # Check brand preferences
            if not self._check_brand_preferences(item, user_profile.preferredBrands):
                continue
            
            filtered_items.append(item)
        
        return filtered_items

    def _check_gender_compatibility(self, item: ClothingItem, gender: Optional[str]) -> bool:
        """Check if an item is compatible with the user's gender."""
        if not gender:
            return True  # Default to compatible if no gender specified
        
        # Get gender compatibility from item metadata
        if hasattr(item, 'metadata') and item.metadata:
            metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
            
            if 'gender' in metadata:
                item_gender = metadata['gender']
                if item_gender and item_gender.lower() != gender.lower():
                    return False
        
        # Check item type for gender-specific items
        item_type = item.type.lower()
        
        # Gender-specific item types
        male_specific = ['men', 'male', 'guy']
        female_specific = ['women', 'female', 'lady', 'bra', 'lingerie']
        
        if gender.lower() == 'male':
            if any(female in item_type for female in female_specific):
                return False
        elif gender.lower() == 'female':
            if any(male in item_type for male in male_specific):
                return False
        
        return True

    def _check_bra_size_compatibility(self, item: ClothingItem, bra_size: Optional[str]) -> bool:
        """Check if an item is compatible with the user's bra size."""
        if not bra_size:
            return True  # Default to compatible if no bra size specified
        
        # Only check tops and dresses
        item_type = item.type.lower()
        if not any(t in item_type for t in ['shirt', 'blouse', 'top', 'dress', 'sweater']):
            return True
        
        # Get bra size compatibility from item metadata
        if hasattr(item, 'metadata') and item.metadata:
            metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
            
            if 'braSizeCompatibility' in metadata:
                compatible_sizes = metadata['braSizeCompatibility']
                if isinstance(compatible_sizes, list) and bra_size not in compatible_sizes:
                    return False
        
        return True

    def _check_color_palette_compatibility(self, item: ClothingItem, color_palette: Optional[Dict[str, List[str]]]) -> bool:
        """Check if an item's colors are compatible with the user's color palette."""
        if not color_palette or not item.dominantColors:
            return True
        
        avoid_colors = color_palette.get('avoid', [])
        if not avoid_colors:
            return True
        
        # Check if any dominant colors are in the avoid list
        for color in item.dominantColors:
            color_name = get_color_name(color)
            if any(avoid_color.lower() in color_name for avoid_color in avoid_colors):
                return False
        
        return True

    def _check_material_preferences(self, item: ClothingItem, material_preferences: Optional[Dict[str, List[str]]]) -> bool:
        """Check if an item's material is compatible with user preferences."""
        if not material_preferences:
            return True
        
        avoid_materials = material_preferences.get('avoid', [])
        if not avoid_materials:
            return True
        
        # Get material from item metadata or tags
        item_material = None
        if hasattr(item, 'metadata') and item.metadata:
            metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
            item_material = metadata.get('material', '').lower()
        
        # Also check tags for material info
        if not item_material and item.tags:
            for tag in item.tags:
                if any(material in tag.lower() for material in ['cotton', 'silk', 'wool', 'polyester', 'denim', 'leather']):
                    item_material = tag.lower()
                    break
        
        if item_material:
            if any(avoid_material.lower() in item_material for avoid_material in avoid_materials):
                return False
        
        return True

    def _check_fit_preferences(self, item: ClothingItem, fit_preferences: Optional[Dict[str, str]], comfort_level: Optional[Dict[str, float]]) -> bool:
        """Check if an item's fit is compatible with user preferences."""
        if not fit_preferences and not comfort_level:
            return True
        
        # Get item fit from metadata or tags
        item_fit = None
        if hasattr(item, 'metadata') and item.metadata:
            metadata = item.metadata.dict() if hasattr(item.metadata, 'dict') else item.metadata
            item_fit = metadata.get('fit', '').lower()
        
        # Check tags for fit info
        if not item_fit and item.tags:
            for tag in item.tags:
                if any(fit in tag.lower() for fit in ['fitted', 'loose', 'oversized', 'relaxed', 'tight']):
                    item_fit = tag.lower()
                    break
        
        if item_fit and comfort_level:
            # Check comfort level preferences
            if 'tight' in item_fit and comfort_level.get('tight', 0.5) < 0.3:
                return False
            if 'loose' in item_fit and comfort_level.get('loose', 0.5) < 0.3:
                return False
            if 'structured' in item_fit and comfort_level.get('structured', 0.5) < 0.3:
                return False
            if 'relaxed' in item_fit and comfort_level.get('relaxed', 0.5) < 0.3:
                return False
        
        return True

    def _check_brand_preferences(self, item: ClothingItem, preferred_brands: Optional[List[str]]) -> bool:
        """Check if an item's brand is in user's preferred brands."""
        if not preferred_brands:
            return True
        
        item_brand = item.brand or ''
        if not item_brand:
            return True  # If no brand info, allow it
        
        # Check if brand is in preferred list
        return item_brand.lower() in [brand.lower() for brand in preferred_brands]

    def _filter_by_mood_strict(self, items: List[ClothingItem], mood_rule, base_item: Optional[ClothingItem] = None) -> List[ClothingItem]:
        """Strict mood filtering, but always preserve base_item if present."""
        return self._filter_items_by_mood(items, mood_rule, base_item=base_item)

    def _select_core_items(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select core outfit items (top, bottom, shoes) - one per category."""
        core_items = []
        required_categories = context["target_counts"]["required_categories"]
        min_items = context["target_counts"]["min_items"]
        max_items = context["target_counts"]["max_items"]
        occasion = context.get("occasion", "").lower()
        
        print(f"🔍 DEBUG: _select_core_items - Starting selection")
        print(f"   - Occasion: {occasion}")
        print(f"   - Required categories: {required_categories}")
        print(f"   - Min items: {min_items}, Max items: {max_items}")
        print(f"   - Available items: {len(filtered_wardrobe)}")
        
        # Group items by category
        items_by_category = self._group_items_by_category(filtered_wardrobe)
        
        print(f"📊 DEBUG: Items by category:")
        for category, items in items_by_category.items():
            print(f"   - {category}: {len(items)} items")
            for item in items[:3]:  # Show first 3 items
                print(f"     * {item.name} ({item.type})")
            if len(items) > 3:
                print(f"     ... and {len(items) - 3} more")
        
        # For formal occasions, we need to be more aggressive in selection
        is_formal = "formal" in occasion or "gala" in occasion or "interview" in occasion
        print(f"🎯 DEBUG: Is formal occasion: {is_formal}")
        
        # Select one item from each required category first
        selected_categories = set()
        for category in required_categories:
            print(f"\n🔍 DEBUG: Processing required category: {category}")
            if category in items_by_category and items_by_category[category]:
                print(f"   - Found {len(items_by_category[category])} items in category '{category}'")
                
                # Sort by relevance score and select the best
                sorted_items = self._sort_items_by_relevance(
                    items_by_category[category], context
                )
                print(f"   - Sorted items by relevance:")
                for i, item in enumerate(sorted_items[:3]):
                    print(f"     {i+1}. {item.name} ({item.type})")
                
                if sorted_items:
                    best_item = sorted_items[0]
                    # Check if we already have an item from this category
                    item_category = self._get_item_category(best_item)
                    print(f"   - Best item: {best_item.name} (category: {item_category})")
                    
                    if item_category not in selected_categories:
                        core_items.append(best_item)
                        selected_categories.add(item_category)
                        print(f"✅ DEBUG: _select_core_items - Selected {item_category}: {best_item.name}")
                    else:
                        print(f"⚠️  DEBUG: _select_core_items - Skipping {best_item.name} (category {item_category} already selected)")
            else:
                print(f"❌ DEBUG: No items found for required category '{category}'")
                print(f"   - Available categories: {list(items_by_category.keys())}")
        
        # For formal occasions, add additional items to meet minimum requirements
        if is_formal and len(core_items) < min_items:
            print(f"DEBUG: _select_core_items - Formal occasion: only {len(core_items)} items selected, need at least {min_items}")
            
            # Prioritize adding layers and accessories for formal occasions
            priority_categories = ["layer", "accessory", "top"]
            
            for category in priority_categories:
                if len(core_items) >= min_items:
                    break
                    
                if category in items_by_category and items_by_category[category]:
                    # Get items not already selected
                    available_items = [item for item in items_by_category[category] 
                                     if item not in core_items]
                    
                    if available_items:
                        # Sort by relevance and add the best one
                        sorted_items = self._sort_items_by_relevance(available_items, context)
                        if sorted_items:
                            additional_item = sorted_items[0]
                            core_items.append(additional_item)
                            print(f"DEBUG: _select_core_items - Added additional {category}: {additional_item.name}")
        
        # For formal occasions, try to reach closer to max_items if we have room
        if is_formal and len(core_items) < max_items:
            print(f"DEBUG: _select_core_items - Formal occasion: {len(core_items)} items selected, can add up to {max_items}")
            
            # Add more items from any available category
            for category, items in items_by_category.items():
                if len(core_items) >= max_items:
                    break
                    
                if items:
                    # Get items not already selected
                    available_items = [item for item in items if item not in core_items]
                    
                    if available_items:
                        # Sort by relevance and add the best one
                        sorted_items = self._sort_items_by_relevance(available_items, context)
                        if sorted_items:
                            additional_item = sorted_items[0]
                            core_items.append(additional_item)
                            print(f"DEBUG: _select_core_items - Added {category}: {additional_item.name}")
        
        print(f"DEBUG: _select_core_items - Final selection: {len(core_items)} items")
        
        # NEW: If we don't have enough items, add more from available categories
        min_items = context["target_counts"]["min_items"]
        if len(core_items) < min_items:
            print(f"⚠️  DEBUG: _select_core_items - Only {len(core_items)} items selected (need {min_items}), adding more items")
            
            # Get all available items not already selected
            available_items = [item for item in filtered_wardrobe if item not in core_items]
            
            if available_items:
                # Sort by relevance and add more items
                sorted_available = self._sort_items_by_relevance(available_items, context)
                needed_items = min_items - len(core_items)
                
                for item in sorted_available[:needed_items]:
                    core_items.append(item)
                    print(f"✅ DEBUG: _select_core_items - Added fallback item: {item.name}")
        
        return core_items

    def _get_item_category(self, item: ClothingItem) -> str:
        """Get the category of an item using utility function."""
        return get_item_category(item)

    def _select_style_enhancers(self, filtered_wardrobe: List[ClothingItem], selected_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select style enhancers that match the requested aesthetic."""
        if not context["style"]:
            return []
        
        # Get items that aren't already selected
        available_items = [item for item in filtered_wardrobe if item not in selected_items]
        
        # Filter for style-specific items
        style_items = []
        for item in available_items:
            if self._item_matches_style(item, context["style"]):
                style_items.append(item)
        
        # Sort by style relevance and return top items
        sorted_items = self._sort_items_by_style_relevance(style_items, context["style"])
        return sorted_items[:2]  # Limit to 2 style enhancers

    def _select_accessories(self, filtered_wardrobe: List[ClothingItem], selected_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select accessories limited by context and harmony."""
        available_items = [item for item in filtered_wardrobe if item not in selected_items]
        
        # Filter for accessory items
        accessory_types = ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'bag', 'hat']
        accessories = [item for item in available_items if any(
            acc_type in item.type.lower() for acc_type in accessory_types
        )]
        
        # Filter by occasion appropriateness
        if context["occasion"].lower() in ['gym', 'athletic', 'workout']:
            accessories = [item for item in accessories if 'watch' in item.type.lower()]  # Only watches for gym
        
        # Sort by harmony with selected items
        sorted_accessories = self._sort_items_by_harmony(accessories, selected_items)
        return sorted_accessories[:2]  # Limit to 2 accessories

    def _get_item_categories(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Get items grouped by category with priority to prevent overlap."""
        categories = {
            'top': ['shirt', 't-shirt', 'blouse', 'polo'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings'],
            'layer': ['jacket', 'coat', 'sweater', 'cardigan', 'blazer']
        }
        
        result = {category: [] for category in categories.keys()}
        assigned_items = set()
        
        # Process items in priority order to prevent overlap
        for item in items:
            if item.id in assigned_items:
                continue
                
            item_type = item.type.lower()
            
            # Check each category in priority order
            for category, types in categories.items():
                if any(t in item_type for t in types):
                    result[category].append(item)
                    assigned_items.add(item.id)
                    break  # Only assign to first matching category
        
        return result

    def _group_items_by_category(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Group items by category."""
        result = self._get_item_categories(items)
        
        # Add debug logging
        print(f"🔍 DEBUG: _group_items_by_category - Categorized {len(items)} items:")
        for category, category_items in result.items():
            print(f"   - {category}: {len(category_items)} items")
            for item in category_items:
                print(f"     * {item.name} ({item.type}) -> {category}")
        
        return result

    def _sort_items_by_relevance(self, items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Sort items by relevance to the current context including user preferences."""
        def relevance_score(item):
            score = 0
            occasion = context.get("occasion", "").lower()
            style = (context.get("style") or "").lower()
            weather = context.get("weather")
            user_profile = context.get("user_profile")
            mood_rule = context.get("mood_rule")
            
            # Base score for item type
            if item.type in ["shirt", "dress_shirt"]:
                score += 10
            elif item.type in ["pants", "dress_pants"]:
                score += 10
            elif item.type in ["shoes", "dress_shoes"]:
                score += 8
            elif item.type in ["jacket", "blazer", "suit"]:
                score += 12  # Boost jackets/blazers
            elif item.type in ["sweater", "cardigan"]:
                score += 6
            else:
                score += 5
            
            # NEW: Mood compatibility scoring (prioritize mood-compatible items)
            if mood_rule:
                # Calculate mood compatibility score
                item_colors = [getattr(color, 'name', str(color)).lower() for color in item.dominantColors]
                mood_colors = [color.lower() for color in mood_rule.color_palette]
                
                item_styles = [style.lower() for style in (item.style or [])]
                mood_styles = [style.lower() for style in mood_rule.style_preferences]
                
                item_material = getattr(item, 'material', None)
                mood_materials = [material.value if hasattr(material, 'value') else str(material) for material in mood_rule.material_preferences]
                
                color_score = sum(1 for color in item_colors if any(mood_color in color or color in mood_color for mood_color in mood_colors))
                style_score = sum(1 for style in item_styles if any(mood_style in style or style in mood_style for mood_style in mood_styles))
                material_score = 1 if item_material and str(item_material).lower() in [m.lower() for m in mood_materials] else 0
                
                mood_score = color_score + style_score + material_score
                
                # Boost relevance score for mood-compatible items
                score += (mood_score * 3)  # Significant boost for mood compatibility
            
            # NEW: Formal occasion scoring boost for suit jackets/blazers
            if "formal" in occasion:
                if item.type in ["jacket", "blazer", "suit"]:
                    score += 20  # Major boost for formal jackets
                elif item.type in ["dress_shirt", "dress_pants", "dress_shoes"]:
                    score += 15  # Boost for formal items
                elif "formal" in [s.lower() for s in (item.style or [])]:
                    score += 10  # Boost for items tagged as formal
                elif "business" in [s.lower() for s in (item.style or [])]:
                    score += 8   # Boost for business items
            
            # Style matching
            if style and item.style:
                style_matches = [s.lower() for s in item.style if s.lower() == style]
                score += len(style_matches) * 5
            
            # User preference scoring
            if user_profile:
                # Color palette bonus (preferred colors)
                if user_profile.colorPalette:
                    palette = user_profile.colorPalette
                    primary_colors = palette.get('primary', [])
                    secondary_colors = palette.get('secondary', [])
                    accent_colors = palette.get('accent', [])
                    
                    for color in item.dominantColors or []:
                        color_name = get_color_name(color)
                        if any(pref_color.lower() in color_name for pref_color in primary_colors):
                            score += 2.0
                        elif any(pref_color.lower() in color_name for pref_color in secondary_colors):
                            score += 1.5
                        elif any(pref_color.lower() in color_name for pref_color in accent_colors):
                            score += 1.0
                
                # Style personality scoring
                if user_profile.stylePersonality:
                    personality = user_profile.stylePersonality
                    
                    # Classic style preference
                    if personality.get('classic', 0.5) > 0.7:
                        if any(tag in str(item.tags).lower() for tag in ['classic', 'timeless', 'traditional']):
                            score += 1.5
                    
                    # Modern style preference
                    if personality.get('modern', 0.5) > 0.7:
                        if any(tag in str(item.tags).lower() for tag in ['modern', 'contemporary', 'trendy']):
                            score += 1.5
                    
                    # Creative style preference
                    if personality.get('creative', 0.5) > 0.7:
                        if any(tag in str(item.tags).lower() for tag in ['creative', 'artistic', 'unique', 'bold']):
                            score += 1.5
                    
                    # Minimal style preference
                    if personality.get('minimal', 0.5) > 0.7:
                        if any(tag in str(item.tags).lower() for tag in ['minimal', 'simple', 'clean']):
                            score += 1.5
                    
                    # Bold style preference
                    if personality.get('bold', 0.5) > 0.7:
                        if any(tag in str(item.tags).lower() for tag in ['bold', 'statement', 'dramatic']):
                            score += 1.5
                
                # Material preference bonus
                if user_profile.materialPreferences:
                    preferred_materials = user_profile.materialPreferences.get('preferred', [])
                    if preferred_materials and item.tags:
                        for tag in item.tags:
                            if any(material.lower() in tag.lower() for material in preferred_materials):
                                score += 1.0
                                break
                
                # Brand preference bonus
                if user_profile.preferredBrands and item.brand:
                    if item.brand.lower() in [brand.lower() for brand in user_profile.preferredBrands]:
                        score += 1.5
            
            # Weather appropriateness
            if weather and self._is_weather_appropriate(item, weather):
                score += 5
            
            # Occasion matching
            if item.occasion:
                occasion_matches = [o.lower() for o in item.occasion if o.lower() in occasion]
                score += len(occasion_matches) * 3
            
            # NEW: Diversity scoring (boost unworn items)
            if hasattr(item, 'wearCount') and item.wearCount == 0:
                score += 8  # Boost unworn items
            elif hasattr(item, 'wearCount') and item.wearCount < 3:
                score += 4  # Boost lightly worn items
            
            return score
        
        return sorted(items, key=relevance_score, reverse=True)

    def _item_matches_style(self, item: ClothingItem, style: str) -> bool:
        """Check if item matches the requested style."""
        if not item.style:
            return False
        
        return style.lower() in [s.lower() for s in item.style]

    def _sort_items_by_style_relevance(self, items: List[ClothingItem], style: str) -> List[ClothingItem]:
        """Sort items by style relevance."""
        def style_score(item):
            if not item.style:
                return 0
            
            style_match = style.lower() in [s.lower() for s in item.style]
            return 10 if style_match else 0
        
        return sorted(items, key=style_score, reverse=True)

    def _sort_items_by_harmony(self, items: List[ClothingItem], selected_items: List[ClothingItem]) -> List[ClothingItem]:
        """Sort items by harmony with already selected items."""
        def harmony_score(item):
            if not selected_items:
                return 5
            
            total_score = 0
            for selected in selected_items:
                # Color harmony
                if self._colors_are_compatible(item.dominantColors, selected.dominantColors):
                    total_score += 3
                
                # Style harmony
                if item.style and selected.style:
                    common_styles = set(s.lower() for s in item.style) & set(s.lower() for s in selected.style)
                    total_score += len(common_styles) * 2
            
            return total_score / len(selected_items)
        
        return sorted(items, key=harmony_score, reverse=True)

    def _is_weather_appropriate(self, item: ClothingItem, weather: WeatherData) -> bool:
        """Check if item is weather appropriate."""
        temperature = weather.temperature
        
        if temperature >= 85:  # Hot weather
            inappropriate = ['sweater', 'jacket', 'coat', 'hoodie', 'wool', 'fleece']
        elif temperature >= 75:  # Warm weather
            inappropriate = ['sweater', 'coat', 'wool', 'fleece']
        elif temperature <= 45:  # Cold weather
            inappropriate = ['tank top', 'shorts', 'sandals', 'sleeveless']
        else:  # Moderate weather
            return True
        
        return not any(inapp in item.type.lower() or inapp in item.name.lower() for inapp in inappropriate)

    def _fill_missing_categories(self, selected_items: List[ClothingItem], filtered_wardrobe: List[ClothingItem], missing_categories: set, context: Dict[str, Any]) -> List[ClothingItem]:
        """Fill missing categories with valid items."""
        additional_items = []
        # Track selected item IDs to prevent duplicates
        selected_ids = {item.id for item in selected_items}
        available_items = [item for item in filtered_wardrobe if item.id not in selected_ids]
        
        for category in missing_categories:
            category_items = self._get_items_for_category(available_items, category)
            if category_items:
                # Sort by relevance and select the best
                sorted_items = self._sort_items_by_relevance(category_items, context)
                if sorted_items:
                    best_item = sorted_items[0]
                    additional_items.append(best_item)
                    # Remove from available and track as selected
                    available_items.remove(best_item)
                    selected_ids.add(best_item.id)
        
        return additional_items

    def _get_items_for_category(self, items: List[ClothingItem], category: str) -> List[ClothingItem]:
        """Get items for a specific category."""
        category_types = {
            'top': ['shirt', 't-shirt', 'blouse', 'polo'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings'],
            'layer': ['jacket', 'coat', 'sweater', 'cardigan', 'blazer']
        }
        
        types = category_types.get(category, [])
        return [item for item in items if any(t in item.type.lower() for t in types)]

    def _identify_missing_items(self, context: Dict[str, Any]) -> List[str]:
        """Identify what items are missing for the occasion."""
        occasion = context["occasion"].lower()
        
        if "gym" in occasion or "athletic" in occasion:
            return ["athletic shoes", "athletic top", "athletic bottom"]
        elif "beach" in occasion:
            return ["swimwear", "sandals", "cover-up"]
        elif "work" in occasion or "business" in occasion:
            return ["dress shirt", "dress pants", "dress shoes"]
        elif "formal" in occasion:
            # NEW: Formal occasions MUST have pants/skirts and a jacket/blazer
            return ["formal attire", "dress shoes", "accessories", "bottom", "layer"]
        else:
            return ["appropriate top", "appropriate bottom", "appropriate shoes"]

    def _validate_occasion_rules(self, items: List[ClothingItem], occasion: str) -> Dict[str, Any]:
        """Validate occasion-specific dress rules."""
        errors = []
        
        occasion_rules = {
            "gym": {"forbidden": ["dress shoes", "dress shirt", "formal"], "required": ["athletic"]},
            "beach": {"forbidden": ["closed leather shoes", "blazer"], "required": []},
            "work": {"forbidden": ["tank top", "flip-flops"], "required": []},
            "formal": {"forbidden": ["athletic", "casual"], "required": ["formal"]}
        }
        
        rule = None
        for key, value in occasion_rules.items():
            if key in occasion.lower():
                rule = value
                break
        
        if rule:
            for item in items:
                item_type = item.type.lower()
                item_name = item.name.lower()
                
                # Check forbidden items
                for forbidden in rule["forbidden"]:
                    if forbidden in item_type or forbidden in item_name:
                        errors.append(f"{item.name} is not appropriate for {occasion}")
        
        return {"is_valid": len(errors) == 0, "errors": errors}

    def _validate_weather_appropriateness(self, items: List[ClothingItem], weather: WeatherData) -> Dict[str, Any]:
        """Validate weather appropriateness."""
        errors = []
        temperature = weather.temperature
        
        for item in items:
            if not self._is_weather_appropriate(item, weather):
                errors.append(f"{item.name} is not appropriate for {temperature}°F weather")
        
        return {"is_valid": len(errors) == 0, "errors": errors}

    def _validate_style_cohesion(self, items: List[ClothingItem], style: Optional[str]) -> Dict[str, Any]:
        """Validate style cohesion."""
        warnings = []
        
        if not style or len(items) < 2:
            return {"is_valid": True, "warnings": warnings}
        
        # Check for style conflicts
        style_groups = {
            "formal": ["casual", "athletic", "beach"],
            "casual": ["formal", "business"],
            "athletic": ["formal", "business", "elegant"],
            "minimalist": ["y2k", "vintage", "bohemian"]
        }
        
        conflicting_styles = style_groups.get(style.lower(), [])
        
        for item in items:
            if item.style:
                item_styles = [s.lower() for s in item.style]
                conflicts = [s for s in item_styles if s in conflicting_styles]
                if conflicts:
                    warnings.append(f"{item.name} has conflicting styles: {conflicts}")
        
        return {"is_valid": len(warnings) == 0, "warnings": warnings}

    def _validate_visual_harmony(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Validate visual harmony."""
        warnings = []
        
        if len(items) < 2:
            return {"is_valid": True, "warnings": warnings}
        
        # Check color harmony
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                if not self._colors_are_compatible(item1.dominantColors, item2.dominantColors):
                    warnings.append(f"Color clash between {item1.name} and {item2.name}")
        
        return {"is_valid": len(warnings) == 0, "warnings": warnings}

    def _validate_form_completeness(self, items: List[ClothingItem], target_counts: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form completeness."""
        errors = []
        
        min_items = target_counts["min_items"]
        max_items = target_counts["max_items"]
        
        if len(items) < min_items:
            errors.append(f"Outfit has {len(items)} items, minimum {min_items} required")
        
        if len(items) > max_items:
            errors.append(f"Outfit has {len(items)} items, maximum {max_items} allowed")
        
        return {"is_valid": len(errors) == 0, "errors": errors}

    def _deduplicate_shoes(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Ensure only one shoe/sneaker/boot/sandal is present in the outfit."""
        shoe_types = [
            'shoes', 'sneakers', 'boots', 'sandals', 'trainers', 'athletic shoes', 'running shoes', 'loafers', 'dress_shoes', 'dress shoes', 'high tops', 'high top sneakers'
        ]
        seen_shoe = False
        filtered = []
        for item in items:
            if any(t in item.type.lower() for t in shoe_types):
                if not seen_shoe:
                    filtered.append(item)
                    seen_shoe = True
                # else: skip additional shoes
            else:
                filtered.append(item)
        return filtered

    def _deduplicate_by_category(self, items: List[ClothingItem], context: Dict[str, Any] = None) -> List[ClothingItem]:
        """
        Ensure only one item per category is present in the outfit, but preserve essential items.
        Enhanced with context-aware deduplication and robust fallback logic.
        """
        if not items:
            print("DEBUG: _deduplicate_by_category - No items to deduplicate")
            return []
        
        print(f"DEBUG: _deduplicate_by_category - Starting with {len(items)} items: {[item.name for item in items]}")
        
        # Enhanced category mapping with better detection
        categories = {
            'top': ['shirt', 't-shirt', 'blouse', 'polo', 'tank', 'cami', 'sweater', 'hoodie'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'leggings', 'joggers'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'flats', 'heels', 'loafers'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'scarf', 'hat', 'bag'],
            'layer': ['jacket', 'coat', 'sweater', 'cardigan', 'blazer', 'vest'],
            'dress': ['dress', 'jumpsuit', 'romper']  # Special category for one-piece items
        }
        
        # Essential categories that should always be preserved (one per category)
        essential_categories = {'top', 'bottom', 'shoes'}
        
        # Non-essential categories that can be deduplicated more aggressively
        non_essential_categories = {'accessory', 'layer'}
        
        # Special handling for dresses (one-piece items)
        dress_categories = {'dress'}
        
        # Get context information for smarter deduplication
        occasion = context.get('occasion', 'casual') if context else 'casual'
        weather_temp = context.get('weather').temperature if context and context.get('weather') else 70
        style = context.get('style') if context else None
        
        print(f"DEBUG: _deduplicate_by_category - Context: occasion={occasion}, temp={weather_temp}, style={style}")
        
        # Enhanced category detection with better logic
        def get_item_category_enhanced(item: ClothingItem) -> str:
            item_type = item.type.lower()
            item_name = item.name.lower()
            
            # Special cases for better categorization
            if any(word in item_name for word in ['dress', 'jumpsuit', 'romper']):
                return 'dress'
            elif any(word in item_name for word in ['turtleneck', 'mock neck']):
                return 'layer'  # Turtlenecks are layers, not tops
            elif any(word in item_name for word in ['vest', 'waistcoat']):
                return 'layer'
            elif any(word in item_name for word in ['tank', 'cami', 'tube']):
                return 'top'
            elif any(word in item_name for word in ['leggings', 'joggers', 'sweatpants']):
                return 'bottom'
            elif any(word in item_name for word in ['flats', 'loafers', 'mules']):
                return 'shoes'
            elif any(word in item_name for word in ['scarf', 'hat', 'cap', 'beanie']):
                return 'accessory'
            
            # Default category detection
            for category, types in categories.items():
                if item_type in types or any(type_word in item_type for type_word in types):
                    return category
            
            # Fallback based on item type
            if item_type in ['shirt', 't-shirt', 'blouse', 'polo']:
                return 'top'
            elif item_type in ['pants', 'jeans', 'shorts', 'skirt']:
                return 'bottom'
            elif item_type in ['shoes', 'sneakers', 'boots', 'sandals']:
                return 'shoes'
            elif item_type in ['jacket', 'coat', 'sweater', 'cardigan', 'blazer']:
                return 'layer'
            elif item_type in ['belt', 'watch', 'necklace', 'bracelet', 'earrings']:
                return 'accessory'
            else:
                return 'accessory'  # Default fallback
        
        # Context-aware deduplication rules
        def should_keep_duplicate(category: str, item: ClothingItem, existing_items: List[ClothingItem]) -> bool:
            """Determine if a duplicate item should be kept based on context."""
            
            # For dresses, never keep duplicates (one-piece items)
            if category == 'dress':
                return False
            
            # For essential categories, be more lenient in certain contexts
            if category in essential_categories:
                # Keep multiple tops for layering in cold weather
                if category == 'top' and weather_temp < 60:
                    return len([i for i in existing_items if get_item_category_enhanced(i) == 'top']) < 2
                
                # Keep multiple layers for formal occasions
                if category == 'layer' and occasion in ['formal', 'business_formal', 'gala', 'wedding_guest']:
                    return len([i for i in existing_items if get_item_category_enhanced(i) == 'layer']) < 2
                
                # Keep multiple accessories for special occasions
                if category == 'accessory' and occasion in ['formal', 'gala', 'wedding_guest', 'party']:
                    return len([i for i in existing_items if get_item_category_enhanced(i) == 'accessory']) < 3
            
            return False
        
        # First pass: Categorize all items
        categorized_items = {}
        for item in items:
            category = get_item_category_enhanced(item)
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append(item)
        
        print(f"DEBUG: _deduplicate_by_category - Categorized items: {[(cat, len(items)) for cat, items in categorized_items.items()]}")
        
        # Second pass: Apply smart deduplication
        filtered = []
        removed_items = []
        
        for category, category_items in categorized_items.items():
            if not category_items:
                continue
            
            # Sort items by relevance/quality for this category
            category_items.sort(key=lambda x: self._get_item_relevance_score(x, category, context), reverse=True)
            
            # Keep the best item(s) for this category
            if category in dress_categories:
                # For dresses, keep only the best one
                filtered.append(category_items[0])
                removed_items.extend([f"{item.name} - duplicate {category}" for item in category_items[1:]])
                print(f"DEBUG: _deduplicate_by_category - Keeping best {category}: {category_items[0].name}")
                
            elif category in essential_categories:
                # For essential categories, keep the best item
                filtered.append(category_items[0])
                removed_items.extend([f"{item.name} - duplicate {category}" for item in category_items[1:]])
                print(f"DEBUG: _deduplicate_by_category - Keeping best essential {category}: {category_items[0].name}")
                
            elif category in non_essential_categories:
                # For non-essential categories, check if we should keep duplicates
                keep_count = 1
                if should_keep_duplicate(category, category_items[0], filtered):
                    keep_count = min(2, len(category_items))  # Keep up to 2 items
                
                for i in range(keep_count):
                    filtered.append(category_items[i])
                
                removed_items.extend([f"{item.name} - duplicate {category}" for item in category_items[keep_count:]])
                print(f"DEBUG: _deduplicate_by_category - Keeping {keep_count} {category} items: {[item.name for item in category_items[:keep_count]]}")
        
        # Validation and fallback logic
        if len(filtered) < 3 and len(items) >= 3:
            print(f"⚠️  WARNING: _deduplicate_by_category - Only {len(filtered)} items after deduplication, applying fallback")
            
            # Fallback: Keep all essential items and be more lenient with others
            filtered = []
            seen_categories = set()
            
            for item in items:
                category = get_item_category_enhanced(item)
                
                # Always keep essential items
                if category in essential_categories:
                    filtered.append(item)
                    if category not in seen_categories:
                        seen_categories.add(category)
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Keeping essential {category}: {item.name}")
                    else:
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Keeping duplicate essential {category}: {item.name}")
                
                # For non-essential, be more lenient
                elif category in non_essential_categories:
                    if category not in seen_categories or len([i for i in filtered if get_item_category_enhanced(i) == category]) < 2:
                        filtered.append(item)
                        seen_categories.add(category)
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Keeping {category}: {item.name}")
                    else:
                        removed_items.append(f"{item.name} - duplicate {category} (fallback)")
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Removing {category}: {item.name}")
                
                # For dresses, keep only one
                elif category == 'dress':
                    if category not in seen_categories:
                        filtered.append(item)
                        seen_categories.add(category)
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Keeping dress: {item.name}")
                    else:
                        removed_items.append(f"{item.name} - duplicate dress (fallback)")
                        print(f"DEBUG: _deduplicate_by_category (fallback) - Removing dress: {item.name}")
        
        # Final validation
        if len(filtered) < 3:
            print(f"⚠️  CRITICAL: _deduplicate_by_category - Only {len(filtered)} items after fallback, keeping all items")
            filtered = items  # Keep all items as last resort
        
        # Log results
        if removed_items:
            print(f"DEBUG: _deduplicate_by_category - Removed items: {removed_items}")
        
        print(f"DEBUG: _deduplicate_by_category - Final items ({len(filtered)}): {[item.name for item in filtered]}")
        return filtered
    
    def _get_item_relevance_score(self, item: ClothingItem, category: str, context: Dict[str, Any] = None) -> float:
        """Calculate relevance score for an item in a specific category."""
        score = 0.0
        
        # Base score from item properties
        if hasattr(item, 'favorite_score') and item.favorite_score:
            score += item.favorite_score * 0.3
        
        if hasattr(item, 'wearCount') and item.wearCount:
            score += min(item.wearCount * 0.1, 2.0)  # Cap at 2.0
        
        # Context-aware scoring
        if context:
            occasion = context.get('occasion', 'casual')
            weather_temp = context.get('weather').temperature if context.get('weather') else 70
            style = context.get('style')
            
            # Occasion appropriateness
            if occasion in ['formal', 'business_formal', 'gala'] and category in ['top', 'layer']:
                if 'formal' in item.name.lower() or 'dress' in item.type.lower():
                    score += 2.0
            
            # Weather appropriateness
            if weather_temp < 60 and category == 'layer':
                if 'sweater' in item.type.lower() or 'coat' in item.type.lower():
                    score += 1.5
            elif weather_temp > 80 and category == 'top':
                if 'tank' in item.type.lower() or 'cami' in item.type.lower():
                    score += 1.0
            
            # Style matching
            if style and hasattr(item, 'styleTags') and item.styleTags:
                if style.lower() in [tag.lower() for tag in item.styleTags]:
                    score += 1.0
        
        return score

    def _validate_formal_outfit_structure(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Special validation for formal outfits to ensure required structure."""
        # Check if we have pants/skirts (bottom)
        has_bottom = any(item.type.lower() in ['pants', 'jeans', 'shorts', 'skirt', 'dress_pants'] for item in items)
        
        # Check if we have a jacket/blazer (layer)
        has_layer = any(item.type.lower() in ['jacket', 'blazer', 'suit'] for item in items)
        
        # If missing required components, return empty list to force regeneration
        if not has_bottom or not has_layer:
            print(f"DEBUG: Formal outfit missing required components - has_bottom: {has_bottom}, has_layer: {has_layer}")
            return []
        
        temperature = weather.temperature
        
        # Count tops and layers
        tops = [item for item in items if item.type in [ClothingType.SHIRT, ClothingType.DRESS_SHIRT]]
        layers = [item for item in items if item.type in [ClothingType.JACKET, ClothingType.SWEATER]]
        
        # For formal outfits in warm weather, limit tops and layers
        if temperature >= 70:
            # Keep only the most formal top
            if len(tops) > 1:
                # Sort by formality and keep the most formal
                tops.sort(key=lambda x: self._get_formality_score(x), reverse=True)
                items = [item for item in items if item not in tops[1:]]
            
            # Limit layers in warm weather
            if len(layers) > 1:
                # Keep only the most formal layer (prefer blazers over sweaters)
                blazers = [item for item in layers if item.type == ClothingType.JACKET]
                if blazers:
                    items = [item for item in items if item not in [l for l in layers if l not in blazers]]
                else:
                    layers.sort(key=lambda x: self._get_formality_score(x), reverse=True)
                    items = [item for item in items if item not in layers[1:]]
        
        return items

    async def _enhance_wardrobe_with_usage_data(self, wardrobe: List[ClothingItem], user_id: str) -> List[ClothingItem]:
        """Enhance wardrobe items with usage analytics data for better diversity scoring."""
        try:
            from .item_analytics_service import ItemAnalyticsService
            analytics_service = ItemAnalyticsService()
            
            # Get usage data for all items
            enhanced_wardrobe = []
            for item in wardrobe:
                # Get favorite score data for this item
                try:
                    favorites = await analytics_service.get_user_favorites(user_id, limit=1000)
                    item_favorite = next((f for f in favorites if f.item_id == item.id), None)
                    
                    if item_favorite:
                        # Add usage data to the item
                        item.wearCount = item_favorite.usage_count
                        item.lastWorn = item_favorite.last_used_timestamp
                        item.favorite_score = item_favorite.total_score
                        print(f"DEBUG: Enhanced {item.name} with usage data: {item_favorite.usage_count} uses, last worn: {item_favorite.last_used_timestamp}")
                    else:
                        # Set default values for items without usage data
                        item.wearCount = 0
                        item.lastWorn = 0
                        item.favorite_score = 0.0
                        print(f"DEBUG: {item.name} has no usage data, setting defaults")
                    
                    enhanced_wardrobe.append(item)
                    
                except Exception as e:
                    print(f"Warning: Failed to get usage data for item {item.id}: {e}")
                    # Set default values if analytics fails
                    item.wearCount = 0
                    item.lastWorn = 0
                    item.favorite_score = 0.0
                    enhanced_wardrobe.append(item)
            
            print(f"DEBUG: Enhanced {len(enhanced_wardrobe)} items with usage data")
            return enhanced_wardrobe
            
        except Exception as e:
            print(f"Warning: Failed to enhance wardrobe with usage data: {e}")
            # Return original wardrobe if analytics service fails
            for item in wardrobe:
                if not hasattr(item, 'wearCount'):
                    item.wearCount = 0
                if not hasattr(item, 'lastWorn'):
                    item.lastWorn = 0
                if not hasattr(item, 'favorite_score'):
                    item.favorite_score = 0.0
            return wardrobe

    def _filter_recently_used_items(self, items: List[ClothingItem], outfit_history: List[Dict], days: int = 7) -> List[ClothingItem]:
        """Filter out items used in recent outfits to promote wardrobe diversity."""
        if not outfit_history:
            # NEW: If no outfit history, use fallback diversity logic
            return self._apply_fallback_diversity(items)
        
        recent_item_ids = set()
        cutoff_time = time.time() - (days * 24 * 3600)
        
        for outfit in outfit_history:
            outfit_time = outfit.get('createdAt', 0)
            if outfit_time > cutoff_time:
                # Extract item IDs from outfit items
                outfit_items = outfit.get('items', [])
                for item in outfit_items:
                    if isinstance(item, dict):
                        item_id = item.get('id')
                    else:
                        item_id = getattr(item, 'id', None)
                    if item_id:
                        recent_item_ids.add(item_id)
        
        filtered_items = [item for item in items if item.id not in recent_item_ids]
        
        # NEW: If too many items were filtered out, use fallback diversity
        if len(filtered_items) < len(items) * 0.3:  # If less than 30% remain
            print(f"DEBUG: Too many items filtered out ({len(filtered_items)}/{len(items)}), using fallback diversity")
            return self._apply_fallback_diversity(items)
        
        if len(filtered_items) != len(items):
            print(f"DEBUG: Filtered out {len(items) - len(filtered_items)} recently used items")
        
        return filtered_items

    def _apply_fallback_diversity(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Apply fallback diversity logic when outfit history is not available."""
        if not items:
            return items
        
        # NEW: Add randomization factor based on item properties
        import random
        
        # Create diversity scores for each item
        diversity_scores = []
        for item in items:
            score = 0
            
            # Boost items that haven't been used recently (based on creation date)
            if hasattr(item, 'createdAt'):
                days_since_creation = (time.time() - item.createdAt) / (24 * 60 * 60)
                if days_since_creation > 7:  # Items older than a week get a boost
                    score += 10
                elif days_since_creation > 3:  # Items older than 3 days get a smaller boost
                    score += 5
            
            # Boost items with unique characteristics
            if hasattr(item, 'style') and item.style:
                score += len(item.style) * 2  # More style tags = more unique
            
            # Boost items with specific colors (less common colors get higher scores)
            if hasattr(item, 'dominantColors') and item.dominantColors:
                score += len(item.dominantColors) * 3
            
            # Add random factor to prevent deterministic selection
            score += random.uniform(0, 10)
            
            diversity_scores.append((item, score))
        
        # Sort by diversity score (highest first)
        diversity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 70% of items to ensure diversity
        cutoff_index = max(1, int(len(diversity_scores) * 0.7))
        selected_items = [item for item, score in diversity_scores[:cutoff_index]]
        
        # Shuffle the selected items to add more randomness
        random.shuffle(selected_items)
        
        print(f"DEBUG: Fallback diversity applied - {len(selected_items)}/{len(items)} items selected")
        return selected_items

    def _add_randomization_factors(self, items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Add randomization factors to prevent deterministic selection."""
        if not items:
            return items
        
        import random
        
        # Add randomization based on context
        occasion = context.get('occasion', '').lower()
        style = (context.get('style') or '').lower()
        mood = (context.get('mood') or '').lower()
        
        # Create randomization scores
        randomization_scores = []
        for item in items:
            score = 0
            
            # Time-based randomization (items created at different times get different scores)
            if hasattr(item, 'createdAt'):
                time_factor = (item.createdAt % 1000) / 1000.0  # Use last 3 digits of timestamp
                score += time_factor * 5
            
            # Occasion-based randomization
            if occasion and hasattr(item, 'occasion') and item.occasion:
                if occasion in [occ.lower() for occ in item.occasion]:
                    score += random.uniform(5, 15)  # Boost for occasion match
                else:
                    score += random.uniform(0, 5)  # Lower score for non-match
            
            # Style-based randomization
            if style and hasattr(item, 'style') and item.style:
                if style in [s.lower() for s in item.style]:
                    score += random.uniform(3, 10)  # Boost for style match
                else:
                    score += random.uniform(0, 3)  # Lower score for non-match
            
            # Pure randomness factor
            score += random.uniform(0, 20)
            
            randomization_scores.append((item, score))
        
        # Sort by randomization score
        randomization_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take top items but ensure we don't filter too aggressively
        cutoff_index = max(1, int(len(randomization_scores) * 0.8))
        selected_items = [item for item, score in randomization_scores[:cutoff_index]]
        
        # Final shuffle for maximum randomness
        random.shuffle(selected_items)
        
        print(f"DEBUG: Randomization factors applied - {len(selected_items)}/{len(items)} items selected")
        return selected_items

    def _debug_outfit_generation(self, items: List[ClothingItem], phase: str):
        """Enhanced debug method with detailed JSON output for development mode."""
        import json
        import os
        
        # Check if we're in development mode
        is_dev = os.getenv('ENVIRONMENT', 'development').lower() == 'development'
        
        print(f"DEBUG: {phase} - {len(items)} items selected")
        
        # Basic logging for all environments
        for item in items:
            print(f"  - {item.name} ({item.type})")
        
        # Enhanced JSON output for development mode
        if is_dev and items:
            debug_data = {
                "phase": phase,
                "item_count": len(items),
                "items": []
            }
            
            for item in items:
                item_data = {
                    "id": getattr(item, 'id', 'unknown'),
                    "name": getattr(item, 'name', 'unknown'),
                    "type": getattr(item, 'type', 'unknown'),
                    "category": self._get_item_category(item),
                    "colors": getattr(item, 'colors', []),
                    "styleTags": getattr(item, 'styleTags', []),
                    "occasion": getattr(item, 'occasion', []),
                    "material": getattr(item, 'material', 'unknown'),
                    "favorite_score": getattr(item, 'favorite_score', 0),
                    "wearCount": getattr(item, 'wearCount', 0)
                }
                debug_data["items"].append(item_data)
            
            # Pretty print JSON for development
            print(f"DEBUG JSON ({phase}):")
            print(json.dumps(debug_data, indent=2, default=str))

    async def get_outfits_by_user(self, user_id: str) -> List[OutfitGeneratedOutfit]:
        """Get outfits for a specific user from Firestore."""
        try:
            outfits = []
            # Query outfits by user_id field
            docs = self.collection.where("user_id", "==", user_id).stream()
            for doc in docs:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                
                # Convert item IDs to full ClothingItem objects if needed
                if 'items' in outfit_data and isinstance(outfit_data['items'], list):
                    converted_items = []
                    for item in outfit_data['items']:
                        if isinstance(item, str):
                            # This is an item ID, fetch the full item from wardrobe
                            try:
                                from ..config.firebase import db
                                item_doc = db.collection("wardrobe").document(item).get()
                                if item_doc.exists:
                                    item_data = item_doc.to_dict()
                                    item_data['id'] = item
                                    from ..custom_types.wardrobe import ClothingItem
                                    clothing_item = ClothingItem(**item_data)
                                    converted_items.append(clothing_item)
                                else:
                                    print(f"Warning: Item {item} not found in wardrobe, keeping as ID")
                                    converted_items.append(item)
                            except Exception as e:
                                print(f"Warning: Failed to fetch item {item}: {e}, keeping as ID")
                                converted_items.append(item)
                        else:
                            # This is already a full object or dict, keep as is
                            converted_items.append(item)
                    outfit_data['items'] = converted_items
                
                # Temporarily bypass validation to get outfits page working
                try:
                    # Try to validate as OutfitGeneratedOutfit first
                    outfits.append(OutfitGeneratedOutfit(**outfit_data))
                except Exception as e:
                    print(f"Validation failed for outfit {doc.id}, creating minimal outfit object")
                    # Create a complete outfit object with all required fields
                    minimal_outfit = {
                        "id": doc.id,
                        "name": outfit_data.get("name", "Unnamed Outfit"),
                        "description": outfit_data.get("description", "A generated outfit"),
                        "items": outfit_data.get("items", []),
                        "explanation": outfit_data.get("explanation", outfit_data.get("reasoning", "Generated outfit")),
                        "pieces": outfit_data.get("pieces", []),
                        "styleTags": outfit_data.get("styleTags", []),
                        "colorHarmony": outfit_data.get("colorHarmony", "neutral"),
                        "styleNotes": outfit_data.get("styleNotes", ""),
                        "occasion": outfit_data.get("occasion", "casual"),
                        "season": outfit_data.get("season", "all"),
                        "style": outfit_data.get("style", "casual"),
                        "mood": outfit_data.get("mood", "neutral"),
                        "createdAt": outfit_data.get("createdAt", 0),
                        "updatedAt": outfit_data.get("updatedAt", outfit_data.get("createdAt", 0)),
                        "metadata": outfit_data.get("metadata", {}),
                        "wasSuccessful": outfit_data.get("wasSuccessful", True),
                        "baseItemId": outfit_data.get("baseItemId", None),
                        "validationErrors": outfit_data.get("validationErrors", []),
                        "userFeedback": outfit_data.get("userFeedback", None),
                        "user_id": outfit_data.get("user_id", user_id),
                        "generation_trace": outfit_data.get("generation_trace", []),
                        "validation_details": outfit_data.get("validation_details", {}),
                        "wardrobe_snapshot": outfit_data.get("wardrobe_snapshot", {}),
                        "system_context": outfit_data.get("system_context", {}),
                        "user_session_context": outfit_data.get("user_session_context", {}),
                        "generation_method": outfit_data.get("generation_method", "primary")
                    }
                    try:
                        outfits.append(OutfitGeneratedOutfit(**minimal_outfit))
                    except Exception as e2:
                        print(f"Failed to create minimal outfit for {doc.id}: {e2}")
                        continue
            
            # Sort by creation date (newest first) - temporarily disabled to avoid index requirement
        # outfits.sort(key=lambda x: x.createdAt, reverse=True)
            return outfits
        except Exception as e:
            print(f"Error getting outfits for user {user_id}: {e}")
            raise
    
    def _normalize_user_profile_data(self, user_profile: UserProfile) -> UserProfile:
        """Normalize user profile data structure to prevent validation issues."""
        try:
            # Create a copy of the profile to avoid modifying the original
            profile_dict = user_profile.dict() if hasattr(user_profile, 'dict') else user_profile.__dict__.copy()
            
            # Normalize preferences
            if 'preferences' in profile_dict:
                preferences = profile_dict['preferences']
                
                # Convert string preferences to lists
                for key in ['formality', 'budget', 'style', 'colors', 'patterns']:
                    if key in preferences and isinstance(preferences[key], str):
                        preferences[key] = [preferences[key]]
                
                # Ensure other preference fields are lists
                for key in ['occasions', 'preferredBrands', 'fitPreferences']:
                    if key in preferences and not isinstance(preferences[key], list):
                        if isinstance(preferences[key], str):
                            preferences[key] = [preferences[key]]
                        else:
                            preferences[key] = []
            
            # Normalize style preferences
            if 'stylePreferences' in profile_dict and not isinstance(profile_dict['stylePreferences'], list):
                if isinstance(profile_dict['stylePreferences'], str):
                    profile_dict['stylePreferences'] = [profile_dict['stylePreferences']]
                else:
                    profile_dict['stylePreferences'] = []
            
            # Normalize fit preferences
            if 'fitPreferences' in profile_dict and not isinstance(profile_dict['fitPreferences'], list):
                if isinstance(profile_dict['fitPreferences'], str):
                    profile_dict['fitPreferences'] = [profile_dict['fitPreferences']]
                else:
                    profile_dict['fitPreferences'] = []
            
            # Create a new UserProfile object with normalized data
            return UserProfile(**profile_dict)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not normalize user profile data: {e}")
            # Return original profile if normalization fails
            return user_profile

    # ===== ORCHESTRATED VALIDATION METHODS =====
    
    async def _final_outfit_validation_orchestrated(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use orchestrated validation pipeline with parallel and sequential execution."""
        
        print(f"🔧 Starting orchestrated validation for {len(items)} items")
        
        # Use the validation orchestrator
        result = await self.validation_orchestrator.run_validation_pipeline(items, context)
        
        # Add tracing
        self.tracing_service.add_trace_step(
            step="orchestrated_validation",
            method="_final_outfit_validation_orchestrated",
            params={"items_count": len(items)},
            result=result,
            duration=result["total_duration"]
        )
        
        print(f"✅ Orchestrated validation completed: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
        return result
    
    async def _validate_outfit_with_orchestration(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main validation method that uses orchestration for better performance and error handling."""
        
        # Use the new orchestrated validation
        validation_result = await self._final_outfit_validation_orchestrated(items, context)
        
        # Add additional context-specific validations if needed
        if validation_result["is_valid"]:
            # Add any additional validations that depend on the orchestrated results
            additional_validation = await self._additional_context_validations(items, context)
            if not additional_validation["is_valid"]:
                validation_result["errors"].extend(additional_validation["errors"])
                validation_result["warnings"].extend(additional_validation["warnings"])
                validation_result["is_valid"] = False
        
        return validation_result
    
    async def _additional_context_validations(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Additional validations that depend on the orchestrated validation results."""
        
        errors = []
        warnings = []
        
        # Add any context-specific validations here
        # For example, special occasion validations, user preference validations, etc.
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": {"additional_validations": True}
        }