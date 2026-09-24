import { act, renderHook, waitFor } from '@testing-library/react';
import { useBadges, useChallenges, useGamificationStats } from './useGamificationStats';

declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;

const mockUser = { uid: 'owner', getIdToken: jest.fn() };
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
  expect(result.current).toMatchObject({ stats: null, error: 'Your progress could not be refreshed. Please try again.' });
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('refreshes through the same proxy on confirmed activity and removes the listener on unmount', async () => {
  (fetch as jest.Mock).mockResolvedValue(success());
  const { result, unmount } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.loading).toBe(false));

  await act(async () => { window.dispatchEvent(new CustomEvent('gamificationActivityChanged', { detail: { uid: 'owner' } })); });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect((fetch as jest.Mock).mock.calls.every(([url]) => url === '/api/gamification/stats')).toBe(true);

  unmount();
  window.dispatchEvent(new CustomEvent('gamificationActivityChanged', { detail: { uid: 'owner' } }));
  expect(fetch).toHaveBeenCalledTimes(2);
});


it('refreshes after a same-account wear receipt and return to the tab, ignoring another account', async () => {
  (fetch as jest.Mock).mockResolvedValue(success());
  const { result } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn', { detail: { uid: 'other' } })); });
  expect(fetch).toHaveBeenCalledTimes(1);
  await act(async () => { window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn', { detail: { uid: 'owner', event_revision: 2, undone: true } })); });
  expect(fetch).toHaveBeenCalledTimes(2);
  Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' });
  await act(async () => { document.dispatchEvent(new Event('visibilitychange')); });
  expect(fetch).toHaveBeenCalledTimes(3);
});

it('refreshes the summary after challenge changes only for the current account', async () => {
  (fetch as jest.Mock).mockResolvedValue(success());
  const { result } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { window.dispatchEvent(new CustomEvent('gamificationActivityChanged', { detail: { uid: 'other' } })); });
  expect(fetch).toHaveBeenCalledTimes(1);
  await act(async () => { window.dispatchEvent(new CustomEvent('gamificationActivityChanged', { detail: { uid: 'owner' } })); });
  expect(fetch).toHaveBeenCalledTimes(2);
});


it('a successful challenge start refreshes the list and summary without emitting a wear receipt', async () => {
  let started = false;
  (fetch as jest.Mock).mockImplementation(async (url: string) => {
    if (url.endsWith('/start')) { started = true; return { ok: true, json: async () => ({ success: true }) }; }
    if (url.endsWith('/stats')) return success({ ...stats, active_challenges_count: started ? 1 : 0 });
    return { ok: true, json: async () => ({ data: { challenges: [] } }) };
  });
  const wear = jest.fn(); window.addEventListener('outfitMarkedAsWorn', wear);
  const { result } = renderHook(() => ({ summary: useGamificationStats(), challenges: useChallenges() }));
  await waitFor(() => expect(result.current.summary.loading || result.current.challenges.loading).toBe(false));
  await act(async () => { expect(await result.current.challenges.startChallenge('thirty-wears')).toBe(true); });
  await waitFor(() => expect(result.current.summary.stats?.active_challenges_count).toBe(1));
  expect(wear).not.toHaveBeenCalled();
  window.removeEventListener('outfitMarkedAsWorn', wear);
});

it('loads completed history while keeping its failure separate from active challenges', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.endsWith('/history')
    ? { ok: false, status: 503 }
    : { ok: true, json: async () => ({ success: true, data: { challenges: [{ challenge_id: 'one', status: 'in_progress' }] } }) });
  const { result } = renderHook(useChallenges);
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.error).toBeNull();
  expect(result.current.activeChallenges).toHaveLength(1);
  expect(result.current.historyError).toMatch(/could not be loaded/);
  expect(result.current.completedChallenges).toEqual([]);
});

it('uses the history response and excludes expired instances from completed accomplishments', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, data: { challenges: [
    { challenge_id: 'done', status: 'completed', instance_id: 'week-1' }, { challenge_id: 'old', status: 'expired' },
  ] } }) });
  const { result } = renderHook(useChallenges);
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.completedChallenges.map(c => c.challenge_id)).toEqual(['done']);
  expect((fetch as jest.Mock).mock.calls.some(([url, options]) => url.endsWith('/history') && options.cache === 'no-store')).toBe(true);
});

it('rejects an HTTP-success application failure when starting a challenge', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => ({ ok: true, json: async () => url.endsWith('/start') ? { success: false } : { success: true, data: { challenges: [] } } }));
  const { result } = renderHook(useChallenges);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { expect(await result.current.startChallenge('one')).toBe(false); });
});

it('does not turn a malformed success payload into level one and zero counts', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, data: {} }) });
  const { result } = renderHook(useGamificationStats);
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.stats).toBeNull();
  expect(result.current.error).toMatch(/could not be loaded/);
});

it('refreshes summary after a confirmed badge unlock without recursively re-reading badges', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.endsWith('/badges')
    ? { ok: true, json: async () => ({ success: true, data: { badges: [{ id: 'starter_closet' }], newly_unlocked: ['starter_closet'] } }) }
    : success());
  const { result } = renderHook(() => ({ summary: useGamificationStats(), badges: useBadges() }));
  await waitFor(() => expect(result.current.summary.loading || result.current.badges.loading).toBe(false));
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.endsWith('/badges'))).toHaveLength(1);
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.endsWith('/stats'))).toHaveLength(2);
});

it('releases an unconfirmed challenge start after the request deadline without claiming success', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string, options: RequestInit) => {
    if (url.endsWith('/start')) return new Promise((_resolve, reject) => options.signal?.addEventListener('abort', () => reject(new DOMException('Timed out', 'AbortError'))));
    return { ok: true, json: async () => ({ success: true, data: { challenges: [] } }) };
  });
  const { result } = renderHook(useChallenges);
  await waitFor(() => expect(result.current.loading).toBe(false));
  jest.useFakeTimers();
  try {
    let started!: Promise<boolean | undefined>;
    await act(async () => { started = result.current.startChallenge('one'); });
    await act(async () => { jest.advanceTimersByTime(30000); expect(await started).toBe(false); });
  } finally { jest.useRealTimers(); }
});
