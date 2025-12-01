"""
Usage Tracking Service
Tracks monthly usage for outfit generations, wardrobe items, and other features.
Similar to flat lay quota system but for monthly limits.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

from ..config.firebase import db
from .subscription_utils import DEFAULT_SUBSCRIPTION_TIER
from .subscription_feature_access import get_user_subscription_info

logger = logging.getLogger(__name__)

# Monthly limits per tier (None = unlimited)
TIER_MONTHLY_LIMITS = {
    "tier1": {
        "outfit_generations": 100,
        "wardrobe_items": 100,
    },
    "tier2": {
        "outfit_generations": None,  # Unlimited
        "wardrobe_items": None,  # Unlimited
    },
    "tier3": {
        "outfit_generations": None,  # Unlimited
        "wardrobe_items": None,  # Unlimited
    },
}

# Monthly allowance window (30 days)
MONTHLY_ALLOWANCE_SECONDS = 30 * 24 * 60 * 60


class UsageTrackingService:
    """Service for tracking and managing monthly usage limits"""
    
    def __init__(self):
        self.db = db
        self.collection = "usage_tracking"
    
    def _get_current_month_key(self) -> str:
        """Get current month key in YYYY-MM format"""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m")
    
    def _get_month_start_timestamp(self, month_key: Optional[str] = None) -> int:
        """Get timestamp for the start of the month"""
        if month_key:
            year, month = map(int, month_key.split("-"))
            month_start = datetime(year, month, 1, tzinfo=timezone.utc)
        else:
            now = datetime.now(timezone.utc)
            month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        return int(month_start.timestamp())
    
    def _get_next_month_start_timestamp(self) -> int:
        """Get timestamp for the start of next month"""
        now = datetime.now(timezone.utc)
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_month = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        return int(next_month.timestamp())
    
    async def get_monthly_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get current month's usage for a user.
        
        Returns:
            Dict with usage counts and reset date
        """
        try:
            month_key = self._get_current_month_key()
            doc_id = f"{user_id}_{month_key}"
            doc_ref = self.db.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict() or {}
                return {
                    "outfit_generations": data.get("outfit_generations", 0),
                    "wardrobe_items": data.get("wardrobe_items", 0),
                    "month_key": month_key,
                    "reset_date": data.get("reset_date", self._get_next_month_start_timestamp()),
                }
            else:
                # No usage yet this month
                reset_date = self._get_next_month_start_timestamp()
                return {
                    "outfit_generations": 0,
                    "wardrobe_items": 0,
                    "month_key": month_key,
                    "reset_date": reset_date,
                }
        except Exception as e:
            logger.error(f"Error getting monthly usage: {e}", exc_info=True)
            return {
                "outfit_generations": 0,
                "wardrobe_items": 0,
                "month_key": self._get_current_month_key(),
                "reset_date": self._get_next_month_start_timestamp(),
            }
    
    async def track_outfit_generation(self, user_id: str) -> Dict[str, Any]:
        """
        Track an outfit generation and return updated usage.
        
        Returns:
            Dict with current usage and limit info
        """
        try:
            month_key = self._get_current_month_key()
            doc_id = f"{user_id}_{month_key}"
            doc_ref = self.db.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            
            # Get current count
            if doc.exists:
                data = doc.to_dict() or {}
                current_count = data.get("outfit_generations", 0)
            else:
                current_count = 0
            
            # Increment count
            new_count = current_count + 1
            reset_date = self._get_next_month_start_timestamp()
            
            doc_ref.set({
                "user_id": user_id,
                "month_key": month_key,
                "outfit_generations": new_count,
                "wardrobe_items": doc.to_dict().get("wardrobe_items", 0) if doc.exists else 0,
                "reset_date": reset_date,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }, merge=True)
            
            # Get user's tier and limits
            subscription_info = get_user_subscription_info(user_id)
            role = subscription_info.get("role", DEFAULT_SUBSCRIPTION_TIER)
            limits = TIER_MONTHLY_LIMITS.get(role, TIER_MONTHLY_LIMITS[DEFAULT_SUBSCRIPTION_TIER])
            limit = limits.get("outfit_generations")
            
            logger.info(f"Tracked outfit generation for user {user_id}: {new_count} (limit: {limit})")
            
            return {
                "current_count": new_count,
                "limit": limit,
                "remaining": None if limit is None else max(0, limit - new_count),
                "reset_date": reset_date,
                "can_generate": limit is None or new_count < limit,
            }
        except Exception as e:
            logger.error(f"Error tracking outfit generation: {e}", exc_info=True)
            raise
    
    async def track_item_upload(self, user_id: str) -> Dict[str, Any]:
        """
        Track a wardrobe item upload and return updated usage.
        
        Returns:
            Dict with current usage and limit info
        """
        try:
            month_key = self._get_current_month_key()
            doc_id = f"{user_id}_{month_key}"
            doc_ref = self.db.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            
            # Get current count
            if doc.exists:
                data = doc.to_dict() or {}
                current_count = data.get("wardrobe_items", 0)
            else:
                current_count = 0
            
            # Increment count
            new_count = current_count + 1
            reset_date = self._get_next_month_start_timestamp()
            
            doc_ref.set({
                "user_id": user_id,
                "month_key": month_key,
                "wardrobe_items": new_count,
                "outfit_generations": doc.to_dict().get("outfit_generations", 0) if doc.exists else 0,
                "reset_date": reset_date,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }, merge=True)
            
            # Get user's tier and limits
            subscription_info = get_user_subscription_info(user_id)
            role = subscription_info.get("role", DEFAULT_SUBSCRIPTION_TIER)
            limits = TIER_MONTHLY_LIMITS.get(role, TIER_MONTHLY_LIMITS[DEFAULT_SUBSCRIPTION_TIER])
            limit = limits.get("wardrobe_items")
            
            logger.info(f"Tracked item upload for user {user_id}: {new_count} (limit: {limit})")
            
            return {
                "current_count": new_count,
                "limit": limit,
                "remaining": None if limit is None else max(0, limit - new_count),
                "reset_date": reset_date,
                "can_upload": limit is None or new_count < limit,
            }
        except Exception as e:
            logger.error(f"Error tracking item upload: {e}", exc_info=True)
            raise
    
    async def check_generation_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user can generate an outfit based on their monthly limit.
        
        Returns:
            Dict with limit check results
        """
        try:
            usage = await self.get_monthly_usage(user_id)
            subscription_info = get_user_subscription_info(user_id)
            role = subscription_info.get("role", DEFAULT_SUBSCRIPTION_TIER)
            limits = TIER_MONTHLY_LIMITS.get(role, TIER_MONTHLY_LIMITS[DEFAULT_SUBSCRIPTION_TIER])
            limit = limits.get("outfit_generations")
            
            current_count = usage.get("outfit_generations", 0)
            can_generate = limit is None or current_count < limit
            remaining = None if limit is None else max(0, limit - current_count)
            
            # Format reset date
            reset_timestamp = usage.get("reset_date", self._get_next_month_start_timestamp())
            if reset_timestamp and reset_timestamp > 0:
                reset_date = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
                reset_date_str = reset_date.strftime("%B %d, %Y")
            else:
                reset_date_str = None
            
            message = None
            if not can_generate:
                reset_msg = reset_date_str if reset_date_str else "the 1st of next month"
                message = f"You've reached your monthly limit of {limit} outfit generations. Upgrade for unlimited or wait until {reset_msg}."
            
            return {
                "can_generate": can_generate,
                "current_count": current_count,
                "limit": limit,
                "remaining": remaining,
                "reset_date": reset_timestamp,
                "reset_date_str": reset_date_str,
                "message": message,
                "unlimited": limit is None,
            }
        except Exception as e:
            logger.error(f"Error checking generation limit: {e}", exc_info=True)
            # Default to allowing if check fails
            return {
                "can_generate": True,
                "current_count": 0,
                "limit": None,
                "remaining": None,
                "reset_date": self._get_next_month_start_timestamp(),
                "reset_date_str": "Unknown",
                "message": None,
                "unlimited": True,
            }
    
    async def check_item_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user can upload an item based on their monthly limit.
        
        Returns:
            Dict with limit check results
        """
        try:
            usage = await self.get_monthly_usage(user_id)
            subscription_info = get_user_subscription_info(user_id)
            role = subscription_info.get("role", DEFAULT_SUBSCRIPTION_TIER)
            limits = TIER_MONTHLY_LIMITS.get(role, TIER_MONTHLY_LIMITS[DEFAULT_SUBSCRIPTION_TIER])
            limit = limits.get("wardrobe_items")
            
            current_count = usage.get("wardrobe_items", 0)
            can_upload = limit is None or current_count < limit
            remaining = None if limit is None else max(0, limit - current_count)
            
            # Format reset date
            reset_timestamp = usage.get("reset_date", self._get_next_month_start_timestamp())
            if reset_timestamp and reset_timestamp > 0:
                reset_date = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
                reset_date_str = reset_date.strftime("%B %d, %Y")
            else:
                reset_date_str = None
            
            message = None
            if not can_upload:
                reset_msg = reset_date_str if reset_date_str else "the 1st of next month"
                message = f"You've reached your monthly limit of {limit} wardrobe items. Upgrade for unlimited or wait until {reset_msg}."
            
            return {
                "can_upload": can_upload,
                "current_count": current_count,
                "limit": limit,
                "remaining": remaining,
                "reset_date": reset_timestamp,
                "reset_date_str": reset_date_str,
                "message": message,
                "unlimited": limit is None,
            }
        except Exception as e:
            logger.error(f"Error checking item limit: {e}", exc_info=True)
            # Default to allowing if check fails
            return {
                "can_upload": True,
                "current_count": 0,
                "limit": None,
                "remaining": None,
                "reset_date": self._get_next_month_start_timestamp(),
                "reset_date_str": "Unknown",
                "message": None,
                "unlimited": True,
            }

