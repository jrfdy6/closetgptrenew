import type { User } from 'firebase/auth';
import { subscriptionService } from './subscriptionService';

declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;

const originalFetch = global.fetch;
const getIdToken = jest.fn();
const user = { getIdToken } as unknown as User;

beforeEach(() => {
  global.fetch = jest.fn();
  getIdToken.mockReset().mockResolvedValue('firebase-token');
});

afterAll(() => {
  global.fetch = originalFetch;
});

it.each([0, 1])('reads the authenticated balance %i through the uncached same-origin proxy', async remaining => {
  const subscription = { role: 'tier1', status: 'active', flatlays_remaining: remaining };
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => subscription });

  await expect(subscriptionService.getCurrentSubscription(user)).resolves.toEqual(subscription);

  expect(getIdToken).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('/api/payments/subscription/current', {
    cache: 'no-store',
    headers: {
      Authorization: 'Bearer firebase-token',
      'Content-Type': 'application/json',
    },
  });
});

it('does not request a balance for an unauthenticated user', async () => {
  await expect(subscriptionService.getCurrentSubscription(null)).rejects.toThrow('User not authenticated');
  expect(fetch).not.toHaveBeenCalled();
});

it('preserves authentication failure without making a request', async () => {
  getIdToken.mockRejectedValue(new Error('Session expired'));

  await expect(subscriptionService.getCurrentSubscription(user)).rejects.toThrow('Session expired');
  expect(fetch).not.toHaveBeenCalled();
});

it('preserves server error details without inventing a balance or retrying', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ detail: 'Subscription unavailable' }) });

  await expect(subscriptionService.getCurrentSubscription(user)).rejects.toThrow('Subscription unavailable');
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('reports a failed non-JSON response as unavailable', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => { throw new SyntaxError('Invalid JSON'); } });

  await expect(subscriptionService.getCurrentSubscription(user)).rejects.toThrow('Failed to fetch subscription');
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('preserves network failure rather than returning zero credits', async () => {
  (fetch as jest.Mock).mockRejectedValue(new TypeError('Failed to fetch'));

  await expect(subscriptionService.getCurrentSubscription(user)).rejects.toThrow('Failed to fetch');
  expect(fetch).toHaveBeenCalledTimes(1);
});
