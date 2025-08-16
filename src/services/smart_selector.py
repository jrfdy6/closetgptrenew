from typing import List, Dict, Any
from ..custom_types.wardrobe import ClothingItem
from .outfit_fallback_service import OutfitFallbackService

# --- Scoring logic ---
def calculate_style_score(item: ClothingItem, context: Dict[str, Any]) -> float:
    base_score = 1.0
    occasion = context.get("occasion", "").lower()
    if occasion and hasattr(item, 'occasion'):
        if occasion in [occ.lower() for occ in getattr(item, 'occasion', [])]:
            base_score += 0.3
    style = context.get("style", "")
    if style and hasattr(item, 'style'):
        style_lower = style.lower() if style else ""
        if style_lower in [s.lower() for s in getattr(item, 'style', [])]:
            base_score += 0.2
    weather = context.get("weather", {})
    if hasattr(weather, 'temperature'):
        temperature = weather.temperature
    else:
        temperature = weather.get("temperature", 70)
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
        print(f"⚠️ Warning: Could not fetch favorite items: {e}")
        return set()

def score_items(items: List[ClothingItem], context: Dict[str, Any]) -> List[dict]:
    user_id = context.get("user_id")
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
            print(f"⚠️ Warning: Could not get favorite items: {e}")
            favorite_ids = set()
    scored = []
    for item in items:
        base_score = calculate_style_score(item, context)
        if hasattr(item, 'id') and item.id in favorite_ids:
            base_score += 0.3
            print(f"⭐ Favorite item boosted: {getattr(item, 'name', str(item))} (score: {base_score:.2f})")
        scored.append({"item": item, "score": base_score})
    return scored

async def score_items_async(items: List[ClothingItem], context: Dict[str, Any]) -> List[dict]:
    user_id = context.get("user_id")
    favorite_ids = set()
    if user_id:
        favorite_ids = await get_favorite_item_ids(user_id)
    scored = []
    for item in items:
        base_score = calculate_style_score(item, context)
        if hasattr(item, 'id') and item.id in favorite_ids:
            base_score += 0.3
            print(f"⭐ Favorite item boosted: {getattr(item, 'name', str(item))} (score: {base_score:.2f})")
        scored.append({"item": item, "score": base_score})
    return scored

def pick_top_ranked_items(scored: List[dict], target_count: int = 5) -> List[ClothingItem]:
    sorted_items = sorted(scored, key=lambda x: x["score"], reverse=True)
    return [entry["item"] for entry in sorted_items[:target_count]]

async def select_items(filtered_items: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
    print(f"🎯 Smart selection: Processing {len(filtered_items)} items")
    
    # Check if there's a base item that should be included
    base_item = context.get("base_item")
    base_item_included = False
    
    if base_item:
        print(f"🎯 Base item specified: {base_item.name}")
        # Check if base item is in filtered items
        base_item_in_filtered = any(item.id == base_item.id for item in filtered_items)
        if base_item_in_filtered:
            print(f"✅ Base item found in filtered items")
            base_item_included = True
        else:
            print(f"⚠️ Base item not found in filtered items, will try to include it")
    
    scored = await score_items_async(filtered_items, context)
    target_counts = context.get("target_counts", {})
    target_count = target_counts.get("target_items", 5)
    
    # If we have a base item, ensure it's included
    if base_item and not base_item_included:
        # Add base item to scored items with high score
        base_item_score = {"item": base_item, "score": 10.0}  # Very high score to ensure selection
        scored.append(base_item_score)
        print(f"🎯 Added base item to selection with high priority score")
    
    selected = pick_top_ranked_items(scored, target_count)
    
    # Ensure base item is first in the list if it exists
    if base_item:
        # Remove base item from its current position and put it first
        selected = [item for item in selected if item.id != base_item.id]
        if base_item_in_filtered or any(item.id == base_item.id for item in filtered_items):
            selected.insert(0, base_item)
            print(f"✅ Base item placed first in selection")
    
    print(f"✅ Smart selection: Selected {len(selected)} items")
    return selected 