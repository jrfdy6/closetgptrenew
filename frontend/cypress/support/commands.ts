/// <reference types="cypress" />

/**
 * Set mobile viewport for testing
 * Uses viewports from Cypress env config
 */
Cypress.Commands.add('setMobileViewport', (device: string) => {
  const viewports = Cypress.env('projectViewports') || {};
  const viewport = viewports[device];
  if (!viewport) {
    throw new Error(`Unknown device: ${device}. Available devices: ${Object.keys(viewports).join(', ')}`);
  }
  cy.viewport(viewport.width, viewport.height);
});

/**
 * Check if element meets minimum touch target size (WCAG AAA - 44x44px)
 * Uses UX standards from config (default 44px)
 */
Cypress.Commands.add('hasMinimumTouchTarget', { prevSubject: 'element' }, (subject) => {
  const minSize = Cypress.env('uxStandards')?.minTouchTarget || 44;
  
  cy.wrap(subject).then(($el) => {
    // Skip hidden elements
    if (!$el.is(':visible')) {
      cy.log('Element is hidden, skipping touch target check');
      return;
    }
    
    const width = $el.outerWidth() || 0;
    const height = $el.outerHeight() || 0;
    
    expect(width, `Element width should be at least ${minSize}px for accessibility`).to.be.at.least(minSize);
    expect(height, `Element height should be at least ${minSize}px for accessibility`).to.be.at.least(minSize);
  });
});

/**
 * Check touch target (alternative name for consistency)
 */
Cypress.Commands.add('checkTouchTarget', { prevSubject: 'element' }, (subject) => {
  cy.wrap(subject).hasMinimumTouchTarget();
});

/**
 * Check for horizontal scroll (should not exist)
 * Validates no horizontal scrolling on mobile
 */
Cypress.Commands.add('checkNoHorizontalScroll', () => {
  cy.window().then((win) => {
    const scrollWidth = win.document.documentElement.scrollWidth;
    const clientWidth = win.document.documentElement.clientWidth;
    
    if (scrollWidth > clientWidth) {
      cy.log('⚠️ Horizontal scroll detected!');
      cy.log(`ScrollWidth: ${scrollWidth}, ClientWidth: ${clientWidth}`);
      cy.log(`Difference: ${scrollWidth - clientWidth}px`);
    }
    
    expect(scrollWidth, 'Page content should not exceed viewport width (no horizontal scroll)').to.be.lte(clientWidth);
  });
});

/**
 * Should not scroll horizontally (alternative name)
 */
Cypress.Commands.add('shouldNotScrollHorizontally', () => {
  cy.checkNoHorizontalScroll();
});

/**
 * Check if text input has readable font size (minimum 16px to prevent iOS zoom)
 * Uses UX standards from config (default 16px)
 */
Cypress.Commands.add('hasReadableText', { prevSubject: 'element' }, (subject) => {
  const minSize = Cypress.env('uxStandards')?.minFontSize || 16;
  
  cy.wrap(subject).then(($el) => {
    const fontSize = parseFloat($el.css('font-size'));
    expect(fontSize, `Font size should be at least ${minSize}px to prevent zoom on mobile`).to.be.at.least(minSize);
  });
});

/**
 * Check mobile font size (alternative name for consistency)
 */
Cypress.Commands.add('checkMobileFontSize', { prevSubject: 'element' }, (subject) => {
  cy.wrap(subject).hasReadableText();
});

/**
 * Test mobile navigation menu functionality
 */
Cypress.Commands.add('testMobileNav', () => {
  // Look for mobile menu button (hamburger icon)
  cy.get('body').then(($body) => {
    // Check if mobile menu exists (should be visible on mobile)
    const menuButton = $body.find('button[aria-label*="menu" i], button:contains("Menu"), [data-testid*="menu"]').first();
    
    if (menuButton.length > 0) {
      // Open menu
      cy.wrap(menuButton).should('be.visible').click();
      
      // Wait for menu to open
      cy.wait(300);
      
      // Check if menu overlay is visible
      cy.get('body').should('have.class', 'menu-open').or(($body) => {
        // Alternative: check for menu overlay or navigation panel
        const menuOverlay = $body.find('[role="menu"], [aria-label*="navigation"], nav').first();
        expect(menuOverlay.length).to.be.greaterThan(0);
      });
      
      // Close menu (click overlay or close button)
      cy.get('body').click(0, 0); // Click outside
      cy.wait(300);
    }
  });
});
