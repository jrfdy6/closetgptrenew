#!/usr/bin/env python3
"""
Outfit Generation Service with Integrated Thought Clarification Pipeline
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from src.custom_types.wardrobe import ClothingItem
from src.custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile
from src.services.outfit_fallback_service import OutfitFallbackService
from src.services.outfit_validation_service import OutfitValidationService
from src.services.cohesive_outfit_composition_service import CohesiveOutfitCompositionService
from src.services.outfit_validation_pipeline import validation_pipeline, ValidationContext
from src.config.firebase import db

logger = logging.getLogger(__name__)

class OutfitGenerationService:
    def __init__(self):
        self.fallback_service = OutfitFallbackService()
        self.validation_service = OutfitValidationService()
        self.composition_service = CohesiveOutfitCompositionService()
    
    async def generate_outfit(
        self,
        user_id: str,
        wardrobe: List[ClothingItem],
        occasion: str,
        weather: WeatherData,
        user_profile: UserProfile,
        style: Optional[str] = None,
        mood: Optional[str] = None,
        base_item_id: Optional[str] = None
    ) -> OutfitGeneratedOutfit:
        print("🎯 Starting Integrated Thought Clarification Pipeline")
        
        # Ensure we have unique items by ID
        unique_items = {}
        for item in wardrobe:
            if item.id not in unique_items:
                unique_items[item.id] = item
        
        unique_wardrobe = list(unique_items.values())
        
        # NEW: Use cohesive composition service for harmonious outfit creation
#         print("🎨 Creating cohesive outfit composition...")
        try:
            composition = await self.composition_service.create_cohesive_outfit(
                wardrobe=unique_wardrobe,
                occasion=occasion,
                style=style,
                mood=mood,
                weather=weather,
                user_profile=user_profile,
                max_items=6  # Allow 3-6 items for complete outfits
            )
            
            # Extract items from composition
            selected_items = [composition.base_piece] + composition.complementary_pieces
            
            # print(f"✅ Cohesive composition created:")
#             print(f"  - Base piece: {composition.base_piece.name} ({composition.base_piece.type})")
#             print(f"  - Total items: {composition.total_items}")
#             print(f"  - Color harmony: {composition.color_harmony.value}")
#             print(f"  - Style consistency: {composition.style_consistency:.1f}")
            for i, item in enumerate(composition.complementary_pieces):
#                 print(f"  - Complementary {i+1}: {item.name} ({item.type})")
            
        except Exception as e:
            # print(f"⚠️ Cohesive composition failed: {e}, falling back to traditional selection")
            # Fallback to traditional selection
            selected_items = self._select_appropriate_items(unique_wardrobe, occasion, style, base_item_id)
        
        # NEW: Apply comprehensive validation pipeline
        # print("🔍 Applying comprehensive validation pipeline...")
        
        # Create validation context
        validation_context = ValidationContext(
            occasion=occasion,
            style=style or "casual",
            mood=mood or "neutral",
            weather=weather.__dict__ if hasattr(weather, '__dict__') else weather,
            user_profile=user_profile.__dict__ if hasattr(user_profile, '__dict__') else user_profile,
            temperature=getattr(weather, 'temperature', 70.0) if hasattr(weather, 'temperature') else 70.0
        )
        
        # Create outfit dict for validation
        outfit_dict = {
            "items": [item.__dict__ if hasattr(item, '__dict__') else item for item in selected_items]
        }
        
        try:
            # Run comprehensive validation pipeline
            validation_result = await validation_pipeline.validate_outfit(outfit_dict, validation_context)
            
            if not validation_result.valid:
                # print(f"❌ VALIDATION FAILED: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")
#                 print(f"   Errors: {validation_result.errors}")
#                 print(f"   Warnings: {validation_result.warnings}")
#                 print(f"   Suggestions: {validation_result.suggestions}")
                
                # For now, we'll continue with the outfit but log the issues
                # In the future, we could implement repair logic or regeneration
                # print("⚠️ Continuing with outfit despite validation issues (repair mode not yet implemented)")
            else:
                # print(f"✅ VALIDATION PASSED: {len(validation_result.warnings)} warnings")
                if validation_result.warnings:
#                     print(f"   Warnings: {validation_result.warnings}")
                if validation_result.suggestions:
#                     print(f"   Suggestions: {validation_result.suggestions}")
                
        except Exception as e:
            # print(f"⚠️ Validation pipeline failed: {e}, using original selection")
        
        # LEGACY: Apply enhanced validation to prevent inappropriate combinations
        # print("🔍 Applying legacy enhanced validation...")
        legacy_validation_context = {
            "occasion": occasion,
            "weather": weather,
            "user_profile": user_profile,
            "style": style,
            "mood": mood
        }
        
        try:
            validation_result = await self.validation_service.validate_outfit_with_enhanced_rules(
                selected_items, legacy_validation_context
            )
            
            if validation_result.get("filtered_items"):
                validated_items = validation_result["filtered_items"]
                # print(f"✅ Legacy validation applied: {len(selected_items)} → {len(validated_items)} items")
                if validation_result.get("errors"):
                    # print(f"⚠️ Legacy validation errors: {validation_result['errors']}")
                if validation_result.get("warnings"):
                    # print(f"⚠️ Legacy validation warnings: {validation_result['warnings']}")
                selected_items = validated_items
            else:
                # print("⚠️ Legacy validation returned no filtered items, using original selection")
                
        except Exception as e:
            # print(f"⚠️ Legacy validation failed: {e}, using original selection")
        
        return await self._create_outfit_from_items(
            items=selected_items,
            occasion=occasion,
            weather=weather,
            user_profile=user_profile,
            style=style,
            context={"mood": mood}
        )

    async def _create_outfit_from_items(
        self,
        items: List[ClothingItem],
        occasion: str,
        weather: WeatherData,
        user_profile: UserProfile,
        style: Optional[str],
        context: Dict[str, Any]
    ) -> OutfitGeneratedOutfit:
        # Convert to outfit pieces
        outfit_pieces = []
        for item in items:
            outfit_piece = OutfitPiece(
                itemId=item.id,
                name=item.name,
                type=item.type,
                reason=generate_piece_reasoning(item, occasion, style),
                dominantColors=[color.name for color in (item.dominantColors or [])],
                style=item.style or [],
                occasion=item.occasion or [],
                imageUrl=item.imageUrl or ""
            )
            outfit_pieces.append(outfit_piece)
        # Create outfit description
        description = f"A {style or 'casual'} outfit for {occasion}"
        return OutfitGeneratedOutfit(
            id=f"outfit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{occasion.title()} Outfit",
            description=description,
            items=[item.id for item in items],  # Add required items field
            occasion=occasion,
            mood=(context.get("mood", "casual") if context else "casual") or "neutral",  # Ensure mood is not None
            style=style or "casual",
            pieces=outfit_pieces,
            explanation="Generated using integrated thought clarification pipeline",
            styleTags=[],
            colorHarmony="neutral",
            styleNotes="",
            season="all",
            createdAt=int(datetime.now().timestamp()),
            updatedAt=int(datetime.now().timestamp()),
            metadata={
                "used_favorites": [],
                "warnings": (context.get("warnings", []) if context else []),
                "errors": (context.get("errors", []) if context else [])
            }
        )

    def _select_appropriate_items(self, wardrobe: List[ClothingItem], occasion: str, style: Optional[str], base_item_id: Optional[str] = None) -> List[ClothingItem]:
        """TEMPORARILY SIMPLIFIED: Select appropriate items based on occasion and style."""
        # print(f"🔍 DEBUG: _select_appropriate_items called with base_item_id: {base_item_id}")
        # print(f"🔍 DEBUG: Wardrobe size: {len(wardrobe)}")
        
        # TEMPORARILY SIMPLIFIED: Just return first 4 items for debugging
        try:
            if base_item_id:
                # Find base item first
                base_item = None
                for item in wardrobe:
                    if item.id == base_item_id:
                        base_item = item
                        break
                
                if base_item:
#                     print(f"🎯 Including base item: {base_item.name} ({base_item.type})")
                    # Add base item + 3 more items
                    remaining_items = [item for item in wardrobe if item.id != base_item_id]
                    selected_items = [base_item] + remaining_items[:3]
                else:
                    # print(f"⚠️ Base item not found, using first 4 items")
                    selected_items = wardrobe[:4]
            else:
                selected_items = wardrobe[:4]
            
            # print(f"✅ Selected {len(selected_items)} items for debugging")
            return selected_items
            
        except Exception as e:
            # print(f"⚠️ Selection failed: {e}, using emergency fallback")
            return wardrobe[:4] if wardrobe else []
        
        # Add comprehensive handling for all dropdown occasions
        occasion_lower = occasion.lower()
        if "interview" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "school" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "beach" in occasion_lower:
            priorities = ["shirt", "shorts", "sandals", "accessory"]
        elif "airport" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket"]
        elif "loungewear" in occasion_lower:
            priorities = ["shirt", "pants", "shoes"]
        elif "brunch" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "cocktail" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "festival" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "concert" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket"]
        elif "errands" in occasion_lower:
            priorities = ["shirt", "pants", "shoes"]
        elif "museum" in occasion_lower or "gallery" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "first date" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "fashion event" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "outdoor gathering" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket"]
        elif "gala" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "holiday" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "rainy day" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "snow day" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif "hot weather" in occasion_lower:
            priorities = ["shirt", "shorts", "sandals", "accessory"]
        elif "cold weather" in occasion_lower or "chilly evening" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "jacket", "accessory"]
        elif occasion_lower == "formal":
            priorities = ["shirt", "pants", "shoes", "accessory", "jacket"]
        elif occasion_lower == "casual":
            priorities = ["shirt", "pants", "shoes"]
        elif occasion_lower == "athletic":
            priorities = ["shirt", "pants", "shoes"]
        elif "funeral" in occasion_lower or "memorial" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "business" in occasion_lower or "work" in occasion_lower or "office" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "party" in occasion_lower or "night out" in occasion_lower or "club" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "formal" in occasion_lower or "black tie" in occasion_lower or "wedding" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory", "jacket"]
        elif "vacation" in occasion_lower or "travel" in occasion_lower or "holiday" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "date" in occasion_lower or "romantic" in occasion_lower:
            priorities = ["shirt", "pants", "shoes", "accessory"]
        elif "casual" in occasion_lower or "everyday" in occasion_lower:
            priorities = ["shirt", "pants", "shoes"]
        else:
            priorities = ["shirt", "pants", "shoes"]
        
        # Group items by type
        items_by_type = {}
        for item in filtered_wardrobe:
            # Normalize item type for consistent categorization
            normalized_type = self._normalize_item_type(item.type, item.name)
            if normalized_type not in items_by_type:
                items_by_type[normalized_type] = []
            items_by_type[normalized_type].append(item)
        
        # Select items based on priorities
        used_types = set()
        for priority_type in priorities:
            # Map priority types to normalized types for better matching
            normalized_priority = self._normalize_item_type(priority_type, priority_type)
            
            if normalized_priority in items_by_type and normalized_priority not in used_types:
                # Get the first available item of this type
                available_items = items_by_type[normalized_priority]
                if available_items:
                    selected_items.append(available_items[0])
                    used_types.add(normalized_priority)
                    # Remove this item from available items
                    items_by_type[normalized_priority] = available_items[1:]
            elif priority_type in items_by_type and priority_type not in used_types:
                # Fallback to original priority type if normalized version not found
                available_items = items_by_type[priority_type]
                if available_items:
                    selected_items.append(available_items[0])
                    used_types.add(priority_type)
                    # Remove this item from available items
                    items_by_type[priority_type] = available_items[1:]
        
        # If we still don't have essential items, try to find alternatives
        essential_types = ["shirt", "pants", "shoes"]
        for essential_type in essential_types:
            if essential_type not in used_types:
                # Look for any item that could serve this purpose
                for item_type, items in items_by_type.items():
                    if items and len(selected_items) < 5:
                        # Check if this item type could serve the essential purpose
                        if (essential_type == "shoes" and "shoe" in item_type) or \
                           (essential_type == "shirt" and "shirt" in item_type) or \
                           (essential_type == "pants" and "pants" in item_type):
                            selected_items.append(items[0])
                            used_types.add(item_type)
                            items_by_type[item_type] = items[1:]
                            break
        
        # If we don't have enough items, add more from any available type
        # But prioritize different types to avoid duplicates and ensure essential items
        if len(selected_items) < 3:
            # First, ensure we have essential items (shirt, pants, shoes)
            essential_types = ["shirt", "pants", "shoes"]
            for essential_type in essential_types:
                if essential_type not in used_types and essential_type in items_by_type:
                    available_items = items_by_type[essential_type]
                    if available_items and len(selected_items) < 5:
                        selected_items.append(available_items[0])
                        used_types.add(essential_type)
            
            # Then add other items if we still need more, but avoid duplicates
            for item_type, items in items_by_type.items():
                if items and len(selected_items) < 5 and item_type not in used_types:
                    selected_items.append(items[0])
                    used_types.add(item_type)
                    break  # Only add one additional item to avoid too many of same type
        
        return selected_items[:5]  # Limit to 5 items

    def _normalize_item_type(self, item_type: str, item_name: str) -> str:
        """Normalize item types for consistent categorization."""
        type_lower = item_type.lower()
        name_lower = item_name.lower()
        
        # Normalize footwear types
        if any(footwear in type_lower or footwear in name_lower for footwear in [
            "shoes", "sneakers", "boots", "sandals", "flats", "heels", "oxford", "loafers", 
            "toe shoes", "footwear", "foot wear"
        ]):
            return "shoes"
        
        # Normalize top types
        if any(top in type_lower or top in name_lower for top in [
            "shirt", "t-shirt", "tshirt", "blouse", "sweater", "hoodie", "jacket", "coat",
            "top", "upper", "shirt"
        ]):
            return "shirt"
        
        # Normalize bottom types
        if any(bottom in type_lower or bottom in name_lower for bottom in [
            "pants", "trousers", "jeans", "shorts", "skirt", "leggings", "tracksuit",
            "bottom", "lower", "pants"
        ]):
            return "pants"
        
        # Normalize accessory types
        if any(accessory in type_lower or accessory in name_lower for accessory in [
            "belt", "watch", "jewelry", "necklace", "bracelet", "ring", "earrings",
            "accessory", "accessories", "belt"
        ]):
            return "accessory"
        
        # Normalize outerwear types
        if any(outerwear in type_lower or outerwear in name_lower for outerwear in [
            "jacket", "coat", "blazer", "suit jacket", "cardigan", "sweater",
            "outerwear", "jacket"
        ]):
            return "jacket"
        
        # Return original type if no normalization applies
        return type_lower

    def _is_layering_item(self, item: ClothingItem) -> bool:
        """Check if an item is a layering item (can be worn over other items)."""
        layering_types = [
            'sweater', 'cardigan', 'hoodie', 'jacket', 'blazer', 'coat', 'vest'
        ]
        return any(layer_type in item.type.lower() for layer_type in layering_types)

    def _get_item_category(self, item: ClothingItem) -> str:
        """Get the broad category of an item."""
        item_type = item.type.lower()
        
        if any(top in item_type for top in ['shirt', 'blouse', 't-shirt', 'sweater', 'hoodie']):
            return "top"
        elif any(bottom in item_type for bottom in ['pants', 'jeans', 'shorts', 'skirt']):
            return "bottom"
        elif any(shoe in item_type for shoe in ['shoes', 'sneakers', 'boots', 'sandals']):
            return "shoes"
        elif any(outer in item_type for outer in ['jacket', 'blazer', 'coat']):
            return "outerwear"
        else:
            return "accessory"

    def _filter_items_by_occasion(self, wardrobe: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Filter items based on occasion appropriateness."""
        occasion_lower = occasion.lower()
        
        if "interview" in occasion_lower:
            # For interviews, prefer professional items and avoid casual/athletic items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid casual/athletic items for interviews
                if any(casual in name_lower for casual in ["t-shirt", "sweatpants", "sneakers", "athletic", "sport", "shorts", "sandals", "hoodie", "graphic"]):
                    continue
                
                # Prefer professional items
                if any(professional in name_lower for professional in ["dress shirt", "dress pants", "blazer", "suit", "oxford", "loafers", "heels"]):
                    appropriate_items.insert(0, item)  # Prioritize professional items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "school" in occasion_lower:
            # For school, avoid revealing, overly casual, or formal items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for school
                if any(inappropriate in name_lower for inappropriate in ["swim", "beach", "gown", "tux", "crop", "tank", "sweatpants", "revealing", "dress pants", "dress shirt", "formal", "suit"]):
                    continue
                
                # Prefer appropriate school items
                if any(school in name_lower for school in ["polo", "button-down", "khakis", "jeans", "sneakers", "casual"]):
                    appropriate_items.insert(0, item)  # Prioritize school-appropriate items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "beach" in occasion_lower:
            # For beach, prefer swimwear, shorts, sandals, avoid formal/business
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Prefer beach-appropriate items
                if any(beach in name_lower for beach in ["swim", "shorts", "sandals", "flip flop", "tank", "coverup", "beach"]):
                    appropriate_items.insert(0, item)  # Prioritize beach items
                elif any(formal in name_lower for formal in ["blazer", "suit", "oxford", "heels", "dress pants"]):
                    continue  # Skip formal items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "airport" in occasion_lower:
            # For airport, prefer comfort, avoid formal, avoid uncomfortable items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for airport
                if any(inappropriate in name_lower for inappropriate in ["swim", "beach", "gown", "tux", "heels", "dress pants", "formal", "suit"]):
                    continue
                
                # Prefer comfortable airport items
                if any(comfortable in name_lower for comfortable in ["comfortable", "travel", "lightweight", "stretchy", "casual", "jeans", "sneakers"]):
                    appropriate_items.insert(0, item)  # Prioritize comfortable items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "loungewear" in occasion_lower:
            # For loungewear, prefer comfortable items and avoid inappropriate items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for loungewear
                if any(inappropriate in name_lower for inappropriate in [
                    "blazer", "suit", "dress pants", "oxford", "heels", "loafers",  # Too formal
                    "athletic", "gym", "jersey", "basketball", "sport",  # Too athletic
                    "work", "business", "professional",  # Too work-like
                    "jeans", "denim"  # Too structured
                ]):
                    continue
                
                # Prefer loungewear items
                if any(lounge in name_lower for lounge in ["sweat", "hoodie", "t-shirt", "jogger", "lounge", "pajama", "comfortable", "soft"]):
                    appropriate_items.insert(0, item)  # Prioritize loungewear items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "brunch" in occasion_lower:
            # For brunch, prefer smart casual, avoid athletic, avoid swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for brunch
                if any(inappropriate in name_lower for inappropriate in ["swim", "athletic", "gym", "sweatpants"]):
                    continue
                
                # Prefer smart casual items
                if any(smart_casual in name_lower for smart_casual in ["blouse", "button-down", "khakis", "loafers", "cardigan"]):
                    appropriate_items.insert(0, item)  # Prioritize smart casual items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "cocktail" in occasion_lower:
            # For cocktail, prefer semi-formal, avoid shorts, t-shirts, sneakers
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid casual items for cocktail
                if any(casual in name_lower for casual in ["shorts", "t-shirt", "sneaker", "sandals", "swim", "hoodie"]):
                    continue
                
                # Prefer semi-formal items
                if any(semi_formal in name_lower for semi_formal in ["dress", "blouse", "dress pants", "heels", "blazer"]):
                    appropriate_items.insert(0, item)  # Prioritize semi-formal items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "festival" in occasion_lower:
            # For festival, allow expressive, avoid formal, business
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid formal items for festival
                if any(formal in name_lower for formal in ["blazer", "suit", "oxford", "heels", "dress pants"]):
                    continue
                
                # Prefer expressive items
                if any(expressive in name_lower for expressive in ["colorful", "pattern", "trendy", "stylish"]):
                    appropriate_items.insert(0, item)  # Prioritize expressive items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "concert" in occasion_lower:
            # For concert, allow expressive, avoid formal, business
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid formal items for concert
                if any(formal in name_lower for formal in ["blazer", "suit", "oxford", "heels", "dress pants"]):
                    continue
                
                # Prefer expressive items
                if any(expressive in name_lower for expressive in ["colorful", "pattern", "trendy", "stylish"]):
                    appropriate_items.insert(0, item)  # Prioritize expressive items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "errands" in occasion_lower:
            # For errands, prefer comfort, avoid formal
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid formal items for errands
                if any(formal in name_lower for formal in ["blazer", "suit", "oxford", "heels", "dress pants"]):
                    continue
                
                # Prefer comfortable items
                if any(comfortable in name_lower for comfortable in ["comfortable", "casual", "jeans", "sneakers"]):
                    appropriate_items.insert(0, item)  # Prioritize comfortable items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "museum" in occasion_lower or "gallery" in occasion_lower:
            # For museum/gallery, prefer smart casual, avoid athletic, swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for museum/gallery
                if any(inappropriate in name_lower for inappropriate in ["swim", "athletic", "gym", "sweatpants"]):
                    continue
                
                # Prefer smart casual items
                if any(smart_casual in name_lower for smart_casual in ["blouse", "button-down", "khakis", "loafers", "cardigan"]):
                    appropriate_items.insert(0, item)  # Prioritize smart casual items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "first date" in occasion_lower:
            # For first date, avoid overly casual, avoid athletic, avoid swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for first date
                if any(inappropriate in name_lower for inappropriate in ["swim", "athletic", "gym", "sweatpants"]):
                    continue
                
                # Prefer stylish items
                if any(stylish in name_lower for stylish in ["stylish", "designer", "fashion", "trendy", "blouse", "dress"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "fashion event" in occasion_lower:
            # For fashion event, prefer stylish, avoid athletic, swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for fashion event
                if any(inappropriate in name_lower for inappropriate in ["swim", "athletic", "gym", "sweatpants"]):
                    continue
                
                # Prefer stylish items
                if any(stylish in name_lower for stylish in ["stylish", "designer", "fashion", "trendy", "couture"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "outdoor gathering" in occasion_lower:
            # For outdoor gathering, prefer comfort, avoid formal
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid formal items for outdoor gathering
                if any(formal in name_lower for formal in ["blazer", "suit", "oxford", "heels", "dress pants"]):
                    continue
                
                # Prefer comfortable items
                if any(comfortable in name_lower for comfortable in ["comfortable", "casual", "jeans", "sneakers"]):
                    appropriate_items.insert(0, item)  # Prioritize comfortable items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "gala" in occasion_lower:
            # For gala, prefer very formal, avoid casual, shorts, t-shirts
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid casual items for gala
                if any(casual in name_lower for casual in ["shorts", "t-shirt", "sneaker", "sandals", "swim", "hoodie", "jeans"]):
                    continue
                
                # Prefer formal items
                if any(formal in name_lower for formal in ["suit", "dress", "blazer", "dress shirt", "dress pants", "heels", "oxford"]):
                    appropriate_items.insert(0, item)  # Prioritize formal items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "rainy day" in occasion_lower:
            # For rainy day, prefer waterproof, avoid sandals, swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for rainy day
                if any(inappropriate in name_lower for inappropriate in ["sandals", "flip flop", "swim"]):
                    continue
                
                # Prefer waterproof items
                if any(waterproof in name_lower for waterproof in ["waterproof", "rain", "boots", "jacket"]):
                    appropriate_items.insert(0, item)  # Prioritize waterproof items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "snow day" in occasion_lower:
            # For snow day, prefer warm, avoid sandals, swimwear
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for snow day
                if any(inappropriate in name_lower for inappropriate in ["sandals", "flip flop", "swim"]):
                    continue
                
                # Prefer warm items
                if any(warm in name_lower for warm in ["warm", "winter", "coat", "sweater", "boots"]):
                    appropriate_items.insert(0, item)  # Prioritize warm items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "hot weather" in occasion_lower:
            # For hot weather, prefer shorts, avoid jackets, sweaters
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid warm items for hot weather
                if any(warm in name_lower for warm in ["jacket", "coat", "sweater", "winter"]):
                    continue
                
                # Prefer cool items
                if any(cool in name_lower for cool in ["shorts", "sandals", "tank", "lightweight", "breathable"]):
                    appropriate_items.insert(0, item)  # Prioritize cool items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "cold weather" in occasion_lower or "chilly evening" in occasion_lower:
            # For cold weather, prefer warm, avoid shorts, sandals
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid cool items for cold weather
                if any(cool in name_lower for cool in ["shorts", "sandals", "flip flop", "swim"]):
                    continue
                
                # Prefer warm items
                if any(warm in name_lower for warm in ["warm", "winter", "coat", "sweater", "boots"]):
                    appropriate_items.insert(0, item)  # Prioritize warm items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "funeral" in occasion_lower or "memorial" in occasion_lower:
            # For funerals, prefer dark, solid colors and avoid bright/patterned items
            appropriate_items = []
            for item in wardrobe:
                # Check if item has inappropriate patterns or colors
                name_lower = item.name.lower()
                if any(pattern in name_lower for pattern in ["floral", "bright", "colorful", "neon"]):
                    continue  # Skip inappropriate items
                
                # Prefer dark colors for funerals
                if any(color in name_lower for color in ["black", "navy", "dark", "gray", "charcoal"]):
                    appropriate_items.insert(0, item)  # Prioritize dark items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "formal" in occasion_lower or "black tie" in occasion_lower or "wedding" in occasion_lower:
            # For formal events, prefer dressy items and avoid casual items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid casual items for formal events
                if any(casual in name_lower for casual in ["t-shirt", "sweatpants", "sneakers", "athletic", "sport", "jersey", "basketball", "tank", "slides", "sandals", "flip"]):
                    continue
                
                # Prefer formal items
                if any(formal in name_lower for formal in ["suit", "dress", "blazer", "dress shirt", "dress pants", "heels", "oxford"]):
                    appropriate_items.insert(0, item)  # Prioritize formal items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "business" in occasion_lower or "work" in occasion_lower or "office" in occasion_lower:
            # For business/work, prefer professional items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid casual/athletic items for business
                if any(casual in name_lower for casual in ["t-shirt", "sweatpants", "sneakers", "athletic", "sport", "jeans", "shorts", "bermuda", "casual", "beach", "jersey", "basketball", "tank", "slides", "sandals", "flip"]):
                    continue
                
                # Prefer business items
                if any(business in name_lower for business in ["dress shirt", "dress pants", "blazer", "suit", "oxford", "loafers", "professional"]):
                    appropriate_items.insert(0, item)  # Prioritize business items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "party" in occasion_lower or "night out" in occasion_lower or "club" in occasion_lower:
            # For parties/night out, prefer stylish items and avoid inappropriate items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for parties
                if any(inappropriate in name_lower for inappropriate in [
                    "suit", "dress pants", "oxford", "loafers",  # Too formal
                    "athletic", "gym", "jersey", "basketball", "sport",  # Too athletic
                    "sweatpants", "joggers", "lounge", "pajama",  # Too casual
                    "work", "business", "professional"  # Too work-like
                ]):
                    continue
                
                # Prefer stylish/trendy items
                if any(style in name_lower for style in ["designer", "trendy", "stylish", "fashion", "party", "evening"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "athletic" in occasion_lower or "gym" in occasion_lower or "workout" in occasion_lower or "sport" in occasion_lower:
            # For athletic activities, prefer athletic items and block formal items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                item_type = item.type.lower()
                
                # CRITICAL: Block formal/structured items for athletic occasions
                gym_blocks = [
                    'blazer', 'suit', 'dress pants', 'dress shirt', 'oxford', 'loafers', 'heels',
                    'formal', 'business', 'professional', 'dress', 'suit jacket', 'sport coat',
                    'button up', 'button-up', 'button down', 'button-down',
                    'polo', 'henley', 'collar', 'rugby shirt',
                    'chinos', 'khaki', 'trouser', 'cargo', 'jeans', 'denim',
                    'dockers', 'slim fit pants', 'casual shorts', 'bermuda',
                    'slide', 'slides', 'sandal', 'sandals', 'flip-flop', 'flip flop'
                ]
                
                if any(formal in name_lower or formal in item_type for formal in gym_blocks):
                    continue
                
                # Prefer athletic items
                if any(athletic in name_lower for athletic in ["athletic", "sport", "gym", "workout", "sneakers", "track", "jersey", "tank", "shorts", "jogger"]):
                    appropriate_items.insert(0, item)  # Prioritize athletic items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "casual" in occasion_lower or "everyday" in occasion_lower:
            # For casual events, prefer comfortable items and avoid overly formal items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid overly formal items for casual
                if any(formal in name_lower for formal in ["suit", "dress pants", "heels", "oxford"]):
                    continue
                
                # Prefer casual items
                if any(casual in name_lower for casual in ["t-shirt", "jeans", "sneakers", "casual", "comfortable"]):
                    appropriate_items.insert(0, item)  # Prioritize casual items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "vacation" in occasion_lower or "travel" in occasion_lower or "holiday" in occasion_lower:
            # For vacation/travel, prefer comfortable and versatile items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid overly formal items for vacation
                if any(formal in name_lower for formal in ["suit", "dress pants", "heels"]):
                    continue
                
                # Prefer comfortable and versatile items
                if any(comfortable in name_lower for comfortable in ["comfortable", "versatile", "travel", "lightweight"]):
                    appropriate_items.insert(0, item)  # Prioritize comfortable items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "date" in occasion_lower or "romantic" in occasion_lower:
            # For dates, prefer stylish items but avoid inappropriate items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for dates
                if any(inappropriate in name_lower for inappropriate in [
                    "sweatpants", "athletic", "gym", "workout", "jersey", "basketball", "sport",  # Too athletic
                    "lounge", "pajama", "sleep",  # Too casual
                    "work", "business", "professional",  # Too work-like
                    "swim", "beach", "bikini"  # Too beachy
                ]):
                    continue
                
                # Prefer stylish/romantic items
                if any(style in name_lower for style in ["stylish", "designer", "fashion", "trendy", "romantic", "elegant", "sophisticated"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "weekend" in occasion_lower:
            # For weekend, prefer casual items but avoid inappropriate items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid inappropriate items for weekend
                if any(inappropriate in name_lower for inappropriate in [
                    "suit", "dress pants", "oxford", "loafers", "heels",  # Too formal
                    "athletic", "gym", "jersey", "basketball", "sport",  # Too athletic (unless specified)
                    "work", "business", "professional"  # Too work-like
                ]):
                    continue
                
                # Prefer casual/comfortable items
                if any(casual in name_lower for casual in ["casual", "comfortable", "relaxed", "weekend", "jeans", "sneakers", "t-shirt"]):
                    appropriate_items.insert(0, item)  # Prioritize casual items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        # For other occasions, return all items
        return wardrobe

    def _fetch_item_from_database(self, item_id: str) -> Optional[ClothingItem]:
        """Fetch a wardrobe item from the database by ID."""
        try:
            # print(f"🔍 Fetching item from database: {item_id}")
            doc_ref = db.collection('wardrobe').document(item_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                # print(f"❌ Item not found in database: {item_id}")
                return None
            
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            # Convert to ClothingItem
            clothing_item = ClothingItem(**item_data)
            # print(f"✅ Successfully fetched item from database: {clothing_item.name} ({clothing_item.type})")
            return clothing_item
            
        except Exception as e:
            # print(f"❌ Error fetching item from database: {e}")
            return None

def generate_piece_reasoning(item: ClothingItem, occasion: str, style: str) -> str:
    """Generate intelligent reasoning for why each piece was selected."""
    try:
        item_type = item.type.lower() if hasattr(item.type, 'value') else str(item.type).lower()
        item_name = item.name.lower()
        
        # Occasion-specific reasoning
        if occasion.lower() == 'formal':
            if 'blazer' in item_type or 'blazer' in item_name:
                return "Essential for formal occasions - adds structure and professionalism"
            elif 'dress' in item_type or 'dress' in item_name:
                return "Perfect one-piece solution for formal events"
            elif 'heels' in item_type or 'heels' in item_name:
                return "Elevates the entire look for formal settings"
        
        elif occasion.lower() == 'casual':
            if 'jean' in item_type or 'jean' in item_name:
                return "Classic casual staple - comfortable and versatile"
            elif 'sneaker' in item_type or 'sneaker' in item_name:
                return "Perfect for casual comfort and everyday wear"
            elif 't-shirt' in item_type or 't-shirt' in item_name:
                return "Essential casual piece - relaxed and easy to wear"
        
        elif occasion.lower() == 'business':
            if 'blazer' in item_type or 'blazer' in item_name:
                return "Professional touch for business settings"
            elif 'dress' in item_type or 'dress' in item_name:
                return "Polished and professional for business occasions"
            elif 'pants' in item_type or 'pants' in item_name:
                return "Structured bottom for professional appearance"
        
        # Style-specific reasoning
        if style and style.lower() == 'minimalist':
            return "Clean, simple design that fits minimalist aesthetic"
        elif style and style.lower() == 'bohemian':
            return "Free-spirited piece that embodies boho style"
        elif style and style.lower() == 'athletic':
            return "Performance-focused design for active lifestyle"
        
        # General reasoning based on item type
        if 'blazer' in item_type or 'blazer' in item_name:
            return "Adds sophistication and structure to the outfit"
        elif 'dress' in item_type or 'dress' in item_name:
            return "Versatile one-piece that works for many occasions"
        elif 'jean' in item_type or 'jean' in item_name:
            return "Timeless denim piece - comfortable and stylish"
        elif 'sneaker' in item_type or 'sneaker' in item_name:
            return "Comfortable footwear for all-day wear"
        elif 'heels' in item_type or 'heels' in item_name:
            return "Elevates the look and adds elegance"
        else:
            return f"Selected to complete the {occasion} look"
            
    except Exception as e:
        return f"Selected for {occasion} occasion"
