declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;

import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { User } from 'firebase/auth';
import SavedOutfitView from './SavedOutfitView';
import OutfitResultsDisplay from '@/components/ui/outfit-results-display';
import { subscriptionService } from '@/lib/services/subscriptionService';
import { requestFlatLay } from '@/lib/services/flatLayService';
import { clearWearOperation } from '@/lib/savedOutfit';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock('@/lib/services/subscriptionService', () => ({ subscriptionService: { getCurrentSubscription: jest.fn() } }));
jest.mock('@/lib/services/flatLayService', () => ({ requestFlatLay: jest.fn() }));
jest.mock('@/components/ui/outfit-results-display', () => ({ __esModule: true, default: jest.fn((props: any) => <div>
  <h1>{props.outfit.name}</h1><p>Favorite: {String(props.isFavorite)}</p><p>Wear count: {props.wearCount}</p>
  <p>Worn today: {String(props.isWorn)}</p><p>Preview: {props.outfit.flat_lay_status}</p>
  <p>Credits: {props.flatLayUsage?.remaining ?? 'unknown'}</p><p>{props.flatLayError}</p><p>{props.wearError}</p><p>{props.favoriteError}</p>
  <p>Feedback: {props.rating.feedback}</p>
  <button onClick={props.onRefresh}>Refresh detail</button>
  <button onClick={props.onFavoriteToggle}>Favorite</button>
  <button onClick={props.onWearOutfit} disabled={!props.canWear}>Wear</button>
  <button onClick={props.onRequestFlatLay} disabled={!props.hasFlatLayCredits || !!props.flatLayError}>Create flatlay</button>
  <button onClick={props.onSaveFeedback}>Save feedback</button>
</div>) }));

const user = { uid: 'owner', getIdToken: jest.fn(async () => 'owner-token') } as unknown as User;
const viewer = OutfitResultsDisplay as jest.Mock;
const subscription = subscriptionService.getCurrentSubscription as jest.Mock;
const previewRequest = requestFlatLay as jest.Mock;
const response = (data: unknown, status = 200) => Promise.resolve({ ok: status < 400, status, json: async () => data } as Response);
const clone = (value: any) => JSON.parse(JSON.stringify(value));
const deferred = () => { let resolve!: (value: any) => void; const promise = new Promise<any>(r => { resolve = r; }); return { promise, resolve }; };
let outfit: any;
let fetchMock: jest.Mock;
const latest = () => viewer.mock.calls[viewer.mock.calls.length - 1][0];
async function loaded() { await screen.findByRole('heading', { name: 'A saved afternoon' }); await waitFor(() => expect(latest().flatLayLoading).toBe(false)); }
const writes = () => fetchMock.mock.calls.filter(([, options]) => options?.method && options.method !== 'GET');

beforeEach(() => {
  jest.clearAllMocks();
  clearWearOperation('owner', 'look');
  outfit = { id: 'look', user_id: 'owner', name: 'A saved afternoon', style: 'Classic', mood: 'Relaxed', occasion: 'Casual',
    items: [{ id: 'dress', type: 'dress', name: 'Blue dress', color: 'blue' }, { id: 'shoes', type: 'shoes', name: 'White sneakers', color: 'white' }],
    isFavorite: false, wearCount: 0, flat_lay_status: 'awaiting_consent', flat_lay_request_allowed: true };
  subscription.mockResolvedValue({ role: 'free', flatlays_remaining: 1 });
  previewRequest.mockResolvedValue({ success: true, id: 'look', flat_lay_status: 'pending' });
  fetchMock = jest.fn(() => response(clone(outfit)));
  global.fetch = fetchMock;
});
afterEach(() => { jest.useRealTimers(); });

describe('Owned saved outfit controller', () => {
  it('reopens and refreshes the owned result without generation, preview or wear writes', async () => {
    const first = render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    expect(latest().isWorn).toBe(false);
    fireEvent.click(screen.getByText('Refresh detail'));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    first.unmount();
    render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    expect(writes()).toHaveLength(0);
    expect(previewRequest).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledWith('/api/outfits/look', expect.objectContaining({ cache: 'no-store', headers: expect.objectContaining({ Authorization: 'Bearer owner-token' }) }));
  });

  it('never exposes a result for another owner or keeps one after a confirming 404', async () => {
    const view = render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    fetchMock.mockImplementation(() => response({ error: 'Unavailable' }, 404));
    fireEvent.click(screen.getByText('Refresh detail'));
    await screen.findByText('Unavailable');
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    fetchMock.mockImplementation(() => response({ ...outfit, user_id: 'foreign' }));
    fireEvent.click(screen.getByText('Try again'));
    await screen.findByText('The server could not confirm this saved outfit.');
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    view.rerender(<SavedOutfitView id="look" user={null} />);
    expect(screen.getByRole('link', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('recovers a failed balance read and enables explicit creation without a hidden request', async () => {
    subscription.mockRejectedValueOnce(new Error('offline'));
    render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    expect(screen.getByRole('button', { name: 'Create flatlay' })).toBeDisabled();
    fireEvent.click(screen.getByText('Refresh detail'));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Create flatlay' })).toBeEnabled());
    expect(screen.queryByText('Unable to load your flatlay balance. Refresh to try again.')).not.toBeInTheDocument();
    expect(previewRequest).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Create flatlay' }));
    await waitFor(() => expect(previewRequest).toHaveBeenCalledTimes(1));
    expect(previewRequest).toHaveBeenCalledWith('look', 'owner-token');
  });

  it('polls a pending request through refund and refreshes the last credit before explicit retry', async () => {
    jest.useFakeTimers();
    outfit = { ...outfit, flat_lay_status: 'pending', flat_lay_request_id: 'request-1', flat_lay_credit_status: 'reserved' };
    subscription.mockResolvedValue({ role: 'free', flatlays_remaining: 0 });
    render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    expect(screen.getByText('Credits: 0')).toBeInTheDocument();
    outfit = { ...outfit, flat_lay_status: 'failed', flat_lay_credit_status: 'refunded', flat_lay_request_allowed: true };
    subscription.mockResolvedValue({ role: 'free', flatlays_remaining: 1 });
    await act(async () => { jest.advanceTimersByTime(5000); });
    await waitFor(() => expect(screen.getByText('Credits: 1')).toBeInTheDocument());
    expect(previewRequest).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Create flatlay' }));
    await waitFor(() => expect(previewRequest).toHaveBeenCalledTimes(1));
  });

  it('ignores a detail read that started before the favorite acknowledgment', async () => {
    render(<SavedOutfitView id="look" user={user} />);
    await loaded();
    const oldRead = deferred();
    fetchMock.mockImplementationOnce(() => oldRead.promise);
    fireEvent.click(screen.getByText('Refresh detail'));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    fetchMock.mockImplementation((url, options) => {
      if (options?.method === 'PUT') { outfit.isFavorite = JSON.parse(options.body).isFavorite; return response({ isFavorite: outfit.isFavorite }); }
      return response(clone(outfit));
    });
    fireEvent.click(screen.getByText('Favorite', { selector: 'button' }));
    await screen.findByText('Favorite: true');
    await act(async () => { oldRead.resolve(await response({ ...outfit, isFavorite: false })); });
    expect(screen.getByText('Favorite: true')).toBeInTheDocument();
    expect(writes()).toHaveLength(1);
  });

  it('retries an ambiguous favorite as the same explicit desired value', async () => {
    let attempts = 0;
    fetchMock.mockImplementation((url, options) => {
      if (options?.method === 'PUT') { attempts++; outfit.isFavorite = true; return attempts === 1 ? response({ error: 'Lost acknowledgment' }, 503) : response({ isFavorite: true }); }
      return response(clone(outfit));
    });
    render(<SavedOutfitView id="look" user={user} />); await loaded();
    fireEvent.click(screen.getByText('Favorite', { selector: 'button' }));
    await screen.findByText('Lost acknowledgment');
    fireEvent.click(screen.getByText('Favorite', { selector: 'button' }));
    await screen.findByText('Favorite: true');
    expect(writes().map(([, options]) => JSON.parse(options.body))).toEqual([{ isFavorite: true }, { isFavorite: true }]);
  });

  it('keeps the same wear key after lost acknowledgment and remount, and adopts authoritative current counts', async () => {
    let attempts = 0;
    const receipt = { success: true, outfit_id: 'look', event_id: 'original-event', wear_date: '2026-09-20', wear_count: 6,
      last_worn: Date.now(), last_wear_date: '2026-09-22', last_wear_timezone: 'UTC' };
    fetchMock.mockImplementation((url, options) => {
      if (options?.method === 'POST') {
        attempts++;
        if (attempts === 1) return response({ error: 'Lost acknowledgment' }, 503);
        outfit = { ...outfit, wearCount: receipt.wear_count, lastWorn: receipt.last_worn };
        return response(receipt);
      }
      return response(clone(outfit));
    });
    const first = render(<SavedOutfitView id="look" user={user} />); await loaded();
    fireEvent.click(screen.getByText('Wear', { selector: 'button' }));
    await screen.findByText('Lost acknowledgment');
    first.unmount();
    render(<SavedOutfitView id="look" user={user} />); await loaded();
    fireEvent.click(screen.getByText('Wear', { selector: 'button' }));
    await screen.findByText('Wear count: 6');
    const keys = writes().map(([, options]) => JSON.parse(options.body).idempotency_key);
    expect(keys).toHaveLength(2); expect(keys[0]).toBe(keys[1]); expect(keys[0]).toBeTruthy();
    expect(screen.getByText('Wear recorded for 2026-09-20.')).toBeInTheDocument();
  });

  it('fences a delayed owner result after account change', async () => {
    const delayed = deferred(); fetchMock.mockImplementationOnce(() => delayed.promise);
    const view = render(<SavedOutfitView id="look" user={user} />);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    view.rerender(<SavedOutfitView id="look" user={null} />);
    await act(async () => { delayed.resolve(await response(outfit)); });
    expect(screen.queryByRole('heading', { name: 'A saved afternoon' })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('hydrates text-only saved feedback and submits only on explicit save', async () => {
    outfit.feedback = 'I would use a different jacket';
    fetchMock.mockImplementation((url, options) => options?.method === 'POST' ? response({ success: true }) : response(clone(outfit)));
    render(<SavedOutfitView id="look" user={user} />); await loaded();
    expect(screen.getByText('Feedback: I would use a different jacket')).toBeInTheDocument();
    expect(latest().ratingSubmitted).toBe(true); expect(writes()).toHaveLength(0);
    fireEvent.click(screen.getByText('Save feedback'));
    await waitFor(() => expect(writes()).toHaveLength(1));
    expect(writes()[0][0]).toBe('/api/outfits/rate');
    expect(JSON.parse(writes()[0][1].body).feedback).toBe(outfit.feedback);
  });

  it('disables wear for unavailable pieces without redirecting to generation', async () => {
    outfit.items_available = false;
    render(<SavedOutfitView id="look" user={user} />); await loaded();
    expect(screen.getByText('Wear', { selector: 'button' })).toBeDisabled();
    fireEvent.click(screen.getByText('Wear', { selector: 'button' }));
    expect(mockPush).not.toHaveBeenCalled(); expect(writes()).toHaveLength(0);
  });
});
