"""
Outfit Explanation Service
Generates structured explanations for outfit suggestions with all 5 categories:
Style Reasoning, Color Harmony, Occasion Fit, Weather Appropriateness, Personalization
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..config.firebase import db

logger = logging.getLogger(__name__)


class OutfitExplanationService:
    """Service to generate comprehensive outfit explanations"""
    
    def __init__(self):
        self.db = db
    
    async def generate_explanation(
        self,
        outfit: Dict[str, Any],
        context: Dict[str, Any],
        user_profile: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for outfit suggestion.
        
        Args:
            outfit: Outfit data with items, style, occasion, etc.
            context: Generation context (weather, mood, etc.)
            user_profile: User profile data
            user_id: User ID for history queries
            
        Returns:
            Structured explanation with all 5 categories and confidence breakdown
        """
        try:
            items = outfit.get('items', [])
            style = outfit.get('style', context.get('style', 'Casual'))
            occasion = outfit.get('occasion', context.get('occasion', 'Casual'))
            weather = context.get('weather', {})
            mood = outfit.get('mood', context.get('mood', 'Neutral'))
            
            # Get user history for personalization
            user_history = await self.get_user_outfit_history(user_id, days=90)
            
            # Generate explanations for each category
            explanations = []
            
            # 1. Style Reasoning
            style_explanation = self.explain_style_reasoning(items, style, user_profile)
            explanations.append(style_explanation)
            
            # 2. Color Harmony
            color_explanation = self.explain_color_harmony(items, user_profile)
            explanations.append(color_explanation)
            
            # 3. Occasion Fit
            occasion_explanation = self.explain_occasion_fit(outfit, occasion, user_profile)
            explanations.append(occasion_explanation)
            
            # 4. Weather Appropriateness
            weather_explanation = self.explain_weather_appropriateness(outfit, weather)
            explanations.append(weather_explanation)
            
            # 5. Personalization
            personalization_explanation = self.explain_personalization(outfit, user_history)
            explanations.append(personalization_explanation)
            
            # Calculate confidence breakdown
            confidence_breakdown = self.calculate_confidence_breakdown(explanations)
            
            return {
                "explanations": explanations,
                "confidence_breakdown": confidence_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error generating outfit explanation: {e}")
            # Return basic fallback explanation
            return self._generate_fallback_explanation(outfit, context)
    
    def explain_style_reasoning(
        self,
        items: List[Dict[str, Any]],
        style: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain style reasoning"""
        try:
            # Analyze style consistency across items
            item_styles = []
            for item in items:
                item_style = item.get('style') or item.get('metadata', {}).get('style', [])
                if isinstance(item_style, list):
                    item_styles.extend(item_style)
                elif isinstance(item_style, str):
                    item_styles.append(item_style)
            
            # Find common styles
            common_styles = list(set(item_styles)) if item_styles else [style]
            
            # Generate explanation
            if len(common_styles) > 0:
                style_text = f"These items share a {common_styles[0]} aesthetic"
                if len(common_styles) > 1:
                    style_text += f" with {', '.join(common_styles[1:2])} elements"
                style_text += f", creating a cohesive {style} look."
            else:
                style_text = f"This creates a balanced {style} look that matches your style preferences."
            
            # Check if matches user's style persona
            user_style_persona = user_profile.get('stylePersona') or user_profile.get('style_persona')
            if user_style_persona:
                style_text += f" Your '{user_style_persona}' style persona loves this combination."
            
            confidence = 0.90 if len(common_styles) > 0 else 0.75
            
            return {
                "category": "style",
                "icon": "palette",
                "title": "Style Reasoning",
                "text": style_text,
                "confidence": confidence,
                "tips": [
                    f"All pieces work together to create a {style} aesthetic",
                    "The style consistency ensures a cohesive look",
                    "This combination matches your personal style profile"
                ]
            }
        except Exception as e:
            logger.error(f"Error in style reasoning: {e}")
            return self._default_style_explanation(style)
    
    def explain_color_harmony(
        self,
        items: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain color harmony"""
        try:
            colors = []
            for item in items:
                item_color = item.get('color') or item.get('dominantColors', [{}])[0].get('name', 'Neutral')
                if isinstance(item_color, str):
                    colors.append(item_color)
                elif isinstance(item_color, list) and len(item_color) > 0:
                    colors.append(item_color[0].get('name', 'Neutral') if isinstance(item_color[0], dict) else str(item_color[0]))
            
            unique_colors = list(set(colors))[:3]  # Top 3 unique colors
            
            if len(unique_colors) == 1:
                color_text = f"A monochrome {unique_colors[0]} look creates a sophisticated, unified aesthetic."
            elif len(unique_colors) == 2:
                color_text = f"{unique_colors[0]} and {unique_colors[1]} create a classic, balanced combination."
            elif len(unique_colors) >= 3:
                color_text = f"The {', '.join(unique_colors[:2])} palette with {unique_colors[2]} accents creates dynamic contrast."
            else:
                color_text = "These colors work harmoniously together to create a cohesive look."
            
            # Check for complementary colors
            if len(unique_colors) >= 2:
                color_text += " The color combination follows proven fashion principles for visual harmony."
            
            confidence = 0.85 if len(unique_colors) >= 2 else 0.70
            
            return {
                "category": "color",
                "icon": "droplet",
                "title": "Color Harmony",
                "text": color_text,
                "confidence": confidence,
                "tips": [
                    "Color placement draws the eye to your best features",
                    "These colors complement each other naturally",
                    "The palette creates visual interest without overwhelming"
                ]
            }
        except Exception as e:
            logger.error(f"Error in color harmony: {e}")
            return self._default_color_explanation()
    
    def explain_occasion_fit(
        self,
        outfit: Dict[str, Any],
        occasion: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain occasion fit"""
        try:
            occasion_lower = occasion.lower()
            
            if 'business' in occasion_lower or 'work' in occasion_lower or 'professional' in occasion_lower:
                occasion_text = "Professional enough for the office, comfortable for all day wear."
            elif 'casual' in occasion_lower:
                occasion_text = "Perfect for a casual day out - relaxed yet put-together."
            elif 'formal' in occasion_lower or 'dress' in occasion_lower:
                occasion_text = "Sophisticated and elegant, perfect for formal events."
            elif 'date' in occasion_lower:
                occasion_text = "Sophisticated but not overdressed for a date night."
            elif 'weekend' in occasion_lower:
                occasion_text = "Perfect for a casual weekend - comfortable and stylish."
            else:
                occasion_text = f"This outfit hits the right tone for {occasion} occasions."
            
            confidence = 0.88
            
            return {
                "category": "occasion",
                "icon": "calendar",
                "title": "Occasion Fit",
                "text": occasion_text,
                "confidence": confidence,
                "tips": [
                    "The formality level matches the occasion perfectly",
                    "Comfortable enough to wear confidently all day",
                    "Easy to accessorize up or down as needed"
                ]
            }
        except Exception as e:
            logger.error(f"Error in occasion fit: {e}")
            return self._default_occasion_explanation(occasion)
    
    def explain_weather_appropriateness(
        self,
        outfit: Dict[str, Any],
        weather: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain weather appropriateness"""
        try:
            if not weather:
                return self._default_weather_explanation()
            
            temperature = weather.get('temperature', 70)
            condition = weather.get('condition', 'Clear').lower()
            
            if temperature >= 80:
                weather_text = f"Lightweight, breathable fabrics perfect for {temperature}°F weather."
            elif temperature >= 65:
                weather_text = f"Lightweight layers ideal for {temperature}°F weather - comfortable and versatile."
            elif temperature >= 50:
                weather_text = f"Layered pieces perfect for {temperature}°F weather - warm but not heavy."
            elif temperature >= 32:
                weather_text = f"Warm layers appropriate for {temperature}°F weather - cozy and protective."
            else:
                weather_text = f"Heavy layers and insulation for {temperature}°F weather - maximum warmth."
            
            # Add condition-specific advice
            if 'rain' in condition or 'storm' in condition:
                weather_text += " Water-resistant pieces help you stay dry."
            elif 'snow' in condition:
                weather_text += " Insulated layers keep you warm in snowy conditions."
            elif 'sun' in condition or 'clear' in condition:
                weather_text += " Perfect for sunny conditions."
            
            confidence = 0.80
            
            return {
                "category": "weather",
                "icon": "cloud",
                "title": "Weather Appropriateness",
                "text": weather_text,
                "confidence": confidence,
                "tips": [
                    f"Temperature-appropriate for {temperature}°F conditions",
                    "Layering allows you to adjust throughout the day",
                    "Materials chosen for weather comfort"
                ]
            }
        except Exception as e:
            logger.error(f"Error in weather appropriateness: {e}")
            return self._default_weather_explanation()
    
    def explain_personalization(
        self,
        outfit: Dict[str, Any],
        user_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain personalization based on user history"""
        try:
            items = outfit.get('items', [])
            item_ids = [item.get('id') for item in items if item.get('id')]
            
            # Analyze item usage from history
            item_usage = user_history.get('item_usage', {})
            favorite_outfits = user_history.get('favorite_outfits', [])
            
            # Count how many times each item was worn
            worn_counts = {}
            favorite_counts = {}
            
            for item_id in item_ids:
                worn_counts[item_id] = item_usage.get(item_id, {}).get('wear_count', 0)
                # Count how many favorite outfits featured this item
                favorite_counts[item_id] = sum(
                    1 for outfit_data in favorite_outfits
                    if item_id in [i.get('id') for i in outfit_data.get('items', [])]
                )
            
            # Find most-worn item
            most_worn_item_id = max(worn_counts.items(), key=lambda x: x[1])[0] if worn_counts else None
            most_worn_count = worn_counts.get(most_worn_item_id, 0) if most_worn_item_id else 0
            
            # Find item in most favorites
            most_favorite_item_id = max(favorite_counts.items(), key=lambda x: x[1])[0] if favorite_counts else None
            most_favorite_count = favorite_counts.get(most_favorite_item_id, 0) if most_favorite_item_id else 0
            
            # Generate personalized message
            if most_favorite_count >= 3:
                personalization_text = f"You've worn items from this outfit in {most_favorite_count} of your favorite outfits - this combination aligns with your style preferences!"
            elif most_worn_count >= 5:
                personalization_text = f"Based on your wardrobe history, you love wearing these pieces - this outfit combines your most-worn items in a fresh way."
            elif most_worn_count > 0:
                personalization_text = f"You've worn pieces from this outfit before - we're combining them in a new way that matches your style."
            else:
                personalization_text = "You haven't worn these items together yet - let's try something new! This combination explores your style in a fresh direction."
            
            confidence = 0.75 if most_worn_count > 0 or most_favorite_count > 0 else 0.65
            
            return {
                "category": "personalization",
                "icon": "heart",
                "title": "Personalized for You",
                "text": personalization_text,
                "confidence": confidence,
                "tips": [
                    "This outfit is tailored to your personal style history",
                    "Based on items you've loved wearing before",
                    "A combination that matches your preferences"
                ]
            }
        except Exception as e:
            logger.error(f"Error in personalization: {e}")
            return self._default_personalization_explanation()
    
    def calculate_confidence_breakdown(
        self,
        explanations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate confidence breakdown with per-factor scores"""
        try:
            factors = {}
            for explanation in explanations:
                category = explanation.get('category', '')
                confidence = explanation.get('confidence', 0.75)
                
                if category == 'style':
                    factors['style_match'] = confidence
                elif category == 'color':
                    factors['color_combo'] = confidence
                elif category == 'occasion':
                    factors['occasion_fit'] = confidence
                elif category == 'weather':
                    factors['weather'] = confidence
                elif category == 'personalization':
                    factors['personalization'] = confidence
            
            # Calculate overall confidence (weighted average)
            if factors:
                overall = sum(factors.values()) / len(factors)
            else:
                overall = 0.75
            
            # Generate summary text
            sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
            top_factors = sorted_factors[:3]
            
            factor_names = {
                'style_match': 'Matches your style',
                'color_combo': 'Great color combo',
                'occasion_fit': 'Perfect for the occasion',
                'weather': 'Weather-appropriate',
                'personalization': 'Personalized for you'
            }
            
            summary_parts = []
            for factor_key, score in top_factors:
                factor_name = factor_names.get(factor_key, factor_key.replace('_', ' ').title())
                summary_parts.append(f"{factor_name} ({int(score * 100)}%)")
            
            summary = "High confidence because: " + ", ".join(summary_parts)
            
            if overall < 0.7:
                summary = "Trying something new for you - " + summary.lower()
            
            return {
                "overall": round(overall, 2),
                "factors": {k: round(v, 2) for k, v in factors.items()},
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Error calculating confidence breakdown: {e}")
            return {
                "overall": 0.75,
                "factors": {},
                "summary": "Confidence analysis available"
            }
    
    async def get_user_outfit_history(
        self,
        user_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get user's outfit history for personalization explanations.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dictionary with item usage counts and favorite outfits
        """
        try:
            if not self.db:
                logger.warning("Firebase not initialized, returning empty history")
                return {"item_usage": {}, "favorite_outfits": []}
            
            # Query outfit history
            outfits_ref = self.db.collection('outfits')
            cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
            
            # Get outfits from last N days (createdAt can be int timestamp or datetime)
            # Try both user_id and userId fields for compatibility
            outfits_docs = []
            try:
                outfits_query = outfits_ref.where('user_id', '==', user_id)\
                                          .where('createdAt', '>=', cutoff_timestamp)\
                                          .limit(100)
                outfits_docs = list(outfits_query.stream())
            except Exception:
                pass
            
            # If no results, try with userId field
            if len(outfits_docs) == 0:
                try:
                    outfits_query = outfits_ref.where('userId', '==', user_id)\
                                              .where('createdAt', '>=', cutoff_timestamp)\
                                              .limit(100)
                    outfits_docs = list(outfits_query.stream())
                except Exception:
                    pass
            
            # Fallback: just get recent outfits without date filter
            if len(outfits_docs) == 0:
                try:
                    outfits_query = outfits_ref.where('user_id', '==', user_id).limit(100)
                    outfits_docs = list(outfits_query.stream())
                except Exception:
                    try:
                        outfits_query = outfits_ref.where('userId', '==', user_id).limit(100)
                        outfits_docs = list(outfits_query.stream())
                    except Exception:
                        outfits_docs = []
            
            item_usage = {}
            favorite_outfits = []
            
            for doc in outfits_docs:
                outfit_data = doc.to_dict()
                items = outfit_data.get('items', [])
                is_favorite = outfit_data.get('isFavorite', False) or outfit_data.get('rating', 0) >= 4
                
                # Track item usage
                for item in items:
                    item_id = item.get('id') if isinstance(item, dict) else str(item)
                    if item_id:
                        if item_id not in item_usage:
                            item_usage[item_id] = {'wear_count': 0, 'last_worn': None}
                        item_usage[item_id]['wear_count'] += 1
                        outfit_date = outfit_data.get('createdAt') or outfit_data.get('lastWorn')
                        if outfit_date:
                            item_usage[item_id]['last_worn'] = outfit_date
                
                # Track favorite outfits
                if is_favorite:
                    favorite_outfits.append(outfit_data)
            
            return {
                "item_usage": item_usage,
                "favorite_outfits": favorite_outfits
            }
            
        except Exception as e:
            logger.error(f"Error getting user outfit history: {e}")
            return {"item_usage": {}, "favorite_outfits": []}
    
    def _generate_fallback_explanation(
        self,
        outfit: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic fallback explanation if main generation fails"""
        return {
            "explanations": [
                self._default_style_explanation(outfit.get('style', 'Casual')),
                self._default_color_explanation(),
                self._default_occasion_explanation(outfit.get('occasion', 'Casual')),
                self._default_weather_explanation(),
                self._default_personalization_explanation()
            ],
            "confidence_breakdown": {
                "overall": 0.75,
                "factors": {
                    "style_match": 0.75,
                    "color_combo": 0.75,
                    "occasion_fit": 0.75,
                    "weather": 0.75,
                    "personalization": 0.75
                },
                "summary": "Confidence analysis available"
            }
        }
    
    def _default_style_explanation(self, style: str) -> Dict[str, Any]:
        return {
            "category": "style",
            "icon": "palette",
            "title": "Style Reasoning",
            "text": f"This creates a balanced {style} look.",
            "confidence": 0.75,
            "tips": ["Style consistency ensures a cohesive look"]
        }
    
    def _default_color_explanation(self) -> Dict[str, Any]:
        return {
            "category": "color",
            "icon": "droplet",
            "title": "Color Harmony",
            "text": "These colors work harmoniously together.",
            "confidence": 0.75,
            "tips": ["Color combination follows fashion principles"]
        }
    
    def _default_occasion_explanation(self, occasion: str) -> Dict[str, Any]:
        return {
            "category": "occasion",
            "icon": "calendar",
            "title": "Occasion Fit",
            "text": f"Perfect for {occasion} occasions.",
            "confidence": 0.75,
            "tips": ["Formality level matches the occasion"]
        }
    
    def _default_weather_explanation(self) -> Dict[str, Any]:
        return {
            "category": "weather",
            "icon": "cloud",
            "title": "Weather Appropriateness",
            "text": "Weather-appropriate outfit selection.",
            "confidence": 0.75,
            "tips": ["Temperature-appropriate for current conditions"]
        }
    
    def _default_personalization_explanation(self) -> Dict[str, Any]:
        return {
            "category": "personalization",
            "icon": "heart",
            "title": "Personalized for You",
            "text": "This outfit is tailored to your style preferences.",
            "confidence": 0.75,
            "tips": ["Based on your personal style profile"]
        }

