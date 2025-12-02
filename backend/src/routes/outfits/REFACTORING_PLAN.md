# Outfits.py Refactoring Plan

## Current State
- **File**: `backend/src/routes/outfits.py`
- **Lines**: 7,513
- **Status**: Monolithic file with all functionality

## Target Structure

### Modules to Create:

1. **`scoring.py`** (~600 lines)
   - `calculate_outfit_score()`
   - `calculate_composition_score()`
   - `calculate_layering_score()`
   - `calculate_color_score()`
   - `calculate_material_score()`
   - `calculate_style_coherence_score()`
   - `calculate_wardrobe_intelligence_score()`
   - `calculate_outfit_performance_score()`
   - `calculate_wardrobe_diversity_bonus()`
   - `interpret_score()`
   - `get_score_grade()`

2. **`database.py`** (~400 lines)
   - `save_outfit()`
   - `get_user_wardrobe()`
   - `get_user_profile()`
   - `resolve_item_ids_to_objects()`
   - `get_user_outfits()`
   - `convert_firebase_url()`
   - `compute_created_at_ms()`
   - `normalize_created_at()`

3. **`generation_logic.py`** (~1500 lines)
   - `generate_outfit_logic()`
   - `generate_rule_based_outfit()`
   - `generate_fallback_outfit()`
   - `generate_intelligent_outfit_name()`
   - `generate_intelligent_reasoning()`
   - Helper functions for generation

4. **`helpers.py`** (~300 lines)
   - `is_layer_item()`
   - `get_item_category()`
   - `_generate_wardrobe_hash()`
   - `_generate_outfit_cache_key()`
   - `_validate_cached_outfit()`
   - `ensure_base_item_included()`

5. **`validation_extended.py`** (~500 lines)
   - `validate_outfit_composition()`
   - `validate_layering_rules()`
   - `validate_color_material_harmony()`
   - `validate_color_theory()`
   - `validate_material_compatibility()`
   - `analyze_color_palette()`
   - `analyze_material_combinations()`

6. **`routes.py`** (already exists, needs updating)
   - Main route handlers
   - Import from other modules

7. **`debug.py`** (already exists, needs updating)
   - Debug endpoints
   - Import from other modules

## Already Extracted:
- `models.py` - Pydantic models
- `utils.py` - Utility functions
- `validation.py` - Basic validation
- `styling.py` - Style filtering
- `weather.py` - Weather functions

## Main File (`outfits.py`)
After refactoring, should only contain:
- Router initialization
- Imports from modules
- Route registration

## Execution Order:
1. Create `scoring.py`
2. Create `database.py`
3. Create `helpers.py`
4. Create `validation_extended.py`
5. Create `generation_logic.py`
6. Update `routes.py` to use new modules
7. Update main `outfits.py` to import from modules
8. Test imports

