"""
Diversity Filter Service - Prevents repetitive outfit recommendations
Implements similarity detection and rotation system for wardrobe diversity.
"""

import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
import logging
from ..custom_types.wardrobe import ClothingItem

logger = logging.getLogger(__name__)

# Import Firebase
try:
    from ..config.firebase import db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("⚠️ Firebase not available for diversity filtering")

@dataclass
class OutfitSimilarity:
    """Represents similarity between two outfits"""
    outfit1_id: str
    outfit2_id: str
    similarity_score: float
    common_items: List[str]
    different_items: List[str]
    similarity_type: str  # "exact", "high", "medium", "low"

@dataclass
class DiversityMetrics:
    """Metrics for outfit diversity analysis"""
    total_outfits: int
    unique_combinations: int
    similarity_threshold: float
    rotation_effectiveness: float
    diversity_score: float
    recent_repetitions: int

class DiversityFilterService:
    """Service for ensuring outfit diversity and preventing repetitive recommendations"""
    
    def __init__(self):
        self.outfit_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.item_usage_count: Dict[str, int] = defaultdict(int)
        self.outfit_similarities: List[OutfitSimilarity] = []
        self.rotation_schedule: Dict[str, List[str]] = defaultdict(list)
        
        # Configuration
        self.similarity_threshold = 0.7  # Outfits with >70% similarity are considered too similar
        self.max_recent_outfits = 50  # Keep track of last 50 outfits per user
        self.rotation_period_days = 7  # Rotate items every 7 days
        self.diversity_boost_factor = 1.5  # Boost score for diverse items
        
        logger.info("🎭 Diversity Filter Service initialized")
    
    def calculate_outfit_similarity(self, outfit1: List[ClothingItem], outfit2: List[ClothingItem]) -> float:
        """Calculate similarity score between two outfits (0.0 = completely different, 1.0 = identical)"""
        
        if not outfit1 or not outfit2:
            return 0.0
        
        # Extract item IDs
        items1 = {item.id for item in outfit1}
        items2 = {item.id for item in outfit2}
        
        # Calculate Jaccard similarity
        intersection = len(items1 & items2)
        union = len(items1 | items2)
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Calculate type similarity
        types1 = {item.type for item in outfit1}
        types2 = {item.type for item in outfit2}
        type_intersection = len(types1 & types2)
        type_union = len(types1 | types2)
        type_similarity = type_intersection / type_union if type_union > 0 else 0.0
        
        # Calculate color similarity
        colors1 = {item.color for item in outfit1}
        colors2 = {item.color for item in outfit2}
        color_intersection = len(colors1 & colors2)
        color_union = len(colors1 | colors2)
        color_similarity = color_intersection / color_union if color_union > 0 else 0.0
        
        # Calculate style similarity
        styles1 = set()
        styles2 = set()
        for item in outfit1:
            styles1.update(item.style or [])
        for item in outfit2:
            styles2.update(item.style or [])
        
        style_intersection = len(styles1 & styles2)
        style_union = len(styles1 | styles2)
        style_similarity = style_intersection / style_union if style_union > 0 else 0.0
        
        # Weighted combination
        similarity_score = (
            jaccard_similarity * 0.4 +      # Item overlap (most important)
            type_similarity * 0.3 +         # Type similarity
            color_similarity * 0.2 +        # Color similarity
            style_similarity * 0.1          # Style similarity
        )
        
        return min(max(similarity_score, 0.0), 1.0)
    
    def _load_outfit_history_from_firestore(self, user_id: str) -> List[Dict[str, Any]]:
        """Load outfit history from Firestore for diversity checking"""
        
        if not FIREBASE_AVAILABLE:
            logger.warning("⚠️ Firebase not available, using in-memory history only")
            return self.outfit_history[user_id]
        
        try:
            # Query recent outfits from Firestore (last 50)
            outfits_ref = db.collection('outfits')\
                .where('user_id', '==', user_id)\
                .order_by('createdAt', direction='DESCENDING')\
                .limit(self.max_recent_outfits)
            
            docs = outfits_ref.stream()
            firestore_outfits = []
            
            for doc in docs:
                outfit_data = doc.to_dict()
                # Convert items to ClothingItem objects if they're dicts
                items = outfit_data.get('items', [])
                clothing_items = []
                
                for item in items:
                    if isinstance(item, dict):
                        # Create ClothingItem from dict
                        try:
                            clothing_item = ClothingItem(**item)
                            clothing_items.append(clothing_item)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to convert item to ClothingItem: {e}")
                            # Skip items that can't be converted
                            continue
                    elif isinstance(item, ClothingItem):
                        clothing_items.append(item)
                
                firestore_outfits.append({
                    'id': doc.id,
                    'items': clothing_items,
                    'occasion': outfit_data.get('occasion', 'unknown'),
                    'style': outfit_data.get('style', 'unknown'),
                    'mood': outfit_data.get('mood', 'unknown'),
                    'createdAt': outfit_data.get('createdAt', 0),
                    'confidence': outfit_data.get('confidence', 0.0)
                })
            
            logger.info(f"📊 Loaded {len(firestore_outfits)} outfits from Firestore for user {user_id}")
            return firestore_outfits
            
        except Exception as e:
            logger.error(f"❌ Failed to load outfit history from Firestore: {e}")
            return self.outfit_history[user_id]
    
    def check_outfit_diversity(self, user_id: str, new_outfit: List[ClothingItem], 
                             occasion: str, style: str, mood: str) -> Dict[str, Any]:
        """Check if a new outfit is diverse enough compared to recent outfits"""
        
        # Load outfit history from Firestore if in-memory cache is empty
        if not self.outfit_history[user_id] or len(self.outfit_history[user_id]) < 5:
            logger.info(f"🔄 Loading outfit history from Firestore for user {user_id}")
            firestore_history = self._load_outfit_history_from_firestore(user_id)
            if firestore_history:
                self.outfit_history[user_id] = firestore_history
        
        user_history = self.outfit_history[user_id]
        recent_outfits = user_history[-self.max_recent_outfits:]
        
        diversity_result = {
            "is_diverse": True,
            "similarity_scores": [],
            "most_similar_outfit": None,
            "diversity_score": 1.0,
            "recommendations": [],
            "rotation_suggestions": []
        }
        
        if not recent_outfits:
            return diversity_result
        
        # CRITICAL FIX: Filter to same occasion/style/mood combination
        # Compare apples-to-apples, not all outfits globally
        same_combination_outfits = []
        for i, outfit in enumerate(recent_outfits):
            if outfit:
                # Match by occasion (required) and optionally style/mood
                occasion_match = outfit.get('occasion', '').lower() == occasion.lower()
                style_match = outfit.get('style', '').lower() == style.lower()
                
                # Strict matching: same occasion AND style
                if occasion_match and style_match:
                    same_combination_outfits.append((i, outfit))
        
        logger.info(f"🔍 DIVERSITY: Comparing against {len(same_combination_outfits)} outfits with same combination (occasion={occasion}, style={style})")
        logger.info(f"   Total history: {len(recent_outfits)} outfits, Filtered to same combo: {len(same_combination_outfits)}")
        
        # If no matching combinations found, compare against all (fallback)
        if not same_combination_outfits:
            logger.info(f"⚠️ No matching combinations found, comparing against all recent outfits")
            same_combination_outfits = [(i, outfit) for i, outfit in enumerate(recent_outfits)]
        
        # Calculate similarity with outfits of the SAME combination
        similarities = []
        for i, recent_outfit in same_combination_outfits:
            if recent_outfit and 'items' in recent_outfit:
                recent_items = recent_outfit['items']
                similarity = self.calculate_outfit_similarity(new_outfit, recent_items)
                similarities.append({
                    'index': i,
                    'similarity': similarity,
                    'outfit_id': (recent_outfit.get('id', f'outfit_{i}') if recent_outfit else f'outfit_{i}'),
                    'created_at': (recent_outfit.get('createdAt', 0) if recent_outfit else 0),
                    'occasion': recent_outfit.get('occasion', 'unknown'),
                    'style': recent_outfit.get('style', 'unknown')
                })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        diversity_result['similarity_scores'] = similarities
        
        # Check if too similar to recent outfits
        high_similarity_outfits = [s for s in similarities if s['similarity'] > self.similarity_threshold]
        
        if high_similarity_outfits:
            most_similar = high_similarity_outfits[0]
            diversity_result['is_diverse'] = False
            diversity_result['most_similar_outfit'] = most_similar
            diversity_result['diversity_score'] = 1.0 - most_similar['similarity']
            
            # Log the similarity issue
            logger.warning(f"⚠️ DIVERSITY ALERT: New outfit is {most_similar['similarity']:.1%} similar to recent outfit {most_similar['outfit_id']}")
            logger.warning(f"   Diversity score: {diversity_result['diversity_score']:.2f}")
            
            # Generate recommendations
            diversity_result['recommendations'].append(
                f"Outfit is {most_similar['similarity']:.1%} similar to recent outfit"
            )
            diversity_result['recommendations'].append(
                "Try different colors, styles, or item combinations"
            )
            
            # Check if it's the same occasion/style combination
            if (most_similar['index'] < len(recent_outfits) and 
                recent_outfits[most_similar['index']] and 
                recent_outfits[most_similar['index']].get('occasion') == occasion):
                diversity_result['recommendations'].append(
                    "Consider different items for the same occasion"
                )
        
        # Calculate overall diversity score
        if similarities:
            avg_similarity = sum(s['similarity'] for s in similarities) / len(similarities)
            diversity_result['diversity_score'] = 1.0 - avg_similarity
        
        # Check rotation effectiveness
        rotation_suggestions = self._check_rotation_effectiveness(user_id, new_outfit)
        diversity_result['rotation_suggestions'] = rotation_suggestions
        
        return diversity_result
    
    def _check_rotation_effectiveness(self, user_id: str, new_outfit: List[ClothingItem]) -> List[str]:
        """Check if items are being rotated effectively"""
        suggestions = []
        
        # Check item usage frequency
        for item in new_outfit:
            usage_count = self.item_usage_count[item.id]
            if usage_count > 5:  # Item used more than 5 times recently
                suggestions.append(f"Consider rotating out frequently used item: {item.name}")
        
        # Check if using items from rotation schedule
        user_rotation = self.rotation_schedule[user_id]
        if user_rotation:
            unused_rotation_items = [item_id for item_id in user_rotation 
                                   if item_id not in [item.id for item in new_outfit]]
            if unused_rotation_items:
                suggestions.append(f"Consider using items from rotation schedule: {len(unused_rotation_items)} available")
        
        return suggestions
    
    def apply_diversity_boost(self, items: List[ClothingItem], user_id: str, 
                            occasion: str, style: str, mood: str) -> List[Tuple[ClothingItem, float]]:
        """Apply diversity boost to item scores to encourage variety"""
        
        # Load outfit history from Firestore if needed
        if not self.outfit_history[user_id] or len(self.outfit_history[user_id]) < 5:
            logger.info(f"🔄 Loading outfit history from Firestore for diversity boost (user {user_id})")
            firestore_history = self._load_outfit_history_from_firestore(user_id)
            if firestore_history:
                self.outfit_history[user_id] = firestore_history
        
        boosted_items = []
        user_history = self.outfit_history[user_id]
        recent_outfits = user_history[-self.max_recent_outfits:]
        
        # CRITICAL FIX: Filter to same occasion/style combination FIRST
        # This prevents the same outfit for the same combination
        same_combo_outfits = []
        for outfit in recent_outfits:
            if outfit:
                occasion_match = outfit.get('occasion', '').lower() == occasion.lower()
                style_match = outfit.get('style', '').lower() == style.lower()
                
                if occasion_match and style_match:
                    same_combo_outfits.append(outfit)
        
        logger.info(f"🎭 DIVERSITY BOOST: Checking {len(same_combo_outfits)} outfits with same combination (occasion={occasion}, style={style})")
        
        # Use same-combination outfits for similarity check, or all if none found
        comparison_outfits = same_combo_outfits if same_combo_outfits else recent_outfits
        
        for item in items:
            base_score = 1.0
            diversity_boost = 0.0
            
            # Boost items that haven't been used recently in THIS COMBINATION
            # Count usage in same-combination outfits, not globally
            same_combo_usage = 0
            for outfit in comparison_outfits:
                if outfit and 'items' in outfit:
                    if any(hasattr(oi, 'id') and oi.id == item.id for oi in outfit['items']):
                        same_combo_usage += 1
            
            if same_combo_usage == 0:
                diversity_boost += 0.3  # Not used in this combination
                logger.debug(f"  🆕 {item.name[:30]}: Not used in {occasion}/{style} → +0.30")
            elif same_combo_usage < 2:
                diversity_boost += 0.15  # Lightly used in this combination
                logger.debug(f"  🌱 {item.name[:30]}: Used {same_combo_usage}x in {occasion}/{style} → +0.15")
            elif same_combo_usage > 3:
                diversity_boost -= 0.15  # Overused in this combination
                logger.debug(f"  🔁 {item.name[:30]}: Overused {same_combo_usage}x in {occasion}/{style} → -0.15")
            
            # Boost items that are different from recent SAME-COMBO outfits
            if comparison_outfits:
                item_similarities = []
                for recent_outfit in comparison_outfits:
                    if 'items' in recent_outfit:
                        recent_items = recent_outfit['items']
                        # Check if this item was in recent outfits
                        if any(hasattr(ri, 'id') and ri.id == item.id for ri in recent_items):
                            item_similarities.append(1.0)  # Exact match
                        else:
                            # Calculate similarity with this item
                            item_similarity = self._calculate_item_similarity(item, recent_items)
                            item_similarities.append(item_similarity)
                
                if item_similarities:
                    avg_similarity = sum(item_similarities) / len(item_similarities)
                    diversity_boost += (1.0 - avg_similarity) * 0.2  # Boost dissimilar items
            
            # Boost items that fit rotation schedule
            if item.id in self.rotation_schedule[user_id]:
                diversity_boost += 0.2
            
            # Apply diversity boost
            final_score = base_score + (diversity_boost * self.diversity_boost_factor)
            boosted_items.append((item, final_score))
        
        return boosted_items
    
    def _calculate_item_similarity(self, item: ClothingItem, outfit_items: List[ClothingItem]) -> float:
        """Calculate similarity between an item and items in an outfit"""
        
        if not outfit_items:
            return 0.0
        
        similarities = []
        for outfit_item in outfit_items:
            # Type similarity
            type_sim = 1.0 if item.type == outfit_item.type else 0.0
            
            # Color similarity
            color_sim = 1.0 if item.color == outfit_item.color else 0.0
            
            # Style similarity
            item_styles = set(item.style or [])
            outfit_styles = set(outfit_item.style or [])
            style_intersection = len(item_styles & outfit_styles)
            style_union = len(item_styles | outfit_styles)
            style_sim = style_intersection / style_union if style_union > 0 else 0.0
            
            # Weighted similarity
            item_similarity = (type_sim * 0.4 + color_sim * 0.3 + style_sim * 0.3)
            similarities.append(item_similarity)
        
        return max(similarities) if similarities else 0.0
    
    def record_outfit_generation(self, user_id: str, outfit: Dict[str, Any], 
                               items: List[ClothingItem]) -> None:
        """Record a generated outfit for diversity tracking"""
        
        # Add to user history
        outfit_record = {
            'id': outfit.get('id', f'outfit_{int(time.time())}') if outfit else f'outfit_{int(time.time())}',
            'items': items,
            'occasion': outfit.get('occasion', 'unknown') if outfit else 'unknown',
            'style': outfit.get('style', 'unknown') if outfit else 'unknown',
            'mood': outfit.get('mood', 'unknown') if outfit else 'unknown',
            'createdAt': outfit.get('createdAt', int(time.time())) if outfit else int(time.time()),
            'confidence': outfit.get('confidence', 0.0) if outfit else 0.0
        }
        
        self.outfit_history[user_id].append(outfit_record)
        
        # Update item usage counts
        for item in items:
            self.item_usage_count[item.id] += 1
        
        # Keep only recent outfits
        if len(self.outfit_history[user_id]) > self.max_recent_outfits:
            self.outfit_history[user_id] = self.outfit_history[user_id][-self.max_recent_outfits:]
        
        # Update rotation schedule
        self._update_rotation_schedule(user_id, items)
        
        logger.info(f"📊 Recorded outfit for user {user_id}: {len(items)} items, diversity tracking updated")
    
    def _update_rotation_schedule(self, user_id: str, items: List[ClothingItem]) -> None:
        """Update rotation schedule for user"""
        
        # Simple rotation: add items to schedule, remove old ones
        current_schedule = self.rotation_schedule[user_id]
        
        # Add new items
        for item in items:
            if item.id not in current_schedule:
                current_schedule.append(item.id)
        
        # Keep only last 20 items in rotation
        if len(current_schedule) > 20:
            self.rotation_schedule[user_id] = current_schedule[-20:]
    
    def get_diversity_metrics(self, user_id: str) -> DiversityMetrics:
        """Get diversity metrics for a user"""
        
        user_history = self.outfit_history[user_id]
        total_outfits = len(user_history)
        
        if total_outfits < 2:
            return DiversityMetrics(
                total_outfits=total_outfits,
                unique_combinations=total_outfits,
                similarity_threshold=self.similarity_threshold,
                rotation_effectiveness=1.0,
                diversity_score=1.0,
                recent_repetitions=0
            )
        
        # Calculate unique combinations
        outfit_hashes = set()
        for outfit in user_history:
            if 'items' in outfit:
                item_ids = sorted([item.id for item in outfit['items']])
                outfit_hash = hashlib.md5(json.dumps(item_ids).encode()).hexdigest()
                outfit_hashes.add(outfit_hash)
        
        unique_combinations = len(outfit_hashes)
        
        # Calculate diversity score
        similarities = []
        for i in range(len(user_history) - 1):
            for j in range(i + 1, len(user_history)):
                if 'items' in user_history[i] and 'items' in user_history[j]:
                    similarity = self.calculate_outfit_similarity(
                        user_history[i]['items'], 
                        user_history[j]['items']
                    )
                    similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        diversity_score = 1.0 - avg_similarity
        
        # Calculate recent repetitions
        recent_outfits = user_history[-10:] if len(user_history) >= 10 else user_history
        recent_repetitions = 0
        for i in range(len(recent_outfits) - 1):
            for j in range(i + 1, len(recent_outfits)):
                if 'items' in recent_outfits[i] and 'items' in recent_outfits[j]:
                    similarity = self.calculate_outfit_similarity(
                        recent_outfits[i]['items'], 
                        recent_outfits[j]['items']
                    )
                    if similarity > self.similarity_threshold:
                        recent_repetitions += 1
        
        # Calculate rotation effectiveness
        rotation_items = len(self.rotation_schedule[user_id])
        total_unique_items = len(set(item.id for outfit in user_history 
                                   for item in (outfit.get('items', []) if outfit else [])))
        rotation_effectiveness = rotation_items / total_unique_items if total_unique_items > 0 else 1.0
        
        return DiversityMetrics(
            total_outfits=total_outfits,
            unique_combinations=unique_combinations,
            similarity_threshold=self.similarity_threshold,
            rotation_effectiveness=rotation_effectiveness,
            diversity_score=diversity_score,
            recent_repetitions=recent_repetitions
        )
    
    def suggest_diverse_items(self, user_id: str, available_items: List[ClothingItem], 
                            target_count: int = 3) -> List[ClothingItem]:
        """Suggest diverse items from available items"""
        
        if not available_items:
            return []
        
        # Apply diversity boost
        boosted_items = self.apply_diversity_boost(available_items, user_id, "", "", "")
        
        # Sort by diversity score (highest first)
        boosted_items.sort(key=lambda x: x[1], reverse=True)
        
        # Select top diverse items
        selected_items = [item for item, score in boosted_items[:target_count]]
        
        logger.info(f"🎭 Selected {len(selected_items)} diverse items for user {user_id}")
        return selected_items
    
    def reset_user_diversity(self, user_id: str) -> None:
        """Reset diversity tracking for a user"""
        self.outfit_history[user_id] = []
        self.rotation_schedule[user_id] = []
        
        # Reset item usage counts for this user's items
        user_items = set()
        for outfit in self.outfit_history[user_id]:
            if 'items' in outfit:
                user_items.update(item.id for item in outfit['items'])
        
        for item_id in user_items:
            if item_id in self.item_usage_count:
                del self.item_usage_count[item_id]
        
        logger.info(f"🔄 Reset diversity tracking for user {user_id}")
    
    def get_diversity_suggestions(self, user_id: str, current_outfit: List[Dict[str, Any]], **kwargs) -> List[str]:
        """
        Get diversity suggestions for improving outfit variety.
        Returns list of item IDs that could improve diversity.
        """
        try:
            # Get recent outfit history
            recent_outfits = self.outfit_history.get(user_id, [])
            if not recent_outfits:
                return []  # No history, no suggestions needed
            
            # Get current outfit item IDs
            current_item_ids = [item.get('id', '') for item in current_outfit if item and item.get('id')]
            
            # Find items that haven't been used recently
            recently_used_items = set()
            for outfit in recent_outfits[-10:]:  # Check last 10 outfits
                if outfit and 'items' in outfit:
                    for item in outfit['items']:
                        if item and 'id' in item:
                            recently_used_items.add(item['id'])
            
            # Suggest items that haven't been used recently
            suggestions = []
            for item in current_outfit:
                if item and item.get('id') and item['id'] not in recently_used_items:
                    suggestions.append(item['id'])
            
            return suggestions[:3]  # Return max 3 suggestions
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting diversity suggestions: {e}")
            return []

# Global instance
diversity_filter = DiversityFilterService()
