#!/usr/bin/env python3
"""
Outfit Validation Pipeline
=========================

A comprehensive validation system that treats outfit validation like a pipeline:
each validator checks a constraint, and if it fails → reject or request a fix.

This system provides:
- Modular validation components
- Detailed error reporting
- Progressive hardening capabilities
- Integration with generation flow
- Comprehensive logging for rule tuning
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"    # Must fix - outfit completely inappropriate
    HIGH = "high"           # Should fix - major style violation
    MEDIUM = "medium"       # Consider fixing - minor style issue
    LOW = "low"            # Optional fix - style preference

@dataclass
class ValidationResult:
    """Result of a validation check"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    suggestions: List[str] = None
    confidence: float = 1.0

@dataclass
class ValidationContext:
    """Context for outfit validation"""
    occasion: str
    style: str
    mood: str
    weather: Dict[str, Any]
    user_profile: Dict[str, Any]
    temperature: float
    season: str = "unknown"

class OutfitValidationPipeline:
    """
    Core validation pipeline that orchestrates all validation checks
    """
    
    def __init__(self):
        self.validators = [
            WeatherValidator(),
            OccasionValidator(),
            StyleValidator(),
            LayeringValidator(),
            FormalityValidator(),
            ColorHarmonyValidator(),
            MaterialValidator(),
            FitValidator()
        ]
        
        # Validation statistics for tuning
        self.validation_stats = {
            "total_validations": 0,
            "failed_validations": 0,
            "common_failures": {},
            "severity_counts": {severity.value: 0 for severity in ValidationSeverity}
        }
    
    async def validate_outfit(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        """
        Main validation method that runs all validators in sequence
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1
        
        logger.info(f"🔍 Starting outfit validation pipeline for {context.occasion} occasion")
        logger.info(f"📋 Outfit items: {len(outfit.get('items', []))}")
        
        all_errors = []
        all_warnings = []
        all_suggestions = []
        max_severity = ValidationSeverity.LOW
        min_confidence = 1.0
        
        # Run all validators
        for validator in self.validators:
            try:
                result = await validator.validate(outfit, context)
                
                if not result.valid:
                    all_errors.extend(result.errors)
                    self.validation_stats["failed_validations"] += 1
                    
                    # Track common failures for tuning
                    for error in result.errors:
                        if error in self.validation_stats["common_failures"]:
                            self.validation_stats["common_failures"][error] += 1
                        else:
                            self.validation_stats["common_failures"][error] = 1
                
                if result.warnings:
                    all_warnings.extend(result.warnings)
                
                if result.suggestions:
                    all_suggestions.extend(result.suggestions)
                
                # Track severity
                if result.severity.value > max_severity.value:
                    max_severity = result.severity
                
                # Track confidence
                if result.confidence < min_confidence:
                    min_confidence = result.confidence
                
                # Update severity counts
                self.validation_stats["severity_counts"][result.severity.value] += 1
                
                logger.info(f"✅ {validator.__class__.__name__}: {'PASS' if result.valid else 'FAIL'}")
                if result.errors:
                    logger.info(f"   Errors: {result.errors}")
                if result.warnings:
                    logger.info(f"   Warnings: {result.warnings}")
                    
            except Exception as e:
                logger.error(f"❌ Validator {validator.__class__.__name__} failed: {e}")
                all_errors.append(f"Validation error in {validator.__class__.__name__}: {str(e)}")
        
        # Calculate overall result
        is_valid = len(all_errors) == 0
        duration = time.time() - start_time
        
        logger.info(f"🔍 Validation completed in {duration:.2f}s - {'PASS' if is_valid else 'FAIL'}")
        logger.info(f"📊 Errors: {len(all_errors)}, Warnings: {len(all_warnings)}")
        
        return ValidationResult(
            valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            severity=max_severity,
            suggestions=all_suggestions,
            confidence=min_confidence
        )
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics for tuning"""
        return self.validation_stats.copy()

class BaseValidator:
    """Base class for all validators"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        """Override this method in subclasses"""
        raise NotImplementedError

class WeatherValidator(BaseValidator):
    """Validates outfit appropriateness for weather conditions"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        temp = context.temperature
        condition = context.weather.get('condition', 'clear')
        precipitation = context.weather.get('precipitation', 0)
        
        items = outfit.get('items', [])
        
        # Check for heavy coats in hot weather
        if temp > 75:
            heavy_items = [item for item in items if self._is_heavy_item(item)]
            if heavy_items:
                errors.append(f"Too warm ({temp}°F) for heavy items: {[item.get('name', 'Unknown') for item in heavy_items]}")
                suggestions.append("Consider lighter fabrics like cotton or linen")
        
        # Check for shorts in cold weather
        if temp < 45:
            shorts = [item for item in items if 'shorts' in item.get('name', '').lower() or 'shorts' in item.get('type', '').lower()]
            if shorts:
                errors.append(f"Too cold ({temp}°F) for shorts: {[item.get('name', 'Unknown') for item in shorts]}")
                suggestions.append("Consider pants or long bottoms for cold weather")
        
        # Check for inappropriate rain wear
        if precipitation > 0.5 and condition in ['rain', 'drizzle']:
            inappropriate_rain_items = [item for item in items if self._is_inappropriate_for_rain(item)]
            if inappropriate_rain_items:
                warnings.append(f"Consider waterproof items for rainy weather: {[item.get('name', 'Unknown') for item in inappropriate_rain_items]}")
                suggestions.append("Add a rain jacket or umbrella")
        
        # Check for sun protection in hot, sunny weather
        if temp > 80 and condition == 'sunny':
            sun_protection = any('hat' in item.get('name', '').lower() or 'sunglasses' in item.get('name', '').lower() for item in items)
            if not sun_protection:
                suggestions.append("Consider adding sun protection for hot, sunny weather")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.HIGH if errors else ValidationSeverity.LOW
        )
    
    def _is_heavy_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is too heavy for hot weather"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        heavy_indicators = ['coat', 'wool', 'fleece', 'down', 'puffer', 'parka', 'heavy']
        return any(indicator in name or indicator in material for indicator in heavy_indicators)
    
    def _is_inappropriate_for_rain(self, item: Dict[str, Any]) -> bool:
        """Check if item is inappropriate for rainy weather"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        rain_inappropriate = ['suede', 'leather', 'canvas', 'cotton']
        return any(material_type in material for material_type in rain_inappropriate)

class OccasionValidator(BaseValidator):
    """Validates outfit appropriateness for the occasion"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        occasion = context.occasion.lower()
        items = outfit.get('items', [])
        
        # Business formal validation
        if 'formal' in occasion or 'business' in occasion:
            # Check for inappropriate shoes
            inappropriate_shoes = [item for item in items if self._is_inappropriate_shoe_for_formal(item)]
            if inappropriate_shoes:
                errors.append(f"Inappropriate shoes for {occasion}: {[item.get('name', 'Unknown') for item in inappropriate_shoes]}")
                suggestions.append("Consider dress shoes, oxfords, or loafers for formal occasions")
            
            # Check for casual tops
            casual_tops = [item for item in items if self._is_casual_top(item)]
            if casual_tops:
                errors.append(f"Too casual for {occasion}: {[item.get('name', 'Unknown') for item in casual_tops]}")
                suggestions.append("Consider dress shirts or blouses for formal occasions")
            
            # Check for shorts
            shorts = [item for item in items if 'shorts' in item.get('name', '').lower()]
            if shorts:
                errors.append(f"Shorts are not appropriate for {occasion}: {[item.get('name', 'Unknown') for item in shorts]}")
                suggestions.append("Consider dress pants or skirts for formal occasions")
        
        # Athletic occasion validation
        elif 'athletic' in occasion or 'gym' in occasion:
            # Check for formal items
            formal_items = [item for item in items if self._is_formal_item(item)]
            if formal_items:
                errors.append(f"Too formal for {occasion}: {[item.get('name', 'Unknown') for item in formal_items]}")
                suggestions.append("Consider athletic wear, sneakers, and comfortable clothing")
        
        # Party occasion validation
        elif 'party' in occasion or 'night' in occasion:
            # Check for work clothes
            work_items = [item for item in items if self._is_work_item(item)]
            if work_items:
                warnings.append(f"Consider more festive items for {occasion}: {[item.get('name', 'Unknown') for item in work_items]}")
                suggestions.append("Consider stylish, trendy, or dressy items for parties")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.CRITICAL if errors else ValidationSeverity.LOW
        )
    
    def _is_inappropriate_shoe_for_formal(self, item: Dict[str, Any]) -> bool:
        """Check if shoe is inappropriate for formal occasions"""
        if item.get('type', '').lower() not in ['shoes', 'footwear']:
            return False
        
        name = item.get('name', '').lower()
        inappropriate = ['sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs']
        return any(term in name for term in inappropriate)
    
    def _is_casual_top(self, item: Dict[str, Any]) -> bool:
        """Check if top is too casual for formal occasions"""
        if item.get('type', '').lower() not in ['shirt', 'top', 'blouse']:
            return False
        
        name = item.get('name', '').lower()
        casual_indicators = ['t-shirt', 'tank', 'hoodie', 'sweatshirt', 'jersey']
        return any(indicator in name for indicator in casual_indicators)
    
    def _is_formal_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is too formal for athletic occasions"""
        name = item.get('name', '').lower()
        formal_indicators = ['suit', 'dress pants', 'oxford', 'loafers', 'heels', 'blazer']
        return any(indicator in name for indicator in formal_indicators)
    
    def _is_work_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is too work-like for party occasions"""
        name = item.get('name', '').lower()
        work_indicators = ['work', 'business', 'professional', 'office']
        return any(indicator in name for indicator in work_indicators)

class StyleValidator(BaseValidator):
    """Validates outfit consistency with requested style"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        style = context.style.lower()
        items = outfit.get('items', [])
        
        # Check style consistency
        if style == 'minimalist':
            if len(items) > 4:
                warnings.append(f"Minimalist style typically uses fewer items (current: {len(items)})")
                suggestions.append("Consider removing one or two items for a cleaner look")
        
        elif style == 'maximalist':
            if len(items) < 5:
                warnings.append(f"Maximalist style typically uses more items (current: {len(items)})")
                suggestions.append("Consider adding accessories or layers for a bolder look")
        
        # Check for style-appropriate items
        inappropriate_items = [item for item in items if not self._is_style_appropriate(item, style)]
        if inappropriate_items:
            warnings.append(f"Some items may not match {style} style: {[item.get('name', 'Unknown') for item in inappropriate_items]}")
            suggestions.append(f"Consider items that better match {style} aesthetic")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.LOW
        )
    
    def _is_style_appropriate(self, item: Dict[str, Any], style: str) -> bool:
        """Check if item is appropriate for the style"""
        name = item.get('name', '').lower()
        item_style = item.get('style', [])
        
        if isinstance(item_style, list):
            item_style = ' '.join(item_style).lower()
        else:
            item_style = str(item_style).lower()
        
        # Basic style matching - can be enhanced
        style_keywords = {
            'minimalist': ['minimal', 'simple', 'clean', 'basic'],
            'maximalist': ['bold', 'patterned', 'colorful', 'statement'],
            'classic': ['classic', 'traditional', 'timeless'],
            'modern': ['modern', 'contemporary', 'sleek'],
            'vintage': ['vintage', 'retro', 'classic'],
            'bohemian': ['bohemian', 'boho', 'flowy', 'artistic']
        }
        
        if style in style_keywords:
            return any(keyword in name or keyword in item_style for keyword in style_keywords[style])
        
        return True  # Default to appropriate if style not recognized

class LayeringValidator(BaseValidator):
    """Validates proper layering for the occasion and weather"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        items = outfit.get('items', [])
        temp = context.temperature
        occasion = context.occasion.lower()
        
        # Count layering items
        tops = [item for item in items if item.get('type', '').lower() in ['shirt', 'top', 'blouse', 'sweater']]
        outerwear = [item for item in items if item.get('type', '').lower() in ['jacket', 'coat', 'blazer', 'cardigan']]
        
        # Check for excessive layering in hot weather
        if temp > 80 and len(tops) + len(outerwear) > 3:
            warnings.append(f"Too many layers for hot weather ({temp}°F): {len(tops + outerwear)} items")
            suggestions.append("Consider removing a layer for hot weather")
        
        # Check for insufficient layering in cold weather
        if temp < 50 and len(tops) + len(outerwear) < 2:
            warnings.append(f"May need more layers for cold weather ({temp}°F): {len(tops + outerwear)} items")
            suggestions.append("Consider adding a sweater or jacket for cold weather")
        
        # Check for formal layering requirements
        if 'formal' in occasion or 'business' in occasion:
            if not outerwear:
                warnings.append("Formal occasions typically include a jacket or blazer")
                suggestions.append("Consider adding a blazer or jacket for formal occasions")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.MEDIUM if warnings else ValidationSeverity.LOW
        )

class FormalityValidator(BaseValidator):
    """Validates formality consistency across the outfit"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        items = outfit.get('items', [])
        
        # Check for formality mismatches
        formal_items = [item for item in items if self._is_formal_item(item)]
        casual_items = [item for item in items if self._is_casual_item(item)]
        
        if formal_items and casual_items:
            warnings.append(f"Mixed formality levels: formal items {[item.get('name', 'Unknown') for item in formal_items]} with casual items {[item.get('name', 'Unknown') for item in casual_items]}")
            suggestions.append("Consider matching formality levels across all items")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.MEDIUM
        )
    
    def _is_formal_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is formal"""
        name = item.get('name', '').lower()
        formal_indicators = ['suit', 'dress pants', 'oxford', 'loafers', 'heels', 'blazer', 'dress shirt']
        return any(indicator in name for indicator in formal_indicators)
    
    def _is_casual_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is casual"""
        name = item.get('name', '').lower()
        casual_indicators = ['t-shirt', 'sneakers', 'jeans', 'shorts', 'hoodie', 'sweatpants']
        return any(indicator in name for indicator in casual_indicators)

class ColorHarmonyValidator(BaseValidator):
    """Validates color harmony and coordination"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        items = outfit.get('items', [])
        colors = [item.get('color', '').lower() for item in items if item.get('color')]
        
        if len(colors) < 2:
            return ValidationResult(valid=True, errors=[], warnings=[], suggestions=[])
        
        # Check for too many different colors
        unique_colors = set(colors)
        if len(unique_colors) > 4:
            warnings.append(f"Many different colors ({len(unique_colors)}): {list(unique_colors)}")
            suggestions.append("Consider limiting to 3-4 colors for better coordination")
        
        # Check for clashing colors (basic implementation)
        clashing_pairs = [('red', 'green'), ('blue', 'orange'), ('yellow', 'purple')]
        for color1, color2 in clashing_pairs:
            if color1 in colors and color2 in colors:
                warnings.append(f"Potential color clash: {color1} and {color2}")
                suggestions.append("Consider using complementary or neutral colors")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.LOW
        )

class MaterialValidator(BaseValidator):
    """Validates material appropriateness for weather and occasion"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        items = outfit.get('items', [])
        temp = context.temperature
        
        for item in items:
            material = item.get('material', '').lower()
            name = item.get('name', '').lower()
            
            # Check for inappropriate materials in hot weather
            if temp > 80 and material in ['wool', 'fleece', 'suede']:
                warnings.append(f"Material {material} may be too warm for {temp}°F: {item.get('name', 'Unknown')}")
                suggestions.append("Consider lighter materials like cotton or linen for hot weather")
            
            # Check for inappropriate materials in cold weather
            if temp < 50 and material in ['linen', 'silk']:
                warnings.append(f"Material {material} may be too light for {temp}°F: {item.get('name', 'Unknown')}")
                suggestions.append("Consider warmer materials like wool or fleece for cold weather")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.LOW
        )

class FitValidator(BaseValidator):
    """Validates fit appropriateness for the occasion"""
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        items = outfit.get('items', [])
        occasion = context.occasion.lower()
        
        # Check for overly tight or loose items in formal occasions
        if 'formal' in occasion or 'business' in occasion:
            for item in items:
                name = item.get('name', '').lower()
                if 'oversized' in name or 'loose' in name:
                    warnings.append(f"Consider more fitted items for formal occasions: {item.get('name', 'Unknown')}")
                    suggestions.append("Formal occasions typically call for well-fitted clothing")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.LOW
        )

# Global validation pipeline instance
validation_pipeline = OutfitValidationPipeline()
