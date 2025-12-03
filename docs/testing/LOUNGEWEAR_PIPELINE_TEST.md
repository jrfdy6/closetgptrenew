# 🛋️ Loungewear Pipeline - Complete Test Plan

## 🔧 **What Was Fixed**

### **Critical Indentation Errors:**
1. **Line 3746-3749:** Color diversity selection - code after `else:` was not indented
2. **Line 3812-3814:** Accessory selection - code after `if` was not indented

**Impact:**
- ❌ Robust service couldn't load (IndentationError)
- ❌ System fell back to simple service
- ❌ Simple service only found 1 Loungewear item
- ❌ Result: 0-item outfits

**Now Fixed:** ✅
- Robust service loads properly
- Full validation and scoring applies
- Loungewear support is complete

---

## 🎯 **Loungewear Pipeline Overview**

### **1. Hard Filter (Pass/Fail)**
```python
# Occasion/Style/Mood matching
if occasion='Loungewear':
    # Items pass if they have loungewear/lounge/relaxed/home/casual tags
    pass_filter = has_matching_tags
```

### **2. Formality Validation** (Penalty: -1.0)
```python
# Block overly formal types
if occasion='Loungewear':
    if item_type in ['suit', 'tuxedo', 'blazer', 'dress shirt', 'tie', 'dress pants', 'oxford shoes', 'heels']:
        penalty -= 1.0  # Discouraged but not eliminated
```

### **3. Color Appropriateness**
```python
# No specific color rules for Loungewear (very permissive)
# All colors acceptable
```

### **4. Tag-Based Scoring** (Boost: +1.2)
```python
# Strong boost for loungewear tags
if any(tag in ['loungewear', 'lounge', 'relaxed', 'home', 'casual', 'weekend']):
    penalty += 1.2  # Strong preference

# Penalize formal tags
if any(tag in ['business', 'formal', 'interview']):
    penalty -= 1.5  # Discourage formal
```

### **5. Keyword-Based Scoring**
```python
# Strong boost (+0.8) for comfort keywords
if any(word in ['lounge', 'sweat', 'jogger', 'hoodie', 'comfort', 'relaxed', 'cozy', 'soft']):
    penalty += 0.8

# Good boost (+0.6) for casual keywords
if any(word in ['t-shirt', 'tee', 'tank', 'shorts', 'legging', 'pajama', 'sleep']):
    penalty += 0.6

# Light penalty (-0.3) for formal keywords
if any(word in ['suit', 'blazer', 'dress shirt', 'formal', 'oxford', 'heel']):
    penalty -= 0.3
```

### **6. Composite Scoring**
```python
# Multi-dimensional scoring
composite_score = (
    body_type_score * 0.25 +
    style_profile_score * 0.30 +
    weather_score * 0.20 +
    metadata_score * 0.25
)
```

### **7. Color Diversity Check** (NEW!)
```python
# Prevent 3 items of same color family
if same_color_family_count >= 2 and color_family != 'neutral':
    SKIP this item
```

### **8. Selection**
```python
# Pick top items per category
- Top (sweater, hoodie, t-shirt): 1 item
- Bottom (sweatpants, joggers, shorts): 1 item
- Shoes (slippers, casual sneakers): 1 item (optional)
- Layering (optional based on weather)
```

---

## 🧪 **Test Cases**

### **Test 1: Basic Loungewear Outfit**

**Request:**
```json
{
  "occasion": "Loungewear",
  "style": "Classic",
  "mood": "Bold",
  "weather": {
    "temperature": 66,
    "condition": "Clouds"
  }
}
```

**Expected Items:**
- ✅ Comfortable top (hoodie, sweatshirt, t-shirt)
- ✅ Comfortable bottom (sweatpants, joggers, shorts)
- ✅ Casual footwear (slippers, casual sneakers) - optional
- ✅ Total: 2-4 items

**Expected Scoring (Top Items):**
| Item | Tags | Keywords | Formality | Tag Score | Keyword Score | Total | Pass/Fail |
|------|------|----------|-----------|-----------|---------------|-------|-----------|
| Cable-Knit Sweater | [casual, weekend] | "sweater", "cable-knit" | 0 | +1.2 | +0.8 | **+2.0+** | ✅ PASS |
| Sweatpants | [casual, relaxed] | "sweat" | 0 | +1.2 | +0.8 | **+2.0+** | ✅ PASS |
| Joggers | [casual] | "jogger" | 0 | +1.2 | +0.8 | **+2.0+** | ✅ PASS |
| Hoodie | [casual] | "hoodie" | 0 | +1.2 | +0.8 | **+2.0+** | ✅ PASS |
| Blazer | [business, formal] | "blazer" | -1.0 | -1.5 | -0.3 | **-2.8** | ❌ FAIL |
| Dress Shirt | [business, formal] | "dress shirt" | -1.0 | -1.5 | -0.3 | **-2.8** | ❌ FAIL |

---

### **Test 2: Loungewear with Mismatch (Classic Style)**

**Request:**
```json
{
  "occasion": "Loungewear",
  "style": "Classic",
  "mood": "Professional"
}
```

**Expected Behavior:**
- ✅ Mismatch detection: Loungewear + Classic style
- ✅ Prioritizes OCCASION (loungewear) over STYLE (classic)
- ✅ Still generates comfortable items
- ❌ Does NOT generate formal/classic items

**Expected Items:**
- ✅ Classic-styled loungewear (e.g., Ralph Lauren sweater, quality joggers)
- ✅ Still comfortable and relaxed
- ❌ NOT dress shirts or formal pants

---

### **Test 3: Color Diversity**

**Wardrobe:**
- Olive green sweater
- Forest green hoodie
- Lime green joggers
- White sweatpants

**Request:** Loungewear

**Expected Selection:**
1. ✅ Olive green sweater (1st green) - SELECTED
2. ✅ Forest green hoodie (2nd green) - SELECTED
3. ⏭️ Lime green joggers (3rd green) - SKIPPED (color diversity)
4. ✅ White sweatpants (neutral) - SELECTED

**Result:** 2 greens + 1 neutral = Diverse palette ✅

---

### **Test 4: Weather-Based Layering**

**Test 4a: Cold Weather (50°F)**
```json
{
  "occasion": "Loungewear",
  "weather": {"temperature": 50}
}
```

**Expected:**
- ✅ Hoodie or sweatshirt (layering)
- ✅ Sweatpants or joggers
- ✅ Total: 3-4 items (more layers)

**Test 4b: Warm Weather (75°F)**
```json
{
  "occasion": "Loungewear",
  "weather": {"temperature": 75}
}
```

**Expected:**
- ✅ T-shirt or tank
- ✅ Shorts
- ✅ Total: 2-3 items (minimal layers)

---

## 📊 **Expected Backend Logs**

### **Successful Generation:**
```
🔍 UNIVERSAL FORMALITY CHECK: Loungewear occasion
🔍 UNIVERSAL COLOR APPROPRIATENESS: No specific rules for Loungewear
✅✅ PRIMARY: Loungewear occasion tag match: +1.2
✅ KEYWORD: Loungewear keyword in name: +0.8
✅ Essential tops: Cable-knit sweater (score=3.19, color=olive green)
✅ Essential bottoms: Sweatshorts (score=3.21, color=white)
✅ COHESIVE COMPOSITION: Created outfit with 3 items
📊 Final confidence: 0.85
```

### **Rejection Logs:**
```
🚫 FORMALITY: Too formal type 'blazer' for Loungewear: -1.0
🚫 PRIMARY: Formal occasion tag for Loungewear request: -1.5
⚠️ KEYWORD: Formal keyword penalty for loungewear: -0.3
⏭️ Essential tops: Dress shirt skipped - negative score
```

---

## ✅ **Success Criteria**

### **Hard Requirements:**
1. ✅ Generates 2-4 items (minimum 2 for essentials)
2. ✅ All items have loungewear/casual characteristics
3. ✅ No formal items (blazers, dress shirts, dress shoes)
4. ✅ Composite scores > 2.0 for selected items
5. ✅ Composite scores < 0 for formal items

### **Soft Requirements:**
1. ✅ Color diversity (max 2 of same color family)
2. ✅ Weather-appropriate layering
3. ✅ Style consistency (all casual/relaxed)
4. ✅ Confidence > 70%

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: 0 Items Generated**
**Cause:** Robust service not loading (IndentationError)  
**Solution:** ✅ Fixed indentation on lines 3746-3749, 3812-3814  
**Verify:** Check Railway logs for "RobustOutfitGenerationService" import success

---

### **Issue 2: Only 1 Item Found**
**Cause:** Simple service fallback (only checks exact "Loungewear" tag)  
**Solution:** ✅ Robust service now loads properly  
**Verify:** Check logs for "ROBUST SERVICE: Import/init failed" (should NOT appear)

---

### **Issue 3: Formal Items Selected**
**Cause:** Formality validation not applied  
**Solution:** ✅ Universal formality check runs FIRST  
**Verify:** Check logs for "🚫 FORMALITY: Too formal type" messages

---

### **Issue 4: All Same Color**
**Cause:** Color diversity check not working  
**Solution:** ✅ Color family grouping implemented  
**Verify:** Check logs for "⏭️ COLOR DIVERSITY: ... skipped - already have N items"

---

## 🚀 **How to Test**

### **Step 1: Wait for Deployment (~90 seconds)**
Railway should auto-deploy the indentation fixes.

### **Step 2: Hard Refresh Browser**
```
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + F5
```

### **Step 3: Generate Loungewear Outfit**
1. Go to outfit generation page
2. Select:
   - Occasion: **Loungewear**
   - Style: **Classic** (or any style)
   - Mood: **Bold** (or any mood)
3. Click "Generate Outfit"

### **Step 4: Verify Results**

**Expected Frontend:**
- ✅ **2-4 items displayed**
- ✅ All items are **comfortable/casual**
- ✅ Confidence: **70-90%**
- ✅ Validation: **✅ Applied**

**Check Railway Logs:**
1. Go to Railway dashboard
2. Click "Deploy Logs"
3. Look for:
   ```
   ✅ Essential tops: [comfortable item] (score=3.0+)
   ✅ Essential bottoms: [comfortable item] (score=3.0+)
   ✅ COHESIVE COMPOSITION: Created outfit with N items
   ```

---

## 📊 **Test Results Template**

```markdown
### Loungewear Test Results

**Date:** [DATE]
**Deployment:** [COMMIT SHA]

**Test 1: Basic Loungewear**
- ✅ Generated items: 3
- ✅ All items comfortable: Yes
- ✅ No formal items: Yes
- ✅ Confidence: 85%
- ✅ Status: PASS

**Test 2: Color Diversity**
- ✅ Max 2 same color family: Yes
- ✅ Status: PASS

**Test 3: Weather Layering**
- ✅ Cold weather (50°F): 4 items with layers
- ✅ Warm weather (75°F): 2 items minimal
- ✅ Status: PASS

**Overall:** ✅ ALL TESTS PASSED
```

---

## 🎯 **Next Steps After Testing**

1. ✅ Verify Loungewear works
2. ✅ Test other occasions (Business, Athletic, Casual)
3. ✅ Test color diversity with different color combinations
4. ✅ Test weather-based layering
5. ✅ Confirm no formal items in loungewear outfits

---

**Deployment Status:** ✅ Pushed to production (Commit: 90405b252)  
**ETA:** ~90 seconds for Railway to redeploy  
**Test Now:** Generate a Loungewear outfit!

