declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { act, renderHook, waitFor } from '@testing-library/react';
import { useOnboardingState } from './useOnboardingState';
import { deriveOnboardingState } from '@/lib/onboarding/state';

let mockUser: { uid: string; getIdToken: jest.Mock } | null;
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
const state = deriveOnboardingState({ wardrobe: [], outfits: [] });
beforeEach(() => {
  mockUser = { uid: 'first', getIdToken: jest.fn().mockResolvedValue('first-token') };
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ success: true, state }) });
});

it('exposes a load failure separately from an empty capsule and can retry', async () => {
  (fetch as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  const hook = renderHook(() => useOnboardingState());
  await waitFor(() => expect(hook.result.current.loading).toBe(false));
  expect(hook.result.current.state).toBeNull();
  expect(hook.result.current.error).toBeTruthy();
  await act(async () => { await hook.result.current.refresh(); });
  expect(hook.result.current.state).toEqual(state);
  expect(hook.result.current.error).toBeNull();
});

it('does not expose a late response from the previous account', async () => {
  let finishFirst!: (response: any) => void;
  (fetch as jest.Mock).mockImplementationOnce(() => new Promise(resolve => { finishFirst = resolve; }));
  const hook = renderHook(() => useOnboardingState());
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
  mockUser = { uid: 'second', getIdToken: jest.fn().mockResolvedValue('second-token') };
  hook.rerender();
  await waitFor(() => expect(hook.result.current.loading).toBe(false));
  await act(async () => { finishFirst({ ok: true, json: async () => ({ success: true, state: { ...state, revision: 999 } }) }); });
  expect(hook.result.current.state?.revision).toBe(0);
  expect(fetch).toHaveBeenLastCalledWith('/api/onboarding', expect.objectContaining({ headers: { Authorization: 'Bearer second-token' } }));
});

it('masks the previously loaded account on the very first render of an account switch', async () => {
  const seen: Array<ReturnType<typeof useOnboardingState>> = [];
  const hook = renderHook(() => { const result = useOnboardingState(); seen.push(result); return result; });
  await waitFor(() => expect(hook.result.current.state).toEqual(state));
  (fetch as jest.Mock).mockImplementationOnce(() => new Promise(() => {}));
  seen.length = 0;
  mockUser = { uid: 'second', getIdToken: jest.fn().mockResolvedValue('second-token') };
  hook.rerender();
  expect(seen[0]).toMatchObject({ state: null, loading: true, error: null });
  expect(seen.every(result => result.state === null && result.error === null)).toBe(true);
});

it('does not leak the previous account’s error during the first render of a switch', async () => {
  (fetch as jest.Mock).mockRejectedValueOnce(new Error('first account unavailable'));
  const seen: Array<ReturnType<typeof useOnboardingState>> = [];
  const hook = renderHook(() => { const result = useOnboardingState(); seen.push(result); return result; });
  await waitFor(() => expect(hook.result.current.error).toBeTruthy());
  (fetch as jest.Mock).mockImplementationOnce(() => new Promise(() => {}));
  seen.length = 0;
  mockUser = { uid: 'second', getIdToken: jest.fn().mockResolvedValue('second-token') };
  hook.rerender();
  expect(seen[0]).toMatchObject({ state: null, loading: true, error: null });
});

it('masks loaded progress immediately on sign-out, before the cleanup effect', async () => {
  const seen: Array<ReturnType<typeof useOnboardingState>> = [];
  const hook = renderHook(() => { const result = useOnboardingState(); seen.push(result); return result; });
  await waitFor(() => expect(hook.result.current.state).toEqual(state));
  seen.length = 0;
  mockUser = null;
  hook.rerender();
  expect(seen[0]).toMatchObject({ state: null, loading: true, error: null });
  expect(hook.result.current).toMatchObject({ state: null, loading: false, error: null });
});
