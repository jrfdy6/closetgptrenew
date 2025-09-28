#!/usr/bin/env python3
"""
Wardrobe Preprocessor Service
============================

Ensures all wardrobe items are properly converted to valid ClothingItem objects
before being passed to the robust outfit generation service.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..custom_types.wardrobe import ClothingItem
from ..utils.validation import normalize_clothing_type

logger = logging.getLogger(__name__)

class WardrobePreprocessor:
    """Preprocessor that guarantees all wardrobe items are valid ClothingItem objects"""
    
    def __init__(self):
        self.conversion_errors = []
    
    def preprocess_wardrobe(self, raw_wardrobe: List[Dict[str, Any]], user_id: str) -> List[ClothingItem]:
        """
        Convert raw wardrobe data to valid ClothingItem objects with safe defaults.
        
        Args:
            raw_wardrobe: List of raw wardrobe item dictionaries
            user_id: User ID for default assignment
            
        Returns:
            List of valid ClothingItem objects
        """
        logger.info(f"🔧 WARDROBE PREPROCESSOR: Starting preprocessing of {len(raw_wardrobe)} items")
        
        clothing_items = []
        self.conversion_errors = []
        
        for i, raw_item in enumerate(raw_wardrobe):
            try:
                clothing_item = self._convert_to_clothing_item(raw_item, user_id, i)
                clothing_items.append(clothing_item)
                logger.debug(f"✅ Preprocessed item {i+1}: {clothing_item.name} ({clothing_item.type})")
                
            except Exception as e:
                error_msg = f"Failed to preprocess item {i+1}: {e}"
                self.conversion_errors.append(error_msg)
                logger.warning(f"⚠️ {error_msg}")
                logger.warning(f"⚠️ Raw item data: {raw_item}")
                continue
        
        if self.conversion_errors:
            logger.warning(f"⚠️ {len(self.conversion_errors)} items failed preprocessing: {self.conversion_errors}")
        
        logger.info(f"🔧 WARDROBE PREPROCESSOR: {len(raw_wardrobe)} raw items -> {len(clothing_items)} valid ClothingItem objects")
        
        return clothing_items
    
    def _convert_to_clothing_item(self, raw: Dict[str, Any], user_id: str, item_index: int) -> ClothingItem:
        """
        Convert a single raw wardrobe item to a valid ClothingItem with safe defaults.
        
        Args:
            raw: Raw wardrobe item dictionary
            user_id: User ID for default assignment
            item_index: Index of item for error reporting
            
        Returns:
            Valid ClothingItem object
        """
        # Get current timestamp
        now = int(time.time() * 1000)
        
        # Normalize type to lowercase
        raw_type = raw.get("type", "other")
        if isinstance(raw_type, str):
            raw_type = raw_type.lower()
        
        # Normalize the type using the validation utility
        normalized_type = normalize_clothing_type(raw_type)
        
        # Extract metadata with safe defaults
        metadata = raw.get("metadata", {})
        
        # Ensure all required fields have safe defaults
        return ClothingItem(
            # Required fields with safe defaults
            id=raw.get("id", f"item_{item_index}_{now}"),
            name=raw.get("name", "Unknown Item"),
            type=normalized_type,
            color=raw.get("color", "unknown"),
            imageUrl=raw.get("imageUrl", ""),
            userId=raw.get("userId", user_id),
            dominantColors=raw.get("dominantColors", []),
            matchingColors=raw.get("matchingColors", []),
            createdAt=raw.get("createdAt", now),
            updatedAt=raw.get("updatedAt", now),
            
            # Optional fields with safe defaults
            style=raw.get("style", []),
            occasion=raw.get("occasion", ["casual"]),
            season=raw.get("season", ["all"]),
            tags=raw.get("tags", []),
            brand=raw.get("brand", None),
            wearCount=raw.get("wearCount", 0),
            favorite_score=raw.get("favorite_score", 0.0),
            subType=raw.get("subType", None),
            colorName=raw.get("colorName", None),
            backgroundRemoved=raw.get("backgroundRemoved", None),
            embedding=raw.get("embedding", None),
            
            # Metadata with all required fields
            metadata={
                "analysisTimestamp": metadata.get("analysisTimestamp", now),
                "originalType": metadata.get("originalType", raw_type),
                "originalSubType": metadata.get("originalSubType", None),
                "styleTags": metadata.get("styleTags", raw.get("style", [])),
                "occasionTags": metadata.get("occasionTags", raw.get("occasion", ["casual"])),
                "brand": metadata.get("brand", raw.get("brand", None)),
                "imageHash": metadata.get("imageHash", None),
                "colorAnalysis": metadata.get("colorAnalysis", {
                    "dominant": [],
                    "matching": []
                }),
                "basicMetadata": metadata.get("basicMetadata", None),
                "visualAttributes": metadata.get("visualAttributes", None),
                "itemMetadata": metadata.get("itemMetadata", None),
                "naturalDescription": metadata.get("naturalDescription", None),
                "temperatureCompatibility": metadata.get("temperatureCompatibility", None),
                "materialCompatibility": metadata.get("materialCompatibility", None),
                "bodyTypeCompatibility": metadata.get("bodyTypeCompatibility", None),
                "skinToneCompatibility": metadata.get("skinToneCompatibility", None),
                "outfitScoring": metadata.get("outfitScoring", None)
            }
        )
    
    def get_conversion_errors(self) -> List[str]:
        """Get list of conversion errors from the last preprocessing run"""
        return self.conversion_errors.copy()
    
    def has_errors(self) -> bool:
        """Check if there were any conversion errors in the last preprocessing run"""
        return len(self.conversion_errors) > 0
