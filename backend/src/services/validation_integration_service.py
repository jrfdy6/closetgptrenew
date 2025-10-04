#!/usr/bin/env python3
"""
Validation Integration Service
=============================

This service integrates the Enhanced Outfit Validator into the existing
outfit generation pipeline, replacing the failing validation system
with a robust, comprehensive solution.

Key Features:
- Replaces failing validation with robust system
- Maintains compatibility with existing code
- Provides detailed validation feedback
- Prevents inappropriate outfit combinations
- No fallback to bad outfits
"""

import logging
from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from .enhanced_outfit_validator import EnhancedOutfitValidator, ValidationResult, ValidationSeverity

logger = logging.getLogger(__name__)

class ValidationIntegrationService:
    """
    Integration service that replaces the failing validation system
    with the robust Enhanced Outfit Validator
    """
    
    def __init__(self):
        self.enhanced_validator = EnhancedOutfitValidator()
        logger.info("✅ Enhanced Outfit Validator initialized")
    
    async def validate_outfit_composition(
        self, 
        items: List[Dict[str, Any]], 
        occasion: str, 
        base_item: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Main validation method that replaces the failing validate_outfit_composition
        
        This method:
        1. Uses the Enhanced Outfit Validator
        2. Provides robust validation with no fallback to bad outfits
        3. Returns only validated, appropriate items
        4. Maintains compatibility with existing code
        """
        logger.info(f"🔍 ENHANCED VALIDATION: Starting validation with {len(items)} items for {occasion}")
        
        try:
            # Convert items to ClothingItem objects if needed
            clothing_items = self._convert_to_clothing_items(items)
            
            # Create validation context
            context = {
                'occasion': occasion,
                'style': 'unknown',  # Will be filled by caller if available
                'mood': 'unknown',   # Will be filled by caller if available
                'weather': {'temperature': 70, 'condition': 'clear'},  # Default
                'user_profile': {},
                'base_item': base_item
            }
            
            # Run comprehensive validation
            validation_result: ValidationResult = await self.enhanced_validator.validate_outfit_comprehensive(
                items, context
            )
            
            logger.info(f"✅ ENHANCED VALIDATION: Completed - Valid: {validation_result.is_valid}")
            logger.info(f"📊 ENHANCED VALIDATION: Issues: {len(validation_result.issues)}")
            logger.info(f"📊 ENHANCED VALIDATION: Confidence: {validation_result.confidence_score:.1f}%")
            
            # Log validation details
            if validation_result.issues:
                logger.info("🔍 ENHANCED VALIDATION: Issues found:")
                for issue in validation_result.issues:
                    logger.info(f"   - {issue}")
            
            if validation_result.suggestions:
                logger.info("💡 ENHANCED VALIDATION: Suggestions:")
                for suggestion in validation_result.suggestions:
                    logger.info(f"   - {suggestion}")
            
            # CRITICAL: Only return items if validation passes
            if validation_result.is_valid:
                logger.info(f"✅ ENHANCED VALIDATION: Returning {len(validation_result.filtered_items)} validated items")
                return validation_result.filtered_items
            else:
                # NO FALLBACK TO BAD OUTFITS - Return empty list if validation fails
                logger.error(f"❌ ENHANCED VALIDATION: Validation failed - returning empty list")
                logger.error(f"❌ ENHANCED VALIDATION: Issues: {validation_result.issues}")
                logger.error(f"❌ ENHANCED VALIDATION: Severity: {validation_result.severity.value}")
                
                # Log detailed failure information
                details = validation_result.validation_details
                logger.error(f"❌ ENHANCED VALIDATION: Details: {details}")
                
                return []
                
        except Exception as e:
            logger.error(f"❌ ENHANCED VALIDATION: Exception during validation: {e}")
            logger.error(f"❌ ENHANCED VALIDATION: Returning empty list due to exception")
            
            # NO FALLBACK TO BAD OUTFITS - Return empty list on exception
            return []
    
    async def validate_outfit_with_enhanced_rules(
        self, 
        clothing_items: List[ClothingItem], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced validation method that replaces the failing validate_outfit_with_enhanced_rules
        
        This method maintains compatibility with existing code while providing
        robust validation through the Enhanced Outfit Validator
        """
        logger.info(f"🔍 ENHANCED RULES VALIDATION: Starting with {len(clothing_items)} items")
        
        try:
            # Convert ClothingItem objects to dictionaries
            items = [self._clothing_item_to_dict(item) for item in clothing_items]
            
            # Run comprehensive validation
            validation_result: ValidationResult = await self.enhanced_validator.validate_outfit_comprehensive(
                items, context
            )
            
            logger.info(f"✅ ENHANCED RULES VALIDATION: Completed - Valid: {validation_result.is_valid}")
            
            # Convert filtered items back to ClothingItem objects
            filtered_clothing_items = []
            for item_dict in validation_result.filtered_items:
                try:
                    clothing_item = self._dict_to_clothing_item(item_dict)
                    filtered_clothing_items.append(clothing_item)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to convert item back to ClothingItem: {e}")
            
            # Return result in expected format
            result = {
                'is_valid': validation_result.is_valid,
                'filtered_items': filtered_clothing_items,
                'issues': validation_result.issues,
                'suggestions': validation_result.suggestions,
                'confidence_score': validation_result.confidence_score,
                'severity': validation_result.severity.value,
                'validation_details': validation_result.validation_details
            }
            
            logger.info(f"✅ ENHANCED RULES VALIDATION: Returning {len(filtered_clothing_items)} validated items")
            return result
            
        except Exception as e:
            logger.error(f"❌ ENHANCED RULES VALIDATION: Exception during validation: {e}")
            
            # Return failure result
            return {
                'is_valid': False,
                'filtered_items': [],
                'issues': [f"Validation system error: {str(e)}"],
                'suggestions': ["Contact support - validation system needs attention"],
                'confidence_score': 0.0,
                'severity': 'critical',
                'validation_details': {'error': str(e)}
            }
    
    def _convert_to_clothing_items(self, items: List[Dict[str, Any]]) -> List[ClothingItem]:
        """Convert dictionary items to ClothingItem objects"""
        clothing_items = []
        for item in items:
            try:
                # Create ClothingItem from dictionary
                clothing_item = ClothingItem(
                    id=(item.get('id', '') if item else ''),
                    name=(item.get('name', '') if item else ''),
                    type=(item.get('type', '') if item else ''),
                    color=(item.get('color', '') if item else ''),
                    brand=(item.get('brand', '') if item else ''),
                    size=(item.get('size', '') if item else ''),
                    imageUrl=(item.get('imageUrl', '') if item else ''),
                    style=(item.get('style', []) if item else []),
                    occasion=(item.get('occasion', []) if item else []),
                    material=(item.get('material', '') if item else ''),
                    season=(item.get('season', []) if item else []),
                    dominantColors=(item.get('dominantColors', []) if item else []),
                    metadata=(item.get('metadata', {}) if item else {}),
                    favorite_score=(item.get('favorite_score', 0.0) if item else 0.0),
                    wearCount=(item.get('wearCount', 0) if item else 0),
                    quality_score=(item.get('quality_score', 0.5) if item else 0.5)
                )
                clothing_items.append(clothing_item)
            except Exception as e:
                logger.warning(f"⚠️ Failed to convert item to ClothingItem: {e}")
                continue
        
        return clothing_items
    
    def _clothing_item_to_dict(self, clothing_item: ClothingItem) -> Dict[str, Any]:
        """Convert ClothingItem to dictionary"""
        return {
            'id': clothing_item.id,
            'name': clothing_item.name,
            'type': clothing_item.type,
            'color': clothing_item.color,
            'brand': clothing_item.brand,
            'size': clothing_item.size,
            'imageUrl': clothing_item.imageUrl,
            'style': clothing_item.style or [],
            'occasion': clothing_item.occasion or [],
            'material': clothing_item.material,
            'season': clothing_item.season or [],
            'dominantColors': clothing_item.dominantColors or [],
            'metadata': clothing_item.metadata or {},
            'favorite_score': clothing_item.favorite_score,
            'wearCount': clothing_item.wearCount,
            'quality_score': clothing_item.quality_score
        }
    
    def _dict_to_clothing_item(self, item_dict: Dict[str, Any]) -> ClothingItem:
        """Convert dictionary back to ClothingItem"""
        return ClothingItem(
            id=(item_dict.get('id', '') if item_dict else ''),
            name=(item_dict.get('name', '') if item_dict else ''),
            type=(item_dict.get('type', '') if item_dict else ''),
            color=(item_dict.get('color', '') if item_dict else ''),
            brand=(item_dict.get('brand', '') if item_dict else ''),
            size=(item_dict.get('size', '') if item_dict else ''),
            imageUrl=(item_dict.get('imageUrl', '') if item_dict else ''),
            style=(item_dict.get('style', []) if item_dict else []),
            occasion=(item_dict.get('occasion', []) if item_dict else []),
            material=(item_dict.get('material', '') if item_dict else ''),
            season=(item_dict.get('season', []) if item_dict else []),
            dominantColors=(item_dict.get('dominantColors', []) if item_dict else []),
            metadata=(item_dict.get('metadata', {}) if item_dict else {}),
            favorite_score=(item_dict.get('favorite_score', 0.0) if item_dict else 0.0),
            wearCount=(item_dict.get('wearCount', 0) if item_dict else 0),
            quality_score=(item_dict.get('quality_score', 0.5) if item_dict else 0.5)
        )
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.enhanced_validator.get_validation_stats()
