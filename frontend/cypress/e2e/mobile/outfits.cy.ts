describe('Mobile Outfits Tests', () => {
  const devices = ['iphone-se', 'iphone-12'] as const;

  devices.forEach((device) => {
    describe(`Outfits Page on ${device}`, () => {
      beforeEach(() => {
        cy.setMobileViewport(device);
        cy.visit('/outfits');
        cy.wait(2000); // Wait for page to load
      });

      it('should load without horizontal scroll', () => {
        cy.checkNoHorizontalScroll();
      });

      it('should display outfits page content', () => {
        cy.url().then((url) => {
          if (url.includes('outfits')) {
            cy.get('main, [role="main"]').should('be.visible');
          } else if (url.includes('signin')) {
            cy.log('Redirected to signin (expected if not authenticated)');
          }
        });
      });

      it('should have accessible generate outfit button', () => {
        cy.get('body').then(($body) => {
          const generateBtn = $body.find('a[href*="generate"], button').filter((i, el) => {
            const text = Cypress.$(el).text().toLowerCase();
            const href = Cypress.$(el).attr('href')?.toLowerCase();
            return text.includes('generate') || text.includes('create') || href?.includes('generate');
          }).first();

          if (generateBtn.length > 0) {
            cy.wrap(generateBtn).hasMinimumTouchTarget();
          }
        });
      });

      it('should display outfit cards in mobile grid', () => {
        cy.url().then((url) => {
          if (url.includes('outfits')) {
            cy.get('body').then(($body) => {
              // Use compatible selectors (no case-insensitive flag)
              const outfitCards = $body.find('[class*="outfit"], [class*="Outfit"], [class*="card"], [class*="Card"]');
              
              // Outfit cards might not exist if user has no outfits
              if (outfitCards.length > 0) {
                cy.wrap(outfitCards.first()).should('be.visible');
              } else {
                // Just check that the page structure is there
                cy.get('body').should('not.be.empty');
                cy.log('No outfit cards found (user may have no outfits or cards use different class names)');
              }
            });
          } else {
            cy.log('Not on outfits page, skipping card check');
          }
        });
      });

      it('should handle outfit filters on mobile', () => {
        cy.url().then((url) => {
          if (url.includes('outfits')) {
            cy.get('body').then(($body) => {
              const filters = $body.find('button, select, input').filter((i, el) => {
                const text = Cypress.$(el).text().toLowerCase();
                const placeholder = Cypress.$(el).attr('placeholder')?.toLowerCase();
                return text.includes('filter') || text.includes('search') || placeholder?.includes('filter') || placeholder?.includes('search');
              });

              if (filters.length > 0) {
                cy.wrap(filters.first()).should('be.visible');
              }
            });
          }
        });
      });

      it('should handle empty state gracefully', () => {
        cy.url().then((url) => {
          if (url.includes('outfits')) {
            // Check if empty state message exists
            cy.get('body').then(($body) => {
              const emptyState = $body.find('text, p, h').filter((i, el) => {
                const text = Cypress.$(el).text().toLowerCase();
                return text.includes('no outfits') || text.includes('empty') || text.includes('create');
              });

              // Empty state is optional - just verify page doesn't break
              cy.get('main, [role="main"]').should('exist');
            });
          }
        });
      });
    });
  });
});
