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
                    
                    # Fix timestamp issues before creating Outfit object
                    if 'createdAt' in outfit_data:
                        created_at = outfit_data['createdAt']
                        if isinstance(created_at, (int, float)):
                            # Handle both seconds and milliseconds timestamps
                            if created_at > 1e12:  # Likely milliseconds
                                timestamp_seconds = created_at / 1000.0
                            else:
                                timestamp_seconds = created_at
                            # Sanity check: Unix timestamps should be roughly between 2000-2100
                            if 946684800 <= timestamp_seconds <= 4102444800:
                                outfit_data['createdAt'] = datetime.fromtimestamp(timestamp_seconds)
                            else:
                                logger.warning(f"⚠️ Invalid createdAt timestamp for outfit {doc.id}: {created_at}")
                                outfit_data['createdAt'] = datetime.utcnow()
                        elif hasattr(created_at, 'timestamp'):
                            # Firestore timestamp object
                            outfit_data['createdAt'] = created_at
                        elif isinstance(created_at, str):
                            # Already a string, leave as is
                            pass
                        else:
                            logger.warning(f"⚠️ Unknown createdAt type for outfit {doc.id}: {type(created_at)}")
                            outfit_data['createdAt'] = datetime.utcnow()
                    
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
    
    async def create_custom_outfit(self, outfit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom outfit (alias for create_outfit with data transformation).
        This method adapts the route's payload to work with the existing create_outfit method.
        """
        try:
            logger.info(f"🎨 Creating custom outfit")
            
            # Extract user_id from the user_profile if present
            user_profile = outfit_data.get('user_profile', {})
            user_id = user_profile.get('id')
            if not user_id:
                raise ValueError("User ID is required for creating custom outfits")
            
            # Create OutfitCreate object from the payload
            from ..custom_types.outfit import OutfitCreate, OutfitItem
            
            # Transform items if needed
            items = outfit_data.get('items', [])
            outfit_items = []
            for item in items:
                if isinstance(item, dict):
                    # Provide all required fields for OutfitItem
                    outfit_item = OutfitItem(
                        id=item.get('id', ''),
                        name=item.get('name', ''),
                        userId=user_id,  # Required field
                        subType=item.get('subType') or item.get('category') or item.get('type', 'item'),  # Required field
                        type=item.get('type', 'item'),
                        color=item.get('color', ''),
                        imageUrl=item.get('imageUrl') or item.get('image_url') or item.get('image', ''),
                        style=item.get('style', []) if isinstance(item.get('style'), list) else [item.get('style', 'casual')],  # Required List[str]
                        occasion=item.get('occasion', []) if isinstance(item.get('occasion'), list) else [item.get('occasion', 'casual')],  # Required List[str]
                        brand=item.get('brand', ''),
                        wearCount=item.get('wearCount', 0),
                        favorite_score=item.get('favorite_score', 0.0)
                    )
                    outfit_items.append(outfit_item)
            
            # Create the outfit data object
            outfit_create = OutfitCreate(
                name=outfit_data.get('name', 'Custom Outfit'),
                occasion=outfit_data.get('occasion', 'Casual'),
                style=outfit_data.get('style', 'Casual'),
                mood=outfit_data.get('mood'),
                items=outfit_items,
                confidenceScore=outfit_data.get('confidenceScore'),
                reasoning=outfit_data.get('description') or outfit_data.get('reasoning')
            )
            
            # Call the existing create_outfit method
            created_outfit = await self.create_outfit(user_id, outfit_create)
            
            # Return the result in the expected format
            return {
                'id': created_outfit.id,
                'name': created_outfit.name,
                'occasion': created_outfit.occasion,
                'style': created_outfit.style,
                'mood': created_outfit.mood,
                'items': created_outfit.items,
                'createdAt': created_outfit.createdAt.isoformat() if hasattr(created_outfit.createdAt, 'isoformat') else str(created_outfit.createdAt),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create custom outfit: {e}")
            raise DatabaseError(f"Failed to create custom outfit: {str(e)}")
    
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
            
            # NEW: Update individual wardrobe item wear counters
            await self._update_wardrobe_item_wear_counters(existing_outfit.items, user_id)
            
            logger.info(f"✅ Successfully marked outfit {outfit_id} as worn and updated wardrobe item counters")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to mark outfit {outfit_id} as worn: {e}")
            raise DatabaseError(f"Failed to mark outfit as worn: {str(e)}")
    
    async def _update_wardrobe_item_wear_counters(self, outfit_items: List[Dict], user_id: str) -> None:
        """
        Update wear counters for individual wardrobe items when an outfit is worn.
        This ensures the scoring system has accurate wear data for each item.
        """
        try:
            logger.info(f"👕 Updating wear counters for {len(outfit_items)} wardrobe items")
            
            # Get Firestore client
            from firebase_admin import firestore
            db = firestore.client()
            
            current_time = datetime.now()
            updated_count = 0
            
            for item in outfit_items:
                item_id = item.get('id')
                if not item_id:
                    logger.warning(f"⚠️ Skipping item without ID: {item}")
                    continue
                
                try:
                    # Get the wardrobe item document
                    wardrobe_ref = db.collection('wardrobe').document(item_id)
                    wardrobe_doc = wardrobe_ref.get()
                    
                    if not wardrobe_doc.exists:
                        logger.warning(f"⚠️ Wardrobe item {item_id} not found, skipping wear counter update")
                        continue
                    
                    # Verify the item belongs to the user
                    wardrobe_data = wardrobe_doc.to_dict()
                    if wardrobe_data.get('userId') != user_id:
                        logger.warning(f"⚠️ Wardrobe item {item_id} does not belong to user {user_id}, skipping")
                        continue
                    
                    # Update wear counter and last worn date
                    current_wear_count = wardrobe_data.get('wearCount', 0)
                    new_wear_count = current_wear_count + 1
                    
                    wardrobe_ref.update({
                        'wearCount': new_wear_count,
                        'lastWorn': current_time,
                        'updatedAt': current_time
                    })
                    
                    updated_count += 1
                    logger.info(f"✅ Updated wear counter for item {item_id}: {current_wear_count} → {new_wear_count}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to update wear counter for item {item_id}: {e}")
                    # Continue with other items even if one fails
                    continue
            
            logger.info(f"✅ Successfully updated wear counters for {updated_count}/{len(outfit_items)} wardrobe items")
            
        except Exception as e:
            logger.error(f"❌ Failed to update wardrobe item wear counters: {e}")
            # Don't raise the error - this is a secondary operation
            # The main outfit wear tracking should still succeed
    
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


