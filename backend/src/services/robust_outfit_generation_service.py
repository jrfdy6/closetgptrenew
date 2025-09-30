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
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..custom_types.wardrobe import ClothingItem
from ..custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from .robust_hydrator import ensure_items_safe_for_pydantic
from .strategy_analytics_service import strategy_analytics, StrategyStatus
from .diversity_filter_service import diversity_filter
from .adaptive_tuning_service import adaptive_tuning, PerformanceMetrics

logger = logging.getLogger(__name__)

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
        """Generate an outfit with comprehensive validation and fallback strategies"""
        logger.info(f"🎨 Starting robust outfit generation for user {context.user_id}")
        logger.info(f"📋 Context: {context.occasion}, {context.style}, {context.mood}")
        logger.info(f"📦 Wardrobe size: {len(context.wardrobe)} items")
        
        # STRESS TEST: Comprehensive logging for robust generator failure analysis
        logger.error(f"🚨 STRESS TEST v1.0: ROBUST GENERATOR START - User: {context.user_id}")
        logger.error(f"🚨 STRESS TEST v1.0: Context - Occasion: {context.occasion}, Style: {context.style}, Mood: {context.mood}")
        logger.error(f"🚨 STRESS TEST v1.0: Wardrobe size: {len(context.wardrobe)} items")
        
        # Log first few wardrobe items for analysis
        if context.wardrobe:
            logger.error(f"🚨 STRESS TEST v1.0: First wardrobe item keys: {list(context.wardrobe[0].keys()) if isinstance(context.wardrobe[0], dict) else 'Not a dict'}")
            logger.error(f"🚨 STRESS TEST v1.0: First wardrobe item type: {type(context.wardrobe[0])}")
            if isinstance(context.wardrobe[0], dict):
                logger.error(f"🚨 STRESS TEST v1.0: First item sample: {dict(list(context.wardrobe[0].items())[:5])}")
        
        # Safety-net hydration at start of pipeline
        logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR START - Processing {len(context.wardrobe)} items")
        try:
            if isinstance(context.wardrobe, list) and len(context.wardrobe) > 0 and isinstance(context.wardrobe[0], dict):
                logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR - Calling ensure_items_safe_for_pydantic")
                # Convert raw wardrobe items to ClothingItem objects with safety net
                safe_wardrobe = ensure_items_safe_for_pydantic(context.wardrobe)
                logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR SUCCESS - {len(safe_wardrobe)} items validated")
                
                # Log sample of hydrated items
                if safe_wardrobe:
                    logger.error(f"🚨 STRESS TEST v1.0: HYDRATED ITEM SAMPLE - Type: {type(safe_wardrobe[0])}")
                    logger.error(f"🚨 STRESS TEST v1.0: HYDRATED ITEM FIELDS - {list(safe_wardrobe[0].__dict__.keys()) if hasattr(safe_wardrobe[0], '__dict__') else 'No __dict__'}")
                
                # Update context with safe wardrobe
                context.wardrobe = safe_wardrobe
            else:
                logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR SKIP - Items already ClothingItem objects")
        except Exception as hydrator_error:
            logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR FAILURE - {hydrator_error}")
            logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR TRACEBACK - {hydrator_error.__class__.__name__}: {str(hydrator_error)}")
            import traceback
            logger.error(f"🚨 STRESS TEST v1.0: HYDRATOR FULL TRACEBACK - {traceback.format_exc()}")
        
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
        
        # Log wardrobe item types for debugging
        item_types = [item.type for item in context.wardrobe]
        type_counts = {item_type: item_types.count(item_type) for item_type in set(item_types)}
        logger.info(f"📊 Wardrobe breakdown: {type_counts}")
        
        # Get current tuned parameters
        tuned_params = adaptive_tuning.get_current_parameters()
        confidence_threshold = tuned_params.get('confidence_threshold', 0.6)
        max_items = int(tuned_params.get('max_items_per_outfit', 6))
        min_items = int(tuned_params.get('min_items_per_outfit', 3))
        
        logger.info(f"🎛️ Using tuned parameters: confidence={confidence_threshold:.2f}, items={min_items}-{max_items}")
        
        # Try each generation strategy in order
        logger.info(f"🔄 Available strategies: {[s.value for s in self.generation_strategies]}")
        session_id = f"session_{int(time.time())}_{context.user_id}"
        
        # STRESS TEST: Strategy execution loop with detailed logging
        logger.error(f"🚨 STRESS TEST v1.0: STRATEGY LOOP START - {len(self.generation_strategies)} strategies")
        
        for i, strategy in enumerate(self.generation_strategies):
            strategy_start_time = time.time()
            validation_start_time = 0
            validation_time = 0
            generation_time = 0
            
            logger.error(f"🚨 STRESS TEST v1.0: STRATEGY {i+1}/{len(self.generation_strategies)} - {strategy.value}")
            
            try:
                logger.info(f"🔄 Trying generation strategy: {strategy.value}")
                logger.error(f"🚨 STRESS TEST v1.0: STRATEGY {strategy.value} EXECUTION START")
                context.generation_strategy = strategy
                
                # Log strategy-specific context
                logger.info(f"🔍 Strategy {strategy.value} - Starting generation...")
                logger.error(f"🚨 STRESS TEST v1.0: CALLING _generate_with_strategy for {strategy.value}")
                outfit = await self._generate_with_strategy(context)
                generation_time = time.time() - strategy_start_time
                logger.info(f"🔍 Strategy {strategy.value} - Generated outfit with {len(outfit.items)} items")
                logger.error(f"🚨 STRESS TEST v1.0: STRATEGY {strategy.value} GENERATION COMPLETE - {generation_time:.3f}s, {len(outfit.items)} items")
                
                # Validate the generated outfit
                validation_start_time = time.time()
                logger.info(f"🔍 Strategy {strategy.value} - Starting validation...")
                logger.error(f"🚨 STRESS TEST v1.0: VALIDATION START for {strategy.value}")
                validation = await self._validate_outfit(outfit, context)
                validation_time = time.time() - validation_start_time
                logger.info(f"🔍 Strategy {strategy.value} - Validation complete: valid={validation.is_valid}, confidence={validation.confidence}")
                logger.error(f"🚨 STRESS TEST v1.0: VALIDATION COMPLETE - {validation_time:.3f}s, Valid: {validation.is_valid}, Confidence: {validation.confidence:.2f}")
                logger.error(f"🚨 STRESS TEST v1.0: VALIDATION ISSUES - {validation.issues}")
                
                # ENHANCED STRATEGY ANALYTICS TRACKING
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
                
                # PER-STRATEGY LOGGING
                strategy_name = strategy.value.upper()
                logger.info(f"[{strategy_name}] Items selected: {len(outfit.items)}")
                logger.info(f"[{strategy_name}] Confidence: {validation.confidence}")
                logger.info(f"[{strategy_name}] Validation: valid={validation.is_valid}, score={validation.score}")
                logger.info(f"[{strategy_name}] Issues: {validation.issues}")
                logger.info(f"[{strategy_name}] Suggestions: {validation.suggestions}")
                logger.info(f"[{strategy_name}] Timing: {generation_time:.3f}s generation, {validation_time:.3f}s validation")
                
                # Use adaptive confidence threshold
                # confidence_threshold is already set from tuned parameters above
                
                if validation.is_valid and validation.confidence >= confidence_threshold:
                    logger.error(f"🚨 STRESS TEST v1.0: STRATEGY SUCCESS - {strategy.value} passed validation!")
                    logger.error(f"🚨 STRESS TEST v1.0: SUCCESS CRITERIA - Valid: {validation.is_valid}, Confidence: {validation.confidence:.2f} >= {confidence_threshold}")
                    
                    # Apply diversity filtering
                    logger.error(f"🚨 STRESS TEST v1.0: DIVERSITY CHECK START for {strategy.value}")
                    diversity_result = diversity_filter.check_outfit_diversity(
                        user_id=context.user_id,
                        new_outfit=outfit.items,
                        occasion=context.occasion,
                        style=context.style,
                        mood=context.mood
                    )
                    logger.error(f"🚨 STRESS TEST v1.0: DIVERSITY CHECK COMPLETE - Diverse: {diversity_result['is_diverse']}, Score: {diversity_result['diversity_score']:.2f}")
                    
                    logger.info(f"🎭 Diversity check: diverse={diversity_result['is_diverse']}, score={diversity_result['diversity_score']:.2f}")
                    
                    if not diversity_result['is_diverse']:
                        logger.warning(f"⚠️ Outfit not diverse enough, trying diversity boost")
                        
                        # Apply diversity boost to items
                        boosted_items = diversity_filter.apply_diversity_boost(
                            items=outfit.items,
                            user_id=context.user_id,
                            occasion=context.occasion,
                            style=context.style,
                            mood=context.mood
                        )
                        
                        # Re-select items with diversity boost
                        if boosted_items:
                            # Sort by diversity score and take top items
                            boosted_items.sort(key=lambda x: x[1], reverse=True)
                            diverse_items = [item for item, score in boosted_items[:len(outfit.items)]]
                            
                            # Update outfit with diverse items
                            outfit.items = diverse_items
                            
                            # Re-validate with diverse items
                            validation = await self._validate_outfit(outfit, context)
                            logger.info(f"🎭 Re-validated with diverse items: valid={validation.is_valid}, confidence={validation.confidence}")
                    
                    logger.info(f"✅ Successfully generated outfit with strategy {strategy.value}")
                    logger.info(f"📊 Validation score: {validation.score}, Confidence: {validation.confidence}")
                    logger.info(f"📦 Final outfit items: {[item.name for item in outfit.items]}")
                    
                    # Record outfit for diversity tracking
                    diversity_filter.record_outfit_generation(
                        user_id=context.user_id,
                        outfit=outfit.__dict__,
                        items=outfit.items
                    )
                    
                    # Record performance metrics for adaptive tuning
                    self._record_generation_performance(
                        context=context,
                        strategy=strategy.value,
                        success=True,
                        confidence=validation.confidence,
                        generation_time=generation_time,
                        validation_time=validation_time,
                        items_selected=len(outfit.items),
                        diversity_score=diversity_result['diversity_score']
                    )
                    
                    return outfit
                else:
                    logger.warning(f"⚠️ Strategy {strategy.value} failed validation: {validation.issues}")
                    logger.warning(f"⚠️ Validation details: valid={validation.is_valid}, confidence={validation.confidence}, score={validation.score}")
                    logger.warning(f"⚠️ Confidence threshold not met: {validation.confidence} < {confidence_threshold}")
                    
                    # Record failed attempt
                    self._record_generation_performance(
                        context=context,
                        strategy=strategy.value,
                        success=False,
                        confidence=validation.confidence,
                        generation_time=generation_time,
                        validation_time=validation_time,
                        items_selected=len(outfit.items),
                        diversity_score=0.0
                    )
                    
                    if strategy == GenerationStrategy.EMERGENCY_DEFAULT:
                        # If even emergency default fails, return it anyway
                        logger.error(f"🚨 All generation strategies failed, returning emergency default")
                        return outfit
                        
            except Exception as e:
                generation_time = time.time() - strategy_start_time
                logger.error(f"❌ Strategy {strategy.value} failed with error: {e}", exc_info=True)
                logger.error(f"❌ Strategy {strategy.value} error context: user={context.user_id}, occasion={context.occasion}")
                logger.error(f"🚨 STRESS TEST v1.0: STRATEGY CRASH - {strategy.value} crashed with {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"🚨 STRESS TEST v1.0: STRATEGY CRASH TRACEBACK - {traceback.format_exc()}")
                
                # Track strategy failure
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
                continue
        
        # This should never be reached due to emergency default
        raise Exception("All outfit generation strategies failed")
    
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
        
        # AGGRESSIVE COMPLETENESS CHECK - Force complete outfits
        if len(complete_outfit) < 3:
            logger.warning(f"⚠️ COHESIVE: Outfit incomplete ({len(complete_outfit)} items), forcing completion")
            complete_outfit = await self._force_complete_outfit(context.wardrobe, context)
        
        # Create outfit response
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"{context.style} {context.occasion} Outfit",
            description=f"Carefully curated {context.style} outfit optimized for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.95,
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
        
        # Get user's body type information
        body_type = context.user_profile.get('bodyType', 'average')
        height = context.user_profile.get('height', 'average')
        
        # Filter items based on body type compatibility
        suitable_items = await self._filter_by_body_type(context.wardrobe, body_type, height)
        
        # Apply body type optimization rules
        optimized_items = await self._apply_body_type_optimization(suitable_items, body_type, height)
        
        # Create outfit with body type considerations
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Body-Optimized {context.style} Outfit",
            description=f"Body-optimized {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.90,
            items=optimized_items,
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
        
        # Get user's style preferences
        style_preferences = context.user_profile.get('stylePreferences', {})
        favorite_colors = style_preferences.get('favoriteColors', [])
        preferred_brands = style_preferences.get('preferredBrands', [])
        
        # Filter items by style preferences
        style_matched_items = await self._filter_by_style_preferences(
            context.wardrobe, style_preferences, favorite_colors, preferred_brands
        )
        
        # Create outfit with style profile matching
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Style-Matched {context.style} Outfit",
            description=f"Style-matched {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.88,
            items=style_matched_items,
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
        
        # Filter items based on weather
        weather_appropriate_items = await self._filter_by_weather(context.wardrobe, context.weather)
        
        # Create weather-appropriate outfit
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"Weather-Adapted {context.style} Outfit",
            description=f"Weather-adapted {context.style} outfit for {context.occasion}",
            occasion=context.occasion,
            style=context.style,
            mood=context.mood,
            confidence=0.92,
            items=weather_appropriate_items,
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
        suitable_items = []
        occasion_rejected = 0
        style_rejected = 0
        
        for item in context.wardrobe:
            # Check occasion compatibility
            if self._is_occasion_compatible(item, context.occasion):
                # Check style compatibility
                if self._is_style_compatible(item, context.style):
                    suitable_items.append(item)
                else:
                    style_rejected += 1
            else:
                occasion_rejected += 1
        
        logger.info(f"🔍 FILTER: Results - {len(suitable_items)} suitable, {occasion_rejected} rejected by occasion, {style_rejected} rejected by style")
        
        # SAFETY NET: Prevent empty filtered lists
        if len(suitable_items) == 0:
            logger.warning(f"🚨 SAFETY NET: No suitable items found, falling back to occasion-appropriate items")
            # Fall back to occasion-appropriate items only (skip style filtering)
            for item in context.wardrobe:
                if self._is_occasion_compatible(item, context.occasion):
                    suitable_items.append(item)
            
            if len(suitable_items) == 0:
                logger.warning(f"🚨 SAFETY NET: Still no occasion-appropriate items, using all items")
                # Last resort: use all items
                suitable_items = context.wardrobe[:]
        
        logger.info(f"📦 Found {len(suitable_items)} suitable items from {len(context.wardrobe)} total")
        return suitable_items
    
    async def _intelligent_item_selection(self, suitable_items: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Intelligently select items with TARGET-DRIVEN sizing and proportional category balancing"""
        selected_items = []
        
        # SAFETY NET: Ensure we have items to work with
        if len(suitable_items) == 0:
            logger.warning(f"🚨 SAFETY NET: No suitable items for intelligent selection, using all wardrobe items")
            suitable_items = context.wardrobe[:]
        
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
        """Ensure outfit has essential categories and is complete"""
        # Check for essential categories
        categories_present = set(self._get_item_category(item) for item in items)
        essential_categories = {"tops", "bottoms", "shoes"}
        
        missing_categories = essential_categories - categories_present
        
        # If missing essential categories, try to add them
        if missing_categories:
            logger.warning(f"⚠️ Missing essential categories: {missing_categories}")
            # Try to find items for missing categories
            for category in missing_categories:
                category_item = await self._find_item_for_category(context.wardrobe, category)
                if category_item:
                    items.append(category_item)
        
        # Final validation
        if len(items) < self.min_items:
            logger.warning(f"⚠️ Outfit has only {len(items)} items, minimum is {self.min_items}")
            # Add more items if needed
            while len(items) < self.min_items:
                additional_item = await self._find_additional_item(context.wardrobe, items)
                if additional_item:
                    items.append(additional_item)
                else:
                    break
        
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
    
    def _is_occasion_compatible(self, item: ClothingItem, occasion: str) -> bool:
        """Check if item is compatible with occasion"""
        item_occasions = getattr(item, 'occasion', [])
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions]
        
        return occasion.lower() in [occ.lower() for occ in item_occasions]
    
    def _is_style_compatible(self, item: ClothingItem, style: str) -> bool:
        """Check if item is compatible with style"""
        item_styles = getattr(item, 'style', [])
        if isinstance(item_styles, str):
            item_styles = [item_styles]
        
        return style.lower() in [s.lower() for s in item_styles]
    
    async def _calculate_item_score(self, item: ClothingItem, context: GenerationContext) -> float:
        """Calculate preference score for item with formal occasion prioritization"""
        score = 50.0  # Base score
        
        # COMPREHENSIVE: Occasion-based prioritization for ALL occasions
        occasion_lower = context.occasion.lower()
        item_name = getattr(item, 'name', '').lower()
        item_type = getattr(item, 'type', '').lower()
        
        # FORMAL OCCASIONS (Business, Formal, Interview)
        if any(formal_term in occasion_lower for formal_term in ['formal', 'business', 'interview']):
            # Prioritize formal shoes (dress shoes, oxfords, loafers)
            if any(formal_shoe in item_name or formal_shoe in item_type for formal_shoe in [
                'dress shoe', 'oxford', 'loafer', 'derby', 'wingtip', 'brogue', 'dress boot'
            ]):
                score += 100.0  # MASSIVE priority for formal shoes
                logger.info(f"🎯 FORMAL PRIORITY: Boosting formal shoes: {item_name}")
            
            # Prioritize formal tops (dress shirts, blazers)
            elif any(formal_top in item_name or formal_top in item_type for formal_top in [
                'dress shirt', 'button down', 'button-up', 'blazer', 'suit jacket', 'sport coat'
            ]):
                score += 80.0  # High priority for formal tops
                logger.info(f"🎯 FORMAL PRIORITY: Boosting formal tops: {item_name}")
            
            # Prioritize formal bottoms (dress pants, suit pants)
            elif any(formal_bottom in item_name or formal_bottom in item_type for formal_bottom in [
                'dress pant', 'suit pant', 'trouser', 'slack', 'formal pant'
            ]):
                score += 70.0  # High priority for formal bottoms
                logger.info(f"🎯 FORMAL PRIORITY: Boosting formal bottoms: {item_name}")
            
            # Penalize casual items on formal occasions
            elif any(casual_term in item_name or casual_term in item_type for casual_term in [
                'sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs',
                't-shirt', 'tank', 'jersey', 'basketball', 'sport', 'hoodie', 'sweatpants'
            ]):
                score -= 50.0  # Heavy penalty for casual items
                logger.info(f"🎯 FORMAL PENALTY: Penalizing casual item: {item_name}")
        
        # ATHLETIC OCCASIONS (Athletic, Gym, Workout, Sport)
        elif any(athletic_term in occasion_lower for athletic_term in ['athletic', 'gym', 'workout', 'sport']):
            # Prioritize athletic items
            if any(athletic_term in item_name or athletic_term in item_type for athletic_term in [
                'sneaker', 'athletic', 'sport', 'gym', 'workout', 'jersey', 'tank', 'shorts'
            ]):
                score += 60.0  # High priority for athletic items
                logger.info(f"🎯 ATHLETIC PRIORITY: Boosting athletic item: {item_name}")
            
            # Penalize formal items on athletic occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'blazer', 'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 40.0  # Penalty for formal items
                logger.info(f"🎯 ATHLETIC PENALTY: Penalizing formal item: {item_name}")
        
        # PARTY OCCASIONS (Party, Night Out, Club)
        elif any(party_term in occasion_lower for party_term in ['party', 'night out', 'club']):
            # Prioritize stylish/trendy items
            if any(party_term in item_name or party_term in item_type for party_term in [
                'party', 'dress', 'blouse', 'top', 'heels', 'boot', 'jacket', 'blazer'
            ]):
                score += 50.0  # High priority for party items
                logger.info(f"🎯 PARTY PRIORITY: Boosting party item: {item_name}")
            
            # Penalize work/athletic items on party occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'work', 'business', 'professional', 'athletic', 'gym', 'sport', 'sweatpants'
            ]):
                score -= 30.0  # Penalty for inappropriate items
                logger.info(f"🎯 PARTY PENALTY: Penalizing inappropriate item: {item_name}")
        
        # DATE OCCASIONS (Date, Romantic)
        elif any(date_term in occasion_lower for date_term in ['date', 'romantic']):
            # Prioritize elegant/romantic items
            if any(date_term in item_name or date_term in item_type for date_term in [
                'dress', 'blouse', 'button down', 'blazer', 'jacket', 'heels', 'boot'
            ]):
                score += 45.0  # High priority for date items
                logger.info(f"🎯 DATE PRIORITY: Boosting date item: {item_name}")
            
            # Penalize athletic/casual items on date occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'athletic', 'gym', 'sport', 'sweatpants', 'hoodie', 'sneaker', 'canvas'
            ]):
                score -= 35.0  # Penalty for inappropriate items
                logger.info(f"🎯 DATE PENALTY: Penalizing inappropriate item: {item_name}")
        
        # WEEKEND OCCASIONS (Weekend, Casual)
        elif any(weekend_term in occasion_lower for weekend_term in ['weekend', 'casual']):
            # Prioritize casual/comfortable items
            if any(weekend_term in item_name or weekend_term in item_type for weekend_term in [
                'casual', 'jeans', 'sneaker', 't-shirt', 'sweater', 'hoodie', 'jacket'
            ]):
                score += 40.0  # High priority for weekend items
                logger.info(f"🎯 WEEKEND PRIORITY: Boosting weekend item: {item_name}")
            
            # Penalize formal items on weekend occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 25.0  # Penalty for formal items
                logger.info(f"🎯 WEEKEND PENALTY: Penalizing formal item: {item_name}")
        
        # LOUNGEWEAR OCCASIONS (Loungewear, Relaxed)
        elif any(lounge_term in occasion_lower for lounge_term in ['loungewear', 'relaxed', 'lounge']):
            # Prioritize comfortable/loungewear items
            if any(lounge_term in item_name or lounge_term in item_type for lounge_term in [
                'sweat', 'hoodie', 't-shirt', 'jogger', 'lounge', 'pajama', 'comfortable', 'soft'
            ]):
                score += 50.0  # High priority for loungewear items
                logger.info(f"🎯 LOUNGE PRIORITY: Boosting loungewear item: {item_name}")
            
            # Penalize formal/structured items on loungewear occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'blazer', 'suit', 'dress pant', 'oxford', 'heels', 'loafer', 'jeans', 'denim'
            ]):
                score -= 40.0  # Penalty for inappropriate items
                logger.info(f"🎯 LOUNGE PENALTY: Penalizing inappropriate item: {item_name}")
        
        # Style match bonus
        if self._is_style_compatible(item, context.style):
            score += 20.0
        
        # Occasion match bonus
        if self._is_occasion_compatible(item, context.occasion):
            score += 15.0
        
        # Favorite score bonus
        favorite_score = getattr(item, 'favorite_score', 0.0)
        score += favorite_score * 10.0
        
        # Wear count penalty (prefer less worn items)
        wear_count = getattr(item, 'wearCount', 0)
        if wear_count > 10:
            score -= 5.0
        
        return score
    
    def _get_item_category(self, item: ClothingItem) -> str:
        """Get item category for validation"""
        item_type = getattr(item, 'type', '').lower()
        
        # Map item types to categories
        if item_type in ['shirt', 'blouse', 'tank', 'sweater', 'hoodie', 'jacket']:
            return 'tops'
        elif item_type in ['pants', 'jeans', 'shorts', 'skirt', 'dress']:
            return 'bottoms'
        elif item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']:
            return 'shoes'
        elif item_type in ['coat', 'blazer', 'cardigan', 'vest']:
            return 'outerwear'
        else:
            return 'accessories'
    
    def _check_inappropriate_combination(self, item1: ClothingItem, item2: ClothingItem) -> Optional[str]:
        """Check for inappropriate item combinations"""
        type1 = getattr(item1, 'type', '').lower()
        type2 = getattr(item2, 'type', '').lower()
        
        # Check against inappropriate combinations
        for (type_a, type_b), message in self.inappropriate_combinations.items():
            if (type1 == type_a and type2 == type_b) or (type1 == type_b and type2 == type_a):
                return message
        
        return None
    
    async def _filter_by_body_type(self, wardrobe: List[ClothingItem], body_type: str, height: str) -> List[ClothingItem]:
        """Filter items based on body type compatibility"""
        # Simplified body type filtering logic
        compatible_items = []
        
        for item in wardrobe:
            # Basic body type compatibility rules
            if body_type == 'tall' and getattr(item, 'type', '') == 'shorts':
                continue  # Skip shorts for tall people
            elif body_type == 'petite' and getattr(item, 'type', '') == 'long_dress':
                continue  # Skip long dresses for petite people
            
            compatible_items.append(item)
        
        return compatible_items
    
    async def _apply_body_type_optimization(self, items: List[ClothingItem], body_type: str, height: str) -> List[ClothingItem]:
        """Apply body type optimization to selected items"""
        # Simplified body type optimization
        optimized_items = items[:self.max_items]  # Limit to max items
        
        # Ensure we have essential categories
        categories_present = set(self._get_item_category(item) for item in optimized_items)
        essential_categories = {"tops", "bottoms", "shoes"}
        
        if len(essential_categories - categories_present) == 0:
            return optimized_items
        else:
            # Return what we have if we can't complete
            return optimized_items
    
    async def _filter_by_style_preferences(self, wardrobe: List[ClothingItem], style_preferences: Dict, favorite_colors: List[str], preferred_brands: List[str]) -> List[ClothingItem]:
        """Filter items based on style preferences"""
        matched_items = []
        
        for item in wardrobe:
            score = 0
            
            # Color preference bonus
            item_color = getattr(item, 'color', '').lower()
            if item_color in [color.lower() for color in favorite_colors]:
                score += 10
            
            # Brand preference bonus
            item_brand = getattr(item, 'brand', '').lower()
            if item_brand in [brand.lower() for brand in preferred_brands]:
                score += 5
            
            if score > 0:
                matched_items.append(item)
        
        return matched_items[:self.max_items]
    
    async def _filter_by_weather(self, wardrobe: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Filter items based on weather conditions"""
        weather_appropriate = []
        temperature = weather.temperature
        
        for item in wardrobe:
            item_type = getattr(item, 'type', '').lower()
            
            # Temperature-based filtering
            if temperature < 60:  # Cold weather
                if item_type in ['shorts', 'sandals', 'tank']:
                    continue
            elif temperature > 80:  # Hot weather
                if item_type in ['coat', 'heavy_sweater', 'boots']:
                    continue
            
            # Weather condition filtering
            condition = weather.condition.lower()
            if 'rain' in condition and item_type in ['suede', 'leather']:
                continue  # Avoid suede/leather in rain
            
            weather_appropriate.append(item)
        
        return weather_appropriate[:self.max_items]
    
    async def _select_basic_items(self, wardrobe: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Select basic items for fallback generation with occasion filtering"""
        logger.info(f"🔍 BASIC_SELECT: Starting with {len(wardrobe)} wardrobe items")
        basic_items = []
        categories_needed = ["tops", "bottoms", "shoes"]
        categories_found = set()
        
        # Filter items by occasion appropriateness first
        suitable_items = await self._filter_suitable_items(context)
        logger.info(f"🔍 BASIC_SELECT: After filtering, {len(suitable_items)} suitable items")
        
        # Simple selection: one item per essential category from suitable items
        for item in suitable_items:
            category = self._get_item_category(item)
            if category in categories_needed and category not in categories_found:
                basic_items.append(item)
                categories_found.add(category)
                
                if len(categories_found) == len(categories_needed):
                    break
        
        # If we don't have enough suitable items, fall back to any items
        if len(categories_found) < len(categories_needed):
            logger.warning(f"⚠️ Only found {len(categories_found)} suitable categories, falling back to any items")
            for item in wardrobe:
                category = self._get_item_category(item)
                if category in categories_needed and category not in categories_found:
                    basic_items.append(item)
                    categories_found.add(category)
                    
                    if len(categories_found) == len(categories_needed):
                        break
        
        return basic_items
    
    async def _find_item_for_category(self, wardrobe: List[ClothingItem], category: str) -> Optional[ClothingItem]:
        """Find an item for a specific category"""
        for item in wardrobe:
            if self._get_item_category(item) == category:
                return item
        return None
    
    async def _find_additional_item(self, wardrobe: List[ClothingItem], existing_items: List[ClothingItem]) -> Optional[ClothingItem]:
        """Find an additional item to complete the outfit"""
        existing_ids = {getattr(item, 'id', '') for item in existing_items}
        
        for item in wardrobe:
            if getattr(item, 'id', '') not in existing_ids:
                return item
        
        return None
    
    async def _force_complete_outfit(self, wardrobe: List[ClothingItem], context: GenerationContext) -> List[ClothingItem]:
        """Force creation of a complete outfit with all essential categories"""
        logger.info(f"🔧 FORCE COMPLETE: Creating complete outfit from {len(wardrobe)} items")
        
        outfit_items = []
        essential_categories = ["tops", "bottoms", "shoes"]
        
        # Force add one item from each essential category
        for category in essential_categories:
            category_item = await self._find_item_for_category(wardrobe, category)
            if category_item:
                outfit_items.append(category_item)
                logger.info(f"🔧 FORCE COMPLETE: Added {category}: {getattr(category_item, 'name', 'Unknown')}")
            else:
                logger.warning(f"⚠️ FORCE COMPLETE: No {category} found in wardrobe")
        
        # Add additional items to reach minimum count
        while len(outfit_items) < self.min_items and len(outfit_items) < len(wardrobe):
            additional_item = await self._find_additional_item(wardrobe, outfit_items)
            if additional_item:
                outfit_items.append(additional_item)
                logger.info(f"🔧 FORCE COMPLETE: Added additional item: {getattr(additional_item, 'name', 'Unknown')}")
            else:
                break
        
        logger.info(f"🔧 FORCE COMPLETE: Created outfit with {len(outfit_items)} items")
        return outfit_items
    
    def _determine_season_from_weather(self, weather: WeatherData) -> str:
        """Determine season from weather data"""
        temperature = weather.temperature
        
        if temperature < 40:
            return "winter"
        elif temperature < 60:
            return "fall"
        elif temperature < 80:
            return "spring"
        else:
            return "summer"
