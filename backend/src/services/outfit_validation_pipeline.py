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
        
        # Analytics integration
        self.analytics_enabled = True
    
    async def validate_outfit(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        """
        Main validation method that runs all validators in sequence
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1
        
        logger.info(f"🔍 Starting outfit validation pipeline for {context.occasion} occasion")
        logger.info(f"📋 Outfit items: {len((outfit.get('items', []) if outfit else []))}")
        
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
        
        # Log validation failures to analytics (if enabled and validation failed)
        if self.analytics_enabled and not is_valid:
            try:
                from .validation_analytics_service import validation_analytics
                
                # Log each validator failure separately
                for validator in self.validators:
                    try:
                        result = await validator.validate(outfit, context)
                        if not result.valid:
                            await validation_analytics.log_validation_failure(
                                validator_name=validator.__class__.__name__,
                                severity=result.severity.value,
                                error_message="; ".join(result.errors) if result.errors else "",
                                warning_message="; ".join(result.warnings) if result.warnings else "",
                                suggestion_message="; ".join(result.suggestions) if result.suggestions else "",
                                context={
                                    "occasion": context.occasion,
                                    "style": context.style,
                                    "mood": context.mood,
                                    "temperature": context.temperature,
                                    "weather": context.weather
                                },
                                outfit_items=(outfit.get("items", []) if outfit else []),
                                user_id=context.(user_profile.get("id", "unknown") if user_profile else "unknown"),
                                validation_duration=duration,
                                outfit_id=(outfit.get("id", f"outfit_{int(time.time() if outfit else f"outfit_{int(time.time())}"),
                                generation_request_id=f"req_{int(time.time())}",
                                retry_attempt=0
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to log validation failure for {validator.__class__.__name__}: {e}")
                        
            except ImportError:
                logger.warning("⚠️ Analytics service not available for validation logging")
            except Exception as e:
                logger.warning(f"⚠️ Failed to log validation failures: {e}")
        
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
    
    def __init__(self):
        # Enhanced temperature thresholds
        self.temp_thresholds = {
            'very_hot': 85,      # >85°F - no heavy items allowed
            'hot': 75,           # >75°F - no heavy coats, warn about heavy items
            'warm': 65,          # >65°F - allow lightweight jackets
            'moderate': 55,      # >55°F - allow light layering
            'cool': 45,          # >45°F - allow moderate layering
            'cold': 35,          # >35°F - require warm clothing
            'very_cold': 25      # <25°F - require heavy winter clothing
        }
        
        # Item weight classifications
        self.heavy_items = {
            'coats': ['parka', 'down', 'puffer', 'wool coat', 'heavy coat', 'winter coat', 'overcoat'],
            'materials': ['wool', 'fleece', 'down', 'heavy cotton', 'thick'],
            'types': ['coat', 'parka', 'overcoat']
        }
        
        self.lightweight_items = {
            'jackets': ['blazer', 'sport coat', 'light jacket', 'cardigan', 'sweater'],
            'materials': ['cotton', 'linen', 'light wool', 'breathable'],
            'types': ['blazer', 'cardigan', 'sweater']
        }
        
        self.moderate_items = {
            'jackets': ['jacket', 'sweater', 'hoodie', 'cardigan'],
            'materials': ['cotton', 'light wool', 'acrylic'],
            'types': ['jacket', 'sweater', 'hoodie']
        }
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        temp = context.temperature
        condition = context.(weather.get('condition', 'clear') if weather else 'clear')
        precipitation = context.(weather.get('precipitation', 0) if weather else 0)
        
        items = (outfit.get('items', []) if outfit else [])
        
        # Enhanced temperature-based validation
        temp_validation = self._validate_temperature_appropriateness(items, temp)
        errors.extend(temp_validation['errors'])
        warnings.extend(temp_validation['warnings'])
        suggestions.extend(temp_validation['suggestions'])
        
        # Check for inappropriate rain wear
        if precipitation > 0.5 and condition in ['rain', 'drizzle']:
            inappropriate_rain_items = [item for item in items if self._is_inappropriate_for_rain(item)]
            if inappropriate_rain_items:
                warnings.append(f"Consider waterproof items for rainy weather: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in inappropriate_rain_items]}")
                suggestions.append("Add a rain jacket or umbrella")
        
        # Check for sun protection in hot, sunny weather
        if temp > 80 and condition == 'sunny':
            sun_protection = any('hat' in ((item.get('name', '') if item else '') if item else '').lower() or 'sunglasses' in ((item.get('name', '') if item else '') if item else '').lower() for item in items)
            if not sun_protection:
                suggestions.append("Consider adding sun protection for hot, sunny weather")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.HIGH if errors else ValidationSeverity.LOW
        )
    
    def _validate_temperature_appropriateness(self, items: List[Dict[str, Any]], temp: float) -> Dict[str, List[str]]:
        """Enhanced temperature validation with graduated thresholds"""
        errors = []
        warnings = []
        suggestions = []
        
        # Very hot weather (>85°F) - no heavy items allowed
        if temp > self.temp_thresholds['very_hot']:
            heavy_items = [item for item in items if self._is_heavy_item(item)]
            if heavy_items:
                errors.append(f"TOO HOT ({temp}°F): Heavy items not allowed: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in heavy_items]}")
                suggestions.append("CRITICAL: Remove heavy coats, use only lightweight fabrics")
        
        # Hot weather (>75°F) - no heavy coats, warn about heavy items
        elif temp > self.temp_thresholds['hot']:
            heavy_coats = [item for item in items if self._is_heavy_coat(item)]
            if heavy_coats:
                errors.append(f"HOT WEATHER ({temp}°F): Heavy coats not appropriate: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in heavy_coats]}")
                suggestions.append("Consider lightweight blazers or cardigans instead of heavy coats")
            
            # Check for borderline items
            borderline_items = [item for item in items if self._is_borderline_heavy(item)]
            if borderline_items:
                warnings.append(f"HOT WEATHER ({temp}°F): Consider lighter alternatives: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in borderline_items]}")
                suggestions.append("Lightweight jackets or cardigans are better for hot weather")
        
        # Warm weather (>65°F) - allow lightweight jackets
        elif temp > self.temp_thresholds['warm']:
            # Check for appropriate lightweight layering
            lightweight_items = [item for item in items if self._is_lightweight_item(item)]
            if lightweight_items:
                suggestions.append(f"PERFECT: Lightweight layering appropriate for {temp}°F: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in lightweight_items]}")
        
        # Moderate weather (>55°F) - allow light layering
        elif temp > self.temp_thresholds['moderate']:
            # Check for appropriate moderate layering
            moderate_items = [item for item in items if self._is_moderate_item(item)]
            if moderate_items:
                suggestions.append(f"GOOD: Moderate layering appropriate for {temp}°F: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in moderate_items]}")
        
        # Cool weather (>45°F) - allow moderate layering
        elif temp > self.temp_thresholds['cool']:
            # Check for appropriate cool weather clothing
            if not any(self._is_warm_item(item) for item in items):
                warnings.append(f"COOL WEATHER ({temp}°F): Consider adding a light jacket or sweater")
                suggestions.append("Add a light jacket, sweater, or cardigan for cool weather")
        
        # Cold weather (>35°F) - require warm clothing
        elif temp > self.temp_thresholds['cold']:
            warm_items = [item for item in items if self._is_warm_item(item)]
            if not warm_items:
                errors.append(f"COLD WEATHER ({temp}°F): Warm clothing required")
                suggestions.append("REQUIRED: Add a jacket, sweater, or warm outer layer")
            
            # Check for shorts in cold weather
            shorts = [item for item in items if 'shorts' in ((item.get('name', '') if item else '') if item else '').lower() or 'shorts' in item.get('type', '').lower()]
            if shorts:
                errors.append(f"TOO COLD ({temp}°F) for shorts: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in shorts]}")
                suggestions.append("REQUIRED: Use pants or long bottoms for cold weather")
        
        # Very cold weather (<35°F) - require heavy winter clothing
        else:
            heavy_winter_items = [item for item in items if self._is_heavy_winter_item(item)]
            if not heavy_winter_items:
                errors.append(f"VERY COLD ({temp}°F): Heavy winter clothing required")
                suggestions.append("REQUIRED: Add heavy coat, parka, or winter jacket")
            
            # Check for insufficient layering
            total_layers = len([item for item in items if item.get('type', '').lower() in ['shirt', 'top', 'sweater', 'jacket', 'coat']])
            if total_layers < 2:
                warnings.append(f"VERY COLD ({temp}°F): Consider more layers for warmth")
                suggestions.append("Add multiple layers for very cold weather")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _is_heavy_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is heavy (not suitable for hot weather)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        # Check against heavy item classifications
        for category, terms in self.heavy_items.items():
            if any(term in name or term in material for term in terms):
                return True
        
        return False
    
    def _is_heavy_coat(self, item: Dict[str, Any]) -> bool:
        """Check if item is specifically a heavy coat"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        return any(term in name or term in material for term in self.heavy_items['coats'])
    
    def _is_borderline_heavy(self, item: Dict[str, Any]) -> bool:
        """Check if item is borderline heavy (warn but don't error)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        borderline_terms = ['sweater', 'cardigan', 'jacket', 'blazer']
        return any(term in name for term in borderline_terms) and any(heavy_term in material for heavy_term in ['wool', 'fleece'])
    
    def _is_lightweight_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is lightweight (suitable for warm weather)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        for category, terms in self.lightweight_items.items():
            if any(term in name or term in material for term in terms):
                return True
        
        return False
    
    def _is_moderate_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is moderate weight (suitable for moderate weather)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        for category, terms in self.moderate_items.items():
            if any(term in name or term in material for term in terms):
                return True
        
        return False
    
    def _is_warm_item(self, item: Dict[str, Any]) -> bool:
        """Check if item provides warmth (suitable for cool weather)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        warm_indicators = ['sweater', 'cardigan', 'jacket', 'coat', 'hoodie', 'wool', 'fleece']
        return any(indicator in name or indicator in material for indicator in warm_indicators)
    
    def _is_heavy_winter_item(self, item: Dict[str, Any]) -> bool:
        """Check if item is heavy winter clothing (suitable for very cold weather)"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        winter_indicators = ['parka', 'down', 'puffer', 'winter coat', 'heavy coat', 'overcoat', 'wool coat']
        return any(indicator in name or indicator in material for indicator in winter_indicators)
    
    def _is_inappropriate_for_rain(self, item: Dict[str, Any]) -> bool:
        """Check if item is inappropriate for rainy weather"""
        name = item.get('name', '').lower()
        material = item.get('material', '').lower()
        
        rain_inappropriate = ['suede', 'leather', 'canvas', 'cotton']
        return any(material_type in material for material_type in rain_inappropriate)

class OccasionValidator(BaseValidator):
    """Validates outfit appropriateness for the occasion"""
    
    def __init__(self):
        # Explicit blacklists for formal occasions - ENHANCED MATCHING
        self.formal_blacklist = {
            'shoes': ['sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs', 'running', 'basketball', 'tennis', 'smooth shoes', 'solid shoes', 'casual shoes'],
            'tops': ['t-shirt', 't shirt', 'tank', 'tank top', 'jersey', 'basketball', 'sport', 'athletic', 'hoodie', 'sweatshirt', 'tee', 't-shirt'],
            'bottoms': ['shorts', 'sweatpants', 'joggers', 'athletic', 'basketball', 'sport'],
            'outerwear': ['biker', 'leather jacket', 'hoodie', 'sweatshirt']
        }
        
        # Positive reinforcement items for formal occasions
        self.formal_positive = {
            'shoes': ['oxford', 'loafer', 'dress shoe', 'dress shoes', 'heels', 'pumps', 'derby'],
            'tops': ['dress shirt', 'button up', 'button-up', 'blouse', 'dress shirt', 'oxford shirt'],
            'bottoms': ['dress pants', 'dress trousers', 'slacks', 'dress skirt', 'pencil skirt'],
            'outerwear': ['blazer', 'suit jacket', 'sport coat', 'dress coat', 'overcoat']
        }
        
        # Business casual specific rules
        self.business_casual_allowed = {
            'shoes': ['loafer', 'dress shoe', 'dress shoes', 'oxford', 'derby', 'boots', 'chukka'],
            'tops': ['dress shirt', 'button up', 'button-up', 'polo', 'sweater', 'cardigan'],
            'bottoms': ['dress pants', 'chinos', 'dress trousers', 'khakis', 'dress skirt'],
            'outerwear': ['blazer', 'sport coat', 'cardigan', 'sweater']
        }
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        occasion = context.occasion.lower()
        items = (outfit.get('items', []) if outfit else [])
        
        # Business formal validation - STRICTEST RULES
        if 'formal' in occasion or 'business' in occasion:
            # Check for explicitly blacklisted items
            blacklist_violations = self._check_blacklist_violations(items, occasion)
            if blacklist_violations:
                for category, violations in blacklist_violations.items():
                    errors.append(f"Blacklisted {category} for {occasion}: {violations}")
                
                # Provide specific suggestions based on violations
                if 'shoes' in blacklist_violations:
                    suggestions.append("REQUIRED: Dress shoes, oxfords, or loafers for formal occasions")
                if 'tops' in blacklist_violations:
                    suggestions.append("REQUIRED: Dress shirts, button-ups, or blouses for formal occasions")
                if 'bottoms' in blacklist_violations:
                    suggestions.append("REQUIRED: Dress pants, slacks, or dress skirts for formal occasions")
                if 'outerwear' in blacklist_violations:
                    suggestions.append("REQUIRED: Blazers, suit jackets, or dress coats for formal occasions")
            
            # Check for positive reinforcement items (boost scoring)
            positive_items = self._check_positive_reinforcement(items, occasion)
            if positive_items:
                suggestions.append(f"EXCELLENT: Found appropriate formal items: {positive_items}")
            
            # Check for missing essential formal items
            missing_essentials = self._check_missing_formal_essentials(items, occasion)
            if missing_essentials:
                warnings.append(f"Consider adding formal essentials: {missing_essentials}")
                suggestions.extend([f"Add {item} for complete formal look" for item in missing_essentials])
        
        # Business casual validation - MODERATE RULES
        elif 'business' in occasion and 'casual' in occasion:
            # Check for inappropriate items for business casual
            inappropriate_items = [item for item in items if self._is_inappropriate_for_business_casual(item)]
            if inappropriate_items:
                errors.append(f"Inappropriate for business casual: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in inappropriate_items]}")
                suggestions.append("Business casual allows dress shoes, polo shirts, chinos, and blazers")
        
        # Athletic occasion validation
        elif 'athletic' in occasion or 'gym' in occasion:
            # Check for formal items
            formal_items = [item for item in items if self._is_formal_item(item)]
            if formal_items:
                errors.append(f"Too formal for {occasion}: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in formal_items]}")
                suggestions.append("Consider athletic wear, sneakers, and comfortable clothing")
            
            # Check for blazers and jackets specifically
            blazer_items = [item for item in items if 'blazer' in ((item.get('name', '') if item else '') if item else '').lower() or 'jacket' in ((item.get('name', '') if item else '') if item else '').lower()]
            if blazer_items:
                errors.append(f"Inappropriate for {occasion}: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in blazer_items]}")
                suggestions.append("Athletic occasions require athletic wear, not formal jackets")
        
        # Party occasion validation
        elif 'party' in occasion or 'night' in occasion:
            # Check for work clothes
            work_items = [item for item in items if self._is_work_item(item)]
            if work_items:
                warnings.append(f"Consider more festive items for {occasion}: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in work_items]}")
                suggestions.append("Consider stylish, trendy, or dressy items for parties")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=ValidationSeverity.CRITICAL if errors else ValidationSeverity.LOW
        )
    
    def _check_blacklist_violations(self, items: List[Dict[str, Any]], occasion: str) -> Dict[str, List[str]]:
        """Check for blacklisted items in formal occasions"""
        violations = {}
        
        for item in items:
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
            
            # Map item types to categories
            category = None
            if item_type in ['shoes', 'footwear']:
                category = 'shoes'
            elif item_type in ['shirt', 'top', 'blouse', 'sweater', 'hoodie']:
                category = 'tops'
            elif item_type in ['pants', 'bottoms', 'shorts', 'trousers']:
                category = 'bottoms'
            elif item_type in ['jacket', 'coat', 'blazer', 'outerwear']:
                category = 'outerwear'
            
            if category and category in self.formal_blacklist:
                # Enhanced matching - check if item name contains any blacklisted terms
                for blacklisted_term in self.formal_blacklist[category]:
                    if blacklisted_term in item_name:
                        if category not in violations:
                            violations[category] = []
                        violations[category].append(f"{(item.get('name', 'Unknown') if item else 'Unknown')} (matched: '{blacklisted_term}')")
                        break
                
                # Additional check for generic shoe names that might be sneakers
                if category == 'shoes' and not any(term in item_name for term in self.formal_blacklist[category]):
                    # Check for generic shoe descriptions that are likely sneakers
                    generic_sneaker_indicators = ['smooth shoes', 'solid shoes', 'casual shoes', 'white shoes', 'black shoes']
                    if any(indicator in item_name for indicator in generic_sneaker_indicators):
                        if category not in violations:
                            violations[category] = []
                        violations[category].append(f"{(item.get('name', 'Unknown') if item else 'Unknown')} (generic shoe - likely sneaker)")
        
        return violations
    
    def _check_positive_reinforcement(self, items: List[Dict[str, Any]], occasion: str) -> List[str]:
        """Check for positive reinforcement items in formal occasions"""
        positive_items = []
        
        for item in items:
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
            
            # Map item types to categories
            category = None
            if item_type in ['shoes', 'footwear']:
                category = 'shoes'
            elif item_type in ['shirt', 'top', 'blouse', 'sweater']:
                category = 'tops'
            elif item_type in ['pants', 'bottoms', 'trousers']:
                category = 'bottoms'
            elif item_type in ['jacket', 'coat', 'blazer', 'outerwear']:
                category = 'outerwear'
            
            if category and category in self.formal_positive:
                # Check if item name contains any positive terms
                for positive_term in self.formal_positive[category]:
                    if positive_term in item_name:
                        positive_items.append((item.get('name', 'Unknown') if item else 'Unknown'))
                        break
        
        return positive_items
    
    def _check_missing_formal_essentials(self, items: List[Dict[str, Any]], occasion: str) -> List[str]:
        """Check for missing essential formal items"""
        missing = []
        
        # Check for essential formal items
        has_formal_shoes = any(
            any(term in item.get('name', '').lower() for term in self.formal_positive['shoes'])
            for item in items if item.get('type', '').lower() in ['shoes', 'footwear']
        )
        
        has_formal_top = any(
            any(term in item.get('name', '').lower() for term in self.formal_positive['tops'])
            for item in items if item.get('type', '').lower() in ['shirt', 'top', 'blouse']
        )
        
        has_formal_bottom = any(
            any(term in item.get('name', '').lower() for term in self.formal_positive['bottoms'])
            for item in items if item.get('type', '').lower() in ['pants', 'bottoms', 'trousers']
        )
        
        if not has_formal_shoes:
            missing.append("formal shoes")
        if not has_formal_top:
            missing.append("formal top")
        if not has_formal_bottom:
            missing.append("formal bottom")
        
        return missing
    
    def _is_inappropriate_for_business_casual(self, item: Dict[str, Any]) -> bool:
        """Check if item is inappropriate for business casual"""
        item_type = item.get('type', '').lower()
        item_name = item.get('name', '').lower()
        
        # Business casual allows more flexibility than formal
        inappropriate_terms = [
            't-shirt', 'tank', 'sweatpants', 'shorts', 'sneakers', 'flip', 'slides'
        ]
        
        return any(term in item_name for term in inappropriate_terms)
    
    def _is_inappropriate_shoe_for_formal(self, item: Dict[str, Any]) -> bool:
        """Check if shoe is inappropriate for formal occasions"""
        if item.get('type', '').lower() not in ['shoes', 'footwear']:
            return False
        
        name = (item.get('name', '') if item else '').lower()
        inappropriate = ['sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs']
        return any(term in name for term in inappropriate)
    
    def _is_casual_top(self, item: Dict[str, Any]) -> bool:
        """Check if top is too casual for formal occasions"""
        if item.get('type', '').lower() not in ['shirt', 'top', 'blouse']:
            return False
        
        name = (item.get('name', '') if item else '').lower()
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
    
    def __init__(self):
        # Enhanced style definitions with specific rules
        self.style_rules = {
            'minimalist': {
                'max_items': 4,
                'color_limit': 3,
                'preferred_items': ['simple', 'clean', 'basic', 'solid'],
                'avoid_items': ['patterned', 'bold', 'colorful', 'statement', 'loud'],
                'severity': ValidationSeverity.MEDIUM
            },
            'maximalist': {
                'min_items': 5,
                'color_limit': 6,
                'preferred_items': ['bold', 'patterned', 'colorful', 'statement', 'vibrant'],
                'avoid_items': ['simple', 'plain', 'basic', 'minimal'],
                'severity': ValidationSeverity.MEDIUM
            },
            'formal': {
                'required_items': ['dress shoes', 'dress shirt', 'dress pants'],
                'preferred_items': ['suit', 'blazer', 'oxford', 'loafer', 'dress'],
                'avoid_items': ['casual', 'sneaker', 't-shirt', 'shorts'],
                'severity': ValidationSeverity.HIGH
            },
            'classic': {
                'preferred_items': ['traditional', 'timeless', 'elegant', 'sophisticated'],
                'avoid_items': ['trendy', 'fashion-forward', 'edgy', 'experimental'],
                'severity': ValidationSeverity.LOW
            },
            'modern': {
                'preferred_items': ['contemporary', 'sleek', 'clean', 'streamlined'],
                'avoid_items': ['vintage', 'retro', 'outdated', 'old-fashioned'],
                'severity': ValidationSeverity.LOW
            }
        }
    
    async def validate(self, outfit: Dict[str, Any], context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        
        style = context.style.lower()
        items = (outfit.get('items', []) if outfit else [])
        
        # Get style rules
        style_rule = self.(style_rules.get(style, {}) if style_rules else {})
        if not style_rule:
            return ValidationResult(valid=True, errors=[], warnings=[], suggestions=[])
        
        # Check item count rules
        item_count_validation = self._validate_item_count(items, style, style_rule)
        errors.extend(item_count_validation['errors'])
        warnings.extend(item_count_validation['warnings'])
        suggestions.extend(item_count_validation['suggestions'])
        
        # Check color count rules
        color_validation = self._validate_color_count(items, style, style_rule)
        warnings.extend(color_validation['warnings'])
        suggestions.extend(color_validation['suggestions'])
        
        # Check for style-appropriate items
        appropriateness_validation = self._validate_style_appropriateness(items, style, style_rule)
        errors.extend(appropriateness_validation['errors'])
        warnings.extend(appropriateness_validation['warnings'])
        suggestions.extend(appropriateness_validation['suggestions'])
        
        # Check for required items (for formal style)
        if 'required_items' in style_rule:
            required_validation = self._validate_required_items(items, style, style_rule)
            errors.extend(required_validation['errors'])
            suggestions.extend(required_validation['suggestions'])
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity=(style_rule.get('severity', ValidationSeverity.LOW) if style_rule else ValidationSeverity.LOW)
        )
    
    def _validate_item_count(self, items: List[Dict[str, Any]], style: str, style_rule: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate item count against style rules"""
        errors = []
        warnings = []
        suggestions = []
        
        item_count = len(items)
        
        # Check maximum items for minimalist
        if 'max_items' in style_rule and item_count > style_rule['max_items']:
            errors.append(f"TOO MANY ITEMS for {style} style: {item_count} items (max {style_rule['max_items']})")
            suggestions.append(f"REMOVE {item_count - style_rule['max_items']} items for authentic {style} look")
        
        # Check minimum items for maximalist
        if 'min_items' in style_rule and item_count < style_rule['min_items']:
            errors.append(f"TOO FEW ITEMS for {style} style: {item_count} items (min {style_rule['min_items']})")
            suggestions.append(f"ADD {style_rule['min_items'] - item_count} accessories or layers for {style} style")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_color_count(self, items: List[Dict[str, Any]], style: str, style_rule: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate color count against style rules"""
        errors = []
        warnings = []
        suggestions = []
        
        if 'color_limit' not in style_rule:
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        colors = [item.get('color', '').lower() for item in items if item.get('color')]
        unique_colors = set(colors)
        color_count = len(unique_colors)
        
        if color_count > style_rule['color_limit']:
            warnings.append(f"TOO MANY COLORS for {style} style: {color_count} colors (limit {style_rule['color_limit']})")
            suggestions.append(f"REDUCE to {style_rule['color_limit']} colors for {style} aesthetic")
        elif color_count < 2 and style != 'minimalist':
            warnings.append(f"TOO FEW COLORS for {style} style: {color_count} colors")
            suggestions.append(f"ADD more color variety for {style} style")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_style_appropriateness(self, items: List[Dict[str, Any]], style: str, style_rule: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate style appropriateness of items"""
        errors = []
        warnings = []
        suggestions = []
        
        inappropriate_items = []
        preferred_items = []
        
        for item in items:
            name = (item.get('name', '') if item else '').lower()
            
            # Check for items to avoid
            if 'avoid_items' in style_rule:
                if any(avoid_term in name for avoid_term in style_rule['avoid_items']):
                    inappropriate_items.append((item.get('name', 'Unknown') if item else 'Unknown'))
            
            # Check for preferred items
            if 'preferred_items' in style_rule:
                if any(preferred_term in name for preferred_term in style_rule['preferred_items']):
                    preferred_items.append((item.get('name', 'Unknown') if item else 'Unknown'))
        
        if inappropriate_items:
            if style_rule.get('severity') == ValidationSeverity.HIGH:
                errors.append(f"INAPPROPRIATE items for {style} style: {inappropriate_items}")
            else:
                warnings.append(f"Consider more {style}-appropriate items: {inappropriate_items}")
            suggestions.append(f"Replace with {style}-style items")
        
        if preferred_items:
            suggestions.append(f"EXCELLENT {style} items: {preferred_items}")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_required_items(self, items: List[Dict[str, Any]], style: str, style_rule: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate required items for specific styles"""
        errors = []
        warnings = []
        suggestions = []
        
        if 'required_items' not in style_rule:
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        required_items = style_rule['required_items']
        item_names = [(item.get('name', '') if item else '').lower() for item in items]
        
        missing_required = []
        for required in required_items:
            if not any(required_term in name for name in item_names for required_term in required.split()):
                missing_required.append(required)
        
        if missing_required:
            errors.append(f"MISSING REQUIRED items for {style} style: {missing_required}")
            suggestions.extend([f"ADD {item} for complete {style} look" for item in missing_required])
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
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
        
        items = (outfit.get('items', []) if outfit else [])
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
        
        items = (outfit.get('items', []) if outfit else [])
        
        # Check for formality mismatches
        formal_items = [item for item in items if self._is_formal_item(item)]
        casual_items = [item for item in items if self._is_casual_item(item)]
        
        if formal_items and casual_items:
            warnings.append(f"Mixed formality levels: formal items {[((item.get('name', 'Unknown') if item else 'Unknown') if item else 'Unknown') for item in formal_items]} with casual items {[((item.get('name', 'Unknown') if item else 'Unknown') if item else 'Unknown') for item in casual_items]}")
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
        
        items = (outfit.get('items', []) if outfit else [])
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
        
        items = (outfit.get('items', []) if outfit else [])
        temp = context.temperature
        
        for item in items:
            material = (item.get('material', '') if item else '').lower()
            name = (item.get('name', '') if item else '').lower()
            
            # Check for inappropriate materials in hot weather
            if temp > 80 and material in ['wool', 'fleece', 'suede']:
                warnings.append(f"Material {material} may be too warm for {temp}°F: {(item.get('name', 'Unknown') if item else 'Unknown')}")
                suggestions.append("Consider lighter materials like cotton or linen for hot weather")
            
            # Check for inappropriate materials in cold weather
            if temp < 50 and material in ['linen', 'silk']:
                warnings.append(f"Material {material} may be too light for {temp}°F: {(item.get('name', 'Unknown') if item else 'Unknown')}")
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
        
        items = (outfit.get('items', []) if outfit else [])
        occasion = context.occasion.lower()
        
        # Check for overly tight or loose items in formal occasions
        if 'formal' in occasion or 'business' in occasion:
            for item in items:
                name = (item.get('name', '') if item else '').lower()
                if 'oversized' in name or 'loose' in name:
                    warnings.append(f"Consider more fitted items for formal occasions: {(item.get('name', 'Unknown') if item else 'Unknown')}")
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
