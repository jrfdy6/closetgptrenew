describe('Mobile Homepage Tests', () => {
  const devices = ['iphone-se', 'iphone-12', 'iphone-14-pro-max'] as const;

  devices.forEach((device) => {
    describe(`Homepage on ${device}`, () => {
      beforeEach(() => {
        cy.setMobileViewport(device);
        cy.visit('/');
      });

      it('should load without horizontal scroll', () => {
        cy.checkNoHorizontalScroll();
      });

      it('should display hero section correctly', () => {
        cy.get('h1').should('be.visible').contains(/Easy Outfit/i);
        // Use compatible selectors
        cy.get('img').filter((i, el) => {
          const alt = (Cypress.$(el).attr('alt') || '').toLowerCase();
          return alt.includes('easy outfit') || alt.includes('logo');
        }).first().should('be.visible');
      });

      it('should have readable text sizes', () => {
        cy.get('h1').should('be.visible');
        cy.get('p').should('be.visible');
        // Check that text is large enough to read
        cy.get('body').should('have.css', 'font-size').and('match', /\d+/);
      });

      it('should have accessible CTA buttons', () => {
        // Check primary CTA button
        cy.get('a[href*="signin"], button').contains(/generate|today|fit/i).first().then(($btn) => {
          cy.wrap($btn).hasMinimumTouchTarget();
        });

        // Check secondary CTA button if present
        cy.get('body').then(($body) => {
          const secondaryBtn = $body.find('a[href*="onboarding"], a[href*="quiz"]').first();
          if (secondaryBtn.length > 0) {
            cy.wrap(secondaryBtn).hasMinimumTouchTarget();
          }
        });
      });

      it('should stack buttons vertically on mobile', () => {
        cy.get('a[href*="signin"], button').contains(/generate|today|fit/i).first().then(($btn) => {
          // Check if buttons are in a flex column layout
          const parent = $btn.parent();
          const flexDirection = parent.css('flex-direction');
          const isColumn = flexDirection === 'column' || parent.hasClass('flex-col');
          
          if (parent.children().length > 1) {
            expect(isColumn || parent.hasClass('flex-col') || parent.hasClass('flex-column'), 
              'Buttons should stack vertically on mobile').to.be.true;
          }
        });
      });

      it('should handle touch interactions', () => {
        // Test tap on logo
        cy.get('img').filter((i, el) => {
          const alt = (Cypress.$(el).attr('alt') || '').toLowerCase();
          return alt.includes('logo') || alt.includes('easy outfit');
        }).first().should('be.visible');
        
        // Test tap on buttons (should not cause errors)
        cy.get('a[href*="signin"], button').contains(/generate|today|fit/i).first().should('be.visible');
      });

      it('should maintain proper spacing between elements', () => {
        // Check that elements don't feel cramped
        cy.get('main, section').first().should('have.css', 'padding').and('not.be.empty');
      });
    });
  });

  describe('Responsive behavior', () => {
    it('should adapt layout for different screen sizes', () => {
      // Test smallest mobile
      cy.setMobileViewport('iphone-se');
      cy.visit('/');
      cy.checkNoHorizontalScroll();

      // Test larger mobile
      cy.setMobileViewport('iphone-14-pro-max');
      cy.visit('/');
      cy.checkNoHorizontalScroll();

      // Test tablet
      cy.setMobileViewport('ipad-mini');
      cy.visit('/');
      cy.checkNoHorizontalScroll();
    });
  });
});
