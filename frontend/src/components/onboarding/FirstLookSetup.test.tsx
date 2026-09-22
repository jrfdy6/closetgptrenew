import { fireEvent, render, screen } from '@testing-library/react';
import FirstLookSetup from './FirstLookSetup';
import type { OnboardingState } from '@/lib/onboarding/types';
declare const expect: jest.Expect;
declare const it: jest.It;

const ready: OnboardingState = {
  schemaVersion: 1, revision: 4, draft: { answers: [], currentQuestionId: null }, profileComplete: true,
  capsule: { minimum: 10, savedCount: 10, usableCount: 10, hasCoverage: true, missingCategories: [], ready: true },
  stage: 'first-look', milestones: { styleCompletedAt: 'saved', capsuleCompletedAt: 'saved', firstOutfitId: null },
};
const mockProgress = { state: ready as OnboardingState | null, loading: false, error: null as string | null, refresh: jest.fn() };
jest.mock('@/lib/hooks/useOnboardingState', () => ({ useOnboardingState: () => mockProgress }));
const options = { occasions: ['Casual'], styles: ['Minimalist'], moods: ['Relaxed'] };

beforeEach(() => {
  mockProgress.state = ready;
  mockProgress.loading = false;
  mockProgress.error = null;
  mockProgress.refresh.mockClear();
});

it('reveals the configuration after persisted readiness without automatically generating', () => {
  const onGenerate = jest.fn();
  const onShuffle = jest.fn();
  render(<FirstLookSetup onGenerate={onGenerate} onShuffle={onShuffle} {...options} />);
  expect(screen.getByRole('region', { name: 'First outfit configuration' })).toBeVisible();
  expect(onGenerate).not.toHaveBeenCalled();
  expect(onShuffle).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Casual' }));
  fireEvent.click(screen.getByRole('button', { name: 'Minimalist' }));
  fireEvent.click(screen.getByRole('button', { name: 'Relaxed' }));
  fireEvent.click(screen.getByRole('button', { name: 'Create my first outfit' }));
  expect(onGenerate).toHaveBeenCalledWith({ occasion: 'Casual', style: 'Minimalist', mood: 'Relaxed' });
});

it('does not treat a failed progress read as an empty capsule', () => {
  mockProgress.state = null;
  mockProgress.error = 'Saved progress could not be loaded.';
  render(<FirstLookSetup onGenerate={jest.fn()} onShuffle={jest.fn()} {...options} />);
  expect(screen.getByRole('alert')).toHaveTextContent('Saved progress could not be loaded.');
  expect(screen.queryByText(/needs a few essentials/)).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Create my first outfit' })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Retry saved progress' }));
  expect(mockProgress.refresh).toHaveBeenCalledTimes(1);
});

it('requires both the completed full profile and currently ready capsule on direct entry', () => {
  mockProgress.state = { ...ready, profileComplete: false, stage: 'style' };
  const { rerender } = render(<FirstLookSetup onGenerate={jest.fn()} onShuffle={jest.fn()} {...options} />);
  expect(screen.getByRole('link', { name: 'Continue my style profile' })).toHaveAttribute('href', '/onboarding');
  expect(screen.queryByRole('region', { name: 'First outfit configuration' })).not.toBeInTheDocument();
  mockProgress.state = { ...ready, capsule: { ...ready.capsule, ready: false, hasCoverage: false, missingCategories: ['shoes'] } };
  rerender(<FirstLookSetup onGenerate={jest.fn()} onShuffle={jest.fn()} {...options} />);
  expect(screen.getByRole('link', { name: 'Continue my capsule' })).toHaveAttribute('href', '/onboarding');
});
