# Onboarding Quiz - Remaining Fixes

## ✅ **COMPLETED (Deployed)**

- ✅ Removed annual clothing budget question
- ✅ Added undergarments spending question  
- ✅ Added swimwear spending question
- ✅ Added combined body type for non-binary users (12 options)
- ✅ Updated backend to accept new spending categories

**Commit:** 94f9a774f (Pushed to main)

---

## 🔧 **REMAINING ISSUES TO FIX**

### Issue #1: Skin Tone Auto-Advance 🔴 HIGH PRIORITY
**Problem:** Slider advances immediately when moved - can't play with it

**Current Code (Line 1490-1494):**
```typescript
onChange={(e) => {
  const value = parseInt(e.target.value);
  const skinTone = `skin_tone_${value}`;
  handleAnswer(question.id, skinTone);  // ← Advances immediately!
}}
```

**Fix Needed:**
1. Change `onChange` to update local state only
2. Add a Next/Confirm button below slider
3. Button calls `handleAnswer` when clicked
4. Allow users to adjust slider freely before confirming

---

### Issue #2: Question Reordering 🟡 MEDIUM PRIORITY
**Problem:** Spending questions appear too early (before size questions)

**Current Order:**
1. Gender
2. Body type
3. Skin tone
4. Height
5. ❌ Spending questions (8) ← TOO EARLY
6. Weight
7. Top size
8. Bottom size
9. Cup size
10. Shoe size
11. Style questions

**Needed Order:**
1. Gender
2. Body type
3. Skin tone
4. Height
5. Weight
6. Top size ← Size questions
7. Bottom size
8. Cup size
9. Shoe size
10. ✅ Spending questions (8) ← MOVE HERE
11. Style questions

**Fix:** Reorder elements in `QUIZ_QUESTIONS` array

---

### Issue #3: Button Scrolling 🔴 HIGH PRIORITY
**Problem:** Option buttons don't fit on screen - requires scrolling on mobile AND desktop

**Affected Questions:**
- All text-based questions with 4+ options
- Gender (4 options)
- Height (6 options)
- Weight (10 options!)
- Size questions (9 options each)
- Spending questions (5 options each)

**Current Layout:**
```typescript
<button className="w-full py-5 px-6 ...">  // ← py-5 = 1.25rem padding = too tall
```

**Fix Needed:**
1. Reduce button padding: `py-5` → `py-3` (mobile), `py-4` (desktop)
2. Add grid layout for options: `grid-cols-2` on mobile for 6+ options
3. Reduce font size: `text-lg` → `text-base` (mobile)
4. Add `max-h-[80vh] overflow-hidden` to ensure fits

---

###Issue #4: Style Question Scrolling 🔴 HIGH PRIORITY
**Problem:** EVERY style question requires scrolling

**Current Issue:**
- Style question cards are too large
- Images take up too much space
- Text is too large
- Doesn't fit on screen

**Fix Needed:**
1. Reduce card size
2. Smaller images
3. Compact text
4. Grid layout optimization
5. Remove excessive padding

---

### Issue #5: Dark Stripe Styling 🟡 LOW PRIORITY
**Problem:** Dark color stripe at bottom looks bad

**Location:** Likely in the page wrapper or container styling

**Fix Needed:**
1. Find the dark stripe element
2. Remove or update color
3. Ensure consistent background

---

## 📝 **IMPLEMENTATION NOTES**

### File Size Warning:
`frontend/src/app/onboarding/page.tsx` is **2008 lines**

**Approach:**
- Make one fix at a time
- Test after each fix
- Commit incrementally

### Testing Requirements:
After each fix, test on:
- Mobile (375px width)
- Tablet (768px)
- Desktop (1920px)

---

## 🎯 **PRIORITY ORDER**

1. **HIGH:** Fix button scrolling (affects all questions)
2. **HIGH:** Fix style question scrolling (major UX issue)
3. **HIGH:** Fix skin tone auto-advance (user can't adjust)
4. **MEDIUM:** Reorder questions (spending after sizes)
5. **LOW:** Fix dark stripe (cosmetic)

---

**Would you like me to continue implementing these fixes?** They require careful UI/layout changes to the 2008-line onboarding file.

