import '@testing-library/jest-dom';
import { act, fireEvent, render, screen } from '@testing-library/react';
import Page from './page';
declare const beforeEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
const mockSubscription = jest.fn();
const mockAuth = { user: { uid: 'a' } as { uid: string } | null, loading: false };
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => mockAuth }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
jest.mock('@/lib/services/subscriptionService', () => ({ subscriptionService: { getCurrentSubscription: (...args: unknown[]) => mockSubscription(...args), getTierDisplayName: () => 'Pro' } }));
beforeEach(() => { jest.clearAllMocks(); mockAuth.user = { uid: 'a' }; window.history.replaceState({}, '', '/subscription-success?session_id=fabricated'); });
it('does not treat a checkout URL as payment confirmation', async () => {
  mockSubscription.mockResolvedValue({ role: 'tier1', status: 'active' });
  render(<Page />);
  expect(await screen.findByText(/does not yet show an active paid plan/)).toBeVisible();
  expect(screen.queryByText(/Payment successful/i)).not.toBeInTheDocument();
  expect(screen.getByText(/does not confirm a payment/)).toBeVisible();
});
it('shows only the account status returned by the existing service', async () => {
  mockSubscription.mockResolvedValue({ role: 'tier2', status: 'active' });
  render(<Page />);
  expect(await screen.findByText('Your account currently has the Pro plan active.')).toBeVisible();
});
it('offers a retry after an unavailable response', async () => {
  mockSubscription.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({ role: 'tier2', status: 'trialing' });
  render(<Page />);
  expect(await screen.findByRole('alert')).toHaveTextContent('could not load');
  fireEvent.click(screen.getByRole('button', { name: 'Check again' }));
  expect(await screen.findByText('Your account currently has the Pro plan on trial.')).toBeVisible();
});
it('does not display a previous account response after switching users', async () => {
  let resolve!: (value: unknown) => void;
  mockSubscription.mockImplementationOnce(() => new Promise(done => { resolve = done; })).mockResolvedValue({ role: 'tier1', status: 'active' });
  const { rerender } = render(<Page />);
  mockAuth.user = { uid: 'b' }; rerender(<Page />);
  await screen.findByText(/does not yet show an active paid plan/);
  await act(async () => resolve({ role: 'tier2', status: 'active' }));
  expect(screen.queryByText('Your account currently has the Pro plan active.')).not.toBeInTheDocument();
});
