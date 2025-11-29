// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Mobile viewport helpers and UX standards commands
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Set mobile viewport from configured devices
       * @example cy.setMobileViewport('iphone-12')
       */
      setMobileViewport(device: string): Chainable<void>
      
      /**
       * Check if element has minimum touch target size (44x44px WCAG AAA)
       * @example cy.get('[data-testid="button"]').hasMinimumTouchTarget()
       */
      hasMinimumTouchTarget(): Chainable<void>
      
      /**
       * Check touch target (alias for hasMinimumTouchTarget)
       * @example cy.get('button').checkTouchTarget()
       */
      checkTouchTarget(): Chainable<void>
      
      /**
       * Check for horizontal scroll (should not exist)
       * @example cy.checkNoHorizontalScroll()
       */
      checkNoHorizontalScroll(): Chainable<void>
      
      /**
       * Should not scroll horizontally (alias)
       * @example cy.shouldNotScrollHorizontally()
       */
      shouldNotScrollHorizontally(): Chainable<void>
      
      /**
       * Check if text is readable (minimum 16px font size to prevent iOS zoom)
       * @example cy.get('input').hasReadableText()
       */
      hasReadableText(): Chainable<void>
      
      /**
       * Check mobile font size (alias for hasReadableText)
       * @example cy.get('input').checkMobileFontSize()
       */
      checkMobileFontSize(): Chainable<void>
      
      /**
       * Test mobile navigation menu
       * @example cy.testMobileNav()
       */
      testMobileNav(): Chainable<void>
    }
  }
}

// Hide fetch/XHR requests from command log
const app = window.top;
if (!app.document.head.querySelector('[data-hide-command-log-request]')) {
  const style = app.document.createElement('style');
  style.innerHTML =
    '.command-name-request, .command-name-xhr { display: none }';
  style.setAttribute('data-hide-command-log-request', '');
  app.document.head.appendChild(style);
}
