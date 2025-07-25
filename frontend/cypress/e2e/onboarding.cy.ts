describe('Onboarding Flow', () => {
  beforeEach(() => {
    // Clear any existing data and start fresh
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  it('should allow a new user to complete onboarding', () => {
    cy.visit('/signup')
    
    // Fill out signup form
    cy.get('input[name="email"]').type('testuser@example.com')
    cy.get('input[name="password"]').type('TestPassword123!')
    cy.get('input[name="confirmPassword"]').type('TestPassword123!')
    cy.get('button[type="submit"]').click()
    
    // Should redirect to onboarding
    cy.url().should('include', '/onboarding')
    
    // Complete onboarding steps
    cy.contains('Welcome').should('exist')
    
    // Step 1: Basic Info
    cy.get('input[name="firstName"]').type('Test')
    cy.get('input[name="lastName"]').type('User')
    cy.get('select[name="gender"]').select('female')
    cy.get('button').contains('Next').click()
    
    // Step 2: Style Preferences
    cy.get('input[name="stylePreference"]').type('casual')
    cy.get('button').contains('Next').click()
    
    // Step 3: Body Type
    cy.get('input[name="bodyType"]').type('athletic')
    cy.get('button').contains('Next').click()
    
    // Step 4: Color Preferences
    cy.get('input[name="colorPalette"]').type('neutral')
    cy.get('button').contains('Next').click()
    
    // Step 5: Budget
    cy.get('input[name="budget"]').type('100')
    cy.get('button').contains('Finish').click()
    
    // Should complete onboarding and redirect to dashboard
    cy.url().should('include', '/dashboard')
    cy.contains('Welcome').should('exist')
  })

  it('should handle onboarding validation errors', () => {
    cy.visit('/onboarding')
    
    // Try to proceed without filling required fields
    cy.get('button').contains('Next').click()
    
    // Should show validation errors
    cy.contains('required').should('exist')
  })

  it('should allow users to go back and edit previous steps', () => {
    cy.visit('/onboarding')
    
    // Fill first step
    cy.get('input[name="firstName"]').type('Test')
    cy.get('input[name="lastName"]').type('User')
    cy.get('button').contains('Next').click()
    
    // Go back and edit
    cy.get('button').contains('Back').click()
    cy.get('input[name="firstName"]').clear().type('Updated')
    cy.get('button').contains('Next').click()
    
    // Should have updated value
    cy.get('input[name="firstName"]').should('have.value', 'Updated')
  })
}) 