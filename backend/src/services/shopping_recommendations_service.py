#!/usr/bin/env python3
"""
Shopping Recommendations Service
===============================

This service provides intelligent shopping recommendations based on wardrobe gaps,
user preferences, and current fashion trends.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class ShoppingRecommendationsService:
    def __init__(self):
        self.db = None  # Will be initialized when needed
    
    async def get_shopping_recommendations(
        self, 
        user_id: str, 
        gaps: List[Dict[str, Any]], 
        user_profile: Dict[str, Any],
        budget_range: Optional[str] = None,
        preferred_stores: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized shopping recommendations based on wardrobe gaps.
        
        Args:
            user_id: User ID
            gaps: List of wardrobe gaps identified
            user_profile: User's style profile and preferences
            budget_range: Optional budget range ("low", "medium", "high", "luxury")
            preferred_stores: Optional list of preferred stores
            
        Returns:
            Dict containing shopping recommendations with specific items and stores
        """
        try:
            logger.info(f"🛍️ Generating shopping recommendations for user {user_id}")
            
            # Get user's style preferences
            style_preferences = (user_profile.get('stylePreferences', []) if user_profile else [])
            color_preferences = (user_profile.get('colorPreferences', []) if user_profile else [])
            body_type = (user_profile.get('bodyType', 'average') if user_profile else 'average')
            gender = (user_profile.get('gender', 'unisex') if user_profile else 'unisex')
            
            # Generate recommendations for each gap
            recommendations = []
            total_estimated_cost = 0
            
            for gap in gaps:
                gap_recommendations = await self._generate_gap_recommendations(
                    gap, style_preferences, color_preferences, body_type, gender, budget_range
                )
                recommendations.extend(gap_recommendations)
                total_estimated_cost += sum((rec.get('estimated_price', 0) if rec else 0) for rec in gap_recommendations)
            
            # Sort by priority and budget
            recommendations = self._prioritize_recommendations(recommendations, budget_range)
            
            # Get store recommendations
            store_recommendations = await self._get_store_recommendations(
                recommendations, preferred_stores, budget_range
            )
            
            # Generate shopping strategy
            shopping_strategy = self._generate_shopping_strategy(recommendations, budget_range)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "store_recommendations": store_recommendations,
                "shopping_strategy": shopping_strategy,
                "total_estimated_cost": total_estimated_cost,
                "budget_range": budget_range or "medium",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating shopping recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "store_recommendations": [],
                "shopping_strategy": {}
            }
    
    async def _generate_gap_recommendations(
        self, 
        gap: Dict[str, Any], 
        style_preferences: List[str], 
        color_preferences: List[str], 
        body_type: str,
        gender: str,
        budget_range: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Generate specific item recommendations for a wardrobe gap."""
        
        category = (gap.get('category', '') if gap else '')
        priority = (gap.get('priority', 'medium') if gap else 'medium')
        suggested_items = (gap.get('suggestedItems', []) if gap else [])
        
        recommendations = []
        
        # Define item templates based on category and style
        item_templates = self._get_item_templates(category, style_preferences, gender)
        
        for item_type in suggested_items[:3]:  # Limit to top 3 items per gap
            for template in item_templates:
                if item_type.lower() in template['name'].lower():
                    recommendation = {
                        "id": f"{category}_{item_type}_{len(recommendations)}",
                        "name": template['name'],
                        "category": category,
                        "item_type": item_type,
                        "description": template['description'],
                        "style_tags": template['style_tags'],
                        "colors": self._get_recommended_colors(color_preferences, template['colors']),
                        "sizes": self._get_recommended_sizes(body_type, gender),
                        "materials": template['materials'],
                        "estimated_price": self._estimate_price(item_type, budget_range),
                        "priority": priority,
                        "why_needed": (gap.get('description', '') if gap else ''),
                        "styling_tips": template['styling_tips'],
                        "care_instructions": template['care_instructions'],
                        "versatility_score": template['versatility_score'],
                        "seasonality": template['seasonality'],
                        "formality_level": template['formality_level']
                    }
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _get_item_templates(self, category: str, style_preferences: List[str], gender: str) -> List[Dict[str, Any]]:
        """Get item templates based on category and style preferences."""
        
        templates = {
            'Tops': [
                {
                    "name": "Classic White Button-Down Shirt",
                    "description": "A versatile white button-down that works for both casual and professional looks",
                    "style_tags": ["classic", "professional", "versatile"],
                    "colors": ["white", "ivory", "light blue"],
                    "materials": ["cotton", "cotton blend"],
                    "styling_tips": "Layer under sweaters, tuck into high-waisted pants, or wear open over a tank top",
                    "care_instructions": "Machine wash cold, hang dry to prevent shrinking",
                    "versatility_score": 9,
                    "seasonality": ["spring", "summer", "fall"],
                    "formality_level": "semi-formal"
                },
                {
                    "name": "Cozy Knit Sweater",
                    "description": "A comfortable sweater perfect for layering and cooler weather",
                    "style_tags": ["casual", "cozy", "layering"],
                    "colors": ["beige", "gray", "navy", "black"],
                    "materials": ["wool", "cashmere", "cotton blend"],
                    "styling_tips": "Pair with jeans for casual looks or dress pants for smart casual",
                    "care_instructions": "Hand wash or dry clean depending on material",
                    "versatility_score": 8,
                    "seasonality": ["fall", "winter"],
                    "formality_level": "casual"
                }
            ],
            'Bottoms': [
                {
                    "name": "Dark Wash Straight-Leg Jeans",
                    "description": "A classic pair of dark wash jeans that flatters most body types",
                    "style_tags": ["classic", "versatile", "casual"],
                    "colors": ["dark blue", "black"],
                    "materials": ["denim", "stretch denim"],
                    "styling_tips": "Dress up with a blazer or keep casual with a t-shirt",
                    "care_instructions": "Wash inside out in cold water, air dry to maintain shape",
                    "versatility_score": 9,
                    "seasonality": ["all"],
                    "formality_level": "casual"
                },
                {
                    "name": "Tailored Trousers",
                    "description": "Professional trousers that work for office and smart casual occasions",
                    "style_tags": ["professional", "tailored", "versatile"],
                    "colors": ["black", "navy", "gray", "khaki"],
                    "materials": ["wool", "polyester blend", "cotton blend"],
                    "styling_tips": "Pair with blouses, sweaters, or blazers for a polished look",
                    "care_instructions": "Dry clean or machine wash on gentle cycle",
                    "versatility_score": 8,
                    "seasonality": ["all"],
                    "formality_level": "semi-formal"
                }
            ],
            'Shoes': [
                {
                    "name": "Classic White Sneakers",
                    "description": "Clean white sneakers that go with almost everything",
                    "style_tags": ["casual", "clean", "versatile"],
                    "colors": ["white", "off-white"],
                    "materials": ["canvas", "leather", "synthetic"],
                    "styling_tips": "Perfect with jeans, dresses, or even tailored pants for a modern look",
                    "care_instructions": "Spot clean with mild soap, air dry",
                    "versatility_score": 9,
                    "seasonality": ["spring", "summer", "fall"],
                    "formality_level": "casual"
                },
                {
                    "name": "Black Ankle Boots",
                    "description": "Versatile ankle boots that work for multiple seasons and occasions",
                    "style_tags": ["versatile", "edgy", "seasonal"],
                    "colors": ["black", "brown", "tan"],
                    "materials": ["leather", "suede", "synthetic"],
                    "styling_tips": "Great with jeans, dresses, or skirts. Tuck pants in for a modern look",
                    "care_instructions": "Use appropriate leather cleaner, condition regularly",
                    "versatility_score": 8,
                    "seasonality": ["fall", "winter", "spring"],
                    "formality_level": "casual"
                }
            ],
            'Outerwear': [
                {
                    "name": "Classic Trench Coat",
                    "description": "A timeless trench coat that works for multiple seasons",
                    "style_tags": ["classic", "elegant", "versatile"],
                    "colors": ["beige", "black", "navy"],
                    "materials": ["cotton", "polyester blend"],
                    "styling_tips": "Belt it for a cinched waist or leave open for a relaxed look",
                    "care_instructions": "Dry clean or spot clean, hang to dry",
                    "versatility_score": 9,
                    "seasonality": ["spring", "fall"],
                    "formality_level": "semi-formal"
                },
                {
                    "name": "Wool Blazer",
                    "description": "A structured blazer that elevates any outfit",
                    "style_tags": ["professional", "structured", "versatile"],
                    "colors": ["black", "navy", "gray", "plaid"],
                    "materials": ["wool", "wool blend"],
                    "styling_tips": "Wear with jeans for smart casual or dress pants for professional",
                    "care_instructions": "Dry clean only",
                    "versatility_score": 8,
                    "seasonality": ["all"],
                    "formality_level": "semi-formal"
                }
            ],
            'Accessories': [
                {
                    "name": "Leather Crossbody Bag",
                    "description": "A practical and stylish crossbody bag for everyday use",
                    "style_tags": ["practical", "versatile", "classic"],
                    "colors": ["black", "brown", "tan", "navy"],
                    "materials": ["leather", "vegan leather"],
                    "styling_tips": "Adjust strap length to sit at your natural waist",
                    "care_instructions": "Use leather conditioner, store with shape keeper",
                    "versatility_score": 9,
                    "seasonality": ["all"],
                    "formality_level": "casual"
                },
                {
                    "name": "Silk Scarf",
                    "description": "An elegant silk scarf that adds sophistication to any outfit",
                    "style_tags": ["elegant", "versatile", "luxury"],
                    "colors": ["multicolor", "solid", "patterned"],
                    "materials": ["silk", "silk blend"],
                    "styling_tips": "Wear as a headband, around neck, or tied to bag",
                    "care_instructions": "Hand wash in cold water, air dry",
                    "versatility_score": 7,
                    "seasonality": ["all"],
                    "formality_level": "semi-formal"
                }
            ]
        }
        
        return (templates.get(category, []) if templates else [])
    
    def _get_recommended_colors(self, color_preferences: List[str], template_colors: List[str]) -> List[str]:
        """Get recommended colors based on user preferences and template options."""
        if not color_preferences:
            return template_colors[:3]  # Return first 3 template colors
        
        # Prioritize user's preferred colors
        preferred_colors = [color for color in template_colors if color.lower() in [pref.lower() for pref in color_preferences]]
        other_colors = [color for color in template_colors if color not in preferred_colors]
        
        return preferred_colors[:2] + other_colors[:1]  # 2 preferred + 1 other
    
    def _get_recommended_sizes(self, body_type: str, gender: str) -> List[str]:
        """Get recommended sizes based on body type and gender."""
        size_guides = {
            'female': {
                'petite': ['XS', 'S', 'M'],
                'average': ['S', 'M', 'L'],
                'tall': ['M', 'L', 'XL'],
                'plus': ['L', 'XL', 'XXL']
            },
            'male': {
                'slim': ['S', 'M', 'L'],
                'average': ['M', 'L', 'XL'],
                'athletic': ['M', 'L', 'XL'],
                'big': ['L', 'XL', 'XXL']
            }
        }
        
        return (size_guides.get(gender, size_guides['female']) if size_guides else size_guides['female']).get(body_type, ['S', 'M', 'L'])
    
    def _estimate_price(self, item_type: str, budget_range: Optional[str]) -> int:
        """Estimate price based on item type and budget range."""
        base_prices = {
            'shirt': 30, 'sweater': 60, 'pants': 80, 'jeans': 70,
            'shoes': 100, 'boots': 120, 'jacket': 150, 'blazer': 200,
            'bag': 80, 'scarf': 40, 'accessory': 25
        }
        
        base_price = (base_prices.get(item_type.lower() if base_prices else None), 50)
        
        if budget_range == 'low':
            return int(base_price * 0.6)
        elif budget_range == 'medium':
            return base_price
        elif budget_range == 'high':
            return int(base_price * 1.5)
        elif budget_range == 'luxury':
            return int(base_price * 3)
        else:
            return base_price
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]], budget_range: Optional[str]) -> List[Dict[str, Any]]:
        """Sort recommendations by priority and budget considerations."""
        def sort_key(rec):
            priority_scores = {'high': 3, 'medium': 2, 'low': 1}
            priority_score = (priority_scores.get((rec.get('priority', 'medium') if rec else 'medium') if priority_scores else 'medium'), 2)
            versatility_score = (rec.get('versatility_score', 5) if rec else 5)
            return (priority_score, versatility_score)
        
        return sorted(recommendations, key=sort_key, reverse=True)
    
    async def _get_store_recommendations(
        self, 
        recommendations: List[Dict[str, Any]], 
        preferred_stores: Optional[List[str]], 
        budget_range: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get store recommendations based on budget and preferences."""
        
        stores = {
            'low': [
                {"name": "Target", "description": "Affordable basics and trendy pieces", "price_range": "$10-50"},
                {"name": "H&M", "description": "Fast fashion with good basics", "price_range": "$5-40"},
                {"name": "Uniqlo", "description": "Quality basics at reasonable prices", "price_range": "$10-60"},
                {"name": "Old Navy", "description": "Casual wear and denim", "price_range": "$10-50"}
            ],
            'medium': [
                {"name": "Zara", "description": "Trendy pieces with good quality", "price_range": "$20-100"},
                {"name": "Mango", "description": "European style and quality", "price_range": "$30-120"},
                {"name": "J.Crew", "description": "Classic American style", "price_range": "$40-150"},
                {"name": "Madewell", "description": "Denim and casual chic", "price_range": "$30-120"}
            ],
            'high': [
                {"name": "Everlane", "description": "Ethical fashion and quality basics", "price_range": "$50-200"},
                {"name": "COS", "description": "Minimalist and architectural designs", "price_range": "$60-300"},
                {"name": "Theory", "description": "Modern professional wear", "price_range": "$100-400"},
                {"name": "Aritzia", "description": "Contemporary women's fashion", "price_range": "$50-300"}
            ],
            'luxury': [
                {"name": "Nordstrom", "description": "High-end department store", "price_range": "$100-1000+"},
                {"name": "Saks Fifth Avenue", "description": "Luxury fashion and designer pieces", "price_range": "$200-2000+"},
                {"name": "Net-a-Porter", "description": "Online luxury fashion", "price_range": "$300-5000+"},
                {"name": "SSENSE", "description": "Contemporary luxury and streetwear", "price_range": "$200-3000+"}
            ]
        }
        
        budget = budget_range or 'medium'
        store_list = (stores.get(budget, stores['medium']) if stores else stores['medium'])
        
        # Filter by preferred stores if provided
        if preferred_stores:
            store_list = [store for store in store_list if store['name'].lower() in [s.lower() for s in preferred_stores]]
        
        return store_list[:4]  # Return top 4 stores
    
    def _generate_shopping_strategy(self, recommendations: List[Dict[str, Any]], budget_range: Optional[str]) -> Dict[str, Any]:
        """Generate a shopping strategy based on recommendations and budget."""
        
        total_items = len(recommendations)
        high_priority = len([r for r in recommendations if r.get('priority') == 'high'])
        estimated_cost = sum(r.get('estimated_price', 0) for r in recommendations)
        
        strategy = {
            "total_items_needed": total_items,
            "high_priority_items": high_priority,
            "estimated_total_cost": estimated_cost,
            "budget_range": budget_range or "medium",
            "shopping_phases": [],
            "tips": []
        }
        
        # Create shopping phases based on priority
        if high_priority > 0:
            strategy["shopping_phases"].append({
                "phase": 1,
                "name": "Essential Items",
                "description": f"Focus on {high_priority} high-priority items first",
                "items": [r for r in recommendations if r.get('priority') == 'high'],
                "estimated_cost": sum(r.get('estimated_price', 0) for r in recommendations if r.get('priority') == 'high')
            })
        
        medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
        if medium_priority:
            strategy["shopping_phases"].append({
                "phase": 2,
                "name": "Style Builders",
                "description": f"Add {len(medium_priority)} medium-priority items to enhance your wardrobe",
                "items": medium_priority,
                "estimated_cost": sum((r.get('estimated_price', 0) if r else 0) for r in medium_priority)
            })
        
        # Add shopping tips
        strategy["tips"] = [
            "Start with high-priority items that will have the most impact",
            "Look for versatile pieces that can be styled multiple ways",
            "Consider buying one quality item over multiple cheap alternatives",
            "Check for sales and seasonal discounts",
            "Try items on in-store when possible for the best fit",
            "Keep receipts for easy returns if needed"
        ]
        
        return strategy
