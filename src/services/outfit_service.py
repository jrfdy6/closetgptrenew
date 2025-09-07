"""
Main Outfit Service
Orchestrates all modular outfit services with proper temperature handling.
"""

from typing import List, Optional, Dict, Any, Union
import time
import uuid
from ..config.firebase import db
from ..custom_types.outfit import OutfitGeneratedOutfit
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile

# Import modular services
from .outfit_core_service import OutfitCoreService
from .outfit_filtering_service import OutfitFilteringService
from .outfit_validation_service import OutfitValidationService
from .outfit_selection_service import OutfitSelectionService
from .outfit_scoring_service import OutfitScoringService
from .outfit_utility_service import OutfitUtilityService
from .outfit_generation_pipeline_service import OutfitGenerationPipelineService
from .outfit_fallback_service import OutfitFallbackService
from .outfit_generation_service import OutfitGenerationService
from .initial_filter import light_filtering
from .smart_selector_fixed import select_items
from .validation_orchestrator import validate_outfit
from .fallback_handler import run_fallback

async def generate_outfit_pipeline(user_id, wardrobe, context):
    print(f"🔍 DEBUG: Starting outfit generation pipeline with {len(wardrobe)} items")
    
    # Step 1: Light filtering
    filtered = light_filtering(wardrobe, context)
    print(f"🔍 DEBUG: After filtering: {len(filtered)} items")
    
    # Step 2: Smart selection
    selection = await select_items(filtered, context)
    print(f"🔍 DEBUG: After selection: {len(selection)} items")
    
    # Step 3: Validate only the selected items, not the entire wardrobe
    if selection:
        validation_result = await validate_outfit(selection, context)
        print(f"🔍 DEBUG: Validation result - valid: {validation_result['is_valid']}, errors: {len(validation_result['errors'])}, warnings: {len(validation_result['warnings'])}")
    else:
        print("🔍 DEBUG: No items selected, skipping validation")
        validation_result = {"is_valid": False, "errors": ["No items selected"], "warnings": []}

    if validation_result["is_valid"]:
        return {
            "outfit": selection,
            "warnings": validation_result["warnings"],
            "status": "success"
        }

    # Soft fail fallback attempt
    print("🔍 DEBUG: Primary selection failed, trying fallback")
    fallback_items = await run_fallback(filtered, context)
    print(f"🔍 DEBUG: Fallback selected {len(fallback_items)} items")
    
    if fallback_items:
        retry_validation = await validate_outfit(fallback_items, context)
        print(f"🔍 DEBUG: Fallback validation - valid: {retry_validation['is_valid']}, errors: {len(retry_validation['errors'])}, warnings: {len(retry_validation['warnings'])}")
    else:
        print("🔍 DEBUG: No fallback items selected")
        retry_validation = {"is_valid": False, "errors": ["No fallback items selected"], "warnings": []}

    if retry_validation["is_valid"]:
        return {
            "outfit": fallback_items,
            "warnings": ["Fallback triggered"] + retry_validation["warnings"],
            "status": "fallback_success"
        }

    # Final fail - return at least some items if we have them
    if selection:
        print("🔍 DEBUG: Returning original selection despite validation failures")
        return {
            "outfit": selection,
            "warnings": ["Validation failed but returning items anyway"] + validation_result["warnings"],
            "status": "soft_fail"
        }
    elif fallback_items:
        print("🔍 DEBUG: Returning fallback items despite validation failures")
        return {
            "outfit": fallback_items,
            "warnings": ["Validation failed but returning fallback items anyway"] + retry_validation["warnings"],
            "status": "soft_fail"
        }

    # Complete failure
    print("🔍 DEBUG: Complete generation failure")
    return {
        "outfit": [],
        "errors": retry_validation["errors"],
        "status": "fail"
    }

class OutfitService:
    """Main outfit service that orchestrates all modular services."""
    
    def __init__(self):
        self.db = db
        self.collection = self.db.collection("outfits")
        self.wardrobe_collection = self.db.collection("wardrobe")
        
        # Initialize modular services
        self.core_service = OutfitCoreService()
        self.filtering_service = OutfitFilteringService()
        self.validation_service = OutfitValidationService()
        self.selection_service = OutfitSelectionService()
        self.scoring_service = OutfitScoringService()
        self.utility_service = OutfitUtilityService()
        self.pipeline_service = OutfitGenerationPipelineService()
        self.fallback_service = OutfitFallbackService()
        self.generation_service = OutfitGenerationService()
        
    def _safe_temperature_convert(self, temperature) -> float:
        """Safely convert temperature to float to prevent string vs float comparison errors."""
        if isinstance(temperature, str):
            try:
                return float(temperature)
            except (ValueError, TypeError):
                return 70.0
        elif temperature is None:
            return 70.0
        else:
            return float(temperature)
    
    async def get_outfits(self) -> List[OutfitGeneratedOutfit]:
        """Get all outfits from Firestore."""
        return await self.core_service.get_outfits()
    
    async def get_outfit(self, outfit_id: str) -> Optional[OutfitGeneratedOutfit]:
        """Get a single outfit by ID from Firestore."""
        return await self.core_service.get_outfit(outfit_id)
    
    async def get_outfits_by_user(self, user_id: str) -> List[OutfitGeneratedOutfit]:
        """Get all outfits for a specific user."""
        try:
            outfits_ref = self.collection.where('user_id', '==', user_id)
            outfits_docs = outfits_ref.stream()
            
            outfits = []
            for doc in outfits_docs:
                outfit_data = doc.to_dict()
                # Convert to OutfitGeneratedOutfit format
                outfit = OutfitGeneratedOutfit(
                    id=doc.id,
                    name=outfit_data.get("name", "Untitled Outfit"),
                    description=outfit_data.get("description", ""),
                    items=outfit_data.get("items", []),
                    explanation=outfit_data.get("reasoning", ""),
                    pieces=outfit_data.get("items", []),
                    styleTags=[outfit_data.get("style", "casual")],
                    colorHarmony="neutral",
                    styleNotes=outfit_data.get("description", ""),
                    occasion=outfit_data.get("occasion", "Casual"),
                    season=outfit_data.get("season", "all"),
                    style=outfit_data.get("style", "casual"),
                    mood=outfit_data.get("mood", "neutral"),
                    wasSuccessful=outfit_data.get("wasSuccessful", True),
                    confidence_score=outfit_data.get("confidence_score", 1.0),
                    userFeedback=outfit_data.get("userFeedback"),
                    feedback_summary=outfit_data.get("feedback_summary"),
                    warnings=outfit_data.get("warnings", []),
                    validationErrors=outfit_data.get("validationErrors", []),
                    validation_details=outfit_data.get("validation_details", {
                        "errors": [],
                        "warnings": [],
                        "fixes": []
                    })
                )
                outfits.append(outfit)
            
            return outfits
        except Exception as e:
            print(f"Error getting outfits for user {user_id}: {e}")
            return []
    
    async def create_custom_outfit(self, outfit_data: Dict[str, Any]) -> OutfitGeneratedOutfit:
        """Create a custom outfit by saving it directly to the database."""
        try:
            # Generate a unique ID if not provided
            if not outfit_data.get("id"):
                outfit_data["id"] = str(uuid.uuid4())
            
            # Ensure required fields
            outfit_data["createdAt"] = outfit_data.get("createdAt", int(time.time()))
            outfit_data["is_custom"] = True
            
            # Save to Firestore
            doc_ref = self.collection.document(outfit_data["id"])
            doc_ref.set(outfit_data)
            
            # Convert to OutfitGeneratedOutfit format
            return OutfitGeneratedOutfit(
                id=outfit_data["id"],
                name=outfit_data["name"],
                description=outfit_data.get("description", ""),
                items=outfit_data["items"],
                explanation=outfit_data.get("reasoning", "Custom outfit created by user"),
                pieces=outfit_data["items"],
                styleTags=[outfit_data.get("style", "custom")],
                colorHarmony="custom",
                styleNotes=outfit_data.get("description", "Custom outfit"),
                occasion=outfit_data["occasion"],
                season="all",
                style=outfit_data["style"],
                mood="custom",
                wasSuccessful=True,
                confidence_score=outfit_data.get("confidence_score", 1.0),
                userFeedback=None,
                feedback_summary=None,
                warnings=[],
                validationErrors=[],
                validation_details={
                    "errors": [],
                    "warnings": [],
                    "fixes": []
                }
            )
            
        except Exception as e:
            print(f"Error creating custom outfit: {e}")
            raise e
    
    async def update_outfit(self, outfit_id: str, outfit_data: Dict[str, Any], user_id: str) -> OutfitGeneratedOutfit:
        """Update an existing outfit with new details and items."""
        try:
            # Check if outfit exists and belongs to user
            outfit_doc = self.collection.document(outfit_id).get()
            if not outfit_doc.exists:
                raise Exception("Outfit not found")
            
            outfit_doc_data = outfit_doc.to_dict()
            stored_user_id = outfit_doc_data.get('user_id')
            
            # For development: allow updates if using fallback authentication
            if stored_user_id != user_id:
                raise Exception("Access denied - outfit does not belong to user")
            
            # Update the outfit document with items
            self.collection.document(outfit_id).update(outfit_data)
            
            # Get user's wardrobe to fetch full item details
            wardrobe_collection = self.db.collection('wardrobe')
            wardrobe_docs = wardrobe_collection.where('userId', '==', user_id).stream()
            wardrobe_items = {doc.id: doc.to_dict() for doc in wardrobe_docs}
            
            # Create updated pieces array to match the new items
            updated_pieces = []
            for item_id in outfit_data["items"]:
                # Get full item details from wardrobe
                item_data = wardrobe_items.get(item_id, {})
                
                # Convert dominantColors from complex objects to simple strings
                dominant_colors = []
                raw_colors = item_data.get("dominantColors", [])
                for color in raw_colors:
                    if isinstance(color, dict) and 'name' in color:
                        dominant_colors.append(color['name'])
                    elif isinstance(color, str):
                        dominant_colors.append(color)
                    else:
                        dominant_colors.append(str(color))
                
                # Create piece with full item info
                piece = {
                    "itemId": item_id,
                    "name": item_data.get("name", "Unknown Item"),
                    "type": item_data.get("type", "unknown"),
                    "reason": "Updated outfit item",
                    "dominantColors": dominant_colors,
                    "style": item_data.get("style", []),
                    "occasion": item_data.get("occasion", []),
                    "imageUrl": item_data.get("imageUrl", "")
                }
                updated_pieces.append(piece)
            
            # Update the pieces field in the database
            self.collection.document(outfit_id).update({"pieces": updated_pieces})
            
            # Get the updated outfit
            updated_doc = self.collection.document(outfit_id).get()
            updated_data = updated_doc.to_dict()
            
            # Convert items to proper format for OutfitGeneratedOutfit
            formatted_items = []
            formatted_pieces = []
            
            # Get user's wardrobe to fetch full item details
            wardrobe_collection = self.db.collection('wardrobe')
            wardrobe_docs = wardrobe_collection.where('userId', '==', user_id).stream()
            wardrobe_items = {doc.id: doc.to_dict() for doc in wardrobe_docs}
            
            for item_id in updated_data["items"]:
                # Store the ID in items array (for Pydantic validation)
                formatted_items.append(item_id)
                
                # Get full item details from wardrobe
                item_data = wardrobe_items.get(item_id, {})
                
                # Convert dominantColors from complex objects to simple strings
                dominant_colors = []
                raw_colors = item_data.get("dominantColors", [])
                for color in raw_colors:
                    if isinstance(color, dict) and 'name' in color:
                        dominant_colors.append(color['name'])
                    elif isinstance(color, str):
                        dominant_colors.append(color)
                    else:
                        dominant_colors.append(str(color))
                
                # Store full item info in pieces array (for frontend display)
                formatted_pieces.append({
                    "itemId": item_id,
                    "name": item_data.get("name", "Unknown Item"),
                    "type": item_data.get("type", "unknown"),
                    "reason": "Updated outfit item",
                    "dominantColors": dominant_colors,
                    "style": item_data.get("style", []),
                    "occasion": item_data.get("occasion", []),
                    "imageUrl": item_data.get("imageUrl", "")
                })
            
            # Convert to OutfitGeneratedOutfit format
            return OutfitGeneratedOutfit(
                id=outfit_id,
                name=updated_data["name"],
                description=updated_data.get("description", ""),
                items=formatted_items,
                explanation=updated_data.get("reasoning", "Outfit updated by user"),
                pieces=formatted_pieces,
                styleTags=[updated_data.get("style", "custom")],
                colorHarmony="custom",
                styleNotes=updated_data.get("description", "Updated outfit"),
                occasion=updated_data["occasion"],
                season="all",
                style=updated_data["style"],
                mood="custom",
                wasSuccessful=True,
                confidence_score=updated_data.get("confidence_score", 1.0),
                userFeedback=updated_data.get("userFeedback"),
                feedback_summary=updated_data.get("feedback_summary"),
                warnings=[],
                validationErrors=[],
                validation_details={
                    "errors": [],
                    "warnings": [],
                    "fixes": []
                }
            )
            
        except Exception as e:
            print(f"Error updating outfit: {e}")
            raise e
    
    async def generate_outfit(
        self,
        occasion: str,
        weather: WeatherData,
        wardrobe: List[ClothingItem],
        user_profile: UserProfile,
        likedOutfits: List[str],
        trendingStyles: List[str],
        preferences: Optional[Dict[str, Any]] = None,
        outfitHistory: Optional[List[Dict[str, Any]]] = None,
        randomSeed: Optional[float] = None,
        season: Optional[str] = None,
        style: Optional[str] = None,
        baseItem: Optional[ClothingItem] = None,
        mood: Optional[str] = None
    ) -> OutfitGeneratedOutfit:
        """Main outfit generation method - orchestrates all modular services."""
        
        # Ensure temperature is properly converted
        weather.temperature = self._safe_temperature_convert(weather.temperature)
        
        # Prepare context for the new modular pipeline
        context = {
            "occasion": occasion,
            "weather": weather,
            "user_profile": user_profile,
            "style": style,
            "mood": mood,
            "base_item": baseItem,
            "trending_styles": trendingStyles or [],
            "liked_outfits": likedOutfits or [],
            "outfit_history": outfitHistory or [],
            "original_wardrobe": wardrobe,
            "preferences": preferences or {},
            "season": season,
            "random_seed": randomSeed
        }
        
        # Use the new modular pipeline
        result = await generate_outfit_pipeline(
            user_id=user_profile.id,
            wardrobe=wardrobe,
            context=context
        )
        
        # Check if pipeline was successful
        if result["status"] == "fail":
            # Return error outfit
            return OutfitGeneratedOutfit(
                id="error",
                name=f"{occasion} Outfit",
                description=f"Error: {result.get('errors', ['Generation failed'])}",
                items=[],
                explanation="Generation failed",
                pieces=[],
                styleTags=[],
                colorHarmony="neutral",
                styleNotes="Generation failed",
                occasion=occasion,
                season=season or "all",
                style=style or "casual",
                mood=mood or "neutral",
                wasSuccessful=False,
                validationErrors=result.get('errors', ['Generation failed'])
            )
        
        # Extract items from successful result
        selected_items = result.get("outfit", [])
        warnings = result.get("warnings", [])
        
        # Convert items to OutfitPiece format
        pieces = []
        for item in selected_items:
            # Convert dominantColors to strings
            dominant_colors = []
            for color in getattr(item, 'dominantColors', []):
                if hasattr(color, 'name'):
                    dominant_colors.append(color.name)
                elif isinstance(color, dict) and 'name' in color:
                    dominant_colors.append(color['name'])
                elif isinstance(color, str):
                    dominant_colors.append(color)
                else:
                    # Fallback for any other color format
                    dominant_colors.append(str(color))
            
            piece = {
                "itemId": item.id,
                "name": item.name,
                "type": item.type,
                "reason": f"Selected for {occasion} occasion",
                "dominantColors": dominant_colors,
                "style": getattr(item, 'style', []),
                "occasion": getattr(item, 'occasion', []),
                "imageUrl": getattr(item, 'imageUrl', "")
            }
            pieces.append(piece)
        
        # Generate outfit details
        outfit_name = f"{occasion} Outfit"
        outfit_description = f"A {style or 'casual'} outfit for {occasion}"
        outfit_explanation = f"Generated {len(selected_items)} items for {occasion} with {style or 'casual'} style"
        
        # Generate style tags
        style_tags = []
        if style:
            style_tags.append(style)
        style_tags.extend([occasion, "generated"])
        
        # Determine color harmony
        color_harmony = "neutral"
        if selected_items:
            # Simple color harmony logic
            all_colors = []
            for item in selected_items:
                colors = getattr(item, 'dominantColors', [])
                # Convert Color objects to strings for set operations
                for color in colors:
                    if hasattr(color, 'name'):
                        all_colors.append(color.name)
                    elif isinstance(color, dict) and 'name' in color:
                        all_colors.append(color['name'])
                    elif isinstance(color, str):
                        all_colors.append(color)
                    else:
                        # Fallback for any other color format
                        all_colors.append(str(color))
            
            unique_colors = set(all_colors)
            if len(unique_colors) <= 2:
                color_harmony = "monochromatic"
            elif len(unique_colors) <= 4:
                color_harmony = "complementary"
            else:
                color_harmony = "eclectic"
        
        # Generate style notes
        style_notes = f"Generated outfit with {len(selected_items)} items for {occasion}"
        if style:
            style_notes += f" in {style} style"
        
        # Create the outfit
        generated_outfit = OutfitGeneratedOutfit(
            id=str(uuid.uuid4()),
            name=outfit_name,
            description=outfit_description,
            items=selected_items,
            explanation=outfit_explanation,
            pieces=pieces,
            styleTags=style_tags,
            colorHarmony=color_harmony,
            styleNotes=style_notes,
            occasion=occasion,
            season=season or "all",
            style=style or "casual",
            mood=mood or "neutral",
            wasSuccessful=True,
            user_id=user_profile.id,
            warnings=warnings # Add warnings to the generated outfit
        )
        
        # Save the outfit to the database
        await self.core_service.save_outfit(generated_outfit)
        
        return generated_outfit
    
    async def update_outfit_feedback(self, outfit_id: str, feedback: Dict[str, Any]) -> bool:
        """Update outfit feedback."""
        return await self.core_service.update_outfit_feedback(outfit_id, feedback)
    
    async def get_outfit_analytics(self, user_id: str = None, start_date: int = None, end_date: int = None) -> Dict[str, Any]:
        """Get outfit analytics."""
        return await self.core_service.get_outfit_analytics(user_id, start_date, end_date)
    
    # Delegate to specific services for specialized operations
    def filter_by_weather(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Filter items by weather with proper temperature handling."""
        return self.filtering_service.filter_by_weather_strict(items, weather)
    
    def filter_by_occasion(self, items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Filter items by occasion."""
        return self.filtering_service.filter_by_occasion_strict(items, occasion)
    
    def validate_outfit(self, items: List[ClothingItem], context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outfit using validation service."""
        return self.validation_service.validate_outfit_with_orchestration(items, context)
    
    def calculate_weather_score(self, items: List[ClothingItem], weather: WeatherData) -> float:
        """Calculate weather appropriateness score."""
        return self.scoring_service.calculate_weather_appropriateness(items, weather)
    
    def select_items(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select items using selection service."""
        return self.selection_service.smart_selection_phase(filtered_wardrobe, context)
    
    def debug_outfit_generation(self, items: List[ClothingItem], phase: str):
        """Debug outfit generation process."""
        self.utility_service.debug_outfit_generation(items, phase)


