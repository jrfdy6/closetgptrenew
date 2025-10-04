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
            # print(f"✅ Phase 1: Context gathered - {len(wardrobe)} items, {occasion}, {style}")
            if baseItem:
#                 print(f"🎯 Base item in context: {baseItem.name} ({baseItem.type})")
#                 print(f"🎯 Context base_item: {(context.get('base_item', 'Not found') if context else 'Not found')}")
            
            # Phase 2: Light Filtering (based on availability/weather only)
            filtered_wardrobe = self.filtering_service.apply_light_filtering(wardrobe, context)
            # print(f"✅ Phase 2: Light filtering - {len(filtered_wardrobe)} items available")
            
            if len(filtered_wardrobe) < 2:
                return {
                    "success": False,
                    "message": f"Insufficient items after light filtering: {len(filtered_wardrobe)} items (minimum 2 required)"
                }
            
            # Phase 3: Smart Selection (style/mood-aware)
            selected_items = self.selection_service.smart_selection_phase(filtered_wardrobe, context)
            # print(f"✅ Phase 3: Smart selection - {len(selected_items)} items selected")
            
            # Remove duplicates
            unique_items = []
            seen_ids = set()
            for item in selected_items:
                if item.id not in seen_ids:
                    unique_items.append(item)
                    seen_ids.add(item.id)
            
            if len(unique_items) != len(selected_items):
                # print(f"⚠️  Removed {len(selected_items) - len(unique_items)} duplicate items")
                selected_items = unique_items
            
            # Phase 4: Enhanced Validation (hard/soft rules + simulation-based rules)
            validation_result = await self.validation_service.validate_outfit_with_enhanced_rules(selected_items, context)
            
            # Phase 5: Handle Validation Results
            if validation_result["is_valid"]:
                # Use filtered items if available, otherwise use selected items
                final_items = validation_result.get("filtered_items", selected_items)
                # print(f"✅ Phase 4: Validation passed - {len(final_items)} items")
                return {
                    "success": True,
                    "items": final_items,
                    "context": context,
                    "warnings": (validation_result.get("warnings", []) if validation_result else [])
                }
            else:
                # Check if it's a soft failure (can be auto-fixed)
                soft_errors = [error for error in validation_result["errors"] 
                             if self._is_soft_error(error)]
                hard_errors = [error for error in validation_result["errors"] 
                             if not self._is_soft_error(error)]
                
                if soft_errors and not hard_errors:
                    # Soft Fail - Auto-Fix via Fallback
                    # print(f"⚠️  Phase 4: Soft validation failures - attempting auto-fix")
                    return await self._handle_soft_failure(selected_items, soft_errors, context)
                else:
                    # Hard Fail - Suggest Retry or Error
                    # print(f"❌ Phase 4: Hard validation failures - cannot auto-fix")
                    return {
                        "success": False,
                        "message": f"Hard validation errors: {hard_errors}",
                        "errors": hard_errors,
                        "warnings": (validation_result.get("warnings", []) if validation_result else [])
                    }
            
        except Exception as e:
            # print(f"❌ ERROR: _generate_outfit_refined_pipeline - {str(e)}")
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
        # print("🔧 Attempting auto-fix via fallback...")
        
        try:
            healed_items, remaining_errors, healing_log = await self.fallback_service.heal_outfit_with_fallbacks(
                failed_outfit=selected_items,
                validation_errors=soft_errors,
                context=context
            )
            
            if healed_items and len(healed_items) >= context["target_counts"]["min_items"]:
                # print(f"✅ Auto-fix successful - {len(healed_items)} items")
                return {
                    "success": True,
                    "items": healed_items,
                    "context": context,
                    "warnings": [f"Auto-fixed: {', '.join(soft_errors)}"],
                    "healing_log": healing_log
                }
            else:
                # print(f"⚠️  Auto-fix failed - {len(healed_items) if healed_items else 0} items")
                return {
                    "success": False,
                    "message": f"Auto-fix failed: {remaining_errors}",
                    "errors": remaining_errors,
                    "warnings": [f"Attempted auto-fix but failed: {', '.join(soft_errors)}"]
                }
                
        except Exception as fallback_error:
            # print(f"❌ Fallback error: {fallback_error}")
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
        
        # Determine target item counts by occasion, style, mood, and temperature
        temperature = weather.temperature if hasattr(weather, 'temperature') else 70.0
        target_counts = self.get_target_item_counts(occasion, style, mood, temperature)
        
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
        
    def get_target_item_counts(self, occasion: str, style: str = None, mood: str = None, temperature: float = 70.0) -> Dict[str, Any]:
        """Get dynamic target item counts based on occasion, style, mood, and temperature with intelligent layering."""
        import random
        
        # Temperature ranges for layering decisions
        is_hot = temperature >= 80
        is_warm = 70 <= temperature < 80
        is_moderate = 50 <= temperature < 70
        is_cold = temperature < 50
        is_very_cold = temperature < 32
        
        # Base counts for different occasions
        occasion_lower = occasion.lower()
        
        if 'formal' in occasion_lower or 'business' in occasion_lower or 'interview' in occasion_lower:
            # Formal occasions - ALWAYS require blazer/suit jacket, then layer based on temperature
            required_categories = ["top", "bottom", "shoes", "outerwear", "accessory"]
            
            # Temperature-based layering for formal occasions
            if is_very_cold:
                # Very cold: shirt + sweater + blazer + coat
                required_categories.extend(["sweater", "coat"])
                total_items = random.randint(6, 7)
            elif is_cold:
                # Cold: shirt + sweater + blazer
                required_categories.append("sweater")
                total_items = random.randint(5, 6)
            else:
                # Moderate/Warm/Hot: shirt + blazer (standard formal)
                total_items = random.randint(4, 5)
            
            base_counts = {
                "min_items": max(4, total_items - 1),
                "max_items": min(7, total_items + 1),
                "required_categories": required_categories
            }
            
        elif 'athletic' in occasion_lower or 'gym' in occasion_lower:
            # Athletic occasions - functional, fewer items, temperature-appropriate
            required_categories = ["top", "bottom", "shoes"]
            
            if is_cold or is_very_cold:
                required_categories.append("outerwear")
                total_items = random.randint(4, 5)
            else:
                total_items = random.randint(3, 4)
            
            base_counts = {
                "min_items": max(3, total_items - 1),
                "max_items": min(5, total_items + 1),
                "required_categories": required_categories
            }
            
        elif 'casual' in occasion_lower or 'weekend' in occasion_lower or 'loungewear' in occasion_lower:
            # Casual occasions - relaxed, temperature-appropriate layering
            required_categories = ["top", "bottom", "shoes"]
            
            if is_very_cold:
                required_categories.extend(["sweater", "outerwear"])
                total_items = random.randint(5, 6)
            elif is_cold:
                required_categories.extend(["sweater", "outerwear"])
                total_items = random.randint(4, 5)
            elif is_moderate:
                required_categories.append("outerwear")
                total_items = random.randint(4, 5)
            else:
                total_items = random.randint(3, 4)
            
            base_counts = {
                "min_items": max(3, total_items - 1),
                "max_items": min(6, total_items + 1),
                "required_categories": required_categories
            }
            
        elif 'party' in occasion_lower or 'date' in occasion_lower:
            # Social occasions - stylish, temperature-appropriate layering
            required_categories = ["top", "bottom", "shoes", "accessory"]
            
            if is_cold or is_very_cold:
                required_categories.append("outerwear")
                total_items = random.randint(5, 6)
            else:
                total_items = random.randint(4, 5)
            
            base_counts = {
                "min_items": max(4, total_items - 1),
                "max_items": min(6, total_items + 1),
                "required_categories": required_categories
            }
            
        else:
            # Default - balanced approach with temperature consideration
            required_categories = ["top", "bottom", "shoes"]
            
            if is_cold or is_very_cold:
                required_categories.append("outerwear")
                total_items = random.randint(4, 5)
            else:
                required_categories.append("accessory")
                total_items = random.randint(3, 4)
            
            base_counts = {
                "min_items": max(3, total_items - 1),
                "max_items": min(5, total_items + 1),
                "required_categories": required_categories
            }
        
        # Style-based adjustments
        if style:
            style_lower = style.lower()
            
            if 'minimalist' in style_lower or 'minimal' in style_lower:
                # Minimalist styles - fewer items, cleaner look
                total_items = max(3, total_items - 1)
                if total_items <= 3:
                    base_counts["required_categories"] = ["top", "bottom", "shoes"]
                    
            elif 'maximalist' in style_lower or 'maximal' in style_lower:
                # Maximalist styles - more items, layered look
                total_items = min(6, total_items + 1)
                if "accessory" not in base_counts["required_categories"]:
                    base_counts["required_categories"].append("accessory")
                    
            elif 'bohemian' in style_lower or 'boho' in style_lower:
                # Bohemian styles - more accessories and layers
                total_items = min(6, total_items + 1)
                if "accessory" not in base_counts["required_categories"]:
                    base_counts["required_categories"].append("accessory")
                    
            elif 'streetwear' in style_lower or 'urban' in style_lower:
                # Streetwear - more accessories, layered look
                total_items = min(6, total_items + 1)
                if "accessory" not in base_counts["required_categories"]:
                    base_counts["required_categories"].append("accessory")
                    
            elif 'classic' in style_lower or 'preppy' in style_lower:
                # Classic styles - structured, moderate items
                total_items = max(4, min(5, total_items))
                
        # Mood-based adjustments
        if mood:
            mood_lower = mood.lower()
            
            if 'bold' in mood_lower or 'dynamic' in mood_lower or 'energetic' in mood_lower:
                # Bold moods - more items, statement pieces
                total_items = min(6, total_items + 1)
                if "accessory" not in base_counts["required_categories"]:
                    base_counts["required_categories"].append("accessory")
                    
            elif 'subtle' in mood_lower or 'serene' in mood_lower:
                # Subtle moods - fewer items, understated
                total_items = max(3, total_items - 1)
                if total_items <= 3:
                    base_counts["required_categories"] = ["top", "bottom", "shoes"]
                    
            elif 'romantic' in mood_lower or 'playful' in mood_lower:
                # Romantic/playful moods - more accessories
                if "accessory" not in base_counts["required_categories"]:
                    base_counts["required_categories"].append("accessory")
        
        # Update min/max based on total_items
        base_counts["min_items"] = max(3, total_items - 1)
        base_counts["max_items"] = min(6, total_items + 1)
        
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
