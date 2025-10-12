# Gym Occasion - Gap Analysis

## Problem
Gym occasion generates inappropriate outfits with polo shirts, casual shorts, and slides instead of athletic wear.

## Root Cause: Missing Blocks in Gym Logic

### Gap #1: POLO SHIRTS ARE NOT BLOCKED ❌
**Lines 2081-2094** in `robust_outfit_generation_service.py`

**Loungewear blocks:**
```python
'polo', 'henley', 'collared', 'collar',  # NO collars for loungewear
```

**Gym blocks:**
```python
'dress shirt', 'button up', 'button down', 'button-up', 'button-down'
# ❌ MISSING: 'polo', 'henley', 'collared' shirts!
```

**Result:** Polo shirts slip through gym filtering!

---

### Gap #2: CASUAL SHORTS WITHOUT ATHLETIC TAGS NOT PENALIZED ❌

**Current logic** (lines 2122-2130):
- Items WITH `athletic/gym/workout` tags → +1.5 bonus ✅
- Items WITH `casual` tags → +0.8 bonus
- Items WITHOUT athletic tags → No penalty!

**Problem:** "A loose, solid, crinkled casual shorts" has NO athletic tags but isn't penalized for gym occasion.

**Loungewear comparison:**
- Loungewear gives +1.2 for loungewear tags
- **BUT also penalizes items without appropriate tags**

---

### Gap #3: SLIDES/SANDALS ALLOWED FOR GYM ❌

**Lines 2104-2106**:
```python
athletic_shoe_keywords = ['sneaker', 'athletic', 'running', 'training', 'sport', 
                         'basketball', 'tennis', 'cross-trainer', 'gym shoe',
                         'slide', 'sandal', 'flip-flop']  # ❌ WRONG!
```

**Problem:** Slides and sandals are classified as "athletic shoes"!

**Fix needed:** Remove 'slide', 'sandal', 'flip-flop' from athletic shoes. These should get -2.0 penalty.

---

### Gap #4: NO WAISTBAND TYPE BOOST FOR GYM ❌

**Loungewear logic** (lines 2133-2148):
```python
if waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
    penalty += 1.5  # Perfect for loungewear
elif waistband_type == 'belt_loops':
    penalty -= 3.0  # Too structured for loungewear
```

**Gym logic:**
- ❌ NO waistband type checking!
- Athletic shorts with `elastic_drawstring` get NO bonus
- Casual shorts with `belt_loops` get NO penalty

---

### Gap #5: NO POSITIVE BOOST FOR ATHLETIC ITEMS WITHOUT TAGS ❌

**Current keyword scoring** (lines 2201-2205):
```python
if occasion_lower == 'athletic':
    if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'workout']):
        penalty += 0.6  # Boost for athletic keywords
```

**Problems:**
1. This only runs for `occasion_lower == 'athletic'`, NOT 'gym'!
2. Missing keywords: 'shorts', 'tank', 'jersey', 'sneaker', 'jogger'
3. No penalty for non-athletic items

---

### Gap #6: FORMALITY MAPPING INCONSISTENT ❌

**Waistband formality mapping** (lines 2240-2254):
```python
occasion_formality = {
    'loungewear': 0,
    'gym': 0,  # ✅ Gym is here
    'athletic': 1,  # ❌ But gym=0, athletic=1 is inconsistent!
    ...
}
```

**Problem:** Gym and Athletic should have SAME formality level (both should be 0).

---

## COMPREHENSIVE FIX NEEDED

### Fix #1: Add Missing Blocks to Gym
```python
gym_blocks = [
    # ... existing blocks ...
    'polo', 'henley', 'collared', 'collar',  # ADD THESE
    # Also add:
    'casual shorts', 'bermuda', 'khaki shorts'  # Block non-athletic shorts
]
```

### Fix #2: Remove Slides from Athletic Shoes
```python
athletic_shoe_keywords = ['sneaker', 'athletic', 'running', 'training', 'sport', 
                         'basketball', 'tennis', 'cross-trainer', 'gym shoe']
# REMOVED: 'slide', 'sandal', 'flip-flop'
```

### Fix #3: Add Waistband Type Logic for Gym
```python
# After line 2148, add gym waistband logic:
elif occasion_lower in ['gym', 'athletic', 'workout']:
    if waistband_type in ['elastic', 'drawstring', 'elastic_drawstring']:
        penalty += 1.5  # Perfect for gym/athletic
    elif waistband_type == 'belt_loops':
        penalty -= 2.0  # Belt loops = structured pants, bad for gym
```

### Fix #4: Fix Keyword Scoring for Gym
```python
# Line 2201 - change from 'athletic' to include 'gym':
if occasion_lower in ['athletic', 'gym', 'workout']:  # ADD GYM
    # Boost athletic keywords
    if any(word in item_name for word in ['athletic', 'sport', 'gym', 'running', 'workout', 'training', 'performance', 'jogger', 'track']):
        penalty += 0.6
    # Boost athletic items
    elif any(word in item_name for word in ['tank', 'sneaker', 'shorts', 'jersey']):
        penalty += 0.5
    # PENALIZE non-athletic items
    elif any(word in item_name for word in ['polo', 'button', 'dress', 'formal', 'oxford', 'blazer', 'slide']):
        penalty -= 0.5  # NEW: Penalty for non-athletic items
```

### Fix #5: Require Athletic Tags for Gym
```python
# After athletic occasion tag checks, add:
# If no athletic tags at all for gym occasion, apply penalty
if occasion_lower in ['gym', 'athletic', 'workout']:
    if not any(occ in item_occasion_lower for occ in ['athletic', 'gym', 'workout', 'sport', 'casual']):
        penalty -= 1.0  # Penalty for items with no relevant tags
```

### Fix #6: Align Gym with Athletic Formality
```python
occasion_formality = {
    'loungewear': 0,
    'gym': 0,  # Keep at 0
    'athletic': 0,  # CHANGE from 1 to 0 to match gym
```

---

## Summary of Gaps

| Gap | Loungewear | Gym (Current) | Gym (Should Be) |
|-----|------------|---------------|-----------------|
| **Blocks polo/henley** | ✅ Yes | ❌ No | ✅ Yes |
| **Blocks slides/sandals** | ✅ Yes (via formality) | ❌ No | ✅ Yes |
| **Waistband type boost** | ✅ Yes | ❌ No | ✅ Yes |
| **Penalizes non-athletic** | ✅ Yes | ❌ No | ✅ Yes |
| **Keyword scoring** | ✅ Comprehensive | ⚠️ Only for 'athletic' not 'gym' | ✅ Both |
| **Formality consistency** | ✅ Level 0 | ⚠️ Level varies | ✅ Level 0 |

---

## Impact

**Current behavior:**
- Gym outfits include polo shirts ❌
- Gym outfits include casual shorts instead of athletic shorts ❌  
- Gym outfits include slides instead of sneakers ❌

**After fixes:**
- Gym outfits will ONLY include athletic/workout clothing ✅
- Elastic waistband shorts will be preferred ✅
- Sneakers/athletic shoes will be required ✅
- Polo shirts and slides will be blocked ✅

---

## Files to Fix
1. `backend/src/services/robust_outfit_generation_service.py` - All 6 fixes needed

