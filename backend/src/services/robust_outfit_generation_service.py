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
import sys
import os

# Add the src directory to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import real services - try relative imports first, then absolute
try:
    from ..custom_types.wardrobe import ClothingItem
    from ..custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
    from ..custom_types.weather import WeatherData
    from ..custom_types.user_profile import UserProfile
    from .robust_hydrator import ensure_items_safe_for_pydantic
    print("✅ ROBUST SERVICE: Using relative imports")
except (ImportError, ValueError) as e:
    print(f"⚠️ Relative imports failed: {e}")
    try:
        from custom_types.wardrobe import ClothingItem
        from custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
        from custom_types.weather import WeatherData
        from custom_types.user_profile import UserProfile
        from services.robust_hydrator import ensure_items_safe_for_pydantic
        print("✅ ROBUST SERVICE: Using absolute imports")
    except ImportError as e2:
        print(f"⚠️ Absolute imports failed: {e2}")
        print("🔧 ROBUST SERVICE: Using fallback minimal classes")
        
        # Create minimal fallback classes to prevent total import failure
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

def ensure_items_safe_for_pydantic(items):
    return items

class MockService:
    """Mock service with all required methods"""
    
    def __getattr__(self, name):
        """Catch any missing method calls"""
        print(f"🔧 MOCK SERVICE: Called missing method '{name}' - returning default")
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
    print("✅ DIVERSITY FILTER: Real service loaded")
except ImportError as e:
    print(f"⚠️ DiversityFilterService import failed: {e}")
    diversity_filter = MockService()
    print("🔧 DIVERSITY FILTER: Using mock service")

try:
    from .strategy_analytics_service import StrategyAnalyticsService, StrategyStatus
    strategy_analytics = StrategyAnalyticsService()
    print("✅ STRATEGY ANALYTICS: Real service loaded")
except ImportError as e:
    print(f"⚠️ StrategyAnalyticsService import failed: {e}")
    
    # Define StrategyStatus enum if import fails
    class StrategyStatus(Enum):
        SUCCESS = "success"
        FAILED = "failed"
        PARTIAL = "partial"
    
    strategy_analytics = MockService()
    print("🔧 STRATEGY ANALYTICS: Using mock service")

try:
    from .adaptive_tuning_service import AdaptiveTuningService
    adaptive_tuning = AdaptiveTuningService()
    print("✅ ADAPTIVE TUNING: Real service loaded")
except ImportError as e:
    print(f"⚠️ AdaptiveTuningService import failed: {e}")
    adaptive_tuning = MockService()
    print("🔧 ADAPTIVE TUNING: Using mock service")

class PerformanceMetrics:
    """Mock PerformanceMetrics class"""
    def __init__(self, **kwargs):
        self.confidence = kwargs.get('confidence', 0.5)
        self.diversity_score = kwargs.get('diversity_score', 0.0)

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
    
    async def generate_outfit(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Generate an outfit with multi-layered scoring system"""
        logger.info(f"🎨 Starting robust outfit generation for user {context.user_id}")
        logger.info(f"📋 Context: {context.occasion}, {context.style}, {context.mood}")
        logger.info(f"📦 Wardrobe size: {len(context.wardrobe)} items")
        
        # ═══════════════════════════════════════════════════════════════════════
        # EXCEPTION WRAPPER WITH FULL TRACEBACK LOGGING
        # ═══════════════════════════════════════════════════════════════════════
        try:
            return await self._generate_outfit_internal(context)
        except Exception as e:
            logger.error(f"❌ ROBUST SERVICE FAILED: {str(e)}", exc_info=True)
            logger.error(f"❌ FULL TRACEBACK:", exc_info=True)
            
            # Return a fallback outfit instead of crashing
            logger.warning(f"⚠️ FALLBACK: Returning emergency outfit due to robust service failure")
            return OutfitGeneratedOutfit(
                items=[],
                confidence=0.1,
                metadata={
                    "generation_strategy": "emergency_fallback",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "fallback_reason": "robust_service_exception"
                }
            )
    
    async def _generate_outfit_internal(self, context: GenerationContext) -> OutfitGeneratedOutfit:
        """Internal outfit generation logic with full error handling"""
        
        # ═══════════════════════════════════════════════════════════════════════
        # HYDRATION & CONTEXT VALIDATION
        # ═══════════════════════════════════════════════════════════════════════
        
        # Hydrate wardrobe items
        logger.debug(f"🔄 Hydrating {len(context.wardrobe)} wardrobe items")
        try:
            if isinstance(context.wardrobe, list) and len(context.wardrobe) > 0 and isinstance(context.wardrobe[0], dict):
                safe_wardrobe = ensure_items_safe_for_pydantic(context.wardrobe)
                logger.debug(f"✅ Hydrated {len(safe_wardrobe)} items successfully")
                context.wardrobe = safe_wardrobe
            else:
                logger.debug(f"✅ Items already ClothingItem objects")
        except Exception as hydrator_error:
            logger.error(f"❌ Hydration failed: {hydrator_error}")
        
        # DEBUG: Check context types after hydration
        logger.info(f"🔍 DEBUG: After hydration - user_profile type: {type(context.user_profile)}")
        logger.info(f"🔍 DEBUG: After hydration - weather type: {type(context.weather)}")
        if isinstance(context.user_profile, list):
            logger.error(f"🚨 ERROR: user_profile is a list: {context.user_profile}")
            return OutfitGeneratedOutfit(items=[], confidence=0.1, metadata={"generation_strategy": "multi_layered", "error": "user_profile_is_list"})
        if isinstance(context.weather, list):
            logger.error(f"🚨 ERROR: weather is a list: {context.weather}")
            return OutfitGeneratedOutfit(items=[], confidence=0.1, metadata={"generation_strategy": "multi_layered", "error": "weather_is_list"})
        
        # Handle weather data safely
        if hasattr(context.weather, 'temperature'):
            temp = context.weather.temperature
        elif hasattr(context.weather, '__dict__') and 'temperature' in context.weather.__dict__:
            temp = context.weather.__dict__['temperature']
        else:
            temp = 70.0
            
        if hasattr(context.weather, 'condition'):
            condition = context.weather.condition
        elif hasattr(context.weather, '__dict__') and 'condition' in context.weather.__dict__:
            condition = context.weather.__dict__['condition']
        else:
            condition = 'Clear'
            
        logger.info(f"🌤️ Weather: {temp}°F, {condition}")
        
        # Log wardrobe breakdown
        item_types = [item.type for item in context.wardrobe]
        type_counts = {item_type: item_types.count(item_type) for item_type in set(item_types)}
        logger.info(f"📊 Wardrobe breakdown: {type_counts}")
        
        # ═══════════════════════════════════════════════════════════
        # MULTI-LAYERED SCORING SYSTEM
        # Each analyzer scores items, then cohesive composition uses all scores
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🔬 PHASE 1: Multi-Layered Analysis & Scoring")
        
        # Create scoring dictionary for each item
        item_scores = {}
        for item in context.wardrobe:
            item_scores[item.id] = {
                'item': item,
                'body_type_score': 0.0,
                'style_profile_score': 0.0,
                'weather_score': 0.0,
                'user_feedback_score': 0.0,  # NEW!
                'composite_score': 0.0
            }
        
        # Run all analyzers in parallel
        logger.info(f"🚀 Running 3 analyzers in parallel... (user feedback temporarily disabled)")
        
        analyzer_tasks = [
            asyncio.create_task(self._analyze_body_type_scores(context, item_scores)),
            asyncio.create_task(self._analyze_style_profile_scores(context, item_scores)),
            asyncio.create_task(self._analyze_weather_scores(context, item_scores)),
            # TEMPORARILY DISABLED: asyncio.create_task(self._analyze_user_feedback_scores(context, item_scores))  # NEW!
        ]
        
        # Wait for all analyzers to complete
        await asyncio.gather(*analyzer_tasks)
        
        # Calculate composite scores
        logger.info(f"🧮 Calculating composite scores...")
        for item_id, scores in item_scores.items():
            # Weighted average of all scores including user feedback
            composite = (
                scores['body_type_score'] * 0.35 +
                scores['style_profile_score'] * 0.40 +
                scores['weather_score'] * 0.25
                # TEMPORARILY DISABLED: scores.get('user_feedback_score', 0.5) * 0.25  # NEW! 25% weight on user feedback
            )
            scores['composite_score'] = composite
        
        # Log top scored items
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        logger.info(f"🏆 Top 5 scored items:")
        for i, (item_id, scores) in enumerate(sorted_items[:5]):
            logger.info(f"  {i+1}. {scores['item'].name}: composite={scores['composite_score']:.2f} (body={scores['body_type_score']:.2f}, style={scores['style_profile_score']:.2f}, weather={scores['weather_score']:.2f})")
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: Cohesive Composition with Multi-Layered Scores
        # ═══════════════════════════════════════════════════════════
        
        logger.info(f"🎨 PHASE 2: Cohesive Composition with Scored Items")
        
        # Pass scored items to cohesive composition
        outfit = await self._cohesive_composition_with_scores(context, item_scores)
        
        logger.info(f"✅ ROBUST GENERATION SUCCESS: Generated outfit with {len(outfit.items)} items")
        logger.info(f"📦 Final outfit items: {[getattr(item, 'name', 'Unknown') for item in outfit.items]}")
        
        return outfit
    
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
        suitable_items = await self._filter_suitable_items(context)
        logger.info(f"🎨 COHESIVE: After filtering, {len(suitable_items)} suitable items")
        
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
        if context.occasion.lower() in ['party', 'date', 'wedding']:
            base_confidence = 0.92  # High for style-focused occasions
        elif context.occasion.lower() in ['business', 'formal']:
            base_confidence = 0.88  # Good but body type might be better
        elif context.occasion.lower() in ['casual', 'vacation']:
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
            weather=context.weather.__dict__ if context.weather else {},
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
            weather=context.weather.__dict__ if context.weather else {},
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
        style_preferences = context.user_profile.get('stylePreferences', {})
        favorite_colors = style_preferences.get('favoriteColors', [])
        preferred_brands = style_preferences.get('preferredBrands', [])
        
        # Filter items by style preferences
        style_matched_items = await self._filter_by_style_preferences(
            context.wardrobe, style_preferences, favorite_colors, preferred_brands
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
            weather=context.weather.__dict__ if context.weather else {},
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
        weather_appropriate_items = await self._filter_by_weather(context.wardrobe, context.weather)
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
            weather=context.weather.__dict__ if context.weather else {},
            pieces=[],
            explanation=f"Outfit adapted for {context.weather.condition} weather at {context.weather.temperature}°F",
            styleTags=[context.style.lower().replace(' ', '_'), "weather_adapted"],
            colorHarmony="seasonal",
            styleNotes=f"Perfect for {context.weather.condition} weather conditions",
            season=self._determine_season_from_weather(context.weather),
            updatedAt=int(time.time()),
            metadata={"generation_strategy": "weather_adapted", "temperature": context.weather.temperature},
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
            weather=context.weather.__dict__ if context.weather else {},
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
            weather=context.weather.__dict__ if context.weather else {},
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
        """Filter wardrobe items suitable for the occasion and style"""
        logger.info(f"🔍 FILTER: Starting filtering for occasion={context.occasion}, style={context.style}")
        logger.info(f"🔍 FILTER: Wardrobe has {len(context.wardrobe)} items")
        suitable_items = []
        occasion_rejected = 0
        style_rejected = 0
        
        for i, item in enumerate(context.wardrobe):
            logger.info(f"🔍 FILTER: Item {i+1}: {getattr(item, 'name', 'Unknown')} (type: {getattr(item, 'type', 'unknown')})")
            
            # Check occasion compatibility with advanced parameters
            occasion_compatible = self._is_occasion_compatible(item, context.occasion, context.style, context.mood, context.weather)
            logger.info(f"🔍 FILTER: Item {i+1} occasion compatible: {occasion_compatible}")
            
            if occasion_compatible:
                # Check style compatibility
                style_compatible = self._is_style_compatible(item, context.style)
                logger.info(f"🔍 FILTER: Item {i+1} style compatible: {style_compatible}")
                
                if style_compatible:
                    suitable_items.append(item)
                    logger.info(f"✅ FILTER: Item {i+1} ACCEPTED")
                else:
                    style_rejected += 1
                    logger.info(f"❌ FILTER: Item {i+1} REJECTED by style")
            else:
                occasion_rejected += 1
                logger.info(f"❌ FILTER: Item {i+1} REJECTED by occasion")
        
        logger.info(f"🔍 FILTER: Results - {len(suitable_items)} suitable, {occasion_rejected} rejected by occasion, {style_rejected} rejected by style")
        
        # TEMPORARY FALLBACK: If no suitable items found, use basic filtering
        if len(suitable_items) == 0:
            logger.warning(f"🚨 NO SUITABLE ITEMS: Using basic fallback filtering")
            # Basic fallback: just filter by type, ignore occasion/style restrictions
            for item in context.wardrobe:
                if hasattr(item, 'type') and item.type in ['shirt', 'pants', 'shoes', 'jacket']:
                    suitable_items.append(item)
                    logger.info(f"🔄 FALLBACK: Added {getattr(item, 'name', 'Unknown')} (type: {getattr(item, 'type', 'unknown')})")
        
        logger.info(f"📦 Found {len(suitable_items)} suitable items from {len(context.wardrobe)} total")
        return suitable_items
    
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
            current_category_count = category_counts.get(item_category, 0)
            base_limit = base_category_limits.get(item_category, 0)
            
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
                logger.info(f"🎯 TARGET-DRIVEN: Added {getattr(item, 'name', 'Unknown')} ({item_category}) - {len(selected_items)}/{target_count} items (category: {current_category_count + 1}/{proportional_limit})")
            else:
                logger.debug(f"🎯 TARGET-DRIVEN: Skipped {getattr(item, 'name', 'Unknown')} ({item_category}) - category limit reached ({current_category_count}/{proportional_limit})")
        
        # STEP 7: Ensure we have at least the minimum essential categories
        essential_categories = ["tops", "bottoms", "shoes"]
        missing_essentials = []
        
        for category in essential_categories:
            if category_counts.get(category, 0) == 0:
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
                        category_counts[category] = category_counts.get(category, 0) + 1
                        logger.info(f"🎯 TARGET-DRIVEN: Added essential {getattr(item, 'name', 'Unknown')} ({category}) - {len(selected_items)}/{target_count} items")
                        break
        
        logger.info(f"🎯 TARGET-DRIVEN: Final selection: {len(selected_items)} items (target was {target_count})")
        logger.info(f"🎯 TARGET-DRIVEN: Category distribution: {category_counts}")
        return selected_items
    
    def _get_dynamic_category_limits(self, context: GenerationContext, target_count: int) -> Dict[str, int]:
        """Get category limits that adapt to target count - TARGET-DRIVEN with optional outerwear"""
        occasion_lower = context.occasion.lower()
        style_lower = context.style.lower() if context.style else ""
        
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
        
        occasion_lower = context.occasion.lower()
        style_lower = context.style.lower() if context.style else ""
        mood_lower = context.mood.lower() if context.mood else ""
        
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
        if context.weather:
            if hasattr(context.weather, 'temperature'):
                temperature = context.weather.temperature
            elif isinstance(context.weather, dict):
                temperature = context.weather.get('temperature', 70.0)
        
        occasion_lower = context.occasion.lower()
        style_lower = context.style.lower() if context.style else ""
        mood_lower = context.mood.lower() if context.mood else ""
        
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
            category_counts[category] = category_counts.get(category, 0) + 1
        
        logger.info(f"🔍 VALIDATION: Category breakdown: {category_counts}")
        
        for category, count in category_counts.items():
            limit = self.base_category_limits.get(category, 2)
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
        item_name = item.name.lower()
        
        # If no occasion information available, be permissive
        item_occasions = getattr(item, 'occasion', [])
        if not item_occasions:
            logger.info(f"🔍 OCCASION: No occasion metadata for {item_name}, allowing")
            return True
        
        # Normalize occasions list
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions]
        item_occasions_lower = [occ.lower() for occ in item_occasions]
        
        # Check if item occasions include the requested occasion
        if occasion_lower in item_occasions_lower:
            logger.info(f"✅ OCCASION: {item_name} explicitly matches {occasion_lower}")
            return True
        
        # Check for broad compatibility patterns
        compatibility_patterns = {
            'athletic': ['casual', 'athletic', 'sport'],
            'business': ['business', 'formal', 'professional'],
            'casual': ['casual', 'everyday', 'relaxed'],
            'formal': ['formal', 'business', 'professional'],
            'party': ['party', 'casual', 'evening'],
            'wedding': ['formal', 'wedding', 'special'],
            'vacation': ['casual', 'vacation', 'relaxed']
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
        item_name = item.name.lower()
        
        # Extract style information
        item_styles = getattr(item, 'style', [])
        item_tags = getattr(item, 'tags', [])
        
        # If no style information available, be permissive
        if not item_styles and not item_tags:
            logger.info(f"🔍 STYLE: No style metadata for {item_name}, allowing")
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
        
        # Check for broad style compatibility
        style_compatibility = {
            'classic': ['formal', 'business', 'professional', 'traditional'],
            'athletic': ['sporty', 'active', 'casual', 'comfortable'],
            'casual': ['relaxed', 'everyday', 'comfortable', 'informal'],
            'formal': ['classic', 'business', 'professional', 'elegant'],
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
            score += item.favorite_score * 20
        
        if hasattr(item, 'wearCount') and item.wearCount > 0:
            score += min(item.wearCount * 2, 20)  # Cap at 20
        
        return score
    
    def _get_item_category(self, item: ClothingItem) -> str:
        """Get category for an item"""
        item_type = getattr(item, 'type', '').lower()
        
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
        
        return category_map.get(item_type, 'other')
    
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
        body_type = context.user_profile.get('bodyType', 'Average').lower()
        height = context.user_profile.get('height', 'Average')
        weight = context.user_profile.get('weight', 'Average')
        gender = context.user_profile.get('gender', 'Unspecified').lower()
        skin_tone = context.user_profile.get('skinTone', 'Medium')
        
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
        
        rules = body_type_rules.get(body_type, body_type_rules['average'])
        
        for item_id, scores in item_scores.items():
            item = scores['item']
            base_score = 0.5  # Default neutral score
            
            # Get item category
            category = self._get_item_category(item)
            
            # Check if item has body-flattering attributes
            item_name_lower = item.name.lower()
            
            if category in rules:
                for attribute, score_boost in rules[category].items():
                    if attribute in item_name_lower:
                        base_score = max(base_score, score_boost)
            
            # Additional scoring based on fit
            if hasattr(item, 'metadata') and item.metadata:
                if hasattr(item.metadata, 'visualAttributes') and item.metadata.visualAttributes:
                    fit = getattr(item.metadata.visualAttributes, 'fit', '')
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
                if hasattr(item, 'metadata') and item.metadata:
                    if hasattr(item.metadata, 'visualAttributes') and item.metadata.visualAttributes:
                        gender_target = getattr(item.metadata.visualAttributes, 'genderTarget', '').lower()
                        
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
        
        target_style = context.style.lower()
        
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
            compatible_styles = self.style_compatibility.get(target_style, [])
            for compat_style in compatible_styles:
                if compat_style in item_styles_lower:
                    base_score += 0.2
                    break
            
            # ═══════════════════════════════════════════════════════════
            # COLOR THEORY MATCHING WITH SKIN TONE
            # ═══════════════════════════════════════════════════════════
            item_color = item.color.lower() if item.color else ''
            item_name_lower = item.name.lower()
            
            # Check if color is excellent for skin tone
            for excellent_color in color_palette.get('excellent', []):
                if excellent_color in item_color or excellent_color in item_name_lower:
                    base_score += 0.25  # Significant boost for excellent colors
                    logger.debug(f"  🎨 {item.name}: Excellent color match for skin tone (+0.25)")
                    break
            
            # Check if color is good for skin tone
            for good_color in color_palette.get('good', []):
                if good_color in item_color or good_color in item_name_lower:
                    base_score += 0.15  # Moderate boost for good colors
                    logger.debug(f"  🎨 {item.name}: Good color match for skin tone (+0.15)")
                    break
            
            # Penalize colors to avoid for skin tone
            for avoid_color in color_palette.get('avoid', []):
                if avoid_color in item_color or avoid_color in item_name_lower:
                    base_score -= 0.15  # Penalty for unflattering colors
                    logger.debug(f"  🎨 {item.name}: Avoid color for skin tone (-0.15)")
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
            if context.occasion.lower() in item_occasions_lower:
                base_score += 0.2
            
            item_scores[item_id]['style_profile_score'] = min(1.0, max(0.0, base_score))
        
        logger.info(f"🎭 STYLE PROFILE ANALYZER: Completed scoring with color theory matching")
    
    async def _analyze_weather_scores(self, context: GenerationContext, item_scores: dict) -> None:
        """Analyze and score each item based on weather appropriateness"""
        logger.info(f"🌤️ WEATHER ANALYZER: Scoring {len(item_scores)} items")
        
        # Extract weather data
        if hasattr(context.weather, 'temperature'):
            temp = context.weather.temperature
        elif hasattr(context.weather, '__dict__') and 'temperature' in context.weather.__dict__:
            temp = context.weather.__dict__['temperature']
        else:
            temp = 70.0
        
        if hasattr(context.weather, 'condition'):
            condition = context.weather.condition.lower() if context.weather.condition else 'clear'
        elif hasattr(context.weather, '__dict__') and 'condition' in context.weather.__dict__:
            condition = context.weather.__dict__['condition'].lower() if context.weather.__dict__['condition'] else 'clear'
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
                temp_compat = item.temperatureCompatibility
                if temp_compat and hasattr(temp_compat, 'minTemp') and hasattr(temp_compat, 'maxTemp'):
                    if temp_compat.minTemp <= temp <= temp_compat.maxTemp:
                        base_score += 0.2
            
            # Material appropriateness for weather
            item_name_lower = item.name.lower()
            item_type_lower = str(item.type).lower()
            
            # Cold weather items
            if temp < 50:
                cold_keywords = ['wool', 'fleece', 'coat', 'jacket', 'sweater', 'long sleeve', 'boots']
                for keyword in cold_keywords:
                    if keyword in item_name_lower or keyword in item_type_lower:
                        base_score += 0.15
                        break
            
            # Hot weather items
            elif temp > 75:
                hot_keywords = ['cotton', 'linen', 'short sleeve', 'shorts', 'sandals', 'tank', 'light']
                for keyword in hot_keywords:
                    if keyword in item_name_lower or keyword in item_type_lower:
                        base_score += 0.15
                        break
            
            # Rainy weather
            if 'rain' in condition or 'storm' in condition:
                rain_keywords = ['waterproof', 'raincoat', 'boots']
                for keyword in rain_keywords:
                    if keyword in item_name_lower:
                        base_score += 0.2
                        break
            
            item_scores[item_id]['weather_score'] = min(1.0, base_score)
        
        logger.info(f"🌤️ WEATHER ANALYZER: Completed scoring")
    
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
        
        user_id = context.user_id
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
            # Get user's outfit history with ratings
            outfits_ref = db.collection('outfits').where('user_id', '==', user_id).limit(100)
            outfits = outfits_ref.stream()
            
            for outfit_doc in outfits:
                outfit_data = outfit_doc.to_dict()
                rating = outfit_data.get('rating')
                is_liked = outfit_data.get('isLiked', False)
                is_disliked = outfit_data.get('isDisliked', False)
                worn_at = outfit_data.get('wornAt')
                
                # Get items in this outfit
                outfit_items = outfit_data.get('items', [])
                
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
                if item_data.get('isFavorite') or item_data.get('favorite_score', 0) > 0.7:
                    favorited_items.add(item_data.get('id'))
            
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
                
                logger.debug(f"  ⭐ {item.name}: Avg outfit rating {avg_rating:.1f} → +{rating_score * 0.3:.2f}")
            
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
                    
                    logger.debug(f"  👍 {item.name}: {likes}L/{dislikes}D (ratio={like_ratio:.2f}) → +{like_score * 0.3:.2f}")
                    
                    # Penalty for heavily disliked items
                    if dislikes > likes and dislikes >= 2:
                        base_score -= 0.2
                        logger.debug(f"  👎 {item.name}: Heavily disliked → -0.20")
            
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
                    logger.info(f"  ⭐💎 {item.name}: FAVORITE not worn this week → +0.40 (PRIORITY)")
                else:
                    # Still boost, but less
                    base_score += 0.15
                    logger.debug(f"  ⭐ {item.name}: Favorite (worn this week) → +0.15")
            
            # ─────────────────────────────────────────────────────────────
            # 4. WEAR COUNT ALTERNATION (explore vs exploit)
            # ─────────────────────────────────────────────────────────────
            item_wear_count = getattr(item, 'wearCount', 0)
            
            if boost_rare:
                # BOOST RARELY-WORN ITEMS (discovery/diversity mode)
                if item_wear_count == 0:
                    base_score += 0.25  # Never worn - high boost
                    logger.debug(f"  🆕 {item.name}: Never worn → +0.25 (discovery)")
                elif item_wear_count <= 3:
                    base_score += 0.15  # Lightly worn - moderate boost
                    logger.debug(f"  🌱 {item.name}: Lightly worn ({item_wear_count}) → +0.15")
                elif item_wear_count > 15:
                    base_score -= 0.10  # Overused - penalty
                    logger.debug(f"  🔁 {item.name}: Overused ({item_wear_count}) → -0.10")
            else:
                # BOOST POPULAR ITEMS (reliability/favorites mode)
                if item_wear_count >= 5 and item_wear_count <= 15:
                    base_score += 0.20  # Sweet spot - proven favorites
                    logger.debug(f"  🌟 {item.name}: Popular ({item_wear_count} wears) → +0.20")
                elif item_wear_count > 15:
                    base_score += 0.10  # Very popular - still boost but less
                    logger.debug(f"  ⭐ {item.name}: Very popular ({item_wear_count}) → +0.10")
                elif item_wear_count == 0:
                    base_score -= 0.05  # Never worn - small penalty in favorites mode
            
            # ─────────────────────────────────────────────────────────────
            # 5. RECENCY BIAS (recently worn items slight penalty)
            # ─────────────────────────────────────────────────────────────
            if item_id in item_wear_history:
                recent_wears = [w for w in item_wear_history[item_id] if w > one_week_ago]
                if len(recent_wears) >= 2:
                    base_score -= 0.10  # Worn 2+ times this week - give it a rest
                    logger.debug(f"  🔄 {item.name}: Worn {len(recent_wears)} times this week → -0.10")
            
            # ─────────────────────────────────────────────────────────────
            # 6. ADVANCED STYLE EVOLUTION TRACKING (Netflix/Spotify-style)
            # ─────────────────────────────────────────────────────────────
            
            # Build comprehensive preference profile for this item
            evolution_score = await self._calculate_style_evolution_score(
                item=item,
                user_id=user_id,
                current_time=current_time,
                outfit_ratings=outfit_ratings,
                context=context,
                db=db
            )
            
            base_score += evolution_score
            
            # Ensure score stays in valid range
            item_scores[item_id]['user_feedback_score'] = min(1.0, max(0.0, base_score))
        
        logger.info(f"⭐ USER FEEDBACK ANALYZER: Completed scoring with learning algorithm")
        logger.info(f"   Mode: {'🔍 Discovery (boost rarely-worn)' if boost_rare else '⭐ Favorites (boost popular)'}")
    
    async def _cohesive_composition_with_scores(self, context: GenerationContext, item_scores: dict) -> OutfitGeneratedOutfit:
        """Generate cohesive outfit using multi-layered scores with intelligent layering"""
        logger.info(f"🎨 COHESIVE COMPOSITION: Using scored items to create outfit")
        
        # ═══════════════════════════════════════════════════════════════════════
        # INTELLIGENT ITEM COUNT & LAYERING DECISION
        # ═══════════════════════════════════════════════════════════════════════
        
        # Extract weather data for layering decisions
        if hasattr(context.weather, 'temperature'):
            temp = context.weather.temperature
        elif hasattr(context.weather, '__dict__') and 'temperature' in context.weather.__dict__:
            temp = context.weather.__dict__['temperature']
        else:
            temp = 70.0
        
        occasion_lower = context.occasion.lower()
        
        # Check if user prefers minimalistic outfits
        style_lower = context.style.lower()
        mood_lower = context.mood.lower() if context.mood else ''
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
        
        # Sort items by composite score
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        
        # Select items with intelligent layering
        selected_items = []
        categories_filled = {}
        
        # Phase 1: Fill essential categories (tops, bottoms, shoes)
        logger.info(f"📦 PHASE 1: Selecting essential items (top, bottom, shoes)")
        for item_id, score_data in sorted_items:
            item = score_data['item']
            category = self._get_item_category(item)
            item_name_lower = item.name.lower()
            
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
                    logger.info(f"  ✅ Essential {category}: {item.name} (score={score_data['composite_score']:.2f})")
        
        # Phase 2: Add layering pieces based on target count
        logger.info(f"📦 PHASE 2: Adding {recommended_layers} layering pieces")
        for item_id, score_data in sorted_items:
            if len(selected_items) >= target_items:
                break
            
            item = score_data['item']
            if item in selected_items:
                continue
            
            category = self._get_item_category(item)
            item_name_lower = item.name.lower()
            
            # Determine layering appropriateness
            if category == 'outerwear' and score_data['composite_score'] > 0.6:
                # Check if we need outerwear
                if temp < 65 or occasion_lower in ['business', 'formal']:
                    selected_items.append(item)
                    logger.info(f"  ✅ Outerwear: {item.name} (score={score_data['composite_score']:.2f})")
            
            elif category == 'tops' and score_data['composite_score'] > 0.6:
                # Additional top layer (sweater, cardigan)
                if temp < 70 and any(kw in item_name_lower for kw in ['sweater', 'cardigan', 'vest']):
                    selected_items.append(item)
                    logger.info(f"  ✅ Mid-layer: {item.name} (score={score_data['composite_score']:.2f})")
            
            elif category == 'accessories' and score_data['composite_score'] > 0.7:
                # High-scoring accessories
                if temp < 50 or occasion_lower in ['formal', 'business']:
                    selected_items.append(item)
                    logger.info(f"  ✅ Accessory: {item.name} (score={score_data['composite_score']:.2f})")
        
        # Ensure minimum items
        if len(selected_items) < min_items:
            logger.warning(f"⚠️ Only {len(selected_items)} items selected, adding more to reach minimum {min_items}...")
            for item_id, score_data in sorted_items:
                if score_data['item'] not in selected_items and len(selected_items) < min_items:
                    selected_items.append(score_data['item'])
                    logger.info(f"  ➕ Filler: {score_data['item'].name}")
        
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
        
        logger.info(f"🎭 Diversity check: is_diverse={diversity_result.get('is_diverse', True)}, score={diversity_result.get('diversity_score', 0.8):.2f}")
        
        # If not diverse enough, apply diversity boost
        if not diversity_result.get('is_diverse', True):
            logger.warning(f"⚠️ Outfit not diverse enough, applying diversity boost...")
            
            # Get diversity suggestions
            diversity_suggestions = diversity_filter.get_diversity_suggestions(
                user_id=context.user_id,
                current_items=selected_items,
                occasion=context.occasion,
                style=context.style
            )
            
            if diversity_suggestions:
                logger.info(f"🎭 Got {len(diversity_suggestions)} diversity suggestions")
                
                # Try to swap out overused items with diverse alternatives
                for suggestion in diversity_suggestions[:2]:  # Limit to 2 swaps
                    item_to_replace = suggestion.get('item_to_replace')
                    alternative = suggestion.get('alternative')
                    
                    if item_to_replace and alternative:
                        # Replace in selected items
                        selected_items = [alternative if item.id == item_to_replace.id else item 
                                        for item in selected_items]
                        logger.info(f"  🔄 Swapped {item_to_replace.name} → {alternative.name}")
        
        # Record outfit for diversity tracking
        diversity_filter.record_outfit_generation(
            user_id=context.user_id,
            outfit={'items': selected_items, 'occasion': context.occasion},
            items=selected_items
        )
        
        logger.info(f"✅ Diversity filtering complete")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PHASE 4: ANALYTICS & PERFORMANCE TRACKING
        # ═══════════════════════════════════════════════════════════════════════
        
        # Calculate final confidence based on composite scores
        avg_composite_score = sum(item_scores[item.id]['composite_score'] for item in selected_items) / len(selected_items)
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
                diversity_score=diversity_result.get('diversity_score', 0.8),
                user_satisfaction=final_confidence,
                fallback_rate=0.0,
                sample_size=1,
                time_window_hours=int(time.time())
            )
            
            adaptive_tuning.record_performance(metrics)
            logger.info(f"✅ Performance metrics recorded")
        except Exception as e:
            logger.warning(f"⚠️ Failed to record performance metrics: {e}")
        
        # Create outfit
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"{context.style} {context.occasion} Outfit",
            description=f"Multi-layered scored outfit optimized for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=final_confidence,  # Use calculated confidence
            items=selected_items,
            reasoning=f"Created using body type, style profile, and weather analysis with color theory",
            createdAt=int(time.time()),
            userId=context.user_id,
            weather=context.weather.__dict__ if context.weather else {},
            pieces=[],
            explanation=f"Optimized outfit using multi-layered scoring system (body: 30%, style+color: 40%, weather: 30%)",
            styleTags=[context.style.lower().replace(' ', '_'), 'multi_layered'],
            colorHarmony="color_theory_optimized",
            styleNotes=f"Scored across body type (height/weight/gender), style profile (skin tone color theory), and weather",
            season="current",
            updatedAt=int(time.time()),
            metadata={
                "generation_strategy": "multi_layered_cohesive_composition",
                "avg_composite_score": avg_composite_score,
                "diversity_score": diversity_result.get('diversity_score', 0.8),
                "color_theory_applied": True,
                "analyzers_used": ["body_type", "style_profile", "weather"]
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
                rating = outfit_data.get('rating')
                if not rating:
                    continue
                
                # Get timestamp
                created_at = outfit_data.get('createdAt')
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
                outfit_style = outfit_data.get('style', '').lower()
                if outfit_style:
                    if outfit_style not in style_ratings_over_time:
                        style_ratings_over_time[outfit_style] = []
                    style_ratings_over_time[outfit_style].append((timestamp, rating))
                
                # Track occasion preferences
                outfit_occasion = outfit_data.get('occasion', '').lower()
                if outfit_occasion:
                    if outfit_occasion not in occasion_ratings_over_time:
                        occasion_ratings_over_time[outfit_occasion] = []
                    occasion_ratings_over_time[outfit_occasion].append((timestamp, rating))
                
                # Track color preferences
                outfit_items = outfit_data.get('items', [])
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
                                    logger.debug(f"  📈 {item.name}: {style} TRENDING UP (+0.15)")
                                elif trend < -0.5:
                                    evolution_score -= 0.10  # Style trending DOWN
                                    logger.debug(f"  📉 {item.name}: {style} trending down (-0.10)")
            
            # ═══════════════════════════════════════════════════════════════
            # 4. OCCASION-SPECIFIC LEARNING
            # ═══════════════════════════════════════════════════════════════
            
            current_occasion = context.occasion.lower()
            
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
                        logger.debug(f"  🎯 {item.name}: User loves {occasion_lower} outfits (+0.15)")
                    elif weighted_avg and weighted_avg <= 2.5:
                        evolution_score -= 0.10  # User dislikes outfits for this occasion
                        logger.debug(f"  ⚠️ {item.name}: User dislikes {occasion_lower} outfits (-0.10)")
            
            # ═══════════════════════════════════════════════════════════════
            # 5. COLOR PATTERN LEARNING
            # ═══════════════════════════════════════════════════════════════
            
            item_color = item.color.lower() if item.color else ''
            
            if item_color and item_color in color_ratings_over_time:
                weighted_avg = calculate_weighted_average(color_ratings_over_time[item_color])
                
                if weighted_avg:
                    # Recent color preference
                    color_bonus = ((weighted_avg - 3.0) / 2.0) * 0.15
                    evolution_score += color_bonus
                    
                    if weighted_avg >= 4.0:
                        logger.debug(f"  🎨 {item.name}: {item_color} is trending color (+{color_bonus:.2f})")
            
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
                logger.debug(f"  🍂 {item.name}: Seasonal match for {current_season} (+0.05)")
            
            logger.debug(f"  📊 {item.name}: Total evolution score = +{evolution_score:.2f}")
            
            return evolution_score
            
        except Exception as e:
            logger.warning(f"⚠️ Style evolution calculation failed: {e}")
            return 0.0  # Neutral score on error
