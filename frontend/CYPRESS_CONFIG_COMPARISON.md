# Cypress Config: Current vs. Recommended

## 📊 Current Configuration

```typescript
viewportWidth: 1280,    // Desktop default
viewportHeight: 720,    // Desktop default
```

## 🎯 Recommended Configuration (Based on App Infrastructure)

```typescript
viewportWidth: 390,     // iPhone 12 (most common mobile device)
viewportHeight: 844,    // Matches mobile height
```

## 📱 Why This Matters

### Your App's Breakpoints

**From `globals.css` and component code:**

```css
/* Mobile-first breakpoints */
@media (max-width: 640px) {  /* Mobile styles */
@media (min-width: 768px) {  /* Tablet styles */  
@media (min-width: 1024px) { /* Desktop styles */
```

**Current viewport (1280×720)** tests desktop view, missing:
- Mobile-specific styles (active below 640px)
- Tablet styles (768px-1024px)
- Touch target validations
- Mobile navigation patterns

### Key Findings from Your App

1. **Mobile-First Design** (`container-mobile` classes)
   - Padding changes: `px-4` → `sm:px-6` → `lg:px-8`
   - Layout stacks vertically on mobile

2. **Touch Targets** (WCAG AAA compliance)
   - Required: 44×44px minimum
   - Current tests found buttons at 36px (too small!)

3. **Typography** (16px minimum)
   - Prevents iOS zoom on input focus
   - Mobile-specific styles at `max-width: 640px`

4. **Critical Breakpoint: 768px**
   - Tailwind `md` breakpoint
   - Navigation changes here
   - Layout switches to tablet mode

## 🔄 Recommended Config Updates

### Option 1: Mobile-First Default
```typescript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 390,      // ✅ iPhone 12 (mobile-first)
    viewportHeight: 844,     // ✅ Mobile height
    // ... rest of config
  }
});
```

### Option 2: Multiple Configs (Recommended)
```typescript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    
    // Default to most common mobile size
    viewportWidth: 390,
    viewportHeight: 844,
    
    env: {
      mobileViewports: {
        // Critical breakpoint tests
        'mobile-360': { width: 360, height: 640 },      // Minimum width
        'mobile-375': { width: 375, height: 667 },      // iPhone SE (sm breakpoint)
        'mobile-390': { width: 390, height: 844 },      // iPhone 12 (default)
        'mobile-430': { width: 430, height: 932 },      // Large mobile
        
        // Critical: 768px breakpoint (md)
        'tablet-768': { width: 768, height: 1024 },     // ⚠️ Critical breakpoint!
        'tablet-820': { width: 820, height: 1180 },     // iPad Air
        
        // Desktop comparison
        'desktop-1024': { width: 1024, height: 768 },   // lg breakpoint
        'desktop-1280': { width: 1280, height: 720 },   // Current default
      }
    },
  }
});
```

## 📋 What Each Viewport Tests

### 360px (Minimum Width)
- Tests smallest supported device
- Validates no horizontal scroll
- Ensures content fits minimum viewport

### 375px (iPhone SE / sm breakpoint boundary)
- Tests right below Tailwind `sm` (640px)
- Validates mobile-only styles
- Checks `max-width: 640px` media queries

### 390px (iPhone 12 - Recommended Default)
- **Most common mobile device**
- Represents majority of users
- Good middle ground for mobile testing

### 430px (Largest iPhone)
- Tests largest mobile devices
- Validates touch target sizing
- Checks scaling behavior

### 768px (Critical Tablet Breakpoint) ⚠️
- **Tailwind `md` breakpoint**
- Navigation switches here
- Layout changes to tablet mode
- **MUST TEST THIS SIZE**

### 1024px (Desktop Breakpoint)
- Tailwind `lg` breakpoint
- Desktop navigation active
- Full layout capabilities

## 🎯 Testing Strategy

### Quick Tests (Run Always)
```bash
# Test critical mobile sizes
cy.setMobileViewport('mobile-390')  # iPhone 12 (most common)
cy.setMobileViewport('tablet-768')  # Critical breakpoint
```

### Comprehensive Tests (Full Suite)
```bash
# Test all breakpoints
All mobile viewports (360px - 430px)
Tablet viewports (768px, 820px)
Desktop viewports (1024px, 1280px)
```

## 📊 Priority Order

1. **390×844** (iPhone 12) - Default, most common
2. **768×1024** (iPad Mini) - Critical breakpoint
3. **375×667** (iPhone SE) - Small mobile test
4. **430×932** (iPhone 14 Pro Max) - Large mobile test
5. **1280×720** (Desktop) - Desktop comparison

## ✅ Action Items

1. **Change default viewport** from `1280×720` to `390×844`
2. **Add 768px viewport** (critical breakpoint) to test list
3. **Update test suites** to prioritize mobile sizes
4. **Document breakpoint strategy** in test files

## 🔍 Verification

After updating config, verify:
- ✅ Mobile navigation appears (not desktop nav)
- ✅ Touch targets are properly sized
- ✅ Mobile-specific styles are applied
- ✅ No horizontal scrolling
- ✅ Responsive typography scales correctly

---

**Recommendation**: Change default to `390×844` (iPhone 12) for mobile-first testing, keeping desktop as secondary priority.
