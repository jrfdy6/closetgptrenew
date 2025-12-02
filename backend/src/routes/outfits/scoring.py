"""
Scoring functions for outfit evaluation and rating.
Calculates comprehensive outfit scores across multiple dimensions.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


# Helper function for item categorization (used by scoring functions)
def get_item_category(item_type: str) -> str:
    """Categorize item type into outfit categories."""
    item_type_lower = item_type.lower()
    
    # Top items
    if any(top_type in item_type_lower for top_type in ['shirt', 'blouse', 't-shirt', 'sweater', 'jacket', 'coat', 'blazer', 'cardigan', 'hoodie']):
        return "top"
    
    # Bottom items
    elif any(bottom_type in item_type_lower for bottom_type in ['pants', 'jeans', 'shorts', 'skirt', 'leggings', 'trousers']):
        return "bottom"
    
    # Shoes
    elif any(shoe_type in item_type_lower for shoe_type in ['shoes', 'sneakers', 'boots', 'heels', 'flats', 'sandals', 'loafers']):
        return "shoes"
    
    # Accessories
    elif any(acc_type in item_type_lower for acc_type in ['bag', 'purse', 'hat', 'scarf', 'belt', 'jewelry', 'watch']):
        return "accessory"
    
    # Dresses (count as both top and bottom)
    elif 'dress' in item_type_lower:
        return "dress"
    
    # Default to top if unclear
    else:
        return "top"


async def calculate_outfit_score(items: List[Dict], req, layering_validation: Dict, color_material_validation: Dict, user_id: str) -> Dict[str, Any]:
    """Calculate comprehensive outfit score across multiple dimensions."""
    logger.info(f"🔍 DEBUG: Calculating outfit score for {len(items)} items")
    
    # Initialize component scores
    scores = {}
    
    # 1. Composition Score (20% weight) - Basic outfit structure
    composition_score = calculate_composition_score(items, (req.occasion if req else "unknown"))
    scores["composition_score"] = composition_score
    logger.info(f"🔍 DEBUG: Composition score: {composition_score}")
    
    # 2. Layering Score (15% weight) - Smart layering and conflicts
    layering_score = calculate_layering_score(layering_validation)
    scores["layering_score"] = layering_score
    logger.info(f"🔍 DEBUG: Layering score: {layering_score}")
    
    # 3. Color Harmony Score (15% weight) - Color theory and psychology
    color_score = calculate_color_score((color_material_validation.get("colors", {}) if color_material_validation else {}))
    scores["color_score"] = color_score
    logger.info(f"🔍 DEBUG: Color score: {color_score}")
    
    # 4. Material Compatibility Score (10% weight) - Fabric and texture harmony
    material_score = calculate_material_score((color_material_validation.get("materials", {}) if color_material_validation else {}))
    scores["material_score"] = material_score
    logger.info(f"🔍 DEBUG: Material score: {material_score}")
    
    # 5. Style Coherence Score (15% weight) - Style and mood alignment
    style_score = calculate_style_coherence_score(items, (req.style if req else "unknown"), (req.mood if req else "unknown"))
    scores["style_score"] = style_score
    logger.info(f"🔍 DEBUG: Style score: {style_score}")
    
    # 6. Wardrobe Intelligence Score (25% weight) - Favorites, wear history, diversity
    wardrobe_score = await calculate_wardrobe_intelligence_score(items, user_id)
    scores["wardrobe_intelligence_score"] = wardrobe_score
    logger.info(f"🔍 DEBUG: Wardrobe intelligence score: {wardrobe_score}")
    
    # Calculate weighted total score (0-100 scale)
    weights = {
        "composition_score": 0.20,
        "layering_score": 0.15,
        "color_score": 0.15,
        "material_score": 0.10,
        "style_score": 0.15,
        "wardrobe_intelligence_score": 0.25
    }
    
    total_score = sum(scores[component] * weights[component] for component in scores.keys())
    scores["total_score"] = round(total_score, 2)
    
    # Add score interpretation
    scores["score_interpretation"] = interpret_score(total_score)
    scores["grade"] = get_score_grade(total_score)
    
    logger.info(f"🔍 DEBUG: Final outfit score: {total_score} ({scores['grade']})")
    
    return scores


def calculate_composition_score(items: List[Dict], occasion: str) -> float:
    """Calculate score for outfit composition and completeness."""
    score = 0.0
    
    # Required categories for different occasions
    required_categories = {
        "casual": ["top", "bottom"],
        "business": ["top", "bottom", "shoes"],
        "formal": ["top", "bottom", "shoes"],
        "athletic": ["top", "bottom", "shoes"],
        "beach": ["top", "bottom"],
        "party": ["top", "bottom", "shoes"],
        "date": ["top", "bottom", "shoes"],
        "travel": ["top", "bottom", "shoes"]
    }
    
    required = required_categories.get(occasion.lower(), ["top", "bottom"])
    
    # Categorize items
    categorized_items = {}
    for item in items:
        item_type = (item.get('type', '') if item else '').lower()
        category = get_item_category(item_type)
        if category not in categorized_items:
            categorized_items[category] = []
        categorized_items[category].append(item)
    
    # Score based on required categories present
    required_present = sum(1 for cat in required if cat in categorized_items and categorized_items[cat])
    required_score = (required_present / len(required)) * 40 if required else 0  # 40 points for required categories
    
    # Score based on item count appropriateness
    item_count_score = 0
    if len(items) >= 3 and len(items) <= 6:
        item_count_score = 30  # Perfect item count
    elif len(items) >= 2 and len(items) <= 7:
        item_count_score = 20  # Acceptable item count
    else:
        item_count_score = 10  # Too few or too many items
    
    # Score based on category variety
    variety_score = min(len(categorized_items) * 10, 30)  # Up to 30 points for variety
    
    score = required_score + item_count_score + variety_score
    return min(score, 100.0)  # Cap at 100


def calculate_layering_score(layering_validation: Dict) -> float:
    """Calculate score for layering appropriateness."""
    score = 100.0  # Start with perfect score
    
    warnings = (layering_validation.get('warnings', []) if layering_validation else [])
    layer_count = (layering_validation.get('layer_count', 0) if layering_validation else 0)
    
    # Deduct points for warnings
    for warning in warnings:
        if "too heavy" in warning.lower():
            score -= 15
        elif "too many layers" in warning.lower():
            score -= 10
        elif "too few layers" in warning.lower():
            score -= 8
        elif "conflict" in warning.lower():
            score -= 12
    
    # Bonus for optimal layer count
    if 2 <= layer_count <= 3:
        score += 5  # Bonus for optimal layering
    elif layer_count == 1:
        score += 2  # Bonus for single layer (appropriate for some occasions)
    
    return max(score, 0.0)  # Don't go below 0


def calculate_color_score(color_analysis: Dict) -> float:
    """Calculate score for color harmony and theory."""
    if not color_analysis:
        return 70.0  # Neutral score if no color data
    
    score = 100.0  # Start with perfect score
    
    total_colors = (color_analysis.get('total_colors', 0) if color_analysis else 0)
    palette_type = (color_analysis.get('palette_type', 'neutral') if color_analysis else 'neutral')
    
    # Score based on color count
    if total_colors == 0:
        score -= 30  # No color data
    elif total_colors == 1:
        score += 10  # Monochromatic (good)
    elif 2 <= total_colors <= 4:
        score += 15  # Optimal color range
    elif total_colors > 6:
        score -= 10  # Too many colors
    
    # Score based on palette type
    if palette_type == 'neutral':
        score += 5  # Neutral palettes are versatile
    elif palette_type in ['warm', 'cool']:
        score += 10  # Cohesive temperature
    
    return max(score, 0.0)


def calculate_material_score(material_analysis: Dict) -> float:
    """Calculate score for material compatibility."""
    if not material_analysis:
        return 70.0  # Neutral score if no material data
    
    score = 100.0  # Start with perfect score
    
    material_quality = (material_analysis.get('material_quality', 'mixed') if material_analysis else 'mixed')
    natural_count = (material_analysis.get('natural_materials', 0) if material_analysis else 0)
    luxury_count = (material_analysis.get('luxury_materials', 0) if material_analysis else 0)
    
    # Score based on material quality
    if material_quality == 'luxury':
        score += 15  # Luxury materials get bonus
    elif material_quality == 'natural':
        score += 10  # Natural materials get bonus
    
    # Score based on material variety
    if natural_count > 0 and luxury_count > 0:
        score += 5  # Good mix of materials
    
    return max(score, 0.0)


def calculate_style_coherence_score(items: List[Dict], style: str, mood: str) -> float:
    """Calculate score for style and mood coherence."""
    score = 100.0  # Start with perfect score
    
    # Style-specific scoring
    style_rules = {
        "minimalist": {"max_items": 4, "description": "Fewer items for minimalist style"},
        "maximalist": {"min_items": 5, "description": "More items for maximalist style"},
        "monochrome": {"color_variety": 2, "description": "Limited color variety for monochrome"},
        "colorblock": {"min_colors": 3, "description": "Multiple colors for colorblock style"}
    }
    
    if style.lower() in style_rules:
        rule = style_rules[style.lower()]
        
        if "max_items" in rule and len(items) > rule["max_items"]:
            score -= 15  # Too many items for minimalist style
        elif "min_items" in rule and len(items) < rule["min_items"]:
            score -= 15  # Too few items for maximalist style
    
    # Mood-based scoring
    mood_rules = {
        "calm": {"max_colors": 4, "description": "Fewer colors for calm mood"},
        "energetic": {"min_colors": 3, "description": "More colors for energetic mood"},
        "sophisticated": {"min_items": 3, "description": "More items for sophisticated look"}
    }
    
    if mood.lower() in mood_rules:
        rule = mood_rules[mood.lower()]
        
        if "max_colors" in rule:
            # Count unique colors (simplified)
            colors = set()
            for item in items:
                item_color = item.get('color', '')
                if item_color:
                    colors.add(item_color.lower())
            
            if len(colors) > rule["max_colors"]:
                score -= 10  # Too many colors for calm mood
    
    return max(score, 0.0)


def interpret_score(score: float) -> str:
    """Interpret the numerical score into a meaningful description."""
    if score >= 90:
        return "Exceptional outfit with perfect harmony and style"
    elif score >= 80:
        return "Excellent outfit with great composition and few issues"
    elif score >= 70:
        return "Very good outfit with minor areas for improvement"
    elif score >= 60:
        return "Good outfit with some compatibility issues"
    elif score >= 50:
        return "Acceptable outfit with several areas for improvement"
    else:
        return "Outfit needs significant improvement in multiple areas"


def get_score_grade(score: float) -> str:
    """Convert numerical score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    else:
        return "D"


async def calculate_wardrobe_intelligence_score(items: List[Dict], user_id: str) -> float:
    """Calculate score based on wardrobe intelligence: favorites, wear history, diversity."""
    logger.info(f"🔍 DEBUG: Calculating wardrobe intelligence score for {len(items)} items")
    
    # Import db inside function to prevent import-time crashes
    try:
        from ...config.firebase import db
    except ImportError:
        logger.warning("⚠️ Firebase not available for wardrobe intelligence scoring")
        return 50.0  # Return neutral score if db unavailable
    
    # Use the provided user ID
    current_user_id = user_id
    
    total_score = 0.0
    item_scores = []
    
    for item in items:
        item_score = 0.0
        item_id = (item.get('id', '') if item else '')
        
        # Get item analytics data
        try:
            # Query item analytics collection for wear history and favorites
            analytics_ref = db.collection('item_analytics').where('item_id', '==', item_id).where('user_id', '==', current_user_id).limit(1)
            analytics_docs = analytics_ref.stream()
            analytics_data = None
            for doc in analytics_docs:
                analytics_data = doc.to_dict()
                break
            
            if analytics_data:
                # 1. Favorite Status Bonus (up to 25 points)
                # Check both analytics and wardrobe collection for favorite status
                is_favorite = (analytics_data.get('is_favorite', False) if analytics_data else False)
                
                # Also check wardrobe collection for favorite status
                try:
                    wardrobe_ref = db.collection('wardrobe').document(item_id)
                    wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None
                    if wardrobe_doc and wardrobe_doc.exists:
                        wardrobe_data = wardrobe_doc.to_dict()
                        if wardrobe_data.get('isFavorite', False):
                            is_favorite = True
                except Exception as e:
                    logger.warning(f"⚠️ Could not check wardrobe favorite status for item {item_id}: {e}")
                
                if is_favorite:
                    item_score += 25
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +25 favorite bonus")
                else:
                    # Bonus for non-favorited items that perform well in outfits
                    outfit_performance_score = await calculate_outfit_performance_score(item_id, current_user_id)
                    outfit_performance_bonus = min(10, outfit_performance_score)  # Up to 10 bonus points
                    item_score += outfit_performance_bonus
                    logger.info(f"🔍 DEBUG: Non-favorited item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{outfit_performance_bonus} performance bonus")
                
                # 2. Wear Count Scoring (up to 20 points)
                wear_count = (analytics_data.get('wear_count', 0) if analytics_data else 0)
                
                # Fallback to wardrobe collection if no analytics data
                if wear_count == 0:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
                        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None
                        if wardrobe_doc and wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            wear_count = (wardrobe_data.get('wearCount', 0) if wardrobe_data else 0)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get wear count from wardrobe for item {item_id}: {e}")
                
                if wear_count == 0:
                    item_score += 20  # Bonus for unworn items
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +20 unworn bonus")
                elif wear_count <= 3:
                    item_score += 15  # Good for moderately worn items
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +15 moderately worn bonus")
                elif wear_count <= 7:
                    item_score += 10  # Acceptable for frequently worn items
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +10 frequently worn bonus")
                else:
                    item_score += 5   # Minimal points for over-worn items
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 over-worn bonus")
                
                # 3. Recent Wear Penalty (up to -15 points)
                last_worn = (analytics_data.get('last_worn') if analytics_data else None)
                
                # Fallback to wardrobe collection if no analytics data
                if not last_worn:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
                        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None
                        if wardrobe_doc and wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            last_worn = (wardrobe_data.get('lastWorn') if wardrobe_data else None)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get last worn from wardrobe for item {item_id}: {e}")
                
                if last_worn:
                    try:
                        # Parse last_worn timestamp
                        if isinstance(last_worn, str):
                            last_worn_dt = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                        else:
                            last_worn_dt = last_worn
                        
                        days_since_worn = (datetime.now() - last_worn_dt).days
                        
                        if days_since_worn <= 1:
                            item_score -= 15  # Heavy penalty for worn yesterday
                            logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -15 penalty (worn yesterday)")
                        elif days_since_worn <= 3:
                            item_score -= 10  # Penalty for worn this week
                            logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -10 penalty (worn this week)")
                        elif days_since_worn <= 7:
                            item_score -= 5   # Light penalty for worn this month
                            logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -5 penalty (worn this month)")
                        else:
                            item_score += 5   # Bonus for items not worn recently
                            logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 bonus (not worn recently)")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse last_worn date for item {item_id}: {e}")
                        item_score += 5  # Neutral score if date parsing fails
                
                # 4. User Feedback Bonus (up to 15 points)
                feedback_rating = (analytics_data.get('average_feedback_rating', 0) if analytics_data else 0)
                if feedback_rating >= 4.5:
                    item_score += 15  # Excellent feedback
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +15 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 4.0:
                    item_score += 10  # Good feedback
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +10 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 3.5:
                    item_score += 5   # Average feedback
                    logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 feedback bonus (rating: {feedback_rating})")
                
                # 5. Style Preference Match (up to 10 points)
                style_match = (analytics_data.get('style_preference_score', 0.5) if analytics_data else 0.5)
                item_score += style_match * 10
                logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{style_match * 10:.1f} style preference bonus")
                
                # 6. Outfit Performance Bonus (up to 20 points) - NEW!
                outfit_performance_score = await calculate_outfit_performance_score(item_id, current_user_id)
                item_score += outfit_performance_score
                logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{outfit_performance_score} outfit performance bonus")
                
                # 7. Wardrobe Diversity Bonus (up to 5 points) - NEW!
                diversity_bonus = await calculate_wardrobe_diversity_bonus(item_id, current_user_id)
                item_score += diversity_bonus
                logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{diversity_bonus} diversity bonus")
                
            else:
                # No analytics data - neutral score
                item_score = 50
                logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets neutral score (no analytics data)")
            
        except Exception as e:
            logger.error(f"❌ Error calculating wardrobe intelligence for item {item_id}: {e}")
            item_score = 50  # Neutral score on error
        
        # Ensure score stays within bounds
        item_score = max(0, min(100, item_score))
        item_scores.append(item_score)
        total_score += item_score
        
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} final wardrobe score: {item_score}")
    
    # Calculate average score across all items
    if item_scores:
        average_score = total_score / len(item_scores)
        logger.info(f"🔍 DEBUG: Average wardrobe intelligence score: {average_score:.2f}")
        return round(average_score, 2)
    else:
        return 50.0  # Neutral score if no items


async def calculate_outfit_performance_score(item_id: str, user_id: str) -> float:
    """Calculate score based on how well this item performs in outfits."""
    logger.info(f"🔍 DEBUG: Calculating outfit performance score for item {item_id}")
    
    # Import db inside function to prevent import-time crashes
    try:
        from ...config.firebase import db
    except ImportError:
        logger.warning("⚠️ Firebase not available for outfit performance scoring")
        return 0.0
    
    try:
        # Query outfits that contain this item
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        outfits_docs = outfits_ref.stream()
        
        total_score = 0.0
        outfit_count = 0
        high_rated_outfits = 0
        worn_outfits = 0
        
        for outfit_doc in outfits_docs:
            outfit_data = outfit_doc.to_dict()
            outfit_items = (outfit_data.get('items', []) if outfit_data else [])
            
            # Check if this item is in this outfit
            item_in_outfit = any((item.get('id') if item else None) == item_id for item in outfit_items)
            if not item_in_outfit:
                continue
            
            outfit_count += 1
            
            # 1. Outfit Rating Bonus (up to 10 points)
            outfit_rating = (outfit_data.get('rating', 0) if outfit_data else 0)
            if outfit_rating >= 4.5:
                total_score += 10  # Excellent outfit rating
                high_rated_outfits += 1
                logger.info(f"🔍 DEBUG: Item in 5-star outfit: +10 points")
            elif outfit_rating >= 4.0:
                total_score += 8   # Very good outfit rating
                high_rated_outfits += 1
                logger.info(f"🔍 DEBUG: Item in 4-star outfit: +8 points")
            elif outfit_rating >= 3.5:
                total_score += 6   # Good outfit rating
                logger.info(f"🔍 DEBUG: Item in 3.5-star outfit: +6 points")
            elif outfit_rating >= 3.0:
                total_score += 4   # Average outfit rating
                logger.info(f"🔍 DEBUG: Item in 3-star outfit: +4 points")
            elif outfit_rating >= 2.0:
                total_score += 2   # Below average outfit rating
                logger.info(f"🔍 DEBUG: Item in 2-star outfit: +2 points")
            else:
                total_score += 0   # Poor outfit rating (no bonus)
                logger.info(f"🔍 DEBUG: Item in 1-star outfit: +0 points")
            
            # 2. Outfit Wear Count Bonus (up to 5 points)
            outfit_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
            if outfit_wear_count >= 5:
                total_score += 5   # Frequently worn outfit
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in frequently worn outfit: +5 points")
            elif outfit_wear_count >= 3:
                total_score += 3   # Moderately worn outfit
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in moderately worn outfit: +3 points")
            elif outfit_wear_count >= 1:
                total_score += 1   # Worn at least once
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in worn outfit: +1 point")
            
            # 3. Outfit Like/Dislike Bonus (up to 5 points)
            outfit_liked = (outfit_data.get('isLiked', False) if outfit_data else False)
            outfit_disliked = (outfit_data.get('isDisliked', False) if outfit_data else False)
            
            if outfit_liked:
                total_score += 5   # Liked outfit bonus
                logger.info(f"🔍 DEBUG: Item in liked outfit: +5 points")
            elif outfit_disliked:
                total_score -= 2   # Disliked outfit penalty
                logger.info(f"🔍 DEBUG: Item in disliked outfit: -2 points")
        
        # 4. Performance Multipliers
        if outfit_count > 0:
            # Average score per outfit
            base_score = total_score / outfit_count
            
            # Bonus for items that consistently perform well
            if high_rated_outfits >= 3:
                base_score *= 1.2  # 20% bonus for 3+ high-rated outfits
                logger.info(f"🔍 DEBUG: Consistency bonus: 20% multiplier for {high_rated_outfits} high-rated outfits")
            elif high_rated_outfits >= 1:
                base_score *= 1.1  # 10% bonus for at least 1 high-rated outfit
                logger.info(f"🔍 DEBUG: Performance bonus: 10% multiplier for {high_rated_outfits} high-rated outfit")
            
            # Bonus for items that create worn outfits
            if worn_outfits >= 3:
                base_score *= 1.15  # 15% bonus for 3+ worn outfits
                logger.info(f"🔍 DEBUG: Wearability bonus: 15% multiplier for {worn_outfits} worn outfits")
            elif worn_outfits >= 1:
                base_score *= 1.05  # 5% bonus for at least 1 worn outfit
                logger.info(f"🔍 DEBUG: Usability bonus: 5% multiplier for {worn_outfits} worn outfit")
            
            final_score = min(base_score, 20.0)  # Cap at 20 points
            logger.info(f"🔍 DEBUG: Final outfit performance score: {final_score:.2f} (from {outfit_count} outfits)")
            return round(final_score, 2)
        else:
            logger.info(f"🔍 DEBUG: Item not found in any outfits: 0 points")
            return 0.0
            
    except Exception as e:
        logger.error(f"❌ Error calculating outfit performance score for item {item_id}: {e}")
        return 0.0  # Return 0 on error


async def calculate_wardrobe_diversity_bonus(item_id: str, user_id: str) -> float:
    """Calculate bonus for items that add diversity to the wardrobe."""
    logger.info(f"🔍 DEBUG: Calculating wardrobe diversity bonus for item {item_id}")
    
    # Import db inside function to prevent import-time crashes
    try:
        from ...config.firebase import db
    except ImportError:
        logger.warning("⚠️ Firebase not available for wardrobe diversity scoring")
        return 0.0
    
    try:
        # Get the current item's type and color
        wardrobe_ref = db.collection('wardrobe').document(item_id)
        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None
        
        if not wardrobe_doc or not wardrobe_doc.exists:
            return 0.0
        
        current_item = wardrobe_doc.to_dict()
        current_type = (current_item.get('type', '') if current_item else '').lower()
        current_color = (current_item.get('color', '') if current_item else '').lower()
        
        # Query all user's wardrobe items
        all_wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        all_wardrobe_docs = all_wardrobe_ref.stream()
        
        type_count = 0
        color_count = 0
        total_items = 0
        
        for doc in all_wardrobe_docs:
            if doc.id == item_id:
                continue  # Skip the current item
            
            item_data = doc.to_dict()
            total_items += 1
            
            # Count items of the same type
            if item_data.get('type', '').lower() == current_type:
                type_count += 1
            
            # Count items of the same color
            if item_data.get('color', '').lower() == current_color:
                color_count += 1
        
        # Calculate diversity bonus
        diversity_score = 0.0
        
        # Type diversity (up to 3 points)
        if type_count == 0:
            diversity_score += 3  # Unique type
        elif type_count <= 2:
            diversity_score += 2  # Rare type
        elif type_count <= 5:
            diversity_score += 1  # Common type
        else:
            diversity_score += 0  # Very common type
        
        # Color diversity (up to 2 points)
        if color_count == 0:
            diversity_score += 2  # Unique color
        elif color_count <= 3:
            diversity_score += 1  # Rare color
        else:
            diversity_score += 0  # Common color
        
        logger.info(f"🔍 DEBUG: Diversity bonus: +{diversity_score} (type_count: {type_count}, color_count: {color_count})")
        return diversity_score
        
    except Exception as e:
        logger.error(f"❌ Error calculating wardrobe diversity bonus for item {item_id}: {e}")
        return 0.0

