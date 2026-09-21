// Keep Jest assertions local when Cypress contributes ambient test globals.
declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;

import '@testing-library/jest-dom';
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { doc, onSnapshot } from 'firebase/firestore';
import FlatLayViewer from '@/components/FlatLayViewer';
import OutfitResultsDisplay, { type GeneratedOutfit } from './outfit-results-display';

jest.mock('@/lib/firebase/config', () => ({ db: { testDatabase: true } }));
jest.mock('firebase/firestore', () => ({
  doc: jest.fn((_db, collection, id) => ({ collection, id })),
  onSnapshot: jest.fn(),
}));
jest.mock('@/components/FlatLayViewer', () => ({ __esModule: true, default: jest.fn(() => null) }));

type Snapshot = { exists: () => boolean; data: () => Record<string, unknown> };
type Listener = {
  reference: { collection: string; id: string };
  next: (snapshot: Snapshot) => void;
  error: (error: Error) => void;
  unsubscribe: jest.Mock;
};
const listeners: Listener[] = [];
const viewerMock = FlatLayViewer as jest.Mock;
const snapshotMock = onSnapshot as jest.Mock;
const outfit: GeneratedOutfit = {
  id: 'outfit-one', name: 'An afternoon in the city', style: 'Classic', mood: 'Relaxed', occasion: 'Casual',
  items: [{ id: 'shirt', name: 'Linen shirt', type: 'shirt', imageUrl: '/synthetic-shirt.jpg', color: 'White' }],
  flat_lay_status: 'awaiting_consent',
};

function props(overrides: Partial<React.ComponentProps<typeof OutfitResultsDisplay>> = {}) {
  return {
    outfit,
    rating: { rating: 0, isLiked: false, isDisliked: false, feedback: '' },
    onRatingChange: jest.fn(), onLikeToggle: jest.fn(), onDislikeToggle: jest.fn(), onFeedbackChange: jest.fn(),
    onWearOutfit: jest.fn(), onRegenerate: jest.fn(), onViewOutfits: jest.fn(), ratingSubmitted: false,
    ...overrides,
  };
}
function viewerProps() {
  return viewerMock.mock.calls[viewerMock.mock.calls.length - 1][0];
}
async function connected(count = 1) {
  await waitFor(() => expect(listeners).toHaveLength(count));
}
function emit(listener: Listener, data: Record<string, unknown>, exists = true) {
  act(() => listener.next({ exists: () => exists, data: () => data }));
}

describe('Outfit results presentation and live image updates', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    listeners.length = 0;
    snapshotMock.mockImplementation((reference, next, error) => {
      const listener = { reference, next, error, unsubscribe: jest.fn() };
      listeners.push(listener);
      return listener.unsubscribe;
    });
    viewerMock.mockImplementation(() => <div data-testid="flat-lay-viewer" />);
  });
  afterEach(() => jest.useRealTimers());

  it('updates the current outfit from props without recreating its listener', async () => {
    const initialProps = props();
    const { rerender } = render(<OutfitResultsDisplay {...initialProps} />);
    await connected();
    expect(doc).toHaveBeenCalledWith({ testDatabase: true }, 'outfits', outfit.id);
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: null, status: 'awaiting_consent', error: null }));

    rerender(<OutfitResultsDisplay {...initialProps} outfit={{ ...outfit, name: 'Updated outfit', flat_lay_status: 'pending', flat_lay_error: null, flat_lay_request_allowed: false }} />);
    expect(screen.getByRole('heading', { name: 'Updated outfit' })).toBeInTheDocument();
    expect(viewerProps()).toEqual(expect.objectContaining({ status: 'pending', requestAllowed: false }));
    expect(snapshotMock).toHaveBeenCalledTimes(1);

    rerender(<OutfitResultsDisplay {...initialProps} outfit={{ ...outfit, flat_lay_status: 'done', flat_lay_url: '/finished.png' }} />);
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: '/finished.png', status: 'done' }));
  });

  it('replaces live state with each full snapshot, respecting explicit canonical clears', async () => {
    render(<OutfitResultsDisplay {...props()} />);
    await connected();
    emit(listeners[0], { flat_lay_status: 'failed', flat_lay_error: 'Earlier request failed', flat_lay_request_allowed: false });
    expect(viewerProps()).toEqual(expect.objectContaining({ status: 'failed', error: 'Earlier request failed', requestAllowed: false }));

    emit(listeners[0], {
      flat_lay_status: 'pending', flat_lay_url: null, flat_lay_error: null, flat_lay_request_allowed: true,
      flatLayUrl: '/stale-alias.png', flatLayError: 'Stale alias error',
      metadata: { flat_lay_error: 'Stale nested error', flat_lay_url: '/stale-nested.png' },
    });
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: null, status: 'pending', error: null, requestAllowed: true }));

    emit(listeners[0], { flat_lay_status: 'done', flat_lay_url: '/finished.png' });
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: '/finished.png', status: 'done', error: null }));
    emit(listeners[0], {});
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: null, status: 'awaiting_consent', error: null, requestAllowed: true }));
  });

  it('shows subscription failures without losing the outfit and supports reconnect and cleanup', async () => {
    const { unmount } = render(<OutfitResultsDisplay {...props()} />);
    await connected();
    emit(listeners[0], { flat_lay_status: 'pending' });
    act(() => listeners[0].error(new Error('Connection lost')));
    expect(screen.getByRole('status')).toHaveTextContent('Live preview updates are unavailable');
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(viewerProps().status).toBe('pending');

    fireEvent.click(screen.getByRole('button', { name: 'Reconnect' }));
    await connected(2);
    expect(listeners[0].unsubscribe).toHaveBeenCalledTimes(1);
    emit(listeners[1], { flat_lay_status: 'done', flat_lay_url: '/reconnected.png' });
    expect(screen.queryByText(/Live preview updates are unavailable/)).not.toBeInTheDocument();
    expect(viewerProps().flatLayUrl).toBe('/reconnected.png');
    unmount();
    expect(listeners[1].unsubscribe).toHaveBeenCalledTimes(1);
  });

  it('keeps current state when the document temporarily disappears and clears the warning when it returns', async () => {
    render(<OutfitResultsDisplay {...props()} />);
    await connected();
    emit(listeners[0], { flat_lay_status: 'processing' });
    emit(listeners[0], {}, false);
    expect(screen.getByRole('status')).toHaveTextContent('Live preview updates are unavailable');
    expect(viewerProps().status).toBe('processing');
    emit(listeners[0], { flat_lay_status: 'done', flat_lay_url: '/returned.png' });
    expect(screen.queryByRole('button', { name: 'Reconnect' })).not.toBeInTheDocument();
    expect(viewerProps().flatLayUrl).toBe('/returned.png');
  });

  it('recovers from listener setup failure through the same reconnect action', async () => {
    snapshotMock.mockImplementationOnce(() => { throw new Error('Listener unavailable'); });
    render(<OutfitResultsDisplay {...props()} />);
    expect(await screen.findByRole('button', { name: 'Reconnect' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Reconnect' }));
    await connected();
    emit(listeners[0], { flat_lay_status: 'done', flat_lay_url: '/ready.png' });
    expect(screen.queryByRole('button', { name: 'Reconnect' })).not.toBeInTheDocument();
  });

  it('unsubscribes and ignores stale callbacks when changing outfits', async () => {
    const initialProps = props();
    const { rerender, unmount } = render(<OutfitResultsDisplay {...initialProps} />);
    await connected();
    const previous = listeners[0];
    rerender(<OutfitResultsDisplay {...initialProps} outfit={{ ...outfit, id: 'outfit-two', name: 'Another look', flat_lay_status: 'manual_pending' }} />);
    await connected(2);
    expect(previous.unsubscribe).toHaveBeenCalledTimes(1);
    expect(listeners[1].reference.id).toBe('outfit-two');
    emit(previous, { flat_lay_status: 'done', flat_lay_url: '/wrong-outfit.png' });
    act(() => previous.error(new Error('Stale error')));
    expect(viewerProps()).toEqual(expect.objectContaining({ flatLayUrl: null, status: 'manual_pending' }));
    expect(screen.queryByRole('button', { name: 'Reconnect' })).not.toBeInTheDocument();
    unmount();
    expect(listeners[1].unsubscribe).toHaveBeenCalledTimes(1);
  });

  it('does not subscribe if unmounted before dynamic imports finish', async () => {
    const { unmount } = render(<OutfitResultsDisplay {...props()} />);
    unmount();
    await act(async () => { await Promise.resolve(); });
    expect(snapshotMock).not.toHaveBeenCalled();
  });

  it('shows a delayed session message after 90 seconds and clears it when a result arrives', async () => {
    jest.useFakeTimers();
    const initialProps = props({ outfit: { ...outfit, flat_lay_status: 'pending' } });
    const { rerender, unmount } = render(<OutfitResultsDisplay {...initialProps} />);
    await act(async () => { await Promise.resolve(); });
    expect(listeners).toHaveLength(1);
    act(() => jest.advanceTimersByTime(89999));
    expect(viewerProps().status).toBe('pending');
    act(() => jest.advanceTimersByTime(1));
    expect(viewerProps().status).toBe('delayed');
    emit(listeners[0], { flat_lay_status: 'done', flat_lay_url: '/finished.png' });
    expect(viewerProps()).toEqual(expect.objectContaining({ status: 'done', flatLayUrl: '/finished.png' }));
    rerender(<OutfitResultsDisplay {...initialProps} outfit={{ ...outfit, id: 'new-outfit', flat_lay_status: 'processing' }} />);
    expect(viewerProps().status).toBe('processing');
    act(() => jest.advanceTimersByTime(89999));
    expect(viewerProps().status).toBe('processing');
    unmount();
    act(() => jest.advanceTimersByTime(100000));
  });

  it('does not invent confidence or weather praise when no supporting information exists', async () => {
    render(<OutfitResultsDisplay {...props()} />);
    await connected();
    expect(screen.queryByText(/85%|85\/100|match|weather.?appropriate|perfect.*weather|protective layers/i)).not.toBeInTheDocument();
    expect(screen.queryByText('Styling notes')).not.toBeInTheDocument();
    expect(screen.getByText('Selected from your wardrobe')).toBeVisible();
    expect(screen.queryByText(/Weather context|Estimated context/)).not.toBeInTheDocument();
  });

  it('preserves a valid zero score and presents only supplied styling evidence', async () => {
    render(<OutfitResultsDisplay {...props({ outfit: {
      ...outfit, confidence_score: 0, reasoning: 'The shirt and trousers have a similar visual weight.',
      outfitAnalysis: { color: { insight: 'A neutral palette.' }, weather: { score: 0.8 } },
      weather: { temperature: 72, fallback: true },
      items: [{ ...outfit.items[0], reason: 'A breathable layer.' }],
    } })} />);
    await connected();
    expect(screen.getByText('Estimated context: 72°F')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Styling notes'));
    expect(screen.getByText('Styling score: 0/100 · Internal ranking score')).toBeVisible();
    expect(screen.getByText('The shirt and trousers have a similar visual weight.')).toBeVisible();
    expect(screen.getByText('A neutral palette.')).toBeVisible();
    expect(screen.getByText(/A breathable layer/)).toBeVisible();
    expect(screen.queryByText(/85%|weather.?appropriate|perfect.*weather/i)).not.toBeInTheDocument();
  });

  it.each([-0.1, 1.1, NaN, Infinity])('omits an invalid ranking score %s', async (score) => {
    render(<OutfitResultsDisplay {...props({ outfit: { ...outfit, confidence_score: score } })} />);
    await connected();
    expect(screen.queryByText('Styling notes')).not.toBeInTheDocument();
    expect(screen.queryByText(/Styling score/)).not.toBeInTheDocument();
  });

  it('wires wear, regenerate, navigation, and optional feedback controls', async () => {
    const callbacks = props();
    render(<OutfitResultsDisplay {...callbacks} />);
    await connected();
    fireEvent.click(screen.getByRole('button', { name: 'Wear this outfit' }));
    fireEvent.click(screen.getByRole('button', { name: 'Try another' }));
    fireEvent.click(screen.getByRole('button', { name: 'My Looks' }));
    expect(callbacks.onWearOutfit).toHaveBeenCalledTimes(1);
    expect(callbacks.onRegenerate).toHaveBeenCalledTimes(1);
    expect(callbacks.onViewOutfits).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByText('How does this feel?'));
    fireEvent.click(screen.getByRole('button', { name: 'Rate 3 stars' }));
    fireEvent.click(screen.getByRole('button', { name: 'Like' }));
    fireEvent.click(screen.getByRole('button', { name: 'Not for me' }));
    fireEvent.change(screen.getByLabelText('Anything you would change?'), { target: { value: 'Lighter shoes' } });
    expect(callbacks.onRatingChange).toHaveBeenCalledWith(3);
    expect(callbacks.onLikeToggle).toHaveBeenCalledTimes(1);
    expect(callbacks.onDislikeToggle).toHaveBeenCalledTimes(1);
    expect(callbacks.onFeedbackChange).toHaveBeenCalledWith('Lighter shoes');
  });

  it('reflects worn and submitted feedback state without repeating their mutations', async () => {
    const callbacks = props({ isWorn: true, ratingSubmitted: true, rating: { rating: 3, isLiked: true, isDisliked: false, feedback: 'Works well' } });
    render(<OutfitResultsDisplay {...callbacks} />);
    await connected();
    fireEvent.click(screen.getByRole('button', { name: 'View My Looks' }));
    expect(callbacks.onViewOutfits).toHaveBeenCalledTimes(1);
    expect(callbacks.onWearOutfit).not.toHaveBeenCalled();
    expect(screen.getByText('Marked as worn')).toBeVisible();
    fireEvent.click(screen.getByText('Feedback saved'));
    expect(screen.getByRole('button', { name: 'Rate 3 stars' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Rate 3 stars' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: 'Liked' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Liked' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByLabelText('Anything you would change?')).toBeDisabled();
    expect(screen.getByLabelText('Anything you would change?')).toHaveValue('Works well');
  });

  it('forwards the existing request and credit contracts to the viewer', async () => {
    const request = jest.fn();
    const skip = jest.fn();
    const usage = { tier: 'premium', remaining: 1, limit: 5, used: 4 };
    render(<OutfitResultsDisplay {...props({
      outfit: { ...outfit, flat_lay_request_allowed: false },
      onRequestFlatLay: request, onSkipFlatLay: skip, flatLayUsage: usage, flatLayLoading: true,
      flatLayError: 'Credit balance unavailable', flatLayActionLoading: true, hasFlatLayCredits: true,
    })} />);
    await connected();
    expect(viewerProps()).toEqual(expect.objectContaining({
      requestAllowed: false, onRequestFlatLay: request, onSkipFlatLay: skip, flatLayUsage: usage,
      flatLayLoading: true, flatLayError: 'Credit balance unavailable', flatLayActionLoading: true,
      hasFlatLayCredits: true,
    }));
  });
});
