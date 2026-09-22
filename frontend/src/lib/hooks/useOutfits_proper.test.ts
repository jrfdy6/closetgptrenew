// Keep Jest types local; Cypress also declares global test functions.
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { act, renderHook, waitFor } from '@testing-library/react';
import { useOutfits } from './useOutfits_proper';

let mockUser: { uid: string; getIdToken: jest.Mock } | null;
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));

const draft = { name: 'Manual pair', occasion: 'Casual', style: 'Classic', user_id: 'user-1', items: [] };
let createStatus: number;
let createPayload: unknown;

beforeEach(() => {
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});
  jest.spyOn(console, 'warn').mockImplementation(() => {});
  mockUser = { uid: 'user-1', getIdToken: jest.fn().mockResolvedValue('test-token') };
  sessionStorage.clear();
  createStatus = 200;
  createPayload = { outfit_id: 'saved-1' };
  global.fetch = jest.fn(async (url: string, options?: RequestInit) => {
    const body = options?.method === 'POST' ? createPayload : url.includes('/outfit-stats/') ? { success: true, data: {} } : { outfits: [] };
    const status = options?.method === 'POST' ? createStatus : 200;
    return { ok: status < 400, status, json: async () => body };
  }) as jest.Mock;
});
afterEach(() => { jest.restoreAllMocks(); jest.useRealTimers(); });

it('returns the same normalized created outfit that it adds to the list', async () => {
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.loading).toBe(false));
  let created: unknown;
  await act(async () => { created = await result.current.createOutfit(draft); });
  expect(created).toMatchObject({ ...draft, id: 'saved-1' });
  expect(result.current.outfits).toEqual([created]);
});

it.each([503, 200])('retains prior outfits and reports a local create failure for status %s without an ID', async status => {
  createStatus = status;
  createPayload = { error: 'Save unavailable' };
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { result.current.addNewOutfit({ ...draft, id: 'prior-1' } as any); });
  await act(async () => { expect(await result.current.createOutfit(draft)).toBeNull(); });
  expect(result.current.outfits.map(outfit => outfit.id)).toEqual(['prior-1']);
  expect(result.current.error).toBeNull();
  expect(result.current.mutationErrors.create).toBeTruthy();
  expect(result.current.pendingMutations).toEqual([]);
});

const response = (body: unknown, status = 200) => ({ ok: status < 400, status, json: async () => body });
const savedLook = { ...draft, id: 'saved-1', isFavorite: false, wearCount: 2 };
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>(done => { resolve = done; });
  return { promise, resolve };
}

it('exposes the first list failure and never schedules background retries', async () => {
  jest.useFakeTimers();
  (fetch as jest.Mock).mockImplementation(async (url: string) => response(url.includes('/outfit-stats/') ? {} : { error: 'Unavailable' }, url.includes('/outfit-stats/') ? 200 : 503));
  const { result } = renderHook(useOutfits);
  await act(async () => {});
  expect(result.current.error).toMatch(/saved outfits could not be loaded/);
  expect(result.current.loading).toBe(false);
  await act(async () => { jest.advanceTimersByTime(20000); });
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.startsWith('/api/outfits?'))).toHaveLength(1);
  (fetch as jest.Mock).mockImplementation(async (url: string) => response(url.includes('/outfit-stats/') ? {} : { outfits: [savedLook] }));
  await act(async () => { await result.current.refresh(); });
  expect(result.current.error).toBeNull();
  expect(result.current.outfits.map(look => look.id)).toEqual(['saved-1']);
});

it('rejects malformed successful list payloads without discarding previously saved looks', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => response(url.includes('/outfit-stats/') ? {} : { outfits: [savedLook] }));
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(1));
  (fetch as jest.Mock).mockImplementation(async () => response({ success: false }));
  await act(async () => { await result.current.fetchOutfits(); });
  expect(result.current.outfits[0].id).toBe('saved-1');
  expect(result.current.error).toBeTruthy();
});

it('does not let an older filter response replace the newest list', async () => {
  const old = deferred<ReturnType<typeof response>>();
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/outfit-stats/') ? response({}) : url.includes('occasion=Travel') ? response({ outfits: [{ ...savedLook, name: 'New filter' }] }) : old.promise);
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(fetch).toHaveBeenCalled());
  await act(async () => { await result.current.fetchOutfits({ occasion: 'Travel' }); });
  expect(result.current.outfits[0].name).toBe('New filter');
  await act(async () => { old.resolve(response({ outfits: [{ ...savedLook, name: 'Stale filter' }] })); });
  expect(result.current.outfits[0].name).toBe('New filter');
});

it('hides previous account rows and discards its pending list and stats responses', async () => {
  const oldList = deferred<ReturnType<typeof response>>();
  const oldStats = deferred<ReturnType<typeof response>>();
  const newList = deferred<ReturnType<typeof response>>();
  (fetch as jest.Mock).mockImplementation(async (url: string, options: RequestInit) => {
    const otherUser = (options.headers as Record<string, string>).Authorization === 'Bearer other-token';
    if (url.includes('/outfit-stats/')) return otherUser ? response({ total: 22 }) : oldStats.promise;
    return otherUser ? newList.promise : oldList.promise;
  });
  const { result, rerender } = renderHook(useOutfits);
  await act(async () => { result.current.addNewOutfit(savedLook as any); });
  expect(result.current.outfits).toHaveLength(1);
  mockUser = { uid: 'user-2', getIdToken: jest.fn().mockResolvedValue('other-token') };
  rerender();
  expect(result.current.outfits).toEqual([]);
  await act(async () => {
    oldList.resolve(response({ outfits: [{ ...savedLook, name: 'Private previous look' }] }));
    oldStats.resolve(response({ total: 99 }));
  });
  expect(result.current.outfits).toEqual([]);
  expect(result.current.stats).toEqual({ total: 22 });
  await act(async () => { newList.resolve(response({ outfits: [{ ...savedLook, user_id: 'user-2', name: 'Current look' }] })); });
  expect(result.current.outfits[0].name).toBe('Current look');
  mockUser = null;
  rerender();
  expect(result.current.outfits).toEqual([]);
  expect(result.current.stats).toBeNull();
});

it('does not apply a delayed favorite acknowledgement to the next account', async () => {
  const pending = deferred<ReturnType<typeof response>>();
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/favorite') ? pending.promise : response(url.includes('/outfit-stats/') ? {} : { outfits: [savedLook] }));
  const { result, rerender } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(1));
  let mutation!: Promise<boolean>;
  await act(async () => { mutation = result.current.toggleFavorite('saved-1', true); });
  mockUser = { uid: 'user-2', getIdToken: jest.fn().mockResolvedValue('other-token') };
  rerender();
  await waitFor(() => expect(result.current.outfits).toHaveLength(1));
  await act(async () => { pending.resolve(response({ isFavorite: true })); expect(await mutation).toBe(false); });
  expect(result.current.outfits[0].isFavorite).toBe(false);
  expect(result.current.pendingMutations).toEqual([]);
});

it('does not dispatch a mutation after its pending token resolves for a departed account', async () => {
  (fetch as jest.Mock).mockImplementation(async (url: string) => response(url.includes('/outfit-stats/') ? {} : { outfits: [savedLook] }));
  const { result, rerender } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(1));
  const token = deferred<string>();
  mockUser!.getIdToken.mockReturnValue(token.promise);
  let mutation!: Promise<boolean>;
  await act(async () => { mutation = result.current.toggleFavorite('saved-1', true); });
  mockUser = { uid: 'user-2', getIdToken: jest.fn().mockResolvedValue('other-token') };
  rerender();
  await act(async () => { token.resolve('old-token'); expect(await mutation).toBe(false); });
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.includes('/favorite'))).toHaveLength(0);
});

it('retries a lost wear acknowledgement with the same key and uses authoritative totals', async () => {
  let wearAttempts = 0;
  (fetch as jest.Mock).mockImplementation(async (url: string) => {
    if (url.endsWith('/worn')) {
      wearAttempts += 1;
      if (wearAttempts === 1) throw new Error('Response lost');
      return response({ success: true, outfit_id: 'saved-1', event_id: 'event-1', wear_count: 8, last_worn: 1790100000000 });
    }
    return response(url.includes('/outfit-stats/') ? {} : { outfits: [savedLook] });
  });
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(1));
  await act(async () => { expect(await result.current.markAsWorn('saved-1')).toBe(false); });
  expect(result.current.outfits[0].wearCount).toBe(2);
  await act(async () => { expect(await result.current.markAsWorn('saved-1')).toBe(true); });
  const requests = (fetch as jest.Mock).mock.calls.filter(([url]) => url.endsWith('/worn')).map(([, options]) => JSON.parse(options.body));
  expect(requests[0].idempotency_key).toBe(requests[1].idempotency_key);
  expect(result.current.outfits[0].wearCount).toBe(8);
  expect(result.current.outfits[0].lastWorn).toBe(1790100000000);
  expect(sessionStorage.getItem('easyoutfit:pending-wear:v1:user-1:saved-1')).toBeNull();
});

it('retains the first page after a failed next page and permits a bounded explicit retry', async () => {
  const firstPage = Array.from({ length: 50 }, (_, index) => ({ ...savedLook, id: `look-${index}` }));
  const pending = deferred<ReturnType<typeof response>>();
  let nextPage: () => Promise<ReturnType<typeof response>> = () => pending.promise;
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/outfit-stats/') ? response({}) : url.includes('offset=50') ? nextPage() : response({ outfits: firstPage }));
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(50));
  let loading!: Promise<void>;
  await act(async () => { loading = result.current.loadMoreOutfits(); void result.current.loadMoreOutfits(); });
  expect((fetch as jest.Mock).mock.calls.filter(([url]) => url.includes('offset=50'))).toHaveLength(1);
  await act(async () => { pending.resolve(response({ error: 'Unavailable' }, 503)); await loading; });
  expect(result.current.outfits).toHaveLength(50);
  expect(result.current.error).toMatch(/More saved outfits could not be loaded/);
  expect(result.current.hasMore).toBe(true);
  nextPage = async () => response({ outfits: [{ ...savedLook, id: 'look-50' }] });
  await act(async () => { await result.current.loadMoreOutfits(); });
  expect(result.current.outfits).toHaveLength(51);
  expect(result.current.error).toBeNull();
  expect(result.current.hasMore).toBe(false);
});

it('discards a pending next page when a new filter becomes current', async () => {
  const firstPage = Array.from({ length: 50 }, (_, index) => ({ ...savedLook, id: `look-${index}` }));
  const pending = deferred<ReturnType<typeof response>>();
  (fetch as jest.Mock).mockImplementation(async (url: string) => url.includes('/outfit-stats/') ? response({}) : url.includes('occasion=Travel') ? response({ outfits: [{ ...savedLook, id: 'travel' }] }) : url.includes('offset=50') ? pending.promise : response({ outfits: firstPage }));
  const { result } = renderHook(useOutfits);
  await waitFor(() => expect(result.current.outfits).toHaveLength(50));
  let loading!: Promise<void>;
  await act(async () => { loading = result.current.loadMoreOutfits(); });
  await act(async () => { await result.current.fetchOutfits({ occasion: 'Travel' }); });
  await act(async () => { pending.resolve(response({ outfits: [{ ...savedLook, id: 'stale-page' }] })); await loading; });
  expect(result.current.outfits.map(look => look.id)).toEqual(['travel']);
  expect(result.current.loadingMore).toBe(false);
});
