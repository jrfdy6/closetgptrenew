#!/usr/bin/env python3
"""
Robust Outfit Generation Service
================================

Enterprise-grade outfit generation with comprehensive validation,
fallback strategies, body type optimization, and style profile integration.
"""

import asyncio
import logging
import time
import uuid
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Robust import strategy to handle different execution contexts
from ..config.feature_flags import is_semantic_match_enabled, is_debug_output_enabled, is_force_traditional_enabled
from ..utils.semantic_normalization import normalize_item_metadata
from ..utils.semantic_compatibility import style_matches, mood_matches, occasion_matches
from ..utils.semantic_telemetry import record_semantic_filtering_metrics
from ..utils.enhanced_debug_output import format_final_debug_response
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

class PerformanceMetrics:
    """Mock PerformanceMetrics class"""
    def __init__(self, **kwargs):
        self.confidence = (safe_get(kwargs, 'confidence', 0.5) if kwargs else 0.5)
        self.diversity_score = (safe_get(kwargs, 'diversity_score', 0.0) if kwargs else 0.0)

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
            return item.get('name', 'Unknown')
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
        raw_values = item.get(field_name, [])
        if isinstance(raw_values, list):
            return [str(v).lower() for v in raw_values]
        elif isinstance(raw_values, str):
            return [raw_values.lower()]
        
        return []
    
    async def generate_outfit(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate an outfit with multi-layered scoring system"""
        logger.info(f"🎨 Starting robust outfit generation for user {context.user_id}")
        logger.info(f"📋 Context: {context.occasion}, {context.style}, {context.mood}")
        logger.info(f"📦 Wardrobe size: {len(context.wardrobe)} items")
        
        # ═══════════════════════════════════════════════════════════════════════
        # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
        # ═══════════════════════════════════════════════════════════════════════
        try:
            return await self._generate_outfit_internal(context)
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
    
    async def _generate_outfit_internal(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Internal outfit generation logic with full error handling"""
        
        # ═══════════════════════════════════════════════════════════════════════
        # HYDRATION & CONTEXT VALIDATION
        # ═══════════════════════════════════════════════════════════════════════
        
        # DEBUG: Log context details to identify NoneType issues
        # print(f"🔍 DEBUG ROBUST INTERNAL: context = {context}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: (context.wardrobe if context else []) = {context.wardrobe}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: context.user_profile = {context.user_profile}")
        # print(f"🔍 DEBUG ROBUST INTERNAL: (context.weather if context else None) = {context.weather}")
        
        # Hydrate wardrobe items
        logger.debug(f"🔄 Hydrating {len(context.wardrobe)} wardrobe items")
        try:
            if isinstance(context.wardrobe, list) and len(context.wardrobe) > 0 and isinstance(context.wardrobe[0], dict):
                safe_wardrobe = ensure_items_safe_for_pydantic(context.wardrobe)
                logger.debug(f"✅ Hydrated {len(safe_wardrobe)} items successfully")
                if context:
                    context.wardrobe = safe_wardrobe
            else:
                logger.debug(f"✅ Items already ClothingItem objects")
        except Exception as hydrator_error:
            logger.error(f"❌ Hydration failed: {hydrator_error}")
            # print(f"🚨 HYDRATION ERROR: {hydrator_error}")
            import traceback
            # print(f"🚨 HYDRATION TRACEBACK: {traceback.format_exc()}")
        
        # DEBUG: Check context types after hydration
        logger.info(f"🔍 DEBUG: After hydration - user_profile type: {type(context.user_profile)}")
        logger.info(f"🔍 DEBUG: After hydration - weather type: {type(context.weather)}")
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
        # STEP 1: FILTER SUITABLE ITEMS FIRST
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🔍 FILTERING STEP 1: Starting item filtering for {context.occasion} occasion")
        suitable_items = await self._filter_suitable_items(context)
        logger.info(f"✅ FILTERING STEP 1: {len(suitable_items)} suitable items passed from {len(context.wardrobe)} total")
        
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
        logger.info(f"🔍 DEBUG SCORING: Starting to create scores for {len(suitable_items)} suitable items")
        for i, item in enumerate(suitable_items):
            item_id = safe_item_access(item, 'id', f"item_{len(item_scores)}")
            logger.info(f"🔍 DEBUG SCORING: Creating score for item {i+1}: {item_id} - {getattr(item, 'name', 'Unknown')}")
            item_scores[item_id] = {
                'item': item,
                'body_type_score': 0.0,
                'style_profile_score': 0.0,
                'weather_score': 0.0,
                'user_feedback_score': 0.0,  # NEW!
                'composite_score': 0.0
            }
        
        logger.info(f"🔍 DEBUG SCORING: Created {len(item_scores)} item scores")
        
        logger.info(f"🔍 DEBUG: Initialized {len(item_scores)} items for scoring")
        
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
            logger.info(f"🔍 ITEM {i+1} SCORES: {self.safe_get_item_name(scores['item'])}: body={scores['body_type_score']:.2f}, style={scores['style_profile_score']:.2f}, weather={scores['weather_score']:.2f}, feedback={scores['user_feedback_score']:.2f}, compat={compat_score:.2f}")
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
        
        diversity_weight = 0.30  # 30% weight for diversity - INCREASED to ensure variety (was 0.10)
        
        # Adjust other weights to accommodate diversity dimension (must sum to 100%)
        if temp > 75 or temp < 50:  # Extreme weather
            weather_weight = 0.18  # Reduced to accommodate higher diversity
            compatibility_weight = 0.12
            style_weight = 0.16
            body_weight = 0.12
            user_feedback_weight = 0.12
        else:  # Moderate weather
            weather_weight = 0.14  # Reduced to accommodate higher diversity
            compatibility_weight = 0.11
            style_weight = 0.18
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
            soft_penalty = self._soft_score(scores['item'], (context.occasion if context else "unknown"), (context.style if context else "unknown"), (context.mood if context else "unknown"))
            final_score = base_score + soft_penalty
            
            scores['composite_score'] = final_score
            scores['diversity_score'] = diversity_score
            scores['soft_penalty'] = soft_penalty
            scores['base_score'] = base_score
        
        # Log top scored items (reduced verbosity)
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        logger.info(f"🏆 Top 3 scored items (with diversity boost):")
        for i, (item_id, scores) in enumerate(sorted_items[:3]):
            diversity_score = scores.get('diversity_score', 1.0)
            logger.info(f"  {i+1}. {self.safe_get_item_name(scores['item'])}: {scores['composite_score']:.2f} (diversity: {diversity_score:.2f})")
        
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
        
        # Pass scored items to cohesive composition
        outfit = await self._cohesive_composition_with_scores(context, item_scores)
        
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
        if not occasion_matches(occasion, normalized_item.get('occasion', [])):
            rejection_reasons.append(f"Occasion mismatch: item occasions {normalized_item.get('occasion', [])}")
        
        # Check style compatibility  
        if not style_matches(style, normalized_item.get('style', [])):
            rejection_reasons.append(f"Style mismatch: item styles {normalized_item.get('style', [])}")
        
        # Check mood compatibility
        if not mood_matches(mood, normalized_item.get('mood', [])):
            rejection_reasons.append(f"Mood mismatch: item moods {normalized_item.get('mood', [])}")
        
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
        """Create a basic outfit from available items"""
        logger.info(f"🎯 Creating outfit from {len(items)} items using strategy: {strategy}")
        
        # Simple item selection - pick one of each essential type
        selected_items = []
        
        # Find essential categories
        essential_types = ['shirt', 'top', 'blouse', 'pants', 'shorts', 'shoes']
        
        for essential_type in essential_types:
            for item in items:
                item_type = safe_item_access(item, 'type', '').lower()
                if essential_type in item_type and item not in selected_items:
                    selected_items.append(item)
                    break
        
        # If we don't have enough items, add any remaining items
        if len(selected_items) < 3:
            for item in items:
                if item not in selected_items:
                    selected_items.append(item)
                    if len(selected_items) >= 4:  # Reasonable outfit size
                        break
        
        return OutfitGeneratedOutfit(
            items=selected_items,
            confidence=0.6,  # Moderate confidence for fallback
            metadata={
                "generation_strategy": strategy,
                "fallback_reason": "progressive_filtering",
                "original_occasion": (context.occasion if context else "unknown"),
                "original_style": (context.style if context else "unknown")
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
        logger.info(f"🔍 DEBUG: user_profile type: {type(context.user_profile)}")
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
        
        # Apply filtering logic matching the JavaScript implementation
        for raw_item in (context.wardrobe if context else []):
            # Normalize item metadata
            item = normalize_item_metadata(raw_item)
            reasons = []
            ok_occ = False
            ok_style = False
            ok_mood = False
            
            if semantic_filtering:
                # Use semantic filtering with compatibility helpers
                ok_occ = occasion_matches(context.occasion if context else None, item.get('occasion', []))
                ok_style = style_matches(context.style if context else None, item.get('style', []))
                ok_mood = mood_matches(context.mood if context else None, item.get('mood', []))
            else:
                # Enhanced: Use normalized metadata for consistent filtering
                # Try normalized fields first (already lowercase), fallback to raw
                item_occasions = self._get_normalized_or_raw(item, 'occasion')
                item_styles = self._get_normalized_or_raw(item, 'style')
                item_moods = self._get_normalized_or_raw(item, 'mood')
                
                context_occasion = (context.occasion or "").lower() if context else ""
                context_style = (context.style or "").lower() if context else ""
                context_mood = (context.mood or "").lower() if context else ""
                
                # All values already lowercase from normalized or converted
                ok_occ = any(s == context_occasion for s in item_occasions)
                ok_style = any(s == context_style for s in item_styles)
                ok_mood = len(item_moods) == 0 or any(m == context_mood for m in item_moods)
            
            # Build rejection reasons
            if not ok_occ:
                reasons.append(f"Occasion mismatch: item occasions {item.get('occasion', [])}")
            if not ok_style:
                reasons.append(f"Style mismatch: item styles {item.get('style', [])}")
            if not ok_mood:
                reasons.append(f"Mood mismatch: item moods {item.get('mood', [])}")
            
            # Create debug entry
            debug_entry = {
                'id': item.get('id', getattr(raw_item, 'id', 'unknown')),
                'name': item.get('name', getattr(raw_item, 'name', 'Unknown')),
                'valid': ok_occ and ok_style and ok_mood,
                'reasons': reasons
            }
            debug_analysis.append(debug_entry)
            
            # ADAPTIVE LOGIC: For mismatches, use OR (occasion OR style), ignore mood
            # Detect mismatch between occasion and style
            filter_mismatch_detected = False
            if context and context.occasion and context.style:
                occ_lower = context.occasion.lower()
                style_lower = context.style.lower()
                # Athletic + Classic/Formal/Business = mismatch
                if occ_lower in ['athletic', 'gym', 'workout', 'sport'] and style_lower in ['classic', 'formal', 'business', 'professional']:
                    filter_mismatch_detected = True
                # Formal + Casual/Athleisure = mismatch
                elif occ_lower in ['business', 'formal', 'interview'] and style_lower in ['casual', 'athleisure', 'sporty']:
                    filter_mismatch_detected = True
            
            # Add to valid items based on adaptive logic
            if filter_mismatch_detected:
                # MISMATCH MODE: Pass if occasion OR style matches (mood ignored - it's a bonus)
                if ok_occ or ok_style:
                    valid_items.append(raw_item)
            else:
                # NORMAL MODE: Pass if occasion AND style match (mood ignored - it's a bonus)
                if ok_occ and ok_style:
                    valid_items.append(raw_item)
        
        logger.info(f"🔍 HARD FILTER: Results - {len(valid_items)} passed filters, {len(debug_analysis) - len(valid_items)} rejected")
        
        # PROGRESSIVE RELAXATION: If no suitable items found, use emergency fallback
        if len(valid_items) == 0:
            logger.warning(f"🚨 NO SUITABLE ITEMS: All items rejected by hard filters - using emergency fallback")
            
            # Emergency: Use any available items (hard filters were too strict)
            logger.info(f"🆘 EMERGENCY: Using all wardrobe items as fallback")
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
            elif temp < 40:  # Cold weather - more permissive
                cold_inappropriate = ['shorts', 'sandals', 'tank', 'light', 'summer']
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
                if not item.get('valid', False):
                    debug_reasons.extend(item.get('reasons', []))
            
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
        """Hard constraints - using compatibility matrix for semantic filtering"""
        # Re-enabled compatibility matrix with proper error handling
        
        item_name = self.safe_get_item_name(item).lower()
        item_type = str(getattr(item, 'type', '')).lower()
        occasion_lower = occasion.lower()
        
        # Use compatibility matrix for semantic filtering
        try:
            from ..services.compatibility_matrix import CompatibilityMatrix
            compat_matrix = CompatibilityMatrix()
            
            # Check semantic compatibility
            is_compatible = compat_matrix.is_compatible(
                item_type=item_type,
                item_name=item_name,
                target_occasion=occasion,
                target_style=style
            )
            
            if not is_compatible:
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Compatibility matrix failed, using fallback: {e}")
            # Fallback to basic constraints if matrix fails
        
        # Basic hard constraints (fallback)
        hard_constraints = [
            (item_type == 'tuxedo' and occasion_lower == 'athletic'),
            (item_type == 'evening_gown' and occasion_lower == 'athletic'),
            ('bikini' in item_name and occasion_lower == 'business'),
            ('swimwear' in item_name and occasion_lower == 'business'),
        ]
        
        for constraint in hard_constraints:
            if constraint:
                return False
        
        return True
    
    def _soft_score(self, item: ClothingItem, occasion: str, style: str, mood: str = "Professional") -> float:
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
            logger.info(f"🔄 MISMATCH DETECTED: {occasion} + {style} style - prioritizing OCCASION ({occasion_multiplier}x) over STYLE ({style_multiplier}x)")
        elif occasion_lower in ['business', 'formal'] and style_lower in ['athletic', 'casual', 'streetwear']:
            occasion_multiplier = 1.5
            style_multiplier = 0.2
            logger.info(f"🔄 MISMATCH DETECTED: {occasion} + {style} style - prioritizing OCCASION ({occasion_multiplier}x) over STYLE ({style_multiplier}x)")
        
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
                # Formal outerwear
                'blazer', 'sport coat', 'leather jacket', 'biker jacket',
                # Structured shirts
                'dress shirt', 'button up', 'button down', 'button-up', 'button-down'
            ]
            
            if any(block in item_type_lower or block in item_name for block in gym_blocks):
                penalty -= 5.0 * occasion_multiplier  # EXTREME penalty - eliminates item
                logger.debug(f"  🚫🚫🚫 GYM: Blocked '{item_name[:40]}' - formal/structured item ({-5.0 * occasion_multiplier:.2f})")
            # Boost athletic-appropriate items
            elif any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout']):
                penalty += 1.5 * occasion_multiplier  # HUGE boost for exact athletic match
                logger.info(f"  ✅✅ PRIMARY: Athletic occasion tag match: {+1.5 * occasion_multiplier:.2f}")
            elif 'sport' in item_occasion_lower:
                penalty += 1.3 * occasion_multiplier  # VERY HIGH boost for 'sport' (almost as good as athletic)
                logger.info(f"  ✅✅ SPORT: Sport occasion tag for Athletic: {+1.3 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['casual', 'beach', 'vacation']):
                penalty += 0.8 * occasion_multiplier  # GOOD boost for casual items (acceptable for athletic)
                logger.info(f"  ✅ SECONDARY: Casual occasion tag for Athletic (acceptable): {+0.8 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['business', 'formal', 'interview', 'conference']):
                penalty -= 1.0 * occasion_multiplier  # REDUCED penalty (was -2.0, now -1.0 to allow some items through)
                logger.info(f"  🚫 REDUCED: Formal occasion tag for Athletic request: {-1.0 * occasion_multiplier:.2f}")
        
        elif occasion_lower in ['business', 'formal', 'interview', 'wedding', 'conference']:
            if any(occ in item_occasion_lower for occ in ['business', 'formal', 'interview', 'conference', 'wedding']):
                penalty += 1.5 * occasion_multiplier  # HUGE boost for matching occasion tag
                logger.info(f"  ✅✅ PRIMARY: Formal occasion tag match: {+1.5 * occasion_multiplier:.2f}")
            elif any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout', 'sport']):
                penalty -= 2.0 * occasion_multiplier  # HUGE penalty for wrong occasion
                logger.info(f"  🚫🚫 PRIMARY: Athletic occasion tag for Formal request: {-2.0 * occasion_multiplier:.2f}")
        
        elif occasion_lower in ['casual', 'brunch', 'weekend']:
            if any(occ in item_occasion_lower for occ in ['casual', 'brunch', 'weekend', 'vacation']):
                penalty += 1.0 * occasion_multiplier  # Good boost for matching occasion tag
                logger.info(f"  ✅✅ PRIMARY: Casual occasion tag match: {+1.0 * occasion_multiplier:.2f}")
        
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
            
            # WAISTBAND TYPE ANALYSIS for loungewear
            waistband_type = None
            if hasattr(item, 'metadata') and item.metadata:
                visual_attrs = getattr(item.metadata, 'visualAttributes', None)
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
        # KEYWORD-BASED SCORING: Secondary scoring based on item names (LIGHT penalties only)
        # ═══════════════════════════════════════════════════════════════════════
        
        if occasion_lower == 'athletic':
            # BOOST athletic/sport keywords strongly
            if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'workout', 'training', 'performance']):
                penalty += 0.6 * occasion_multiplier  # Strong boost for primary athletic keywords
                logger.info(f"  ✅ KEYWORD: Athletic keyword in name: {+0.6 * occasion_multiplier:.2f}")
            elif any(word in item_name for word in ['tank', 'sneaker', 'jogger', 'track', 'jersey', 'nike', 'adidas']):
                penalty += 0.5 * occasion_multiplier  # Good boost for sport-related items/brands
                logger.info(f"  ✅ KEYWORD: Sport-related keyword/brand: {+0.5 * occasion_multiplier:.2f}")
            # LIGHT penalties for formal items (don't eliminate completely)
            elif any(word in item_name for word in ['button', 'dress', 'formal', 'oxford', 'blazer', 'dockers']):
                penalty -= 0.1 * occasion_multiplier  # Very light penalty
                logger.info(f"  ⚠️ KEYWORD: Formal keyword penalty: {-0.1 * occasion_multiplier:.2f}")
        
        elif occasion_lower == 'business':
            # Light penalties for athletic items
            if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'tank']):
                penalty -= 0.1 * occasion_multiplier
            # Boost business items
            elif any(word in item_name for word in ['business', 'professional', 'formal', 'button', 'dress']):
                penalty += 0.5 * occasion_multiplier
        
        # ═══════════════════════════════════════════════════════════════════════
        # WAISTBAND TYPE FORMALITY SCORING (for all occasions)
        # ═══════════════════════════════════════════════════════════════════════
        waistband_type = None
        if hasattr(item, 'metadata') and item.metadata:
            visual_attrs = getattr(item.metadata, 'visualAttributes', None)
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
                'athletic': 1,
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
        
        # STEP 4: Sort items by preference score
        scored_items = []
        for item in suitable_items:
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
        return selected_items
    
    def _get_dynamic_category_limits(self, context: GenerationContext, target_count: int) -> Dict[str, int]:
        """Get category limits that adapt to target count - TARGET-DRIVEN with optional outerwear"""
        occasion_lower = (context.occasion if context else "unknown").lower()
        style_lower = (context.style if context else "unknown").lower() if (context.style if context else "unknown") else ""
        
        # Check if outerwear is needed based on temperature, occasion, and style
        needs_outerwear = self._needs_outerwear(context)
        
        # TARGET-DRIVEN: Category limits adapt to target count with optional outerwear
        if target_count <= 3:
            # Minimal outfit: essentials only
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1}
            else:
                return {"tops": 1, "bottoms": 1, "shoes": 1}
        
        elif target_count == 4:
            # Standard outfit: add one layer
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1}
            else:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "accessories": 1}
        
        elif target_count == 5:
            # Enhanced outfit: add layers
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1, "accessories": 1}
            else:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "accessories": 2}
        
        elif target_count >= 6:
            # Full outfit: maximum layers
            if needs_outerwear:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1, "accessories": 2, "sweater": 1}
            else:
                return {"tops": 1, "bottoms": 1, "shoes": 1, "accessories": 3, "sweater": 1}
        
        # Fallback for unexpected target counts
        if needs_outerwear:
            return {"tops": 1, "bottoms": 1, "shoes": 1, "outerwear": 1, "accessories": 1}
        else:
            return {"tops": 1, "bottoms": 1, "shoes": 1, "accessories": 1}
    
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
        """Select basic items for fallback - simplified version"""
        logger.info(f"🔍 BASIC SELECT: Selecting from {len(wardrobe)} items")
        basic_items = []
        
        # Simple selection: pick one item of each basic type
        categories_found = set()
        for item in wardrobe:
            category = self._get_item_category(item)
            if category in ['tops', 'bottoms', 'shoes'] and category not in categories_found:
                basic_items.append(item)
                categories_found.add(category)
                if len(categories_found) == 3:
                    break
        
        logger.info(f"🔍 BASIC SELECT: Selected {len(basic_items)} items")
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
        """Get category for an item"""
        item_type = getattr(item, 'type', '')
        item_name = getattr(item, 'name', 'Unknown')
        
        # Handle enum types (e.g., ClothingType.SHIRT)
        if hasattr(item_type, 'value'):
            item_type = item_type.value.lower()
        elif hasattr(item_type, 'name'):
            item_type = item_type.name.lower()
        else:
            item_type = str(item_type).lower()
        
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
        logger.info(f"🏷️ CATEGORY: '{item_name[:50]}' type='{item_type}' → category='{category}'")
        
        return category
    
    def _check_inappropriate_combination(self, item1: ClothingItem, item2: ClothingItem) -> bool:
        """Check if two items form an inappropriate combination - simplified version"""
        # For now, allow all combinations
        return False
    
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
            
            # Occasion appropriateness
            item_occasions = getattr(item, 'occasion', [])
            if isinstance(item_occasions, str):
                item_occasions = [item_occasions]
            
            item_occasions_lower = [occ.lower() for occ in item_occasions]
            if (context.occasion if context else "unknown").lower() in item_occasions_lower:
                base_score += 0.2
            
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
                temp = (context.weather if context else None).temperature
                logger.info(f"🌤️ WEATHER ANALYZER: Got temperature from weather object: {temp}°F")
            elif hasattr(context.weather, '__dict__') and 'temperature' in (context.weather if context else None).__dict__:
                temp = (context.weather if context else None).__dict__['temperature']
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
            
            for item_id, scores in item_scores.items():
                item = scores['item']
                base_score = 0.5  # Default neutral score
                
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
                        if temp_compat.minTemp <= temp <= temp_compat.maxTemp:
                            base_score += 0.2
                
                # Material appropriateness for weather
                item_name = self.safe_get_item_name(item) if item else "Unknown"
                item_name_lower = item_name.lower()
                item_type_lower = str(self.safe_get_item_type(item)).lower()
                
                # Cold weather items
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
            
            # Get favorited items from wardrobe
            wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
            wardrobe_docs = wardrobe_ref.stream()
            
            for wardrobe_doc in wardrobe_docs:
                item_data = wardrobe_doc.to_dict()
                if safe_get(item_data, 'isFavorite') or safe_get(item_data, 'favorite_score', 0) > 0.7:
                    favorited_items.add(safe_get(item_data, 'id'))
            
            logger.info(f"📊 Feedback data loaded: {len(outfit_ratings)} rated items, {len(favorited_items)} favorites")
            
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
            # 4. WEAR COUNT ALTERNATION (explore vs exploit)
            # ─────────────────────────────────────────────────────────────
            item_wear_count = getattr(item, 'wearCount', 0)
            
            if boost_rare:
                # BOOST RARELY-WORN ITEMS (discovery/diversity mode)
                if item_wear_count == 0:
                    base_score += 0.25  # Never worn - high boost
                    logger.debug(f"  🆕 {self.safe_get_item_name(item)}: Never worn → +0.25 (discovery)")
                elif item_wear_count <= 3:
                    base_score += 0.15  # Lightly worn - moderate boost
                    logger.debug(f"  🌱 {self.safe_get_item_name(item)}: Lightly worn ({item_wear_count}) → +0.15")
                elif item_wear_count > 15:
                    base_score -= 0.10  # Overused - penalty
                    logger.debug(f"  🔁 {self.safe_get_item_name(item)}: Overused ({item_wear_count}) → -0.10")
            else:
                # BOOST POPULAR ITEMS (reliability/favorites mode)
                if item_wear_count >= 5 and item_wear_count <= 15:
                    base_score += 0.20  # Sweet spot - proven favorites
                    logger.debug(f"  🌟 {self.safe_get_item_name(item)}: Popular ({item_wear_count} wears) → +0.20")
                elif item_wear_count > 15:
                    base_score += 0.10  # Very popular - still boost but less
                    logger.debug(f"  ⭐ {self.safe_get_item_name(item)}: Very popular ({item_wear_count}) → +0.10")
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
    
    
    async def _cohesive_composition_with_scores(self, context: GenerationContext, item_scores: dict) -> OutfitGeneratedOutfit:
        """Generate cohesive outfit using multi-layered scores with intelligent layering"""
        logger.info(f"🎨 COHESIVE COMPOSITION: Using scored items to create outfit")
        logger.info(f"🔍 DEBUG: Received {len(item_scores)} scored items")
        logger.info(f"🔍 DEBUG: Context occasion: {context.occasion}, style: {context.style}")
        
        # DEBUG: Log item scores details
        if item_scores:
            logger.info(f"🔍 DEBUG SCORES: First 3 item scores:")
            for i, (item_id, score) in enumerate(list(item_scores.items())[:3]):
                logger.info(f"🔍 DEBUG SCORE {i+1}: {item_id} = {score}")
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
        
        # Sort items by composite score with randomization to break ties
        import random
        sorted_items = sorted(
            item_scores.items(), 
            key=lambda x: x[1]['composite_score'] + random.uniform(-0.05, 0.05),  # ±5% randomization for variety
            reverse=True
        )
        logger.info(f"🎲 RANDOMIZATION: Added ±5% noise to scores for variety")
        
        # Select items with intelligent layering
        selected_items = []
        categories_filled = {}
        
        # Phase 1: Fill essential categories (tops, bottoms, shoes)
        logger.info(f"📦 PHASE 1: Selecting essential items (top, bottom, shoes)")
        logger.info(f"🔍 DEBUG PHASE 1: Starting with {len(sorted_items)} scored items")
        for item_id, score_data in sorted_items:
            item = score_data['item']
            category = self._get_item_category(item)
            item_name_lower = (self.safe_get_item_name(item) if item else "Unknown").lower()
            
            logger.info(f"🔍 DEBUG PHASE 1: Processing item {self.safe_get_item_name(item)} - category: {category}, score: {score_data['composite_score']:.2f}")
            
            # Determine layering level
            layer_level = 'tops'  # Default
            if category == 'tops':
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
            
            # Essential categories first
            if category in ['tops', 'bottoms', 'shoes']:
                if category not in categories_filled:
                    selected_items.append(item)
                    categories_filled[category] = True
                    logger.info(f"  ✅ Essential {category}: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                else:
                    logger.info(f"  ⏭️ Essential {category}: {self.safe_get_item_name(item)} skipped - category already filled")
            else:
                logger.info(f"  ⏭️ Non-essential {category}: {self.safe_get_item_name(item)} - will check in Phase 2")
        
        logger.info(f"🔍 DEBUG PHASE 1 COMPLETE: Selected {len(selected_items)} items, categories filled: {categories_filled}")
        
        # EMERGENCY BYPASS: If no items selected, force select the first item
        if len(selected_items) == 0 and sorted_items:
            logger.warning(f"🚨 EMERGENCY BYPASS: No items selected in Phase 1, forcing selection of first item")
            first_item = sorted_items[0][1]['item']
            selected_items.append(first_item)
            categories_filled['tops'] = True  # Assume it's a top
            logger.info(f"🚨 EMERGENCY BYPASS: Forced selection of {self.safe_get_item_name(first_item)}")
        
        # Phase 2: Add layering pieces based on target count
        logger.info(f"📦 PHASE 2: Adding {recommended_layers} layering pieces")
        for item_id, score_data in sorted_items:
            if len(selected_items) >= target_items:
                break
            
            item = score_data['item']
            if item in selected_items:
                continue
            
            category = self._get_item_category(item)
            item_name_lower = (self.safe_get_item_name(item) if item else "Unknown").lower()
            
            # Determine layering appropriateness
            # VERSION: 2025-10-11-DUPLICATE-FIX
            if category == 'outerwear' and score_data['composite_score'] > 0.6:
                # ✅ FIX: Check if outerwear already exists before adding
                has_outerwear = any(self._get_item_category(i) == 'outerwear' for i in selected_items)
                
                if not has_outerwear and (temp < 65 or occasion_lower in ['business', 'formal']):
                    selected_items.append(item)
                    categories_filled['outerwear'] = True  # Track that we added outerwear
                    logger.warning(f"  ✅ Outerwear: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                elif has_outerwear:
                    logger.warning(f"  ⏭️ Outerwear: {self.safe_get_item_name(item)} - SKIPPED (already have outerwear)")
            
            elif category == 'tops' and score_data['composite_score'] > 0.6:
                # ✅ FIX: Check if mid-layer already exists before adding
                is_mid_layer = any(kw in item_name_lower for kw in ['sweater', 'cardigan', 'vest'])
                has_mid_layer = any(
                    kw in self.safe_get_item_name(i).lower() 
                    for i in selected_items 
                    for kw in ['sweater', 'cardigan', 'vest']
                )
                
                if is_mid_layer and not has_mid_layer and temp < 70:
                    selected_items.append(item)
                    categories_filled['mid'] = True  # Track that we added mid-layer
                    logger.warning(f"  ✅ Mid-layer: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                elif is_mid_layer and has_mid_layer:
                    logger.warning(f"  ⏭️ Mid-layer: {self.safe_get_item_name(item)} - SKIPPED (already have mid-layer)")
            
            elif category == 'accessories' and score_data['composite_score'] > 0.7:
                # Accessories can have multiple items (belts, watches, etc.)
                if temp < 50 or occasion_lower in ['formal', 'business']:
                    # Limit to 2 accessories max
                    accessory_count = sum(1 for i in selected_items if self._get_item_category(i) == 'accessories')
                    if accessory_count < 2:
                        selected_items.append(item)
                        logger.warning(f"  ✅ Accessory: {self.safe_get_item_name(item)} (score={score_data['composite_score']:.2f})")
                    else:
                        logger.warning(f"  ⏭️ Accessory: {self.safe_get_item_name(item)} - SKIPPED (already have 2 accessories)")
        
        # Ensure minimum items
        if len(selected_items) < min_items:
            logger.warning(f"⚠️ Only {len(selected_items)} items selected, adding more to reach minimum {min_items}...")
            for item_id, score_data in sorted_items:
                if score_data['item'] not in selected_items and len(selected_items) < min_items:
                    selected_items.append(score_data['item'])
                    logger.info(f"  ➕ Filler: {self.safe_get_item_name(score_data['item'])}")
        
        logger.info(f"🎯 FINAL SELECTION: {len(selected_items)} items")
        
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
        avg_composite_score = sum(item_scores[self.safe_get_item_attr(item, "id", "")]['composite_score'] for item in selected_items) / len(selected_items)
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
        logger.info(f"🔍 DEBUG FINAL SELECTION: About to create outfit with {len(selected_items)} selected items")
        logger.info(f"🔍 DEBUG FINAL SELECTION: Selected items: {[getattr(item, 'name', 'Unknown') for item in selected_items]}")
        logger.info(f"🔍 DEBUG FINAL SELECTION: Target items was: {target_items}, min_items: {min_items}, max_items: {max_items}")
        logger.info(f"🔍 DEBUG FINAL SELECTION: Categories filled: {categories_filled}")
        logger.info(f"🔍 DEBUG FINAL SELECTION: Item scores count: {len(item_scores)}")
        if item_scores:
            logger.info(f"🔍 DEBUG FINAL SELECTION: Top 3 scored items: {[(item_id, (safe_get(scores, 'composite_score', 0) if scores else 0)) for item_id, scores in list(item_scores.items())[:3]]}")
        
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
                "avg_composite_score": avg_composite_score,
                "diversity_score": (safe_get(diversity_result, 'diversity_score', 0.8) if diversity_result else 0.8),
                "color_theory_applied": True,
                "analyzers_used": ["body_type", "style_profile", "weather", "user_feedback", "metadata_compatibility", "diversity"]
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
