# Easy Outfit App — "Sophisticated Gamification" UX/UI Blueprint

**Version:** 1.0  
**Last Updated:** December 2025  
**Document Type:** UX/UI Refinement Specification  
**Purpose:** Visual design refinements to align with "Silent Luxury" positioning while maintaining comprehensive feature set

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Dashboard Refinements](#dashboard-refinements)
3. [Outfits Page Flow Refinements](#outfits-page-flow-refinements)
4. [Gamification Visual Refinements](#gamification-visual-refinements)
5. [Component Library Specifications](#component-library-specifications)
6. [Animation & Micro-Interaction Refinements](#animation--micro-interaction-refinements)
7. [Typography & Color Refinements](#typography--color-refinements)
8. [Implementation Guide](#implementation-guide)

---

## Executive Summary

### Synthesis of Decisions

This blueprint synthesizes a **minimal luxury-focused UX approach** with the existing **comprehensive feature set** of Easy Outfit App. The result is **"Sophisticated Gamification"** — a design philosophy that maintains all functionality while refining visual styling to feel premium, sophisticated, and aspirational.

### Key Design Decisions

1. **Hybrid Approach**: Minimal default with progressive disclosure (differentiates Free vs Pro users)
2. **Outfits Page**: Blueprint-style minimal default with "Shuffle" + "Expand" buttons → single bottom sheet
3. **Gamification**: Visible but refined — subtle progress bars, minimal XP notifications, elegant badges
4. **Visual Identity**: Keep dark mode primary, amber accents, dual-font system (Space Grotesk + Inter)
5. **Animations**: Keep 3-level hierarchy, refine gamification animations to be subtle
6. **Features**: Keep all comprehensive functionality, refine visual styling only

### "Sophisticated Gamification" Philosophy

**Core Principle:** Gamification should feel like a natural part of the luxury experience, not a separate game layer.

**Visual Approach:**
- **Progress bars**: Amber gradient (not bright purple/pink), subtle fill animation
- **XP notifications**: Small toast (top-right), amber accent, no popup animations
- **Badges**: Minimal line icons with amber glow on unlock, subtle shimmer (no confetti)
- **Level indicators**: Typography-based (not icon-heavy), amber gradient text
- **Challenges**: Minimal cards with subtle borders, no bright colors

**Interaction Approach:**
- Maintain 3-level interaction hierarchy (contextual feedback)
- Gamification elements use Level 1-2 interactions (subtle, not celebratory)
- Only major achievements (level ups, milestones) use Level 3 celebrations
- All animations respect "Silent Luxury" — smooth, purposeful, not playful

---

## Dashboard Refinements

### Overview

The dashboard adopts a **minimal above-fold layout** that prioritizes the daily outfit experience while maintaining access to key information. The layout follows a "Silent Luxury" approach: clean, sophisticated, and focused on the primary action (getting dressed).

### Minimal Above-Fold Layout

**Layout Structure:**
```
┌─────────────────────────────────────┐
│  Let's get you dressed ✨           │
│  Your look today is ready           │
│                                      │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │   Daily Outfit Hero Card      │  │
│  │   (Weather-aware suggestion)  │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  🌤️ 52°F, Partly Cloudy      │  │
│  │  [Weather Widget - Compact]    │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  Monthly Usage                │  │
│  │  [Progress bars]              │  │
│  │  [Upgrade CTA if needed]     │  │
│  └───────────────────────────────┘  │
│                                      │
│  [Gamification cards below fold]    │
└─────────────────────────────────────┘
```

**Above-Fold Priority:**
1. **Daily Outfit Hero Card** (primary focus)
2. **Weather Widget** (compact, contextual)
3. **Combined Usage/Upgrade Component** (monthly usage + premium upgrade CTA)
4. **Gamification cards** (below fold, refined styling)

### Daily Outfit Hero Card

**Purpose:** Primary focus of dashboard — shows today's AI-generated outfit suggestion

**Specifications:**
- **Background**: Surface (#2C2119) with subtle amber gradient overlay
- **Border radius**: 24px
- **Padding**: 24px (mobile) → 32px (desktop)
- **Shadow**: 0 12px 40px rgba(0, 0, 0, 0.4)
- **Border**: 1px solid amber gradient (subtle, 20% opacity)
- **Min-height**: 200px (mobile), 240px (desktop)

**Content Structure:**
```
┌─────────────────────────────────────┐
│  Today's Outfit                     │
│  [Date: Monday, Dec 2]              │
│                                      │
│  [Outfit Preview Image/Items]       │
│                                      │
│  Occasion: Business Casual          │
│  Mood: Confident                     │
│  Weather: 52°F, Partly Cloudy       │
│                                      │
│  [Wear This] [View Details]          │
└─────────────────────────────────────┘
```

**Elements:**
- **Title**: "Today's Outfit" (H2, 24px, display font)
- **Date**: Current date formatted (Body, 14px, textSecondary)
- **Outfit Preview**: 
  - If items available: Grid of item thumbnails (3-4 items, 60px × 60px)
  - If no items: Placeholder with sparkle icon
- **Metadata**: Occasion, mood, weather (Body Small, 13px, textSecondary)
- **Actions**:
  - Primary: "Wear This" button (amber gradient, 48px height)
  - Secondary: "View Details" link (ghost button)

**Empty State** (no outfit generated):
- **Icon**: Sparkles icon, 64px, amber (#FFB84C)
- **Title**: "Your look today ✨" (H2, display font)
- **Subtitle**: "Generate a weather-perfect outfit" (Body, textSecondary)
- **CTA**: "Generate today's fit" button (amber gradient, full-width)

**Animation:**
- **Load**: Fade in (300ms easeOut)
- **Outfit Reveal**: Progressive reveal (2.2-3.6s) if generating
- **Hover**: Subtle scale(1.01) + shadow increase (desktop only)

**Code Example:**
```tsx
<Card className="bg-[#2C2119] border border-[#FFB84C]/20 rounded-3xl p-6 sm:p-8
  shadow-[0_12px_40px_rgba(0,0,0,0.4)]
  hover:shadow-[0_16px_48px_rgba(0,0,0,0.5)] transition-all duration-300">
  <CardHeader>
    <CardTitle className="text-2xl font-display text-[#F8F5F1]">
      Today's Outfit
    </CardTitle>
    <CardDescription className="text-sm text-[#C4BCB4]">
      {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
    </CardDescription>
  </CardHeader>
  <CardContent>
    {/* Outfit preview, metadata, actions */}
  </CardContent>
</Card>
```

### Weather Widget (Compact)

**Purpose:** Show current weather context for outfit suggestions (above fold, compact)

**Specifications:**
- **Size**: Compact (not full card)
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Border radius**: 16px
- **Padding**: 16px
- **Height**: Auto (min 80px)

**Content Structure:**
```
┌─────────────────────────────────────┐
│  🌤️  52°F                          │
│  Partly Cloudy • San Francisco     │
│  [Refresh icon]                     │
└─────────────────────────────────────┘
```

**Elements:**
- **Icon**: Weather icon (Cloud, Sun, etc.), 24px, amber (#FFB84C)
- **Temperature**: Large text (H3, 20px, textPrimary)
- **Condition**: Body Small (13px, textSecondary)
- **Location**: Body Small (13px, textTertiary)
- **Refresh Button**: Ghost button, 32px × 32px, top-right

**Refined Styling:**
- **No bright colors**: Use amber accent only
- **Minimal borders**: 1px solid #3D2F24
- **Subtle hover**: Background → #3D2F24
- **No recommendations expanded by default**: Keep compact

**Code Example:**
```tsx
<Card className="bg-[#2C2119] border border-[#3D2F24] rounded-2xl p-4">
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-3">
      <Cloud className="w-6 h-6 text-[#FFB84C]" />
      <div>
        <div className="text-xl font-display font-semibold text-[#F8F5F1]">
          {temperature}°F
        </div>
        <div className="text-xs text-[#C4BCB4]">
          {condition} • {location}
        </div>
      </div>
    </div>
    <Button variant="ghost" size="icon" className="h-8 w-8">
      <RefreshCw className="h-4 w-4" />
    </Button>
  </div>
</Card>
```

### Combined Monthly Usage / Premium Upgrade Component

**Purpose:** Single component that shows monthly usage limits and premium upgrade CTA (above fold)

**Specifications:**
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Border radius**: 16px
- **Padding**: 20px
- **Layout**: Vertical stack (usage above, upgrade below if needed)

**Content Structure:**
```
┌─────────────────────────────────────┐
│  Monthly Usage                      │
│  Resets on Dec 1                    │
│                                      │
│  Outfits: [████████░░] 8/10        │
│  Items:   [██████████] 50/50       │
│                                      │
│  ─────────────────────────────────  │
│                                      │
│  [Upgrade to Premium]               │
│  Unlimited outfits + items          │
└─────────────────────────────────────┘
```

**Usage Section:**
- **Title**: "Monthly Usage" (Body, 14px, font-medium, textPrimary)
- **Reset Date**: "Resets on [date]" (Body Small, 13px, textSecondary)
- **Progress Bars**: 
  - Height: 4px (subtle, as per gamification refinements)
  - Background: #3D2F24
  - Fill: Amber gradient
  - Label: "Outfits: 8/10" (Body Small, 13px, textSecondary)
- **Spacing**: 16px gap between usage items

**Upgrade Section** (shown if limit reached or approaching):
- **Divider**: 1px solid #3D2F24, 16px margin top/bottom
- **Message**: "Unlock unlimited access" (Body, 14px, textPrimary)
- **CTA Button**: 
  - Full-width, 48px height
  - Amber gradient background
  - Text: "Upgrade to Premium"
  - Icon: Crown or Zap icon, 20px

**Refined Styling:**
- **No bright warning colors**: Use amber gradient for progress only
- **Subtle borders**: 1px solid #3D2F24
- **Minimal spacing**: 16px between sections
- **Typography-based**: No icon-heavy design

**Code Example:**
```tsx
<Card className="bg-[#2C2119] border border-[#3D2F24] rounded-2xl p-5">
  <div className="space-y-4">
    {/* Usage Section */}
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-[#F8F5F1]">Monthly Usage</h3>
        <span className="text-xs text-[#8A827A]">Resets on {resetDate}</span>
      </div>
      
      {/* Outfit Usage */}
      <div className="space-y-1 mb-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-[#C4BCB4]">Outfits</span>
          <span className="text-[#C4BCB4]">{current}/{limit}</span>
        </div>
        <Progress value={percentage} className="h-1" />
      </div>
      
      {/* Item Usage */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs">
          <span className="text-[#C4BCB4]">Items</span>
          <span className="text-[#C4BCB4]">{current}/{limit}</span>
        </div>
        <Progress value={percentage} className="h-1" />
      </div>
    </div>
    
    {/* Upgrade Section (if needed) */}
    {(limitReached || approachingLimit) && (
      <>
        <div className="border-t border-[#3D2F24] pt-4">
          <p className="text-sm text-[#F8F5F1] mb-3">
            Unlock unlimited access
          </p>
          <Button className="w-full h-12 bg-gradient-to-r from-[#FFB84C] to-[#FF9400]">
            <Crown className="w-5 h-5 mr-2" />
            Upgrade to Premium
          </Button>
        </div>
      </>
    )}
  </div>
</Card>
```

### Gamification Cards (Below Fold, Refined Styling)

**Purpose:** Show gamification progress (XP, level, AI Fit Score, challenges) with refined "Sophisticated Gamification" styling

**Layout:**
- **Position**: Below fold (after daily outfit, weather, usage)
- **Grid**: 2 columns (mobile), 3-4 columns (desktop)
- **Gap**: 16px
- **Spacing**: 24px margin-top from above-fold content

**Card Specifications:**
- **Background**: Surface (#2C2119)
- **Border**: 1px solid #3D2F24
- **Border radius**: 16px
- **Padding**: 20px
- **Shadow**: None (minimal)

**Gamification Elements** (as per Gamification Visual Refinements section):
- **XP Progress**: Typography-based level indicator + 4px amber progress bar
- **AI Fit Score**: Circular progress (120px) with amber gradient
- **Challenges**: Minimal cards with subtle borders, no bright colors
- **Badges**: Compact grid (3 columns), minimal icons

**Refined Styling Principles:**
- **No bright colors**: Amber gradient only
- **Subtle progress bars**: 4px height
- **Typography-based**: No icon-heavy design
- **Minimal borders**: 1px solid #3D2F24
- **Consistent spacing**: 16px gaps

**Code Example:**
```tsx
<div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
  {/* XP / Level Card */}
  <Card className="bg-[#2C2119] border border-[#3D2F24] rounded-2xl p-5">
    <div className="text-center">
      <h3 className="text-xl font-display font-semibold
        bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
        Level {level}
      </h3>
      <p className="text-xs text-[#C4BCB4] uppercase tracking-wider mt-1">
        {levelName}
      </p>
      <Progress value={xpPercentage} className="h-1 mt-2" />
      <p className="text-xs text-[#8A827A] mt-1">
        {xp} / {xpNeeded} XP
      </p>
    </div>
  </Card>
  
  {/* AI Fit Score Card */}
  <Card className="bg-[#2C2119] border border-[#3D2F24] rounded-2xl p-5">
    {/* Circular progress indicator */}
  </Card>
  
  {/* Challenges Card */}
  <Card className="bg-[#2C2119] border border-[#3D2F24] rounded-2xl p-5">
    {/* Challenge list */}
  </Card>
</div>
```

### Dashboard Layout Priority

**Above Fold (First Screen):**
1. Daily Outfit Hero Card (primary)
2. Weather Widget (compact)
3. Combined Usage/Upgrade Component

**Below Fold (Scroll to See):**
4. Gamification Cards (refined styling)
5. Wardrobe Insights
6. Top Items Grid
7. Other analytics

**Spacing:**
- **Between above-fold elements**: 16px gap
- **Above-fold to below-fold**: 24px margin-top
- **Between below-fold sections**: 24px gap

### Responsive Behavior

**Mobile (320px - 639px):**
- **Daily Outfit Card**: Full-width, 24px padding
- **Weather Widget**: Full-width, below outfit card
- **Usage/Upgrade**: Full-width, below weather
- **Gamification Cards**: 2-column grid

**Tablet (768px - 1023px):**
- **Daily Outfit Card**: Full-width, 32px padding
- **Weather + Usage**: Side-by-side (2-column), 16px gap
- **Gamification Cards**: 3-column grid

**Desktop (1024px+):**
- **Daily Outfit Card**: Full-width, 32px padding
- **Weather + Usage**: Side-by-side (2-column), 20px gap
- **Gamification Cards**: 4-column grid

---

## Outfits Page Flow Refinements

### Overview

The Outfits page (where users go to be "hands-on") adopts a **blueprint-style minimal default** with progressive disclosure. Users see a clean interface with two primary actions: "Shuffle" (quick random outfit) and "Expand" (full customization).

### Minimal Default State

**Layout:**
```
┌─────────────────────────────────────┐
│  My Looks                           │
│  [Subtitle: Save the fits you love] │
│                                      │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │   AI Suggested Outfit         │  │
│  │   (Weather-aware, context)   │  │
│  │                               │  │
│  │   [Outfit Preview Card]       │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌──────────┐  ┌──────────┐         │
│  │ Shuffle  │  │  Expand  │         │
│  └──────────┘  └──────────┘         │
│                                      │
│  [Saved Outfits Grid Below]          │
└─────────────────────────────────────┘
```

**Elements:**
- **AI Suggested Outfit Card**: Shows weather-aware outfit suggestion (if available)
- **Shuffle Button**: One-tap random outfit generation (+2 XP)
- **Expand Button**: Opens Adjust bottom sheet with full customization options
- **Saved Outfits Grid**: Existing outfit grid below (unchanged)

**Button Specifications:**
- **Shuffle Button**:
  - Size: 48px height, full-width or 50% width (side-by-side with Expand)
  - Background: Surface color (#2C2119) with 1px border (#3D2F24)
  - Text: "Shuffle" with shuffle icon (Lucide Shuffle)
  - Hover: Background → #3D2F24
  - Active: Scale(0.95)
  - Animation: None (static button)

- **Expand Button**:
  - Size: 48px height, full-width or 50% width
  - Background: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
  - Text: "Expand" with chevron-down icon
  - Hover: Shadow increase (0 4px 12px rgba(255, 180, 76, 0.3))
  - Active: Scale(0.95)
  - Animation: None (static button)

### Adjust Bottom Sheet

**Purpose:** Single bottom sheet that contains all outfit customization options (Occasion, Mood, Style, Base Item).

**Layout Structure:**
```
┌─────────────────────────────────────┐
│  Refine your look              [×]  │
│  AI suggestion: Smart Casual        │
│  52°F, partly cloudy                │
├─────────────────────────────────────┤
│                                      │
│  Occasion                           │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐    │
│  │ B │ │ C │ │ D │ │ G │ │ W │    │
│  └───┘ └───┘ └───┘ └───┘ └───┘    │
│  [Horizontal scrollable pills]      │
│                                      │
│  Mood                               │
│  ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Confid│ │Playfu│ │Sophis│        │
│  └──────┘ └──────┘ └──────┘       │
│  [Minimal text chips, airy spacing] │
│                                      │
│  Style                              │
│  ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Minima│ │Preppy│ │Street│        │
│  └──────┘ └──────┘ └──────┘       │
│  [Text-only aesthetic chips]        │
│                                      │
│  Base Item (Optional)               │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐         │
│  │  │ │  │ │  │ │  │ │  │         │
│  └──┘ └──┘ └──┘ └──┘ └──┘         │
│  [Horizontal item carousel]         │
│                                      │
│  ┌───────────────────────────────┐  │
│  │      Generate Look            │  │
│  └───────────────────────────────┘  │
│  [Sticky bottom button]             │
└─────────────────────────────────────┘
```

**Component Specifications:**

#### Header Section
- **Title**: "Refine your look" (H3, display font, 20px)
- **Subtitle**: AI suggestion with weather context (Body, 14px, textSecondary)
- **Close Button**: X icon, top-right, 44px × 44px touch target

#### Occasion Section
- **Label**: "Occasion" (Body Small, 13px, textSecondary, uppercase, letter-spacing: 0.5px)
- **Chips**: Horizontal scrollable pills
  - Height: 32px
  - Padding: 12px 16px
  - Border radius: 16px
  - Background: Surface (#2C2119)
  - Border: 1px solid #3D2F24
  - Text: Body Small (13px), textPrimary
  - Selected state:
    - Background: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
    - Border: None
    - Text: #1A1510 (dark text on amber)
  - Gap: 8px between chips
  - Scroll: Horizontal, snap points

#### Mood Section
- **Label**: "Mood" (same as Occasion label)
- **Chips**: Minimal text chips, airy spacing
  - Height: 36px
  - Padding: 10px 20px
  - Border radius: 18px
  - Background: Transparent
  - Border: 1px solid #3D2F24
  - Text: Body (14px), textPrimary
  - Selected state:
    - Background: #3D2F24 (subtle fill)
    - Border: 1px solid #FFB84C (amber border)
  - Gap: 12px between chips
  - Layout: Wrap (not horizontal scroll)

#### Style Section
- **Label**: "Style" (same as Occasion label)
- **Chips**: Text-only aesthetic chips
  - Height: 32px
  - Padding: 10px 18px
  - Border radius: 16px
  - Background: Transparent
  - Border: 1px solid #3D2F24
  - Text: Body Small (13px), textPrimary
  - Selected state:
    - Background: #3D2F24
    - Border: 1px solid #FFB84C
  - Gap: 8px between chips
  - Layout: Wrap

#### Base Item Section (Optional)
- **Label**: "Base Item (Optional)" (Body Small, textSecondary)
- **Carousel**: Horizontal item carousel from wardrobe
  - Item size: 60px × 60px (square thumbnails)
  - Border radius: 12px
  - Gap: 12px
  - Selected state:
    - Border: 2px solid #FFB84C (amber)
    - Shadow: 0 4px 12px rgba(255, 180, 76, 0.3)
  - Scroll: Horizontal, snap points

#### Generate Look Button (Sticky Bottom)
- **Position**: Sticky to bottom of sheet
- **Size**: Full-width, 56px height
- **Background**: Deep charcoal (#1A1510) or amber gradient (user preference)
- **Text**: "Generate Look" (Body, 16px, white or dark text)
- **Border radius**: 16px (top corners only if sticky)
- **Shadow**: 0 8px 24px rgba(0, 0, 0, 0.4)
- **Interaction**:
  - Hover: Shadow increase
  - Active: Scale(0.98)
  - Haptic: Light tap (0.05s)

**Sheet Animation:**
- **Open**: Slide up from bottom + fade in
  - translateY: 100% → 0%
  - opacity: 0 → 1
  - Duration: 350ms
  - Easing: easeOut
- **Close**: Slide down + fade out
  - translateY: 0% → 100%
  - opacity: 1 → 0
  - Duration: 300ms
  - Easing: easeIn

**Sheet Dimensions:**
- **Max height**: 90vh (90% of viewport height)
- **Border radius**: 24px (top corners only)
- **Background**: Surface (#2C2119)
- **Backdrop**: Blur overlay (backdrop-blur-sm, rgba(0,0,0,0.5))

---

## Gamification Visual Refinements

### Philosophy

Gamification elements should feel like **natural extensions of the luxury experience**, not separate game mechanics. All visual styling uses the amber gradient palette and maintains "Silent Luxury" sophistication.

### Progress Bars

**Current State:** Bright purple/pink gradients, prominent animations

**Refined State:**
- **Background**: Surface variant (#3D2F24)
- **Fill**: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
- **Height**: 4px (subtle, not prominent)
- **Border radius**: 2px (fully rounded)
- **Animation**: Smooth fill (300ms easeOut)
- **Shadow**: None (minimal)

**Usage Contexts:**
1. **XP Progress Bar** (to next level):
   - Shows current XP / XP needed for next level
   - Position: Below level indicator
   - Width: Full-width of card
   - Label: "2,450 / 3,000 XP" (Body Small, textSecondary)

2. **Wardrobe Unlock Progress**:
   - Shows items added / items needed
   - Position: Empty state or onboarding
   - Width: Full-width
   - Label: "2 of 8 items" (Body Small, textSecondary)

3. **Challenge Progress**:
   - Shows challenge completion percentage
   - Position: Inside challenge card
   - Width: Full-width of card
   - Label: "3 / 5 items worn" (Body Small, textSecondary)

**Code Example:**
```tsx
<div className="w-full h-1 bg-[#3D2F24] rounded-full overflow-hidden">
  <motion.div
    className="h-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400]"
    initial={{ width: 0 }}
    animate={{ width: `${percentage}%` }}
    transition={{ duration: 0.3, ease: "easeOut" }}
  />
</div>
```

### XP Notifications

**Current State:** Large popup notifications, purple/pink gradients, prominent animations

**Refined State:**
- **Position**: Fixed top-right, 16px from top, 16px from right
- **Size**: Min-width 240px, max-width 320px
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Padding**: 12px 16px
- **Border radius**: 12px
- **Shadow**: 0 4px 12px rgba(0, 0, 0, 0.3)
- **Animation**:
  - Enter: Slide in from right + fade (opacity 0→1, translateX 20px→0)
  - Duration: 250ms
  - Easing: easeOut
  - Exit: Slide out right + fade (opacity 1→0, translateX 0→20px)
  - Duration: 200ms
- **Auto-dismiss**: 3 seconds
- **Stacking**: Multiple notifications stack vertically with 8px gap

**Content:**
- **Icon**: Sparkles icon (Lucide), 20px, amber (#FFB84C)
- **XP Amount**: "+10 XP" (Body, 14px, amber gradient text)
- **Reason**: "Logged outfit" (Body Small, 13px, textSecondary)
- **Level Up Variant**: 
  - Background: Amber gradient (subtle, not bright)
  - Text: White (#F8F5F1)
  - Icon: Award icon (Lucide), 20px, white

**Code Example:**
```tsx
<motion.div
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: 20 }}
  transition={{ duration: 0.25, ease: "easeOut" }}
  className="fixed top-4 right-4 z-50 min-w-[240px] max-w-[320px]
    bg-[#2C2119] border border-[#3D2F24] rounded-xl p-3
    shadow-lg"
>
  <div className="flex items-center gap-3">
    <Sparkles className="w-5 h-5 text-[#FFB84C]" />
    <div className="flex-1">
      <div className="text-sm font-medium bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
        +{xp} XP
      </div>
      <div className="text-xs text-[#C4BCB4] mt-0.5">
        {reason}
      </div>
    </div>
  </div>
</motion.div>
```

### Badges

**Current State:** Colorful badges with confetti animations, bright colors

**Refined State:**
- **Icon Style**: Minimal line icons (Lucide), 24px
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Size**: 64px × 64px (square)
- **Border radius**: 16px
- **Unlock Animation**:
  - Scale: 0 → 1.1 → 1.0 (subtle bounce)
  - Rotate: -5° → 5° → 0° (subtle wobble)
  - Duration: 400ms
  - Easing: easeOut
  - **Shimmer Effect**: Subtle amber glow (not confetti)
    - Box-shadow: 0 0 20px rgba(255, 180, 76, 0.3)
    - Duration: 600ms
    - Easing: easeInOut

**Rarity Colors** (refined):
- **Common**: Border #3D2F24 (no color change)
- **Rare**: Border #3D2F24, subtle blue tint on icon (#3B82F6 at 20% opacity)
- **Epic**: Border #3D2F24, subtle purple tint on icon (#8B5CF6 at 20% opacity)
- **Legendary**: Border #FFB84C (amber), amber glow on icon

**Display Contexts:**
1. **Badge Grid** (Profile page):
   - 3-column grid (mobile), 4-column (desktop)
   - Gap: 16px
   - Unlocked: Full opacity
   - Locked: 30% opacity, Lock icon overlay

2. **Badge Card** (Dashboard):
   - Compact view: 5 badges in horizontal scroll
   - Size: 48px × 48px
   - Icon: 20px
   - Text: Badge name below (Body Small, 12px)

**Code Example:**
```tsx
<motion.div
  initial={{ scale: 0, rotate: -5 }}
  animate={{ scale: 1, rotate: 0 }}
  transition={{ 
    type: "spring",
    stiffness: 200,
    damping: 15
  }}
  className="w-16 h-16 bg-[#2C2119] border border-[#3D2F24] rounded-2xl
    flex items-center justify-center
    hover:border-[#FFB84C] transition-colors"
>
  <IconComponent className="w-6 h-6 text-[#FFB84C]" />
</motion.div>
```

### Level Indicators

**Current State:** Icon-heavy, colorful level badges

**Refined State:**
- **Typography-based**: No icons, text-only
- **Level Text**: "Level 5" (H3, 20px, display font)
- **Level Name**: "Stylist" (Body, 14px, textSecondary, uppercase, letter-spacing: 1px)
- **XP Text**: "2,450 / 3,000 XP" (Body Small, 13px, textSecondary)
- **Progress Bar**: 4px height, amber gradient fill (as specified above)
- **Background**: None (transparent, not in card)
- **Color**: Text uses amber gradient for level number only

**Layout:**
```
Level 5
STYLIST
[Progress bar: 2,450 / 3,000 XP]
```

**Code Example:**
```tsx
<div className="text-center">
  <h3 className="text-xl font-display font-semibold 
    bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
    Level {level}
  </h3>
  <p className="text-sm text-[#C4BCB4] uppercase tracking-wider mt-1">
    {levelName}
  </p>
  <div className="mt-2">
    <ProgressBar current={xp} max={xpNeeded} />
    <p className="text-xs text-[#8A827A] mt-1">
      {xp} / {xpNeeded} XP
    </p>
  </div>
</div>
```

### Challenges

**Current State:** Bright colored cards, prominent borders

**Refined State:**
- **Card Background**: Surface (#2C2119)
- **Border**: 1px solid #3D2F24
- **Border radius**: 16px
- **Padding**: 16px
- **Active Challenge**: Border color → #FFB84C (amber, subtle)
- **Completed Challenge**: Opacity 60%, checkmark icon (green #10B981)
- **No bright colors**: All text uses existing color hierarchy

**Content:**
- **Title**: Challenge name (Body, 14px, textPrimary, font-medium)
- **Description**: Challenge details (Body Small, 13px, textSecondary)
- **Progress**: Progress bar (4px, amber gradient)
- **Reward**: "+75 XP" (Body Small, 13px, amber gradient text)

**Layout:**
```
┌─────────────────────────────────┐
│ Forgotten Gems Challenge        │
│ Wear 2 items dormant 60+ days   │
│ [Progress: ████████░░] 1/2     │
│ Reward: +75 XP                  │
└─────────────────────────────────┘
```

**Code Example:**
```tsx
<Card className="bg-[#2C2119] border border-[#3D2F24] 
  hover:border-[#FFB84C] transition-colors">
  <CardHeader>
    <CardTitle className="text-sm font-medium text-[#F8F5F1]">
      {challenge.name}
    </CardTitle>
    <CardDescription className="text-xs text-[#C4BCB4]">
      {challenge.description}
    </CardDescription>
  </CardHeader>
  <CardContent>
    <ProgressBar current={progress} max={challenge.goal} />
    <div className="flex justify-between items-center mt-2">
      <span className="text-xs text-[#8A827A]">
        {progress} / {challenge.goal}
      </span>
      <span className="text-xs bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
        +{challenge.reward} XP
      </span>
    </div>
  </CardContent>
</Card>
```

### AI Fit Score

**Current State:** Circular progress indicator with bright colors

**Refined State:**
- **Display**: Circular progress indicator (unchanged shape)
- **Background Circle**: #3D2F24 (surface variant)
- **Progress Circle**: Amber gradient (conic-gradient from #FFB84C to #FF9400)
- **Center Text**: Score number (H2, 24px, display font, amber gradient text)
- **Label**: "AI Fit Score" (Body Small, 13px, textSecondary)
- **Size**: 120px × 120px (circular)
- **Animation**: Smooth fill (600ms easeOut)

**Breakdown Display** (below circle):
- **Components**: Feedback Count, Preference Consistency, Prediction Confidence
- **Layout**: 3-column grid (mobile), horizontal (desktop)
- **Each Component**:
  - Label: "Feedback" (Body Small, 13px, textSecondary)
  - Value: "40 / 40" (Body, 14px, textPrimary)
  - Progress: 4px bar, amber gradient

**Code Example:**
```tsx
<div className="flex flex-col items-center gap-4">
  <div className="relative w-30 h-30">
    <svg className="w-30 h-30 transform -rotate-90">
      <circle
        cx="60"
        cy="60"
        r="54"
        fill="none"
        stroke="#3D2F24"
        strokeWidth="8"
      />
      <motion.circle
        cx="60"
        cy="60"
        r="54"
        fill="none"
        stroke="url(#amber-gradient)"
        strokeWidth="8"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: score / 100 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      />
    </svg>
    <div className="absolute inset-0 flex items-center justify-center">
      <span className="text-2xl font-display font-semibold
        bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
        {score}
      </span>
    </div>
  </div>
  <p className="text-xs text-[#8A827A]">AI Fit Score</p>
</div>
```

---

## Component Library Specifications

### FAB (Floating Action Button)

**Purpose:** Primary outfit generation trigger, always visible

**Specifications:**
- **Position**: Fixed bottom-right, 16px from edge, 80px from bottom (above nav)
- **Size**: 64px × 64px (square)
- **Background**: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
- **Border radius**: 50% (circle)
- **Shadow**: 0 8px 24px rgba(255, 180, 76, 0.4)
- **Z-index**: 50 (above content, below modals)
- **Icon**: Sparkles (Lucide), 28px, white (#F8F5F1)

**Animation - Breathing Pulse:**
```css
@keyframes breathe {
  0%, 100% { transform: scale(1.0); }
  50% { transform: scale(1.05); }
}

.fab {
  animation: breathe 2s ease-in-out infinite;
}
```

**Interaction States:**
- **Default**: Breathing pulse (as above)
- **Hover** (desktop): Shadow intensifies (0 12px 32px rgba(255, 180, 76, 0.5))
- **Press**: Scale(0.95) + blur overlay starts
- **Active**: Full-screen outfit generation initiated
- **Haptic**: Light tap (0.05s) on press

**Accessibility:**
- `aria-label`: "Generate outfit for today"
- `role`: "button"
- Keyboard: Space or Enter activates
- Focus: 2px amber ring with 2px offset

**Code Example:**
```tsx
<motion.button
  className="fixed bottom-20 right-4 w-16 h-16 rounded-full
    bg-gradient-to-r from-[#FFB84C] to-[#FF9400]
    shadow-lg shadow-amber-500/40
    flex items-center justify-center
    z-50"
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  animate={{
    scale: [1, 1.05, 1],
  }}
  transition={{
    duration: 2,
    repeat: Infinity,
    ease: "easeInOut"
  }}
  aria-label="Generate outfit for today"
>
  <Sparkles className="w-7 h-7 text-white" />
</motion.button>
```

### Bottom Sheet (Adjust Sheet)

**Purpose:** Single bottom sheet for outfit customization

**Specifications:**
- **Max height**: 90vh
- **Width**: Full-width (mobile), max-width 640px (desktop, centered)
- **Background**: Surface (#2C2119)
- **Border radius**: 24px (top corners only)
- **Padding**: 24px
- **Backdrop**: Blur overlay (backdrop-blur-sm, rgba(0,0,0,0.5))
- **Z-index**: 100 (above FAB)

**Animation:**
- **Open**: Slide up from bottom + fade
  - translateY: 100% → 0%
  - opacity: 0 → 1
  - Duration: 350ms
  - Easing: easeOut
- **Close**: Slide down + fade
  - translateY: 0% → 100%
  - opacity: 1 → 0
  - Duration: 300ms
  - Easing: easeIn

**Header:**
- **Title**: "Refine your look" (H3, 20px, display font)
- **Subtitle**: AI suggestion with weather (Body, 14px, textSecondary)
- **Close Button**: X icon, 44px × 44px, top-right

**Content Sections:**
- **Spacing**: 24px gap between sections
- **Labels**: Body Small (13px), textSecondary, uppercase, letter-spacing: 0.5px
- **Scroll**: Vertical scroll if content exceeds max height

**Code Example:**
```tsx
<Sheet open={isOpen} onOpenChange={setIsOpen}>
  <SheetContent side="bottom" className="h-[90vh] rounded-t-3xl">
    <SheetHeader>
      <SheetTitle className="text-xl font-display">Refine your look</SheetTitle>
      <SheetDescription className="text-sm text-[#C4BCB4]">
        {aiSuggestion} • {weather}
      </SheetDescription>
    </SheetHeader>
    <div className="mt-6 space-y-6 overflow-y-auto">
      {/* Occasion, Mood, Style, Base Item sections */}
    </div>
    <div className="sticky bottom-0 mt-6 pt-4 border-t border-[#3D2F24]">
      <Button className="w-full h-14 bg-[#1A1510] text-white">
        Generate Look
      </Button>
    </div>
  </SheetContent>
</Sheet>
```

### Chip Components

**Purpose:** Selectable options for Occasion, Mood, Style

**Base Specifications:**
- **Height**: 32px (Occasion, Style) or 36px (Mood)
- **Padding**: 12px 16px (Occasion, Style) or 10px 20px (Mood)
- **Border radius**: 16px (Occasion, Style) or 18px (Mood)
- **Font**: Body Small (13px) or Body (14px)
- **Gap**: 8px (Occasion, Style) or 12px (Mood)

**Default State:**
- **Background**: Transparent or Surface (#2C2119)
- **Border**: 1px solid #3D2F24
- **Text**: textPrimary (#F8F5F1)
- **Hover**: Background → #3D2F24

**Selected State:**
- **Background**: Amber gradient (Occasion) or #3D2F24 (Mood, Style)
- **Border**: None (Occasion) or 1px solid #FFB84C (Mood, Style)
- **Text**: #1A1510 (Occasion) or textPrimary (Mood, Style)

**Interaction:**
- **Tap**: Scale(0.95) → Scale(1.0)
- **Duration**: 150ms
- **Haptic**: Light tap (0.05s)

**Code Example:**
```tsx
<button
  className={cn(
    "h-8 px-4 rounded-2xl text-sm font-medium transition-all",
    "border",
    selected
      ? "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] border-transparent text-[#1A1510]"
      : "bg-transparent border-[#3D2F24] text-[#F8F5F1] hover:bg-[#3D2F24]"
  )}
  onClick={() => onSelect(value)}
>
  {label}
</button>
```

### Progress Bars

**Purpose:** Show progress for XP, challenges, unlocks

**Specifications:**
- **Height**: 4px (subtle, not prominent)
- **Background**: Surface variant (#3D2F24)
- **Fill**: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
- **Border radius**: 2px (fully rounded)
- **Animation**: Smooth fill (300ms easeOut)
- **Shadow**: None

**Code Example:**
```tsx
<div className="w-full h-1 bg-[#3D2F24] rounded-full overflow-hidden">
  <motion.div
    className="h-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400]"
    initial={{ width: 0 }}
    animate={{ width: `${percentage}%` }}
    transition={{ duration: 0.3, ease: "easeOut" }}
  />
</div>
```

### Toast Notifications

**Purpose:** XP gains, achievements, system messages

**Specifications:**
- **Position**: Fixed top-right, 16px from top, 16px from right
- **Size**: Min-width 240px, max-width 320px
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Padding**: 12px 16px
- **Border radius**: 12px
- **Shadow**: 0 4px 12px rgba(0, 0, 0, 0.3)
- **Z-index**: 50

**Animation:**
- **Enter**: Slide in from right + fade (opacity 0→1, translateX 20px→0)
- **Duration**: 250ms
- **Easing**: easeOut
- **Exit**: Slide out right + fade (opacity 1→0, translateX 0→20px)
- **Duration**: 200ms
- **Auto-dismiss**: 3 seconds

**Stacking**: Multiple toasts stack vertically with 8px gap

**Code Example:**
```tsx
<motion.div
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: 20 }}
  transition={{ duration: 0.25, ease: "easeOut" }}
  className="fixed top-4 right-4 z-50 min-w-[240px] max-w-[320px]
    bg-[#2C2119] border border-[#3D2F24] rounded-xl p-3 shadow-lg"
>
  {/* Content */}
</motion.div>
```

### Badge Components

**Purpose:** Display earned badges with unlock animations

**Specifications:**
- **Size**: 64px × 64px (square)
- **Background**: Surface (#2C2119) with 1px border (#3D2F24)
- **Border radius**: 16px
- **Icon**: Lucide icon, 24px, amber (#FFB84C)
- **Padding**: 20px (centered icon)

**Unlock Animation:**
- **Scale**: 0 → 1.1 → 1.0 (subtle bounce)
- **Rotate**: -5° → 5° → 0° (subtle wobble)
- **Duration**: 400ms
- **Easing**: easeOut
- **Shimmer**: Subtle amber glow
  - Box-shadow: 0 0 20px rgba(255, 180, 76, 0.3)
  - Duration: 600ms
  - Easing: easeInOut

**Rarity States:**
- **Common**: Border #3D2F24
- **Rare**: Border #3D2F24, subtle blue tint (#3B82F6 at 20% opacity)
- **Epic**: Border #3D2F24, subtle purple tint (#8B5CF6 at 20% opacity)
- **Legendary**: Border #FFB84C, amber glow

**Code Example:**
```tsx
<motion.div
  initial={{ scale: 0, rotate: -5 }}
  animate={{ scale: 1, rotate: 0 }}
  transition={{ 
    type: "spring",
    stiffness: 200,
    damping: 15
  }}
  className="w-16 h-16 bg-[#2C2119] border border-[#3D2F24] rounded-2xl
    flex items-center justify-center
    hover:border-[#FFB84C] transition-colors"
>
  <IconComponent className="w-6 h-6 text-[#FFB84C]" />
</motion.div>
```

### Card Variants

**Hero Card** (Daily Outfit):
- **Background**: Surface (#2C2119) with gradient overlay
- **Border radius**: 24px
- **Padding**: 24px (mobile) → 32px (desktop)
- **Shadow**: 0 12px 40px rgba(0, 0, 0, 0.4)
- **Border**: 1px solid amber gradient (subtle)

**Feature Card** (Important Content):
- **Background**: Surface (#2C2119) or amber gradient (context-dependent)
- **Border radius**: 20px
- **Padding**: 20px (mobile) → 24px (desktop)
- **Shadow**: 0 8px 24px rgba(0, 0, 0, 0.3)
- **Border**: None

**Default Card** (Browsing):
- **Background**: Surface (#2C2119)
- **Border radius**: 16px
- **Padding**: 16px (mobile) → 20px (desktop)
- **Shadow**: None
- **Border**: 1px solid #3D2F24

### Button Variants

**Primary Button:**
- **Background**: Amber gradient (linear-gradient(135deg, #FFB84C 0%, #FF9400 100%))
- **Text**: White or dark (#1A1510)
- **Padding**: 14px 24px (mobile) → 16px 32px (desktop)
- **Border radius**: 12px
- **Font**: Body (14px → 16px), font-medium (500)
- **Shadow**: 0 4px 12px rgba(255, 180, 76, 0.3)
- **Hover**: Shadow increase
- **Active**: Scale(0.98)

**Secondary Button:**
- **Background**: Transparent
- **Border**: 2px solid #3D2F24
- **Text**: textPrimary (#F8F5F1)
- **Padding**: 14px 24px
- **Border radius**: 12px
- **Hover**: Background → #3D2F24

**Ghost Button:**
- **Background**: None
- **Border**: None
- **Text**: textPrimary (#F8F5F1)
- **Padding**: 12px 16px
- **Hover**: Background → #3D2F24

---

## Animation & Micro-Interaction Refinements

### 3-Level Interaction Hierarchy (Maintained)

**Level 1: Browsing (Minimal - Silent & Sophisticated)**
- **Context**: Scrolling, minor taps, viewing lists
- **Visual**: Scale 1.0 → 1.02 (subtle grow)
- **Duration**: 80-120ms
- **Easing**: easeOut
- **Haptic**: None
- **Audio**: Silent

**Level 2: Core Actions (Medium - Satisfying Feedback)**
- **Context**: FAB tap, Generate Outfit, Save outfit, Primary CTAs
- **Visual**: Press scale(0.95), release scale(1.0)
- **Duration**: 250-400ms
- **Easing**: easeInOut
- **Haptic**: Light vibration (0.05-0.1s)
- **Audio**: Silent

**Level 3: Achievements (Celebration - Memorable Moments)**
- **Context**: Milestones, streaks, level ups, first outfit
- **Visual**: Shimmer effect (not confetti), modal, badge animation
- **Duration**: 1-2s
- **Easing**: easeOut with subtle bounce
- **Haptic**: Pattern rhythm (tap-pause-tap-tap)
- **Audio**: Silent (optional soft chime if enabled)

### Gamification-Specific Animations

**XP Notification:**
- **Enter**: Slide in from right + fade (250ms easeOut)
- **Exit**: Slide out right + fade (200ms easeIn)
- **No bounce, no pop**: Smooth, minimal

**Badge Unlock:**
- **Scale**: 0 → 1.1 → 1.0 (400ms spring)
- **Rotate**: -5° → 5° → 0° (subtle wobble)
- **Shimmer**: Amber glow pulse (600ms easeInOut)
- **No confetti**: Subtle glow only

**Progress Bar Fill:**
- **Width**: 0 → target percentage
- **Duration**: 300ms
- **Easing**: easeOut
- **No bounce**: Smooth fill

**Level Up:**
- **Text**: Scale 0 → 1.2 → 1.0 (500ms spring)
- **Background**: Fade in amber gradient (300ms)
- **No confetti**: Subtle shimmer only

### Shimmer Effects (Replacing Confetti)

**Purpose**: Subtle celebration without playful confetti

**Implementation:**
```css
@keyframes shimmer {
  0% { 
    box-shadow: 0 0 10px rgba(255, 180, 76, 0.3);
    opacity: 0.5;
  }
  50% { 
    box-shadow: 0 0 30px rgba(255, 180, 76, 0.6);
    opacity: 1;
  }
  100% { 
    box-shadow: 0 0 10px rgba(255, 180, 76, 0.3);
    opacity: 0.5;
  }
}

.shimmer {
  animation: shimmer 1.5s ease-in-out infinite;
}
```

**Usage:**
- Badge unlocks
- Level ups
- Major milestones
- **Not used for**: Regular XP gains, progress updates

### Amber Gradient Animations

**Gradient Pulse** (for active states):
```css
@keyframes gradient-pulse {
  0%, 100% { 
    background-position: 0% 50%;
  }
  50% { 
    background-position: 100% 50%;
  }
}

.gradient-pulse {
  background: linear-gradient(135deg, #FFB84C 0%, #FF9400 100%);
  background-size: 200% 200%;
  animation: gradient-pulse 3s ease-in-out infinite;
}
```

**Usage:**
- FAB breathing pulse
- Active challenge borders
- Selected chip backgrounds (subtle)

---

## Typography & Color Refinements

### Typography System (Maintained)

**Display Font**: Space Grotesk (headlines, hero moments)
- **Weights**: 500 (Medium), 600 (SemiBold), 700 (Bold)
- **Usage**: Page titles, outfit generation screens, level indicators

**Body Font**: Inter (UI, buttons, labels)
- **Weights**: 400 (Regular), 500 (Medium), 600 (SemiBold)
- **Usage**: All body text, buttons, labels, navigation

**Type Scale:**
- H1: 32px (mobile) → 40px (desktop)
- H2: 24px → 28px
- H3: 20px → 24px
- Body: 14px → 16px
- Body Small: 13px → 14px
- Caption: 12px

### Color System (Maintained)

**Dark Mode (Primary Theme):**
- Background: `#1A1510` (Amber-tinted dark)
- Surface: `#2C2119` (Cards/elevated surfaces)
- Surface Variant: `#3D2F24` (Hover states)
- Text Primary: `#F8F5F1` (Warm light neutral)
- Text Secondary: `#C4BCB4` (Muted)
- Text Tertiary: `#8A827A` (Subtle)

**Amber Gradients (Brand Signature):**
- Primary: `linear-gradient(135deg, #FFB84C 0%, #FF9400 100%)`
- Secondary: `linear-gradient(135deg, #FF9400 0%, #FF7700 100%)`
- Accent: `linear-gradient(135deg, #FFCC66 0%, #FFB84C 100%)`

### Gamification Color Usage

**Progress Bars:**
- Background: `#3D2F24` (Surface variant)
- Fill: Amber gradient (Primary)

**XP Notifications:**
- Background: `#2C2119` (Surface)
- Border: `#3D2F24` (Surface variant)
- Icon: `#FFB84C` (Amber)
- XP Text: Amber gradient (text-transparent with bg-clip-text)

**Badges:**
- Background: `#2C2119` (Surface)
- Border: `#3D2F24` (default) or `#FFB84C` (legendary)
- Icon: `#FFB84C` (Amber)

**Level Indicators:**
- Level Number: Amber gradient (text-transparent with bg-clip-text)
- Level Name: `#C4BCB4` (Text secondary)
- XP Text: `#8A827A` (Text tertiary)

**Challenges:**
- Background: `#2C2119` (Surface)
- Border: `#3D2F24` (default) or `#FFB84C` (active)
- Text: `#F8F5F1` (Text primary)
- Reward: Amber gradient (text-transparent with bg-clip-text)

### Text Color Hierarchy for Gamification

**Primary Information** (Level, XP amount, Challenge name):
- Color: `#F8F5F1` (Text primary) or Amber gradient
- Font: Body (14px) or H3 (20px for levels)
- Weight: Medium (500) or SemiBold (600)

**Secondary Information** (Level name, XP needed, Challenge description):
- Color: `#C4BCB4` (Text secondary)
- Font: Body Small (13px)
- Weight: Regular (400)

**Tertiary Information** (Progress labels, timestamps):
- Color: `#8A827A` (Text tertiary)
- Font: Caption (12px)
- Weight: Regular (400)

---

## Implementation Guide

### Priority Order for Refinements

**Phase 1: Core Gamification Refinements (Week 1)**
1. Progress bars (amber gradient, 4px height)
2. XP notifications (top-right toast, amber accent)
3. Badge unlock animations (shimmer, no confetti)
4. Level indicators (typography-based)

**Phase 2: Outfits Page Flow (Week 2)**
5. Minimal default state (Shuffle + Expand buttons)
6. Adjust bottom sheet (single sheet, all options)
7. Chip components (occasion, mood, style)

**Phase 3: Component Library (Week 3)**
8. FAB refinements (breathing pulse maintained)
9. Card variants (hero, feature, default)
10. Button variants (primary, secondary, ghost)

**Phase 4: Polish & Testing (Week 4)**
11. Animation refinements (shimmer effects)
12. Color consistency audit
13. Accessibility testing
14. Performance optimization

### Component-by-Component Update Checklist

**Gamification Components:**
- [ ] `XPNotification.tsx` - Refine to top-right toast, amber accent
- [ ] `BadgeDisplay.tsx` - Remove confetti, add shimmer effect
- [ ] `Progress` component (ui/progress.tsx) - 4px height, amber gradient
- [ ] `AIFitScoreCard.tsx` - Typography-based level indicator
- [ ] `ChallengeCard.tsx` - Minimal borders, no bright colors
- [ ] `CPWCard.tsx` - Amber gradient for progress
- [ ] `TVECard.tsx` - Amber gradient for progress

**Outfits Page Components:**
- [ ] `outfits/page.tsx` - Add Shuffle + Expand buttons
- [ ] `OutfitAdjustSheet.tsx` (new) - Single bottom sheet with all options
- [ ] Chip components (new) - Occasion, Mood, Style selectors
- [ ] Base item carousel (new) - Horizontal scrollable item selector

**Core Components:**
- [ ] `FloatingActionButton.tsx` - Maintain breathing pulse
- [ ] `BottomSheet.tsx` - Refine animation timings
- [ ] `Card` variants (ui/card.tsx) - Hero, feature, default
- [ ] `Button` variants (ui/button.tsx) - Primary, secondary, ghost

### Styling Migration Guide

**From Current to Refined:**

1. **Progress Bars:**
   ```tsx
   // Before: Bright colors, prominent
   <Progress className="h-2 bg-purple-100" />
   
   // After: Amber gradient, subtle
   <Progress className="h-1 bg-[#3D2F24]" />
   // Fill uses amber gradient
   ```

2. **XP Notifications:**
   ```tsx
   // Before: Large popup, purple gradient
   <div className="bg-gradient-to-r from-purple-500 to-pink-500">
   
   // After: Small toast, amber accent
   <div className="bg-[#2C2119] border border-[#3D2F24]">
   <Sparkles className="text-[#FFB84C]" />
   ```

3. **Badges:**
   ```tsx
   // Before: Confetti animation
   <Confetti />
   
   // After: Shimmer effect
   <div className="animate-shimmer" />
   ```

4. **Level Indicators:**
   ```tsx
   // Before: Icon-heavy
   <div className="flex items-center gap-2">
     <Icon /> Level {level}
   </div>
   
   // After: Typography-based
   <h3 className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
     Level {level}
   </h3>
   ```

### Testing Considerations

**Visual Testing:**
- [ ] All gamification elements use amber gradient (not bright colors)
- [ ] Progress bars are 4px height (subtle, not prominent)
- [ ] XP notifications are top-right toast (not center popup)
- [ ] Badges use shimmer (not confetti)
- [ ] Level indicators are typography-based (not icon-heavy)

**Interaction Testing:**
- [ ] All animations respect 3-level hierarchy
- [ ] Gamification uses Level 1-2 interactions (subtle)
- [ ] Only major achievements use Level 3 (celebration)
- [ ] All animations are smooth (60fps)
- [ ] Reduced motion is respected

**Accessibility Testing:**
- [ ] All touch targets are 44px minimum
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Screen reader labels are descriptive
- [ ] Keyboard navigation works
- [ ] Focus indicators are visible (2px amber ring)

**Performance Testing:**
- [ ] Animations use GPU-accelerated properties (transform, opacity)
- [ ] No layout shifts during animations
- [ ] Toast notifications don't stack excessively
- [ ] Badge animations don't cause jank

### Code Examples Repository

All component code examples are provided in their respective sections above. Key files to update:

**Frontend Components:**
- `frontend/src/components/gamification/XPNotification.tsx`
- `frontend/src/components/gamification/BadgeDisplay.tsx`
- `frontend/src/components/gamification/AIFitScoreCard.tsx`
- `frontend/src/components/gamification/ChallengeCard.tsx`
- `frontend/src/components/ui/progress.tsx`
- `frontend/src/app/outfits/page.tsx` (new Shuffle + Expand flow)
- `frontend/src/components/OutfitAdjustSheet.tsx` (new component)

**Styling:**
- `frontend/src/app/globals.css` (shimmer animations, amber gradients)
- `frontend/tailwind.config.ts` (color system, spacing)

---

## Summary

This blueprint provides comprehensive specifications for refining Easy Outfit App's UX/UI to align with "Sophisticated Gamification" while maintaining all existing functionality. The key principle is **refining visual styling, not removing features**.

**Key Takeaways:**
1. **Gamification is visible but refined** - Amber gradients, subtle animations, minimal notifications
2. **Outfits page is minimal by default** - Shuffle + Expand buttons, single bottom sheet
3. **All features remain** - Only visual styling changes
4. **"Silent Luxury" maintained** - Smooth, purposeful, sophisticated animations
5. **3-level hierarchy preserved** - Contextual feedback based on action importance

**Next Steps:**
1. Review this blueprint with design/development team
2. Prioritize Phase 1 refinements (gamification)
3. Create component update tickets
4. Implement refinements incrementally
5. Test and iterate

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Ready for Implementation

