import '@testing-library/jest-dom';
// Keep Jest types local; Cypress also declares global test functions.
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import CreateOutfitPage from './page';

const mockCreateOutfit = jest.fn();
const mockPush = jest.fn();
const mockToast = jest.fn();
const mockRequestFlatLay = jest.fn();
const mockUser = { uid: 'user-1', getIdToken: jest.fn().mockResolvedValue('test-token') };
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush, back: jest.fn() }) }));
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/hooks/useOutfits_proper', () => ({ useOutfits: () => ({ createOutfit: mockCreateOutfit }) }));
jest.mock('@/lib/hooks/useWardrobe', () => ({ useWardrobe: () => ({ loading: false, items: [
  { id: 'shirt-1', name: 'Blue shirt', type: 'shirt', color: 'blue', style: ['Classic'], userId: 'user-1', imageUrl: '/shirt.jpg' },
] }) }));
jest.mock('@/components/ui/use-toast', () => ({ useToast: () => ({ toast: mockToast }) }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/ClientOnlyNav', () => ({ __esModule: true, default: () => null }));
jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('@/lib/services/flatLayService', () => ({ requestFlatLay: (...args: unknown[]) => mockRequestFlatLay(...args) }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));
jest.mock('@/lib/services/subscriptionService', () => ({ subscriptionService: {
  getCurrentSubscription: jest.fn().mockResolvedValue({ role: 'tier1', flatlays_remaining: 1 }),
  getTierInfo: () => ({ limit: '1 flat lay/week' }),
} }));

beforeEach(() => {
  jest.clearAllMocks();
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
});
afterEach(() => { jest.restoreAllMocks(); });

async function fillDraft() {
  render(<CreateOutfitPage />);
  fireEvent.click(screen.getByRole('button', { name: /Blue shirt/i }));
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
  fireEvent.change(screen.getByLabelText(/Outfit Name/), { target: { value: 'My manual look' } });
  fireEvent.change(screen.getByLabelText('Notes (Optional)'), { target: { value: 'Keep the exact blue shirt' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save Outfit' }));
}

it.each([null, {}])('keeps items/details after an unconfirmed save and never redirects or claims success: %j', async response => {
  mockCreateOutfit.mockResolvedValue(response);
  await fillDraft();
  await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })));
  expect(screen.getByDisplayValue('My manual look')).toBeVisible();
  expect(screen.getByDisplayValue('Keep the exact blue shirt')).toBeVisible();
  expect(screen.getByAltText('Blue shirt')).toBeVisible();
  expect(mockPush).not.toHaveBeenCalled();
  expect(mockToast).not.toHaveBeenCalledWith(expect.objectContaining({ title: 'Outfit saved' }));
  expect(screen.getByRole('button', { name: 'Save Outfit' })).toBeEnabled();
});

it('can retry the same draft after failure and proceed only after an ID is confirmed', async () => {
  mockCreateOutfit.mockRejectedValueOnce(new Error('Network unavailable'));
  await fillDraft();
  await waitFor(() => expect(screen.getByRole('button', { name: 'Save Outfit' })).toBeEnabled());
  mockCreateOutfit.mockResolvedValueOnce({ id: 'saved-1' });
  fireEvent.click(screen.getByRole('button', { name: 'Save Outfit' }));
  await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Outfit created!' })));
  expect(mockCreateOutfit).toHaveBeenLastCalledWith(expect.objectContaining({
    name: 'My manual look', notes: 'Keep the exact blue shirt',
    items: [expect.objectContaining({ id: 'shirt-1' })],
  }));
  expect(mockPush).not.toHaveBeenCalled();
});

it('keeps the saved outfit and dialog after a failed preview request, then retries the same ID', async () => {
  mockCreateOutfit.mockResolvedValue({ id: 'saved-1' });
  mockRequestFlatLay.mockRejectedValueOnce(new Error('Could not confirm the request.'));
  await fillDraft();
  const button = await screen.findByRole('button', { name: 'Create flat lay now' });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  await screen.findByRole('alert');
  expect(mockPush).not.toHaveBeenCalled();
  expect(button).toBeEnabled();
  mockRequestFlatLay.mockResolvedValueOnce({ flat_lay_status: 'pending' });
  fireEvent.click(button);
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits?refresh=1'));
  expect(mockRequestFlatLay.mock.calls).toEqual([['saved-1', 'test-token'], ['saved-1', 'test-token']]);
  expect(mockCreateOutfit).toHaveBeenCalledTimes(1);
});

it('shows a server review hold without claiming it queued or letting another request through', async () => {
  mockCreateOutfit.mockResolvedValue({ id: 'saved-1' });
  mockRequestFlatLay.mockResolvedValue({ flat_lay_status: 'failed', request_allowed: false, flat_lay_error: 'This earlier preview needs review. No new credit was used.' });
  await fillDraft();
  const button = await screen.findByRole('button', { name: 'Create flat lay now' });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  expect(await screen.findByRole('alert')).toHaveTextContent('No new credit was used');
  expect(screen.getByRole('button', { name: 'Preview needs review' })).toBeDisabled();
  expect(mockPush).not.toHaveBeenCalled();
  expect(mockToast).not.toHaveBeenCalledWith(expect.objectContaining({ title: 'Flat lay requested' }));
  fireEvent.click(screen.getByRole('button', { name: 'Not right now' }));
  expect(mockPush).toHaveBeenCalledWith('/outfits?refresh=1');
  expect(mockRequestFlatLay).toHaveBeenCalledTimes(1);
});

it('does not sell an upgrade when the balance lookup fails', async () => {
  const { subscriptionService } = await import('@/lib/services/subscriptionService');
  (subscriptionService.getCurrentSubscription as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  mockCreateOutfit.mockResolvedValue({ id: 'saved-1' });
  await fillDraft();
  expect(await screen.findByRole('button', { name: 'Check balance again' })).toBeEnabled();
  expect(screen.queryByRole('link', { name: /Upgrade/ })).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Balance unavailable' })).toBeDisabled();
});
