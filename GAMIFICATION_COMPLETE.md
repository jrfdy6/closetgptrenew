# Easy Outfit App - Complete Gamification & Ecosystem Engineering System

## 🎮 Overview

A comprehensive gamification system that transforms wardrobe management into an engaging, rewarding experience. This includes both the original gamification features (XP, Levels, Badges, Challenges) and the **Ecosystem Engineering** mechanics (Streaks, Style Tokens, Gacha, Roles) designed to create psychological engagement hooks.

### Core Principles
- **Leverage Existing Systems:** Wraps Forgotten Gems, feedback, and analytics
- **Triple Reward Loop:** XP (immediate) + AI Fit Score (progress) + Better recommendations (value)
- **Ecosystem Engineering:** Variable rewards, status progression, and loss aversion mechanics
- **Integrated Experience:** Gamification lives within existing UI, not separate pages
- **Non-Invasive CPW:** Uses spending ranges instead of per-item prices
- **Engagement-Only Economy:** Tokens are earned through gameplay, never purchased

---

## Access by Plan (Gating)

| Feature | FREE | PRO | PREMIUM |
| --- | --- | --- | --- |
| Gamification summary (levels, streaks, challenges) | Visible | Visible | Visible |
| 30-Wears Progress | Visible | Visible | Visible |
| Analytics (CPW, Utilization, GWS, TVE, AI Fit Score details) | Blurred (soft gated) | Full | Full |
| Flat Lays | 1/week | 5/week | Unlimited |

Free-user nudge shown on the Gamification Summary: *"You're leveling up—unlock the 'why' behind your gains with PRO analytics."*

PRO and PREMIUM unlock all analytics. Blurring is used for FREE to create a curiosity gap; data still loads to avoid extra API branching.

---

## 🌟 Core Gamification Features

### 1. Experience Points (XP) & Leveling

**XP Earning:**
- **+10 XP** for logging an outfit (with streak multiplier)
- **+5 XP** for rating an outfit
- **+2 XP** for using "Dress Me" shuffle
- **+75-300 XP** for completing challenges

**Streak Multipliers:**
- Daily streak maintenance applies multiplier to XP rewards
- Max multiplier: **3.0x** (at 20+ day streak)
- Formula: `1.0 + (streak_days * 0.1)` capped at 3.0

**Level Tiers:**
- **Novice** (Level 1-4): 0-2,999 XP
- **Stylist** (Level 5-9): 3,000-6,999 XP
- **Curator** (Level 10-14): 7,000-11,999 XP
- **Connoisseur** (Level 15+): 12,000+ XP

### 2. AI Fit Score (0-100)

Measures how well the AI understands your style.

**Components:**
- **Feedback Count** (40 points max): More ratings = higher score
- **Preference Consistency** (30 points): Clear preferences = higher score
- **Prediction Confidence** (30 points): Successful outfits = higher score

**Milestones:**
- **25+ score**: Learning your style
- **50+ score**: AI Apprentice
- **75+ score**: AI Master

### 3. Cost Per Wear (CPW) Tracking

Calculates value from your wardrobe using spending ranges.

**Formula:** `Estimated Cost / Wear Count`

**Spending Ranges** (collected in onboarding):
- Annual total: Under $500 to $10,000+
- By category: Tops, Pants, Shoes, Jackets, Dresses, Accessories
- If "Not sure": Auto-estimated from wardrobe

**Insights:**
- Average CPW across wardrobe
- CPW trends (30-day comparison)
- Per-item CPW tracking

### 4. Challenges

All challenges now award both **XP and Style Tokens** (matching amounts).

#### Forgotten Gems (Weekly)
- **Goal:** Wear 2 items dormant for 60+ days
- **Reward:** +75 XP + 75 Tokens, "Hidden Gem Hunter" badge
- **Auto-generated:** Uses existing forgotten gems system

#### 30-Wears Challenge (Always Active)
- **Goal:** Wear any item 30 times
- **Rewards:**
  - 30 wears: Bronze badge + 100 XP + 100 Tokens
  - 60 wears: Silver badge + 150 XP + 150 Tokens
  - 100 wears: Gold badge + 250 XP + 250 Tokens

#### Featured Weekly Challenges
- **Color Harmony:** Create 3 outfits with complementary colors (+120 XP + 120 Tokens)
- **Versatile Styling:** Outfit for multiple contexts (+100 XP + 100 Tokens)
- Rotates weekly

**All Challenge Rewards Include Tokens:**
- Token amounts match XP rewards for each challenge
- Awarded automatically upon challenge completion

### 5. Badges (12 Types)

**Onboarding:**
- Starter Closet (10 items)
- Closet Cataloger (50 items)

**Usage:**
- Hidden Gem Hunter (Complete Forgotten Gems)
- Treasure Hunter (5x Forgotten Gems)

**Sustainability:**
- Sustainable Style Bronze/Silver/Gold (30/60/100 wears)

**Engagement:**
- Style Contributor (25 ratings)
- AI Trainer (100 ratings)

**Mastery:**
- Color Master, Weather Warrior, Versatile Pro

### 6. "Dress Me" Shuffle
- One-click random outfit generation
- Uses existing robust outfit generation with random seed
- Awards +2 XP
- Instant gratification feature

---

## 🎰 Ecosystem Engineering Features

### 7. Daily Streaks & Loss Aversion

**Mechanism:**
- Track consecutive days of logging outfits
- Streak breaks if more than 24 hours pass without logging
- Fear of losing streak multiplier drives daily engagement

**Multipliers:**
- **Day 1-7:** 1.0x - 1.7x multiplier
- **Day 8-14:** 1.8x - 2.4x multiplier  
- **Day 15+:** 2.5x - 3.0x multiplier (capped)

**Rewards:**
- Streak bonus tokens: +25 tokens per day maintained
- XP multiplier applied to all XP awards
- Longest streak tracking for personal records

**Initialization:**
- Streak data created automatically on first outfit log
- Default: 0 streak, 1.0x multiplier

### 8. Style Tokens & Gacha System (Variable Ratio Reinforcement)

**Token Earning:**
- **+50 tokens** base for logging an outfit
- **+75-300 tokens** for completing challenges (matches XP)
- **+25 tokens** streak bonus per day
- **+10 tokens** for providing feedback
- Role multipliers apply (see Roles section)

**Token Multipliers (by Role):**
- **Lurker:** 1.0x (base)
- **Scout:** 1.2x (20% bonus)
- **Trendsetter:** 1.5x (50% bonus)

**Gacha Pull System:**
- **Cost:** 500 tokens per pull
- **Variable Rewards:**
  - **COMMON (70%):** +50 XP bonus for next outfit log
  - **RARE (25%):** Advanced styling insight (color combo, pattern mixing)
  - **LEGENDARY (5%):** Exclusive AI-generated style recipe for your wardrobe

**Role-Based Luck Boosts:**
- **Scout:** +5% to rare/legendary rates
- **Trendsetter:** +10% to rare/legendary rates + exclusive pool access

**Gacha Pull History:**
- All pulls logged with rarity, reward, and timestamp
- Statistics tracked (legendary/rare/common counts)

**Security:** 
- Tokens **CANNOT be purchased** - earned only through gameplay
- No store/purchase endpoints exist

### 9. Internal Status Roles (Status & Power)

**Role Tiers:**

#### Lurker (Default)
- **Requirements:** None (starting role)
- **Perks:**
  - Token Multiplier: 1.0x
  - XP Multiplier: 1.0x
  - Gacha Luck Boost: 0%
- **Description:** Basic app access

#### Scout (Tier 2)
- **Promotion Requirements:**
  - 10 total outfits logged
- **Perks:**
  - Token Multiplier: 1.2x (+20% bonus)
  - XP Multiplier: 1.1x (+10% bonus)
  - Gacha Luck Boost: +5% to rare/legendary rates
- **Description:** Style Scout - Early access, token bonuses

#### Trendsetter (Tier 3)
- **Promotion Requirements:**
  - 30 total outfits logged
  - 7-day streak maintained
- **Maintenance Requirements:**
  - 5 outfits logged per week
  - Grace period: 7 days after promotion
  - Failure to maintain = demotion to Scout
- **Perks:**
  - Token Multiplier: 1.5x (+50% bonus)
  - XP Multiplier: 1.2x (+20% bonus)
  - Gacha Luck Boost: +10% to rare/legendary rates
  - Exclusive Gacha Pool access
  - Priority AI processing
- **Description:** Trendsetter - Premium perks, exclusive features

**Role Decay (Loss Aversion):**
- Trendsetters must log 5 outfits/week to maintain status
- Weekly check runs automatically
- Demotion warning if approaching limit
- Grace period protects newly promoted users
- Status anxiety drives consistent engagement

---

## 🔗 API Endpoints

### Core Gamification
- `GET /api/gamification/profile` - User's XP, level, badges, ecosystem data
- `GET /api/gamification/stats` - Dashboard data (XP, CPW, AI score, GWS)
- `GET /api/gamification/badges` - Badge details
- `GET /api/gamification/ai-fit-score` - AI Fit Score breakdown
- `GET /api/gamification/cpw-summary` - CPW stats and trends

### Challenges
- `GET /api/challenges/available` - Start-able challenges
- `GET /api/challenges/active` - In-progress challenges
- `POST /api/challenges/{id}/start` - Start a challenge
- `GET /api/challenges/history` - Completed challenges
- `GET /api/challenges/{id}/progress` - Challenge details
- `GET /api/challenges/catalog` - All challenge types

### Gacha & Style Tokens
- `GET /api/gacha/balance` - Get token balance and pull availability
- `POST /api/gacha/pull` - Spend 500 tokens for variable reward
- `GET /api/gacha/pull-history` - View past gacha pulls with statistics

### Roles & Status
- `GET /api/roles/status` - Current role, perks, and progress to next tier
- `POST /api/roles/check-promotion` - Manually trigger promotion check

### Wardrobe Audit (Subscription-Gated)
- `GET /api/audit/status` - Get audit state (gated by subscription plan)
- `GET /api/audit/donation-manifest` - Get donation list (PREMIUM only)

### Shuffle
- `POST /api/shuffle` - Generate random outfit
- `POST /api/shuffle/quick` - Quick casual outfit

---

## 💻 Frontend Components

### Dashboard Cards
Located in `frontend/src/components/gamification/`:

- **GamificationSummaryCard** - XP, level, badges, challenges
- **CPWCard** - Average CPW with trend
- **AIFitScoreCard** - Circular progress with breakdown
- **ChallengeCard** - Individual challenge display
- **ChallengeList** - Grid with tabs
- **XPNotification** - Toast with animation (rosegold/creme/espresso colors)
- **LevelUpModal** - Level celebration with confetti (rosegold colors)
- **BadgeUnlockModal** - Badge celebration modal
- **ShuffleButton** - Animated shuffle button
- **ThirtyWearsProgress** - Progress tracker for items

### Hooks
- `useGamificationStats()` - Fetches all gamification data
- `useBadges()` - Fetches user badges
- `useChallenges()` - Fetches challenges + startChallenge helper

### Pages
- `/challenges` - Full challenges page with tabs
- `/dashboard` - Includes gamification cards and shuffle button
- `/onboarding` - Includes spending range questions

### 10. Wardrobe Audit (Subscription-Gated ROI Report)

**Purpose:**
The Wardrobe Audit serves as the **ROI-focused investment report** for paid subscribers. It helps users understand financial value from their wardrobe and creates a paid subscription incentive by gating features.

**Subscription Tiers:**

#### Free Plan
- **Ghost Report:** Shows item counts only (total items, items worn, items unworn)
- **Dollar values:** Locked 🔒
- **Donation manifest:** Locked 🔒
- **Message:** "Unlock Detailed Insights with PRO or PREMIUM"

#### PRO Plan
- **Wardrobe Utilization Rate (WUR):** Unlocked
- **Formula:** `(Items Worn / Total Items) × 100`
- **Visual:** Progress bar with percentage
- **Dollar values:** Still locked
- **Donation manifest:** Locked
- **Message:** "Upgrade to PREMIUM for financial analysis"

#### PREMIUM Plan
- **WUR:** Fully visible
- **Estimated Waste Value:** Unlocked
  - Formula: `(Unworn Items × Avg Cost Per Item) from spending ranges`
  - Uses user's spending ranges for privacy (no exact prices)
- **Donation Manifest:** Full access to list of items recommended for donation
  - Sorted by wear count (never worn first)
  - Top 20 candidates shown
  - Each item shows: name, type, color, wear count, reason
  - Actionable: "Donate these items to reclaim closet space"

**API Endpoints:**
- `GET /api/audit/status` - Returns audit state based on plan
- `GET /api/audit/donation-manifest` - Returns donation list (PREMIUM only)

**Frontend Component:**
- **AuditReportCard** - Renders different UI based on subscription plan
  - Uses rosegold/creme/espresso color scheme
  - Expandable donation list with Framer Motion animations
  - Financial impact visualization for PREMIUM users

**Psychological Hooks:**
- **Financial Loss Visuals** (Free users): See their waste in item counts
- **Upgrade FOMO** (Free/PRO users): Blurred dollar values create curiosity
- **Value Realization** (PREMIUM users): See actual savings potential
- **Actionable Closure** (PREMIUM users): Donation list provides next step

---

## 🎨 Design System

### Color Scheme (Rosegold/Creme/Espresso)
**All gamification notifications use this palette:**
- **Text:** Rosegold (`#C9956F`, `#D4A574`, `#B8860B`)
- **Light Mode Backgrounds:** Creme (`#F5F0E8`)
- **Dark Mode Backgrounds:** Espresso (`#1A1410`, `#251D18`)
- **NO green, blue, or purple colors**

**Components:**
- XP notifications: Rosegold text on creme/espresso background
- Level Up modal: Rosegold gradients for all tiers
- Confetti: Rosegold/copper colors only
- Progress bars: Rosegold fills

### Animations (Framer Motion)
- XP notification: Slide in from top-right
- Progress bars: Smooth fill animation
- Buttons: Scale on tap (0.95)
- Badges: Zoom and rotate on unlock
- Level up: Confetti (rosegold colors only)
- Gacha pulls: Visual effects based on rarity

### Icons (Lucide React)
- XP: Sparkles
- Challenges: Target
- Badges: Award, Trophy, Medal
- AI Score: Brain
- CPW: DollarSign
- Shuffle: Shuffle
- Tokens: Coins
- Gacha: Package
- Roles: Crown (Trendsetter), Compass (Scout), Eye (Lurker)

---

## 🔄 User Flows

### Flow 1: Daily Engagement Loop (Streaks & Tokens)
```
User logs outfit today
  ↓
Backend:
  - Checks streak (broken if >24hrs since last log)
  - Updates streak (0 → 1, or increments)
  - Calculates streak multiplier (1.0x - 3.0x)
  - Awards 50 base tokens × role multiplier
  - Awards 25 streak bonus tokens
  - Awards 10 XP × streak multiplier
  ↓
Frontend:
  - "+10 XP (1.1x streak bonus!)" notification
  - "+75 tokens earned!" notification (rosegold)
  - Streak counter updates
  - Token balance updates
  ↓
User feels progress + fear of losing streak tomorrow
```

### Flow 2: Gacha Pull (Variable Ratio Reinforcement)
```
User has 500+ tokens
  ↓
Clicks "Pull" button
  ↓
Backend:
  - Deducts 500 tokens
  - Rolls for rarity (with role luck boost)
  - Awards reward (common/rare/legendary)
  - Logs pull to history
  ↓
Frontend:
  - Visual effect (gold confetti for legendary)
  - Reward reveal animation
  - "+50 XP Bonus!" or "Style Recipe Unlocked!"
  - Token balance updates
  ↓
User experiences dopamine hit from variable reward
  - Wants to pull again (farms more tokens)
```

### Flow 3: Role Promotion (Status & Power)
```
User logs 30th outfit
  ↓
Backend checks promotion criteria:
  - 30 outfits ✅
  - 7-day streak ✅
  ↓
User promoted to Trendsetter
  ↓
Backend:
  - Updates role in profile
  - Applies new perks (1.5x tokens, +10% gacha luck)
  - Sets maintenance requirements (5/week)
  ↓
Frontend:
  - "🎉 Promoted to Trendsetter!" modal
  - Shows new perks
  - Visual celebration
  ↓
User feels powerful + anxiety about maintaining status
```

### Flow 4: Challenge Completion (Tokens Awarded)
```
User completes "Hidden Gem Hunter" challenge
  ↓
Backend:
  - Awards +75 XP
  - Awards +75 Tokens (NEW)
  - Applies role multiplier to tokens (if Scout/Trendsetter)
  - Unlocks badge
  ↓
Frontend:
  - "🎉 Challenge Complete! +75 XP + 88 Tokens!" (with Scout 1.2x)
  - Badge unlock animation
  - Token balance updates
  ↓
User feels rewarded + can afford gacha pull
```

### Flow 5: Trendsetter Decay Check (Loss Aversion)
```
7 days pass since Trendsetter promotion
  ↓
User logs outfit (triggers maintenance check)
  ↓
Backend:
  - Counts outfits logged in last 7 days
  - Only 3 outfits (needs 5)
  ↓
If in grace period:
  - Warning: "Log 2 more outfits this week to keep Trendsetter!"
  
If grace period expired:
  - Demotion to Scout
  - Loss of 1.5x token multiplier
  - Loss of +10% gacha luck
  ↓
Frontend:
  - "⚠️ Demoted to Scout - Log more to regain Trendsetter!"
  ↓
User feels loss + motivation to regain status
```

---

## 🛠️ Technical Architecture

### Data Models

**User Profile (Firestore):**
```json
{
  "xp": 1250,
  "level": 5,
  "ai_fit_score": 68.5,
  "badges": ["starter_closet", "hidden_gem_hunter"],
  "spending_ranges": {
    "annual_total": "$2,500-$5,000",
    "tops": "$250-$500",
    "pants": "$500-$1,000",
    "shoes": "$250-$500",
    "jackets": "$500-$1,000",
    "dresses": "$100-$250",
    "accessories": "$0-$100"
  },
  "streak": {
    "current_streak": 7,
    "longest_streak": 12,
    "last_log_date": "2025-12-10",
    "streak_multiplier": 1.7
  },
  "style_tokens": {
    "balance": 750,
    "total_earned": 1200,
    "total_spent": 500,
    "last_earned_at": "2025-12-10T10:30:00Z"
  },
  "role": {
    "current_role": "scout",
    "role_earned_at": "2025-12-05T10:00:00Z",
    "role_decay_checks_remaining": 0,
    "privileges": {
      "token_multiplier": 1.2,
      "xp_multiplier": 1.1,
      "gacha_luck_boost": 0.05
    }
  }
}
```

**Gacha Pull Record:**
```json
{
  "user_id": "user123",
  "rarity": "RARE",
  "reward_type": "style_insight",
  "reward_data": {
    "type": "Advanced Styling Insight",
    "description": "Unlock new color combination technique"
  },
  "visual_effect": "PURPLE_SPARKLE",
  "cost": 500,
  "pulled_at": "2025-12-10T10:30:00Z"
}
```

### Service Layer

**Gamification Service:**
- Single source of truth for XP and badges
- Handles level calculations
- Logs all events to analytics_events

**Addiction Service:**
- `check_and_update_streak()` - Streak tracking and multiplier
- `award_style_tokens()` - Token earning with role multipliers
- `perform_style_gacha_pull()` - Gacha mechanics with role luck boosts
- `check_for_promotion()` - Role promotion logic
- `check_trendsetter_decay()` - Maintenance and demotion checks
- `get_user_addiction_state()` - Complete ecosystem state

**CPW Service:**
- Estimates item costs from spending ranges
- Batch calculates wardrobe CPW
- Tracks trends over time

**AI Fit Score Service:**
- Hybrid scoring algorithm
- Real-time updates on feedback
- Milestone tracking

**Challenge Service:**
- Wraps existing systems (Forgotten Gems)
- Manages challenge lifecycle
- Distributes rewards (XP + Tokens)

---

## 📈 Analytics Events

All gamification actions logged to `analytics_events`:

**Original Events:**
- `xp_earned`
- `level_up`
- `badge_unlocked`
- `challenge_started`
- `challenge_completed`
- `ai_fit_score_updated`

**New Ecosystem Events:**
- `streak_updated` - Streak incremented or broken
- `tokens_earned` - Tokens awarded
- `tokens_spent` - Tokens spent (gacha pull)
- `gacha_pull` - Gacha pull with rarity
- `role_promoted` - Role upgrade
- `role_demoted` - Role decay/demotion

---

## 🎯 Success Metrics

### Key Performance Indicators

**Engagement:**
- Daily Active Users (DAU) - Target: +25% with streaks
- Feedback rate increase: Target +20%
- Outfit logging increase: Target +30%
- Shuffle usage: Target 2-3x per user/week
- Challenge completion: Target 40%+

**Ecosystem Metrics:**
- Average streak length
- Token earning rate per user
- Gacha pull frequency
- Role distribution (Lurker/Scout/Trendsetter percentages)

**Progression:**
- Average XP per user
- Level distribution across tiers
- AI Fit Score growth rate
- Badge unlock rate

**Value:**
- CPW decrease month-over-month
- Wardrobe utilization increase
- Session length increase
- 30-day retention lift: Target +10%

---

## 🚀 Quick Start (Development)

### Backend
```bash
cd backend
# All dependencies already installed
python app.py
# Server runs on port 3001
```

Test endpoints:
```bash
# Get stats
curl http://localhost:3001/api/gamification/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get token balance
curl http://localhost:3001/api/gacha/balance \
  -H "Authorization: Bearer YOUR_TOKEN"

# Perform gacha pull
curl -X POST http://localhost:3001/api/gacha/pull \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get role status
curl http://localhost:3001/api/roles/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend
```bash
cd frontend
npm run dev
# App runs on port 3000
```

Navigate to:
- `/dashboard` - See gamification cards
- `/challenges` - Full challenges page
- `/onboarding` - Test spending questions

---

## 🔗 Integration Points

### Existing Systems Used
1. **Forgotten Gems** (`backend/src/routes/forgotten_gems.py`) - Called by challenge service
2. **Feedback System** (`backend/src/routes/feedback.py`) - Extended with XP awards
3. **Outfit History** (`backend/src/routes/outfit_history.py`) - Extended with streaks, tokens, role checks
4. **Analytics Events** - All gamification logged here
5. **Wardrobe Stats** - CPW integrated alongside existing metrics

### New Systems Created
1. **Gamification Service** - XP, levels, badges
2. **Addiction Service** - Streaks, tokens, gacha, roles
3. **CPW Service** - Cost per wear calculations
4. **AI Fit Score Service** - Style learning progress
5. **Challenge Service** - Challenge management (updated to award tokens)

### Route Files
**Core Gamification:**
- `backend/src/routes/gamification.py` - XP, levels, badges, CPW, AI score
- `backend/src/routes/challenges.py` - Challenge management
- `backend/src/routes/shuffle.py` - Random outfit generation

**Ecosystem Engineering:**
- `backend/src/routes/gacha.py` - Style Tokens and Gacha pulls
- `backend/src/routes/roles.py` - Internal status roles

---

## 🎊 System Status

**✅ PRODUCTION READY**

**Original Gamification:** 22 major components
- 11 backend components (services, routes, models)
- 9 frontend components (cards, pages, hooks)
- 2 integration points (feedback, outfit logging)

**Ecosystem Engineering:** 2 route files + 1 service
- Addiction Service with core methods
- 2 API route modules (Gacha, Roles)
- Integrated into outfit logging flow
- Token earning through gameplay only

**All Features Tested:**
- Triple Reward Loop ✅
- Challenge system ✅
- CPW tracking ✅
- XP and leveling ✅
- Badge unlocking ✅
- Shuffle feature ✅
- Streak tracking ✅
- Style Tokens ✅
- Gacha pulls ✅
- Role promotion/demotion ✅
- Dashboard integration ✅
- Onboarding integration ✅

---

## 🎨 Color Palette Reference

**Rosegold/Creme/Espresso Scheme:**
- **Rosegold Light:** `#D4A574`
- **Rosegold Mid:** `#C9956F`
- **Rosegold Dark:** `#B8860B`
- **Creme:** `#F5F0E8`
- **Espresso Background:** `#1A1410`
- **Espresso Card:** `#251D18`

**NO green, blue, or purple in gamification notifications.**

---

## 📚 Documentation Files

- `GAMIFICATION_COMPLETE.md` - This file (complete reference)
- `GAMIFICATION_INDEX.md` - File structure index
- `GAMIFICATION_COMPLETE_SUMMARY.md` - Implementation summary
- `GAMIFICATION_DEPLOYMENT_GUIDE.md` - Deployment steps
- `COLOR_PALETTE.md` - Color system reference

---

## 👨‍💻 Developer Notes

### Code Organization
```
backend/src/
├── custom_types/gamification.py     # Pydantic models
├── services/
│   ├── gamification_service.py      # XP & badges
│   ├── addiction_service.py         # Streaks, tokens, gacha, roles
│   ├── cpw_service.py               # Cost per wear
│   ├── ai_fit_score_service.py      # AI learning score
│   └── challenge_service.py         # Challenges (awards tokens)
└── routes/
    ├── gamification.py               # Gamification endpoints
    ├── challenges.py                 # Challenge endpoints
    ├── shuffle.py                    # Shuffle endpoint
    ├── gacha.py                      # Gacha & tokens
    └── roles.py                      # Roles & status

frontend/src/
├── hooks/useGamificationStats.ts     # Data fetching hooks
├── components/gamification/          # UI components (rosegold colors)
└── app/
    └── challenges/page.tsx           # Challenges page
```

### Key Design Decisions
1. **No Duplication:** Wraps existing systems instead of rebuilding
2. **Non-Blocking:** Gamification failures don't break core flows
3. **Efficient Queries:** Uses Firestore indexes for speed
4. **Progressive Enhancement:** Works even if some components fail
5. **Privacy-First:** Spending ranges, not exact prices
6. **Engagement-Only Economy:** Tokens earned, never purchased
7. **Graceful Degradation:** New services wrapped in try/except
8. **Psychological Hooks:** Variable rewards, status anxiety, loss aversion

---

## 🙏 Credits

Built on top of Easy Outfit App's robust infrastructure:
- Existing Forgotten Gems system
- Feedback processing service
- Outfit generation service
- Analytics framework
- ShadCN UI components
- Framer Motion animations

**Ecosystem Engineering inspired by:**
- Gacha game variable rewards (Genshin Impact)
- Discord role hierarchies
- Reddit karma/status loops
- Snapchat streaks

---

**Ready to gamify your wardrobe and build an addictive ecosystem! 🎮✨**

