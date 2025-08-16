"""
Validation Orchestrator Service

This service provides workflow orchestration for outfit validation with:
- Parallel execution of independent validations
- Sequential execution of dependent validations  
- Clean error accumulation and performance tracking
- Comprehensive tracing and debugging
"""

import time
import asyncio
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
from ..custom_types.weather import WeatherData

class ValidationStep(Enum):
    OCCASION_APPROPRIATENESS = "occasion_appropriateness"
    LAYER_COUNT_APPROPRIATENESS = "layer_count_appropriateness"
    WEATHER_COMPATIBILITY = "weather_compatibility"
    STYLE_COHESION = "style_cohesion"
    FORM_COMPLETENESS = "form_completeness"
    COLOR_HARMONY = "color_harmony"
    BODY_TYPE_COMPATIBILITY = "body_type_compatibility"
    DEDUPLICATION = "deduplication"
    LAYERING_COMPLIANCE = "layering_compliance"

@dataclass
class ValidationResult:
    step: ValidationStep
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    duration: float

class ValidationOrchestrator:
    """Orchestrates validation steps with parallel execution where possible."""
    
    def __init__(self, outfit_service):
        self.outfit_service = outfit_service
        self.results: List[ValidationResult] = []
        
    async def run_validation_pipeline(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run all validation steps with orchestration."""
        
        print(f"🔧 Starting validation orchestration for {len(items)} items")
        
        # Add debugging to see what items we're validating
        if len(items) > 10:
            print(f"⚠️  WARNING: Validating {len(items)} items - this seems like the entire wardrobe!")
            print(f"🔍 First few items: {[item.name[:50] for item in items[:3]]}")
        else:
            print(f"✅ Validating {len(items)} selected items")
        
        # Phase 1: Parallel validations (independent checks)
        print("🔄 Phase 1: Running parallel validations...")
        parallel_tasks = [
            self._validate_occasion_appropriateness(items, context),
            self._validate_weather_compatibility(items, context),
            self._validate_style_cohesion(items, context),
            self._validate_body_type_compatibility(items, context),
        ]
        
        # Execute parallel validations
        parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid results
        valid_parallel_results = []
        for result in parallel_results:
            if isinstance(result, ValidationResult):
                valid_parallel_results.append(result)
            else:
                print(f"⚠️  Parallel validation failed: {result}")
        
        # Phase 2: Sequential validations (dependent on previous results)
        print("🔄 Phase 2: Running sequential validations...")
        sequential_results = []
        
        # Form completeness depends on occasion rules
        form_result = await self._validate_form_completeness(items, context)
        sequential_results.append(form_result)
        
        # Layer count depends on weather and occasion
        layer_result = await self._validate_layer_count_appropriateness(items, context)
        sequential_results.append(layer_result)
        
        # Layering compliance depends on weather and items
        layering_result = await self._validate_layering_compliance(items, context)
        sequential_results.append(layering_result)
        
        # Color harmony depends on all previous results
        color_result = await self._validate_color_harmony(items, context)
        sequential_results.append(color_result)
        
        # Phase 3: Deduplication (final step)
        dedup_result = await self._validate_deduplication(items, context)
        sequential_results.append(dedup_result)
        
        # Combine all results
        all_results = valid_parallel_results + sequential_results
        self.results = all_results
        
        final_result = self._aggregate_results()
        print(f"✅ Validation orchestration completed: {len(final_result['errors'])} errors, {len(final_result['warnings'])} warnings")
        
        return final_result
    
    async def _validate_occasion_appropriateness(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if items are appropriate for the occasion."""
        start_time = time.time()
        errors = []
        warnings = []
        
        occasion = context.get("occasion", "").lower()
        
        # Define occasion-specific rules - make them more lenient
        occasion_rules = {
            "formal": {
                "forbidden": ["athletic", "tank", "flip-flops"],  # Removed casual, shorts, sneakers
                "required": [],  # Removed strict requirements
                "preferred": ["formal", "business", "professional", "dress", "suit", "blazer", "dress_shoes"]
            },
            "casual": {
                "forbidden": [],  # Removed all forbidden items for casual
                "required": [],  # Removed strict requirements
                "preferred": ["casual", "comfortable", "relaxed", "jeans", "t-shirt", "sneakers", "hoodie"]
            },
            "athletic": {
                "forbidden": ["formal", "business", "dress", "suit"],  # Keep only formal items forbidden
                "required": [],  # Removed strict requirements
                "preferred": ["athletic", "sport", "active", "athletic_shoes", "athletic_pants", "athletic_shirt"]
            },
            "business": {
                "forbidden": ["athletic", "tank", "flip-flops"],  # Removed casual, shorts
                "required": [],  # Removed strict requirements
                "preferred": ["business", "professional", "formal", "dress_shirt", "dress_pants", "dress_shoes"]
            },
            "school": {
                "forbidden": [],  # Removed all forbidden items
                "required": [],  # Removed strict requirements
                "preferred": ["casual", "comfortable", "appropriate", "jeans", "t-shirt", "sneakers"]
            }
        }
        
        if occasion in occasion_rules:
            rules = occasion_rules[occasion]
            
            for item in items:
                # Check forbidden attributes
                item_attributes = [
                    item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower(),
                    *[tag.lower() for tag in item.tags],
                    *[style.lower() for style in item.style]
                ]
                
                for forbidden in rules["forbidden"]:
                    if forbidden in item_attributes:
                        warnings.append(f"Item '{item.name}' may not be ideal for {occasion} occasion")  # Changed from error to warning
                        break
                
                # Check if item has preferred attributes - make this optional
                has_preferred = any(preferred in item_attributes for preferred in rules.get("preferred", []))
                if not has_preferred:
                    warnings.append(f"Item '{item.name}' may not be ideal for {occasion} occasion")  # Keep as warning, not error
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.OCCASION_APPROPRIATENESS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"occasion": occasion, "rules_applied": occasion_rules.get(occasion, {})},
            duration=duration
        )
    
    async def _validate_weather_compatibility(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if items are appropriate for the weather conditions."""
        start_time = time.time()
        errors = []
        warnings = []
        
        weather = context.get("weather", {})
        # Handle both WeatherData objects and dictionaries
        if hasattr(weather, 'temperature'):
            temperature = weather.temperature
            condition = weather.condition.lower()
        else:
            temperature = weather.get("temperature", 70)
            condition = weather.get("condition", "clear").lower()
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        for item in items:
            # Temperature-based validation
            if temperature < 50:  # Cold weather
                cold_inappropriate = ["shorts", "tank", "sleeveless", "sandals"]
                item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
                if any(cold in item_type for cold in cold_inappropriate):
                    warnings.append(f"Item '{item.name}' may be too light for cold weather ({temperature}°F)")
            
            elif temperature > 80:  # Hot weather
                hot_inappropriate = ["heavy_coat", "sweater", "jacket", "long_sleeve"]
                item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
                if any(hot in item_type for hot in hot_inappropriate):
                    warnings.append(f"Item '{item.name}' may be too heavy for hot weather ({temperature}°F)")
            
            # Weather condition validation
            if condition == "rainy":
                rain_inappropriate = ["suede", "leather_shoes", "delicate"]
                item_materials = [tag.lower() for tag in item.tags if tag.lower() in ["suede", "leather", "delicate"]]
                if item_materials:
                    warnings.append(f"Item '{item.name}' may not be suitable for rainy weather")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.WEATHER_COMPATIBILITY,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"temperature": temperature, "condition": condition},
            duration=duration
        )
    
    async def _validate_style_cohesion(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if items have cohesive style."""
        start_time = time.time()
        errors = []
        warnings = []
        
        style = context.get("style", "").lower()
        
        # Collect all styles from items
        item_styles = []
        for item in items:
            item_styles.extend([s.lower() for s in item.style])
        
        # Check for style conflicts
        style_conflicts = {
            "formal": ["casual", "athletic", "bohemian"],
            "casual": ["formal", "business"],
            "athletic": ["formal", "business", "elegant"],
            "business": ["casual", "athletic", "bohemian"],
            "bohemian": ["formal", "business", "athletic"]
        }
        
        if style in style_conflicts:
            conflicting_styles = style_conflicts[style]
            for item_style in item_styles:
                if item_style in conflicting_styles:
                    warnings.append(f"Style conflict: {item_style} doesn't match {style} aesthetic")
        
        # Check for style consistency
        if len(set(item_styles)) > 3:
            warnings.append("Outfit has too many different styles, may lack cohesion")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.STYLE_COHESION,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"requested_style": style, "item_styles": list(set(item_styles))},
            duration=duration
        )
    
    async def _validate_body_type_compatibility(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if items are compatible with user's body type."""
        start_time = time.time()
        errors = []
        warnings = []
        
        user_profile = context.get("user_profile", {})
        # body_type = user_profile.get("body_type", "").lower()
        body_type = getattr(user_profile, 'bodyType', '') or ''
        body_type = body_type.lower()
        
        # Body type compatibility rules
        body_type_rules = {
            "rectangle": {
                "good": ["fitted", "structured", "belt"],
                "avoid": ["baggy", "oversized"]
            },
            "triangle": {
                "good": ["dark_bottom", "light_top", "structured_top"],
                "avoid": ["light_bottom", "baggy_top"]
            },
            "inverted_triangle": {
                "good": ["dark_top", "light_bottom", "structured_bottom"],
                "avoid": ["light_top", "baggy_bottom"]
            },
            "hourglass": {
                "good": ["fitted", "belt", "structured"],
                "avoid": ["baggy", "oversized"]
            }
        }
        
        if body_type in body_type_rules:
            rules = body_type_rules[body_type]
            
            for item in items:
                item_tags = [tag.lower() for tag in item.tags]
                
                # Check for items to avoid
                for avoid_tag in rules["avoid"]:
                    if avoid_tag in item_tags:
                        warnings.append(f"Item '{item.name}' may not flatter {body_type} body type")
                        break
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.BODY_TYPE_COMPATIBILITY,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"body_type": body_type, "rules_applied": body_type_rules.get(body_type, {})},
            duration=duration
        )
    
    async def _validate_form_completeness(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if outfit has all required form elements."""
        start_time = time.time()
        errors = []
        warnings = []
        
        target_counts = context.get("target_counts", {})
        min_items = target_counts.get("min_items", 3)
        required_categories = target_counts.get("required_categories", ["top", "bottom", "shoes"])
        
        # Count items by category
        category_counts = {}
        for item in items:
            category = self._get_item_category(item)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Check minimum items - make this a warning instead of error
        if len(items) < min_items:
            warnings.append(f"Outfit has {len(items)} items, minimum {min_items} recommended")  # Changed from error to warning
        
        # Check required categories - make this more lenient
        missing_categories = []
        for category in required_categories:
            if category not in category_counts or category_counts[category] == 0:
                missing_categories.append(category)
        
        if missing_categories:
            warnings.append(f"Missing recommended categories: {', '.join(missing_categories)}")  # Changed from error to warning
        
        # Check for too many items
        max_items = target_counts.get("max_items", 6)
        if len(items) > max_items:
            warnings.append(f"Outfit has {len(items)} items, maximum {max_items} recommended")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.FORM_COMPLETENESS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"item_count": len(items), "category_counts": category_counts, "target_counts": target_counts},
            duration=duration
        )
    
    async def _validate_layer_count_appropriateness(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate if layer count is appropriate for weather and occasion."""
        start_time = time.time()
        errors = []
        warnings = []
        
        weather = context.get("weather", {})
        # Handle both WeatherData objects and dictionaries
        if hasattr(weather, 'temperature'):
            temperature = weather.temperature
        else:
            temperature = weather.get("temperature", 70)
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        occasion = context.get("occasion", "").lower()
        
        # Calculate layer count
        layer_count = len([item for item in items if self._is_layer_item(item)])
        
        # Define layer rules by temperature and occasion - make them warnings instead of errors
        if temperature < 50:  # Cold weather
            if layer_count < 2:
                warnings.append(f"Consider adding more layers for cold weather: {layer_count} layers")  # Changed from error to warning
            elif layer_count < 3:
                warnings.append(f"Consider adding more layers for cold weather: {layer_count} layers")
        elif temperature > 80:  # Hot weather
            if layer_count > 2:
                warnings.append(f"Consider fewer layers for hot weather: {layer_count} layers")  # Changed from error to warning
        
        # Occasion-specific layer rules - make them warnings
        if "formal" in occasion and layer_count < 2:
            warnings.append(f"Formal occasion typically requires at least 2 layers, got {layer_count}")  # Changed from error to warning
        elif "casual" in occasion and layer_count > 3:
            warnings.append(f"Casual occasion may have too many layers: {layer_count} layers")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.LAYER_COUNT_APPROPRIATENESS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"layer_count": layer_count, "temperature": temperature, "occasion": occasion},
            duration=duration
        )
    
    async def _validate_layering_compliance(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate layering compliance using basic layering rules."""
        start_time = time.time()
        errors = []
        warnings = []
        
        weather = context.get("weather", {})
        # Handle both WeatherData objects and dictionaries
        if hasattr(weather, 'temperature'):
            temperature = weather.temperature
        else:
            temperature = weather.get("temperature", 70)
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        occasion = context.get("occasion", "")
        
        # Basic layering validation without outfit_service dependency
        layer_items = [item for item in items if self._is_layer_item(item)]
        
        # Temperature-based layering rules
        if temperature < 50:  # Cold weather
            if len(layer_items) < 2:
                warnings.append("Cold weather suggests multiple layers")
        elif temperature > 80:  # Hot weather
            if len(layer_items) > 1:
                warnings.append("Hot weather suggests fewer layers")
        
        # Occasion-based layering rules
        if occasion.lower() in ["formal", "business"]:
            if len(layer_items) < 1:
                warnings.append("Formal occasions typically require at least one layer")
        
        # Check for layering conflicts
        layer_types = [item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower() for item in layer_items]
        if "sweater" in layer_types and "jacket" in layer_types:
            warnings.append("Sweater and jacket combination may be too heavy")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.LAYERING_COMPLIANCE,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"layer_count": len(layer_items), "temperature": temperature, "occasion": occasion},
            duration=duration
        )
    
    async def _validate_color_harmony(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate color harmony between items."""
        start_time = time.time()
        errors = []
        warnings = []
        
        # Collect all dominant colors
        all_colors = []
        for item in items:
            if hasattr(item, 'dominantColors') and item.dominantColors:
                all_colors.extend([color.name.lower() for color in item.dominantColors])
        
        # Check for color conflicts
        color_conflicts = {
            "red": ["green"],
            "blue": ["orange"],
            "yellow": ["purple"],
            "green": ["red"],
            "purple": ["yellow"],
            "orange": ["blue"]
        }
        
        for i, color1 in enumerate(all_colors):
            for j, color2 in enumerate(all_colors[i+1:], i+1):
                if color1 in color_conflicts and color2 in color_conflicts[color1]:
                    warnings.append(f"Color conflict: {color1} and {color2} may clash")
        
        # Check for too many colors
        unique_colors = list(set(all_colors))
        if len(unique_colors) > 4:
            warnings.append(f"Too many colors ({len(unique_colors)}), may lack harmony")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.COLOR_HARMONY,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"unique_colors": unique_colors, "total_colors": len(all_colors)},
            duration=duration
        )
    
    async def _validate_deduplication(
        self, 
        items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that there are no duplicate items or categories."""
        start_time = time.time()
        errors = []
        warnings = []
        
        # Check for duplicate items
        item_ids = [item.id for item in items]
        if len(item_ids) != len(set(item_ids)):
            errors.append("Duplicate items detected in outfit")
        
        # Check for duplicate categories
        categories = [self._get_item_category(item) for item in items]
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            if count > 1:
                warnings.append(f"Multiple {category} items ({count}), consider variety")
        
        duration = time.time() - start_time
        return ValidationResult(
            step=ValidationStep.DEDUPLICATION,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"category_counts": category_counts, "unique_items": len(set(item_ids))},
            duration=duration
        )
    
    def _get_item_category(self, item: ClothingItem) -> str:
        """Get the category of an item."""
        item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
        
        # Map item types to categories
        category_mapping = {
            "shirt": "top",
            "t-shirt": "top", 
            "blouse": "top",
            "sweater": "top",
            "jacket": "outerwear",
            "coat": "outerwear",
            "pants": "bottom",
            "jeans": "bottom",
            "shorts": "bottom",
            "skirt": "bottom",
            "dress": "dress",
            "shoes": "shoes",
            "sneakers": "shoes",
            "boots": "shoes",
            "accessory": "accessory",
            "bag": "accessory"
        }
        
        return category_mapping.get(item_type, "other")
    
    def _is_layer_item(self, item: ClothingItem) -> bool:
        """Check if item is a layering item."""
        layer_types = ["shirt", "t-shirt", "blouse", "sweater", "jacket", "coat"]
        item_type = item.type.value.lower() if hasattr(item.type, 'value') else str(item.type).lower()
        return item_type in layer_types
    
    def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate all validation results."""
        all_errors = []
        all_warnings = []
        total_duration = 0
        step_summary = {}
        
        for result in self.results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            total_duration += result.duration
            step_summary[result.step.value] = {
                "is_valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "duration": result.duration
            }
        
        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "step_results": [result.__dict__ for result in self.results],
            "step_summary": step_summary,
            "total_duration": total_duration,
            "steps_executed": len(self.results),
            "success_rate": len([r for r in self.results if r.is_valid]) / len(self.results) if self.results else 0
        }

async def validate_outfit(items, context):
    """Convenience function to validate an outfit using the orchestrator."""
    orchestrator = ValidationOrchestrator(None)  # Pass None for outfit_service
    result = await orchestrator.run_validation_pipeline(items, context)
    return result 