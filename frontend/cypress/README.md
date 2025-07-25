# Cypress E2E Tests for Outfit Generation

This directory contains comprehensive End-to-End (E2E) tests for the outfit generation feature, including validation scenarios.

## Test Structure

### Core Test Files

1. **`outfit-validation-e2e.cy.ts`** - Comprehensive E2E tests covering:
   - Full user flow from login to outfit generation
   - Valid outfit generation with no errors
   - Soft rule violations (warnings only)
   - Hard rule violations (no outfit generated)
   - Validation UI components
   - User interaction with validation
   - Performance and error handling

2. **`outfit-validation-simple.cy.ts`** - Simplified tests using custom commands:
   - Focused on core validation scenarios
   - Uses reusable custom commands
   - Easier to maintain and understand

### Test Fixtures

- **`outfit-response.json`** - Sample successful outfit generation response
- **`outfit-error-response.json`** - Sample error response for failed generation

### Custom Commands

The tests use custom Cypress commands defined in `support/commands.ts`:

- `generateOutfit(occasion, weather, temperature)` - Generate outfit with specific parameters
- `expectOutfitValidation(shouldHaveErrors, shouldHaveWarnings)` - Check validation state
- `waitForOutfitGeneration()` - Wait for outfit generation to complete

## Running the Tests

### Prerequisites

1. Start the backend server:
   ```bash
   cd backend
   python -m src.app
   ```

2. Start the frontend server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Ensure you have test data:
   - Test user account: `testuser@example.com` / `TestPassword123!`
   - Some items in the wardrobe for testing

### Running Tests

```bash
# Run all E2E tests
npm run cypress:run

# Open Cypress UI
npm run cypress:open

# Run specific test file
npx cypress run --spec "cypress/e2e/outfit-validation-simple.cy.ts"
```

## Test Scenarios Covered

### 1. Valid Outfit Generation
- ✅ Generates outfits with no errors
- ✅ Handles different occasions appropriately
- ✅ Ensures minimum 3 items per outfit
- ✅ Validates outfit completeness

### 2. Soft Rule Violations (Warnings)
- ✅ Generates outfits even with warnings
- ✅ Displays warnings with proper styling
- ✅ Shows color harmony warnings
- ✅ Indicates weather appropriateness warnings

### 3. Hard Rule Violations (No Outfit)
- ✅ Returns empty when wardrobe insufficient
- ✅ Handles missing required categories
- ✅ Shows appropriate error messages
- ✅ Provides helpful suggestions

### 4. User Interaction
- ✅ Allows regeneration when issues occur
- ✅ Displays validation summary
- ✅ Shows validation status
- ✅ Handles warning dismissal

### 5. Performance & Reliability
- ✅ Completes within reasonable time (30s)
- ✅ Handles network errors gracefully
- ✅ Retries failed requests
- ✅ Shows loading states

## Validation Rules Tested

### Soft Rules (Warnings Only)
- Color harmony between items
- Weather appropriateness
- Style cohesion
- Body type compatibility
- Skin tone compatibility

### Hard Rules (Errors - No Outfit)
- Minimum 3 items required
- Required categories (shoes, top, bottom)
- Sufficient layers for weather
- No duplicate items

## Data Test IDs Used

The tests rely on these data-testid attributes in the UI:

- `outfit-item` - Individual outfit items
- `outfit-error` - Error messages
- `outfit-warning` - Warning messages
- `validation-summary` - Validation summary component
- `validation-status` - Validation status indicator
- `dismiss-warning` - Warning dismiss button
- `warning-suggestion` - Warning suggestions

## Debugging

### Common Issues

1. **Tests failing due to missing wardrobe items**
   - Ensure test user has sufficient items in wardrobe
   - Add test data setup in beforeEach if needed

2. **Network timeouts**
   - Check backend server is running
   - Verify API endpoints are accessible
   - Increase timeout values if needed

3. **UI elements not found**
   - Verify data-testid attributes are present
   - Check for dynamic content loading
   - Ensure proper wait conditions

### Debug Commands

```bash
# Run with video recording
npx cypress run --record

# Run with specific browser
npx cypress run --browser chrome

# Run with custom config
npx cypress run --config baseUrl=http://localhost:3000
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use custom commands when possible
3. Add appropriate data-testid attributes to UI components
4. Include both positive and negative test cases
5. Test edge cases and error scenarios
6. Document new test scenarios in this README 