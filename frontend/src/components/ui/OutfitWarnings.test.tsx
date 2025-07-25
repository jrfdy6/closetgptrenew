import React from 'react';
import { render, screen } from '@testing-library/react';
import { OutfitWarnings } from './OutfitWarnings';

describe('OutfitWarnings', () => {
  it('should handle string warnings correctly', () => {
    render(
      <OutfitWarnings
        warnings={['This is a string warning']}
        validationErrors={[]}
      />
    );
    
    expect(screen.getByText('This is a string warning')).toBeInTheDocument();
  });

  it('should handle object warnings correctly', () => {
    render(
      <OutfitWarnings
        warnings={[{ step: 'validation', message: 'Object warning' }]}
        validationErrors={[]}
      />
    );
    
    expect(screen.getByText(/validation: Object warning/)).toBeInTheDocument();
  });

  it('should handle mixed string and object warnings', () => {
    render(
      <OutfitWarnings
        warnings={['String warning', { step: 'test', message: 'Object warning' }]}
        validationErrors={[]}
      />
    );
    
    expect(screen.getByText('String warning')).toBeInTheDocument();
    expect(screen.getByText(/test: Object warning/)).toBeInTheDocument();
  });

  it('should handle validation errors with objects', () => {
    render(
      <OutfitWarnings
        warnings={[]}
        validationErrors={[{ errors: ['Error 1'], step: 'test' }]}
      />
    );
    
    expect(screen.getByText(/test:.*Error 1/)).toBeInTheDocument();
  });

  it('should not render when no warnings or errors', () => {
    const { container } = render(
      <OutfitWarnings
        warnings={[]}
        validationErrors={[]}
      />
    );
    
    expect(container.firstChild).toBeNull();
  });
}); 