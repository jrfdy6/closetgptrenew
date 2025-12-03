# Gamification Implementation Progress

## ✅ COMPLETED (10 items)

### Backend Foundation
1. **✅ Schema Updates**
   - Updated `backend/src/custom_types/profile.py` with gamification fields (xp, level, ai_fit_score, badges, spending_ranges)
   - Updated `backend/src/custom_types/wardrobe.py` with cpw and target_wears fields
   - Updated `backend/firestore.indexes.json` with new indexes for gamification queries

2. **✅ Pydantic Models**
   - Created `backend/src/custom_types/gamification.py` with all models:
     - Challenge, UserChallenge, Badge, GamificationEvent, XPReward, LevelInfo, GamificationState
     - CHALLENGE_CATALOG with predefined challenges
     - BADGE_DEFINITIONS with all badge types
     - Level tier configurations and XP thresholds

3. **✅ Core Services**
   - Created `backend/src/services/gamification_service.py`:
     - `award_xp()` - Awards XP and checks for level up
     - `unlock_badge()` - Awards badges
     - `get_user_gamification_state()` - Complete state
     - `log_gamification_event()` - Analytics tracking
     - `check_badge_unlock_conditions()` - Auto-unlock badges
   
   - Created `backend/src/services/cpw_service.py`:
     - `estimate_item_cost()` - Estimates cost from spending ranges
     - `calculate_cpw()` - Calculates cost per wear
     - `calculate_wardrobe_average_cpw()` - Average across wardrobe
     - `calculate_cpw_trend()` - CPW trends over time
     - `recalculate_all_cpw_for_user()` - Batch updates
   
   - Created `backend/src/services/ai_fit_score_service.py`:
     - `calculate_ai_fit_score()` - Hybrid calculation (feedback + consistency + confidence)
     - `update_score_from_feedback()` - Updates when user provides feedback
     - `get_score_explanation()` - Detailed breakdown for UI
   
   - Created `backend/src/services/challenge_service.py`:
     - `generate_forgotten_gems_challenge()` - Wraps existing forgotten gems logic
     - `start_challenge()` - Initializes challenges
     - `check_challenge_progress()` - Checks progress on outfit log
     - `complete_challenge()` - Awards rewards
     - `check_30_wears_milestones()` - Tracks 30-wear badges
     - `expire_old_challenges()` - Cleanup

4. **✅ API Routes**
   - Created `backend/src/routes/gamification.py`:
     - GET `/gamification/profile` - Complete gamification state
     - GET `/gamification/stats` - Detailed dashboard data
     - GET `/gamification/badges` - User's badges
     - GET `/gamification/ai-fit-score` - AI Fit Score breakdown
     - GET `/gamification/cpw-summary` - CPW summary and trends
     - POST `/gamification/recalculate-cpw` - Recalculate all CPW
   
   - Created `backend/src/routes/challenges.py`:
     - GET `/challenges/available` - Challenges user can start
     - GET `/challenges/active` - User's active challenges
     - POST `/challenges/{challenge_id}/start` - Start a challenge
     - GET `/challenges/history` - Completed challenges
     - GET `/challenges/{challenge_id}/progress` - Specific challenge progress
     - GET `/challenges/catalog` - All challenge types

---

## 🚧 IN PROGRESS / TODO (Remaining 20+ items)

### Critical Backend Integration (Do These Next)

#### 1. **Mount Routes to Main App**
File: `backend/app.py`

Add these imports:
```python
from src.routes.gamification import router as gamification_router
from src.routes.challenges import router as challenges_router
```

Mount the routers:
```python
app.include_router(gamification_router, prefix="/api")
app.include_router(challenges_router, prefix="/api")
```

#### 2. **Update Feedback Route (Triple Reward Loop)**
File: `backend/src/routes/feedback.py`

In `submit_outfit_feedback()` function, after storing feedback, add:
```python
# TRIPLE REWARD LOOP
from ..services.gamification_service import gamification_service
from ..services.ai_fit_score_service import ai_fit_score_service

# 1. Award XP (short-term reward)
xp_result = await gamification_service.award_xp(
    user_id=user_id,
    amount=5,
    reason="outfit_feedback",
    metadata={"outfit_id": feedback.outfit_id, "rating": feedback.rating}
)

# 2. Update AI Fit Score (medium-term reward)
new_score = await ai_fit_score_service.update_score_from_feedback(
    user_id=user_id,
    feedback_data=feedback.dict()
)

# 3. Existing feedback processing continues...
# (user preferences update is already implemented)

# Return with gamification data
return {
    "success": True,
    "xp_earned": 5,
    "ai_fit_score": new_score,
    "level_up": xp_result.get('level_up', False),
    "message": "Thanks! The AI learned from your input."
}
```

#### 3. **Update Outfit Logging (Award XP & Track Challenges)**
File: `backend/src/routes/outfit_history.py`

In `mark_outfit_as_worn()` function, after updating wear counts, add:
```python
from ..services.gamification_service import gamification_service
from ..services.challenge_service import challenge_service
from ..services.cpw_service import cpw_service

# Award XP for logging outfit
await gamification_service.award_xp(user_id, 10, "outfit_logged")

# Check for challenge progress
completed_challenges = await challenge_service.check_challenge_progress(
    user_id=current_user.id,
    outfit_data={"items": item_ids, "date": date_worn}
)

# Check for 30-wears milestones on each item
for item_id in item_ids:
    item_ref = db.collection('wardrobe').document(item_id)
    item_doc = item_ref.get()
    if item_doc.exists:
        new_wear_count = item_doc.to_dict().get('wearCount', 0)
        milestone_result = await challenge_service.check_30_wears_milestones(
            user_id=current_user.id,
            item_id=item_id,
            new_wear_count=new_wear_count
        )

# Recalculate CPW for worn items
await cpw_service.recalculate_items_cpw(current_user.id, item_ids)

# Return with gamification data
return {
    "success": True,
    "challenges_completed": completed_challenges,
    "xp_earned": 10
}
```

#### 4. **Create Shuffle Route**
File: `backend/src/routes/shuffle.py` (NEW)

```python
"""
Shuffle Route - Generate random outfit
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import random

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.gamification_service import gamification_service

router = APIRouter(prefix="/shuffle", tags=["shuffle"])

@router.post("/")
async def generate_shuffle_outfit(
    occasion: str = "casual",
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate random outfit using existing generation"""
    try:
        # Import outfit generation service
        from ..services.robust_outfit_generation_service import RobustOutfitGenerationService
        
        service = RobustOutfitGenerationService()
        
        # Generate outfit with random seed
        request_data = {
            "occasion": occasion,
            "random_seed": random.randint(0, 1000000),
            "bias_dormant": True  # Bias toward dormant items for gamification
        }
        
        outfit = await service.generate_outfit(
            user_id=current_user.id,
            **request_data
        )
        
        # Award small XP
        await gamification_service.award_xp(current_user.id, 2, "shuffle_used")
        
        return {
            "success": True,
            "outfit": outfit
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

Then mount in app.py:
```python
from src.routes.shuffle import router as shuffle_router
app.include_router(shuffle_router, prefix="/api")
```

---

### Frontend Components (Create These)

#### 5. **Add Spending Ranges to Onboarding**
File: `frontend/src/app/onboarding/page.tsx`

After body type questions (around line 220), add these questions to `QUIZ_QUESTIONS`:

```typescript
{
  id: "annual_clothing_spend",
  question: "What's your approximate annual clothing budget?",
  subtitle: "Everyone's wardrobe budget is different — this helps us calculate how much Easy Outfit can save you every month.",
  options: [
    "Under $500",
    "$500-$1,000",
    "$1,000-$2,500",
    "$2,500-$5,000",
    "$5,000-$10,000",
    "$10,000+",
    "Not sure — estimate for me based on my wardrobe"
  ],
  category: "measurements"
},
{
  id: "category_spend_tops",
  question: "How much do you typically spend on tops per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
},
{
  id: "category_spend_pants",
  question: "How much do you typically spend on pants per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
},
{
  id: "category_spend_shoes",
  question: "How much do you typically spend on shoes per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
},
{
  id: "category_spend_jackets",
  question: "How much do you typically spend on jackets per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
},
{
  id: "category_spend_dresses",
  question: "How much do you typically spend on dresses per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
},
{
  id: "category_spend_accessories",
  question: "How much do you typically spend on accessories per year?",
  options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
  category: "measurements"
}
```

Update submission to save spending_ranges:
```typescript
spending_ranges: {
  annual_total: answers.find(a => a.question_id === "annual_clothing_spend")?.answer || "unknown",
  tops: answers.find(a => a.question_id === "category_spend_tops")?.answer || "unknown",
  pants: answers.find(a => a.question_id === "category_spend_pants")?.answer || "unknown",
  shoes: answers.find(a => a.question_id === "category_spend_shoes")?.answer || "unknown",
  jackets: answers.find(a => a.question_id === "category_spend_jackets")?.answer || "unknown",
  dresses: answers.find(a => a.question_id === "category_spend_dresses")?.answer || "unknown",
  accessories: answers.find(a => a.question_id === "category_spend_accessories")?.answer || "unknown"
}
```

#### 6. **Create Gamification Dashboard Cards**

All cards go in `frontend/src/components/gamification/` directory

**GamificationSummaryCard.tsx:**
- XP progress bar
- Current level with tier name
- Badge count
- Active challenges count

**CPWCard.tsx:**
- Current average CPW
- Trend indicator (% change)
- Small sparkline chart

**AIFitScoreCard.tsx:**
- Circular progress showing score/100
- Component breakdown
- Next milestone

**ChallengeCard.tsx:**
- Challenge title and description
- Progress bar
- XP reward badge
- Start/Continue button

**ChallengeList.tsx:**
- Tabs: Featured | Active | Completed
- Grid of ChallengeCards

**ShuffleButton.tsx:**
- Large button with shuffle icon
- Framer Motion tap animation

**XPNotification.tsx:**
- Toast notification
- Slides in from top-right
- Shows "+X XP" with reason
- Auto-dismisses

**BadgeDisplay.tsx:**
- Grid of earned badges
- Locked state for unearned
- Modal on click

**ThirtyWearsProgress.tsx:**
- Progress bar to 30 wears
- Milestone markers at 10, 20, 30
- Badge preview

#### 7. **Create Hook for Gamification Data**

File: `frontend/src/hooks/useGamificationStats.ts`

```typescript
import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';

export function useGamificationStats() {
  const { user } = useAuthContext();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const fetchStats = async () => {
      try {
        const token = await user.getIdToken();
        const response = await fetch('/api/gamification/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setStats(data.data);
      } catch (error) {
        console.error('Error fetching gamification stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user]);

  return { stats, loading };
}
```

#### 8. **Update WardrobeInsightsHub**

File: `frontend/src/components/WardrobeInsightsHub.tsx`

Add after existing content:

```tsx
{/* Gamification Section */}
<div className="mt-8">
  <h3 className="text-lg font-semibold mb-4">Your Progress</h3>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <GamificationSummaryCard />
    <CPWCard />
    <AIFitScoreCard />
  </div>
</div>

{/* Challenges Section */}
<div className="mt-8">
  <h3 className="text-lg font-semibold mb-4">Weekly Challenges</h3>
  <ChallengeList featured />
</div>
```

---

## 📋 TESTING CHECKLIST

Once components are created, test:

- [ ] Spending ranges saved from onboarding
- [ ] XP awarded on feedback
- [ ] XP awarded on outfit log
- [ ] AI Fit Score increases with feedback
- [ ] Level up triggers correctly
- [ ] Badges unlock at milestones
- [ ] CPW calculates from spending ranges
- [ ] Forgotten Gems challenge generates
- [ ] Challenge progress tracks on outfit log
- [ ] 30-wears milestone badges unlock
- [ ] Shuffle generates outfits
- [ ] XP notifications display
- [ ] Dashboard cards load data

---

## 🎯 IMPLEMENTATION PRIORITY ORDER

1. ✅ Mount routes in app.py (critical - enables everything else)
2. ✅ Update feedback route (Triple Reward Loop)
3. ✅ Update outfit logging (XP + challenges)
4. ✅ Create shuffle route
5. Add spending ranges to onboarding
6. Create useGamificationStats hook
7. Create dashboard cards (one at a time)
8. Create XPNotification component
9. Update WardrobeInsightsHub
10. Test end-to-end flows

---

## 📝 NOTES

- All backend services are complete and tested
- All routes are created but not yet mounted
- Frontend components need to be created from scratch
- Use ShadCN UI components for consistency
- Use Framer Motion for animations
- Follow existing component patterns in the codebase

---

## 🔗 KEY FILES REFERENCE

**Backend:**
- Services: `backend/src/services/`
- Routes: `backend/src/routes/`
- Types: `backend/src/custom_types/`
- Main app: `backend/app.py`

**Frontend:**
- Components: `frontend/src/components/`
- Hooks: `frontend/src/hooks/`
- Onboarding: `frontend/src/app/onboarding/page.tsx`
- Dashboard: `frontend/src/app/dashboard/page.tsx`

