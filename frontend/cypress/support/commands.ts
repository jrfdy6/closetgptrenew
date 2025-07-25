// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

/// <reference types="cypress" />

// Custom command for login
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(email)
  cy.get('[data-testid="password-input"]').type(password)
  cy.get('[data-testid="login-submit"]').click()
  cy.url().should('not.include', '/login')
})

// Custom command for clearing wardrobe
Cypress.Commands.add('clearWardrobe', () => {
  cy.visit('/wardrobe')
  cy.get('[data-testid="clear-wardrobe"]').click({ force: true })
  cy.get('[data-testid="confirm-clear"]').click()
})

// Custom command for adding test item
Cypress.Commands.add('addTestItem', (itemName: string = 'Test Item') => {
  cy.visit('/wardrobe/add')
  cy.get('[data-testid="item-name"]').type(itemName)
  cy.get('[data-testid="item-type"]').select('shirt')
  cy.get('[data-testid="item-color"]').type('blue')
  cy.get('[data-testid="item-style"]').select('casual')
  cy.get('[data-testid="save-item"]').click()
  cy.get('[data-testid="save-success"]').should('be.visible')
})

// Extend Cypress namespace
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      clearWardrobe(): Chainable<void>
      addTestItem(itemName?: string): Chainable<void>
      generateOutfit(occasion?: string, weather?: string, temperature?: number): Chainable<void>
      expectOutfitValidation(shouldHaveErrors?: boolean, shouldHaveWarnings?: boolean): Chainable<void>
      waitForOutfitGeneration(): Chainable<void>
    }
  }
}

// Custom command for generating outfits
Cypress.Commands.add('generateOutfit', (occasion = 'casual', weather = 'clear', temperature = 75) => {
  cy.visit('/outfits')
  cy.get('select[name="occasion"]').select(occasion)
  cy.get('select[name="weather"]').select(weather)
  cy.get('input[name="temperature"]').clear().type(temperature.toString())
  cy.get('button').contains('Generate Outfit').click()
})

// Custom command for expecting outfit validation
Cypress.Commands.add('expectOutfitValidation', (shouldHaveErrors = false, shouldHaveWarnings = false) => {
  if (shouldHaveErrors) {
    cy.get('[data-testid="outfit-error"]').should('exist')
  } else {
    cy.get('[data-testid="outfit-error"]').should('not.exist')
  }
  
  if (shouldHaveWarnings) {
    cy.get('[data-testid="outfit-warning"]').should('exist')
  }
})

// Custom command for waiting for outfit generation
Cypress.Commands.add('waitForOutfitGeneration', () => {
  cy.contains('Generating').should('exist')
  cy.contains('Generated Outfit', { timeout: 30000 }).should('exist')
})

// Prevent TypeScript from reading file as legacy script
export {}; 