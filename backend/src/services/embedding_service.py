#!/usr/bin/env python3
"""
Embedding Service - Vector Embeddings for Personalized Recommendations
====================================================================

This service implements vector embeddings for users and outfits/items to enable
personalized recommendations based on semantic similarity.

Core Features:
- Generate embeddings for wardrobe items and outfits
- Update user embeddings based on interactions
- Compute cosine similarity for recommendations
- Continuous learning and adaptation
- Integration with existing outfit generation system
"""

import logging
import numpy as np
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import openai
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)

class EmbeddingType(Enum):
    """Types of embeddings"""
    ITEM = "item"
    OUTFIT = "outfit"
    USER = "user"

@dataclass
class EmbeddingData:
    """Embedding data structure"""
    id: str
    type: EmbeddingType
    vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: float
    updated_at: float
    version: int = 1

@dataclass
class UserInteraction:
    """User interaction data for embedding updates"""
    user_id: str
    item_id: Optional[str] = None
    outfit_id: Optional[str] = None
    interaction_type: str = "view"  # view, like, wear, dislike
    rating: Optional[float] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class EmbeddingService:
    """
    Service for generating and managing vector embeddings for personalized recommendations
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or "your-openai-api-key"
        self.embedding_dimension = 1536  # OpenAI text-embedding-ada-002 dimension
        
        # Initialize OpenAI client
        if self.openai_api_key and self.openai_api_key != "your-openai-api-key":
            openai.api_key = self.openai_api_key
        
        # In-memory storage for demo (replace with vector database in production)
        self.embeddings: Dict[str, EmbeddingData] = {}
        self.user_embeddings: Dict[str, np.ndarray] = {}
        
        # Learning parameters
        self.learning_rate = 0.1  # α in the moving average formula
        self.exploration_rate = 0.1  # ε for exploration vs exploitation
        
        # Interaction tracking
        self.user_interactions: List[UserInteraction] = []
        
        logger.info("✅ Embedding Service initialized")
    
    async def generate_item_embedding(self, item: Dict[str, Any]) -> np.ndarray:
        """
        Generate embedding for a wardrobe item
        
        Creates a rich text representation of the item including:
        - Type, color, style, material
        - Occasion, season, formality
        - Brand, fit, and other metadata
        """
        try:
            # Create rich text representation for embedding
            item_text = self._create_item_text_representation(item)
            
            # Generate embedding using OpenAI API
            embedding = await self._generate_embedding_with_openai(item_text)
            
            logger.info(f"✅ Generated item embedding for {item.get('name', 'Unknown')}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate item embedding: {e}")
            # Return random embedding as fallback
            return np.random.normal(0, 1, self.embedding_dimension)
    
    async def generate_outfit_embedding(self, outfit: Dict[str, Any]) -> np.ndarray:
        """
        Generate embedding for an outfit
        
        Creates a rich text representation of the outfit including:
        - All items and their properties
        - Overall style, color harmony, occasion
        - Weather appropriateness, formality level
        """
        try:
            # Create rich text representation for embedding
            outfit_text = self._create_outfit_text_representation(outfit)
            
            # Generate embedding using OpenAI API
            embedding = await self._generate_embedding_with_openai(outfit_text)
            
            logger.info(f"✅ Generated outfit embedding for {outfit.get('name', 'Unknown Outfit')}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate outfit embedding: {e}")
            # Return random embedding as fallback
            return np.random.normal(0, 1, self.embedding_dimension)
    
    async def generate_user_embedding(self, user_id: str, initial_items: List[Dict[str, Any]] = None) -> np.ndarray:
        """
        Generate initial user embedding based on their wardrobe and preferences
        
        If no initial items provided, creates a neutral embedding
        """
        try:
            if initial_items and len(initial_items) > 0:
                # Generate embeddings for user's initial items
                item_embeddings = []
                for item in initial_items:
                    item_embedding = await self.generate_item_embedding(item)
                    item_embeddings.append(item_embedding)
                
                # Average the item embeddings to create user embedding
                user_embedding = np.mean(item_embeddings, axis=0)
                logger.info(f"✅ Generated user embedding from {len(initial_items)} items")
            else:
                # Create neutral embedding
                user_embedding = np.zeros(self.embedding_dimension)
                logger.info(f"✅ Generated neutral user embedding")
            
            # Store user embedding
            self.user_embeddings[user_id] = user_embedding
            
            return user_embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate user embedding: {e}")
            # Return neutral embedding as fallback
            return np.zeros(self.embedding_dimension)
    
    async def update_user_embedding(self, user_id: str, interaction: UserInteraction) -> np.ndarray:
        """
        Update user embedding based on interaction using moving average
        
        Formula: u_new = α * o + (1 - α) * u_old
        """
        try:
            # Get current user embedding
            current_embedding = self.user_embeddings.get(user_id, np.zeros(self.embedding_dimension))
            
            # Get item/outfit embedding
            if interaction.item_id:
                item_embedding = await self._get_item_embedding(interaction.item_id)
            elif interaction.outfit_id:
                outfit_embedding = await self._get_outfit_embedding(interaction.outfit_id)
            else:
                logger.warning(f"No item_id or outfit_id provided for interaction")
                return current_embedding
            
            # Determine learning rate based on interaction type and rating
            alpha = self._calculate_learning_rate(interaction)
            
            # Update embedding using moving average
            if interaction.item_id:
                new_embedding = alpha * item_embedding + (1 - alpha) * current_embedding
            else:
                new_embedding = alpha * outfit_embedding + (1 - alpha) * current_embedding
            
            # Normalize the embedding
            new_embedding = normalize([new_embedding])[0]
            
            # Update stored embedding
            self.user_embeddings[user_id] = new_embedding
            
            # Store interaction for analysis
            self.user_interactions.append(interaction)
            
            logger.info(f"✅ Updated user embedding for {user_id} with {interaction.interaction_type}")
            return new_embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to update user embedding: {e}")
            return self.user_embeddings.get(user_id, np.zeros(self.embedding_dimension))
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        candidate_outfits: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized outfit recommendations based on cosine similarity
        
        Returns outfits ranked by similarity to user embedding
        """
        try:
            # Get user embedding
            user_embedding = self.user_embeddings.get(user_id)
            if user_embedding is None:
                logger.warning(f"No user embedding found for {user_id}")
                return candidate_outfits[:top_k]
            
            # Calculate similarities
            similarities = []
            for outfit in candidate_outfits:
                # Get or generate outfit embedding
                outfit_embedding = await self._get_outfit_embedding(outfit.get('id', ''))
                
                # Calculate cosine similarity
                similarity = cosine_similarity([user_embedding], [outfit_embedding])[0][0]
                
                similarities.append({
                    'outfit': outfit,
                    'similarity': similarity,
                    'outfit_id': outfit.get('id', '')
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Apply exploration (occasionally recommend slightly different outfits)
            if np.random.random() < self.exploration_rate:
                # Shuffle top 50% to introduce some exploration
                mid_point = len(similarities) // 2
                top_half = similarities[:mid_point]
                bottom_half = similarities[mid_point:]
                np.random.shuffle(top_half)
                similarities = top_half + bottom_half
            
            # Return top-k recommendations
            recommendations = similarities[:top_k]
            
            logger.info(f"✅ Generated {len(recommendations)} personalized recommendations for {user_id}")
            return [rec['outfit'] for rec in recommendations]
            
        except Exception as e:
            logger.error(f"❌ Failed to get personalized recommendations: {e}")
            return candidate_outfits[:top_k]
    
    def _create_item_text_representation(self, item: Dict[str, Any]) -> str:
        """Create rich text representation of an item for embedding"""
        parts = []
        
        # Basic information
        parts.append(f"Item: {item.get('name', 'Unknown')}")
        parts.append(f"Type: {item.get('type', 'unknown')}")
        parts.append(f"Color: {item.get('color', 'unknown')}")
        
        # Style information
        styles = item.get('style', [])
        if styles:
            parts.append(f"Styles: {', '.join(styles)}")
        
        # Occasion information
        occasions = item.get('occasion', [])
        if occasions:
            parts.append(f"Occasions: {', '.join(occasions)}")
        
        # Material and texture
        material = item.get('material', '')
        if material:
            parts.append(f"Material: {material}")
        
        # Season information
        seasons = item.get('season', [])
        if seasons:
            parts.append(f"Seasons: {', '.join(seasons)}")
        
        # Brand information
        brand = item.get('brand', '')
        if brand:
            parts.append(f"Brand: {brand}")
        
        # Additional metadata
        metadata = item.get('metadata', {})
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float)):
                    parts.append(f"{key}: {value}")
        
        return " | ".join(parts)
    
    def _create_outfit_text_representation(self, outfit: Dict[str, Any]) -> str:
        """Create rich text representation of an outfit for embedding"""
        parts = []
        
        # Basic outfit information
        parts.append(f"Outfit: {outfit.get('name', 'Unknown Outfit')}")
        parts.append(f"Style: {outfit.get('style', 'unknown')}")
        parts.append(f"Occasion: {outfit.get('occasion', 'unknown')}")
        parts.append(f"Mood: {outfit.get('mood', 'unknown')}")
        
        # Items in the outfit
        items = outfit.get('items', [])
        if items:
            item_descriptions = []
            for item in items:
                item_desc = f"{item.get('name', 'Unknown')} ({item.get('type', 'unknown')}, {item.get('color', 'unknown')})"
                item_descriptions.append(item_desc)
            parts.append(f"Items: {', '.join(item_descriptions)}")
        
        # Color palette
        colors = []
        for item in items:
            color = item.get('color', '')
            if color and color not in colors:
                colors.append(color)
        if colors:
            parts.append(f"Color palette: {', '.join(colors)}")
        
        # Weather information
        weather = outfit.get('weather', {})
        if weather:
            temp = weather.get('temperature', '')
            condition = weather.get('condition', '')
            if temp and condition:
                parts.append(f"Weather: {temp}°F, {condition}")
        
        # Formality level
        formality = outfit.get('formality', '')
        if formality:
            parts.append(f"Formality: {formality}")
        
        # Confidence and quality scores
        confidence = outfit.get('confidence', '')
        if confidence:
            parts.append(f"Confidence: {confidence}")
        
        return " | ".join(parts)
    
    async def _generate_embedding_with_openai(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI API"""
        try:
            if self.openai_api_key == "your-openai-api-key":
                # Fallback to random embedding for demo
                logger.warning("Using random embedding (OpenAI API key not configured)")
                return np.random.normal(0, 1, self.embedding_dimension)
            
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            
            return np.array(response['data'][0]['embedding'])
            
        except Exception as e:
            logger.error(f"❌ OpenAI embedding generation failed: {e}")
            # Return random embedding as fallback
            return np.random.normal(0, 1, self.embedding_dimension)
    
    def _calculate_learning_rate(self, interaction: UserInteraction) -> float:
        """Calculate learning rate based on interaction type and rating"""
        base_learning_rate = self.learning_rate
        
        # Adjust based on interaction type
        if interaction.interaction_type == "like":
            base_learning_rate *= 1.5
        elif interaction.interaction_type == "wear":
            base_learning_rate *= 2.0
        elif interaction.interaction_type == "dislike":
            base_learning_rate *= 0.5
        
        # Adjust based on rating
        if interaction.rating is not None:
            if interaction.rating >= 4.0:
                base_learning_rate *= 1.5
            elif interaction.rating <= 2.0:
                base_learning_rate *= 0.5
        
        return min(base_learning_rate, 0.5)  # Cap at 0.5
    
    async def _get_item_embedding(self, item_id: str) -> np.ndarray:
        """Get item embedding from storage or generate new one"""
        # In production, this would query a vector database
        # For now, return random embedding
        return np.random.normal(0, 1, self.embedding_dimension)
    
    async def _get_outfit_embedding(self, outfit_id: str) -> np.ndarray:
        """Get outfit embedding from storage or generate new one"""
        # In production, this would query a vector database
        # For now, return random embedding
        return np.random.normal(0, 1, self.embedding_dimension)
    
    def get_user_embedding_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's embedding and interactions"""
        user_embedding = self.user_embeddings.get(user_id)
        user_interactions = [i for i in self.user_interactions if i.user_id == user_id]
        
        return {
            "user_id": user_id,
            "has_embedding": user_embedding is not None,
            "embedding_dimension": self.embedding_dimension if user_embedding is not None else 0,
            "total_interactions": len(user_interactions),
            "interaction_types": {
                interaction_type: len([i for i in user_interactions if i.interaction_type == interaction_type])
                for interaction_type in set(i.interaction_type for i in user_interactions)
            },
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        return {
            "total_embeddings": len(self.embeddings),
            "total_users": len(self.user_embeddings),
            "total_interactions": len(self.user_interactions),
            "embedding_dimension": self.embedding_dimension,
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate
        }
