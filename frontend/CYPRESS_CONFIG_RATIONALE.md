# Cypress Configuration Rationale
## Infrastructure & UX/UI Information to Guide Config Decisions

## 📱 Responsive Breakpoints (Tailwind Defaults)

### Tailwind Breakpoint System
```javascript
// Default Tailwind breakpoints (from tailwind.config.ts)
sm: '640px'   // Small devices (phones)
md: '768px'   // Medium devices (tablets)
lg: '1024px'  // Large devices (desktops)
xl: '1280px'  // Extra large devices
2xl: '1400px' // 2X Extra large devices (container max-width)
```

### App-Specific Breakpoint Usage
Based on codebase analysis:
- **Mobile**: 320px - 768px (uses: `sm`, `max-width: 640px` for typography)
- **Tablet**: 768px - 1024px (uses: `md`, `lg`)
- **Desktop**: 1024px+ (uses: `lg`, `xl`, `2xl`)

### Container Padding
```css
.container-mobile {
  px-4      /* 16px on mobile (< 640px) */
  sm:px-6   /* 24px on small devices (≥640px) */
  lg:px-8   /* 32px on large devices (≥1024px) */
}
```

## 🎯 Mobile-First Design Patterns

### Touch Target Requirements
**WCAG AAA Compliance** (from `globals.css`):
```css
/* All interactive elements */
button, [role="button"], input, select, textarea, a[role="button"] {
  min-height: 44px; /* Minimum touch target size */
}
```

**Test Requirements:**
- All buttons/interactive elements must be ≥44×44px
- Adequate spacing (8px minimum) between touch targets

### Typography Standards
**Mobile Readability** (from `globals.css`):
```css
/* Base font size - prevents zoom on iOS */
html { font-size: 16px; }

/* Mobile-specific (max-width: 640px) */
body { font-size: 16px; } /* Prevents zoom on focus */
input, textarea, select { font-size: 16px !important; }
```

**Test Requirements:**
- All inputs must have ≥16px font size
- Text must be readable without zooming

### Responsive Typography Scale
```css
.heading-xl {
  text-[32px]        /* Mobile: 32px */
  sm:text-[40px]     /* Small+: 40px */
}

.heading-lg {
  text-[24px]        /* Mobile: 24px */
  sm:text-[28px]     /* Small+: 28px */
}
```

## 🖼️ Image Optimization Configuration

### Next.js Image Configuration
```javascript
deviceSizes: [640, 750, 828, 1080, 1200, 1920]
imageSizes: [16, 32, 48, 64, 96, 128, 256, 384]
```

**Test Implications:**
- Test image loading at different viewport sizes
- Verify responsive image behavior
- Check image optimization on mobile

## 🎨 UI Component Patterns

### Mobile-First Card System
```css
.card-mobile {
  rounded-2xl        /* Mobile: 1rem border radius */
  sm:rounded-3xl     /* Tablet+: 1.5rem border radius */
}
```

### Container Patterns
```css
.container-mobile {
  w-full            /* Full width on mobile */
  px-4              /* 16px padding */
  sm:px-6           /* 24px padding on tablet */
  lg:px-8           /* 32px padding on desktop */
}
```

## 🌙 Dark Mode Support

**Configuration:**
- Dark mode: `class` strategy (Tailwind)
- Toggleable via theme switcher
- Affects all UI components

**Test Requirements:**
- Test both light and dark modes
- Verify contrast ratios
- Check theme persistence

## 📐 Viewport Recommendations for Cypress Config

### Priority Viewports Based on App Usage

#### Critical Mobile Devices
```typescript
'iphone-se': { width: 375, height: 667 }        // Smallest modern iPhone
'iphone-12': { width: 390, height: 844 }        // Standard iPhone (most common)
'iphone-14-pro-max': { width: 430, height: 932 } // Largest iPhone
```

**Rationale:**
- Covers 320px-430px mobile range
- Tests at breakpoint boundaries (<640px for mobile styles)
- Represents 80%+ of mobile users

#### Android Devices
```typescript
'galaxy-s20': { width: 360, height: 800 }       // Common Android size
'pixel-5': { width: 393, height: 851 }          // Google Pixel (common)
```

**Rationale:**
- Tests Android viewport variations
- 360px is minimum supported width
- 393px matches iPhone 12 closely

#### Tablet Devices
```typescript
'ipad-mini': { width: 768, height: 1024 }       // Tablet breakpoint boundary
'ipad-air': { width: 820, height: 1180 }        // Larger tablet
```

**Rationale:**
- 768px is Tailwind `md` breakpoint (critical)
- Tests tablet-specific layouts
- 820px tests between tablet/desktop

#### Desktop (Optional for Mobile Testing)
```typescript
'desktop-sm': { width: 1024, height: 768 }      // Tailwind `lg` breakpoint
'desktop-lg': { width: 1280, height: 720 }      // Standard desktop
'desktop-xl': { width: 1920, height: 1080 }     // Large desktop
```

## ⚙️ Recommended Cypress Config Enhancements

### Viewport Configuration
```typescript
const mobileViewports = {
  // Critical breakpoints
  'mobile-xs': { width: 360, height: 640 },      // Minimum supported
  'mobile-sm': { width: 375, height: 667 },      // iPhone SE (sm breakpoint test)
  'mobile-md': { width: 390, height: 844 },      // iPhone 12 (common)
  'mobile-lg': { width: 430, height: 932 },      // iPhone 14 Pro Max
  
  // Android variants
  'android-sm': { width: 360, height: 800 },     // Galaxy S20
  'android-md': { width: 393, height: 851 },     // Pixel 5
  
  // Tablet breakpoints (critical)
  'tablet-sm': { width: 768, height: 1024 },     // md breakpoint (critical!)
  'tablet-md': { width: 820, height: 1180 },     // iPad Air
  
  // Desktop (for comparison)
  'desktop-sm': { width: 1024, height: 768 },    // lg breakpoint
  'desktop-md': { width: 1280, height: 720 },    // Standard desktop
};
```

### Test Configuration Settings

#### Base URL
```typescript
baseUrl: 'http://localhost:3000'  // Dev server
// Or: 'https://your-production-url.vercel.app' for production tests
```

#### Viewport Defaults
```typescript
viewportWidth: 390,   // iPhone 12 (most common)
viewportHeight: 844,  // Match common mobile height
```

#### Retry Strategy
```typescript
retries: {
  runMode: 2,    // CI/CD: retry 2 times (flaky test handling)
  openMode: 0,   // Interactive: no retries (see failures immediately)
}
```

#### Screenshots & Videos
```typescript
video: false,                    // Disable by default (save space/time)
screenshotOnRunFailure: true,    // Always capture failures
```

#### Timeouts
```typescript
defaultCommandTimeout: 4000,     // 4s for commands (network requests)
pageLoadTimeout: 30000,          // 30s for page loads
requestTimeout: 5000,            // 5s for API requests
```

## 🎯 Testing Priorities

### Critical Tests (Run on All Viewports)
1. **No horizontal scroll** - Check at all breakpoints
2. **Touch target sizes** - Verify ≥44px on mobile
3. **Font readability** - Verify ≥16px inputs
4. **Responsive layout** - Test breakpoint transitions

### Breakpoint-Specific Tests

#### Mobile (< 640px)
- Single column layouts
- Stacked buttons
- Mobile navigation menu
- Full-width cards

#### Tablet (768px - 1024px)
- Multi-column grids
- Side-by-side buttons
- Tablet-optimized navigation
- Responsive typography

#### Desktop (≥ 1024px)
- Multi-column layouts
- Hover states
- Desktop navigation
- Optimal spacing

## 🔧 Environment-Specific Configurations

### Development
```typescript
baseUrl: 'http://localhost:3000',
watchForFileChanges: true,
```

### Staging
```typescript
baseUrl: 'https://staging.vercel.app',
```

### Production
```typescript
baseUrl: 'https://your-production-url.vercel.app',
```

## 📊 Performance Considerations

### Image Loading
- Test with slow 3G network
- Verify lazy loading behavior
- Check image optimization

### Page Load Times
- First Contentful Paint: < 1.8s
- Time to Interactive: < 3.5s
- Largest Contentful Paint: < 2.5s

### Network Conditions
```typescript
// Test with throttling
cy.visit('/', {
  onBeforeLoad: (win) => {
    // Simulate slow network
  }
});
```

## 🎨 Design System Alignment

### Color Testing
- Test light mode contrast
- Test dark mode contrast
- Verify WCAG AA compliance (4.5:1 ratio)

### Component Testing
- Card components (`card-mobile`)
- Navigation (`mobile-optimized-nav`)
- Forms (readable inputs)
- Buttons (touch targets)

## 📝 Config Recommendations Summary

### Must Have
1. ✅ Mobile viewports covering 360px - 430px range
2. ✅ Tablet viewports at 768px (critical breakpoint)
3. ✅ Touch target size validation (44px)
4. ✅ Font size validation (16px inputs)
5. ✅ Horizontal scroll detection

### Should Have
6. ✅ Multiple device sizes (iPhone, Android, iPad)
7. ✅ Breakpoint boundary testing (640px, 768px, 1024px)
8. ✅ Dark mode testing
9. ✅ Performance metrics

### Nice to Have
10. ✅ Network throttling tests
11. ✅ Orientation testing (portrait/landscape)
12. ✅ Browser-specific testing (Safari, Chrome)

## 🚀 Recommended Final Config Structure

```typescript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 390,  // iPhone 12 default
    viewportHeight: 844,
    
    // Mobile viewports covering critical breakpoints
    env: {
      mobileViewports: {
        // Mobile (< 640px)
        'mobile-xs': { width: 360, height: 640 },
        'mobile-sm': { width: 375, height: 667 },
        'mobile-md': { width: 390, height: 844 },
        'mobile-lg': { width: 430, height: 932 },
        
        // Tablet (768px+)
        'tablet-sm': { width: 768, height: 1024 },  // Critical breakpoint!
        'tablet-md': { width: 820, height: 1180 },
        
        // Desktop (for comparison)
        'desktop': { width: 1280, height: 720 },
      }
    },
    
    // Test execution
    retries: { runMode: 2, openMode: 0 },
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 4000,
    pageLoadTimeout: 30000,
    
    // Test patterns
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
  }
});
```

---

**Key Takeaways:**
1. **Breakpoints are critical** - Test at 640px, 768px, 1024px boundaries
2. **Mobile-first** - Prioritize mobile viewports (< 768px)
3. **Touch targets** - Always verify 44×44px minimum
4. **Font sizes** - Ensure 16px minimum to prevent zoom
5. **Responsive patterns** - Test container padding and layout changes
