// Keep Jest types local; Cypress also declares global test functions.
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { act, renderHook, waitFor } from '@testing-library/react';
import { useOutfits } from './useOutfits_proper';

const mockUser = { uid: 'user-1', getIdToken: jest.fn().mockResolvedValue('test-token') };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));

const draft = { name: 'Manual pair', occasion: 'Casual', style: 'Classic', user_id: 'user-1', items: [] };
let createStatus: number;
let createPayload: unknown;

beforeEach(() => {
  jest.spyOn(console, 'log').mockImplementation(() => {});
  createStatus = 200;
  createPayload = { outfit_id: 'saved-1' };
  global.fetch = jest.fn(async (url: string, options?: RequestInit) => {
    const body = options?.method === 'POST' ? createPayload : url.includes('/outfit-stats/') ? { success: true, data: {} } : { outfits: [] };
    const status = options?.method === 'POST' ? createStatus : 200;
    return { ok: status < 400, status, json: async () => body };
  }) as jest.Mock;
});
afterEach(() => { jest.restoreAllMocks(); });

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
