describe('Mobile Responsiveness', () => {
  const viewports = [
    { width: 375, height: 667, device: 'iPhone SE' },
    { width: 414, height: 896, device: 'iPhone 11 Pro' },
    { width: 768, height: 1024, device: 'iPad' },
    { width: 1920, height: 1080, device: 'Desktop' }
  ]

  beforeEach(() => {
    // Login before each test
    cy.visit('/signin')
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })

  viewports.forEach(viewport => {
    it(`should display correctly on ${viewport.device}`, () => {
      cy.viewport(viewport.width, viewport.height)
      
      // Test navigation
      cy.visit('/dashboard')
      cy.get('nav').should('be.visible')
      
      // Test wardrobe page
      cy.visit('/wardrobe')
      cy.get('[data-testid="wardrobe-grid"]').should('be.visible')
      
      // Test outfits page
      cy.visit('/outfits')
      cy.get('[data-testid="outfit-generator"]').should('be.visible')
      
      // Test profile page
      cy.visit('/profile')
      cy.get('[data-testid="profile-form"]').should('be.visible')
    })
  })

  it('should have touch-friendly buttons on mobile', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/outfits')
    
    // Check button sizes are appropriate for touch
    cy.get('button').each(($button) => {
      cy.wrap($button).should('have.css', 'min-height', '44px')
      cy.wrap($button).should('have.css', 'min-width', '44px')
    })
  })

  it('should handle mobile navigation menu', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/dashboard')
    
    // Mobile menu should be accessible
    cy.get('[data-testid="mobile-menu-button"]').click()
    cy.get('[data-testid="mobile-menu"]').should('be.visible')
    
    // Menu items should be clickable
    cy.get('[data-testid="mobile-menu"]').contains('Wardrobe').click()
    cy.url().should('include', '/wardrobe')
  })

  it('should not have horizontal scrolling issues', () => {
    cy.viewport(375, 667) // iPhone SE
    
    const pages = ['/dashboard', '/wardrobe', '/outfits', '/profile']
    
    pages.forEach(page => {
      cy.visit(page)
      
      // Check for horizontal overflow
      cy.get('body').then(($body) => {
        const bodyWidth = $body[0].scrollWidth
        const viewportWidth = $body[0].clientWidth
        
        expect(bodyWidth).to.be.at.most(viewportWidth)
      })
    })
  })

  it('should handle image upload on mobile', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/wardrobe')
    cy.get('[data-testid="upload-button"]').click()
    
    // Should show mobile-friendly upload interface
    cy.get('[data-testid="upload-modal"]').should('be.visible')
    cy.get('input[type="file"]').should('be.visible')
  })

  it('should have readable text on mobile', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/dashboard')
    
    // Check text is readable
    cy.get('body').should('have.css', 'font-size', '16px')
    cy.get('h1, h2, h3').should('have.css', 'font-size').and('be.greater.than', '14px')
  })

  it('should handle keyboard input on mobile', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/profile')
    
    // Test form inputs work on mobile
    cy.get('input[name="firstName"]').type('Test')
    cy.get('input[name="firstName"]').should('have.value', 'Test')
    
    // Test textarea
    cy.get('textarea[name="bio"]').type('Test bio')
    cy.get('textarea[name="bio"]').should('have.value', 'Test bio')
  })

  it('should handle orientation changes', () => {
    cy.viewport(375, 667) // Portrait
    cy.visit('/dashboard')
    cy.get('[data-testid="dashboard-content"]').should('be.visible')
    
    cy.viewport(667, 375) // Landscape
    cy.get('[data-testid="dashboard-content"]').should('be.visible')
  })

  it('should have proper spacing on mobile', () => {
    cy.viewport(375, 667) // iPhone SE
    
    cy.visit('/wardrobe')
    
    // Check for adequate spacing between elements
    cy.get('[data-testid="wardrobe-item"]').each(($item) => {
      cy.wrap($item).should('have.css', 'margin-bottom', '16px')
    })
  })
}) 