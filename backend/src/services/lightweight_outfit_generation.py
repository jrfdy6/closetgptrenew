#!/usr/bin/env python3
"""
Lightweight Outfit Generation with Embeddings - No External Dependencies
=======================================================================

This service provides personalized outfit generation using lightweight
embeddings without requiring external APIs or databases.

Features:
- Personalized outfit ranking using lightweight embeddings
- Integration with existing outfit generation pipeline
- Continuous learning from user interactions
- Fallback to original generation if embeddings fail
- No external dependencies required
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .lightweight_embedding_service import LightweightEmbeddingService, UserInteraction
from .lightweight_recommendation_engine import LightweightRecommendationEngine, RecommendationStrategy

logger = logging.getLogger(__name__)

@dataclass
class LightweightOutfitResult:
    """Result of lightweight outfit generation"""
    outfits: List[Dict[str, Any]]
    personalization_applied: bool
    strategy_used: str
    personalization_score: float
    confidence: float
    metadata: Dict[str, Any]

class LightweightOutfitGeneration:
    """
    Lightweight outfit generation with embeddings and personalization
    """
    
    def __init__(self):
        # Initialize services
        self.embedding_service = LightweightEmbeddingService()
        self.recommendation_engine = LightweightRecommendationEngine(self.embedding_service)
        
        # Integration settings
        self.enable_personalization = True
        self.fallback_to_original = True
        self.max_personalized_outfits = 5
        
        logger.info("✅ Lightweight Outfit Generation initialized")
    
    async def generate_personalized_outfits(
        self,
        user_id: str,
        base_outfit_generation_func,
        generation_context: Dict[str, Any],
        user_wardrobe: List[Dict[str, Any]] = None
    ) -> LightweightOutfitResult:
        """
        Generate personalized outfits using lightweight embeddings
        
        Args:
            user_id: ID of the user
            base_outfit_generation_func: Function that generates base outfits
            generation_context: Context for outfit generation
            user_wardrobe: User's wardrobe items for embedding generation
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎯 Starting lightweight personalized outfit generation for user {user_id}")
            
            # Step 1: Ensure user has embedding
            await self._ensure_user_embedding(user_id, user_wardrobe)
            
            # Step 2: Generate base outfits using existing system
            base_outfits = await self._generate_base_outfits(
                base_outfit_generation_func, generation_context
            )
            
            if not base_outfits:
                logger.warning("No base outfits generated, returning empty result")
                return LightweightOutfitResult(
                    outfits=[],
                    personalization_applied=False,
                    strategy_used="none",
                    personalization_score=0.0,
                    confidence=0.0,
                    metadata={"error": "No base outfits generated"}
                )
            
            # Step 3: Apply personalization if enabled
            if self.enable_personalization:
                personalized_result = await self._apply_personalization(
                    user_id, base_outfits, generation_context
                )
                
                if personalized_result.outfits:
                    logger.info(f"✅ Personalized {len(personalized_result.outfits)} outfits")
                    return personalized_result
            
            # Step 4: Fallback to base outfits if personalization fails
            if self.fallback_to_original:
                logger.info("Using base outfits as fallback")
                return LightweightOutfitResult(
                    outfits=base_outfits[:self.max_personalized_outfits],
                    personalization_applied=False,
                    strategy_used="fallback",
                    personalization_score=0.0,
                    confidence=0.7,
                    metadata={"fallback_reason": "personalization_disabled_or_failed"}
                )
            
            # Step 5: Return empty if no fallback
            return LightweightOutfitResult(
                outfits=[],
                personalization_applied=False,
                strategy_used="none",
                personalization_score=0.0,
                confidence=0.0,
                metadata={"error": "No outfits generated"}
            )
            
        except Exception as e:
            logger.error(f"❌ Lightweight personalized outfit generation failed: {e}")
            
            # Emergency fallback
            if self.fallback_to_original:
                try:
                    base_outfits = await self._generate_base_outfits(
                        base_outfit_generation_func, generation_context
                    )
                    return LightweightOutfitResult(
                        outfits=base_outfits[:self.max_personalized_outfits],
                        personalization_applied=False,
                        strategy_used="emergency_fallback",
                        personalization_score=0.0,
                        confidence=0.5,
                        metadata={"error": str(e), "emergency_fallback": True}
                    )
                except Exception as fallback_error:
                    logger.error(f"❌ Emergency fallback also failed: {fallback_error}")
            
            return LightweightOutfitResult(
                outfits=[],
                personalization_applied=False,
                strategy_used="none",
                personalization_score=0.0,
                confidence=0.0,
                metadata={"error": str(e)}
            )
        
        finally:
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Lightweight personalized outfit generation completed in {generation_time:.2f}s")
    
    async def _ensure_user_embedding(self, user_id: str, user_wardrobe: List[Dict[str, Any]] = None):
        """Ensure user has an embedding, create one if needed"""
        
        user_stats = self.embedding_service.get_user_embedding_stats(user_id)
        
        if not user_stats["has_embedding"]:
            logger.info(f"Creating initial lightweight embedding for user {user_id}")
            
            # Use wardrobe items to create initial embedding
            initial_items = user_wardrobe[:10] if user_wardrobe else []  # Use first 10 items
            
            await self.embedding_service.generate_user_embedding(user_id, initial_items)
            logger.info(f"✅ Created initial lightweight embedding for user {user_id}")
        else:
            logger.info(f"User {user_id} already has lightweight embedding")
    
    async def _generate_base_outfits(
        self, 
        base_outfit_generation_func, 
        generation_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate base outfits using the existing system"""
        
        try:
            # Call the base outfit generation function
            result = await base_outfit_generation_func()
            
            # Extract outfits from result
            if isinstance(result, dict):
                outfits = result.get('outfits', []) or result.get('items', [])
            elif isinstance(result, list):
                outfits = result
            else:
                outfits = []
            
            logger.info(f"Generated {len(outfits)} base outfits")
            return outfits
            
        except Exception as e:
            logger.error(f"❌ Base outfit generation failed: {e}")
            return []
    
    async def _apply_personalization(
        self,
        user_id: str,
        base_outfits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> LightweightOutfitResult:
        """Apply personalization to base outfits"""
        
        try:
            # Generate personalized recommendations
            recommendation_result = await self.recommendation_engine.generate_personalized_outfits(
                user_id=user_id,
                base_outfits=base_outfits,
                context=context,
                max_outfits=self.max_personalized_outfits
            )
            
            # Convert to LightweightOutfitResult
            return LightweightOutfitResult(
                outfits=recommendation_result.outfits,
                personalization_applied=True,
                strategy_used=recommendation_result.strategy_used.value,
                personalization_score=recommendation_result.personalization_score,
                confidence=recommendation_result.confidence,
                metadata=recommendation_result.metadata
            )
            
        except Exception as e:
            logger.error(f"❌ Personalization failed: {e}")
            raise e
    
    async def record_outfit_interaction(
        self,
        user_id: str,
        outfit_id: str,
        interaction_type: str,
        rating: Optional[float] = None
    ) -> bool:
        """Record user interaction with an outfit"""
        
        try:
            interaction = UserInteraction(
                user_id=user_id,
                outfit_id=outfit_id,
                interaction_type=interaction_type,
                rating=rating
            )
            
            success = await self.recommendation_engine.record_user_interaction(
                user_id, interaction
            )
            
            if success:
                logger.info(f"✅ Recorded {interaction_type} interaction for user {user_id}")
            else:
                logger.warning(f"⚠️ Failed to record {interaction_type} interaction for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
            return False
    
    async def record_item_interaction(
        self,
        user_id: str,
        item_id: str,
        interaction_type: str,
        rating: Optional[float] = None
    ) -> bool:
        """Record user interaction with an item"""
        
        try:
            interaction = UserInteraction(
                user_id=user_id,
                item_id=item_id,
                interaction_type=interaction_type,
                rating=rating
            )
            
            success = await self.recommendation_engine.record_user_interaction(
                user_id, interaction
            )
            
            if success:
                logger.info(f"✅ Recorded {interaction_type} interaction for item {item_id}")
            else:
                logger.warning(f"⚠️ Failed to record {interaction_type} interaction for item {item_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to record item interaction: {e}")
            return False
    
    def get_personalization_status(self, user_id: str) -> Dict[str, Any]:
        """Get personalization status for a user"""
        
        user_stats = self.embedding_service.get_user_embedding_stats(user_id)
        recommendation_analytics = self.recommendation_engine.get_recommendation_analytics(user_id)
        
        return {
            "user_id": user_id,
            "personalization_enabled": self.enable_personalization,
            "has_user_embedding": user_stats["has_embedding"],
            "total_interactions": user_stats["total_interactions"],
            "recommended_strategy": recommendation_analytics["recommended_strategy"],
            "personalization_score": recommendation_analytics.get("personalization_score", 0.0),
            "confidence": recommendation_analytics.get("confidence", 0.0),
            "system_parameters": {
                "personalization_weight": self.recommendation_engine.personalization_weight,
                "exploration_rate": self.recommendation_engine.exploration_rate,
                "min_similarity_threshold": self.recommendation_engine.min_similarity_threshold
            }
        }
    
    def update_personalization_settings(
        self,
        enable_personalization: Optional[bool] = None,
        max_personalized_outfits: Optional[int] = None,
        personalization_weight: Optional[float] = None,
        exploration_rate: Optional[float] = None
    ):
        """Update personalization settings"""
        
        if enable_personalization is not None:
            self.enable_personalization = enable_personalization
        
        if max_personalized_outfits is not None:
            self.max_personalized_outfits = max(1, max_personalized_outfits)
        
        if personalization_weight is not None:
            self.recommendation_engine.update_recommendation_parameters(
                personalization_weight=personalization_weight
            )
        
        if exploration_rate is not None:
            self.recommendation_engine.update_recommendation_parameters(
                exploration_rate=exploration_rate
            )
        
        logger.info(f"✅ Updated lightweight personalization settings: enabled={self.enable_personalization}, max_outfits={self.max_personalized_outfits}")
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get overall system analytics"""
        
        embedding_stats = self.embedding_service.get_system_stats()
        
        return {
            "embedding_service": embedding_stats,
            "personalization_enabled": self.enable_personalization,
            "fallback_enabled": self.fallback_to_original,
            "max_personalized_outfits": self.max_personalized_outfits,
            "recommendation_parameters": {
                "personalization_weight": self.recommendation_engine.personalization_weight,
                "exploration_rate": self.recommendation_engine.exploration_rate,
                "min_similarity_threshold": self.recommendation_engine.min_similarity_threshold
            }
        }
