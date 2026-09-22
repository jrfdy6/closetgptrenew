declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { act, renderHook, waitFor } from '@testing-library/react';
import { useLayoutEffect } from 'react';
import { useOnboardingDraft } from './useOnboardingDraft';
import type { OnboardingDraft, OnboardingState } from '@/lib/onboarding/types';
const user = { uid: 'draft-owner', getIdToken: jest.fn(async () => 'test-token') };
const answer = (value: string): OnboardingDraft => ({ answers: [{ question_id: 'gender', selected_option: value }], currentQuestionId: 'body_type_male' });
const state = (draft = answer('Male'), revision = 4): OnboardingState => ({ schemaVersion: 1, revision, draft, profileComplete: false, stage: 'style', capsule: { savedCount: 0, usableCount: 0, minimum: 10, hasCoverage: false, missingCategories: ['top', 'bottom', 'shoes'], ready: false }, milestones: { styleCompletedAt: null, capsuleCompletedAt: null, firstOutfitId: null } });
const ack = (value: OnboardingState, status = 200) => ({ ok: status === 200, status, json: async () => ({ success: status === 200, state: { schemaVersion: 1, revision: value.revision, draft: value.draft, milestones: value.milestones } }) });
const reply = (value: OnboardingState, status = 200) => ({ ok: status === 200, status, json: async () => ({ success: status === 200, state: value }) });
let originalFetch: typeof fetch;
let mockFetch: jest.Mock;
beforeEach(() => { originalFetch = global.fetch; mockFetch = jest.fn(); global.fetch = mockFetch; sessionStorage.clear(); });
afterEach(() => { global.fetch = originalFetch; jest.useRealTimers(); });
it('restores saved answers and question before allowing edits', async () => {
  let resolve!: (value: unknown) => void;
  mockFetch.mockReturnValue(new Promise(done => { resolve = done; }));
  const { result } = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  expect(result.current.ready).toBe(false);
  act(() => result.current.updateDraft(answer('Female')));
  expect(result.current.draft.answers).toHaveLength(0);
  await act(async () => resolve(reply(state())));
  expect(result.current.ready).toBe(true);
  expect(result.current.draft).toEqual(answer('Male'));
  expect(mockFetch).toHaveBeenCalledTimes(1);
});
it('keeps authenticated guest mode local and resumes its separate browser draft', async () => {
  const { result, unmount } = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: true }));
  act(() => result.current.updateDraft(answer('Female')));
  await act(async () => { expect(await result.current.flush()).toBe(true); });
  unmount();
  const resumed = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: true }));
  expect(resumed.result.current.draft).toEqual(answer('Female'));
  expect(mockFetch).not.toHaveBeenCalled();
});
it('serializes edits during an in-flight save using its returned revision', async () => {
  let resolvePatch!: (value: unknown) => void;
  mockFetch.mockResolvedValueOnce(reply(state())).mockReturnValueOnce(new Promise(done => { resolvePatch = done; })).mockImplementationOnce(async (_url, options) => ack(state(JSON.parse(options.body).draft, 6)));
  const { result } = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(result.current.ready).toBe(true));
  act(() => result.current.updateDraft(answer('Female')));
  let saving!: Promise<boolean>;
  act(() => { saving = result.current.flush(); });
  await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));
  act(() => result.current.updateDraft(answer('Non-binary')));
  await act(async () => { resolvePatch(ack(state(answer('Female'), 5))); await saving; });
  expect(JSON.parse(mockFetch.mock.calls[2][1].body)).toMatchObject({ expectedRevision: 5, draft: answer('Non-binary') });
  expect(result.current.status).toBe('saved');
});
it('retains unsaved work after network failure and reload, then retries', async () => {
  mockFetch.mockResolvedValueOnce(reply(state())).mockRejectedValueOnce(new Error('Offline'));
  const mounted = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  act(() => mounted.result.current.updateDraft(answer('Female')));
  await act(async () => { expect(await mounted.result.current.flush()).toBe(false); });
  expect(mounted.result.current.status).toBe('error');
  mounted.unmount();
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(reply(state(answer('Female'), 5)));
  const resumed = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(resumed.result.current.ready).toBe(true));
  expect(resumed.result.current.draft).toEqual(answer('Female'));
  await act(async () => { expect(await resumed.result.current.retry()).toBe(true); });
  expect(resumed.result.current.status).toBe('saved');
});
it('preserves local answers on conflict until explicitly loading the newer draft', async () => {
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(ack(state(answer('Non-binary'), 8), 409));
  const { result } = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(result.current.ready).toBe(true));
  act(() => result.current.updateDraft(answer('Female')));
  await act(async () => { expect(await result.current.flush()).toBe(false); });
  expect(result.current.status).toBe('conflict');
  expect(result.current.draft).toEqual(answer('Female'));
  await act(async () => { expect(await result.current.retry()).toBe(false); });
  expect(mockFetch).toHaveBeenCalledTimes(2);
  act(() => result.current.reloadLatest());
  expect(result.current.draft).toEqual(answer('Non-binary'));
  expect(result.current.state?.revision).toBe(8);
  expect(result.current.state?.capsule.minimum).toBe(10);
});
it('ignores a previous account late response after switching users', async () => {
  let firstResponse!: (value: unknown) => void;
  mockFetch.mockReturnValueOnce(new Promise(done => { firstResponse = done; })).mockResolvedValueOnce(reply(state(answer('Female'), 1)));
  const other = { ...user, uid: 'other-owner' };
  const { result, rerender } = renderHook(({ account }) => useOnboardingDraft({ user: account, enabled: true, guest: false }), { initialProps: { account: user } });
  await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));
  rerender({ account: other });
  await waitFor(() => expect(result.current.ready).toBe(true));
  await act(async () => firstResponse(reply(state(answer('Male')))));
  expect(result.current.draft).toEqual(answer('Female'));
});
it('does not modify a completed profile draft without explicit retake', async () => {
  mockFetch.mockResolvedValue(reply({ ...state(), profileComplete: true, stage: 'capsule' }));
  const { result } = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(result.current.ready).toBe(true));
  act(() => result.current.updateDraft(answer('Female')));
  await act(async () => result.current.flush());
  expect(result.current.draft).toEqual(answer('Male'));
  expect(mockFetch).toHaveBeenCalledTimes(1);
});


it('masks an account switch in the first render and blocks actions before passive reset', async () => {
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(reply(state(answer('Non-binary'), 1)));
  const seen: Array<ReturnType<typeof useOnboardingDraft>> = [];
  let earlyFlush: Promise<boolean> | undefined;
  const other = { uid: 'other-owner', getIdToken: jest.fn(async () => 'other-token') };
  const mounted = renderHook(({ account }) => {
    const result = useOnboardingDraft({ user: account, enabled: true, guest: false });
    seen.push(result);
    useLayoutEffect(() => {
      if (account.uid === 'other-owner') {
        result.updateDraft(answer('Female'));
        earlyFlush = result.flush();
        result.reloadLatest();
      }
    }, [account.uid]);
    return result;
  }, { initialProps: { account: user } });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  act(() => mounted.result.current.updateDraft(answer('Female')));
  seen.length = 0;
  mounted.rerender({ account: other });
  expect(seen[0]).toMatchObject({ draft: { answers: [] }, state: null, ready: false, status: 'loading', error: null, conflict: null });
  expect(await earlyFlush).toBe(false);
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  expect(mounted.result.current.draft).toEqual(answer('Non-binary'));
  expect(mockFetch.mock.calls.every(([, options]) => options.method === 'GET')).toBe(true);
  expect(sessionStorage.getItem('easyoutfit:onboarding:other-owner:v1')).toBeNull();
});

it.each([
  { guest: true, enabled: true, account: user },
  { guest: false, enabled: false, account: user },
  { guest: false, enabled: true, account: null },
])('synchronously masks answers when scope changes to %j', async ({ guest, enabled, account }) => {
  mockFetch.mockResolvedValue(reply(state()));
  const seen: Array<ReturnType<typeof useOnboardingDraft>> = [];
  let earlyFlush: Promise<boolean> | undefined;
  const mounted = renderHook((props: { account: typeof user | null; guest: boolean; enabled: boolean; changed: boolean }) => {
    const result = useOnboardingDraft({ user: props.account, guest: props.guest, enabled: props.enabled });
    seen.push(result);
    useLayoutEffect(() => {
      if (props.changed) { result.updateDraft(answer('Female')); earlyFlush = result.flush(); }
    }, [props.changed]);
    return result;
  }, { initialProps: { account: user as typeof user | null, guest: false, enabled: true, changed: false } });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  seen.length = 0;
  mounted.rerender({ account, guest, enabled, changed: true });
  expect(seen[0]).toMatchObject({ draft: { answers: [] }, state: null, ready: false, status: 'loading', error: null, conflict: null });
  expect(await earlyFlush).toBe(false);
  expect(sessionStorage.getItem('easyoutfit:onboarding:guest:v1')).toBeNull();
  expect(mockFetch).toHaveBeenCalledTimes(1);
});

it('does not expose a guest draft when switching into an authenticated account', async () => {
  mockFetch.mockResolvedValue(reply(state()));
  const seen: Array<ReturnType<typeof useOnboardingDraft>> = [];
  const mounted = renderHook(({ guest }) => { const result = useOnboardingDraft({ user, guest, enabled: true }); seen.push(result); return result; }, { initialProps: { guest: true } });
  act(() => mounted.result.current.updateDraft(answer('Female')));
  expect(mounted.result.current.draft).toEqual(answer('Female'));
  seen.length = 0;
  mounted.rerender({ guest: false });
  expect(seen[0]).toMatchObject({ draft: { answers: [] }, state: null, ready: false });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  expect(mounted.result.current.draft).toEqual(answer('Male'));
  expect(JSON.parse(sessionStorage.getItem('easyoutfit:onboarding:guest:v1')!).draft).toEqual(answer('Female'));
});

it('blocks retained callbacks from a previous account even after the new account hydrates', async () => {
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(reply(state(answer('Non-binary'), 1)));
  const other = { ...user, uid: 'other-owner' };
  const mounted = renderHook(({ account }) => useOnboardingDraft({ user: account, enabled: true, guest: false }), { initialProps: { account: user } });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  const previousActions = mounted.result.current;
  mounted.rerender({ account: other });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  await act(async () => {
    previousActions.updateDraft(answer('Female'));
    expect(await previousActions.flush()).toBe(false);
    expect(await previousActions.retry()).toBe(false);
    expect(await previousActions.refresh()).toBeNull();
  });
  expect(mounted.result.current.draft).toEqual(answer('Non-binary'));
  expect(mockFetch).toHaveBeenCalledTimes(2);
});

it('keeps hydration read-only and reconciles verified milestones only on explicit refresh', async () => {
  mockFetch.mockResolvedValue(reply(state()));
  const mounted = renderHook(() => useOnboardingDraft({ user, enabled: true, guest: false }));
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  expect(mockFetch).toHaveBeenNthCalledWith(1, '/api/onboarding', expect.objectContaining({ method: 'GET' }));
  await act(async () => { await mounted.result.current.refresh(); });
  expect(mockFetch).toHaveBeenNthCalledWith(2, '/api/onboarding', expect.objectContaining({ method: 'POST' }));
});

it('stops a previous account save if its token arrives only after switching accounts', async () => {
  let finishToken!: (value: string) => void;
  const first = { uid: 'first-owner', getIdToken: jest.fn().mockResolvedValueOnce('first-token').mockImplementationOnce(() => new Promise(resolve => { finishToken = resolve; })) };
  const second = { uid: 'second-owner', getIdToken: jest.fn().mockResolvedValue('second-token') };
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(reply(state(answer('Non-binary'), 1)));
  const mounted = renderHook(({ account }) => useOnboardingDraft({ user: account, enabled: true, guest: false }), { initialProps: { account: first } });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  act(() => mounted.result.current.updateDraft(answer('Female')));
  let saving!: Promise<boolean>;
  act(() => { saving = mounted.result.current.flush(); });
  mounted.rerender({ account: second });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  await act(async () => { finishToken('late-first-token'); expect(await saving).toBe(false); });
  expect(mounted.result.current.draft).toEqual(answer('Non-binary'));
  expect(mockFetch).toHaveBeenCalledTimes(2);
  expect(mockFetch.mock.calls.every(([, options]) => options.method === 'GET')).toBe(true);
});

it('masks an existing conflict on switch and cannot apply it to the next account', async () => {
  mockFetch.mockResolvedValueOnce(reply(state())).mockResolvedValueOnce(ack(state(answer('Prefer not to say'), 7), 409))
    .mockResolvedValueOnce(reply(state(answer('Non-binary'), 1)));
  const seen: Array<ReturnType<typeof useOnboardingDraft>> = [];
  const mounted = renderHook(({ account }) => { const result = useOnboardingDraft({ user: account, enabled: true, guest: false }); seen.push(result); return result; }, { initialProps: { account: user } });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  act(() => mounted.result.current.updateDraft(answer('Female')));
  await act(async () => { await mounted.result.current.flush(); });
  expect(mounted.result.current.conflict).not.toBeNull();
  const oldReload = mounted.result.current.reloadLatest;
  seen.length = 0;
  mounted.rerender({ account: { ...user, uid: 'other-owner' } });
  expect(seen[0]).toMatchObject({ draft: { answers: [] }, state: null, ready: false, status: 'loading', error: null, conflict: null });
  await waitFor(() => expect(mounted.result.current.ready).toBe(true));
  act(() => oldReload());
  expect(mounted.result.current.draft).toEqual(answer('Non-binary'));
  expect(mounted.result.current.conflict).toBeNull();
  expect(sessionStorage.getItem('easyoutfit:onboarding:other-owner:v1')).toBeNull();
});
