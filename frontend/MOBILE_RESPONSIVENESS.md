# Mobile Responsiveness Guide

This document outlines the mobile responsiveness implementation, testing guidelines, and best practices for the ClosetGPT frontend.

## 🎯 Overview

Our frontend is built with a **mobile-first approach** using Tailwind CSS and custom responsive utilities. All components are designed to work seamlessly across devices from mobile phones to desktop computers.

## 📱 Breakpoints

We use Tailwind CSS breakpoints with custom mobile-first utilities:

```css
/* Default (mobile first) */
/* sm: 640px and up */
/* md: 768px and up */
/* lg: 1024px and up */
/* xl: 1280px and up */
/* 2xl: 1536px and up */
```

## 🛠️ Responsive Utilities

### Container Utilities
```css
.container-mobile      /* px-4 sm:px-6 lg:px-8 */
.container-mobile-sm   /* px-2 sm:px-4 lg:px-6 */
.container-mobile-lg   /* px-6 sm:px-8 lg:px-12 */
```

### Text Utilities
```css
.text-responsive-sm    /* text-xs sm:text-sm */
.text-responsive-base  /* text-sm sm:text-base */
.text-responsive-lg    /* text-base sm:text-lg */
.text-responsive-xl    /* text-lg sm:text-xl */
```

### Grid Utilities
```css
.grid-responsive-2     /* grid-cols-1 sm:grid-cols-2 */
.grid-responsive-3     /* grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 */
.grid-responsive-4     /* grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 */
.grid-responsive-6     /* grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 */
```

### Spacing Utilities
```css
.space-responsive-sm   /* space-y-2 sm:space-y-3 */
.space-responsive-base /* space-y-3 sm:space-y-4 */
.space-responsive-lg   /* space-y-4 sm:space-y-6 */
.space-responsive-xl   /* space-y-6 sm:space-y-8 */
```

## 📋 Component Guidelines

### 1. Touch Targets
All interactive elements must meet minimum touch target requirements:

```css
/* Minimum 44px for primary actions */
.touch-target {
  min-height: 44px;
  min-width: 44px;
}

/* 32px for secondary actions */
.touch-target-sm {
  min-height: 32px;
  min-width: 32px;
}

/* 56px for important actions */
.touch-target-lg {
  min-height: 56px;
  min-width: 56px;
}
```

### 2. Text Sizing
Use responsive text utilities for optimal readability:

```tsx
// ✅ Good - Responsive text sizing
<Text className="text-responsive-base">
  This text adapts to screen size
</Text>

// ❌ Avoid - Fixed text sizes
<Text className="text-sm">
  This text stays small on all devices
</Text>
```

### 3. Image Handling
Images should be responsive and handle loading states:

```tsx
// ✅ Good - Responsive image with fallback
<Image
  src={item.imageUrl}
  alt={item.name}
  fill
  className="object-cover transition-transform duration-200 group-hover:scale-105"
  sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, (max-width: 1280px) 20vw, 16vw"
  onError={() => handleImageError(item.id)}
/>
```

### 4. Form Elements
Forms should be mobile-friendly with proper spacing:

```tsx
// ✅ Good - Mobile-friendly form
<form className="space-y-4">
  <div className="space-y-2">
    <Label htmlFor="name">Name</Label>
    <Input 
      id="name" 
      placeholder="Enter your name"
      className="touch-target" // Ensures minimum touch target
    />
  </div>
</form>
```

## 🔄 Loading States

### Skeleton Components
Use appropriate skeleton loaders for different content types:

```tsx
// Wardrobe items
<WardrobeItemSkeleton />

// Forms
<FormSkeleton />

// Lists
<ListSkeleton items={5} showImage={true} />

// Grids
<GridSkeleton columns={3} rows={2} />
```

### Spinner Components
```tsx
// Inline loading
<InlineLoading message="Loading data..." />

// Full screen overlay
<LoadingOverlay message="Processing..." />
```

## 🚨 Fallback States

### Empty States
```tsx
// Wardrobe empty
<WardrobeEmptyState onAddItems={handleAddItems} />

// Search no results
<SearchEmptyState searchQuery={query} onClearSearch={handleClear} />
```

### Error States
```tsx
// Network error
<NetworkErrorState onRetry={handleRetry} />

// Permission error
<PermissionErrorState onGoBack={handleGoBack} />
```

## 📱 Mobile-Specific Features

### Safe Area Support
```css
.safe-area-top    /* padding-top: env(safe-area-inset-top) */
.safe-area-bottom /* padding-bottom: env(safe-area-inset-bottom) */
.safe-area-left   /* padding-left: env(safe-area-inset-left) */
.safe-area-right  /* padding-right: env(safe-area-inset-right) */
```

### Touch Optimizations
```css
.tap-highlight-none /* -webkit-tap-highlight-color: transparent */
.no-scrollbar       /* Hide scrollbars on mobile */
```

## 🧪 Testing Guidelines

### 1. Device Testing
Test on actual devices when possible:
- iPhone (various sizes)
- Android phones (various sizes)
- Tablets (iPad, Android tablets)
- Desktop browsers

### 2. Browser Testing
Test across different browsers:
- Safari (iOS)
- Chrome (Android)
- Firefox
- Edge
- Chrome (Desktop)

### 3. Responsive Testing Tools
- Chrome DevTools Device Toolbar
- Firefox Responsive Design Mode
- BrowserStack (for real device testing)

### 4. Test Scenarios
For each component, test:
- [ ] Portrait orientation
- [ ] Landscape orientation
- [ ] Different screen sizes
- [ ] Touch interactions
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Accessibility (screen readers)

## 📊 Performance Considerations

### 1. Image Optimization
```tsx
// Use Next.js Image component with proper sizing
<Image
  src={imageUrl}
  alt={alt}
  fill
  sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 33vw"
  priority={isAboveFold}
/>
```

### 2. Lazy Loading
```tsx
// Lazy load components below the fold
const LazyComponent = lazy(() => import('./HeavyComponent'));

<Suspense fallback={<Skeleton />}>
  <LazyComponent />
</Suspense>
```

### 3. Bundle Size
- Use dynamic imports for large components
- Optimize images and assets
- Monitor bundle size with tools like `@next/bundle-analyzer`

## 🎨 Design System

### Color Palette
Our design system supports both light and dark modes with CSS custom properties:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  --primary: 0 0% 9%;
  /* ... more colors */
}
```

### Typography Scale
```css
.text-xs    /* 12px */
.text-sm    /* 14px */
.text-base  /* 16px */
.text-lg    /* 18px */
.text-xl    /* 20px */
.text-2xl   /* 24px */
```

### Spacing Scale
```css
.space-y-2  /* 8px */
.space-y-4  /* 16px */
.space-y-6  /* 24px */
.space-y-8  /* 32px */
```

## 🔧 Development Workflow

### 1. Component Development
1. Start with mobile design
2. Add responsive breakpoints
3. Test on multiple screen sizes
4. Add loading and error states
5. Test accessibility

### 2. Code Review Checklist
- [ ] Mobile-first approach used
- [ ] Touch targets meet minimum requirements
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Empty states provided
- [ ] Accessibility considerations
- [ ] Performance optimized

### 3. Testing Checklist
- [ ] Mobile devices tested
- [ ] Tablet devices tested
- [ ] Desktop browsers tested
- [ ] Touch interactions work
- [ ] Loading states display correctly
- [ ] Error states handle gracefully
- [ ] Empty states are helpful

## 📚 Resources

### Documentation
- [Tailwind CSS Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web.dev Responsive Design](https://web.dev/responsive-design/)

### Tools
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [BrowserStack](https://www.browserstack.com/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### Testing
- [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)
- [PageSpeed Insights](https://pagespeed.web.dev/)

## 🚀 Best Practices

1. **Mobile-First**: Always design for mobile first, then enhance for larger screens
2. **Touch-Friendly**: Ensure all interactive elements are easy to tap
3. **Fast Loading**: Optimize images and assets for mobile networks
4. **Progressive Enhancement**: Core functionality should work without JavaScript
5. **Accessibility**: Follow WCAG guidelines for mobile accessibility
6. **Performance**: Monitor and optimize for mobile performance
7. **Testing**: Test on real devices, not just simulators
8. **User Experience**: Consider mobile user behavior and patterns

## 📝 Notes

- Always test on real devices when possible
- Consider network conditions (3G, 4G, WiFi)
- Test with different user preferences (reduced motion, high contrast)
- Monitor Core Web Vitals for mobile performance
- Keep bundle sizes small for mobile users
- Use appropriate loading strategies for mobile networks 