"""
Working authentication routes for Easy Outfit App.
Follows the exact pattern used by working wardrobe.py and outfits.py
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import time
# Firebase imports moved inside functions to prevent import-time crashes
# from firebase_admin import auth
# from firebase_admin import firestore
# from ..config.firebase import db, firebase_initialized
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

# HTTP Bearer scheme for token extraction
security = HTTPBearer()

logger = logging.getLogger("auth_working")

router = APIRouter(tags=["authentication"])

@router.get("/profile/health")
async def profile_health():
    """Health check for profile route - no authentication required."""
    logger.info("🔍 PROFILE: Health check called")
    try:
        from ..config.firebase import firebase_initialized, db
        return {
            "status": "ok",
            "firebase_initialized": firebase_initialized,
            "db_available": db is not None
        }
    except Exception as e:
        logger.error(f"🔍 PROFILE: Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/profile")
async def get_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user's profile."""
    import asyncio
    import time
    
    try:
        profile_start = time.time()
        logger.info(f"🔍 PROFILE: Route handler called for user: {current_user.id if current_user else 'None'}")
        
        # Verify we have a valid user object
        if not current_user:
            logger.error("🔍 PROFILE: current_user is None - authentication dependency failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed - user not found"
            )
        
        if not hasattr(current_user, 'id') or not current_user.id:
            logger.error("🔍 PROFILE: current_user missing id attribute")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed - invalid user data"
            )
        
        logger.info(f"🔍 PROFILE: Getting profile for user: {current_user.id}")
        
        # Always return at least basic profile from token (fast path)
        basic_profile = {
            "user_id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "avatar_url": None,
            "created_at": current_user.createdAt,
            "updated_at": current_user.updatedAt
        }
        
        # Try to get enhanced profile from Firestore with timeout
        try:
            from ..config.firebase import db, firebase_initialized
            
            if not firebase_initialized:
                logger.warning("🔍 PROFILE: Firebase not initialized, returning basic profile")
                return basic_profile
            
            # Use asyncio timeout to prevent hanging
            try:
                firestore_start = time.time()
                
                # Firestore get() is synchronous, but we'll wrap it
                logger.info(f"⏱️ PROFILE: Starting Firestore query for user: {current_user.id}")
                user_doc = db.collection('users').document(current_user.id).get()
                
                logger.info(f"⏱️ PROFILE: Firestore get() completed ({time.time() - firestore_start:.2f}s)")
                
                if not user_doc.exists:
                    logger.info(f"🔍 PROFILE: No Firestore profile found for user: {current_user.id}")
                    return basic_profile
                
                user_data = user_doc.to_dict()
                if user_data:
                    logger.info(f"🔍 PROFILE: Retrieved Firestore profile for user: {current_user.id}, fields: {len(user_data.keys())}")
                    
                    # OPTIMIZED: Exclude large fields that aren't needed for profile
                    # These fields can be very large and slow down response
                    excluded_fields = ['metadata', 'analysis', 'wardrobe_items', 'outfits', 'preferences_cache']
                    filtered_user_data = {k: v for k, v in user_data.items() if k not in excluded_fields}
                    
                    # Merge Firestore data with basic profile (Firestore takes precedence)
                    merged_profile = {**basic_profile, **filtered_user_data}
                    logger.info(f"⏱️ PROFILE: Profile prepared (total: {time.time() - profile_start:.2f}s)")
                    return merged_profile
                else:
                    logger.warning(f"🔍 PROFILE: Firestore profile exists but is empty for user: {current_user.id}")
                    return basic_profile
                    
            except Exception as firestore_error:
                logger.error(f"🔍 PROFILE: Firestore query failed: {firestore_error}", exc_info=True)
                # Return basic profile as fallback
                return basic_profile
                
        except ImportError as e:
            logger.warning(f"🔍 PROFILE: Firebase import failed: {e}, returning basic profile")
            return basic_profile
        except Exception as firebase_error:
            logger.error(f"🔍 PROFILE: Firebase error: {firebase_error}", exc_info=True)
            # Return basic profile as fallback
            return basic_profile
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 401, 503)
        raise
    except Exception as e:
        logger.error(f"🔍 PROFILE: Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
        # Even on unexpected errors, try to return basic profile if we have user data
        try:
            return {
                "user_id": current_user.id if hasattr(current_user, 'id') else "unknown",
                "email": current_user.email if hasattr(current_user, 'email') else None,
                "name": current_user.name if hasattr(current_user, 'name') else None,
                "avatar_url": None,
                "created_at": current_user.createdAt if hasattr(current_user, 'createdAt') else None,
                "updated_at": current_user.updatedAt if hasattr(current_user, 'updatedAt') else None,
                "error": "Partial profile data due to error"
            }
        except:
            # Last resort - return error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user profile: {str(e)}"
            )

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    background_tasks: BackgroundTasks,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update current user's profile."""
    try:
        logger.info(f"🔍 DEBUG: Updating profile for user: {current_user.id}")
        logger.info(f"🔍 DEBUG: Profile data received: fields_count={len(profile_data.keys()) if profile_data else 0}, user_id={current_user.id}")
        
        # Import Firebase inside function to prevent import-time crashes
        from ..config.firebase import db, firebase_initialized
        
        # Check if Firebase is available
        if not firebase_initialized:
            logger.warning("Firebase not available, cannot update profile")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase service not available"
            )
        
        user_ref = db.collection('users').document(current_user.id)
        
        # Prepare update data with all profile fields
        frontend_updated_at = ((profile_data.get('updated_at') if profile_data else None) if profile_data else None) or profile_data.get('updatedAt')
        current_time = int(time.time())
        final_updated_at = frontend_updated_at or current_time
        
        # Also check for createdAt/created_at
        frontend_created_at = ((profile_data.get('created_at') if profile_data else None) if profile_data else None) or profile_data.get('createdAt')
        final_created_at = frontend_created_at or current_time
        
        logger.info(f"🔍 DEBUG: Timestamp handling - frontend_updated_at: {frontend_updated_at}, current_time: {current_time}, final_updated_at: {final_updated_at}")
        logger.info(f"🔍 DEBUG: Profile data keys: {list(profile_data.keys())}")
        logger.info(f"🔍 DEBUG: measurements in profile_data: {'measurements' in profile_data}, value: {profile_data.get('measurements')}")
        logger.info(f"🔍 DEBUG: stylePreferences in profile_data: {'stylePreferences' in profile_data}, value: {profile_data.get('stylePreferences')}")
        
        # Get existing user data to preserve created_at
        existing_user_doc = user_ref.get()
        existing_created_at = None
        existing_spending_ranges = None
        if existing_user_doc.exists:
            existing_data = existing_user_doc.to_dict()
            existing_created_at = existing_data.get('created_at') or existing_data.get('createdAt')
            existing_spending_ranges = existing_data.get('spending_ranges')
        
        update_data = {
            'name': (profile_data.get('name') if profile_data else None),
            'email': (profile_data.get('email') if profile_data else None),
            # NEVER overwrite created_at if it already exists
            'created_at': existing_created_at or final_created_at,
            'updated_at': final_updated_at  # Always update this
        }
        
        # Add all the detailed profile fields if they exist
        if 'gender' in profile_data:
            update_data['gender'] = profile_data['gender']
        if 'measurements' in profile_data:
            update_data['measurements'] = profile_data['measurements']
            logger.info(f"✅ DEBUG: Added measurements to update_data")
        if 'stylePreferences' in profile_data:
            update_data['stylePreferences'] = profile_data['stylePreferences']
            logger.info(f"✅ DEBUG: Added stylePreferences to update_data: {profile_data['stylePreferences']}")
        if 'preferences' in profile_data:
            update_data['preferences'] = profile_data['preferences']
        if 'bodyType' in profile_data:
            update_data['bodyType'] = profile_data['bodyType']
        if 'skinTone' in profile_data:
            update_data['skinTone'] = profile_data['skinTone']
        if 'fitPreference' in profile_data:
            update_data['fitPreference'] = profile_data['fitPreference']
        if 'sizePreference' in profile_data:
            update_data['sizePreference'] = profile_data['sizePreference']
        if 'colorPalette' in profile_data:
            update_data['colorPalette'] = profile_data['colorPalette']
        if 'stylePersonality' in profile_data:
            update_data['stylePersonality'] = profile_data['stylePersonality']
        if 'materialPreferences' in profile_data:
            update_data['materialPreferences'] = profile_data['materialPreferences']
        if 'fitPreferences' in profile_data:
            update_data['fitPreferences'] = profile_data['fitPreferences']
        if 'comfortLevel' in profile_data:
            update_data['comfortLevel'] = profile_data['comfortLevel']
        if 'preferredBrands' in profile_data:
            update_data['preferredBrands'] = profile_data['preferredBrands']
        if 'budget' in profile_data:
            update_data['budget'] = profile_data['budget']
        if 'avatar_url' in profile_data:
            update_data['avatar_url'] = profile_data['avatar_url']
        if 'stylePersona' in profile_data:
            update_data['stylePersona'] = profile_data['stylePersona']
        spending_ranges_changed = False
        if 'spending_ranges' in profile_data:
            update_data['spending_ranges'] = profile_data['spending_ranges']
            logger.info(f"✅ DEBUG: Added spending_ranges to update_data: {profile_data['spending_ranges']}")
            spending_ranges_changed = (profile_data.get('spending_ranges') != existing_spending_ranges)
        if 'height' in profile_data:
            update_data['height'] = profile_data['height']
        if 'weight' in profile_data:
            update_data['weight'] = profile_data['weight']
        if 'heightFeetInches' in profile_data:
            update_data['heightFeetInches'] = profile_data['heightFeetInches']
        
        # Use set() instead of update() to create the document if it doesn't exist
        user_ref.set(update_data, merge=True)
        
        logger.info(f"✅ User profile updated successfully: {current_user.id}")
        logger.info(f"🔍 DEBUG: Updated profile data: user_id={current_user.id}, fields_updated={len(update_data.keys()) if update_data else 0}")
        logger.info(f"🔍 DEBUG: Fields in update_data: {list(update_data.keys())}")
        logger.info(f"🔍 DEBUG: Has measurements: {'measurements' in update_data}, Has stylePreferences: {'stylePreferences' in update_data}")
        
        # If spending ranges changed, mark TVE recalculation as queued.
        # IMPORTANT: Do NOT run the recalculation in-process here (even in BackgroundTasks).
        # Running it alongside user requests can still saturate the server and cause onboarding
        # requests (including quiz submit / wardrobeCount) to time out.
        if spending_ranges_changed:
            try:
                user_ref.set(
                    {
                        "tveRecalcStatus": "queued",
                        "tveRecalcRequestedAt": int(time.time()),
                    },
                    merge=True,
                )
                logger.info(f"💰 Spending ranges changed - marked TVE recalculation queued for user {current_user.id}")
            except Exception as queue_error:
                logger.warning(f"⚠️ Failed to queue TVE recalculation: {queue_error}")
                # Don't fail the profile update if background queueing fails
        
        # Fetch the updated profile to get wardrobeItemCount
        updated_doc = user_ref.get()
        wardrobe_count = 0
        if updated_doc.exists:
            updated_data = updated_doc.to_dict()
            wardrobe_count = updated_data.get('wardrobeItemCount', 0)
        
        logger.info(f"📦 Returning wardrobeItemCount: {wardrobe_count} for user {current_user.id}")
        
        # Return the updated profile data with wardrobe count
        return {
            **update_data,
            'wardrobeCount': wardrobe_count,
            'wardrobe_count': wardrobe_count  # Support both naming conventions
        }
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


async def recalculate_tve_for_user(user_id: str) -> None:
    """
    Background TVE recalculation when spending ranges change.
    Runs after the response is returned so onboarding stays fast.
    """
    try:
        from ..config.firebase import db
        from ..services.tve_service import tve_service

        user_ref = db.collection("users").document(user_id)
        user_ref.set(
            {
                "tveRecalcStatus": "running",
                "tveRecalcStartedAt": int(time.time()),
            },
            merge=True,
        )

        wardrobe_ref = db.collection("wardrobe").where("userId", "==", user_id)
        items = list(wardrobe_ref.stream())

        recalculated_count = 0
        for doc in items:
            try:
                success = await tve_service.initialize_item_tve_fields(user_id, doc.id)
                if success:
                    recalculated_count += 1
            except Exception:
                # Keep going; one bad item shouldn't kill the batch
                continue

        user_ref.set(
            {
                "tveRecalcStatus": "completed",
                "tveRecalcCompletedAt": int(time.time()),
                "tveRecalcUpdatedCount": recalculated_count,
            },
            merge=True,
        )
    except Exception as e:
        try:
            from ..config.firebase import db

            db.collection("users").document(user_id).set(
                {
                    "tveRecalcStatus": "error",
                    "tveRecalcCompletedAt": int(time.time()),
                    "tveRecalcError": str(e)[:500],
                },
                merge=True,
            )
        except Exception:
            pass
