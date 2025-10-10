# Filtering Diagnosis Guide

## 🎯 **The Issue: Same Outfits for Same Combination**

You're experiencing this pattern:
```
Casual/Classic/Comfortable → Outfit A
Casual/Classic/Comfortable → Outfit A (SAME!)
Casual/Classic/Comfortable → Outfit A (SAME!)
```

---

## 🔍 **Root Cause Analysis**

### **Problem #1: Strict Filtering**

The filtering requires items to match **BOTH** occasion AND style:

```python
# Line 1874-1876 in robust_outfit_generation_service.py
if ok_occ and ok_style:  # ← Requires BOTH!
    valid_items.append(item)
```

**For "Casual/Classic/Comfortable" to work:**
- Item must have "casual" in `occasion` tags ✅
- Item must have "classic" in `style` tags ✅

**If only 5 items match both**, you'll always get the same 5 items!

---

### **Problem #2: Diversity Boost May Not Be Strong Enough**

Even with diversity boost active, if filtering only returns 5 items:
```
Item 1: Score 2.8 (used 0x in Casual/Classic) → boost +0.30 = 3.10
Item 2: Score 2.7 (used 0x in Casual/Classic) → boost +0.30 = 3.00  
Item 3: Score 2.6 (used 0x in Casual/Classic) → boost +0.30 = 2.90
Item 4: Score 2.5 (used 0x in Casual/Classic) → boost +0.30 = 2.80
Item 5: Score 2.4 (used 0x in Casual/Classic) → boost +0.30 = 2.70

After first generation:
Item 1: Score 2.8 (used 1x in Casual/Classic) → boost +0.15 = 2.95
Item 2: Score 2.7 (used 1x in Casual/Classic) → boost +0.15 = 2.85
Item 3: Score 2.6 (used 1x in Casual/Classic) → boost +0.15 = 2.75
→ Top 3 still the same! (Items 1, 2, 3)
```

The penalty isn't strong enough if the base scores differ significantly.

---

## 🔧 **How to Diagnose**

### **Step 1: Use Frontend Debug Button**

1. Go to: https://closetgpt-frontend.vercel.app/personalization-demo
2. Set your problematic combination (e.g., Casual/Classic/Comfortable)
3. Click **"Debug Item Filtering"** button
4. Look for:
   - **Total items:** How many in wardrobe
   - **Passed filters:** How many items passed
   - **Hard rejected:** How many rejected

**Share this output with me!**

---

### **Step 2: Check Railway Logs**

Look for these lines in Railway Deploy Logs:
```
🔍 HARD FILTER: Results - X passed filters, Y rejected
🎭 DIVERSITY BOOST: Checking Z outfits with same combination
```

**If X (passed filters) is <15, filtering is TOO STRICT!**

---

## ✅ **Possible Solutions**

### **Solution A: Relax Filtering for Specific Combinations**

```python
# For combinations with <15 matching items, use OR instead of AND
if len(exact_matches) < 15:
    # Relax: Pass items that match occasion OR style
    if ok_occ or ok_style:
        valid_items.append(item)
```

### **Solution B: Stronger Diversity Penalty**

```python
# Current:
if same_combo_usage > 3:
    diversity_boost -= 0.15

# Stronger:
if same_combo_usage > 2:
    diversity_boost -= 0.40  # Much bigger penalty
elif same_combo_usage == 2:
    diversity_boost -= 0.25
elif same_combo_usage == 1:
    diversity_boost += 0.05  # Still boost if only used once
```

### **Solution C: Add More Metadata Tags**

If filtering is strict, ensure items have multiple tags:
```
Blue Shirt currently: occasion=["Casual"], style=["Preppy"]
Blue Shirt improved:  occasion=["Casual", "Business"], style=["Preppy", "Classic", "Professional"]
```

---

## 📋 **Next Step**

**Please share the debug output from the frontend button** and I'll tell you:
1. How many items are passing filters
2. Whether it's a filtering or diversity issue
3. The exact fix needed

**To use debug:**
1. Open personalization demo page
2. Select the problematic combination
3. Click "Debug Item Filtering"
4. Paste the results here

