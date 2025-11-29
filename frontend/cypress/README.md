# Cypress Mobile Testing Setup

This directory contains automated end-to-end tests for mobile UX/UI testing of Easy Outfit App.

## Structure

```
cypress/
├── e2e/
│   └── mobile/          # Mobile-specific tests
│       ├── homepage.cy.ts
│       ├── authentication.cy.ts
│       ├── navigation.cy.ts
│       ├── dashboard.cy.ts
│       └── outfits.cy.ts
├── support/
│   ├── e2e.ts          # Global test setup
│   └── commands.ts     # Custom Cypress commands
└── fixtures/           # Test data (if needed)
```

## Running Tests

### Run All Mobile Tests
```bash
npm run test:e2e:mobile
```

### Open Cypress UI (Interactive)
```bash
npm run test:e2e:mobile:open
```

### Run Specific Test File
```bash
npx cypress run --spec "cypress/e2e/mobile/homepage.cy.ts"
```

### Run with Specific Viewport
```bash
npx cypress run --config viewportWidth=375,viewportHeight=667
```

## Custom Commands

### `cy.setMobileViewport(device)`
Set viewport to a specific mobile device size.

**Available devices:**
- `iphone-se` (375 × 667px)
- `iphone-12` (390 × 844px)
- `iphone-14-pro-max` (430 × 932px)
- `galaxy-s20` (360 × 800px)
- `pixel-5` (393 × 851px)
- `ipad-mini` (768 × 1024px)
- `ipad-air` (820 × 1180px)

**Example:**
```typescript
cy.setMobileViewport('iphone-12');
cy.visit('/');
```

### `cy.hasMinimumTouchTarget()`
Check if an element meets minimum touch target size (44×44px).

**Example:**
```typescript
cy.get('button').hasMinimumTouchTarget();
```

### `cy.checkNoHorizontalScroll()`
Verify that the page doesn't have unwanted horizontal scrolling.

**Example:**
```typescript
cy.visit('/');
cy.checkNoHorizontalScroll();
```

### `cy.hasReadableText()`
Check if an input field has readable font size (≥16px to prevent zoom).

**Example:**
```typescript
cy.get('input[type="email"]').hasReadableText();
```

### `cy.testMobileNav()`
Test mobile navigation menu functionality.

**Example:**
```typescript
cy.testMobileNav();
```

## Writing New Tests

### Test Structure
```typescript
describe('Feature Name', () => {
  const devices = ['iphone-se', 'iphone-12'] as const;

  devices.forEach((device) => {
    describe(`Feature on ${device}`, () => {
      beforeEach(() => {
        cy.setMobileViewport(device);
        cy.visit('/page');
      });

      it('should work correctly', () => {
        // Your test here
        cy.checkNoHorizontalScroll();
      });
    });
  });
});
```

### Best Practices

1. **Always check for horizontal scroll** on each page
2. **Test touch targets** - ensure all interactive elements are ≥44px
3. **Test readability** - verify font sizes are ≥16px for inputs
4. **Test multiple devices** - use the devices array pattern
5. **Wait for page loads** - use `cy.wait()` appropriately
6. **Handle authentication** - either mock or use test credentials

## Viewport Testing

All mobile tests run across multiple viewports to ensure responsive design works correctly. Tests automatically run for:
- Small mobile devices (iPhone SE)
- Standard mobile devices (iPhone 12)
- Large mobile devices (iPhone 14 Pro Max)
- Tablets (iPad Mini)

## Continuous Integration

Mobile tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run mobile E2E tests
  run: npm run test:e2e:mobile
```

## Debugging

### Run Tests in Headed Mode
```bash
npx cypress run --headed
```

### Take Screenshots
Tests automatically take screenshots on failure. Check `cypress/screenshots/` directory.

### Video Recording
Videos are disabled by default but can be enabled in `cypress.config.ts`:
```typescript
video: true,
```

## Troubleshooting

### Tests Fail on CI but Pass Locally
- Check viewport differences
- Verify network conditions
- Check timing issues (add `cy.wait()`)

### Elements Not Found
- Use `cy.wait()` for dynamic content
- Check if element is visible with `should('be.visible')`
- Use data-testid attributes for reliable selectors

### Authentication Issues
- Mock authentication in tests
- Use test credentials if needed
- Check for redirects to signin page

## Resources

- [Cypress Documentation](https://docs.cypress.io/)
- [Mobile Testing Guide](../MOBILE_UX_TESTING_GUIDE.md)
- [Manual Testing Checklist](../MOBILE_MANUAL_TEST_CHECKLIST.md)
