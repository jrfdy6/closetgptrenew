# robust_hydrator.py
from copy import deepcopy
from datetime import datetime
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

# -------------------------------
# Logging Configuration
# -------------------------------
def setup_hydrator_logger(debug: bool = False):
    logger = logging.getLogger("WardrobeHydrator")
    logger.handlers.clear()  # clear previous handlers
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if debug else logging.WARNING)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

# Use environment variable to control debug mode
import os
debug_mode = os.getenv("HYDRATOR_DEBUG", "false").lower() == "true"
logger = setup_hydrator_logger(debug=debug_mode)

# -------------------------------
# Pydantic Models
# -------------------------------
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
    type: str
    imageUrl: str
    userId: str
    dominantColors: List[str]
    matchingColors: List[str]
    createdAt: int
    updatedAt: int
    metadata: Metadata = Field(default_factory=Metadata)

    # Optional style/business fields (not patched)
    style: list | None = None
    occasion: list | None = None
    season: list | None = None
    formalityLevel: str | None = None
    fit: str | None = None

# -------------------------------
# Synthetic placeholder values
# -------------------------------
PLACEHOLDERS = {
    "imageUrl": "https://placeholder.com/wardrobe-item.png",
    "userId": "unknown-user",
    "dominantColors": ["unknown"],
    "matchingColors": ["unknown"],
    "createdAt": lambda: int(datetime.utcnow().timestamp() * 1000),
    "updatedAt": lambda: int(datetime.utcnow().timestamp() * 1000),
    "metadata": Metadata(),  # default empty Metadata instance
    "quality_score": 0.5,
    "pairability_score": 0.5
}

CORE_FIELDS = ["imageUrl", "userId", "dominantColors", "matchingColors", "createdAt", "updatedAt", "metadata", "quality_score", "pairability_score"]

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
        item_copy = deepcopy(raw_item)
        patched_fields = []

        # Patch core survival fields
        for field in CORE_FIELDS:
            if field not in item_copy or item_copy[field] in [None, ""]:
                value = PLACEHOLDERS[field]() if callable(PLACEHOLDERS[field]) else PLACEHOLDERS[field]
                item_copy[field] = value
                patched_fields.append(field)

        # Normalize type field
        if "type" in item_copy and item_copy["type"]:
            item_copy["type"] = item_copy["type"].lower()

        # Logging
        if patched_fields:
            logger.warning(f"⚠️ Item {item_copy.get('id', '<unknown>')} required emergency hydration")
            logger.debug(f"🔧 EMERGENCY HYDRATION: Item {item_copy.get('id', '<unknown>')} patched fields: {patched_fields}")

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
    logger.error(f"🚨 FORCE REDEPLOY v10.0: HYDRATOR ENTRY: Starting safety check for {len(items)} items")
    safe_items = hydrate_wardrobe_items(items)
    logger.error(f"🚨 FORCE REDEPLOY v10.0: HYDRATOR EXIT: {len(safe_items)} items validated and ready")
    return safe_items
