import { act, renderHook, waitFor } from '@testing-library/react';
import { useGamificationStats } from './useGamificationStats';

declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;

const mockUser = { getIdToken: jest.fn() };
const mockAuth = { user: mockUser as typeof mockUser | null };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => mockAuth }));

const originalFetch = global.fetch;
const stats = {
  xp: 25,
  level: { level: 1, tier: 'Beginner', current_xp: 25, xp_for_next_level: 100, progress_percentage: 25 },
  ai_fit_score: {
    total_score: 20,
    components: {
      feedback: { score: 10, max: 40 },
      consistency: { score: 5, max: 30 },
      confidence: { score: 5, max: 30 },
    },
    explanations: [],
    next_milestone: null,
  },
  tve: {
    total_tve: 5, total_wardrobe_cost: 100, percent_recouped: 5,
    annual_potential_range: { low: 10, high: 20 }, tve_by_category: {}, lowest_progress_category: null,
  },
  badges: [], active_challenges: [], active_challenges_count: 0,
};
const success = (data = stats) => ({ ok: true, json: async () => ({ success: true, data }) });

beforeEach(() => {
  mockAuth.user = mockUser;
  mockUser.getIdToken.mockReset().mockResolvedValue('firebase-token');
  global.fetch = jest.fn();
  jest.spyOn(console, 'error').mockImplementation(() => {});
  jest.spyOn(console, 'log').mockImplementation(() => {});
});

afterEach(() => {
  global.fetch = originalFetch;
  jest.restoreAllMocks();
});

it('keeps loading distinct from data while reading the authenticated same-origin proxy', async () => {
  let resolveResponse!: (value: ReturnType<typeof success>) => void;
  (fetch as jest.Mock).mockImplementation(() => new Promise(resolve => { resolveResponse = resolve; }));
  const { result } = renderHook(useGamificationStats);

  expect(result.current).toMatchObject({ stats: null, loading: true, error: null });
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
  expect(fetch).toHaveBeenCalledWith('/api/gamification/stats', {
    cache: 'no-store',
    headers: { Authorization: 'Bearer firebase-token', 'Content-Type': 'application/json' },
    signal: expect.any(AbortSignal),
  });
  expect(mockUser.getIdToken).toHaveBeenCalledTimes(1);

  await act(async () => resolveResponse(success()));
  expect(result.current).toMatchObject({ stats, loading: false, error: null });
});

it('does not request stats without an authenticated user', async () => {
  mockAuth.user = null;
  const { result } = renderHook(useGamificationStats);

  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.stats).toBeNull();
  expect(fetch).not.toHaveBeenCalled();
});

it('surfaces token failures without making an unauthenticated request', async () => {
  mockUser.getIdToken.mockRejectedValue(new Error('Session expired'));
  const { result } = renderHook(useGamificationStats);

  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current).toMatchObject({ stats: null, error: 'Session expired' });
  expect(fetch).not.toHaveBeenCalled();
});

it.each([
  [{ ok: false, status: 503 }, 'Failed to fetch gamification stats: 503'],
  [{ ok: true, json: async () => ({ success: false, error: 'Stats unavailable' }) }, 'Stats unavailable'],
])('keeps failed responses unavailable without inventing scores', async (response, error) => {
  (fetch as jest.Mock).mockResolvedValue(response);
  const { result } = renderHook(useGamificationStats);

  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current).toMatchObject({ stats: null, error });
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('retains last-known stats on network failure and allows explicit recovery', async () => {
  const updated = { ...stats, xp: 30 };
  (fetch as jest.Mock).mockResolvedValueOnce(success())
    .mockRejectedValueOnce(new TypeError('Failed to fetch'))
    .mockResolvedValueOnce(success(updated));
  const { result } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.stats).toEqual(stats));

  await act(async () => result.current.refetch());
  expect(result.current).toMatchObject({ stats, loading: false, error: 'Failed to fetch' });
  expect(fetch).toHaveBeenCalledTimes(2);

  await act(async () => result.current.refetch());
  expect(result.current).toMatchObject({ stats: updated, loading: false, error: null });
  expect(fetch).toHaveBeenCalledTimes(3);
});

it('preserves timeout completion as unavailable instead of zero stats', async () => {
  (fetch as jest.Mock).mockRejectedValue(new DOMException('Request timed out', 'AbortError'));
  const { result } = renderHook(useGamificationStats);

  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current).toMatchObject({ stats: null, error: null });
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('refreshes through the same proxy on outfit ratings and removes the listener on unmount', async () => {
  (fetch as jest.Mock).mockResolvedValue(success());
  const { result, unmount } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.loading).toBe(false));

  await act(async () => { window.dispatchEvent(new Event('outfitRated')); });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect((fetch as jest.Mock).mock.calls.every(([url]) => url === '/api/gamification/stats')).toBe(true);

  unmount();
  window.dispatchEvent(new Event('outfitRated'));
  expect(fetch).toHaveBeenCalledTimes(2);
});
