# Semantic Expansion Testing Guide

This guide shows you how to verify that the semantic expansion actually improves outfit selection using your metadata.

---

## 🎯 What We're Testing

**Before Semantic Expansion:**
- "Business" request only matched items with exact "business" tag
- "Bold" mood only matched items with exact "bold" tag
- Many false negatives (good items rejected)

**After Semantic Expansion:**
- "Business" request matches: business, work, brunch, dinner, conference, etc.
- "Bold" mood matches: confident, daring, fierce, powerful, statement, etc.
- Fewer false negatives (more good items pass)

---

## 📊 Quick Visual Test (5 minutes)

Use a local frontend by default:

```bash
cd frontend
npm run dev
```

Then open `http://localhost:3000/personalization-demo`.

`/personalization-demo` is treated as an internal route. In production it is blocked unless `ENABLE_INTERNAL_DEBUG_PAGES=true` is explicitly set.

### Step 1: Test Traditional Filtering (Semantic OFF)

1. Go to: `http://localhost:3000/personalization-demo`
2. Set filters:
   - Occasion: **Business**
   - Style: **Classic**
   - Mood: **Bold**
3. **Disable** "Semantic (Compatible Styles)" → Traditional (Exact Match)
4. Click **"Debug Item Filtering"**
5. **Record the results:**
   - Total items: _____
   - Passed: _____
   - Rejected: _____
   - **Pass rate: _____%**

### Step 2: Test Semantic Filtering (Semantic ON)

1. Same filters (Business + Classic + Bold)
2. **Enable** "Semantic (Compatible Styles)"
3. Click **"Debug Item Filtering"**
4. **Record the results:**
   - Total items: _____
   - Passed: _____
   - Rejected: _____
   - **Pass rate: _____%**

### Step 3: Compare Results

**Expected Improvement:**
- Traditional: ~40-50 items pass (25-35%)
- Semantic: ~90-100 items pass (55-65%)
- **Improvement: +40-50 items (+30% pass rate)**

---

## 🔍 Detailed Item Analysis (10 minutes)

### Test Case 1: Button-Up Shirts Tagged "Brunch"

**What to look for in debug output:**

**Traditional Filtering (Semantic OFF):**
```
❌ "A long, solid, smooth button up shirt by GAP"
   Rejection: Occasion mismatch (item: brunch, dinner)
```

**Semantic Filtering (Semantic ON):**
```
✅ "A long, solid, smooth button up shirt by GAP"
   ✅ Semantic Match Found
   Occasions: brunch, dinner → matches Business
```

### Test Case 2: Items Tagged "Dinner"

**Traditional:**
```
❌ Dress shirts with "dinner" → REJECTED
```

**Semantic:**
```
✅ Dress shirts with "dinner" → ACCEPTED (business-appropriate)
```

### Test Case 3: Items Tagged "Smart Casual"

**Traditional:**
```
❌ Smart casual items → REJECTED (not exact "business")
```

**Semantic:**
```
✅ Smart casual items → ACCEPTED (business-compatible)
```

---

## 📈 Multiple Occasion Tests (15 minutes)

Test different occasions to see semantic expansion across the board:

### Test 1: Casual Occasion
**Filters:** Casual + Relaxed + Comfortable

| Mode | Items Passed | Expected |
|------|-------------|----------|
| Traditional | ~60 | Lower |
| Semantic | ~120+ | Much higher |

**Why:** "Casual" now matches brunch, dinner, vacation, everyday, weekend, etc.

---

### Test 2: Formal Occasion
**Filters:** Formal + Elegant + Sophisticated

| Mode | Items Passed | Expected |
|------|-------------|----------|
| Traditional | ~35 | Lower |
| Semantic | ~50 | Higher |

**Why:** "Formal" now matches wedding, gala, cocktail, evening, business, etc.

---

### Test 3: Beach Occasion
**Filters:** Beach + Casual + Playful

| Mode | Items Passed | Expected |
|------|-------------|----------|
| Traditional | ~40 | Lower |
| Semantic | ~60 | Higher |

**Why:** "Beach" now matches vacation, resort, tropical, summer, outdoor, etc.

---

## 🎨 Mood Expansion Tests (10 minutes)

### Test 1: Bold Mood
**Filters:** Business + Classic + **Bold**

**Look for items with these mood tags getting accepted:**
- ✅ confident
- ✅ powerful
- ✅ statement
- ✅ striking
- ✅ daring

**Traditional:** Only items with exact "bold" tag pass
**Semantic:** Items with any bold-related mood pass

---

### Test 2: Relaxed Mood
**Filters:** Casual + Minimalist + **Relaxed**

**Look for items with these mood tags getting accepted:**
- ✅ calm
- ✅ comfortable
- ✅ easy
- ✅ chill
- ✅ easygoing

---

### Test 3: Elegant Mood
**Filters:** Formal + Classic + **Elegant**

**Look for items with these mood tags getting accepted:**
- ✅ sophisticated
- ✅ refined
- ✅ chic
- ✅ polished
- ✅ graceful

---

## 📊 Quantitative Comparison (Railway Logs)

Check your Railway logs for these markers:

### Traditional Filtering:
```
🚩 FEATURE FLAG: Traditional filtering (default)
semantic_filtering=False
```

### Semantic Filtering:
```
🎯 FRONTEND CONTROL: Semantic filtering explicitly set to True
VERSION: 2025-10-11-COMPREHENSIVE
```

---

## 🧪 Automated Test Script

I'll create an automated script that runs both modes and compares results...

---

## 💡 What Success Looks Like

### Good Signs (Semantic is working):
1. **Higher pass rates** with semantic ON vs OFF
2. **Items with related occasions accepted** (e.g., "brunch" items for "Business")
3. **Items with related moods accepted** (e.g., "confident" items for "Bold")
4. **Version logs show** `2025-10-11-COMPREHENSIVE`
5. **Debug output shows** "✅ Semantic Match Found"

### Red Flags (Something's wrong):
1. **Same pass rate** for both modes
2. **No "Semantic Match Found" messages**
3. **Old version markers** in logs
4. **All items still rejected** even with semantic ON

---

## 🔧 Specific Examples to Test

### Example 1: Dress Shirt Tagged "Brunch, Dinner"
**Request:** Business + Classic + Bold
- **Traditional:** ❌ REJECTED (not exact "business")
- **Semantic:** ✅ ACCEPTED (brunch/dinner are business-appropriate)

### Example 2: Blazer Tagged "Smart Casual, Dinner"
**Request:** Business + Professional + Polished
- **Traditional:** ❌ REJECTED (not exact "business")
- **Semantic:** ✅ ACCEPTED (smart casual is business-compatible)

### Example 3: T-Shirt Tagged "Beach, Vacation"
**Request:** Business + Classic + Bold
- **Traditional:** ❌ REJECTED (correct - too casual)
- **Semantic:** ❌ REJECTED (correct - still too casual)

**This shows semantic is smart, not broken!**

---

## 📝 Recording Your Results

Create a simple table:

| Test Scenario | Traditional Pass Rate | Semantic Pass Rate | Improvement |
|--------------|----------------------|-------------------|-------------|
| Business + Classic + Bold | ___% | ___% | +___% |
| Casual + Relaxed + Comfortable | ___% | ___% | +___% |
| Formal + Elegant + Sophisticated | ___% | ___% | +___% |
| Beach + Casual + Playful | ___% | ___% | +___% |

**Expected average improvement: +25-35% pass rate**

---

## 🎯 Next Steps

1. Run the manual tests above (30 minutes)
2. Run the automated comparison script (see below)
3. Check Railway logs for version markers
4. Document your findings
5. If results are good → celebrate! 🎉
6. If results are poor → we'll debug together

---

## ⚠️ Troubleshooting

**If semantic doesn't seem to work:**

1. Check Railway logs for:
   ```
   VERSION: 2025-10-11-COMPREHENSIVE
   ```

2. Verify frontend is sending `semantic=true`:
   ```
   🎯 FRONTEND CONTROL: Semantic filtering explicitly set to True
   ```

3. Check debug output for:
   ```
   ✅ Semantic Match Found
   ```

4. If none of these appear → deployment might not have finished (wait 2-3 min)
