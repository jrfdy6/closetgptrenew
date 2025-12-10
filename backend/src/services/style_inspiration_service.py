"""
Style Inspiration Service
Provides personalized style recommendations based on user profile and weather
"""

import json
import math
import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class StyleInspirationService:
    """Service for generating style inspiration recommendations"""
    
    def __init__(self):
        self.catalog: List[Dict[str, Any]] = []
        self.catalog_path = Path(__file__).parent.parent / "data" / "style_inspiration_catalog.json"
        self._load_catalog()
    
    def _load_catalog(self):
        """Load the demo catalog from JSON file"""
        try:
            with open(self.catalog_path, 'r') as f:
                data = json.load(f)
                self.catalog = data.get('items', [])
            logger.info(f"✅ Loaded {len(self.catalog)} items from style catalog")
        except Exception as e:
            logger.error(f"❌ Failed to load catalog: {e}")
            self.catalog = []
    
    def _cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """Compute cosine similarity between two style vectors"""
        # Get common keys
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0
        
        # Compute dot product and norms
        dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
        norm_a = math.sqrt(sum(vec_a[k] ** 2 for k in common_keys))
        norm_b = math.sqrt(sum(vec_b[k] ** 2 for k in common_keys))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _compute_weather_score(self, item: Dict[str, Any], weather: Optional[Dict[str, Any]]) -> float:
        """Compute weather compatibility score (0-1)"""
        if not weather:
            return 0.75  # Neutral if no weather data
        
        temp_c = weather.get('temp_c', weather.get('temperature', 20))
        precip_mm = weather.get('precip_mm', weather.get('precipitation', 0))
        wind_kph = weather.get('wind_kph', 0)
        
        # Temperature score
        temp_min = item.get('temp_min_c', -50)
        temp_max = item.get('temp_max_c', 50)
        thermal = item.get('material_thermal_score', 0.5)
        
        if temp_min <= temp_c <= temp_max:
            temp_score = 1.0
        else:
            dist = min(abs(temp_c - temp_max), abs(temp_c - temp_min))
            decay = max(0, 1 - (dist / 20))
            temp_score = decay * thermal
        
        # Precipitation score
        water_res = item.get('water_resistance', 0)
        if precip_mm <= 1:
            precip_score = 1.0
        else:
            precip_score = min(1.0, water_res + 0.2)
        
        # Wind score
        wind_res = item.get('wind_resistance', 0)
        if wind_kph <= 15:
            wind_score = 1.0
        else:
            factor = max(0, 1 - (wind_kph - 15) / 60)
            wind_score = factor * (wind_res + 0.2)
        
        # Combine (weighted)
        return 0.6 * temp_score + 0.25 * precip_score + 0.15 * wind_score
    
    def _user_style_vector_from_profile(self, user_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract or construct a style vector from user profile
        Uses stylePersonality if available, otherwise constructs from preferences
        """
        # Try to use stylePersonality directly (if it matches our style names)
        style_personality = user_profile.get('stylePersonality', {})
        
        # Map common profile fields to our canonical styles
        # This is a simple mapping - can be expanded
        style_vector = {
            'Old Money': 0.0,
            'Urban Street': 0.0,
            'Minimalist': 0.0,
            'Preppy': 0.0,
            'Boho': 0.0,
            'Y2K': 0.0,
            'Avant-Garde': 0.0,
            'Classic': 0.0
        }
        
        # If stylePersonality has our canonical styles, use them
        for style in style_vector.keys():
            if style in style_personality:
                style_vector[style] = style_personality[style]
        
        # Otherwise, try to infer from stylePreferences list
        style_prefs = user_profile.get('stylePreferences', [])
        if not any(style_vector.values()) and style_prefs:
            # Simple heuristic mapping
            for pref in style_prefs:
                pref_lower = pref.lower()
                if 'classic' in pref_lower or 'timeless' in pref_lower:
                    style_vector['Classic'] += 0.3
                    style_vector['Old Money'] += 0.2
                if 'minimal' in pref_lower or 'clean' in pref_lower:
                    style_vector['Minimalist'] += 0.4
                if 'street' in pref_lower or 'urban' in pref_lower or 'casual' in pref_lower:
                    style_vector['Urban Street'] += 0.4
                if 'preppy' in pref_lower or 'collegiate' in pref_lower:
                    style_vector['Preppy'] += 0.4
                if 'boho' in pref_lower or 'bohemian' in pref_lower:
                    style_vector['Boho'] += 0.4
                if 'modern' in pref_lower or 'contemporary' in pref_lower:
                    style_vector['Minimalist'] += 0.2
                    style_vector['Urban Street'] += 0.2
                if 'luxury' in pref_lower or 'refined' in pref_lower:
                    style_vector['Old Money'] += 0.3
        
        # If still empty, provide neutral defaults
        if not any(style_vector.values()):
            style_vector = {k: 0.5 for k in style_vector.keys()}
        
        return style_vector
    
    def _get_dominant_styles(self, style_vector: Dict[str, float], top_n: int = 2) -> List[Tuple[str, float]]:
        """Get the top N dominant styles from a style vector"""
        sorted_styles = sorted(style_vector.items(), key=lambda x: x[1], reverse=True)
        return sorted_styles[:top_n]
    
    def _classify_item(
        self,
        item: Dict[str, Any],
        user_style_vector: Dict[str, float],
        similarity: float
    ) -> str:
        """
        Classify item as 'reinforce', 'bridge', or 'expand'
        """
        item_style_vector = item.get('style_vector', {})
        dominant_styles = self._get_dominant_styles(user_style_vector, 2)
        
        if len(dominant_styles) < 2:
            return 'reinforce'
        
        dominant_a = dominant_styles[0][0]
        dominant_b = dominant_styles[1][0]
        
        score_a = item_style_vector.get(dominant_a, 0)
        score_b = item_style_vector.get(dominant_b, 0)
        balance = abs(score_a - score_b)
        
        # Bridge: blends both dominant styles
        if similarity >= 0.55 and balance <= 0.3 and score_a >= 0.25 and score_b >= 0.25:
            return 'bridge'
        
        # Reinforce: strongly matches primary style
        if score_a >= 0.75 and similarity >= 0.6:
            return 'reinforce'
        
        # Expand: introduces new styles
        if similarity >= 0.5:
            return 'expand'
        
        return 'expand'
    
    def _generate_rationale(
        self,
        item: Dict[str, Any],
        user_style_vector: Dict[str, float],
        classification: str,
        weather_score: float
    ) -> str:
        """Generate human-readable explanation for why this item was recommended"""
        item_name = item.get('title', 'this item')
        dominant_user_styles = self._get_dominant_styles(user_style_vector, 2)
        item_style_vector = item.get('style_vector', {})
        
        # Find top item styles
        item_dominant = self._get_dominant_styles(item_style_vector, 2)
        
        if classification == 'reinforce':
            style_name = dominant_user_styles[0][0] if dominant_user_styles else 'your style'
            rationale = f"{item_name} — reinforces your {style_name} aesthetic with its {', '.join(item.get('tags', [])[:2])} qualities."
        
        elif classification == 'bridge':
            if len(dominant_user_styles) >= 2:
                style_a = dominant_user_styles[0][0]
                style_b = dominant_user_styles[1][0]
                rationale = f"{item_name} — bridges {style_a} and {style_b} with {', '.join(item.get('tags', [])[:2])} elements."
            else:
                rationale = f"{item_name} — versatile piece that blends multiple style dimensions."
        
        else:  # expand
            if item_dominant:
                new_style = item_dominant[0][0]
                rationale = f"{item_name} — introduces {new_style} elements to expand your style range."
            else:
                rationale = f"{item_name} — a fresh direction that complements your wardrobe."
        
        # Add weather note if relevant
        if weather_score > 0.8:
            weather_tags = item.get('weather_tags', [])
            if weather_tags:
                rationale += f" Perfect for today's weather ({', '.join(weather_tags)})."
        
        return rationale
    
    def _filter_by_gender_and_preferences(
        self, 
        items: List[Dict[str, Any]], 
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter items by user's gender and style preferences"""
        
        user_gender = user_profile.get('gender', '').lower()
        user_style_prefs = user_profile.get('stylePreferences', [])
        
        # Extract preferences from nested structure if needed
        if not user_style_prefs and 'preferences' in user_profile:
            user_style_prefs = user_profile.get('preferences', {}).get('style', [])
        
        filtered = []
        
        for item in items:
            # Gender filtering
            if user_gender:
                item_categories = [cat.lower() for cat in item.get('categories', [])]
                item_tags = [tag.lower() for tag in item.get('tags', [])]
                
                # Skip gender-specific items that don't match
                if user_gender in ['male', 'man', 'men']:
                    # Skip explicitly feminine items
                    feminine_keywords = ['dress', 'skirt', 'bra', 'heels', 'makeup']
                    if any(kw in ' '.join(item_categories + item_tags) for kw in feminine_keywords):
                        continue
                
                elif user_gender in ['female', 'woman', 'women']:
                    # Skip explicitly masculine items
                    masculine_keywords = ['mens', 'masculine']
                    if any(kw in ' '.join(item_categories + item_tags) for kw in masculine_keywords):
                        continue
            
            # Style preference filtering (if user has strong preferences)
            # Made more lenient: only filter if user has 3+ preferences AND item matches none
            if user_style_prefs and len(user_style_prefs) >= 3:
                item_style_vector = item.get('style_vector', {})
                
                # Check if item aligns with at least one of user's style preferences
                has_matching_style = False
                
                # Map common preference variations to catalog style names
                # This ensures users with different preference names still get matched items
                style_mapping = {
                    # Minimalist variations
                    'minimalist': ['minimalist', 'minimal'],
                    'clean minimal': ['minimalist', 'minimal'],
                    'minimal': ['minimalist', 'minimal'],
                    # Classic variations
                    'classic': ['classic', 'old money'],
                    'classic elegant': ['classic', 'old money'],
                    'old money': ['old money', 'classic'],
                    'timeless': ['classic', 'old money'],
                    # Street/Urban variations
                    'street style': ['urban street', 'street'],
                    'urban street': ['urban street', 'street'],
                    'grunge street': ['urban street', 'street'],
                    'streetwear': ['urban street', 'street'],
                    'edgy': ['urban street', 'street'],
                    # Bohemian variations
                    'boho': ['boho', 'bohemian'],
                    'bohemian': ['boho', 'bohemian'],
                    'natural boho': ['boho', 'bohemian'],
                    'cottagecore': ['boho', 'bohemian', 'romantic'],
                    # Other styles
                    'preppy': ['preppy'],
                    'y2k': ['y2k'],
                    'avant-garde': ['avant-garde', 'avant garde'],
                    'romantic': ['romantic', 'boho'],
                    'vintage': ['vintage', 'boho'],
                    'sophisticated': ['classic', 'old money'],
                    'athletic': ['urban street', 'street']
                }
                
                for pref in user_style_prefs:
                    pref_normalized = pref.strip().lower()
                    
                    # Get possible style names to match
                    possible_styles = style_mapping.get(pref_normalized, [pref_normalized])
                    
                    # Check if preference matches any style in the item's vector
                    for style_name, score in item_style_vector.items():
                        style_name_lower = style_name.lower()
                        
                        # Check if this style is in our possible matches
                        matches = any(
                            possible_style.lower() in style_name_lower or 
                            style_name_lower in possible_style.lower() or
                            any(word in style_name_lower for word in possible_style.split() if len(word) > 3)
                            for possible_style in possible_styles
                        )
                        
                        if matches and score >= 0.2:  # Lowered threshold from 0.3 to 0.2
                            has_matching_style = True
                            break
                    
                    if has_matching_style:
                        break
                
                # Only skip if user has 3+ preferences AND item matches none
                if not has_matching_style:
                    continue
            
            filtered.append(item)
        
        return filtered
    
    def get_inspiration(
        self,
        user_profile: Dict[str, Any],
        weather: Optional[Dict[str, Any]] = None,
        excluded_ids: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get one style inspiration item for the user
        
        Args:
            user_profile: User profile with stylePersonality/stylePreferences
            weather: Optional weather context (temp_c, precip_mm, wind_kph)
            excluded_ids: List of item IDs to exclude (already seen)
        
        Returns:
            Dict with item info + recommendation metadata, or None if no suitable item
        """
        if not self.catalog:
            logger.warning("⚠️ Catalog is empty")
            return None
        
        excluded_ids = excluded_ids or []
        
        # Filter by gender and style preferences FIRST
        filtered_catalog = self._filter_by_gender_and_preferences(self.catalog, user_profile)
        
        # Remove excluded items from filtered catalog
        filtered_catalog = [item for item in filtered_catalog if item['id'] not in excluded_ids]
        
        # If no items match after filtering (or all were excluded), try a more lenient approach
        if not filtered_catalog:
            logger.warning("⚠️ No items match user's gender and style preferences, trying lenient filtering")
            # Fallback: only filter by gender, ignore style preferences
            user_gender = user_profile.get('gender', '').lower()
            filtered_catalog = []
            
            for item in self.catalog:
                if item['id'] in excluded_ids:
                    continue
                    
                # Only apply gender filtering (more lenient)
                if user_gender:
                    item_categories = [cat.lower() for cat in item.get('categories', [])]
                    item_tags = [tag.lower() for tag in item.get('tags', [])]
                    
                    if user_gender in ['male', 'man', 'men']:
                        feminine_keywords = ['dress', 'skirt', 'bra', 'heels', 'makeup']
                        if any(kw in ' '.join(item_categories + item_tags) for kw in feminine_keywords):
                            continue
                    elif user_gender in ['female', 'woman', 'women']:
                        masculine_keywords = ['mens', 'masculine']
                        if any(kw in ' '.join(item_categories + item_tags) for kw in masculine_keywords):
                            continue
                
                filtered_catalog.append(item)
            
            # If still no items, return any item (last resort)
            if not filtered_catalog:
                logger.warning("⚠️ No items after lenient filtering, returning any available item")
                filtered_catalog = [item for item in self.catalog if item['id'] not in excluded_ids]
        
        if not filtered_catalog:
            logger.warning("⚠️ No items available after all filtering attempts")
            return None
        
        logger.info(f"✅ Filtered catalog: {len(filtered_catalog)}/{len(self.catalog)} items available")
        
        # Get user's style vector
        user_style_vector = self._user_style_vector_from_profile(user_profile)
        
        # Score filtered items (excluded_ids already removed above)
        scored_items = []
        for item in filtered_catalog:
            
            # Compute similarity
            item_style_vector = item.get('style_vector', {})
            similarity = self._cosine_similarity(user_style_vector, item_style_vector)
            
            # Weather compatibility
            weather_score = self._compute_weather_score(item, weather)
            
            # Classification
            classification = self._classify_item(item, user_style_vector, similarity)
            
            # Final score (weighted combination)
            # Weights: 55% similarity, 20% weather, 15% trend fit, 10% novelty
            trend_score = item.get('trend_score', 0.5)
            
            # For simplicity, assume trend_awareness = 0.5 (can be read from profile later)
            trend_awareness = user_profile.get('fingerprint', {}).get('trend_awareness', 0.5)
            trend_component = trend_awareness * trend_score + (1 - trend_awareness) * (1 - trend_score)
            
            final_score = (
                0.55 * similarity +
                0.20 * weather_score +
                0.15 * trend_component +
                0.10 * (1 - similarity)  # Slight novelty boost
            )
            
            scored_items.append({
                'item': item,
                'similarity': similarity,
                'weather_score': weather_score,
                'classification': classification,
                'final_score': final_score
            })
        
        if not scored_items:
            return None
        
        # Sort by final score
        scored_items.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Add randomization: pick from top 20 high-scoring items instead of always the #1
        # This ensures quality while adding variety
        top_candidates = min(20, len(scored_items))
        
        # Only consider items with score >= 70% of the best score (quality threshold)
        best_score = scored_items[0]['final_score']
        quality_threshold = best_score * 0.70
        
        high_quality_items = [
            item for item in scored_items[:top_candidates]
            if item['final_score'] >= quality_threshold
        ]
        
        if not high_quality_items:
            high_quality_items = scored_items[:1]  # Fallback to best item
        
        # Randomly select from high-quality pool
        best = random.choice(high_quality_items)
        
        logger.info(f"🎲 Selected from pool of {len(high_quality_items)} high-quality items (score: {best['final_score']:.2f})")
        
        # Generate rationale
        rationale = self._generate_rationale(
            best['item'],
            user_style_vector,
            best['classification'],
            best['weather_score']
        )
        
        # Format response
        item = best['item']
        return {
            'id': item['id'],
            'title': item['title'],
            'brand': item['brand'],
            'price': f"${item['price_cents'] / 100:.2f}",
            'price_cents': item['price_cents'],
            'currency': item['currency'],
            'image_url': item['image_url'],
            'categories': item['categories'],
            'tags': item['tags'],
            'style_vector': item['style_vector'],
            'classification': best['classification'],
            'similarity_score': round(best['similarity'], 2),
            'weather_score': round(best['weather_score'], 2),
            'final_score': round(best['final_score'], 2),
            'rationale': rationale,
            'seasonality': item.get('seasonality', []),
            'materials': item.get('materials', [])
        }

