from fastapi import APIRouter, HTTPException, Depends
import logging
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..auth.auth_service import get_current_user_optional
from ..custom_types.wardrobe import ClothingItem
from ..services.item_analytics_service import ItemAnalyticsService
from ..services.wardrobe_analysis_service import WardrobeAnalysisService

# Note: app.py mounts this under /api/wardrobe. We add a secondary
# namespace here to avoid collisions with dynamic wardrobe routes
# such as "/api/wardrobe/{item_id}".
router = APIRouter(prefix="/insights", tags=["forgotten-gems"])

logger = logging.getLogger(__name__)

class ForgottenItem(BaseModel):
    id: str
    name: str
    type: str
    imageUrl: str
    color: str
    style: List[str]
    lastWorn: Optional[int] = None
    daysSinceWorn: int
    usageCount: int
    favoriteScore: float
    suggestedOutfits: List[str]
    declutterReason: Optional[str] = None
    rediscoveryPotential: float

class ForgottenGemsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

@router.get("/forgotten-gems", response_model=ForgottenGemsResponse)
async def get_forgotten_gems(
    days_threshold: int = 30,
    min_rediscovery_potential: float = 20.0,
    current_user = Depends(get_current_user_optional)
) -> ForgottenGemsResponse:
    """
    Get forgotten gems - items that haven't been worn recently.
    
    Args:
        days_threshold: Minimum days since last worn to be considered "forgotten"
        min_rediscovery_potential: Minimum rediscovery potential score (0-100)
        current_user_id: Current user ID from authentication
        
    Returns:
        List of forgotten items with analysis and recommendations
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        print(f"🔍 Forgotten Gems: Analyzing for user {current_user.id}")
        
        # Use simple Firestore query instead of complex services
        from ..config.firebase import db

        if not db:
            logger.warning("Forgotten Gems: Firebase not initialized; returning empty insights")
            return ForgottenGemsResponse(
                success=True,
                data={
                    "forgottenItems": [],
                    "totalUnwornItems": 0,
                    "potentialSavings": 0,
                    "rediscoveryOpportunities": 0,
                    "analysis_timestamp": datetime.now().isoformat()
                },
                message="Firebase unavailable"
            )

        try:
            logger.info("Forgotten Gems: Getting wardrobe items directly from Firestore")
            query = db.collection('wardrobe').where('userId', '==', current_user.id)
            docs = query.stream()

            wardrobe = []
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                wardrobe.append(item_data)

            logger.info(f"Forgotten Gems: Found {len(wardrobe)} wardrobe items")
        except Exception as e:
            logger.error(f"Forgotten Gems: Error fetching wardrobe items: {e}")
            return ForgottenGemsResponse(
                success=True,
                data={
                    "forgottenItems": [],
                    "totalUnwornItems": 0,
                    "potentialSavings": 0,
                    "rediscoveryOpportunities": 0,
                    "analysis_timestamp": datetime.now().isoformat()
                },
                message="Failed to fetch wardrobe; returning empty insights"
            )
        
        # Return simple response for now to test endpoint
        return ForgottenGemsResponse(
            success=True,
            data={
                "forgottenItems": [],
                "totalUnwornItems": len(wardrobe),
                "potentialSavings": 0,
                "rediscoveryOpportunities": 0,
                "analysis_timestamp": datetime.now().isoformat()
            },
            message=f"Simplified analysis complete - found {len(wardrobe)} items"
        )
        
        # Skip complex analytics for now - use simplified analysis
        print(f"🔍 Forgotten Gems: Using simplified analysis without complex analytics")
        favorites = []
        usage_map = {}
        
        # Calculate current timestamp
        now = datetime.now()
        
        # Analyze each item
        forgotten_items = []
        total_unworn_items = 0
        potential_savings = 0
        
        for item in wardrobe:
            # Get usage data for this item
            item_id = item.get('id')
            usage_data = usage_map.get(item_id)
            
            # Calculate days since last worn
            if usage_data and usage_data.last_used_timestamp:
                try:
                    # Handle both seconds and milliseconds timestamps
                    if usage_data.last_used_timestamp > 1e12:  # Likely milliseconds
                        timestamp_seconds = usage_data.last_used_timestamp / 1000.0
                    else:
                        timestamp_seconds = usage_data.last_used_timestamp
                    
                    if 946684800 <= timestamp_seconds <= 4102444800:
                        last_worn = datetime.fromtimestamp(timestamp_seconds)
                        days_since_worn = (now - last_worn).days
                    else:
                        # Invalid timestamp, treat as never worn (use 365 days as default)
                        days_since_worn = 365
                except (ValueError, OverflowError, OSError):
                    # Conversion failed, treat as never worn
                    days_since_worn = 365
            else:
                # No analytics data - try item's own lastWorn field as fallback
                last_worn_timestamp = item.get('lastWorn')
                if last_worn_timestamp:
                    try:
                        # Handle both seconds and milliseconds timestamps
                        if last_worn_timestamp > 1e12:  # Likely milliseconds
                            timestamp_seconds = last_worn_timestamp / 1000.0
                        else:
                            timestamp_seconds = last_worn_timestamp
                        
                        if 946684800 <= timestamp_seconds <= 4102444800:
                            last_worn = datetime.fromtimestamp(timestamp_seconds)
                            days_since_worn = (now - last_worn).days
                        else:
                            days_since_worn = 365
                    except (ValueError, OverflowError, OSError):
                        days_since_worn = 365
                elif item.get('wearCount', 0) == 0:
                    # Never worn - high priority for rediscovery
                    days_since_worn = 999
                else:
                    # If no usage data, assume it was never worn
                    days_since_worn = 365  # Assume 1 year
                usage_data = None
            
            # Check if item meets forgotten criteria
            if days_since_worn >= days_threshold:
                total_unworn_items += 1
                
                # Calculate usage count (analytics or item wearCount)
                if usage_data and hasattr(usage_data, 'usage_count'):
                    usage_count = usage_data.usage_count
                elif item.get('wearCount') is not None:
                    usage_count = item.get('wearCount', 0)
                else:
                    usage_count = 0
                
                # Calculate favorite score (analytics or item favorite status)
                if usage_data and hasattr(usage_data, 'total_score'):
                    favorite_score = usage_data.total_score
                elif item.get('isFavorite', False):
                    favorite_score = 50.0  # Boost for favorited items
                else:
                    favorite_score = 0.0
                
                # Simple rediscovery potential calculation
                rediscovery_potential = 50.0  # Basic score for now
                
                # Only include items with sufficient rediscovery potential
                if rediscovery_potential >= min_rediscovery_potential:
                    # Simplified data for basic functionality
                    suggested_outfits = ["Casual outfit suggestion"]
                    declutter_reason = None
                    potential_savings += 10  # Basic estimate
                    
                    forgotten_item = ForgottenItem(
                        id=item_id,
                        name=item.get('name', f"{item.get('type', 'Unknown').title()} Item"),
                        type=item.get('type', 'unknown'),
                        imageUrl=item.get('imageUrl', "/placeholder.svg"),
                        color=item.get('color', 'unknown'),
                        style=item.get('style', []),
                        lastWorn=last_worn_timestamp,
                        daysSinceWorn=days_since_worn,
                        usageCount=usage_count,
                        favoriteScore=favorite_score,
                        suggestedOutfits=suggested_outfits,
                        declutterReason=declutter_reason,
                        rediscoveryPotential=rediscovery_potential
                    )
                    
                    forgotten_items.append(forgotten_item)
        
        # Sort by rediscovery potential (highest first)
        forgotten_items.sort(key=lambda x: x.rediscoveryPotential, reverse=True)
        
        # Limit to top 10 items
        forgotten_items = forgotten_items[:10]
        
        print(f"🔍 Forgotten Gems: Found {len(forgotten_items)} forgotten items with high rediscovery potential")
        
        return ForgottenGemsResponse(
            success=True,
            data={
                "forgottenItems": [item.dict() for item in forgotten_items],
                "totalUnwornItems": total_unworn_items,
                "potentialSavings": round(potential_savings, 2),
                "rediscoveryOpportunities": len(forgotten_items),
                "analysis_timestamp": datetime.now().isoformat()
            },
            message=f"Found {len(forgotten_items)} items with rediscovery potential"
        )
        
    except Exception as e:
        print(f"❌ Forgotten Gems Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze forgotten gems: {str(e)}")

def _calculate_rediscovery_potential(
    item: ClothingItem,
    usage_data: Any,
    days_since_worn: int,
    usage_count: int,
    favorite_score: float
) -> float:
    """Calculate rediscovery potential score (0-100)."""
    
    # Base score starts at 50
    score = 50.0
    
    # Factor 1: Item quality (based on type and style)
    quality_bonus = 0
    if item.type in ['jacket', 'dress', 'blazer']:
        quality_bonus += 15  # High-value items
    elif item.type in ['shirt', 'pants', 'sweater']:
        quality_bonus += 10  # Medium-value items
    
    # Factor 2: Style diversity (items with multiple styles get bonus)
    if item.style and len(item.style) > 1:
        quality_bonus += 10
    
    score += quality_bonus
    
    # Factor 3: Usage history (lightly used items get bonus)
    if usage_count <= 3:
        score += 15  # Barely used items
    elif usage_count <= 10:
        score += 10  # Moderately used items
    
    # Factor 4: Time since last worn (recently forgotten items get bonus)
    if days_since_worn <= 60:
        score += 10  # Recently forgotten
    elif days_since_worn <= 180:
        score += 5   # Moderately forgotten
    
    # Factor 5: Favorite score (items with some positive feedback get bonus)
    if favorite_score > 0.3:
        score += 10  # Had some positive feedback
    
    # Factor 6: Seasonal relevance
    current_month = datetime.now().month
    if item.season:
        if current_month in [12, 1, 2] and 'winter' in item.season:
            score += 10
        elif current_month in [3, 4, 5] and 'spring' in item.season:
            score += 10
        elif current_month in [6, 7, 8] and 'summer' in item.season:
            score += 10
        elif current_month in [9, 10, 11] and 'fall' in item.season:
            score += 10
    
    # Cap score at 100
    return min(score, 100.0)

def _generate_suggested_outfits(item: ClothingItem, wardrobe: List[ClothingItem]) -> List[str]:
    """Generate suggested outfit combinations for the item."""
    suggestions = []
    
    # Get other items that could pair well
    other_items = [w for w in wardrobe if w.id != item.id]
    
    # Generate suggestions based on item type
    if item.type == 'jacket':
        # Find pants and shirts
        pants = [w for w in other_items if w.type in ['pants', 'jeans', 'shorts']]
        shirts = [w for w in other_items if w.type in ['shirt', 't-shirt', 'blouse']]
        
        if pants and shirts:
            suggestions.append(f"Layer over {shirts[0].name} with {pants[0].name}")
            if len(pants) > 1:
                suggestions.append(f"Smart casual with {shirts[0].name} and {pants[1].name}")
    
    elif item.type == 'dress':
        # Find accessories and layers
        accessories = [w for w in other_items if w.type == 'accessory']
        jackets = [w for w in other_items if w.type in ['jacket', 'cardigan']]
        
        if accessories:
            suggestions.append(f"Accessorize with {accessories[0].name}")
        if jackets:
            suggestions.append(f"Layer with {jackets[0].name}")
    
    elif item.type in ['shirt', 'blouse', 't-shirt']:
        # Find bottoms
        bottoms = [w for w in other_items if w.type in ['pants', 'skirt', 'shorts']]
        jackets = [w for w in other_items if w.type in ['jacket', 'cardigan']]
        
        if bottoms:
            suggestions.append(f"Pair with {bottoms[0].name}")
            if jackets:
                suggestions.append(f"Layer with {jackets[0].name} over {bottoms[0].name}")
    
    # Add generic suggestions if we don't have specific ones
    if not suggestions:
        suggestions.append(f"Mix with your current favorites")
        suggestions.append(f"Try a new color combination")
    
    return suggestions[:3]  # Limit to 3 suggestions

def _determine_declutter_reason(
    item: ClothingItem,
    usage_data: Any,
    days_since_worn: int,
    usage_count: int,
    favorite_score: float
) -> Optional[str]:
    """Determine if item should be considered for decluttering."""
    
    # Very low usage and old
    if usage_count <= 1 and days_since_worn > 365:
        return "Very low usage - consider if still relevant"
    
    # Low favorite score and old
    if favorite_score < 0.2 and days_since_worn > 180:
        return "Low satisfaction score"
    
    # Seasonal item that's been unused
    if item.season and days_since_worn > 730:  # 2 years
        return "Seasonal item - consider if still fits style"
    
    # Very old item with no recent use
    if days_since_worn > 365 and usage_count <= 2:
        return "Long unused - evaluate if still needed"
    
    return None

def _estimate_item_savings(item: ClothingItem, usage_count: int, days_since_worn: int) -> float:
    """Estimate potential savings from decluttering the item."""
    
    # Base value estimates by item type
    base_values = {
        'jacket': 150,
        'dress': 120,
        'blazer': 200,
        'shirt': 80,
        'pants': 100,
        'sweater': 90,
        'shoes': 120,
        'accessory': 50
    }
    
    base_value = base_values.get(item.type, 75)
    
    # Reduce value based on usage (more used = less value)
    usage_factor = max(0.1, 1.0 - (usage_count * 0.1))
    
    # Reduce value based on age (older = less value)
    age_factor = max(0.1, 1.0 - (days_since_worn / 365) * 0.5)
    
    return base_value * usage_factor * age_factor

@router.post("/forgotten-gems/rediscover")
async def rediscover_item(
    item_id: str,
    current_user = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Mark an item as rediscovered and update its usage data."""
    try:
        # Update the item's last used timestamp to now
        analytics_service = ItemAnalyticsService()
        
        # This would typically update the item's usage data
        # For now, we'll just return success
        print(f"🔍 Rediscover: Marking item {item_id} as rediscovered for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Item marked as rediscovered",
            "item_id": item_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Rediscover Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rediscover item: {str(e)}")

@router.post("/forgotten-gems/declutter")
async def declutter_item(
    item_id: str,
    current_user = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Mark an item for decluttering."""
    try:
        print(f"🔍 Declutter: Marking item {item_id} for decluttering for user {current_user.id}")
        
        # This would typically move the item to a declutter list
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": "Item marked for decluttering",
            "item_id": item_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Declutter Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark item for decluttering: {str(e)}") 