#!/usr/bin/env python3
"""
Lightweight Embedding Service - No External Dependencies
=======================================================

This service provides vector embeddings and personalized recommendations
without requiring external services like OpenAI or vector databases.

Features:
- Simple hash-based embeddings (no external API calls)
- In-memory storage with JSON persistence
- Cosine similarity using pure Python
- Personalized recommendations based on user preferences
- Lightweight and production-ready
"""

import logging
import json
import hashlib
import math
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)

class EmbeddingType(Enum):
    """Types of embeddings"""
    ITEM = "item"
    OUTFIT = "outfit"
    USER = "user"

@dataclass
class LightweightEmbedding:
    """Lightweight embedding data structure"""
    id: str
    type: EmbeddingType
    vector: List[float]
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

class LightweightEmbeddingService:
    """
    Lightweight embedding service that works without external dependencies
    """
    
    def __init__(self, storage_file: str = "embeddings.json"):
        self.embedding_dimension = 64  # Smaller dimension for efficiency
        self.storage_file = storage_file
        
        # In-memory storage
        self.embeddings: Dict[str, LightweightEmbedding] = {}
        self.user_embeddings: Dict[str, List[float]] = {}
        self.user_interactions: List[UserInteraction] = []
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.1
        
        # Load existing data
        self._load_data()
        
        logger.info("✅ Lightweight Embedding Service initialized")
    
    def _load_data(self):
        """Load embeddings from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                # Load embeddings
                for embedding_id, embedding_data in (data.get('embeddings', {}) if data else {}).items():
                    self.embeddings[embedding_id] = LightweightEmbedding(
                        id=embedding_data['id'],
                        type=EmbeddingType(embedding_data['type']),
                        vector=embedding_data['vector'],
                        metadata=embedding_data['metadata'],
                        created_at=embedding_data['created_at'],
                        updated_at=embedding_data['updated_at'],
                        version=(embedding_data.get('version', 1) if embedding_data else 1)
                    )
                
                # Load user embeddings
                self.user_embeddings = (data.get('user_embeddings', {}) if data else {})
                
                # Load interactions
                interactions_data = (data.get('interactions', []) if data else [])
                self.user_interactions = [
                    UserInteraction(**interaction) for interaction in interactions_data
                ]
                
                logger.info(f"✅ Loaded {len(self.embeddings)} embeddings and {len(self.user_embeddings)} user embeddings")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load data: {e}")
    
    def _save_data(self):
        """Save embeddings to storage file"""
        try:
            data = {
                'embeddings': {
                    embedding_id: {
                        'id': embedding.id,
                        'type': embedding.type.value,
                        'vector': embedding.vector,
                        'metadata': embedding.metadata,
                        'created_at': embedding.created_at,
                        'updated_at': embedding.updated_at,
                        'version': embedding.version
                    }
                    for embedding_id, embedding in self.embeddings.items()
                },
                'user_embeddings': self.user_embeddings,
                'interactions': [
                    {
                        'user_id': interaction.user_id,
                        'item_id': interaction.item_id,
                        'outfit_id': interaction.outfit_id,
                        'interaction_type': interaction.interaction_type,
                        'rating': interaction.rating,
                        'timestamp': interaction.timestamp
                    }
                    for interaction in self.user_interactions
                ]
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}")
    
    def _create_lightweight_embedding(self, text: str, item_type: str = "item") -> List[float]:
        """Create a lightweight embedding using hash-based approach"""
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to vector
        vector = []
        for i in range(0, len(text_hash), 2):
            # Convert hex pairs to normalized floats
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            vector.append(value)
        
        # Pad or truncate to desired dimension
        while len(vector) < self.embedding_dimension:
            vector.append(0.0)
        
        vector = vector[:self.embedding_dimension]
        
        # Add some semantic weighting based on item type
        if item_type == "outfit":
            # Boost outfit embeddings slightly
            vector = [v * 1.1 for v in vector]
        elif item_type == "user":
            # User embeddings get different weighting
            vector = [v * 0.9 for v in vector]
        
        return vector
    
    async def generate_item_embedding(self, item: Dict[str, Any]) -> List[float]:
        """Generate embedding for a wardrobe item"""
        try:
            # Create rich text representation
            item_text = self._create_item_text_representation(item)
            
            # Generate lightweight embedding
            embedding = self._create_lightweight_embedding(item_text, "item")
            
            # Store embedding
            item_id = (item.get('id', f"item_{int(time.time())}") if item else f"item_{int(time.time())}")
            self.embeddings[item_id] = LightweightEmbedding(
                id=item_id,
                type=EmbeddingType.ITEM,
                vector=embedding,
                metadata={
                    "name": (item.get('name', 'Unknown') if item else 'Unknown'),
                    "type": (item.get('type', 'unknown') if item else 'unknown'),
                    "color": (item.get('color', 'unknown') if item else 'unknown'),
                    "style": (item.get('style', []) if item else []),
                    "occasion": (item.get('occasion', []) if item else [])
                },
                created_at=time.time(),
                updated_at=time.time()
            )
            
            logger.info(f"✅ Generated lightweight item embedding for {(item.get('name', 'Unknown') if item else 'Unknown')}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate item embedding: {e}")
            # Return random embedding as fallback
            return [0.0] * self.embedding_dimension
    
    async def generate_outfit_embedding(self, outfit: Dict[str, Any]) -> List[float]:
        """Generate embedding for an outfit"""
        try:
            # Create rich text representation
            outfit_text = self._create_outfit_text_representation(outfit)
            
            # Generate lightweight embedding
            embedding = self._create_lightweight_embedding(outfit_text, "outfit")
            
            # Store embedding
            outfit_id = (outfit.get('id', f"outfit_{int(time.time() if outfit else f"outfit_{int(time.time())}")
            self.embeddings[outfit_id] = LightweightEmbedding(
                id=outfit_id,
                type=EmbeddingType.OUTFIT,
                vector=embedding,
                metadata={
                    "name": (outfit.get('name', 'Unknown Outfit') if outfit else 'Unknown Outfit'),
                    "style": (outfit.get('style', 'unknown') if outfit else 'unknown'),
                    "occasion": (outfit.get('occasion', 'unknown') if outfit else 'unknown'),
                    "mood": (outfit.get('mood', 'unknown') if outfit else 'unknown'),
                    "items_count": len((outfit.get('items', []) if outfit else []))
                },
                created_at=time.time(),
                updated_at=time.time()
            )
            
            logger.info(f"✅ Generated lightweight outfit embedding for {(outfit.get('name', 'Unknown Outfit') if outfit else 'Unknown Outfit')}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate outfit embedding: {e}")
            # Return random embedding as fallback
            return [0.0] * self.embedding_dimension
    
    async def generate_user_embedding(self, user_id: str, initial_items: List[Dict[str, Any]] = None) -> List[float]:
        """Generate initial user embedding based on their wardrobe"""
        try:
            if initial_items and len(initial_items) > 0:
                # Generate embeddings for user's initial items
                item_embeddings = []
                for item in initial_items[:10]:  # Limit to first 10 items
                    item_embedding = await self.generate_item_embedding(item)
                    item_embeddings.append(item_embedding)
                
                # Average the item embeddings to create user embedding
                if item_embeddings:
                    user_embedding = [
                        sum(emb[i] for emb in item_embeddings) / len(item_embeddings)
                        for i in range(self.embedding_dimension)
                    ]
                else:
                    user_embedding = [0.0] * self.embedding_dimension
                
                logger.info(f"✅ Generated user embedding from {len(initial_items)} items")
            else:
                # Create neutral embedding
                user_embedding = [0.0] * self.embedding_dimension
                logger.info(f"✅ Generated neutral user embedding")
            
            # Store user embedding
            self.user_embeddings[user_id] = user_embedding
            self._save_data()
            
            return user_embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate user embedding: {e}")
            # Return neutral embedding as fallback
            return [0.0] * self.embedding_dimension
    
    async def update_user_embedding(self, user_id: str, interaction: UserInteraction) -> List[float]:
        """Update user embedding based on interaction"""
        try:
            # Get current user embedding
            current_embedding = self.(user_embeddings.get(user_id, [0.0] * self.embedding_dimension) if user_embeddings else [0.0] * self.embedding_dimension)
            
            # Get item/outfit embedding
            if interaction.item_id and interaction.item_id in self.embeddings:
                item_embedding = self.embeddings[interaction.item_id].vector
            elif interaction.outfit_id and interaction.outfit_id in self.embeddings:
                item_embedding = self.embeddings[interaction.outfit_id].vector
            else:
                logger.warning(f"No embedding found for interaction")
                return current_embedding
            
            # Determine learning rate based on interaction type and rating
            alpha = self._calculate_learning_rate(interaction)
            
            # Update embedding using moving average
            new_embedding = [
                alpha * item_embedding[i] + (1 - alpha) * current_embedding[i]
                for i in range(self.embedding_dimension)
            ]
            
            # Normalize the embedding
            magnitude = math.sqrt(sum(x**2 for x in new_embedding))
            if magnitude > 0:
                new_embedding = [x / magnitude for x in new_embedding]
            
            # Update stored embedding
            self.user_embeddings[user_id] = new_embedding
            
            # Store interaction
            self.user_interactions.append(interaction)
            
            # Save data
            self._save_data()
            
            logger.info(f"✅ Updated user embedding for {user_id} with {interaction.interaction_type}")
            return new_embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to update user embedding: {e}")
            return self.(user_embeddings.get(user_id, [0.0] * self.embedding_dimension) if user_embeddings else [0.0] * self.embedding_dimension)
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        candidate_outfits: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Get personalized outfit recommendations based on cosine similarity"""
        try:
            # Get user embedding
            user_embedding = self.(user_embeddings.get(user_id) if user_embeddings else None)
            if not user_embedding:
                logger.warning(f"No user embedding found for {user_id}")
                return candidate_outfits[:top_k]
            
            # Calculate similarities
            similarities = []
            for outfit in candidate_outfits:
                # Get or generate outfit embedding
                outfit_embedding = await self._get_outfit_embedding((outfit.get('id', '') if outfit else ''))
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(user_embedding, outfit_embedding)
                
                similarities.append({
                    'outfit': outfit,
                    'similarity': similarity,
                    'outfit_id': (outfit.get('id', '') if outfit else '')
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Apply exploration (occasionally recommend slightly different outfits)
            if self._should_explore():
                # Shuffle top 50% to introduce some exploration
                mid_point = len(similarities) // 2
                top_half = similarities[:mid_point]
                bottom_half = similarities[mid_point:]
                import random
                random.shuffle(top_half)
                similarities = top_half + bottom_half
            
            # Return top-k recommendations
            recommendations = similarities[:top_k]
            
            logger.info(f"✅ Generated {len(recommendations)} personalized recommendations for {user_id}")
            return [rec['outfit'] for rec in recommendations]
            
        except Exception as e:
            logger.error(f"❌ Failed to get personalized recommendations: {e}")
            return candidate_outfits[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a**2 for a in vec1))
        magnitude2 = math.sqrt(sum(b**2 for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _should_explore(self) -> bool:
        """Determine if we should explore (random choice)"""
        import random
        return random.random() < self.exploration_rate
    
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
    
    def _create_item_text_representation(self, item: Dict[str, Any]) -> str:
        """Create rich text representation of an item for embedding"""
        parts = []
        
        # Basic information
        parts.append(f"Item: {(item.get('name', 'Unknown') if item else 'Unknown')}")
        parts.append(f"Type: {(item.get('type', 'unknown') if item else 'unknown')}")
        parts.append(f"Color: {(item.get('color', 'unknown') if item else 'unknown')}")
        
        # Style information
        styles = (item.get('style', []) if item else [])
        if styles:
            parts.append(f"Styles: {', '.join(styles)}")
        
        # Occasion information
        occasions = (item.get('occasion', []) if item else [])
        if occasions:
            parts.append(f"Occasions: {', '.join(occasions)}")
        
        # Material and texture
        material = (item.get('material', '') if item else '')
        if material:
            parts.append(f"Material: {material}")
        
        # Brand information
        brand = (item.get('brand', '') if item else '')
        if brand:
            parts.append(f"Brand: {brand}")
        
        return " | ".join(parts)
    
    def _create_outfit_text_representation(self, outfit: Dict[str, Any]) -> str:
        """Create rich text representation of an outfit for embedding"""
        parts = []
        
        # Basic outfit information
        parts.append(f"Outfit: {(outfit.get('name', 'Unknown Outfit') if outfit else 'Unknown Outfit')}")
        parts.append(f"Style: {(outfit.get('style', 'unknown') if outfit else 'unknown')}")
        parts.append(f"Occasion: {(outfit.get('occasion', 'unknown') if outfit else 'unknown')}")
        parts.append(f"Mood: {(outfit.get('mood', 'unknown') if outfit else 'unknown')}")
        
        # Items in the outfit
        items = (outfit.get('items', []) if outfit else [])
        if items:
            item_descriptions = []
            for item in items:
                item_desc = f"{(((item.get('name', 'Unknown') if item else 'Unknown') if item else 'Unknown') if item else 'Unknown')} ({item.get('type', 'unknown')}, {item.get('color', 'unknown')})"
                item_descriptions.append(item_desc)
            parts.append(f"Items: {', '.join(item_descriptions)}")
        
        # Color palette
        colors = []
        for item in items:
            color = (item.get('color', '') if item else '')
            if color and color not in colors:
                colors.append(color)
        if colors:
            parts.append(f"Color palette: {', '.join(colors)}")
        
        return " | ".join(parts)
    
    async def _get_outfit_embedding(self, outfit_id: str) -> List[float]:
        """Get outfit embedding from storage or generate new one"""
        if outfit_id in self.embeddings:
            return self.embeddings[outfit_id].vector
        else:
            # Return neutral embedding if not found
            return [0.0] * self.embedding_dimension
    
    def get_user_embedding_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's embedding and interactions"""
        user_embedding = self.(user_embeddings.get(user_id) if user_embeddings else None)
        user_interactions = [i for i in self.user_interactions if i.user_id == user_id]
        
        return {
            "user_id": user_id,
            "has_embedding": user_embedding is not None,
            "embedding_dimension": self.embedding_dimension if user_embedding else 0,
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
            "exploration_rate": self.exploration_rate,
            "storage_file": self.storage_file
        }
