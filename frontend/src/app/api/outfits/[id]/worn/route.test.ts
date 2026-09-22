// Jest assertions are explicit because Cypress also contributes global types.
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import type { NextRequest } from 'next/server';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: Record<string, string> }) => ({
  status: init?.status ?? 200, headers: new Headers(init?.headers), json: async () => body,
}) } }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example/' }));
const originalFetch = global.fetch;
const params = { params: { id: 'look /?#1' } };
const operation = { idempotency_key: 'wear-operation-one', timezone: 'America/New_York' };
const receipt = { success: true, outfit_id: params.params.id, event_id: 'wear-event-one', wear_count: 3, garment_wear_counts: { shirt: 4 }, last_worn: 1790121600000, date_worn: 1790121600000, already_recorded: false };
function request(body: unknown = operation, auth: string | null = 'Bearer test-token', raw?: string): NextRequest {
  const input = raw === undefined ? JSON.stringify(body) : raw;
  return {
    headers: new Headers(auth === null ? {} : { authorization: auth }),
    text: async () => input,
    json: async () => JSON.parse(input),
  } as NextRequest;
}
beforeEach(() => { global.fetch = jest.fn(); });
afterEach(() => { global.fetch = originalFetch; jest.useRealTimers(); });

it.each([null, '', 'Basic token', 'Bearer ', 'Bearer one two'])('rejects malformed wear auth before forwarding: %s', async auth => {
  const response = await POST(request(operation, auth), params);
  expect(response.status).toBe(401);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect((await response.json()).success).toBe(false);
  expect(fetch).not.toHaveBeenCalled();
});

it('forwards only the stable operation key and timezone to an encoded owned route', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => receipt });
  const response = await POST(request({ ...operation, user_id: 'untrusted-user', wear_count: 999 }), params);
  expect(response.status).toBe(200);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(await response.json()).toEqual(receipt);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('https://backend.example/api/outfits/look%20%2F%3F%231/worn', expect.objectContaining({
    method: 'POST', cache: 'no-store', signal: expect.any(AbortSignal),
    headers: { Authorization: 'Bearer test-token', 'Content-Type': 'application/json' },
    body: JSON.stringify(operation),
  }));
});

it('keeps the identical key on an explicit response retry and returns the backend receipt', async () => {
  (fetch as jest.Mock).mockRejectedValueOnce(new Error('Lost acknowledgment')).mockResolvedValueOnce({ ok: true, json: async () => ({ ...receipt, already_recorded: true }) });
  expect((await POST(request(), params)).status).toBe(503);
  expect(fetch).toHaveBeenCalledTimes(1);
  const response = await POST(request(), params);
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ ...receipt, already_recorded: true });
  expect((fetch as jest.Mock).mock.calls.map(([, init]) => JSON.parse(init.body).idempotency_key)).toEqual([operation.idempotency_key, operation.idempotency_key]);
});

it('preserves legacy no-body calls for the backend compatibility operation', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => receipt });
  const response = await POST(request(operation, 'Bearer test-token', ''), params);
  expect(response.status).toBe(200);
  expect((fetch as jest.Mock).mock.calls[0][1].body).toBeUndefined();
  expect(fetch).toHaveBeenCalledTimes(1);
});

it.each([null, {}, { idempotency_key: '' }, { idempotency_key: '   ' }, { idempotency_key: 7 }, { idempotency_key: 'x'.repeat(129) }])('rejects an explicit invalid operation rather than treating it as legacy: %j', async body => {
  const response = await POST(request(body), params);
  expect(response.status).toBe(422);
  expect((await response.json()).success).toBe(false);
  expect(fetch).not.toHaveBeenCalled();
});

it('rejects malformed nonempty JSON before contacting the backend', async () => {
  const response = await POST(request(operation, 'Bearer test-token', '{invalid'), params);
  expect(response.status).toBe(422);
  expect(fetch).not.toHaveBeenCalled();
});

it.each([403, 404, 409, 503])('keeps a failed wear status %s and never fabricates success', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status, json: async () => ({ detail: 'Wear could not be recorded.' }) });
  const response = await POST(request(), params);
  expect(response.status).toBe(status);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect((await response.json()).success).toBe(false);
});

it('sanitizes backend infrastructure failure details', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 503, json: async () => ({ detail: 'PRIVATE_DATABASE_CREDENTIALS' }) });
  const response = await POST(request(), params);
  expect(response.status).toBe(503);
  expect(JSON.stringify(await response.json())).not.toContain('PRIVATE_');
});

it.each([null, {}, { ...receipt, success: false }, { ...receipt, outfit_id: 'other-look' }, { ...receipt, event_id: '' }, { ...receipt, event_id: '   ' }, { ...receipt, event_id: {} }, { ...receipt, wear_count: -1 }, { ...receipt, wear_count: 2.5 }, { ...receipt, wear_count: '3' }])('rejects an unconfirmed wear receipt: %j', async data => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  const response = await POST(request(), params);
  expect(response.status).toBe(502);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect((await response.json()).success).toBe(false);
});

it('rejects malformed backend JSON without claiming the wear failed to save', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => { throw new Error('PRIVATE_PARSE_DETAILS'); } });
  const response = await POST(request(), params);
  expect(response.status).toBe(502);
  const body = await response.json();
  expect(body.success).toBe(false);
  expect(body.error).toMatch(/confirm|same action/i);
  expect(JSON.stringify(body)).not.toContain('PRIVATE_');
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('reports an uncertain network result safely without retrying or changing the key', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('PRIVATE_CONNECTION_DETAILS'));
  const response = await POST(request(), params);
  expect(response.status).toBe(503);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  const body = await response.json();
  expect(body.success).toBe(false);
  expect(body.error).toMatch(/may have saved|same action/i);
  expect(JSON.stringify(body)).not.toContain('PRIVATE_');
  expect(fetch).toHaveBeenCalledTimes(1);
});
