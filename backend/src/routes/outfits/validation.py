"""
Validation functions for outfit generation.
Handles outfit composition, layering, color/material harmony, and weather validation.
"""

import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import helper functions
from .helpers import is_layer_item


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


def safe_get_metadata(obj: Dict[str, Any], key: str, default=None):
    """Safely get a value from metadata, handling None metadata."""
    if obj is None:
        return default
    metadata = obj.get("metadata") or {}
    return (metadata.get(key, default) if metadata else default)


def log_generation_strategy(outfit_response: Dict[str, Any], user_id: str = "unknown", 
                          generation_time: float = 0.0, validation_time: float = 0.0,
                          failed_rules: List[str] = None, fallback_reason: str = None):
    """Log generation strategy usage and record metrics for monitoring."""
    strategy = safe_get_metadata(outfit_response, "generation_strategy", "unknown")
    outfit_id = (outfit_response.get("id", "unknown") if outfit_response else "unknown")
    occasion = (outfit_response.get("occasion", "unknown") if outfit_response else "unknown")
    style = (outfit_response.get("style", "unknown") if outfit_response else "unknown")
    mood = (outfit_response.get("mood", "unknown") if outfit_response else "unknown")
    item_count = len((outfit_response.get("items", []) if outfit_response else []))
    
    # CRITICAL DEBUG: Log what strategy we're about to log
    logger.info(f"🔍 DEBUG LOG_GENERATION_STRATEGY: About to log strategy = {strategy}")
    print(f"🔍 DEBUG LOG_GENERATION_STRATEGY: About to log strategy = {strategy}")
    # Define which strategies are considered "complex" vs "fallback"
    complex_strategies = ["cohesive_composition", "body_type_optimized", "style_profile_matched", "weather_adapted", "rule_based"]
    fallback_strategies = ["fallback_simple", "emergency_default"]
    
    # Determine if this was a successful generation
    success = strategy in complex_strategies
    
    # Record metrics
    try:
        from ...services.generation_metrics_service import generation_metrics
        generation_metrics.record_generation(
            strategy=strategy,
            occasion=occasion,
            style=style,
            mood=mood,
            user_id=user_id,
            generation_time=generation_time,
            validation_time=validation_time,
            failed_rules=failed_rules or [],
            fallback_reason=fallback_reason,
            success=success
        )
    except Exception as e:
        logger.warning(f"Failed to record generation metrics: {e}")
    
    # Enhanced logging with segmentation and failed rules
    if strategy in fallback_strategies or not success:
        failed_rules_str = ", ".join(failed_rules) if failed_rules else "none"
        logger.warning(
            f"[GENERATION][FALLBACK] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count} "
            f"failed_rules=[{failed_rules_str}] reason={fallback_reason or 'unknown'}"
        )
    elif strategy in complex_strategies:
        logger.info(
            f"[GENERATION][SUCCESS] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count}"
        )
    else:
        logger.warning(
            f"[GENERATION][UNKNOWN] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count}"
        )


async def validate_style_gender_compatibility(style: str, user_gender: str) -> Dict[str, Any]:
    """Validate if the requested style is appropriate for the user's gender."""
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


async def validate_outfit_composition(items: List[Dict], occasion: str, base_item: Optional[Dict] = None, style: str = "casual") -> List[Dict]:
    """Validate and ensure outfit has required components using enhanced validation."""
    # Convert dict items to ClothingItem objects for validation
    from ...custom_types.wardrobe import ClothingItem
    
    clothing_items = []
    for item_dict in items:
        try:
            # Normalize the type using the validation utility
            from ...utils.validation import normalize_clothing_type
            normalized_type = normalize_clothing_type((item_dict.get('type', 'other') if item_dict else 'other'))
            
            # Create a basic ClothingItem from the dict with all required fields
            clothing_item = ClothingItem(
                id=(item_dict.get('id', '') if item_dict else ''),
                name=(item_dict.get('name', '') if item_dict else ''),
                type=normalized_type,
                color=(item_dict.get('color', 'unknown') if item_dict else 'unknown'),
                imageUrl=(item_dict.get('imageUrl', '') if item_dict else ''),
                style=(item_dict.get('style', []) if item_dict else []),
                occasion=(item_dict.get('occasion', ['casual']) if item_dict else ['casual']),
                season=(item_dict.get('season', ['all']) if item_dict else ['all']),
                userId=(item_dict.get('userId', 'unknown') if item_dict else 'unknown'),
                dominantColors=(item_dict.get('dominantColors', []) if item_dict else []),
                matchingColors=(item_dict.get('matchingColors', []) if item_dict else []),
                createdAt=(item_dict.get('createdAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
                updatedAt=(item_dict.get('updatedAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
                brand=(item_dict.get('brand', None) if item_dict else None),
                wearCount=(item_dict.get('wearCount', 0) if item_dict else 0),
                favorite_score=(item_dict.get('favorite_score', 0.0) if item_dict else 0.0),
                tags=(item_dict.get('tags', []) if item_dict else []),
                metadata=item_dict.get('metadata', {
                    'analysisTimestamp': int(time.time() * 1000),
                    'originalType': (item_dict.get('type', 'other') if item_dict else 'other'),
                    'originalSubType': None,
                    'styleTags': (item_dict.get('style', []) if item_dict else []),
                    'occasionTags': (item_dict.get('occasion', ['casual']) if item_dict else ['casual']),
                    'brand': (item_dict.get('brand', None) if item_dict else None),
                    'imageHash': None,
                    'colorAnalysis': {
                        'dominant': [],
                        'matching': []
                    },
                    'basicMetadata': None,
                    'visualAttributes': None,
                    'itemMetadata': None,
                    'naturalDescription': None,
                    'temperatureCompatibility': None,
                    'materialCompatibility': None,
                    'bodyTypeCompatibility': None,
                    'skinToneCompatibility': None,
                    'outfitScoring': None
                })
            )
            clothing_items.append(clothing_item)
        except Exception as e:
            logger.warning(f"⚠️ Failed to convert item to ClothingItem: {e}")
            continue
    
    # Use ENHANCED validation service with integrated thought clarification
    from ...services.validation_integration_service import ValidationIntegrationService
    validation_service = ValidationIntegrationService()
    
    # Create context for validation
    context = {
        "occasion": occasion,
        "weather": {"temperature": 70, "condition": "clear"},  # Default weather
        "user_profile": {},
        "style": style,  # Use actual request style instead of hardcoded "casual"
        "mood": None,
        "target_counts": {
            "min_items": 3,
            "max_items": 6,
            "required_categories": ["top", "bottom", "shoes"]
        }
    }
    
    logger.info(f"🔍 DATA HANDOFF: Validation context created - occasion='{context['occasion']}', style='{context['style']}', mood='{context['mood']}'")
    
    # Run enhanced validation with inappropriate combination enforcement + simulation-based rules
    print(f"🔍 VALIDATION DEBUG: Item types: {[item.type for item in clothing_items]}")
    try:
        validation_result = await validation_service.validate_outfit_with_enhanced_rules(clothing_items, context)
    
        if validation_result.get("filtered_items"):
            # Convert back to dict format
            validated_outfit = []
            for item in validation_result["filtered_items"]:
                item_dict = {
                    "id": item.id,
                    "name": item.name,
                    "type": item.type,
                    "color": item.color,
                    "imageUrl": item.imageUrl,
                    "style": item.style,
                    "occasion": item.occasion,
                    "brand": item.brand,
                    "wearCount": item.wearCount,
                    "favorite_score": item.favorite_score,
                    "tags": item.tags,
                    "metadata": item.metadata
                }
                validated_outfit.append(item_dict)
            
            logger.info(f"✅ Enhanced validation completed: {len(validated_outfit)} items after filtering")
            if validation_result.get("errors"):
                errors = validation_result["errors"]
                logger.info(f"🔍 Validation errors: {errors}")
            if validation_result.get("warnings"):
                warnings = validation_result["warnings"]
                logger.info(f"🔍 Validation warnings: {warnings}")
            
            return validated_outfit
        else:
            print(f"❌ VALIDATION DEBUG: No filtered items returned from enhanced validation!")
            print(f"❌ VALIDATION DEBUG: Validation result: {validation_result}")
            # NO FALLBACK TO BAD OUTFITS - Return empty list if validation fails
            return []
            
    except Exception as validation_error:
        print(f"❌ VALIDATION DEBUG: Enhanced validation failed with error: {validation_error}")
        logger.error(f"Enhanced validation failed: {validation_error}")
        # NO FALLBACK TO BAD OUTFITS - Return empty list on validation failure
        return []
    
    # CRITICAL: Check if we have any items at all before falling back
    if not clothing_items:
        print(f"❌ VALIDATION CRITICAL: No clothing items to validate!")
        return []  # NO FALLBACK TO BAD OUTFITS - Return empty list
    
    # NO FALLBACK TO BAD OUTFITS - If we reach here, validation failed
    logger.error("❌ Enhanced validation failed completely - no fallback allowed")
    print(f"🚨 VALIDATION FAILURE: No valid outfit can be generated")
    print(f"🚨 VALIDATION REASON: All items failed enhanced validation rules")
    return []


async def validate_layering_rules(items: List[Dict], occasion: str) -> Dict[str, Any]:
    """Validate layering rules for the outfit."""
    logger.info(f"🔍 DEBUG: Validating layering rules for {occasion} occasion")
    
    # Count layering items
    layer_items = [item for item in items if is_layer_item((item.get('type', '') if item else ''))]
    layer_count = len(layer_items)
    
    logger.info(f"🔍 DEBUG: Found {layer_count} layering items: {[(item.get('name', 'unnamed') if item else 'unnamed') for item in layer_items]}")
    
    warnings = []
    
    # Occasion-based layering rules
    if occasion.lower() in ['formal', 'business']:
        if layer_count < 2:
            warnings.append(f"Formal occasion typically requires at least 2 layers, got {layer_count}")
        elif layer_count > 3:
            warnings.append(f"Formal occasion may have too many layers: {layer_count}")
    
    elif occasion.lower() in ['casual', 'weekend']:
        if layer_count > 3:
            warnings.append(f"Casual occasion may have too many layers: {layer_count}")
    
    elif occasion.lower() in ['athletic', 'gym', 'sporty']:
        if layer_count > 2:
            warnings.append(f"Athletic occasion typically needs fewer layers: {layer_count}")
    
    # Check for layering conflicts
    layer_types = [(item.get('type', '') if item else '').lower() for item in layer_items]
    
    # Heavy combinations
    if 'sweater' in layer_types and 'jacket' in layer_types:
        warnings.append("Sweater and jacket combination may be too heavy")
    
    if 'sweater' in layer_types and 'coat' in layer_types:
        warnings.append("Sweater and coat combination may be too heavy")
    
    if 'jacket' in layer_types and 'coat' in layer_types:
        warnings.append("Jacket and coat combination may be too heavy")
    
    # Multiple heavy items
    heavy_items = [item for item in layer_items if item.get('type', '').lower() in ['sweater', 'jacket', 'coat']]
    if len(heavy_items) > 2:
        warnings.append(f"Too many heavy layering items: {len(heavy_items)}")
    
    # ENHANCED: Prevent shirt-on-shirt combinations
    shirt_types = ['t-shirt', 'polo', 'shirt', 'blouse', 'dress shirt', 'button up', 'button-up', 'oxford', 'dress-shirt']
    shirt_count = sum(1 for layer_type in layer_types if any(shirt_type in layer_type for shirt_type in shirt_types))
    if shirt_count > 1:
        warnings.append(f"Multiple shirt types detected ({shirt_count}): Avoid layering shirts on shirts")
        logger.warning(f"🔍 DEBUG: Shirt-on-shirt combination detected: {layer_types}")
    
    # ENHANCED: Prevent flip-flops/slides with formal wear
    formal_items = ['blazer', 'suit', 'suit jacket', 'sport coat', 'jacket']
    casual_shoes = ['flip-flops', 'flip flops', 'slides', 'sandals', 'thongs']
    
    has_formal_item = any(formal_type in layer_type for formal_type in formal_items for layer_type in layer_types)
    has_casual_shoes = any(casual_shoe in layer_type for casual_shoe in casual_shoes for layer_type in layer_types)
    
    if has_formal_item and has_casual_shoes:
        warnings.append("Flip-flops/slides should not be worn with blazers or suits")
        logger.warning(f"🔍 DEBUG: Formal-casual shoe mismatch detected: formal={formal_items}, casual_shoes={casual_shoes}")
    
    logger.info(f"🔍 DEBUG: Layering validation complete: {len(warnings)} warnings")
    
    return {
        "layer_count": layer_count,
        "layer_items": [(item.get('name', 'unnamed') if item else 'unnamed') for item in layer_items],
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }


async def validate_color_material_harmony(items: List[Dict], style: str, mood: str) -> Dict[str, Any]:
    """Validate color theory and material compatibility."""
    logger.info(f"🔍 DEBUG: Validating color and material harmony for {style} style, {mood} mood")
    
    warnings = []
    color_analysis = {}
    material_analysis = {}
    
    # Extract colors and materials from items
    all_colors = []
    all_materials = []
    
    for item in items:
        # Extract colors (handle different field names)
        item_colors = (item.get('dominantColors', []) or item.get('colors', []) or item.get('color', [])) if item else []
        if isinstance(item_colors, str):
            item_colors = [item_colors]
        elif not isinstance(item_colors, list):
            item_colors = []
        
        # Extract materials (handle different field names)
        item_material = (item.get('material', '') or item.get('fabric', '') or '') if item else ''
        
        if item_colors:
            all_colors.extend([color.lower() if isinstance(color, str) else str(color).lower() for color in item_colors])
        if item_material:
            all_materials.append(item_material.lower())
    
    logger.info(f"🔍 DEBUG: Found colors: {all_colors}")
    logger.info(f"🔍 DEBUG: Found materials: {all_materials}")
    
    # Color Theory Validation
    if all_colors:
        color_warnings = validate_color_theory(all_colors, style, mood)
        warnings.extend(color_warnings)
        color_analysis = analyze_color_palette(all_colors)
    
    # Material Compatibility Validation
    if all_materials:
        material_warnings = validate_material_compatibility(all_materials, style, mood)
        warnings.extend(material_warnings)
        material_analysis = analyze_material_combinations(all_materials)
    
    logger.info(f"🔍 DEBUG: Color/material validation complete: {len(warnings)} warnings")
    
    return {
        "colors": color_analysis,
        "materials": material_analysis,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }


def validate_color_theory(colors: List[str], style: str, mood: str) -> List[str]:
    """Apply advanced color theory rules."""
    warnings = []
    
    # Color conflicts (complementary colors that may clash)
    color_conflicts = {
        "red": ["green"],
        "blue": ["orange"], 
        "yellow": ["purple"],
        "green": ["red"],
        "purple": ["yellow"],
        "orange": ["blue"],
        "pink": ["lime", "bright green"],
        "teal": ["coral", "bright orange"]
    }
    
    # Check for color conflicts
    for i, color1 in enumerate(colors):
        for j, color2 in enumerate(colors[i+1:], i+1):
            if color1 in color_conflicts and color2 in color_conflicts[color1]:
                warnings.append(f"Color conflict: {color1} and {color2} may clash")
    
    # Style-based color rules
    style_color_rules = {
        "minimalist": {"max_colors": 3, "description": "Minimalist style prefers fewer colors"},
        "maximalist": {"max_colors": 6, "description": "Maximalist style can handle more colors"},
        "monochrome": {"max_colors": 2, "description": "Monochrome style should stick to one color family"},
        "colorblock": {"min_colors": 3, "description": "Colorblock style needs multiple distinct colors"}
    }
    
    if style.lower() in style_color_rules:
        rule = style_color_rules[style.lower()]
        unique_colors = list(set(colors))
        
        if "max_colors" in rule and len(unique_colors) > rule["max_colors"]:
            warnings.append(f"{rule['description']}: {len(unique_colors)} colors (max {rule['max_colors']})")
        elif "min_colors" in rule and len(unique_colors) < rule["min_colors"]:
            warnings.append(f"{rule['description']}: {len(unique_colors)} colors (min {rule['min_colors']})")
    
    # Mood-based color psychology
    mood_color_rules = {
        "calm": ["blue", "green", "lavender", "sage"],
        "energetic": ["red", "orange", "yellow", "pink"],
        "sophisticated": ["black", "navy", "burgundy", "cream"],
        "playful": ["coral", "mint", "yellow", "pink"],
        "professional": ["navy", "gray", "white", "burgundy"]
    }
    
    if mood.lower() in mood_color_rules:
        recommended_colors = mood_color_rules[mood.lower()]
        current_colors = list(set(colors))
        matching_colors = [c for c in current_colors if c in recommended_colors]
        
        if len(matching_colors) < len(current_colors) * 0.5:  # Less than 50% match
            warnings.append(f"Mood '{mood}' works better with colors like: {', '.join(recommended_colors[:3])}")
    
    return warnings


def validate_material_compatibility(materials: List[str], style: str, mood: str) -> List[str]:
    """Validate material compatibility and appropriateness."""
    warnings = []
    
    # Material texture conflicts
    texture_conflicts = {
        "smooth": ["rough", "textured", "knit"],
        "rough": ["smooth", "silk", "satin"],
        "heavy": ["light", "sheer", "linen"],
        "light": ["heavy", "wool", "leather"]
    }
    
    # Check for texture conflicts
    for i, material1 in enumerate(materials):
        for j, material2 in enumerate(materials[i+1:], i+1):
            for texture, conflicts in texture_conflicts.items():
                if texture in material1 and any(conflict in material2 for conflict in conflicts):
                    warnings.append(f"Texture conflict: {material1} and {material2} may not work well together")
    
    # Style-based material rules
    style_material_rules = {
        "formal": ["silk", "wool", "cashmere", "cotton"],
        "casual": ["denim", "cotton", "linen", "jersey"],
        "luxury": ["silk", "cashmere", "leather", "wool"],
        "athletic": ["polyester", "spandex", "nylon", "cotton"],
        "bohemian": ["linen", "cotton", "suede", "knit"]
    }
    
    if style.lower() in style_material_rules:
        recommended_materials = style_material_rules[style.lower()]
        current_materials = list(set(materials))
        matching_materials = [m for m in current_materials if any(rec in m for rec in recommended_materials)]
        
        if len(matching_materials) < len(current_materials) * 0.6:  # Less than 60% match
            warnings.append(f"Style '{style}' works better with materials like: {', '.join(recommended_materials[:3])}")
    
    # Seasonal material appropriateness
    seasonal_materials = {
        "summer": ["linen", "cotton", "seersucker", "chambray"],
        "winter": ["wool", "cashmere", "tweed", "velvet"],
        "spring": ["cotton", "linen", "silk", "denim"],
        "fall": ["wool", "corduroy", "denim", "leather"]
    }
    
    # Check for seasonal mismatches (this could be enhanced with actual season detection)
    for season, season_materials in seasonal_materials.items():
        if any(season_mat in mat for mat in materials for season_mat in season_materials):
            # Found seasonal material, could add season-specific warnings here
            pass
    
    return warnings


def analyze_color_palette(colors: List[str]) -> Dict[str, Any]:
    """Analyze the color palette for insights."""
    unique_colors = list(set(colors))
    
    # Color temperature analysis
    warm_colors = ["red", "orange", "yellow", "pink", "coral", "peach"]
    cool_colors = ["blue", "green", "purple", "teal", "navy", "sage"]
    neutral_colors = ["black", "white", "gray", "beige", "cream", "brown"]
    
    warm_count = sum(1 for c in unique_colors if c in warm_colors)
    cool_count = sum(1 for c in unique_colors if c in cool_colors)
    neutral_count = sum(1 for c in unique_colors if c in neutral_colors)
    
    return {
        "total_colors": len(unique_colors),
        "warm_colors": warm_count,
        "cool_colors": cool_count,
        "neutral_colors": neutral_count,
        "palette_type": "warm" if warm_count > cool_count else "cool" if cool_count > warm_count else "neutral"
    }


def analyze_material_combinations(materials: List[str]) -> Dict[str, Any]:
    """Analyze material combinations for insights."""
    unique_materials = list(set(materials))
    
    # Material type analysis
    natural_materials = ["cotton", "wool", "silk", "linen", "cashmere"]
    synthetic_materials = ["polyester", "nylon", "spandex", "acrylic"]
    luxury_materials = ["silk", "cashmere", "leather", "velvet"]
    
    natural_count = sum(1 for m in unique_materials if any(nat in m for nat in natural_materials))
    synthetic_count = sum(1 for m in unique_materials if any(syn in m for syn in synthetic_materials))
    luxury_count = sum(1 for m in unique_materials if any(lux in m for lux in luxury_materials))
    
    return {
        "total_materials": len(unique_materials),
        "natural_materials": natural_count,
        "synthetic_materials": synthetic_count,
        "luxury_materials": luxury_count,
        "material_quality": "luxury" if luxury_count > 1 else "natural" if natural_count > synthetic_count else "mixed"
    }


def validate_weather_outfit_combinations(outfit: Dict[str, Any], weather, mode: str = "soft") -> Dict[str, Any]:
    """Validate outfit combinations for weather appropriateness with hard/soft rule modes.
    
    Args:
        outfit: The generated outfit dictionary
        weather: Weather data object
        mode: "hard" to exclude inappropriate items, "soft" to warn but keep items
    """
    try:
        items = (outfit.get('items', []) if outfit else [])
        if not items:
            return outfit
            
        # Safely extract weather data
        temp = getattr(weather, 'temperature', None) or (weather.get('temperature', 70) if weather else 70) if hasattr(weather, 'get') else 70
        condition = getattr(weather, 'condition', None) or (weather.get('condition', 'clear') if weather else 'clear') if hasattr(weather, 'get') else 'clear'
        if isinstance(condition, str):
            condition = condition.lower()
        else:
            condition = 'clear'
        
        # Check for problematic combinations
        outfit_warnings = []
        items_to_remove = []
        
        # Get item types for combination analysis
        item_types = [(item.get('type', '') if item else '').lower() for item in items]
        item_names = [(item.get('name', '') if item else '').lower() for item in items]
        item_materials = [(item.get('material', '') if item else '').lower() for item in items]
        
        # Check for temperature-inappropriate combinations
        has_shorts = any('shorts' in t or 'short' in name for t, name in zip(item_types, item_names))
        has_heavy_jacket = any(('jacket' in t or 'coat' in t) and any(heavy in name for heavy in ['heavy', 'winter', 'wool']) for t, name in zip(item_types, item_names))
        has_tank_top = any('tank' in t or 'sleeveless' in t for t in item_types)
        has_sweater = any('sweater' in t or 'pullover' in t for t in item_types)
        has_wool = any('wool' in mat for mat in item_materials)
        has_thermal = any('thermal' in mat or 'fleece' in mat for mat in item_materials)
        
        # HARD RULES - Items that should be excluded for comfort
        for i, (item_type, item_name, item_material) in enumerate(zip(item_types, item_names, item_materials)):
            # Very hot weather exclusions
            if temp >= 85:
                if 'heavy' in item_name or 'winter' in item_name or 'wool' in item_material or 'thermal' in item_material:
                    if mode == "hard":
                        items_to_remove.append(i)
                        logger.info(f"🌡️ Hard rule: Excluding {item_name} for {temp}°F weather")
                    else:
                        outfit_warnings.append(f"Warning: {item_name} may be too warm for {temp}°F weather.")
            
            # Very cold weather exclusions  
            elif temp <= 40:
                if 'tank' in item_type or 'sleeveless' in item_type or 'short' in item_type:
                    if mode == "hard":
                        items_to_remove.append(i)
                        logger.info(f"🌡️ Hard rule: Excluding {item_name} for {temp}°F weather")
                    else:
                        outfit_warnings.append(f"Warning: {item_name} may be inadequate for {temp}°F weather.")
        
        # SOFT RULES - Combinations that should be warned about
        if temp <= 67 and has_shorts:
            outfit_warnings.append(f"Note: Shorts may be cool for {temp}°F weather - consider adding layers.")
        
        if temp >= 75 and has_heavy_jacket:
            outfit_warnings.append(f"Note: Heavy jacket may be too warm for {temp}°F weather.")
        
        if temp >= 80 and (has_sweater or has_wool or has_thermal):
            outfit_warnings.append(f"Note: Heavy layers may cause overheating in {temp}°F weather.")
        
        if temp <= 50 and has_tank_top:
            outfit_warnings.append(f"Note: Tank tops may be inadequate for {temp}°F {condition} conditions - consider adding layers.")
        
        # Apply hard rules if mode is "hard"
        if mode == "hard" and items_to_remove:
            # Remove items in reverse order to maintain indices
            for i in sorted(items_to_remove, reverse=True):
                removed_item = items.pop(i)
                logger.info(f"🗑️ Removed inappropriate item: {(removed_item.get('name', 'Unknown') if removed_item else 'Unknown')}")
            outfit['items'] = items
        
        # Add warnings to reasoning if any found
        if outfit_warnings:
            current_reasoning = outfit.get('reasoning', '')
            warning_text = "\n\n" + " ".join(outfit_warnings)
            outfit['reasoning'] = current_reasoning + warning_text
            logger.info(f"🌤️ Added {len(outfit_warnings)} weather combination warnings to outfit")
        
        return outfit
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to validate weather outfit combinations: {e}")
        return outfit
