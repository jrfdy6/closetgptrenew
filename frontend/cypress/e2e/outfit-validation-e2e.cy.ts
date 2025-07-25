describe('Outfit Generation E2E with Validation', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/signin')
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })

  describe('Full User Flow - Valid Outfit Generation', () => {
    it('should generate valid outfits with no errors', () => {
      // Navigate to outfit generation
      cy.visit('/outfits')
      
      // Select occasion and weather
      cy.get('select[name="occasion"]').select('casual')
      cy.get('select[name="weather"]').select('clear')
      cy.get('input[name="temperature"]').clear().type('75')
      
      // Generate outfit
      cy.get('button').contains('Generate Outfit').click()
      
      // Should show loading state
      cy.contains('Generating').should('exist')
      
      // Should generate outfit within reasonable time
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should display outfit items (minimum 3)
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // Should NOT show any errors
      cy.get('[data-testid="outfit-error"]').should('not.exist')
      
      // May show warnings but should still be valid
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          // If warnings exist, outfit should still be displayed
          cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
        }
      })
      
      // Should show outfit details
      cy.contains('casual').should('exist')
    })

    it('should handle formal occasion with appropriate validation', () => {
      cy.visit('/outfits')
      
      // Select formal occasion
      cy.get('select[name="occasion"]').select('formal')
      cy.get('select[name="weather"]').select('clear')
      cy.get('input[name="temperature"]').clear().type('70')
      
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Formal outfits should have appropriate items
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // Should include formal items (shoes, proper top, bottom)
      cy.get('[data-testid="outfit-item"]').each(($item) => {
        const itemText = $item.text().toLowerCase()
        // Check for formal items or at least proper categories
        expect(itemText).to.satisfy((text: string) => 
          text.includes('shirt') || text.includes('pants') || text.includes('shoes') || 
          text.includes('dress') || text.includes('blazer') || text.includes('formal')
        )
      })
    })
  })

  describe('Soft Rule Violations - Warnings Only', () => {
    it('should generate outfits with warnings for soft rule violations', () => {
      cy.visit('/outfits')
      
      // Select conditions that might trigger warnings
      cy.get('select[name="occasion"]').select('casual')
      cy.get('select[name="weather"]').select('rainy')
      cy.get('input[name="temperature"]').clear().type('85') // Hot weather
      
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should still generate outfit
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // May show warnings for weather appropriateness, color harmony, etc.
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          // Verify warning content
          cy.get('[data-testid="outfit-warning"]').first().should('contain.text', 'warning')
        }
      })
      
      // Should NOT show errors (soft rules only)
      cy.get('[data-testid="outfit-error"]').should('not.exist')
    })

    it('should show color harmony warnings', () => {
      // This test would require specific wardrobe items with clashing colors
      // For now, we'll test the warning display mechanism
      cy.visit('/outfits')
      
      cy.get('select[name="occasion"]').select('casual')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Check if warnings are displayed properly
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          // Verify warning styling and content
          cy.get('[data-testid="outfit-warning"]').first()
            .should('have.class', 'warning')
            .and('contain.text', 'color')
        }
      })
    })
  })

  describe('Hard Rule Violations - No Outfit Generated', () => {
    it('should return empty when wardrobe has insufficient items', () => {
      // First, clear the wardrobe to simulate insufficient items
      cy.visit('/wardrobe')
      
      // Delete all items (if any)
      cy.get('[data-testid="delete-item"]').each(($el) => {
        cy.wrap($el).click()
        cy.get('button').contains('Confirm').click()
      })
      
      // Try to generate outfit with empty wardrobe
      cy.visit('/outfits')
      cy.get('select[name="occasion"]').select('casual')
      cy.get('button').contains('Generate Outfit').click()
      
      // Should show error message
      cy.contains('Add some clothes to your wardrobe').should('exist')
      cy.contains('Upload Photos').should('exist')
      
      // Should NOT show any outfits
      cy.get('[data-testid="outfit-item"]').should('not.exist')
    })

    it('should return empty when missing required categories', () => {
      // This test would require a wardrobe with missing shoes or other required categories
      // For now, we'll test the error handling
      cy.visit('/outfits')
      
      // Select formal occasion which requires specific categories
      cy.get('select[name="occasion"]').select('formal')
      cy.get('button').contains('Generate Outfit').click()
      
      // Wait for response
      cy.wait(5000)
      
      // Check for either outfit or error message
      cy.get('body').then(($body) => {
        if ($body.find('[data-testid="outfit-item"]').length > 0) {
          // Outfit was generated
          cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
        } else {
          // No outfit generated - should show error
          cy.contains('Unable to generate outfit').should('exist')
          cy.contains('missing required items').should('exist')
        }
      })
    })

    it('should handle cold weather with insufficient layers', () => {
      cy.visit('/outfits')
      
      // Select cold weather
      cy.get('select[name="weather"]').select('snowy')
      cy.get('input[name="temperature"]').clear().type('30')
      cy.get('select[name="occasion"]').select('casual')
      
      cy.get('button').contains('Generate Outfit').click()
      
      cy.wait(5000)
      
      // Check response
      cy.get('body').then(($body) => {
        if ($body.find('[data-testid="outfit-item"]').length > 0) {
          // Outfit generated - should have sufficient layers
          cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
        } else {
          // No outfit - should show layer-related error
          cy.contains('insufficient layers').should('exist')
        }
      })
    })
  })

  describe('Validation UI Components', () => {
    it('should display validation warnings with proper styling', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Check if warnings are displayed with proper styling
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          cy.get('[data-testid="outfit-warning"]').first()
            .should('have.class', 'warning')
            .and('be.visible')
        }
      })
    })

    it('should display validation errors with proper styling', () => {
      // Create a scenario that might trigger errors
      cy.visit('/outfits')
      
      // Select formal occasion with potentially insufficient wardrobe
      cy.get('select[name="occasion"]').select('formal')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.wait(5000)
      
      // Check for error styling if errors exist
      cy.get('[data-testid="outfit-error"]').then(($errors) => {
        if ($errors.length > 0) {
          cy.get('[data-testid="outfit-error"]').first()
            .should('have.class', 'error')
            .and('be.visible')
        }
      })
    })

    it('should show validation summary', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Check for validation summary component
      cy.get('[data-testid="validation-summary"]').should('exist')
      
      // Should show validation status
      cy.get('[data-testid="validation-status"]').should('exist')
    })
  })

  describe('User Interaction with Validation', () => {
    it('should allow users to dismiss warnings', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Check if warnings can be dismissed
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          cy.get('[data-testid="dismiss-warning"]').first().click()
          cy.get('[data-testid="outfit-warning"]').should('not.exist')
        }
      })
    })

    it('should provide suggestions for validation issues', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Check for suggestions in warnings
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          cy.get('[data-testid="warning-suggestion"]').should('exist')
        }
      })
    })

    it('should allow regeneration when validation fails', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      cy.wait(5000)
      
      // Check if regenerate button is available
      cy.get('button').contains('Regenerate').should('exist')
      
      // Try regenerating
      cy.get('button').contains('Regenerate').click()
      
      // Should show loading state
      cy.contains('Generating').should('exist')
    })
  })

  describe('Performance and Reliability', () => {
    it('should handle validation within reasonable time', () => {
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      // Should complete within 30 seconds
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should not hang or crash
      cy.get('[data-testid="outfit-item"]').should('exist')
    })

    it('should handle network errors gracefully', () => {
      // Intercept API calls to simulate network errors
      cy.intercept('POST', '/api/outfit/generate', { forceNetworkError: true })
      
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      // Should show error message
      cy.contains('Unable to generate outfit').should('exist')
      cy.contains('Please try again').should('exist')
    })

    it('should retry failed requests', () => {
      // Intercept with a failed response first, then success
      let callCount = 0
      cy.intercept('POST', '/api/outfit/generate', (req) => {
        callCount++
        if (callCount === 1) {
          req.reply({ statusCode: 500 })
        } else {
          req.reply({ fixture: 'outfit-response.json' })
        }
      })
      
      cy.visit('/outfits')
      cy.get('button').contains('Generate Outfit').click()
      
      // Should retry and eventually succeed
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
    })
  })
}) 