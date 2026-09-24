import { act, render, screen } from '@testing-library/react';
import PremiumTeaser from './PremiumTeaser';
import { subscriptionService } from '@/lib/services/subscriptionService';

jest.mock('next/navigation', () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: { uid: 'owner' } }) }));
jest.mock('@/lib/services/subscriptionService', () => ({ subscriptionService: { getCurrentSubscription: jest.fn(), createCheckoutSession: jest.fn() } }));

beforeEach(() => localStorage.clear());

it.each(['tier2', 'tier3', 'pro', 'premium'])('does not offer the teaser to role %s', async role => {
  jest.mocked(subscriptionService.getCurrentSubscription).mockResolvedValue({ role, status: 'active', flatlays_remaining: 1 });
  await act(async () => { render(<PremiumTeaser variant="compact" showSocialProof={false} />); });
  expect(screen.queryByText('Unlock Premium Features')).not.toBeInTheDocument();
});

it('retains the teaser for the free role', async () => {
  jest.mocked(subscriptionService.getCurrentSubscription).mockResolvedValue({ role: 'tier1', status: 'active', flatlays_remaining: 1 });
  render(<PremiumTeaser variant="compact" showSocialProof={false} />);
  expect(await screen.findByText('Unlock Premium Features')).toBeVisible();
});

it('keeps product benefits without fabricated users, upgrades, or testimonials', async () => {
  jest.mocked(subscriptionService.getCurrentSubscription).mockResolvedValue({ role: 'tier1', status: 'active', flatlays_remaining: 1 });
  render(<PremiumTeaser showSocialProof />);
  expect(await screen.findByText('Advanced Analytics')).toBeInTheDocument();
  expect(screen.queryByText(/Premium Users|joined today|Sarah M\.|Alex T\.|Jordan L\./)).not.toBeInTheDocument();
});
