# Blocking Wardrobe Modal - Architecture & Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Easy Outfit App Frontend                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            PAGES (Protected with Modal Check)                │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │   Wardrobe   │  │    Outfits   │  │  Dashboard   │       │   │
│  │  │    Page      │  │    Page      │  │    Page      │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │         │                 │                  │               │   │
│  │         └─────────────────┴──────────────────┘               │   │
│  │                     │                                        │   │
│  │              Check wardrobeItems.length < 10                │   │
│  │                     │                                        │   │
│  │         ┌───────────┴────────────┐                          │   │
│  │         ▼                        ▼                          │   │
│  │      YES (< 10)               NO (≥ 10)                    │   │
│  │         │                        │                          │   │
│  └─────────┼────────────────────────┼──────────────────────────┘   │
│            │                        │                              │
│            ▼                        ▼                              │
│  ┌──────────────────────┐  ┌──────────────────────┐               │
│  │ MissingWardrobeModal │  │  Show Page Normally  │               │
│  │  (BLOCKING OVERLAY)  │  │  (No Modal)          │               │
│  └──────────────────────┘  └──────────────────────┘               │
│         │                                                          │
│         ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │        GuidedUploadWizard                                │    │
│  │  (Same as Onboarding Flow)                              │    │
│  │  ┌────────────────────────────────────────────────────┐ │    │
│  │  │ "Let's Build Your Digital Wardrobe"                │ │    │
│  │  │ Recommended Items:                                 │ │    │
│  │  │ - 3 jackets                                        │ │    │
│  │  │ - 3 shirts                                        │ │    │
│  │  │ - 3 pants                                         │ │    │
│  │  │ - 1 shoes                                         │ │    │
│  │  │                                                    │ │    │
│  │  │ [Photo Best Practices Guide]                       │ │    │
│  │  │ [BatchImageUpload Component]                       │ │    │
│  │  │ [Progress Bar]                                     │ │    │
│  │  └────────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
│         │                                                          │
│         ▼                                                          │
│  Upload 10 Items                                                  │
│         │                                                          │
│         ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │        Success Screen                                   │    │
│  │  🎉 Wardrobe Ready!                                     │    │
│  │  You've added 10 items                                  │    │
│  │  Our AI is ready to generate outfits...                │    │
│  │                                                          │    │
│  │  [Redirecting...]                                       │    │
│  └──────────────────────────────────────────────────────────┘    │
│         │                                                          │
│         ▼                                                          │
│  onComplete() Callback Triggered                                  │
│         │                                                          │
│         ├─► setShowMissingWardrobeModal(false)                   │
│         └─► refetch() / refetchWardrobe()                        │
│             │                                                      │
│             ▼                                                      │
│         wardrobeItems.length updated (now ≥ 10)                   │
│         Modal automatically closes                                │
│         Page displays with full functionality                     │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │            PROFILE PAGE (Always Accessible)              │    │
│  │  ✅ No modal check                                       │    │
│  │  ✅ Always displays regardless of item count            │    │
│  │  ✅ User can access anytime                             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
App
├── Wardrobe Page
│   ├── Navigation
│   ├── Header
│   ├── FilterPills
│   ├── Tabs
│   │   ├── All Items Grid
│   │   ├── Favorites
│   │   ├── Recently Worn
│   │   └── Unworn
│   │
│   ├── MissingWardrobeModal (BLOCKING OVERLAY)
│   │   └── GuidedUploadWizard
│   │       ├── Wizard Intro Screen
│   │       │   ├── Title
│   │       │   ├── Recommendations List
│   │       │   ├── Photo Best Practices
│   │       │   └── Start Button
│   │       │
│   │       └── Upload Screen
│   │           ├── Progress Card
│   │           └── BatchImageUpload
│   │               ├── Dropzone
│   │               ├── File List
│   │               └── Upload Progress
│   │
│   └── ClientOnlyNav
│
├── Outfits Page
│   ├── Navigation
│   ├── Header with Buttons
│   ├── OutfitGrid
│   ├── MissingWardrobeModal (BLOCKING OVERLAY)
│   │   └── GuidedUploadWizard
│   └── ClientOnlyNav
│
├── Dashboard Page
│   ├── Navigation
│   ├── Stats
│   ├── Top Items
│   ├── Recent Outfits
│   ├── MissingWardrobeModal (BLOCKING OVERLAY)
│   │   └── GuidedUploadWizard
│   └── ClientOnlyNav
│
└── Profile Page (No Modal)
    ├── Navigation
    ├── User Settings
    ├── Account Info
    └── ClientOnlyNav
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER NAVIGATION                              │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PAGE COMPONENT LOADS                            │
│  (Wardrobe, Outfits, or Dashboard)                             │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│           useWardrobe() Hook Fetches Items                      │
│  const { items: wardrobeItems, loading: wardrobeLoading } = ... │
│                                                                  │
│  Makes API call to:                                            │
│  GET /api/wardrobe/items                                       │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│          useEffect Checks Item Count                            │
│  if (!wardrobeLoading && wardrobeItems.length < 10)            │
│    setShowMissingWardrobeModal(true)                           │
└─────────────────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────┬──────────────────────┐
              ▼                             ▼                      ▼
        < 10 items               >= 10 items              Page Re-render
              │                       │                        │
              ▼                       ▼                        ▼
    Modal Opens              No Modal Shows         Normal Page Display
    (BLOCKING)               (Page Normal)              (Full Access)
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│      User Uploads Items (GuidedUploadWizard)                   │
│  - BatchImageUpload component handles uploads                   │
│  - Each item processed and saved                                │
│  - Progress tracked in real-time                                │
│  - Success screen shown when complete                           │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│         onComplete() Callback Triggered                         │
│  - setShowMissingWardrobeModal(false)                          │
│  - refetch() or refetchWardrobe()                              │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│      useWardrobe() Re-Fetches Item Count                       │
│  (New data with all 10+ items)                                 │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│          useEffect Checks Count Again                           │
│  if (!wardrobeLoading && wardrobeItems.length < 10) → FALSE    │
│    setShowMissingWardrobeModal(false)                          │
│                                                                  │
│  Modal already closed, no change needed                        │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│               PAGE RE-RENDERS                                   │
│  - Modal not shown (showMissingWardrobeModal = false)          │
│  - Full page content displays                                  │
│  - User has full access                                        │
│  - Page state maintained (same URL, same scroll position)      │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
        USER CAN NOW ACCESS PAGE FULLY
```

---

## State Management

```typescript
// Each page maintains this state:

const [showMissingWardrobeModal, setShowMissingWardrobeModal] = useState(false);

// Input from useWardrobe hook:
const { 
  items: wardrobeItems,           // Array of ClothingItem
  loading: wardrobeLoading,       // boolean: true while fetching
  refetch                         // Function to refresh items
} = useWardrobe();

// Logic:
useEffect(() => {
  // Only check when NOT loading and we have data
  if (!wardrobeLoading && wardrobeItems.length < 10) {
    // Show blocking modal
    setShowMissingWardrobeModal(true);
  }
}, [wardrobeLoading, wardrobeItems.length]);

// Output to MissingWardrobeModal:
<MissingWardrobeModal
  userId={user?.uid || ''}
  isOpen={showMissingWardrobeModal}           // Control visibility
  onComplete={() => {
    setShowMissingWardrobeModal(false);       // Close modal
    refetch();                                // Refresh item count
  }}
  targetCount={10}
/>
```

---

## CSS/Styling Architecture

```
MissingWardrobeModal Overlay
├── Position: fixed inset-0 z-[9999]
│   └── Covers entire viewport, highest z-index
│
├── Background: bg-background/80
│   └── Semi-transparent background
│
├── Backdrop: backdrop-blur-sm
│   └── Blurs content behind
│
├── Layout: flex items-center justify-center
│   └── Centers content vertically and horizontally
│
└── Content: w-full h-full
    └── Takes full screen (GuidedUploadWizard fills space)
        ├── Card styling (border, rounded, shadow)
        ├── Gradient backgrounds (copper/gold theme)
        ├── Progress bar
        ├── Badge for item count
        └── Buttons with hover states
```

---

## User Journey Map

```
START: User Creates Account
   │
   ├─► Onboarding Quiz
   │   ├─► Gender/Body Type
   │   ├─► Style Preferences
   │   ├─► Personal Info
   │   └─► Style Persona Result
   │
   ├─► TWO POSSIBLE FLOWS:
   │   │
   │   ├─ Flow 1: Sign up → Quiz → Persona → GuidedUploadWizard
   │   │
   │   └─ Flow 2: Quiz → Sign up → Persona → GuidedUploadWizard
   │
   ├─► GuidedUploadWizard (Onboarding)
   │   ├─► Upload 10 items
   │   ├─► Success screen
   │   └─► Redirect to Outfit Generator
   │
   └─► DASHBOARD (First time with < 10 items)
       ├─ MissingWardrobeModal appears
       │ └─► Same GuidedUploadWizard
       │     └─► Upload 10 items
       │         └─► Success → Modal closes
       │
       └─ User can now access:
          ├─ Wardrobe page (+ Modal if < 10 items)
          ├─ Outfits page (+ Modal if < 10 items)
          ├─ Dashboard page (+ Modal if < 10 items)
          ├─ Profile page (✅ Always accessible)
          └─ Outfit Generator

RESULT: User has 10+ items and full app access
```

---

## Decision Tree

```
                    USER VISITS PAGE
                          │
                          ▼
                  Is page Wardrobe/Outfits/Dashboard?
                   /                              \
                  YES                             NO (Profile, etc)
                  │                               │
                  ▼                               ▼
          Check wardrobeItems              Render page
          Already loaded?                  normally
                  │                        (no modal)
                  ▼
           Is loading complete?
               /        \
              NO         YES
              │          │
              Wait       ▼
                   wardrobeItems.length < 10?
                      /              \
                     YES             NO
                     │               │
                     ▼               ▼
              Show Modal         Show Page
              (BLOCKING)         (Normal)
                     │
                     ▼
          User Uploads 10+ Items
                     │
                     ▼
          onComplete() Callback
                     │
                     ├─► Close Modal
                     ├─► Refetch Items
                     │
                     ▼
          Re-check: wardrobeItems.length < 10?
                     │
                     NO → Modal hidden
                     │
                     ▼
          Page Displays Normally
             (Full Access)
```

---

## Browser DevTools Inspection

```
When modal is open:

DOM Structure:
<div class="min-h-screen">
  <Navigation />
  
  <!-- Modal Overlay -->
  <div class="fixed inset-0 z-[9999] bg-background/80 backdrop-blur-sm...">
    <div class="w-full h-full">
      <!-- GuidedUploadWizard content -->
      <div class="min-h-screen bg-background flex items-center justify-center...">
        <Card class="max-w-4xl w-full">
          <!-- Upload wizard UI -->
        </Card>
      </div>
    </div>
  </div>
  
  <!-- Page content behind (invisible due to overlay) -->
  <main>...</main>
  
  <ClientOnlyNav />
</div>

Z-Index Stack:
- MissingWardrobeModal overlay: z-[9999]  ← Top (visible)
- Page content:                 z-auto    ← Behind (hidden)
- Navigation bar:               z-50      ← Behind (hidden)

Computed Styles:
- Modal: display: block (or flex)
- Backdrop: filter: blur(4px)
- Background: rgba(0, 0, 0, 0.2)
- Cursor: default (no dismiss cursor)
```

---

This architecture ensures a consistent, non-dismissible blocking experience that requires users to complete the 10-item requirement before accessing core app functionality, while maintaining a seamless user experience through reuse of existing components and patterns.

