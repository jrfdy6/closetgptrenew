# Total Value Extracted (TVE) Framework - Implementation Complete ✅

## Overview

The **Total Value Extracted (TVE)** framework has successfully replaced the Cost Per Wear (CPW) system. This new framework shifts from a cost-avoidance mindset to a **value-creation** approach, motivating users to extract maximum value from their wardrobe investment.

---

## 🎯 Core Concept

**TVE = Investment Value Recouped Through Usage**

- User's wardrobe is treated as an **investment**
- Each wear extracts **value** based on dynamic, personalized targets
- Progress is measured as **% of investment recouped**
- Encourages wearing the "forgotten 50-70%" of wardrobes

---

## 📐 Mathematical Foundation

### 1. **Dynamic CPW Target (Value Per Wear)**

Formula per category:
```
CPW_target = Annual Spending (S) / (Item Count (I) × Target Wear Rate (R))
```

**Example for Tops:**
- Annual Spending: $175
- Item Count: 10 tops
- Target Wear Rate: 12 wears/year
- **CPW_target = $175 / (10 × 12) = $1.75 per wear**

### 2. **Item-Level TVE**

```
TVE = Item Wears × Value Per Wear (V_W)
```

**Progress:**
- 1 wear: $1.75
- 5 wears: $8.75
- 20 wears: $35.00
- When TVE ≥ Estimated Cost → **"Full Value" achieved!**

### 3. **Target Wears Per Item**

```
Target Wears (T) = Estimated Item Cost (C) / CPW_target
```

### 4. **Annual Potential Range**

```
Low Potential = Total Wardrobe Cost × 30%
High Potential = Total Wardrobe Cost × 50%
```

Shows the value users can extract by increasing utilization from 30% to 50%.

---

## 🎮 Category-Specific Wear Rates

These constants define realistic annual wear targets:

| Category | Target Wears/Year | Rationale |
|----------|------------------|-----------|
| **Tops** | 12 | High rotation, everyday wear |
| **Pants** | 15 | Limited variety, frequent use |
| **Dresses** | 8 | Occasion-specific, less frequent |
| **Jackets** | 10 | Seasonal, essential |
| **Shoes** | 20 | High utility, limited pairs |
| **Activewear** | 15 | Regular active lifestyle |
| **Accessories** | 12 | Varied usage patterns |

---

## 🏗️ Implementation Architecture

### Backend Services

#### **1. TVE Service** (`backend/src/services/tve_service.py`)

**Key Functions:**
- `estimate_item_cost()` - Calculate estimated item cost from spending ranges
- `calculate_dynamic_cpw_target()` - Calculate CPW target for a category
- `initialize_item_tve_fields()` - Set up TVE fields when item is created
- `increment_item_tve()` - Add value when item is worn
- `calculate_wardrobe_tve()` - Get comprehensive TVE statistics
- `update_user_tve_cache()` - Update cached totals (future use)

**Constants:**
- `TARGET_WEAR_RATES` - Category-specific targets
- `RANGE_MIDPOINTS` - Spending range midpoints
- `CATEGORY_TO_SPENDING_KEY` - Item type → category mapping

#### **2. GWS Service** (`backend/src/services/gws_service.py`)

**Updated Formula:**
```
GWS = 40% Utilization + 30% TVE Progress + 20% AI Fit Score + 10% Revived Items
```

**TVE Progress Component (30 points):**
```python
tve_progress_ratio = min(1.0, total_tve / total_wardrobe_cost)
tve_component = tve_progress_ratio * 30
```

#### **3. Gamification Routes** (`backend/src/routes/gamification.py`)

**New Endpoints:**
- `GET /gamification/stats` - Returns TVE stats instead of CPW
- `GET /gamification/tve-summary` - Detailed TVE breakdown
- `POST /gamification/initialize-tve` - Batch initialize TVE for all items

**Removed:**
- `GET /gamification/cpw-summary` (replaced)
- `POST /gamification/recalculate-cpw` (replaced)

#### **4. Outfit History Routes** (`backend/src/routes/outfit_history.py`)

**Event-Triggered TVE Updates:**

When outfits are logged:
1. Increment wear counts (existing)
2. **NEW:** Increment TVE for each item
   - Get `value_per_wear` from item
   - If missing, initialize TVE fields
   - Add `value_per_wear` to `current_tve`
3. Log total TVE increment

**Endpoints Updated:**
- `POST /outfit-history/mark-worn`
- `POST /outfit-history/mark-today-suggestion-as-worn`

---

### Frontend Components

#### **1. TVECard Component** (`frontend/src/components/gamification/TVECard.tsx`)

**Displays:**
- **Total Value Extracted** (big green number)
- **% Investment Recouped** (progress bar with animation)
- **Annual Potential Range** ($X - $Y based on 30-50% utilization)
- **Lowest Progress Category** (actionable insight)

**Bonus Value Celebration:**
When TVE ≥ 100%, shows sparkle animation and "Generating bonus value!" message

#### **2. TypeScript Types** (`frontend/src/hooks/useGamificationStats.ts`)

```typescript
export interface TVEStats {
  total_tve: number;
  total_wardrobe_cost: number;
  percent_recouped: number;
  annual_potential_range: {
    low: number;
    high: number;
  };
  tve_by_category: {
    [category: string]: {
      tve: number;
      cost: number;
      percent: number;
    };
  };
  lowest_progress_category: {
    category: string;
    percent: number;
  } | null;
}
```

#### **3. Updated Pages**
- `/challenges` - Uses TVECard instead of CPWCard
- Dashboard (via `wardrobe-insights-hub.tsx`) - Uses TVECard

---

## 💾 Data Model

### Item Document Fields (Firestore `wardrobe` collection)

**New TVE Fields:**
```javascript
{
  // Existing fields...
  wearCount: number,
  lastWorn: timestamp,
  
  // NEW TVE Fields
  estimated_cost: number,        // Estimated item cost (C)
  value_per_wear: number,         // CPW_target for category (V_W)
  target_wears: number,           // Target wears to full value (T)
  current_tve: number            // Running total of value extracted
}
```

### User Document Fields (Firestore `users` collection)

**Cached TVE Totals (for future optimization):**
```javascript
{
  // Existing fields...
  xp: number,
  level: number,
  
  // NEW TVE Cache (optional, calculated on-demand for now)
  total_tve: number,
  total_wardrobe_cost: number,
  tve_by_category: {
    tops: number,
    pants: number,
    // ...
  }
}
```

---

## 🔄 Event Flow

### When User Logs an Outfit

```
1. POST /outfit-history/mark-worn
   ↓
2. Update outfit wear count
   ↓
3. Batch update item wear counts
   ↓
4. FOR EACH item:
   - Get value_per_wear
   - If missing → initialize TVE fields
   - Increment current_tve
   ↓
5. Award XP (10 XP for logging)
   ↓
6. Check challenge progress
   ↓
7. Return success + TVE increment logged
```

### When Dashboard Loads

```
1. GET /gamification/stats
   ↓
2. TVE Service calculates:
   - total_tve (sum of all items)
   - total_wardrobe_cost (sum of estimated costs)
   - percent_recouped
   - annual_potential_range
   - category breakdown
   ↓
3. Frontend displays in TVECard
```

---

## 🎨 UI/UX Improvements

### Psychological Motivation

**Old CPW Approach:**
- "You need to wear this more to lower the cost per wear"
- Focus: Minimize waste
- Feeling: Guilt

**New TVE Approach:**
- "You've extracted $50 in value so far!"
- Focus: Maximize gains
- Feeling: Achievement

### Visual Design

1. **Green color scheme** - Represents growth and value
2. **Big TVE number** - Primary focus, always increasing
3. **Progress bar** - Visual satisfaction of % recouped
4. **Animated shimmer** - Celebration of progress
5. **Potential range** - Aspirational goal
6. **Category target** - Specific action item

---

## 🧪 Testing Guide

### 1. **Initialize TVE for Existing Users**

```bash
curl -X POST https://closetgptrenew-production.up.railway.app/gamification/initialize-tve \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. **Verify TVE Calculation**

```bash
curl -X GET https://closetgptrenew-production.up.railway.app/gamification/tve-summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. **Test Outfit Logging**

1. Log an outfit
2. Check dashboard - TVE should increase
3. Verify item `current_tve` in Firestore

### 4. **Test GWS Integration**

```bash
curl -X GET https://closetgptrenew-production.up.railway.app/gamification/gws \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Verify `tve_progress` component shows in breakdown.

---

## 📊 Key Metrics to Monitor

### User Engagement
- TVE card interaction rate
- Average % recouped across users
- Category-specific utilization improvements

### System Performance
- TVE calculation time (should be <100ms)
- Event-triggered update latency
- Database query efficiency

### Business Impact
- Increased outfit logging frequency
- Wardrobe utilization rate (target: 40%+)
- User retention after seeing TVE progress

---

## 🚀 Future Enhancements

### Phase 2: Advanced Features

1. **Historical TVE Tracking**
   - Chart showing TVE growth over time
   - Month-over-month comparisons

2. **Category Deep Dive**
   - Detailed view per category
   - Underutilized item alerts

3. **Social Sharing**
   - "I've extracted $X in value!" achievements
   - Community leaderboards

4. **Smart Recommendations**
   - "Wear these 3 items to boost TVE by $15"
   - Category-specific targets

5. **User-Set Goals**
   - Custom annual utilization targets
   - Personalized wear rates

---

## 📝 Migration Notes

### From CPW to TVE

**No data migration required** - TVE fields are added on-the-fly:
1. Existing items continue to work
2. First wear after TVE deployment initializes fields
3. Users can manually trigger via `/initialize-tve` endpoint

### Backward Compatibility

- Old CPW service remains in codebase (commented)
- CPWCard component still exists (not exported)
- Easy rollback if needed

---

## ✅ Verification Checklist

- [x] Backend TVE service created with all calculations
- [x] GWS service updated to use TVE Progress (30%)
- [x] Gamification routes return TVE stats
- [x] TVECard component displays all metrics
- [x] TypeScript types updated
- [x] Challenges page uses TVECard
- [x] Dashboard uses TVECard
- [x] Outfit logging increments TVE (event-triggered)
- [x] Category-specific wear rates configured
- [x] Documentation complete

---

## 🎓 Formula Quick Reference

```
CPW_target = Annual Spending / (Item Count × Target Wear Rate)

TVE = Item Wears × CPW_target

Target Wears = Estimated Cost / CPW_target

% Recouped = (Total TVE / Total Wardrobe Cost) × 100%

Annual Potential = TWC × (30% to 50%)

GWS = 40% Utilization + 30% TVE Progress + 20% AI Fit + 10% Revived
```

---

## 📞 Support

For questions or issues:
1. Check logs: `backend/logs` and browser console
2. Verify Firestore data structure
3. Test with `/tve-summary` endpoint
4. Review this documentation

---

**Implementation Date:** December 4, 2025  
**Status:** ✅ Complete and Ready for Production  
**Framework Version:** 1.0.0

