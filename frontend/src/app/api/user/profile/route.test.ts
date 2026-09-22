declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { GET, POST } from './route';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) } }));
jest.mock('firebase-admin/firestore', () => ({ Timestamp: { now: () => ({ seconds: 12345 }) } }));
const mockVerify = jest.fn();
const mockGet = jest.fn();
const mockSet = jest.fn();
const mockCreate = jest.fn();
const mockDoc = jest.fn();
jest.mock('@/lib/server/firebaseAdmin', () => ({
  getFirebaseAdminAuth: () => ({ verifyIdToken: mockVerify }),
  getFirebaseAdminDb: () => ({ collection: () => ({ doc: mockDoc }) }),
}));
function request(token = 'shared.jwt.header-prefix.abcdefghijklmnopqrstuvwxyz.account-a', body: unknown = {}): Request {
  return { headers: new Headers(token ? { authorization: `Bearer ${token}` } : {}), json: async () => body } as Request;
}
beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn();
  mockVerify.mockResolvedValue({ uid: 'a', email: 'a@example.test', name: 'Alex Example' });
  mockDoc.mockReturnValue({ get: mockGet, set: mockSet, create: mockCreate });
  mockGet.mockResolvedValue({ exists: true, data: () => ({ name: 'Alex Example' }) });
  mockSet.mockResolvedValue(undefined); mockCreate.mockResolvedValue(undefined);
});
it('never shares profiles between tokens with identical JWT header prefixes', async () => {
  mockVerify.mockResolvedValueOnce({ uid: 'a', email: 'a@example.test' }).mockResolvedValueOnce({ uid: 'b', email: 'b@example.test' });
  mockGet.mockResolvedValueOnce({ exists: true, data: () => ({ name: 'User A' }) }).mockResolvedValueOnce({ exists: true, data: () => ({ name: 'User B' }) });
  const first = await GET(request());
  const second = await GET(request('shared.jwt.header-prefix.abcdefghijklmnopqrstuvwxyz.account-b'));
  expect(await first.json()).toMatchObject({ name: 'User A', userId: 'a' });
  expect(await second.json()).toMatchObject({ name: 'User B', userId: 'b' });
  expect(mockVerify).toHaveBeenCalledTimes(2);
  expect(mockDoc.mock.calls).toEqual([['a'], ['b']]);
});
it.each([GET, POST])('fails closed for missing, forged or expired credentials without backend fallback', async handler => {
  expect((await handler(request(''))).status).toBe(401);
  mockVerify.mockRejectedValue(Object.assign(new Error('invalid signature'), { code: 'auth/invalid-id-token' }));
  expect((await handler(request('test'))).status).toBe(401);
  expect(fetch).not.toHaveBeenCalled();
  expect(mockDoc).not.toHaveBeenCalled();
});
it('verifies a previously seen token again, so a prior success cannot bypass later rejection', async () => {
  expect((await GET(request())).status).toBe(200);
  mockVerify.mockRejectedValue(Object.assign(new Error('expired'), { code: 'auth/id-token-expired' }));
  expect((await GET(request())).status).toBe(401);
  expect(mockGet).toHaveBeenCalledTimes(1);
});
it.each([GET, POST])('returns retryable unavailability rather than downgrading authentication', async handler => {
  mockVerify.mockRejectedValue(new Error('Firebase Admin not configured'));
  expect((await handler(request())).status).toBe(503);
  expect(fetch).not.toHaveBeenCalled();
});
it('preserves entered names and refuses cross-account identity fields', async () => {
  expect((await POST(request(undefined, { userId: 'b' }))).status).toBe(403);
  expect(mockSet).not.toHaveBeenCalled();
  expect((await POST(request(undefined, { gender: 'Male' }))).status).toBe(200);
  expect(mockSet.mock.calls[0][0]).toMatchObject({ name: 'Alex Example', userId: 'a', gender: 'Male' });
});
it('does not manufacture a successful profile save when Firestore fails', async () => {
  mockSet.mockRejectedValue(new Error('write failed'));
  expect((await POST(request(undefined, { name: 'New name' }))).status).toBe(503);
  expect(fetch).not.toHaveBeenCalled();
});
it('does not overwrite a style profile saved concurrently while GET was creating a minimal profile', async () => {
  mockGet.mockResolvedValueOnce({ exists: false, data: () => undefined }).mockResolvedValueOnce({ exists: true, data: () => ({ name: 'Saved name', stylePersona: { id: 'classic' } }) });
  mockCreate.mockRejectedValue(Object.assign(new Error('already exists'), { code: 6 }));
  const result = await GET(request());
  expect(result.status).toBe(200);
  expect(await result.json()).toMatchObject({ name: 'Saved name', stylePersona: { id: 'classic' } });
  expect(mockSet).not.toHaveBeenCalled();
});
