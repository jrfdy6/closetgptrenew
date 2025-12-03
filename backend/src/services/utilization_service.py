"""
Wardrobe Utilization Service
Calculates percentage of wardrobe worn and identifies dormant items
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..config.firebase import db

logger = logging.getLogger(__name__)


class UtilizationService:
    """Service for calculating wardrobe utilization metrics"""
    
    def __init__(self):
        self.db = db
    
    async def calculate_utilization_percentage(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate percentage of wardrobe worn in the last N days
        
        Args:
            user_id: User ID
            days: Number of days to look back (30, 60, or 90)
            
        Returns:
            Dict with utilization percentage and details
        """
        try:
            # Get all wardrobe items
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            all_items = list(wardrobe_ref.stream())
            total_items = len(all_items)
            
            if total_items == 0:
                return {
                    "utilization_percentage": 0,
                    "items_worn": 0,
                    "total_items": 0,
                    "dormant_items": 0,
                    "period_days": days
                }
            
            # Calculate cutoff timestamp
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_timestamp = cutoff_date.timestamp() * 1000
            
            # Count items worn in period
            items_worn = 0
            dormant_items = 0
            
            for doc in all_items:
                item_data = doc.to_dict()
                last_worn = item_data.get('lastWorn', 0)
                
                if last_worn and last_worn >= cutoff_timestamp:
                    items_worn += 1
                elif last_worn == 0 or last_worn < cutoff_timestamp:
                    dormant_items += 1
            
            # Calculate percentage
            utilization_percentage = (items_worn / total_items) * 100 if total_items > 0 else 0
            
            return {
                "utilization_percentage": round(utilization_percentage, 1),
                "items_worn": items_worn,
                "total_items": total_items,
                "dormant_items": dormant_items,
                "period_days": days,
                "last_calculated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating utilization: {e}", exc_info=True)
            return {
                "utilization_percentage": 0,
                "items_worn": 0,
                "total_items": 0,
                "dormant_items": 0,
                "period_days": days,
                "error": str(e)
            }
    
    async def get_dormant_items(
        self,
        user_id: str,
        days_threshold: int = 180
    ) -> List[Dict[str, Any]]:
        """
        Get items that haven't been worn in N days
        
        Args:
            user_id: User ID
            days_threshold: Days since last worn to consider dormant
            
        Returns:
            List of dormant items with details
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            cutoff_timestamp = cutoff_date.timestamp() * 1000
            
            # Get all wardrobe items
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            all_items = list(wardrobe_ref.stream())
            
            dormant_items = []
            
            for doc in all_items:
                item_data = doc.to_dict()
                last_worn = item_data.get('lastWorn', 0)
                
                # Consider dormant if never worn or not worn recently
                if last_worn == 0 or last_worn < cutoff_timestamp:
                    days_since_worn = 999 if last_worn == 0 else int((datetime.now().timestamp() * 1000 - last_worn) / (1000 * 60 * 60 * 24))
                    
                    dormant_items.append({
                        "id": doc.id,
                        "name": item_data.get('name'),
                        "type": item_data.get('type'),
                        "imageUrl": item_data.get('imageUrl'),
                        "lastWorn": last_worn,
                        "days_since_worn": days_since_worn,
                        "wearCount": item_data.get('wearCount', 0)
                    })
            
            # Sort by days since worn (most dormant first)
            dormant_items.sort(key=lambda x: x['days_since_worn'], reverse=True)
            
            return dormant_items
            
        except Exception as e:
            logger.error(f"Error getting dormant items: {e}", exc_info=True)
            return []
    
    async def calculate_category_utilization(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate utilization by category
        
        Returns:
            Dict with utilization percentage per category
        """
        try:
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            all_items = list(wardrobe_ref.stream())
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_timestamp = cutoff_date.timestamp() * 1000
            
            # Track by category
            category_stats = {}
            
            for doc in all_items:
                item_data = doc.to_dict()
                category = item_data.get('type', 'other')
                last_worn = item_data.get('lastWorn', 0)
                
                if category not in category_stats:
                    category_stats[category] = {"total": 0, "worn": 0}
                
                category_stats[category]["total"] += 1
                
                if last_worn and last_worn >= cutoff_timestamp:
                    category_stats[category]["worn"] += 1
            
            # Calculate percentages
            category_utilization = {}
            for category, stats in category_stats.items():
                percentage = (stats["worn"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                category_utilization[category] = {
                    "percentage": round(percentage, 1),
                    "worn": stats["worn"],
                    "total": stats["total"]
                }
            
            return category_utilization
            
        except Exception as e:
            logger.error(f"Error calculating category utilization: {e}", exc_info=True)
            return {}
    
    async def get_utilization_trends(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get utilization trends over different time periods
        
        Returns:
            Dict with 7, 30, 60, 90 day utilization
        """
        try:
            trends = {}
            
            for days in [7, 30, 60, 90]:
                util = await self.calculate_utilization_percentage(user_id, days)
                trends[f"{days}_days"] = util
            
            return {
                "trends": trends,
                "improvement": self._calculate_improvement(trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting utilization trends: {e}", exc_info=True)
            return {"trends": {}, "improvement": None}
    
    def _calculate_improvement(self, trends: Dict[str, Any]) -> Optional[float]:
        """Calculate if utilization is improving"""
        try:
            util_30 = trends.get("30_days", {}).get("utilization_percentage", 0)
            util_90 = trends.get("90_days", {}).get("utilization_percentage", 0)
            
            if util_90 > 0:
                improvement = ((util_30 - util_90) / util_90) * 100
                return round(improvement, 1)
            
            return None
        except:
            return None


# Create singleton instance
utilization_service = UtilizationService()


# Export
__all__ = ['UtilizationService', 'utilization_service']

