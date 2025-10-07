from typing import List, Dict, Any, Optional, Tuple
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.style_engine import StyleAttributes, StyleDefinition, get_style_definition, validate_style_combination
from ..custom_types.visual_harmony import VisualHarmonyRule, VISUAL_HARMONY_RULES, ColorHarmonyType, SilhouetteBalance, TextureVariation

def analyze_item_style(item: ClothingItem) -> Dict[str, Any]:
    """Analyze the style attributes of a clothing item and return a detailed analysis."""
    analysis = {
        "style_tags": item.style,
        "style_compatibility": {},
        "style_suggestions": [],
        "style_warnings": []
    }

    # Get style definitions for each style tag
    style_definitions = []
    for style_tag in item.style:
        style_def = get_style_definition(style_tag)
        if style_def:
            style_definitions.append(style_def)

    # Analyze style compatibility
    for style_def in style_definitions:
        # Check compatible styles
        for compatible_style in style_def.compatible_styles:
            if compatible_style not in item.style:
                analysis["style_suggestions"].append(
                    f"Consider adding {compatible_style} style elements to complement {style_def.name}"
                )

        # Check incompatible styles
        for incompatible_style in style_def.incompatible_styles:
            if incompatible_style in item.style:
                analysis["style_warnings"].append(
                    f"Warning: {incompatible_style} style may conflict with {style_def.name}"
                )

    # Analyze style attributes
    if item.style_attributes:
        analysis["attributes"] = {
            "fit": item.style_attributes.fit.value if item.style_attributes.fit else None,
            "silhouette": item.style_attributes.silhouette.value if item.style_attributes.silhouette else None,
            "materials": [m.value for m in item.style_attributes.materials],
            "necklines": [n.value for n in item.style_attributes.necklines],
            "details": [d.value for d in item.style_attributes.details],
            "accessories": [a.value for a in item.style_attributes.accessories],
            "color_palette": item.style_attributes.color_palette,
            "layers": item.style_attributes.layers
        }

    return analysis

def find_compatible_items(
    item: ClothingItem,
    wardrobe: List[ClothingItem],
    min_compatibility: float = 0.5
) -> List[Tuple[ClothingItem, float]]:
    """Find items in the wardrobe that are compatible with the given item."""
    compatible_items = []
    
    for wardrobe_item in wardrobe:
        if wardrobe_item.id == item.id:
            continue
            
        compatibility_score = item.get_style_compatibility(wardrobe_item)
        if compatibility_score >= min_compatibility:
            compatible_items.append((wardrobe_item, compatibility_score))
    
    # Sort by compatibility score in descending order
    return sorted(compatible_items, key=lambda x: x[1], reverse=True)

def generate_style_recommendations(
    item: ClothingItem,
    wardrobe: List[ClothingItem]
) -> Dict[str, Any]:
    """Generate style recommendations based on the item and wardrobe."""
    recommendations = {
        "compatible_items": [],
        "style_suggestions": [],
        "color_suggestions": [],
        "accessory_suggestions": []
    }

    # Get compatible items
    compatible_items = find_compatible_items(item, wardrobe)
    recommendations["compatible_items"] = [
        {
            "item": compatible_item,
            "compatibility_score": score,
            "reasoning": f"Matches {item.name}'s style attributes"
        }
        for compatible_item, score in compatible_items[:5]  # Top 5 compatible items
    ]

    # Generate style suggestions based on style definitions
    for style_tag in item.style:
        style_def = get_style_definition(style_tag)
        if style_def:
            # Add style suggestions
            for compatible_style in style_def.compatible_styles:
                if compatible_style not in item.style:
                    recommendations["style_suggestions"].append(
                        f"Consider incorporating {compatible_style} elements to enhance your {style_def.name} look"
                    )

            # Add color suggestions
            if style_def.attributes.color_palette:
                recommendations["color_suggestions"].extend(
                    f"Try incorporating {color} to match the {style_def.name} aesthetic"
                    for color in style_def.attributes.color_palette
                    if color not in item.style_attributes.color_palette
                )

            # Add accessory suggestions
            if style_def.attributes.accessories:
                recommendations["accessory_suggestions"].extend(
                    f"Consider adding {accessory.value} to complete your {style_def.name} look"
                    for accessory in style_def.attributes.accessories
                    if accessory not in item.style_attributes.accessories
                )

    return recommendations

def validate_outfit_against_style(outfit_items: List[ClothingItem], target_style: str) -> Dict[str, Any]:
    """Validate an outfit against a specific style's visual harmony rules."""
    validation = {
        "is_compliant": True,
        "style_matches": [],
        "style_violations": [],
        "suggestions": [],
        "compatibility_score": 0.0,
        "partial_matches": [],
        "material_penalties": []
    }
    
    # Get the style rules
    style_rules = (VISUAL_HARMONY_RULES.get(target_style.lower() if VISUAL_HARMONY_RULES else None))
    if not style_rules:
        validation["is_compliant"] = False
        validation["style_violations"].append(f"Style '{target_style}' not found in visual harmony rules")
        return validation
    
    # Calculate similarity threshold for fuzzy matching
    SIMILARITY_THRESHOLD = 0.7
    MIN_REQUIRED_MATCHES = 0.6  # Require at least 60% of required elements
    
    # Track matches and partial matches for required elements
    required_matches = []
    partial_matches = []
    
    # Check required elements with fuzzy matching
    for required_element in style_rules.required_elements:
        element_matched = False
        best_match_score = 0.0
        best_match_item = None
        
        for item in outfit_items:
            # Check item name
            name_similarity = calculate_similarity(required_element.lower(), item.name.lower())
            # Check item type
            type_similarity = calculate_similarity(required_element.lower(), item.type.lower())
            # Check tags
            tag_similarities = [
                calculate_similarity(required_element.lower(), tag.lower())
                for tag in (item.metadata.get('tags', []) if item.metadata else [])
            ]
            tag_similarity = max(tag_similarities) if tag_similarities else 0.0
            
            # Get the best similarity score
            similarity = max(name_similarity, type_similarity, tag_similarity)
            
            if similarity > best_match_score:
                best_match_score = similarity
                best_match_item = item
        
        if best_match_score >= SIMILARITY_THRESHOLD:
            required_matches.append(required_element)
            validation["style_matches"].append(f"Found match for {required_element} in {best_match_item.name}")
        elif best_match_score >= 0.5:  # Lower threshold for partial matches
            partial_matches.append(required_element)
            validation["partial_matches"].append(f"Partial match for {required_element} in {best_match_item.name} (score: {best_match_score:.2f})")
    
    # Calculate required elements fulfillment
    total_required = len(style_rules.required_elements)
    matched_required = len(required_matches)
    partial_required = len(partial_matches)
    
    # Check if we have enough matches (including partial matches)
    if (matched_required + (partial_required * 0.5)) / total_required < MIN_REQUIRED_MATCHES:
        validation["is_compliant"] = False
        validation["style_violations"].append(
            f"Insufficient style matches. Found {matched_required} full matches and {partial_required} partial matches out of {total_required} required elements."
        )
    
    # Check forbidden elements with fuzzy matching
    for forbidden_element in style_rules.forbidden_elements:
        for item in outfit_items:
            # Check item name
            name_similarity = calculate_similarity(forbidden_element.lower(), item.name.lower())
            # Check item type
            type_similarity = calculate_similarity(forbidden_element.lower(), item.type.lower())
            # Check tags
            tag_similarities = [
                calculate_similarity(forbidden_element.lower(), tag.lower())
                for tag in (item.(metadata.get('tags', []) if metadata else []) if item.metadata else [])
            ]
            tag_similarity = max(tag_similarities) if tag_similarities else 0.0
            
            # If any similarity is above threshold, it's a violation
            if max(name_similarity, type_similarity, tag_similarity) >= SIMILARITY_THRESHOLD:
                validation["is_compliant"] = False
                validation["style_violations"].append(f"Contains forbidden element: {forbidden_element} (found in {item.name})")
    
    # Check color harmony with fuzzy matching
    outfit_colors = [item.color.lower() for item in outfit_items if item.color]
    for color in outfit_colors:
        for avoid_color in style_rules.avoid_colors:
            if calculate_similarity(color, avoid_color.lower()) >= SIMILARITY_THRESHOLD:
                validation["is_compliant"] = False
                validation["style_violations"].append(f"Contains avoided color: {color} (similar to {avoid_color})")
    
    # Check pattern rules with fuzzy matching
    for item in outfit_items:
        if item.metadata and 'pattern' in item.metadata:
            pattern = item.metadata['pattern'].lower()
            for forbidden_pattern in style_rules.pattern_rules['forbidden']:
                if calculate_similarity(pattern, forbidden_pattern.lower()) >= SIMILARITY_THRESHOLD:
                    validation["is_compliant"] = False
                    validation["style_violations"].append(f"Contains forbidden pattern: {pattern} (similar to {forbidden_pattern})")
    
    # Check material compatibility with scoring system
    material_penalty = 0
    max_material_penalty = 0.3  # Maximum penalty of 30% to compatibility score
    
    for i, item1 in enumerate(outfit_items):
        if not item1.metadata or 'material' not in item1.metadata:
            continue
            
        material1 = item1.metadata['material'].lower()
        
        # Check against style's material rules
        for avoid_material in style_rules.material_rules['avoid']:
            similarity = calculate_similarity(material1, avoid_material.lower())
            if similarity >= SIMILARITY_THRESHOLD:
                penalty = similarity * 0.1  # 10% penalty per avoided material
                material_penalty += penalty
                validation["material_penalties"].append(
                    f"Material '{material1}' in {item1.name} is similar to avoided material '{avoid_material}' (penalty: {penalty:.2f})"
                )
        
        # Check compatibility with other items
        for item2 in outfit_items[i+1:]:
            if not item2.metadata or 'material' not in item2.metadata:
                continue
                
            material2 = item2.metadata['material'].lower()
            
            # Check if materials are compatible
            is_compatible = False
            for compatible_group in style_rules.material_rules['compatible']:
                if material1 in compatible_group and material2 in compatible_group:
                    is_compatible = True
                    break
            
            if not is_compatible:
                similarity = calculate_similarity(material1, material2)
                if similarity < 0.3:  # Only penalize if materials are quite different
                    penalty = (1 - similarity) * 0.05  # 5% penalty per incompatible material pair
                    material_penalty += penalty
                    validation["material_penalties"].append(
                        f"Materials '{material1}' and '{material2}' may not work well together (penalty: {penalty:.2f})"
                    )
    
    # Calculate compatibility score with partial matches and material penalties
    total_checks = len(style_rules.required_elements)
    passed_checks = matched_required + (partial_required * 0.5)  # Count partial matches as half
    base_score = passed_checks / total_checks if total_checks > 0 else 1.0
    
    # Apply material penalty (capped at max_material_penalty)
    final_penalty = min(material_penalty, max_material_penalty)
    validation["compatibility_score"] = base_score * (1 - final_penalty)
    
    return validation

def validate_outfit_style(outfit_items: List[ClothingItem]) -> Dict[str, Any]:
    """Validate the style consistency of an outfit."""
    validation = {
        "is_consistent": True,
        "style_conflicts": [],
        "style_suggestions": [],
        "compatibility_scores": {},
        "style_validations": {}
    }

    # Get all unique styles from the outfit
    all_styles = set()
    for item in outfit_items:
        if hasattr(item, 'style'):
            all_styles.update(item.style)
    
    # Validate against each style
    for style in all_styles:
        style_validation = validate_outfit_against_style(outfit_items, style)
        validation["style_validations"][style] = style_validation
        
        if not style_validation["is_compliant"]:
            validation["is_consistent"] = False
            validation["style_conflicts"].extend(style_validation["style_violations"])
        
        validation["style_suggestions"].extend(style_validation["suggestions"])
        validation["compatibility_scores"][style] = style_validation["compatibility_score"]

    return validation 
