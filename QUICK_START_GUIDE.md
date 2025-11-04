# Easy Outfit App - Quick Start Guide
**"Silent Luxury" Mobile Web App**

---

## 🚀 **Getting Started**

### Live App
**Production:** https://my-app.vercel.app  
**Auto-deploys:** On push to `main` branch

### Local Development
```bash
# Frontend (from project root)
cd frontend
npm install
npm run dev
# Visit: http://localhost:3000

# Backend (from project root)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
# Runs on: http://localhost:3001
```

---

## 🎨 **Design System at a Glance**

### Colors
```
Dark Mode (Primary):
- Background: #1A1510 (amber-tinted)
- Cards: #2C2119
- Text: #F8F5F1

Light Mode:
- Background: #FAFAF9
- Cards: #FFFFFF
- Text: #1C1917

Brand Gradient:
#FFB84C → #FF9400 (amber to orange)
```

### Typography
```
Display: Space Grotesk (headlines)
Body: Inter (UI, content)

Headings: 32-40px
Body: 14-16px
Buttons: 14-16px
Captions: 12px
```

### Components
```
Navigation:
- Bottom Nav (4 items: Home, Closet, Looks, Profile)
- FAB (✨ floating action button with breathing pulse)

Wardrobe:
- 3-column grid (mobile-first)
- Filter pills (horizontal scroll)
- Bottom sheet (item details)

Outfit Generation:
- Progressive reveal (3s animation)
- Swipeable cards (Tinder-style)
- Micro-affirmations on save

Feedback:
- Level 1: Hover (scale 1.02, no haptic)
- Level 2: Tap (scale 0.95, light haptic)
- Level 3: Achievement (confetti, triple haptic)
```

---

## 📱 **Key Features**

### Navigation
- **Bottom Nav:** Always visible, 4 items, amber active states
- **FAB:** Breathing pulse animation, generates outfits
- **Skip Link:** Keyboard accessibility (Tab to focus)

### Wardrobe Browsing
- **3-column grid:** Dense, efficient, mobile-optimized
- **Filter pills:** Always visible, one-tap filtering
- **Bottom sheet:** Fast item details, swipe to dismiss

### Outfit Generation
- **Progressive reveal:** 3-second animation with floating clothing items
- **Swipeable cards:** Full-screen, Tinder-style gestures
- **Micro-affirmations:** "Nice. That's very 'you'." on save
- **Haptic feedback:** Light tap on save, triple tap on milestones

### Accessibility
- **Reduce motion:** Respects OS setting
- **High contrast:** Toggleable in settings
- **Large text:** 18px base option
- **Skip to content:** Keyboard navigation
- **44px touch targets:** WCAG compliance

### Audio (Silent Luxury)
- **Silent by default:** No embarrassment in public
- **Optional chime:** On outfit save (150ms)
- **Optional celebration:** On milestones (1s)
- **User choice:** Enable in settings

---

## 🛠️ **Common Tasks**

### Add New Component
```typescript
// 1. Create component in /frontend/src/components/
// 2. Use design system classes

import { cn } from "@/lib/utils";

export default function MyComponent() {
  return (
    <div className="card-surface rounded-xl p-6">
      <h2 className="heading-lg mb-4">Title</h2>
      <p className="text-body text-gray-600 dark:text-[#C4BCB4]">
        Content here
      </p>
      <button className="gradient-primary text-white px-6 py-3 rounded-xl text-button">
        Action
      </button>
    </div>
  );
}
```

### Trigger Micro-Interaction
```typescript
import { triggerInteraction, showToast } from '@/lib/utils/interactions';

// Level 2: Confirmation
triggerInteraction(2, {
  haptic: true,
  sound: 'chime',
  callback: () => {
    showToast("Saved!", "success");
  }
});

// Level 3: Achievement
triggerInteraction(3, {
  haptic: true,
  sound: 'celebration',
  callback: () => {
    showToast("7-day streak! 🔥", "success");
  }
});
```

### Use Bottom Sheet
```typescript
import BottomSheet from '@/components/BottomSheet';

const [showSheet, setShowSheet] = useState(false);

<BottomSheet
  isOpen={showSheet}
  onClose={() => setShowSheet(false)}
  title="Details"
>
  <div className="p-6">
    {/* Content */}
  </div>
</BottomSheet>
```

---

## 🎯 **CSS Utility Classes**

### Layout
```css
.card-surface → White card with dark mode support
.card-surface-variant → Cream/warm gray variant
.page-bg-light → #FAFAF9
.page-bg-dark → #1A1510
```

### Typography
```css
.font-display → Space Grotesk
.font-body → Inter
.heading-xl/lg/md/sm → Display font headings
.text-body/body-lg/body-sm → Body text
.text-button → Button text
.text-label → Label text
.text-caption → Small text
```

### Gradients
```css
.gradient-primary → #FFB84C to #FF9400
.gradient-secondary → #FF9400 to #FF7700
.gradient-accent → #FFCC66 to #FFB84C
```

### Animations
```css
.animate-fade-in → Fade + slide up
.animate-slide-up → Slide from bottom
.animate-scale-in → Scale from 0
.animate-breathe → Pulse (1.0 ↔ 1.05)
.animate-float-in-right/left/top/bottom → Rotating float
```

### Interactions
```css
.hover:scale-102 → Level 1
.active:scale-95 → Level 2
.scale-110 → Achievement pop
```

### Accessibility
```css
.high-contrast → High contrast mode
.large-text → 18px base font
.skip-to-content → Skip link
.scrollbar-hide → Hide scrollbar
```

---

## 🐛 **Troubleshooting**

### Build Fails
- Check for `export const dynamic` conflicts
- Verify all components have `"use client"`
- Check for missing imports

### FAB Not Showing
- Check if `mounted` state is true (client-side)
- Verify z-index (should be 50)
- Check bottom padding on page (should be pb-24)

### Animations Not Working
- Check if `prefers-reduced-motion` is enabled (OS setting)
- Verify animation classes are in globals.css
- Check browser support for transforms

### Haptics Not Working
- Only works on mobile devices
- Check Vibration API support
- Verify hapticsEnabled in localStorage

### Audio Not Playing
- Check soundsEnabled in localStorage (default: false)
- Verify audio files exist in /public/sounds/
- Check browser autoplay policy

---

## 📚 **Documentation**

- **Design System:** `/CLOSETGPT_DESIGN_SYSTEM.md` (1903 lines, comprehensive)
- **Phase 2 Summary:** `/PHASE_2_IMPLEMENTATION_SUMMARY.md` (540 lines)
- **This Guide:** `/QUICK_START_GUIDE.md`
- **Audio Spec:** `/frontend/public/sounds/README.md`

---

## ✨ **Key Interactions**

### BottomNav
- Tap icons to navigate
- Active state: Amber gradient with indicator line
- Sticky at bottom, 64px height

### FloatingActionButton (FAB)
- Always visible, bottom-right
- Breathing pulse animation
- Tap to generate outfit
- 64px size (highly tappable)

### Filter Pills
- Horizontal scroll on mobile
- Tap to select/deselect
- Active: Amber gradient
- Clear all button appears when filters active

### Bottom Sheet
- Swipe down to dismiss
- Tap backdrop to close
- Smooth spring animation
- Max height: 85vh

### Swipeable Outfit Card
- Left swipe: Remix
- Right swipe: Next
- Tap ❤️: Save (haptic + chime + affirmation)
- Swipe down: Close

---

## 🎬 **User Flows**

### Morning Ritual (Primary Loop)
```
Open app → Tap ✨ FAB → 3s animation → Swipeable card → Save ❤️ → Affirmation
```

### Wardrobe Browsing
```
Tap 👗 Closet → Filter pills → Tap item → Bottom sheet → Use in Outfit
```

### Settings
```
Tap 👤 Profile → Scroll to Accessibility → Toggle preferences
```

---

## 📊 **Performance Targets**

- **Animation FPS:** 60fps minimum
- **Grid scroll:** Smooth, no jank
- **Bottom sheet:** <300ms slide-up
- **Progressive reveal:** Exactly 3s
- **Touch response:** <100ms perceived
- **Filter tap:** Instant (<50ms)

---

## 🔐 **Authentication**

- **Firebase Auth:** Required for all personalized features
- **Guest Mode:** Not supported (requires user account)
- **Sign In:** `/signin`
- **Sign Up:** `/signup`
- **Protected Routes:** Dashboard, Wardrobe, Outfits, Profile

---

## 🎨 **Brand Voice**

### Microcopy Examples
```
"Let's get you dressed ✨"
"Nice. That's very 'you'."
"Your AI stylist is waiting..."
"Building your fit..."
"That's it. You nailed it."
```

### Tone
- Sophisticated, not pretentious
- Confident, not arrogant
- Encouraging, not pushy
- Fashion-forward, not intimidating
- Warm, not corporate

---

**Built with Next.js 14, React, TypeScript, Tailwind CSS, and dopamine psychology.** ✨

