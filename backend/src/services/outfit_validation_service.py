"""
Outfit Validation Service
Handles all validation logic for outfit generation including temperature comparison fixes.
"""

from typing import List, Dict, Any, Optional, Tuple
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
from ..custom_types.weather import WeatherData
from ..services.validation_orchestrator import ValidationResult


class OutfitValidationService:
    """Handles all validation operations for outfit generation."""
    
    def __init__(self):
        # Define inappropriate combinations
        self.inappropriate_combinations = {
            "blazer_shorts": {
                "description": "Blazer + Shorts",
                "reason": "Blazers are formal wear and should not be paired with casual shorts",
                "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
                "keep_items": ["blazer", "suit jacket", "sport coat"]
            },
            "formal_jacket_casual_shorts": {
                "description": "Formal Jacket + Casual Shorts", 
                "reason": "Formal jackets require more formal bottoms",
                "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
                "keep_items": ["blazer", "suit jacket", "sport coat", "coat"]
            },
            "business_athletic": {
                "description": "Business Wear + Athletic Wear",
                "reason": "Business items should not be mixed with athletic wear",
                "remove_items": ["athletic shorts", "basketball shorts", "sweatpants", "athletic pants"],
                "keep_items": ["blazer", "suit", "dress shirt", "dress pants"]
            },
            "formal_shoes_casual_shorts": {
                "description": "Formal Shoes + Casual Shorts",
                "reason": "Formal shoes require more formal bottoms",
                "remove_items": ["shorts", "athletic shorts"],
                "keep_items": ["oxford", "loafers", "dress shoes", "heels"]
            },
            "formal_wear_casual_shoes": {
                "description": "Formal Wear + Casual Shoes",
                "reason": "Flip-flops/slides should not be worn with blazers or suits",
                "remove_items": ["flip-flops", "flip flops", "slides", "sandals", "thongs"],
                "keep_items": ["blazer", "suit", "suit jacket", "sport coat", "jacket"]
            },
            "blazer_flip_flops": {
                "description": "Blazer + Flip Flops",
                "reason": "Blazers are formal wear and should not be paired with flip flops",
                "remove_items": ["flip-flops", "flip flops", "slides", "thongs"],
                "keep_items": ["blazer", "suit jacket", "sport coat"]
            },
            "formal_shoes_shorts": {
                "description": "Formal Shoes + Shorts",
                "reason": "Formal shoes should not be worn with shorts",
                "remove_items": ["shorts", "athletic shorts", "basketball shorts"],
                "keep_items": ["oxford", "loafers", "dress shoes", "heels", "pumps"]
            },
            "blazer_cargos": {
                "description": "Blazer + Cargo Pants",
                "reason": "Cargo pants are casual/athletic wear and should not be paired with formal blazers",
                "remove_items": ["cargo pants", "cargos", "cargo shorts", "cargo"],
                "keep_items": ["blazer", "suit jacket", "sport coat", "jacket"]
            },
            "formal_casual_bottoms": {
                "description": "Formal Wear + Casual Bottoms",
                "reason": "Formal jackets require more formal bottoms than cargo pants",
                "remove_items": ["cargo pants", "cargos", "cargo shorts", "cargo", "joggers", "sweatpants"],
                "keep_items": ["blazer", "suit jacket", "sport coat", "jacket", "suit"]
            }
        }
    
    async def validate_outfit_with_orchestration(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate outfit using the validation orchestrator and enforce inappropriate combinations."""
        from .validation_orchestrator import ValidationOrchestrator
        
        # First, enforce inappropriate combinations by removing problematic items
        filtered_items, combination_errors = self._enforce_inappropriate_combinations(items)
        
        # Create a mock outfit service for validation
        class MockOutfitService:
            def get_item_category_enhanced(self, item):
                return item.type.value if hasattr(item.type, 'value') else str(item.type)
            
            def _get_layering_rule(self, temperature):
                return {"temperature": temperature, "layers": 1}
            
            def _get_occasion_rule(self, occasion):
                return {"occasion": occasion}
            
            def _get_mood_rule(self, mood):
                return {"mood": mood}
            
            def _validate_layering_compliance(self, *args, **kwargs):
                return {
                    "is_valid": True,
                    "is_compliant": True,
                    "errors": [],
                    "warnings": []
                }
        
        orchestrator = ValidationOrchestrator(MockOutfitService())
        result = await orchestrator.run_validation_pipeline(filtered_items, context)
        
        # Combine inappropriate combination errors with validation errors
        all_errors = combination_errors + result["errors"]
        
        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": result["warnings"],
            "details": result.get("details", {}),
            "filtered_items": filtered_items
        }
    
    def _enforce_inappropriate_combinations(self, items: List[ClothingItem]) -> Tuple[List[ClothingItem], List[str]]:
        """Enforce inappropriate combinations by removing problematic items."""
        if not items:
            return items, []
        
        filtered_items = items.copy()
        errors = []
        
        # Check each inappropriate combination rule
        for rule_name, rule in self.inappropriate_combinations.items():
            keep_items = rule.get("keep_items", [])
            remove_items = rule.get("remove_items", [])
            
            # Find items that should be kept (formal items)
            has_formal_items = False
            for item in filtered_items:
                item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
                item_name = item.name.lower()
                
                # Check if this item should be kept
                should_keep = any(keep_type in item_type or keep_type in item_name for keep_type in keep_items)
                if should_keep:
                    has_formal_items = True
                    break
            
            # If we have formal items that should be kept, remove casual items
            if has_formal_items:
                items_to_remove = []
                for item in filtered_items:
                    item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
                    item_name = item.name.lower()
                    
                    # Check if this item should be removed
                    should_remove = any(remove_type in item_type or remove_type in item_name for remove_type in remove_items)
                    
                    # Additional checks for cargo pants variations
                    if not should_remove and "cargo" in remove_items:
                        cargo_variations = ["cargo", "cargos", "cargo pants", "cargo shorts", "cargo trousers"]
                        should_remove = any(cargo_var in item_name for cargo_var in cargo_variations)
                    
                    if should_remove:
                        items_to_remove.append(item)
                        errors.append(f"Removed {item.name} - {rule['reason']}")
                
                # Remove the inappropriate items
                for item in items_to_remove:
                    if item in filtered_items:
                        filtered_items.remove(item)
        
        return filtered_items, errors
    
    def validate_layering_compatibility(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Validate layering compatibility with temperature conversion."""
        if not items:
            return {"is_valid": True, "errors": [], "warnings": []}
        
        errors = []
        warnings = []
        
        # Get layering items
        layering_items = [item for item in items if self._is_layering_item(item)]
        
        if len(layering_items) > 2:
            warnings.append("Multiple layering items may be too warm")
        
        # Check for incompatible layering combinations
        for i, item1 in enumerate(layering_items):
            for item2 in layering_items[i+1:]:
                if not self._are_layering_items_compatible(item1, item2):
                    errors.append(f"Incompatible layering: {item1.name} and {item2.name}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_layering_item(self, item: ClothingItem) -> bool:
        """Check if item is a layering item."""
        layering_types = ['shirt', 'sweater', 'jacket', 'coat', 'blazer', 'cardigan']
        return any(layer_type in item.type.lower() for layer_type in layering_types)
    
    def _are_layering_items_compatible(self, item1: ClothingItem, item2: ClothingItem) -> bool:
        """Check if two layering items are compatible."""
        # Add layering compatibility logic here
        return True
    
    def validate_weather_appropriateness(
        self, 
        items: List[ClothingItem], 
        weather: WeatherData
    ) -> Dict[str, Any]:
        """Validate weather appropriateness with temperature conversion."""
        if not items:
            return {"is_valid": True, "errors": [], "warnings": []}
        
        # Ensure temperature is a float
        temperature = weather.temperature
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        errors = []
        warnings = []
        
        for item in items:
            if not self._is_weather_appropriate(item, temperature):
                if temperature >= 80:  # Hot weather
                    errors.append(f"{item.name} may be too warm for {temperature}°F weather")
                elif temperature < 50:  # Cold weather
                    errors.append(f"{item.name} may be too light for {temperature}°F weather")
                else:
                    warnings.append(f"{item.name} may not be optimal for {temperature}°F weather")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_weather_appropriate(self, item: ClothingItem, temperature: float) -> bool:
        """Check if item is appropriate for the given temperature."""
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        # Get material from metadata if available
        material = ""
        if item.metadata and item.metadata.visualAttributes and item.metadata.visualAttributes.material:
            material = item.metadata.visualAttributes.material.lower()
        
        # Hot weather (80°F+)
        if temperature >= 80:
            winter_materials = ['wool', 'fleece', 'thick', 'heavy']
            if material and any(mat in material for mat in winter_materials):
                return False
        
        # Cold weather (<50°F)
        elif temperature < 50:
            summer_materials = ['linen', 'light cotton']
            if material and any(mat in material for mat in summer_materials):
                return False
        
        return True
    
    def validate_occasion_appropriateness(
        self, 
        items: List[ClothingItem], 
        occasion: str
    ) -> Dict[str, Any]:
        """Validate occasion appropriateness."""
        if not items:
            return {"is_valid": True, "errors": [], "warnings": []}
        
        errors = []
        warnings = []
        
        occasion_lower = occasion.lower()
        
        # Check for occasion-specific requirements
        if 'formal' in occasion_lower or 'business' in occasion_lower:
            formal_items = [item for item in items if self._is_formal_item(item)]
            if len(formal_items) < 2:
                errors.append("Formal occasion requires more formal items")
        
        elif 'athletic' in occasion_lower or 'gym' in occasion_lower:
            athletic_items = [item for item in items if self._is_athletic_item(item)]
            if len(athletic_items) < 2:
                errors.append("Athletic occasion requires more athletic items")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_formal_item(self, item: ClothingItem) -> bool:
        """Check if item is formal."""
        formal_types = ['shirt', 'pants', 'dress', 'blazer', 'suit']
        return any(formal_type in item.type.lower() for formal_type in formal_types)
    
    def _is_athletic_item(self, item: ClothingItem) -> bool:
        """Check if item is athletic."""
        athletic_types = ['shirt', 'pants', 'shorts', 'sneakers', 'athletic']
        return any(athletic_type in item.type.lower() for athletic_type in athletic_types)
    
    def validate_form_completeness(
        self, 
        items: List[ClothingItem], 
        target_counts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that the outfit has the required number of items."""
        if not items:
            return {"is_valid": False, "errors": ["No items selected"], "warnings": []}
        
        min_items = target_counts.get("min_items", 2)
        max_items = target_counts.get("max_items", 6)
        
        errors = []
        warnings = []
        
        if len(items) < min_items:
            errors.append(f"Only {len(items)} items selected (minimum {min_items} required)")
        
        if len(items) > max_items:
            warnings.append(f"{len(items)} items may be too many (maximum {max_items} recommended)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_visual_harmony(self, items: List[ClothingItem]) -> Dict[str, Any]:
        """Validate visual harmony of the outfit."""
        if not items:
            return {"is_valid": True, "errors": [], "warnings": []}
        
        errors = []
        warnings = []
        
        # Check color compatibility
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                if not self._are_colors_compatible(item1, item2):
                    warnings.append(f"Color clash: {item1.name} and {item2.name}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _are_colors_compatible(self, item1: ClothingItem, item2: ClothingItem) -> bool:
        """Check if two items have compatible colors."""
        # Add color compatibility logic here
        return True
    
    def validate_formal_outfit_structure(
        self, 
        items: List[ClothingItem], 
        weather: WeatherData
    ) -> List[ClothingItem]:
        """Validate and adjust formal outfit structure."""
        # For now, return items as-is
        return items
    
    def structural_integrity_check(
        self, 
        selected_items: List[ClothingItem], 
        filtered_wardrobe: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check structural integrity of selected items."""
        # For now, return items as complete
        return {
            "is_complete": True, 
            "items": selected_items,
            "missing_categories": []
        }
    
    def debug_outfit_generation(self, items: List[ClothingItem], phase: str):
        """Debug outfit generation process."""
        print(f"🔍 DEBUG: {phase} - {len(items)} items")
        if items:
            print(f"  Items: {[item.name for item in items[:3]]}")
            if len(items) > 3:
                print(f"  ... and {len(items) - 3} more items") 