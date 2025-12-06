"""
Total Value Extracted (TVE) Service
Calculates and tracks total value extracted from wardrobe items
Based on dynamic CPW targets and category-specific wear rates
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..config.firebase import db

logger = logging.getLogger(__name__)


# Category-specific Target Wear Rates (R) - wears per year
# Updated to benchmark against "Efficient Minimalist" standards (weekly active rotation)
# instead of wasteful industry averages ("Hoarder Standard")
TARGET_WEAR_RATES = {
    "tops": 52,        # 1/week - A good shirt is part of your weekly rotation
    "pants": 75,       # 1.5/week - Pants have higher re-wear potential
    "dresses": 25,     # 1/2 weeks - Occasion wear, but still needs frequent use
    "jackets": 50,     # Seasonal daily, averaged to 1/week annual
    "shoes": 100,      # 2/week - Good shoes are worn constantly
    "activewear": 75,  # 1.5/week - Workout gear gets heavy rotation
    "accessories": 45  # ~0.9/week - Core accessories (belt, watch) get regular use
}

# Range midpoints for cost estimation (from old CPW system)
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


class TVEService:
    """Service for calculating and managing Total Value Extracted"""
    
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
            Estimated cost in dollars (C)
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
                
                # Estimate average items purchased per year
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
    
    async def calculate_dynamic_cpw_target(
        self,
        user_id: str,
        category: str
    ) -> Optional[float]:
        """
        Calculate dynamic CPW target (Value Per Wear) for a category
        
        Formula: CPW_target = Annual Spending (S) / (Item Count (I) × Target Wear Rate (R))
        
        Args:
            user_id: User ID
            category: Spending category (tops, pants, etc.)
            
        Returns:
            CPW target (Value Per Wear) or None if cannot calculate
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
            
            # Get annual spending for category (S)
            spending_range = spending_ranges.get(category, "unknown")
            annual_spending = RANGE_MIDPOINTS.get(spending_range, 100)
            
            # Get item count in category (I)
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            items = list(wardrobe_ref.stream())
            
            # Count items in this category
            item_count = 0
            for doc in items:
                item_data = doc.to_dict()
                item_type = item_data.get('type', '').lower().replace(" ", "_")
                item_category = CATEGORY_TO_SPENDING_KEY.get(item_type, "tops")
                if item_category == category:
                    item_count += 1
            
            if item_count == 0:
                logger.warning(f"No items in category {category} for user {user_id}")
                return None
            
            # Get target wear rate for category (R)
            target_wear_rate = TARGET_WEAR_RATES.get(category, 52)  # Default to tops standard
            
            # Calculate CPW target: S / (I × R)
            cpw_target = annual_spending / (item_count * target_wear_rate)
            
            logger.info(f"CPW target for {category}: ${cpw_target:.2f} "
                       f"(S=${annual_spending}, I={item_count}, R={target_wear_rate})")
            
            return round(cpw_target, 2)
            
        except Exception as e:
            logger.error(f"Error calculating CPW target for {category}: {e}", exc_info=True)
            return None
    
    async def initialize_item_tve_fields(
        self,
        user_id: str,
        item_id: str
    ) -> bool:
        """
        Initialize TVE-related fields on an item when it's created
        
        Sets:
        - estimated_cost (C)
        - value_per_wear (V_W = CPW_target for category)
        - target_wears (T = C / V_W)
        - current_tve (starts at 0)
        
        Returns:
            True if successful
        """
        try:
            # Get item
            item_ref = self.db.collection('wardrobe').document(item_id)
            item_doc = item_ref.get()
            
            if not item_doc.exists:
                logger.error(f"Item {item_id} not found")
                return False
            
            item_data = item_doc.to_dict()
            item_type = item_data.get('type', 'other')
            
            # ✅ CRITICAL FIX: Preserve existing TVE before recalculation
            existing_tve = item_data.get('current_tve', 0.0)
            
            # Get user's spending ranges
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return False
            
            user_data = user_doc.to_dict()
            spending_ranges = user_data.get('spending_ranges', {})
            
            # Calculate estimated item cost (C)
            estimated_cost = self.estimate_item_cost(item_type, spending_ranges)
            
            # Get category
            item_type_lower = item_type.lower().replace(" ", "_")
            category = CATEGORY_TO_SPENDING_KEY.get(item_type_lower, "tops")
            
            # Calculate dynamic CPW target (V_W)
            value_per_wear = await self.calculate_dynamic_cpw_target(user_id, category)
            
            if value_per_wear is None:
                logger.warning(f"Could not calculate value_per_wear for item {item_id}")
                value_per_wear = 1.0  # Default fallback (more realistic for value standard)
            
            # Calculate target wears (T = C / V_W)
            # More reasonable fallback: if $50 item with $0.50/wear = 100 wears target
            target_wears = round(estimated_cost / value_per_wear) if value_per_wear > 0 else round(estimated_cost / 0.50)
            
            # Update item with TVE fields
            item_ref.update({
                'estimated_cost': estimated_cost,
                'value_per_wear': value_per_wear,
                'target_wears': target_wears,
                'current_tve': existing_tve  # ✅ FIX: Preserve accumulated value
            })
            
            logger.info(f"✅ Initialized TVE fields for item {item_id}: "
                       f"C=${estimated_cost}, V_W=${value_per_wear}, T={target_wears}, "
                       f"TVE preserved: ${existing_tve}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing TVE fields for item {item_id}: {e}", exc_info=True)
            return False
    
    async def increment_item_tve(
        self,
        item_id: str,
        value_per_wear: float
    ) -> bool:
        """
        Increment an item's TVE when it's worn
        
        Args:
            item_id: Item ID
            value_per_wear: Value to add (V_W)
            
        Returns:
            True if successful
        """
        try:
            item_ref = self.db.collection('wardrobe').document(item_id)
            item_doc = item_ref.get()
            
            if not item_doc.exists:
                logger.error(f"Item {item_id} not found")
                return False
            
            item_data = item_doc.to_dict()
            current_tve = item_data.get('current_tve', 0.0)
            new_tve = current_tve + value_per_wear
            
            item_ref.update({'current_tve': new_tve})
            
            logger.info(f"✅ Incremented TVE for item {item_id}: ${current_tve:.2f} → ${new_tve:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing TVE for item {item_id}: {e}", exc_info=True)
            return False
    
    async def calculate_wardrobe_tve(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive TVE statistics for user's wardrobe
        
        Returns:
            Dict with:
            - total_tve: Total value extracted across all items
            - total_wardrobe_cost: Sum of all estimated item costs (TWC)
            - percent_recouped: (TVE / TWC) × 100
            - annual_potential_range: [TWC × 0.30, TWC × 0.50]
            - tve_by_category: Category breakdown
            - lowest_progress_category: Category with lowest % recouped
        """
        try:
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            items = list(wardrobe_ref.stream())
            
            if not items:
                return {
                    "total_tve": 0,
                    "total_wardrobe_cost": 0,
                    "percent_recouped": 0,
                    "annual_potential_range": {"low": 0, "high": 0},
                    "tve_by_category": {},
                    "lowest_progress_category": None
                }
            
            total_tve = 0
            total_wardrobe_cost = 0
            tve_by_category = {}
            
            for doc in items:
                item_data = doc.to_dict()
                
                # Get TVE and cost
                current_tve = item_data.get('current_tve', 0.0)
                estimated_cost = item_data.get('estimated_cost', 0.0)
                
                # Get category
                item_type = item_data.get('type', '').lower().replace(" ", "_")
                category = CATEGORY_TO_SPENDING_KEY.get(item_type, "tops")
                
                # Aggregate
                total_tve += current_tve
                total_wardrobe_cost += estimated_cost
                
                # Category tracking
                if category not in tve_by_category:
                    tve_by_category[category] = {
                        "tve": 0,
                        "cost": 0,
                        "percent": 0
                    }
                
                tve_by_category[category]["tve"] += current_tve
                tve_by_category[category]["cost"] += estimated_cost
            
            # Calculate percentages
            percent_recouped = (total_tve / total_wardrobe_cost * 100) if total_wardrobe_cost > 0 else 0
            
            # Calculate category percentages
            for category, data in tve_by_category.items():
                data["percent"] = (data["tve"] / data["cost"] * 100) if data["cost"] > 0 else 0
            
            # Find lowest progress category
            lowest_category = None
            lowest_percent = 100
            for category, data in tve_by_category.items():
                if data["percent"] < lowest_percent:
                    lowest_percent = data["percent"]
                    lowest_category = category
            
            # Calculate annual potential range (50% to 75% of TWC)
            # Reflects higher extraction potential with weekly rotation standards
            annual_potential_range = {
                "low": round(total_wardrobe_cost * 0.50, 2),   # 50% = baseline weekly rotation
                "high": round(total_wardrobe_cost * 0.75, 2)    # 75% = active rotation (2x/week)
            }
            
            result = {
                "total_tve": round(total_tve, 2),
                "total_wardrobe_cost": round(total_wardrobe_cost, 2),
                "percent_recouped": round(percent_recouped, 1),
                "annual_potential_range": annual_potential_range,
                "tve_by_category": tve_by_category,
                "lowest_progress_category": {
                    "category": lowest_category,
                    "percent": round(lowest_percent, 1)
                } if lowest_category else None
            }
            logger.info(f"✅ TVE: Calculation complete (total: {time.time() - tve_calc_start:.2f}s)")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating wardrobe TVE for user {user_id}: {e}", exc_info=True)
            return {
                "total_tve": 0,
                "total_wardrobe_cost": 0,
                "percent_recouped": 0,
                "annual_potential_range": {"low": 0, "high": 0},
                "tve_by_category": {},
                "lowest_progress_category": None
            }
    
    async def update_user_tve_cache(
        self,
        user_id: str,
        tve_increment: float,
        category: str
    ) -> bool:
        """
        Update cached TVE totals on user document (event-triggered)
        
        Args:
            user_id: User ID
            tve_increment: Amount to add to total TVE
            category: Category to increment
            
        Returns:
            True if successful
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return False
            
            user_data = user_doc.to_dict()
            
            # Get current cached values
            current_total_tve = user_data.get('total_tve', 0.0)
            tve_by_category = user_data.get('tve_by_category', {})
            
            # Increment totals
            new_total_tve = current_total_tve + tve_increment
            
            if category in tve_by_category:
                tve_by_category[category] += tve_increment
            else:
                tve_by_category[category] = tve_increment
            
            # Update user document
            user_ref.update({
                'total_tve': new_total_tve,
                'tve_by_category': tve_by_category
            })
            
            logger.info(f"✅ Updated user {user_id} TVE cache: +${tve_increment:.2f} ({category})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user TVE cache: {e}", exc_info=True)
            return False
    
    async def recalculate_user_tve(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Recalculate TVE for all user's items using new wear rates.
        This migration function updates value_per_wear and recalculates current_tve
        based on wearCount × new_value_per_wear.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with stats about the recalculation
        """
        try:
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            items = list(wardrobe_ref.stream())
            
            if not items:
                return {
                    "success": True,
                    "message": "No items to recalculate",
                    "items_processed": 0,
                    "items_updated": 0
                }
            
            stats = {
                "items_processed": 0,
                "items_updated": 0,
                "items_skipped": 0,
                "errors": 0,
                "total_tve_before": 0.0,
                "total_tve_after": 0.0
            }
            
            # Get user's spending ranges
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            user_data = user_doc.to_dict()
            spending_ranges = user_data.get('spending_ranges', {})
            
            for doc in items:
                try:
                    item_data = doc.to_dict()
                    item_id = doc.id
                    stats["items_processed"] += 1
                    
                    # Get current values
                    old_tve = item_data.get('current_tve', 0.0)
                    stats["total_tve_before"] += old_tve
                    
                    item_type = item_data.get('type', 'other')
                    wear_count = item_data.get('wearCount', 0)
                    
                    # Calculate new estimated cost
                    estimated_cost = self.estimate_item_cost(item_type, spending_ranges)
                    
                    # Get category
                    item_type_lower = item_type.lower().replace(" ", "_")
                    category = CATEGORY_TO_SPENDING_KEY.get(item_type_lower, "tops")
                    
                    # Calculate new value_per_wear using updated rates
                    value_per_wear = await self.calculate_dynamic_cpw_target(user_id, category)
                    
                    if value_per_wear is None:
                        logger.warning(f"Could not calculate value_per_wear for item {item_id}, using default")
                        value_per_wear = 1.0
                    
                    # Calculate new target wears
                    target_wears = round(estimated_cost / value_per_wear) if value_per_wear > 0 else round(estimated_cost / 0.50)
                    
                    # Recalculate current_tve based on wear count and new value_per_wear
                    new_tve = wear_count * value_per_wear
                    
                    # Update item
                    item_ref = self.db.collection('wardrobe').document(item_id)
                    item_ref.update({
                        'estimated_cost': estimated_cost,
                        'value_per_wear': value_per_wear,
                        'target_wears': target_wears,
                        'current_tve': round(new_tve, 2)
                    })
                    
                    stats["total_tve_after"] += new_tve
                    stats["items_updated"] += 1
                    
                    logger.info(f"✅ Recalculated TVE for item {item_id}: "
                               f"wearCount={wear_count}, old_tve=${old_tve:.2f}, "
                               f"new_tve=${new_tve:.2f}, value_per_wear=${value_per_wear:.2f}")
                    
                except Exception as e:
                    logger.error(f"Error recalculating TVE for item {doc.id}: {e}", exc_info=True)
                    stats["errors"] += 1
            
            tve_change = stats["total_tve_after"] - stats["total_tve_before"]
            
            return {
                "success": True,
                "message": f"Recalculated TVE for {stats['items_updated']} items",
                "stats": {
                    "items_processed": stats["items_processed"],
                    "items_updated": stats["items_updated"],
                    "items_skipped": stats["items_skipped"],
                    "errors": stats["errors"],
                    "total_tve_before": round(stats["total_tve_before"], 2),
                    "total_tve_after": round(stats["total_tve_after"], 2),
                    "tve_change": round(tve_change, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error recalculating user TVE: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Create singleton instance
tve_service = TVEService()


# Export
__all__ = ['TVEService', 'tve_service', 'TARGET_WEAR_RATES', 'CATEGORY_TO_SPENDING_KEY']

