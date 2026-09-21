import '@testing-library/jest-dom';
// Keep Jest types local; Cypress also declares global test functions.
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import OutfitGrid from './OutfitGrid';

const mockUser = { uid: 'user-1', getIdToken: jest.fn().mockResolvedValue('test-token') };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));
jest.mock('./OutfitEditModal', () => ({ __esModule: true, default: () => null }));

const look = { id: 'look-1', name: 'Monday classic', occasion: 'Work', style: 'Classic', items: [], isFavorite: false, createdAt: '2026-09-21T10:00:00Z', wearCount: 0 };
const otherLook = { ...look, id: 'look-2', name: 'Weekend casual' };
let loadedOutfits: typeof look[];
let favoriteResponse: () => Promise<unknown>;

const json = (body: unknown, status = 200) => ({ ok: status < 400, status, json: async () => body });

beforeEach(() => {
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});
  loadedOutfits = [look, otherLook];
  favoriteResponse = async () => json({ success: true, isFavorite: true });
  global.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} } as unknown as typeof IntersectionObserver;
  global.fetch = jest.fn(async (url: string, options?: RequestInit) => {
    if (url.includes('/favorite')) return favoriteResponse();
    if (url.includes('/worn')) return json({ error: 'Could not record wear' }, 503);
    if (url.includes('/outfit-stats/')) return json({ success: true, data: {} });
    if (options?.method === 'DELETE') return json({ error: 'Could not delete outfit' }, 503);
    return json({ outfits: loadedOutfits });
  }) as jest.Mock;
});

afterEach(() => { jest.restoreAllMocks(); });

it('keeps both cards visible and the old state when favoriting fails, then allows retry', async () => {
  favoriteResponse = async () => json({ error: 'Unable to save favorite' }, 503);
  render(<OutfitGrid />);
  fireEvent.click(await screen.findByRole('button', { name: 'Add Monday classic to favorites' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Unable to save favorite');
  expect(screen.getByText('Weekend casual')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Add Monday classic to favorites' })).toHaveAttribute('aria-pressed', 'false');

  favoriteResponse = async () => json({ success: true, isFavorite: true });
  fireEvent.click(screen.getByRole('button', { name: 'Add Monday classic to favorites' }));
  expect(await screen.findByRole('button', { name: 'Remove Monday classic from favorites' })).toHaveAttribute('aria-pressed', 'true');
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('disables only the changing card and prevents duplicate requests while a favorite is pending', async () => {
  let resolve!: (value: unknown) => void;
  favoriteResponse = () => new Promise(done => { resolve = done; });
  render(<OutfitGrid />);
  const button = await screen.findByRole('button', { name: 'Add Monday classic to favorites' });
  fireEvent.click(button);
  fireEvent.click(button);
  await waitFor(() => expect(button).toBeDisabled());
  expect(screen.getByRole('button', { name: 'Add Weekend casual to favorites' })).toBeEnabled();
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.includes('/favorite'))).toHaveLength(1);
  await act(async () => resolve(json({ success: true, isFavorite: true })));
  expect(await screen.findByRole('button', { name: 'Remove Monday classic from favorites' })).toBeEnabled();
});

it('shows a genuine zero-result search and restores outfits after clearing it', async () => {
  render(<OutfitGrid />);
  await screen.findByText('Monday classic');
  fireEvent.change(screen.getByLabelText('Search outfits'), { target: { value: 'nonexistent' } });
  fireEvent.click(screen.getByRole('button', { name: 'Search' }));
  expect(await screen.findByText('No outfits found')).toBeVisible();
  expect(screen.queryByText('Monday classic')).not.toBeInTheDocument();
  expect(screen.getByText(/Found 0 outfits matching/)).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Clear search' }));
  expect(await screen.findByText('Monday classic')).toBeVisible();
});

it('includes newly fetched matches instead of filtering a stale pre-fetch snapshot', async () => {
  render(<OutfitGrid />);
  await screen.findByText('Monday classic');
  loadedOutfits = [...loadedOutfits, { ...look, id: 'look-3', name: 'Newly loaded travel' }];
  fireEvent.change(screen.getByLabelText('Search outfits'), { target: { value: 'travel' } });
  fireEvent.click(screen.getByRole('button', { name: 'Search' }));
  expect(await screen.findByText('Newly loaded travel')).toBeVisible();
  expect(screen.queryByText('Monday classic')).not.toBeInTheDocument();
});

it('does not increment wear or announce a successful wear when the request fails', async () => {
  const listener = jest.fn();
  window.addEventListener('outfitMarkedAsWorn', listener);
  render(<OutfitGrid />);
  fireEvent.click(await screen.findByRole('button', { name: 'Mark Monday classic as worn' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Could not record wear');
  expect(screen.getAllByText('Worn 0 times')).toHaveLength(2);
  expect(listener).not.toHaveBeenCalled();
  window.removeEventListener('outfitMarkedAsWorn', listener);
});

it('keeps the deleted card available when deletion fails after one confirmation', async () => {
  const confirm = jest.spyOn(window, 'confirm');
  render(<OutfitGrid />);
  fireEvent.click(await screen.findByRole('button', { name: 'Delete Monday classic' }));
  fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Could not delete outfit');
  expect(screen.getByText('Monday classic')).toBeVisible();
  expect(screen.getByText('Weekend casual')).toBeVisible();
  expect(confirm).not.toHaveBeenCalled();
});
