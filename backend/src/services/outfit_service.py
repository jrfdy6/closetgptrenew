"""
Main Outfit Service
Orchestrates all modular outfit services with proper temperature handling.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from firebase_admin import firestore

# Import the established pattern components
from ..core.exceptions import ValidationError, DatabaseError
from ..custom_types.outfit import OutfitCreate, OutfitUpdate, OutfitFilters, Outfit
from ..config.firebase import db

logger = logging.getLogger(__name__)

class OutfitService:
    """
    Outfit service following the established wardrobe service architecture pattern.
    
    This service contains business logic and external API calls,
    following the same separation of concerns as the wardrobe service.
    """
    
    def __init__(self):
        """Initialize the outfit service with database connection."""
        try:
            self.db = db
            self.collection = self.db.collection('outfits')
            logger.info("✅ OutfitService initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OutfitService: {e}")
            raise DatabaseError("Failed to initialize outfit service")
    
    # ===== CORE BUSINESS LOGIC METHODS =====
    
    async def get_user_outfits(self, user_id: str, filters: OutfitFilters) -> List[Outfit]:
        """
        Get user's outfits with filtering and pagination.
        Business logic: Apply filters, validate user access, transform data.
        """
        try:
            logger.info(f"🔍 Getting outfits for user {user_id} with filters: {filters}")
            
            # Validate user ID
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Build query with business logic
            query = self.collection.where('user_id', '==', user_id)
            
            # Apply business logic filters
            if filters.occasion:
                query = query.where('occasion', '==', filters.occasion)
            
            if filters.style:
                query = query.where('style', '==', filters.style)
            
            if filters.mood:
                query = query.where('mood', '==', filters.mood)
            
            # Apply pagination
            if filters.offset and filters.offset > 0:
                query = query.offset(filters.offset)
            
            if filters.limit:
                query = query.limit(filters.limit)
            
            # Execute query
            docs = query.stream()
            
            # Transform to business objects
            outfits = []
            for doc in docs:
                try:
                    outfit_data = doc.to_dict()
                    outfit_data['id'] = doc.id
                    outfit = Outfit(**outfit_data)
                    outfits.append(outfit)
                except Exception as e:
                    logger.warning(f"⚠️ Skipping invalid outfit document {doc.id}: {e}")
                    continue
            
            logger.info(f"✅ Retrieved {len(outfits)} outfits for user {user_id}")
            return outfits
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get user outfits: {e}")
            raise DatabaseError(f"Failed to retrieve outfits: {str(e)}")
    
    async def get_outfit_by_id(self, user_id: str, outfit_id: str) -> Optional[Outfit]:
        """
        Get a specific outfit by ID.
        Business logic: Validate ownership, ensure user isolation.
        """
        try:
            logger.info(f"🔍 Getting outfit {outfit_id} for user {user_id}")
            
            # Validate inputs
            if not outfit_id or not outfit_id.strip():
                raise ValidationError("Invalid outfit ID")
            
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get outfit document
            doc_ref = self.collection.document(outfit_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"⚠️ Outfit {outfit_id} not found")
                return None
            
            outfit_data = doc.to_dict()
            
            # Business logic: Ensure user isolation
            if outfit_data.get('user_id') != user_id:
                logger.warning(f"🚫 User {user_id} attempted to access outfit {outfit_id} owned by {outfit_data.get('user_id')}")
                raise ValidationError("Access denied: Outfit does not belong to user")
            
            # Transform to business object
            outfit_data['id'] = doc.id
            outfit = Outfit(**outfit_data)
            
            logger.info(f"✅ Successfully retrieved outfit {outfit_id}")
            return outfit
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get outfit {outfit_id}: {e}")
            raise DatabaseError(f"Failed to retrieve outfit: {str(e)}")
    
    async def create_outfit(self, user_id: str, outfit_data: OutfitCreate) -> Outfit:
        """
        Create a new outfit.
        Business logic: Validate data, ensure user ownership, apply business rules.
        """
        try:
            logger.info(f"🎨 Creating outfit for user {user_id}")
            
            # Validate user ID
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Business logic: Validate outfit data
            if not outfit_data.name or not outfit_data.name.strip():
                raise ValidationError("Outfit name is required")
            
            if not outfit_data.occasion or not outfit_data.occasion.strip():
                raise ValidationError("Outfit occasion is required")
            
            if not outfit_data.style or not outfit_data.style.strip():
                raise ValidationError("Outfit style is required")
            
            # Business logic: Apply default values and business rules
            outfit_dict = outfit_data.dict()
            outfit_dict.update({
                'user_id': user_id,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
                'wearCount': 0,
                'isFavorite': False,
                'lastWorn': None
            })
            
            # Create document in database
            doc_ref = self.collection.add(outfit_dict)
            outfit_id = doc_ref[1].id
            
            # Get the created outfit
            created_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            
            logger.info(f"✅ Successfully created outfit {outfit_id}")
            return created_outfit
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to create outfit: {e}")
            raise DatabaseError(f"Failed to create outfit: {str(e)}")
    
    async def update_outfit(self, user_id: str, outfit_id: str, outfit_data: OutfitUpdate) -> Outfit:
        """
        Update an existing outfit.
        Business logic: Validate ownership, apply business rules, maintain data integrity.
        """
        try:
            logger.info(f"🔄 Updating outfit {outfit_id} for user {user_id}")
            
            # Validate inputs
            if not outfit_id or not outfit_id.strip():
                raise ValidationError("Invalid outfit ID")
            
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get existing outfit to validate ownership
            existing_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            if not existing_outfit:
                raise ValidationError(f"Outfit {outfit_id} not found")
            
            # Business logic: Prepare update data
            update_data = outfit_data.dict(exclude_unset=True)
            update_data['updatedAt'] = datetime.now()
            
            # Update document in database
            doc_ref = self.collection.document(outfit_id)
            doc_ref.update(update_data)
            
            # Get the updated outfit
            updated_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            
            logger.info(f"✅ Successfully updated outfit {outfit_id}")
            return updated_outfit
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to update outfit {outfit_id}: {e}")
            raise DatabaseError(f"Failed to update outfit: {str(e)}")
    
    async def delete_outfit(self, user_id: str, outfit_id: str) -> None:
        """
        Delete an outfit.
        Business logic: Validate ownership, ensure data consistency.
        """
        try:
            logger.info(f"🗑️ Deleting outfit {outfit_id} for user {user_id}")
            
            # Validate inputs
            if not outfit_id or not outfit_id.strip():
                raise ValidationError("Invalid outfit ID")
            
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get existing outfit to validate ownership
            existing_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            if not existing_outfit:
                raise ValidationError(f"Outfit {outfit_id} not found")
            
            # Delete document from database
            doc_ref = self.collection.document(outfit_id)
            doc_ref.delete()
            
            logger.info(f"✅ Successfully deleted outfit {outfit_id}")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to delete outfit {outfit_id}: {e}")
            raise DatabaseError(f"Failed to delete outfit: {str(e)}")
    
    async def mark_outfit_as_worn(self, user_id: str, outfit_id: str) -> None:
        """
        Mark an outfit as worn.
        Business logic: Validate ownership, increment wear count, update last worn date.
        """
        try:
            logger.info(f"👕 Marking outfit {outfit_id} as worn for user {user_id}")
            
            # Validate inputs
            if not outfit_id or not outfit_id.strip():
                raise ValidationError("Invalid outfit ID")
            
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get existing outfit to validate ownership
            existing_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            if not existing_outfit:
                raise ValidationError(f"Outfit {outfit_id} not found")
            
            # Business logic: Update wear statistics
            update_data = {
                'wearCount': (existing_outfit.wearCount or 0) + 1,
                'lastWorn': datetime.now(),
                'updatedAt': datetime.now()
            }
            
            # Update document in database
            doc_ref = self.collection.document(outfit_id)
            doc_ref.update(update_data)
            
            logger.info(f"✅ Successfully marked outfit {outfit_id} as worn")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to mark outfit {outfit_id} as worn: {e}")
            raise DatabaseError(f"Failed to mark outfit as worn: {str(e)}")
    
    async def toggle_outfit_favorite(self, user_id: str, outfit_id: str) -> None:
        """
        Toggle outfit favorite status.
        Business logic: Validate ownership, toggle boolean value.
        """
        try:
            logger.info(f"❤️ Toggling favorite for outfit {outfit_id} for user {user_id}")
            
            # Validate inputs
            if not outfit_id or not outfit_id.strip():
                raise ValidationError("Invalid outfit ID")
            
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get existing outfit to validate ownership
            existing_outfit = await self.get_outfit_by_id(user_id, outfit_id)
            if not existing_outfit:
                raise ValidationError(f"Outfit {outfit_id} not found")
            
            # Business logic: Toggle favorite status
            new_favorite_status = not (existing_outfit.isFavorite or False)
            
            # Update document in database
            doc_ref = self.collection.document(outfit_id)
            doc_ref.update({
                'isFavorite': new_favorite_status,
                'updatedAt': datetime.now()
            })
            
            logger.info(f"✅ Successfully {'favorited' if new_favorite_status else 'unfavorited'} outfit {outfit_id}")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to toggle favorite for outfit {outfit_id}: {e}")
            raise DatabaseError(f"Failed to toggle outfit favorite: {str(e)}")
    
    async def get_outfit_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get outfit statistics for user.
        Business logic: Aggregate data, calculate metrics, provide insights.
        """
        try:
            logger.info(f"📊 Getting outfit stats for user {user_id}")
            
            # Validate user ID
            if not user_id or not user_id.strip():
                raise ValidationError("Invalid user ID")
            
            # Get all user outfits for statistics
            all_outfits = await self.get_user_outfits(user_id, OutfitFilters(limit=1000))
            
            # Business logic: Calculate statistics
            stats = {
                'totalOutfits': len(all_outfits),
                'favoriteOutfits': len([o for o in all_outfits if o.isFavorite]),
                'totalWearCount': sum(o.wearCount or 0 for o in all_outfits),
                'occasions': {},
                'styles': {},
                'recentActivity': None
            }
            
            # Count occasions and styles
            for outfit in all_outfits:
                # Count occasions
                occasion = outfit.occasion or 'Unknown'
                stats['occasions'][occasion] = stats['occasions'].get(occasion, 0) + 1
                
                # Count styles
                style = outfit.style or 'Unknown'
                stats['styles'][style] = stats['styles'].get(style, 0) + 1
            
            # Business logic: Calculate recent activity
            if all_outfits:
                recent_outfits = sorted(all_outfits, key=lambda x: x.updatedAt or x.createdAt, reverse=True)[:5]
                stats['recentActivity'] = [
                    {
                        'id': o.id,
                        'name': o.name,
                        'lastUpdated': o.updatedAt or o.createdAt
                    }
                    for o in recent_outfits
                ]
            
            logger.info(f"✅ Successfully calculated outfit stats for user {user_id}")
            return stats
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get outfit stats: {e}")
            raise DatabaseError(f"Failed to retrieve outfit statistics: {str(e)}")
    
    # ===== UTILITY METHODS =====
    
    async def search_outfits(self, user_id: str, query: str, filters: OutfitFilters) -> List[Outfit]:
        """
        Search outfits with text query and filters.
        Business logic: Text search, relevance scoring, result ranking.
        """
        try:
            logger.info(f"🔍 Searching outfits for user {user_id} with query: {query}")
            
            # Get all user outfits first (for text search)
            all_outfits = await self.get_user_outfits(user_id, filters)
            
            if not query or not query.strip():
                return all_outfits
            
            # Business logic: Simple text search implementation
            query_lower = query.lower()
            search_results = []
            
            for outfit in all_outfits:
                # Search in name, occasion, style, and mood
                searchable_text = f"{outfit.name} {outfit.occasion} {outfit.style} {outfit.mood or ''}".lower()
                
                if query_lower in searchable_text:
                    search_results.append(outfit)
            
            # Business logic: Sort by relevance (simple implementation)
            search_results.sort(key=lambda x: (
                query_lower in x.name.lower(),  # Name matches first
                query_lower in x.occasion.lower(),  # Then occasion
                query_lower in x.style.lower(),  # Then style
                x.updatedAt or x.createdAt  # Then by recency
            ), reverse=True)
            
            logger.info(f"✅ Search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Failed to search outfits: {e}")
            raise DatabaseError(f"Failed to search outfits: {str(e)}")

# ===== SERVICE INSTANCE =====
outfit_service = OutfitService()


