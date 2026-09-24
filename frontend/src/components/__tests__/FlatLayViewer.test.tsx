// Cypress also supplies globals; use Jest assertions explicitly in this module.
declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;

import '@testing-library/jest-dom';
import React from 'react';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FlatLayViewer from '@/components/FlatLayViewer';

const pieces = [
  { id: 'shirt', name: 'Linen shirt', type: 'shirt', imageUrl: '/test-shirt.jpg' },
  { id: 'trousers', name: 'Navy trousers', type: 'pants', imageUrl: '/test-trousers.jpg' },
];
const credits = { tier: 'premium', remaining: 1, limit: 5, used: 4 };
const ready = { flatLayUrl: '/test-flat-lay.png', outfitName: 'A quiet afternoon', outfitItems: pieces };
const originalFetch = global.fetch;

function loadImage() {
  fireEvent.load(screen.getByRole('img', { name: 'AI-styled preview of A quiet afternoon' }));
}

describe('Flat lay presentation', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    Object.defineProperty(navigator, 'share', { configurable: true, value: undefined });
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: undefined });
  });
  afterEach(() => {
    jest.restoreAllMocks();
    global.fetch = originalFetch;
  });

  it('keeps the real pieces visible before consent and requests only on an explicit click', () => {
    const request = jest.fn();
    const skip = jest.fn();
    const { container } = render(<FlatLayViewer outfitItems={pieces} status="awaiting_consent" onRequestFlatLay={request} onSkipFlatLay={skip} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByRole('list', { name: 'Outfit pieces' })).toBeVisible();
    expect(screen.getByRole('img', { name: 'Linen shirt' })).toBeVisible();
    expect(container.querySelector('[class*="blur-"]')).toBeNull();
    expect(screen.getByRole('list', { name: 'Outfit pieces' })).not.toHaveClass('pointer-events-none');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Create flat lay' }));
    expect(request).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Maybe later' }));
    expect(skip).toHaveBeenCalledTimes(1);
  });

  it.each(['pending', 'processing', 'queued', 'delayed'])('keeps pieces available without a duplicate request while %s', (status) => {
    const request = jest.fn();
    render(<FlatLayViewer outfitItems={pieces} status={status} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(screen.getByRole('status')).toHaveTextContent(status === 'delayed' ? 'taking longer than expected' : 'being prepared');
    expect(screen.queryByText(/few seconds/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /request|create/i })).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
  });

  it.each([
    { flatLayUsage: null },
    { flatLayUsage: { ...credits, remaining: 0 }, flatLayLoading: true },
    { flatLayUsage: { ...credits, remaining: 0 }, flatLayError: 'Balance service unavailable' },
  ])('does not treat unknown, loading, or failed balance checks as exhausted credits: %j', (balance) => {
    render(<FlatLayViewer outfitItems={pieces} status="awaiting_consent" onRequestFlatLay={jest.fn()} {...balance} />);
    expect(screen.queryByRole('link', { name: 'View plans' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create flat lay' })).toBeDisabled();
    expect(screen.getByText('Linen shirt')).toBeVisible();
  });

  it('offers a plan link only after a verified exhausted balance', () => {
    render(<FlatLayViewer outfitItems={pieces} status="awaiting_consent" onRequestFlatLay={jest.fn()} flatLayUsage={{ ...credits, remaining: 0 }} />);
    expect(screen.getByRole('link', { name: 'View plans' })).toHaveAttribute('href', '/upgrade');
    expect(screen.getByText('0 flat lay credits remaining this week.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create flat lay' })).toBeDisabled();
  });

  it('keeps a failed generation visible with its pieces and an explicit request action', () => {
    const request = jest.fn();
    render(<FlatLayViewer outfitItems={pieces} status="failed" error="The image service is unavailable." onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByRole('alert')).toHaveTextContent('could not be created');
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(request).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Request a new flat lay' }));
    expect(request).toHaveBeenCalledTimes(1);
  });

  it('honors a blocked retry contract without offering another paid request', () => {
    const request = jest.fn();
    render(<FlatLayViewer outfitItems={pieces} status="failed" error="This previous request needs review before another can be made." requestAllowed={false} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByRole('alert')).toHaveTextContent('needs review');
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(screen.queryByRole('button', { name: /request|create/i })).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
  });

  it('uses a square image stage and supports accessible view selection without losing the user choice on status updates', () => {
    const onViewChange = jest.fn();
    const { rerender } = render(<FlatLayViewer {...ready} status="completed" onViewChange={onViewChange} />);
    const image = screen.getByRole('img', { name: 'AI-styled preview of A quiet afternoon' });
    expect(image.parentElement).toHaveClass('aspect-square');
    expect(image).toHaveClass('object-contain');
    expect(screen.getByText('AI styled preview')).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Your look' })).toBeVisible();
    expect(screen.getByText('Garment details may vary. See Pieces for original photos.')).toBeVisible();
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Pieces' }));
    expect(onViewChange).toHaveBeenLastCalledWith('grid');
    expect(screen.getByText('From your wardrobe')).toBeVisible();
    expect(screen.getByRole('heading', { name: 'The pieces' })).toBeVisible();
    expect(screen.queryByText('AI styled preview')).not.toBeInTheDocument();
    expect(screen.queryByText(/Garment details may vary/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pieces' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText('Linen shirt')).toBeVisible();
    rerender(<FlatLayViewer {...ready} status="ready" onViewChange={onViewChange} />);
    expect(screen.getByText('Linen shirt')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Flat lay' }));
    expect(onViewChange).toHaveBeenLastCalledWith('flat-lay');
    expect(screen.getByRole('img', { name: 'AI-styled preview of A quiet afternoon' })).toBeVisible();
  });

  it.each([
    { outfitItems: pieces, showItemGrid: false },
    { outfitItems: [], showItemGrid: true },
  ])('omits directions to Pieces when the source-photo view is unavailable: %j', (availability) => {
    render(<FlatLayViewer {...ready} {...availability} />);
    loadImage();
    expect(screen.getByText('Garment details may vary.')).toBeVisible();
    expect(screen.queryByText(/See Pieces/)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Pieces' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'View flat lay in full screen' }));
    expect(within(screen.getByRole('dialog')).getByText('Garment details may vary.')).toBeVisible();
    expect(within(screen.getByRole('dialog')).queryByText(/See Pieces/)).not.toBeInTheDocument();
  });

  it('enables controls for a cached image even when no new load event arrives', () => {
    jest.spyOn(HTMLImageElement.prototype, 'complete', 'get').mockReturnValue(true);
    jest.spyOn(HTMLImageElement.prototype, 'naturalWidth', 'get').mockReturnValue(1024);
    render(<FlatLayViewer {...ready} />);
    expect(screen.getByRole('button', { name: 'View flat lay in full screen' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Download' })).toBeEnabled();
    expect(screen.queryByText('Loading flat lay')).not.toBeInTheDocument();
  });

  it('settles a cached image when its URL arrives after the pieces were displayed', () => {
    jest.spyOn(HTMLImageElement.prototype, 'complete', 'get').mockReturnValue(true);
    jest.spyOn(HTMLImageElement.prototype, 'naturalWidth', 'get').mockReturnValue(1024);
    const { rerender } = render(<FlatLayViewer outfitItems={pieces} status="processing" />);
    rerender(<FlatLayViewer {...ready} status="done" />);
    expect(screen.getByRole('button', { name: 'View flat lay in full screen' })).toBeEnabled();
    expect(screen.queryByText('Loading flat lay')).not.toBeInTheDocument();
  });

  it('falls back to actual pieces when the flat lay image fails, without creating another generation', () => {
    const request = jest.fn();
    render(<FlatLayViewer {...ready} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    fireEvent.error(screen.getByRole('img', { name: 'AI-styled preview of A quiet afternoon' }));
    expect(screen.getByRole('alert')).toHaveTextContent('could not be loaded');
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(screen.queryByRole('button', { name: /request|create/i })).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
  });

  it('retains item names when an individual garment photo fails', () => {
    render(<FlatLayViewer outfitItems={pieces} />);
    fireEvent.error(screen.getByRole('img', { name: 'Linen shirt' }));
    expect(screen.getByText('Photo unavailable')).toBeVisible();
    expect(screen.getByText('Linen shirt')).toBeVisible();
    expect(screen.getByRole('img', { name: 'Navy trousers' })).toBeVisible();
  });

  it('opens a named dialog and closes with Escape, restoring focus to its trigger', async () => {
    const user = userEvent.setup();
    render(<FlatLayViewer {...ready} />);
    loadImage();
    const trigger = screen.getByRole('button', { name: 'View flat lay in full screen' });
    await user.click(trigger);
    const dialog = screen.getByRole('dialog', { name: 'A quiet afternoon' });
    expect(within(dialog).getByRole('img', { name: 'AI-styled preview of A quiet afternoon, enlarged' })).toBeVisible();
    expect(dialog).toContainElement(document.activeElement as HTMLElement);
    expect(within(dialog).getByText('Garment details may vary. See Pieces for original photos.')).toBeVisible();
    await user.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(trigger).toHaveFocus();
  });

  it.each([
    { ok: false, headers: { get: () => 'image/png' } },
    { ok: true, headers: { get: () => 'application/json' } },
    { ok: true, headers: { get: () => 'image/png' }, blob: async () => new Blob([], { type: 'image/png' }) },
  ])('shows a truthful download failure for a non-image, failed, or empty response: %j', async (response) => {
    (global.fetch as jest.Mock).mockResolvedValue(response);
    render(<FlatLayViewer {...ready} />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Download' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('could not be downloaded');
    expect(screen.queryByText('Download started.')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Download' })).toBeEnabled();
  });

  it('downloads an image response and releases its object URL', async () => {
    const click = jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: jest.fn(() => 'blob:local-test-image') });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: jest.fn() });
    (global.fetch as jest.Mock).mockResolvedValue({ ok: true, headers: { get: () => 'image/png' }, blob: async () => new Blob(['image-data'], { type: 'image/png' }) });
    render(<FlatLayViewer {...ready} />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Download' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Download started.');
    expect(click).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:local-test-image');
    expect(document.querySelector('a[download]')).toBeNull();
  });

  it('waits for clipboard confirmation and shows a failure instead of claiming a copied link', async () => {
    const writeText = jest.fn().mockRejectedValue(new Error('Clipboard blocked'));
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } });
    render(<FlatLayViewer {...ready} />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Share' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('could not be shared');
    expect(screen.queryByText('Flat lay link copied.')).not.toBeInTheDocument();
    expect(writeText).toHaveBeenCalledWith(ready.flatLayUrl);
  });

  it('confirms a successful clipboard copy', async () => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: jest.fn().mockResolvedValue(undefined) } });
    render(<FlatLayViewer {...ready} />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Share' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Flat lay link copied.');
  });

  it('does not report native share cancellation as an error', async () => {
    Object.defineProperty(navigator, 'share', { configurable: true, value: jest.fn().mockRejectedValue(new DOMException('Cancelled', 'AbortError')) });
    render(<FlatLayViewer {...ready} />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Share' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Share' })).toBeEnabled());
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
  it('retries a failed image load without submitting a new paid request', () => {
    const request = jest.fn();
    render(<FlatLayViewer {...ready} onRequestFlatLay={request} />);
    fireEvent.error(screen.getByRole('img', { name: 'AI-styled preview of A quiet afternoon' }));
    fireEvent.click(screen.getByRole('button', { name: 'Retry loading image' }));
    loadImage();
    expect(screen.getByRole('button', { name: 'Download' })).toBeEnabled();
    expect(request).not.toHaveBeenCalled();
  });

  it.each(['queued', 'processing', 'failed', 'stale', 'unexpected_state'])('hides an earlier image when the current state is %s', status => {
    render(<FlatLayViewer {...ready} status={status} onRequestFlatLay={jest.fn()} />);
    expect(screen.queryByRole('img', { name: 'AI-styled preview of A quiet afternoon' })).not.toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Linen shirt' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Download' })).not.toBeInTheDocument();
  });

  it('requires a status refresh for an unknown state or a completed request without an image', () => {
    const refresh = jest.fn();
    const request = jest.fn();
    const { rerender } = render(<FlatLayViewer outfitItems={pieces} status="unknown" onRefresh={refresh} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByText('Your flat lay status is unavailable')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Create flat lay' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Refresh status' }));
    expect(refresh).toHaveBeenCalledTimes(1);
    rerender(<FlatLayViewer outfitItems={pieces} status="done" onRefresh={refresh} onRequestFlatLay={request} />);
    expect(screen.getByText('Your flat lay status is unavailable')).toBeVisible();
    expect(request).not.toHaveBeenCalled();
  });

  it('does not download or display stale success after navigating to another saved look', async () => {
    let resolveFetch!: (value: unknown) => void;
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(resolve => { resolveFetch = resolve; }));
    const click = jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    const { rerender } = render(<FlatLayViewer {...ready} outfitId="first" />);
    loadImage();
    fireEvent.click(screen.getByRole('button', { name: 'Download' }));
    rerender(<FlatLayViewer outfitId="second" outfitItems={pieces} status="awaiting_consent" />);
    await act(async () => { resolveFetch({ ok: true, headers: { get: () => 'image/png' }, blob: async () => new Blob(['late-image'], { type: 'image/png' }) }); });
    expect(click).not.toHaveBeenCalled();
    expect(screen.queryByText('Download started.')).not.toBeInTheDocument();
  });

  it.each(['awaiting_consent', 'manual_pending', 'failed', 'stale'])('offers read-only balance recovery while %s without creating a request', status => {
    const refresh = jest.fn();
    const request = jest.fn();
    const { rerender } = render(<FlatLayViewer outfitItems={pieces} status={status} onRefresh={refresh} onRequestFlatLay={request} />);
    fireEvent.click(screen.getByRole('button', { name: 'Refresh status' }));
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(request).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: status === 'failed' ? 'Request a new flat lay' : 'Create flat lay' })).toBeDisabled();
    rerender(<FlatLayViewer outfitItems={pieces} status={status} onRefresh={refresh} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits flatLayError="Credit check failed" refreshPending />);
    expect(screen.getByRole('button', { name: 'Refreshing…' })).toBeDisabled();
    expect(screen.getByText('Credit check failed')).toBeVisible();
    expect(request).not.toHaveBeenCalled();
    rerender(<FlatLayViewer outfitItems={pieces} status={status} onRefresh={refresh} onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByRole('button', { name: status === 'failed' ? 'Request a new flat lay' : 'Create flat lay' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Refresh status' })).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
  });

  it('explains a changed outfit when the server returns to awaiting consent without creating another image', () => {
    const request = jest.fn();
    const explanation = 'These pieces have changed since your previous flat lay. Create a new one when you are ready.';
    render(<FlatLayViewer outfitItems={pieces} flatLayUrl={null} status="awaiting_consent" error={explanation} requestAllowed onRequestFlatLay={request} flatLayUsage={credits} hasFlatLayCredits />);
    expect(screen.getByText('Your outfit has changed')).toBeVisible();
    expect(screen.getByText(explanation)).toBeVisible();
    expect(screen.getByRole('img', { name: 'Linen shirt' })).toBeVisible();
    expect(screen.queryByRole('img', { name: /AI-styled preview/ })).not.toBeInTheDocument();
    expect(request).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Create flat lay' }));
    expect(request).toHaveBeenCalledTimes(1);
  });

});

it('keeps original pieces visible and disables new requests during the global pause', () => {
  const request = jest.fn();
  render(<FlatLayViewer outfitItems={pieces} status="awaiting_consent" onRequestFlatLay={request}
    requestAllowed={false} admissionPaused admissionReason="Flat-lay requests are temporarily paused. No credit was used."
    flatLayUsage={credits} hasFlatLayCredits />);
  expect(screen.getByRole('button', { name: 'Temporarily unavailable' })).toBeDisabled();
  expect(screen.getByText(/requests are temporarily paused/)).toBeVisible();
  expect(screen.getByRole('img', { name: 'Linen shirt' })).toBeVisible();
  expect(request).not.toHaveBeenCalled();
});
