"""
Main outfit generation service that orchestrates the generation process.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from src.routes.outfits.models import OutfitRequest, OutfitResponse
from src.routes.outfits.utils import log_generation_strategy, clean_for_firestore
from src.routes.outfits.validation import validate_style_gender_compatibility
from src.routes.outfits.generation import ensure_base_item_included

logger = logging.getLogger(__name__)


class OutfitGenerationService:
    """Main service for outfit generation that orchestrates the entire process."""
    
    def __init__(self):
        self.logger = logger
    
    async def generate_outfit_logic(self, req: OutfitRequest, user_id: str) -> Dict[str, Any]:
        """
        Main outfit generation logic using user's wardrobe and AI recommendations.
        This is the core function extracted from the original outfits.py file.
        """
        print(f"🔎 MAIN LOGIC ENTRY: Starting generation for user {user_id}")
        print(f"🔎 MAIN LOGIC ENTRY: Request - style: {req.style}, mood: {req.mood}, occasion: {req.occasion}")
        
        # DEBUG: Log detailed request information
        print(f"🔍 DEBUG INPUT: req.resolved_wardrobe = {req.resolved_wardrobe}")
        
        if req.wardrobe:
            for i, item in enumerate(req.wardrobe[:3]):  # Log first 3 items
                print(f"🔍 DEBUG INPUT ITEM {i+1}: {getattr(item, 'id', 'NO_ID')} - {getattr(item, 'name', 'NO_NAME')} - {getattr(item, 'type', 'NO_TYPE')}")

        print(f"🔍 DEBUG INPUT: Weather data: {req.weather}")
        print(f"🔍 DEBUG INPUT: Base item ID: {req.baseItemId}")
        
        # Initialize debug info variable at function level
        robust_debug_info = None
        
        # Import Firebase inside function to prevent import-time crashes
        try:
            from src.config.firebase import db, firebase_initialized
            from src.auth.auth_service import get_current_user
            from src.custom_types.profile import UserProfile
            from src.custom_types.outfit import OutfitGeneratedOutfit
            FIREBASE_AVAILABLE = True
            print(f"🔎 MAIN LOGIC: Firebase imports successful")
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            print(f"🚨 MAIN LOGIC: Firebase import FAILED: {e}")
            FIREBASE_AVAILABLE = False
            db = None
            firebase_initialized = False
            get_current_user = None
            UserProfile = None
            OutfitGeneratedOutfit = None
        
        # Import robust generation service
        try:
            from src.services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
            print(f"✅ MAIN LOGIC: Robust generation service imported successfully")
            logger.info(f"✅ ROBUST IMPORT: Robust generation service imported successfully")
        except ImportError as e:
            logger.error(f"🚨 FORCE REDEPLOY v12.0: Robust service import failed: {e}")
            print(f"🚨 MAIN LOGIC: Robust service import FAILED: {e}")
            raise Exception(f"Robust service import failed: {e}")
        
        # Import ClothingItem for validation
        try:
            from src.custom_types.wardrobe import ClothingItem
            print(f"🔎 MAIN LOGIC: ClothingItem import successful")
        except ImportError as e:
            logger.error(f"🚨 FORCE REDEPLOY v12.0: ClothingItem import failed: {e}")
            print(f"🚨 MAIN LOGIC: ClothingItem import FAILED: {e}")
            ClothingItem = None
        
        # Get user profile for style-gender compatibility
        user_profile = None
        if FIREBASE_AVAILABLE and db:
            try:
                user_doc = db.collection('users').document(user_id).get()
                if user_doc.exists:
                    user_profile = user_doc.to_dict()
                    logger.info(f"✅ User profile loaded for {user_id}")
                else:
                    logger.warning(f"⚠️ No user profile found for {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load user profile: {e}")
        
        # Validate style-gender compatibility
        if user_profile and user_profile.get('gender'):
            style_validation = await validate_style_gender_compatibility(req.style, user_profile['gender'])
            if not style_validation.get('is_compatible'):
                logger.warning(f"⚠️ Style-gender compatibility issue: {style_validation.get('warning')}")
                # For now, we'll continue but log the warning
                # In the future, we could suggest alternatives or reject the request
        
        # Process wardrobe items
        wardrobe_items = req.resolved_wardrobe
        
        # Create generation context
        try:
            # Initialize clothing_items list
            clothing_items = []
            
            if ClothingItem is None:
                logger.warning(f"⚠️ ClothingItem not available, skipping validation")
                clothing_items = wardrobe_items  # Use raw items if ClothingItem not available
            else:
                for i, item_dict in enumerate(wardrobe_items):
                    print(f"🔍 DEBUG ITEM CONVERSION: Processing item {i}: {item_dict}")
                    try:
                        clothing_item = ClothingItem(**item_dict)
                        clothing_items.append(clothing_item)
                        print(f"🔍 DEBUG ITEM CONVERSION: Successfully converted item {i}")
                    except Exception as item_error:
                        logger.warning(f"⚠️ Failed to convert item {i}: {item_error}")
                        print(f"🚨 ITEM CONVERSION ERROR: {item_error}")
                        continue
            
            logger.info(f"✅ Pre-outfit-construction guard completed - {len(clothing_items)} items converted successfully")
        
        except Exception as e:
            logger.error(f"❌ Error during wardrobe processing: {e}")
            raise
        
        # DEBUG: Check clothing_items for None values
        for i, item in enumerate(clothing_items):
            print(f"🔍 DEBUG CONTEXT CREATION: item {i} = {item}")
            if item is None:
                print(f"🚨 CRITICAL: clothing_items[{i}] is None!")
        
        # Create generation context
        try:
            weather_data = req.weather
            if isinstance(weather_data, dict):
                # Convert dict to object-like structure for robust service
                from types import SimpleNamespace
                weather_data = SimpleNamespace(**weather_data)
                logger.info(f"🔧 CONVERTED WEATHER: dict -> object for robust service")
            
            context = GenerationContext(
                user_id=user_id,
                occasion=req.occasion,
                style=req.style,
                mood=req.mood,
                weather=weather_data,
                wardrobe=clothing_items,  # Use converted ClothingItem objects
                base_item_id=req.baseItemId,
                user_profile=user_profile
            )
            
            logger.info(f"[GENERATION][ROBUST] START for user {user_id}, wardrobe size={len(wardrobe_items)}")
            logger.info(f"[GENERATION][ROBUST] Context: occasion={req.occasion}, style={req.style}, mood={req.mood}")
            logger.info(f"[GENERATION][ROBUST] Wardrobe categories: {[(item.get('type', 'unknown') if item else 'unknown') for item in wardrobe_items[:10]]}...")
            
        except Exception as e:
            logger.error(f"❌ Error creating generation context: {e}")
            raise
        
        # Generate outfit using robust service
        try:
            robust_service = RobustOutfitGenerationService()
            
            # DEBUG: Collect robust service debug information
            debug_info = {
                "robust_input": {
                    "wardrobe_count": len(context.wardrobe),
                    "occasion": context.occasion,
                    "style": context.style,
                    "mood": context.mood,
                    "user_id": context.user_id,
                    "wardrobe_items": [
                        {
                            "id": getattr(item, 'id', 'NO_ID'),
                            "name": getattr(item, 'name', 'NO_NAME'),
                            "type": str(getattr(item, 'type', 'NO_TYPE'))
                        } for item in context.wardrobe[:3]
                    ]
                }
            }
            
            # DEBUG: Log wardrobe item types before robust service call
            print(f"🔍 DEBUG WARDROBE ITEMS: About to call robust service")
            if hasattr(context, 'wardrobe') and context.wardrobe:
                for i, item in enumerate(context.wardrobe):
                    item_type = getattr(item, 'type', 'NO_TYPE')
                    item_name = getattr(item, 'name', 'NO_NAME')
                    print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type='{item_type}' name='{item_name}'")
                    if hasattr(item_type, 'value'):
                        print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type.value='{item_type.value}'")
                    if hasattr(item_type, 'name'):
                        print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type.name='{item_type.name}'")
            else:
                print(f"🔍 DEBUG WARDROBE ITEMS: No wardrobe items or wardrobe is None")
            
            # Call robust service
            robust_outfit = await robust_service.generate_outfit(context)
            logger.error(f"🚨 FORCE REDEPLOY v12.0: generate_outfit completed successfully")
            
        except Exception as e:
            import traceback
            error_details = {
                "error_type": str(type(e).__name__),
                "error_message": str(e),
                "full_traceback": traceback.format_exc(),
                "context_info": {
                    "context_type": str(type(context)),
                    "context_wardrobe_length": len(context.wardrobe) if hasattr(context, 'wardrobe') and context.wardrobe else 0,
                    "context_occasion": getattr(context, 'occasion', 'NO_OCCASION'),
                    "context_style": getattr(context, 'style', 'NO_STYLE'),
                    "context_user_id": getattr(context, 'user_id', 'NO_USER_ID')
                }
            }
            logger.error("🔥 Robust outfit generation crash", extra=error_details, exc_info=True)
            print(f"🔥 ROBUST GENERATION CRASH: {error_details}")
            print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
            
            # Return debug information instead of raising
            return {
                'id': str(uuid4()),
                'name': f"Debug {req.style} outfit",
                'style': req.style,
                'mood': req.mood,
                'occasion': req.occasion,
                'items': [],
                'confidence_score': 0.0,
                'reasoning': f"Robust service failed: {error_details['error_message']}",
                'createdAt': datetime.now(),
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'wearCount': 0,
                'lastWorn': None,
                'metadata': {
                    'generation_strategy': 'robust_debug',
                    'generation_time': time.time(),
                    'error_details': error_details
                }
            }
        
        print(f"🔍 DEBUG ROBUST RETURN: robust_outfit = {robust_outfit}")
        if robust_outfit is None:
            print(f"🚨 CRITICAL: robust_outfit is None!")
            raise Exception("Robust service returned None - this should not happen")
        
        # Convert robust outfit to expected format
        try:
            outfit = {
                'id': str(uuid4()),
                'name': f"{req.style} {req.occasion} outfit",
                'style': req.style,
                'mood': req.mood,
                'occasion': req.occasion,
                'items': [],
                'confidence_score': 0.8,
                'reasoning': f"Generated using robust service for {req.occasion} {req.style} style",
                'createdAt': datetime.now(),
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'wearCount': 0,
                'lastWorn': None,
                'metadata': {
                    'generation_strategy': 'robust_service',
                    'generation_time': time.time(),
                    'wardrobe_size': len(wardrobe_items)
                }
            }
            
            # Convert robust outfit items to expected format
            if hasattr(robust_outfit, 'items') and robust_outfit.items:
                print(f"🔍 DEBUG CONVERSION: First item: {robust_outfit.items[0]}")
                outfit['items'] = robust_outfit.items
                logger.info(f"✅ Successfully converted robust outfit to expected format")
                logger.info(f"✅ Outfit has {len(outfit.get('items', []))} items")
            
            # Ensure base item is included
            if req.baseItemId:
                outfit = ensure_base_item_included(outfit, req.baseItemId, wardrobe_items)
            
            # Log generation strategy
            log_generation_strategy(outfit, user_id)
            
            logger.info(f"✨ Generated outfit: {outfit.get('name', 'Unknown')}")
            
        except Exception as conversion_error:
            logger.error(f"❌ Error converting robust outfit: {conversion_error}")
            raise
        
        return outfit
