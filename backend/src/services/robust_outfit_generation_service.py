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
        logger.info(f"🌤️ Weather: {context.weather.temperature}°F, {context.weather.condition}")
        
        # Log wardrobe item types for debugging
        item_types = [item.type for item in context.wardrobe]
        type_counts = {item_type: item_types.count(item_type) for item_type in set(item_types)}
        logger.info(f"📊 Wardrobe breakdown: {type_counts}")
        
        # Try each generation strategy in order
        logger.info(f"🔄 Available strategies: {[s.value for s in self.generation_strategies]}")
        for strategy in self.generation_strategies:
            try:
                logger.info(f"🔄 Trying generation strategy: {strategy.value}")
                context.generation_strategy = strategy
                
                # Log strategy-specific context
                logger.info(f"🔍 Strategy {strategy.value} - Starting generation...")
                outfit = await self._generate_with_strategy(context)
                logger.info(f"🔍 Strategy {strategy.value} - Generated outfit with {len(outfit.items)} items")
                
                # Validate the generated outfit
                logger.info(f"🔍 Strategy {strategy.value} - Starting validation...")
                validation = await self._validate_outfit(outfit, context)
                logger.info(f"🔍 Strategy {strategy.value} - Validation complete: valid={validation.is_valid}, confidence={validation.confidence}")
                
                if validation.is_valid and validation.confidence >= 0.7:
                    logger.info(f"✅ Successfully generated outfit with strategy {strategy.value}")
                    logger.info(f"📊 Validation score: {validation.score}, Confidence: {validation.confidence}")
                    logger.info(f"📦 Final outfit items: {[item.name for item in outfit.items]}")
                    return outfit
                else:
                    logger.warning(f"⚠️ Strategy {strategy.value} failed validation: {validation.issues}")
                    logger.warning(f"⚠️ Validation details: valid={validation.is_valid}, confidence={validation.confidence}, score={validation.score}")
                    if strategy == GenerationStrategy.EMERGENCY_DEFAULT:
                        # If even emergency default fails, return it anyway
                        logger.error(f"🚨 All generation strategies failed, returning emergency default")
                        return outfit
                        
            except Exception as e:
                logger.error(f"❌ Strategy {strategy.value} failed with error: {e}", exc_info=True)
                logger.error(f"❌ Strategy {strategy.value} error context: user={context.user_id}, occasion={context.occasion}")
                continue
        
        # This should never be reached due to emergency default
        raise Exception("All outfit generation strategies failed")
    
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
        
        # Create outfit response
        outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=f"{context.style} {context.occasion} Outfit",
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
    
    async def _filter_suitable_items(self, context: GenerationContext) -> List[Dict[str, Any]]:
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
        
        logger.info(f"📦 Found {len(suitable_items)} suitable items from {len(context.wardrobe)} total")
        return suitable_items
    
    async def _intelligent_item_selection(self, suitable_items: List[Dict[str, Any]], context: GenerationContext) -> List[Dict[str, Any]]:
        """Intelligently select items for the outfit with dynamic limits"""
        selected_items = []
        
        # Get dynamic category limits based on occasion and style
        category_limits = self._get_dynamic_category_limits(context)
        category_counts = {cat: 0 for cat in category_limits.keys()}
        
        # Calculate target item count based on occasion and style
        target_count = self._get_target_item_count(context)
        
        # Determine if outerwear is needed based on temperature and occasion
        needs_outerwear = self._needs_outerwear(context)
        
        # Sort items by preference score
        scored_items = []
        for item in suitable_items:
            score = await self._calculate_item_score(item, context)
            scored_items.append((item, score))
        
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Select items ensuring dynamic category limits
        for item, score in scored_items:
            item_category = self._get_item_category(item)
            
            # Skip outerwear if not needed
            if item_category == "outerwear" and not needs_outerwear:
                continue
                
            if category_counts.get(item_category, 0) < category_limits.get(item_category, 2):
                selected_items.append(item)
                category_counts[item_category] += 1
                
                if len(selected_items) >= target_count:
                    break
        
        return selected_items
    
    def _get_dynamic_category_limits(self, context: GenerationContext) -> Dict[str, int]:
        """Get dynamic category limits based on occasion and style - SIMPLIFIED"""
        import random
        
        # Start with base limits - SIMPLIFIED
        limits = {
            "tops": 2,      # Usually just 1-2 tops
            "bottoms": 1,   # Always just 1 bottom
            "shoes": 1,     # Always just 1 pair of shoes
            "outerwear": 1, # Usually just 1 outerwear (optional)
            "accessories": 2 # Usually 0-2 accessories
        }
        
        occasion_lower = context.occasion.lower()
        style_lower = context.style.lower() if context.style else ""
        
        # Adjust based on occasion - SIMPLIFIED
        if 'formal' in occasion_lower or 'business' in occasion_lower:
            # Formal: allow more accessories
            limits["accessories"] = 3
        elif 'athletic' in occasion_lower or 'gym' in occasion_lower:
            # Athletic: keep it simple
            limits["tops"] = 2
            limits["accessories"] = 1
        elif 'party' in occasion_lower or 'date' in occasion_lower:
            # Social: allow more accessories
            limits["accessories"] = 3
        elif 'casual' in occasion_lower:
            # Casual: flexible
            limits["tops"] = 2
            limits["accessories"] = 2
        
        return limits
    
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
    
    async def _ensure_outfit_completeness(self, items: List[Dict[str, Any]], context: GenerationContext) -> List[Dict[str, Any]]:
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
        """Comprehensive outfit validation"""
        issues = []
        suggestions = []
        score = 100.0
        
        # Check item count
        if len(outfit.items) < self.min_items:
            issues.append(f"Outfit has only {len(outfit.items)} items, minimum is {self.min_items}")
            score -= 20.0
        elif len(outfit.items) > self.max_items:
            issues.append(f"Outfit has {len(outfit.items)} items, maximum is {self.max_items}")
            score -= 10.0
        
        # Check category limits
        category_counts = {}
        for item in outfit.items:
            category = self._get_item_category(item)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            limit = self.base_category_limits.get(category, 2)
            if count > limit:
                issues.append(f"Too many {category}: {count} (max {limit})")
                score -= 15.0
        
        # Check for inappropriate combinations
        for item1 in outfit.items:
            for item2 in outfit.items:
                if item1 != item2:
                    combination = self._check_inappropriate_combination(item1, item2)
                    if combination:
                        issues.append(combination)
                        score -= 25.0
        
        # Check essential categories
        categories_present = set(self._get_item_category(item) for item in outfit.items)
        essential_categories = {"tops", "bottoms", "shoes"}
        missing_essential = essential_categories - categories_present
        
        if missing_essential:
            issues.append(f"Missing essential categories: {missing_essential}")
            score -= 30.0
        
        # Calculate confidence
        confidence = max(0.0, min(1.0, score / 100.0))
        
        is_valid = len(issues) == 0 and confidence >= 0.7
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence
        )
    
    def _is_occasion_compatible(self, item: Dict[str, Any], occasion: str) -> bool:
        """Check if item is compatible with occasion"""
        item_occasions = item.get('occasion', [])
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions]
        
        return occasion.lower() in [occ.lower() for occ in item_occasions]
    
    def _is_style_compatible(self, item: Dict[str, Any], style: str) -> bool:
        """Check if item is compatible with style"""
        item_styles = item.get('style', [])
        if isinstance(item_styles, str):
            item_styles = [item_styles]
        
        return style.lower() in [s.lower() for s in item_styles]
    
    async def _calculate_item_score(self, item: Dict[str, Any], context: GenerationContext) -> float:
        """Calculate preference score for item"""
        score = 50.0  # Base score
        
        # Style match bonus
        if self._is_style_compatible(item, context.style):
            score += 20.0
        
        # Occasion match bonus
        if self._is_occasion_compatible(item, context.occasion):
            score += 15.0
        
        # Favorite score bonus
        favorite_score = item.get('favorite_score', 0.0)
        score += favorite_score * 10.0
        
        # Wear count penalty (prefer less worn items)
        wear_count = item.get('wearCount', 0)
        if wear_count > 10:
            score -= 5.0
        
        return score
    
    def _get_item_category(self, item: Dict[str, Any]) -> str:
        """Get item category for validation"""
        item_type = item.get('type', '').lower()
        
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
    
    def _check_inappropriate_combination(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> Optional[str]:
        """Check for inappropriate item combinations"""
        type1 = item1.get('type', '').lower()
        type2 = item2.get('type', '').lower()
        
        # Check against inappropriate combinations
        for (type_a, type_b), message in self.inappropriate_combinations.items():
            if (type1 == type_a and type2 == type_b) or (type1 == type_b and type2 == type_a):
                return message
        
        return None
    
    async def _filter_by_body_type(self, wardrobe: List[Dict[str, Any]], body_type: str, height: str) -> List[Dict[str, Any]]:
        """Filter items based on body type compatibility"""
        # Simplified body type filtering logic
        compatible_items = []
        
        for item in wardrobe:
            # Basic body type compatibility rules
            if body_type == 'tall' and item.get('type') == 'shorts':
                continue  # Skip shorts for tall people
            elif body_type == 'petite' and item.get('type') == 'long_dress':
                continue  # Skip long dresses for petite people
            
            compatible_items.append(item)
        
        return compatible_items
    
    async def _apply_body_type_optimization(self, items: List[Dict[str, Any]], body_type: str, height: str) -> List[Dict[str, Any]]:
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
    
    async def _filter_by_style_preferences(self, wardrobe: List[Dict[str, Any]], style_preferences: Dict, favorite_colors: List[str], preferred_brands: List[str]) -> List[Dict[str, Any]]:
        """Filter items based on style preferences"""
        matched_items = []
        
        for item in wardrobe:
            score = 0
            
            # Color preference bonus
            item_color = item.get('color', '').lower()
            if item_color in [color.lower() for color in favorite_colors]:
                score += 10
            
            # Brand preference bonus
            item_brand = item.get('brand', '').lower()
            if item_brand in [brand.lower() for brand in preferred_brands]:
                score += 5
            
            if score > 0:
                matched_items.append(item)
        
        return matched_items[:self.max_items]
    
    async def _filter_by_weather(self, wardrobe: List[Dict[str, Any]], weather: WeatherData) -> List[Dict[str, Any]]:
        """Filter items based on weather conditions"""
        weather_appropriate = []
        temperature = weather.temperature
        
        for item in wardrobe:
            item_type = item.get('type', '').lower()
            
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
    
    async def _select_basic_items(self, wardrobe: List[Dict[str, Any]], context: GenerationContext) -> List[Dict[str, Any]]:
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
    
    async def _find_item_for_category(self, wardrobe: List[Dict[str, Any]], category: str) -> Optional[Dict[str, Any]]:
        """Find an item for a specific category"""
        for item in wardrobe:
            if self._get_item_category(item) == category:
                return item
        return None
    
    async def _find_additional_item(self, wardrobe: List[Dict[str, Any]], existing_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find an additional item to complete the outfit"""
        existing_ids = {item.get('id') for item in existing_items}
        
        for item in wardrobe:
            if item.get('id') not in existing_ids:
                return item
        
        return None
    
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
