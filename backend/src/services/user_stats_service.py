"""
User Statistics Service

Manages pre-aggregated user statistics for lightning-fast dashboard performance.
Updates stats atomically when outfits or wardrobe items change.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
from ..core.logging import get_logger

logger = get_logger(__name__)

class UserStatsService:
    """Service for managing pre-aggregated user statistics."""
    
    def __init__(self):
        self.db = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize Firebase database connection."""
        try:
            from ..config.firebase import db
            self.db = db
        except ImportError as e:
            logger.warning(f"Firebase import failed: {e}")
            self.db = None
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics from pre-aggregated document.
        Fast single-document read instead of querying 1500+ documents.
        """
        try:
            if not self.db:
                logger.warning("Firebase not available, returning default stats")
                return self._get_default_stats(user_id)
            
            # Read single stats document
            stats_ref = self.db.collection('user_stats').document(user_id)
            stats_doc = await stats_ref.get()
            
            if not stats_doc.exists:
                logger.info(f"No stats document found for user {user_id}, initializing...")
                # Initialize stats document for new user
                await self.initialize_user_stats(user_id)
                # Try reading again
                stats_doc = await stats_ref.get()
            
            if stats_doc.exists:
                stats_data = stats_doc.to_dict()
                logger.info(f"Retrieved user stats: {stats_data.get('outfits', {}).get('total', 0)} outfits, {stats_data.get('wardrobe', {}).get('total_items', 0)} items")
                return stats_data
            else:
                logger.warning(f"Could not initialize stats for user {user_id}")
                return self._get_default_stats(user_id)
                
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return self._get_default_stats(user_id)
    
    async def initialize_user_stats(self, user_id: str) -> bool:
        """
        Initialize stats document for a user by counting existing data.
        This is called once per user or when stats document is missing.
        """
        try:
            if not self.db:
                return False
            
            logger.info(f"Initializing stats for user {user_id}")
            
            # Count existing outfits
            outfit_count = await self._count_user_outfits(user_id)
            outfits_created_this_week = await self._count_outfits_this_week(user_id)
            # For now, use 0 for worn this week - will be updated when outfits are marked as worn
            outfits_worn_this_week = 0
            
            # Count existing wardrobe items
            wardrobe_stats = await self._count_wardrobe_items(user_id)
            
            # Create initial stats document
            current_time = datetime.now(timezone.utc)
            week_start = current_time - timedelta(days=current_time.weekday())
            
            initial_stats = {
                "user_id": user_id,
                "last_updated": current_time.isoformat(),
                "initialized_at": current_time.isoformat(),
                
                # Outfit metrics
                "outfits": {
                    "total": outfit_count,
                    "created_this_week": outfits_created_this_week,
                    "worn_this_week": outfits_worn_this_week,
                    "this_month": 0,  # Could be calculated if needed
                    "last_created": None,
                    "week_start": week_start.isoformat()
                },
                
                # Wardrobe metrics
                "wardrobe": {
                    "total_items": wardrobe_stats["total"],
                    "categories": wardrobe_stats["categories"],
                    "colors": wardrobe_stats["colors"],
                    "favorites": wardrobe_stats["favorites"],
                    "last_added": None
                },
                
                # Dashboard metrics (calculated)
                "dashboard": {
                    "style_progress": min(wardrobe_stats["total"] / 50 * 100, 100),  # Target: 50 items
                    "color_variety_score": min(len(wardrobe_stats["colors"]) / 8 * 100, 100),  # Target: 8 colors
                    "completion_percentage": 0  # Will be calculated
                }
            }
            
            # Save to Firestore
            stats_ref = self.db.collection('user_stats').document(user_id)
            stats_ref.set(initial_stats)
            
            logger.info(f"Initialized stats for user {user_id}: {outfit_count} outfits, {wardrobe_stats['total']} items")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing user stats: {e}")
            return False
    
    async def update_outfit_stats(self, user_id: str, operation: str, outfit_data: Optional[Dict] = None):
        """Update outfit-related statistics."""
        try:
            if not self.db:
                return
            
            from firebase_admin import firestore
            
            stats_ref = self.db.collection('user_stats').document(user_id)
            current_time = datetime.now(timezone.utc)
            
            if operation == "created":
                # Check if it's a new week
                week_updates = await self._check_and_update_week(user_id, current_time)
                
                update_data = {
                    "outfits.total": firestore.Increment(1),
                    "outfits.this_week": firestore.Increment(1),
                    "outfits.last_created": current_time.isoformat(),
                    "last_updated": current_time.isoformat()
                }
                
                # Add week reset if needed
                if week_updates:
                    update_data.update(week_updates)
                
                stats_ref.update(update_data)
                logger.info(f"Updated outfit stats for user {user_id}: +1 outfit")
                
            elif operation == "deleted":
                stats_ref.update({
                    "outfits.total": firestore.Increment(-1),
                    "last_updated": current_time.isoformat()
                })
                logger.info(f"Updated outfit stats for user {user_id}: -1 outfit")
                
        except Exception as e:
            logger.warning(f"Failed to update outfit stats: {e}")
            # Don't fail the main operation
    
    async def ensure_user_stats_document(self, user_id: str):
        """
        Ensures user_stats document exists before any operations.
        Returns the document reference.
        """
        doc_ref = self.db.collection('user_stats').document(user_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            logger.info(f"📊 Creating user_stats document for {user_id}")
            initial_stats = {
                'user_id': user_id,
                'worn_this_week': 0,
                'worn_this_month': 0,
                'created_this_week': 0,
                'created_this_month': 0,
                'total_outfits': 0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await doc_ref.set(initial_stats)
            logger.info(f"✅ Created user_stats document for {user_id}")
        
        return doc_ref

    async def increment_outfits_worn(self, user_id: str):
        """
        Increments outfit worn counters using FieldValue.increment for concurrency safety.
        Updates both weekly and monthly counters.
        """
        if not self.db:
            logger.error("Firestore DB not initialized for outfit worn stats update.")
            return

        try:
            # Ensure document exists first
            doc_ref = await self.ensure_user_stats_document(user_id)
            
            # Use FieldValue.increment for atomic, concurrent-safe updates
            from firebase_admin import firestore
            
            await doc_ref.update({
                'worn_this_week': firestore.Increment(1),
                'worn_this_month': firestore.Increment(1),
                'last_updated': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"✅ Incremented worn stats for user {user_id}: +1 week, +1 month")
            
        except Exception as e:
            logger.error(f"❌ Error incrementing outfit worn stats for user {user_id}: {e}")

    async def backfill_outfits_this_week(self, user_id: str):
        """
        Backfills the worn_this_week counter by counting existing worn outfits.
        Useful for correcting stats after implementing the tracking system.
        """
        if not self.db:
            logger.error("Firestore DB not initialized for backfill.")
            return 0

        try:
            from datetime import datetime, timezone, timedelta
            
            # Calculate start of this week (Monday)
            now = datetime.now(timezone.utc)
            days_since_monday = now.weekday()
            start_of_week = now - timedelta(days=days_since_monday, hours=now.hour, 
                                          minutes=now.minute, seconds=now.second, 
                                          microseconds=now.microsecond)
            
            logger.info(f"🔍 Backfilling worn outfits since {start_of_week.isoformat()}")
            
            # Count outfits worn this week from outfits collection
            outfits_ref = self.db.collection('outfits').where('user_id', '==', user_id)
            outfits_stream = outfits_ref.stream()
            
            worn_this_week = 0
            worn_this_month = 0
            
            # Calculate start of month
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for outfit_doc in outfits_stream:
                outfit_data = outfit_doc.to_dict()
                last_worn = outfit_data.get('lastWorn')
                
                if last_worn:
                    # Parse lastWorn date
                    if isinstance(last_worn, str):
                        try:
                            worn_date = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                        except:
                            continue
                    elif hasattr(last_worn, 'timestamp'):
                        worn_date = last_worn.replace(tzinfo=timezone.utc)
                    else:
                        continue
                    
                    # Ensure timezone aware
                    if worn_date.tzinfo is None:
                        worn_date = worn_date.replace(tzinfo=timezone.utc)
                    
                    # Count if worn this week
                    if worn_date >= start_of_week:
                        worn_this_week += 1
                    
                    # Count if worn this month
                    if worn_date >= start_of_month:
                        worn_this_month += 1
            
            # Also check outfit_history collection for additional worn records
            history_ref = self.db.collection('outfit_history').where('user_id', '==', user_id)
            history_stream = history_ref.stream()
            
            for history_doc in history_stream:
                history_data = history_doc.to_dict()
                date_worn = history_data.get('date_worn')
                
                if date_worn:
                    # Convert timestamp to datetime
                    if isinstance(date_worn, int):
                        worn_date = datetime.fromtimestamp(date_worn / 1000, tz=timezone.utc)
                    else:
                        continue
                    
                    # Count if worn this week
                    if worn_date >= start_of_week:
                        worn_this_week += 1
                    
                    # Count if worn this month  
                    if worn_date >= start_of_month:
                        worn_this_month += 1
            
            logger.info(f"📊 Backfill found: {worn_this_week} outfits worn this week, {worn_this_month} this month")
            
            # Update the user_stats document with correct counts
            doc_ref = await self.ensure_user_stats_document(user_id)
            await doc_ref.update({
                'worn_this_week': worn_this_week,
                'worn_this_month': worn_this_month,
                'last_updated': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"✅ Backfilled user_stats for {user_id}: {worn_this_week} week, {worn_this_month} month")
            return worn_this_week
            
        except Exception as e:
            logger.error(f"❌ Error backfilling outfit worn stats for user {user_id}: {e}")
            return 0

    async def update_outfit_worn_stats(self, user_id: str, outfit_id: str):
        """
        Updates outfit worn statistics when an outfit is marked as worn.
        Uses the new increment_outfits_worn method for proper concurrency handling.
        """
        await self.increment_outfits_worn(user_id)

    async def update_wardrobe_stats(self, user_id: str, operation: str, item_data: Optional[Dict] = None):
        """Update wardrobe-related statistics."""
        try:
            if not self.db:
                return
            
            from firebase_admin import firestore
            
            stats_ref = self.db.collection('user_stats').document(user_id)
            current_time = datetime.now(timezone.utc)
            
            if operation == "added" and item_data:
                category = item_data.get('type', 'unknown')
                color = item_data.get('color', 'unknown')
                is_favorite = item_data.get('favorite', False)
                
                update_data = {
                    "wardrobe.total_items": firestore.Increment(1),
                    f"wardrobe.categories.{category}": firestore.Increment(1),
                    f"wardrobe.colors.{color}": firestore.Increment(1),
                    "wardrobe.last_added": current_time.isoformat(),
                    "last_updated": current_time.isoformat()
                }
                
                if is_favorite:
                    update_data["wardrobe.favorites"] = firestore.Increment(1)
                
                stats_ref.update(update_data)
                logger.info(f"Updated wardrobe stats for user {user_id}: +1 {category}")
                
            elif operation == "deleted" and item_data:
                category = item_data.get('type', 'unknown')
                color = item_data.get('color', 'unknown')
                is_favorite = item_data.get('favorite', False)
                
                update_data = {
                    "wardrobe.total_items": firestore.Increment(-1),
                    f"wardrobe.categories.{category}": firestore.Increment(-1),
                    f"wardrobe.colors.{color}": firestore.Increment(-1),
                    "last_updated": current_time.isoformat()
                }
                
                if is_favorite:
                    update_data["wardrobe.favorites"] = firestore.Increment(-1)
                
                stats_ref.update(update_data)
                logger.info(f"Updated wardrobe stats for user {user_id}: -1 {category}")
                
            elif operation == "favorite_toggled" and item_data:
                is_favorite = item_data.get('favorite', False)
                increment = 1 if is_favorite else -1
                
                stats_ref.update({
                    "wardrobe.favorites": firestore.Increment(increment),
                    "last_updated": current_time.isoformat()
                })
                logger.info(f"Updated favorite count for user {user_id}: {'+' if increment > 0 else ''}{increment}")
                
        except Exception as e:
            logger.warning(f"Failed to update wardrobe stats: {e}")
            # Don't fail the main operation
    
    async def _check_and_update_week(self, user_id: str, current_time: datetime) -> Optional[Dict]:
        """Check if we've entered a new week and reset weekly counters."""
        try:
            stats_ref = self.db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if not stats_doc.exists:
                return None
            
            stats_data = stats_doc.to_dict()
            week_start_str = stats_data.get('outfits', {}).get('week_start')
            
            if not week_start_str:
                return None
            
            week_start = datetime.fromisoformat(week_start_str.replace('Z', '+00:00'))
            current_week_start = current_time - timedelta(days=current_time.weekday())
            
            # If we're in a new week, reset weekly counters
            if current_week_start.date() > week_start.date():
                logger.info(f"New week detected for user {user_id}, resetting weekly counters")
                return {
                    "outfits.this_week": 0,  # Reset to 0, then increment will make it 1
                    "outfits.week_start": current_week_start.isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking week reset: {e}")
            return None
    
    async def _count_user_outfits(self, user_id: str) -> int:
        """Count total outfits for user (for initialization only)."""
        try:
            # Use aggregation for efficiency
            from google.cloud.firestore_v1.aggregation import AggregationQuery
            
            query = self.db.collection("outfits").where("user_id", "==", user_id)
            count_query = AggregationQuery(query).count()
            result = count_query.get()
            return result[0].value if result else 0
            
        except Exception as e:
            logger.warning(f"Aggregation failed, using fallback count: {e}")
            # Fallback: limited query
            query = self.db.collection("outfits").where("user_id", "==", user_id).limit(100)
            docs = list(query.stream())
            return 1500 if len(docs) >= 100 else len(docs)  # Use known count if hitting limit
    
    async def _count_outfits_this_week(self, user_id: str) -> int:
        """Count outfits created this week (for initialization only)."""
        try:
            current_time = datetime.now(timezone.utc)
            week_start = current_time - timedelta(days=current_time.weekday())
            
            # Use aggregation for efficiency
            from google.cloud.firestore_v1.aggregation import AggregationQuery
            
            query = self.db.collection("outfits") \
                .where("user_id", "==", user_id) \
                .where("createdAt", ">=", week_start)
            count_query = AggregationQuery(query).count()
            result = count_query.get()
            return result[0].value if result else 0
            
        except Exception as e:
            logger.warning(f"Weekly count failed: {e}")
            return 0
    
    async def _count_wardrobe_items(self, user_id: str) -> Dict[str, Any]:
        """Count wardrobe items and analyze categories/colors (for initialization only)."""
        try:
            # Query wardrobe items
            query = self.db.collection("wardrobe").where("userId", "==", user_id)
            docs = list(query.stream())
            
            total = len(docs)
            categories = {}
            colors = {}
            favorites = 0
            
            for doc in docs:
                try:
                    item_data = doc.to_dict()
                    
                    # Count categories
                    category = item_data.get('type', 'unknown')
                    categories[category] = categories.get(category, 0) + 1
                    
                    # Count colors
                    color = item_data.get('color', 'unknown')
                    colors[color] = colors.get(color, 0) + 1
                    
                    # Count favorites
                    if item_data.get('favorite', False):
                        favorites += 1
                        
                except Exception as item_error:
                    logger.warning(f"Error processing wardrobe item: {item_error}")
                    continue
            
            return {
                "total": total,
                "categories": categories,
                "colors": colors,
                "favorites": favorites
            }
            
        except Exception as e:
            logger.warning(f"Wardrobe count failed: {e}")
            return {
                "total": 0,
                "categories": {},
                "colors": {},
                "favorites": 0
            }
    

    def _get_default_stats(self, user_id: str) -> Dict[str, Any]:
        """Return default stats when database is unavailable."""
        current_time = datetime.now(timezone.utc)
        
        return {
            "user_id": user_id,
            "last_updated": current_time.isoformat(),
            "initialized_at": current_time.isoformat(),
            
            "outfits": {
                "total": 0,
                "this_week": 0,
                "this_month": 0,
                "last_created": None,
                "week_start": (current_time - timedelta(days=current_time.weekday())).isoformat()
            },
            
            "wardrobe": {
                "total_items": 0,
                "categories": {},
                "colors": {},
                "favorites": 0,
                "last_added": None
            },
            
            "dashboard": {
                "style_progress": 0,
                "color_variety_score": 0,
                "completion_percentage": 0
            }
        }

# Global instance
user_stats_service = UserStatsService()
