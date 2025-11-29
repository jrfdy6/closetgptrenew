import { defineConfig } from 'cypress';

// Mobile-first viewport configurations aligned with app breakpoints
const projectViewports = {
  // Mobile devices (< 640px) - Critical for mobile-first design
  'mobile-xs': { width: 360, height: 640 },      // Minimum supported width
  'iphone-se': { width: 375, height: 667 },      // Small mobile (sm breakpoint boundary)
  'iphone-12': { width: 390, height: 844 },      // Most common mobile (default)
  'iphone-14-pro-max': { width: 430, height: 932 }, // Large mobile
  'galaxy-s20': { width: 360, height: 800 },     // Android small
  'pixel-5': { width: 393, height: 851 },        // Android medium
  
  // Tablet devices (768px+) - Critical md breakpoint
  'ipad-mini': { width: 768, height: 1024 },     // ⚠️ Critical md breakpoint!
  'ipad-air': { width: 820, height: 1180 },      // Larger tablet
  
  // Desktop (for comparison)
  'desktop-sm': { width: 1024, height: 768 },    // lg breakpoint
  'desktop-standard': { width: 1280, height: 720 }, // Standard desktop
};

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: false,
    screenshotOnRunFailure: true,
    
    // Mobile-first default viewport (iPhone 12 - most common device)
    viewportWidth: 390,
    viewportHeight: 844,
    
    // Timeouts for mobile network conditions
    defaultCommandTimeout: 4000,
    pageLoadTimeout: 30000,
    requestTimeout: 5000,
    
    retries: {
      runMode: 2,
      openMode: 0,
    },
    setupNodeEvents(on, config) {
      // implement node event listeners here
      return config;
    },
    env: {
      projectViewports,
      // UX standards for validation
      uxStandards: {
        minTouchTarget: 44,  // WCAG AAA requirement
        minFontSize: 16,     // iOS zoom prevention
        minSpacing: 8,       // Minimum spacing between touch targets
      },
    },
  },
  component: {
    devServer: {
      framework: 'next',
      bundler: 'webpack',
    },
    supportFile: 'cypress/support/component.ts',
    specPattern: 'cypress/component/**/*.cy.{js,jsx,ts,tsx}',
  },
}); 