/// <reference types="cypress" />

describe('ClosetGPT Production Testing Suite', () => {
  beforeEach(() => {
    // Clear any existing data and start fresh
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('http://localhost:3000')
  })

  describe('1. Core Functionality & End-to-End Testing', () => {
    it('should complete user onboarding flow', () => {
      // Test registration/login
      cy.get('[data-testid="signup-button"]').click()
      cy.get('[data-testid="email-input"]').type('test@example.com')
      cy.get('[data-testid="password-input"]').type('securePassword123')
      cy.get('[data-testid="signup-submit"]').click()
      
      // Should redirect to onboarding
      cy.url().should('include', '/onboarding')
      
      // Complete style quiz
      cy.get('[data-testid="style-quiz-start"]').click()
      cy.get('[data-testid="style-preference-minimalist"]').click()
      cy.get('[data-testid="body-type-rectangle"]').click()
      cy.get('[data-testid="color-preference-neutral"]').click()
      cy.get('[data-testid="budget-mid-range"]').click()
      cy.get('[data-testid="quiz-submit"]').click()
      
      // Should complete onboarding
      cy.url().should('include', '/dashboard')
      cy.get('[data-testid="onboarding-complete"]').should('be.visible')
    })

    it('should handle wardrobe item upload and management', () => {
      // Login first
      cy.login('test@example.com', 'securePassword123')
      
      // Navigate to wardrobe
      cy.visit('/wardrobe/add')
      
      // Upload test image
      cy.fixture('test-shirt.jpg').then((fileContent) => {
        cy.get('[data-testid="file-upload"]').attachFile({
          fileContent,
          fileName: 'test-shirt.jpg',
          mimeType: 'image/jpeg'
        })
      })
      
      // Wait for AI analysis
      cy.get('[data-testid="analysis-loading"]').should('be.visible')
      cy.get('[data-testid="analysis-complete"]', { timeout: 30000 }).should('be.visible')
      
      // Verify analysis results
      cy.get('[data-testid="item-type"]').should('contain', 'shirt')
      cy.get('[data-testid="item-color"]').should('be.visible')
      cy.get('[data-testid="item-style"]').should('be.visible')
      
      // Save item
      cy.get('[data-testid="save-item"]').click()
      cy.get('[data-testid="save-success"]').should('be.visible')
      
      // Verify item appears in wardrobe
      cy.visit('/wardrobe')
      cy.get('[data-testid="wardrobe-item"]').should('have.length.at.least', 1)
    })

    it('should generate outfits successfully', () => {
      // Login and ensure wardrobe has items
      cy.login('test@example.com', 'securePassword123')
      cy.visit('/wardrobe')
      
      // Navigate to outfit generation
      cy.visit('/outfits/generate')
      
      // Set generation parameters
      cy.get('[data-testid="occasion-select"]').click()
      cy.get('[data-testid="occasion-casual"]').click()
      
      cy.get('[data-testid="weather-input"]').type('72')
      cy.get('[data-testid="weather-condition-sunny"]').click()
      
      // Generate outfit
      cy.get('[data-testid="generate-outfit"]').click()
      
      // Wait for generation
      cy.get('[data-testid="generation-loading"]').should('be.visible')
      cy.get('[data-testid="outfit-result"]', { timeout: 30000 }).should('be.visible')
      
      // Verify outfit components
      cy.get('[data-testid="outfit-top"]').should('be.visible')
      cy.get('[data-testid="outfit-bottom"]').should('be.visible')
      cy.get('[data-testid="outfit-shoes"]').should('be.visible')
      
      // Rate outfit
      cy.get('[data-testid="outfit-rating-5"]').click()
      cy.get('[data-testid="rating-submitted"]').should('be.visible')
    })

    it('should handle empty wardrobe gracefully', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Clear wardrobe (if possible)
      cy.visit('/wardrobe')
      cy.get('[data-testid="clear-wardrobe"]').click({ force: true })
      
      // Try to generate outfit with empty wardrobe
      cy.visit('/outfits/generate')
      cy.get('[data-testid="generate-outfit"]').click()
      
      // Should show empty state
      cy.get('[data-testid="empty-wardrobe-message"]').should('be.visible')
      cy.get('[data-testid="add-first-item"]').should('be.visible')
      cy.get('[data-testid="shopping-suggestions"]').should('be.visible')
    })
  })

  describe('2. UI Dead End Prevention', () => {
    it('should handle all button interactions properly', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Test all navigation buttons
      const navButtons = [
        '[data-testid="nav-dashboard"]',
        '[data-testid="nav-wardrobe"]',
        '[data-testid="nav-outfits"]',
        '[data-testid="nav-profile"]'
      ]
      
      navButtons.forEach(button => {
        cy.get(button).should('be.visible').and('not.be.disabled')
        cy.get(button).click()
        cy.url().should('not.include', 'undefined')
        cy.get('[data-testid="page-content"]').should('be.visible')
      })
    })

    it('should handle modal interactions correctly', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Test upload modal
      cy.visit('/wardrobe')
      cy.get('[data-testid="add-item-button"]').click()
      cy.get('[data-testid="upload-modal"]').should('be.visible')
      
      // Test modal close via X button
      cy.get('[data-testid="modal-close"]').click()
      cy.get('[data-testid="upload-modal"]').should('not.be.visible')
      
      // Test modal close via backdrop
      cy.get('[data-testid="add-item-button"]').click()
      cy.get('[data-testid="modal-backdrop"]').click({ force: true })
      cy.get('[data-testid="upload-modal"]').should('not.be.visible')
      
      // Test modal close via escape key
      cy.get('[data-testid="add-item-button"]').click()
      cy.get('body').type('{esc}')
      cy.get('[data-testid="upload-modal"]').should('not.be.visible')
    })

    it('should validate forms properly', () => {
      cy.visit('/signup')
      
      // Test invalid email
      cy.get('[data-testid="email-input"]').type('invalid-email')
      cy.get('[data-testid="password-input"]').type('123')
      cy.get('[data-testid="signup-submit"]').click()
      
      cy.get('[data-testid="email-error"]').should('be.visible')
      cy.get('[data-testid="password-error"]').should('be.visible')
      
      // Test valid form
      cy.get('[data-testid="email-input"]').clear().type('valid@example.com')
      cy.get('[data-testid="password-input"]').clear().type('securePassword123')
      cy.get('[data-testid="signup-submit"]').click()
      
      cy.get('[data-testid="email-error"]').should('not.exist')
      cy.get('[data-testid="password-error"]').should('not.exist')
    })
  })

  describe('3. State Management & Data Persistence', () => {
    it('should preserve wardrobe data across sessions', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Add test item
      cy.visit('/wardrobe/add')
      cy.fixture('test-shirt.jpg').then((fileContent) => {
        cy.get('[data-testid="file-upload"]').attachFile({
          fileContent,
          fileName: 'test-shirt.jpg',
          mimeType: 'image/jpeg'
        })
      })
      
      cy.get('[data-testid="save-item"]').click()
      cy.get('[data-testid="save-success"]').should('be.visible')
      
      // Reload page
      cy.reload()
      
      // Verify item still exists
      cy.visit('/wardrobe')
      cy.get('[data-testid="wardrobe-item"]').should('have.length.at.least', 1)
    })

    it('should preserve user preferences', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Set preferences
      cy.visit('/profile')
      cy.get('[data-testid="style-preferences"]').click()
      cy.get('[data-testid="preference-minimalist"]').click()
      cy.get('[data-testid="save-preferences"]').click()
      
      // Reload page
      cy.reload()
      
      // Verify preferences persist
      cy.get('[data-testid="preference-minimalist"]').should('have.class', 'selected')
    })

    it('should handle form data persistence during navigation', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Start filling form
      cy.visit('/wardrobe/add')
      cy.get('[data-testid="item-name"]').type('Test Item')
      cy.get('[data-testid="item-type"]').select('shirt')
      
      // Navigate away and back
      cy.visit('/dashboard')
      cy.visit('/wardrobe/add')
      
      // Verify form data is preserved
      cy.get('[data-testid="item-name"]').should('have.value', 'Test Item')
      cy.get('[data-testid="item-type"]').should('have.value', 'shirt')
    })
  })

  describe('4. Error Handling & Edge Cases', () => {
    it('should handle API failures gracefully', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Mock API failure
      cy.intercept('POST', '/api/outfit/generate', {
        statusCode: 500,
        body: { error: 'Internal server error' }
      }).as('generateOutfit')
      
      cy.visit('/outfits/generate')
      cy.get('[data-testid="generate-outfit"]').click()
      
      cy.wait('@generateOutfit')
      cy.get('[data-testid="error-message"]').should('be.visible')
      cy.get('[data-testid="retry-button"]').should('be.visible')
    })

    it('should handle network timeouts', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Mock slow API
      cy.intercept('POST', '/api/wardrobe/upload', {
        delay: 10000,
        statusCode: 200
      }).as('uploadItem')
      
      cy.visit('/wardrobe/add')
      cy.fixture('test-shirt.jpg').then((fileContent) => {
        cy.get('[data-testid="file-upload"]').attachFile({
          fileContent,
          fileName: 'test-shirt.jpg',
          mimeType: 'image/jpeg'
        })
      })
      
      // Should show timeout after 5 seconds
      cy.get('[data-testid="timeout-message"]', { timeout: 6000 }).should('be.visible')
    })

    it('should handle invalid file uploads', () => {
      cy.login('test@example.com', 'securePassword123')
      
      cy.visit('/wardrobe/add')
      
      // Upload invalid file
      cy.fixture('test.txt').then((fileContent) => {
        cy.get('[data-testid="file-upload"]').attachFile({
          fileContent,
          fileName: 'test.txt',
          mimeType: 'text/plain'
        })
      })
      
      cy.get('[data-testid="file-error"]').should('be.visible')
      cy.get('[data-testid="file-error"]').should('contain', 'Invalid file type')
    })

    it('should handle large wardrobe performance', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Add multiple items quickly
      cy.visit('/wardrobe/add')
      
      for (let i = 0; i < 5; i++) {
        cy.fixture('test-shirt.jpg').then((fileContent) => {
          cy.get('[data-testid="file-upload"]').attachFile({
            fileContent,
            fileName: `test-shirt-${i}.jpg`,
            mimeType: 'image/jpeg'
          })
        })
        cy.get('[data-testid="save-item"]').click()
        cy.get('[data-testid="save-success"]').should('be.visible')
      }
      
      // Test search performance
      cy.visit('/wardrobe')
      const startTime = Date.now()
      cy.get('[data-testid="search-input"]').type('shirt')
      cy.get('[data-testid="search-results"]').should('be.visible')
      const endTime = Date.now()
      
      // Should complete within 2 seconds
      expect(endTime - startTime).to.be.lessThan(2000)
    })
  })

  describe('5. Accessibility & Responsive Design', () => {
    it('should be keyboard navigable', () => {
      cy.visit('/')
      
      // Test tab navigation
      cy.get('body').tab()
      cy.focused().should('be.visible')
      
      // Test enter key
      cy.focused().type('{enter}')
      cy.url().should('not.eq', 'http://localhost:3000/')
    })

    it('should be responsive on different screen sizes', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Test mobile view
      cy.viewport('iphone-x')
      cy.visit('/dashboard')
      cy.get('[data-testid="mobile-menu"]').should('be.visible')
      
      // Test tablet view
      cy.viewport('ipad-2')
      cy.get('[data-testid="tablet-layout"]').should('be.visible')
      
      // Test desktop view
      cy.viewport(1920, 1080)
      cy.get('[data-testid="desktop-layout"]').should('be.visible')
    })
  })

  describe('6. Security & Authentication', () => {
    it('should protect private routes', () => {
      // Try to access private route without login
      cy.visit('/wardrobe')
      cy.url().should('include', '/login')
    })

    it('should handle authentication errors', () => {
      cy.visit('/login')
      cy.get('[data-testid="email-input"]').type('invalid@example.com')
      cy.get('[data-testid="password-input"]').type('wrongpassword')
      cy.get('[data-testid="login-submit"]').click()
      
      cy.get('[data-testid="auth-error"]').should('be.visible')
    })

    it('should handle session expiration', () => {
      cy.login('test@example.com', 'securePassword123')
      
      // Mock session expiration
      cy.clearLocalStorage()
      cy.visit('/wardrobe')
      
      cy.url().should('include', '/login')
    })
  })
}) 