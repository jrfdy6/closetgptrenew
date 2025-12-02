# 🎯 Complete Feedback Touchpoint Mapping

## All User Interaction Points Found

### 1. OUTFIT INTERACTIONS

#### A. Rating Outfits (Generate Page)
- **Location:** `frontend/src/app/outfits/generate/page.tsx`
- **Actions:**
  - Like button (`onLikeToggle`)
  - Dislike button (`onDislikeToggle`)
  - 1-5 star rating (`onRatingChange`)
  - Text feedback (`onFeedbackChange`)
- **Current Endpoint:** `/api/outfits/rate` ❌ **BROKEN (405 error)**
- **Learning Impact:** HIGH (explicit quality signal)

#### B. Wearing Outfits
- **Location:** Multiple places
  - Generate page: `handleWearOutfit()`
  - Outfit grid: `onWear`
- **Current Endpoint:** `/api/outfit-history/mark-worn`
- **Learning Impact:** HIGH (reveals actual usage)

#### C. Favoriting Outfits
- **Location:** Outfit cards
  - `onFavorite` in OutfitCard
- **Learning Impact:** MEDIUM (saves but may not wear)

---

### 2. ITEM INTERACTIONS

#### D. Favoriting Items
- **Location:** `frontend/src/app/wardrobe/page.tsx`
- **Actions:**
  - `onToggleFavorite` in WardrobeItemDetails
  - `handleToggleFavorite()`
- **Learning Impact:** MEDIUM (preference signal)

#### E. Item Wear Tracking
- **Location:** Wardrobe page
- **Actions:**
  - `onIncrementWear`
  - `handleWearIncrement()`
- **Learning Impact:** HIGH (actual usage data)

---

### 3. IMPLICIT INTERACTIONS

#### F. Outfit Generation
- **Impact:** User chose specific occasion/style/mood
- **Learning:** Track what they request most often

#### G. Outfit Views
- **Impact:** User viewed outfit (browsing history)
- **Learning:** Interest tracking

#### H. Creating Custom Outfits
- **Impact:** User manually selected items
- **Learning:** Reveals preferred combinations

---

## 🔄 SPOTIFY-STYLE INTEGRATION PLAN

### What Spotify Tracks:
| Spotify Action | Signal Strength | Your App Equivalent |
|----------------|-----------------|---------------------|
| Play song | HIGH | Wear outfit |
| Like song | HIGH | Rate outfit 5 stars |
| Add to playlist | MEDIUM | Favorite outfit |
| Skip song | HIGH | Dislike/1 star |
| Repeat listen | HIGH | Wear outfit multiple times |
| Add to library | MEDIUM | Favorite item |
| Create playlist | HIGH | Create custom outfit |
| Listen duration | MEDIUM | Outfit view time |

### Unified Learning System:

ALL interactions should update `user_preferences` in Firestore:

```
Rating outfit (5 stars) →
  preferred_styles += outfit.style
  preferred_colors += outfit.colors
  preferred_items += outfit.items
  total_feedback_count += 1
  
Wearing outfit →
  frequently_worn_items += outfit.items
  occasion_preferences[occasion] += outfit.style
  
Favoriting item →
  preferred_items += item.id
  preferred_colors += item.color
  
Disliking outfit (1-2 stars) →
  avoided_styles += outfit.style (if consistent pattern)
  avoided_combinations += item combinations
```

---

## 📋 INTEGRATION POINTS NEEDED

### Priority 1: CRITICAL (Fix Broken Rating)
✅ CREATE `/api/outfits/rate` endpoint
✅ Update user_preferences on rating
✅ Return learning confirmation

### Priority 2: HIGH (Wear Tracking)
✅ Verify `/api/outfit-history/mark-worn` updates preferences
✅ Add learning from wear patterns

### Priority 3: MEDIUM (Item Favorites)
✅ Integrate item favorite into preferences
✅ Learn color/style from favorited items

### Priority 4: MEDIUM (Custom Outfits)
✅ Learn from user-created outfit combinations
✅ Update preferred_combinations

---

## ❓ NEXT QUESTION

Ready for Question 6...
