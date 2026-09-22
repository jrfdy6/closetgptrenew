import '@testing-library/jest-dom';
// Keep Jest types local; Cypress also declares global test functions.
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import OutfitGrid from './OutfitGrid';

let mockUser: { uid: string; getIdToken: jest.Mock };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));
jest.mock('./OutfitEditModal', () => ({ __esModule: true, default: ({ outfit }: { outfit: { name: string } }) => <div role="dialog">Editing {outfit.name}</div> }));

const look = { id: 'look-1', name: 'Monday classic', occasion: 'Work', style: 'Classic', items: [], isFavorite: false, createdAt: '2026-09-21T10:00:00Z', wearCount: 0 };
const otherLook = { ...look, id: 'look-2', name: 'Weekend casual' };
let loadedOutfits: Array<Record<string, unknown>>;
let favoriteResponse: () => Promise<unknown>;

const json = (body: unknown, status = 200) => ({ ok: status < 400, status, json: async () => body });

beforeEach(() => {
  mockUser = { uid: 'user-1', getIdToken: jest.fn().mockResolvedValue('test-token') };
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

it('opens an encoded saved-outfit address without generating or recording a wear', async () => {
  loadedOutfits = [{ ...look, id: 'look id#1' }];
  const listener = jest.fn();
  window.addEventListener('outfitMarkedAsWorn', listener);
  render(<OutfitGrid />);
  const link = await screen.findByRole('link', { name: 'Open Monday classic' });
  expect(link).toHaveAttribute('href', '/outfits/look%20id%231');
  // A normal Next Link lets keyboard, browser Back, and open-in-new-tab keep
  // navigation semantics. Its click is read navigation, not a mutation callback.
  link.addEventListener('click', event => event.preventDefault());
  fireEvent.click(link);
  expect(screen.queryByRole('button', { name: /mark .* as worn/i })).not.toBeInTheDocument();
  expect(screen.getByText('Not worn yet')).toBeVisible();
  expect(listener).not.toHaveBeenCalled();
  expect((fetch as jest.Mock).mock.calls.every(([url, init]) => !url.includes('generate') && !url.includes('/worn') && (!init?.method || init.method === 'GET'))).toBe(true);
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

it('keeps old empty entries visible without invented images or confidence claims', async () => {
  loadedOutfits = [{ ...look, confidenceScore: 0.99, flat_lay_url: 'https://example.test/stale.png', flat_lay_status: 'done', metadata: { flatLayUrl: 'https://example.test/old.png' } }];
  render(<OutfitGrid />);
  expect(await screen.findByRole('link', { name: 'Open Monday classic' })).toBeVisible();
  expect(screen.getByText('No pieces saved with this outfit.')).toBeVisible();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
  expect(screen.queryByText(/confidence|99%/i)).not.toBeInTheDocument();
});

it('shows original piece photos and an honest failure placeholder without a stale flatlay fallback', async () => {
  loadedOutfits = [{ ...look, items: [{ id: 'shirt', name: 'White shirt', originalImageUrl: '/original.jpg', imageUrl: '/cutout.png' }],
    flat_lay_url: null, metadata: { flat_lay_url: '/stale-flatlay.jpg', flat_lay_status: 'done' } }];
  render(<OutfitGrid />);
  const photo = await screen.findByRole('img', { name: 'White shirt' });
  expect(photo).toHaveAttribute('src', '/original.jpg');
  fireEvent.error(photo);
  expect(screen.getByText(/Photo unavailable/)).toBeVisible();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Open Monday classic' })).toBeVisible();
});

it('reads a saved favorite on a new visit, including explicit false over a legacy true alias', async () => {
  loadedOutfits = [{ ...look, isFavorite: true }];
  const firstVisit = render(<OutfitGrid />);
  expect(await screen.findByRole('button', { name: 'Remove Monday classic from favorites' })).toHaveAttribute('aria-pressed', 'true');
  firstVisit.unmount();
  loadedOutfits = [{ ...look, isFavorite: false, favorite: true }];
  render(<OutfitGrid />);
  expect(await screen.findByRole('button', { name: 'Add Monday classic to favorites' })).toHaveAttribute('aria-pressed', 'false');
});

it('keeps a failed load visible with a working retry instead of an empty-success state', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/outfit-stats/') ? json({ success: true, data: {} }) : json({ error: 'Unavailable' }, 503));
  render(<OutfitGrid />);
  expect(await screen.findByRole('alert')).toBeVisible();
  expect(screen.queryByText('No outfits yet')).not.toBeInTheDocument();
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/outfit-stats/') ? json({ success: true, data: {} }) : json({ outfits: [look] }));
  fireEvent.click(screen.getByRole('button', { name: 'Try Again' }));
  expect(await screen.findByRole('link', { name: 'Open Monday classic' })).toBeVisible();
});

it('keeps filtering secondary and can hide search independently', async () => {
  const view = render(<OutfitGrid showSearch={false} />);
  await screen.findByText('Monday classic');
  expect(screen.queryByLabelText('Search outfits')).not.toBeInTheDocument();
  const disclosure = screen.getByText('Filters and sort').closest('details');
  expect(disclosure).not.toHaveAttribute('open');
  view.rerender(<OutfitGrid showFilters={false} />);
  expect(screen.getByLabelText('Search outfits')).toBeVisible();
  expect(screen.queryByText('Filters and sort')).not.toBeInTheDocument();
});

it('closes the previous account edit dialog when the signed-in account changes', async () => {
  const view = render(<OutfitGrid />);
  fireEvent.click(await screen.findByRole('button', { name: 'Edit Monday classic' }));
  expect(screen.getByRole('dialog')).toHaveTextContent('Editing Monday classic');
  loadedOutfits = [{ ...look, id: 'other-look', name: 'Other account look' }];
  mockUser = { uid: 'user-2', getIdToken: jest.fn().mockResolvedValue('other-token') };
  view.rerender(<OutfitGrid />);
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(screen.queryByText('Monday classic')).not.toBeInTheDocument();
  expect(await screen.findByRole('link', { name: 'Open Other account look' })).toBeVisible();
});
