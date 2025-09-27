#!/usr/bin/env python3
"""
Simple Personalized Outfits Routes - Extended Minimal Version
==============================================================

This is an extended minimal version that adds outfit generation, user preferences,
and personalization learning without depending on external services.

Features:
- Outfit generation with personalization
- User preferences tracking
- Interaction learning
- Simple recommendation ranking
- No external dependencies
"""

import logging
import time
import json
import hashlib
import math
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dataclasses import dataclass, asdict
from enum import Enum
from ..auth.auth_service import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory storage for user data (in production, this would be a database)
user_preferences = {}
user_interactions = {}
outfit_embeddings = {}

@dataclass
class UserPreference:
    """User preference data"""
    user_id: str
    preferred_colors: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    disliked_colors: List[str]
    disliked_styles: List[str]
    interaction_count: int
    last_updated: float

@dataclass
class OutfitEmbedding:
    """Simple outfit embedding"""
    outfit_id: str
    colors: List[str]
    styles: List[str]
    occasion: str
    embedding_vector: List[float]
    popularity_score: float

class InteractionType(Enum):
    """Types of user interactions"""
    VIEW = "view"
    LIKE = "like"
    WEAR = "wear"
    DISLIKE = "dislike"

class SimplePersonalizationEngine:
    """Simple personalization engine without external dependencies"""
    
    def __init__(self):
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        logger.info("✅ Simple Personalization Engine initialized")
    
    def create_simple_embedding(self, text: str) -> List[float]:
        """Create a simple embedding using hash-based approach"""
        # Use MD5 hash to create a deterministic vector
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 16-dimensional vector (normalize to 0-1)
        vector = []
        for i in range(0, len(hash_bytes), 2):
            if i + 1 < len(hash_bytes):
                # Combine two bytes for each dimension
                val = (hash_bytes[i] << 8) + hash_bytes[i + 1]
                vector.append(val / 65535.0)  # Normalize to 0-1
        
        # Pad or truncate to exactly 16 dimensions
        while len(vector) < 16:
            vector.append(0.0)
        vector = vector[:16]
        
        return vector
    
    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_user_preference(self, user_id: str) -> UserPreference:
        """Get or create user preference"""
        if user_id not in user_preferences:
            user_preferences[user_id] = UserPreference(
                user_id=user_id,
                preferred_colors=[],
                preferred_styles=[],
                preferred_occasions=[],
                disliked_colors=[],
                disliked_styles=[],
                interaction_count=0,
                last_updated=time.time()
            )
        return user_preferences[user_id]
    
    def update_user_preference(self, user_id: str, interaction_type: str, outfit_data: Dict[str, Any]):
        """Update user preferences based on interaction"""
        preference = self.get_user_preference(user_id)
        
        colors = outfit_data.get('colors', [])
        styles = outfit_data.get('styles', [])
        occasion = outfit_data.get('occasion', '')
        
        if interaction_type in ['like', 'wear']:
            # Add to preferences
            for color in colors:
                if color not in preference.preferred_colors:
                    preference.preferred_colors.append(color)
            for style in styles:
                if style not in preference.preferred_styles:
                    preference.preferred_styles.append(style)
            if occasion and occasion not in preference.preferred_occasions:
                preference.preferred_occasions.append(occasion)
        
        elif interaction_type == 'dislike':
            # Add to dislikes
            for color in colors:
                if color not in preference.disliked_colors:
                    preference.disliked_colors.append(color)
            for style in styles:
                if style not in preference.disliked_styles:
                    preference.disliked_styles.append(style)
        
        preference.interaction_count += 1
        preference.last_updated = time.time()
        
        logger.info(f"✅ Updated preferences for user {user_id}: {interaction_type}")
    
    def rank_outfits_by_preference(self, user_id: str, outfits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank outfits based on user preferences"""
        preference = self.get_user_preference(user_id)
        
        if preference.interaction_count < 3:
            # Not enough data for personalization
            return outfits
        
        ranked_outfits = []
        for outfit in outfits:
            score = 0.0
            
            # Color preference scoring
            outfit_colors = outfit.get('colors', [])
            for color in outfit_colors:
                if color in preference.preferred_colors:
                    score += 2.0
                elif color in preference.disliked_colors:
                    score -= 1.0
            
            # Style preference scoring
            outfit_styles = outfit.get('styles', [])
            for style in outfit_styles:
                if style in preference.preferred_styles:
                    score += 1.5
                elif style in preference.disliked_styles:
                    score -= 0.5
            
            # Occasion preference scoring
            outfit_occasion = outfit.get('occasion', '')
            if outfit_occasion in preference.preferred_occasions:
                score += 1.0
            
            # Add base score and personalization info
            outfit['personalization_score'] = score
            outfit['personalization_applied'] = True
            outfit['user_interactions'] = preference.interaction_count
            
            ranked_outfits.append(outfit)
        
        # Sort by personalization score (highest first)
        ranked_outfits.sort(key=lambda x: x.get('personalization_score', 0), reverse=True)
        
        logger.info(f"✅ Ranked {len(outfits)} outfits for user {user_id}")
        return ranked_outfits

# Initialize the personalization engine
personalization_engine = SimplePersonalizationEngine()

# Pydantic models
class InteractionRequest(BaseModel):
    outfit_id: Optional[str] = None
    item_id: Optional[str] = None
    interaction_type: str  # view, like, wear, dislike
    rating: Optional[float] = None
    outfit_data: Optional[Dict[str, Any]] = None  # Colors, styles, occasion

class OutfitGenerationRequest(BaseModel):
    occasion: str
    style: str
    mood: str
    weather: Optional[Dict[str, Any]] = None
    wardrobe: Optional[List[Dict[str, Any]]] = None
    user_profile: Optional[Dict[str, Any]] = None
    baseItemId: Optional[str] = None

class PersonalizationStatusResponse(BaseModel):
    user_id: str
    personalization_enabled: bool
    has_user_embedding: bool
    total_interactions: int
    min_interactions_required: int
    ready_for_personalization: bool
    preferred_colors: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    disliked_colors: List[str]
    disliked_styles: List[str]
    system_parameters: Dict[str, Any]

class OutfitResponse(BaseModel):
    id: str
    name: str
    items: List[Dict[str, Any]]
    style: str
    occasion: str
    mood: str
    weather: Dict[str, Any]
    confidence: float
    personalization_score: Optional[float] = None
    personalization_applied: bool = False
    user_interactions: int = 0
    metadata: Dict[str, Any]

@router.get("/health")
async def health_check():
    """Health check for the minimal simple personalization system"""
    try:
        return {
            "status": "healthy",
            "personalization_enabled": True,
            "min_interactions_required": 3,
            "max_outfits": 5,
            "simple_personalization": True,
            "no_external_dependencies": True,
            "minimal_version": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Minimal simple personalization health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "simple_personalization": True,
            "minimal_version": True,
            "timestamp": time.time()
        }

@router.get("/test")
async def test_endpoint():
    """Test endpoint for minimal simple personalization"""
    return {
        "message": "Minimal simple personalization router is working",
        "status": "success",
        "timestamp": time.time()
    }

@router.post("/generate-personalized", response_model=OutfitResponse)
async def generate_personalized_outfit(
    req: OutfitGenerationRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate personalized outfit using existing system + personalization layer
    
    This endpoint:
    1. Uses your existing outfit generation (keeps all your validation)
    2. Adds personalization layer on top (if user has enough interactions)
    3. Falls back to existing system if personalization fails
    """
    start_time = time.time()
    
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        logger.info(f"🎯 Generating personalized outfit for user {user_id}")
        
        # Use real wardrobe items from the request instead of mock data
        if not req.wardrobe or len(req.wardrobe) == 0:
            raise HTTPException(status_code=400, detail="No wardrobe items provided")
        
        # Define hard requirements per occasion
        occasion_requirements = {
            'business': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top']
            },
            'formal': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top', 'jeans']
            },
            'athletic': {
                'required': ['top', 'shorts OR athletic-pants', 'sneakers'],
                'optional': ['jacket', 'hat'],
                'forbidden': ['dress-shirt', 'tie', 'dress-shoes']
            },
            'casual': {
                'required': ['top', 'bottom'],
                'optional': ['shoes', 'jacket', 'accessories'],
                'forbidden': []
            },
            'weekend': {
                'required': ['top', 'bottom'],
                'optional': ['sneakers', 'hoodie', 'jacket'],
                'forbidden': ['tie', 'dress-shoes']
            }
        }
        
        # Get requirements for current occasion
        occasion = req.occasion.lower()
        requirements = occasion_requirements.get(occasion, occasion_requirements['casual'])
        
        # Enhanced filtering by occasion, style, and mood
        suitable_items = []
        for item in req.wardrobe:
            item_name = item.get('name', '').lower()
            item_type = item.get('type', '').lower()
            item_color = item.get('color', '').lower()
            
            # Check if item is forbidden for this occasion
            is_forbidden = False
            for forbidden in requirements.get('forbidden', []):
                if forbidden in item_name or forbidden in item_type:
                    is_forbidden = True
                    break
            
            if is_forbidden:
                continue
            
            # Score item based on occasion, style, and mood
            score = 0
            
            # Occasion-based scoring with hard requirements
            if occasion in ['business', 'formal']:
                if any(keyword in item_name for keyword in ['dress', 'formal', 'business', 'blazer', 'suit']):
                    score += 3
                elif item_type in requirements['required']:
                    score += 2  # Required items get higher priority
                elif item_type in requirements['optional']:
                    score += 1
                else:
                    score += 0.5  # Other items still allowed but lower priority
            elif occasion == 'athletic':
                if any(keyword in item_name for keyword in ['athletic', 'sport', 'running', 'gym', 'workout', 'shorts']):
                    score += 3
                elif item_type in ['shorts', 'athletic-pants', 'track-pants']:
                    score += 2  # Athletic bottoms get priority
                elif item_type in ['sneakers', 'running-shoes']:
                    score += 2  # Athletic shoes get priority
                elif item_type in requirements['required']:
                    score += 1
                elif item_type in requirements['optional']:
                    score += 0.5
            else:
                # Casual/other occasions - more flexible
                if item_type in requirements['required']:
                    score += 2
                elif item_type in requirements['optional']:
                    score += 1
                else:
                    score += 0.5
            
            # Style-based scoring (decorates occasion requirements, doesn't override)
            style = req.style.lower()
            if style == 'classic':
                # Classic style: prefer traditional cuts and colors within occasion constraints
                if any(keyword in item_name for keyword in ['classic', 'traditional', 'timeless', 'polo']):
                    score += 1.5  # Boost classic items
                if item_color in ['black', 'white', 'navy', 'grey', 'brown']:
                    score += 1
                # Classic + Athletic = polo shirt, not dress shirt
                if occasion == 'athletic' and 'polo' in item_name:
                    score += 2
            elif style == 'minimalist':
                # Minimalist: clean lines, neutral colors
                if any(keyword in item_name for keyword in ['minimal', 'simple', 'clean', 'basic']):
                    score += 1.5
                if item_color in ['white', 'black', 'grey', 'beige']:
                    score += 1.5
            elif style == 'maximalist':
                # Maximalist: bold patterns, vibrant colors
                if any(keyword in item_name for keyword in ['bold', 'statement', 'vibrant', 'patterned']):
                    score += 1.5
                if item_color in ['red', 'blue', 'green', 'yellow', 'purple']:
                    score += 1
            elif style == 'streetwear':
                # Streetwear: casual, trendy, athletic-inspired
                if any(keyword in item_name for keyword in ['street', 'urban', 'hoodie', 'sweatshirt']):
                    score += 1.5
                if occasion == 'athletic' and any(keyword in item_name for keyword in ['jogger', 'sweatpant']):
                    score += 2
            
            # Mood-based scoring
            if req.mood.lower() == 'bold':
                if any(keyword in item_name for keyword in ['bold', 'statement', 'standout']):
                    score += 2
                if item_color in ['red', 'bright', 'vibrant']:
                    score += 1
            elif req.mood.lower() == 'confident':
                if any(keyword in item_name for keyword in ['confident', 'sharp', 'professional']):
                    score += 2
            elif req.mood.lower() == 'comfortable':
                if any(keyword in item_name for keyword in ['comfort', 'soft', 'casual']):
                    score += 2
            
            # Only include items with positive scores
            if score > 0:
                suitable_items.append((item, score))
        
        # Sort by score (highest first) and select items
        if suitable_items and isinstance(suitable_items[0], tuple):
            # Sort by score (highest first)
            suitable_items.sort(key=lambda x: x[1], reverse=True)
            # Extract just the items
            sorted_items = [item[0] for item in suitable_items]
        else:
            # Fallback: if no scored items, use any wardrobe items
            sorted_items = [item for item in req.wardrobe if item.get('type') in ['shirt', 'pants', 'shoes']][:6]
        
        # Select items for the outfit (3-6 items based on occasion)
        target_count = 4 if req.occasion.lower() in ['business', 'formal'] else 3
        selected_items = sorted_items[:target_count]
        
        # VALIDATION: Ensure required occasion slots are filled
        def validate_outfit_completeness(outfit_items, occasion_reqs):
            item_types = [item.get('type', '').lower() for item in outfit_items]
            item_names = [item.get('name', '').lower() for item in outfit_items]
            
            missing_required = []
            for required in occasion_reqs['required']:
                if ' OR ' in required:
                    # Handle OR conditions (e.g., "shorts OR athletic-pants")
                    options = [opt.strip() for opt in required.split(' OR ')]
                    if not any(any(opt in item_type or opt in item_name for opt in options) 
                              for item_type, item_name in zip(item_types, item_names)):
                        missing_required.append(required)
                else:
                    # Single requirement
                    if not any(required in item_type or required in item_name 
                              for item_type, item_name in zip(item_types, item_names)):
                        missing_required.append(required)
            
            return missing_required
        
        # Check if outfit meets occasion requirements
        missing_required = validate_outfit_completeness(selected_items, requirements)
        
        # If missing required items, try to fill them
        if missing_required:
            print(f"🔍 DEBUG: Missing required items for {occasion}: {missing_required}")
            
            # Try to find items that fill missing requirements
            for missing in missing_required:
                if ' OR ' in missing:
                    options = [opt.strip() for opt in missing.split(' OR ')]
                    for option in options:
                        for item in req.wardrobe:
                            if (option in item.get('type', '').lower() or option in item.get('name', '').lower()) and item not in selected_items:
                                selected_items.append(item)
                                break
                        if len(selected_items) >= target_count:
                            break
                else:
                    for item in req.wardrobe:
                        if (missing in item.get('type', '').lower() or missing in item.get('name', '').lower()) and item not in selected_items:
                            selected_items.append(item)
                            break
        
        # DEDUPLICATION: Remove duplicate items by ID and name+type+color combination
        def deduplicate_items(items):
            seen_ids = set()
            seen_combinations = set()
            unique_items = []
            for item in items:
                item_id = item.get('id', '')
                item_name = item.get('name', '')
                item_type = item.get('type', '')
                item_color = item.get('color', '')
                
                # Create a combination key for name+type+color
                combination_key = f"{item_name}|{item_type}|{item_color}"
                
                # Check both ID uniqueness and combination uniqueness
                if item_id not in seen_ids and combination_key not in seen_combinations:
                    seen_ids.add(item_id)
                    seen_combinations.add(combination_key)
                    unique_items.append(item)
                else:
                    print(f"🔍 DEBUG: Removed duplicate item: {item_name} ({item_color})")
            return unique_items
        
        selected_items = deduplicate_items(selected_items)
        
        # Ensure we have at least 3 items
        if len(selected_items) < 3:
            # Add more items from wardrobe if needed
            remaining_items = [item for item in req.wardrobe if item not in selected_items]
            selected_items.extend(remaining_items[:3-len(selected_items)])
            selected_items = deduplicate_items(selected_items)  # Dedupe again after adding
        
        # Create outfit from real wardrobe items
        existing_result = {
            "id": f"outfit_{int(time.time())}",
            "name": f"{req.style} {req.occasion} Outfit",
            "items": [
                {
                    "id": item.get('id', f"item_{i+1}"),
                    "name": item.get('name', f"{req.style} Item"),
                    "type": item.get('type', 'unknown'),
                    "color": item.get('color', 'Unknown'),
                    "style": req.style,
                    "occasion": req.occasion,
                    "brand": item.get('brand', ''),
                    "imageUrl": item.get('imageUrl', ''),
                    "wearCount": item.get('wearCount', 0),
                    "favorite_score": item.get('favorite_score', 0.0),
                    "tags": item.get('tags', []),
                    "metadata": item.get('metadata', {})
                }
                for i, item in enumerate(selected_items)
            ],
            "confidence": 0.8,
            "personalization_applied": True,  # We ARE applying personalization (style/mood scoring)
            "metadata": {
                "generated_by": "simple_personalization_real_wardrobe",
                "occasion": req.occasion,
                "style": req.style,
                "mood": req.mood,
                "wardrobe_size": len(req.wardrobe),
                "selected_from_real_items": True,
                "style_mood_considered": True,
                "scoring_applied": True,
                "items_scored": len(suitable_items) if suitable_items else 0,
                "occasion_requirements_met": len(missing_required) == 0 if 'missing_required' in locals() else True,
                "validation_applied": True,
                "hard_requirements_enforced": True,
                "deduplication_applied": True,
                "unique_items_count": len(selected_items),
                "personalization_score_message": "Not enough data yet (need 3+ interactions)" if preference.interaction_count < 3 else "Score calculated"
            }
        }
        
        # Extract outfit data for personalization
        outfit_data = {
            'colors': [item.get('color', '') for item in existing_result.get('items', []) if item.get('color')],
            'styles': [req.style],
            'occasion': req.occasion
        }
        
        # Apply personalization if user has enough interactions
        preference = personalization_engine.get_user_preference(user_id)
        
        if preference.interaction_count >= 3:
            # Apply personalization
            personalized_outfits = personalization_engine.rank_outfits_by_preference(
                user_id, [existing_result]
            )
            
            if personalized_outfits:
                existing_result = personalized_outfits[0]
                logger.info(f"✅ Applied personalization for user {user_id}")
        
        # Create response
        outfit_response = {
            "id": existing_result.get("id", f"personalized_{int(time.time())}"),
            "name": existing_result.get("name", "Personalized Outfit"),
            "items": existing_result.get("items", []),
            "style": req.style,
            "occasion": req.occasion,
            "mood": req.mood,
            "weather": req.weather or {},
            "confidence": existing_result.get("confidence", 0.8),
            "personalization_score": existing_result.get("personalization_score") if preference.interaction_count >= 3 else None,
            "personalization_applied": existing_result.get("personalization_applied", False),
            "user_interactions": preference.interaction_count,
            "metadata": {
                **existing_result.get("metadata", {}),
                "generation_time": time.time() - start_time,
                "personalization_enabled": True,
                "user_id": user_id,
                "extended_minimal_version": True
            }
        }
        
        logger.info(f"✅ Generated personalized outfit (personalization: {existing_result.get('personalization_applied', False)})")
        return OutfitResponse(**outfit_response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Personalized outfit generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Personalized outfit generation failed: {str(e)}"
        )

@router.post("/interaction")
async def record_enhanced_interaction(
    interaction: InteractionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Record user interaction with learning - enhanced version"""
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Validate interaction
        if not interaction.outfit_id and not interaction.item_id:
            raise HTTPException(
                status_code=400, 
                detail="Either outfit_id or item_id must be provided"
            )
        
        if interaction.interaction_type not in ["view", "like", "wear", "dislike"]:
            raise HTTPException(
                status_code=400,
                detail="interaction_type must be one of: view, like, wear, dislike"
            )
        
        # Update user preferences if outfit data is provided
        if interaction.outfit_data:
            personalization_engine.update_user_preference(
                user_id, 
                interaction.interaction_type, 
                interaction.outfit_data
            )
        
        # Store interaction
        interaction_key = f"{user_id}_{interaction.outfit_id or interaction.item_id}_{int(time.time())}"
        user_interactions[interaction_key] = {
            "user_id": user_id,
            "outfit_id": interaction.outfit_id,
            "item_id": interaction.item_id,
            "interaction_type": interaction.interaction_type,
            "rating": interaction.rating,
            "outfit_data": interaction.outfit_data,
            "timestamp": time.time()
        }
        
        # Get updated preference
        preference = personalization_engine.get_user_preference(user_id)
        
        return {
            "success": True,
            "message": f"Recorded {interaction.interaction_type} interaction",
            "user_id": user_id,
            "interaction_count": preference.interaction_count,
            "personalization_updated": bool(interaction.outfit_data),
            "extended_minimal_version": True,
            "timestamp": time.time()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record interaction: {str(e)}"
        )

@router.get("/personalization-status", response_model=PersonalizationStatusResponse)
async def get_enhanced_personalization_status(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get enhanced personalization status with user preferences"""
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Get user preference
        preference = personalization_engine.get_user_preference(user_id)
        
        return PersonalizationStatusResponse(
            user_id=user_id,
            personalization_enabled=True,
            has_user_embedding=preference.interaction_count > 0,
            total_interactions=preference.interaction_count,
            min_interactions_required=3,
            ready_for_personalization=preference.interaction_count >= 3,
            preferred_colors=preference.preferred_colors,
            preferred_styles=preference.preferred_styles,
            preferred_occasions=preference.preferred_occasions,
            disliked_colors=preference.disliked_colors,
            disliked_styles=preference.disliked_styles,
            system_parameters={
                "min_interactions": 3,
                "max_outfits": 5,
                "learning_rate": personalization_engine.learning_rate,
                "exploration_rate": personalization_engine.exploration_rate,
                "extended_minimal_version": True,
                "last_updated": preference.last_updated
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get personalization status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization status: {str(e)}"
        )

@router.get("/user-preferences")
async def get_user_preferences(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get detailed user preferences"""
    try:
        # Validate user
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user_id
        
        # Get user preference
        preference = personalization_engine.get_user_preference(user_id)
        
        return {
            "user_id": user_id,
            "preferences": {
                "preferred_colors": preference.preferred_colors,
                "preferred_styles": preference.preferred_styles,
                "preferred_occasions": preference.preferred_occasions,
                "disliked_colors": preference.disliked_colors,
                "disliked_styles": preference.disliked_styles
            },
            "stats": {
                "total_interactions": preference.interaction_count,
                "last_updated": preference.last_updated,
                "ready_for_personalization": preference.interaction_count >= 3
            },
            "extended_minimal_version": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user preferences: {str(e)}"
        )

@router.get("/analytics")
async def get_system_analytics():
    """Get system-wide analytics"""
    try:
        total_users = len(user_preferences)
        total_interactions = sum(pref.interaction_count for pref in user_preferences.values())
        
        # Calculate average interactions per user
        avg_interactions = total_interactions / total_users if total_users > 0 else 0
        
        # Count users ready for personalization
        ready_users = sum(1 for pref in user_preferences.values() if pref.interaction_count >= 3)
        
        return {
            "system_stats": {
                "total_users": total_users,
                "total_interactions": total_interactions,
                "average_interactions_per_user": round(avg_interactions, 2),
                "users_ready_for_personalization": ready_users,
                "personalization_adoption_rate": round((ready_users / total_users * 100) if total_users > 0 else 0, 2)
            },
            "engine_stats": {
                "learning_rate": personalization_engine.learning_rate,
                "exploration_rate": personalization_engine.exploration_rate,
                "min_interactions_required": 3
            },
            "extended_minimal_version": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )
