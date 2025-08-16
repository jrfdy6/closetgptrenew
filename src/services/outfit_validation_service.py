"""
Outfit Validation Service
Handles all validation logic for outfit generation including temperature comparison fixes.
"""

from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
from ..custom_types.weather import WeatherData
from ..services.validation_orchestrator import ValidationResult


class OutfitValidationService:
    """Handles all validation operations for outfit generation."""
    
    def __init__(self):
        pass
    
    async def validate_outfit_with_orchestration(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate outfit using the validation orchestrator."""
        from .validation_orchestrator import ValidationOrchestrator
        
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
        result = await orchestrator.run_validation_pipeline(items, context)
        
        return {
            "is_valid": result["is_valid"],
            "errors": result["errors"],
            "warnings": result["warnings"],
            "details": result.get("details", {})
        }
    
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