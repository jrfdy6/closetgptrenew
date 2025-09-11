from typing import List, Dict, Optional, Tuple
import time
from ..custom_types.wardrobe import ClothingItem, Season
from ..custom_types.profile import UserProfile
from ..services.validation_orchestrator import ValidationResult, ValidationStep

# Material compatibility rules
COMPATIBLE_MATERIALS: Dict[str, List[str]] = {
    'cotton': ['denim', 'linen', 'wool', 'silk'],
    'denim': ['cotton', 'leather', 'wool'],
    'wool': ['cotton', 'silk', 'cashmere'],
    'silk': ['cotton', 'wool', 'cashmere'],
    'leather': ['denim', 'cotton', 'wool'],
    'linen': ['cotton', 'silk'],
    'cashmere': ['wool', 'silk', 'cotton']
}

# Weather-appropriate materials
WEATHER_MATERIALS: Dict[str, List[str]] = {
    'winter': ['wool', 'cashmere', 'leather', 'thick_cotton'],
    'summer': ['cotton', 'linen', 'silk', 'light_wool'],
    'spring': ['cotton', 'linen', 'light_wool'],
    'fall': ['wool', 'cotton', 'denim', 'leather']
}

# Skin tone color compatibility
SKIN_TONE_COLORS: Dict[str, List[str]] = {
    'warm': ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red'],
    'cool': ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald'],
    'neutral': ['navy', 'gray', 'white', 'black', 'beige', 'mauve']
}

# Body type fit recommendations - inclusive and positive
BODY_TYPE_FITS: Dict[str, List[str]] = {
    'hourglass': ['fitted', 'relaxed', 'wrap', 'belted'],
    'pear': ['fitted_top', 'relaxed_bottom', 'a_line', 'bootcut'],
    'apple': ['relaxed_top', 'fitted_bottom', 'empire_waist', 'v_neck'],
    'rectangle': ['fitted', 'oversized', 'layered', 'belted'],
    'inverted_triangle': ['relaxed_top', 'fitted_bottom', 'wide_leg', 'a_line'],
    'round_apple': ['relaxed_top', 'fitted_bottom', 'empire_waist', 'v_neck'],
    'plus_size': ['relaxed', 'fitted', 'wrap', 'a_line', 'empire_waist'],
    'plus_curvy': ['fitted', 'wrap', 'belted', 'a_line'],
    'plus_hourglass': ['fitted', 'wrap', 'belted', 'v_neck'],
    'plus_apple': ['relaxed_top', 'empire_waist', 'v_neck', 'a_line'],
    'athletic': ['fitted', 'relaxed', 'structured', 'tailored'],
    'petite': ['fitted', 'high_waisted', 'vertical_lines', 'monochrome'],
    'tall': ['long_lines', 'maxi', 'layered', 'statement'],
    'slim': ['fitted', 'layered', 'textured', 'structured'],
    'muscular': ['relaxed', 'fitted', 'stretchy', 'tailored']
}

def validate_material_compatibility(items: List[ClothingItem]) -> ValidationResult:
    start_time = time.time()
    warnings = []
    materials = [item.metadata.visualAttributes.material.lower() if item.metadata and item.metadata.visualAttributes and item.metadata.visualAttributes.material else 'unknown' for item in items]

    for i in range(len(materials)):
        for j in range(i + 1, len(materials)):
            material1 = materials[i]
            material2 = materials[j]

            if material1 == 'unknown' or material2 == 'unknown':
                continue

            compatible_with1 = COMPATIBLE_MATERIALS.get(material1, [])
            compatible_with2 = COMPATIBLE_MATERIALS.get(material2, [])

            if material2 not in compatible_with1 and material1 not in compatible_with2:
                warnings.append(f"Material compatibility warning: {material1} and {material2} may not work well together")

    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.FORM_COMPLETENESS,
        is_valid=len(warnings) == 0,
        errors=[],
        warnings=warnings,
        metadata={"materials": materials},
        duration=duration
    )

def validate_weather_appropriateness(items: List[ClothingItem], season: Season) -> ValidationResult:
    start_time = time.time()
    warnings = []
    season_materials = WEATHER_MATERIALS.get(season.value.lower(), [])

    for item in items:
        if not item.metadata or not item.metadata.visualAttributes:
            continue
        material = item.metadata.visualAttributes.material
        if material and material.lower() not in season_materials:
            warnings.append(f"{item.name} ({material}) may not be appropriate for {season.value} weather")

    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.WEATHER_COMPATIBILITY,
        is_valid=len(warnings) == 0,
        errors=[],
        warnings=warnings,
        metadata={"season": season.value, "season_materials": season_materials},
        duration=duration
    )

def validate_skin_tone_compatibility(items: List[ClothingItem], user_profile: UserProfile) -> ValidationResult:
    start_time = time.time()
    warnings = []
    skin_tone = user_profile.skinTone.lower() if user_profile.skinTone else None

    if not skin_tone:
        return ValidationResult(
            step=ValidationStep.FORM_COMPLETENESS,
            is_valid=True,
            errors=[],
            warnings=[],
            metadata={"skin_tone": None},
            duration=0.0
        )

    recommended_colors = SKIN_TONE_COLORS.get(skin_tone, [])
    for item in items:
        color = getattr(item, 'color', '').lower() if hasattr(item, 'color') else ''
        if not any(rec_color in color for rec_color in recommended_colors):
            warnings.append(f"{item.name} ({color}) may not complement your {skin_tone} skin tone")

    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.FORM_COMPLETENESS,
        is_valid=len(warnings) == 0,
        errors=[],
        warnings=warnings,
        metadata={"skin_tone": skin_tone, "recommended_colors": recommended_colors},
        duration=duration
    )

def validate_body_type_fit(items: List[ClothingItem], user_profile: UserProfile) -> ValidationResult:
    start_time = time.time()
    warnings = []
    body_type = user_profile.bodyType.lower() if user_profile.bodyType else None
    fit_preference = user_profile.fitPreference.lower() if user_profile.fitPreference else None

    if not body_type:
        return ValidationResult(
            step=ValidationStep.BODY_TYPE_COMPATIBILITY,
            is_valid=True,
            errors=[],
            warnings=[],
            metadata={"body_type": None},
            duration=0.0
        )

    recommended_fits = BODY_TYPE_FITS.get(body_type, [])
    for item in items:
        if not item.metadata or not item.metadata.visualAttributes:
            continue
        item_fit = item.metadata.visualAttributes.fit
        if item_fit:
            item_fit = item_fit.lower()
            if item_fit not in recommended_fits:
                warnings.append(f"{item.name} ({item_fit} fit) may not be ideal for your {body_type} body type")
            if fit_preference and item_fit != fit_preference:
                warnings.append(f"{item.name} ({item_fit} fit) doesn't match your preferred {fit_preference} fit")

    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.BODY_TYPE_COMPATIBILITY,
        is_valid=len(warnings) == 0,
        errors=[],
        warnings=warnings,
        metadata={"body_type": body_type, "recommended_fits": recommended_fits},
        duration=duration
    )

def validate_gender_appropriateness(items: List[ClothingItem], user_profile: UserProfile) -> ValidationResult:
    start_time = time.time()
    warnings = []
    gender = user_profile.gender.lower() if user_profile.gender else None

    if not gender:
        return ValidationResult(
            step=ValidationStep.FORM_COMPLETENESS,
            is_valid=True,
            errors=[],
            warnings=[],
            metadata={"gender": None},
            duration=0.0
        )

    for item in items:
        if not item.metadata or not item.metadata.visualAttributes:
            continue
        item_gender = item.metadata.visualAttributes.genderTarget
        if item_gender and item_gender.lower() != 'unisex' and item_gender.lower() != gender:
            warnings.append(f"{item.name} is targeted for {item_gender} but your preference is {gender}")

    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.FORM_COMPLETENESS,
        is_valid=len(warnings) == 0,
        errors=[],
        warnings=warnings,
        metadata={"gender": gender},
        duration=duration
    )

def validate_outfit_compatibility(
    items: List[ClothingItem],
    user_profile: UserProfile,
    season: Season
) -> ValidationResult:
    start_time = time.time()
    results = [
        validate_material_compatibility(items),
        validate_weather_appropriateness(items, season),
        validate_skin_tone_compatibility(items, user_profile),
        validate_body_type_fit(items, user_profile),
        validate_gender_appropriateness(items, user_profile)
    ]

    all_warnings = [warning for result in results for warning in result.warnings]
    is_valid = all(result.is_valid for result in results)
    duration = time.time() - start_time
    return ValidationResult(
        step=ValidationStep.FORM_COMPLETENESS,
        is_valid=is_valid,
        errors=[],
        warnings=all_warnings,
        metadata={},
        duration=duration
    ) 