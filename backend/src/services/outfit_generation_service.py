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
from src.config.firebase import db

logger = logging.getLogger(__name__)

class OutfitGenerationService:
    def __init__(self):
        self.fallback_service = OutfitFallbackService()
    
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
        
        # Select appropriate items based on occasion
        selected_items = self._select_appropriate_items(unique_wardrobe, occasion, style, base_item_id)
        
        print(f"🔍 Selected {len(selected_items)} items for {occasion} occasion")
        for i, item in enumerate(selected_items):
            print(f"  {i+1}. {item.name} ({item.type})")
        
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
                reason="Selected for outfit",
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
            mood=context.get("mood", "casual") or "neutral",  # Ensure mood is not None
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
                "warnings": context.get("warnings", []),
                "errors": context.get("errors", [])
            }
        )

    def _select_appropriate_items(self, wardrobe: List[ClothingItem], occasion: str, style: Optional[str], base_item_id: Optional[str] = None) -> List[ClothingItem]:
        """Select appropriate items based on occasion and style."""
        print(f"🔍 DEBUG: _select_appropriate_items called with base_item_id: {base_item_id}")
        print(f"🔍 DEBUG: Wardrobe size: {len(wardrobe)}")
        selected_items = []
        
        # If base item is specified, prioritize it FIRST (before any filtering)
        base_item = None
        if base_item_id:
            # First, try to find it in the provided wardrobe
            for item in wardrobe:
                if item.id == base_item_id:
                    base_item = item
                    break
            
            # If not found in wardrobe, fetch from database
            if not base_item:
                print(f"🔍 Base item not found in wardrobe, fetching from database: {base_item_id}")
                base_item = self._fetch_item_from_database(base_item_id)
            
            if base_item:
                print(f"🎯 Including base item in selection: {base_item.name} ({base_item.type})")
                selected_items.append(base_item)
            else:
                print(f"⚠️ Base item not found in database: {base_item_id}")
        
        # Now filter items by occasion appropriateness (excluding the base item)
        wardrobe_without_base = [item for item in wardrobe if not base_item_id or item.id != base_item_id]
        filtered_wardrobe = self._filter_items_by_occasion(wardrobe_without_base, occasion)
        
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
            # For loungewear, prefer sweats, hoodies, t-shirts, avoid formal/jeans
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Prefer loungewear items
                if any(lounge in name_lower for lounge in ["sweat", "hoodie", "t-shirt", "jogger", "lounge", "pajama"]):
                    appropriate_items.insert(0, item)  # Prioritize loungewear items
                elif any(formal in name_lower for formal in ["blazer", "suit", "jeans", "oxford", "heels"]):
                    continue  # Skip formal items
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
                if any(casual in name_lower for casual in ["t-shirt", "sweatpants", "sneakers", "athletic", "sport"]):
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
                if any(casual in name_lower for casual in ["t-shirt", "sweatpants", "sneakers", "athletic", "sport", "jeans", "shorts", "bermuda", "casual", "beach"]):
                    continue
                
                # Prefer business items
                if any(business in name_lower for business in ["dress shirt", "dress pants", "blazer", "suit", "oxford", "loafers", "professional"]):
                    appropriate_items.insert(0, item)  # Prioritize business items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "party" in occasion_lower or "night out" in occasion_lower or "club" in occasion_lower:
            # For parties/night out, prefer stylish items and avoid formal/business items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid overly formal items for parties
                if any(formal in name_lower for formal in ["suit", "dress pants", "oxford", "loafers"]):
                    continue
                
                # Prefer stylish/trendy items
                if any(style in name_lower for style in ["designer", "trendy", "stylish", "fashion"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        elif "athletic" in occasion_lower or "gym" in occasion_lower or "workout" in occasion_lower or "sport" in occasion_lower:
            # For athletic activities, prefer athletic items
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Prefer athletic items
                if any(athletic in name_lower for athletic in ["athletic", "sport", "gym", "workout", "sneakers", "track", "jersey"]):
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
            # For dates, prefer stylish items but not overly formal
            appropriate_items = []
            for item in wardrobe:
                name_lower = item.name.lower()
                # Avoid overly casual items for dates
                if any(casual in name_lower for casual in ["sweatpants", "athletic", "gym", "workout"]):
                    continue
                
                # Prefer stylish items
                if any(style in name_lower for style in ["stylish", "designer", "fashion", "trendy"]):
                    appropriate_items.insert(0, item)  # Prioritize stylish items
                else:
                    appropriate_items.append(item)
            
            return appropriate_items
        
        # For other occasions, return all items
        return wardrobe

    def _fetch_item_from_database(self, item_id: str) -> Optional[ClothingItem]:
        """Fetch a wardrobe item from the database by ID."""
        try:
            print(f"🔍 Fetching item from database: {item_id}")
            doc_ref = db.collection('wardrobe').document(item_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"❌ Item not found in database: {item_id}")
                return None
            
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            # Convert to ClothingItem
            clothing_item = ClothingItem(**item_data)
            print(f"✅ Successfully fetched item from database: {clothing_item.name} ({clothing_item.type})")
            return clothing_item
            
        except Exception as e:
            print(f"❌ Error fetching item from database: {e}")
            return None
