import '@testing-library/jest-dom';
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import OutfitsPage from './page';
import type { OnboardingState } from '@/lib/onboarding/types';

const mockRefresh = jest.fn();
let mockProgress: { state: OnboardingState | null; loading: boolean; error: string | null; refresh: typeof mockRefresh };
jest.mock('@/lib/hooks/useOnboardingState', () => ({ useOnboardingState: () => mockProgress }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/ClientOnlyNav', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/OutfitGrid', () => ({ __esModule: true, default: ({ initialFavoritesOnly }: { initialFavoritesOnly?: boolean }) =>
  <div><a href="/outfits/saved-1">Open saved look</a><span>{initialFavoritesOnly ? 'Favorites filter active' : 'All saved looks'}</span></div> }));

const readyState: OnboardingState = {
  schemaVersion: 1, revision: 1, stage: 'complete', profileComplete: true,
  draft: { answers: [], currentQuestionId: null },
  capsule: { savedCount: 10, usableCount: 10, minimum: 10, hasCoverage: true, missingCategories: [], ready: true },
  milestones: { styleCompletedAt: null, capsuleCompletedAt: null, firstOutfitId: 'saved-1' },
};
beforeEach(() => {
  mockRefresh.mockReset();
  mockProgress = { state: readyState, loading: false, error: null, refresh: mockRefresh };
});

it('keeps saved looks accessible below ten items with a nonblocking capsule continuation', () => {
  mockProgress.state = { ...readyState, capsule: { ...readyState.capsule, savedCount: 4, usableCount: 4, ready: false } };
  render(<OutfitsPage />);
  expect(screen.getByRole('link', { name: 'Open saved look' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Continue my capsule' })).toHaveAttribute('href', '/onboarding');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'New outfit' })).toHaveAttribute('href', '/outfits/generate');
});

it('does not treat ten pieces without coverage as a ready capsule', () => {
  mockProgress.state = { ...readyState, capsule: { ...readyState.capsule, hasCoverage: false, ready: false, missingCategories: ['shoes'] } };
  render(<OutfitsPage />);
  expect(screen.getByRole('link', { name: 'Continue my capsule' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Open saved look' })).toBeVisible();
});

it('prioritizes unfinished style questions without hiding saved looks', () => {
  mockProgress.state = { ...readyState, stage: 'style', profileComplete: false };
  render(<OutfitsPage />);
  expect(screen.getByRole('link', { name: 'Continue my style profile' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Open saved look' })).toBeVisible();
});

it('keeps progress failures separate from the saved outfit list and supports retry', () => {
  mockProgress = { ...mockProgress, state: null, error: 'Could not load' };
  render(<OutfitsPage />);
  expect(screen.getByRole('alert')).toHaveTextContent('You can still open your saved looks');
  expect(screen.getByRole('link', { name: 'Open saved look' })).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Retry setup progress' }));
  expect(mockRefresh).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole('link', { name: 'Continue my capsule' })).not.toBeInTheDocument();
});

it('retains favorite deep links and does not prompt completed users to upload again', () => {
  render(<OutfitsPage searchParams={{ view: 'favorites' }} />);
  expect(screen.getByText('Favorites filter active')).toBeVisible();
  expect(screen.queryByRole('complementary', { name: 'Continue your setup' })).not.toBeInTheDocument();
});
