# Favorited Items - Complete Integration Guide

## ✅ YES! Favorited Items ARE Considered (Multiple Ways)

Favorited items are handled across **3 different dimensions** in the 6D scoring system:

---

## 📊 **How Favorited Items Get Scored**

### **Dimension 4: User Feedback Analysis (17% weight)**

**Location:** `robust_outfit_generation_service.py`, lines 3358-3372

```python
if item_id in favorited_items:
    # Check if worn this week
    worn_this_week = (recent_wears in last 7 days)
    
    if not worn_this_week:
        # BIG BOOST: Favorite not worn recently
        base_score += 0.40  # HIGHEST BOOST IN THE SYSTEM!
        logger.info(f"⭐💎 FAVORITE not worn this week → +0.40 (PRIORITY)")
    else:
        # Still boost, just less
        base_score += 0.15
        logger.debug(f"⭐ Favorite (worn this week) → +0.15")
```

**Impact:**
- ✅ Favorited items get **+0.40 boost** (largest single boost in the system!)
- ✅ If worn recently, still get **+0.15 boost**
- ✅ Applied to User Feedback score (17% of composite)

---

### **Dimension 4 (Continued): Wear Count Strategy**

**Location:** Lines 3377-3399

The system alternates between two modes:

#### **Mode A: Discovery (boost rarely-worn)**
```python
if boost_rare:  # Every other generation
    if item_wear_count == 0:
        base_score += 0.25  # Never worn
    elif item_wear_count <= 3:
        base_score += 0.15  # Lightly worn
    elif item_wear_count > 15:
        base_score -= 0.10  # Overused - PENALTY
```

#### **Mode B: Favorites (boost popular)**
```python
else:  # Alternate generations
    if item_wear_count >= 5 and item_wear_count <= 15:
        base_score += 0.20  # Sweet spot - proven favorites
    elif item_wear_count > 15:
        base_score += 0.10  # Very popular - still boost
    elif item_wear_count == 0:
        base_score -= 0.05  # Never worn - small penalty
```

**Impact:**
- ✅ System alternates between exploring new items and using favorites
- ✅ In "Favorites mode", popular items (5-15 wears) get +0.20
- ✅ Prevents stagnation by alternating strategies

---

### **Dimension 6: Diversity Boost (10% weight)**

**Location:** `diversity_filter_service.py`, lines 209-246

```python
def apply_diversity_boost(items, user_id, occasion, style, mood):
    for item in items:
        diversity_boost = 0.0
        
        # 1. NEW ITEM BOOST
        if item_usage == 0:
            diversity_boost += 0.3  # Never worn
        
        # 2. LIGHTLY USED BOOST
        elif item_usage < 3:
            diversity_boost += 0.1  # Rarely worn
        
        # 3. DISSIMILARITY BOOST
        avg_similarity = calculate_similarity_to_recent_outfits(item)
        diversity_boost += (1.0 - avg_similarity) * 0.2
        
        # 4. ROTATION SCHEDULE BOOST
        if item in rotation_schedule:
            diversity_boost += 0.2
        
        # Final score
        diversity_score = 1.0 + (diversity_boost * 1.5)
```

**Impact:**
- ✅ Items not in recent outfits get up to +0.2 boost
- ✅ Ensures variety even among favorited items
- ✅ 10% weight in composite score

---

## 🎯 **Example: Favorited Item Scoring**

Let's trace a **favorited blue shirt** through the system:

### **Scenario A: Favorite + Not Worn This Week + Lightly Used (3 wears)**

| Dimension | Score Calculation | Result |
|-----------|-------------------|--------|
| **User Feedback** | Base (0.0) + Favorite not worn (+0.40) + Lightly worn (+0.15) | **0.55** |
| × Weight (17%) | 0.55 × 0.17 | **0.094** |
| **Diversity** | Base (1.0) + Lightly used (+0.1 × 1.5) | **1.15** |
| × Weight (10%) | 1.15 × 0.10 | **0.115** |
| **Other Dimensions** | Body (0.8) + Style (0.85) + Weather (0.75) + Compat (0.9) | **3.30** |
| × Weights (63%) | (0.8×0.18) + (0.85×0.23) + (0.75×0.18) + (0.9×0.14) | **0.565** |
| **TOTAL COMPOSITE** | 0.094 + 0.115 + 0.565 | **0.774** |

**Result:** ✅ High score! Very likely to be selected!

---

### **Scenario B: Favorite + Worn Recently + Overused (20 wears)**

| Dimension | Score Calculation | Result |
|-----------|-------------------|--------|
| **User Feedback** | Base (0.0) + Favorite worn recently (+0.15) + Overused penalty (−0.10) | **0.05** |
| × Weight (17%) | 0.05 × 0.17 | **0.009** |
| **Diversity** | Base (1.0) + No boost (used recently) | **1.0** |
| × Weight (10%) | 1.0 × 0.10 | **0.100** |
| **Other Dimensions** | Body (0.8) + Style (0.85) + Weather (0.75) + Compat (0.9) | **3.30** |
| × Weights (63%) | Same as above | **0.565** |
| **TOTAL COMPOSITE** | 0.009 + 0.100 + 0.565 | **0.674** |

**Result:** ⚠️ Lower score - might not be selected this time (giving other items a chance)

---

## 🔄 **Smart Alternation Strategy**

The system alternates between two modes:

```
Generation 1: Discovery Mode (boost rarely-worn)
   → Explores wardrobe, tries new items
   → Favorited items still get +0.40 if not worn this week

Generation 2: Favorites Mode (boost popular)  
   → Uses proven favorites
   → Popular items (5-15 wears) get +0.20 boost

Generation 3: Discovery Mode
   → Back to exploring

...and so on
```

**This ensures:**
- ✅ You see favorited items regularly
- ✅ But not EVERY generation (prevents repetition)
- ✅ System balances exploration vs exploitation

---

## 📊 **Favorited Items Detection**

**How items are marked as favorited:**

```python
# Line 3286-3292
wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
wardrobe_docs = wardrobe_ref.stream()

for item in wardrobe_docs:
    if item.get('isFavorite') or item.get('favorite_score', 0) > 0.7:
        favorited_items.add(item.id)
```

**Checks:**
1. ✅ `isFavorite` field (boolean)
2. ✅ `favorite_score` field (>0.7 threshold)

---

## 🎯 **Key Benefits**

✅ **Favorited items get PRIORITY** (+0.40 boost if not worn recently)  
✅ **But system prevents overuse** (diversity penalty if worn too much)  
✅ **Smart alternation** between favorites and discovery  
✅ **Balances user preference** with wardrobe variety  
✅ **Recency awareness** (bigger boost if not worn this week)  

---

## 🔍 **In Railway Logs, You'll See:**

```
⭐ USER FEEDBACK ANALYZER: Scoring 82 items with learning algorithm
📊 Feedback data loaded: 25 rated items, 12 favorites

  ⭐💎 Blue Shirt: FAVORITE not worn this week → +0.40 (PRIORITY)
  🌱 Blue Shirt: Lightly worn (3) → +0.15
  
🎭 Applying diversity boost to prevent outfit repetition...
✅ Diversity boost applied to 82 items

🏆 Top 3 scored items (with diversity boost):
   1. Blue Shirt (favorited): 2.85 (diversity: 1.15)  ← HIGH SCORE!
   2. Black Pants: 2.12 (diversity: 0.85)
   3. White Shoes: 2.08 (diversity: 1.20)
```

---

## ✅ **Summary**

**Favorited items ARE considered across 3 dimensions:**

1. **User Feedback (17%):** +0.40 boost if not worn this week
2. **Wear Count Strategy:** Alternates between favoring popular items and exploring new ones
3. **Diversity (10%):** Ensures variety even among favorites

**Result:** You'll see your favorited items often, but the system prevents them from dominating every outfit! 🎨

