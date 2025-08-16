"""
Outfit Core Service
Main outfit service with database operations and core methods.
"""

from typing import List, Optional, Dict, Any, Union
import time
import uuid
from ..config.firebase import db
from ..custom_types.outfit import Outfit, OutfitPiece, OutfitGeneratedOutfit, OutfitGenerationRequest
from ..custom_types.wardrobe import ClothingType, ClothingItem, Season, StyleTag, Color
from ..custom_types.outfit_rules import get_weather_rule, get_occasion_rule, LayeringRule, ClothingType as RuleClothingType, get_mood_rule
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from ..custom_types.style_engine import Material
import random
from ..utils.pairability import average_pairability
from ..utils.outfit_utils import get_color_name, athletic_sort_key, check_body_type_compatibility, check_skin_tone_compatibility, extract_color_names, get_item_category
from .outfit_fallback_service import OutfitFallbackService
from .pipeline_tracing_service import PipelineTracingService
from .analytics_service import log_outfit_generation
from .validation_orchestrator import ValidationOrchestrator

class OutfitCoreService:
    def __init__(self):
        self.db = db
        self.collection = self.db.collection("outfits")
        self.wardrobe_collection = self.db.collection("wardrobe")
        self.fallback_service = OutfitFallbackService()
        self.tracing_service = PipelineTracingService()
        self.validation_orchestrator = ValidationOrchestrator(self)
        
    def _safe_temperature_convert(self, temperature) -> float:
        """Safely convert temperature to float to prevent string vs float comparison errors."""
        if isinstance(temperature, str):
            try:
                return float(temperature)
            except (ValueError, TypeError):
                return 70.0
        elif temperature is None:
            return 70.0
        else:
            return float(temperature)
            
    async def save_outfit(self, outfit: OutfitGeneratedOutfit) -> bool:
        """Save an outfit to Firestore."""
        try:
            # Convert outfit to dict for storage
            outfit_dict = outfit.dict()
            
            # Save to Firestore
            self.collection.document(outfit.id).set(outfit_dict)
            
            print(f"✅ Saved outfit {outfit.id} to database")
            return True
        except Exception as e:
            print(f"❌ Error saving outfit {outfit.id}: {e}")
            return False

    async def get_outfits(self) -> List[OutfitGeneratedOutfit]:
        """Get all outfits from Firestore."""
        try:
            docs = self.collection.stream()
            outfits = []
            
            for doc in docs:
                try:
                    outfit_data = doc.to_dict()
                    outfit_data['id'] = doc.id
                    
                    # Try to validate as OutfitGeneratedOutfit
                    outfit = OutfitGeneratedOutfit(**outfit_data)
                    outfits.append(outfit)
                except Exception as e:
                    print(f"Warning: Failed to load outfit {doc.id}: {e}")
                    # Try to convert from old format
                    try:
                        converted_data = self._convert_old_outfit_format(outfit_data)
                        outfit = OutfitGeneratedOutfit(**converted_data)
                        outfits.append(outfit)
                    except Exception as e2:
                        print(f"Failed to convert outfit {doc.id}: {e2}")
                        # Delete problematic outfit
                        self.collection.document(doc.id).delete()
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
            
            # Handle items and pieces fields - convert to proper format
            if 'items' in outfit_data and isinstance(outfit_data['items'], list):
                print(f"DEBUG: get_outfit - Processing items field with {len(outfit_data['items'])} items")
                print(f"DEBUG: get_outfit - Items field contains: {outfit_data['items']}")
                
                # Convert items to proper format (keep as IDs for Pydantic validation)
                converted_items = []
                for item in outfit_data['items']:
                    if isinstance(item, str):
                        # This is an item ID, keep as is
                        converted_items.append(item)
                    elif isinstance(item, dict):
                        # This is a full object, extract the ID
                        item_id = item.get('id') or item.get('itemId')
                        if item_id:
                            converted_items.append(item_id)
                        else:
                            # No ID found, generate a new one
                            new_id = str(uuid.uuid4())
                            print(f"Warning: No ID found in item dict, generating new ID: {new_id}")
                            converted_items.append(new_id)
                    else:
                        # Unknown type, keep as is
                        converted_items.append(item)
                outfit_data['items'] = converted_items
                print(f"DEBUG: get_outfit - Converted items to IDs: {converted_items}")
                
                # Keep pieces field as is (frontend expects OutfitPiece format)
                if 'pieces' in outfit_data and isinstance(outfit_data['pieces'], list):
                    print(f"DEBUG: get_outfit - Keeping pieces field as is with {len(outfit_data['pieces'])} pieces")
                    print(f"DEBUG: get_outfit - First piece structure: {outfit_data['pieces'][0] if outfit_data['pieces'] else 'No pieces'}")
                    print(f"DEBUG: get_outfit - All pieces: {outfit_data['pieces']}")
                    # Don't modify pieces - frontend expects OutfitPiece format
                else:
                    print(f"DEBUG: get_outfit - No pieces field found")
            
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
        
    async def generate_outfit(self, occasion: str, weather: WeatherData, wardrobe: List[ClothingItem], 
                            user_profile: UserProfile, likedOutfits: List[str], trendingStyles: List[str],
                            preferences: Optional[Dict[str, Any]] = None, outfitHistory: Optional[List[Dict[str, Any]]] = None,
                            randomSeed: Optional[float] = None, season: Optional[str] = None, style: Optional[str] = None,
                            baseItem: Optional[ClothingItem] = None, mood: Optional[str] = None) -> OutfitGeneratedOutfit:
        """Main outfit generation method - orchestrates other services."""
        # Implementation will be moved from main service
        pass
