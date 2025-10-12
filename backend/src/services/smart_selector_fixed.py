from typing import List, Dict, Any
from ..custom_types.wardrobe import ClothingItem
from .outfit_fallback_service import OutfitFallbackService

# --- Scoring logic ---
def calculate_style_score(item: ClothingItem, context: Dict[str, Any]) -> float:
    base_score = 1.0
    occasion = (context.get("occasion", "") if context else "").lower()
    if occasion and hasattr(item, 'occasion'):
        if occasion in [occ.lower() for occ in getattr(item, 'occasion', [])]:
            base_score += 0.3
    style = (context.get("style", "") if context else "")
    if style and hasattr(item, 'style'):
        style_lower = style.lower() if style else ""
        if style_lower in [s.lower() for s in getattr(item, 'style', [])]:
            base_score += 0.2
    weather = (context.get("weather", {}) if context else {})
    if hasattr(weather, 'temperature'):
        temperature = weather.temperature
    else:
        temperature = (weather.get("temperature", 70) if weather else 70)
    if isinstance(temperature, str):
        try:
            temperature = float(temperature)
        except (ValueError, TypeError):
            temperature = 70.0
    if hasattr(item, 'season'):
        if temperature < 60 and 'winter' in getattr(item, 'season', []):
            base_score += 0.2
        elif 60 <= temperature <= 80 and 'spring' in getattr(item, 'season', []):
            base_score += 0.2
        elif temperature > 80 and 'summer' in getattr(item, 'season', []):
            base_score += 0.2
    if hasattr(item, 'quality_score'):
        base_score += getattr(item, 'quality_score', 0) * 0.1
    return base_score

async def get_favorite_item_ids(user_id: str) -> set:
    try:
        fallback_service = OutfitFallbackService()
        favorite_items = await fallback_service._query_favorite_items(user_id)
        return {item.id for item in favorite_items}
    except Exception as e:
        # print(f"⚠️ Warning: Could not fetch favorite items: {e}")
        return set()

def score_items(items: List[ClothingItem], context: Dict[str, Any]) -> List[dict]:
    user_id = (context.get("user_id") if context else None)
    favorite_ids = set()
    if user_id:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                favorite_ids = set()  # Will be populated in async version
            else:
                favorite_ids = loop.run_until_complete(get_favorite_item_ids(user_id))
        except Exception as e:
            # print(f"⚠️ Warning: Could not get favorite items: {e}")
            favorite_ids = set()
    scored = []
    for item in items:
        base_score = calculate_style_score(item, context)
        if hasattr(item, 'id') and item.id in favorite_ids:
            base_score += 0.3
#             print(f"⭐ Favorite item boosted: {getattr(item, 'name', str(item))} (score: {base_score:.2f})")
        scored.append({"item": item, "score": base_score})
    return scored

async def score_items_async(items: List[ClothingItem], context: Dict[str, Any]) -> List[dict]:
    user_id = (context.get("user_id") if context else None)
    favorite_ids = set()
    if user_id:
        favorite_ids = await get_favorite_item_ids(user_id)
    scored = []
    for item in items:
        base_score = calculate_style_score(item, context)
        if hasattr(item, 'id') and item.id in favorite_ids:
            base_score += 0.3
#             print(f"⭐ Favorite item boosted: {getattr(item, 'name', str(item))} (score: {base_score:.2f})")
        scored.append({"item": item, "score": base_score})
    return scored

def normalize_item_type(item: ClothingItem) -> str:
    """Normalize item types to prevent duplicates."""
    type_lower = item.type.lower()
    name_lower = item.name.lower()
    
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
        "bottom", "lower", "pants", "pleated skirt"
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

def filter_by_occasion_appropriateness(items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
    """Filter items based on occasion appropriateness."""
    occasion_lower = occasion.lower()
    filtered_items = []
    
    for item in items:
        item_name_lower = item.name.lower()
        item_type_lower = item.type.lower()
        
        # Skip inappropriate items for specific occasions
        if "work" in occasion_lower or "business" in occasion_lower or "office" in occasion_lower:
            if "shorts" in item_name_lower or "shorts" in item_type_lower:
                continue  # Skip shorts for work
            if "athletic" in item_name_lower or "gym" in item_name_lower:
                continue  # Skip athletic items for work
        
        elif "athletic" in occasion_lower or "gym" in occasion_lower:
            # Block formal/structured items for gym/athletic
            gym_blocks = ['dress', 'formal', 'blazer', 'suit', 'oxford', 'loafer', 
                         'button up', 'button-up', 'button down', 'button-down',
                         'polo', 'henley', 'collar', 'slide', 'sandal', 'flip-flop',
                         'chinos', 'khaki', 'trouser', 'cargo', 'jeans', 'denim']
            if any(block in item_name_lower or block in item_type_lower for block in gym_blocks):
                continue  # Skip formal/structured items for athletic
        
        elif "airport" in occasion_lower:
            if "dress" in item_name_lower or "formal" in item_name_lower:
                continue  # Skip formal items for airport
        
        elif "gala" in occasion_lower:
            if "shorts" in item_name_lower or "casual" in item_name_lower:
                continue  # Skip casual items for gala
        
        elif "errands" in occasion_lower:
            if "dress" in item_name_lower or "formal" in item_name_lower:
                continue  # Skip formal items for errands
        
        elif "brunch" in occasion_lower:
            if "dress" in item_name_lower or "formal" in item_name_lower:
                continue  # Skip formal items for brunch
        
        # If item passes all filters, include it
        filtered_items.append(item)
    
    return filtered_items

def pick_top_ranked_items_no_duplicates(scored: List[dict], target_count: int = 5) -> List[ClothingItem]:
    """Select top ranked items ensuring no duplicates by type."""
    sorted_items = sorted(scored, key=lambda x: x["score"], reverse=True)
    
    selected_items = []
    used_types = set()
    
    for entry in sorted_items:
        item = entry["item"]
        normalized_type = normalize_item_type(item)
        
        # Only add item if we haven't used this type yet
        if normalized_type not in used_types:
            selected_items.append(item)
            used_types.add(normalized_type)
            
            # Stop if we have enough items
            if len(selected_items) >= target_count:
                break
    
    return selected_items

def ensure_essential_items(selected_items: List[ClothingItem], all_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
    """Ensure we have essential items (shirt, pants, shoes)."""
    essential_types = ["shirt", "pants", "shoes"]
    used_types = {normalize_item_type(item) for item in selected_items}
    
    # Check what essentials we're missing
    missing_essentials = []
    for essential_type in essential_types:
        if essential_type not in used_types:
            missing_essentials.append(essential_type)
    
    # If we're missing essentials, try to add them
    if missing_essentials:
        # Score all remaining items
        remaining_items = [item for item in all_items if item not in selected_items]
        scored_remaining = []
        for item in remaining_items:
            score = calculate_style_score(item, context)
            scored_remaining.append({"item": item, "score": score})
        
        # Sort by score
        scored_remaining.sort(key=lambda x: x["score"], reverse=True)
        
        # Try to add missing essentials
        for entry in scored_remaining:
            item = entry["item"]
            normalized_type = normalize_item_type(item)
            
            if normalized_type in missing_essentials:
                selected_items.append(item)
                missing_essentials.remove(normalized_type)
                
                if not missing_essentials:
                    break
    
    return selected_items

async def select_items_fixed(filtered_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
    """Fixed version of select_items that prevents duplicates and ensures essentials."""
#     print(f"🎯 Smart selection (FIXED): Processing {len(filtered_items)} items")
    
    # Step 1: Filter by occasion appropriateness
    filtered_items = filter_by_occasion_appropriateness(filtered_items, (context.get("occasion", "") if context else ""))
#     print(f"🎯 After occasion filtering: {len(filtered_items)} items")
    
    # Step 2: Check if there's a base item that should be included
    base_item = (context.get("base_item") if context else None)
    base_item_included = False
    
    if base_item:
#         print(f"🎯 Base item specified: {base_item.name}")
        # Check if base item is in filtered items
        base_item_in_filtered = any(item.id == base_item.id for item in filtered_items)
        if base_item_in_filtered:
            # print(f"✅ Base item found in filtered items")
            base_item_included = True
        else:
            # print(f"⚠️ Base item not found in filtered items, will try to include it")
    
    # Step 3: Score items
    scored = await score_items_async(filtered_items, context)
    target_counts = (context.get("target_counts", {}) if context else {})
    target_count = (target_counts.get("target_items", 5) if target_counts else 5)
    
    # Step 4: If we have a base item, ensure it's included
    if base_item and not base_item_included:
        # Add base item to scored items with high score
        base_item_score = {"item": base_item, "score": 10.0}  # Very high score to ensure selection
        scored.append(base_item_score)
#         print(f"🎯 Added base item to selection with high priority score")
    
    # Step 5: Select items without duplicates
    selected = pick_top_ranked_items_no_duplicates(scored, target_count)
    
    # Step 6: Ensure base item is first in the list if it exists
    if base_item:
        # Remove base item from its current position and put it first
        selected = [item for item in selected if item.id != base_item.id]
        if base_item_in_filtered or any(item.id == base_item.id for item in filtered_items):
            selected.insert(0, base_item)
            # print(f"✅ Base item placed first in selection")
    
    # Step 7: Ensure we have essential items
    selected = ensure_essential_items(selected, filtered_items, context)
    
    # print(f"✅ Smart selection (FIXED): Selected {len(selected)} items")
    for i, item in enumerate(selected):
#         print(f"  {i+1}. {item.name} ({normalize_item_type(item)})")
    
    return selected

# Keep the original function for backward compatibility
async def select_items(filtered_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
    """Original select_items function - now calls the fixed version."""
    return await select_items_fixed(filtered_items, context) 