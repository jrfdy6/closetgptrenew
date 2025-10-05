"""
Personalization Service
======================

Enhanced personalization service that integrates the existing data personalization
engine with the modular outfit generation services.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from src.services.existing_data_personalization import ExistingDataPersonalizationEngine
from src.routes.outfits.models import OutfitRequest
from src.routes.personalization_demo.models import PersonalizationDemoRequest, PersonalizationDemoResponse

logger = logging.getLogger(__name__)

class PersonalizationService:
    """
    Enhanced personalization service that combines:
    1. Existing data personalization engine
    2. Modular outfit generation services
    3. Generation mode selection (simple-minimal vs robust)
    """
    
    def __init__(self):
        self.personalization_engine = ExistingDataPersonalizationEngine()
        self.logger = logger
        
        # Initialize generation services
        self._initialize_generation_services()
    
    def _initialize_generation_services(self):
        """Initialize the modular generation services."""
        try:
            from src.services.outfits.generation_service import OutfitGenerationService
            from src.services.outfits.simple_service import SimpleOutfitService
            from src.services.outfits.robust_service import RobustOutfitGenerationService
            
            self.generation_service = OutfitGenerationService()
            self.simple_service = SimpleOutfitService()
            self.robust_service = RobustOutfitGenerationService()
            
            self.logger.info("✅ All generation services initialized successfully")
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to initialize generation services: {e}")
            self.generation_service = None
            self.simple_service = None
            self.robust_service = None
    
    async def generate_personalized_outfit(
        self, 
        req: PersonalizationDemoRequest, 
        user_id: str
    ) -> PersonalizationDemoResponse:
        """
        Generate a personalized outfit using the selected generation mode.
        
        Args:
            req: Personalization demo request with generation mode
            user_id: User ID for personalization
            
        Returns:
            Personalized outfit response with generation details
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🎯 Generating personalized outfit using {req.generation_mode} mode for user {user_id}")
            
            # Get user preferences from existing data
            preference = await self.personalization_engine.get_user_preference_from_existing_data(user_id)
            
            # Convert request to OutfitRequest for generation services
            outfit_request = self._convert_to_outfit_request(req)
            
            # Generate outfit based on selected mode
            if req.generation_mode == "robust":
                outfit_data = await self._generate_robust_outfit(outfit_request, user_id)
                generation_strategy = "robust_with_personalization"
            else:  # simple-minimal
                outfit_data = await self._generate_simple_outfit(outfit_request, user_id)
                generation_strategy = "simple_with_personalization"
            
            # Apply personalization if user has enough data
            if preference.total_interactions >= 3:
                outfit_data = await self._apply_personalization(outfit_data, preference, user_id)
                personalization_applied = True
                personalization_score = outfit_data.get('personalization_score', 0.0)
            else:
                personalization_applied = False
                personalization_score = None
            
            # Convert ClothingItem objects to dictionaries if needed
            items = outfit_data.get("items", [])
            converted_items = []
            for item in items:
                if hasattr(item, 'model_dump'):  # Pydantic model
                    converted_items.append(item.model_dump())
                elif hasattr(item, '__dict__'):  # Regular object
                    converted_items.append(item.__dict__)
                elif isinstance(item, dict):  # Already a dictionary
                    converted_items.append(item)
                else:
                    # Fallback: convert to string representation
                    converted_items.append({"name": str(item), "type": "unknown"})
            
            # Create enhanced response
            response = PersonalizationDemoResponse(
                id=outfit_data.get("id", f"personalized_{int(time.time())}"),
                name=outfit_data.get("name", f"{req.style} {req.occasion} Outfit"),
                items=converted_items,
                style=req.style,
                occasion=req.occasion,
                mood=req.mood,
                weather=req.weather or {},
                confidence_score=outfit_data.get("confidence_score", 0.8),
                personalization_score=personalization_score,
                personalization_applied=personalization_applied,
                user_interactions=preference.total_interactions,
                data_source="personalization_demo",
                generation_mode=req.generation_mode,
                generation_strategy=generation_strategy,
                metadata={
                    **outfit_data.get("metadata", {}),
                    "generation_time": time.time() - start_time,
                    "personalization_enabled": True,
                    "user_id": user_id,
                    "preference_data_source": preference.data_source,
                    "generation_mode": req.generation_mode,
                    "ready_for_personalization": preference.total_interactions >= 3
                }
            )
            
            self.logger.info(f"✅ Generated personalized outfit using {req.generation_mode} mode (personalization: {personalization_applied})")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Personalized outfit generation failed: {e}")
            raise
    
    def _convert_to_outfit_request(self, req: PersonalizationDemoRequest) -> OutfitRequest:
        """Convert personalization demo request to outfit request."""
        return OutfitRequest(
            occasion=req.occasion,
            style=req.style,
            mood=req.mood,
            weather=req.weather,
            wardrobe=req.wardrobe,
            user_profile=req.user_profile,
            baseItemId=req.baseItemId
        )
    
    async def _generate_robust_outfit(self, outfit_request: OutfitRequest, user_id: str) -> Dict[str, Any]:
        """Generate outfit using robust generation service."""
        if not self.generation_service:
            raise Exception("Robust generation service not available")
        
        try:
            outfit_data = await self.generation_service.generate_outfit_logic(outfit_request, user_id)
            self.logger.info("✅ Robust outfit generation successful")
            return outfit_data
        except Exception as e:
            self.logger.warning(f"⚠️ Robust generation failed: {e}")
            # Fallback to simple generation
            return await self._generate_simple_outfit(outfit_request, user_id)
    
    async def _generate_simple_outfit(self, outfit_request: OutfitRequest, user_id: str) -> Dict[str, Any]:
        """Generate outfit using simple generation service."""
        if not self.simple_service:
            raise Exception("Simple generation service not available")
        
        outfit_data = await self.simple_service.generate_simple_outfit(outfit_request, user_id)
        self.logger.info("✅ Simple outfit generation successful")
        return outfit_data
    
    async def _apply_personalization(
        self, 
        outfit_data: Dict[str, Any], 
        preference, 
        user_id: str
    ) -> Dict[str, Any]:
        """Apply personalization to the generated outfit."""
        try:
            # Rank outfit by existing preferences
            personalized_outfits = self.personalization_engine.rank_outfits_by_existing_preferences(
                user_id, [outfit_data], preference
            )
            
            if personalized_outfits:
                personalized_outfit = personalized_outfits[0]
                self.logger.info(f"✅ Applied personalization for user {user_id}")
                return personalized_outfit
            else:
                self.logger.warning("⚠️ Personalization ranking returned no outfits")
                return outfit_data
                
        except Exception as e:
            self.logger.error(f"❌ Failed to apply personalization: {e}")
            return outfit_data
    
    async def get_personalization_status(self, user_id: str) -> Dict[str, Any]:
        """Get personalization status for the user."""
        try:
            status = await self.personalization_engine.get_personalization_status_from_existing_data(user_id)
            
            # Add generation mode information
            status["available_generation_modes"] = ["simple-minimal", "robust"]
            status["personalization_demo_enabled"] = True
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get personalization status: {e}")
            return {
                "user_id": user_id,
                "personalization_enabled": False,
                "error": str(e),
                "available_generation_modes": ["simple-minimal"],
                "personalization_demo_enabled": False
            }
