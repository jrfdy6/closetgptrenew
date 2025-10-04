"""
Dynamic Healing Context for Outfit Generation Fallback System

This module provides a dynamic context system that learns from fallback failures
and adapts strategies based on what didn't work in previous attempts.
"""

import time
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

class ErrorType(Enum):
    """Types of errors that can occur during outfit generation."""
    WEATHER_MISMATCH = "weather_mismatch"
    DUPLICATE_ITEMS = "duplicate_items"
    STYLE_CONFLICT = "style_conflict"
    LAYERING_ISSUE = "layering_issue"
    LAYERING_CONFLICT = "layering_conflict"
    OCCASION_MISMATCH = "occasion_mismatch"
    INSUFFICIENT_ITEMS = "insufficient_items"
    VALIDATION_FAILURE = "validation_failure"
    HEALING_EXCEPTION = "healing_exception"

class FixType(Enum):
    """Types of fixes that can be attempted."""
    WEATHER_FIX = "weather_fix"
    DUPLICATE_FIX = "duplicate_fix"
    STYLE_FIX = "style_fix"
    LAYERING_FIX = "layering_fix"
    ITEM_REPLACEMENT = "item_replacement"
    SCRATCH_GENERATION = "scratch_generation"
    RELAXED_VALIDATION = "relaxed_validation"

@dataclass
class ErrorRecord:
    """Record of an error encountered during healing."""
    error_type: ErrorType
    details: str
    pass_number: int
    timestamp: float
    item_ids: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FixAttempt:
    """Record of a fix attempt during healing."""
    fix_type: FixType
    success: bool
    details: Optional[Dict[str, Any]]
    pass_number: int
    timestamp: float
    items_affected: List[str] = field(default_factory=list)

@dataclass
class RuleTrigger:
    """Record of a rule that was triggered during healing."""
    rule_name: str
    reason: str
    pass_number: int
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)

class DynamicHealingContext:
    """
    Dynamic healing context that learns from fallback failures and adapts strategies.
    
    This class tracks:
    - Errors encountered during healing
    - Items that have been removed/failed
    - Rules that were triggered and failed
    - Fix attempts and their success/failure
    - Learning history for debugging
    """
    
    def __init__(self, base_context: Dict[str, Any]):
        self.base_context = base_context
        self.errors_seen: List[ErrorRecord] = []
        self.items_removed: Set[str] = set()
        self.rules_triggered: Dict[str, List[RuleTrigger]] = {}
        self.fixes_attempted: List[FixAttempt] = []
        self.healing_pass: int = 1
        self.learning_history: List[Dict[str, Any]] = []
        self.session_id: str = f"healing_{int(time.time())}"
        
        # Track specific learning patterns
        self.weather_learning: Dict[str, Set[str]] = {}  # temperature -> materials to avoid
        self.style_learning: Dict[str, Set[str]] = {}    # style -> conflicting styles
        self.category_learning: Dict[str, Set[str]] = {} # category -> problematic items
        
    def add_error_seen(self, error_type: ErrorType, details: str, item_ids: List[str] = None, context: Dict[str, Any] = None):
        """Track an error we've encountered during healing."""
        error_record = ErrorRecord(
            error_type=error_type,
            details=details,
            pass_number=self.healing_pass,
            timestamp=time.time(),
            item_ids=item_ids or [],
            context=context or {}
        )
        self.errors_seen.append(error_record)
        
        # Add to learning history
        self.learning_history.append({
            'action': 'error_seen',
            'error_type': error_type.value,
            'details': details,
            'pass': self.healing_pass,
            'timestamp': time.time()
        })
        
        print(f"🔍 Error recorded: {error_type.value} - {details}")
    
    def add_item_removed(self, item_id: str, reason: str, item_data: Dict[str, Any] = None):
        """Mark an item as removed to avoid retrying it in future passes."""
        self.items_removed.add(item_id)
        
        # Extract learning from item removal
        if item_data:
            self._extract_learning_from_item_removal(item_id, reason, item_data)
        
        self.learning_history.append({
            'action': 'item_removed',
            'item_id': item_id,
            'reason': reason,
            'pass': self.healing_pass,
            'timestamp': time.time(),
            'item_data': item_data
        })
        
        print(f"🚫 Item removed: {item_id} - {reason}")
    
    def add_rule_triggered(self, rule_name: str, failure_reason: str, context: Dict[str, Any] = None):
        """Track which rules failed and why."""
        if rule_name not in self.rules_triggered:
            self.rules_triggered[rule_name] = []
        
        rule_trigger = RuleTrigger(
            rule_name=rule_name,
            reason=failure_reason,
            pass_number=self.healing_pass,
            timestamp=time.time(),
            context=context or {}
        )
        self.rules_triggered[rule_name].append(rule_trigger)
        
        # Extract learning from rule failure
        self._extract_learning_from_rule_failure(rule_name, failure_reason, context)
        
        self.learning_history.append({
            'action': 'rule_triggered',
            'rule_name': rule_name,
            'reason': failure_reason,
            'pass': self.healing_pass,
            'timestamp': time.time(),
            'context': context
        })
        
        print(f"⚡ Rule triggered: {rule_name} - {failure_reason}")
    
    def add_fix_attempted(self, fix_type: FixType, success: bool, details: Optional[Dict[str, Any]] = None, items_affected: List[str] = None):
        """Track a fix attempt and its outcome."""
        fix_attempt = FixAttempt(
            fix_type=fix_type,
            success=success,
            details=details,
            pass_number=self.healing_pass,
            timestamp=time.time(),
            items_affected=items_affected or []
        )
        self.fixes_attempted.append(fix_attempt)
        
        self.learning_history.append({
            'action': 'fix_attempted',
            'fix_type': fix_type.value,
            'success': success,
            'details': details,
            'pass': self.healing_pass,
            'timestamp': time.time(),
            'items_affected': items_affected
        })
        
        status = "✅" if success else "❌"
        print(f"{status} Fix attempted: {fix_type.value} - {'Success' if success else 'Failed'}")
    
    def increment_pass(self):
        """Move to the next healing pass."""
        self.healing_pass += 1
        print(f"🔄 Moving to healing pass {self.healing_pass}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the healing context for logging."""
        return {
            'session_id': self.session_id,
            'errors_seen': [self._error_to_dict(e) for e in self.errors_seen],
            'items_removed': list(self.items_removed),
            'rules_triggered': {k: [self._rule_to_dict(r) for r in v] for k, v in self.rules_triggered.items()},
            'fixes_attempted': [self._fix_to_dict(f) for f in self.fixes_attempted],
            'healing_pass': self.healing_pass,
            'learning_history': self.learning_history,
            'weather_learning': {k: list(v) for k, v in self.weather_learning.items()},
            'style_learning': {k: list(v) for k, v in self.style_learning.items()},
            'category_learning': {k: list(v) for k, v in self.category_learning.items()}
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the healing context."""
        return {
            'total_errors': len(self.errors_seen),
            'total_items_removed': len(self.items_removed),
            'total_rules_triggered': len(self.rules_triggered),
            'total_fixes_attempted': len(self.fixes_attempted),
            'healing_passes': self.healing_pass,
            'successful_fixes': len([f for f in self.fixes_attempted if f.success]),
            'failed_fixes': len([f for f in self.fixes_attempted if not f.success])
        }
    
    def should_exclude_item(self, item_id: str, item_data: Dict[str, Any] = None) -> bool:
        """Check if an item should be excluded based on learning."""
        # Direct item exclusion
        if item_id in self.items_removed:
            return True
        
        # Weather-based exclusion
        if item_data and 'weather' in self.base_context:
            temperature = self.base_context['weather'].get('temperature', 70)
            temp_key = f"{temperature//10*10}-{(temperature//10*10)+10}"  # e.g., "70-80"
            
            if temp_key in self.weather_learning:
                material = (item_data.get('material', '') if item_data else '').lower()
                if material in self.weather_learning[temp_key]:
                    return True
        
        # Style-based exclusion
        if item_data and 'style' in self.base_context:
            target_style = self.base_context['style']
            if target_style and target_style in self.style_learning:
                item_style = (item_data.get('style', '') if item_data else '').lower()
                if item_style in self.style_learning[target_style]:
                    return True
        
        return False
    
    def get_excluded_materials_for_temperature(self, temperature: float) -> Set[str]:
        """Get materials that should be excluded for a given temperature."""
        temp_key = f"{temperature//10*10}-{(temperature//10*10)+10}"
        return self.(weather_learning.get(temp_key, set() if weather_learning else set())
    
    def get_excluded_styles_for_style(self, target_style: str) -> Set[str]:
        """Get styles that should be excluded for a given target style."""
        return self.(style_learning.get(target_style, set() if style_learning else set())
    
    def _extract_learning_from_item_removal(self, item_id: str, reason: str, item_data: Dict[str, Any]):
        """Extract learning patterns from item removal."""
        # Weather-based learning
        if "hot" in reason.lower() or "temperature" in reason.lower():
            if 'weather' in self.base_context:
                temperature = self.base_context['weather'].get('temperature', 70)
                temp_key = f"{temperature//10*10}-{(temperature//10*10)+10}"
                
                if temp_key not in self.weather_learning:
                    self.weather_learning[temp_key] = set()
                
                material = (item_data.get('material', '') if item_data else '').lower()
                if material:
                    self.weather_learning[temp_key].add(material)
        
        # Style-based learning
        if "style" in reason.lower() or "conflict" in reason.lower():
            if 'style' in self.base_context:
                target_style = self.base_context['style']
                if target_style:
                    if target_style not in self.style_learning:
                        self.style_learning[target_style] = set()
                    
                    item_style = (item_data.get('style', '') if item_data else '').lower()
                    if item_style:
                        self.style_learning[target_style].add(item_style)
        
        # Category-based learning
        category = (item_data.get('type', '') if item_data else '').lower()
        if category:
            if category not in self.category_learning:
                self.category_learning[category] = set()
            self.category_learning[category].add(item_id)
    
    def _extract_learning_from_rule_failure(self, rule_name: str, failure_reason: str, context: Dict[str, Any]):
        """Extract learning patterns from rule failures."""
        if rule_name == 'weather' and context:
            temperature = (context.get('temperature', 70) if context else 70)
            temp_key = f"{temperature//10*10}-{(temperature//10*10)+10}"
            
            if temp_key not in self.weather_learning:
                self.weather_learning[temp_key] = set()
            
            # Extract materials from failure reason
            if 'wool' in failure_reason.lower():
                self.weather_learning[temp_key].add('wool')
            if 'fleece' in failure_reason.lower():
                self.weather_learning[temp_key].add('fleece')
            if 'sweater' in failure_reason.lower():
                self.weather_learning[temp_key].add('sweater')
    
    def _error_to_dict(self, error: ErrorRecord) -> Dict[str, Any]:
        """Convert ErrorRecord to dictionary."""
        return {
            'error_type': error.error_type.value,
            'details': error.details,
            'pass_number': error.pass_number,
            'timestamp': error.timestamp,
            'item_ids': error.item_ids,
            'context': error.context
        }
    
    def _rule_to_dict(self, rule: RuleTrigger) -> Dict[str, Any]:
        """Convert RuleTrigger to dictionary."""
        return {
            'rule_name': rule.rule_name,
            'reason': rule.reason,
            'pass_number': rule.pass_number,
            'timestamp': rule.timestamp,
            'context': rule.context
        }
    
    def _fix_to_dict(self, fix: FixAttempt) -> Dict[str, Any]:
        """Convert FixAttempt to dictionary."""
        return {
            'fix_type': fix.fix_type.value,
            'success': fix.success,
            'details': fix.details,
            'pass_number': fix.pass_number,
            'timestamp': fix.timestamp,
            'items_affected': fix.items_affected
        } 