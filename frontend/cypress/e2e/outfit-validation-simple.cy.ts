describe('Outfit Generation Validation E2E', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/signin')
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })

  describe('Valid Outfit Generation', () => {
    it('should generate valid outfits with no errors', () => {
      cy.generateOutfit('casual', 'clear', 75)
      cy.waitForOutfitGeneration()
      
      // Should display outfit items (minimum 3)
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // Should NOT show any errors
      cy.expectOutfitValidation(false, true) // No errors, may have warnings
    })

    it('should handle formal occasions appropriately', () => {
      cy.generateOutfit('formal', 'clear', 70)
      cy.waitForOutfitGeneration()
      
      // Should generate outfit with formal items
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // Check for formal items
      cy.get('[data-testid="outfit-item"]').each(($item) => {
        const itemText = $item.text().toLowerCase()
        expect(itemText).to.satisfy((text: string) => 
          text.includes('shirt') || text.includes('pants') || text.includes('shoes') || 
          text.includes('dress') || text.includes('blazer') || text.includes('formal')
        )
      })
    })
  })

  describe('Soft Rule Violations - Warnings', () => {
    it('should generate outfits with warnings for soft violations', () => {
      // Test with hot weather that might trigger warnings
      cy.generateOutfit('casual', 'sunny', 90)
      cy.waitForOutfitGeneration()
      
      // Should still generate outfit
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // May show warnings but no errors
      cy.expectOutfitValidation(false, true) // No errors, may have warnings
    })

    it('should display warnings with proper styling', () => {
      cy.generateOutfit()
      cy.waitForOutfitGeneration()
      
      // Check if warnings are displayed properly
      cy.get('[data-testid="outfit-warning"]').then(($warnings) => {
        if ($warnings.length > 0) {
          cy.get('[data-testid="outfit-warning"]').first()
            .should('have.class', 'warning')
            .and('be.visible')
        }
      })
    })
  })

  describe('Hard Rule Violations - No Outfit', () => {
    it('should return empty when wardrobe is insufficient', () => {
      // Clear wardrobe first
      cy.visit('/wardrobe')
      cy.get('[data-testid="delete-item"]').each(($el) => {
        cy.wrap($el).click()
        cy.get('button').contains('Confirm').click()
      })
      
      // Try to generate outfit
      cy.generateOutfit()
      
      // Should show error message
      cy.contains('Add some clothes to your wardrobe').should('exist')
      cy.contains('Upload Photos').should('exist')
      
      // Should NOT show any outfits
      cy.get('[data-testid="outfit-item"]').should('not.exist')
    })

    it('should handle missing required categories', () => {
      // Test formal occasion which requires specific categories
      cy.generateOutfit('formal', 'clear', 70)
      
      cy.wait(5000)
      
      // Check for either outfit or error message
      cy.get('body').then(($body) => {
        if ($body.find('[data-testid="outfit-item"]').length > 0) {
          // Outfit was generated
          cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
        } else {
          // No outfit generated - should show error
          cy.contains('Unable to generate outfit').should('exist')
        }
      })
    })
  })

  describe('User Interaction with Validation', () => {
    it('should allow regeneration when validation issues occur', () => {
      cy.generateOutfit()
      cy.waitForOutfitGeneration()
      
      // Check if regenerate button is available
      cy.get('button').contains('Regenerate').should('exist')
      
      // Try regenerating
      cy.get('button').contains('Regenerate').click()
      
      // Should show loading state
      cy.contains('Generating').should('exist')
    })

    it('should display validation summary', () => {
      cy.generateOutfit()
      cy.waitForOutfitGeneration()
      
      // Check for validation summary component
      cy.get('[data-testid="validation-summary"]').should('exist')
      
      // Should show validation status
      cy.get('[data-testid="validation-status"]').should('exist')
    })
  })

  describe('Performance and Error Handling', () => {
    it('should complete generation within reasonable time', () => {
      cy.generateOutfit()
      
      // Should complete within 30 seconds
      cy.waitForOutfitGeneration()
      
      // Should not hang or crash
      cy.get('[data-testid="outfit-item"]').should('exist')
    })

    it('should handle network errors gracefully', () => {
      // Intercept API calls to simulate network errors
      cy.intercept('POST', '/api/outfit/generate', { forceNetworkError: true })
      
      cy.generateOutfit()
      
      // Should show error message
      cy.contains('Unable to generate outfit').should('exist')
      cy.contains('Please try again').should('exist')
    })
  })
}) 