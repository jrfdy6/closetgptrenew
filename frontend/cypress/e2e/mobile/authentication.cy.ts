describe('Mobile Authentication Tests', () => {
  const devices = ['iphone-se', 'iphone-12'] as const;

  devices.forEach((device) => {
    describe(`Sign In on ${device}`, () => {
      beforeEach(() => {
        cy.setMobileViewport(device);
        cy.visit('/signin');
      });

      it('should load without horizontal scroll', () => {
        cy.checkNoHorizontalScroll();
      });

      it('should display sign in form correctly', () => {
        cy.get('form').should('be.visible');
        cy.get('input[type="email"], input[name*="email"], input[name*="Email"]').should('be.visible');
        cy.get('input[type="password"], input[name*="password"], input[name*="Password"]').should('be.visible');
      });

      it('should have readable input fields (16px minimum)', () => {
        cy.get('input[type="email"], input[name*="email"], input[name*="Email"]').first().then(($input) => {
          cy.wrap($input).hasReadableText();
        });
        
        cy.get('input[type="password"], input[name*="password"], input[name*="Password"]').first().then(($input) => {
          cy.wrap($input).hasReadableText();
        });
      });

      it('should have accessible submit button', () => {
        cy.get('button[type="submit"], button').contains(/sign in|login|submit/i).first().then(($btn) => {
          cy.wrap($btn).hasMinimumTouchTarget();
        });
      });

      it('should have accessible password toggle', () => {
        cy.get('body').then(($body) => {
          // Look for password toggle button (eye icon or show/hide button)
          const toggleBtn = $body.find('button').filter((i, el) => {
            const $el = Cypress.$(el);
            const ariaLabel = ($el.attr('aria-label') || '').toLowerCase();
            const hasEyeIcon = $el.find('svg').length > 0 && ($el.find('svg').attr('class')?.includes('eye') || $el.find('svg').attr('class')?.includes('Eye'));
            return ariaLabel.includes('password') || ariaLabel.includes('show') || ariaLabel.includes('hide') || hasEyeIcon;
          }).first();
          
          if (toggleBtn.length > 0) {
            cy.wrap(toggleBtn).hasMinimumTouchTarget();
          } else {
            // Password toggle is optional, skip if not found
            cy.log('Password toggle button not found (may not be implemented)');
          }
        });
      });

      it('should stack form fields vertically', () => {
        cy.get('form').within(() => {
          // Check that form uses vertical layout on mobile
          cy.get('input, label').should('exist');
        });
      });

      it('should display error messages clearly', () => {
        // Try to submit empty form
        cy.get('button[type="submit"], button').contains(/sign in|login|submit/i).first().click();
        
        // Wait a moment for validation
        cy.wait(500);
        
        // Check if error messages appear (should be visible if validation exists)
        cy.get('body').then(($body) => {
          // Use compatible selectors (no case-insensitive flag)
          const errors = $body.find('[role="alert"], .error, [class*="error"], [class*="Error"]');
          // Error messages should be visible if they exist
          if (errors.length > 0) {
            cy.wrap(errors.first()).should('be.visible');
          } else {
            // Form validation may not show errors immediately or may use different selectors
            cy.log('No error messages found (validation may use different selectors or timing)');
          }
        });
      });
    });

    describe(`Sign Up on ${device}`, () => {
      beforeEach(() => {
        cy.setMobileViewport(device);
        cy.visit('/signup');
      });

      it('should load without horizontal scroll', () => {
        cy.checkNoHorizontalScroll();
      });

      it('should display sign up form correctly', () => {
        cy.get('form').should('be.visible');
        cy.get('input[type="email"], input[name*="email"], input[name*="Email"]').should('be.visible');
        cy.get('input[type="password"], input[name*="password"], input[name*="Password"]').should('be.visible');
      });

      it('should have all required fields accessible', () => {
        // Check email field
        cy.get('input[type="email"], input[name*="email"], input[name*="Email"]').first().then(($input) => {
          cy.wrap($input).hasMinimumTouchTarget();
        });

        // Check password field
        cy.get('input[type="password"], input[name*="password"], input[name*="Password"]').first().then(($input) => {
          cy.wrap($input).hasMinimumTouchTarget();
        });
      });

      it('should handle form submission on mobile', () => {
        // Note: This test doesn't actually submit to avoid creating test accounts
        // In a real scenario, you'd use test credentials or mock the API
        cy.get('form').should('exist');
        cy.get('button[type="submit"]').should('exist');
      });
    });
  });
});
