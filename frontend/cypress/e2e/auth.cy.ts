/// <reference types="cypress" />

describe('Authentication', () => {
  beforeEach(() => {
    cy.visit('/auth/login');
  });

  it('should display login form', () => {
    cy.get('form').should('exist');
    cy.get('input[type="email"]').should('exist');
    cy.get('input[type="password"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
  });

  it('should show validation errors for invalid email', () => {
    cy.get('input[type="email"]').type('invalid-email');
    cy.get('button[type="submit"]').click();
    cy.get('[data-testid="email-error"]').should('be.visible');
  });

  it('should show validation errors for empty password', () => {
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('button[type="submit"]').click();
    cy.get('[data-testid="password-error"]').should('be.visible');
  });

  it('should navigate to register page', () => {
    cy.get('a[href="/auth/register"]').click();
    cy.url().should('include', '/auth/register');
  });

  it('should show error message for invalid credentials', () => {
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    cy.get('[data-testid="auth-error"]').should('be.visible');
  });

  it('should successfully login with valid credentials', () => {
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('validpassword');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
}); 