# Base Item Debugging Guide

## Problem
Base items are sometimes being filtered out during outfit generation, and you need to identify exactly where in the pipeline this is happening.

## Solution
I've implemented a comprehensive tracking system that monitors the base item through every stage of the outfit generation pipeline.

## What I Added

### 1. Base Item Tracker Utility (`backend/src/utils/base_item_debugger.py`)
A specialized debugging tool that:
- Tracks the base item through each pipeline stage
- Detects exactly where the base item is lost
- Provides detailed diagnostic reports
- Logs checkpoints with item counts and status

### 2. Integrated Tracking in Robust Generation Service
Added **8 tracking checkpoints** throughout the pipeline:

```
01_initial_wardrobe              → Starting wardrobe
02_after_hydration              → After item hydration
03_after_occasion_filter        → After occasion filtering  
04_after_style_mood_weather_filter  → After style/mood/weather filtering
05_after_score_initialization   → Item scores initialized
06_after_composite_scoring      → After composite score calculation
07_before_cohesive_composition  → Right before final composition
08_final_outfit                 → Final generated outfit
```

## How to Use

### Step 1: Trigger Outfit Generation with Base Item
Make a request with a `baseItemId`:

```json
POST /api/outfits/generate
{
  "occasion": "casual",
  "style": "modern",
  "baseItemId": "your-item-id-here",
  "wardrobe": [...],
  "weather": {...}
}
```

### Step 2: Check the Logs
The tracker will automatically log detailed information at each checkpoint:

```
✅ BASE ITEM TRACKER [01_initial_wardrobe]: 50 items, base_item_present=True Starting with 50 items
✅ BASE ITEM TRACKER [02_after_hydration]: 50 items, base_item_present=True After hydration
✅ BASE ITEM TRACKER [03_after_occasion_filter]: 30 items, base_item_present=True After occasion filter: casual
❌ BASE ITEM TRACKER [04_after_style_mood_weather_filter]: NOT FOUND in 15 items After style/mood/weather filter
🚨 BASE ITEM LOST: Was present in '03_after_occasion_filter', not found in '04_after_style_mood_weather_filter'
```

### Step 3: Read the Summary Report
At the end of generation, a complete summary is printed:

```
================================================================================
🔍 BASE ITEM TRACKING SUMMARY
================================================================================
Base Item ID: abc123
Ever Found: True
Last Seen: 03_after_occasion_filter
Lost At: 04_after_style_mood_weather_filter
--------------------------------------------------------------------------------
Pipeline Checkpoints (8):
  1. [01_initial_wardrobe] ✅ PRESENT - 50 items - Starting with 50 items
  2. [02_after_hydration] ✅ PRESENT - 50 items - After hydration
  3. [03_after_occasion_filter] ✅ PRESENT - 30 items - After occasion filter: casual
  4. [04_after_style_mood_weather_filter] ❌ MISSING - 15 items - After style/mood/weather filter
  5. [05_after_score_initialization] ❌ MISSING - 15 items - Item scores initialized
  6. [06_after_composite_scoring] ❌ MISSING - 15 items - After composite score calculation
  7. [07_before_cohesive_composition] ❌ MISSING - 15 items - Before cohesive composition
  8. [08_final_outfit] ❌ MISSING - 4 items - Final outfit generated with 4 items
================================================================================
🚨 DIAGNOSTIC: Base item was lost at stage '04_after_style_mood_weather_filter'
💡 SUGGESTION: Check filtering/scoring logic in that stage
================================================================================
```

## Common Issues and Fixes

### Issue 1: Lost at `03_after_occasion_filter`
**Problem:** Base item doesn't match the selected occasion  
**Location:** `backend/src/services/robust_outfit_generation_service.py` → `_get_occasion_appropriate_candidates()`  
**Fix:** Base item should be pre-approved and added to occasion candidates regardless of match

### Issue 2: Lost at `04_after_style_mood_weather_filter`
**Problem:** Base item filtered out by style/mood/weather matching  
**Location:** `backend/src/services/robust_outfit_generation_service.py` → `_filter_suitable_items_with_debug()`  
**Expected Behavior:** Lines 2212-2226 should pre-approve the base item  
**Check:** Look for logs saying "✅ BASE ITEM FILTER: Base item pre-approved"

### Issue 3: Lost at `05_after_score_initialization` or `06_after_composite_scoring`
**Problem:** Base item is being scored but getting a very low score  
**Location:** Various scoring functions in the service  
**Solution:** Base item should receive a score boost or bypass low-score filtering

### Issue 4: Lost at `08_final_outfit`
**Problem:** Base item made it through all filtering but wasn't selected in final composition  
**Location:** `backend/src/services/robust_outfit_generation_service.py` → `_cohesive_composition_with_scores()`  
**Expected Behavior:** Phase 0 (lines 5471-5498) should prioritize and add base item first

## Interpreting Scores

When you see checkpoint logs with scores:

```
✅ BASE ITEM TRACKER [06_after_composite_scoring]: Present with composite_score=0.45 After composite score calculation
```

**Score Interpretation:**
- **> 2.0** = Very high score (should definitely be selected)
- **1.0 - 2.0** = Good score (likely to be selected)
- **0.5 - 1.0** = Moderate score (may be selected)
- **0.0 - 0.5** = Low score (may be filtered out)
- **< 0.0** = Negative score (will be filtered out)

If the base item has a low score but should be included anyway, we need to add a special boost for base items in the scoring logic.

## Key Code Sections

### Base Item Pre-Approval (Filtering Stage)
```python
# File: backend/src/services/robust_outfit_generation_service.py
# Lines: 2212-2226

if context.base_item_id:
    logger.info(f"🎯 BASE ITEM FILTER: Looking for base item with ID: {context.base_item_id}")
    for item in context.wardrobe:
        if item_id == context.base_item_id:
            base_item_obj = item
            valid_items.append(base_item_obj)  # Pre-approved!
            logger.info(f"✅ BASE ITEM FILTER: Base item pre-approved")
            break
```

### Weather Filter Bypass
```python
# Lines: 2395-2400

# Always keep base item regardless of weather
if base_item_obj and getattr(item, 'id', None) == context.base_item_id:
    weather_appropriate_items.append(item)
    logger.info(f"✅ WEATHER FILTER: Base item bypasses weather filtering")
    continue
```

### Base Item Priority (Composition Stage)
```python
# Lines: 5471-5498 (Phase 0)

if context.base_item_id:
    logger.info(f"🎯 PHASE 0: Checking for base item: {context.base_item_id}")
    # Add base item FIRST before any other selection
    # Has fallback to search entire wardrobe if not in scored items
```

## Next Steps

1. **Run outfit generation** with a base item
2. **Check logs** for the tracking summary
3. **Identify** where the base item was lost
4. **Review** the corresponding code section
5. **Fix** the filtering/scoring logic in that specific stage

## Testing Scenarios

### Test 1: Weather-Inappropriate Base Item
```json
{
  "baseItemId": "wool-sweater-123",
  "weather": { "temperature": 95, "condition": "sunny" }
}
```
**Expected:** Base item included with warning message

### Test 2: Occasion-Mismatched Base Item
```json
{
  "baseItemId": "gym-shorts-123",
  "occasion": "formal",
  "style": "classic"
}
```
**Expected:** Base item included despite occasion mismatch

### Test 3: Style-Mismatched Base Item
```json
{
  "baseItemId": "punk-leather-jacket-123",
  "occasion": "business",
  "style": "professional"
}
```
**Expected:** Base item included as anchor piece

## Conclusion

The tracking system will show you **exactly** where and why the base item is being filtered out. Once you identify the problematic stage, you can implement the appropriate fix (pre-approval, score boost, bypass filter, etc.).

The key principle: **User-selected base items should ALWAYS be included**, regardless of algorithmic scoring or filtering, with appropriate warnings if they're not ideal for the context.

