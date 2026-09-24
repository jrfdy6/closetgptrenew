declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import GuidedUploadWizard from './GuidedUploadWizard';
import { evaluateCapsule } from '@/lib/onboarding/state';
let mockItems: any[] = [];
let mockNext: any[] = [];
let mockFailure = false;
const mockUser = { uid: 'owner', getIdToken: async () => 'token' };
const mockRefresh = jest.fn(async () => ({ capsule: evaluateCapsule(mockItems) }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser }) }));
jest.mock('@/lib/hooks/useOnboardingState', () => ({ useOnboardingState: () => ({ state: { capsule: evaluateCapsule(mockItems) }, loading: false, error: null, refresh: mockRefresh }) }));
jest.mock('./BatchImageUpload', () => ({ __esModule: true, default: ({ onItemSaved }: any) => <button onClick={() => { mockItems = [...mockItems, ...mockNext]; mockNext.forEach(item => { void onItemSaved(item); }); }}>Save next batch</button> }));
const garment = (id: number, type: string, extra = {}) => ({ id: `item-${id}`, userId: 'owner', name: `Garment ${id}`, imageUrl: `https://example.test/${id}.jpg`, type, ...extra });
const fullCapsule = () => [garment(0, 'shirt'), garment(1, 'pants'), garment(2, 'shoes'), ...Array.from({ length: 7 }, (_, i) => garment(i + 3, 'shirt'))];
let previousFetch: typeof fetch;
let mockFetch: jest.Mock;
beforeEach(() => {
  previousFetch = global.fetch; mockItems = []; mockNext = []; mockFailure = false; mockRefresh.mockClear();
  mockFetch = jest.fn(async (url, options) => {
    if (options?.method === 'PUT') {
      const type = JSON.parse(options.body).type;
      mockItems = mockItems.map(item => url.endsWith(`/${item.id}`) ? { ...item, type } : item);
      return { ok: true, json: async () => ({ success: true }) };
    }
    if (options?.method === 'POST') return { ok: true, json: async () => ({ success: true }) };
    return { ok: !mockFailure, json: async () => ({ success: !mockFailure, items: mockFailure ? [] : mockItems }) };
  });
  global.fetch = mockFetch;
});
afterEach(() => { global.fetch = previousFetch; });
it('loads four saved items after return and adds six acknowledged items without auto advancing', async () => {
  mockItems = fullCapsule().slice(0, 4);
  const complete = jest.fn();
  const first = render(<GuidedUploadWizard userId="owner" onComplete={complete} />);
  await screen.findByText('4 of 10 capsule items saved'); first.unmount();
  render(<GuidedUploadWizard userId="owner" onComplete={complete} />);
  await screen.findByText('4 of 10 capsule items saved');
  mockNext = fullCapsule().slice(4);
  fireEvent.click(screen.getByRole('button', { name: 'Save next batch' }));
  await screen.findByText('10 of 10 capsule items saved');
  expect(complete).not.toHaveBeenCalled();
  const button = screen.getByRole('button', { name: 'Continue to my first look' });
  await waitFor(() => expect(button).toBeEnabled()); fireEvent.click(button);
  await waitFor(() => expect(complete).toHaveBeenCalledWith(10));
});
it('keeps wardrobe load failure distinct from a zero count and supports retry', async () => {
  mockFailure = true;
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be loaded');
  expect(screen.queryByText('0 of 10 capsule items saved')).not.toBeInTheDocument();
  mockFailure = false; mockItems = fullCapsule().slice(0, 4);
  fireEvent.click(screen.getByRole('button', { name: 'Retry loading capsule' }));
  await screen.findByText('4 of 10 capsule items saved');
});
it('ten shirts show missing coverage and category corrections change readiness', async () => {
  mockItems = Array.from({ length: 10 }, (_, i) => garment(i, 'shirt'));
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText('10 of 10 capsule items saved');
  expect(screen.getByText(/Still needed: shoes, bottom or one-piece/)).toBeVisible();
  expect(screen.getByRole('button', { name: 'Continue to my first look' })).toBeDisabled();
  fireEvent.change(screen.getAllByRole('combobox')[0], { target: { value: 'shoes' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save category' }));
  await waitFor(() => expect(mockItems[0].type).toBe('shoes'));
  await waitFor(() => expect(screen.queryByRole('button', { name: 'Saving category…' })).not.toBeInTheDocument());
  fireEvent.change(screen.getAllByRole('combobox')[1], { target: { value: 'bottom' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save category' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Continue to my first look' })).toBeEnabled());
  expect(mockFetch.mock.calls.filter(([, options]) => options?.method === 'PUT').map(([, options]) => JSON.parse(options.body))).toEqual([{ type: 'shoes' }, { type: 'pants' }]);
});
it('one-piece plus shoes provides coverage without a top, bottom or jacket quota', async () => {
  mockItems = [garment(0, 'shoes'), ...Array.from({ length: 9 }, (_, i) => garment(i + 1, 'dress'))];
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText('10 of 10 capsule items saved');
  expect(screen.getByText('Your essentials are covered')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Continue to my first look' })).toBeEnabled();
});
it('duplicate IDs and image identities cannot inflate acknowledged inventory', async () => {
  mockItems = [...fullCapsule().slice(0, 9), garment(9, 'shirt', { imageUrl: 'https://example.test/0.jpg' }), garment(0, 'shirt')];
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText('9 of 10 capsule items saved');
  expect(screen.getByText(/Repeated photos/)).toBeVisible();
  expect(screen.getByRole('button', { name: 'Continue to my first look' })).toBeDisabled();
});
it('pending and failed cutouts keep originals usable, with selective protected retry', async () => {
  mockItems = fullCapsule();
  mockItems[0] = { ...mockItems[0], processing_status: 'failed', processing_retryable: true, processing_retry_action: 'retry_item', processing_attempt_id: 'terminal-a' };
  mockItems[1] = { ...mockItems[1], processing_status: 'pending' };
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText('10 of 10 capsule items saved');
  expect(screen.getByText('Original saved. Cutout is queued.')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Continue to my first look' })).toBeEnabled();
  fireEvent.click(screen.getByRole('button', { name: 'Retry cutout' }));
  await waitFor(() => expect(mockFetch).toHaveBeenCalledWith('/api/wardrobe/item-0/retry-processing', expect.objectContaining({ method: 'POST', body: JSON.stringify({ expected_attempt_id: 'terminal-a' }) })));
});
it('invalid-photo failures show replacement guidance instead of a futile retry', async () => {
  mockItems = [garment(0, 'shirt', { processing_status: 'failed', processing_retry_action: 'replace_photo', processing_retryable: false })];
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText(/Add a clearer replacement photo/);
  expect(screen.queryByRole('button', { name: 'Retry cutout' })).not.toBeInTheDocument();
});
it('queued analysis is saved but does not count until category is known', async () => {
  mockItems = [garment(0, 'unknown', { processing_status: 'codex_pending' })];
  render(<GuidedUploadWizard userId="owner" onComplete={jest.fn()} />);
  await screen.findByText('0 of 10 capsule items saved');
  expect(screen.getByText('Photo saved. Item details are being identified.')).toBeVisible();
});
it('keeps Continue pending until the completion acknowledgment and displays its failure', async () => {
  mockItems = fullCapsule();
  let rejectCompletion: (error: Error) => void = () => {};
  const complete = jest.fn(() => new Promise<void>((_resolve, reject) => { rejectCompletion = reject; }));
  render(<GuidedUploadWizard userId="owner" onComplete={complete} />);
  await screen.findByText('10 of 10 capsule items saved');
  const button = screen.getByRole('button', { name: 'Continue to my first look' });
  fireEvent.click(button);
  await waitFor(() => expect(complete).toHaveBeenCalled());
  expect(button).toBeDisabled();
  rejectCompletion(new Error('Your progress could not be confirmed. Please retry.'));
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be confirmed');
  await waitFor(() => expect(button).toBeEnabled());
});
