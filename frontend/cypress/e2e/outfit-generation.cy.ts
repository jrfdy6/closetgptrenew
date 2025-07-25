describe('Outfit Generation', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/signin')
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })

  it('should generate outfits for different occasions', () => {
    const occasions = ['casual', 'business', 'formal', 'athletic']
    
    occasions.forEach(occasion => {
      cy.visit('/outfits')
      cy.get('select[name="occasion"]').select(occasion)
      cy.get('button').contains('Generate Outfit').click()
      
      // Should show loading state
      cy.contains('Generating').should('exist')
      
      // Should generate outfit within reasonable time
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should display outfit items
      cy.get('[data-testid="outfit-item"]').should('have.length.at.least', 3)
      
      // Should show outfit details
      cy.contains(occasion).should('exist')
    })
  })

  it('should handle weather-based outfit generation', () => {
    cy.visit('/outfits')
    
    // Test different weather conditions
    const weatherConditions = [
      { temp: 'hot', condition: 'sunny' },
      { temp: 'cold', condition: 'snowy' },
      { temp: 'mild', condition: 'rainy' }
    ]
    
    weatherConditions.forEach(weather => {
      cy.get('select[name="weather"]').select(weather.condition)
      cy.get('button').contains('Generate Outfit').click()
      
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should show weather-appropriate items
      if (weather.temp === 'hot') {
        cy.contains('lightweight').should('exist')
      } else if (weather.temp === 'cold') {
        cy.contains('warm').should('exist')
      }
    })
  })

  it('should allow users to save and favorite outfits', () => {
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
    
    // Save outfit
    cy.get('button').contains('Save Outfit').click()
    cy.contains('Outfit saved').should('exist')
    
    // Favorite outfit
    cy.get('button[aria-label="Favorite"]').click()
    cy.get('button[aria-label="Favorite"]').should('have.class', 'favorited')
  })

  it('should handle empty wardrobe gracefully', () => {
    // Clear wardrobe (simulate empty state)
    cy.visit('/wardrobe')
    cy.get('[data-testid="delete-item"]').each(($el) => {
      cy.wrap($el).click()
      cy.get('button').contains('Confirm').click()
    })
    
    // Try to generate outfit
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    // Should show helpful message
    cy.contains('Add some clothes to your wardrobe').should('exist')
    cy.contains('Upload Photos').should('exist')
  })

  it('should regenerate outfits when requested', () => {
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
    
    // Get first outfit details
    cy.get('[data-testid="outfit-description"]').first().invoke('text').then((firstOutfit) => {
      // Regenerate
      cy.get('button').contains('Regenerate').click()
      cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
      
      // Should be different outfit
      cy.get('[data-testid="outfit-description"]').first().invoke('text').then((secondOutfit) => {
        expect(secondOutfit).to.not.equal(firstOutfit)
      })
    })
  })

  it('should provide outfit explanations', () => {
    cy.visit('/outfits')
    cy.get('button').contains('Generate Outfit').click()
    
    cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
    
    // Should show outfit explanation
    cy.get('[data-testid="outfit-explanation"]').should('exist')
    cy.get('[data-testid="outfit-explanation"]').should('not.be.empty')
  })
}) 