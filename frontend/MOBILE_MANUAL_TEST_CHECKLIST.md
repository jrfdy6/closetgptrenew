# 📱 Mobile Manual Testing Checklist

## Quick Start

1. **Chrome DevTools**: Open DevTools → Toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M)
2. **Real Device**: Connect phone via USB or use remote testing tools
3. **Network Throttling**: Test on 3G/4G conditions

## Device Testing Matrix

### iOS Devices
- [ ] iPhone SE (375 × 667px)
- [ ] iPhone 12/13/14 (390 × 844px)
- [ ] iPhone 14 Pro Max (430 × 932px)
- [ ] iPad Mini (768 × 1024px)

### Android Devices
- [ ] Samsung Galaxy S20 (360 × 800px)
- [ ] Google Pixel 5 (393 × 851px)
- [ ] Samsung Galaxy Tab (768 × 1024px)

## Core User Flows

### ✅ Flow 1: New User Journey

#### Step 1: Landing Page
- [ ] Open app on mobile browser
- [ ] Verify logo displays correctly
- [ ] Check hero text is readable
- [ ] Verify CTA buttons are full-width
- [ ] Test tap on "Generate Today's Fit" button
- [ ] Test tap on "Start Style Quiz" button
- [ ] Check no horizontal scrolling
- [ ] Verify page loads quickly (< 3s)

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 2: Sign Up
- [ ] Tap "Sign Up" or navigate to signup page
- [ ] Verify form fields are accessible
- [ ] Test email input (no zoom on focus)
- [ ] Test password input (toggle visibility works)
- [ ] Verify submit button is easy to tap
- [ ] Test form validation messages
- [ ] Complete sign up flow
- [ ] Verify success redirect

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 3: Onboarding Quiz
- [ ] Start onboarding quiz
- [ ] Verify questions display clearly
- [ ] Test answer selection (easy to tap)
- [ ] Check progress indicator
- [ ] Test image upload (camera/gallery)
- [ ] Complete quiz
- [ ] Verify results display

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### ✅ Flow 2: Outfit Generation

#### Step 1: Dashboard Access
- [ ] Open dashboard
- [ ] Verify mobile navigation menu works
- [ ] Test hamburger menu open/close
- [ ] Check stats cards display correctly
- [ ] Verify quick actions are accessible

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 2: Generate Outfit
- [ ] Tap "Generate Outfit" button
- [ ] Select occasion, style, mood
- [ ] Verify filters are mobile-friendly
- [ ] Submit generation request
- [ ] Wait for outfit to generate
- [ ] Verify outfit displays correctly

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 3: View & Interact with Outfit
- [ ] View outfit details
- [ ] Test favorite button
- [ ] Test "Wear Today" button
- [ ] Test share functionality
- [ ] Test edit outfit (if available)
- [ ] Verify all buttons are easy to tap

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### ✅ Flow 3: Wardrobe Management

#### Step 1: View Wardrobe
- [ ] Navigate to wardrobe page
- [ ] Verify grid/list view toggle
- [ ] Check items display correctly
- [ ] Test scrolling performance
- [ ] Verify filters work on mobile

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 2: Add Items
- [ ] Tap "Add Item" or upload button
- [ ] Test camera access
- [ ] Test gallery selection
- [ ] Upload test image
- [ ] Verify upload progress
- [ ] Check item appears in wardrobe

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

#### Step 3: Manage Items
- [ ] Tap on wardrobe item
- [ ] View item details
- [ ] Test edit functionality
- [ ] Test delete functionality
- [ ] Verify swipe actions (if implemented)

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## UI Component Testing

### Navigation
- [ ] Mobile menu opens smoothly
- [ ] Menu items are easy to tap (≥44px)
- [ ] Menu closes when tapping outside
- [ ] Active page is highlighted
- [ ] Bottom navigation works (if present)
- [ ] Back button works (Android)

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Forms
- [ ] All inputs have readable text (≥16px)
- [ ] No zoom on input focus
- [ ] Labels are clear
- [ ] Error messages are visible
- [ ] Submit buttons are accessible
- [ ] Form validation works

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Buttons & CTAs
- [ ] All buttons are ≥44×44px
- [ ] Adequate spacing between buttons (≥8px)
- [ ] Button states are clear (pressed/active)
- [ ] Loading states are visible
- [ ] Icons are appropriately sized

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Modals & Dialogs
- [ ] Modals open smoothly
- [ ] Close button is easy to tap
- [ ] Tapping backdrop closes modal
- [ ] Modal content scrolls if needed
- [ ] Keyboard doesn't cover inputs
- [ ] Full-screen on small devices

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Images
- [ ] Images load quickly
- [ ] Images scale correctly
- [ ] Aspect ratios maintained
- [ ] Lazy loading works
- [ ] Placeholders display
- [ ] Error states handled

**Issues Found:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Performance Testing

### Load Times
- [ ] First Contentful Paint < 1.8s
- [ ] Time to Interactive < 3.5s
- [ ] Page loads fully < 5s on 4G
- [ ] Images load progressively

**Performance Notes:**
```
[ ] Slow page: 
[ ] Slow images: 
[ ] Slow API calls: 
```

### Network Conditions
- [ ] Works on 3G (slow connection)
- [ ] Works on 4G (normal connection)
- [ ] Handles offline gracefully
- [ ] Shows loading states

**Network Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Smooth Interactions
- [ ] Smooth scrolling (60fps)
- [ ] No jank during animations
- [ ] Buttons respond quickly
- [ ] No lag on tap

**Performance Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Accessibility Testing

### Touch Targets
- [ ] All interactive elements ≥44×44px
- [ ] Adequate spacing between targets
- [ ] No overlapping touch areas

**Accessibility Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Visual Accessibility
- [ ] Text is readable without zoom
- [ ] Contrast meets WCAG AA (4.5:1)
- [ ] Focus indicators are visible
- [ ] Dark mode works correctly

**Accessibility Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Screen Reader (Optional)
- [ ] Labels read correctly
- [ ] Buttons announced properly
- [ ] Navigation is logical
- [ ] Errors are announced

**Screen Reader Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Device-Specific Testing

### iOS (Safari)
- [ ] Respects safe area (notch)
- [ ] Pull to refresh works
- [ ] Back swipe gesture works
- [ ] Share sheet works
- [ ] Camera access works
- [ ] No 300ms tap delay

**iOS-Specific Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

### Android (Chrome)
- [ ] Respects system UI
- [ ] Hardware back button works
- [ ] Camera permission works
- [ ] File picker works
- [ ] Share intent works
- [ ] Status bar handled correctly

**Android-Specific Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Common Mobile Issues Checklist

- [ ] **Horizontal Scroll**: No unwanted horizontal scrolling
- [ ] **Text Zoom**: Inputs don't zoom on focus
- [ ] **Viewport Height**: Handles dynamic viewport (browser UI)
- [ ] **Safe Areas**: Respects notches and home indicators
- [ ] **Touch Delays**: No noticeable tap delay
- [ ] **Form Submission**: Works with mobile keyboards
- [ ] **Image Orientation**: Correct from camera
- [ ] **Modal Z-index**: Modals appear above all content
- [ ] **Fixed Elements**: Fixed headers/footers work correctly
- [ ] **Scrolling**: Momentum scrolling works smoothly

**Critical Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Dark Mode Testing

- [ ] Dark mode toggle works
- [ ] All colors have proper contrast
- [ ] Text remains readable
- [ ] Images display correctly
- [ ] UI elements are visible
- [ ] No white flashes

**Dark Mode Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Orientation Testing

### Portrait
- [ ] Layout works in portrait
- [ ] All content visible
- [ ] No horizontal scroll

### Landscape
- [ ] Layout adapts to landscape
- [ ] Content remains accessible
- [ ] Navigation works

**Orientation Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Browser Testing

### Mobile Browsers
- [ ] Safari (iOS)
- [ ] Chrome (Android)
- [ ] Firefox (Android)
- [ ] Samsung Internet
- [ ] Edge (mobile)

**Browser-Specific Issues:**
```
[ ] Issue 1: 
[ ] Issue 2: 
```

## Test Results Summary

### Test Date: _______________
### Tester: _______________
### Device(s) Tested: _______________
### Browser(s) Tested: _______________

### Overall Status
- [ ] ✅ All tests passed
- [ ] ⚠️ Minor issues found
- [ ] ❌ Critical issues found

### Priority Issues

**Critical (Fix Immediately):**
1. 
2. 
3. 

**High (Fix Soon):**
1. 
2. 
3. 

**Medium (Fix When Possible):**
1. 
2. 
3. 

**Low (Nice to Have):**
1. 
2. 
3. 

### Notes
```
Additional observations, feedback, or suggestions:
```

---

**Next Steps:**
1. Document all issues in issue tracker
2. Prioritize fixes
3. Retest after fixes
4. Update test checklist based on findings
