declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import { getFirebaseAdminAuth } from '@/lib/server/firebaseAdmin';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({
  status: init?.status ?? 200, headers: init?.headers, json: async () => body,
}) } }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example' }));
jest.mock('@/lib/server/firebaseAdmin', () => ({ getFirebaseAdminAuth: jest.fn() }));
const verify = jest.fn();
const request = (body: unknown = { expected_attempt_id: 'failed-attempt' }, authorization = 'Bearer signed-token') => ({
  headers: new Headers({ authorization }), json: async () => body,
}) as Request;
const params = { params: { id: 'item-1' } };
const acknowledgement = { success: true, garment_id: 'item-1', status: 'pending', generation_id: 'generation-2', attempt_count: 0, idempotent: false };

beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn();
  (getFirebaseAdminAuth as jest.Mock).mockReturnValue({ verifyIdToken: verify });
  verify.mockResolvedValue({ uid: 'verified-user' });
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => acknowledgement });
});
afterEach(() => { jest.useRealTimers(); });

it('verifies revocation and forwards only the exact failed attempt, returning a private acknowledgement', async () => {
  const response = await POST(request(), params);
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual(acknowledgement);
  expect(verify).toHaveBeenCalledWith('signed-token', true);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('https://backend.example/api/wardrobe/item-1/retry-processing', expect.objectContaining({
    method: 'POST', headers: { Authorization: 'Bearer signed-token', 'Content-Type': 'application/json' },
    body: '{"expected_attempt_id":"failed-attempt"}', cache: 'no-store', redirect: 'error',
  }));
  expect(response.headers).toEqual({ 'Cache-Control': 'private, no-store' });
});

it.each(['', 'Bearer ', 'Basic token', 'Bearer test', 'Bearer TEST', 'Bearer two tokens'])('rejects unauthorized input %s before verification or forwarding', async authorization => {
  const response = await POST(request(undefined, authorization), params);
  expect(response.status).toBe(401);
  expect(response.headers).toEqual({ 'Cache-Control': 'private, no-store' });
  expect(verify).not.toHaveBeenCalled();
  expect(fetch).not.toHaveBeenCalled();
});

it.each(['auth/id-token-revoked', 'auth/id-token-expired', 'auth/invalid-id-token', 'auth/user-disabled'])('rejects invalid Firebase identity %s without forwarding', async code => {
  verify.mockRejectedValue({ code, message: 'private auth details' });
  const response = await POST(request(), params);
  expect(response.status).toBe(401);
  expect(JSON.stringify(await response.json())).not.toContain('private auth details');
  expect(fetch).not.toHaveBeenCalled();
});

it('fails closed when identity verification is unavailable', async () => {
  (getFirebaseAdminAuth as jest.Mock).mockImplementation(() => { throw new Error('private service account configuration'); });
  const response = await POST(request(), params);
  expect(response.status).toBe(503);
  expect(JSON.stringify(await response.json())).not.toContain('private service account configuration');
  expect(fetch).not.toHaveBeenCalled();
});

it.each([{}, { uid: '' }, { uid: ' ' }])('rejects missing verified UID %j', async claims => {
  verify.mockResolvedValue(claims);
  expect((await POST(request(), params)).status).toBe(401);
  expect(fetch).not.toHaveBeenCalled();
});

it.each([null, [], {}, { expected_attempt_id: '' }, { expected_attempt_id: ' ' }, { expected_attempt_id: 123 },
  { expected_attempt_id: 'a'.repeat(257) }, { expected_attempt_id: 'attempt', userId: 'foreign' },
  { expected_attempt_id: 'attempt', processing_status: 'pending' }])('rejects non-exact retry body %j', async body => {
  expect((await POST(request(body), params)).status).toBe(422);
  expect(fetch).not.toHaveBeenCalled();
});

it.each(['..', 'item/path', 'item?owner=foreign', 'item#fragment', 'a'.repeat(129)])('rejects invalid item path %s', async id => {
  expect((await POST(request(), { params: { id } })).status).toBe(422);
  expect(fetch).not.toHaveBeenCalled();
});

it('rejects malformed JSON without forwarding', async () => {
  const input = request();
  input.json = async () => { throw new Error('malformed'); };
  expect((await POST(input, params)).status).toBe(422);
  expect(fetch).not.toHaveBeenCalled();
});

it.each([401, 404, 409, 422, 429, 503])('preserves finite failure status %s without leaking upstream details', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status, json: async () => ({ detail: 'private upstream exception' }) });
  const response = await POST(request(), params);
  expect(response.status).toBe(status);
  expect(await response.json()).toMatchObject({ success: false, error: expect.any(String) });
  expect(JSON.stringify(await response.json())).not.toContain('private upstream exception');
});

it('maps unknown upstream errors to a finite gateway error', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 500 });
  expect((await POST(request(), params)).status).toBe(502);
});

it.each(['pending', 'processing', 'done', 'failed', 'cancelled'])('accepts idempotent replay after the retry advances to %s and filters extra fields', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ ...acknowledgement, status, attempt_count: 3, idempotent: true, internal: 'private' }) });
  const response = await POST(request(), params);
  expect(await response.json()).toEqual({ ...acknowledgement, status, attempt_count: 3, idempotent: true });
  expect(fetch).toHaveBeenCalledTimes(1);
});

it.each([{}, { ...acknowledgement, garment_id: 'other' }, { ...acknowledgement, status: 'invented' },
  { ...acknowledgement, generation_id: '' }, { ...acknowledgement, attempt_count: 4 },
  { ...acknowledgement, attempt_count: -1 }, { ...acknowledgement, idempotent: 'true' }])('rejects unconfirmed backend responses %j', async data => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  expect((await POST(request(), params)).status).toBe(502);
});

it('bounds the backend request, returns an uncertain timeout, and never retries automatically', async () => {
  jest.useFakeTimers();
  let started!: () => void;
  const waiting = new Promise<void>(resolve => { started = resolve; });
  (fetch as jest.Mock).mockImplementation((_url: string, options: RequestInit) => new Promise((_resolve, reject) => {
    options.signal?.addEventListener('abort', () => reject(new Error('private timeout details')));
    started();
  }));
  const result = POST(request(), params);
  await waiting;
  jest.advanceTimersByTime(15_000);
  const response = await result;
  expect(response.status).toBe(504);
  expect(await response.json()).toEqual({ success: false, error: expect.stringContaining('same request will not restart processing twice') });
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('does not retry an ambiguous network failure or expose exception text', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('private network payload'));
  const response = await POST(request(), params);
  expect(response.status).toBe(502);
  expect(JSON.stringify(await response.json())).not.toContain('private network payload');
  expect(fetch).toHaveBeenCalledTimes(1);
});
