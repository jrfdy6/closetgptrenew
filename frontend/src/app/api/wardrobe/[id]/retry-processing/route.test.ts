declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import { proxyToBackend } from '@/lib/server/backendProxy';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
jest.mock('@/lib/server/backendProxy', () => ({ proxyToBackend: jest.fn() }));
const proxy = proxyToBackend as jest.Mock;
const request = (body: unknown = { expected_attempt_id: 'failed-attempt' }, authorization = 'Bearer signed-token') => ({ headers: new Headers({ authorization }), json: async () => body }) as Request;
const params = { params: { id: 'item-1' } };
const acknowledgement = { success: true, garment_id: 'item-1', status: 'pending', generation_id: 'generation-2', attempt_count: 0, idempotent: false };
beforeEach(() => { jest.clearAllMocks(); proxy.mockResolvedValue({ ok: true, json: async () => acknowledgement }); });

it('forwards only the exact failed attempt through the fixed backend proxy', async () => {
  const input = request();
  const response = await POST(input, params);
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual(acknowledgement);
  expect(proxy).toHaveBeenCalledWith(input, '/api/wardrobe/item-1/retry-processing', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: '{"expected_attempt_id":"failed-attempt"}', timeoutMs: 15_000,
  });
  expect(response.headers).toEqual({ 'Cache-Control': 'private, no-store' });
});
it.each(['', 'Bearer ', 'Basic token', 'Bearer test', 'Bearer TEST', 'Bearer two tokens'])('rejects malformed authorization %s before forwarding', async authorization => {
  expect((await POST(request(undefined, authorization), params)).status).toBe(401);
  expect(proxy).not.toHaveBeenCalled();
});
it.each([null, [], {}, { expected_attempt_id: '' }, { expected_attempt_id: ' ' }, { expected_attempt_id: 123 },
  { expected_attempt_id: 'a'.repeat(257) }, { expected_attempt_id: 'attempt', userId: 'foreign' },
  { expected_attempt_id: 'attempt', processing_status: 'pending' }])('rejects non-exact retry body %j', async body => {
  expect((await POST(request(body), params)).status).toBe(422);
  expect(proxy).not.toHaveBeenCalled();
});
it.each(['..', 'item/path', 'item?owner=foreign', 'item#fragment', 'a'.repeat(129)])('rejects invalid item path %s', async id => {
  expect((await POST(request(), { params: { id } })).status).toBe(422);
  expect(proxy).not.toHaveBeenCalled();
});
it('rejects malformed JSON without forwarding', async () => {
  const input = request(); input.json = async () => { throw new Error('malformed'); };
  expect((await POST(input, params)).status).toBe(422);
  expect(proxy).not.toHaveBeenCalled();
});
it.each([401, 403, 404, 409, 422, 429, 503, 504])('preserves finite backend failure %s without private details or automatic retries', async status => {
  proxy.mockResolvedValue({ ok: false, status, json: async () => ({ detail: 'private upstream error' }) });
  const response = await POST(request(), params);
  expect(response.status).toBe(status);
  expect(JSON.stringify(await response.json())).not.toContain('private upstream error');
  expect(proxy).toHaveBeenCalledTimes(1);
});
it('maps unknown backend failures to a finite gateway error', async () => {
  proxy.mockResolvedValue({ ok: false, status: 500 });
  expect((await POST(request(), params)).status).toBe(502);
});
it.each(['pending', 'processing', 'done', 'failed', 'cancelled'])('accepts idempotent replay after state advances to %s and filters extras', async status => {
  proxy.mockResolvedValue({ ok: true, json: async () => ({ ...acknowledgement, status, attempt_count: 3, idempotent: true, internal: 'private' }) });
  const response = await POST(request(), params);
  expect(await response.json()).toEqual({ ...acknowledgement, status, attempt_count: 3, idempotent: true });
  expect(proxy).toHaveBeenCalledTimes(1);
});
it.each([{}, { ...acknowledgement, garment_id: 'other' }, { ...acknowledgement, status: 'invented' },
  { ...acknowledgement, generation_id: '' }, { ...acknowledgement, attempt_count: 4 },
  { ...acknowledgement, attempt_count: -1 }, { ...acknowledgement, idempotent: 'true' }])('rejects unconfirmed acknowledgement %j', async body => {
  proxy.mockResolvedValue({ ok: true, json: async () => body });
  expect((await POST(request(), params)).status).toBe(502);
});
it('handles unreadable acknowledgement without leaking exception details', async () => {
  proxy.mockResolvedValue({ ok: true, json: async () => { throw new Error('private'); } });
  const response = await POST(request(), params);
  expect(response.status).toBe(502);
  expect(JSON.stringify(await response.json())).not.toContain('private');
});
