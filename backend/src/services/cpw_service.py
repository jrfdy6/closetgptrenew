"""
Cost Per Wear (CPW) Service
Calculates and tracks cost per wear for wardrobe items
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..config.firebase import db

logger = logging.getLogger(__name__)


# Range midpoints for cost estimation
RANGE_MIDPOINTS = {
    "$0-$100": 50,
    "$100-$250": 175,
    "$250-$500": 375,
    "$500-$1,000": 750,
    "$1,000+": 1500,
    "unknown": 100  # Default fallback
}

# Category mappings for wardrobe items to spending categories
CATEGORY_TO_SPENDING_KEY = {
    # Tops
    "shirt": "tops",
    "t-shirt": "tops",
    "blouse": "tops",
    "tank_top": "tops",
    "crop_top": "tops",
    "polo": "tops",
    "dress_shirt": "tops",
    "sweater": "tops",
    "hoodie": "tops",
    "cardigan": "tops",
    
    # Bottoms
    "pants": "pants",
    "jeans": "pants",
    "chinos": "pants",
    "slacks": "pants",
    "joggers": "pants",
    "sweatpants": "pants",
    "shorts": "pants",
    "skirt": "pants",
    "mini_skirt": "pants",
    "midi_skirt": "pants",
    "maxi_skirt": "pants",
    "pencil_skirt": "pants",
    
    # Dresses
    "dress": "dresses",
    "sundress": "dresses",
    "cocktail_dress": "dresses",
    "maxi_dress": "dresses",
    "mini_dress": "dresses",
    
    # Outerwear
    "jacket": "jackets",
    "blazer": "jackets",
    "coat": "jackets",
    "vest": "jackets",
    
    # Shoes
    "shoes": "shoes",
    "sneakers": "shoes",
    "boots": "shoes",
    "sandals": "shoes",
    "heels": "shoes",
    "flats": "shoes",
    "loafers": "shoes",
    "dress_shoes": "shoes",
    
    # Accessories
    "hat": "accessories",
    "scarf": "accessories",
    "belt": "accessories",
    "jewelry": "accessories",
    "bag": "accessories",
    "watch": "accessories",
    "accessory": "accessories",
}


class CPWService:
    """Service for calculating and managing Cost Per Wear"""
    
    def __init__(self):
        self.db = db
    
    def estimate_item_cost(
        self,
        item_type: str,
        spending_ranges: Dict[str, str]
    ) -> float:
        """
        Estimate the cost of an item based on user's spending ranges
        
        Args:
            item_type: Type of clothing item
            spending_ranges: User's spending ranges by category
            
        Returns:
            Estimated cost in dollars
        """
        # Normalize item type
        item_type_lower = item_type.lower().replace(" ", "_")
        
        # Map item type to spending category
        spending_key = CATEGORY_TO_SPENDING_KEY.get(item_type_lower, "tops")
        
        # Get user's spending range for that category
        spending_range = spending_ranges.get(spending_key, "unknown")
        
        # If not sure, try to infer from annual total
        if spending_range == "unknown" or spending_range == "Not sure — estimate for me based on my wardrobe":
            annual_total = spending_ranges.get("annual_total", "unknown")
            if annual_total != "unknown":
                # Estimate based on annual total
                # Assume tops are ~25% of budget, bottoms 25%, shoes 20%, jackets 20%, accessories 10%
                category_percentages = {
                    "tops": 0.25,
                    "pants": 0.25,
                    "shoes": 0.20,
                    "jackets": 0.20,
                    "dresses": 0.15,
                    "activewear": 0.10,
                    "accessories": 0.10
                }
                
                annual_budget_midpoint = RANGE_MIDPOINTS.get(annual_total, 2000)
                category_budget = annual_budget_midpoint * category_percentages.get(spending_key, 0.20)
                
                # Estimate average items purchased per year (rough estimate)
                items_per_year = {
                    "tops": 8,
                    "pants": 5,
                    "shoes": 4,
                    "jackets": 2,
                    "dresses": 4,
                    "activewear": 6,
                    "accessories": 10
                }
                
                avg_items = items_per_year.get(spending_key, 5)
                estimated_cost = category_budget / avg_items if avg_items > 0 else 100
                
                return round(estimated_cost, 2)
        
        # Use the midpoint of the range
        return RANGE_MIDPOINTS.get(spending_range, 100)
    
    def calculate_cpw(
        self,
        estimated_cost: float,
        wear_count: int
    ) -> float:
        """
        Calculate cost per wear
        
        Args:
            estimated_cost: Estimated cost of the item
            wear_count: Number of times the item has been worn
            
        Returns:
            Cost per wear (cost / wears, or cost if never worn)
        """
        if wear_count == 0:
            return estimated_cost
        return round(estimated_cost / wear_count, 2)
    
    async def calculate_item_cpw(
        self,
        user_id: str,
        item_id: str
    ) -> Optional[float]:
        """
        Calculate CPW for a specific item
        
        Returns:
            CPW value or None if item not found
        """
        try:
            # Get user's spending ranges
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return None
            
            user_data = user_doc.to_dict()
            spending_ranges = user_data.get('spending_ranges', {})
            
            # Get item
            item_ref = self.db.collection('wardrobe').document(item_id)
            item_doc = item_ref.get()
            
            if not item_doc.exists:
                logger.error(f"Item {item_id} not found")
                return None
            
            item_data = item_doc.to_dict()
            item_type = item_data.get('type', 'other')
            wear_count = item_data.get('wearCount', 0)
            
            # Estimate cost
            estimated_cost = self.estimate_item_cost(item_type, spending_ranges)
            
            # Calculate CPW
            cpw = self.calculate_cpw(estimated_cost, wear_count)
            
            # Update item with CPW
            item_ref.update({'cpw': cpw})
            
            return cpw
            
        except Exception as e:
            logger.error(f"Error calculating CPW for item {item_id}: {e}", exc_info=True)
            return None
    
    async def recalculate_items_cpw(
        self,
        user_id: str,
        item_ids: List[str]
    ) -> Dict[str, float]:
        """
        Recalculate CPW for multiple items
        
        Returns:
            Dict mapping item_id to cpw
        """
        results = {}
        for item_id in item_ids:
            cpw = await self.calculate_item_cpw(user_id, item_id)
            if cpw is not None:
                results[item_id] = cpw
        return results
    
    async def calculate_wardrobe_average_cpw(
        self,
        user_id: str
    ) -> Optional[float]:
        """
        Calculate average CPW across all items in user's wardrobe
        
        Returns:
            Average CPW or None if no items
        """
        try:
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            items = list(wardrobe_ref.stream())
            
            if not items:
                return None
            
            total_cpw = 0
            count = 0
            
            for doc in items:
                item_data = doc.to_dict()
                cpw = item_data.get('cpw')
                
                # If CPW not calculated, calculate it now
                if cpw is None:
                    cpw = await self.calculate_item_cpw(user_id, doc.id)
                
                if cpw is not None:
                    total_cpw += cpw
                    count += 1
            
            if count == 0:
                return None
            
            avg_cpw = total_cpw / count
            return round(avg_cpw, 2)
            
        except Exception as e:
            logger.error(f"Error calculating average CPW for user {user_id}: {e}", exc_info=True)
            return None
    
    async def calculate_cpw_trend(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate CPW trend over a time period
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dict with current CPW, previous CPW, and percentage change
        """
        try:
            # Calculate current average CPW
            current_cpw = await self.calculate_wardrobe_average_cpw(user_id)
            
            if current_cpw is None:
                return {
                    "current_cpw": None,
                    "previous_cpw": None,
                    "change_percentage": 0,
                    "trend": "no_data"
                }
            
            # Get outfit history to see what was worn in the past period
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
            
            history_ref = self.db.collection('outfit_history')\
                .where('user_id', '==', user_id)\
                .where('date_worn', '>=', cutoff_timestamp)
            
            history_docs = list(history_ref.stream())
            
            # If no recent history, can't calculate trend
            if not history_docs:
                return {
                    "current_cpw": current_cpw,
                    "previous_cpw": current_cpw,
                    "change_percentage": 0,
                    "trend": "stable"
                }
            
            # Estimate previous CPW by simulating what CPW would have been
            # before these wears were logged
            # This is a simplified calculation
            
            # Count how many total wears happened in the period
            total_recent_wears = len(history_docs)
            
            # Estimate that CPW decreased by roughly the wear activity
            # This is an approximation - exact calculation would require historical snapshots
            estimated_decrease_percentage = min(total_recent_wears * 0.5, 20)  # Cap at 20% decrease
            
            if total_recent_wears > 0:
                # CPW should be decreasing with more wears
                previous_cpw = current_cpw * (1 + estimated_decrease_percentage / 100)
                change_percentage = -estimated_decrease_percentage
                trend = "decreasing"
            else:
                previous_cpw = current_cpw
                change_percentage = 0
                trend = "stable"
            
            return {
                "current_cpw": current_cpw,
                "previous_cpw": round(previous_cpw, 2),
                "change_percentage": round(change_percentage, 1),
                "trend": trend,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error calculating CPW trend for user {user_id}: {e}", exc_info=True)
            return {
                "current_cpw": None,
                "previous_cpw": None,
                "change_percentage": 0,
                "trend": "error"
            }
    
    async def recalculate_all_cpw_for_user(
        self,
        user_id: str
    ) -> int:
        """
        Batch recalculate CPW for all items in user's wardrobe
        
        Returns:
            Number of items updated
        """
        try:
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            items = list(wardrobe_ref.stream())
            
            count = 0
            for doc in items:
                cpw = await self.calculate_item_cpw(user_id, doc.id)
                if cpw is not None:
                    count += 1
            
            logger.info(f"✅ Recalculated CPW for {count} items for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error batch recalculating CPW for user {user_id}: {e}", exc_info=True)
            return 0


# Create singleton instance
cpw_service = CPWService()


# Export
__all__ = ['CPWService', 'cpw_service']

