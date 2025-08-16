"""
Outfit Generation Pipeline Service
Pipeline orchestration and context processing.
"""

from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from .outfit_filtering_service import OutfitFilteringService
from .outfit_selection_service import OutfitSelectionService
from .outfit_validation_service import OutfitValidationService
from .outfit_fallback_service import OutfitFallbackService

class OutfitGenerationPipelineService:
    def __init__(self):
        self.filtering_service = OutfitFilteringService()
        self.selection_service = OutfitSelectionService()
        self.validation_service = OutfitValidationService()
        self.fallback_service = OutfitFallbackService()
        
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
            
    async def generate_outfit_refined_pipeline(self, occasion: str, weather: WeatherData, wardrobe: List[ClothingItem],
                                       user_profile: UserProfile, style: Optional[str] = None, mood: Optional[str] = None,
                                       baseItem: Optional[ClothingItem] = None, trendingStyles: List[str] = None,
                                       likedOutfits: List[str] = None, outfit_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Main pipeline for outfit generation with light filtering and smart fallback."""
        try:
            print("🔄 Starting refined pipeline...")
            
            # Phase 1: Input Context Gathering
            context = self.gather_input_context(
                occasion, weather, user_profile, style, mood, 
                trendingStyles or [], likedOutfits or [], baseItem, outfit_history, wardrobe
            )
            print(f"✅ Phase 1: Context gathered - {len(wardrobe)} items, {occasion}, {style}")
            
            # Phase 2: Light Filtering (based on availability/weather only)
            filtered_wardrobe = self.filtering_service.apply_light_filtering(wardrobe, context)
            print(f"✅ Phase 2: Light filtering - {len(filtered_wardrobe)} items available")
            
            if len(filtered_wardrobe) < 2:
                return {
                    "success": False,
                    "message": f"Insufficient items after light filtering: {len(filtered_wardrobe)} items (minimum 2 required)"
                }
            
            # Phase 3: Smart Selection (style/mood-aware)
            selected_items = self.selection_service.smart_selection_phase(filtered_wardrobe, context)
            print(f"✅ Phase 3: Smart selection - {len(selected_items)} items selected")
            
            # Remove duplicates
            unique_items = []
            seen_ids = set()
            for item in selected_items:
                if item.id not in seen_ids:
                    unique_items.append(item)
                    seen_ids.add(item.id)
            
            if len(unique_items) != len(selected_items):
                print(f"⚠️  Removed {len(selected_items) - len(unique_items)} duplicate items")
                selected_items = unique_items
            
            # Phase 4: Validation (hard/soft rules)
            validation_result = await self.validation_service.validate_outfit_with_orchestration(selected_items, context)
            
            # Phase 5: Handle Validation Results
            if validation_result["is_valid"]:
                # Pass - Return Outfit + Warnings
                print(f"✅ Phase 4: Validation passed - {len(selected_items)} items")
                return {
                    "success": True,
                    "items": selected_items,
                    "context": context,
                    "warnings": validation_result.get("warnings", [])
                }
            else:
                # Check if it's a soft failure (can be auto-fixed)
                soft_errors = [error for error in validation_result["errors"] 
                             if self._is_soft_error(error)]
                hard_errors = [error for error in validation_result["errors"] 
                             if not self._is_soft_error(error)]
                
                if soft_errors and not hard_errors:
                    # Soft Fail - Auto-Fix via Fallback
                    print(f"⚠️  Phase 4: Soft validation failures - attempting auto-fix")
                    return await self._handle_soft_failure(selected_items, soft_errors, context)
                else:
                    # Hard Fail - Suggest Retry or Error
                    print(f"❌ Phase 4: Hard validation failures - cannot auto-fix")
                    return {
                        "success": False,
                        "message": f"Hard validation errors: {hard_errors}",
                        "errors": hard_errors,
                        "warnings": validation_result.get("warnings", [])
                    }
            
        except Exception as e:
            print(f"❌ ERROR: _generate_outfit_refined_pipeline - {str(e)}")
            return {
                "success": False,
                "message": f"Pipeline error: {str(e)}"
            }
    
    def _is_soft_error(self, error: str) -> bool:
        """Determine if an error is soft (can be auto-fixed) or hard (requires retry)."""
        soft_error_keywords = [
            "insufficient", "too few", "missing", "duplicate", "layering", 
            "style mismatch", "color harmony", "weather appropriateness"
        ]
        
        error_lower = error.lower()
        return any(keyword in error_lower for keyword in soft_error_keywords)
    
    async def _handle_soft_failure(self, selected_items: List[ClothingItem], soft_errors: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle soft failures by attempting fallback fixes."""
        print("🔧 Attempting auto-fix via fallback...")
        
        try:
            healed_items, remaining_errors, healing_log = await self.fallback_service.heal_outfit_with_fallbacks(
                failed_outfit=selected_items,
                validation_errors=soft_errors,
                context=context
            )
            
            if healed_items and len(healed_items) >= context["target_counts"]["min_items"]:
                print(f"✅ Auto-fix successful - {len(healed_items)} items")
                return {
                    "success": True,
                    "items": healed_items,
                    "context": context,
                    "warnings": [f"Auto-fixed: {', '.join(soft_errors)}"],
                    "healing_log": healing_log
                }
            else:
                print(f"⚠️  Auto-fix failed - {len(healed_items) if healed_items else 0} items")
                return {
                    "success": False,
                    "message": f"Auto-fix failed: {remaining_errors}",
                    "errors": remaining_errors,
                    "warnings": [f"Attempted auto-fix but failed: {', '.join(soft_errors)}"]
                }
                
        except Exception as fallback_error:
            print(f"❌ Fallback error: {fallback_error}")
            return {
                "success": False,
                "message": f"Fallback error: {str(fallback_error)}",
                "errors": soft_errors
            }
        
    def gather_input_context(self, occasion: str, weather: WeatherData, user_profile: UserProfile,
                           style: Optional[str], mood: Optional[str], trendingStyles: List[str],
                           likedOutfits: List[str], baseItem: Optional[ClothingItem],
                           outfit_history: Optional[List[Dict[str, Any]]] = None,
                           original_wardrobe: Optional[List[ClothingItem]] = None) -> Dict[str, Any]:
        """Gather input context for outfit generation."""
        # Get rules and rules
        occasion_rule = self._get_occasion_rule(occasion)
        layering_rule = self._get_layering_rule(weather.temperature)
        mood_rule = self._get_mood_rule(mood) if mood else None
        
        # Determine target item counts by occasion
        target_counts = self.get_target_item_counts(occasion)
        
        # Get style compatibility matrix
        style_matrix = self._get_style_compatibility_matrix(style)
        
        return {
            "occasion": occasion,
            "weather": weather,
            "user_profile": user_profile,
            "style": style,
            "mood": mood,
            "base_item": baseItem,
            "trending_styles": trendingStyles,
            "liked_outfits": likedOutfits,
            "outfit_history": outfit_history or [],  # NEW: Include outfit history for diversity
            "original_wardrobe": original_wardrobe or [],  # NEW: Include original wardrobe for fallback
            "occasion_rule": occasion_rule,
            "layering_rule": layering_rule,
            "mood_rule": mood_rule,
            "target_counts": target_counts,
            "style_matrix": style_matrix
        }
        
    def get_target_item_counts(self, occasion: str) -> Dict[str, Any]:
        """Get target item counts for the occasion."""
        # Basic target counts
        base_counts = {
            "min_items": 3,
            "max_items": 6,
            "required_categories": ["top", "bottom", "shoes"]
        }
        
        # Adjust for specific occasions
        if "formal" in occasion.lower() or "business" in occasion.lower():
            base_counts["min_items"] = 4
            base_counts["required_categories"] = ["top", "bottom", "shoes", "accessory"]
        elif "athletic" in occasion.lower() or "gym" in occasion.lower():
            base_counts["min_items"] = 3
            base_counts["required_categories"] = ["top", "bottom", "shoes"]
        elif "casual" in occasion.lower():
            base_counts["min_items"] = 3
            base_counts["required_categories"] = ["top", "bottom", "shoes"]
        
        return base_counts

    # Helper methods
    def _get_occasion_rule(self, occasion: str):
        """Get occasion rule."""
        return {"occasion": occasion}
    
    def _get_layering_rule(self, temperature: float):
        """Get layering rule based on temperature."""
        return {"temperature": temperature, "layers": 1}
    
    def _get_mood_rule(self, mood: str):
        """Get mood rule."""
        return {"mood": mood}
    
    def _get_style_compatibility_matrix(self, style: Optional[str]) -> Dict[str, Any]:
        """Get style compatibility matrix."""
        return {"style": style or "casual"}
