"""
Validation functions for outfit generation and management.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def validate_outfit_completeness(outfit_items, occasion_reqs, occasion):
    """Enhanced validation that uses semantic matching like the robust generator"""
    missing_required = []
    
    for required in occasion_reqs['required']:
        if ' OR ' in required:
            # Handle OR conditions (e.g., "shorts OR athletic-pants")
            options = [opt.strip() for opt in required.split(' OR ')]
            if not any(_is_semantically_appropriate(outfit_items, opt, occasion) for opt in options):
                missing_required.append(required)
        else:
            # Single requirement with semantic matching
            if not _is_semantically_appropriate(outfit_items, required, occasion):
                missing_required.append(required)
    
    return missing_required


def _is_semantically_appropriate(outfit_items, required_item, occasion):
    """Check if outfit has semantically appropriate items for the requirement"""
    occasion_lower = occasion.lower()
    
    for item in outfit_items:
        # Safety check: handle list, dict, and object formats
        if isinstance(item, list):
            # Skip if item is a list (shouldn't happen but safety check)
            continue
        elif isinstance(item, dict):
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
        else:
            # Handle object format
            item_type = getattr(item, 'type', '').lower()
            item_name = getattr(item, 'name', '').lower()
        
        # Direct match first
        if required_item in item_type or required_item in item_name:
            return True
        
        # Semantic matching based on occasion and requirement
        if required_item == 'sneakers' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate footwear
            athletic_shoes = ['athletic', 'sport', 'running', 'training', 'gym', 'tennis', 'basketball']
            if any(term in item_name or term in item_type for term in athletic_shoes):
                return True
            # Accept casual shoes for athletic (more flexible)
            if 'shoes' in item_type and not any(formal in item_name for formal in ['dress', 'formal', 'oxford', 'loafer']):
                return True
        
        elif required_item == 'shirt' and occasion_lower in ['business', 'formal']:
            # Accept any business-appropriate top
            business_tops = ['shirt', 'blouse', 'button', 'dress', 'polo', 'business']
            if any(term in item_name or term in item_type for term in business_tops):
                return True
        
        elif required_item == 'pants' and occasion_lower in ['business', 'formal']:
            # Accept any business-appropriate bottom
            business_bottoms = ['pants', 'trousers', 'slacks', 'dress', 'formal']
            if any(term in item_name or term in item_type for term in business_bottoms):
                return True
        
        elif required_item == 'shorts' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate bottom
            athletic_bottoms = ['shorts', 'athletic', 'sport', 'running', 'training', 'gym']
            if any(term in item_name or term in item_type for term in athletic_bottoms):
                return True
        
        elif required_item == 'athletic-appropriate footwear' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate footwear
            athletic_shoes = ['athletic', 'sport', 'running', 'training', 'gym', 'tennis', 'basketball', 'sneakers']
            if any(term in item_name or term in item_type for term in athletic_shoes):
                return True
            # Accept casual shoes for athletic (more flexible)
            if 'shoes' in item_type and not any(formal in item_name for formal in ['dress', 'formal', 'oxford', 'loafer']):
                return True
        
        elif required_item == 'athletic-appropriate bottoms' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate bottom
            athletic_bottoms = ['shorts', 'athletic', 'sport', 'running', 'training', 'gym', 'leggings', 'sweatpants']
            if any(term in item_name or term in item_type for term in athletic_bottoms):
                return True
        
        elif required_item == 'athletic-appropriate top' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate top
            athletic_tops = ['t-shirt', 'tank', 'athletic', 'sport', 'running', 'training', 'gym', 'shirt']
            if any(term in item_name or term in item_type for term in athletic_tops):
                return True
        
        elif required_item == 'shirt OR t-shirt' and occasion_lower == 'casual':
            # Accept any casual top
            casual_tops = ['shirt', 't-shirt', 'top', 'blouse', 'polo']
            if any(term in item_name or term in item_type for term in casual_tops):
                return True
        
        elif required_item == 'pants OR shorts' and occasion_lower == 'casual':
            # Accept any casual bottom
            casual_bottoms = ['pants', 'jeans', 'shorts', 'bottom', 'trousers']
            if any(term in item_name or term in item_type for term in casual_bottoms):
                return True
    
    return False


async def validate_style_gender_compatibility(style: str, user_gender: str) -> Dict[str, Any]:
    """Validate if the requested style is appropriate for the user's gender."""
    # Validating style for gender
    
    # Gender-specific style definitions
    feminine_styles = [
        'french girl', 'romantic', 'pinup', 'boho', 'cottagecore', 
        'coastal grandmother', 'clean girl', 'feminine', 'delicate'
    ]
    
    masculine_styles = [
        'techwear', 'grunge', 'streetwear', 'rugged', 'masculine', 
        'athletic', 'sporty', 'urban'
    ]
    
    unisex_styles = [
        'minimalist', 'modern', 'classic', 'business casual', 'preppy',
        'casual', 'formal', 'avant-garde', 'artsy', 'maximalist',
        'colorblock', 'scandinavian', 'coastal chic', 'athleisure'
    ]
    
    style_lower = style.lower()
    user_gender_lower = user_gender.lower()
    
    # Check style appropriateness
    if user_gender_lower == 'male' and style_lower in feminine_styles:
        return {
            "is_compatible": False,
            "warning": f"Style '{style}' is typically feminine and may not be appropriate for male users",
            "suggested_alternatives": [s for s in unisex_styles if s not in ['french girl', 'romantic']]
        }
    
    elif user_gender_lower == 'female' and style_lower in masculine_styles:
        return {
            "is_compatible": False,
            "warning": f"Style '{style}' is typically masculine and may not be appropriate for female users",
            "suggested_alternatives": [s for s in unisex_styles if s not in ['techwear', 'grunge']]
        }
    
    else:
        return {
            "is_compatible": True,
            "warning": None,
            "suggested_alternatives": []
        }


# Note: The remaining validation functions (validate_outfit_composition, validate_layering_rules, 
# validate_color_material_harmony) are very large and will be extracted in a separate step
# to keep this file manageable.
