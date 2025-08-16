from typing import List
from ..custom_types.wardrobe import ClothingItem
from .smart_selector import select_items

async def run_fallback(original_items: List[ClothingItem], context) -> List[ClothingItem]:
    # Example: relax constraints in context (dummy)
    relaxed_context = dict(context)
    relaxed_context['relaxed'] = True
    return await select_items(original_items, relaxed_context) 