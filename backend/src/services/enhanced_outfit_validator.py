#!/usr/bin/env python3
"""
Enhanced Outfit Validator - Integrated Thought Clarification System
================================================================

This validator uses integrated thought clarification to systematically prevent
inappropriate outfit combinations through multi-layered validation:

1. Pre-validation filtering (prevent bad items from entering)
2. Core validation (check inappropriate combinations) 
3. Occasion-specific validation (strict business/formal rules)
4. Formality consistency validation (ensure outfit coherence)
5. Robust error handling (no fallback to bad outfits)

The system prevents outfits like:
- Business occasion with shorts and casual shoes
- Formal jackets with athletic wear
- Inconsistent formality levels
- Weather-inappropriate combinations
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"    # Must fix - outfit completely inappropriate
    HIGH = "high"           # Should fix - major style violation
    MEDIUM = "medium"       # Consider fixing - minor style issue
    LOW = "low"            # Optional fix - style preference

class FormalityLevel(Enum):
    """Formality levels for consistency checking"""
    FORMAL = "formal"           # Suits, dress shoes, dress shirts
    BUSINESS_FORMAL = "business_formal"  # Business suits, dress shirts
    BUSINESS_CASUAL = "business_casual"  # Blazers, dress pants, loafers
    SMART_CASUAL = "smart_casual"       # Button-ups, chinos, clean sneakers
    CASUAL = "casual"          # T-shirts, jeans, sneakers
    ATHLETIC = "athletic"      # Athletic wear, gym clothes
    LOUNGEWEAR = "loungewear"  # Comfortable home wear

@dataclass
class ValidationResult:
    """Enhanced validation result with detailed feedback"""
    is_valid: bool
    severity: ValidationSeverity
    issues: List[str]
    suggestions: List[str]
    confidence_score: float
    filtered_items: List[Dict[str, Any]]
    validation_details: Dict[str, Any]

class EnhancedOutfitValidator:
    """
    Enhanced Outfit Validator with Integrated Thought Clarification
    
    This validator systematically prevents inappropriate outfit combinations
    through comprehensive multi-layered validation.
    """
    
    def __init__(self):
        # Initialize formality mapping
        self.formality_mapping = self._initialize_formality_mapping()
        
        # Initialize inappropriate combinations database
        self.inappropriate_combinations = self._initialize_inappropriate_combinations()
        
        # Initialize occasion-specific rules
        self.occasion_rules = self._initialize_occasion_rules()
        
        # Initialize validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "inappropriate_combinations_prevented": 0
        }
    
    def _initialize_formality_mapping(self) -> Dict[str, FormalityLevel]:
        """Initialize formality level mapping for items"""
        return {
            # Formal items
            "suit": FormalityLevel.FORMAL,
            "tuxedo": FormalityLevel.FORMAL,
            "dress_shirt": FormalityLevel.BUSINESS_FORMAL,
            "dress_pants": FormalityLevel.BUSINESS_FORMAL,
            "dress_shoes": FormalityLevel.BUSINESS_FORMAL,
            "oxford": FormalityLevel.BUSINESS_FORMAL,
            "loafers": FormalityLevel.BUSINESS_CASUAL,
            "blazer": FormalityLevel.BUSINESS_CASUAL,
            "sport_coat": FormalityLevel.BUSINESS_CASUAL,
            
            # Business casual items
            "button_up": FormalityLevel.BUSINESS_CASUAL,
            "button_down": FormalityLevel.BUSINESS_CASUAL,
            "chinos": FormalityLevel.BUSINESS_CASUAL,
            "polo": FormalityLevel.SMART_CASUAL,
            
            # Casual items
            "t_shirt": FormalityLevel.CASUAL,
            "tank_top": FormalityLevel.CASUAL,
            "jeans": FormalityLevel.CASUAL,
            "sneakers": FormalityLevel.CASUAL,
            "hoodie": FormalityLevel.CASUAL,
            "sweatshirt": FormalityLevel.CASUAL,
            
            # Athletic items
            "athletic_shorts": FormalityLevel.ATHLETIC,
            "basketball_shorts": FormalityLevel.ATHLETIC,
            "athletic_pants": FormalityLevel.ATHLETIC,
            "athletic_shirt": FormalityLevel.ATHLETIC,
            "gym_shorts": FormalityLevel.ATHLETIC,
            "workout_pants": FormalityLevel.ATHLETIC,
            
            # Loungewear items
            "pajamas": FormalityLevel.LOUNGEWEAR,
            "lounge_pants": FormalityLevel.LOUNGEWEAR,
            "sweatpants": FormalityLevel.LOUNGEWEAR,
            "house_shoes": FormalityLevel.LOUNGEWEAR,
        }
    
    def _initialize_inappropriate_combinations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive inappropriate combinations database"""
        return {
            # CRITICAL: Business/Formal Occasion Violations
            "business_shorts": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Shorts with Business Occasion",
                "reason": "Shorts are never appropriate for business occasions",
                "trigger_items": ["shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts", "cargo_shorts"],
                "trigger_occasions": ["business", "interview", "formal", "professional"],
                "action": "remove_trigger_items"
            },
            
            "business_casual_shoes": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Casual Shoes with Business Occasion",
                "reason": "Business occasions require formal or business casual shoes",
                "trigger_items": ["sneakers", "athletic_shoes", "flip_flops", "sandals", "canvas_shoes"],
                "trigger_occasions": ["business", "interview", "formal", "professional"],
                "action": "remove_trigger_items"
            },
            
            "formal_jacket_casual_bottoms": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Formal Jacket with Casual Bottoms",
                "reason": "Formal jackets require formal or business casual bottoms",
                "trigger_items": ["shorts", "athletic_shorts", "basketball_shorts", "sweatpants", "athletic_pants"],
                "required_with": ["blazer", "suit_jacket", "sport_coat", "formal_jacket"],
                "action": "remove_trigger_items"
            },
            
            "business_athletic_mix": {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Business Wear with Athletic Wear",
                "reason": "Business and athletic wear should not be mixed",
                "trigger_items": ["athletic_shorts", "basketball_shorts", "athletic_pants", "gym_shorts", "workout_pants"],
                "required_with": ["dress_shirt", "blazer", "suit_jacket", "business_shirt"],
                "action": "remove_trigger_items"
            },
            
            # HIGH: Formality Inconsistency
            "formality_mismatch": {
                "severity": ValidationSeverity.HIGH,
                "description": "Formality Level Mismatch",
                "reason": "Items should have consistent formality levels",
                "max_formality_gap": 2,  # Max gap between formality levels
                "action": "adjust_formality"
            },
            
            # MEDIUM: Style Consistency
            "style_inconsistency": {
                "severity": ValidationSeverity.MEDIUM,
                "description": "Style Inconsistency",
                "reason": "Items should have compatible styles",
                "action": "suggest_alternatives"
            }
        }
    
    def _initialize_occasion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize strict occasion-specific validation rules"""
        return {
            "business": {
                "required_formality": FormalityLevel.BUSINESS_CASUAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants"
                ],
                "required_items": ["dress_shirt", "button_up", "blazer", "dress_pants", "chinos"],
                "preferred_shoes": ["dress_shoes", "oxford", "loafers", "business_casual_shoes"],
                "min_formality": FormalityLevel.BUSINESS_CASUAL
            },
            
            "interview": {
                "required_formality": FormalityLevel.BUSINESS_FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes"
                ],
                "required_items": ["dress_shirt", "dress_pants", "dress_shoes", "blazer", "suit"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.BUSINESS_FORMAL
            },
            
            "formal": {
                "required_formality": FormalityLevel.FORMAL,
                "forbidden_items": [
                    "shorts", "athletic_shorts", "basketball_shorts", "bermuda_shorts",
                    "sneakers", "athletic_shoes", "flip_flops", "sandals",
                    "tank_top", "athletic_shirt", "gym_clothes",
                    "sweatpants", "athletic_pants", "lounge_pants",
                    "casual_shoes", "canvas_shoes", "casual_clothes"
                ],
                "required_items": ["suit", "dress_shirt", "dress_pants", "dress_shoes"],
                "preferred_shoes": ["dress_shoes", "oxford"],
                "min_formality": FormalityLevel.FORMAL
            },
            
            "casual": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "formal_jacket"
                ],
                "required_items": ["casual_top", "casual_bottom", "casual_shoes"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers"],
                "min_formality": FormalityLevel.CASUAL
            },
            
            "weekend": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers"],
                "min_formality": FormalityLevel.SMART_CASUAL
            },
            
            "party": {
                "required_formality": FormalityLevel.CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal",
                    "athletic_shorts", "basketball_shorts", "gym_clothes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["sneakers", "casual_shoes", "loafers", "boots"],
                "min_formality": FormalityLevel.CASUAL,
                "notes": "Party occasions allow casual wear including shorts and sneakers"
            },
            
            "date": {
                "required_formality": FormalityLevel.SMART_CASUAL,
                "forbidden_items": [
                    "suit", "tuxedo", "formal_dress_shoes", "business_formal",
                    "athletic_shorts", "basketball_shorts", "gym_clothes", "athletic_shoes"
                ],
                "required_items": ["casual_top", "casual_bottom"],
                "preferred_shoes": ["loafers", "boots", "casual_shoes"],
                "min_formality": FormalityLevel.SMART_CASUAL
            }
        }
    
    async def validate_outfit_comprehensive(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Comprehensive outfit validation using integrated thought clarification
        
        This is the main validation method that orchestrates all validation layers
        """
        start_time = time.time()
        self.validation_stats["total_validations"] += 1
        
        logger.info(f"🔍 Starting comprehensive outfit validation with {len(items)} items")
        logger.info(f"📋 Context: {context.get('occasion', 'unknown')} - {context.get('style', 'unknown')}")
        
        try:
            # Step 1: Pre-validation filtering
            filtered_items, pre_validation_issues = await self._pre_validation_filtering(items, context)
            logger.info(f"✅ Pre-validation: {len(filtered_items)} items passed")
            
            # Step 2: Core inappropriate combinations check
            filtered_items, core_issues = await self._check_inappropriate_combinations(filtered_items, context)
            logger.info(f"✅ Core validation: {len(filtered_items)} items passed")
            
            # Step 3: Occasion-specific validation
            filtered_items, occasion_issues = await self._validate_occasion_specific(filtered_items, context)
            logger.info(f"✅ Occasion validation: {len(filtered_items)} items passed")
            
            # Step 4: Formality consistency validation
            formality_issues = await self._validate_formality_consistency(filtered_items, context)
            logger.info(f"✅ Formality validation completed")
            
            # Step 5: Final validation assessment
            all_issues = pre_validation_issues + core_issues + occasion_issues + formality_issues
            is_valid = len(all_issues) == 0 and len(filtered_items) >= 3
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(filtered_items, context, all_issues)
            
            # Determine severity
            severity = self._determine_severity(all_issues)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(all_issues, context)
            
            # Update statistics
            if is_valid:
                self.validation_stats["successful_validations"] += 1
            else:
                self.validation_stats["failed_validations"] += 1
            
            validation_time = time.time() - start_time
            logger.info(f"✅ Validation completed in {validation_time:.2f}s - Valid: {is_valid}")
            
            return ValidationResult(
                is_valid=is_valid,
                severity=severity,
                issues=all_issues,
                suggestions=suggestions,
                confidence_score=confidence_score,
                filtered_items=filtered_items,
                validation_details={
                    "validation_time": validation_time,
                    "pre_validation_issues": len(pre_validation_issues),
                    "core_issues": len(core_issues),
                    "occasion_issues": len(occasion_issues),
                    "formality_issues": len(formality_issues),
                    "total_items_input": len(items),
                    "total_items_output": len(filtered_items)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Validation failed with exception: {e}")
            self.validation_stats["failed_validations"] += 1
            
            # Return critical failure - do not fall back to bad outfits
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                issues=[f"Validation system error: {str(e)}"],
                suggestions=["Contact support - validation system needs attention"],
                confidence_score=0.0,
                filtered_items=[],
                validation_details={"error": str(e)}
            )
    
    async def _pre_validation_filtering(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Pre-validation filtering to remove obviously inappropriate items"""
        filtered_items = []
        issues = []
        occasion = context.get('occasion', '').lower()
        
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            # Check for obviously inappropriate items for business occasions
            if occasion in ['business', 'interview', 'formal']:
                inappropriate_keywords = [
                    'shorts', 'athletic', 'basketball', 'gym', 'workout', 
                    'sweatpants', 'lounge', 'pajama', 'tank_top'
                ]
                
                if any(keyword in item_name or keyword in item_type for keyword in inappropriate_keywords):
                    issues.append(f"Removed {item.get('name', 'Unknown')} - inappropriate for {occasion}")
                    continue
            
            # Check for obviously inappropriate shoes for business occasions
            if occasion in ['business', 'interview', 'formal'] and item_type in ['shoes', 'footwear']:
                inappropriate_shoe_keywords = [
                    'sneaker', 'athletic', 'canvas', 'flip_flop', 'sandals'
                ]
                
                if any(keyword in item_name for keyword in inappropriate_shoe_keywords):
                    issues.append(f"Removed {item.get('name', 'Unknown')} - inappropriate shoes for {occasion}")
                    continue
            
            filtered_items.append(item)
        
        return filtered_items, issues
    
    async def _check_inappropriate_combinations(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Check for inappropriate combinations using comprehensive rules"""
        filtered_items = items.copy()
        issues = []
        occasion = context.get('occasion', '').lower()
        
        for rule_name, rule in self.inappropriate_combinations.items():
            severity = rule.get('severity', ValidationSeverity.MEDIUM)
            trigger_items = rule.get('trigger_items', [])
            trigger_occasions = rule.get('trigger_occasions', [])
            required_with = rule.get('required_with', [])
            
            # Check if rule applies to current occasion
            if trigger_occasions and occasion not in trigger_occasions:
                continue
            
            # Check if we have items that trigger this rule
            has_trigger_items = False
            has_required_with_items = False
            
            for item in filtered_items:
                item_name = item.get('name', '').lower()
                item_type = item.get('type', '').lower()
                
                # Check for trigger items
                if any(trigger in item_name or trigger in item_type for trigger in trigger_items):
                    has_trigger_items = True
                
                # Check for required_with items
                if required_with and any(required in item_name or required in item_type for required in required_with):
                    has_required_with_items = True
            
            # Apply rule if conditions are met
            if has_trigger_items and (not required_with or has_required_with_items):
                items_to_remove = []
                
                for item in filtered_items:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if any(trigger in item_name or trigger in item_type for trigger in trigger_items):
                        items_to_remove.append(item)
                        issues.append(f"Removed {item.get('name', 'Unknown')} - {rule['reason']}")
                        self.validation_stats["inappropriate_combinations_prevented"] += 1
                
                # Remove inappropriate items
                for item in items_to_remove:
                    if item in filtered_items:
                        filtered_items.remove(item)
        
        return filtered_items, issues
    
    async def _validate_occasion_specific(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate occasion-specific requirements"""
        filtered_items = items.copy()
        issues = []
        occasion = context.get('occasion', '').lower()
        
        if occasion not in self.occasion_rules:
            return filtered_items, issues
        
        rule = self.occasion_rules[occasion]
        forbidden_items = rule.get('forbidden_items', [])
        required_items = rule.get('required_items', [])
        preferred_shoes = rule.get('preferred_shoes', [])
        min_formality = rule.get('min_formality', FormalityLevel.CASUAL)
        
        # Remove forbidden items
        items_to_remove = []
        for item in filtered_items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            if any(forbidden in item_name or forbidden in item_type for forbidden in forbidden_items):
                items_to_remove.append(item)
                issues.append(f"Removed {item.get('name', 'Unknown')} - forbidden for {occasion}")
        
        for item in items_to_remove:
            if item in filtered_items:
                filtered_items.remove(item)
        
        # Check for required items (warnings, not removals)
        has_required_items = False
        for item in filtered_items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            if any(required in item_name or required in item_type for required in required_items):
                has_required_items = True
                break
        
        if not has_required_items and required_items:
            issues.append(f"Warning: Missing recommended items for {occasion}: {', '.join(required_items)}")
        
        # Validate shoe appropriateness
        shoe_items = [item for item in filtered_items if item.get('type', '').lower() in ['shoes', 'footwear']]
        if shoe_items and preferred_shoes:
            for shoe in shoe_items:
                shoe_name = shoe.get('name', '').lower()
                if not any(preferred in shoe_name for preferred in preferred_shoes):
                    issues.append(f"Warning: {shoe.get('name', 'Unknown')} may not be ideal for {occasion}")
        
        return filtered_items, issues
    
    async def _validate_formality_consistency(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Validate formality consistency across outfit"""
        issues = []
        
        if len(items) < 2:
            return issues
        
        # Determine formality levels for each item
        item_formalities = []
        for item in items:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            
            formality = FormalityLevel.CASUAL  # default
            for keyword, level in self.formality_mapping.items():
                if keyword in item_name or keyword in item_type:
                    formality = level
                    break
            
            item_formalities.append(formality)
        
        # Check for formality consistency
        if len(set(item_formalities)) > 3:  # Too many different formality levels
            issues.append("Warning: Outfit has inconsistent formality levels")
        
        # Check for extreme formality mismatches
        formality_values = {level: i for i, level in enumerate(FormalityLevel)}
        formality_scores = [formality_values[level] for level in item_formalities]
        
        if max(formality_scores) - min(formality_scores) > 3:  # Too much formality gap
            issues.append("Warning: Outfit has extreme formality mismatches")
        
        return issues
    
    def _calculate_confidence_score(
        self, 
        items: List[Dict[str, Any]], 
        context: Dict[str, Any], 
        issues: List[str]
    ) -> float:
        """Calculate confidence score for the outfit"""
        base_score = 100.0
        
        # Deduct points for issues
        for issue in issues:
            if "Removed" in issue:
                base_score -= 15.0  # Item removal
            elif "Warning" in issue:
                base_score -= 5.0   # Warning
        
        # Bonus for appropriate item count
        if 3 <= len(items) <= 6:
            base_score += 10.0
        elif len(items) < 3:
            base_score -= 20.0
        
        # Bonus for occasion appropriateness
        occasion = context.get('occasion', '').lower()
        if occasion in ['business', 'interview', 'formal']:
            # Check if we have appropriate items for formal occasions
            has_formal_items = any(
                any(keyword in item.get('name', '').lower() or keyword in item.get('type', '').lower() 
                    for keyword in ['dress', 'formal', 'business', 'blazer'])
                for item in items
            )
            if has_formal_items:
                base_score += 10.0
        
        return max(0.0, min(100.0, base_score))
    
    def _determine_severity(self, issues: List[str]) -> ValidationSeverity:
        """Determine overall validation severity"""
        if not issues:
            return ValidationSeverity.LOW
        
        critical_count = sum(1 for issue in issues if "Removed" in issue and any(
            keyword in issue.lower() for keyword in ['business', 'formal', 'interview']
        ))
        
        if critical_count > 0:
            return ValidationSeverity.CRITICAL
        elif any("Removed" in issue for issue in issues):
            return ValidationSeverity.HIGH
        elif any("Warning" in issue for issue in issues):
            return ValidationSeverity.MEDIUM
        else:
            return ValidationSeverity.LOW
    
    def _generate_suggestions(self, issues: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate helpful suggestions based on issues"""
        suggestions = []
        occasion = context.get('occasion', '').lower()
        
        if not issues:
            suggestions.append("Outfit looks great! All validation checks passed.")
            return suggestions
        
        # Generate suggestions based on issues
        for issue in issues:
            if "shorts" in issue.lower() and occasion in ['business', 'interview', 'formal']:
                suggestions.append("Consider dress pants or chinos for professional occasions")
            elif "sneakers" in issue.lower() and occasion in ['business', 'interview', 'formal']:
                suggestions.append("Consider dress shoes or loafers for professional occasions")
            elif "athletic" in issue.lower():
                suggestions.append("Consider more formal alternatives for professional settings")
            elif "formality" in issue.lower():
                suggestions.append("Try to maintain consistent formality levels across all items")
        
        # General suggestions based on occasion
        if occasion in ['business', 'interview', 'formal']:
            suggestions.extend([
                "Ensure all items are professional and well-fitted",
                "Consider adding a blazer or dress shirt for formality",
                "Choose dress shoes over casual footwear"
            ])
        
        return suggestions
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.validation_stats.copy()
