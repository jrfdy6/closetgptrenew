# robust_hydrator.py
from copy import deepcopy
from datetime import datetime
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

# Import the main ClothingItem model to ensure consistency
logger = logging.getLogger(__name__)

try:
    # Try relative import first
    from ..custom_types.wardrobe import ClothingItem, Metadata, ColorAnalysis
    logger.info("✅ Using main ClothingItem, Metadata, and ColorAnalysis models from custom_types.wardrobe")
    USING_FALLBACK_CLASSES = False
except ImportError:
    try:
        # Try absolute import
        from custom_types.wardrobe import ClothingItem, Metadata, ColorAnalysis
        logger.info("✅ Using main ClothingItem, Metadata, and ColorAnalysis models from custom_types.wardrobe (absolute)")
        USING_FALLBACK_CLASSES = False
    except ImportError as e:
        logger.error(f"❌ Failed to import main ClothingItem, Metadata, and ColorAnalysis models: {e}")
        logger.error("🔄 Falling back to local ClothingItem and Metadata models")
        USING_FALLBACK_CLASSES = True
    
    # Fallback to local model if import fails
    class BasicMetadata(BaseModel):
        analysisTimestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
        originalType: str | None = None
        originalSubType: str | None = None

    class Metadata(BaseModel):
        basicMetadata: BasicMetadata = Field(default_factory=BasicMetadata)
        visualAttributes: dict | None = None
        itemMetadata: dict | None = None
        colorAnalysis: dict = Field(default_factory=lambda: {"dominant": [], "matching": []})

    class ClothingItem(BaseModel):
        id: str
        name: str  # CRITICAL: Added missing required field
        type: str
        color: str  # CRITICAL: Added missing required field
        season: List[str]  # CRITICAL: Made required field
        imageUrl: str
        userId: str
        dominantColors: List[str]  # Will be converted by validator
        matchingColors: List[str]  # Will be converted by validator
        createdAt: int
        updatedAt: int
        metadata: Metadata = Field(default_factory=Metadata)

        # Optional style/business fields (not patched)
        style: list | None = None
        occasion: list | None = None
        tags: list | None = None
        formalityLevel: str | None = None
        fit: str | None = None

# -------------------------------
# Synthetic placeholder values
# -------------------------------
PLACEHOLDERS = {
    "imageUrl": "https://placeholder.com/wardrobe-item.png",
    "userId": "unknown-user",
    "dominantColors": [],  # Empty list - will be filled by Color validator
    "matchingColors": [],  # Empty list - will be filled by Color validator
    "createdAt": lambda: int(datetime.utcnow().timestamp() * 1000),
    "updatedAt": lambda: int(datetime.utcnow().timestamp() * 1000),
    "metadata": Metadata(
        analysisTimestamp=int(datetime.utcnow().timestamp() * 1000),
        originalType="unknown",
        colorAnalysis=ColorAnalysis()
    ) if not USING_FALLBACK_CLASSES else {"basicMetadata": {"analysisTimestamp": int(datetime.utcnow().timestamp() * 1000)}},  # default empty Metadata instance
    "quality_score": 0.5,
    "pairability_score": 0.5,
    # CRITICAL MISSING FIELDS:
    "name": "Unknown Item",
    "color": "unknown",
    "season": ["spring", "summer", "fall", "winter"],  # Default to all seasons
    "tags": [],
    "style": [],
    "occasion": []
}

CORE_FIELDS = ["imageUrl", "userId", "dominantColors", "matchingColors", "createdAt", "updatedAt", "metadata", "quality_score", "pairability_score", "name", "color", "season", "tags", "style", "occasion"]

def normalize_item_type_to_enum(item_type: str, item_name: str = "") -> str:
    """Normalize item types to match ClothingType enum values."""
    
    # Handle ClothingType enum format (e.g., "ClothingType.SHIRT" -> "shirt")
    if 'clothingtype.' in item_type.lower():
        enum_value = item_type.split('.')[-1].lower()
        # Map enum values to valid ClothingType enum strings
        enum_mappings = {
            'shirt': 'shirt',
            'pants': 'pants', 
            'shoes': 'shoes',
            'jacket': 'jacket',
            'dress': 'dress',
            'sweater': 'sweater',
            'blouse': 'blouse',
            'hoodie': 'hoodie',
            'polo': 'polo',
            'jeans': 'jeans',
            'shorts': 'shorts',
            'skirt': 'skirt',
            'boots': 'boots',
            'sneakers': 'sneakers',
            'heels': 'heels',
            'blazer': 'blazer',
            'coat': 'coat',
            'accessory': 'accessory'
        }
        if enum_value in enum_mappings:
            return enum_mappings[enum_value]
        else:
            return "shirt"  # Default fallback
    
    type_lower = item_type.lower()
    name_lower = item_name.lower()
    
    # Map generic categories to specific enum values
    if type_lower in ["tops", "top", "upper"]:
        # Default to shirt for tops
        return "shirt"
    elif type_lower in ["bottoms", "bottom", "lower"]:
        # Default to pants for bottoms
        return "pants"
    elif type_lower in ["footwear", "shoes"]:
        # Default to shoes for footwear
        return "shoes"
    elif type_lower in ["outerwear", "jackets"]:
        # Default to jacket for outerwear
        return "jacket"
    elif type_lower in ["accessories", "accessory"]:
        # Default to accessory
        return "accessory"
    
    # Map specific types that might be in the database
    type_mappings = {
        "t-shirt": "t-shirt",
        "tshirt": "t-shirt", 
        "dress_shirt": "dress_shirt",
        "blouse": "blouse",
        "sweater": "sweater",
        "hoodie": "hoodie",
        "polo": "polo",
        "tank_top": "tank_top",
        "jeans": "jeans",
        "chinos": "chinos",
        "slacks": "slacks",
        "shorts": "shorts",
        "joggers": "joggers",
        "sweatpants": "sweatpants",
        "skirt": "skirt",
        "dress": "dress",
        "blazer": "blazer",
        "coat": "coat",
        "sneakers": "sneakers",
        "boots": "boots",
        "sandals": "sandals",
        "heels": "heels",
        "flats": "flats",
        "belt": "belt",
        "hat": "hat",
        "scarf": "scarf"
    }
    
    # Return mapped value or original type if it matches enum
    return type_mappings.get(type_lower, type_lower)

# -------------------------------
# Hydrator Function
# -------------------------------
def hydrate_wardrobe_items(items: List[Dict[str, Any]]) -> List[ClothingItem]:
    """
    Safety-net hydrator for wardrobe items.
    Always patches core survival fields.
    Returns a new list of ClothingItem instances (immutable copies).
    """
    logger.error(f"🚨 FORCE REDEPLOY v10.0: HYDRATE_ENTRY: Processing {len(items)} items")
    patched_items = []

    for raw_item in items:
        # Skip None items
        if raw_item is None:
            logger.warning(f"⚠️ Skipping None item in wardrobe")
            continue
            
        item_copy = deepcopy(raw_item)
        
        # Check if deepcopy returned None (shouldn't happen, but just in case)
        if item_copy is None:
            logger.warning(f"⚠️ deepcopy returned None for item, skipping")
            continue
            
        patched_fields = []

        # Patch core survival fields
        for field in CORE_FIELDS:
            if field not in item_copy or item_copy[field] in [None, ""]:
                value = PLACEHOLDERS[field]() if callable(PLACEHOLDERS[field]) else PLACEHOLDERS[field]
                item_copy[field] = value
                patched_fields.append(field)

        # Normalize type field to match ClothingType enum
        if "type" in item_copy and item_copy["type"]:
            item_copy["type"] = normalize_item_type_to_enum(item_copy["type"], item_copy.get("name", "") if item_copy else "")

        # Logging
        if patched_fields:
            item_id = item_copy.get('id', '<unknown>') if item_copy else '<unknown>'
            logger.warning(f"⚠️ Item {item_id} required emergency hydration")
            logger.debug(f"🔧 EMERGENCY HYDRATION: Item {item_id} patched fields: {patched_fields}")

        # Convert to Pydantic model
        try:
            clothing_item = ClothingItem(**item_copy)
            patched_items.append(clothing_item)
        except ValidationError as e:
            logger.error(f"❌ Failed to create ClothingItem: {e}")
            continue

    return patched_items

# -------------------------------
# Integration Helper
# -------------------------------
def ensure_items_safe_for_pydantic(items: List[Dict[str, Any]]) -> List[ClothingItem]:
    """
    Safety-net function to ensure all items are safe for Pydantic validation.
    This is the main entry point for the robust generator.
    """
    logger.error(f"🚨 FORCE REDEPLOY v11.0: HYDRATOR ENTRY: Starting safety check for {len(items)} items")
    print(f"🔍 HYDRATOR DEBUG: items type = {type(items)}")
    print(f"🔍 HYDRATOR DEBUG: items length = {len(items) if items else 'None'}")
    if items:
        print(f"🔍 HYDRATOR DEBUG: first item = {items[0]}")
        print(f"🔍 HYDRATOR DEBUG: first item type = {type(items[0])}")
    try:
        safe_items = hydrate_wardrobe_items(items)
        logger.error(f"🚨 FORCE REDEPLOY v11.0: HYDRATOR EXIT: {len(safe_items)} items validated and ready")
        return safe_items
    except Exception as e:
        logger.error(f"❌ HYDRATOR FAILED: {e}")
        print(f"🚨 HYDRATOR ERROR: {e}")
        import traceback
        print(f"🚨 HYDRATOR TRACEBACK: {traceback.format_exc()}")
        raise
