# Onboarding Quiz Fixes - Implementation Plan

## 📋 **ISSUES TO FIX**

### 1. Dark Color Stripe Styling ❌
**Issue:** Dark stripe at bottom looks bad  
**Fix:** Update styling/remove dark border

### 2. Skin Tone Auto-Advance ❌
**Issue:** Slider advances immediately, can't play with it  
**Fix:** Add "Next" or "Confirm" button, only advance on click

### 3. Male Body Type Question Missing ❌
**Issue:** Male users don't see body type question  
**Fix:** Debug filtering logic (code exists, but not showing)

### 4. Annual Budget Question ❌
**Issue:** Redundant with category questions  
**Fix:** Remove "annual_clothing_spend" question entirely

### 5. Missing Spending Categories ❌
**Issue:** Need undergarments and swimwear  
**Fix:** Add 2 new spending questions

### 6. Question Order ❌
**Issue:** Spending questions in wrong place  
**Fix:** Reorder to: sizes → spending (8) → styles

### 7. Button Scrolling ❌
**Issue:** Buttons don't fit on screen (mobile/desktop)  
**Fix:** Resize columns, reduce padding, ensure no scrolling needed

### 8. Style Question Scrolling ❌
**Issue:** Every style question requires scrolling  
**Fix:** Make style options fit screen height

---

## ✅ **IMPLEMENTATION CHECKLIST**

**File:** `frontend/src/app/onboarding/page.tsx`

- [ ] Fix dark stripe styling
- [ ] Add Next button for skin tone slider
- [ ] Fix male body type filtering bug
- [ ] Remove annual_clothing_spend question
- [ ] Add category_spend_undergarments
- [ ] Add category_spend_swimwear  
- [ ] Update spending_ranges to include undergarments/swimwear
- [ ] Reorder questions array
- [ ] Fix button grid layout (no scrolling)
- [ ] Fix style question grid (fit to screen)

---

## 🎯 **EXPECTED FINAL ORDER**

1. Gender
2. Body type (male/female specific)
3. Skin tone (with Next button)
4. Height
5. Top size
6. Bottom size
7. Shoe size
8. Cup size (women/non-binary/prefer not to say)
9. **Tops spending**
10. **Pants spending**
11. **Shoes spending**
12. **Jackets spending**
13. **Dresses spending**
14. **Accessories spending**
15. **Undergarments spending** ← NEW
16. **Swimwear spending** ← NEW
17. Style questions (all fit on screen, no scrolling)

---

**Ready to implement all fixes now.**

