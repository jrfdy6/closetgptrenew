declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { GET, POST, PATCH } from './route';
import { getFirebaseAdminAuth } from '@/lib/server/firebaseAdmin';
import { DraftRevisionConflict, readOnboardingState, reconcileOnboardingState, saveOnboardingDraft } from '@/lib/server/onboarding';
import { deriveOnboardingState } from '@/lib/onboarding/state';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
jest.mock('@/lib/server/firebaseAdmin', () => ({ getFirebaseAdminAuth: jest.fn(), getFirebaseAdminDb: () => 'injected-test-store' }));
jest.mock('@/lib/server/onboarding', () => ({ ...jest.requireActual('@/lib/server/onboarding'), readOnboardingState: jest.fn(), reconcileOnboardingState: jest.fn(), saveOnboardingDraft: jest.fn() }));
const verify = jest.fn();
const state = deriveOnboardingState({ wardrobe: [], outfits: [] });
const draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }], currentQuestionId: 'body_type_male' };
const request = (body?: unknown, token: string | null = 'signed-user-token') => ({ headers: new Headers(token ? { authorization: `Bearer ${token}` } : {}), json: async () => body }) as Request;

beforeEach(() => {
  jest.clearAllMocks();
  (getFirebaseAdminAuth as jest.Mock).mockReturnValue({ verifyIdToken: verify });
  verify.mockResolvedValue({ uid: 'verified-user' });
  (readOnboardingState as jest.Mock).mockResolvedValue(state);
  (reconcileOnboardingState as jest.Mock).mockResolvedValue(state);
  (saveOnboardingDraft as jest.Mock).mockResolvedValue({ ...state, revision: 1, draft });
});

it('verifies a real token and never trusts a supplied account ID', async () => {
  const response = await PATCH(request({ expectedRevision: 0, draft, userId: 'another-user' }));
  expect(response.status).toBe(200);
  expect(verify).toHaveBeenCalledWith('signed-user-token', true);
  expect(saveOnboardingDraft).toHaveBeenCalledWith('injected-test-store', 'verified-user', 0, draft);
});

it('reconciles milestones solely from the verified account, ignoring client completion claims', async () => {
  const response = await POST(request({ userId: 'foreign', capsuleCompletedAt: 'forged', firstOutfitId: 'forged' }));
  expect(response.status).toBe(200);
  expect(reconcileOnboardingState).toHaveBeenCalledWith('injected-test-store', 'verified-user');
  expect(await response.json()).toEqual({ success: true, state });
});

it('rejects unauthenticated and invalid tokens without reading private state', async () => {
  expect((await GET(request(undefined, null))).status).toBe(401);
  expect((await POST(request(undefined, null))).status).toBe(401);
  verify.mockRejectedValue(new Error('invalid token'));
  expect((await GET(request(undefined, 'test'))).status).toBe(401);
  expect(readOnboardingState).not.toHaveBeenCalled();
  expect(reconcileOnboardingState).not.toHaveBeenCalled();
});

it('returns one uncached state envelope shared by load, save and guest transfer', async () => {
  const response = await GET(request());
  expect(await response.json()).toEqual({ success: true, state });
  expect((response.headers as unknown as Record<string, string>)['Cache-Control']).toBe('private, no-store');
});

it('returns the newer draft on stale revision without declaring success', async () => {
  (saveOnboardingDraft as jest.Mock).mockRejectedValue(new DraftRevisionConflict({ ...state, revision: 4 }));
  const response = await PATCH(request({ expectedRevision: 2, draft }));
  expect(response.status).toBe(409);
  expect(await response.json()).toMatchObject({ success: false, code: 'revision_conflict', state: { revision: 4 } });
});

it('fails truthfully on storage failure instead of returning an empty or successful state', async () => {
  (readOnboardingState as jest.Mock).mockRejectedValue(new Error('offline'));
  (saveOnboardingDraft as jest.Mock).mockRejectedValue(new Error('offline'));
  (reconcileOnboardingState as jest.Mock).mockRejectedValue(new Error('offline'));
  expect((await GET(request())).status).toBe(503);
  expect((await POST(request())).status).toBe(503);
  expect((await PATCH(request({ expectedRevision: 0, draft }))).status).toBe(503);
});

it.each([{}, { expectedRevision: -1, draft }, { expectedRevision: 0, draft: { answers: 'invalid' } }])('rejects invalid patch %j', async body => {
  expect((await PATCH(request(body))).status).toBe(422);
  expect(saveOnboardingDraft).not.toHaveBeenCalled();
});
