declare const beforeEach: jest.Lifecycle;
declare const describe: jest.Describe;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import type { NextRequest } from 'next/server';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) } }));
const mockVerify = jest.fn();
const mockTransaction = jest.fn();
const mockSet = jest.fn();
const mockDoc = jest.fn();
let stored: Record<string, any>;
jest.mock('@/lib/server/firebaseAdmin', () => ({
  getFirebaseAdminAuth: () => ({ verifyIdToken: mockVerify }),
  getFirebaseAdminDb: () => ({ collection: () => ({ doc: mockDoc }), runTransaction: mockTransaction }),
}));
function payload(gender = 'Male') {
  return { answers: fullQuizQuestions(gender).map(question => ({ question_id: question.id, selected_option: question.id === 'gender' ? gender : question.options?.[0] || 'No' })), stylePreferences: ['Minimalist'] };
}
function request(body: unknown, token = 'verified-token'): NextRequest {
  return { headers: new Headers(token ? { authorization: `Bearer ${token}` } : {}), json: async () => body } as NextRequest;
}
beforeEach(() => {
  jest.clearAllMocks();
  stored = {};
  global.fetch = jest.fn().mockRejectedValue(new Error('backend unavailable'));
  mockVerify.mockResolvedValue({ uid: 'account-a', email: 'a@example.test', name: 'Alex Example' });
  mockDoc.mockReturnValue('account-a-reference');
  mockTransaction.mockImplementation(async work => work({ get: async () => ({ data: () => stored }), set: mockSet }));
});

it('requires a verified Authorization token, never trusting a body token', async () => {
  expect((await POST(request({ ...payload(), token: 'unsigned.body.token' }, ''))).status).toBe(401);
  expect(mockVerify).not.toHaveBeenCalled();
  mockVerify.mockRejectedValue(Object.assign(new Error('invalid signature'), { code: 'auth/argument-error' }));
  expect((await POST(request(payload()))).status).toBe(401);
  expect(mockTransaction).not.toHaveBeenCalled();
});
it('rejects a mismatched identity before reading or saving a profile', async () => {
  expect((await POST(request({ ...payload(), userId: 'account-b' }))).status).toBe(403);
  expect(mockDoc).not.toHaveBeenCalled();
});
it.each([{ guest: true }, { mode: 'guest' }, { isGuestFlow: true }, { guest: '1' }])('rejects guest write intent even with a valid token: %j', async flag => {
  expect((await POST(request({ ...payload(), ...flag }))).status).toBe(403);
  expect(mockSet).not.toHaveBeenCalled();
});
it.each(['Male', 'Female', 'Non-binary', 'Prefer not to say'])('accepts the full unchanged %s questionnaire and preserves entered names', async gender => {
  stored = { name: 'email-prefix', created_at: 100, measurements: { customFit: 'saved' } };
  const result = await POST(request(payload(gender)));
  expect(result.status).toBe(200);
  expect(await result.json()).toMatchObject({ success: true, persisted: true });
  expect(mockDoc).toHaveBeenCalledWith('account-a');
  const update = mockSet.mock.calls[0][1];
  expect(update).toMatchObject({ name: 'Alex Example', email: 'a@example.test', userId: 'account-a', created_at: 100, measurements: { customFit: 'saved' } });
  expect(update.styleQuizCompletedAt).toEqual(expect.any(Number));
  expect(update).not.toHaveProperty('onboardingCompleted');
  expect(fetch).not.toHaveBeenCalled();
});
it.each(['Male', 'Female', 'Non-binary', 'Prefer not to say'])('does not falsely complete a short guest %s quiz', async gender => {
  const body = payload(gender);
  body.answers = body.answers.filter(answer => !answer.question_id.startsWith('category_spend_'));
  expect((await POST(request(body))).status).toBe(422);
  expect(mockSet).not.toHaveBeenCalled();
});
it('requires explicit retake to replace a saved style profile', async () => {
  stored = { stylePersona: { id: 'classic' } };
  expect((await POST(request(payload()))).status).toBe(409);
  expect(mockSet).not.toHaveBeenCalled();
  expect((await POST(request({ ...payload(), retake: true }))).status).toBe(200);
});
it('returns a retryable failure when persistence is unavailable; no unsafe fallback or success', async () => {
  mockTransaction.mockRejectedValue(new Error('Firestore unavailable'));
  const result = await POST(request(payload()));
  expect(result.status).toBe(503);
  expect(await result.json()).toMatchObject({ success: false });
  expect(fetch).not.toHaveBeenCalled();
});
it('returns failure when the transaction commit fails after staging the update', async () => {
  mockTransaction.mockImplementation(async work => { await work({ get: async () => ({ data: () => ({}) }), set: mockSet }); throw new Error('commit failed'); });
  expect((await POST(request(payload()))).status).toBe(503);
});
it('preserves existing optional profile fields and queues changed spending bookkeeping', async () => {
  stored = { measurements: { braSize: 'saved-size' }, preferences: { occasions: ['work'], custom: true }, createdAt: 10 };
  const body = { ...payload(), spending_ranges: { tops: '100-250' } };
  expect((await POST(request(body))).status).toBe(200);
  expect(mockSet.mock.calls[0][1]).toMatchObject({ measurements: { braSize: 'saved-size' }, preferences: { custom: true }, created_at: 10, tveRecalcStatus: 'queued' });
});
it('acknowledges a retry after a lost response without replacing the profile again', async () => {
  expect((await POST(request(payload()))).status).toBe(200);
  stored = mockSet.mock.calls[0][1];
  mockSet.mockClear();
  expect((await POST(request(payload()))).status).toBe(200);
  expect(mockSet).not.toHaveBeenCalled();
  const changed = payload();
  changed.stylePreferences = ['Classic'];
  expect((await POST(request(changed))).status).toBe(409);
});
