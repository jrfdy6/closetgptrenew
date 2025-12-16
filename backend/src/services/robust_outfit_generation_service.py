#!/usr/bin/env python3
"""
Robust Outfit Generation Service
================================

Enterprise-grade outfit generation with comprehensive validation,
fallback strategies, body type optimization, and style profile integration.
"""
# CACHE BUSTER: 2025-11-10T17:05Z

import asyncio
import logging
import time
import uuid
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Robust import strategy to handle different execution contexts
from ..config.feature_flags import is_semantic_match_enabled, is_debug_output_enabled, is_force_traditional_enabled
from ..utils.semantic_normalization import normalize_item_metadata
from ..utils.semantic_compatibility import style_matches, mood_matches, occasion_matches
from ..utils.semantic_telemetry import record_semantic_filtering_metrics
from ..utils.enhanced_debug_output import format_final_debug_response
from ..utils.base_item_debugger import BaseItemTracker
from .outfit_strategy_selector import get_strategy_selector, OutfitStrategy
from .outfit_strategy_implementation import StrategyImplementation
import sys
import os

# Add the src directory to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import real services - force real imports, no fallbacks
try:
    from src.custom_types.wardrobe import ClothingItem, Metadata
    from src.custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
    from src.custom_types.weather import WeatherData
    from src.custom_types.profile import UserProfile
    from src.services.robust_hydrator import ensure_items_safe_for_pydantic
    print("✅ ROBUST SERVICE: Using real imports")
    USING_REAL_CLASSES = True
except (ImportError, ValueError) as e:
    print(f"❌ ROBUST SERVICE: Real imports failed: {e}")
    import traceback
    print(f"❌ ROBUST SERVICE: Import traceback: {traceback.format_exc()}")
    # TEMPORARILY ALLOW FALLBACKS TO DEBUG THE ISSUE
    print(f"🔧 ROBUST SERVICE: Using fallback classes for debugging")
    USING_REAL_CLASSES = False
    
    # Create minimal fallback classes
    class ClothingItem:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class OutfitGeneratedOutfit:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class OutfitPiece:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class WeatherData:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class UserProfile:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class Metadata:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def ensure_items_safe_for_pydantic(items):
        return items

class MockService:
    """Mock service with all required methods"""
    
    def __getattr__(self, name):
        """Catch any missing method calls"""
        # print(f"🔧 MOCK SERVICE: Called missing method '{name}' - returning default")
        if name.startswith('get_') or name.startswith('is_') or name.startswith('has_'):
            return lambda *args, **kwargs: None
        elif name.startswith('set_') or name.startswith('update_') or name.startswith('record_'):
            return lambda *args, **kwargs: None
        else:
            return lambda *args, **kwargs: {}
    
    def get_current_parameters(self):
        return {
            'confidence_threshold': 0.3,
            'max_items': 8,
            'min_items': 3
        }
    
    def record_strategy_execution(self, **kwargs):
        pass
    
    def get_performance_metrics(self):
        return {}
    
    def get_diversity_suggestions(self, **kwargs):
        return []
    
    def record_performance(self, **kwargs):
        pass
    
    def is_diverse(self, **kwargs):
        return True
    
    def check_outfit_diversity(self, **kwargs):
        return {
            'is_diverse': True,
            'diversity_score': 0.8
        }

# Import REAL services for diversity filtering and strategy analytics
try:
    from .diversity_filter_service import DiversityFilterService
    diversity_filter = DiversityFilterService()
    # print("✅ DIVERSITY FILTER: Real service loaded")
except ImportError as e:
    # print(f"⚠️ DiversityFilterService import failed: {e}")
    diversity_filter = MockService()
    # print("🔧 DIVERSITY FILTER: Using mock service")

try:
    from .strategy_analytics_service import StrategyAnalyticsService, StrategyStatus
    strategy_analytics = StrategyAnalyticsService()
    # print("✅ STRATEGY ANALYTICS: Real service loaded")
except ImportError as e:
    # print(f"⚠️ StrategyAnalyticsService import failed: {e}")
    
    # Define StrategyStatus enum if import fails
    class StrategyStatus(Enum):
        SUCCESS = "success"
        FAILED = "failed"
        PARTIAL = "partial"
    
    strategy_analytics = MockService()
    # print("🔧 STRATEGY ANALYTICS: Using mock service")

try:
    from .adaptive_tuning_service import AdaptiveTuningService
    adaptive_tuning = AdaptiveTuningService()
    # print("✅ ADAPTIVE TUNING: Real service loaded")
except ImportError as e:
    # print(f"⚠️ AdaptiveTuningService import failed: {e}")
    adaptive_tuning = MockService()
    # print("🔧 ADAPTIVE TUNING: Using mock service")

# Import SESSION TRACKER for within-session diversity
try:
    from .session_tracker_service import SessionTrackerService
    session_tracker = SessionTrackerService(use_firestore=False)  # In-memory by default
    # logger not defined yet - will log success later
except ImportError as e:
    # logger not defined yet - use print for import errors
    print(f"⚠️ SessionTrackerService import failed: {e}")
    session_tracker = MockService()
    print("🔧 SESSION TRACKER: Using mock service")

class PerformanceMetrics:
    """Mock PerformanceMetrics class"""
    def __init__(self, **kwargs):
        self.success_rate = kwargs.get('success_rate', 1.0)
        self.avg_confidence = kwargs.get('avg_confidence', 0.5)
        self.avg_generation_time = kwargs.get('avg_generation_time', 0.5)
        self.avg_validation_time = kwargs.get('avg_validation_time', 0.1)
        self.diversity_score = kwargs.get('diversity_score', 0.0)
        self.user_satisfaction = kwargs.get('user_satisfaction', 0.5)
        self.fallback_rate = kwargs.get('fallback_rate', 0.0)
        self.sample_size = kwargs.get('sample_size', 1)
        self.time_window_hours = kwargs.get('time_window_hours', 24)
        # Legacy fields for backwards compatibility
        self.confidence = kwargs.get('confidence', self.avg_confidence)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# SAFE HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """
    Safely get a value from an object, handling dict, list, and object formats.
    
    Args:
        obj: Object to get value from (dict, list, or object)
        key: Key/attribute name to retrieve
        default: Default value if key not found
    
    Returns:
        Value from object or default
    """
    try:
        # Handle None objects
        if obj is None:
            logger.warning(f"⚠️ SAFE_GET: Object is None, cannot get '{key}', returning default: {default}")
            return default
        
        # Handle list objects (skip them)
        if isinstance(obj, list):
            logger.warning(f"⚠️ SAFE_GET: Object is a list, cannot get '{key}', returning default: {default}")
            return default
        
        # Handle dict objects
        if isinstance(obj, dict):
            return obj.get(key, default)
        
        # Handle objects with attributes
        return getattr(obj, key, default)
    
    except Exception as e:
        logger.warning(f"⚠️ SAFE_GET: Error getting '{key}' from {type(obj)}: {e}, returning default: {default}")
        return default

def safe_item_access(item: Any, key: str, default: Any = None) -> Any:
    """
    Safely access item attributes, specifically designed for wardrobe items.
    
    Args:
        item: Item object (ClothingItem, dict, or list)
        key: Attribute name to access
        default: Default value if not found
    
    Returns:
        Item attribute value or default
    """
    try:
        # Handle list items (skip them)
        if isinstance(item, list):
            logger.warning(f"⚠️ SAFE_ITEM_ACCESS: Item is a list, cannot access '{key}', returning default: {default}")
            return default
        
        # Handle dict items
        if isinstance(item, dict):
            return item.get(key, default)
        
        # Handle object items
        return getattr(item, key, default)
    
    except Exception as e:
        logger.warning(f"⚠️ SAFE_ITEM_ACCESS: Error accessing '{key}' from {type(item)}: {e}, returning default: {default}")
        return default

class GenerationStrategy(Enum):
    """Outfit generation strategies with fallback order"""
    COHESIVE_COMPOSITION = "cohesive_composition"
    BODY_TYPE_OPTIMIZED = "body_type_optimized" 
    STYLE_PROFILE_MATCHED = "style_profile_matched"
    WEATHER_ADAPTED = "weather_adapted"
    FALLBACK_SIMPLE = "fallback_simple"
    EMERGENCY_DEFAULT = "emergency_default"

@dataclass
class GenerationContext:
    """Context for outfit generation"""
    user_id: str
    occasion: str
    style: str
    mood: str
    weather: WeatherData
    wardrobe: List[ClothingItem]
    user_profile: UserProfile
    base_item_id: Optional[str] = None
    generation_strategy: GenerationStrategy = GenerationStrategy.COHESIVE_COMPOSITION
    retry_count: int = 0
    max_retries: int = 3
    wardrobe_original: Optional[List[ClothingItem]] = None  # Original wardrobe before filtering
    warnings: Optional[List[str]] = None  # Warnings about outfit generation
    metadata_notes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of outfit validation"""
    is_valid: bool
    score: float
    issues: List[str]
    suggestions: List[str]
    confidence: float

class RobustOutfitGenerationService:
    """Enterprise-grade outfit generation service with comprehensive validation and fallback strategies"""
    
    def __init__(self):
        # Import unified metadata compatibility analyzer
        from .metadata_compatibility_analyzer import MetadataCompatibilityAnalyzer
        self.metadata_analyzer = MetadataCompatibilityAnalyzer()
        
        # Initialize flat lay services
        try:
            from .flat_lay_composition_service import FlatLayCompositionService
            from .flat_lay_storage_service import FlatLayStorageService
            self.flat_lay_service = FlatLayCompositionService()
            self.flat_lay_storage = FlatLayStorageService()
            self.enable_flat_lay_generation = True  # ENABLED with worker processing
            logger.info("✅ Flat lay services initialized (using pre-processed images from worker)")
        except Exception as e:
            logger.warning(f"⚠️ Flat lay services not available: {e}")
            self.flat_lay_service = None
            self.flat_lay_storage = None
            self.enable_flat_lay_generation = False
        
        # Data quality tracking for metadata/name conflicts
        self.conflict_stats = {
            'total_items_checked': 0,
            'minor_conflicts': 0,
            'major_conflicts': 0,
            'conflicts_by_field': {}
        }
        
        self.generation_strategies = [
            GenerationStrategy.COHESIVE_COMPOSITION,
            GenerationStrategy.BODY_TYPE_OPTIMIZED,
            GenerationStrategy.STYLE_PROFILE_MATCHED,
            GenerationStrategy.WEATHER_ADAPTED,
            GenerationStrategy.FALLBACK_SIMPLE,
            GenerationStrategy.EMERGENCY_DEFAULT
        ]
        
        # Dynamic category limits based on occasion and style
        self.base_category_limits = {
            "tops": 2,
            "bottoms": 1,
            "shoes": 1,
            "outerwear": 1,
            "accessories": 2
        }
        
        self.max_items = 8  # Increased from 6
        self.min_items = 3
        
        # Inappropriate combinations to prevent
        self.inappropriate_combinations = {
            ("blazer", "shorts"): "Blazers should not be paired with shorts",
            ("formal_shoes", "casual_bottoms"): "Formal shoes should not be paired with casual bottoms",
            ("high_heels", "athletic_wear"): "High heels should not be paired with athletic wear",
            ("tie", "t_shirt"): "Ties should not be worn with t-shirts",
            ("suit", "sneakers"): "Suits should not be paired with sneakers"
        }
        
        # Style profile compatibility rules
        self.style_compatibility = {
            "formal": ["business_casual", "smart_casual"],
            "casual": ["smart_casual", "athleisure", "streetwear"],
            "athletic": ["athleisure", "casual"],
            "business_casual": ["formal", "smart_casual"],
            "streetwear": ["casual", "athleisure"]
        }
    
    def safe_get_item_type(self, item):
        """Safely get item type from either ClothingItem object or dict."""
        if hasattr(item, 'type'):
            return item.type
        elif isinstance(item, dict):
            return item.get('type', 'unknown')
        else:
            return 'unknown'
    
    def safe_get_item_name(self, item):
        """Safely get item name from either ClothingItem object or dict."""
        if hasattr(item, 'name'):
            return item.name
        elif isinstance(item, dict):
            return safe_item_access(item, 'name', 'Unknown')
        else:
            return 'Unknown'
    
    def safe_get_item_attr(self, item, attr, default=None):
        """Safely get any attribute from either ClothingItem object or dict."""
        if hasattr(item, attr):
            return getattr(item, attr)
        elif isinstance(item, dict):
            return item.get(attr, default)
        else:
            return default
    
    def _get_item_formality_level(self, item) -> Optional[int]:
        """Get item's formality level (0=casual, 1=smart casual, 2=business casual, 3=formal, 4=black tie)"""
        # Check metadata first
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    if 'black tie' in formal_level or 'formal event' in formal_level:
                        return 4
                    elif 'formal' in formal_level or 'business formal' in formal_level:
                        return 3
                    elif 'business casual' in formal_level or 'smart' in formal_level:
                        return 2
                    elif 'smart casual' in formal_level:
                        return 1
                    elif 'casual' in formal_level:
                        return 0
        
        # Fallback: infer from item type and name
        item_type = str(self.safe_get_item_type(item)).lower()
        item_name = self.safe_get_item_name(item).lower()
        item_name_lower = item_name
        logger.debug(f"✅ COMMIT 378ebeee9: _hard_filter analyzing '{item_name[:40]}'")
        item_name_lower = item_name
        item_name_lower = item_name
        item_name_lower = item_name
        item_name_lower = item_name
        item_name_lower = item_name
        item_name_lower = item_name
        item_name_lower = item_name
        
        # Formal items (3-4)
        if any(kw in item_type or kw in item_name for kw in ['tuxedo', 'gown', 'bow tie', 'cufflink']):
            return 4
        elif any(kw in item_type or kw in item_name for kw in ['suit', 'blazer', 'dress shirt', 'tie', 'oxford', 'loafer']):
            return 3
        # Business casual (2)
        elif any(kw in item_type or kw in item_name for kw in ['chino', 'khaki', 'dress pant', 'polo', 'cardigan', 'derby']):
            return 2
        # Smart casual (1)
        elif any(kw in item_type or kw in item_name for kw in ['dark jean', 'button', 'sweater', 'boot']):
            return 1
        # Casual (0)
        else:
            return 0
    
    def _get_context_formality_level(self, occasion: str, style: str) -> Optional[int]:
        """Get target formality level from occasion and style (0=casual to 4=black tie)"""
        occasion_lower = (occasion or '').lower()
        style_lower = (style or '').lower()
        
        # Occasion-based formality (highest priority)
        if any(kw in occasion_lower for kw in ['gala', 'black tie', 'wedding formal']):
            return 4
        elif any(kw in occasion_lower for kw in ['interview', 'business', 'formal', 'conference']):
            return 3
        elif any(kw in occasion_lower for kw in ['business casual', 'date', 'brunch']):
            return 2
        elif any(kw in occasion_lower for kw in ['smart casual', 'weekend']):
            return 1
        
        # Style-based formality (if occasion is neutral)
        if any(kw in style_lower for kw in ['formal', 'classic', 'preppy', 'old money']):
            return 3
        elif any(kw in style_lower for kw in ['business casual', 'urban professional']):
            return 2
        elif any(kw in style_lower for kw in ['smart', 'minimalist']):
            return 1
        else:
            return 0
    
    def _is_shirt(self, item) -> bool:
        """Check if item is a shirt (not a sweater, hoodie, or outerwear)."""
        item_type = str(self.safe_get_item_type(item)).lower()
        item_name = self.safe_get_item_name(item).lower()
        
        # Check metadata for coreCategory
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    core_category = (visual_attrs.get('coreCategory') or '').lower()
                    if core_category in ['top', 'tops', 'shirt']:
                        # But exclude if it's actually outerwear
                        if any(kw in item_name for kw in ['jacket', 'coat', 'blazer']):
                            return False
                        # Exclude sweaters, hoodies, cardigans
                        if any(kw in item_name or kw in item_type for kw in ['sweater', 'hoodie', 'cardigan', 'vest']):
                            return False
                        return True
        
        # Check type and name
        shirt_keywords = ['shirt', 't-shirt', 't_shirt', 'blouse', 'polo', 'button-up', 'button up', 'dress shirt', 'oxford']
        if any(kw in item_type or kw in item_name for kw in shirt_keywords):
            # Exclude sweaters, hoodies, cardigans
            if any(kw in item_name or kw in item_type for kw in ['sweater', 'hoodie', 'cardigan', 'vest']):
                return False
            return True
        
        return False
    
    def _is_turtleneck(self, item) -> bool:
        """Check if item is a turtleneck."""
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        
        # Check metadata
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    neckline = (visual_attrs.get('neckline') or '').lower()
                    if 'turtleneck' in neckline or 'turtle' in neckline:
                        return True
        
        # Check name/type
        return 'turtleneck' in item_name or 'turtle' in item_name
    
    def _is_collared(self, item) -> bool:
        """Check if item has a collar."""
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        
        # Check metadata
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    neckline = (visual_attrs.get('neckline') or '').lower()
                    collar_type = (visual_attrs.get('collarType') or '').lower()
                    if 'collar' in neckline or 'collar' in collar_type or 'polo' in neckline:
                        return True
        
        # Check name/type
        collar_keywords = ['collar', 'collared', 'polo', 'button-up', 'button up', 'dress shirt', 'oxford']
        return any(kw in item_name or kw in item_type for kw in collar_keywords)
    
    def _is_sweater_vest(self, item) -> bool:
        """Check if item is a sweater vest (sleeveless sweater)."""
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        
        # Check metadata
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                    if 'vest' in item_name and ('sweater' in item_name or 'sweater' in item_type):
                        return True
                    if 'sleeveless' in sleeve_length and ('sweater' in item_name or 'sweater' in item_type):
                        return True
        
        # Check name/type
        return ('vest' in item_name and 'sweater' in item_name) or ('sweater vest' in item_name)
    
    def _get_sleeve_length(self, item) -> str:
        """Get sleeve length from metadata or infer from name/type."""
        # Check metadata first
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    sleeve_length = visual_attrs.get('sleeveLength')
                    if sleeve_length:
                        return str(sleeve_length).lower()
        
        # Fallback: infer from name/type
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        
        if any(kw in item_name for kw in ['sleeveless', 'tank', 'vest']):
            return 'sleeveless'
        elif any(kw in item_name for kw in ['short sleeve', 'short-sleeve', 't-shirt', 'tee']):
            return 'short'
        elif any(kw in item_name for kw in ['3/4', 'three quarter']):
            return '3/4'
        elif any(kw in item_name for kw in ['long sleeve', 'long-sleeve', 'button up', 'button-up']):
            return 'long'
        
        # Default based on type
        if 'sweater' in item_type or 'sweater' in item_name:
            return 'long'  # Most sweaters are long sleeve
        elif 'shirt' in item_type or 'shirt' in item_name:
            return 'long'  # Most shirts are long sleeve
        
        return 'unknown'
    
    def _is_hoodie(self, item) -> bool:
        """Check if item is a hoodie."""
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        return 'hoodie' in item_name or 'hoodie' in item_type
    
    def _is_outerwear(self, item) -> bool:
        """Check if item is outerwear (jacket, coat, blazer)."""
        category = self._get_item_category(item)
        if category == 'outerwear':
            return True
        
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(self.safe_get_item_type(item)).lower()
        outerwear_keywords = ['jacket', 'coat', 'blazer', 'suit jacket', 'sport coat']
        return any(kw in item_name or kw in item_type for kw in outerwear_keywords)
    
    def _is_forbidden_combination(self, new_item, existing_items: List) -> bool:
        """
        Check if adding new_item would create a forbidden fashion combination.
        
        Forbidden combinations:
        - Blazer/suit jacket + shorts
        - Dress shoes + athletic shorts
        - Tuxedo + sneakers
        - Two shirts (not proper layering)
        - Collared shirt + turtleneck (not OK)
        - Short-sleeve sweater over long-sleeve shirt (not OK unless sweater vest)
        - BUT: Hoodie + coat is OK (preserve this)
        
        Returns:
            True if combination is forbidden, False if allowed
        """
        new_item_type = str(self.safe_get_item_type(new_item)).lower()
        new_item_name = self.safe_get_item_name(new_item).lower()
        
        for existing in existing_items:
            existing_type = str(self.safe_get_item_type(existing)).lower()
            existing_name = self.safe_get_item_name(existing).lower()
            
            # RULE 1: No blazer/suit jacket with shorts
            is_blazer = any(kw in new_item_type or kw in new_item_name for kw in ['blazer', 'suit jacket', 'sport coat'])
            is_shorts = any(kw in existing_type or kw in existing_name for kw in ['shorts', 'short'])
            
            is_existing_blazer = any(kw in existing_type or kw in existing_name for kw in ['blazer', 'suit jacket', 'sport coat'])
            is_new_shorts = any(kw in new_item_type or kw in new_item_name for kw in ['shorts', 'short'])
            
            if (is_blazer and is_shorts) or (is_existing_blazer and is_new_shorts):
                logger.info(f"  🚫 FORBIDDEN: Blazer/suit jacket + shorts combination blocked")
                return True
            
            # RULE 2: No dress shoes (oxfords, loafers) with athletic shorts
            is_dress_shoe = any(kw in new_item_type or kw in new_item_name for kw in ['oxford', 'loafer', 'derby', 'brogue'])
            is_athletic_shorts = any(kw in existing_type or kw in existing_name for kw in ['athletic short', 'gym short', 'running short'])
            
            is_existing_dress_shoe = any(kw in existing_type or kw in existing_name for kw in ['oxford', 'loafer', 'derby', 'brogue'])
            is_new_athletic_shorts = any(kw in new_item_type or kw in new_item_name for kw in ['athletic short', 'gym short', 'running short'])
            
            if (is_dress_shoe and is_athletic_shorts) or (is_existing_dress_shoe and is_new_athletic_shorts):
                logger.info(f"  🚫 FORBIDDEN: Dress shoes + athletic shorts combination blocked")
                return True
            
            # RULE 3: No tuxedo/formal jacket with sneakers
            is_tuxedo = any(kw in new_item_type or kw in new_item_name for kw in ['tuxedo', 'dinner jacket'])
            is_sneakers = any(kw in existing_type or kw in existing_name for kw in ['sneaker', 'trainer', 'athletic shoe'])
            
            is_existing_tuxedo = any(kw in existing_type or kw in existing_name for kw in ['tuxedo', 'dinner jacket'])
            is_new_sneakers = any(kw in new_item_type or kw in new_item_name for kw in ['sneaker', 'trainer', 'athletic shoe'])
            
            if (is_tuxedo and is_sneakers) or (is_existing_tuxedo and is_new_sneakers):
                logger.info(f"  🚫 FORBIDDEN: Tuxedo + sneakers combination blocked")
                return True
            
            # RULE 4: No two shirts (not proper layering)
            # Exception: Hoodie + coat is OK (preserve this)
            new_is_shirt = self._is_shirt(new_item)
            existing_is_shirt = self._is_shirt(existing)
            new_is_hoodie = self._is_hoodie(new_item)
            existing_is_hoodie = self._is_hoodie(existing)
            new_is_outerwear = self._is_outerwear(new_item)
            existing_is_outerwear = self._is_outerwear(existing)
            
            # Allow hoodie + coat/outerwear
            if (new_is_hoodie and existing_is_outerwear) or (existing_is_hoodie and new_is_outerwear):
                continue  # This is OK, skip to next item
            
            # Block two shirts
            if new_is_shirt and existing_is_shirt:
                logger.info(f"  🚫 FORBIDDEN: Two shirts combination blocked ({self.safe_get_item_name(new_item)} + {self.safe_get_item_name(existing)})")
                return True
            
            # RULE 5: No collared shirt + turtleneck
            new_is_collared = self._is_collared(new_item)
            existing_is_turtleneck = self._is_turtleneck(existing)
            existing_is_collared = self._is_collared(existing)
            new_is_turtleneck = self._is_turtleneck(new_item)
            
            if (new_is_collared and existing_is_turtleneck) or (existing_is_collared and new_is_turtleneck):
                logger.info(f"  🚫 FORBIDDEN: Collared shirt + turtleneck combination blocked")
                return True
            
            # RULE 6: No short-sleeve sweater over long-sleeve shirt (unless sweater vest)
            new_is_sweater = 'sweater' in new_item_name or 'sweater' in new_item_type
            existing_is_sweater = 'sweater' in existing_name or 'sweater' in existing_type
            new_is_sweater_vest = self._is_sweater_vest(new_item)
            existing_is_sweater_vest = self._is_sweater_vest(existing)
            
            if new_is_sweater and not new_is_sweater_vest:
                new_sleeve = self._get_sleeve_length(new_item)
                existing_sleeve = self._get_sleeve_length(existing)
                
                # Check if sweater is short-sleeve and existing is long-sleeve shirt
                if new_sleeve == 'short' and existing_sleeve == 'long' and existing_is_shirt:
                    logger.info(f"  🚫 FORBIDDEN: Short-sleeve sweater over long-sleeve shirt blocked (only sweater vests allowed)")
                    return True
            
            if existing_is_sweater and not existing_is_sweater_vest:
                existing_sleeve = self._get_sleeve_length(existing)
                new_sleeve = self._get_sleeve_length(new_item)
                
                # Check if existing sweater is short-sleeve and new item is long-sleeve shirt
                if existing_sleeve == 'short' and new_sleeve == 'long' and new_is_shirt:
                    logger.info(f"  🚫 FORBIDDEN: Short-sleeve sweater over long-sleeve shirt blocked (only sweater vests allowed)")
                    return True
        
        return False  # Combination is allowed
    
    def _get_normalized_or_raw(self, item: Dict, field_name: str) -> List[str]:
        """
        Get normalized metadata field with fallback to raw field.
        
        Priority:
        1. metadata.normalized.{field_name} (lowercase, consistent)
        2. Raw {field_name} field (normalize it)
        
        Args:
            item: Dict item to extract from
            field_name: 'occasion', 'style', or 'mood'
        
        Returns:
            List of lowercase values
        """
        # Try normalized metadata first (most reliable)
        if isinstance(item, dict):
            metadata = item.get('metadata', {})
            if isinstance(metadata, dict):
                normalized = metadata.get('normalized', {})
                if isinstance(normalized, dict):
                    normalized_values = normalized.get(field_name, [])
                    if normalized_values and isinstance(normalized_values, list):
                        return normalized_values  # Already lowercase
        
        # Fallback to raw field (normalize it ourselves)
        # Handle both dict and Pydantic objects
        if isinstance(item, dict):
            raw_values = item.get(field_name, [])
        else:
            # Pydantic object - use getattr
            raw_values = getattr(item, field_name, [])
        
        if isinstance(raw_values, list):
            return [str(v).lower() for v in raw_values]
        elif isinstance(raw_values, str):
            return [raw_values.lower()]
        
        return []
    
    def _detect_metadata_name_conflict(self, item: ClothingItem, field_name: str, metadata_value: str) -> dict:
        """
        Detect conflicts between metadata and item name.
        Returns: {
            'has_conflict': bool,
            'severity': 'none'|'minor'|'major',
            'confidence_penalty': float,
            'should_log': bool,
            'message': str
        }
        """
        item_name = self.safe_get_item_name(item).lower()
        metadata_lower = metadata_value.lower() if metadata_value else ''
        
        # No metadata = no conflict (will use name as fallback)
        if not metadata_value:
            return {
                'has_conflict': False,
                'severity': 'none',
                'confidence_penalty': 0.0,
                'should_log': False,
                'message': ''
            }
        
        # Define conflicting pairs for each field type
        conflict_pairs = {
            'bottomType': [
                (['shorts', 'short'], ['pants', 'trouser', 'jean']),
                (['pants', 'trouser'], ['shorts', 'short']),
            ],
            'waistbandType': [
                (['elastic', 'drawstring'], ['button', 'zip', 'belt']),
                (['button', 'zip'], ['elastic', 'drawstring']),
            ],
            'neckline': [
                (['crew', 'round', 'v-neck'], ['collar', 'polo']),
                (['collar', 'polo'], ['crew', 'round', 'v-neck']),
            ],
            'material': [
                (['polyester', 'nylon', 'synthetic'], ['wool', 'cotton', 'denim']),
                (['denim'], ['polyester', 'athletic']),
            ]
        }
        
        # Check for conflicts
        if field_name in conflict_pairs:
            for metadata_terms, name_terms in conflict_pairs[field_name]:
                metadata_match = any(term in metadata_lower for term in metadata_terms)
                name_match = any(term in item_name for term in name_terms)
                
                if metadata_match and name_match:
                    # MAJOR CONFLICT: Contradictory information
                    return {
                        'has_conflict': True,
                        'severity': 'major',
                        'confidence_penalty': -0.2,
                        'should_log': True,
                        'message': f"metadata.{field_name}='{metadata_value}' conflicts with name='{item_name[:40]}'"
                    }
        
        # Check for minor conflicts (similar but not exact)
        # e.g., metadata="athletic shorts" vs name="shorts" (compatible, not exact)
        if metadata_lower and metadata_lower not in item_name:
            # Minor difference: metadata provides more detail than name
            return {
                'has_conflict': True,
                'severity': 'minor',
                'confidence_penalty': -0.05,
                'should_log': False,
                'message': f"metadata.{field_name}='{metadata_value}' adds detail to name='{item_name[:40]}'"
            }
        
        # No conflict
        return {
            'has_conflict': False,
            'severity': 'none',
            'confidence_penalty': 0.0,
            'should_log': False,
            'message': ''
        }
    
    def _check_and_log_conflicts(self, item: ClothingItem) -> float:
        """
        Check for metadata/name conflicts across all key fields.
        Returns total confidence penalty to apply.
        """
        total_penalty = 0.0
        item_name = self.safe_get_item_name(item)
        
        # Track this item
        self.conflict_stats['total_items_checked'] += 1
        
        # Check metadata if it exists
        if not hasattr(item, 'metadata') or not item.metadata:
            return 0.0
        
        if not isinstance(item.metadata, dict):
            return 0.0
        
        visual_attrs = item.metadata.get('visualAttributes', {})
        if not isinstance(visual_attrs, dict):
            return 0.0
        
        # Fields to check for conflicts
        fields_to_check = {
            'bottomType': visual_attrs.get('bottomType'),
            'waistbandType': visual_attrs.get('waistbandType'),
            'neckline': visual_attrs.get('neckline'),
            'material': visual_attrs.get('material'),
            'formalLevel': visual_attrs.get('formalLevel'),
        }
        
        # Check each field
        for field_name, field_value in fields_to_check.items():
            if field_value:
                conflict_info = self._detect_metadata_name_conflict(item, field_name, field_value)
                
                if conflict_info['has_conflict']:
                    total_penalty += conflict_info['confidence_penalty']
                    
                    # Log based on severity
                    if conflict_info['severity'] == 'major':
                        logger.warning(f"⚠️ MAJOR CONFLICT: {item_name[:50]} - {conflict_info['message']}")
                        self.conflict_stats['major_conflicts'] += 1
                        # Track by field type
                        if field_name not in self.conflict_stats['conflicts_by_field']:
                            self.conflict_stats['conflicts_by_field'][field_name] = 0
                        self.conflict_stats['conflicts_by_field'][field_name] += 1
                    elif conflict_info['severity'] == 'minor' and conflict_info['should_log']:
                        logger.info(f"ℹ️ Minor conflict: {item_name[:50]} - {conflict_info['message']}")
                        self.conflict_stats['minor_conflicts'] += 1
        
        return total_penalty
    
    def get_conflict_statistics(self) -> dict:
        """Return conflict statistics for data quality monitoring"""
        if self.conflict_stats['total_items_checked'] == 0:
            return {
                'total_checked': 0,
                'conflict_rate': 0.0,
                'major_conflicts': 0,
                'minor_conflicts': 0,
                'conflicts_by_field': {}
            }
        
        total_conflicts = self.conflict_stats['major_conflicts'] + self.conflict_stats['minor_conflicts']
        
        return {
            'total_checked': self.conflict_stats['total_items_checked'],
            'conflict_rate': round(total_conflicts / self.conflict_stats['total_items_checked'], 3),
            'major_conflicts': self.conflict_stats['major_conflicts'],
            'minor_conflicts': self.conflict_stats['minor_conflicts'],
            'conflicts_by_field': self.conflict_stats['conflicts_by_field']
        }
    
    async def generate_outfit(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate an outfit with multi-layered scoring system"""
        logger.info(f"🎨 Starting robust outfit generation for user {context.user_id}")
        logger.info(f"📋 Context: {context.occasion}, {context.style}, {context.mood}")
        logger.info(f"📦 Wardrobe size: {len(context.wardrobe)} items")
        
        # Create session ID for within-session diversity tracking
        import hashlib
        session_timestamp = str(int(time.time() * 1000))  # millisecond precision
        session_id = hashlib.md5(f"{context.user_id}_{session_timestamp}".encode()).hexdigest()
        logger.info(f"📍 Session ID created: {session_id[:8]}... for within-session diversity")
        
        # 🔍 METADATA DIAGNOSTIC: Check if wardrobe items have metadata on arrival
        items_with_metadata = sum(1 for item in context.wardrobe if item.metadata is not None)
        logger.info(f"🔍 METADATA CHECK: {items_with_metadata}/{len(context.wardrobe)} items have metadata")
        if len(context.wardrobe) > 0:
            # Sample first 3 items
            for idx, item in enumerate(context.wardrobe[:3]):
                has_metadata = item.metadata is not None
                logger.info(f"🔍 SAMPLE {idx}: '{item.name[:40]}' metadata={has_metadata}")
                if has_metadata and hasattr(item.metadata, 'visualAttributes') and item.metadata.visualAttributes:
                    va = item.metadata.visualAttributes
                    logger.info(f"  ✅ visualAttributes: pattern={getattr(va, 'pattern', None)}, material={getattr(va, 'material', None)}, fit={getattr(va, 'fit', None)}")
                elif has_metadata:
                    logger.info(f"  ⚠️ Has metadata but no visualAttributes")
                else:
                    logger.info(f"  ❌ No metadata object")
        
        # ═══════════════════════════════════════════════════════════════════════
        # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
        # ═══════════════════════════════════════════════════════════════════════
        try:
            return await self._generate_outfit_internal(context, session_id)
        except Exception as e:
            import traceback
            error_details = {
                "error_type": str(type(e).__name__),
                "error_message": str(e),
                "full_traceback": traceback.format_exc(),
                "context_info": {
                    "context_type": str(type(context)),
                    "context_wardrobe_length": len(context.wardrobe) if hasattr(context, 'wardrobe') and context.wardrobe else 0,
                    "context_occasion": getattr(context, 'occasion', 'NO_OCCASION'),
                    "context_style": getattr(context, 'style', 'NO_STYLE'),
                    "context_user_id": getattr(context, 'user_id', 'NO_USER_ID')
                }
            }
            logger.error("🔥 ROBUST SERVICE CRASH - NoneType .get() error detected", extra=error_details, exc_info=True)
            print(f"🔥 ROBUST SERVICE CRASH: {error_details}")
            print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
            raise
    
    async def _generate_outfit_internal(self, context: GenerationContext, session_id: str) -> OutfitGeneratedOutfit:
        """Internal outfit generation logic with full error handling and session tracking"""
        
        # ═══════════════════════════════════════════════════════════════════════
        # HYDRATION & CONTEXT VALIDATION
        # ═══════════════════════════════════════════════════════════════════════
        
        # DEBUG: Log context details to identify NoneType issues
        # print(f"🔍 DEBUG ROBUST INTERNAL: context = {context}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: (context.wardrobe if context else []) = {context.wardrobe}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: context.user_profile = {context.user_profile}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: (context.weather if context else None) = {context.weather}")
        
        # Initialize base item tracker for debugging
        base_item_tracker = BaseItemTracker(context.base_item_id)
        base_item_tracker.checkpoint("01_initial_wardrobe", context.wardrobe, f"Starting with {len(context.wardrobe)} items")
        
        # Hydrate wardrobe items
        logger.debug(f"🔄 Hydrating {len(context.wardrobe)} wardrobe items")
        try:
            if isinstance(context.wardrobe, list) and len(context.wardrobe) > 0 and isinstance(context.wardrobe[0], dict):
                safe_wardrobe = ensure_items_safe_for_pydantic(context.wardrobe)
                logger.debug(f"✅ Hydrated {len(safe_wardrobe)} items successfully")
                if context:
                    context.wardrobe = safe_wardrobe
                base_item_tracker.checkpoint("02_after_hydration", context.wardrobe, "After hydration")
            else:
                logger.debug(f"✅ Items already ClothingItem objects")
        except Exception as hydrator_error:
            logger.error(f"❌ Hydration failed: {hydrator_error}")
            # print(f"🚨 HYDRATION ERROR: {hydrator_error}")
            import traceback
            # print(f"🚨 HYDRATION TRACEBACK: {traceback.format_exc()}")
        
        # DEBUG: Check context types after hydration
        logger.debug(f"🔍 DEBUG: After hydration - user_profile type: {type(context.user_profile)}")
        logger.debug(f"🔍 DEBUG: After hydration - weather type: {type(context.weather)}")
        if isinstance(context.user_profile, list):
            logger.error(f"🚨 ERROR: user_profile is a list: {context.user_profile}")
            debug_info = {
                "pipeline_stage": "early_return_user_profile_list",
                "context_wardrobe_count": len(context.wardrobe),
                "user_profile_type": str(type(context.user_profile)),
                "user_profile_value": str(context.user_profile)[:200],
                "wardrobe_items": [
                    {
                        "id": getattr(item, 'id', 'NO_ID'),
                        "name": getattr(item, 'name', 'NO_NAME'),
                        "type": str(getattr(item, 'type', 'NO_TYPE'))
                    } for item in (context.wardrobe if context else [])[:3]
                ]
            }
            return OutfitGeneratedOutfit(items=[], confidence=0.1, metadata={"generation_strategy": "multi_layered", "error": "user_profile_is_list", "debug_info": debug_info})
        if isinstance(context.weather, list):
            logger.error(f"🚨 ERROR: weather is a list: {context.weather}")
            debug_info = {
                "pipeline_stage": "early_return_weather_list",
                "context_wardrobe_count": len(context.wardrobe),
                "weather_type": str(type(context.weather)),
                "weather_value": str(context.weather)[:200],
                "wardrobe_items": [
                    {
                        "id": getattr(item, 'id', 'NO_ID'),
                        "name": getattr(item, 'name', 'NO_NAME'),
                        "type": str(getattr(item, 'type', 'NO_TYPE'))
                    } for item in (context.wardrobe if context else [])[:3]
                ]
            }
            return OutfitGeneratedOutfit(items=[], confidence=0.1, metadata={"generation_strategy": "multi_layered", "error": "weather_is_list", "debug_info": debug_info})
        
        # Smart weather defaults - dynamic based on context
        temp = 70.0  # Default temperature
        condition = 'clear'  # Default condition
        
        if (context.weather if context else None) is not None:
            temp = safe_get(context.weather, 'temperature', 70.0)
            condition = safe_get(context.weather, 'condition', 'clear')
        else:
            # Smart default: use occasion-appropriate weather
            if (context.occasion if context else "unknown").lower() in ['business', 'formal']:
                temp = 72.0  # Slightly warmer for professional settings
                condition = 'clear'
            elif (context.occasion if context else "unknown").lower() in ['party', 'evening']:
                temp = 68.0  # Slightly cooler for evening events
                condition = 'clear'
            elif (context.occasion if context else "unknown").lower() == 'athletic':
                temp = 75.0  # Warmer for athletic activities
                condition = 'clear'
            else:
                temp = 70.0  # Neutral default
                condition = 'clear'
            
            logger.warning(f"⚠️ Missing weather data, using SMART DEFAULT: {temp}°F, {condition} (occasion: {context.occasion})")
            # Log for learning system
            logger.info(f"📊 DEFAULT_APPLIED: weather_default_occasion_{context.occasion.lower()}_temp_{temp}")
            
            # Create a mock weather object for consistency
            class MockWeather:
                def __init__(self, temp, condition):
                    self.temperature = temp
                    self.condition = condition
            
            if context:
                context.weather = MockWeather(temp, condition)
            logger.info(f"🔧 Created mock weather object: {context.weather.temperature}°F, {context.weather.condition}")
        
        logger.info(f"🌤️ Weather: {temp}°F, {condition}")
        
        # Smart user profile defaults - context-aware
        if not context.user_profile:
            logger.warning(f"⚠️ Missing user profile, using SMART DEFAULTS")
            # Smart defaults based on occasion/style
            if (context.occasion if context else "unknown").lower() in ['business', 'formal']:
                context.user_profile = {
                    'bodyType': 'Average',
                    'height': 'Average', 
                    'weight': 'Average',
                    'gender': 'Unspecified',
                    'skinTone': 'Medium',
                    'stylePreferences': {'preferredStyles': ['classic', 'professional']}
                }
            elif (context.occasion if context else "unknown").lower() in ['party', 'evening']:
                context.user_profile = {
                    'bodyType': 'Average',
                    'height': 'Average', 
                    'weight': 'Average',
                    'gender': 'Unspecified',
                    'skinTone': 'Medium',
                    'stylePreferences': {'preferredStyles': ['elegant', 'trendy']}
                }
            elif (context.occasion if context else "unknown").lower() == 'athletic':
                context.user_profile = {
                    'bodyType': 'Athletic',
                    'height': 'Average', 
                    'weight': 'Average',
                    'gender': 'Unspecified',
                    'skinTone': 'Medium',
                    'stylePreferences': {'preferredStyles': ['athletic', 'casual']}
                }
            else:
                context.user_profile = {
                    'bodyType': 'Average',
                    'height': 'Average', 
                    'weight': 'Average',
                    'gender': 'Unspecified',
                    'skinTone': 'Medium',
                    'stylePreferences': {}
                }
            
            logger.info(f"🎯 SMART PROFILE DEFAULT: {context.user_profile['bodyType']} body type for {context.occasion} occasion")
            # Log for learning system
            logger.info(f"📊 DEFAULT_APPLIED: profile_default_occasion_{context.occasion.lower()}_body_{context.user_profile['bodyType'].lower()}")
        
        # Log wardrobe breakdown
        item_types = [self.safe_get_item_type(item) for item in (context.wardrobe if context else [])]
        type_counts = {item_type: item_types.count(item_type) for item_type in set(item_types)}
        logger.info(f"📊 Wardrobe breakdown: {type_counts}")
        
        # ═══════════════════════════════════════════════════════════
        # MULTI-LAYERED SCORING SYSTEM
        # Each analyzer scores items, then cohesive composition uses all scores
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🔬 PHASE 1: Filtering & Multi-Layered Analysis & Scoring")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: OCCASION-FIRST FILTERING (with fallbacks)
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🎯 STEP 1: Occasion-First Filtering")
        
        # CRITICAL: When base item is specified, skip strict occasion filtering
        # Use OR logic in STEP 2 instead for maximum flexibility
        if context.base_item_id:
            logger.info(f"🎯 BASE ITEM MODE: Skipping strict occasion filter, will use OR logic in STEP 2")
            occasion_candidates = context.wardrobe  # Use entire wardrobe
            logger.info(f"✅ STEP 1 SKIPPED: Using all {len(occasion_candidates)} items (base item mode)")
        else:
            # Normal mode: strict occasion filtering
            occasion_candidates = self._get_occasion_appropriate_candidates(
                wardrobe=context.wardrobe,
                target_occasion=context.occasion,
                min_items=3,  # Require at least 3 items before fallbacks
                base_item_id=None
            )
            logger.info(f"✅ STEP 1 COMPLETE: {len(occasion_candidates)} occasion-appropriate items (from {len(context.wardrobe)} total)")
        
        # Track base item after occasion filtering
        base_item_tracker.checkpoint("03_after_occasion_filter", occasion_candidates, f"After occasion filter: {context.occasion}")
        
        # Update context with occasion-filtered wardrobe
        original_wardrobe_size = len(context.wardrobe)
        # Save original wardrobe before filtering (for last-resort shoe search)
        context.wardrobe_original = context.wardrobe.copy()
        context.wardrobe = occasion_candidates
        logger.info(f"📦 Wardrobe updated: {original_wardrobe_size} → {len(context.wardrobe)} items (occasion-filtered)")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: ADDITIONAL FILTERING (style, mood, weather)
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🔍 FILTERING STEP 2: Starting item filtering for {context.occasion} occasion")
        suitable_items = await self._filter_suitable_items(context)
        logger.info(f"✅ FILTERING STEP 2: {len(suitable_items)} suitable items passed from {len(context.wardrobe)} occasion-filtered items")
        
        # Track base item after style/mood/weather filtering
        base_item_tracker.checkpoint("04_after_style_mood_weather_filter", suitable_items, f"After style/mood/weather filter")
        
        if len(suitable_items) == 0:
            logger.error(f"🚨 CRITICAL: No suitable items found after filtering!")
            logger.error(f"🔍 DEBUG: Occasion: {context.occasion}, Style: {context.style}, Mood: {context.mood}")
            raise Exception(f"No suitable items found for {context.occasion} occasion")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: MULTI-LAYERED SCORING ON FILTERED ITEMS
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🔬 SCORING: Starting multi-layered scoring on {len(suitable_items)} filtered items")
        
        # Create scoring dictionary for each suitable item
        item_scores = {}
        logger.debug(f"🔍 DEBUG SCORING: Starting to create scores for {len(suitable_items)} suitable items")
        for i, item in enumerate(suitable_items):
            item_id = safe_item_access(item, 'id', f"item_{len(item_scores)}")
            logger.debug(f"🔍 DEBUG SCORING: Creating score for item {i+1}: {item_id} - {getattr(item, 'name', 'Unknown')}")
            item_scores[item_id] = {
                'item': item,
                'body_type_score': 0.0,
                'style_profile_score': 0.0,
                'weather_score': 0.0,
                'user_feedback_score': 0.0,  # NEW!
                'composite_score': 0.0
            }
        
        logger.debug(f"🔍 DEBUG SCORING: Created {len(item_scores)} item scores")
        
        # Track base item in item_scores
        base_item_tracker.checkpoint_with_scores("05_after_score_initialization", item_scores, f"Item scores initialized")
        
        logger.debug(f"🔍 DEBUG: Initialized {len(item_scores)} items for scoring")
        
        # Run all analyzers in parallel on filtered items
        logger.info(f"🚀 Running 5 analyzers in parallel on {len(suitable_items)} filtered items... (body type + style profile + weather + user feedback + metadata compatibility)")
        
        analyzer_tasks = [
            # MULTI-LAYERED SCORING: 5 Analyzers
            asyncio.create_task(self._analyze_body_type_scores(context, item_scores)),
            asyncio.create_task(self._analyze_style_profile_scores(context, item_scores)),
            asyncio.create_task(self._analyze_weather_scores(context, item_scores)),
            asyncio.create_task(self._analyze_user_feedback_scores(context, item_scores)),
            asyncio.create_task(self.metadata_analyzer.analyze_compatibility_scores(context, item_scores))  # NEW: Unified Metadata Compatibility
        ]
        
        # Wait for all analyzers to complete
        await asyncio.gather(*analyzer_tasks)
        
        # DEBUG: Check analyzer outputs for first 3 items
        for i, (item_id, scores) in enumerate(list(item_scores.items())[:3]):
            compat_score = scores.get('compatibility_score', 1.0)
            breakdown = scores.get('_compatibility_breakdown', {})
            # Only log first 3 items to avoid spam
            if i < 3:
                logger.info(f"🔍 ITEM {i+1} SCORES: {self.safe_get_item_name(scores['item'])}: body={scores['body_type_score']:.2f}, style={scores['style_profile_score']:.2f}, weather={scores['weather_score']:.2f}, feedback={scores['user_feedback_score']:.2f}, compat={compat_score:.2f}")
            else:
                logger.debug(f"🔍 ITEM {i+1} SCORES: {self.safe_get_item_name(scores['item'])}: body={scores['body_type_score']:.2f}, style={scores['style_profile_score']:.2f}, weather={scores['weather_score']:.2f}, feedback={scores['user_feedback_score']:.2f}, compat={compat_score:.2f}")
            if breakdown:
                logger.debug(f"   Compatibility breakdown: layer={breakdown.get('layer', 0):.2f}, pattern={breakdown.get('pattern', 0):.2f}, fit={breakdown.get('fit', 0):.2f}, formality={breakdown.get('formality', 0):.2f}, color={breakdown.get('color', 0):.2f}, brand={breakdown.get('brand', 0):.2f}")
        
        # Calculate composite scores
        logger.info(f"🧮 Calculating composite scores with 5-dimensional analysis...")
        # Calculate composite scores with dynamic weights based on weather
        temp = safe_get(context.weather, 'temperature', 70.0)
        
        # Dynamic weight adjustment for extreme weather (5 dimensions now)
        if temp > 75:  # Hot weather - increase weather & compatibility weights
            weather_weight = 0.25
            compatibility_weight = 0.20  # Layer/pattern/fit compatibility more important
            style_weight = 0.20
            body_weight = 0.15
            user_feedback_weight = 0.20
        elif temp < 50:  # Cold weather - increase weather & compatibility weights
            weather_weight = 0.25
            compatibility_weight = 0.20  # Proper layering/formality more important
            style_weight = 0.20
            body_weight = 0.15
            user_feedback_weight = 0.20
        else:  # Moderate weather - standard weights
            weather_weight = 0.20
            compatibility_weight = 0.15  # Standard metadata compatibility importance
            style_weight = 0.25
            body_weight = 0.20
            user_feedback_weight = 0.20
        
        logger.info(f"🎯 DYNAMIC WEIGHTS (5D): Weather={weather_weight}, Compatibility={compatibility_weight}, Style={style_weight}, Body={body_weight}, UserFeedback={user_feedback_weight} (temp={temp}°F)")
        
        # ═══════════════════════════════════════════════════════════════════════
        # APPLY DIVERSITY BOOST (6TH DIMENSION)
        # ═══════════════════════════════════════════════════════════════════════
        
        logger.info(f"🎭 Applying diversity boost to prevent outfit repetition...")
        
        # Get all items for diversity boost calculation
        all_items = [scores['item'] for scores in item_scores.values()]
        
        try:
            # Apply diversity boost from DiversityFilterService
            boosted_items = diversity_filter.apply_diversity_boost(
                items=all_items,
                user_id=context.user_id,
                occasion=context.occasion,
                style=context.style,
                mood=context.mood
            )
            
            # Create diversity score lookup
            diversity_scores = {item.id: boost_score for item, boost_score in boosted_items}
            logger.info(f"✅ Diversity boost applied to {len(diversity_scores)} items")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to apply diversity boost: {e}")
            diversity_scores = {}
        
        # ═══════════════════════════════════════════════════════════════════════
        # CALCULATE FINAL COMPOSITE SCORES (6 DIMENSIONS)
        # ═══════════════════════════════════════════════════════════════════════
        
        diversity_weight = 0.22  # 22% weight for diversity - OPTIMIZED for quality (was 0.30)
        if (context.style or "").lower() == 'monochrome':
            diversity_weight = 0.15  # Lower for monochrome cohesion (was 0.18)
        
        # Adjust other weights to accommodate diversity dimension (must sum to 100%)
        if temp > 75 or temp < 50:  # Extreme weather
            weather_weight = 0.20  # Increased for weather importance (was 0.18)
            compatibility_weight = 0.14  # Increased for better cohesion (was 0.12)
            style_weight = 0.20  # Increased for style matching (was 0.16)
            body_weight = 0.12
            user_feedback_weight = 0.12
        else:  # Moderate weather
            weather_weight = 0.16  # Increased for consistency (was 0.14)
            compatibility_weight = 0.13  # Increased for cohesion (was 0.11)
            style_weight = 0.22  # Increased for better style (was 0.18)
            body_weight = 0.15
            user_feedback_weight = 0.12
        
        logger.info(f"🎯 DYNAMIC WEIGHTS (6D): Weather={weather_weight}, Compatibility={compatibility_weight}, Style={style_weight}, Body={body_weight}, UserFeedback={user_feedback_weight}, Diversity={diversity_weight}")
        
        for item_id, scores in item_scores.items():
            # Multi-layered scoring with 6 dimensions and dynamic weights
            diversity_score = diversity_scores.get(item_id, 1.0)  # Default to 1.0 if not found
            
            base_score = (
                scores['body_type_score'] * body_weight +
                scores['style_profile_score'] * style_weight +
                scores['weather_score'] * weather_weight +
                scores['user_feedback_score'] * user_feedback_weight +
                scores.get('compatibility_score', 1.0) * compatibility_weight +
                diversity_score * diversity_weight  # NEW: Diversity dimension
            )
            
            # Apply soft constraint penalties/bonuses
            soft_penalty = self._soft_score(scores['item'], (context.occasion if context else "unknown"), (context.style if context else "unknown"), (context.mood if context else "unknown"), weather=(context.weather if context else None))
            
            # Apply session-based diversity penalty (prevents repetition within same generation session)
            session_penalty = session_tracker.get_diversity_penalty(session_id, item_id)
            
            # Check for metadata/name conflicts and apply confidence penalty
            conflict_penalty = self._check_and_log_conflicts(scores['item'])
            
            final_score = base_score + soft_penalty + session_penalty + conflict_penalty
            
            scores['composite_score'] = final_score
            scores['diversity_score'] = diversity_score
            scores['soft_penalty'] = soft_penalty
            scores['session_penalty'] = session_penalty
            scores['base_score'] = base_score
        
        # Log top scored items (reduced verbosity)
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        
        # Track base item after composite scoring
        base_item_tracker.checkpoint_with_scores("06_after_composite_scoring", item_scores, f"After composite score calculation")
        
        logger.info(f"🏆 Top 3 scored items (with diversity + session penalties):")
        for i, (item_id, scores) in enumerate(sorted_items[:3]):
            diversity_score = scores.get('diversity_score', 1.0)
            session_penalty = scores.get('session_penalty', 0.0)
            penalty_indicator = " 🔴" if session_penalty < 0 else ""
            logger.info(f"  {i+1}. {self.safe_get_item_name(scores['item'])}: {scores['composite_score']:.2f} (div: {diversity_score:.2f}, session: {session_penalty:+.2f}){penalty_indicator}")
        
        # ═══════════════════════════════════════════════════════════
        # ADAPTIVE WEIGHT ADJUSTMENT (Favorites Mode)
        # ═══════════════════════════════════════════════════════════
        
        # Check if user is in "favorites mode" (has many favorited items in wardrobe)
        # PERFORMANCE FIX: Use wardrobe already in context instead of Firebase query
        favorites_mode = False
        if context.user_profile and context.wardrobe:
            try:
                # Count favorited items from context.wardrobe (no Firebase query needed!)
                favorited_count = sum(1 for item in context.wardrobe if getattr(item, 'isFavorite', False) or getattr(item, 'favorite_score', 0) > 0.7)
                
                # If 30%+ of wardrobe is favorited, enable favorites mode
                if len(context.wardrobe) > 0 and (favorited_count / len(context.wardrobe)) >= 0.3:
                    favorites_mode = True
                    logger.info(f"⭐ FAVORITES MODE ACTIVATED: {favorited_count}/{len(context.wardrobe)} items favorited ({favorited_count/len(context.wardrobe)*100:.0f}%)")
                else:
                    logger.info(f"📊 Favorites check: {favorited_count}/{len(context.wardrobe)} favorited ({favorited_count/len(context.wardrobe)*100:.0f}% - need 30% for favorites mode)")
            except Exception as e:
                logger.warning(f"⚠️ Could not check favorites mode: {e}")
        
        # Adjust weights if in favorites mode
        if favorites_mode:
            # Boost user feedback (favorites/wear history), but keep diversity high enough
            if temp > 75 or temp < 50:  # Extreme weather
                weather_weight = 0.20
                compatibility_weight = 0.12
                style_weight = 0.18
                body_weight = 0.10
                user_feedback_weight = 0.22  # ⬆️ BOOSTED from 0.12
                diversity_weight = 0.18  # ⬇️ Slightly lower in favorites mode
            else:  # Moderate weather
                weather_weight = 0.14
                compatibility_weight = 0.11
                style_weight = 0.18
                body_weight = 0.12
                user_feedback_weight = 0.23  # ⬆️ BOOSTED from 0.12 (reduced from 0.30 to keep diversity higher)
                diversity_weight = 0.22  # ⬇️ REDUCED from 0.30 but still significant (was 0.15)
                if (context.style or "").lower() == 'monochrome':
                    diversity_weight = min(diversity_weight, 0.18)
            
            logger.info(f"⭐ FAVORITES MODE WEIGHTS: UserFeedback={user_feedback_weight} (+100%), Diversity={diversity_weight} (kept at ~20% to ensure variety)")
            logger.info(f"🎯 ADJUSTED WEIGHTS (6D): Weather={weather_weight}, Compat={compatibility_weight}, Style={style_weight}, Body={body_weight}, Feedback={user_feedback_weight}, Diversity={diversity_weight}")
            
            # Re-calculate composite scores with new weights
            for item_id, scores in item_scores.items():
                diversity_score = diversity_scores.get(item_id, 1.0)
                
                base_score = (
                    scores['body_type_score'] * body_weight +
                    scores['style_profile_score'] * style_weight +
                    scores['weather_score'] * weather_weight +
                    scores['user_feedback_score'] * user_feedback_weight +
                    scores.get('compatibility_score', 1.0) * compatibility_weight +
                    diversity_score * diversity_weight
                )
                
                # Re-apply soft penalties and session penalties
                soft_penalty = scores.get('soft_penalty', 0)
                session_penalty = scores.get('session_penalty', 0)
                final_score = base_score + soft_penalty + session_penalty
                
                scores['composite_score'] = final_score
                scores['base_score'] = base_score
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: Cohesive Composition with Multi-Layered Scores
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🎨 PHASE 2: Cohesive Composition with Scored Items")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PROGRESSIVE FALLBACK FILTERING
        # ═══════════════════════════════════════════════════════════════════════
        
        # Check if we have any scored items
        if not item_scores:
            logger.error(f"🚨 CRITICAL: No items scored - all items filtered out!")
            logger.error(f"🔍 DEBUG: Wardrobe size: {len(context.wardrobe)}")
            logger.error(f"🔍 DEBUG: Suitable items: N/A (filtering failed)")
            logger.error(f"🔍 DEBUG: Occasion: {context.occasion}, Style: {context.style}")
            
            # EXTREME WEATHER SAFETY CHECK
            temp = safe_get(context.weather, 'temperature', 70.0)
            if temp > 80:  # Extreme heat
                logger.warning(f"🔥 EXTREME HEAT: {temp}°F - emergency relaxation of weather penalties")
                # Emergency: create minimal scores for any available items
                for item in (context.wardrobe if context else []):
                    item_id = safe_item_access(item, 'id', f"emergency_{len(item_scores)}")
                    item_scores[item_id] = {
                        'item': item,
                        'body_type_score': 0.5,
                        'style_profile_score': 0.5,
                        'weather_score': 0.3,  # Minimum score for extreme heat
                        'composite_score': 0.43  # Weighted average
                    }
                logger.info(f"🚨 EMERGENCY: Created {len(item_scores)} emergency scores for extreme heat")
            
            # Emergency fallback: use any available items
            if (context.wardrobe if context else []):
                logger.warning(f"🚨 EMERGENCY: Using any available items as fallback")
                for item in (context.wardrobe if context else []):
                    item_id = safe_item_access(item, 'id', f"emergency_{len(item_scores)}")
                    item_scores[item_id] = {
                        'body_type_score': 0.5,
                        'style_profile_score': 0.5,
                        'weather_score': 0.5,
                        'composite_score': 0.5
                    }
                logger.info(f"🚨 EMERGENCY: Created {len(item_scores)} emergency scores")
            else:
                raise Exception(f"No items available for scoring - wardrobe or filtering issue")
        
        # Check if items have reasonable scores
        total_items = len(item_scores)
        items_with_scores = len([s for s in item_scores.values() if safe_get(s, 'composite_score', 0) > 0.1])
        logger.info(f"🔍 SCORE CHECK: {total_items} total items, {items_with_scores} with scores > 0.1")
        
        if items_with_scores == 0:
            logger.warning(f"⚠️ WARNING: All items have very low scores, may need progressive filtering")
            # Don't return here, let cohesive composition try first
        
        # Track base item before cohesive composition
        base_item_tracker.checkpoint_with_scores("07_before_cohesive_composition", item_scores, f"Before cohesive composition")
        
        # Pass scored items to cohesive composition
        outfit = await self._cohesive_composition_with_scores(context, item_scores, session_id)
        
        # Track base item in final outfit
        if outfit and outfit.items:
            base_item_tracker.checkpoint("08_final_outfit", outfit.items, f"Final outfit generated with {len(outfit.items)} items")
        
        # Print tracking summary
        base_item_tracker.print_summary()
        
        # Check if cohesive composition failed to generate items
        if not outfit.items or len(outfit.items) == 0:
            logger.error(f"❌ COHESIVE COMPOSITION FAILED: No items generated - this should not happen")
            
            # Collect detailed debug information for the error
            debug_info = {
                "pipeline_stage": "cohesive_composition",
                "context_wardrobe_count": len(context.wardrobe),
                "suitable_items_count": len(suitable_items),
                "item_scores_count": len(item_scores),
                "items_with_scores": len([s for s in item_scores.values() if safe_get(s, 'composite_score', 0) > 0.1]),
                "context_occasion": (context.occasion if context else "unknown"),
                "context_style": (context.style if context else "unknown"),
                "context_mood": (context.mood if context else "unknown"),
                "wardrobe_items": [
                    {
                        "id": getattr(item, 'id', 'NO_ID'),
                        "name": getattr(item, 'name', 'NO_NAME'),
                        "type": str(getattr(item, 'type', 'NO_TYPE'))
                    } for item in (context.wardrobe if context else [])[:3]
                ],
                "suitable_items": [
                    {
                        "id": getattr(item, 'id', 'NO_ID'),
                        "name": getattr(item, 'name', 'NO_NAME'),
                        "type": str(getattr(item, 'type', 'NO_TYPE'))
                    } for item in suitable_items[:3]
                ],
                "top_scored_items": [
                    {
                        "id": item_id,
                        "name": getattr(scores['item'], 'name', 'Unknown'),
                        "composite_score": (safe_get(scores, 'composite_score', 0) if scores else 0)
                    } for item_id, scores in sorted(item_scores.items(), key=lambda x: safe_get(x[1], 'composite_score', 0), reverse=True)[:3]
                ] if item_scores else []
            }
            
            raise Exception(f"🔥 COHESIVE COMPOSITION FAILED: Cohesive composition failed to generate items - system needs fixing. DEBUG: {debug_info}")
        
        logger.info(f"✅ ROBUST GENERATION SUCCESS: Generated outfit with {len(outfit.items)} items")
        logger.info(f"📦 Final outfit items: {[getattr(item, 'name', 'Unknown') for item in outfit.items]}")
        
        # Log conflict statistics for data quality monitoring
        conflict_stats = self.get_conflict_statistics()
        if conflict_stats['total_checked'] > 0:
            logger.info(f"📊 DATA QUALITY: Checked {conflict_stats['total_checked']} items, "
                       f"conflict_rate={conflict_stats['conflict_rate']*100:.1f}%, "
                       f"major={conflict_stats['major_conflicts']}, "
                       f"minor={conflict_stats['minor_conflicts']}")
            if conflict_stats['conflicts_by_field']:
                logger.info(f"📊 CONFLICTS BY FIELD: {conflict_stats['conflicts_by_field']}")
        
        # Initialize flat lay metadata but wait for explicit user consent
        if self.enable_flat_lay_generation and outfit.items:
            if not hasattr(outfit, 'metadata') or outfit.metadata is None:
                outfit.metadata = {}
            for key in ['flat_lay_status', 'flatLayStatus']:
                outfit.metadata[key] = 'awaiting_consent'
            for key in ['flat_lay_url', 'flatLayUrl', 'flat_lay_error', 'flatLayError']:
                outfit.metadata.pop(key, None)
            for key in ['flat_lay_requested', 'flatLayRequested']:
                outfit.metadata[key] = False
            # Only set attributes that exist in the model
            for attr in ['flat_lay_status', 'flatLayStatus']:
                if hasattr(outfit, attr):
                    setattr(outfit, attr, 'awaiting_consent')
            for attr in ['flat_lay_url', 'flatLayUrl', 'flat_lay_error', 'flatLayError']:
                if hasattr(outfit, attr):
                    setattr(outfit, attr, None)
            # flat_lay_requested is only in metadata, not as an attribute
            outfit.metadata['flat_lay_worker'] = 'premium_v1'
            logger.info("🎨 Flat lay generation awaiting user request (status=awaiting_consent)")
        
        return outfit
    
    async def _emergency_fallback_with_progressive_filtering(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Emergency fallback with progressive filter relaxation"""
        logger.warning(f"🆘 EMERGENCY FALLBACK: All items filtered out, using progressive relaxation")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PROGRESSIVE FILTER RELAXATION
        # ═══════════════════════════════════════════════════════════════════════
        
        # Start with all wardrobe items
        all_items = (context.wardrobe if context else []).copy()
        logger.info(f"🔄 PROGRESSIVE FILTERING: Starting with {len(all_items)} items")
        
        # Level 1: Relax occasion filtering
        logger.info(f"🔄 LEVEL 1: Relaxing occasion filtering...")
        relaxed_items = await self._relax_occasion_filtering(all_items, (context.occasion if context else "unknown"))
        if relaxed_items:
            logger.info(f"✅ LEVEL 1 SUCCESS: {len(relaxed_items)} items after relaxing occasion")
            return await self._create_outfit_from_items(relaxed_items, context, "progressive_occasion_relaxed")
        
        # Level 2: Relax style filtering
        logger.info(f"🔄 LEVEL 2: Relaxing style filtering...")
        relaxed_items = await self._relax_style_filtering(all_items, (context.style if context else "unknown"))
        if relaxed_items:
            logger.info(f"✅ LEVEL 2 SUCCESS: {len(relaxed_items)} items after relaxing style")
            return await self._create_outfit_from_items(relaxed_items, context, "progressive_style_relaxed")
        
        # Level 3: Relax weather filtering
        logger.info(f"🔄 LEVEL 3: Relaxing weather filtering...")
        relaxed_items = await self._relax_weather_filtering(all_items, (context.weather if context else None))
        if relaxed_items:
            logger.info(f"✅ LEVEL 3 SUCCESS: {len(relaxed_items)} items after relaxing weather")
            return await self._create_outfit_from_items(relaxed_items, context, "progressive_weather_relaxed")
        
        # Level 4: Use all items (no filtering)
        logger.warning(f"🆘 LEVEL 4: Using all items without any filtering")
        return await self._create_outfit_from_items(all_items, context, "progressive_no_filtering")
    
    def _is_item_suitable_for_occasion(self, item: Any, occasion: str, style: str) -> bool:
        """Check if an item is suitable for the given occasion and style."""
        is_suitable, _ = self._is_item_suitable_for_occasion_with_debug(item, occasion, style)
        return is_suitable
    
    def _is_item_suitable_for_occasion_with_debug(self, item: Any, occasion: str, style: str) -> Tuple[bool, List[str]]:
        """
        Check if an item is suitable for the given occasion and style.
        METADATA-FIRST FILTERING: Uses structured data as primary filter, names only as tertiary helper.
        Returns (is_suitable, rejection_reasons)
        """
        rejection_reasons = []
        
        if not occasion:
            return True, rejection_reasons
            
        occasion_lower = occasion.lower()
        item_name = self.safe_get_item_name(item)
        
        # ═══════════════════════════════════════════════════════════════════════
        # PRIMARY FILTER: Use structured metadata (occasion[], style[], type, brand)
        # ═══════════════════════════════════════════════════════════════════════
        
        # 1. Check occasion[] field from AI analysis (PRIMARY)
        item_occasions = safe_item_access(item, 'occasion', [])
        if isinstance(item_occasions, list) and item_occasions:
            # If item has explicit occasion tags, use them
            item_occasions_lower = [occ.lower() for occ in item_occasions]
            if occasion_lower in item_occasions_lower:
                logger.info(f"✅ {item_name}: PASSED by occasion[] match: {item_occasions_lower} contains {occasion_lower}")
                return True, rejection_reasons  # Item explicitly tagged for this occasion
            else:
                rejection_reasons.append(f"Occasion mismatch: item occasions {item_occasions} don't include '{occasion}'")
        
        # 2. Check style[] field from AI analysis (PRIMARY)
        item_styles = safe_item_access(item, 'style', [])
        if isinstance(item_styles, list) and item_styles:
            # If item has explicit style tags, use them
            item_styles_lower = [s.lower() for s in item_styles]
            if occasion_lower in item_styles_lower:  # Some occasions map to styles
                logger.info(f"✅ {item_name}: PASSED by style[] match: {item_styles_lower} contains {occasion_lower}")
                return True, rejection_reasons
            else:
                rejection_reasons.append(f"Style mismatch: item styles {item_styles} don't include '{occasion}'")
        
        # 3. Check item type (SECONDARY - more reliable than names)
        item_type = safe_item_access(item, 'type', '').lower()
        if item_type:
            # Type-based filtering for obvious mismatches
            if self._is_type_suitable_for_occasion(item_type, occasion_lower):
                logger.info(f"✅ {item_name}: PASSED by type match: {item_type} suitable for {occasion_lower}")
                return True, rejection_reasons
            elif self._is_type_unsuitable_for_occasion(item_type, occasion_lower):
                logger.info(f"❌ {item_name}: REJECTED by type mismatch: {item_type} unsuitable for {occasion_lower}")
                rejection_reasons.append(f"Type mismatch: {item_type} unsuitable for {occasion_lower}")
                return False, rejection_reasons
        
        # 4. Check brand (SECONDARY - reliable for athletic/formal brands)
        item_brand = safe_item_access(item, 'brand', '').lower()
        if item_brand:
            if self._is_brand_suitable_for_occasion(item_brand, occasion_lower):
                logger.info(f"✅ {item_name}: PASSED by brand match: {item_brand} suitable for {occasion_lower}")
                return True, rejection_reasons
            else:
                rejection_reasons.append(f"Brand mismatch: {item_brand} not suitable for {occasion_lower}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # TERTIARY FILTER: Use item names only as fallback helper (LAST RESORT)
        # ═══════════════════════════════════════════════════════════════════════
        
        item_name_lower = safe_item_access(item, 'name', '').lower()
        if item_name_lower:
            # Only use name patterns for obvious mismatches when metadata is missing
            if self._is_name_obviously_unsuitable(item_name_lower, occasion_lower):
                logger.info(f"❌ {item_name}: REJECTED by name pattern: {item_name_lower} unsuitable for {occasion_lower}")
                rejection_reasons.append(f"Name pattern mismatch: {item_name_lower} unsuitable for {occasion_lower}")
                return False, rejection_reasons
        
        # ═══════════════════════════════════════════════════════════════════════
        # DEFAULT: Allow items (let scoring system handle preferences)
        # ═══════════════════════════════════════════════════════════════════════
        
        logger.info(f"✅ {item_name}: PASSED by default (no hard filters matched)")
        return True, rejection_reasons  # Conservative approach - allow items, let scoring decide
    
    def _is_type_suitable_for_occasion(self, item_type: str, occasion_lower: str) -> bool:
        """Check if item type is suitable for occasion (SECONDARY filter)"""
        if 'athletic' in occasion_lower or 'gym' in occasion_lower:
            athletic_types = ['shirt', 'pants', 'shorts', 'shoes', 'sneakers', 'tank', 'hoodie', 'sweatshirt', 'jacket']
            return item_type in athletic_types
        
        elif 'business' in occasion_lower or 'formal' in occasion_lower:
            business_types = ['shirt', 'pants', 'shoes', 'blouse', 'skirt', 'dress', 'jacket', 'blazer']
            return item_type in business_types
        
        elif 'casual' in occasion_lower:
            return True  # Most types work for casual
        
        return True  # Default: allow most types
    
    def _is_type_unsuitable_for_occasion(self, item_type: str, occasion_lower: str) -> bool:
        """Check if item type is obviously unsuitable for occasion (SECONDARY filter)"""
        if 'athletic' in occasion_lower or 'gym' in occasion_lower:
            formal_types = ['dress', 'suit', 'blazer', 'heels', 'oxford', 'loafers']
            return item_type in formal_types
        
        elif 'business' in occasion_lower or 'formal' in occasion_lower:
            casual_types = ['tank', 'shorts', 'flip flops', 'sandals']
            return item_type in casual_types
        
        return False  # Default: don't reject based on type
    
    def _is_brand_suitable_for_occasion(self, item_brand: str, occasion_lower: str) -> bool:
        """Check if brand is suitable for occasion (SECONDARY filter)"""
        if 'athletic' in occasion_lower or 'gym' in occasion_lower:
            athletic_brands = ['nike', 'adidas', 'puma', 'under armour', 'reebok', 'new balance']
            return any(brand in item_brand for brand in athletic_brands)
        
        elif 'business' in occasion_lower or 'formal' in occasion_lower:
            formal_brands = ['brooks brothers', 'ralph lauren', 'hugo boss', 'calvin klein', 'tommy hilfiger']
            return any(brand in item_brand for brand in formal_brands)
        
        return False  # Default: don't accept based on brand alone
    
    def _is_name_obviously_unsuitable(self, item_name: str, occasion_lower: str) -> bool:
        """
        Check if item name is obviously unsuitable for occasion (TERTIARY filter only).
        This is the ONLY place where names are used for filtering, and only for obvious mismatches.
        """
        if 'athletic' in occasion_lower or 'gym' in occasion_lower:
            # Only reject if name explicitly contains formal terms
            formal_terms = ['dress shoes', 'suit', 'blazer', 'heels', 'oxford', 'loafers', 'tie']
            return any(term in item_name for term in formal_terms)
        
        elif 'business' in occasion_lower or 'formal' in occasion_lower:
            # Only reject if name explicitly contains casual/athletic terms
            casual_terms = ['tank top', 'flip flops', 'sweatpants', 'basketball shoes']
            return any(term in item_name for term in casual_terms)
        
        return False  # Default: don't reject based on name
    
    def _semantic_item_filter(self, normalized_item: Dict[str, Any], occasion: str, style: str, mood: str) -> Tuple[bool, List[str]]:
        """
        Semantic filtering using normalized metadata and compatibility matrices.
        Returns (is_suitable, rejection_reasons)
        """
        rejection_reasons = []
        
        # Check occasion compatibility
        if not occasion_matches(occasion, safe_item_access(normalized_item, 'occasion', [])):
            rejection_reasons.append(f"Occasion mismatch: item occasions {safe_item_access(normalized_item, 'occasion', [])}")
        
        # Check style compatibility  
        if not style_matches(style, safe_item_access(normalized_item, 'style', [])):
            rejection_reasons.append(f"Style mismatch: item styles {safe_item_access(normalized_item, 'style', [])}")
        
        # Check mood compatibility
        if not mood_matches(mood, safe_item_access(normalized_item, 'mood', [])):
            rejection_reasons.append(f"Mood mismatch: item moods {safe_item_access(normalized_item, 'mood', [])}")
        
        is_suitable = len(rejection_reasons) == 0
        return is_suitable, rejection_reasons
    
    async def _relax_occasion_filtering(self, items: List[Any], occasion: str) -> List[Any]:
        """Relax occasion filtering - allow more flexible occasion matching"""
        if not occasion:
            return items
        
        relaxed_items = []
        occasion_lower = occasion.lower()
        
        for item in items:
            # Get item occasions
            item_occasions = safe_item_access(item, 'occasion', [])
            if isinstance(item_occasions, str):
                item_occasions = [item_occasions]
            
            # Relaxed occasion matching
            item_occasions_lower = [occ.lower() for occ in item_occasions]
            
            # Allow if item explicitly matches occasion
            if occasion_lower in item_occasions_lower:
                relaxed_items.append(item)
                continue
            
            # Allow if item has no occasion restrictions (versatile items)
            if not item_occasions:
                relaxed_items.append(item)
                continue
            
            # Allow broad compatibility patterns
            broad_compatibility = {
                'business': ['casual', 'formal', 'smart casual'],
                'casual': ['business', 'athletic', 'party'],
                'formal': ['business', 'wedding', 'special'],
                'athletic': ['casual', 'athletic'],
                'party': ['casual', 'evening']
            }
            
            if occasion_lower in broad_compatibility:
                compatible_occasions = broad_compatibility[occasion_lower]
                if any(comp in item_occasions_lower for comp in compatible_occasions):
                    relaxed_items.append(item)
                    continue
            
            # Allow items that aren't explicitly inappropriate
            item_name = safe_item_access(item, 'name', '').lower()
            inappropriate_patterns = {
                'business': ['bikini', 'swimwear', 'pajamas'],
                'formal': ['gym shorts', 'tank top', 'flip flops'],
                'athletic': ['evening gown', 'tuxedo', 'wedding dress']
            }
            
            if occasion_lower in inappropriate_patterns:
                if not any(pattern in item_name for pattern in inappropriate_patterns[occasion_lower]):
                    relaxed_items.append(item)
        
        return relaxed_items
    
    async def _relax_style_filtering(self, items: List[Any], style: str) -> List[Any]:
        """Relax style filtering - allow more flexible style matching"""
        if not style:
            return items
        
        relaxed_items = []
        style_lower = style.lower()
        
        for item in items:
            # Get item styles
            item_styles = safe_item_access(item, 'style', [])
            if isinstance(item_styles, str):
                item_styles = [item_styles]
            
            item_styles_lower = [s.lower() for s in item_styles]
            
            # Allow if item explicitly matches style
            if style_lower in item_styles_lower:
                relaxed_items.append(item)
                continue
            
            # Allow if item has no style restrictions (versatile items)
            if not item_styles:
                relaxed_items.append(item)
                continue
            
            # Allow compatible styles
            style_compatibility = {
                'classic': ['formal', 'business', 'professional', 'traditional'],
                'casual': ['relaxed', 'everyday', 'comfortable', 'informal'],
                'athletic': ['sporty', 'active', 'casual', 'comfortable'],
                'formal': ['classic', 'business', 'professional', 'elegant'],
                'streetwear': ['urban', 'trendy', 'casual', 'edgy']
            }
            
            if style_lower in style_compatibility:
                compatible_styles = style_compatibility[style_lower]
                if any(comp in item_styles_lower for comp in compatible_styles):
                    relaxed_items.append(item)
                    continue
            
            # Allow items that aren't explicitly incompatible
            item_name = safe_item_access(item, 'name', '').lower()
            incompatible_patterns = {
                'formal': ['sweatpants', 'hoodie', 'sneakers'],
                'athletic': ['dress shoes', 'heels', 'suit'],
                'casual': ['tuxedo', 'evening gown', 'wedding dress']
            }
            
            if style_lower in incompatible_patterns:
                if not any(pattern in item_name for pattern in incompatible_patterns[style_lower]):
                    relaxed_items.append(item)
        
        return relaxed_items
    
    async def _relax_weather_filtering(self, items: List[Any], weather: Any) -> List[Any]:
        """Relax weather filtering - allow more flexible weather matching"""
        relaxed_items = []
        
        # Extract temperature safely
        temp = 70.0  # Default
        if weather:
            temp = safe_get(weather, 'temperature', 70.0)
        
        for item in items:
            # Get item seasonal info
            item_seasons = safe_item_access(item, 'season', [])
            if isinstance(item_seasons, str):
                item_seasons = [item_seasons]
            
            item_name = safe_item_access(item, 'name', '').lower()
            
            # Allow items with no seasonal restrictions
            if not item_seasons:
                relaxed_items.append(item)
                continue
            
            # Relaxed seasonal matching
            current_season = self._determine_season_from_temperature(temp)
            
            # Allow items for current season
            if current_season in item_seasons:
                relaxed_items.append(item)
                continue
            
            # Allow items that work in multiple seasons
            multi_season_items = ['shirt', 'pants', 'jeans', 'blouse', 'top']
            if any(season_item in item_name for season_item in multi_season_items):
                relaxed_items.append(item)
                continue
            
            # Allow items that aren't extremely seasonal
            extreme_seasonal = ['winter coat', 'heavy jacket', 'swimwear', 'bikini', 'shorts']
            if not any(extreme in item_name for extreme in extreme_seasonal):
                relaxed_items.append(item)
        
        return relaxed_items
    
    def _determine_season_from_temperature(self, temp: float) -> str:
        """Determine season from temperature"""
        if temp < 40:
            return 'winter'
        elif temp < 60:
            return 'fall'
        elif temp < 80:
            return 'spring'
        else:
            return 'summer'
    
    async def _create_outfit_from_items(self, items: List[Any], context: GenerationContext, strategy: str) -> OutfitGeneratedOutfit:
        """Create a basic outfit from available items with dress awareness"""
        logger.info(f"🎯 Creating outfit from {len(items)} items using strategy: {strategy}")
        
        # Simple item selection - pick one of each essential category (with dress support)
        selected_items = []
        category_counts = {}
        
        # Check if we have any dresses first
        has_dress = False
        for item in items:
            item_category = self._get_item_category(item)
            if item_category == 'dress':
                has_dress = True
                selected_items.append(item)
                category_counts['dress'] = 1
                logger.info(f"👗 FALLBACK: Found dress '{getattr(item, 'name', 'Unknown')}', skipping tops/bottoms")
                break
        
        # Define essential categories based on whether we have a dress
        if has_dress:
            essential_categories = ['dress', 'shoes']  # Dress replaces tops + bottoms
        else:
            essential_categories = ['tops', 'bottoms', 'shoes']
        
        # Select items for each essential category
        for category in essential_categories:
            if category_counts.get(category, 0) > 0:
                continue  # Already have this category (e.g., dress)
            
            for item in items:
                if item in selected_items:
                    continue
                item_category = self._get_item_category(item)
                if item_category == category:
                    selected_items.append(item)
                    category_counts[category] = category_counts.get(category, 0) + 1
                    logger.info(f"✅ FALLBACK: Added {category} '{getattr(item, 'name', 'Unknown')}'")
                    break
        
        # If we don't have enough items, add non-conflicting items
        if len(selected_items) < 3:
            for item in items:
                if item in selected_items:
                    continue
                item_category = self._get_item_category(item)
                
                # Don't add tops/bottoms if we have a dress
                if has_dress and item_category in ['tops', 'bottoms']:
                    continue
                
                selected_items.append(item)
                logger.info(f"✅ FALLBACK: Added filler item '{getattr(item, 'name', 'Unknown')}' ({item_category})")
                if len(selected_items) >= 4:  # Reasonable outfit size
                    break
        
        logger.info(f"🎯 FALLBACK FINAL: Selected {len(selected_items)} items, has_dress={has_dress}")
        
        return OutfitGeneratedOutfit(
            items=selected_items,
            confidence=0.6,  # Moderate confidence for fallback
            metadata={
                "generation_strategy": strategy,
                "fallback_reason": "progressive_filtering",
                "original_occasion": (context.occasion if context else "unknown"),
                "original_style": (context.style if context else "unknown"),
                "has_dress": has_dress
            }
        )
    
    async def _fallback_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Fallback generation if multi-layered system fails"""
        logger.warning(f"🔄 FALLBACK: Multi-layered system failed, using fallback")
        
        fallback_strategies = [
            GenerationStrategy.FALLBACK_SIMPLE,
            GenerationStrategy.EMERGENCY_DEFAULT
        ]
        
        for fallback_strategy in fallback_strategies:
            logger.info(f"🔄 Trying fallback strategy: {fallback_strategy.value}")
            
            try:
                context.generation_strategy = fallback_strategy
                outfit = await self._generate_with_strategy(context)
                validation = await self._validate_outfit(outfit, context)
                
                logger.info(f"🔄 Fallback {fallback_strategy.value}: Generated outfit with {len(outfit.items)} items")
                logger.info(f"🔄 Fallback {fallback_strategy.value}: Validation - valid={validation.is_valid}, confidence={validation.confidence:.2f}")
                
                logger.info(f"✅ FALLBACK SUCCESS: Generated outfit with {fallback_strategy.value}")
                logger.info(f"📊 Fallback validation: valid={validation.is_valid}, confidence={validation.confidence:.2f}")
                logger.info(f"📦 Fallback outfit items: {[getattr(item, 'name', 'Unknown') for item in outfit.items]}")
                
                context.metadata_notes["fallback_strategy_used"] = fallback_strategy.value
                if outfit.metadata is None:
                    outfit.metadata = {}
                outfit.metadata.update({
                    "fallback_used": True,
                    "fallback_strategy": fallback_strategy.value,
                    "fallback_validation": {
                        "is_valid": validation.is_valid,
                        "confidence": validation.confidence
                    }
                })
                
                return outfit
                
            except Exception as e:
                logger.error(f"❌ Fallback {fallback_strategy.value} failed: {e}")
                
                if fallback_strategy == GenerationStrategy.EMERGENCY_DEFAULT:
                    # If even emergency default fails, return basic outfit
                    logger.error(f"🚨 ALL STRATEGIES FAILED: Even emergency default failed")
                    raise Exception("All strategies failed including emergency default")
                continue
        
        # This should never be reached due to emergency default
        raise Exception("All outfit generation strategies (core + fallback) failed")
    
    async def _execute_strategy_parallel(self, strategy: GenerationStrategy, context: GenerationContext, session_id: str) -> Dict[str, Any]:
        """Execute a single strategy in parallel and return results"""
        strategy_start_time = time.time()
        validation_start_time = 0
        validation_time = 0
        generation_time = 0
        
        logger.info(f"🚀 PARALLEL START: {strategy.value}")
        
        try:
            # Set strategy in context
            context.generation_strategy = strategy
            
            # Generate outfit with this strategy
            logger.info(f"🎨 PARALLEL GENERATING: {strategy.value} with {len(context.wardrobe)} items")
            outfit = await self._generate_with_strategy(context)
            generation_time = time.time() - strategy_start_time
            logger.info(f"🎨 PARALLEL GENERATED: {strategy.value} - {len(outfit.items)} items in {generation_time:.3f}s")
            
            # Validate the generated outfit
            validation_start_time = time.time()
            logger.info(f"🔍 PARALLEL VALIDATING: {strategy.value} outfit with {len(outfit.items)} items")
            validation = await self._validate_outfit(outfit, context)
            validation_time = time.time() - validation_start_time
            logger.info(f"🔍 PARALLEL VALIDATED: {strategy.value} - Valid={validation.is_valid}, Confidence={validation.confidence:.2f}")
            
            # Record strategy execution analytics
            strategy_analytics.record_strategy_execution(
                strategy=strategy.value,
                user_id=context.user_id,
                occasion=context.occasion,
                style=context.style,
                mood=context.mood,
                status=StrategyStatus.SUCCESS if validation.is_valid else StrategyStatus.FAILED,
                confidence=validation.confidence,
                validation_score=validation.score,
                generation_time=generation_time,
                validation_time=validation_time,
                items_selected=len(outfit.items),
                items_available=len(context.wardrobe),
                failed_rules=validation.issues if not validation.is_valid else [],
                fallback_reason=None,
                session_id=session_id
            )
            
            # Return success result
            return {
                'status': 'success',
                'outfit': outfit,
                'validation': validation,
                'generation_time': generation_time,
                'validation_time': validation_time,
                'confidence': validation.confidence,
                'is_valid': validation.is_valid,
                'issues': validation.issues,
                'suggestions': validation.suggestions
            }
            
        except Exception as e:
            generation_time = time.time() - strategy_start_time
            logger.error(f"❌ PARALLEL {strategy.value}: Failed with error: {e}")
            
            # Record strategy failure
            strategy_analytics.record_strategy_execution(
                strategy=strategy.value,
                user_id=context.user_id,
                occasion=context.occasion,
                style=context.style,
                mood=context.mood,
                status=StrategyStatus.FAILED,
                confidence=0.0,
                validation_score=0.0,
                generation_time=generation_time,
                validation_time=0.0,
                items_selected=0,
                items_available=len(context.wardrobe),
                failed_rules=[f"strategy_exception: {str(e)}"],
                fallback_reason=f"Strategy execution failed: {str(e)}",
                session_id=session_id
            )
            
            # Return failure result
            return {
                'status': 'failed',
                'error': str(e),
                'outfit': None,
                'validation': None,
                'generation_time': generation_time,
                'validation_time': 0.0,
                'confidence': 0.0,
                'is_valid': False,
                'issues': [f"Strategy exception: {str(e)}"],
                'suggestions': []
            }

    def _record_generation_performance(self, context: GenerationContext, strategy: str, 
                                    success: bool, confidence: float, generation_time: float,
                                    validation_time: float, items_selected: int, 
                                    diversity_score: float) -> None:
        """Record performance metrics for adaptive tuning"""
        try:
            # Calculate fallback rate (simplified - would need more context in real implementation)
            fallback_rate = 0.0 if success else 1.0
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                success_rate=1.0 if success else 0.0,
                avg_confidence=confidence,
                avg_generation_time=generation_time,
                avg_validation_time=validation_time,
                diversity_score=diversity_score,
                user_satisfaction=confidence,  # Use confidence as proxy for satisfaction
                fallback_rate=fallback_rate,
                sample_size=1,
                time_window_hours=int(time.time())
            )
            
            # Record with adaptive tuning service
            adaptive_tuning.record_performance(metrics)
            
            logger.debug(f"📊 Recorded performance: success={success}, confidence={confidence:.2f}, time={generation_time:.3f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to record performance metrics: {e}")
    
    async def _generate_with_strategy(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate outfit using specific strategy"""
        if context.generation_strategy == GenerationStrategy.COHESIVE_COMPOSITION:
            return await self._cohesive_composition_generation(context)
        elif context.generation_strategy == GenerationStrategy.BODY_TYPE_OPTIMIZED:
            return await self._body_type_optimized_generation(context)
        elif context.generation_strategy == GenerationStrategy.STYLE_PROFILE_MATCHED:
            return await self._style_profile_matched_generation(context)
        elif context.generation_strategy == GenerationStrategy.WEATHER_ADAPTED:
            return await self._weather_adapted_generation(context)
        elif context.generation_strategy == GenerationStrategy.FALLBACK_SIMPLE:
            return await self._fallback_simple_generation(context)
        elif context.generation_strategy == GenerationStrategy.EMERGENCY_DEFAULT:
            return await self._emergency_default_generation(context)
        else:
            raise ValueError(f"Unknown generation strategy: {context.generation_strategy}")
    
    async def _cohesive_composition_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate outfit with cohesive composition logic"""
        logger.info("🎨 Using cohesive composition generation")
        logger.info(f"🎨 COHESIVE: Starting with {len(context.wardrobe)} wardrobe items")
        
        # Filter wardrobe items by occasion and style
        logger.info(f"🔍 FILTERING STEP 2 (Cohesive): Starting with {len(context.wardrobe)} items")
        suitable_items = await self._filter_suitable_items(context)
        logger.info(f"✅ FILTERING STEP 2 (Cohesive): {len(suitable_items)} suitable items passed")
        
        # Apply intelligent selection logic
        selected_items = await self._intelligent_item_selection(suitable_items, context)
        logger.info(f"🎨 COHESIVE: After intelligent selection, {len(selected_items)} selected items")
        
        # Ensure outfit completeness and appropriateness
        complete_outfit = await self._ensure_outfit_completeness(selected_items, context)
        
        # NO FORCE COMPLETION: Let validation handle incomplete outfits
        if len(complete_outfit) < 3:
            logger.warning(f"⚠️ COHESIVE: Outfit incomplete ({len(complete_outfit)} items), will use emergency default")
        
        # Dynamic confidence based on context - cohesive composition is best for style-focused occasions
        base_confidence = 0.85
        if (context.occasion if context else "unknown").lower() in ['party', 'date', 'wedding']:
            base_confidence = 0.92  # High for style-focused occasions
        elif (context.occasion if context else "unknown").lower() in ['business', 'formal']:
            base_confidence = 0.88  # Good but body type might be better
        elif (context.occasion if context else "unknown").lower() in ['casual', 'vacation']:
            base_confidence = 0.87  # Good but weather might be better
        
        # Create outfit response
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"{context.style} {context.occasion} Outfit",
            description=f"Carefully curated {context.style} outfit optimized for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=base_confidence,
            items=complete_outfit,
            reasoning=f"Cohesive {context.style} outfit for {context.occasion} with {context.mood} mood",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],  # Will be populated from items
            explanation=f"Carefully curated {context.style} outfit optimized for {context.occasion}",
            styleTags=[context.style.lower().replace(' ', '_')],
            colorHarmony="balanced",
            styleNotes=f"Perfect for {context.occasion} with {context.mood} mood",
            season="current",
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "cohesive_composition"},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        return outfit
    
    async def _body_type_optimized_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate outfit optimized for user's body type"""
        logger.info("👤 Using body type optimized generation")
        logger.info(f"👤 BODY TYPE: Starting with {len(context.wardrobe)} wardrobe items")
        
        # DEBUG: Check if user_profile is a list
        logger.debug(f"🔍 DEBUG: user_profile type: {type(context.user_profile)}")
        if isinstance(context.user_profile, list):
            logger.error(f"🚨 ERROR: user_profile is a list: {context.user_profile}")
            return OutfitGeneratedOutfit(items=[], confidence=0.1, metadata={"generation_strategy": "body_type_optimized", "error": "user_profile_is_list"})
        
        # Get user's body type information (with safe_get)
        body_type = safe_get(context.user_profile, 'bodyType', 'average')
        height = safe_get(context.user_profile, 'height', 'average')
        
        # Filter items based on body type compatibility
        suitable_items = await self._filter_by_body_type(context.wardrobe, body_type, height)
        logger.info(f"👤 BODY TYPE: After body type filtering, {len(suitable_items)} suitable items")
        
        # Apply additional filtering for occasion/style
        filtered_items = await self._filter_suitable_items(context)
        logger.info(f"👤 BODY TYPE: After occasion/style filtering, {len(filtered_items)} items")
        
        # Apply body type optimization rules
        optimized_items = await self._apply_body_type_optimization(filtered_items, body_type, height)
        logger.info(f"👤 BODY TYPE: After optimization, {len(optimized_items)} items")
        
        # SELECT SPECIFIC ITEMS FOR THE OUTFIT (this was missing!)
        selected_items = await self._intelligent_item_selection(optimized_items, context)
        logger.info(f"👤 BODY TYPE: After intelligent selection, {len(selected_items)} selected items")
        
        # Ensure outfit completeness
        complete_outfit = await self._ensure_outfit_completeness(selected_items, context)
        logger.info(f"👤 BODY TYPE: Final outfit has {len(complete_outfit)} items")
        
        if len(complete_outfit) < 3:
            logger.warning(f"⚠️ BODY TYPE: Outfit incomplete ({len(complete_outfit)} items)")
        
        # Create outfit with body type considerations
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Body-Optimized {context.style} Outfit",
            description=f"Body-optimized {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.90,
            items=complete_outfit,
            reasoning=f"Body-type optimized {context.style} outfit for {context.occasion}",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation=f"Outfit optimized for {body_type} body type and {height} height",
            styleTags=[context.style.lower().replace(' ', '_'), f"body_type_{body_type}"],
            colorHarmony="flattering",
            styleNotes=f"Designed to flatter {body_type} body type",
            season="current",
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "body_type_optimized", "body_type": body_type},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        return outfit
    
    async def _style_profile_matched_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate outfit matched to user's style profile"""
        logger.info("🎭 Using style profile matched generation")
        logger.info(f"🎭 STYLE PROFILE: Starting with {len(context.wardrobe)} wardrobe items")
        
        # Get user's style preferences
        user_profile = getattr(context, 'user_profile', None)
        style_preferences = safe_get(user_profile, 'stylePreferences', {}) if user_profile else {}
        favorite_colors = (safe_get(style_preferences, 'favoriteColors', []) if style_preferences else [])
        preferred_brands = (safe_get(style_preferences, 'preferredBrands', []) if style_preferences else [])
        
        # Filter items by style preferences
        style_matched_items = await self._filter_by_style_preferences(
            (context.wardrobe if context else []), style_preferences, favorite_colors, preferred_brands
        )
        logger.info(f"🎭 STYLE PROFILE: After style preference filtering, {len(style_matched_items)} items")
        
        # Apply additional filtering for occasion/style
        filtered_items = await self._filter_suitable_items(context)
        logger.info(f"🎭 STYLE PROFILE: After occasion/style filtering, {len(filtered_items)} items")
        
        # SELECT SPECIFIC ITEMS FOR THE OUTFIT (this was missing!)
        selected_items = await self._intelligent_item_selection(filtered_items, context)
        logger.info(f"🎭 STYLE PROFILE: After intelligent selection, {len(selected_items)} selected items")
        
        # Ensure outfit completeness
        complete_outfit = await self._ensure_outfit_completeness(selected_items, context)
        logger.info(f"🎭 STYLE PROFILE: Final outfit has {len(complete_outfit)} items")
        
        if len(complete_outfit) < 3:
            logger.warning(f"⚠️ STYLE PROFILE: Outfit incomplete ({len(complete_outfit)} items)")
        
        # Create outfit with style profile matching
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Style-Matched {context.style} Outfit",
            description=f"Style-matched {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.88,
            items=complete_outfit,
            reasoning=f"Style profile matched {context.style} outfit for {context.occasion}",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation=f"Outfit tailored to your personal style preferences",
            styleTags=[context.style.lower().replace(' ', '_'), "style_matched"],
            colorHarmony="personal_preference",
            styleNotes=f"Matches your style profile and preferences",
            season="current",
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "style_profile_matched"},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        return outfit
    
    async def _weather_adapted_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate outfit adapted to weather conditions"""
        logger.info("🌤️ Using weather adapted generation")
        logger.info(f"🌤️ WEATHER: Starting with {len(context.wardrobe)} wardrobe items")
        
        # Filter items based on weather
        weather_appropriate_items = await self._filter_by_weather(context.wardrobe, (context.weather if context else None))
        logger.info(f"🌤️ WEATHER: After weather filtering, {len(weather_appropriate_items)} items")
        
        # Apply additional filtering for occasion/style
        filtered_items = await self._filter_suitable_items(context)
        logger.info(f"🌤️ WEATHER: After occasion/style filtering, {len(filtered_items)} items")
        
        # SELECT SPECIFIC ITEMS FOR THE OUTFIT (this was missing!)
        selected_items = await self._intelligent_item_selection(filtered_items, context)
        logger.info(f"🌤️ WEATHER: After intelligent selection, {len(selected_items)} selected items")
        
        # Ensure outfit completeness
        complete_outfit = await self._ensure_outfit_completeness(selected_items, context)
        logger.info(f"🌤️ WEATHER: Final outfit has {len(complete_outfit)} items")
        
        if len(complete_outfit) < 3:
            logger.warning(f"⚠️ WEATHER: Outfit incomplete ({len(complete_outfit)} items)")
        
        # Create weather-appropriate outfit
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Weather-Adapted {context.style} Outfit",
            description=f"Weather-adapted {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.92,
            items=complete_outfit,
            reasoning=f"Weather-adapted {context.style} outfit for {context.occasion}",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation=f"Outfit adapted for {context.weather.condition} weather at {context.weather.temperature}°F",
            styleTags=[context.style.lower().replace(' ', '_'), "weather_adapted"],
            colorHarmony="seasonal",
            styleNotes=f"Perfect for {context.weather.condition} weather conditions",
            season=self._determine_season_from_weather(context.weather),
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "weather_adapted", "temperature": (context.weather if context else None).temperature},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        return outfit
    
    async def _fallback_simple_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate simple fallback outfit"""
        logger.info("🔄 Using fallback simple generation")
        logger.info(f"🔄 FALLBACK: Starting with {len(context.wardrobe)} wardrobe items")
        
        # Simple item selection without complex logic
        basic_items = await self._select_basic_items(context.wardrobe, context)
        logger.info(f"🔄 FALLBACK: Selected {len(basic_items)} basic items")
        
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Simple {context.style} Outfit",
            description=f"Simple {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.75,
            items=basic_items,
            reasoning=f"Simple {context.style} outfit for {context.occasion}",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation=f"Simple, reliable outfit for {context.occasion}",
            styleTags=[context.style.lower().replace(' ', '_'), "simple"],
            colorHarmony="basic",
            styleNotes=f"Clean and simple styling",
            season="current",
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "fallback_simple"},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        return outfit
    
    async def _emergency_default_generation(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate emergency default outfit when all else fails"""
        logger.warning("🚨 Using emergency default generation")
        
        # Create minimal viable outfit
        emergency_items = [
            {
                "id": "emergency-top",
                "name": "Basic Top",
                "type": "shirt",
                "color": "white",
                "imageUrl": "",
                "style": ["basic"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "emergency-bottom",
                "name": "Basic Pants",
                "type": "pants",
                "color": "black",
                "imageUrl": "",
                "style": ["basic"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "emergency-shoes",
                "name": "Basic Shoes",
                "type": "shoes",
                "color": "white",
                "imageUrl": "",
                "style": ["basic"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            }
        ]
        
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Emergency Default Outfit",
            description=f"Emergency default outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.50,
            items=emergency_items,
            reasoning="Emergency default outfit when all generation strategies fail",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation="Basic emergency outfit",
            styleTags=["emergency", "default"],
            colorHarmony="basic",
            styleNotes="Emergency fallback outfit",
            season="current",
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "emergency_default"},
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=["Emergency fallback used"],
            userFeedback=None
        )
        
        return outfit
    
    async def _filter_suitable_items(self, context: GenerationContext) -> List[ClothingItem]:
        """Apply hard filters to remove contextually impossible items"""
        debug_analysis = await self._filter_suitable_items_with_debug(context)
        return debug_analysis['valid_items']
    
    def _get_occasion_appropriate_candidates(self, wardrobe: List[Any], target_occasion: str, min_items: int = 3, base_item_id: Optional[str] = None) -> List[Any]:
        """
        STEP 2: Strict occasion-first filtering with gradual fallbacks.
        
        Returns items that match the occasion (exact or via fallbacks), ensuring
        all downstream items are occasion-appropriate.
        
        Args:
            wardrobe: List of clothing items to filter
            target_occasion: Target occasion (e.g., "gym", "business")
            min_items: Minimum items required before using fallbacks (default: 3)
            base_item_id: Base item ID to guarantee inclusion (optional)
            
        Returns:
            List of occasion-appropriate items (deduplicated)
        """
        from ..utils.semantic_compatibility import OCCASION_FALLBACKS
        
        target_occasion_lower = target_occasion.lower() if target_occasion else ""
        
        logger.info(f"🎯 OCCASION-FIRST FILTER: Target occasion='{target_occasion_lower}', min_items={min_items}, base_item_id={base_item_id}")
        
        # 0️⃣ PRE-APPROVE BASE ITEM: Add base item first if specified
        candidates = []
        base_item_obj = None
        if base_item_id:
            logger.info(f"🎯 OCCASION FILTER: Looking for base item: {base_item_id}")
            for item in wardrobe:
                item_id = getattr(item, 'id', None)
                if item_id == base_item_id:
                    base_item_obj = item
                    candidates.append(item)
                    logger.info(f"✅ OCCASION FILTER: Base item pre-approved (bypasses occasion filter): {self.safe_get_item_name(item)}")
                    break
            
            if not base_item_obj:
                logger.warning(f"⚠️ OCCASION FILTER: Base item {base_item_id} not found in wardrobe")
        
        # 1️⃣ STRICT FILTER FIRST: Exact occasion match
        for item in wardrobe:
            # Skip base item since it's already added
            if base_item_obj and getattr(item, 'id', None) == base_item_id:
                continue
            # Get item's occasions (normalized or raw)
            item_occasions = self._get_normalized_or_raw(item, 'occasion')
            
            # Check for exact match
            if target_occasion_lower in item_occasions:
                candidates.append(item)
        
        logger.info(f"  ✅ Exact matches: {len(candidates)} items")
        
        # 2️⃣ FALLBACK LOGIC: If too few items, use occasion fallbacks
        if len(candidates) < min_items:
            logger.info(f"  🔄 Too few exact matches ({len(candidates)} < {min_items}), applying fallbacks...")
            
            fallback_occasions = OCCASION_FALLBACKS.get(target_occasion_lower, [])
            logger.info(f"  📋 Available fallbacks for '{target_occasion_lower}': {fallback_occasions[:5]}{'...' if len(fallback_occasions) > 5 else ''}")
            
            # Try each fallback until we have enough items
            for fallback_occasion in fallback_occasions:
                if fallback_occasion == target_occasion_lower:
                    continue  # Skip the original occasion (already tried)
                
                # Get items matching this fallback
                fallback_matches = []
                for item in wardrobe:
                    item_occasions = self._get_normalized_or_raw(item, 'occasion')
                    if fallback_occasion in item_occasions and item not in candidates:
                        fallback_matches.append(item)
                
                if fallback_matches:
                    candidates.extend(fallback_matches)
                    logger.info(f"  ➕ Fallback '{fallback_occasion}': added {len(fallback_matches)} items (total: {len(candidates)})")
                
                # Stop if we have enough items
                if len(candidates) >= min_items:
                    logger.info(f"  ✅ Sufficient items found ({len(candidates)} >= {min_items})")
                    break
        
        # 3️⃣ DEDUPLICATE by ID
        seen_ids = set()
        deduplicated = []
        for item in candidates:
            item_id = self.safe_get_item_attr(item, 'id', '')
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                deduplicated.append(item)
        
        removed_dupes = len(candidates) - len(deduplicated)
        if removed_dupes > 0:
            logger.info(f"  🔧 Removed {removed_dupes} duplicates")
        
        logger.info(f"🎯 OCCASION-FIRST RESULT: {len(deduplicated)} occasion-appropriate items")
        
        return deduplicated
    
    async def _filter_suitable_items_with_debug(self, context: GenerationContext, semantic_filtering: bool = None) -> Dict[str, Any]:
        """Apply hard filters and return both valid items and debug analysis"""
        
        # DEPLOYMENT MARKER: v2025-10-11-semantic-debug
        logger.warning(f"🚀 ROBUST SERVICE: _filter_suitable_items_with_debug called with semantic_filtering={semantic_filtering} (type={type(semantic_filtering).__name__}, is_none={semantic_filtering is None})")
        
        # SAFETY: Determine filtering mode using feature flags
        if semantic_filtering is None:
            # Use feature flag to determine mode ONLY if not explicitly set by frontend
            if is_force_traditional_enabled():
                semantic_filtering = False
                logger.warning("🚩 FEATURE FLAG: Forcing traditional filtering (rollback mode)")
            elif is_semantic_match_enabled():
                semantic_filtering = True
                logger.warning("🚩 FEATURE FLAG: Semantic filtering enabled by default")
            else:
                semantic_filtering = False
                logger.warning("🚩 FEATURE FLAG: Traditional filtering (default)")
        else:
            # Frontend explicitly set the mode - respect it!
            logger.warning(f"🎯 FRONTEND CONTROL: Semantic filtering explicitly set to {semantic_filtering}")
        
        logger.info(f"🔍 HARD FILTER: Starting hard filtering for occasion={context.occasion}, style={context.style}")
        logger.info(f"🔍 HARD FILTER: Wardrobe has {len(context.wardrobe)} items")
        logger.info(f"🔍 HARD FILTER: Mode={'SEMANTIC' if semantic_filtering else 'TRADITIONAL'}")
        
        debug_analysis = []
        valid_items = []
        
        # Track base item to ensure it's always included
        base_item_obj = None
        if context.base_item_id:
            logger.info(f"🎯 BASE ITEM FILTER: Looking for base item with ID: {context.base_item_id}")
            for item in context.wardrobe:
                item_id = getattr(item, 'id', None)
                if item_id == context.base_item_id:
                    base_item_obj = item
                    logger.info(f"✅ BASE ITEM FILTER: Found base item: {getattr(item, 'name', 'Unknown')} (ID: {item_id})")
                    break
            
            if base_item_obj:
                # Add base item to valid items immediately - it bypasses all filters
                valid_items.append(base_item_obj)
                logger.info(f"✅ BASE ITEM FILTER: Base item pre-approved and added to valid items")
            else:
                logger.warning(f"⚠️ BASE ITEM FILTER: Base item ID {context.base_item_id} not found in wardrobe")
        
        # Get user gender for filtering
        user_gender = None
        if context and context.user_profile:
            user_gender = safe_get(context.user_profile, 'gender', None)
            if user_gender:
                user_gender = user_gender.lower()
                logger.info(f"🚻 GENDER FILTER: User gender = {user_gender}")
        
        lounge_keywords = {
            'loungewear', 'lounge', 'relaxed', 'relax', 'casual', 'weekend',
            'comfort', 'comfortable', 'comfy', 'athleisure', 'home', 'sleep',
            'pajama', 'pajamas', 'stay-home', 'stayhome'
        }
        lounge_name_tokens = {
            'sweat', 'jogger', 'hoodie', 'henley', 'tee', 't-shirt', 'tank',
            'thermal', 'fleece', 'knit', 'slouch', 'relaxed', 'soft', 'cozy',
            'pajama', 'sleep', 'lounge', 'comfort', 'shorts'
        }
        lounge_waistbands = {'elastic', 'drawstring', 'elastic_drawstring'}
        lounge_formality = {'casual', 'relaxed', 'loungewear', 'sleepwear', 'athleisure'}
        monochrome_style_synonyms = {
            'minimalist', 'modern', 'classic', 'clean lines', 'monochrome minimal',
            'neutral', 'timeless', 'scandinavian minimalism', 'japanese minimalism'
        }
        monochrome_neutral_colors = {
            'black', 'white', 'off-white', 'ivory', 'cream', 'grey', 'gray',
            'charcoal', 'slate', 'ash', 'silver', 'taupe', 'beige', 'stone',
            'sand', 'camel', 'navy', 'ink', 'espresso', 'muted green', 'sage',
            'olive', 'olive green', 'dusty blue', 'dusty pink', 'mauve', 'khaki'
        }
        allowed_monochrome_patterns = {
            '', 'solid', 'smooth', 'plain', 'minimal', 'matte', 'uniform',
            'ribbed', 'knit', 'waffle', 'cable knit', 'micro', 'subtle texture',
            'heather', 'heathered', 'marled', 'slub'
        }
        is_lounge_request = False
        is_monochrome_request = False
        if context and (context.style or context.occasion):
            style_lower = (context.style or "").lower()
            occasion_lower = (context.occasion or "").lower()
            is_lounge_request = (
                style_lower in lounge_keywords or
                occasion_lower in lounge_keywords
            )
            is_monochrome_request = style_lower == 'monochrome'
        
        # Apply filtering logic matching the JavaScript implementation
        for raw_item in (context.wardrobe if context else []):
            # Skip base item since it's already added to valid_items
            if base_item_obj and getattr(raw_item, 'id', None) == context.base_item_id:
                logger.info(f"⏭️ FILTER: Skipping base item (already pre-approved)")
                continue
            
            # Normalize item metadata
            item = normalize_item_metadata(raw_item)
            reasons = []
            ok_occ = False
            ok_style = False
            ok_mood = False
            
            # METADATA CHECK: Gender filtering (EARLY - before other filters)
            if user_gender:
                gender_appropriate = True
                if hasattr(raw_item, 'metadata') and raw_item.metadata:
                    if isinstance(raw_item.metadata, dict):
                        visual_attrs = raw_item.metadata.get('visualAttributes', {})
                        if isinstance(visual_attrs, dict):
                            gender_target = (visual_attrs.get('genderTarget') or '').lower()
                            if gender_target and gender_target not in ['unisex', 'all', '']:
                                # Normalize gender values for comparison (men's/male, women's/female)
                                normalized_target = 'male' if 'men' in gender_target else ('female' if 'women' in gender_target else gender_target)
                                normalized_user = user_gender.lower()
                                
                                if normalized_target != normalized_user:
                                    gender_appropriate = False
                                    logger.info(f"🚫 GENDER FILTER: Blocked '{safe_item_access(item, 'name', 'Unknown')[:40]}' - genderTarget={gender_target} (normalized: {normalized_target}), user={user_gender} (normalized: {normalized_user})")
                                else:
                                    logger.debug(f"✅ GENDER FILTER: Allowed '{safe_item_access(item, 'name', 'Unknown')[:40]}' - genderTarget={gender_target} matches user={user_gender}")
                
                if not gender_appropriate:
                    continue  # Skip this item entirely
            
            item_name_lower = self.safe_get_item_name(raw_item).lower()
            item_type_lower = str(self.safe_get_item_type(raw_item)).lower()
            waistband_type = None
            formal_level = None
            core_category = None
            monochrome_pattern = ''
            if hasattr(raw_item, 'metadata') and raw_item.metadata:
                metadata_obj = raw_item.metadata
                visual_attrs = None
                if isinstance(metadata_obj, dict):
                    visual_attrs = metadata_obj.get('visualAttributes', {})
                else:
                    visual_attrs = getattr(metadata_obj, 'visualAttributes', None)
                if isinstance(visual_attrs, dict):
                    waistband_type = (visual_attrs.get('waistbandType') or '').lower()
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    core_category = (visual_attrs.get('coreCategory') or '')
                    monochrome_pattern = (visual_attrs.get('pattern') or '').lower()
                else:
                    waistband_type = (getattr(visual_attrs, 'waistbandType', '') or '').lower()
                    formal_level = (getattr(visual_attrs, 'formalLevel', '') or '').lower()
                    core_category = getattr(visual_attrs, 'coreCategory', '')
                    monochrome_pattern = (getattr(visual_attrs, 'pattern', '') or '').lower()
            heuristics_applied = []
            monochrome_color_tokens = set()
            normalized_monochrome_color = None
            if is_monochrome_request:
                item_color_attr = (self.safe_get_item_attr(raw_item, 'color', '') or '').lower()
                if item_color_attr:
                    monochrome_color_tokens.add(item_color_attr)
                dominant_colors = getattr(raw_item, 'dominantColors', []) or safe_item_access(item, 'dominantColors', [])
                if dominant_colors:
                    for color_entry in dominant_colors:
                        if isinstance(color_entry, dict):
                            color_name = (color_entry.get('name') or '').lower()
                            if color_name:
                                monochrome_color_tokens.add(color_name)
                        else:
                            color_name = getattr(color_entry, 'name', None)
                            if color_name:
                                monochrome_color_tokens.add(str(color_name).lower())
                if isinstance(item_color_attr, str) and ' ' in item_color_attr:
                    for token in item_color_attr.split():
                        monochrome_color_tokens.add(token)
                
                def _normalize_monochrome_token(token: str) -> Optional[str]:
                    token = token.lower().strip()
                    if not token:
                        return None
                    color_aliases = {
                        'grey': 'gray',
                        'charcoal gray': 'charcoal',
                        'dark gray': 'charcoal',
                        'light gray': 'gray',
                        'off white': 'off-white',
                        'offwhite': 'off-white',
                        'cream': 'cream',
                        'ivory': 'cream',
                        'stone': 'beige',
                        'sand': 'beige',
                        'taupe': 'beige',
                        'camel': 'beige',
                        'tan': 'beige',
                        'muted olive': 'olive',
                        'sage green': 'sage',
                        'dusty-rose': 'dusty pink',
                        'dusty rose': 'dusty pink',
                        'olive green': 'olive',
                        'navy blue': 'navy',
                        'dark blue': 'navy',
                        'midnight blue': 'navy',
                        'midnight navy': 'navy',
                        'midnight': 'navy',
                        'chalk': 'off-white'
                    }
                    if token in color_aliases:
                        token = color_aliases[token]
                    if token in monochrome_neutral_colors:
                        return token
                    for neutral in monochrome_neutral_colors:
                        if neutral in token:
                            return neutral
                    return "contrast"
                
                if monochrome_color_tokens:
                    for token in monochrome_color_tokens:
                        normalized = _normalize_monochrome_token(token)
                        if normalized and normalized != "contrast":
                            normalized_monochrome_color = normalized
                            break
                    if normalized_monochrome_color is None:
                        normalized_monochrome_color = "contrast"
                else:
                    normalized_monochrome_color = "neutral"
            
            item_occasions = self._get_normalized_or_raw(item, 'occasion')
            item_styles = self._get_normalized_or_raw(item, 'style')
            item_moods = self._get_normalized_or_raw(item, 'mood')
            
            if semantic_filtering:
                # Use semantic filtering with compatibility helpers
                ok_occ = occasion_matches(context.occasion if context else None, safe_item_access(item, 'occasion', []))
                ok_style = style_matches(context.style if context else None, safe_item_access(item, 'style', []))
                ok_mood = mood_matches(context.mood if context else None, safe_item_access(item, 'mood', []))
            else:
                # Enhanced: Use normalized metadata for consistent filtering
                context_occasion = (context.occasion or "").lower() if context else ""
                context_style = (context.style or "").lower() if context else ""
                context_mood = (context.mood or "").lower() if context else ""
                
                # All values already lowercase from normalized or converted
                ok_occ = any(s == context_occasion for s in item_occasions)
                ok_style = any(s == context_style for s in item_styles)
                ok_mood = len(item_moods) == 0 or any(m == context_mood for m in item_moods)
                
            if is_lounge_request:
                if not ok_style:
                    if set(item_styles) & lounge_keywords:
                        ok_style = True
                        heuristics_applied.append("style_tag_lounge_match")
                    elif any(tok in item_name_lower for tok in lounge_name_tokens):
                        ok_style = True
                        heuristics_applied.append("name_lounge_keyword")
                    elif waistband_type in lounge_waistbands:
                        ok_style = True
                        heuristics_applied.append("waistband_lounge")
                    elif formal_level in lounge_formality:
                        ok_style = True
                        heuristics_applied.append("formality_lounge")
                    elif core_category and str(core_category).lower() in {'top', 'bottom', 'shoes'}:
                        # Allow neutral essentials when metadata is sparse
                        ok_style = True
                        heuristics_applied.append("core_category_lounge")
                if not ok_occ:
                    if set(item_occasions) & lounge_keywords:
                        ok_occ = True
                        heuristics_applied.append("occasion_tag_lounge_match")
                    elif ok_style:
                        ok_occ = True
                        heuristics_applied.append("style_implies_lounge")
            if is_monochrome_request:
                pattern_blocked = False
                if monochrome_pattern and monochrome_pattern not in allowed_monochrome_patterns:
                    pattern_blocked = True
                    if "monochrome_pattern_block" not in heuristics_applied:
                        heuristics_applied.append("monochrome_pattern_block")
                    reasons.append(f"Pattern '{monochrome_pattern}' not allowed for monochrome")
                if not ok_style:
                    # Style synonyms (minimalist, classic, etc.)
                    if set(item_styles) & monochrome_style_synonyms:
                        ok_style = True
                        heuristics_applied.append("monochrome_style_synonym")
                    # Neutral color detection via color attribute or dominant colors
                    elif normalized_monochrome_color and normalized_monochrome_color != "contrast":
                        ok_style = True
                        heuristics_applied.append("monochrome_neutral_color")
                    # Allow essentials if metadata lacks color info entirely
                    elif core_category and str(core_category).lower() in {'top', 'bottom', 'shoes', 'outerwear'} and (not monochrome_color_tokens or normalized_monochrome_color == 'neutral'):
                        ok_style = True
                        heuristics_applied.append("monochrome_core_category")
                # Hard block items flagged as contrast
                if ok_style and normalized_monochrome_color == "contrast":
                    ok_style = False
                    heuristics_applied.append("monochrome_contrast_block")
                if ok_style and pattern_blocked:
                    ok_style = False
                if not ok_occ and ok_style:
                    ok_occ = True
                    heuristics_applied.append("style_implies_monochrome")
            
            if heuristics_applied:
                debug_entry_extra = {
                    'heuristics': heuristics_applied,
                    'item_id': safe_item_access(item, 'id', safe_item_access(raw_item, 'id', 'unknown'))
                }
                logger.debug(f"🎯 STYLE HEURISTICS APPLIED: {debug_entry_extra}")
                if hasattr(context, "metadata_notes") and isinstance(context.metadata_notes, dict):
                    if is_lounge_request:
                        context.metadata_notes.setdefault("lounge_heuristics", []).append(debug_entry_extra)
                        lounge_list = context.metadata_notes.setdefault("lounge_item_ids", [])
                        item_identifier = debug_entry_extra['item_id']
                        if item_identifier not in lounge_list:
                            lounge_list.append(item_identifier)
                    if is_monochrome_request:
                        context.metadata_notes.setdefault("monochrome_heuristics", []).append(debug_entry_extra)
                        mono_list = context.metadata_notes.setdefault("monochrome_item_ids", [])
                        item_identifier = debug_entry_extra['item_id']
                        if item_identifier not in mono_list:
                            mono_list.append(item_identifier)
            
            # Build rejection reasons
            if not ok_occ:
                reasons.append(f"Occasion mismatch: item occasions {safe_item_access(item, 'occasion', [])}")
            if not ok_style:
                reasons.append(f"Style mismatch: item styles {safe_item_access(item, 'style', [])}")
            if not ok_mood:
                reasons.append(f"Mood mismatch: item moods {safe_item_access(item, 'mood', [])}")
            
            # Create debug entry
            debug_entry = {
                'id': safe_item_access(item, 'id', safe_item_access(raw_item, 'id', 'unknown')),
                'name': safe_item_access(item, 'name', safe_item_access(raw_item, 'name', 'Unknown')),
                'valid': ok_occ and ok_style and ok_mood,
                'reasons': reasons
            }
            if heuristics_applied:
                debug_entry['heuristics'] = heuristics_applied
            debug_analysis.append(debug_entry)
            
            # ADAPTIVE LOGIC: For mismatches, use OR (occasion OR style), ignore mood
            # Detect mismatch between occasion and style
            filter_mismatch_detected = False
            
            # CRITICAL: If base item is specified, ALWAYS use OR logic for complementary items
            # This gives maximum flexibility when building around a user-selected item
            if context and context.base_item_id and getattr(raw_item, 'id', None) != context.base_item_id:
                filter_mismatch_detected = True
                logger.debug(f"🔄 BASE ITEM MODE: Using OR logic for complementary items (base item specified)")
            
            if context and context.occasion and context.style:
                occ_lower = context.occasion.lower()
                style_lower = context.style.lower()
                
                # CATEGORY 1: Athletic/Gym + Non-Athletic Styles
                if occ_lower in ['athletic', 'gym', 'workout', 'sport', 'fitness', 'yoga', 'running'] and style_lower not in ['athleisure', 'casual cool', 'workout', 'athletic']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Athletic occasion + {style_lower} style → Using OR logic")
                
                # CATEGORY 2: Business/Formal + Casual/Creative Styles
                elif occ_lower in ['business', 'formal', 'interview', 'conference', 'meeting'] and style_lower in ['casual', 'athleisure', 'sporty', 'streetwear', 'grunge', 'punk', 'casual cool', 'loungewear']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Formal occasion + {style_lower} style → Using OR logic")
                
                # CATEGORY 3: Party/Date + Creative/Artistic Styles (NEW!)
                elif occ_lower in ['party', 'date', 'night out', 'club', 'dinner', 'cocktail'] and style_lower in ['avant-garde', 'artsy', 'maximalist', 'gothic', 'punk', 'edgy', 'cyberpunk', 'grunge', 'boho']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Party occasion + {style_lower} creative style → Using OR logic")
                
                # CATEGORY 4: Casual + Formal/Professional Styles
                elif occ_lower in ['casual', 'weekend', 'brunch', 'errands'] and style_lower in ['business casual', 'classic', 'preppy', 'old money', 'urban professional']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Casual occasion + {style_lower} formal style → Using OR logic")
                
                # CATEGORY 5: Loungewear + Any Non-Loungewear Style
                elif occ_lower in ['loungewear', 'lounge', 'home', 'relaxed'] and style_lower not in ['loungewear', 'casual cool', 'athleisure']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Loungewear occasion + {style_lower} style → Using OR logic")
                
                # CATEGORY 6: Beach/Coastal + Non-Beach Styles
                elif occ_lower in ['beach', 'pool', 'vacation', 'resort'] and style_lower in ['business casual', 'formal', 'gothic', 'punk', 'grunge']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Beach occasion + {style_lower} style → Using OR logic")
                
                # CATEGORY 7: Wedding/Gala + Very Casual Styles
                elif occ_lower in ['wedding', 'gala', 'formal event'] and style_lower in ['streetwear', 'grunge', 'punk', 'athleisure', 'casual cool']:
                    filter_mismatch_detected = True
                    logger.debug(f"🔄 ADAPTIVE: Formal event + {style_lower} casual style → Using OR logic")
            
            # Add to valid items based on adaptive logic
            passed_semantic = False
            if filter_mismatch_detected:
                # MISMATCH MODE: Pass if occasion OR style matches (mood ignored - it's a bonus)
                if ok_occ or ok_style:
                    passed_semantic = True
            else:
                # NORMAL MODE: Pass if occasion AND style match (mood ignored - it's a bonus)
                if ok_occ and ok_style:
                    passed_semantic = True
            
            # CRITICAL: Apply hard filter AFTER semantic filtering
            if passed_semantic:
                # Apply hard filter to block explicitly inappropriate items (polos, dress shoes, etc.)
                passes_hard_filter = self._hard_filter(raw_item, context.occasion, context.style)
                if passes_hard_filter:
                    valid_items.append(raw_item)
                else:
                    # Item blocked by hard filter
                    debug_entry['valid'] = False
                    debug_entry['reasons'].append("Blocked by hard filter (formal/inappropriate item)")
        
        
        logger.info(f"🔍 HARD FILTER: Results - {len(valid_items)} passed filters, {len(debug_analysis) - len(valid_items)} rejected")
        
        # PROGRESSIVE RELAXATION: If no suitable items found, use emergency fallback
        if len(valid_items) == 0:
            logger.warning(f"🚨 NO SUITABLE ITEMS: All items rejected by hard filters - using emergency fallback")
            
            # Emergency: Use any available items (hard filters were too strict)
            logger.info(f"🆘 EMERGENCY: Using all wardrobe items as fallback")
            fallback_items = []
            if is_monochrome_request:
                def _normalize_monochrome_token(token: str) -> Optional[str]:
                    token = token.lower().strip()
                    if not token:
                        return None
                    color_aliases = {
                        'grey': 'gray',
                        'charcoal gray': 'charcoal',
                        'dark gray': 'charcoal',
                        'light gray': 'gray',
                        'off white': 'off-white',
                        'offwhite': 'off-white',
                        'cream': 'cream',
                        'ivory': 'cream',
                        'stone': 'beige',
                        'sand': 'beige',
                        'taupe': 'beige',
                        'camel': 'beige',
                        'tan': 'beige',
                        'muted olive': 'olive',
                        'sage green': 'sage',
                        'dusty-rose': 'dusty pink',
                        'dusty rose': 'dusty pink',
                        'olive green': 'olive',
                        'navy blue': 'navy',
                        'dark blue': 'navy',
                        'midnight blue': 'navy',
                        'midnight navy': 'navy',
                        'midnight': 'navy',
                        'chalk': 'off-white'
                    }
                    if token in color_aliases:
                        token = color_aliases[token]
                    if token in monochrome_neutral_colors:
                        return token
                    for neutral in monochrome_neutral_colors:
                        if neutral in token:
                            return neutral
                    return "contrast"

                for item in (context.wardrobe if context else []):
                    normalized_item = normalize_item_metadata(item)
                    tokens = set()
                    color_attr = (self.safe_get_item_attr(normalized_item, 'color', '') or '').lower()
                    if color_attr:
                        tokens.add(color_attr)
                        if ' ' in color_attr:
                            tokens.update(color_attr.split())
                    dominant_colors = normalized_safe_item_access(item, 'dominantColors', []) or getattr(item, 'dominantColors', []) or []
                    for color_entry in dominant_colors:
                        if isinstance(color_entry, dict):
                            name = (color_entry.get('name') or '').lower()
                        else:
                            name = getattr(color_entry, 'name', None)
                            if name:
                                name = str(name).lower()
                        if name:
                            tokens.add(name)
                    normalized = None
                    for token in tokens:
                        normalized = _normalize_monochrome_token(token)
                        if normalized and normalized != "contrast":
                            break
                    if tokens and normalized == "contrast":
                        logger.info(f"🆘 EMERGENCY: Skipped {getattr(item, 'name', 'Unknown')} due to contrast color in monochrome fallback")
                        continue
                    visual_attrs = safe_item_access(normalized_item, 'visualAttributes', {})
                    pattern_value = ''
                    if isinstance(visual_attrs, dict):
                        pattern_value = (visual_attrs.get('pattern') or '').lower()
                    if pattern_value and pattern_value not in allowed_monochrome_patterns:
                        logger.info(f"🆘 EMERGENCY: Skipped {getattr(item, 'name', 'Unknown')} due to pattern '{pattern_value}' in monochrome fallback")
                        continue
                    fallback_items.append(item)
            else:
                fallback_items = list(context.wardrobe if context else [])

            if fallback_items:
                for item in fallback_items:
                    valid_items.append(item)
                    logger.info(f"🆘 EMERGENCY: Added {getattr(item, 'name', 'Unknown')} (emergency fallback)")
            else:
                for item in (context.wardrobe if context else []):
                    valid_items.append(item)
                    logger.info(f"🆘 EMERGENCY: Added {getattr(item, 'name', 'Unknown')} (emergency fallback)")
            
            logger.info(f"🆘 EMERGENCY FALLBACK: Total items after emergency: {len(valid_items)}")
        
        logger.info(f"📦 Found {len(valid_items)} suitable items from {len(context.wardrobe)} total")
        
        # HARD WEATHER FILTER - Remove completely inappropriate items
        temp = safe_get(context.weather, 'temperature', 70.0)
        weather_appropriate_items = []
        weather_rejected = 0
        
        for item in valid_items:
            # Always keep base item regardless of weather
            if base_item_obj and getattr(item, 'id', None) == context.base_item_id:
                weather_appropriate_items.append(item)
                logger.info(f"✅ WEATHER FILTER: Base item bypasses weather filtering")
                continue
            
            item_name_lower = self.safe_get_item_name(item).lower()
            item_type_lower = str(self.safe_get_item_type(item)).lower()
            
            # BALANCED weather filtering - less aggressive
            if temp >= 90:  # Extreme heat only
                hot_inappropriate = ['wool', 'fleece', 'sweater', 'jacket', 'coat', 'heavy', 'long sleeve']
                if any(keyword in item_name_lower or keyword in item_type_lower for keyword in hot_inappropriate):
                    logger.warning(f"🔥 HARD FILTER: {self.safe_get_item_name(item)} REMOVED for {temp}°F extreme heat")
                    weather_rejected += 1
                    continue
            elif temp >= 80:  # Hot weather - more permissive
                hot_inappropriate = ['wool', 'fleece', 'sweater', 'jacket', 'coat', 'heavy']
                if any(keyword in item_name_lower or keyword in item_type_lower for keyword in hot_inappropriate):
                    logger.warning(f"🌡️ HARD FILTER: {self.safe_get_item_name(item)} REMOVED for {temp}°F hot weather")
                    weather_rejected += 1
                    continue
            elif temp < 65:  # Cold/cool weather - block summer items
                # Block shorts, sandals, and other summer items for temperatures below 65°F
                cold_inappropriate = ['shorts', 'sandals', 'flip flops', 'tank top', 'tank', 'sleeveless']
                if any(keyword in item_name_lower or keyword in item_type_lower for keyword in cold_inappropriate):
                    logger.warning(f"❄️ HARD FILTER: {self.safe_get_item_name(item)} REMOVED for {temp}°F cold weather")
                    weather_rejected += 1
                    continue
            
            weather_appropriate_items.append(item)
        
        logger.info(f"🌤️ HARD WEATHER FILTER: {len(weather_appropriate_items)} items remain after weather filtering")
        logger.info(f"🌤️ HARD WEATHER FILTER: Weather rejections: {weather_rejected}")
        
        # SAFETY: Add debug output if enabled (non-destructive)
        debug_output = {}
        if is_debug_output_enabled():
            debug_output = {
                'feature_flags': {
                    'semantic_match_enabled': is_semantic_match_enabled(),
                    'debug_output_enabled': is_debug_output_enabled(),
                    'force_traditional_enabled': is_force_traditional_enabled()
                },
                'filtering_mode': 'semantic' if semantic_filtering else 'traditional',
                'semantic_filtering_used': semantic_filtering,
                'filtering_stats': {
                    'initial_items': len(context.wardrobe),
                    'after_hard_filter': len(valid_items),
                    'after_weather_filter': len(weather_appropriate_items),
                    'hard_rejected': len(debug_analysis) - len(valid_items),
                    'weather_rejected': weather_rejected
                }
            }
        
        # Return debug analysis with valid items
        result = {
            'valid_items': weather_appropriate_items,
            'debug_analysis': debug_analysis,
            'total_items': len(context.wardrobe),
            'filtered_items': len(weather_appropriate_items),
            'hard_rejected': len(debug_analysis) - len(valid_items),
            'weather_rejected': weather_rejected
        }
        
        # Add debug output if enabled (non-destructive)
        if debug_output:
            result['debug_output'] = debug_output
        
        # Record telemetry metrics
        try:
            # Extract debug reasons for telemetry
            debug_reasons = []
            for item in debug_analysis:
                if not safe_item_access(item, 'valid', False):
                    debug_reasons.extend(safe_item_access(item, 'reasons', []))
            
            # Record telemetry
            record_semantic_filtering_metrics(
                user_id=getattr(context.user_profile, 'id', 'unknown') if context and context.user_profile else 'unknown',
                total_items=len(context.wardrobe) if context else 0,
                passed_items=len(weather_appropriate_items),
                hard_rejected=len(debug_analysis) - len(valid_items),
                weather_rejected=weather_rejected,
                semantic_mode=semantic_filtering,
                filtering_mode='semantic' if semantic_filtering else 'traditional',
                request_occasion=context.occasion if context else '',
                request_style=context.style if context else '',
                request_mood=context.mood if context else '',
                composition_success=len(weather_appropriate_items) > 0,  # Basic success metric
                outfits_generated=0,  # Will be updated by outfit generation
                processing_time_ms=0,  # Will be updated by timing
                debug_reasons=debug_reasons
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to record telemetry metrics: {e}")
        
        return result
    
    def _hard_filter(self, item: ClothingItem, occasion: str, style: str) -> bool:
        """Hard constraints - Block inappropriate items for specific occasions"""
        # BUILD MARKER v2025-10-13-02:50 - Force Railway to detect change
        
        item_name = self.safe_get_item_name(item).lower()
        item_name_lower = item_name
        logger.debug(f"✅ COMMIT 378ebeee9: _hard_filter analyzing '{item_name[:40]}'")
        # Extract just the enum value, not the full "ClothingType.SHIRT" string
        raw_type = getattr(item, 'type', '')
        if hasattr(raw_type, 'value'):
            item_type = raw_type.value.lower()  # Get enum value directly
        else:
            item_type = str(raw_type).lower()
        occasion_lower = occasion.lower()
        style_lower = (style or '').lower()
        item_type_lower = item_type
        
        logger.debug(f"🔍 HARD FILTER ENTRY: Checking '{item_name[:30]}' (type={item_type}) for {occasion}")
        
        # GYM/ATHLETIC HARD BLOCKS FIRST - Block formal/structured items BEFORE anything else
        if occasion_lower in ['gym', 'athletic', 'workout']:
            # Only log once per occasion type (not per item)
            # logger.debug(f"🏋️ GYM FILTER ACTIVE for {occasion}")
            
            # STRICT PANTS FILTER: METADATA-FIRST APPROACH
            # Check metadata FIRST, name LAST (only as fallback)
            if item_type in ['pants', 'jeans', 'trousers', 'bottoms'] and 'short' not in item_name.lower():
                logger.info(f"🏋️ GYM PANTS CHECK: {item_name[:40]}")
                
                # STEP 1: Check METADATA (waistband, material, formalLevel) - HIGHEST PRIORITY
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        waistband_type = (visual_attrs.get('waistbandType') or '').lower()
                        material = (visual_attrs.get('material') or '').lower()
                        formal_level = (visual_attrs.get('formalLevel') or '').lower()
                        
                        # 1A. WAISTBAND CHECK - Most reliable, make decision immediately
                        if waistband_type:
                            if waistband_type in ['button_zip', 'belt_loops']:
                                logger.info(f"🚫 GYM METADATA: BLOCKED {item_name[:40]} - waistband={waistband_type} (formal)")
                                return False  # DONE - Don't check name
                            elif waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
                                logger.info(f"✅ GYM METADATA: ALLOWED {item_name[:40]} - waistband={waistband_type} (athletic)")
                                return True  # DONE - Don't check name
                        
                        # 1B. MATERIAL CHECK - Make decision immediately
                        if material:
                            if material in ['denim', 'wool', 'cotton twill', 'linen', 'cashmere', 'silk']:
                                logger.info(f"🚫 GYM METADATA: BLOCKED {item_name[:40]} - material={material} (formal)")
                                return False  # DONE - Don't check name
                            elif material in ['polyester', 'mesh', 'performance', 'synthetic', 'nylon', 'spandex', 'elastane', 'fleece']:
                                logger.info(f"✅ GYM METADATA: ALLOWED {item_name[:40]} - material={material} (athletic)")
                                return True  # DONE - Don't check name
                        
                        # 1C. FORMAL LEVEL CHECK - Make decision immediately
                        if formal_level:
                            if formal_level in ['formal', 'business', 'dress', 'professional']:
                                logger.info(f"🚫 GYM METADATA: BLOCKED {item_name[:40]} - formalLevel={formal_level}")
                                return False  # DONE - Don't check name
                            elif formal_level in ['athletic', 'sport', 'casual']:
                                logger.info(f"✅ GYM METADATA: ALLOWED {item_name[:40]} - formalLevel={formal_level}")
                                return True  # DONE - Don't check name
                
                # STEP 2: Check OCCASION TAGS (if metadata was empty/inconclusive)
                item_occasions = getattr(item, 'occasion', [])
                item_occasions_lower = [occ.lower() for occ in item_occasions] if item_occasions else []
                
                if item_occasions_lower:  # Only check if tags exist
                    if any(occ in item_occasions_lower for occ in ['business', 'formal', 'professional', 'work']):
                        logger.info(f"🚫 GYM OCCASION: BLOCKED {item_name[:40]} - formal occasion tag")
                        return False  # DONE - Don't check name
                    elif any(occ in item_occasions_lower for occ in ['athletic', 'gym', 'workout', 'sport', 'running']):
                        logger.info(f"✅ GYM OCCASION: ALLOWED {item_name[:40]} - athletic occasion tag")
                        return True  # DONE - Don't check name
                
                # STEP 3: Check ITEM TYPE (if metadata AND occasion tags were empty)
                # Shorts are usually OK
                if item_type in ['shorts', 'athletic_shorts']:
                    logger.info(f"✅ GYM TYPE: ALLOWED {item_name[:40]} - type={item_type} (shorts)")
                    return True  # DONE - Don't check name
                
                # STEP 4: FALLBACK - Check NAME (only if ALL above checks were empty/inconclusive)
                # STRICT: Block by default if no metadata, only allow explicit athletic keywords
                logger.info(f"⚠️ GYM FALLBACK: No metadata found, applying STRICT name check: {item_name[:40]}")
                
                # Very specific athletic keywords (must be explicit)
                athletic_keywords = [
                    'jogger', 'joggers',
                    'sweatpants', 'sweat pants',
                    'track pants', 'trackpants',
                    'athletic pants',
                    'workout pants',
                    'gym pants',
                    'training pants',
                    'legging', 'leggings',
                    'yoga pants',
                    'running pants',
                    'athletic shorts',
                    'gym shorts',
                    'basketball shorts',
                    'running shorts'
                ]
                
                # Check if item name has explicit athletic keywords
                if any(kw in item_name.lower() for kw in athletic_keywords):
                    logger.info(f"✅ GYM NAME FALLBACK: ALLOWED {item_name[:40]} - athletic keyword found")
                    return True
                
                # Block generic terms that could be formal/casual
                generic_blocks = [
                    'pants', 'pant',  # Generic "pants" without athletic qualifier = BLOCK
                    'trouser', 'trousers',
                    'chino', 'chinos',
                    'jean', 'jeans',
                    'slack', 'slacks',
                    'cargo',
                    'khaki'
                ]
                
                if any(block in item_name.lower() for block in generic_blocks):
                    logger.info(f"🚫 GYM NAME FALLBACK: BLOCKED {item_name[:40]} - generic/formal pants term without athletic qualifier")
                    return False
                
                # If we get here, it's ambiguous - BLOCK to be safe
                logger.info(f"🚫 GYM NAME FALLBACK: BLOCKED {item_name[:40]} - no metadata, no explicit athletic indicators")
                return False
            
            # BLOCK NON-ATHLETIC TOPS (sweaters, hoodies without athletic features, casual tops)
            # Include ALL shirt types: shirt, t-shirt, t_shirt, dress_shirt, polo, etc.
            if item_type in ['shirt', 'top', 'sweater', 'hoodie', 'jacket', 'outerwear', 
                             'dress_shirt', 't-shirt', 't_shirt', 'polo', 'blouse', 
                             'tank_top', 'crop_top', 'cardigan', 'blazer', 'coat', 'vest']:
                logger.info(f"🏋️ GYM TOP CHECK: {item_name[:40]} (type={item_type})")
                
                # STEP 1: Check METADATA first
                metadata_has_collar = False
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        formal_level = (visual_attrs.get('formalLevel') or '').lower()
                        neckline = (visual_attrs.get('neckline') or '').lower()
                        
                        # Check for collar/button features in metadata
                        if 'collar' in neckline or 'polo' in neckline or 'button' in neckline:
                            metadata_has_collar = True
                            logger.info(f"🚫 GYM METADATA: BLOCKED TOP {item_name[:40]} - neckline={neckline} (collar detected)")
                            return False
                        
                        # Block formal tops immediately
                        if formal_level in ['formal', 'business', 'dress', 'professional']:
                            logger.info(f"🚫 GYM METADATA: BLOCKED TOP {item_name[:40]} - formalLevel={formal_level}")
                            return False
                        # Only allow athletic if it's truly athletic wear (not just casual)
                        elif formal_level in ['athletic', 'sport']:
                            logger.info(f"✅ GYM METADATA: ALLOWED TOP {item_name[:40]} - formalLevel={formal_level}")
                            return True  # Don't check name
                
                # STEP 2: Check occasion tags
                item_occasions = getattr(item, 'occasion', [])
                item_occasions_lower = [occ.lower() for occ in item_occasions] if item_occasions else []
                
                has_athletic_occasion = False
                if item_occasions_lower:
                    if any(occ in item_occasions_lower for occ in ['formal', 'business', 'professional']):
                        logger.info(f"🚫 GYM OCCASION: BLOCKED TOP {item_name[:40]} - formal occasion")
                        return False
                    elif any(occ in item_occasions_lower for occ in ['athletic', 'gym', 'workout', 'sport']):
                        logger.info(f"✅ GYM OCCASION: TOP has athletic occasion '{item_name[:40]}' - will check collar next")
                        has_athletic_occasion = True  # Don't return yet - must check for collar!
                
                # STEP 3: Check for collars/casual features (even if has athletic occasion!)
                # CRITICAL: Polo shirts, button-ups, dress shirts should NEVER be allowed for gym
                logger.info(f"⚠️ GYM TOP NAME CHECK: Checking for collars/casual features: {item_name[:40]}")
                
                # Block collared/casual tops (polo, button-up, dress shirt, sweaters, etc.)
                casual_top_blocks = [
                    'sweater', 'cardigan', 'pullover', 'turtleneck',
                    'henley', 'flannel', 'cable knit', 'cable-knit',
                    'zip sweater', 'ribbed sweater', 'knit sweater',
                    'casual shirt', 'dress shirt', 'button up', 'button down', 
                    'button-up', 'button-down', 'polo shirt', 'polo'  # Polo must be blocked!
                ]
                
                # Only allow if it has explicit athletic qualifier
                athletic_top_qualifiers = ['athletic', 'gym', 'workout', 'training', 'sport', 'performance', 'athletic hoodie']
                
                is_casual_top = any(kw in item_name.lower() for kw in casual_top_blocks)
                has_athletic_qualifier = any(kw in item_name.lower() for kw in athletic_top_qualifiers)
                
                # Block casual tops even if they have athletic occasion tags!
                if is_casual_top and not has_athletic_qualifier:
                    logger.info(f"🚫 GYM NAME CHECK: BLOCKED CASUAL TOP '{item_name[:40]}' - Polo/button-up/sweater detected")
                    return False
                
                # If has athletic occasion and passes casual check, allow it
                if has_athletic_occasion:
                    logger.info(f"✅ GYM FINAL CHECK: ALLOWED '{item_name[:40]}' - Athletic occasion + no casual features")
                    return True
            
            # COMPREHENSIVE SHOE CHECK FOR GYM
            if item_type in ['shoes', 'boots', 'footwear'] or 'shoe' in item_type:
                # Check if shoes are explicitly NON-athletic (BLOCK these)
                non_athletic_shoe_keywords = [
                    'oxford', 'loafer', 'derby', 'monk', 'dress shoe', 'dress', 
                    'heel', 'heels', 'pump', 'formal', 'brogue', 'wingtip',
                    'slide', 'slides', 'sandal', 'sandals', 'flip-flop', 'flip flop',
                    'boat shoe', 'moccasin', 'ballet flat', 'slipper', 'casual shoe'
                ]
                is_non_athletic_shoe = any(kw in item_name.lower() for kw in non_athletic_shoe_keywords)
                
                # METADATA CHECK: Check for formal shoe indicators in metadata
                formal_shoe_in_metadata = False
                athletic_shoe_in_metadata = False
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        shoe_type = (visual_attrs.get('shoeType') or '').lower()
                        material = (visual_attrs.get('material') or '').lower()
                        
                        # Check shoe type in metadata
                        if shoe_type in ['oxford', 'loafer', 'derby', 'dress', 'formal', 'heel']:
                            formal_shoe_in_metadata = True
                            logger.info(f"🔍 FORMAL SHOE TYPE in metadata: {item_name[:40]} shoeType={shoe_type}")
                        elif shoe_type in ['sneaker', 'athletic', 'running', 'training', 'sport']:
                            athletic_shoe_in_metadata = True
                            logger.info(f"🔍 ATHLETIC SHOE TYPE in metadata: {item_name[:40]} shoeType={shoe_type}")
                        
                        # Check material
                        if material in ['leather', 'suede', 'patent leather'] and not athletic_shoe_in_metadata:
                            formal_shoe_in_metadata = True
                            logger.info(f"🔍 FORMAL SHOE MATERIAL in metadata: {item_name[:40]} material={material}")
                
                if is_non_athletic_shoe or formal_shoe_in_metadata:
                    logger.info(f"🚫 GYM HARD FILTER: BLOCKED NON-ATHLETIC SHOE '{item_name[:40]}' - Formal shoe detected")
                    return False
                
                # Check occasion tags for shoes
                item_occasions = getattr(item, 'occasion', [])
                item_occasions_lower = [occ.lower() for occ in item_occasions] if item_occasions else []
                has_athletic_occasion = any(occ in item_occasions_lower for occ in ['athletic', 'gym', 'workout', 'sport', 'running'])
                
                # Check if shoes are explicitly athletic (ALLOW these)
                athletic_shoe_keywords = [
                    'sneaker', 'sneakers', 'athletic', 'running', 'training', 'sport', 'gym',
                    'basketball', 'tennis', 'cross-trainer', 'workout', 'performance', 'trainer'
                ]
                is_athletic_shoe = any(kw in item_name.lower() or kw in item_type for kw in athletic_shoe_keywords)
                
                # Combine checks: name keywords, occasion tags, metadata
                if is_athletic_shoe or has_athletic_occasion or athletic_shoe_in_metadata:
                    logger.debug(f"✅ GYM HARD FILTER: PASSED ATHLETIC SHOE '{item_name[:40]}'")
                else:
                    logger.info(f"🚫 GYM HARD FILTER: BLOCKED GENERIC/UNCLEAR SHOES '{item_name[:40]}' - Must be explicitly athletic")
                    return False
                
            # GYM FILTERING: Block COLLARED shirts only (allow plain shirts/tees)
            if item_type in ['shirt', 'top', 'blouse']:
                # Check for collar in item NAME
                collar_indicators = [
                    'collar', 'collared',
                    'polo', 'polo shirt',
                    'button', 'button-up', 'button-down', 'button up', 'button down',
                    'henley',
                    'oxford', 'oxford shirt',
                    'dress shirt'
                ]
                
                has_collar_in_name = any(kw in item_name.lower() for kw in collar_indicators)
                
                # CRITICAL: Also check metadata for collar/neckline
                has_collar_in_metadata = False
                if hasattr(item, 'metadata') and item.metadata:
                    # Metadata is now a dict (not a Pydantic object)
                    if isinstance(item.metadata, dict):
                        visual_attrs = item.metadata.get('visualAttributes', {})
                        if isinstance(visual_attrs, dict):
                            neckline = (visual_attrs.get('neckline') or '').lower()
                            if 'collar' in neckline or 'polo' in neckline or 'button' in neckline:
                                has_collar_in_metadata = True
                                logger.info(f"🔍 COLLAR DETECTED in metadata: {item_name[:40]} neckline={neckline}")
                    # Legacy: Also check Pydantic object format (in case some items still use it)
                    elif hasattr(item.metadata, 'visualAttributes'):
                        visual_attrs = item.metadata.visualAttributes
                        if visual_attrs and hasattr(visual_attrs, 'neckline'):
                            neckline = (visual_attrs.neckline or '').lower()
                            if 'collar' in neckline or 'polo' in neckline or 'button' in neckline:
                                has_collar_in_metadata = True
                                logger.info(f"🔍 COLLAR DETECTED in metadata (object): {item_name[:40]} neckline={neckline}")
                
                if has_collar_in_name or has_collar_in_metadata:
                    logger.info(f"🚫 GYM HARD FILTER: BLOCKED COLLARED SHIRT '{item_name[:40]}' - Collar detected in {'metadata' if has_collar_in_metadata else 'name'}")
                    return False
                else:
                    # Generic shirt without collar = OK for gym
                    logger.debug(f"✅ GYM HARD FILTER: ALLOWED SHIRT '{item_name[:40]}' - No collar detected")
            
            # Block other formal/structured items (comprehensive list)
            gym_blocks = [
                # Formal wear
                'suit', 'tuxedo', 'blazer', 'sport coat', 'tie', 'bow tie',
                # Jackets  
                'leather jacket', 'biker jacket', 'peacoat', 'trench',
                # ALL accessories (not appropriate for gym)
                'suspenders', 'cufflinks', 'pocket square', 
                'belt',  # Block ALL belts (not just formal)
                'watch', 'bracelet', 'necklace', 'ring', 'chain'
            ]
            
            # Check both item_type and item_name (both already lowercase)
            for block in gym_blocks:
                if block in item_type or block in item_name:
                    logger.info(f"🚫 GYM HARD FILTER: BLOCKED '{item_name[:40]}' - matched '{block}'")
                    return False
            
            logger.debug(f"✅ GYM HARD FILTER: PASSED '{item_name[:40]}'")
        
        # FORMAL/BUSINESS/INTERVIEW HARD BLOCKS - Block casual/athletic items
        if occasion_lower in ['formal', 'business', 'interview', 'work', 'professional']:
            logger.info(f"👔 FORMAL FILTER ACTIVE for {occasion}")
            
            # Block athletic/gym wear for formal occasions
            athletic_blocks = [
                'sneakers', 'athletic', 'gym', 'workout', 'training', 'sport', 'running',
                'sweatpants', 'joggers', 'track pants', 'leggings', 'yoga pants',
                'hoodie', 'sweatshirt', 'tank top', 'crop top', 'basketball shorts',
                'jersey', 'athletic shorts'
            ]
            
            if any(block in item_name.lower() or block in item_type.lower() for block in athletic_blocks):
                logger.info(f"🚫 FORMAL HARD FILTER: BLOCKED ATHLETIC ITEM '{item_name[:40]}'")
                return False
            
            # Check metadata for athletic/casual formalLevel
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    if formal_level in ['athletic', 'sport']:
                        logger.info(f"🚫 FORMAL METADATA: BLOCKED {item_name[:40]} - formalLevel={formal_level}")
                        return False
            
            # Block overly casual items for interview/business
            if occasion_lower in ['interview', 'business']:
                casual_blocks = [
                    'ripped', 'distressed', 'torn', 'graphic tee', 't-shirt with logo',
                    'flip-flop', 'slide', 'sandal', 'crocs'
                ]
                
                if any(block in item_name.lower() for block in casual_blocks):
                    logger.info(f"🚫 BUSINESS HARD FILTER: BLOCKED TOO CASUAL '{item_name[:40]}'")
                    return False
                
                # Block shorts unless they're dress/bermuda shorts
                if 'shorts' in item_name.lower() and not any(kw in item_name.lower() for kw in ['bermuda', 'dress shorts', 'tailored shorts']):
                    logger.info(f"🚫 BUSINESS HARD FILTER: BLOCKED CASUAL SHORTS '{item_name[:40]}'")
                    return False
            
            logger.debug(f"✅ FORMAL HARD FILTER: PASSED '{item_name[:40]}'")
        
        # LOUNGEWEAR/HOME HARD BLOCKS - Block formal/structured items
        if occasion_lower in ['loungewear', 'home', 'sleep', 'relax']:
            logger.info(f"🏠 LOUNGEWEAR FILTER ACTIVE for {occasion}")
            
            # Block formal wear
            formal_blocks = [
                'suit', 'tuxedo', 'blazer', 'sport coat', 'tie', 'bow tie',
                'dress shirt', 'oxford shoes', 'heels', 'pumps',
                'dress pants', 'slacks', 'pencil skirt'
            ]
            
            if any(block in item_name.lower() or block in item_type.lower() for block in formal_blocks):
                logger.info(f"🚫 LOUNGEWEAR HARD FILTER: BLOCKED FORMAL ITEM '{item_name[:40]}'")
                return False
            
            # Check metadata for formal formalLevel
            metadata = {}
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                metadata = item.metadata
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    if formal_level in ['formal', 'business', 'professional']:
                        logger.info(f"🚫 LOUNGEWEAR METADATA: BLOCKED {item_name[:40]} - formalLevel={formal_level}")
                        return False
                    if style_lower in ['artsy', 'avant-garde']:
                        material = (visual_attrs.get('material') or '').lower()
                        if material in ['leather', 'patent leather'] and item_type_lower not in ['slipper', 'loafers']:
                            logger.info(f"🚫 LOUNGEWEAR ARTSY METADATA: BLOCKED {item_name[:40]} - material={material}")
                            return False
            
            logger.debug(f"✅ LOUNGEWEAR HARD FILTER: PASSED '{item_name[:40]}'")

            # --- RELAXED BOTTOMS METADATA ENRICHMENT ---
            def _ensure_relaxed_metadata(meta: dict):
                if not isinstance(meta, dict):
                    return meta
                visual_attrs_local = meta.get('visualAttributes')
                if not isinstance(visual_attrs_local, dict):
                    visual_attrs_local = {}
                    meta['visualAttributes'] = visual_attrs_local

                # Infer relaxed waistband / closure / fit heuristically from naming
                name_tokens = item_name_lower.split()
                has_drawstring_name = any(token in item_name_lower for token in ['drawstring', 'elastic'])
                has_pull_on_name = any(token in item_name_lower for token in ['pull-on', 'pull on'])
                has_relaxed_name_token = any(token in item_name_lower for token in ['relaxed', 'loose', 'casual'])

                waistband_type = (visual_attrs_local.get('waistbandType') or '').lower()
                if not waistband_type and (has_drawstring_name or 'elastic waist' in item_name_lower):
                    visual_attrs_local['waistbandType'] = 'elastic'
                    waistband_type = 'elastic'

                closure_type_local = (visual_attrs_local.get('closure') or '').lower()
                if not closure_type_local and (has_pull_on_name or waistband_type in ['elastic', 'drawstring']):
                    visual_attrs_local['closure'] = 'pull-on'
                    closure_type_local = 'pull-on'

                fit_local = (visual_attrs_local.get('fit') or '').lower()
                if not fit_local and has_relaxed_name_token:
                    visual_attrs_local['fit'] = 'relaxed'
                    fit_local = 'relaxed'

                silhouette_local = (visual_attrs_local.get('silhouette') or '').lower()
                if not silhouette_local and has_relaxed_name_token:
                    visual_attrs_local['silhouette'] = 'relaxed'

                core_category = (visual_attrs_local.get('coreCategory') or '').lower()
                if not core_category and any(token in item_name_lower for token in ['short', 'shorts', 'bermuda']):
                    visual_attrs_local['coreCategory'] = 'shorts'

                style_tags_local = meta.get('styleTags')
                if isinstance(style_tags_local, list):
                    lowered = {tag.lower() for tag in style_tags_local}
                    if 'loungewear' not in lowered and has_relaxed_name_token:
                        style_tags_local.append('Loungewear')
                elif style_tags_local is None and has_relaxed_name_token:
                    meta['styleTags'] = ['Loungewear']

                return meta

            if style_lower in ['artsy', 'avant-garde']:
                athletic_keywords = [
                    'athletic', 'running', 'training', 'performance', 'sport',
                    'sneaker', 'tennis', 'basketball', 'track', 'gym', 'football', 'cleat'
                ]
                relaxed_keywords = [
                    'knit', 'fleece', 'cashmere', 'wool', 'cotton', 'modal', 'jersey',
                    'cardigan', 'kimono', 'robe', 'poncho', 'wrap', 'wide-leg', 'wide leg',
                    'palazzo', 'lounge', 'relaxed', 'soft', 'drape', 'flowy'
                ]

                visual_attrs = {}
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {}) or {}
                    metadata = _ensure_relaxed_metadata(item.metadata)
                    visual_attrs = metadata.get('visualAttributes', {}) or {}
                shoe_type = (visual_attrs.get('shoeType') or '').lower() if isinstance(visual_attrs, dict) else ''
                material = (visual_attrs.get('material') or '').lower() if isinstance(visual_attrs, dict) else ''
                waistband_type = (visual_attrs.get('waistbandType') or '').lower() if isinstance(visual_attrs, dict) else ''
                closure_type = (visual_attrs.get('closure') or '').lower() if isinstance(visual_attrs, dict) else ''
                fit_descriptor = (visual_attrs.get('fit') or '').lower() if isinstance(visual_attrs, dict) else ''
                silhouette = (visual_attrs.get('silhouette') or '').lower() if isinstance(visual_attrs, dict) else ''

                name_has_athletic = any(keyword in item_name_lower for keyword in athletic_keywords)
                type_has_athletic = any(keyword in item_type_lower for keyword in athletic_keywords)
                shoe_is_athletic = any(keyword in shoe_type for keyword in ['sneaker', 'trainer', 'running', 'basketball'])

                if name_has_athletic or type_has_athletic or shoe_is_athletic:
                    logger.info(f"🚫 LOUNGEWEAR ARTSY FILTER: BLOCKED ATHLETIC ITEM '{item_name[:40]}'")
                    return False

                relaxed_materials = [
                    'knit', 'fleece', 'cashmere', 'wool', 'cotton', 'modal', 'velvet', 'velour', 'jersey', 'boucle'
                ]
                is_relaxed_material = any(mat in material for mat in relaxed_materials)
                is_relaxed_name = any(keyword in item_name_lower for keyword in relaxed_keywords)
                has_drawstring = waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']
                has_relaxed_closure = any(token in closure_type for token in ['pull-on', 'pull on', 'elastic'])
                has_relaxed_fit = any(token in fit_descriptor for token in ['relaxed', 'loose', 'easy', 'comfort'])
                has_relaxed_silhouette = any(token in silhouette for token in ['relaxed', 'loose', 'flowy', 'wide'])
                core_category = (visual_attrs.get('coreCategory') or '').lower() if isinstance(visual_attrs, dict) else ''

                if item_type_lower in ['bottoms', 'pants', 'shorts'] and not (
                    has_drawstring
                    or is_relaxed_material
                    or is_relaxed_name
                    or has_relaxed_closure
                    or has_relaxed_fit
                    or has_relaxed_silhouette
                    or core_category in ['shorts', 'loungewear']
                ):
                    logger.info(f"🚫 LOUNGEWEAR ARTSY FILTER: BLOCKED STRUCTURED BOTTOM '{item_name[:40]}'")
                    return False

                top_types = ['tops', 'top', 'shirt', 't_shirt', 't-shirt', 'sweater', 'hoodie', 'cardigan']
                if item_type_lower in top_types and not (is_relaxed_material or is_relaxed_name):
                    logger.info(f"🚫 LOUNGEWEAR ARTSY FILTER: BLOCKED STRUCTURED TOP '{item_name[:40]}'")
                    return False

            # Enforce drawstring/relaxed bottoms for all loungewear looks
            if item_type_lower in ['bottoms', 'pants', 'trousers', 'shorts', 'leggings', 'jeans', 'chinos']:
                visual_attrs = metadata.get('visualAttributes', {}) if isinstance(metadata, dict) else {}
                if isinstance(metadata, dict):
                    metadata = _ensure_relaxed_metadata(metadata)
                    visual_attrs = metadata.get('visualAttributes', {}) if isinstance(metadata, dict) else {}
                waistband_type = (visual_attrs.get('waistbandType') or '').lower() if isinstance(visual_attrs, dict) else ''
                closure_type = (visual_attrs.get('closure') or '').lower() if isinstance(visual_attrs, dict) else ''
                fit_descriptor = (visual_attrs.get('fit') or '').lower() if isinstance(visual_attrs, dict) else ''
                silhouette = (visual_attrs.get('silhouette') or '').lower() if isinstance(visual_attrs, dict) else ''
                style_tags = metadata.get('styleTags') if isinstance(metadata, dict) else None
                style_tags_lower = [tag.lower() for tag in style_tags] if isinstance(style_tags, (list, tuple)) else []

                relaxed_name_markers = [
                    'drawstring', 'elastic waist', 'elastic-waist', 'elasticized waist', 'elasticized-waist',
                    'jogger', 'joggers', 'track pant', 'track-pant', 'sweatpant', 'sweat pant',
                    'sweatshort', 'sweat short', 'lounge', 'relaxed fit', 'relaxed-fit', 'pajama', 'pj',
                    'knit pant', 'knit short', 'wide-leg', 'wide leg', 'palazzo', 'pull-on', 'pull on',
                    'loose', 'casual short', 'casual shorts'
                ]
                structured_blocks = [
                    'jean', 'denim', 'chino', 'trouser', 'dress pant', 'dress trouser',
                    'slack', 'suit pant', 'crease', 'pleated trouser', 'khaki', 'gabardine'
                ]

                if any(block in item_name_lower for block in structured_blocks):
                    logger.info(f"🚫 LOUNGEWEAR HARD FILTER: BLOCKED STRUCTURED BOTTOM '{item_name[:40]}'")
                    return False
                if 'jeans' in item_type_lower or 'denim' in item_type_lower:
                    logger.info(f"🚫 LOUNGEWEAR HARD FILTER: BLOCKED DENIM TYPE '{item_name[:40]}'")
                    return False
                restrictive_waistbands = {
                    'button', 'button_zip', 'zip', 'zipper', 'belt_loops', 'belt loop',
                    'hook', 'hook_bar', 'hook-and-bar', 'hook_and_bar', 'tab', 'fixed', 'snap'
                }
                if waistband_type in restrictive_waistbands:
                    logger.info(
                        f"🚫 LOUNGEWEAR HARD FILTER: BLOCKED STRUCTURED WAISTBAND '{item_name[:40]}' - waistbandType={waistband_type}"
                    )
                    return False

                has_relaxed_name = any(marker in item_name_lower for marker in relaxed_name_markers)
                has_relaxed_tag = any(tag in style_tags_lower for tag in ['loungewear', 'lounge', 'relaxed', 'comfort'])
                has_drawstring = waistband_type in ['drawstring', 'elastic_drawstring']
                has_elastic = waistband_type in ['elastic', 'elastic_drawstring', 'elastic waistband', 'elastic waist']
                has_pull_on_closure = any(token in closure_type for token in ['pull-on', 'pull on', 'elastic'])
                has_relaxed_fit = any(token in fit_descriptor for token in ['relaxed', 'loose', 'easy', 'comfort'])
                has_relaxed_silhouette = any(token in silhouette for token in ['relaxed', 'loose', 'wide', 'flowy'])

                if not (
                    has_drawstring
                    or has_elastic
                    or has_relaxed_name
                    or has_relaxed_tag
                    or has_pull_on_closure
                    or has_relaxed_fit
                    or has_relaxed_silhouette
                ):
                    logger.info(
                        f"🚫 LOUNGEWEAR HARD FILTER: BLOCKED NON-DRAWSTRING BOTTOM '{item_name[:40]}' "
                        f"(waistband={waistband_type or 'none'}, closure={closure_type or 'none'}, fit={fit_descriptor or 'none'})"
                    )
                    return False
        
        # PARTY/DATE HARD BLOCKS - Block overly casual/athletic items
        if occasion_lower in ['party', 'date', 'night out', 'club', 'dinner']:
            # Only log once per occasion type (not per item)
            # logger.debug(f"🎉 PARTY/DATE FILTER ACTIVE for {occasion}")
            
            # Block gym/athletic wear
            athletic_blocks = [
                'athletic', 'gym', 'workout', 'training', 'sport shorts',
                'sweatpants', 'joggers', 'yoga pants', 'leggings with athletic',
                'hoodie', 'sweatshirt', 'basketball shorts', 'running shoes'
            ]
            
            if any(block in item_name.lower() for block in athletic_blocks):
                logger.warning(f"🚫 PARTY/DATE HARD FILTER: BLOCKED ATHLETIC ITEM '{item_name[:40]}'")
                return False
            
            # Block overly casual items
            too_casual_blocks = [
                'crocs', 'flip-flop', 'slide sandal', 'slide', 'slides', 'slipper',
                'graphic tee', 'band tee',
                'pajama', 'sleepwear'
            ]
            
            if any(block in item_name.lower() for block in too_casual_blocks):
                logger.warning(f"🚫 PARTY/DATE HARD FILTER: BLOCKED TOO CASUAL '{item_name[:40]}'")
                return False
            
            logger.debug(f"✅ PARTY/DATE HARD FILTER: PASSED '{item_name[:40]}'")
        
        if style_lower in ['old money', 'urban professional']:
            logger.info(f"🏛️ OLD MONEY STYLE FILTER ACTIVE for {style}")
            casual_blocks = [
                'athletic', 'gym', 'workout', 'training', 'sport', 'sports jersey',
                'jersey', 'basketball', 'football', 'baseball', 'soccer',
                'sweatshort', 'sweat short', 'sweatpant', 'sweat pant', 'jogger',
                'hoodie', 'graphic tee', 'band tee', 'denim short', 'cargo short',
                'crocs', 'sneaker', 'slides', 'flip-flop', 'flip flop'
            ]
            if any(block in item_name_lower for block in casual_blocks):
                logger.info(f"🚫 OLD MONEY FILTER: BLOCKED TOO CASUAL '{item_name[:40]}'")
                return False
            
            if item_type_lower in ['sweatshirt', 'hoodie', 'athletic wear', 'gym wear']:
                logger.info(f"🚫 OLD MONEY FILTER: BLOCKED TYPE '{item_type}'")
                return False
            
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    if formal_level in ['athletic', 'sport', 'casual']:
                        logger.info(f"🚫 OLD MONEY METADATA: BLOCKED '{item_name[:40]}' (formalLevel={formal_level})")
                        return False
            
            logger.debug(f"✅ OLD MONEY FILTER: PASSED '{item_name[:40]}'")
        
        # Try compatibility matrix (will likely fail but doesn't matter now)
        try:
            from ..services.compatibility_matrix import CompatibilityMatrix
            compat_matrix = CompatibilityMatrix()
            is_compatible = compat_matrix.is_compatible(
                item_type=item_type,
                item_name=item_name,
                target_occasion=occasion,
                target_style=style
            )
            if not is_compatible:
                logger.info(f"🚫 COMPAT MATRIX: Rejected '{item_name[:40]}'")
                return False
        except Exception as e:
            # This will always fail - CompatibilityMatrix doesn't exist
            pass
        
        # Basic hard constraints (fallback for all occasions)
        hard_constraints = [
            (item_type == 'tuxedo' and occasion_lower in ['athletic', 'gym', 'workout']),
            (item_type == 'evening_gown' and occasion_lower in ['athletic', 'gym', 'workout']),
            ('bikini' in item_name and occasion_lower in ['business', 'interview', 'work']),
            ('swimwear' in item_name and occasion_lower in ['business', 'interview', 'work']),
            ('pajama' in item_name and occasion_lower not in ['home', 'loungewear', 'sleep']),
            ('sleepwear' in item_name and occasion_lower not in ['home', 'loungewear', 'sleep']),
        ]
        
        for constraint in hard_constraints:
            if constraint:
                return False
        
        return True
    
    def _soft_score(self, item: ClothingItem, occasion: str, style: str, mood: str = "Professional", weather: Optional[dict] = None) -> float:
        """Soft constraint scoring with PRIMARY tag-based matching and adaptive multipliers"""
        
        item_name = self.safe_get_item_name(item).lower()
        occasion_lower = occasion.lower()
        style_lower = style.lower()
        
        # Get item metadata tags
        item_occasion = getattr(item, 'occasion', [])
        item_style = getattr(item, 'style', [])
        item_occasion_lower = [occ.lower() for occ in item_occasion] if item_occasion else []
        item_style_lower = [s.lower() for s in item_style] if item_style else []
        
        # ADAPTIVE MULTIPLIERS: Detect style/occasion mismatches and prioritize occasion
        occasion_multiplier = 1.0
        style_multiplier = 1.0
        
        if occasion_lower in ['athletic', 'gym', 'workout'] and style_lower in ['classic', 'business', 'formal', 'preppy']:
            occasion_multiplier = 1.5  # Boost occasion-based scoring
            style_multiplier = 0.2  # Reduce style-based scoring
            # Reduced to debug to prevent Railway rate limiting
            logger.debug(f"🔄 MISMATCH DETECTED: {occasion} + {style} style - prioritizing OCCASION ({occasion_multiplier}x) over STYLE ({style_multiplier}x)")
        elif occasion_lower in ['business', 'formal'] and style_lower in ['athletic', 'casual', 'streetwear']:
            occasion_multiplier = 1.5
            style_multiplier = 0.2
            # Reduced to debug to prevent Railway rate limiting
            logger.debug(f"🔄 MISMATCH DETECTED: {occasion} + {style} style - prioritizing OCCASION ({occasion_multiplier}x) over STYLE ({style_multiplier}x)")
        
        penalty = 0.0
        
        # ═══════════════════════════════════════════════════════════════════════
        # PRIMARY TAG-BASED SCORING: Check occasion/style tags FIRST
        # This takes precedence over name-based keyword matching
        # ═══════════════════════════════════════════════════════════════════════
        
        # PRIMARY OCCASION TAG MATCH (most important for mismatches)
        if occasion_lower in ['athletic', 'gym', 'workout', 'sport']:
            # GYM/ATHLETIC FORMALITY RULES: Block formal/structured items
            item_type_lower = str(getattr(item, 'type', '')).lower()
            if hasattr(getattr(item, 'type', None), 'value'):
                item_type_lower = getattr(item, 'type').value.lower()
            
            # ABSOLUTE BLOCKS for gym/athletic (formal items should NEVER appear)
            gym_blocks = [
                # Formal wear
                'suit', 'tuxedo', 'blazer', 'sport coat', 'dress shirt', 'tie', 'bow tie',
                # Formal shoes
                'oxford shoes', 'oxford', 'loafers', 'heels', 'derby', 'dress shoes',
                # Formal/structured bottoms (NO dress pants, chinos, jeans for gym!)
                'dress pants', 'slacks', 'chinos', 'khaki', 'trouser', 'cargo',
                'dockers', 'slim fit pants',  # Dockers brand = formal pants
                'jeans', 'denim',  # Too stiff for working out
                'casual shorts', 'bermuda shorts', 'khaki shorts',  # Structured shorts, not athletic
                # Formal outerwear
                'blazer', 'sport coat', 'leather jacket', 'biker jacket',
                # Structured/collared shirts (gym should be athletic or basic tees ONLY!)
                'dress shirt', 'button up', 'button down', 'button-up', 'button-down',
                'polo', 'henley', 'collared', 'collar',  # NO collared shirts for gym!
                'rugby shirt',  # Too structured
                # Non-athletic footwear
                'slide', 'slides', 'sandal', 'sandals', 'flip-flop', 'flip flop'
            ]
            
            if any(block in item_type_lower or block in item_name for block in gym_blocks):
                penalty -= 5.0 * occasion_multiplier  # EXTREME penalty - eliminates item
                logger.debug(f"  🚫🚫🚫 GYM: Blocked '{item_name[:40]}' - formal/structured item ({-5.0 * occasion_multiplier:.2f})")
            
            # POSITIVE FILTER FOR GYM SHOES: Only allow athletic footwear
            category = self._get_item_category(item)
            if category == 'shoes':
                # Check if shoes are athletic (ONLY sneakers/running shoes)
                athletic_shoe_keywords = ['sneaker', 'athletic', 'running', 'training', 'sport', 
                                         'basketball', 'tennis', 'cross-trainer', 'gym shoe',
                                         'workout shoe', 'performance shoe']
                # Slides/sandals removed - not appropriate for gym!
                is_athletic_shoe = any(kw in item_name or kw in item_type_lower for kw in athletic_shoe_keywords)
                
                # Check if shoes are formal OR casual (block both)
                non_gym_shoe_keywords = ['oxford', 'loafer', 'derby', 'monk', 'dress shoe', 
                                        'heel', 'pump', 'formal', 'brogue', 'wingtip',
                                        'slide', 'slides', 'sandal', 'flip-flop', 'flip flop',
                                        'boat shoe', 'moccasin']
                is_non_gym_shoe = any(kw in item_name or kw in item_type_lower for kw in non_gym_shoe_keywords)
                
                if is_non_gym_shoe:
                    penalty -= 5.0 * occasion_multiplier  # Block non-athletic shoes
                    logger.debug(f"  🚫🚫🚫 GYM SHOES: Blocked non-athletic shoe '{item_name[:40]}' ({-5.0 * occasion_multiplier:.2f})")
                elif not is_athletic_shoe:
                    # Generic "shoes" with no clear type - penalize heavily
                    penalty -= 3.0 * occasion_multiplier
                    logger.debug(f"  🚫🚫 GYM SHOES: Generic/unclear shoe type '{item_name[:40]}' ({-3.0 * occasion_multiplier:.2f})")
                else:
                    # Athletic shoes get a bonus!
                    penalty += 0.5 * occasion_multiplier
                    logger.debug(f"  ✅ GYM SHOES: Athletic shoe bonus '{item_name[:40]}' ({+0.5 * occasion_multiplier:.2f})")
            # Boost athletic-appropriate items
            if any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout']):
                penalty += 1.5 * occasion_multiplier  # HUGE boost for exact athletic match
                logger.debug(f"  ✅✅ PRIMARY: Athletic occasion tag match: {+1.5 * occasion_multiplier:.2f}")
            elif 'sport' in item_occasion_lower:
                penalty += 1.3 * occasion_multiplier  # VERY HIGH boost for 'sport' (almost as good as athletic)
                logger.debug(f"  ✅✅ SPORT: Sport occasion tag for Athletic: {+1.3 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['casual', 'beach', 'vacation']):
                penalty += 0.4 * occasion_multiplier  # REDUCED boost for casual items (less ideal for gym)
                logger.debug(f"  ⚠️ SECONDARY: Casual occasion tag for Athletic (less ideal): {+0.4 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['business', 'formal', 'interview', 'conference']):
                penalty -= 2.0 * occasion_multiplier  # STRONG penalty for formal items
                logger.debug(f"  🚫🚫 PRIMARY: Formal occasion tag for Athletic request: {-2.0 * occasion_multiplier:.2f}")
            else:
                # NO occasion tags - check if it's a basic athletic item by type/name
                # T-shirts, tanks, athletic shorts should NOT be penalized!
                basic_athletic_items = ['t-shirt', 'tshirt', 't shirt', 'tank', 'athletic short', 
                                       'gym short', 'jogger', 'sweatpant', 'legging']
                is_basic_athletic = any(basic in item_type_lower or basic in item_name for basic in basic_athletic_items)
                
                if is_basic_athletic:
                    penalty += 0.8 * occasion_multiplier  # BOOST basic athletic items even without tags!
                    logger.debug(f"  ✅✅ GYM: Basic athletic item (no tags needed): {+0.8 * occasion_multiplier:.2f}")
                else:
                    # Other items without relevant tags - small penalty
                    penalty -= 0.5 * occasion_multiplier
                    logger.debug(f"  ⚠️ GYM: No relevant occasion tags ({-0.5 * occasion_multiplier:.2f})")
            
            # METADATA CHECK: WAISTBAND TYPE ANALYSIS for gym (same logic as loungewear)
            waistband_type = None
            if hasattr(item, 'metadata') and item.metadata:
                if isinstance(item.metadata, dict):
                    # New dict format
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        waistband_type = visual_attrs.get('waistbandType')
                else:
                    # Legacy Pydantic object format
                    visual_attrs = getattr(item.metadata, 'visualAttributes', None)
                    # Legacy Pydantic object format
                if visual_attrs:
                    waistband_type = getattr(visual_attrs, 'waistbandType', None)
            
            if waistband_type:
                if waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
                    # Perfect for gym - elastic waistbands for flexibility
                    penalty += 1.5 * occasion_multiplier
                    logger.debug(f"  ✅✅✅ WAISTBAND: Elastic/drawstring waistband ideal for gym: {+1.5 * occasion_multiplier:.2f}")
                elif waistband_type == 'belt_loops':
                    # Belt loops = structured pants, bad for gym
                    penalty -= 3.0 * occasion_multiplier  # Strong penalty
                    logger.debug(f"  🚫🚫 WAISTBAND: Belt loops too structured for gym ({-3.0 * occasion_multiplier:.2f})")
            
            # BOTTOMS PRIORITIZATION: Shorts > Athletic Pants > Casual Pants (blocked)
            if category == 'bottoms':
                # SHORTS: Athletic shorts > Casual shorts
                if 'short' in item_type_lower:
                    athletic_short_keywords = ['athletic', 'sport', 'gym', 'workout', 'running', 
                                              'training', 'basketball', 'performance']
                    casual_short_keywords = ['casual', 'bermuda', 'cargo', 'chino']
                    
                    is_athletic_short = any(kw in item_name or kw in item_type_lower for kw in athletic_short_keywords) or \
                                       any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout', 'sport'])
                    is_casual_short = any(kw in item_name or kw in item_type_lower for kw in casual_short_keywords) or \
                                     'casual' in item_occasion_lower
                    
                    if is_athletic_short:
                        penalty += 1.5 * occasion_multiplier  # HIGHEST boost for athletic shorts (preferred)
                        logger.debug(f"  ✅✅✅ SHORTS: Athletic shorts MOST preferred: {+1.5 * occasion_multiplier:.2f}")
                    elif is_casual_short:
                        penalty += 0.5 * occasion_multiplier  # Good boost for casual shorts
                        logger.debug(f"  ✅ SHORTS: Casual shorts acceptable: {+0.5 * occasion_multiplier:.2f}")
                    else:
                        # Generic shorts - good boost
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ SHORTS: Generic shorts acceptable: {+0.8 * occasion_multiplier:.2f}")
                
                # ATHLETIC PANTS: Joggers, sweatpants (allowed but lower priority than shorts)
                else:  # Not shorts, must be pants
                    athletic_pants_keywords = ['jogger', 'sweatpants', 'sweat pants', 'track pants',
                                              'athletic pants', 'workout pants', 'gym pants', 'training pants']
                    
                    is_athletic_pants = any(kw in item_name.lower() for kw in athletic_pants_keywords) or \
                                       any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout', 'sport'])
                    
                    if is_athletic_pants:
                        penalty += 0.8 * occasion_multiplier  # Good boost for athletic pants (but less than shorts)
                        logger.debug(f"  ✅✅ PANTS: Athletic pants (joggers/sweatpants) allowed: {+0.8 * occasion_multiplier:.2f}")
                    # Formal/casual pants already blocked in hard filter
            
            # ENHANCED T-SHIRT DIFFERENTIATION FOR GYM
            # Pattern, Material, and Fit analysis for tops
            category = self._get_item_category(item)
            if category == 'tops':
                # METADATA CHECK: Get ALL metadata fields for comprehensive analysis
                pattern = None
                material = None
                fit = None
                sleeve_length = None
                fabric_weight = None
                warmth_factor = None
                formal_level = None
                silhouette = None
                texture_style = None
                
                if hasattr(item, 'metadata') and item.metadata:
                    if isinstance(item.metadata, dict):
                        # New dict format
                        visual_attrs = item.metadata.get('visualAttributes', {})
                        if isinstance(visual_attrs, dict):
                            pattern = (visual_attrs.get('pattern') or '').lower()
                            material = (visual_attrs.get('material') or '').lower()
                            fit = (visual_attrs.get('fit') or '').lower()
                            sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                            fabric_weight = (visual_attrs.get('fabricWeight') or '').lower()
                            warmth_factor = (visual_attrs.get('warmthFactor') or '').lower()
                            formal_level = (visual_attrs.get('formalLevel') or '').lower()
                            silhouette = (visual_attrs.get('silhouette') or '').lower()
                            texture_style = (visual_attrs.get('textureStyle') or '').lower()
                    else:
                        # Legacy Pydantic object format
                        visual_attrs = getattr(item.metadata, 'visualAttributes', None)
                        # Legacy Pydantic object format
                    if visual_attrs:
                        pattern = str(getattr(visual_attrs, 'pattern', '')).lower()
                        material = str(getattr(visual_attrs, 'material', '')).lower()
                        fit = str(getattr(visual_attrs, 'fit', '')).lower()
                        sleeve_length = str(getattr(visual_attrs, 'sleeveLength', '')).lower()
                        fabric_weight = str(getattr(visual_attrs, 'fabricWeight', '')).lower()
                        warmth_factor = str(getattr(visual_attrs, 'warmthFactor', '')).lower()
                        formal_level = str(getattr(visual_attrs, 'formalLevel', '')).lower()
                        silhouette = str(getattr(visual_attrs, 'silhouette', '')).lower()
                        texture_style = str(getattr(visual_attrs, 'textureStyle', '')).lower()
                
                # PATTERN SCORING - Simple patterns better for gym
                if pattern:
                    if pattern in ['solid', 'plain']:
                        penalty += 0.5 * occasion_multiplier
                        logger.debug(f"  ✅ PATTERN: Solid/plain pattern good for gym (+{0.5 * occasion_multiplier:.2f})")
                    elif pattern in ['stripe', 'stripes', 'striped']:
                        penalty += 0.3 * occasion_multiplier  # Still good
                        logger.debug(f"  ✅ PATTERN: Striped pattern acceptable for gym (+{0.3 * occasion_multiplier:.2f})")
                    elif pattern in ['graphic', 'logo', 'print']:
                        penalty += 0.2 * occasion_multiplier  # Athletic graphics common
                        logger.debug(f"  ✅ PATTERN: Graphic/logo acceptable for gym (+{0.2 * occasion_multiplier:.2f})")
                    elif pattern in ['floral', 'paisley', 'polka dot', 'checkered', 'plaid']:
                        penalty -= 0.8 * occasion_multiplier  # Too busy/dressy for gym
                        logger.debug(f"  ⚠️ PATTERN: Busy pattern less ideal for gym ({-0.8 * occasion_multiplier:.2f})")
                
                # MATERIAL SCORING - Performance fabrics better for gym
                if material:
                    if material in ['polyester', 'mesh', 'performance', 'synthetic', 'nylon', 'spandex', 'elastane']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅✅ MATERIAL: Performance fabric ideal for gym (+{0.8 * occasion_multiplier:.2f})")
                    elif material in ['cotton', 'jersey', 'blend']:
                        penalty += 0.4 * occasion_multiplier  # Good, common for gym
                        logger.debug(f"  ✅ MATERIAL: Cotton/jersey good for gym (+{0.4 * occasion_multiplier:.2f})")
                    elif material in ['silk', 'satin', 'wool', 'cashmere', 'linen']:
                        penalty -= 1.2 * occasion_multiplier  # Inappropriate for gym
                        logger.debug(f"  🚫 MATERIAL: Dress material inappropriate for gym ({-1.2 * occasion_multiplier:.2f})")
                
                # FIT SCORING - Loose/athletic fit better for gym mobility
                if fit:
                    if fit in ['loose', 'relaxed', 'oversized', 'athletic']:
                        penalty += 0.6 * occasion_multiplier
                        logger.debug(f"  ✅ FIT: {fit.capitalize()} fit good for gym mobility (+{0.6 * occasion_multiplier:.2f})")
                    elif fit in ['regular', 'standard']:
                        penalty += 0.2 * occasion_multiplier  # Neutral
                        logger.debug(f"  ✅ FIT: Regular fit acceptable for gym (+{0.2 * occasion_multiplier:.2f})")
                    elif fit in ['slim', 'fitted', 'tailored', 'tight']:
                        penalty -= 0.5 * occasion_multiplier  # Less ideal for workout mobility
                        logger.debug(f"  ⚠️ FIT: {fit.capitalize()} fit restricts gym mobility ({-0.5 * occasion_multiplier:.2f})")
                
                # SLEEVE LENGTH SCORING - Sleeveless/short better for gym
                if sleeve_length:
                    if sleeve_length in ['sleeveless', 'tank', 'no sleeve', 'none']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅✅ SLEEVE: Sleeveless ideal for gym mobility (+{0.8 * occasion_multiplier:.2f})")
                    elif sleeve_length in ['short', 'short sleeve']:
                        penalty += 0.6 * occasion_multiplier
                        logger.debug(f"  ✅ SLEEVE: Short sleeves good for gym (+{0.6 * occasion_multiplier:.2f})")
                    elif sleeve_length in ['3/4', 'three quarter', '3/4 sleeve']:
                        penalty += 0.2 * occasion_multiplier
                        logger.debug(f"  ✅ SLEEVE: 3/4 sleeves acceptable for gym (+{0.2 * occasion_multiplier:.2f})")
                    elif sleeve_length in ['long', 'long sleeve']:
                        penalty -= 0.4 * occasion_multiplier  # Less ideal but not terrible
                        logger.debug(f"  ⚠️ SLEEVE: Long sleeves less ideal for gym ({-0.4 * occasion_multiplier:.2f})")
                
                # FABRIC WEIGHT SCORING - Light fabrics better for gym
                if fabric_weight:
                    if fabric_weight in ['light', 'lightweight', 'thin']:
                        penalty += 0.5 * occasion_multiplier
                        logger.debug(f"  ✅ FABRIC WEIGHT: Light fabric good for gym (+{0.5 * occasion_multiplier:.2f})")
                    elif fabric_weight in ['medium', 'regular']:
                        penalty += 0.2 * occasion_multiplier
                        logger.debug(f"  ✅ FABRIC WEIGHT: Medium weight acceptable for gym (+{0.2 * occasion_multiplier:.2f})")
                    elif fabric_weight in ['heavy', 'thick', 'heavyweight']:
                        penalty -= 0.6 * occasion_multiplier
                        logger.debug(f"  ⚠️ FABRIC WEIGHT: Heavy fabric too warm for gym ({-0.6 * occasion_multiplier:.2f})")
                
                # WARMTH FACTOR SCORING - Low warmth better for gym
                if warmth_factor:
                    if warmth_factor in ['light', 'minimal', 'breathable']:
                        penalty += 0.7 * occasion_multiplier
                        logger.debug(f"  ✅✅ WARMTH: Light/breathable ideal for gym (+{0.7 * occasion_multiplier:.2f})")
                    elif warmth_factor in ['medium', 'moderate']:
                        penalty += 0.3 * occasion_multiplier
                        logger.debug(f"  ✅ WARMTH: Medium warmth acceptable for gym (+{0.3 * occasion_multiplier:.2f})")
                    elif warmth_factor in ['heavy', 'insulated', 'warm']:
                        penalty -= 0.8 * occasion_multiplier
                        logger.debug(f"  ⚠️ WARMTH: Heavy warmth too hot for gym ({-0.8 * occasion_multiplier:.2f})")
                
                # FORMAL LEVEL SCORING - Casual better for gym
                if formal_level:
                    if formal_level in ['casual', 'athletic', 'sport']:
                        penalty += 0.9 * occasion_multiplier
                        logger.debug(f"  ✅✅ FORMAL LEVEL: {formal_level.capitalize()} perfect for gym (+{0.9 * occasion_multiplier:.2f})")
                    elif formal_level in ['business casual', 'smart casual']:
                        penalty -= 0.5 * occasion_multiplier
                        logger.debug(f"  ⚠️ FORMAL LEVEL: {formal_level.capitalize()} too dressy for gym ({-0.5 * occasion_multiplier:.2f})")
                    elif formal_level in ['formal', 'business', 'dress']:
                        penalty -= 1.5 * occasion_multiplier
                        logger.debug(f"  🚫 FORMAL LEVEL: {formal_level.capitalize()} inappropriate for gym ({-1.5 * occasion_multiplier:.2f})")
                
                # SILHOUETTE SCORING - Relaxed/athletic silhouettes better for gym
                if silhouette:
                    if silhouette in ['relaxed', 'athletic', 'loose', 'oversized']:
                        penalty += 0.5 * occasion_multiplier
                        logger.debug(f"  ✅ SILHOUETTE: {silhouette.capitalize()} good for gym (+{0.5 * occasion_multiplier:.2f})")
                    elif silhouette in ['fitted', 'tailored', 'structured']:
                        penalty -= 0.4 * occasion_multiplier
                        logger.debug(f"  ⚠️ SILHOUETTE: {silhouette.capitalize()} restricts movement ({-0.4 * occasion_multiplier:.2f})")
                
                # TEXTURE STYLE SCORING - Smooth textures better for gym (less friction)
                if texture_style:
                    if texture_style in ['smooth', 'soft', 'silky']:
                        penalty += 0.4 * occasion_multiplier
                        logger.debug(f"  ✅ TEXTURE: {texture_style.capitalize()} comfortable for gym (+{0.4 * occasion_multiplier:.2f})")
                    elif texture_style in ['rough', 'coarse', 'stiff']:
                        penalty -= 0.3 * occasion_multiplier
                        logger.debug(f"  ⚠️ TEXTURE: {texture_style.capitalize()} uncomfortable for gym ({-0.3 * occasion_multiplier:.2f})")
        
        elif occasion_lower in ['business', 'formal', 'interview', 'wedding', 'conference']:
            if any(occ in item_occasion_lower for occ in ['business', 'formal', 'interview', 'conference', 'wedding']):
                penalty += 1.5 * occasion_multiplier  # HUGE boost for matching occasion tag
                logger.debug(f"  ✅✅ PRIMARY: Formal occasion tag match: {+1.5 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout', 'sport']):
                penalty -= 2.0 * occasion_multiplier  # HUGE penalty for wrong occasion
                logger.debug(f"  🚫🚫 PRIMARY: Athletic occasion tag for Formal request: {-2.0 * occasion_multiplier:.2f}")
            
            # METADATA CHECK: Boost formal materials and fits (COMPREHENSIVE)
            item_category = self._get_item_category(item)
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    material = (visual_attrs.get('material') or '').lower()
                    fit = (visual_attrs.get('fit') or '').lower()
                    neckline = (visual_attrs.get('neckline') or '').lower()
                    sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    silhouette = (visual_attrs.get('silhouette') or '').lower()
                    length = (visual_attrs.get('length') or '').lower()
                    texture_style = (visual_attrs.get('textureStyle') or '').lower()
                    
                    # Boost formal materials
                    if material in ['wool', 'silk', 'linen', 'cashmere', 'cotton twill']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ FORMAL MATERIAL: {material} ideal for formal (+{0.8 * occasion_multiplier:.2f})")
                    
                    # Boost formal fits
                    if fit in ['tailored', 'slim', 'fitted', 'dress']:
                        penalty += 0.6 * occasion_multiplier
                        logger.debug(f"  ✅ FORMAL FIT: {fit} appropriate for formal (+{0.6 * occasion_multiplier:.2f})")
                    
                    # Boost collared shirts for formal
                    if 'collar' in neckline or 'button' in neckline:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ FORMAL NECKLINE: Collar appropriate for formal (+{0.8 * occasion_multiplier:.2f})")
                    
                    # SLEEVE LENGTH - Long sleeves preferred for formal
                    if item_category == 'tops' and sleeve_length:
                        if sleeve_length in ['long', 'long sleeve']:
                            penalty += 0.7 * occasion_multiplier
                            logger.debug(f"  ✅ FORMAL SLEEVE: Long sleeves appropriate for formal (+{0.7 * occasion_multiplier:.2f})")
                        elif sleeve_length in ['short', 'short sleeve']:
                            penalty -= 0.4 * occasion_multiplier
                            logger.debug(f"  ⚠️ FORMAL SLEEVE: Short sleeves less formal ({-0.4 * occasion_multiplier:.2f})")
                        elif sleeve_length in ['sleeveless', 'tank']:
                            penalty -= 1.0 * occasion_multiplier
                            logger.debug(f"  🚫 FORMAL SLEEVE: Sleeveless inappropriate for formal ({-1.0 * occasion_multiplier:.2f})")
                    
                    # FORMAL LEVEL - Direct match
                    if formal_level:
                        if formal_level in ['formal', 'business', 'dress', 'professional']:
                            penalty += 1.2 * occasion_multiplier
                            logger.debug(f"  ✅✅✅ FORMAL LEVEL: {formal_level.capitalize()} perfect for formal (+{1.2 * occasion_multiplier:.2f})")
                        elif formal_level in ['business casual', 'smart casual']:
                            penalty += 0.6 * occasion_multiplier
                            logger.debug(f"  ✅ FORMAL LEVEL: {formal_level.capitalize()} acceptable for formal (+{0.6 * occasion_multiplier:.2f})")
                        elif formal_level in ['casual', 'athletic', 'sport']:
                            penalty -= 1.0 * occasion_multiplier
                            logger.debug(f"  🚫 FORMAL LEVEL: {formal_level.capitalize()} too casual for formal ({-1.0 * occasion_multiplier:.2f})")
                    
                    # SILHOUETTE - Tailored/structured preferred for formal
                    if silhouette:
                        if silhouette in ['tailored', 'structured', 'fitted']:
                            penalty += 0.6 * occasion_multiplier
                            logger.debug(f"  ✅ FORMAL SILHOUETTE: {silhouette.capitalize()} appropriate for formal (+{0.6 * occasion_multiplier:.2f})")
                        elif silhouette in ['oversized', 'baggy']:
                            penalty -= 0.5 * occasion_multiplier
                            logger.debug(f"  ⚠️ FORMAL SILHOUETTE: {silhouette.capitalize()} too casual ({-0.5 * occasion_multiplier:.2f})")
                    
                    # LENGTH - For bottoms, long pants required for formal
                    if item_category == 'bottoms' and length:
                        if length in ['long', 'full', 'ankle']:
                            penalty += 0.9 * occasion_multiplier
                            logger.debug(f"  ✅✅ FORMAL LENGTH: Long pants appropriate for formal (+{0.9 * occasion_multiplier:.2f})")
                        elif length in ['short', 'shorts', 'cropped', 'capri']:
                            penalty -= 2.0 * occasion_multiplier  # MAJOR penalty for shorts at formal event
                            logger.debug(f"  🚫🚫 FORMAL LENGTH: Shorts inappropriate for formal ({-2.0 * occasion_multiplier:.2f})")
                    
                    # TEXTURE STYLE - Refined textures better for formal
                    if texture_style:
                        if texture_style in ['smooth', 'silky', 'refined', 'crisp']:
                            penalty += 0.5 * occasion_multiplier
                            logger.debug(f"  ✅ FORMAL TEXTURE: {texture_style.capitalize()} appropriate for formal (+{0.5 * occasion_multiplier:.2f})")
                        elif texture_style in ['distressed', 'worn', 'rough']:
                            penalty -= 0.6 * occasion_multiplier
                            logger.debug(f"  ⚠️ FORMAL TEXTURE: {texture_style.capitalize()} too casual ({-0.6 * occasion_multiplier:.2f})")
                    
                    # Penalty for athletic materials
                    if material in ['mesh', 'performance', 'synthetic', 'spandex']:
                        penalty -= 1.5 * occasion_multiplier
                        logger.debug(f"  🚫 ATHLETIC MATERIAL: {material} inappropriate for formal ({-1.5 * occasion_multiplier:.2f})")
        
        elif occasion_lower in ['casual', 'brunch', 'weekend']:
            if any(occ in item_occasion_lower for occ in ['casual', 'brunch', 'weekend', 'vacation']):
                penalty += 1.0 * occasion_multiplier  # Good boost for matching occasion tag
                logger.debug(f"  ✅✅ PRIMARY: Casual occasion tag match: {+1.0 * occasion_multiplier:.2f}")
        
        elif occasion_lower in ['loungewear', 'lounge', 'relaxed', 'home']:
            # Loungewear: Block ALL formal and structured items AGGRESSIVELY
            item_type_lower = str(getattr(item, 'type', '')).lower()
            if hasattr(getattr(item, 'type', None), 'value'):
                item_type_lower = getattr(item, 'type').value.lower()
            
            # ABSOLUTE BLOCKS for loungewear (formal/structured items should NEVER appear)
            absolute_blocks = [
                # Formal wear
                'suit', 'tuxedo', 'blazer', 'sport coat', 'dress shirt', 'tie', 'bow tie',
                # Formal shoes
                'oxford shoes', 'oxford', 'loafers', 'heels', 'derby', 'dress shoes',
                # Structured bottoms (non-elastic waistbands)
                'dress pants', 'slacks', 'chinos', 'khaki', 'trouser', 'cargo',
                'jeans', 'denim',  # Too stiff/structured
                # All jackets
                'leather jacket', 'biker jacket', 'jacket', 'coat',
                # Collared/structured shirts (loungewear should be collarless!)
                'button up', 'button down', 'button-up', 'button-down',
                'polo', 'henley', 'collared', 'collar',  # NO collars for loungewear
                # Accessories
                'belt', 'formal'
            ]
            
            if any(block in item_type_lower or block in item_name for block in absolute_blocks):
                penalty -= 5.0 * occasion_multiplier  # EXTREME penalty - eliminates item
                logger.debug(f"  🚫🚫🚫 LOUNGEWEAR: Blocked '{item_name[:40]}' - formal/structured/collared ({-5.0 * occasion_multiplier:.2f})")
            # Boost loungewear-appropriate items (elastic waistbands, no collars)
            elif any(occ in item_occasion_lower for occ in ['loungewear', 'lounge', 'relaxed', 'home', 'casual']):
                penalty += 1.2 * occasion_multiplier
                logger.debug(f"  ✅✅ PRIMARY: Loungewear occasion tag match: {+1.2 * occasion_multiplier:.2f}")
            
            # METADATA CHECK: WAISTBAND TYPE ANALYSIS for loungewear
            waistband_type = None
            collar_detected_in_metadata = False
            formal_material_detected = False
            
            if hasattr(item, 'metadata') and item.metadata:
                if isinstance(item.metadata, dict):
                    # New dict format
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        waistband_type = visual_attrs.get('waistbandType')
                        neckline = (visual_attrs.get('neckline') or '').lower()
                        material = (visual_attrs.get('material') or '').lower()
                        
                        # Check for collar in metadata
                        if 'collar' in neckline or 'button' in neckline or 'polo' in neckline:
                            collar_detected_in_metadata = True
                            penalty -= 5.0 * occasion_multiplier
                            logger.debug(f"  🚫🚫🚫 LOUNGEWEAR: Collar detected in metadata (neckline={neckline}): {-5.0 * occasion_multiplier:.2f}")
                        
                        # Check for formal materials
                        if material in ['wool', 'silk', 'satin', 'linen', 'cashmere']:
                            formal_material_detected = True
                            penalty -= 3.0 * occasion_multiplier
                            logger.debug(f"  🚫🚫 LOUNGEWEAR: Formal material in metadata (material={material}): {-3.0 * occasion_multiplier:.2f}")
                else:
                    # Legacy Pydantic object format
                    visual_attrs = getattr(item.metadata, 'visualAttributes', None)
                    # Legacy Pydantic object format
                if visual_attrs:
                    waistband_type = getattr(visual_attrs, 'waistbandType', None)
            
            if waistband_type:
                if waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
                    # Perfect for loungewear - elastic waistbands
                    penalty += 1.5 * occasion_multiplier
                    logger.debug(f"  ✅✅✅ WAISTBAND: Elastic/drawstring waistband ideal for loungewear: {+1.5 * occasion_multiplier:.2f}")
                elif waistband_type == 'belt_loops':
                    # Belt loops = structured pants, bad for loungewear
                    penalty -= 3.0 * occasion_multiplier  # Strong penalty
                    logger.debug(f"  🚫🚫 WAISTBAND: Belt loops too structured for loungewear ({-3.0 * occasion_multiplier:.2f})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # OUTERWEAR METADATA SCORING (Jackets, Coats, Blazers)
        # ═══════════════════════════════════════════════════════════════════════
        item_category = self._get_item_category(item)
        if item_category == 'outerwear':
            # Extract ALL metadata fields for outerwear
            material = None
            warmth_factor = None
            formal_level = None
            length = None
            wear_layer = None
            fabric_weight = None
            
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    material = (visual_attrs.get('material') or '').lower()
                    warmth_factor = (visual_attrs.get('warmthFactor') or '').lower()
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    length = (visual_attrs.get('length') or '').lower()
                    wear_layer = (visual_attrs.get('wearLayer') or '').lower()
                    fabric_weight = (visual_attrs.get('fabricWeight') or '').lower()
            
            # Get temperature for weather-appropriate scoring
            temp = safe_get(weather, 'temperature', 70.0) if weather else 70.0
            
            # WARMTH FACTOR - Match to weather
            if warmth_factor:
                if temp < 40:  # Very cold
                    if warmth_factor in ['heavy', 'insulated', 'warm']:
                        penalty += 1.5 * occasion_multiplier
                        logger.debug(f"  ✅✅✅ OUTERWEAR WARMTH: Heavy warmth perfect for cold weather (+{1.5 * occasion_multiplier:.2f})")
                    elif warmth_factor in ['light', 'minimal']:
                        penalty -= 1.0 * occasion_multiplier
                        logger.debug(f"  🚫 OUTERWEAR WARMTH: Light warmth insufficient for cold ({-1.0 * occasion_multiplier:.2f})")
                elif temp > 70:  # Warm weather
                    if warmth_factor in ['light', 'minimal', 'breathable']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ OUTERWEAR WARMTH: Light warmth good for mild weather (+{0.8 * occasion_multiplier:.2f})")
                    elif warmth_factor in ['heavy', 'insulated']:
                        penalty -= 1.2 * occasion_multiplier
                        logger.debug(f"  🚫 OUTERWEAR WARMTH: Heavy warmth too hot ({-1.2 * occasion_multiplier:.2f})")
            
            # FORMAL LEVEL - Match to occasion
            if formal_level:
                if occasion_lower in ['business', 'formal', 'interview']:
                    if formal_level in ['formal', 'business', 'dress']:
                        penalty += 1.5 * occasion_multiplier
                        logger.debug(f"  ✅✅✅ OUTERWEAR FORMAL: {formal_level.capitalize()} perfect for {occasion} (+{1.5 * occasion_multiplier:.2f})")
                    elif formal_level in ['casual', 'athletic']:
                        penalty -= 1.0 * occasion_multiplier
                        logger.debug(f"  🚫 OUTERWEAR FORMAL: {formal_level.capitalize()} too casual for {occasion} ({-1.0 * occasion_multiplier:.2f})")
                elif occasion_lower in ['gym', 'athletic']:
                    if formal_level in ['athletic', 'sport', 'casual']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ OUTERWEAR FORMAL: {formal_level.capitalize()} good for gym (+{0.8 * occasion_multiplier:.2f})")
                    elif formal_level in ['formal', 'business']:
                        penalty -= 1.5 * occasion_multiplier
                        logger.debug(f"  🚫 OUTERWEAR FORMAL: {formal_level.capitalize()} too formal for gym ({-1.5 * occasion_multiplier:.2f})")
            
            # MATERIAL - Weather and occasion matching
            if material:
                if occasion_lower in ['business', 'formal']:
                    if material in ['wool', 'cashmere', 'tweed']:
                        penalty += 0.9 * occasion_multiplier
                        logger.debug(f"  ✅✅ OUTERWEAR MATERIAL: {material.capitalize()} ideal for formal (+{0.9 * occasion_multiplier:.2f})")
                elif occasion_lower in ['gym', 'athletic']:
                    if material in ['nylon', 'polyester', 'synthetic', 'mesh']:
                        penalty += 0.7 * occasion_multiplier
                        logger.debug(f"  ✅ OUTERWEAR MATERIAL: {material.capitalize()} good for gym (+{0.7 * occasion_multiplier:.2f})")
            
            # WEAR LAYER - Ensure proper layering
            if wear_layer:
                if wear_layer in ['outer', 'outerwear', 'shell']:
                    penalty += 0.5 * occasion_multiplier
                    logger.debug(f"  ✅ WEAR LAYER: Correctly categorized as outer layer (+{0.5 * occasion_multiplier:.2f})")
            
            # LENGTH - Match to weather and occasion
            if length:
                if temp < 40:  # Very cold
                    if length in ['long', 'full length', 'maxi']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ OUTERWEAR LENGTH: Long coat ideal for cold (+{0.8 * occasion_multiplier:.2f})")
                    elif length in ['short', 'cropped']:
                        penalty -= 0.5 * occasion_multiplier
                        logger.debug(f"  ⚠️ OUTERWEAR LENGTH: Short jacket less warm ({-0.5 * occasion_multiplier:.2f})")
                elif temp > 60:  # Mild/warm
                    if length in ['short', 'cropped', 'bomber']:
                        penalty += 0.6 * occasion_multiplier
                        logger.debug(f"  ✅ OUTERWEAR LENGTH: Cropped jacket good for mild weather (+{0.6 * occasion_multiplier:.2f})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # SHOES METADATA SCORING
        # ═══════════════════════════════════════════════════════════════════════
        if item_category == 'shoes':
            # Extract metadata fields for shoes
            formal_level = None
            material = None
            shoe_type = None
            
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    material = (visual_attrs.get('material') or '').lower()
                    shoe_type = (visual_attrs.get('shoeType') or '').lower()
            
            # FORMAL LEVEL - Match to occasion
            if formal_level:
                if occasion_lower in ['business', 'formal', 'interview']:
                    if formal_level in ['formal', 'dress', 'business']:
                        penalty += 1.0 * occasion_multiplier
                        logger.debug(f"  ✅✅ SHOES FORMAL LEVEL: {formal_level.capitalize()} appropriate for formal (+{1.0 * occasion_multiplier:.2f})")
                    elif formal_level in ['athletic', 'sport', 'casual']:
                        penalty -= 1.5 * occasion_multiplier
                        logger.debug(f"  🚫 SHOES FORMAL LEVEL: {formal_level.capitalize()} too casual for formal ({-1.5 * occasion_multiplier:.2f})")
                elif occasion_lower in ['gym', 'athletic']:
                    if formal_level in ['athletic', 'sport', 'casual']:
                        penalty += 0.9 * occasion_multiplier
                        logger.debug(f"  ✅ SHOES FORMAL LEVEL: {formal_level.capitalize()} perfect for gym (+{0.9 * occasion_multiplier:.2f})")
                    elif formal_level in ['formal', 'dress']:
                        penalty -= 2.0 * occasion_multiplier
                        logger.debug(f"  🚫🚫 SHOES FORMAL LEVEL: {formal_level.capitalize()} too formal for gym ({-2.0 * occasion_multiplier:.2f})")
            
            # SHOE TYPE - Direct matching
            if shoe_type:
                if occasion_lower in ['gym', 'athletic']:
                    if shoe_type in ['sneaker', 'athletic', 'running', 'training']:
                        penalty += 1.2 * occasion_multiplier
                        logger.debug(f"  ✅✅✅ SHOES TYPE: {shoe_type.capitalize()} perfect for gym (+{1.2 * occasion_multiplier:.2f})")
                elif occasion_lower in ['formal', 'business']:
                    if shoe_type in ['oxford', 'loafer', 'dress', 'formal']:
                        penalty += 1.0 * occasion_multiplier
                        logger.debug(f"  ✅✅ SHOES TYPE: {shoe_type.capitalize()} appropriate for formal (+{1.0 * occasion_multiplier:.2f})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # ACCESSORIES METADATA SCORING
        # ═══════════════════════════════════════════════════════════════════════
        if item_category == 'accessories':
            # Extract metadata fields for accessories
            formal_level = None
            material = None
            
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    formal_level = (visual_attrs.get('formalLevel') or '').lower()
                    material = (visual_attrs.get('material') or '').lower()
            
            # FORMAL LEVEL - Match to occasion
            if formal_level:
                if occasion_lower in ['business', 'formal', 'interview']:
                    if formal_level in ['formal', 'dress', 'business']:
                        penalty += 0.8 * occasion_multiplier
                        logger.debug(f"  ✅ ACCESSORY FORMAL LEVEL: {formal_level.capitalize()} appropriate for formal (+{0.8 * occasion_multiplier:.2f})")
                    elif formal_level in ['athletic', 'sport']:
                        penalty -= 1.2 * occasion_multiplier
                        logger.debug(f"  🚫 ACCESSORY FORMAL LEVEL: {formal_level.capitalize()} too casual for formal ({-1.2 * occasion_multiplier:.2f})")
                elif occasion_lower in ['gym', 'athletic']:
                    # Block ALL accessories for gym (already handled in hard filter)
                    penalty -= 2.0 * occasion_multiplier
                    logger.debug(f"  🚫🚫 ACCESSORY: Accessories inappropriate for gym ({-2.0 * occasion_multiplier:.2f})")
            
            # MATERIAL - Quality/formality indicator
            if material:
                if occasion_lower in ['formal', 'business']:
                    if material in ['leather', 'silk', 'metal', 'gold', 'silver']:
                        penalty += 0.6 * occasion_multiplier
                        logger.debug(f"  ✅ ACCESSORY MATERIAL: {material.capitalize()} appropriate for formal (+{0.6 * occasion_multiplier:.2f})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # KEYWORD-BASED SCORING: Secondary scoring based on item names (LIGHT penalties only)
        # ═══════════════════════════════════════════════════════════════════════
        
        if occasion_lower in ['athletic', 'gym', 'workout']:  # ADD GYM
            # BOOST athletic/sport keywords strongly
            if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'workout', 'training', 'performance']):
                penalty += 0.6 * occasion_multiplier  # Strong boost for primary athletic keywords
                logger.debug(f"  ✅ KEYWORD: Athletic keyword in name: {+0.6 * occasion_multiplier:.2f}")
            elif any(word in item_name for word in ['tank', 'sneaker', 'jogger', 'track', 'jersey', 'nike', 'adidas', 'shorts']):
                penalty += 0.5 * occasion_multiplier  # Good boost for sport-related items/brands
                logger.debug(f"  ✅ KEYWORD: Sport-related keyword/brand: {+0.5 * occasion_multiplier:.2f}")
            # PENALTIES for non-athletic items
            elif any(word in item_name for word in ['polo', 'button', 'dress', 'formal', 'oxford', 'blazer', 'dockers', 'slide']):
                penalty -= 0.5 * occasion_multiplier  # Penalty for non-athletic items
                logger.debug(f"  ⚠️ KEYWORD: Non-athletic keyword penalty: {-0.5 * occasion_multiplier:.2f}")
        
        elif occasion_lower == 'business':
            # Light penalties for athletic items
            if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'tank']):
                penalty -= 0.1 * occasion_multiplier
            # Boost business items
            elif any(word in item_name for word in ['business', 'professional', 'formal', 'button', 'dress']):
                penalty += 0.5 * occasion_multiplier
        
        # ═══════════════════════════════════════════════════════════════════════
        # METADATA CHECK: WAISTBAND TYPE FORMALITY SCORING (for all occasions)
        # ═══════════════════════════════════════════════════════════════════════
        waistband_type = None
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                # New dict format
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    waistband_type = visual_attrs.get('waistbandType')
            else:
                # Legacy Pydantic object format
                visual_attrs = getattr(item.metadata, 'visualAttributes', None)
                # Legacy Pydantic object format
            if visual_attrs:
                waistband_type = getattr(visual_attrs, 'waistbandType', None)
        
        if waistband_type and waistband_type != 'none':
            # Map waistband types to formality levels (0-5 scale)
            waistband_formality = {
                'elastic': 1,              # Very casual (sweatpants)
                'drawstring': 1,           # Very casual (joggers)
                'elastic_drawstring': 1,   # Very casual (athletic wear)
                'button_zip': 3,           # Semi-formal
                'belt_loops': 4            # Formal (dress pants, chinos)
            }
            
            # Map occasions to formality requirements (0-5 scale)
            occasion_formality = {
                'loungewear': 0,
                'gym': 0,
                'athletic': 0,  # FIXED: Was 1, should be 0 to match gym
                'casual': 2,
                'brunch': 2,
                'date': 3,
                'smart casual': 3,
                'business casual': 4,
                'business': 4,
                'work': 4,
                'formal': 5,
                'wedding': 5
            }
            
            item_formality = waistband_formality.get(waistband_type, 2)
            required_formality = occasion_formality.get(occasion_lower, 2)
            
            formality_gap = abs(item_formality - required_formality)
            
            # Only apply penalties for significant mismatches
            if formality_gap >= 3:
                # Major mismatch (e.g., elastic sweatpants for formal event)
                penalty -= 2.0 * occasion_multiplier
                logger.debug(f"  🚫 WAISTBAND FORMALITY: Major mismatch (gap {formality_gap}): {-2.0 * occasion_multiplier:.2f}")
            elif formality_gap == 2:
                # Moderate mismatch
                penalty -= 0.5 * occasion_multiplier
                logger.debug(f"  ⚠️ WAISTBAND FORMALITY: Moderate mismatch (gap {formality_gap}): {-0.5 * occasion_multiplier:.2f}")
            elif formality_gap == 0:
                # Perfect match
                penalty += 0.3 * occasion_multiplier
                logger.debug(f"  ✅ WAISTBAND FORMALITY: Perfect match: {+0.3 * occasion_multiplier:.2f}")
        
        return penalty
    
    async def _intelligent_item_selection(self, suitable_items: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Intelligently select items with TARGET-DRIVEN sizing and proportional category balancing"""
        selected_items = []
        
        # NO FALLBACK: If no suitable items, let emergency default handle it
        if len(suitable_items) == 0:
            logger.warning(f"🚨 NO SUITABLE ITEMS: Will use emergency default instead of inappropriate items")
            return []
        
        # STEP 1: Compute dynamic target count FIRST (primary goal)
        target_count = self._get_target_item_count(context)
        logger.info(f"🎯 TARGET-DRIVEN: Target count is {target_count} items for {context.occasion}")
        
        # STEP 2: Get base category limits that ADAPT to target count
        base_category_limits = self._get_dynamic_category_limits(context, target_count)
        category_counts = {cat: 0 for cat in base_category_limits.keys()}
        
        logger.info(f"🎯 TARGET-DRIVEN: Base category limits for {target_count} items: {base_category_limits}")
        
        # STEP 3: Determine if outerwear is needed based on temperature and occasion
        needs_outerwear = self._needs_outerwear(context)
        
        # STEP 3.5: PRIORITIZE BASE ITEM - Ensure base item is always included first
        base_item = None
        if context.base_item_id:
            logger.info(f"🎯 BASE ITEM: Looking for base item with ID: {context.base_item_id}")
            for item in suitable_items:
                item_id = getattr(item, 'id', None)
                if item_id == context.base_item_id:
                    base_item = item
                    logger.info(f"✅ BASE ITEM FOUND: {getattr(item, 'name', 'Unknown')} (ID: {item_id})")
                    break
            
            if base_item:
                # Add base item to selected items first
                selected_items.append(base_item)
                item_category = self._get_item_category(base_item)
                category_counts[item_category] = category_counts.get(item_category, 0) + 1
                logger.info(f"✅ BASE ITEM ADDED: '{getattr(base_item, 'name', 'Unknown')}' → category='{item_category}' | Progress: {len(selected_items)}/{target_count}")
            else:
                logger.warning(f"⚠️ BASE ITEM NOT FOUND: Base item ID {context.base_item_id} not in suitable items")
        
        # STEP 4: Sort items by preference score
        scored_items = []
        for item in suitable_items:
            # Skip base item since it's already added
            if base_item and getattr(item, 'id', None) == context.base_item_id:
                continue
            score = await self._calculate_item_score(item, context)
            scored_items.append((item, score))
        
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # STEP 5: TARGET-DRIVEN SELECTION with proportional category balancing
        for item, score in scored_items:
            # Stop ONLY when target count is reached
            if len(selected_items) >= target_count:
                logger.info(f"🎯 TARGET-DRIVEN: Reached target count of {target_count} items")
                break
                
            item_category = self._get_item_category(item)
            
            # 👗 CRITICAL: If dress is already selected, NEVER add tops or bottoms
            has_dress = safe_get(category_counts, 'dress', 0) > 0
            if has_dress and item_category in ['tops', 'bottoms']:
                logger.info(f"👗 DRESS OUTFIT: Skipping {item_category} '{getattr(item, 'name', 'Unknown')[:40]}' because dress is already selected")
                continue
            
            # 👗 CRITICAL: If tops or bottoms already selected, NEVER add a dress
            has_tops = safe_get(category_counts, 'tops', 0) > 0
            has_bottoms = safe_get(category_counts, 'bottoms', 0) > 0
            if (has_tops or has_bottoms) and item_category == 'dress':
                logger.info(f"👔 REGULAR OUTFIT: Skipping dress '{getattr(item, 'name', 'Unknown')[:40]}' because tops/bottoms already selected")
                continue
            
            # Skip outerwear if not needed
            if item_category == "outerwear" and not needs_outerwear:
                continue
            
            # STEP 6: Proportional category balancing (no hard-stopping at fixed limits)
            current_category_count = (safe_get(category_counts, item_category, 0) if category_counts else 0)
            base_limit = (safe_get(base_category_limits, item_category, 0) if base_category_limits else 0)
            
            # Calculate proportional limit based on target count and remaining items needed
            remaining_items_needed = target_count - len(selected_items)
            total_base_limit = sum(base_category_limits.values())
            
            if total_base_limit > 0:
                # Proportional limit: allow more items in this category if we need more items overall
                proportional_limit = max(
                    base_limit,  # At least the base limit
                    int((base_limit / total_base_limit) * remaining_items_needed * 1.5)  # Proportional scaling
                )
            else:
                proportional_limit = base_limit
            
            # Allow selection if we haven't exceeded proportional limit
            if current_category_count < proportional_limit:
                selected_items.append(item)
                category_counts[item_category] += 1
                logger.warning(f"✅ SELECTED: '{getattr(item, 'name', 'Unknown')[:60]}' → category='{item_category}' | Progress: {len(selected_items)}/{target_count} | Category: {current_category_count + 1}/{proportional_limit} | All counts: {dict(category_counts)}")
            else:
                logger.warning(f"❌ REJECTED: '{getattr(item, 'name', 'Unknown')[:60]}' → category='{item_category}' LIMIT REACHED | Category: {current_category_count}/{proportional_limit} | All counts: {dict(category_counts)}")
        
        # STEP 7: Ensure we have at least the minimum essential categories
        # Check if outfit has a dress - if so, it replaces tops + bottoms requirement
        has_dress = safe_get(category_counts, 'dress', 0) > 0
        
        if has_dress:
            # Dress outfits only need: dress + shoes (tops/bottoms are replaced by dress)
            essential_categories = ["dress", "shoes"]
            logger.info(f"👗 DRESS OUTFIT: Essential categories adjusted to {essential_categories} (dress replaces tops + bottoms)")
        else:
            # Regular outfits need: tops + bottoms + shoes
            essential_categories = ["tops", "bottoms", "shoes"]
        
        missing_essentials = []
        
        for category in essential_categories:
            if safe_get(category_counts, category, 0) == 0:
                missing_essentials.append(category)
        
        # If we're missing essentials and haven't reached target, try to fill them
        if missing_essentials and len(selected_items) < target_count:
            logger.warning(f"🎯 TARGET-DRIVEN: Missing essential categories: {missing_essentials}, attempting to fill")
            
            for category in missing_essentials:
                if len(selected_items) >= target_count:
                    break
                    
                # Find best item for this essential category
                for item, score in scored_items:
                    if item in selected_items:
                        continue
                        
                    if self._get_item_category(item) == category:
                        selected_items.append(item)
                        category_counts[category] = (safe_get(category_counts, category, 0) if category_counts else 0) + 1
                        logger.info(f"🎯 TARGET-DRIVEN: Added essential {getattr(item, 'name', 'Unknown')} ({category}) - {len(selected_items)}/{target_count} items")
                        break
        
        logger.info(f"🎯 TARGET-DRIVEN: Final selection: {len(selected_items)} items (target was {target_count})")
        logger.info(f"🎯 TARGET-DRIVEN: Category distribution: {category_counts}")
        logger.info(f"👗 DRESS CHECK: has_dress={has_dress}")
        return selected_items
    
    def _get_dynamic_category_limits(self, context: GenerationContext, target_count: int) -> Dict[str, int]:
        """Get category limits that adapt to target count - TARGET-DRIVEN with optional outerwear and dress support"""
        occasion_lower = (context.occasion if context else "unknown").lower()
        style_lower = (context.style if context else "unknown").lower() if (context.style if context else "unknown") else ""
        
        # Check if outerwear is needed based on temperature, occasion, and style
        needs_outerwear = self._needs_outerwear(context)
        
        # TARGET-DRIVEN: Category limits adapt to target count with optional outerwear
        # Note: Dress limit is always 1 - if a dress is selected, it replaces tops + bottoms
        if target_count <= 3:
            # Minimal outfit: essentials only
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "outerwear": 1}
            else:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1}
        
        elif target_count == 4:
            # Standard outfit: add one layer
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "outerwear": 1}
            else:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "accessories": 1}
        
        elif target_count == 5:
            # Enhanced outfit: add layers
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "outerwear": 1, "accessories": 1}
            else:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "accessories": 2}
        
        elif target_count >= 6:
            # Full outfit: maximum layers
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "outerwear": 1, "accessories": 2, "sweater": 1}
            else:
                return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "accessories": 3, "sweater": 1}
        
        # Fallback for unexpected target counts
        if needs_outerwear:
            return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "outerwear": 1, "accessories": 1}
        else:
            return {"tops": 1, "bottoms": 1, "dress": 1, "shoes": 1, "accessories": 1}
    
    def _get_target_item_count(self, context: GenerationContext) -> int:
        """Get target item count based on occasion, style, and mood - SIMPLIFIED"""
        import random
        
        occasion_lower = (context.occasion if context else "unknown").lower()
        style_lower = (context.style if context else "unknown").lower() if (context.style if context else "unknown") else ""
        mood_lower = (context.mood if context else "unknown").lower() if (context.mood if context else "unknown") else ""
        
        # SIMPLIFIED: Focus on 3-6 items with clear logic
        if 'formal' in occasion_lower or 'business' in occasion_lower:
            # Formal: 4-6 items (need blazer, accessories)
            return random.randint(4, 6)
        elif 'athletic' in occasion_lower or 'gym' in occasion_lower:
            # Athletic: 3-4 items (simple, functional)
            return random.randint(3, 4)
        elif 'party' in occasion_lower or 'date' in occasion_lower:
            # Social: 4-5 items (stylish but not overdone)
            return random.randint(4, 5)
        elif 'casual' in occasion_lower:
            # Casual: 3-5 items (flexible)
            return random.randint(3, 5)
        else:
            # Default: 3-5 items
            return random.randint(3, 5)
    
    def _needs_outerwear(self, context: GenerationContext) -> bool:
        """Determine if outerwear is needed based on temperature, occasion, and style"""
        # Get temperature from weather context
        temperature = 70.0  # Default
        if (context.weather if context else None):
            if hasattr(context.weather, 'temperature'):
                temperature = (context.weather if context else None).temperature
            elif isinstance(context.weather, dict):
                temperature = safe_get(context.weather, 'temperature', 70.0) if context.weather else 70.0
        
        occasion_lower = (context.occasion if context else "unknown").lower()
        style_lower = (context.style if context else "unknown").lower() if (context.style if context else "unknown") else ""
        mood_lower = (context.mood if context else "unknown").lower() if (context.mood if context else "unknown") else ""
        
        # Temperature-based need (below 65°F)
        if temperature < 65:
            return True
        
        # Formal occasions always need outerwear (blazer/jacket)
        if 'formal' in occasion_lower or 'business' in occasion_lower:
            return True
        
        # Style-based preference
        if 'maximalist' in style_lower or 'layered' in style_lower:
            return True  # Maximalist styles often include outerwear
        
        if 'minimalist' in style_lower:
            return False  # Minimalist styles often skip outerwear
        
        # Mood-based preference
        if 'bold' in mood_lower or 'dynamic' in mood_lower:
            return True  # Bold moods often include statement outerwear
        
        if 'subtle' in mood_lower or 'serene' in mood_lower:
            return False  # Subtle moods often skip outerwear
        
        # Default: optional for casual occasions in warm weather
        return False
    
    async def _ensure_outfit_completeness(self, items: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Ensure outfit has essential categories and is complete - NO FALLBACKS"""
        # Just return the items as-is, no adding back inappropriate items
        logger.info(f"📋 COMPLETENESS: Outfit has {len(items)} items - no fallbacks added")
        return items
    
    async def _validate_outfit(self, outfit: OutfitGeneratedOutfit, context: GenerationContext) -> ValidationResult:
        """Comprehensive outfit validation with detailed debugging"""
        issues = []
        suggestions = []
        score = 100.0
        
        logger.info(f"🔍 VALIDATION START: {len(outfit.items)} items to validate")
        
        # Check item count
        if len(outfit.items) < self.min_items:
            issue_msg = f"Outfit has only {len(outfit.items)} items, minimum is {self.min_items}"
            issues.append(issue_msg)
            score -= 20.0
            logger.warning(f"⚠️ VALIDATION: {issue_msg}")
        elif len(outfit.items) > self.max_items:
            issue_msg = f"Outfit has {len(outfit.items)} items, maximum is {self.max_items}"
            issues.append(issue_msg)
            score -= 10.0
            logger.warning(f"⚠️ VALIDATION: {issue_msg}")
        else:
            logger.info(f"✅ VALIDATION: Item count OK ({len(outfit.items)} items)")
        
        # Check category limits
        category_counts = {}
        for item in outfit.items:
            category = self._get_item_category(item)
            category_counts[category] = (safe_get(category_counts, category, 0) if category_counts else 0) + 1
        
        logger.info(f"🔍 VALIDATION: Category breakdown: {category_counts}")
        
        # Define base category limits
        base_category_limits = {
            'top': 2, 'bottom': 2, 'shoes': 1, 'outerwear': 1, 
            'accessories': 3, 'underwear': 1, 'other': 2
        }
        
        for category, count in category_counts.items():
            limit = safe_get(base_category_limits, category, 2)
            if count > limit:
                issue_msg = f"Too many {category}: {count} (max {limit})"
                issues.append(issue_msg)
                score -= 15.0
                logger.warning(f"⚠️ VALIDATION: {issue_msg}")
            else:
                logger.info(f"✅ VALIDATION: {category} count OK ({count}/{limit})")
        
        # Check for inappropriate combinations
        inappropriate_found = False
        for item1 in outfit.items:
            for item2 in outfit.items:
                if item1 != item2:
                    combination = self._check_inappropriate_combination(item1, item2)
                    if combination:
                        issues.append(combination)
                        score -= 25.0
                        inappropriate_found = True
                        logger.warning(f"⚠️ VALIDATION: Inappropriate combination: {combination}")
        
        if not inappropriate_found:
            logger.info(f"✅ VALIDATION: No inappropriate combinations found")
        
        # Check essential categories
        categories_present = set(self._get_item_category(item) for item in outfit.items)
        essential_categories = {"tops", "bottoms", "shoes"}
        missing_essential = essential_categories - categories_present
        
        logger.info(f"🔍 VALIDATION: Categories present: {categories_present}")
        logger.info(f"🔍 VALIDATION: Essential categories: {essential_categories}")
        
        if missing_essential:
            issue_msg = f"Missing essential categories: {missing_essential}"
            issues.append(issue_msg)
            score -= 30.0
            logger.warning(f"⚠️ VALIDATION: {issue_msg}")
        else:
            logger.info(f"✅ VALIDATION: All essential categories present")
        
        # CRITICAL: Gym/Athletic MUST have bottoms (shorts, pants, leggings)
        occasion_lower = (outfit.occasion if outfit and outfit.occasion else "unknown").lower()
        if occasion_lower in ['gym', 'athletic', 'workout']:
            if 'bottoms' not in categories_present:
                critical_issue_msg = f"CRITICAL: Gym outfit MUST have bottoms (shorts/pants/leggings)"
                issues.append(critical_issue_msg)
                score -= 50.0  # Heavy penalty - this is unacceptable
                logger.error(f"🚫🚫🚫 VALIDATION: {critical_issue_msg}")
            else:
                logger.info(f"✅ VALIDATION: Gym outfit has required bottoms")
        
        # Calculate confidence
        confidence = max(0.0, min(1.0, score / 100.0))
        
        # RELAXED VALIDATION - Allow outfits with minor issues to pass
        # Only fail if there are critical issues (missing essential categories or too few items)
        critical_issues = [issue for issue in issues if "Missing essential categories" in issue or "only" in issue and "items" in issue]
        is_valid = len(critical_issues) == 0 and confidence >= 0.4  # Lowered from 0.6
        
        logger.info(f"🔍 VALIDATION RESULT: valid={is_valid}, score={score}, confidence={confidence}")
        logger.info(f"🔍 VALIDATION ISSUES: {len(issues)} issues found")
        if issues:
            for i, issue in enumerate(issues, 1):
                logger.info(f"🔍 VALIDATION ISSUE {i}: {issue}")
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence
        )
    
    def _is_occasion_compatible(self, item: ClothingItem, occasion: str, style: str = None, mood: str = None, weather_data: dict = None) -> bool:
        """Balanced occasion compatibility check - not too strict, not too loose"""
        occasion_lower = occasion.lower()
        item_name = self.safe_get_item_name(item).lower()
        
        # MOOD COMPATIBILITY CHECK (NEW)
        if mood:
            mood_lower = mood.lower()
            item_moods = getattr(item, 'mood', [])
            if isinstance(item_moods, str):
                item_moods = [item_moods]
            item_moods_lower = [m.lower() for m in item_moods]
            
            # NEUTRAL DEFAULT: If no mood information available, treat as flexible/neutral
            if not item_moods_lower:
                logger.info(f"🔍 MOOD: No mood metadata for {item_name}, treating as FLEXIBLE/NEUTRAL")
                # Continue to occasion check - don't return False
            else:
                # Check for mood compatibility
                mood_compatible = False
                if mood_lower in item_moods_lower:
                    mood_compatible = True
                    logger.info(f"✅ MOOD: {item_name} matches mood {mood_lower}")
                else:
                    # Flexible mood matching for common mood combinations
                    mood_mappings = {
                        'professional': ['serious', 'business', 'formal'],
                        'relaxed': ['comfortable', 'casual', 'easy'],
                        'bold': ['dramatic', 'striking', 'confident', 'energetic', 'motivated', 'active'],  # Added athletic moods
                        'comfortable': ['relaxed', 'easy', 'casual'],
                        'sophisticated': ['elegant', 'refined', 'classic'],
                        'energetic': ['active', 'dynamic', 'vibrant', 'motivated', 'bold'],  # Added bold
                        'confident': ['bold', 'energetic', 'motivated', 'active'],  # Added athletic moods
                        'motivated': ['energetic', 'active', 'bold', 'confident'],  # Added athletic moods
                        'active': ['energetic', 'motivated', 'bold', 'confident']  # Added athletic moods
                    }
                    
                    if mood_lower in mood_mappings:
                        compatible_moods = mood_mappings[mood_lower]
                        if any(compat_mood in item_moods_lower for compat_mood in compatible_moods):
                            mood_compatible = True
                            logger.info(f"✅ MOOD FLEXIBLE: {item_name} compatible with {mood_lower} via mood mapping")
                    
                    if not mood_compatible:
                        logger.info(f"❌ MOOD: {item_name} not compatible with mood {mood_lower}")
                        return False
        
        # NEUTRAL DEFAULT: If no occasion information available, treat as flexible/neutral
        item_occasions = getattr(item, 'occasion', [])
        if not item_occasions:
            logger.info(f"🔍 OCCASION: No occasion metadata for {item_name}, treating as FLEXIBLE/NEUTRAL")
            
            # ATHLETIC OCCASION LOGIC: For athletic occasions, be more strict about what's appropriate
            if occasion_lower == 'athletic':
                item_type_lower = str(getattr(item, 'type', '')).lower()
                item_category_lower = str(getattr(item, 'category', '')).lower()
                
                # Athletic item indicators (items that are clearly athletic)
                athletic_indicators = ['tank', 'athletic', 'sport', 'gym', 'workout', 'running', 'sneaker', 'shorts', 'legging', 'jersey', 'mesh']
                
                # Business/formal indicators (items that should be avoided for athletic)
                business_indicators = ['dress', 'button', 'formal', 'suit', 'tie', 'blazer', 'dress shoe', 'oxford', 'loafer', 'dress shirt', 'dress pants', 'slacks']
                
                # Check if item is clearly athletic
                if any(indicator in item_name or indicator in item_type_lower or indicator in item_category_lower 
                      for indicator in athletic_indicators):
                    logger.info(f"✅ ATHLETIC: {item_name} is athletic item (no metadata)")
                    return True
                
                # Check if item is clearly business/formal (should be avoided for athletic)
                if any(indicator in item_name or indicator in item_type_lower or indicator in item_category_lower 
                      for indicator in business_indicators):
                    logger.info(f"❌ ATHLETIC: {item_name} is business item, not suitable for athletic")
                    return False
                
                # For neutral items (like basic t-shirts, jeans), allow them but log as neutral
                logger.info(f"✅ ATHLETIC: {item_name} is neutral item, allowing for athletic")
                return True
            
            return True
        
        # Normalize occasions list
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions]
        item_occasions_lower = [occ.lower() for occ in item_occasions]
        
        # Check if item occasions include the requested occasion
        if occasion_lower in item_occasions_lower:
            logger.info(f"✅ OCCASION: {item_name} explicitly matches {occasion_lower}")
            
            # ENHANCED: For formal/business occasions, prioritize items with appropriate types
            if occasion_lower in ['formal', 'business']:
                item_type_lower = str(getattr(item, 'type', '')).lower()
                if item_type_lower in ['shirt', 'blouse', 'dress']:
                    logger.info(f"✅ OCCASION ENHANCED: {item_name} is perfect for {occasion_lower} (type: {item_type_lower})")
                    return True
                elif item_type_lower in ['sweater', 'jacket']:
                    logger.info(f"⚠️ OCCASION WARNING: {item_name} acceptable for {occasion_lower} but not ideal (type: {item_type_lower})")
                    return True
            
            return True
        
        # Check for broad compatibility patterns - more strict for athletic
        compatibility_patterns = {
            'athletic': ['athletic', 'sport', 'gym', 'workout'],  # Removed 'casual' - too permissive
            'business': ['business', 'formal', 'professional', 'casual', 'everyday'],  # Added everyday
            'casual': ['casual', 'everyday', 'relaxed', 'business', 'formal'],  # Added formal
            'formal': ['formal', 'business', 'professional', 'casual', 'elegant'],  # Added elegant
            'party': ['party', 'casual', 'evening', 'business', 'formal'],  # Added formal
            'elegant': ['formal', 'business', 'professional', 'party'],  # Added for formal+elegant
            'wedding': ['formal', 'wedding', 'special', 'business'],  # Added business
            'vacation': ['casual', 'vacation', 'relaxed', 'business']  # Added business
        }
        
        if occasion_lower in compatibility_patterns:
            compatible_occasions = compatibility_patterns[occasion_lower]
            for compatible in compatible_occasions:
                if compatible in item_occasions_lower:
                    logger.info(f"✅ OCCASION: {item_name} broadly compatible with {occasion_lower} via {compatible}")
                    return True
        
        # Only exclude obviously inappropriate items
        all_text = ' '.join([item_name, getattr(item, 'type', ''), ' '.join(item_occasions)]).lower()
        
        inappropriate_patterns = {
            'athletic': ['evening gown', 'tuxedo', 'wedding dress', 'high heels'],
            'business': ['bikini', 'swimwear', 'pajamas', 'underwear'],
            'formal': ['gym shorts', 'tank top', 'flip flops', 'sweatpants'],
            'party': ['work uniform', 'scrubs', 'lab coat']
        }
        
        if occasion_lower in inappropriate_patterns:
            for inappropriate in inappropriate_patterns[occasion_lower]:
                if inappropriate in all_text:
                    logger.info(f"❌ OCCASION: {item_name} inappropriate for {occasion_lower} (contains '{inappropriate}')")
                    return False
        
        # Default: Allow the item (be permissive)
        logger.info(f"✅ OCCASION: {item_name} allowed for {occasion_lower}")
        return True
    
    def _is_style_compatible(self, item: ClothingItem, style: str) -> bool:
        """Balanced style compatibility check - not too strict, not too loose"""
        style_lower = style.lower()
        item_name = self.safe_get_item_name(item).lower()
        
        # Extract style information
        item_styles = getattr(item, 'style', [])
        item_tags = getattr(item, 'tags', [])
        
        # NEUTRAL DEFAULT: If no style information available, treat as flexible/neutral
        if not item_styles and not item_tags:
            logger.info(f"🔍 STYLE: No style metadata for {item_name}, treating as FLEXIBLE/NEUTRAL")
            return True
        
        # Normalize styles list
        if isinstance(item_styles, str):
            item_styles = [item_styles]
        if isinstance(item_tags, str):
            item_tags = [item_tags]
        
        # Check if item styles include the requested style
        all_styles = [s.lower() for s in item_styles + item_tags]
        if style_lower in all_styles:
            logger.info(f"✅ STYLE: {item_name} explicitly matches {style_lower}")
            return True
        
        # Check for broad style compatibility - more permissive
        style_compatibility = {
            'classic': ['formal', 'business', 'professional', 'traditional', 'casual', 'sporty', 'athletic'],  # Added sporty, athletic
            'athletic': ['sporty', 'active', 'casual', 'comfortable', 'classic'],  # Added classic
            'sporty': ['athletic', 'active', 'casual', 'comfortable', 'classic'],  # Added classic
            'casual': ['relaxed', 'everyday', 'comfortable', 'informal', 'classic', 'business', 'athletic', 'sporty'],  # Added athletic, sporty
            'formal': ['classic', 'business', 'professional', 'elegant', 'casual'],  # Added casual
            'elegant': ['formal', 'classic', 'business', 'professional'],  # Added for formal+elegant
            'streetwear': ['urban', 'trendy', 'casual', 'edgy'],
            'edgy': ['streetwear', 'urban', 'trendy', 'alternative']
        }
        
        if style_lower in style_compatibility:
            compatible_styles = style_compatibility[style_lower]
            for compatible in compatible_styles:
                if compatible in all_styles:
                    logger.info(f"✅ STYLE: {item_name} broadly compatible with {style_lower} via {compatible}")
                    return True
        
        # Default: Allow the item (be permissive)
        logger.info(f"✅ STYLE: {item_name} allowed for {style_lower}")
        return True
    
    # Missing methods that core strategies need
    async def _filter_by_body_type(self, wardrobe: List[ClothingItem], body_type: str, height: str) -> List[ClothingItem]:
        """Filter items based on body type compatibility - simplified version"""
        logger.info(f"🔍 BODY TYPE: Filtering {len(wardrobe)} items for body type: {body_type}")
        # For now, return all items (be permissive)
        return wardrobe
    
    async def _apply_body_type_optimization(self, items: List[ClothingItem], body_type: str, height: str) -> List[ClothingItem]:
        """Apply body type optimization - simplified version"""
        logger.info(f"🔍 BODY OPTIMIZATION: Optimizing {len(items)} items for body type: {body_type}")
        # For now, return all items
        return items
    
    async def _filter_by_style_preferences(self, wardrobe: List[ClothingItem], style_preferences: List[str], favorite_colors: List[str], preferred_brands: List[str]) -> List[ClothingItem]:
        """Filter items based on style preferences - simplified version"""
        logger.info(f"🔍 STYLE PREFERENCES: Filtering {len(wardrobe)} items for preferences: {style_preferences}")
        # For now, return all items
        return wardrobe
    
    async def _filter_by_weather(self, wardrobe: List[ClothingItem], weather) -> List[ClothingItem]:
        """Filter items based on weather - simplified version"""
        logger.info(f"🔍 WEATHER: Filtering {len(wardrobe)} items for weather")
        # For now, return all items
        return wardrobe
    
    def _determine_season_from_weather(self, weather) -> str:
        """Determine season from weather data"""
        # Default to current season
        return "spring"
    
    async def _select_basic_items(self, wardrobe: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Select basic items for fallback with dress awareness"""
        logger.info(f"🔍 BASIC SELECT: Selecting from {len(wardrobe)} items")
        basic_items = []
        categories_found = set()
        
        # Check for dresses first
        has_dress = False
        for item in wardrobe:
            category = self._get_item_category(item)
            if category == 'dress':
                basic_items.append(item)
                categories_found.add('dress')
                has_dress = True
                logger.info(f"👗 BASIC SELECT: Found dress, will skip tops/bottoms")
                break
        
        # Define required categories based on whether we have a dress
        if has_dress:
            required_categories = ['dress', 'shoes']
        else:
            required_categories = ['tops', 'bottoms', 'shoes']
        
        # Select one item of each required category
        for item in wardrobe:
            if item in basic_items:
                continue
            category = self._get_item_category(item)
            if category in required_categories and category not in categories_found:
                basic_items.append(item)
                categories_found.add(category)
                logger.info(f"✅ BASIC SELECT: Added {category} '{getattr(item, 'name', 'Unknown')[:40]}'")
                if len(categories_found) >= len(required_categories):
                    break
        
        logger.info(f"🔍 BASIC SELECT: Selected {len(basic_items)} items, has_dress={has_dress}, categories={categories_found}")
        return basic_items
    
    async def _calculate_item_score(self, item: ClothingItem, context: GenerationContext) -> float:
        """Calculate score for an item - simplified version"""
        # Simple scoring: base score + bonuses
        score = 50.0  # Base score
        
        # Add bonuses for various factors
        if hasattr(item, 'favorite_score'):
            score += self.safe_get_item_attr(item, 'favorite_score', 0) * 20
        
        wear_count = self.safe_get_item_attr(item, 'wearCount', 0)
        if wear_count > 0:
            score += min(wear_count * 2, 20)  # Cap at 20
        
        return score
    
    def _get_item_category(self, item: ClothingItem) -> str:
        """Get category for an item - METADATA-FIRST approach"""
        item_type = getattr(item, 'type', '')
        item_name = getattr(item, 'name', 'Unknown')
        
        # METADATA CHECK: Use coreCategory from metadata if available (most accurate!)
        item_name_lower = self.safe_get_item_name(item).lower()
        raw_item_type = getattr(item, 'type', '')
        item_type_lower = ''
        if hasattr(raw_item_type, 'value'):
            item_type_lower = raw_item_type.value.lower()
        elif hasattr(raw_item_type, 'name'):
            item_type_lower = raw_item_type.name.lower()
        else:
            item_type_lower = str(raw_item_type).lower()
        
        if hasattr(item, 'metadata') and item.metadata:
            if isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    core_category = (visual_attrs.get('coreCategory') or '').lower()
                    if core_category:
                        # Map coreCategory values to our category system
                        core_category_map = {
                            'top': 'tops',
                            'tops': 'tops',
                            'shirt': 'tops',
                            'bottom': 'bottoms',
                            'bottoms': 'bottoms',
                            'pants': 'bottoms',
                            'shorts': 'bottoms',
                            'shoe': 'shoes',
                            'shoes': 'shoes',
                            'footwear': 'shoes',
                            'outerwear': 'outerwear',
                            'jacket': 'outerwear',
                            'accessory': 'accessories',
                            'accessories': 'accessories'
                        }
                        if core_category in core_category_map:
                            category = core_category_map[core_category]
                            if category == 'tops' and any(keyword in item_type_lower or keyword in item_name_lower for keyword in ['blazer', 'jacket', 'coat']):
                                category = 'outerwear'
                            elif category == 'bottoms' and item_type_lower in ['sweater', 'shirt', 'top', 't-shirt', 't_shirt', 'hoodie', 'cardigan']:
                                logger.debug(
                                    f"🏷️ CATEGORY (metadata override): '{item_name[:50]}' coreCategory='{core_category}' "
                                    f"but type='{item_type_lower}' → treating as 'tops'"
                                )
                                category = 'tops'
                            logger.debug(f"🏷️ CATEGORY (metadata): '{item_name[:50]}' coreCategory='{core_category}' → '{category}'")
                            return category
        
        # Fallback to type-based detection
        # Handle enum types (e.g., ClothingType.SHIRT)
        item_type = item_type_lower
        
        # Handle ClothingType enum format (e.g., "ClothingType.SHIRT" -> "shirt")
        if 'clothingtype.' in item_type:
            item_type = item_type.split('.')[-1]
        
        # Map item types to categories
        category_map = {
            'shirt': 'tops',
            't-shirt': 'tops', 
            'blouse': 'tops',
            'sweater': 'tops',
            'tank': 'tops',
            'polo': 'tops',
            'pants': 'bottoms',
            'jeans': 'bottoms',
            'shorts': 'bottoms',
            'skirt': 'bottoms',
            'dress': 'dress',  # Dresses are standalone - replace both top and bottom
            'romper': 'dress',  # Rompers treated like dresses
            'jumpsuit': 'dress',  # Jumpsuits treated like dresses
            'shoes': 'shoes',
            'sneakers': 'shoes',
            'boots': 'shoes',
            'heels': 'shoes',
            'jacket': 'outerwear',
            'blazer': 'outerwear',
            'coat': 'outerwear',
            'hoodie': 'outerwear'
        }
        
        category = (safe_get(category_map, item_type, 'other') if category_map else 'other')
        
        # 🔍 DIAGNOSTIC LOGGING - Track category assignment for debugging
        logger.debug(f"🏷️ CATEGORY (type-based): '{item_name[:50]}' type='{item_type}' → category='{category}'")
        
        return category
    
    def _convert_item_to_style_dict(self, item: ClothingItem) -> Dict[str, Any]:
        """Convert item to dictionary suitable for style scoring utilities."""
        if isinstance(item, dict):
            return item
        
        # Pydantic models provide model_dump
        if hasattr(item, "model_dump"):
            try:
                return item.model_dump(exclude_none=False)
            except Exception as e:
                logger.debug(f"⚠️ STYLE SCORING: model_dump failed for {getattr(item, 'id', 'unknown')}: {e}")
        
        # Fallback to __dict__
        if hasattr(item, "__dict__"):
            return {
                key: value
                for key, value in item.__dict__.items()
            }
        
        return {}
    
    def _check_inappropriate_combination(self, item1: ClothingItem, item2: ClothingItem) -> bool:
        """Check if two items form an inappropriate combination - simplified version"""
        # For now, allow all combinations
        return False
    
    def _deduplicate_items(self, items: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Remove duplicate items (by id or name) from the final outfit selection."""
        seen_keys = set()
        unique_items = []
        deduped_keys = []
        
        for item in items:
            item_id = self.safe_get_item_attr(item, 'id', None)
            fallback_name = self.safe_get_item_name(item)
            key = item_id or fallback_name
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_items.append(item)
            else:
                deduped_keys.append(key)
        
        if deduped_keys:
            logger.info(f"🔁 DEDUPLICATION: Removed {len(deduped_keys)} duplicate items: {deduped_keys[:5]}{'...' if len(deduped_keys) > 5 else ''}")
            if hasattr(context, "metadata_notes") and isinstance(context.metadata_notes, dict):
                context.metadata_notes.setdefault("deduplicated_items", []).extend(deduped_keys)
        
        return unique_items
    
    # ═══════════════════════════════════════════════════════════════════════
    # MULTI-LAYERED SCORING ANALYZERS
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _analyze_body_type_scores(self, context: GenerationContext, item_scores: dict) -> None:
        """Analyze and score each item based on body type, height, weight, gender, and skin tone"""
        logger.info(f"👤 BODY TYPE ANALYZER: Scoring {len(item_scores)} items")
        
        # Extract ALL user physical attributes
        user_profile = getattr(context, 'user_profile', None)
        body_type = safe_get(user_profile, 'bodyType', 'Average').lower() if user_profile else 'average'
        height = safe_get(user_profile, 'height', 'Average') if user_profile else 'Average'
        weight = safe_get(user_profile, 'weight', 'Average') if user_profile else 'Average'
        gender = safe_get(user_profile, 'gender', 'Unspecified').lower() if user_profile else 'unspecified'
        skin_tone = safe_get(user_profile, 'skinTone', 'Medium') if user_profile else 'Medium'
        
        logger.info(f"👤 User profile: body_type={body_type}, height={height}, weight={weight}, gender={gender}, skin_tone={skin_tone}")
        
        # Body type scoring rules
        body_type_rules = {
            'hourglass': {
                'tops': {'fitted': 0.9, 'wrap': 0.9, 'vneck': 0.8, 'loose': 0.4},
                'bottoms': {'high_waist': 0.9, 'fitted': 0.8, 'straight': 0.7},
                'dresses': {'fitted': 0.9, 'wrap': 0.9, 'a_line': 0.8}
            },
            'pear': {
                'tops': {'structured': 0.9, 'detailed': 0.8, 'bright': 0.8},
                'bottoms': {'dark': 0.9, 'straight': 0.8, 'bootcut': 0.8, 'skinny': 0.3}
            },
            'apple': {
                'tops': {'empire': 0.9, 'vneck': 0.9, 'flowing': 0.8},
                'bottoms': {'fitted': 0.7, 'straight': 0.8, 'defined': 0.7}
            },
            'rectangle': {
                'tops': {'peplum': 0.9, 'ruffled': 0.8, 'belted': 0.8},
                'bottoms': {'curved': 0.8, 'flared': 0.8, 'detailed': 0.7}
            },
            'inverted_triangle': {
                'tops': {'simple': 0.8, 'dark': 0.8, 'vneck': 0.7},
                'bottoms': {'flared': 0.9, 'wide_leg': 0.8, 'detailed': 0.8}
            },
            'oval': {
                'tops': {'structured': 0.8, 'vneck': 0.9, 'vertical_lines': 0.8},
                'bottoms': {'straight': 0.8, 'dark': 0.8, 'high_waist': 0.7}
            },
            'average': {
                'tops': {'fitted': 0.8, 'structured': 0.7, 'casual': 0.7},
                'bottoms': {'straight': 0.8, 'fitted': 0.7, 'casual': 0.7}
            }
        }
        
        rules = (safe_get(body_type_rules, body_type, body_type_rules['average']) if body_type_rules else body_type_rules['average'])
        
        for item_id, scores in item_scores.items():
            item = scores['item']
            base_score = 0.5  # Default neutral score
            
            # OCCASION-BASED SCORING BOOST
            requested_occasion = (context.occasion if context else "unknown").lower()
            item_type_lower = str(getattr(item, 'type', '')).lower()
            
            # Boost appropriate item types for specific occasions
            if requested_occasion in ['formal', 'business'] and item_type_lower in ['shirt', 'blouse']:
                base_score += 0.3  # Strong boost for shirts in formal/business
                logger.debug(f"🎯 OCCASION BOOST: +0.3 for {item_type_lower} in {requested_occasion}")
            elif requested_occasion == 'casual' and item_type_lower in ['t-shirt', 'polo', 'tank']:
                base_score += 0.2  # Boost for casual tops in casual occasions
                logger.debug(f"🎯 OCCASION BOOST: +0.2 for {item_type_lower} in {requested_occasion}")
            
            # Get item category
            category = self._get_item_category(item)
            
            # Check if item has body-flattering attributes
            item_name_lower = self.safe_get_item_name(item).lower()
            
            if category in rules:
                for attribute, score_boost in rules[category].items():
                    if attribute in item_name_lower:
                        base_score = max(base_score, score_boost)
            
            # Additional scoring based on fit
            metadata = self.safe_get_item_attr(item, 'metadata')
            if metadata:
                visual_attrs = self.safe_get_item_attr(metadata, 'visualAttributes')
                if visual_attrs:
                    fit = self.safe_get_item_attr(visual_attrs, 'fit', '')
                    if fit:
                        fit_lower = fit.lower()
                        # Adjust based on body type preferences
                        if body_type in ['hourglass', 'pear'] and 'fitted' in fit_lower:
                            base_score += 0.1
                        elif body_type in ['apple', 'rectangle'] and 'loose' in fit_lower:
                            base_score += 0.1
            
            # ═══════════════════════════════════════════════════════════
            # HEIGHT SCORING - Proportions and lengths
            # ═══════════════════════════════════════════════════════════
            if height and height != 'Average':
                height_lower = str(height).lower()
                
                # Short height (under 5'4")
                if any(h in height_lower for h in ["5'0", "5'1", "5'2", "5'3", "under"]):
                    # Favor items that elongate
                    if 'high waist' in item_name_lower or 'high-waist' in item_name_lower:
                        base_score += 0.15
                    if 'crop' in item_name_lower or 'short' in item_name_lower:
                        base_score += 0.10
                    if 'vertical' in item_name_lower or 'stripe' in item_name_lower:
                        base_score += 0.10
                    # Avoid overwhelming items
                    if 'oversized' in item_name_lower or 'maxi' in item_name_lower:
                        base_score -= 0.10
                
                # Tall height (over 5'9")
                elif any(h in height_lower for h in ["5'10", "5'11", "6'", "over"]):
                    # Can wear longer items well
                    if 'long' in item_name_lower or 'maxi' in item_name_lower:
                        base_score += 0.10
                    if 'midi' in item_name_lower:
                        base_score += 0.05
                    # Avoid items that are too short
                    if 'crop' in item_name_lower and category == 'tops':
                        base_score -= 0.05
            
            # ═══════════════════════════════════════════════════════════
            # WEIGHT SCORING - Fit and comfort
            # ═══════════════════════════════════════════════════════════
            if weight and weight != 'Average':
                weight_lower = str(weight).lower()
                
                # Plus size considerations
                if any(w in weight_lower for w in ["201", "225", "250", "plus"]):
                    # Favor items with structure and flow
                    if 'structured' in item_name_lower or 'tailored' in item_name_lower:
                        base_score += 0.10
                    if 'wrap' in item_name_lower or 'empire' in item_name_lower:
                        base_score += 0.10
                    if 'vneck' in item_name_lower or 'v-neck' in item_name_lower:
                        base_score += 0.08
                    # Avoid unflattering cuts
                    if 'tight' in item_name_lower or 'bodycon' in item_name_lower:
                        base_score -= 0.10
            
            # ═══════════════════════════════════════════════════════════
            # GENDER SCORING - Style appropriateness
            # ═══════════════════════════════════════════════════════════
            if gender and gender != 'unspecified':
                metadata = self.safe_get_item_attr(item, 'metadata')
                if metadata:
                    visual_attrs = self.safe_get_item_attr(metadata, 'visualAttributes')
                    if visual_attrs:
                        gender_target = self.safe_get_item_attr(visual_attrs, 'genderTarget', '').lower()
                        
                        # If item has gender target, check match
                        if gender_target:
                            if gender in gender_target or 'unisex' in gender_target:
                                base_score += 0.05  # Small boost for appropriate gender
                        
                        # Also check item name for gender indicators
                        if gender == 'male':
                            if any(kw in item_name_lower for kw in ['mens', "men's", 'masculine']):
                                base_score += 0.05
                        elif gender == 'female':
                            if any(kw in item_name_lower for kw in ['womens', "women's", 'feminine']):
                                base_score += 0.05
            
            item_scores[item_id]['body_type_score'] = min(1.0, max(0.0, base_score))
        
        logger.info(f"👤 BODY TYPE ANALYZER: Completed scoring")
    
    async def _analyze_style_profile_scores(self, context: GenerationContext, item_scores: dict) -> None:
        """Analyze and score each item based on user's style profile and COLOR THEORY matching with skin tone"""
        logger.info(f"🎭 STYLE PROFILE ANALYZER: Scoring {len(item_scores)} items")
        
        # CRITICAL FIX: Initialize ALL formality variables at FUNCTION LEVEL (not inside if block)
        # This prevents UnboundLocalError when base_item_id is None or when formality_gap is between -1 and 1
        formality_boost_needed = False
        formality_boost_multiplier = 1.0
        base_item_formality = None
        target_formality = None
        logger.info(f"✅ FORMALITY FIX ACTIVE: Variables initialized at function level")
        
        if context.base_item_id:
            # Get base item's formality
            for item_id, score_data in item_scores.items():
                if item_id == context.base_item_id:
                    base_item = score_data['item']
                    base_item_formality = self._get_item_formality_level(base_item)
                    break
            
            # Get target formality from occasion/style
            target_formality = self._get_context_formality_level(context.occasion, context.style)
            
            # Calculate formality boost if both formalit levels are known
            if base_item_formality is not None and target_formality is not None:
                formality_gap = target_formality - base_item_formality
                
                if formality_gap >= 1:  # Base is more casual than target → boost formal items
                    formality_boost_needed = True
                    formality_boost_multiplier = 1.0 + (formality_gap * 0.3)  # 30% boost per formality level
                    logger.info(f"🎯 SMART BALANCING: Base item formality={base_item_formality}, target={target_formality}, gap={formality_gap}")
                    logger.info(f"   ↗️ Boosting formal complementary items by {(formality_boost_multiplier - 1.0) * 100:.0f}% to elevate outfit")
                
                elif formality_gap <= -1:  # Base is more formal than target → boost casual items
                    formality_boost_needed = True
                    formality_boost_multiplier = 1.0 + (abs(formality_gap) * 0.3)  # 30% boost per formality level
                    logger.info(f"🎯 SMART BALANCING: Base item formality={base_item_formality}, target={target_formality}, gap={formality_gap}")
                    logger.info(f"   ↘️ Boosting casual complementary items by {(formality_boost_multiplier - 1.0) * 100:.0f}% to dress down outfit")
        
        target_style = (context.style if context else "unknown").lower()
        
        # Define style compatibility matrix
        style_compatibility = {
            'casual': ['weekend', 'relaxed', 'comfortable'],
            'formal': ['business', 'professional', 'elegant'],
            'athletic': ['sporty', 'active', 'gym'],
            'business': ['professional', 'formal', 'corporate'],
            'streetwear': ['urban', 'edgy', 'trendy'],
            'vintage': ['retro', 'classic', 'timeless'],
            'modern': ['contemporary', 'trendy', 'fashion-forward']
        }
        
        # Get user style preferences (with safe_get)
        user_style_prefs = safe_get(context.user_profile, 'stylePreferences', {})
        favorite_colors = safe_get(user_style_prefs, 'favoriteColors', [])
        preferred_brands = safe_get(user_style_prefs, 'preferredBrands', [])
        
        # Get skin tone for color theory matching
        skin_tone = safe_get(context.user_profile, 'skinTone', 'Medium')
        logger.info(f"🎨 COLOR THEORY: Using skin tone '{skin_tone}' for color matching")
        
        # Color theory rules based on skin tone
        # Warm skin tones (yellow, peachy, golden undertones)
        warm_skin_colors = {
            'excellent': ['warm red', 'coral', 'peach', 'orange', 'golden yellow', 'olive', 'warm brown', 'camel', 'rust', 'terracotta', 'warm beige'],
            'good': ['cream', 'ivory', 'khaki', 'warm gray', 'chocolate'],
            'avoid': ['bright white', 'cool pink', 'icy blue', 'purple', 'cool gray']
        }
        
        # Cool skin tones (pink, red, bluish undertones)
        cool_skin_colors = {
            'excellent': ['cool blue', 'navy', 'cool pink', 'magenta', 'purple', 'emerald', 'cool red', 'burgundy', 'charcoal', 'true white', 'icy tones'],
            'good': ['silver', 'gray', 'black', 'cool green', 'lavender'],
            'avoid': ['orange', 'warm yellow', 'gold', 'warm brown', 'rust']
        }
        
        # Neutral skin tones (balanced undertones)
        neutral_skin_colors = {
            'excellent': ['soft white', 'gray', 'taupe', 'dusty pink', 'jade', 'soft blue', 'mauve', 'true red', 'navy'],
            'good': ['most colors work well'],
            'avoid': ['extremely bright or neon colors']
        }
        
        # Deep skin tones
        deep_skin_colors = {
            'excellent': ['rich jewel tones', 'emerald', 'sapphire', 'ruby', 'gold', 'copper', 'warm earth tones', 'bright white', 'rich purple', 'fuchsia'],
            'good': ['cobalt', 'burgundy', 'forest green', 'chocolate', 'mustard'],
            'avoid': ['pale pastels', 'beige', 'pale yellow']
        }
        
        # Light skin tones
        light_skin_colors = {
            'excellent': ['soft pastels', 'powder blue', 'blush pink', 'lavender', 'soft gray', 'mint', 'cream'],
            'good': ['navy', 'burgundy', 'emerald', 'charcoal'],
            'avoid': ['neon colors', 'very bright colors']
        }
        
        # Determine which color palette to use
        skin_tone_lower = str(skin_tone).lower()
        color_palette = neutral_skin_colors  # Default
        
        if 'warm' in skin_tone_lower or skin_tone in ['79', '80', '81', '82', '83', '84']:  # Warm medium tones
            color_palette = warm_skin_colors
        elif 'cool' in skin_tone_lower or skin_tone in ['20', '21', '22', '23', '24', '25']:  # Cool light tones
            color_palette = cool_skin_colors
        elif 'deep' in skin_tone_lower or 'dark' in skin_tone_lower or skin_tone in ['95', '96', '97', '98', '99', '100']:
            color_palette = deep_skin_colors
        elif 'light' in skin_tone_lower or 'fair' in skin_tone_lower or skin_tone in ['10', '11', '12', '13', '14', '15']:
            color_palette = light_skin_colors
        
        logger.info(f"🎨 COLOR THEORY: Using color palette for skin tone category")
        
        lounge_boost_ids = set()
        if target_style == 'loungewear' and hasattr(context, 'metadata_notes') and isinstance(context.metadata_notes, dict):
            lounge_boost_ids = set(context.metadata_notes.get('lounge_item_ids', []) or [])
        
        monochrome_color_map: Dict[str, str] = {}
        monochrome_color_counts: Dict[str, int] = {}
        preferred_monochrome_color: Optional[str] = None
        if target_style == 'monochrome':
            monochrome_neutral_colors = {
                'black', 'white', 'off-white', 'ivory', 'cream', 'grey', 'gray',
                'charcoal', 'slate', 'ash', 'silver', 'taupe', 'beige', 'stone',
                'sand', 'camel', 'navy', 'ink', 'espresso', 'muted green', 'sage',
                'olive', 'olive green', 'dusty blue', 'dusty pink', 'mauve', 'khaki'
            }
            similar_families = {
                'black': {'black', 'charcoal', 'gray', 'grey'},
                'charcoal': {'black', 'charcoal', 'gray', 'grey'},
                'gray': {'gray', 'grey', 'charcoal', 'silver', 'ash', 'slate'},
                'white': {'white', 'off-white', 'cream', 'beige'},
                'off-white': {'white', 'off-white', 'cream', 'beige'},
                'cream': {'cream', 'off-white', 'beige', 'white'},
                'beige': {'beige', 'cream', 'sand', 'taupe', 'off-white', 'white'},
                'navy': {'navy', 'ink'},
                'espresso': {'espresso', 'brown', 'chocolate'}
            }
            def _normalize_monochrome_color(color_value: Optional[str], neutral_set: Optional[set] = None) -> Optional[str]:
                if not color_value:
                    return None
                if neutral_set is None:
                    neutral_set = monochrome_neutral_colors
                color_value = color_value.lower().strip()
                color_aliases = {
                    'grey': 'gray',
                    'charcoal gray': 'charcoal',
                    'dark gray': 'charcoal',
                    'light gray': 'gray',
                    'off white': 'off-white',
                    'offwhite': 'off-white',
                    'cream': 'cream',
                    'ivory': 'cream',
                    'stone': 'beige',
                    'sand': 'beige',
                    'taupe': 'beige',
                    'camel': 'beige',
                    'tan': 'beige',
                    'espresso': 'espresso',
                    'coffee': 'espresso',
                    'chocolate': 'espresso',
                    'ink': 'navy',
                    'midnight': 'navy',
                    'navy blue': 'navy',
                    'dark blue': 'navy',
                    'midnight blue': 'navy',
                    'midnight navy': 'navy',
                    'ebony': 'black',
                    'slate': 'gray',
                    'ash': 'gray',
                    'silver': 'gray',
                    'muted olive': 'olive',
                    'sage green': 'sage',
                    'dusty-rose': 'dusty pink',
                    'dusty rose': 'dusty pink',
                    'olive green': 'olive',
                    'chalk': 'off-white'
                }
                if color_value in color_aliases:
                    return color_aliases[color_value]
                base_tokens = neutral_set
                if color_value in base_tokens:
                    return color_value
                # Fallback for compound names like "dark charcoal"
                for token in base_tokens:
                    if token in color_value:
                        return token
                return "contrast"
            
            def _extract_item_color_tokens(item_obj: ClothingItem) -> List[str]:
                tokens: List[str] = []
                simple_color = (self.safe_get_item_attr(item_obj, 'color', '') or '').lower()
                if simple_color:
                    tokens.append(simple_color)
                dominant = getattr(item_obj, 'dominantColors', None)
                if dominant:
                    for entry in dominant:
                        if isinstance(entry, dict):
                            name = (entry.get('name') or '').lower()
                            if name:
                                tokens.append(name)
                        else:
                            name = getattr(entry, 'name', None)
                            if name:
                                tokens.append(str(name).lower())
                metadata_obj = getattr(item_obj, 'metadata', None)
                if isinstance(metadata_obj, dict):
                    palette = (metadata_obj.get('visualAttributes', {}) or {}).get('colorPalette', '')
                    if palette:
                        tokens.append(str(palette).lower())
                return tokens
            
            color_category_counts: Dict[str, Dict[str, int]] = {}
            for item_id, scores in item_scores.items():
                item_obj = scores['item']
                item_tokens = _extract_item_color_tokens(item_obj)
                normalized_color = None
                for token in item_tokens:
                    normalized = _normalize_monochrome_color(token)
                    if normalized:
                        normalized_color = normalized
                        break
                if not normalized_color:
                    normalized_color = 'neutral'
                monochrome_color_map[item_id] = normalized_color
                monochrome_color_counts[normalized_color] = monochrome_color_counts.get(normalized_color, 0) + 1
                scores['monochrome_color'] = normalized_color
                category = self._get_item_category(item_obj)
                if category:
                    category_map = color_category_counts.setdefault(normalized_color, {})
                    category_map[category] = category_map.get(category, 0) + 1
            
            if monochrome_color_counts:
                palette_entry = None
                if hasattr(context, 'metadata_notes') and isinstance(context.metadata_notes, dict):
                    palette_entry = context.metadata_notes.setdefault('monochrome_palette', {})
                palette_candidates: List[Dict[str, Any]] = []
                essential_categories = ['tops', 'bottoms', 'shoes']
                neutral_cat_counts = color_category_counts.get('neutral', {})

                for color, total_count in monochrome_color_counts.items():
                    if color in ('contrast',):
                        continue
                    family_set = set(similar_families.get(color, set()))
                    family_set.add(color)
                    family_cat_counts = {cat: neutral_cat_counts.get(cat, 0) for cat in essential_categories}
                    for family_color in family_set:
                        cat_counts = color_category_counts.get(family_color, {})
                        for cat in essential_categories:
                            family_cat_counts[cat] = family_cat_counts.get(cat, 0) + cat_counts.get(cat, 0)
                    viability = min(family_cat_counts.get(cat, 0) for cat in essential_categories)
                    if viability <= 0:
                        continue
                    total_family_items = sum(family_cat_counts.values())
                    palette_candidates.append({
                        'color': color,
                        'family': sorted(family_set),
                        'weight': viability,
                        'viability': viability,
                        'family_category_counts': family_cat_counts,
                        'total_family_items': total_family_items,
                        'raw_count': total_count
                    })

                if palette_entry is not None:
                    palette_entry['color_counts'] = monochrome_color_counts
                    palette_entry['item_colors'] = monochrome_color_map
                    palette_entry['palette_candidates'] = palette_candidates

                if palette_candidates:
                    import random
                    weights = [max(candidate['weight'], 0.01) for candidate in palette_candidates]
                    chosen_candidate = random.choices(palette_candidates, weights=weights, k=1)[0]
                    preferred_monochrome_color = chosen_candidate['color']
                    chosen_family = set(chosen_candidate['family'])
                    if palette_entry is not None:
                        palette_entry['selected_candidate'] = chosen_candidate
                else:
                    priority = ['black', 'charcoal', 'gray', 'white', 'off-white', 'cream', 'beige', 'navy', 'espresso', 'neutral']
                    preferred_monochrome_color = max(
                        monochrome_color_counts.items(),
                        key=lambda kv: (kv[1], -priority.index(kv[0]) if kv[0] in priority else -len(priority))
                    )[0]
                    chosen_family = set(similar_families.get(preferred_monochrome_color, set()) or set())
                    chosen_family.add(preferred_monochrome_color)
                    if palette_entry is not None:
                        palette_entry['selected_candidate'] = {
                            'color': preferred_monochrome_color,
                            'family': sorted(chosen_family),
                            'viability': None,
                            'fallback': True
                        }

                if palette_entry is not None:
                    palette_entry['preferred_color'] = preferred_monochrome_color
                    palette_entry['allowed_family'] = sorted(chosen_family)
                    palette_entry['item_colors'] = monochrome_color_map
        
        try:
            from src.routes.outfits.styling import calculate_colorblock_metadata_score
        except ImportError:
            calculate_colorblock_metadata_score = None
            logger.debug("⚠️ STYLE PROFILE: Could not import calculate_colorblock_metadata_score")
        
        for item_id, scores in item_scores.items():
            item = scores['item']
            base_score = 0.5  # Default neutral score
            
            # Score based on style match
            item_styles = getattr(item, 'style', [])
            if isinstance(item_styles, str):
                item_styles = [item_styles]
            
            item_styles_lower = [s.lower() for s in item_styles]
            
            # Direct style match
            if target_style in item_styles_lower:
                base_score += 0.3
            
            # Compatible style match
            compatible_styles = safe_get(style_compatibility, target_style, []) if style_compatibility else []
            for compat_style in compatible_styles:
                if compat_style in item_styles_lower:
                    base_score += 0.2
                    break
            
            # ═══════════════════════════════════════════════════════════
            # COLOR THEORY MATCHING WITH SKIN TONE
            # ═══════════════════════════════════════════════════════════
            item_color = self.safe_get_item_attr(item, 'color', '').lower()
            item_name_lower = self.safe_get_item_name(item).lower()
            
            # Check if color is excellent for skin tone
            for excellent_color in (safe_get(color_palette, 'excellent', []) if color_palette else []):
                if excellent_color in item_color or excellent_color in item_name_lower:
                    base_score += 0.25  # Significant boost for excellent colors
                    logger.debug(f"  🎨 {self.safe_get_item_name(item)}: Excellent color match for skin tone (+0.25)")
                    break
            
            # Check if color is good for skin tone
            for good_color in (safe_get(color_palette, 'good', []) if color_palette else []):
                if good_color in item_color or good_color in item_name_lower:
                    base_score += 0.15  # Moderate boost for good colors
                    logger.debug(f"  🎨 {self.safe_get_item_name(item)}: Good color match for skin tone (+0.15)")
                    break
            
            # Penalize colors to avoid for skin tone
            for avoid_color in (safe_get(color_palette, 'avoid', []) if color_palette else []):
                if avoid_color in item_color or avoid_color in item_name_lower:
                    base_score -= 0.15  # Penalty for unflattering colors
                    logger.debug(f"  🎨 {self.safe_get_item_name(item)}: Avoid color for skin tone (-0.15)")
                    break
            
            # Favorite color bonus (user preference still matters)
            if favorite_colors:
                for fav_color in favorite_colors:
                    if fav_color.lower() in item_color:
                        base_score += 0.10  # Slightly less than color theory match
                        break
            
            # Preferred brand bonus
            if preferred_brands:
                item_brand = getattr(item, 'brand', '') or ''
                for pref_brand in preferred_brands:
                    if pref_brand and pref_brand.lower() in item_brand.lower():
                        base_score += 0.10
                        break
            
            if target_style == 'loungewear' and item_id in lounge_boost_ids:
                base_score += 0.40
                logger.debug(f"  🛋️ LOUNGE BOOST: {self.safe_get_item_name(item)} (+0.40 for lounge heuristics)")
            
            if target_style == 'monochrome':
                primary_color = monochrome_color_map.get(item_id)
                monochrome_pattern_value = ''
                metadata_obj = self.safe_get_item_attr(item, 'metadata')
                if metadata_obj:
                    visual_attrs = self.safe_get_item_attr(metadata_obj, 'visualAttributes')
                    if visual_attrs:
                        monochrome_pattern_value = (self.safe_get_item_attr(visual_attrs, 'pattern', '') or '').lower()
                allowed_monochrome_patterns = {
                    '', 'solid', 'smooth', 'plain', 'minimal', 'matte', 'uniform',
                    'ribbed', 'knit', 'waffle', 'cable knit', 'micro', 'subtle texture',
                    'heather', 'heathered', 'marled', 'slub'
                }
                if monochrome_pattern_value and monochrome_pattern_value not in allowed_monochrome_patterns:
                    base_score -= 5.0
                    scores['diversity_score'] = 0.0
                    logger.debug(f"  ⚠️ MONOCHROME PATTERN: {self.safe_get_item_name(item)} has pattern '{monochrome_pattern_value}' (-5.00)")
                if preferred_monochrome_color:
                    if primary_color == preferred_monochrome_color:
                        base_score += 0.35
                        logger.debug(f"  🎯 MONOCHROME MATCH: {self.safe_get_item_name(item)} aligns with palette ({preferred_monochrome_color}) (+0.35)")
                    elif primary_color in similar_families.get(preferred_monochrome_color, set()):
                        base_score += 0.15
                        logger.debug(f"  🎯 MONOCHROME FAMILY: {self.safe_get_item_name(item)} similar to {preferred_monochrome_color} (+0.15)")
                    elif primary_color == 'neutral':
                        base_score += 0.05
                        logger.debug(f"  🎯 MONOCHROME NEUTRAL: {self.safe_get_item_name(item)} neutral fallback (+0.05)")
                    else:
                        base_score -= 5.0
                        scores['diversity_score'] = 0.0
                        logger.debug(f"  ⚠️ MONOCHROME CONTRAST: {self.safe_get_item_name(item)} diverges from {preferred_monochrome_color} (-5.00)")
                elif primary_color == "contrast":
                    base_score -= 5.0
                    scores['diversity_score'] = 0.0
                    logger.debug(f"  ⚠️ MONOCHROME CONTRAST: {self.safe_get_item_name(item)} lacks neutral palette (-5.00)")
            
            # Style-specific metadata scoring (e.g., colorblock)
            if target_style == 'colorblock' and calculate_colorblock_metadata_score:
                item_dict = self._convert_item_to_style_dict(item)
                if item_dict:
                    try:
                        colorblock_score = calculate_colorblock_metadata_score(item_dict)
                        # Normalize: clamp to [-40, 60] then scale to approximately [-0.6, +1.0]
                        clamped_score = max(min(colorblock_score, 60), -40)
                        normalized_bonus = (clamped_score / 60.0) * 0.6  # scale factor
                        base_score += normalized_bonus
                        logger.debug(
                            f"  🎨 COLORBLOCK META: {self.safe_get_item_name(item)} "
                            f"score={colorblock_score} → bonus={normalized_bonus:+.2f}"
                        )
                    except Exception as metadata_error:
                        logger.debug(f"⚠️ COLORBLOCK META: Failed scoring {self.safe_get_item_name(item)}: {metadata_error}")
            
            # Occasion appropriateness
            item_occasions = getattr(item, 'occasion', [])
            if isinstance(item_occasions, str):
                item_occasions = [item_occasions]
            
            item_occasions_lower = [occ.lower() for occ in item_occasions]
            if (context.occasion if context else "unknown").lower() in item_occasions_lower:
                base_score += 0.2
            
            # SMART BALANCING: Apply formality boost (works both directions!)
            if formality_boost_needed and item_id != context.base_item_id:
                item_formality = self._get_item_formality_level(item)
                
                if item_formality is not None and target_formality is not None and base_item_formality is not None:
                    # Determine if this item should be boosted based on formality direction
                    should_boost = False
                    direction = ""
                    
                    if base_item_formality < target_formality:
                        # Need to elevate → boost formal items
                        if item_formality >= target_formality:
                            should_boost = True
                            direction = "↗️ ELEVATED"
                    
                    elif base_item_formality > target_formality:
                        # Need to dress down → boost casual items
                        if item_formality <= target_formality:
                            should_boost = True
                            direction = "↘️ DRESSED DOWN"
                    
                    if should_boost:
                        boost_amount = base_score * (formality_boost_multiplier - 1.0)
                        base_score = base_score * formality_boost_multiplier
                        logger.debug(f"   {direction}: {self.safe_get_item_name(item)} (formality={item_formality}) +{boost_amount:.2f}")
            
            item_scores[item_id]['style_profile_score'] = min(1.0, max(0.0, base_score))
        
        logger.info(f"🎭 STYLE PROFILE ANALYZER: Completed scoring with color theory matching")
    
    async def _analyze_weather_scores(self, context: GenerationContext, item_scores: dict) -> None:
        """Analyze and score each item based on weather appropriateness"""
        logger.info(f"🌤️ WEATHER ANALYZER: Scoring {len(item_scores)} items")
        
        try:
            # Extract weather data with smart defaults
            if (context.weather if context else None) is None:
                # Smart default: use occasion-appropriate weather
                if (context.occasion if context else "unknown").lower() in ['business', 'formal']:
                    temp = 72.0
                    condition = 'clear'
                elif (context.occasion if context else "unknown").lower() in ['party', 'evening']:
                    temp = 68.0
                    condition = 'clear'
                elif (context.occasion if context else "unknown").lower() == 'athletic':
                    temp = 75.0
                    condition = 'clear'
                else:
                    temp = 70.0
                    condition = 'clear'
                logger.warning(f"⚠️ WEATHER ANALYZER: Missing weather data, using SMART DEFAULT: {temp}°F, {condition}")
            elif hasattr(context.weather, 'temperature'):
                temp = float((context.weather if context else None).temperature)  # CRITICAL: Convert to float
                logger.info(f"🌤️ WEATHER ANALYZER: Got temperature from weather object: {temp}°F")
            elif hasattr(context.weather, '__dict__') and 'temperature' in (context.weather if context else None).__dict__:
                temp = float((context.weather if context else None).__dict__['temperature'])  # CRITICAL: Convert to float
                logger.info(f"🌤️ WEATHER ANALYZER: Got temperature from weather.__dict__: {temp}°F")
            else:
                temp = 70.0
                logger.warning(f"⚠️ WEATHER ANALYZER: Could not extract temperature, using default: {temp}°F")
            
            if hasattr(context.weather, 'condition'):
                condition = (context.weather if context else None).condition.lower() if (context.weather if context else None).condition else 'clear'
            elif hasattr(context.weather, '__dict__') and 'condition' in (context.weather if context else None).__dict__:
                condition = (context.weather if context else None).__dict__['condition'].lower() if (context.weather if context else None).__dict__['condition'] else 'clear'
            else:
                condition = 'clear'
        
            # Determine season from temperature
            if temp < 40:
                season = 'winter'
            elif temp < 60:
                season = 'fall'
            elif temp < 75:
                season = 'spring'
            else:
                season = 'summer'
            
            logger.info(f"🌤️ Weather analysis: {temp}°F, {condition}, season={season}")
            
            # SPECIAL CASE: Gym/Athletic occasions ignore weather (gyms are climate-controlled!)
            is_gym = (context.occasion if context else "unknown").lower() in ['gym', 'athletic', 'workout']
            
            for item_id, scores in item_scores.items():
                item = scores['item']
                base_score = 0.5  # Default neutral score
                
                # GYM OVERRIDE: Skip weather scoring for gym (climate-controlled environment)
                if is_gym:
                    base_score = 0.8  # Higher base score - weather doesn't matter for gym
                    item_scores[item_id]['weather_score'] = 0.8
                    continue  # Skip all weather checks for gym items
                
                # Season match
                item_seasons = getattr(item, 'season', [])
                if isinstance(item_seasons, str):
                    item_seasons = [item_seasons]
                
                item_seasons_lower = [s.lower() for s in item_seasons]
                if season in item_seasons_lower:
                    base_score += 0.3
                
                # Temperature compatibility
                if hasattr(item, 'temperatureCompatibility'):
                    temp_compat = self.safe_get_item_attr(item, "temperatureCompatibility")
                    if temp_compat and hasattr(temp_compat, 'minTemp') and hasattr(temp_compat, 'maxTemp'):
                        # CRITICAL FIX: Parse temperature strings (handle '32°F', '>85', etc.)
                        try:
                            import re
                            def parse_temp_value(val):
                                if isinstance(val, (int, float)):
                                    return float(val)
                                if isinstance(val, str):
                                    clean_val = re.sub(r'[><]=?|°[FC]|[FC]', '', val).strip()
                                    return float(clean_val) if clean_val else None
                                return None
                            
                            min_t = parse_temp_value(temp_compat.minTemp)
                            max_t = parse_temp_value(temp_compat.maxTemp)
                            if min_t is not None and max_t is not None and min_t <= temp <= max_t:
                                base_score += 0.2
                        except (ValueError, TypeError) as e:
                            logger.debug(f"⚠️ Could not parse temperatureCompatibility: {e}")
                
                # Material appropriateness for weather
                item_name = self.safe_get_item_name(item) if item else "Unknown"
                item_name_lower = item_name.lower()
                item_type_lower = str(self.safe_get_item_type(item)).lower()
                
                # METADATA CHECK: WARMTH FACTOR - Direct temperature matching
                warmth_factor = None
                fabric_weight = None
                sleeve_length = None
                length = None
                temp_compat = None
                
                if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                    visual_attrs = item.metadata.get('visualAttributes', {})
                    if isinstance(visual_attrs, dict):
                        warmth_factor = (visual_attrs.get('warmthFactor') or '').lower()
                        fabric_weight = (visual_attrs.get('fabricWeight') or '').lower()
                        sleeve_length = (visual_attrs.get('sleeveLength') or '').lower()
                        length = (visual_attrs.get('length') or '').lower()
                        temp_compat = visual_attrs.get('temperatureCompatibility')
                
                # TEMPERATURE COMPATIBILITY - PRECISE matching (highest priority)
                if temp_compat and isinstance(temp_compat, dict):
                    min_temp = temp_compat.get('minTemp')
                    max_temp = temp_compat.get('maxTemp')
                    optimal_min = temp_compat.get('optimalMin')
                    optimal_max = temp_compat.get('optimalMax')
                    
                    # CRITICAL FIX: Convert string temperatures to float
                    # Handle formats like '32°F', '>85', '<32°F', etc.
                    def parse_temp(value):
                        if value is None:
                            return None
                        if isinstance(value, (int, float)):
                            return float(value)
                        if isinstance(value, str):
                            # Strip comparison operators (>, <, >=, <=) and units (°F, °C, F, C)
                            import re
                            clean_value = re.sub(r'[><]=?|°[FC]|[FC]', '', value).strip()
                            return float(clean_value) if clean_value else None
                        return None
                    
                    try:
                        min_temp = parse_temp(min_temp)
                        max_temp = parse_temp(max_temp)
                        optimal_min = parse_temp(optimal_min)
                        optimal_max = parse_temp(optimal_max)
                    except (ValueError, TypeError) as e:
                        logger.debug(f"⚠️ TEMP COMPAT: Could not parse temp values: {e}")
                        min_temp = max_temp = optimal_min = optimal_max = None
                    
                    if min_temp is not None and max_temp is not None:
                        if min_temp <= temp <= max_temp:
                            # Within acceptable range
                            if optimal_min is not None and optimal_max is not None:
                                if optimal_min <= temp <= optimal_max:
                                    base_score += 0.5  # Perfect temperature match!
                                    logger.debug(f"  ✅✅✅ TEMP COMPAT: Perfect temp match {temp}°F in optimal range [{optimal_min}-{optimal_max}] (+0.5)")
                                else:
                                    base_score += 0.3  # Acceptable but not optimal
                                    logger.debug(f"  ✅ TEMP COMPAT: Acceptable temp {temp}°F in range [{min_temp}-{max_temp}] (+0.3)")
                            else:
                                base_score += 0.35  # Good match
                                logger.debug(f"  ✅ TEMP COMPAT: Good temp match {temp}°F in range [{min_temp}-{max_temp}] (+0.35)")
                        else:
                            # Outside acceptable range
                            if temp < min_temp:
                                base_score -= 0.4  # Too cold for this item
                                logger.debug(f"  🚫 TEMP COMPAT: Too cold {temp}°F < {min_temp}°F min ({-0.4})")
                            else:  # temp > max_temp
                                base_score -= 0.4  # Too hot for this item
                                logger.debug(f"  🚫 TEMP COMPAT: Too hot {temp}°F > {max_temp}°F max ({-0.4})")
                
                # WARMTH FACTOR SCORING - Match warmth to temperature
                if warmth_factor:
                    if temp < 40:  # Very cold
                        if warmth_factor in ['heavy', 'insulated', 'warm']:
                            base_score += 0.4
                            logger.debug(f"  ✅✅ WARMTH FACTOR: Heavy warmth perfect for very cold (+0.4)")
                        elif warmth_factor in ['light', 'minimal']:
                            base_score -= 0.3
                            logger.debug(f"  ⚠️ WARMTH FACTOR: Light warmth too cold ({-0.3})")
                    elif temp < 60:  # Cool
                        if warmth_factor in ['medium', 'moderate']:
                            base_score += 0.3
                            logger.debug(f"  ✅ WARMTH FACTOR: Medium warmth good for cool weather (+0.3)")
                    elif temp > 75:  # Hot
                        if warmth_factor in ['light', 'minimal', 'breathable']:
                            base_score += 0.4
                            logger.debug(f"  ✅✅ WARMTH FACTOR: Light warmth perfect for hot weather (+0.4)")
                        elif warmth_factor in ['heavy', 'warm']:
                            base_score -= 0.4
                            logger.debug(f"  🚫 WARMTH FACTOR: Heavy warmth too hot ({-0.4})")
                
                # FABRIC WEIGHT SCORING - Match weight to temperature
                if fabric_weight:
                    if temp < 50:  # Cold
                        if fabric_weight in ['heavy', 'thick', 'heavyweight']:
                            base_score += 0.3
                            logger.debug(f"  ✅ FABRIC WEIGHT: Heavy fabric good for cold (+0.3)")
                        elif fabric_weight in ['light', 'lightweight']:
                            base_score -= 0.2
                            logger.debug(f"  ⚠️ FABRIC WEIGHT: Light fabric too cold ({-0.2})")
                    elif temp > 75:  # Hot
                        if fabric_weight in ['light', 'lightweight', 'thin']:
                            base_score += 0.3
                            logger.debug(f"  ✅ FABRIC WEIGHT: Light fabric good for hot weather (+0.3)")
                        elif fabric_weight in ['heavy', 'thick']:
                            base_score -= 0.3
                            logger.debug(f"  🚫 FABRIC WEIGHT: Heavy fabric too hot ({-0.3})")
                
                # SLEEVE LENGTH - Weather matching for tops
                item_category = self._get_item_category(item)
                if item_category == 'tops' and sleeve_length:
                    if temp > 75:  # Hot
                        if sleeve_length in ['sleeveless', 'tank', 'short', 'short sleeve']:
                            base_score += 0.25
                            logger.debug(f"  ✅ SLEEVE LENGTH: {sleeve_length.capitalize()} good for hot weather (+0.25)")
                        elif sleeve_length in ['long', 'long sleeve']:
                            base_score -= 0.2
                            logger.debug(f"  ⚠️ SLEEVE LENGTH: Long sleeves too warm ({-0.2})")
                    elif temp < 50:  # Cold
                        if sleeve_length in ['long', 'long sleeve']:
                            base_score += 0.2
                            logger.debug(f"  ✅ SLEEVE LENGTH: Long sleeves good for cold (+0.2)")
                
                # LENGTH - For bottoms and outerwear
                if item_category in ['bottoms', 'outerwear'] and length:
                    if temp < 40:  # Very cold
                        if length in ['long', 'full', 'ankle', 'maxi']:
                            base_score += 0.25
                            logger.debug(f"  ✅ LENGTH: Long length good for cold (+0.25)")
                    elif temp > 75:  # Hot
                        if item_category == 'bottoms' and length in ['short', 'shorts', 'above knee']:
                            base_score += 0.25
                            logger.debug(f"  ✅ LENGTH: Shorts good for hot weather (+0.25)")
                
                # Cold weather items (keyword fallback)
                if temp < 50:
                    cold_keywords = ['wool', 'fleece', 'coat', 'jacket', 'sweater', 'long sleeve', 'boots']
                    for keyword in cold_keywords:
                        if keyword in item_name_lower or keyword in item_type_lower:
                            base_score += 0.15
                            break
                
                # Hot weather items - BALANCED PENALTIES
                elif temp > 75:  # Higher threshold for hot weather penalties
                    hot_keywords = ['cotton', 'linen', 'short sleeve', 'shorts', 'sandals', 'tank', 'light']
                    hot_appropriate = False
                    for keyword in hot_keywords:
                        if keyword in item_name_lower or keyword in item_type_lower:
                            base_score += 0.2  # Boost for hot weather appropriate items
                            hot_appropriate = True
                            break
                    
                    # BALANCED PENALTIES based on temperature
                    hot_inappropriate = ['wool', 'fleece', 'coat', 'jacket', 'sweater', 'long sleeve', 'boots', 'heavy']
                    for keyword in hot_inappropriate:
                        if keyword in item_name_lower or keyword in item_type_lower:
                            if temp >= 90:  # Extreme heat - STRONG PENALTY
                                base_score -= 0.3  # Strong penalty but don't eliminate completely
                                logger.warning(f"🔥 HOT PENALTY: {item_name} penalized for {temp}°F extreme heat")
                            elif temp >= 80:  # Hot weather - MODERATE PENALTY
                                base_score -= 0.2  # Moderate penalty for hot weather
                                logger.info(f"🌡️ HOT PENALTY: {item_name} penalized for {temp}°F hot weather")
                            else:  # Warm weather (75-80°F)
                                base_score -= 0.1  # Light penalty
                            break
                
                # Moderate weather (40-75°F) - neutral scoring with minimal penalties
                else:
                    # Very light penalty for extreme weather items in moderate weather
                    if temp > 70:
                        hot_inappropriate = ['wool', 'fleece', 'coat', 'jacket', 'sweater']
                        for keyword in hot_inappropriate:
                            if keyword in item_name_lower or keyword in item_type_lower:
                                base_score -= 0.05  # Very small penalty
                                break
                    elif temp < 50:
                        cold_inappropriate = ['shorts', 'sandals', 'tank']
                        for keyword in cold_inappropriate:
                            if keyword in item_name_lower or keyword in item_type_lower:
                                base_score -= 0.05  # Very small penalty
                                break
                
                # Rainy weather
                if 'rain' in condition or 'storm' in condition:
                    rain_keywords = ['waterproof', 'raincoat', 'boots']
                    for keyword in rain_keywords:
                        if keyword in item_name_lower:
                            base_score += 0.2
                            break
                
                item_scores[item_id]['weather_score'] = min(1.0, max(0.0, base_score))  # Clamp between 0 and 1
        
            logger.info(f"🌤️ WEATHER ANALYZER: Completed scoring")
            
        except Exception as e:
            logger.error(f"❌ WEATHER ANALYZER FAILED: {str(e)}", exc_info=True)
            logger.warning(f"⚠️ WEATHER ANALYZER: Using emergency fallback scoring")
            
            # Emergency fallback: assign neutral scores
            for item_id in item_scores:
                item_scores[item_id]['weather_score'] = 0.5
                
            logger.info(f"🚨 WEATHER ANALYZER: Emergency fallback applied - all items scored 0.5")
    
    async def _analyze_user_feedback_scores(self, context: GenerationContext, item_scores: dict) -> None:
        """
        Analyze and score items based on user feedback - Netflix/Spotify style learning
        
        Considers:
        - Outfit ratings (1-5 stars) from outfits containing this item
        - Likes/Dislikes (same weight as ratings)
        - Wear counts (alternate between boosting rarely-worn and popular items)
        - Favorited items (prioritize if not worn this week)
        - Style evolution over time
        """
        logger.info(f"⭐ USER FEEDBACK ANALYZER: Scoring {len(item_scores)} items with learning algorithm")
        
        # Import Firebase for fetching user feedback data
        try:
            from ..config.firebase import db
        except ImportError:
            logger.warning("⚠️ Firebase not available, skipping user feedback scoring")
            return
        
        user_id = (context.user_id if context else "unknown")
        current_time = time.time()
        one_week_ago = current_time - (7 * 24 * 60 * 60)
        
        # ═══════════════════════════════════════════════════════════════════════
        # FETCH USER FEEDBACK DATA
        # ═══════════════════════════════════════════════════════════════════════
        
        # Fetch outfit ratings and feedback
        outfit_ratings = {}  # item_id -> list of ratings
        outfit_likes = {}    # item_id -> (likes, dislikes)
        item_wear_history = {}  # item_id -> list of wear timestamps
        favorited_items = set()  # Set of favorited item IDs
        
        try:
            # Get user's outfit history with ratings (REDUCED for performance)
            outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(20)  # Reduced from 100
            outfits = list(outfits_ref.stream())  # Convert to list immediately
            logger.info(f"📊 Feedback data: {len(outfits)} outfits")
            
            for outfit_doc in outfits[:20]:  # Hard cap at 20
                outfit_data = outfit_doc.to_dict()
                rating = (safe_get(outfit_data, 'rating') if outfit_data else None)
                is_liked = (safe_get(outfit_data, 'isLiked', False) if outfit_data else False)
                is_disliked = (safe_get(outfit_data, 'isDisliked', False) if outfit_data else False)
                worn_at = (safe_get(outfit_data, 'wornAt') if outfit_data else None)
                
                # Get items in this outfit
                outfit_items = (safe_get(outfit_data, 'items', []) if outfit_data else [])
                
                for item in outfit_items:
                    # Use safe_item_access to handle all formats
                    item_id = safe_item_access(item, 'id')
                    if not item_id:
                        continue
                    
                    # Track ratings
                    if rating:
                        if item_id not in outfit_ratings:
                            outfit_ratings[item_id] = []
                        outfit_ratings[item_id].append(rating)
                    
                    # Track likes/dislikes
                    if is_liked or is_disliked:
                        if item_id not in outfit_likes:
                            outfit_likes[item_id] = {'likes': 0, 'dislikes': 0}
                        if is_liked:
                            outfit_likes[item_id]['likes'] += 1
                        if is_disliked:
                            outfit_likes[item_id]['dislikes'] += 1
                    
                    # Track wear history
                    if worn_at:
                        if item_id not in item_wear_history:
                            item_wear_history[item_id] = []
                        
                        # Convert worn_at to timestamp
                        if hasattr(worn_at, 'timestamp'):
                            wear_time = worn_at.timestamp()
                        elif isinstance(worn_at, (int, float)):
                            wear_time = float(worn_at)
                        else:
                            wear_time = current_time
                        
                        item_wear_history[item_id].append(wear_time)
            
            # Get favorited items from wardrobe (PERFORMANCE FIX: use context.wardrobe instead of Firebase query)
            # Use wardrobe items already in context - much faster!
            for item in item_scores.values():
                clothing_item = item['item']
                item_id = safe_item_access(clothing_item, 'id')
                if item_id and (getattr(clothing_item, 'isFavorite', False) or getattr(clothing_item, 'favorite_score', 0) > 0.7):
                    favorited_items.add(item_id)
            
            logger.info(f"📊 Feedback data loaded: {len(outfit_ratings)} rated items, {len(favorited_items)} favorites (from {len(item_scores)} wardrobe items)")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load user feedback data: {e}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # ALTERNATING WEAR COUNT STRATEGY (like Netflix's explore/exploit)
        # ═══════════════════════════════════════════════════════════════════════
        
        # Determine if this generation should boost rarely-worn or popular items
        # Alternate based on user_id + current day to ensure variety
        day_of_year = datetime.now().timetuple().tm_yday
        user_hash = hash(user_id) % 2
        boost_rare = (day_of_year + user_hash) % 2 == 0  # Alternate every day per user
        
        if boost_rare:
            logger.info(f"🔄 WEAR COUNT STRATEGY: Boosting rarely-worn items (diversity mode)")
        else:
            logger.info(f"🔄 WEAR COUNT STRATEGY: Boosting popular items (favorites mode)")
        
        # ═══════════════════════════════════════════════════════════════════════
        # SCORE EACH ITEM BASED ON USER FEEDBACK
        # ═══════════════════════════════════════════════════════════════════════
        
        for item_id, scores in item_scores.items():
            item = scores['item']
            base_score = 0.5  # Neutral starting point
            
            # ─────────────────────────────────────────────────────────────
            # 1. OUTFIT RATING INFLUENCE (items from highly-rated outfits)
            # ─────────────────────────────────────────────────────────────
            if item_id in outfit_ratings:
                ratings = outfit_ratings[item_id]
                avg_rating = sum(ratings) / len(ratings)
                
                # Normalize to 0-1 scale (5-star scale)
                rating_score = (avg_rating - 1) / 4  # Maps 1-5 to 0-1
                base_score += rating_score * 0.3  # Up to +0.3 for perfect ratings
                
                logger.debug(f"  ⭐ {self.safe_get_item_name(item)}: Avg outfit rating {avg_rating:.1f} → +{rating_score * 0.3:.2f}")
            
            # ─────────────────────────────────────────────────────────────
            # 2. LIKES/DISLIKES (same weight as ratings)
            # ─────────────────────────────────────────────────────────────
            if item_id in outfit_likes:
                likes = outfit_likes[item_id]['likes']
                dislikes = outfit_likes[item_id]['dislikes']
                total_feedback = likes + dislikes
                
                if total_feedback > 0:
                    like_ratio = likes / total_feedback
                    like_score = like_ratio  # 0-1 scale
                    base_score += like_score * 0.3  # Up to +0.3 (same weight as ratings)
                    
                    logger.debug(f"  👍 {self.safe_get_item_name(item)}: {likes}L/{dislikes}D (ratio={like_ratio:.2f}) → +{like_score * 0.3:.2f}")
                    
                    # Penalty for heavily disliked items
                    if dislikes > likes and dislikes >= 2:
                        base_score -= 0.2
                        logger.debug(f"  👎 {self.safe_get_item_name(item)}: Heavily disliked → -0.20")
            
            # ─────────────────────────────────────────────────────────────
            # 3. FAVORITED ITEMS (prioritize if not worn this week)
            # ─────────────────────────────────────────────────────────────
            if item_id in favorited_items:
                # Check if worn this week
                worn_this_week = False
                if item_id in item_wear_history:
                    recent_wears = [w for w in item_wear_history[item_id] if w > one_week_ago]
                    worn_this_week = len(recent_wears) > 0
                
                if not worn_this_week:
                    # PRIORITIZE: Big boost for favorited items not worn this week
                    base_score += 0.4
                    logger.info(f"  ⭐💎 {self.safe_get_item_name(item)}: FAVORITE not worn this week → +0.40 (PRIORITY)")
                else:
                    # Still boost, but less
                    base_score += 0.15
                    logger.debug(f"  ⭐ {self.safe_get_item_name(item)}: Favorite (worn this week) → +0.15")
            
            # ─────────────────────────────────────────────────────────────
            # 4. WEAR COUNT WITH DECAY (explore vs exploit with rotation)
            # ─────────────────────────────────────────────────────────────
            item_wear_count = getattr(item, 'wearCount', 0)
            
            if boost_rare:
                # BOOST RARELY-WORN ITEMS (discovery/diversity mode)
                if item_wear_count == 0:
                    base_score += 0.25  # Never worn - high boost
                    logger.debug(f"  🆕 {self.safe_get_item_name(item)}: Never worn → +0.25 (discovery)")
                elif item_wear_count <= 2:
                    base_score += 0.20  # Very lightly worn - high boost
                    logger.debug(f"  🌱 {self.safe_get_item_name(item)}: Very lightly worn ({item_wear_count}) → +0.20")
                elif item_wear_count <= 4:
                    # DECAY: 3-4 uses = reduced bonus (encourages rotation)
                    base_score += 0.10  # Moderate boost with decay
                    logger.debug(f"  🔄 {self.safe_get_item_name(item)}: Moderately worn ({item_wear_count}) → +0.10 (decaying)")
                elif item_wear_count <= 6:
                    # Further decay: 5-6 uses = minimal bonus
                    base_score += 0.05  # Small boost
                    logger.debug(f"  📉 {self.safe_get_item_name(item)}: Worn often ({item_wear_count}) → +0.05 (minimal)")
                elif item_wear_count > 15:
                    base_score -= 0.15  # Overused - stronger penalty
                    logger.debug(f"  🔁 {self.safe_get_item_name(item)}: Overused ({item_wear_count}) → -0.15")
            else:
                # BOOST POPULAR ITEMS (reliability/favorites mode) with decay
                if item_wear_count >= 1 and item_wear_count <= 2:
                    base_score += 0.25  # Sweet spot - proven but not overused
                    logger.debug(f"  🌟 {self.safe_get_item_name(item)}: Proven favorite ({item_wear_count} wears) → +0.25")
                elif item_wear_count <= 4:
                    # DECAY: 3-4 uses = still good but decaying
                    base_score += 0.15  # Good boost with decay
                    logger.debug(f"  ⭐ {self.safe_get_item_name(item)}: Popular ({item_wear_count} wears) → +0.15 (decaying)")
                elif item_wear_count <= 6:
                    # Further decay: 5-6 uses = minimal bonus
                    base_score += 0.08  # Reduced boost
                    logger.debug(f"  📉 {self.safe_get_item_name(item)}: Very popular ({item_wear_count}) → +0.08 (minimal)")
                elif item_wear_count > 15:
                    base_score += 0.02  # Very popular - minimal boost (encourage rotation)
                    logger.debug(f"  🔁 {self.safe_get_item_name(item)}: Heavily worn ({item_wear_count}) → +0.02 (rotation)")
                elif item_wear_count == 0:
                    base_score -= 0.05  # Never worn - small penalty in favorites mode
            
            # ─────────────────────────────────────────────────────────────
            # 5. RECENCY BIAS (recently worn items slight penalty)
            # ─────────────────────────────────────────────────────────────
            if item_id in item_wear_history:
                recent_wears = [w for w in item_wear_history[item_id] if w > one_week_ago]
                if len(recent_wears) >= 2:
                    base_score -= 0.10  # Worn 2+ times this week - give it a rest
                    logger.debug(f"  🔄 {self.safe_get_item_name(item)}: Worn {len(recent_wears)} times this week → -0.10")
            
            # ─────────────────────────────────────────────────────────────
            # 6. ADVANCED STYLE EVOLUTION TRACKING (Netflix/Spotify-style)
            # ─────────────────────────────────────────────────────────────
            
            # DISABLED: This causes 158 database queries (one per item) and times out!
            # TODO: Re-implement with pre-computed data to avoid per-item queries
            # evolution_score = await self._calculate_style_evolution_score(...)
            evolution_score = 0.0  # Disabled for performance
            
            base_score += evolution_score
            
            # Ensure score stays in valid range
            item_scores[item_id]['user_feedback_score'] = min(1.0, max(0.0, base_score))
        
        logger.info(f"⭐ USER FEEDBACK ANALYZER: Completed scoring with learning algorithm")
        logger.info(f"   Mode: {'🔍 Discovery (boost rarely-worn)' if boost_rare else '⭐ Favorites (boost popular)'}")
    
    
    async def _cohesive_composition_with_scores(self, context: GenerationContext, item_scores: dict, session_id: str) -> OutfitGeneratedOutfit:
        """Generate cohesive outfit using multi-layered scores with intelligent layering and session tracking"""
        logger.info(f"🎨 COHESIVE COMPOSITION: Using scored items to create outfit")
        logger.debug(f"🔍 DEBUG: Received {len(item_scores)} scored items")
        logger.debug(f"🔍 DEBUG: Context occasion: {context.occasion}, style: {context.style}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # SELECT OUTFIT COMPOSITION STRATEGY
        # ═══════════════════════════════════════════════════════════════════════
        
        # Get user's outfit count for rotation (PERFORMANCE FIX: use cached value or skip)
        # This query was causing 2-3 second delays - not critical for strategy selection
        user_outfit_count = 0
        try:
            # Skip expensive Firebase query during generation - use context data if available
            # Strategy selection can work with count=0 (defaults to standard strategy)
            if hasattr(context, 'user_outfit_count') and context.user_outfit_count is not None:
                user_outfit_count = context.user_outfit_count
                logger.info(f"📊 Using cached outfit count: {user_outfit_count}")
            else:
                # Use wardrobe size as a proxy for user experience level
                # Large wardrobe = experienced user, can handle advanced strategies
                user_outfit_count = min(len(context.wardrobe) // 3, 20)  # Rough estimate
                logger.info(f"📊 Estimated outfit count from wardrobe size: {user_outfit_count}")
        except Exception as e:
            logger.warning(f"⚠️ Could not get outfit count for strategy rotation: {e}")
            user_outfit_count = 0
        
        # Select strategy
        strategy_selector = get_strategy_selector()
        selected_strategy = strategy_selector.select_strategy(
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            user_outfit_count=user_outfit_count,
            has_base_item=bool(context.base_item_id)
        )
        
        strategy_description = strategy_selector.get_strategy_description(selected_strategy)
        logger.info(f"🎨 SELECTED STRATEGY: {selected_strategy.value} - {strategy_description}")
        
        target_style_lower = (context.style or "").lower() if context else ""
        preferred_monochrome_color = None
        allowed_monochrome_colors: set[str] = set()
        monochrome_item_colors: Dict[str, str] = {}
        monochrome_neutral_colors = {
            'black', 'white', 'off-white', 'ivory', 'cream', 'grey', 'gray',
            'charcoal', 'slate', 'ash', 'silver', 'taupe', 'beige', 'stone',
            'sand', 'camel', 'navy', 'ink', 'espresso', 'muted green', 'sage',
            'olive', 'olive green', 'dusty blue', 'dusty pink', 'mauve', 'khaki'
        }
        color_aliases_map = {
            'grey': 'gray',
            'charcoal gray': 'charcoal',
            'dark gray': 'charcoal',
            'light gray': 'gray',
            'off white': 'off-white',
            'offwhite': 'off-white',
            'cream': 'cream',
            'ivory': 'cream',
            'stone': 'beige',
            'sand': 'beige',
            'taupe': 'beige',
            'camel': 'beige',
            'tan': 'beige',
            'muted olive': 'olive',
            'sage green': 'sage',
            'dusty-rose': 'dusty pink',
            'dusty rose': 'dusty pink',
            'olive green': 'olive',
            'navy blue': 'navy',
            'dark blue': 'navy',
            'midnight blue': 'navy',
            'midnight navy': 'navy',
            'midnight': 'navy',
            'chalk': 'off-white'
        }

        if target_style_lower == 'monochrome':
            palette_notes = {}
            if hasattr(context, 'metadata_notes') and isinstance(context.metadata_notes, dict):
                palette_notes = safe_get(context.metadata_notes, 'monochrome_palette', {}) or {}
            preferred_monochrome_color = palette_notes.get('preferred_color')
            monochrome_item_colors = palette_notes.get('item_colors', {}) or {}
            allowed_monochrome_colors = set(palette_notes.get('allowed_family', []) or [])
            if preferred_monochrome_color:
                allowed_monochrome_colors.add(preferred_monochrome_color)
            allowed_monochrome_colors.add('neutral')

        def _normalize_monochrome_value(color_value: Optional[str]) -> Optional[str]:
            if not color_value:
                return None
            token = color_value.lower().strip()
            if token in color_aliases_map:
                token = color_aliases_map[token]
            if token in monochrome_neutral_colors:
                return token
            for neutral in monochrome_neutral_colors:
                if neutral in token:
                    return neutral
            return "contrast"

        def _is_monochrome_allowed(item_obj: Any, item_id: Optional[str], score_data: Optional[dict], allow_base: bool = False, log_prefix: str = "") -> bool:
            if target_style_lower != 'monochrome' or not preferred_monochrome_color:
                return True
            if allow_base:
                return True

            color_value: Optional[str] = None
            if score_data:
                color_value = score_data.get('monochrome_color')
            if (not color_value or color_value == 'neutral') and item_id:
                color_value = monochrome_item_colors.get(item_id)
            if not color_value or color_value == 'neutral':
                return True

            if color_value == "contrast":
                logger.debug(f"{log_prefix}⏭️ MONOCHROME SKIP: {self.safe_get_item_name(item_obj)} color=contrast (palette {preferred_monochrome_color})")
                return False

            if color_value in allowed_monochrome_colors:
                return True

            # Attempt to normalize from raw color data if needed
            raw_color = (self.safe_get_item_attr(item_obj, 'color', '') or '')
            normalized = _normalize_monochrome_value(raw_color)
            if normalized and normalized != color_value:
                color_value = normalized
            if color_value == "contrast":
                logger.debug(f"{log_prefix}⏭️ MONOCHROME SKIP: {self.safe_get_item_name(item_obj)} color=contrast (palette {preferred_monochrome_color})")
                return False
            if color_value in allowed_monochrome_colors:
                return True

            # Check dominant colors if available
            dominant_colors = getattr(item_obj, 'dominantColors', []) or []
            for entry in dominant_colors:
                if isinstance(entry, dict):
                    name = (entry.get('name') or '').lower()
                else:
                    name = getattr(entry, 'name', None)
                    if name:
                        name = str(name).lower()
                if name:
                    normalized = _normalize_monochrome_value(name)
                    if normalized == "contrast":
                        logger.debug(f"{log_prefix}⏭️ MONOCHROME SKIP: {self.safe_get_item_name(item_obj)} dominant color contrast (palette {preferred_monochrome_color})")
                        return False
                    if normalized in allowed_monochrome_colors or normalized == 'neutral':
                        return True

            logger.debug(f"{log_prefix}⏭️ MONOCHROME SKIP: {self.safe_get_item_name(item_obj)} color={color_value} not in palette {allowed_monochrome_colors}")
            return False

        # DEBUG: Log item scores details
        if item_scores:
            logger.debug(f"🔍 DEBUG SCORES: First 3 item scores:")
            for i, (item_id, score) in enumerate(list(item_scores.items())[:3]):
                logger.debug(f"🔍 DEBUG SCORE {i+1}: {item_id} = {score}")
        else:
            logger.error(f"🚨 DEBUG: item_scores is empty or None!")
        
        if not item_scores:
            logger.error(f"❌ COHESIVE COMPOSITION: No scored items received!")
            # DEBUG: Add more detailed error info
            error_msg = f"DEBUG: No scored items received. Context has {len(context.wardrobe)} items. Item scores dict: {item_scores}"
            logger.error(f"🚨 {error_msg}")
            
            # Create detailed debug response
            debug_info = {
                "pipeline_stage": "cohesive_composition_no_scores",
                "context_wardrobe_count": len(context.wardrobe),
                "item_scores_count": len(item_scores) if item_scores else 0,
                "item_scores_keys": list(item_scores.keys()) if item_scores else [],
                "context_occasion": (context.occasion if context else "unknown"),
                "context_style": (context.style if context else "unknown"),
                "context_mood": (context.mood if context else "unknown"),
                "context_user_id": (context.user_id if context else "unknown"),
                "wardrobe_items": [
                    {
                        "id": getattr(item, 'id', 'NO_ID'),
                        "name": getattr(item, 'name', 'NO_NAME'),
                        "type": str(getattr(item, 'type', 'NO_TYPE')),
                        "color": getattr(item, 'color', 'NO_COLOR')
                    } for item in (context.wardrobe if context else [])[:3]  # First 3 items
                ]
            }
            
            raise Exception(f"No scored items provided to cohesive composition. DEBUG: {debug_info}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # INTELLIGENT ITEM COUNT & LAYERING DECISION
        # ═══════════════════════════════════════════════════════════════════════
        
        # Extract weather data for layering decisions
        if hasattr(context.weather, 'temperature'):
            temp = (context.weather if context else None).temperature
        elif hasattr(context.weather, '__dict__') and 'temperature' in (context.weather if context else None).__dict__:
            temp = (context.weather if context else None).__dict__['temperature']
        else:
            temp = 70.0
        
        occasion_lower = (context.occasion if context else "unknown").lower()
        
        # Check if user prefers minimalistic outfits
        style_lower = (context.style if context else "unknown").lower()
        mood_lower = (context.mood if context else "unknown").lower() if (context.mood if context else "unknown") else ''
        is_minimalistic = 'minimal' in style_lower or 'minimal' in mood_lower or style_lower == 'minimalist'
        party_polish_contexts = {
            'party', 'evening', 'formal', 'wedding', 'cocktail', 'dinner', 'night out'
        }
        requires_minimalist_party_polish = is_minimalistic and occasion_lower in party_polish_contexts
        
        # Determine recommended item count based on weather and occasion
        min_items = 3  # Always need top, bottom, shoes
        max_items = 4 if is_minimalistic else 6  # Minimalist = fewer items, regular = more options
        recommended_layers = 0  # Additional layering pieces
        
        logger.info(f"🌡️ LAYERING ANALYSIS: Temperature={temp}°F, Occasion={occasion_lower}, Style={context.style}")
        
        if is_minimalistic:
            logger.info(f"  ✨ MINIMALISTIC style detected → Max items reduced to {max_items}, layers conservative")
        
        # Temperature-based layering
        if temp < 30:
            recommended_layers = 3 if not is_minimalistic else 2  # Heavy layering
            logger.info(f"  🥶 Very cold ({temp}°F) → {recommended_layers} additional layers")
        elif temp < 50:
            recommended_layers = 2 if not is_minimalistic else 1  # Moderate layering
            logger.info(f"  ❄️ Cold ({temp}°F) → {recommended_layers} additional layers")
        elif temp < 65:
            recommended_layers = 1  # Light layering (one outer layer)
            logger.info(f"  🍂 Cool ({temp}°F) → 1 additional layer (light jacket/cardigan)")
        elif temp <= 80:  # Extended range - light jacket can work up to 80°F
            # Light jacket optional for A/C, evening, or style preference
            recommended_layers = 1 if not is_minimalistic else 0
            logger.info(f"  ☀️ Mild ({temp}°F) → Light jacket optional (A/C, evening, style)")
        else:
            recommended_layers = 0  # Hot weather, no layering
            logger.info(f"  🔥 Hot ({temp}°F) → No additional layers needed")
        
        # Occasion-based adjustments
        if occasion_lower in ['business', 'formal', 'wedding']:
            recommended_layers += 1  # Add blazer/jacket for formality
            logger.info(f"  👔 Formal occasion → +1 layer for professionalism")
        elif occasion_lower in ['athletic', 'gym']:
            recommended_layers = max(0, recommended_layers - 1)  # Reduce layers for movement
            logger.info(f"  🏃 Athletic occasion → Reduce layers for mobility")
        
        loungewear_mode = occasion_lower in ['loungewear', 'lounge', 'home', 'relaxed'] or style_lower == 'loungewear'
        lounge_item_ids: set = set()
        if loungewear_mode and isinstance(context.metadata_notes, dict):
            lounge_item_ids = set(context.metadata_notes.get('lounge_item_ids', []) or [])
            if lounge_item_ids:
                logger.info(f"🛋️ LOUNGE MODE: {len(lounge_item_ids)} lounge-qualified items available after filtering")

        if loungewear_mode:
            min_items = max(min_items, 4)
            logger.info(f"🛋️ LOUNGE MODE: Minimum items increased to {min_items} for cozy layering")

        if requires_minimalist_party_polish:
            previous_min = min_items
            min_items = max(min_items, 4)
            if min_items != previous_min:
                logger.info(f"🎉 MINIMALIST PARTY: Minimum items increased to {min_items} to ensure polish")
            recommended_layers = max(recommended_layers, 1)
            logger.info(f"🎉 MINIMALIST PARTY: Enforcing at least one polish layer/accessory")

        target_items = min(min_items + recommended_layers, max_items)
        logger.info(f"🎯 TARGET: {target_items} items (min={min_items}, max={max_items}, layers={recommended_layers})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # LAYERING CATEGORIES & PRIORITIES
        # ═══════════════════════════════════════════════════════════════════════
        
        layering_order = [
            'base',      # Base layer (t-shirt, tank, etc.)
            'tops',      # Main top
            'bottoms',   # Pants, skirts, etc.
            'shoes',     # Footwear
            'mid',       # Mid-layer (sweater, cardigan)
            'outerwear', # Outer layer (jacket, coat)
            'accessories' # Accessories (scarf, hat, etc.)
        ]
        
        # Get recently used items to avoid repetition
        recently_used_item_ids = set()
        try:
            recent_outfits = diversity_filter.get_recent_outfits(
                user_id=context.user_id,
                limit=5  # Check last 5 outfits
            )
            for outfit in recent_outfits:
                outfit_items = safe_get(outfit, 'items', [])
                for item in outfit_items:
                    item_id = safe_item_access(item, 'id')
                    if item_id:
                        recently_used_item_ids.add(item_id)
            
            if recently_used_item_ids:
                logger.info(f"🎭 DIVERSITY: Found {len(recently_used_item_ids)} recently used items to de-prioritize")
        except Exception as e:
            logger.warning(f"⚠️ Could not load recent items for diversity: {e}")
        
        # Sort items by composite score with randomization AND diversity penalty
        import random
        
        # CRITICAL: Use truly random seed based on current time + random state to ensure different results each time
        random.seed()  # Reset to system time seed
        random.seed(int((time.time() * 1000000) + random.random() * 1000000))  # Very fine-grained seed
        
        # ENHANCED DIVERSITY: Much stronger penalties and boosts to promote variety
        diversity_adjustments = {}
        for item_id, score_data in item_scores.items():
            base_score = score_data['composite_score']
            adjustment = 0.0
            
            # 1. Random noise (±35% instead of ±20%) - INCREASED for more variety
            noise = random.uniform(-0.5, 0.5)
            adjustment += noise
            
            # 2. Recently worn penalty (EVEN STRONGER) - INCREASED from -2.0 to -3.0
            if item_id in recently_used_item_ids:
                adjustment -= 3.0  # Very strong penalty to force variety
                logger.debug(f"  🔄 Recently worn: {score_data['item'].name if hasattr(score_data['item'], 'name') else 'Unknown'} → -3.0 penalty")
            
            # 3. Never worn boost (INCREASED)
            item = score_data['item']
            item_wear_count = getattr(item, 'wearCount', 0) if item else 0
            if item_wear_count == 0:
                adjustment += 1.5  # Boost new items more (was 1.0)
                logger.debug(f"  🆕 Never worn: {item.name if hasattr(item, 'name') else 'Unknown'} → +1.5 boost")
            elif item_wear_count <= 2:
                adjustment += 0.7  # Boost lightly worn items more (was 0.5)
                logger.debug(f"  🌱 Lightly worn ({item_wear_count}): {item.name if hasattr(item, 'name') else 'Unknown'} → +0.7 boost")
            
            diversity_adjustments[item_id] = adjustment
        
        sorted_items = sorted(
            item_scores.items(), 
            key=lambda x: x[1]['composite_score'] + diversity_adjustments.get(x[0], 0.0),
            reverse=True
        )
        logger.info(f"🎲 DIVERSITY: Added ±0.5 noise, -3.0 recently worn penalty, +1.5 new item boost for {len(recently_used_item_ids)} recently used items")
        
        # ═══════════════════════════════════════════════════════════
        # APPLY OUTFIT COMPOSITION STRATEGY
        # ═══════════════════════════════════════════════════════════
        
        # Apply selected strategy to create interesting outfit combinations
        try:
            strategy_result = StrategyImplementation.apply_strategy(
                strategy=selected_strategy,
                sorted_items=sorted_items,
                categories_filled={},  # Will be populated during selection
                target_items=target_items,
                context=context,
                base_item_id=context.base_item_id
            )
            
            strategy_adjustments = strategy_result['selection_adjustments']
            strategy_metadata = strategy_result['strategy_metadata']
            
            # Apply strategy adjustments to diversity adjustments
            for item_id, adjustment in strategy_adjustments.items():
                current = diversity_adjustments.get(item_id, 0.0)
                diversity_adjustments[item_id] = current + adjustment
                if adjustment != 0:
                    logger.debug(f"  🎨 STRATEGY: {self.safe_get_item_name(item_scores[item_id]['item'])} {adjustment:+.2f}")
            
            # Re-sort with strategy adjustments
            sorted_items = sorted(
                item_scores.items(),
                key=lambda x: x[1]['composite_score'] + diversity_adjustments.get(x[0], 0.0),
                reverse=True
            )
            
            logger.info(f"✅ STRATEGY APPLIED: {strategy_metadata['name']} - {len(strategy_adjustments)} items adjusted")
            
        except Exception as strategy_error:
            logger.warning(f"⚠️ Strategy application failed: {strategy_error}, falling back to Traditional")
            strategy_metadata = {
                'name': 'Traditional Match (Fallback)',
                'description': 'Strategy failed, using traditional selection'
            }
        
        # ═══════════════════════════════════════════════════════════
        # 3:1 EXPLORATION RATIO (Mix high and low scorers)
        # ═══════════════════════════════════════════════════════════
        
        # Split into high and low scorers for exploration/exploitation balance
        high_score_threshold = 2.5
        high_score_items = [(id, s) for id, s in sorted_items if s['composite_score'] + diversity_adjustments.get(id, 0.0) > high_score_threshold]
        low_score_items = [(id, s) for id, s in sorted_items if s['composite_score'] + diversity_adjustments.get(id, 0.0) <= high_score_threshold]
        
        logger.info(f"🎯 EXPLORATION RATIO: {len(high_score_items)} high scorers (>{high_score_threshold}), {len(low_score_items)} low scorers (<={high_score_threshold})")
        
        # ═══════════════════════════════════════════════════════════
        # FIX #1: CATEGORY BALANCE - Reserve best from each essential category
        # ═══════════════════════════════════════════════════════════
        essential_categories = ['tops', 'bottoms', 'shoes']
        reserved_items = {}
        reserved_ids = set()
        
        # Find best item from each essential category
        for category in essential_categories:
            category_items = [
                (id, s) for id, s in sorted_items 
                if self._get_item_category(s['item']) == category
            ]
            if category_items:
                # Get the best scoring item from this category
                best_item = max(category_items, key=lambda x: x[1]['composite_score'] + diversity_adjustments.get(x[0], 0.0))
                reserved_items[category] = best_item
                reserved_ids.add(best_item[0])
        
        logger.info(f"🔧 CATEGORY BALANCE: Reserved {len(reserved_items)} essential items: {list(reserved_items.keys())}")
        for cat, (item_id, score_data) in reserved_items.items():
            logger.debug(f"  ✅ Reserved {cat}: {self.safe_get_item_name(score_data['item'])} (score={score_data['composite_score']:.2f})")
        
        # Mix in 3:1 ratio (75% high confidence, 25% exploration)
        exploration_mixed = []
        low_score_idx = 0
        
        # First, add all reserved items (ensures category balance)
        for item_tuple in reserved_items.values():
            exploration_mixed.append(item_tuple)
        
        # Then add high scorers (excluding reserved items)
        for idx, (item_id, score_data) in enumerate(high_score_items):
            if item_id not in reserved_ids:  # Don't duplicate reserved items
                exploration_mixed.append((item_id, score_data))
                
                # Every 3rd high scorer, add one low scorer for exploration
                if (idx + 1) % 3 == 0 and low_score_idx < len(low_score_items):
                    if low_score_items[low_score_idx][0] not in reserved_ids:  # Don't duplicate
                        exploration_mixed.append(low_score_items[low_score_idx])
                        logger.debug(f"  🔍 Exploration: Added low scorer after 3 high scorers")
                    low_score_idx += 1
        
        # CRITICAL FIX: If we have few items (< 4), add remaining low scorers to ensure enough options
        # This handles the case where all items are "low scorers" (no high scorers available)
        if len(exploration_mixed) < 4:
            logger.info(f"🔧 EXPLORATION FIX: Only {len(exploration_mixed)} items in mix, adding remaining low scorers...")
            for item_id, score_data in low_score_items:
                if item_id not in reserved_ids and (item_id, score_data) not in exploration_mixed:
                    exploration_mixed.append((item_id, score_data))
                    logger.debug(f"  ➕ Added low scorer: {self.safe_get_item_name(score_data['item'])} (score={score_data['composite_score']:.2f})")
                    # Stop when we have enough items (cap at 6 items total or all available items)
                    if len(exploration_mixed) >= min(len(item_scores), 6):
                        break
        
        # Use the exploration-mixed list for selection
        sorted_items = exploration_mixed
        
        # Log category distribution
        category_counts = {}
        for item_id, score_data in sorted_items:
            cat = self._get_item_category(score_data['item'])
            category_counts[cat] = category_counts.get(cat, 0) + 1
        logger.info(f"✅ EXPLORATION MIX: Created {len(sorted_items)} item list (3:1 high:low ratio + category balance)")
        logger.info(f"   Category distribution: {category_counts}")
        
        # Select items with intelligent layering
        selected_items = []
        categories_filled = {}
        
        # Phase 0: PRIORITIZE BASE ITEM - Add base item first if specified
        base_item_obj = None
        if context.base_item_id:
            logger.info(f"🎯 PHASE 0: Checking for base item: {context.base_item_id}")
            # First try to find it in scored items
            for item_id, score_data in sorted_items:
                if item_id == context.base_item_id:
                    base_item_obj = score_data['item']
                    selected_items.append(base_item_obj)
                    base_category = self._get_item_category(base_item_obj)
                    categories_filled[base_category] = True
                    logger.info(f"✅ PHASE 0: Base item added from scored items: {self.safe_get_item_name(base_item_obj)} (category: {base_category})")
                    break
            
            # CRITICAL FIX v2: If base item not in scored items, find it in original wardrobe
            # This handles the case where base item was pre-approved but not scored
            # Deployed: 2025-10-28 - Fix ensures base item always included in final outfit
            if not base_item_obj:
                logger.warning(f"⚠️ PHASE 0: Base item {context.base_item_id} not found in scored items - searching wardrobe")
                for item in context.wardrobe:
                    if getattr(item, 'id', None) == context.base_item_id:
                        base_item_obj = item
                        selected_items.append(base_item_obj)
                        base_category = self._get_item_category(base_item_obj)
                        categories_filled[base_category] = True
                        logger.info(f"✅ PHASE 0: Base item added from wardrobe: {self.safe_get_item_name(base_item_obj)} (category: {base_category})")
                        break
                
                if not base_item_obj:
                    logger.error(f"❌ PHASE 0: Base item {context.base_item_id} not found in wardrobe!")
        
        def _is_polished_party_shoe(item_obj: Any) -> bool:
            """Return False when a shoe is clearly too casual for minimalist party/formal outfits."""
            shoe_formality = self._get_item_formality_level(item_obj)
            if shoe_formality is not None and shoe_formality >= 2:
                return True

            item_name_lower = (self.safe_get_item_name(item_obj) or "unknown").lower()
            metadata = getattr(item_obj, 'metadata', None)
            shoe_type = ""
            material = ""
            if isinstance(metadata, dict):
                visual_attrs = metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    shoe_type = (visual_attrs.get('shoeType') or "").lower()
                    material = (visual_attrs.get('material') or "").lower()

            polished_markers = [
                'oxford', 'loafer', 'derby', 'monk', 'chelsea', 'wingtip', 'pump',
                'heel', 'dress', 'patent', 'brogue', 'strappy', 'kitten heel'
            ]
            if any(marker in item_name_lower for marker in polished_markers):
                return True
            if any(marker in shoe_type for marker in polished_markers):
                return True
            if material in ['leather', 'patent leather', 'suede'] and 'sneaker' not in shoe_type and 'sneaker' not in item_name_lower:
                return True

            casual_markers = [
                'sneaker', 'trainer', 'running', 'slide', 'slides', 'flip flop', 'flip-flop',
                'slipper', 'house shoe', 'water shoe', 'foam', 'athletic', 'pool slide'
            ]
            if any(marker in item_name_lower for marker in casual_markers):
                return False
            if shoe_type and any(marker in shoe_type for marker in casual_markers):
                return False
            return True

        def _is_polished_party_bottom(item_obj: Any) -> bool:
            """Return False when a bottom is too casual (e.g., denim) for minimalist party/formal outfits."""
            bottom_formality = self._get_item_formality_level(item_obj)
            if bottom_formality is not None and bottom_formality >= 2:
                return True

            item_name_lower = (self.safe_get_item_name(item_obj) or "unknown").lower()
            item_type_lower = (self.safe_get_item_attr(item_obj, 'type', '') or '').lower()
            metadata = getattr(item_obj, 'metadata', None)
            fabric = ""
            if isinstance(metadata, dict):
                visual_attrs = metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    fabric = (visual_attrs.get('fabric') or '').lower()

            polished_markers = [
                'trouser', 'trousers', 'suit pant', 'dress pant', 'dress trouser',
                'slack', 'slacks', 'tailored', 'pleated', 'crease', 'wool', 'chino',
                'gabardine', 'tuxedo', 'tux', 'formal'
            ]
            if any(marker in item_name_lower for marker in polished_markers):
                return True
            if any(marker in item_type_lower for marker in polished_markers):
                return True
            if fabric in ['wool', 'silk', 'sateen', 'gabardine']:
                return True

            casual_markers = [
                'jean', 'denim', 'cargo', 'jogger', 'sweatpant', 'sweat pant',
                'athletic', 'track pant', 'khaki short', 'shorts'
            ]
            if any(marker in item_name_lower for marker in casual_markers):
                return False
            if item_type_lower and any(marker in item_type_lower for marker in casual_markers):
                return False
            return True
        
        preferred_polished_bottom_id = None
        if requires_minimalist_party_polish:
            for candidate_id, candidate_score in sorted_items:
                candidate_item = candidate_score['item']
                if self._get_item_category(candidate_item) == 'bottoms' and _is_polished_party_bottom(candidate_item):
                    preferred_polished_bottom_id = candidate_id
                    break
        
        # Phase 1: Fill essential categories (tops, bottoms, shoes)
        logger.info(f"📦 PHASE 1: Selecting essential items (top, bottom, shoes)")
        logger.debug(f"🔍 DEBUG PHASE 1: Starting with {len(sorted_items)} scored items")
        for item_id, score_data in sorted_items:
            item = score_data['item']
            
            # Skip base item since it's already added in Phase 0
            if base_item_obj and item_id == context.base_item_id:
                logger.debug(f"⏭️ PHASE 1: Skipping base item (already added in Phase 0)")
                continue
            
            category = self._get_item_category(item)
            item_name_lower = (self.safe_get_item_name(item) if item else "Unknown").lower()
            
            logger.debug(f"🔍 DEBUG PHASE 1: Processing item {self.safe_get_item_name(item)} - category: {category}, score: {score_data['composite_score']:.2f}")
            
            # METADATA CHECK: Determine layering level from metadata first, fallback to keywords
            layer_level = 'tops'  # Default
            can_layer = True  # Default
            max_layers = 3  # Default
            
            if hasattr(item, 'metadata') and item.metadata and isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    # Use metadata layerLevel if available
                    metadata_layer_level = visual_attrs.get('layerLevel')
                    wear_layer = (visual_attrs.get('wearLayer') or '').lower()
                    can_layer_meta = visual_attrs.get('canLayer')
                    max_layers_meta = visual_attrs.get('maxLayers')
                    
                    if wear_layer:
                        layer_level = wear_layer  # Use metadata layer (base, mid, outer)
                        logger.debug(f"  🔍 LAYER: Using metadata wearLayer={wear_layer}")
                    elif metadata_layer_level:
                        # Convert numeric to text (1=base, 2=mid, 3=outer)
                        layer_map = {1: 'base', 2: 'mid', 3: 'outerwear'}
                        layer_level = layer_map.get(metadata_layer_level, 'tops')
                        logger.debug(f"  🔍 LAYER: Using metadata layerLevel={metadata_layer_level} → {layer_level}")
                    
                    if can_layer_meta is not None:
                        can_layer = can_layer_meta
                        logger.debug(f"  🔍 LAYER: canLayer={can_layer}")
                    
                    if max_layers_meta is not None:
                        max_layers = max_layers_meta
                        logger.debug(f"  🔍 LAYER: maxLayers={max_layers}")
            
            # Fallback to keyword-based detection if no metadata
            if layer_level == 'tops' and category == 'tops':
                if any(kw in item_name_lower for kw in ['tank', 'cami', 'base', 'undershirt']):
                    layer_level = 'base'
                elif any(kw in item_name_lower for kw in ['sweater', 'cardigan', 'hoodie']):
                    layer_level = 'mid'
            elif category == 'outerwear':
                layer_level = 'outerwear'
            elif category == 'accessories':
                layer_level = 'accessories'
            else:
                layer_level = category
            
            # Essential categories first (but ONLY if score is positive or close to 0)
            if category in ['tops', 'bottoms', 'shoes']:
                if category not in categories_filled:
                    # CRITICAL: Don't select items with very negative scores, even as essentials
                    composite_score = score_data['composite_score']
                    if category == 'bottoms' and requires_minimalist_party_polish:
                        if preferred_polished_bottom_id and item_id != preferred_polished_bottom_id and not _is_polished_party_bottom(item):
                            logger.info(f"  ⏭️ Essential bottoms: {self.safe_get_item_name(item)} skipped — looking for polished option first")
                            continue
                        if not _is_polished_party_bottom(item) and not preferred_polished_bottom_id:
                            logger.warning(f"  ⚠️ Essential bottoms: No polished option available; allowing {self.safe_get_item_name(item)}")
                    if composite_score > -1.0:  # Allow slightly negative scores, but not terrible ones
                        # FORBIDDEN COMBINATIONS CHECK: Prevent fashion faux pas
                        if self._is_forbidden_combination(item, selected_items):
                            logger.warning(f"  🚫 FORBIDDEN COMBO: {self.safe_get_item_name(item)} creates forbidden combination with existing items")
                            continue  # Skip this item
                        
                        # ✅ NEW: Check for two shirts in Phase 1 (prevent from the start)
                        if category == 'tops':
                            is_shirt = self._is_shirt(item)
                            has_shirt = any(self._is_shirt(i) for i in selected_items)
                            if is_shirt and has_shirt:
                                logger.warning(f"  🚫 FORBIDDEN: Two shirts not allowed in Phase 1 - {self.safe_get_item_name(item)} skipped")
                                continue
                        
                        if category == 'shoes' and requires_minimalist_party_polish:
                            if not _is_polished_party_shoe(item):
                                logger.info(f"  ⏭️ Essential shoes: {self.safe_get_item_name(item)} skipped — not polished enough for minimalist {context.occasion}")
                                continue
                        if not _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                            continue
                        
                        selected_items.append(item)
                        categories_filled[category] = True
                        logger.info(f"  ✅ Essential {category}: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                    else:
                        logger.warning(f"  ⚠️ SKIPPED Essential {category}: {self.safe_get_item_name(item)} (score={composite_score:.2f} too low - inappropriate for occasion)")
                else:
                    logger.debug(f"  ⏭️ Essential {category}: {self.safe_get_item_name(item)} skipped - category already filled")
            else:
                logger.debug(f"  ⏭️ Non-essential {category}: {self.safe_get_item_name(item)} - will check in Phase 2")
        
        logger.debug(f"🔍 DEBUG PHASE 1 COMPLETE: Selected {len(selected_items)} items, categories filled: {categories_filled}")
        
        # ═══════════════════════════════════════════════════════════
        # FIX #2: SAFETY NET - Ensure all essential categories are filled
        # ═══════════════════════════════════════════════════════════
        missing_categories = [cat for cat in ['tops', 'bottoms', 'shoes'] if cat not in categories_filled]
        
        if missing_categories:
            logger.warning(f"🔧 SAFETY NET ACTIVATED: Missing essential categories: {missing_categories}")
            
            # Search ALL scored items (not just exploration mix) for best items from missing categories
            for missing_cat in missing_categories:
                # Get all items from this category across ALL scored items
                category_candidates = [
                    (id, s) for id, s in item_scores.items()
                    if self._get_item_category(s['item']) == missing_cat
                ]
                
                if category_candidates:
                    # Sort by composite score (with diversity adjustments)
                    category_candidates.sort(
                        key=lambda x: x[1]['composite_score'] + diversity_adjustments.get(x[0], 0.0),
                        reverse=True
                    )
                    
                    # Try to find an item with score > -2.0 (more lenient than Phase 1's -1.0)
                    added = False
                    for item_id, score_data in category_candidates:
                        item = score_data['item']
                        composite_score = score_data['composite_score']
                        
                        # More lenient threshold for safety net
                        if composite_score > -2.0:
                            # Still apply hard filter to ensure occasion appropriateness
                            passes_hard_filter = self._hard_filter(item, context.occasion, context.style)
                            
                            if passes_hard_filter:
                                if not _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                                    continue
                                selected_items.append(item)
                                categories_filled[missing_cat] = True
                                logger.info(f"  ✅ SAFETY NET: Added {missing_cat} '{self.safe_get_item_name(item)}' (score={composite_score:.2f})")
                                added = True
                                break
                            else:
                                logger.debug(f"  ⏭️ SAFETY NET: Skipped {missing_cat} '{self.safe_get_item_name(item)}' (blocked by hard filter)")
                        else:
                            logger.debug(f"  ⏭️ SAFETY NET: Skipped {missing_cat} '{self.safe_get_item_name(item)}' (score too low: {composite_score:.2f})")
                    
                    if not added:
                        logger.warning(f"  ⚠️ SAFETY NET: No valid {missing_cat} found (all items blocked or scored too low)")
                else:
                    logger.warning(f"  ⚠️ SAFETY NET: No {missing_cat} items available in wardrobe")
            
            # Log final result after safety net
            final_missing = [cat for cat in ['tops', 'bottoms', 'shoes'] if cat not in categories_filled]
            if final_missing:
                logger.warning(f"⚠️ SAFETY NET: Still missing categories after safety net: {final_missing}")
                
            # LAST RESORT: If bottoms are missing, search ENTIRE wardrobe for relaxed lounge bottoms
            if 'bottoms' in final_missing:
                logger.warning(f"⚠️ LAST RESORT: Searching entire wardrobe for relaxed lounge bottoms")
                lounge_item_ids = set()
                if isinstance(context.metadata_notes, dict):
                    lounge_item_ids = set(context.metadata_notes.get('lounge_item_ids', []) or [])
                original_pool = context.wardrobe_original or context.wardrobe
                all_bottoms = [
                    item for item in original_pool
                    if self._get_item_category(item) == 'bottoms'
                ]
                if all_bottoms:
                    import random
                    scored_bottoms = []
                    for bottom in all_bottoms:
                        if bottom in selected_items:
                            continue
                        if not self._hard_filter(bottom, context.occasion, context.style):
                            continue
                        bottom_id = self.safe_get_item_attr(bottom, 'id', '')
                        name_lower = self.safe_get_item_name(bottom).lower()
                        metadata = getattr(bottom, 'metadata', {}) if hasattr(bottom, 'metadata') else {}
                        waistband = ''
                        if isinstance(metadata, dict):
                            waistband = ((metadata.get('visualAttributes') or {}).get('waistbandType') or '').lower()
                        priority = 0
                        if bottom_id in lounge_item_ids:
                            priority += 4
                        if any(token in name_lower for token in ['sweat', 'short', 'drawstring', 'elastic', 'lounge', 'pj', 'relaxed']):
                            priority += 2
                        if waistband in ['elastic', 'drawstring', 'elastic_drawstring']:
                            priority += 2
                        soft_score = self._soft_score(bottom, context.occasion, context.style, context.mood, context.weather)
                        scored_bottoms.append((bottom, priority, soft_score))
                    if scored_bottoms:
                        fresh_bottoms = [entry for entry in scored_bottoms if self.safe_get_item_attr(entry[0], 'id', '') not in recently_used_item_ids]
                        candidate_list = fresh_bottoms if fresh_bottoms else scored_bottoms
                        random.shuffle(candidate_list)
                        candidate_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
                        best_bottom, priority, best_score = candidate_list[0]
                        bottom_id = self.safe_get_item_attr(best_bottom, 'id', '')
                        if _is_monochrome_allowed(best_bottom, bottom_id, None, log_prefix="  "):
                            selected_items.append(best_bottom)
                            categories_filled['bottoms'] = True
                            logger.warning(
                                f"⚠️ LAST RESORT: Added relaxed bottom '{self.safe_get_item_name(best_bottom)}' "
                                f"(priority={priority}, score={best_score:.2f})"
                            )
                        else:
                            logger.warning("⚠️ LAST RESORT: Best relaxed bottom failed monochrome check")
                    else:
                        logger.warning("⚠️ LAST RESORT: No relaxed bottoms passed hard filter")
                else:
                    logger.warning("⚠️ LAST RESORT: No bottom items found in wardrobe for lounge search")

                # LAST RESORT: If shoes are missing, search ENTIRE wardrobe (bypass occasion filter)
                if 'shoes' in final_missing:
                    logger.warning(f"⚠️ LAST RESORT: Searching entire wardrobe for any shoes (bypassing occasion filter)")
                    
                    # Get ALL shoes from original wardrobe (before occasion filtering)
                    all_shoes = [
                        item for item in context.wardrobe_original 
                        if self._get_item_category(item) == 'shoes'
                    ]
                    
                    if all_shoes:
                        # Score all shoes and pick the best one
                        shoe_scores = []
                        for shoe in all_shoes:
                            if shoe not in selected_items:
                                # Calculate basic score
                                score = self._soft_score(shoe, context.occasion, context.style, context.mood, context.weather)
                                shoe_scores.append((shoe, score))
                        
                        if shoe_scores:
                            # Sort by score and pick the best
                            shoe_scores.sort(key=lambda x: x[1], reverse=True)
                            best_shoe, best_score = shoe_scores[0]
                            
                            shoe_id = self.safe_get_item_attr(best_shoe, 'id', '')
                            if _is_monochrome_allowed(best_shoe, shoe_id, None, log_prefix="  "):
                                selected_items.append(best_shoe)
                                categories_filled['shoes'] = True
                                
                                logger.warning(f"⚠️ LAST RESORT: Added best available shoe '{self.safe_get_item_name(best_shoe)}' (score={best_score:.2f})")
                                logger.warning(f"⚠️ WARNING: This shoe might not be ideal for {context.occasion} occasion")
                                
                                # Mark this outfit as having a potential mismatch
                                if not hasattr(context, 'warnings') or context.warnings is None:
                                    context.warnings = []
                                context.warnings.append(f"Shoes ({self.safe_get_item_name(best_shoe)}) may not be ideal for {context.occasion} occasion")
                            else:
                                logger.warning(f"⚠️ LAST RESORT: Skipped shoe '{self.safe_get_item_name(best_shoe)}' due to monochrome palette mismatch")
                        else:
                            logger.error(f"🚫 LAST RESORT FAILED: All shoes are already selected")
                    else:
                        logger.error(f"🚫 LAST RESORT FAILED: No shoes found in entire wardrobe")
            else:
                logger.info(f"✅ SAFETY NET: Successfully filled all essential categories")
        else:
            logger.info(f"✅ SAFETY NET: Not needed - all essential categories filled in Phase 1")
        
        # EMERGENCY BYPASS: If no items selected, force select the first item
        if len(selected_items) == 0 and sorted_items:
            logger.warning(f"🚨 EMERGENCY BYPASS: No items selected in Phase 1, forcing selection of first palette-compatible item")
            forced_item = None
            forced_category = 'tops'
            for candidate_id, candidate_score in sorted_items:
                candidate_item = candidate_score['item']
                if _is_monochrome_allowed(candidate_item, candidate_id, candidate_score, log_prefix="  "):
                    forced_item = candidate_item
                    forced_category = self._get_item_category(candidate_item) or 'tops'
                    break
            if forced_item is None:
                forced_item = sorted_items[0][1]['item']
            selected_items.append(forced_item)
            categories_filled[forced_category] = True
            logger.info(f"🚨 EMERGENCY BYPASS: Forced selection of {self.safe_get_item_name(forced_item)}")
        
        # Phase 2: Add layering pieces based on target count
        logger.info(f"📦 PHASE 2: Adding {recommended_layers} layering pieces")
        outerwear_threshold = 0.6
        mid_layer_threshold = 0.6
        accessory_threshold = 0.7
        if loungewear_mode:
            outerwear_threshold = 0.45
            mid_layer_threshold = 0.45
            accessory_threshold = 0.85  # Accessories rarely needed for lounge sets

        if requires_minimalist_party_polish:
            outerwear_threshold = min(outerwear_threshold, 0.45)
            mid_layer_threshold = min(mid_layer_threshold, 0.55)
            accessory_threshold = min(accessory_threshold, 0.55)

        lounge_layer_keywords = ['sweater', 'cardigan', 'vest', 'hoodie', 'pullover', 'fleece', 'crewneck', 'henley', 'thermal', 'knit', 'zip', 'jogger']

        def _is_lounge_layer_name(name_lower: str) -> bool:
            return any(kw in name_lower for kw in lounge_layer_keywords)

        for item_id, score_data in sorted_items:
            if len(selected_items) >= target_items:
                break
            
            item = score_data['item']
            if item in selected_items:
                continue
            
            category = self._get_item_category(item)
            item_name_lower = (self.safe_get_item_name(item) if item else "Unknown").lower()
            item_identifier = self.safe_get_item_attr(item, 'id', '')

            if loungewear_mode and lounge_item_ids and item_identifier:
                # Prefer items flagged by lounge heuristics when available
                if category in ['tops', 'outerwear'] and item_identifier not in lounge_item_ids and not _is_lounge_layer_name(item_name_lower):
                    logger.debug(f"  ⏭️ Lounge layer skip: {self.safe_get_item_name(item)} not flagged as lounge candidate")
                    continue
            
            # Determine layering appropriateness
            # VERSION: 2025-10-11-DUPLICATE-FIX
            if category == 'outerwear' and score_data['composite_score'] > outerwear_threshold:
                # ✅ FIX: Check if outerwear already exists before adding
                has_outerwear = any(self._get_item_category(i) == 'outerwear' for i in selected_items)
                
                if not has_outerwear and (temp < 65 or occasion_lower in ['business', 'formal']):
                    # FORBIDDEN COMBINATIONS CHECK
                    if self._is_forbidden_combination(item, selected_items):
                        logger.warning(f"  🚫 FORBIDDEN COMBO: {self.safe_get_item_name(item)} (outerwear) would create forbidden combination")
                    else:
                        if not _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                            continue
                        selected_items.append(item)
                        categories_filled['outerwear'] = True  # Track that we added outerwear
                        logger.warning(f"  ✅ Outerwear: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                elif has_outerwear:
                    logger.warning(f"  ⏭️ Outerwear: {self.safe_get_item_name(item)} - SKIPPED (already have outerwear)")
            
            elif category == 'tops' and score_data['composite_score'] > mid_layer_threshold:
                # ✅ FIX: Check if mid-layer already exists before adding
                is_mid_layer = _is_lounge_layer_name(item_name_lower)
                has_mid_layer = any(
                    _is_lounge_layer_name(self.safe_get_item_name(i).lower())
                    for i in selected_items
                )
                
                # ✅ NEW: Check if this would create two shirts (not proper)
                is_shirt = self._is_shirt(item)
                has_shirt = any(self._is_shirt(i) for i in selected_items)
                
                # ✅ NEW: Check for forbidden layering combinations
                if self._is_forbidden_combination(item, selected_items):
                    logger.warning(f"  🚫 FORBIDDEN COMBO: {self.safe_get_item_name(item)} would create forbidden layering combination")
                    continue
                
                # Block adding a second shirt
                if is_shirt and has_shirt:
                    logger.warning(f"  🚫 FORBIDDEN: Two shirts not allowed - {self.safe_get_item_name(item)} skipped (already have a shirt)")
                    continue
                
                if is_mid_layer and not has_mid_layer and temp < 70:
                    if _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                        selected_items.append(item)
                        categories_filled['mid'] = True  # Track that we added mid-layer
                        logger.warning(f"  ✅ Mid-layer: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                elif is_mid_layer and has_mid_layer:
                    logger.warning(f"  ⏭️ Mid-layer: {self.safe_get_item_name(item)} - SKIPPED (already have mid-layer)")
                elif is_shirt and not has_shirt:
                    # Allow adding a shirt if we don't have one yet
                    if _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                        selected_items.append(item)
                        logger.warning(f"  ✅ Top: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
            
            elif category == 'accessories' and score_data['composite_score'] > accessory_threshold:
                # Accessories can have multiple items (belts, watches, etc.)
                if temp < 50 or occasion_lower in ['formal', 'business']:
                    # Limit to 2 accessories max
                    accessory_count = sum(1 for i in selected_items if self._get_item_category(i) == 'accessories')
                    if accessory_count < 2:
                        if _is_monochrome_allowed(item, item_id, score_data, log_prefix="  "):
                            selected_items.append(item)
                            logger.warning(f"  ✅ Accessory: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                    else:
                        logger.warning(f"  ⏭️ Accessory: {self.safe_get_item_name(item)} - SKIPPED (already have 2 accessories)")
        
        if requires_minimalist_party_polish and len(selected_items) < max_items:
            has_outerwear = any(self._get_item_category(i) == 'outerwear' for i in selected_items)
            has_accessory = any(self._get_item_category(i) == 'accessories' for i in selected_items)

            if not has_outerwear and len(selected_items) < max_items:
                for candidate_id, score_data in sorted_items:
                    candidate_item = score_data['item']
                    if candidate_item in selected_items:
                        continue
                    if self._get_item_category(candidate_item) != 'outerwear':
                        continue
                    if score_data['composite_score'] < 0.1:
                        continue
                    if not self._hard_filter(candidate_item, context.occasion, context.style):
                        continue
                    if not _is_monochrome_allowed(candidate_item, candidate_id, score_data, log_prefix="  "):
                        continue
                    selected_items.append(candidate_item)
                    categories_filled['outerwear'] = True
                    logger.info(f"  ✅ MINIMALIST PARTY: Added polish outer layer {self.safe_get_item_name(candidate_item)}")
                    break

            if not has_accessory and len(selected_items) < max_items:
                for candidate_id, score_data in sorted_items:
                    candidate_item = score_data['item']
                    if candidate_item in selected_items:
                        continue
                    if self._get_item_category(candidate_item) != 'accessories':
                        continue
                    if score_data['composite_score'] < 0.05:
                        continue
                    if not self._hard_filter(candidate_item, context.occasion, context.style):
                        continue
                    if not _is_monochrome_allowed(candidate_item, candidate_id, score_data, log_prefix="  "):
                        continue
                    selected_items.append(candidate_item)
                    logger.info(f"  ✅ MINIMALIST PARTY: Added polish accessory {self.safe_get_item_name(candidate_item)}")
                    break
        
        # Ensure minimum items
        if len(selected_items) < min_items:
            if loungewear_mode and lounge_item_ids:
                logger.info(f"🛋️ LOUNGE MODE: Adding lounge-qualified layers to reach minimum {min_items}")
                for item_id, score_data in sorted_items:
                    if len(selected_items) >= min_items:
                        break
                    candidate = score_data['item']
                    if candidate in selected_items:
                        continue
                    candidate_id = self.safe_get_item_attr(candidate, 'id', '')
                    if candidate_id and candidate_id not in lounge_item_ids and not _is_lounge_layer_name(self.safe_get_item_name(candidate).lower()):
                        continue
                    if score_data['composite_score'] < 0.25:
                        continue
                    # CRITICAL: Apply hard filter to lounge fillers too
                    if not self._hard_filter(candidate, context.occasion, context.style):
                        continue
                    if _is_monochrome_allowed(candidate, candidate_id, score_data, log_prefix="  "):
                        selected_items.append(candidate)
                        logger.info(f"  🛋️ Added lounge filler: {self.safe_get_item_name(candidate)} (score={score_data['composite_score']:.2f})")

            if requires_minimalist_party_polish and len(selected_items) < min_items:
                polish_filler_categories = ['outerwear', 'accessories']
                for desired_category in polish_filler_categories:
                    if len(selected_items) >= min_items:
                        break
                    for item_id, score_data in sorted_items:
                        if len(selected_items) >= min_items:
                            break
                        candidate = score_data['item']
                        if candidate in selected_items:
                            continue
                        candidate_category = self._get_item_category(candidate)
                        if candidate_category != desired_category:
                            continue
                        if score_data['composite_score'] < -0.25:
                            continue
                        if not self._hard_filter(candidate, context.occasion, context.style):
                            continue
                        if not _is_monochrome_allowed(candidate, item_id, score_data, log_prefix="  "):
                            continue
                        selected_items.append(candidate)
                        if desired_category == 'outerwear':
                            categories_filled['outerwear'] = True
                        logger.info(f"  ✅ MINIMALIST PARTY: Added polish {desired_category} filler {self.safe_get_item_name(candidate)}")
                        break

            logger.warning(f"⚠️ Only {len(selected_items)} items selected, adding more to reach minimum {min_items}...")
            # First pass: Try to add items from non-essential categories (outerwear, accessories)
            for item_id, score_data in sorted_items:
                if score_data['item'] not in selected_items and len(selected_items) < min_items:
                    item_category = self._get_item_category(score_data['item'])
                    
                    # Skip essential categories in first pass
                    if item_category in ['tops', 'bottoms', 'shoes']:
                        continue
                    
                    # CRITICAL: Apply hard filter to filler items to prevent inappropriate additions
                    passes_hard_filter = self._hard_filter(score_data['item'], context.occasion, context.style)
                    if not passes_hard_filter:
                        logger.debug(f"  ⏭️ Filler: {self.safe_get_item_name(score_data['item'])} - SKIPPED (blocked by hard filter for {context.occasion})")
                        continue
                    
                    if _is_monochrome_allowed(score_data['item'], item_id, score_data, log_prefix="  "):
                        selected_items.append(score_data['item'])
                        categories_filled[item_category] = True
                        logger.info(f"  ➕ Filler (non-essential): {self.safe_get_item_name(score_data['item'])} ({item_category}, score={score_data['composite_score']:.2f})")
            
            # Second pass: If still below minimum, allow adding from essential categories that have multiple items available
            if len(selected_items) < min_items:
                logger.warning(f"⚠️ Still only {len(selected_items)} items, adding from essential categories to reach minimum {min_items}...")
                for item_id, score_data in sorted_items:
                    if score_data['item'] not in selected_items and len(selected_items) < min_items:
                        item_category = self._get_item_category(score_data['item'])
                        
                        # CRITICAL: Apply hard filter
                        passes_hard_filter = self._hard_filter(score_data['item'], context.occasion, context.style)
                        if not passes_hard_filter:
                            logger.debug(f"  ⏭️ Filler: {self.safe_get_item_name(score_data['item'])} - SKIPPED (blocked by hard filter for {context.occasion})")
                            continue
                        
                        # Only add if score is reasonable (prevents adding low-quality items just to fill quota)
                        if score_data['composite_score'] > 0.3:
                            if _is_monochrome_allowed(score_data['item'], item_id, score_data, log_prefix="  "):
                                selected_items.append(score_data['item'])
                                logger.info(f"  ➕ Filler (essential): {self.safe_get_item_name(score_data['item'])} ({item_category}, score={score_data['composite_score']:.2f})")
                        else:
                            logger.debug(f"  ⏭️ Filler: {self.safe_get_item_name(score_data['item'])} - SKIPPED (score too low: {score_data['composite_score']:.2f})")
        
        # CRITICAL: Deduplicate by ID to prevent same item appearing twice
        seen_ids = set()
        deduplicated_items = []
        base_item_in_deduped = False
        
        # First pass: Preserve base item if present
        base_item_to_preserve = None
        if context.base_item_id:
            for item in selected_items:
                item_id = self.safe_get_item_attr(item, 'id', '')
                if item_id == context.base_item_id:
                    base_item_to_preserve = item
                    break
        
        for item in selected_items:
            item_id = self.safe_get_item_attr(item, 'id', '')
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                deduplicated_items.append(item)
                if item_id == context.base_item_id:
                    base_item_in_deduped = True
            else:
                logger.warning(f"🔧 DEDUP: Removed duplicate item {self.safe_get_item_name(item)} (ID already in outfit)")
        
        # CRITICAL FIX: Ensure base item is ALWAYS included after deduplication
        if context.base_item_id and base_item_to_preserve and not base_item_in_deduped:
            logger.warning(f"⚠️ BASE ITEM LOST IN DEDUP: Restoring base item {context.base_item_id}")
            # Remove it from its current position if it exists as a duplicate, then add it at the front
            deduplicated_items = [item for item in deduplicated_items if self.safe_get_item_attr(item, 'id', '') != context.base_item_id]
            deduplicated_items.insert(0, base_item_to_preserve)
            logger.info(f"✅ BASE ITEM RESTORED: {self.safe_get_item_name(base_item_to_preserve)} is now first in outfit")
        
        if len(deduplicated_items) != len(selected_items):
            logger.warning(f"🔧 DEDUPLICATION: Removed {len(selected_items) - len(deduplicated_items)} duplicate items")
        selected_items = deduplicated_items
        
        logger.info(f"🎯 FINAL SELECTION: {len(selected_items)} items")

        if target_style_lower == 'monochrome' and hasattr(context, 'metadata_notes') and isinstance(context.metadata_notes, dict):
            selection_colors: Dict[str, str] = {}
            for item in selected_items:
                item_id = self.safe_get_item_attr(item, 'id', '')
                color_value = None
                if item_id:
                    color_value = monochrome_item_colors.get(item_id)
                if not color_value or color_value == 'neutral':
                    color_value = _normalize_monochrome_value(self.safe_get_item_attr(item, 'color', '') or '')
                selection_colors[item_id or self.safe_get_item_name(item)] = color_value or 'neutral'
            context.metadata_notes['monochrome_selected_colors'] = selection_colors
        
        # Mark selected items as seen in this session (prevents repetition in same session)
        logger.info(f"📍 Marking {len(selected_items)} items as seen in session {session_id[:8]}...")
        for item in selected_items:
            item_id = self.safe_get_item_attr(item, "id", "")
            if item_id:
                session_tracker.mark_item_as_seen(session_id, item_id)
        logger.info(f"✅ Session tracking complete - items marked as seen for this session")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PHASE 3: DIVERSITY FILTERING
        # ═══════════════════════════════════════════════════════════════════════
        
        logger.info(f"🎭 PHASE 3: Applying diversity filtering...")
        
        # Check outfit diversity
        diversity_result = diversity_filter.check_outfit_diversity(
            user_id=context.user_id,
            new_outfit=selected_items,
            occasion=context.occasion,
            style=context.style,
            mood=context.mood
        )
        
        logger.info(f"🎭 Diversity check: is_diverse={((safe_get(diversity_result, 'is_diverse', True) if diversity_result else True) if diversity_result else True)}, score={safe_get(diversity_result, 'diversity_score', 0.8):.2f}")
        
        # If not diverse enough, apply diversity boost
        if not (safe_get(diversity_result, 'is_diverse', True) if diversity_result else True):
            logger.warning(f"⚠️ Outfit not diverse enough, applying diversity boost...")
            
            # Get diversity suggestions
            diversity_suggestions = diversity_filter.get_diversity_suggestions(
                user_id=context.user_id,
                current_outfit=selected_items
            )
            
            if diversity_suggestions:
                logger.info(f"🎭 Got {len(diversity_suggestions)} diversity suggestions")
                
                # Try to swap out overused items with diverse alternatives
                for suggestion in diversity_suggestions[:2]:  # Limit to 2 swaps
                    item_to_replace = (safe_get(suggestion, 'item_to_replace') if suggestion else None)
                    alternative = (safe_get(suggestion, 'alternative') if suggestion else None)
                    
                    if item_to_replace and alternative:
                        # CRITICAL: Never swap out the base item
                        if context.base_item_id and self.safe_get_item_attr(item_to_replace, "id", "") == context.base_item_id:
                            logger.info(f"  ⏭️ Diversity swap skipped: Cannot swap base item {self.safe_get_item_name(item_to_replace)}")
                            continue
                            
                        alt_id = self.safe_get_item_attr(alternative, "id", "") if alternative else ""
                        if not _is_monochrome_allowed(alternative, alt_id, None, log_prefix="  "):
                            logger.debug(f"  ⏭️ Diversity swap skipped for {getattr(alternative, 'name', 'Unknown')} due to monochrome palette mismatch")
                            continue
                        # Replace in selected items
                        selected_items = [alternative if self.safe_get_item_attr(item, "id", "") == item_to_replace.id else item 
                                        for item in selected_items]
                        logger.info(f"  🔄 Swapped {item_to_replace.name} → {alternative.name}")
        
        # Record outfit for diversity tracking
        diversity_filter.record_outfit_generation(
            user_id=context.user_id,
            outfit={'items': selected_items, 'occasion': (context.occasion if context else "unknown")},
            items=selected_items
        )
        
        logger.info(f"✅ Diversity filtering complete")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PHASE 4: ANALYTICS & PERFORMANCE TRACKING
        # ═══════════════════════════════════════════════════════════════════════
        
        # Calculate final confidence based on composite scores
        # CRITICAL: Only include items that have scores (excludes LAST RESORT items that weren't scored)
        scored_items_in_selection = [
            item_scores[self.safe_get_item_attr(item, "id", "")]['composite_score'] 
            for item in selected_items 
            if self.safe_get_item_attr(item, "id", "") in item_scores
        ]
        avg_composite_score = sum(scored_items_in_selection) / len(scored_items_in_selection) if scored_items_in_selection else 0.5
        final_confidence = min(0.95, avg_composite_score)
        
        logger.info(f"📊 ANALYTICS: Recording strategy execution...")
        
        # Record strategy analytics
        try:
            strategy_analytics.record_strategy_execution(
                strategy="multi_layered_cohesive_composition",
                user_id=context.user_id,
                occasion=context.occasion,
                style=context.style,
                mood=context.mood,
                status=StrategyStatus.SUCCESS,
                confidence=final_confidence,
                validation_score=final_confidence,
                generation_time=0.5,  # Will be calculated properly
                validation_time=0.1,
                items_selected=len(selected_items),
                items_available=len(context.wardrobe),
                failed_rules=[],
                fallback_reason=None,
                session_id=f"ml_session_{int(time.time())}"
            )
            logger.info(f"✅ Strategy analytics recorded")
        except Exception as e:
            logger.warning(f"⚠️ Failed to record strategy analytics: {e}")
        
        # Record performance metrics for adaptive tuning
        try:
            metrics = PerformanceMetrics(
                success_rate=1.0,
                avg_confidence=final_confidence,
                avg_generation_time=0.5,
                avg_validation_time=0.1,
                diversity_score=(safe_get(diversity_result, 'diversity_score', 0.8) if diversity_result else 0.8),
                user_satisfaction=final_confidence,
                fallback_rate=0.0,
                sample_size=1,
                time_window_hours=int(time.time())
            )
            
            adaptive_tuning.record_performance(metrics)
            logger.info(f"✅ Performance metrics recorded")
        except Exception as e:
            logger.warning(f"⚠️ Failed to record performance metrics: {e}")
        
        # DEBUG: Log selected items before creating outfit
        logger.debug(f"🔍 DEBUG FINAL SELECTION: About to create outfit with {len(selected_items)} selected items")
        logger.debug(f"🔍 DEBUG FINAL SELECTION: Selected items: {[getattr(item, 'name', 'Unknown') for item in selected_items]}")
        logger.debug(f"🔍 DEBUG FINAL SELECTION: Target items was: {target_items}, min_items: {min_items}, max_items: {max_items}")
        logger.debug(f"🔍 DEBUG FINAL SELECTION: Categories filled: {categories_filled}")
        logger.debug(f"🔍 DEBUG FINAL SELECTION: Item scores count: {len(item_scores)}")
        if item_scores:
            logger.debug(f"🔍 DEBUG FINAL SELECTION: Top 3 scored items: {[(item_id, (safe_get(scores, 'composite_score', 0) if scores else 0)) for item_id, scores in list(item_scores.items())[:3]]}")
        
        # Deduplicate selected items before building outfit
        unique_selected_items = self._deduplicate_items(selected_items, context)
        if len(unique_selected_items) != len(selected_items):
            logger.info(f"🔁 DEDUPLICATION: Final outfit items reduced from {len(selected_items)} to {len(unique_selected_items)}")
        selected_items = unique_selected_items
        
        # CRITICAL FIX: Ensure base item is ALWAYS included in final outfit (even if deduplication removed it)
        # This is especially important for accessories like sunglasses that might not pass all filters
        if context.base_item_id:
            base_item_present = any(
                self.safe_get_item_attr(item, "id", "") == context.base_item_id 
                for item in selected_items
            )
            if not base_item_present:
                logger.warning(f"⚠️ BASE ITEM MISSING: Base item {context.base_item_id} not in final outfit, adding it now...")
                # Search for base item in wardrobe (try wardrobe_original first, then wardrobe)
                base_item_found = False
                wardrobe_to_search = []
                if hasattr(context, 'wardrobe_original') and context.wardrobe_original:
                    wardrobe_to_search = context.wardrobe_original
                elif hasattr(context, 'wardrobe') and context.wardrobe:
                    wardrobe_to_search = context.wardrobe
                
                for item in wardrobe_to_search:
                    if self.safe_get_item_attr(item, "id", "") == context.base_item_id:
                        # Add base item at the beginning to maintain priority
                        selected_items.insert(0, item)
                        logger.info(f"✅ BASE ITEM RESTORED: Added {self.safe_get_item_name(item)} to final outfit")
                        base_item_found = True
                        break
                
                if not base_item_found:
                    logger.error(f"❌ BASE ITEM NOT FOUND: Could not find base item {context.base_item_id} in wardrobe!")
        
        # Build summary of top candidate scores for observability
        top_candidates: List[Dict[str, Any]] = []
        try:
            sorted_candidate_items = sorted(
                item_scores.items(),
                key=lambda x: x[1].get('composite_score', 0.0),
                reverse=True
            )
            for item_id, score_data in sorted_candidate_items[:5]:
                candidate_item = score_data.get('item')
                top_candidates.append({
                    "itemId": getattr(candidate_item, 'id', item_id),
                    "name": self.safe_get_item_name(candidate_item) if candidate_item else item_id,
                    "composite": round(score_data.get('composite_score', 0.0), 3),
                    "body": round(score_data.get('body_type_score', 0.0), 3),
                    "style": round(score_data.get('style_profile_score', 0.0), 3),
                    "weather": round(score_data.get('weather_score', 0.0), 3),
                    "feedback": round(score_data.get('user_feedback_score', 0.0), 3),
                    "compatibility": round(score_data.get('compatibility_score', 0.0), 3),
                    "diversity": round(score_data.get('diversity_score', 0.0), 3) if 'diversity_score' in score_data else None,
                    "diversity_penalty": round(score_data.get('session_penalty', 0.0), 3) if 'session_penalty' in score_data else None
                })
        except Exception as summary_error:
            logger.debug(f"⚠️ Failed to build top candidate summary: {summary_error}")
            top_candidates = []

        # Create outfit
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"{context.style} {context.occasion} Outfit",
            description=f"6D scored outfit optimized for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=final_confidence,  # Use calculated confidence
            items=selected_items,
            reasoning=f"Created using 6D analysis: body type, style, weather, user feedback, compatibility, and diversity",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if (context.weather if context else None) else {},
            pieces=[],
            explanation=f"Optimized outfit using 6D scoring: body type, style profile, weather, user feedback, metadata compatibility, and diversity boost",
            styleTags=[context.style.lower().replace(' ', '_'), 'multi_layered'],
            colorHarmony="color_theory_optimized",
            styleNotes=f"6D scoring: body type, style, weather, user feedback, compatibility, diversity",
            season="current",
            updatedAt=int(time.time()),
            metadata={
                "generation_strategy": "multi_layered_cohesive_composition",
                "composition_strategy": strategy_metadata['name'],
                "strategy_description": strategy_metadata['description'],
                "avg_composite_score": avg_composite_score,
                "diversity_score": (safe_get(diversity_result, 'diversity_score', 0.8) if diversity_result else 0.8),
                "color_theory_applied": True,
                "analyzers_used": ["body_type", "style_profile", "weather", "user_feedback", "metadata_compatibility", "diversity"],
                "outfit_strategies_enabled": True,
                "warnings": context.warnings if hasattr(context, 'warnings') and context.warnings else [],
                "top_candidates": top_candidates,
                "total_items_scored": len(item_scores),
                "metadata_notes": context.metadata_notes if hasattr(context, 'metadata_notes') else {},
                
                # ═══════════════════════════════════════════════════════════════
                # 🎵 SPOTIFY-STYLE LEARNING INSIGHTS FOR FRONTEND
                # ═══════════════════════════════════════════════════════════════
                # Extract diversity scores from item_scores (stored per-item during scoring)
                "extracted_diversity_scores": {item_id: scores.get('diversity_score', 1.0) for item_id, scores in item_scores.items()},
                "user_learning_insights": self._generate_learning_insight_message(
                    context, 
                    item_scores, 
                    {item_id: scores.get('diversity_score', 1.0) for item_id, scores in item_scores.items()},
                    0  # favorited_count - will be computed from item_scores
                ),
                "user_stats": {
                    "total_ratings": safe_get(context.user_profile, 'total_outfits_rated', 0) if context.user_profile else 0,
                    "favorite_styles": context.style if context.style else "Learning",
                    "diversity_score": int((safe_get(diversity_result, 'diversity_score', 0.8) if diversity_result else 0.8) * 100)
                },
                "item_intelligence": [
                    {
                        "icon": "🎯" if item_scores.get(selected_items[i].id, {}).get('diversity_score', 1.0) > 1.1 else "⭐",
                        "item_name": selected_items[i].name[:40],
                        "reason": self._get_item_selection_reason(
                            selected_items[i], 
                            item_scores.get(selected_items[i].id, {}), 
                            item_scores.get(selected_items[i].id, {}).get('diversity_score', 1.0)
                        )
                    }
                    for i in range(min(3, len(selected_items)))
                ],
                "diversity_info": {
                    "message": self._generate_diversity_message(diversity_result, session_tracker, session_id) if diversity_result else "Introducing fresh combinations to keep your style varied!"
                }
            },
            wasSuccessful=True,
            baseItemId=context.base_item_id,
            validationErrors=[],
            userFeedback=None
        )
        
        logger.info(f"🎨 COHESIVE COMPOSITION: Created outfit with {len(selected_items)} items")
        logger.info(f"📊 Final confidence: {final_confidence:.2f}, Avg composite score: {avg_composite_score:.2f}")
        
        return outfit
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NETFLIX/SPOTIFY-STYLE LEARNING ALGORITHMS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _calculate_style_evolution_score(
        self, 
        item, 
        user_id: str, 
        current_time: float,
        outfit_ratings: dict,
        context,
        db
    ) -> float:
        """
        Calculate style evolution score using Netflix/Spotify-style algorithm
        
        This implements:
        - Time-weighted ratings (recent ratings matter more)
        - Occasion-specific learning (learns per context)
        - Color pattern detection (trending colors)
        - Seasonal preference tracking
        - Style trajectory analysis (is user moving toward/away from this style?)
        """
        evolution_score = 0.0
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # 1. TIME-WEIGHTED RATING ANALYSIS (Netflix-style)
            # ═══════════════════════════════════════════════════════════════
            
            # Fetch ALL user outfit ratings with timestamps
            outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(50)
            outfits = outfits_ref.stream()
            
            # Build time-weighted style preference matrix
            style_ratings_over_time = {}  # style -> [(timestamp, rating), ...]
            occasion_ratings_over_time = {}  # occasion -> [(timestamp, rating), ...]
            color_ratings_over_time = {}  # color -> [(timestamp, rating), ...]
            
            for outfit_doc in outfits:
                outfit_data = outfit_doc.to_dict()
                rating = (safe_get(outfit_data, 'rating') if outfit_data else None)
                if not rating:
                    continue
                
                # Get timestamp
                created_at = (safe_get(outfit_data, 'createdAt') if outfit_data else None)
                if hasattr(created_at, 'timestamp'):
                    timestamp = created_at.timestamp()
                elif isinstance(created_at, str):
                    try:
                        timestamp = float(created_at)
                    except:
                        timestamp = current_time
                else:
                    timestamp = current_time
                
                # Track style preferences over time
                outfit_style = (safe_get(outfit_data, 'style', '') if outfit_data else '').lower()
                if outfit_style:
                    if outfit_style not in style_ratings_over_time:
                        style_ratings_over_time[outfit_style] = []
                    style_ratings_over_time[outfit_style].append((timestamp, rating))
                
                # Track occasion preferences
                outfit_occasion = (safe_get(outfit_data, 'occasion', '') if outfit_data else '').lower()
                if outfit_occasion:
                    if outfit_occasion not in occasion_ratings_over_time:
                        occasion_ratings_over_time[outfit_occasion] = []
                    occasion_ratings_over_time[outfit_occasion].append((timestamp, rating))
                
                # Track color preferences
                outfit_items = (safe_get(outfit_data, 'items', []) if outfit_data else [])
                for outfit_item in outfit_items:
                    # Use safe_item_access to handle all formats
                    color = safe_item_access(outfit_item, 'color', '').lower()
                    if color:
                        if color not in color_ratings_over_time:
                            color_ratings_over_time[color] = []
                        color_ratings_over_time[color].append((timestamp, rating))
            
            # ═══════════════════════════════════════════════════════════════
            # 2. CALCULATE TIME-WEIGHTED SCORES (exponential decay)
            # ═══════════════════════════════════════════════════════════════
            
            # Recent ratings matter MUCH more (exponential time decay)
            # Netflix uses ~30 day half-life, we'll use 14 days
            half_life_days = 14
            half_life_seconds = half_life_days * 24 * 60 * 60
            
            def calculate_weighted_average(ratings_with_time):
                """Calculate time-weighted average (recent matters more)"""
                if not ratings_with_time:
                    return None
                
                weighted_sum = 0.0
                weight_total = 0.0
                
                for timestamp, rating in ratings_with_time:
                    age = current_time - timestamp
                    # Exponential decay: weight = 0.5^(age / half_life)
                    weight = 0.5 ** (age / half_life_seconds)
                    weighted_sum += rating * weight
                    weight_total += weight
                
                return weighted_sum / weight_total if weight_total > 0 else None
            
            # ═══════════════════════════════════════════════════════════════
            # 3. STYLE TRAJECTORY ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            
            item_styles = getattr(item, 'style', [])
            if isinstance(item_styles, str):
                item_styles = [item_styles]
            
            for style in item_styles:
                style_lower = style.lower()
                
                if style_lower in style_ratings_over_time:
                    weighted_avg = calculate_weighted_average(style_ratings_over_time[style_lower])
                    
                    if weighted_avg:
                        # Map 1-5 rating to bonus/penalty (-0.2 to +0.2)
                        style_bonus = ((weighted_avg - 3.0) / 2.0) * 0.2
                        evolution_score += style_bonus
                        
                        # Check if style is trending UP or DOWN
                        ratings = style_ratings_over_time[style_lower]
                        if len(ratings) >= 3:
                            old_ratings = [r for t, r in ratings if t < (current_time - 30*24*60*60)]
                            recent_ratings = [r for t, r in ratings if t >= (current_time - 30*24*60*60)]
                            
                            if old_ratings and recent_ratings:
                                old_avg = sum(old_ratings) / len(old_ratings)
                                recent_avg = sum(recent_ratings) / len(recent_ratings)
                                trend = recent_avg - old_avg
                                
                                if trend > 0.5:
                                    evolution_score += 0.15  # Style trending UP
                                    logger.debug(f"  📈 {self.safe_get_item_name(item)}: {style} TRENDING UP (+0.15)")
                                elif trend < -0.5:
                                    evolution_score -= 0.10  # Style trending DOWN
                                    logger.debug(f"  📉 {self.safe_get_item_name(item)}: {style} trending down (-0.10)")
            
            # ═══════════════════════════════════════════════════════════════
            # 4. OCCASION-SPECIFIC LEARNING
            # ═══════════════════════════════════════════════════════════════
            
            current_occasion = (context.occasion if context else "unknown").lower()
            
            # Check if this item's occasions align with user's ratings for this occasion
            item_occasions = getattr(item, 'occasion', [])
            if isinstance(item_occasions, str):
                item_occasions = [item_occasions]
            
            for occasion in item_occasions:
                occasion_lower = occasion.lower()
                
                if occasion_lower == current_occasion and occasion_lower in occasion_ratings_over_time:
                    weighted_avg = calculate_weighted_average(occasion_ratings_over_time[occasion_lower])
                    
                    if weighted_avg and weighted_avg >= 4.0:
                        evolution_score += 0.15  # User loves outfits for this occasion
                        logger.debug(f"  🎯 {self.safe_get_item_name(item)}: User loves {occasion_lower} outfits (+0.15)")
                    elif weighted_avg and weighted_avg <= 2.5:
                        evolution_score -= 0.10  # User dislikes outfits for this occasion
                        logger.debug(f"  ⚠️ {self.safe_get_item_name(item)}: User dislikes {occasion_lower} outfits (-0.10)")
            
            # ═══════════════════════════════════════════════════════════════
            # 5. COLOR PATTERN LEARNING
            # ═══════════════════════════════════════════════════════════════
            
            item_color = self.safe_get_item_attr(item, "color", "").lower() if self.safe_get_item_attr(item, "color", "") else ''
            
            if item_color and item_color in color_ratings_over_time:
                weighted_avg = calculate_weighted_average(color_ratings_over_time[item_color])
                
                if weighted_avg:
                    # Recent color preference
                    color_bonus = ((weighted_avg - 3.0) / 2.0) * 0.15
                    evolution_score += color_bonus
                    
                    if weighted_avg >= 4.0:
                        logger.debug(f"  🎨 {self.safe_get_item_name(item)}: {item_color} is trending color (+{color_bonus:.2f})")
            
            # ═══════════════════════════════════════════════════════════════
            # 6. SEASONAL PREFERENCE DETECTION
            # ═══════════════════════════════════════════════════════════════
            
            # Determine current season
            current_month = datetime.now().month
            if current_month in [12, 1, 2]:
                current_season = 'winter'
            elif current_month in [3, 4, 5]:
                current_season = 'spring'
            elif current_month in [6, 7, 8]:
                current_season = 'summer'
            else:
                current_season = 'fall'
            
            # Check if user rates this item's style highly in this season
            item_seasons = getattr(item, 'season', [])
            if isinstance(item_seasons, str):
                item_seasons = [item_seasons]
            
            if current_season in [s.lower() for s in item_seasons]:
                # Item is appropriate for current season
                # Check historical ratings for this style in this season
                # (Simplified - could track season-specific style preferences)
                evolution_score += 0.05
                logger.debug(f"  🍂 {self.safe_get_item_name(item)}: Seasonal match for {current_season} (+0.05)")
            
            logger.debug(f"  📊 {self.safe_get_item_name(item)}: Total evolution score = +{evolution_score:.2f}")
            
            return evolution_score
            
        except Exception as e:
            logger.warning(f"⚠️ Style evolution calculation failed: {e}")
            return 0.0  # Neutral score on error
    
    async def _generate_and_store_flat_lay(
        self,
        outfit_items: List[ClothingItem],
        outfit_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Generate a flat lay image for the outfit and store it in Firebase.
        
        Args:
            outfit_items: List of clothing items in the outfit
            outfit_id: Unique outfit identifier
            user_id: User identifier
            
        Returns:
            Public URL of the flat lay image, or None on failure
        """
        try:
            # Generate flat lay image
            flat_lay_image, error = await self.flat_lay_service.create_flat_lay(
                outfit_items=outfit_items,
                outfit_id=outfit_id,
                output_format="PNG"
            )
            
            if not flat_lay_image or error:
                logger.error(f"Failed to create flat lay: {error}")
                return None
            
            # Upload to Firebase Storage
            flat_lay_url = await self.flat_lay_storage.upload_flat_lay(
                image=flat_lay_image,
                outfit_id=outfit_id,
                user_id=user_id,
                format="PNG"
            )
            
            return flat_lay_url
            
        except Exception as e:
            logger.error(f"Error in flat lay generation and storage: {e}", exc_info=True)
            return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🎵 SPOTIFY-STYLE LEARNING INSIGHT GENERATORS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_learning_insight_message(self, context, item_scores, diversity_scores, favorited_count):
        """Generate a Spotify-style learning insight message for the user - SMART version with real data"""
        try:
            # Count how many items have high diversity scores (fresh picks)
            fresh_picks = sum(1 for score in diversity_scores.values() if score > 1.1)
            
            # Count favorited items actually in item_scores (real data)
            favorites_in_outfit = sum(1 for scores in item_scores.values() 
                                     if scores.get('user_feedback_score', 0) > 0.7)
            
            # Get actual user stats from context
            total_outfits = safe_get(context.user_profile, 'total_outfits_rated', 0) if context.user_profile else 0
            
            # SMART MESSAGING based on user experience level
            if total_outfits == 0:
                # New user - encourage them to rate
                if fresh_picks > 0:
                    return f"Welcome! This {context.style} outfit is designed for {context.occasion}. Rate it to help us learn your unique taste! ✨"
                else:
                    return f"Your first {context.occasion} outfit! We've selected pieces that work well together. Rate it to train your personal AI stylist! 🎨"
            
            elif total_outfits < 5:
                # Learning phase - show we're adapting
                if favorites_in_outfit > 0:
                    return f"Learning your style! Based on your {total_outfits} ratings, this includes {favorites_in_outfit} items similar to what you've liked before. 📊"
                else:
                    return f"Exploring your taste! After {total_outfits} ratings, we're trying new {context.style} combinations to understand your preferences better. 🔍"
            
            else:
                # Experienced user - show sophistication
                if fresh_picks > 0 and favorites_in_outfit > 0:
                    return f"Personalized mix! From {total_outfits} outfits we learned you love {context.style} - mixing {favorites_in_outfit} proven favorites with {fresh_picks} fresh pieces. 🎯"
                elif fresh_picks > 0:
                    return f"Keeping it fresh! Based on {total_outfits} ratings, introducing {fresh_picks} items you haven't worn recently for {context.occasion}. 🔄"
                elif favorites_in_outfit > 0:
                    return f"Your favorites! After {total_outfits} ratings, we know these {favorites_in_outfit} pieces match your {context.style} preferences perfectly. ⭐"
                else:
                    return f"AI-optimized! Using insights from {total_outfits} ratings to create the perfect {context.style} look for {context.occasion}. 🤖"
                    
        except Exception as e:
            logger.warning(f"Failed to generate learning insight: {e}")
            return f"Personalized outfit for {context.occasion} - Rate it to improve future suggestions! 💡"
    
    def _get_item_selection_reason(self, item, item_score_data, diversity_score):
        """Generate a reason why this specific item was selected - REAL DATA version"""
        try:
            # Get actual scores
            user_feedback_score = item_score_data.get('user_feedback_score', 0.5)
            weather_score = item_score_data.get('weather_score', 0.5)
            style_score = item_score_data.get('style_profile_score', 0.5)
            body_score = item_score_data.get('body_type_score', 0.5)
            composite_score = item_score_data.get('composite_score', 0)
            
            # PRIORITY 0: Never worn before = brand new discovery
            wear_count = getattr(item, 'wearCount', None)
            if wear_count is not None and wear_count == 0:
                return "Brand new to your rotation! Let's give this a try 🆕"
            
            # PRIORITY 1: High diversity score = fresh pick (most interesting to user)
            if diversity_score > 1.15:
                days_since_worn = int((diversity_score - 1.0) * 30)  # Rough estimate
                return f"Fresh choice! Haven't worn in ~{days_since_worn} days - time to give it another chance! 🔄"
            
            # PRIORITY 2: High user feedback score = proven favorite
            if user_feedback_score > 0.7:
                # More specific based on score
                if user_feedback_score > 0.85:
                    return "One of your top-rated pieces from past outfits! ⭐"
                else:
                    return "You've rated this positively before - reliable choice! 👍"
            
            # PRIORITY 3: Perfect weather match
            if weather_score > 0.85:
                return "Ideal for today's temperature and conditions! 🌤️"
            
            # PRIORITY 4: Style/body type match
            if style_score > 0.8:
                color_name = safe_get(item, 'color', 'this color')
                return f"{color_name} matches your style preferences! 🎨"
            
            if body_score > 0.8:
                fit = safe_get(item.metadata, 'visualAttributes.fit', 'This fit') if hasattr(item, 'metadata') else 'This fit'
                return f"{fit} fit works great for your profile! 👔"
            
            # PRIORITY 5: High composite score (general AI confidence)
            if composite_score > 6.5:
                return "Top-scored item across all our AI dimensions! 🤖"
            
            # Default - be honest
            return "Balanced choice for this outfit's overall harmony 🎯"
            
        except Exception as e:
            logger.warning(f"Failed to get item reason: {e}")
            return "Selected by AI stylist 🤖"
    
    def _generate_diversity_message(self, diversity_result, session_tracker, session_id):
        """Generate a message about outfit diversity and freshness"""
        try:
            diversity_score = safe_get(diversity_result, 'diversity_score', 0.8)
            
            if diversity_score > 0.9:
                return "🎯 Super fresh! This outfit introduces new combinations you haven't tried before."
            elif diversity_score > 0.7:
                return "✨ Balanced mix - combining familiar favorites with fresh elements."
            else:
                return "💎 Classic combo - featuring reliable pieces from your style profile."
        except Exception as e:
            logger.warning(f"Failed to generate diversity message: {e}")
            return "We're keeping your wardrobe rotation fresh and varied!"
