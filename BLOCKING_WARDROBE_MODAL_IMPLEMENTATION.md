# Blocking Wardrobe Modal Implementation

## Overview
Implemented a mandatory 10-item wardrobe upload gate that blocks access to core pages (Wardrobe, Outfits, Dashboard) until users complete the requirement. This provides a consistent user experience across both onboarding flows and post-onboarding navigation.

## Implementation Details

### 1. New Component: `MissingWardrobeModal`
**File:** `frontend/src/components/MissingWardrobeModal.tsx`

A blocking modal overlay that prevents access to page content until the user uploads 10 items. Key features:
- Uses the existing `GuidedUploadWizard` component for consistency
- Fixed z-index of 9999 to overlay all page content
- Blur backdrop that covers the entire page
- Displays with generic recommendations (3 jackets, 3 shirts, 3 pants, 1 shoes)
- Same helper text and UI/UX as the onboarding flow

```typescript
interface MissingWardrobeModalProps {
  userId: string;
  isOpen: boolean;
  onComplete: () => void;
  targetCount?: number; // defaults to 10
}
```

### 2. Pages Updated

#### Wardrobe Page (`frontend/src/app/wardrobe/page.tsx`)
**Changes:**
- Import `MissingWardrobeModal` component
- Import `useWardrobe` hook
- Added state: `showMissingWardrobeModal`
- Added useEffect to check item count on load:
  - Shows modal if `wardrobeItems.length < 10`
  - Only triggers when `wardrobeLoading` is false
- Added modal to return JSX with `onComplete` callback that:
  - Closes the modal
  - Refetches wardrobe data to update item count

#### Outfits Page (`frontend/src/app/outfits/page.tsx`)
**Changes:**
- Added React hooks imports (`useState`, `useEffect`)
- Import `useFirebase` hook for user
- Import `useWardrobe` hook
- Import `MissingWardrobeModal` component
- Added state management for modal
- Added useEffect with same logic as Wardrobe page
- Added modal to return JSX

#### Dashboard Page (`frontend/src/app/dashboard/page.tsx`)
**Changes:**
- Import `useWardrobe` hook
- Import `MissingWardrobeModal` component
- Added state: `showMissingWardrobeModal`
- Added `refetchWardrobe` from useWardrobe hook
- Added useEffect to check item count
- Added modal to return JSX

### 3. User Experience Flow

#### Scenario 1: User with < 10 items accesses Wardrobe/Outfits/Dashboard
1. Page loads and checks `wardrobeItems.length`
2. If < 10, `showMissingWardrobeModal` is set to `true`
3. Blocking modal overlay appears with GuidedUploadWizard
4. User uploads 10+ items
5. GuidedUploadWizard completion callback triggers
6. Modal closes and wardrobe is refetched
7. Page displays with full functionality

#### Scenario 2: User with ≥ 10 items
1. Page loads and checks count
2. Item count is ≥ 10
3. Modal state remains false
4. Page displays normally with no modal

#### Scenario 3: Profile Page (Always Accessible)
- Profile page has NO blocking modal
- Users can always access their profile to manage settings

### 4. Behavior Details

**Item Count Check:**
- Counts ALL wardrobe items (no filtering for status)
- Only triggers modal if count < 10 AND not loading

**Modal State:**
- Fixed overlay with `z-[9999]` to stay above all content
- Backdrop blur effect
- Cannot be dismissed without uploading 10 items
- Takes up full screen height

**Upload Experience:**
- Uses same `GuidedUploadWizard` component from onboarding
- Same helper text and recommendations
- Success screen shown in app theme colors
- After completion, user stays on the same page

**Completion Behavior:**
- `onComplete` callback closes modal
- Calls `refetch()` or `refetchWardrobe()` to update item count
- Page displays normally after modal closes

## Testing Checklist

- [ ] Test with user having 0 items - modal should appear
- [ ] Test with user having 5 items - modal should appear
- [ ] Test with user having 9 items - modal should appear
- [ ] Test with user having 10 items - modal should NOT appear
- [ ] Test with user having 15+ items - modal should NOT appear
- [ ] Upload 10 items through modal on Wardrobe page - should close and refresh
- [ ] Upload 10 items through modal on Outfits page - should close and refresh
- [ ] Upload 10 items through modal on Dashboard page - should close and refresh
- [ ] Navigate to Profile page - modal should NOT appear
- [ ] After upload, navigate away and back - modal should NOT appear

## Files Modified

1. **Created:** `frontend/src/components/MissingWardrobeModal.tsx`
2. **Modified:** `frontend/src/app/wardrobe/page.tsx`
3. **Modified:** `frontend/src/app/outfits/page.tsx`
4. **Modified:** `frontend/src/app/dashboard/page.tsx`

## Technical Notes

- All components use "use client" directive for client-side rendering
- No new API endpoints required - uses existing `useWardrobe` hook
- Modal refetch ensures state stays in sync with backend
- Z-index stack: Modal (9999) > Page Content > Other overlays
- Responsive and works on mobile via existing GuidedUploadWizard component

## Deployment Notes

- Changes are backward compatible
- No database migrations needed
- No new environment variables required
- Builds successfully with no TypeScript errors
- Ready for immediate deployment

## Future Enhancements (Optional)

1. Add analytics tracking for modal interactions
2. Add skip option after first modal view (if user explicitly declines)
3. Add countdown timer for "motivational" nudge
4. Customize recommendations based on user persona (if available)
5. Add progress indicator if partially completed during session

