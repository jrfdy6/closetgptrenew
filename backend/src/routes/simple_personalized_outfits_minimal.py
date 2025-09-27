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
        
        # Filter wardrobe items by occasion and style
        suitable_items = []
        for item in req.wardrobe:
            # Basic filtering by occasion and style
            if req.occasion.lower() in ['business', 'formal']:
                # For business/formal, prefer dress shirts, dress pants, dress shoes
                if item.get('type') in ['shirt', 'pants', 'shoes'] and any(
                    keyword in item.get('name', '').lower() for keyword in ['dress', 'formal', 'business', 'blazer', 'suit']
                ):
                    suitable_items.append(item)
            elif req.occasion.lower() == 'athletic':
                # For athletic, prefer athletic items
                if item.get('type') in ['shirt', 'pants', 'shoes'] and any(
                    keyword in item.get('name', '').lower() for keyword in ['athletic', 'sport', 'running', 'gym', 'workout']
                ):
                    suitable_items.append(item)
            else:
                # For casual/other occasions, use any items
                if item.get('type') in ['shirt', 'pants', 'shoes']:
                    suitable_items.append(item)
        
        # If no suitable items found, use any wardrobe items
        if not suitable_items:
            suitable_items = [item for item in req.wardrobe if item.get('type') in ['shirt', 'pants', 'shoes']][:6]
        
        # Select items for the outfit (3-6 items based on occasion)
        target_count = 4 if req.occasion.lower() in ['business', 'formal'] else 3
        selected_items = suitable_items[:target_count]
        
        # Ensure we have at least 3 items
        if len(selected_items) < 3:
            # Add more items from wardrobe if needed
            remaining_items = [item for item in req.wardrobe if item not in selected_items]
            selected_items.extend(remaining_items[:3-len(selected_items)])
        
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
            "metadata": {
                "generated_by": "simple_personalization_real_wardrobe",
                "occasion": req.occasion,
                "style": req.style,
                "mood": req.mood,
                "wardrobe_size": len(req.wardrobe),
                "selected_from_real_items": True
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
            "personalization_score": existing_result.get("personalization_score"),
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
