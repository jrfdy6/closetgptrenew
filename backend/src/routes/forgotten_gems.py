from fastapi import APIRouter, HTTPException, Depends
import logging
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..auth.auth_service import get_current_user
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
    current_user = Depends(get_current_user)
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
        
        # Implement basic scoring to return real forgotten items
        now = datetime.now()

        def compute_days_since_worn(item_dict: Dict[str, Any]) -> int:
            ts = item_dict.get('lastWorn')
            if ts is None:
                return 999 if item_dict.get('wearCount', 0) == 0 else 365
            try:
                # Handle different timestamp formats
                if hasattr(ts, 'timestamp'):
                    # Firestore DatetimeWithNanoseconds object
                    seconds = ts.timestamp()
                elif isinstance(ts, (int, float)):
                    # Already a timestamp
                    seconds = ts / 1000.0 if ts > 1e12 else ts
                else:
                    # Try to convert to datetime first
                    if hasattr(ts, 'timestamp'):
                        seconds = ts.timestamp()
                    else:
                        seconds = float(ts)
                
                if 946684800 <= seconds <= 4102444800:
                    last = datetime.fromtimestamp(seconds)
                    return max(0, (now - last).days)
                return 365
            except Exception as e:
                print(f"🔍 DEBUG: Error processing lastWorn timestamp: {e}, type: {type(ts)}")
                return 365

        scored: List[ForgottenItem] = []
        total_unworn = 0
        potential_savings = 0.0

        for it in wardrobe:
            days_since_worn = compute_days_since_worn(it)
            if days_since_worn < days_threshold:
                continue
            total_unworn += 1
            wear_count = int(it.get('wearCount', 0) or 0)
            is_fav = bool(it.get('isFavorite', False))

            # Basic rediscovery potential: 
            # more days since worn -> higher, fewer wears -> higher, favorite -> small boost
            score = 40.0
            score += min(days_since_worn / 7.0, 40.0)       # up to +40 for very old items
            score -= min(wear_count * 5.0, 25.0)            # up to -25 for commonly worn
            if is_fav:
                score += 5.0                                 # small nudge for favorites
            score = max(0.0, min(100.0, score))

            if score < min_rediscovery_potential:
                continue

            # Convert lastWorn to timestamp if it's a datetime object
            last_worn_ts = it.get('lastWorn')
            if last_worn_ts is not None:
                try:
                    if hasattr(last_worn_ts, 'timestamp'):
                        # Firestore DatetimeWithNanoseconds object
                        last_worn_ts = int(last_worn_ts.timestamp() * 1000)  # Convert to milliseconds
                    elif not isinstance(last_worn_ts, int):
                        # Try to convert to int
                        last_worn_ts = int(last_worn_ts)
                except Exception as e:
                    print(f"🔍 DEBUG: Error converting lastWorn to timestamp: {e}")
                    last_worn_ts = None

            fi = ForgottenItem(
                id=it.get('id', ''),
                name=it.get('name', f"{it.get('type', 'Item').title()}"),
                type=it.get('type', 'unknown'),
                imageUrl=it.get('imageUrl', '/placeholder.svg'),
                color=it.get('color', 'unknown'),
                style=it.get('style', []) if isinstance(it.get('style', []), list) else [],
                lastWorn=last_worn_ts,
                daysSinceWorn=days_since_worn,
                usageCount=wear_count,
                favoriteScore=5.0 if is_fav else 0.0,
                suggestedOutfits=[],
                declutterReason=None,
                rediscoveryPotential=score,
            )
            scored.append(fi)
            potential_savings += 10.0

        # If none met the min threshold, take top candidates by daysSinceWorn anyway
        if not scored:
            fallback_candidates: List[ForgottenItem] = []
            for it in wardrobe:
                dsw = compute_days_since_worn(it)
                if dsw < days_threshold:
                    continue
                wc = int(it.get('wearCount', 0) or 0)
                fav = bool(it.get('isFavorite', False))
                basic_score = 30.0 + min(dsw / 10.0, 30.0) - min(wc * 3.0, 15.0) + (5.0 if fav else 0.0)
                # Convert lastWorn to timestamp if it's a datetime object
                last_worn_ts = it.get('lastWorn')
                if last_worn_ts is not None:
                    try:
                        if hasattr(last_worn_ts, 'timestamp'):
                            # Firestore DatetimeWithNanoseconds object
                            last_worn_ts = int(last_worn_ts.timestamp() * 1000)  # Convert to milliseconds
                        elif not isinstance(last_worn_ts, int):
                            # Try to convert to int
                            last_worn_ts = int(last_worn_ts)
                    except Exception as e:
                        print(f"🔍 DEBUG: Error converting lastWorn to timestamp in fallback: {e}")
                        last_worn_ts = None

                fi = ForgottenItem(
                    id=it.get('id', ''),
                    name=it.get('name', f"{it.get('type', 'Item').title()}"),
                    type=it.get('type', 'unknown'),
                    imageUrl=it.get('imageUrl', '/placeholder.svg'),
                    color=it.get('color', 'unknown'),
                    style=it.get('style', []) if isinstance(it.get('style', []), list) else [],
                    lastWorn=last_worn_ts,
                    daysSinceWorn=dsw,
                    usageCount=wc,
                    favoriteScore=5.0 if fav else 0.0,
                    suggestedOutfits=[],
                    declutterReason=None,
                    rediscoveryPotential=max(0.0, min(100.0, basic_score)),
                )
                fallback_candidates.append(fi)
            fallback_candidates.sort(key=lambda x: x.daysSinceWorn, reverse=True)
            scored = fallback_candidates[:10]

        scored.sort(key=lambda x: x.rediscoveryPotential, reverse=True)
        scored = scored[:10]

        return ForgottenGemsResponse(
            success=True,
            data={
                "forgottenItems": [s.dict() for s in scored],
                "totalUnwornItems": total_unworn,
                "potentialSavings": round(potential_savings, 2),
                "rediscoveryOpportunities": len(scored),
                "analysis_timestamp": datetime.now().isoformat(),
            },
            message=f"Found {len(scored)} forgotten items",
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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