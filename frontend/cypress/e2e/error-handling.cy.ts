describe('Error Handling', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/signin')
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })

  it('should handle network errors gracefully', () => {
    // Intercept API calls and force network errors
    cy.intercept('GET', '/api/outfits', { forceNetworkError: true }).as('outfitsError')
    cy.intercept('POST', '/api/outfits/generate', { forceNetworkError: true }).as('generateError')
    
    cy.visit('/outfits')
    
    // Should show error message for network issues
    cy.contains('Network error').should('exist')
    cy.contains('Please try again').should('exist')
    
    // Should provide retry option
    cy.get('button').contains('Retry').should('exist')
  })

  it('should handle invalid image uploads', () => {
    cy.visit('/wardrobe')
    cy.get('[data-testid="upload-button"]').click()
    
    // Try to upload invalid file
    cy.get('input[type="file"]').selectFile('cypress/fixtures/test.txt', { force: true })
    
    // Should show validation error
    cy.contains('Please upload a valid image').should('exist')
    cy.contains('Supported formats: JPG, PNG, WEBP').should('exist')
  })

  it('should handle server errors (500)', () => {
    cy.intercept('POST', '/api/outfits/generate', { statusCode: 500 }).as('serverError')
    
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    // Should show server error message
    cy.contains('Something went wrong').should('exist')
    cy.contains('Please try again later').should('exist')
  })

  it('should handle authentication errors (401)', () => {
    cy.intercept('GET', '/api/wardrobe', { statusCode: 401 }).as('authError')
    
    cy.visit('/wardrobe')
    
    // Should redirect to login
    cy.url().should('include', '/signin')
    cy.contains('Please sign in to continue').should('exist')
  })

  it('should handle permission errors (403)', () => {
    cy.intercept('DELETE', '/api/wardrobe/*', { statusCode: 403 }).as('permissionError')
    
    cy.visit('/wardrobe')
    cy.get('[data-testid="delete-item"]').first().click()
    cy.get('button').contains('Confirm').click()
    
    // Should show permission error
    cy.contains('You don\'t have permission').should('exist')
  })

  it('should handle not found errors (404)', () => {
    cy.visit('/nonexistent-page')
    
    // Should show 404 page
    cy.contains('Page not found').should('exist')
    cy.contains('Go back home').should('exist')
  })

  it('should handle validation errors in forms', () => {
    cy.visit('/profile')
    
    // Try to submit with invalid data
    cy.get('input[name="email"]').clear().type('invalid-email')
    cy.get('button[type="submit"]').click()
    
    // Should show validation errors
    cy.contains('Please enter a valid email').should('exist')
  })

  it('should handle timeout errors', () => {
    // Intercept with delay to simulate timeout
    cy.intercept('POST', '/api/outfits/generate', (req) => {
      req.reply({ delay: 60000 }) // 60 second delay
    }).as('timeoutError')
    
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    // Should show timeout message after reasonable time
    cy.contains('Request timed out', { timeout: 10000 }).should('exist')
  })

  it('should handle empty state gracefully', () => {
    // Clear all data to simulate empty state
    cy.intercept('GET', '/api/wardrobe', []).as('emptyWardrobe')
    cy.intercept('GET', '/api/outfits', []).as('emptyOutfits')
    
    cy.visit('/wardrobe')
    cy.contains('Your wardrobe is empty').should('exist')
    cy.contains('Start by uploading some photos').should('exist')
    
    cy.visit('/outfits')
    cy.contains('No outfits yet').should('exist')
    cy.contains('Generate your first outfit').should('exist')
  })

  it('should handle malformed data gracefully', () => {
    // Intercept with malformed data
    cy.intercept('GET', '/api/outfits', { invalid: 'data' }).as('malformedData')
    
    cy.visit('/outfits')
    
    // Should handle gracefully without crashing
    cy.get('body').should('not.contain', 'undefined')
    cy.get('body').should('not.contain', 'null')
  })

  it('should provide helpful error recovery options', () => {
    cy.intercept('POST', '/api/outfits/generate', { statusCode: 500 }).as('recoveryError')
    
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    // Should provide recovery options
    cy.contains('Try again').should('exist')
    cy.contains('Contact support').should('exist')
    cy.contains('Go back').should('exist')
  })

  it('should handle concurrent user errors', () => {
    // Simulate concurrent modification
    cy.intercept('PUT', '/api/profile', { statusCode: 409 }).as('concurrentError')
    
    cy.visit('/profile')
    cy.get('input[name="firstName"]').clear().type('New Name')
    cy.get('button[type="submit"]').click()
    
    // Should show conflict resolution message
    cy.contains('Someone else made changes').should('exist')
    cy.contains('Refresh to see latest changes').should('exist')
  })

  it('should handle rate limiting gracefully', () => {
    cy.intercept('POST', '/api/outfits/generate', { statusCode: 429 }).as('rateLimit')
    
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    // Should show rate limit message
    cy.contains('Too many requests').should('exist')
    cy.contains('Please wait a moment').should('exist')
  })
}) 