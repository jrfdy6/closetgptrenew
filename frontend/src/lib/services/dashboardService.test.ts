declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
import type { User } from 'firebase/auth';
import { dashboardService } from './dashboardService';

const fetchMock = jest.fn();
const token = 'private-firebase-token';
const getIdToken = jest.fn();
const user = { uid: 'dashboard-user', email: 'private@example.test', getIdToken } as unknown as User;
const profile = { userId: user.uid, user_id: user.uid, firebase_uid: user.uid, stylePreferences: ['Minimalist'] };
const items = Array.from({ length: 10 }, (_, index) => ({
  id: `garment-${index}`, name: `Saved shirt ${index}`, type: 'shirt',
  color: index % 2 ? 'white' : 'navy', style: ['minimalist'], season: ['spring'],
  favorite: index < 2, wearCount: index, imageUrl: `https://private.invalid/item-${index}.png`,
}));
const success = (body: unknown) => ({ ok: true, json: jest.fn().mockResolvedValue(body) });
const loadError = 'Your dashboard could not be loaded. Please try again.';
const originalFetch = global.fetch;
function respond(failingEndpoint?: string, failure?: () => any) {
  fetchMock.mockImplementation(async (url: string) => {
    if (url === failingEndpoint) return failure!();
    if (url === '/api/wardrobe') return success({ success: true, items, count: items.length });
    if (url === '/api/user/profile') return success(profile);
    throw new Error('Unexpected endpoint');
  });
}

describe('dashboard required data requests', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    global.fetch = fetchMock;
    fetchMock.mockReset();
    getIdToken.mockReset().mockResolvedValue(token);
    // Isolate optional insights, keeping real required requests and calculations.
    jest.spyOn(dashboardService as any, 'getSimpleAnalytics').mockResolvedValue({ outfits_worn_this_week: 3 });
    jest.spyOn(dashboardService as any, 'getTrendingStyles').mockResolvedValue({ styles: [] });
    jest.spyOn(dashboardService as any, 'getWardrobeGapsFromBackend').mockResolvedValue([]);
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
    respond();
  });
  afterEach(() => { jest.restoreAllMocks(); jest.useRealTimers(); global.fetch = originalFetch; });

  it('loads authenticated same-origin proxies and preserves ten items and their calculations', async () => {
    const result = await dashboardService.getDashboardData(user);
    expect(fetchMock.mock.calls.map(call => call[0]).sort()).toEqual(['/api/user/profile', '/api/wardrobe']);
    for (const [, options] of fetchMock.mock.calls) {
      expect(options.method).toBe('GET');
      expect(new Headers(options.headers).get('Authorization')).toBe(`Bearer ${token}`);
      expect(options.cache).toBe('no-store');
      expect(options.signal).toBeInstanceOf(AbortSignal);
    }
    expect(result.totalItems).toBe(10);
    expect(result.favorites).toBe(2);
    expect(result.outfitsThisWeek).toBe(3);
    expect(result.colorVariety.current).toBe(2);
    expect(result.topItems).toHaveLength(5);
    expect(result.topItems[0].wearCount).toBe(9);
    expect(jest.getTimerCount()).toBe(0);
    expect(console.log).not.toHaveBeenCalled();
    expect(console.warn).not.toHaveBeenCalled();
    expect(console.error).not.toHaveBeenCalled();
  });
  it('returns zero only for a successful empty wardrobe', async () => {
    respond('/api/wardrobe', () => success({ success: true, items: [], count: 0 }));
    const result = await dashboardService.getDashboardData(user);
    expect(result.totalItems).toBe(0);
    expect(result.favorites).toBe(0);
    expect(result.topItems).toEqual([]);
    expect((dashboardService as any).getWardrobeGapsFromBackend).not.toHaveBeenCalled();
  });
  it.each(['/api/wardrobe', '/api/user/profile'])('rejects network failure on %s instead of returning zero', async endpoint => {
    respond(endpoint, () => { throw new Error(`private transport details ${token}`); });
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    expect(console.error).not.toHaveBeenCalled();
    expect(jest.getTimerCount()).toBe(0);
  });
  it.each(['/api/wardrobe', '/api/user/profile'])('rejects non-OK %s without exposing its body', async endpoint => {
    const bodyReader = jest.fn().mockResolvedValue({ error: token });
    respond(endpoint, () => ({ ok: false, status: 503, json: bodyReader, text: bodyReader }));
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    expect(bodyReader).not.toHaveBeenCalled();
    expect(console.error).not.toHaveBeenCalled();
  });
  it.each(['/api/wardrobe', '/api/user/profile'])('rejects invalid JSON from %s', async endpoint => {
    respond(endpoint, () => ({ ok: true, json: async () => { throw new SyntaxError('Private response body'); } }));
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
  });
  it.each([
    null, {}, { success: false, items: [], count: 0 }, { success: true, count: 0 },
    { success: true, items: {}, count: 0 }, { success: true, items, count: 0 },
    { success: true, items: [null], count: 1 }, { success: true, items: [{}], count: 1 },
  ])('rejects malformed wardrobe data %#', async body => {
    respond('/api/wardrobe', () => success(body));
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
  });
  it.each([
    null, [], {}, { userId: 'different-user' }, { ...profile, user_id: 'different-user' },
    { ...profile, stylePreferences: 'Minimalist' }, { ...profile, preferences: { style: [null] } },
  ])('rejects malformed or conflicting profile data %#', async body => {
    respond('/api/user/profile', () => success(body));
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
  });
  it('rejects an unauthenticated call without making requests', async () => {
    await expect(dashboardService.getDashboardData(null)).rejects.toThrow(loadError);
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('rejects token acquisition failure without exposing authentication details', async () => {
    getIdToken.mockRejectedValue(new Error(`private authentication details ${token}`));
    await expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(console.error).not.toHaveBeenCalled();
  });
  it('rejects a timed-out required request and clears its deadline', async () => {
    fetchMock.mockImplementation((url: string, options: RequestInit) => {
      if (url === '/api/user/profile') return Promise.resolve(success(profile));
      return new Promise((_, reject) => options.signal!.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError'))));
    });
    const assertion = expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    await jest.advanceTimersByTimeAsync(35000);
    await assertion;
    expect(jest.getTimerCount()).toBe(0);
  });
  it('rejects an unresolved token within the profile deadline instead of hanging the dashboard', async () => {
    getIdToken.mockImplementation(() => new Promise(() => {}));
    const assertion = expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    await jest.advanceTimersByTimeAsync(15000);
    await assertion;
    expect(fetchMock).not.toHaveBeenCalled();
    // The independently started wardrobe request also has its own deadline.
    await jest.advanceTimersByTimeAsync(20000);
    expect(jest.getTimerCount()).toBe(0);
  });
  it('does not start a fetch when token acquisition completes after both request deadlines', async () => {
    let resolveToken!: (value: string) => void;
    const pendingToken = new Promise<string>(resolve => { resolveToken = resolve; });
    getIdToken.mockReturnValue(pendingToken);
    const assertion = expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    await jest.advanceTimersByTimeAsync(35000);
    await assertion;
    resolveToken(token);
    await jest.advanceTimersByTimeAsync(0);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(jest.getTimerCount()).toBe(0);
  });
  it('rejects response parsing that outlives the overall deadline', async () => {
    respond('/api/user/profile', () => ({ ok: true, json: () => new Promise(() => {}) }));
    const assertion = expect(dashboardService.getDashboardData(user)).rejects.toThrow(loadError);
    await jest.advanceTimersByTimeAsync(15000);
    await assertion;
    const profileOptions = fetchMock.mock.calls.find(call => call[0] === '/api/user/profile')![1];
    expect(profileOptions.signal.aborted).toBe(true);
    expect(jest.getTimerCount()).toBe(0);
  });
  it('does not replace an earlier ten-item success with zeros when refresh fails', async () => {
    expect((await dashboardService.getDashboardData(user)).totalItems).toBe(10);
    respond('/api/wardrobe', () => ({ ok: false, status: 503 }));
    await expect(dashboardService.getDashboardData(user, true)).rejects.toThrow(loadError);
  });
});
