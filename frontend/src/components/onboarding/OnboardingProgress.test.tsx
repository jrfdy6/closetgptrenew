import { render, screen } from '@testing-library/react';
import OnboardingProgress from './OnboardingProgress';
declare const expect: jest.Expect;
declare const it: jest.It;

it('announces the current stage and completed previous steps', () => {
  render(<OnboardingProgress stage="capsule" />);
  const steps = screen.getAllByRole('listitem');
  expect(steps[0]).toHaveTextContent('Your style, complete');
  expect(steps[1]).toHaveAttribute('aria-current', 'step');
  expect(steps[2]).not.toHaveAttribute('aria-current');
  expect(screen.getByRole('navigation', { name: 'Your wardrobe setup' })).toBeVisible();
});
