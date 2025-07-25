import React from 'react';
import { mount } from 'cypress/react18';
import ThemeToggle from '../../src/components/ThemeToggle';

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    // Mock localStorage
    cy.stub(localStorage, 'getItem').returns('light');
    cy.stub(localStorage, 'setItem');
  });

  it('renders the theme toggle button', () => {
    mount(<ThemeToggle />);
    cy.get('[data-testid="theme-toggle"]').should('exist');
  });

  it('displays the correct icon based on theme', () => {
    mount(<ThemeToggle />);
    cy.get('[data-testid="theme-toggle"]').should('have.attr', 'aria-label', 'Switch to dark theme');
  });

  it('toggles theme when clicked', () => {
    mount(<ThemeToggle />);
    cy.get('[data-testid="theme-toggle"]').click();
    cy.get('[data-testid="theme-toggle"]').should('have.attr', 'aria-label', 'Switch to light theme');
  });

  it('updates localStorage when theme is toggled', () => {
    mount(<ThemeToggle />);
    cy.get('[data-testid="theme-toggle"]').click();
    cy.wrap(localStorage.setItem).should('be.calledWith', 'theme', 'dark');
  });

  it('applies the correct theme class to document', () => {
    mount(<ThemeToggle />);
    cy.get('[data-testid="theme-toggle"]').click();
    cy.document().its('documentElement').should('have.class', 'dark');
  });
}); 