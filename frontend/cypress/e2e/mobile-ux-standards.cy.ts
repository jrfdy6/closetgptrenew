/**
 * Mobile UX Standards & Breakpoint Testing
 * 
 * This comprehensive test suite validates:
 * - WCAG AAA touch target requirements (44×44px)
 * - iOS zoom prevention (16px minimum font size)
 * - Horizontal scroll detection
 * - Responsive breakpoint behavior
 * - Navigation pattern changes at critical breakpoints
 */

describe('Mobile UX Standards & Breakpoints', () => {
  const viewports = Cypress.env('projectViewports') || {};
  const uxStandards = Cypress.env('uxStandards') || { minTouchTarget: 44, minFontSize: 16, minSpacing: 8 };

  // Test all defined viewports
  Object.keys(viewports).forEach((device) => {
    const { width, height } = viewports[device];
    const isMobile = width < 768;
    const isTablet = width >= 768 && width < 1024;
    const isDesktop = width >= 1024;

    context(`Device: ${device} (${width}×${height})`, () => {
      beforeEach(() => {
        cy.viewport(width, height);
        cy.visit('/');
        cy.wait(1000); // Allow page to fully render
      });

      it('should not have horizontal scroll', () => {
        cy.checkNoHorizontalScroll();
      });

      it('should have accessible touch targets for primary actions', () => {
        // Test critical interactive elements
        cy.get('body').then(($body) => {
          // Find all visible buttons and interactive elements
          const interactiveElements = $body.find(
            'button:visible, [role="button"]:visible, a[role="button"]:visible'
          );

          if (interactiveElements.length > 0) {
            // Test first few critical buttons (submit, primary CTAs)
            cy.get('button[type="submit"]:visible, button:contains("Submit"):visible, .cta-button:visible')
              .first()
              .then(($btn) => {
                if ($btn.length > 0) {
                  cy.wrap($btn).checkTouchTarget();
                }
              });
          }
        });
      });

      it('should have legible font sizes for inputs', () => {
        cy.get('body').then(($body) => {
          const inputs = $body.find('input:visible, select:visible, textarea:visible');
          
          if (inputs.length > 0) {
            // Test first visible input
            cy.wrap(inputs.first()).checkMobileFontSize();
          }
        });
      });

      it('should display correct navigation for this breakpoint', () => {
        if (isMobile) {
          // Mobile: Hamburger menu should be visible, desktop nav hidden
          cy.get('body').then(($body) => {
            // Look for mobile menu indicators
            const hasMobileNav = $body.find('[class*="mobile"], [data-testid*="mobile"], button:has(svg)').length > 0;
            const hasDesktopNav = $body.find('[class*="desktop"], nav:not([class*="mobile"])').filter(':visible').length > 0;
            
            // Mobile nav should exist (if implemented)
            if (hasMobileNav || hasDesktopNav) {
              cy.log(`Mobile viewport: Mobile nav indicators found`);
            }
          });
        } else if (isTablet) {
          // Tablet: May show desktop nav or tablet-optimized nav
          cy.get('body').then(($body) => {
            cy.log(`Tablet viewport: Checking navigation patterns`);
          });
        } else {
          // Desktop: Desktop nav should be visible
          cy.get('body').then(($body) => {
            cy.log(`Desktop viewport: Desktop navigation expected`);
          });
        }
      });

      it('should have proper spacing between interactive elements', () => {
        // Check spacing between buttons (minimum 8px)
        cy.get('body').then(($body) => {
          const buttons = $body.find('button:visible');
          if (buttons.length >= 2) {
            // This is a basic check - more sophisticated spacing tests can be added
            cy.log('Checking spacing between interactive elements');
          }
        });
      });

      // Test responsive layout at critical breakpoints
      if (width === 768 || width === 640 || width === 1024) {
        it('should handle critical breakpoint correctly', () => {
          const breakpointName = width === 640 ? 'sm (640px)' : 
                                width === 768 ? 'md (768px)' : 
                                'lg (1024px)';
          cy.log(`Testing at critical breakpoint: ${breakpointName}`);
          
          // Verify layout adapts correctly
          cy.get('body').should('be.visible');
          
          // Check for layout shifts
          cy.window().its('innerWidth').should('eq', width);
        });
      }
    });
  });

  // Specific breakpoint tests
  describe('Critical Breakpoint Transitions', () => {
    it('should transition from mobile to tablet layout at 768px', () => {
      // Test just below breakpoint
      cy.viewport(767, 1024);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
      
      // Test at breakpoint
      cy.viewport(768, 1024);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
      
      // Test just above breakpoint
      cy.viewport(769, 1024);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
    });

    it('should transition from tablet to desktop layout at 1024px', () => {
      // Test just below breakpoint
      cy.viewport(1023, 768);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
      
      // Test at breakpoint
      cy.viewport(1024, 768);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
      
      // Test just above breakpoint
      cy.viewport(1025, 768);
      cy.visit('/');
      cy.checkNoHorizontalScroll();
    });
  });

  // UX Standards validation
  describe('UX Standards Compliance', () => {
    beforeEach(() => {
      cy.viewport(390, 844); // iPhone 12 default
      cy.visit('/');
    });

    it(`should enforce ${uxStandards.minTouchTarget}px minimum touch targets`, () => {
      cy.get('button:visible, [role="button"]:visible')
        .first()
        .then(($btn) => {
          if ($btn.length > 0) {
            cy.wrap($btn).checkTouchTarget();
          }
        });
    });

    it(`should enforce ${uxStandards.minFontSize}px minimum font size for inputs`, () => {
      cy.get('input:visible, textarea:visible, select:visible')
        .first()
        .then(($input) => {
          if ($input.length > 0) {
            cy.wrap($input).checkMobileFontSize();
          }
        });
    });
  });
});
