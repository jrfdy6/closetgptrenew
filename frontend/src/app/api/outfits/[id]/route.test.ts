// Jest assertions are explicit because Cypress also contributes global types.
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { GET } from './route';
import type { NextRequest } from 'next/server';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: Record<string, string> }) => ({
  status: init?.status ?? 200, headers: new Headers(init?.headers), json: async () => body,
}) } }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example/' }));
const originalFetch = global.fetch;
const params = { params: { id: 'look /?#1' } };
const saved = { id: params.params.id, items: [{ id: 'shirt' }], name: 'Saved look', isFavorite: true, wearCount: 2, flat_lay_request_id: 'request-one', flat_lay_status: 'pending' };
const request = (auth?: string) => ({ headers: new Headers(auth === undefined ? {} : { authorization: auth }) }) as NextRequest;
beforeEach(() => { global.fetch = jest.fn(); });
afterEach(() => { global.fetch = originalFetch; jest.useRealTimers(); });

it.each([undefined, '', 'Basic token', 'Bearer ', 'Bearer one two'])('rejects malformed auth before reading an outfit: %s', async auth => {
  const response = await GET(request(auth), params);
  expect(response.status).toBe(401);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(fetch).not.toHaveBeenCalled();
});

it('reads the same encoded saved ID once with auth and private no-store caching', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => saved });
  const response = await GET(request('Bearer test-token'), params);
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual(saved);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('https://backend.example/api/outfits/look%20%2F%3F%231', expect.objectContaining({
    headers: { Authorization: 'Bearer test-token' }, cache: 'no-store', signal: expect.any(AbortSignal),
  }));
  expect((fetch as jest.Mock).mock.calls[0][1].body).toBeUndefined();
  expect((fetch as jest.Mock).mock.calls[0][0]).not.toContain('/generate');
});

it.each([401, 403, 404, 503])('preserves failed read status %s without leaking backend details', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status, json: async () => ({ detail: 'PRIVATE_BACKEND_DETAIL', token: 'PRIVATE_TOKEN' }) });
  const response = await GET(request('Bearer test-token'), params);
  expect(response.status).toBe(status);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  const body = await response.json();
  expect(body.error).toEqual(expect.any(String));
  expect(JSON.stringify(body)).not.toContain('PRIVATE_');
  expect(body.success).not.toBe(true);
});

it.each([null, {}, { ...saved, id: 'other-look' }, { ...saved, items: null }, { ...saved, items: {} }])('rejects an unconfirmed saved outfit: %j', async data => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  const response = await GET(request('Bearer test-token'), params);
  expect(response.status).toBe(502);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect((await response.json()).success).not.toBe(true);
});

it('rejects malformed backend JSON without substituting or generating an outfit', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => { throw new Error('PRIVATE_PARSE_DETAILS'); } });
  const response = await GET(request('Bearer test-token'), params);
  expect(response.status).toBe(502);
  expect(JSON.stringify(await response.json())).not.toContain('PRIVATE_');
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('returns a safe read failure after a network error without automatic retry', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('PRIVATE_CONNECTION_DETAILS'));
  const response = await GET(request('Bearer test-token'), params);
  expect(response.status).toBe(503);
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(JSON.stringify(await response.json())).not.toContain('PRIVATE_');
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('aborts a stalled backend read at the bounded timeout', async () => {
  jest.useFakeTimers();
  (fetch as jest.Mock).mockImplementation((_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
  }));
  const pending = GET(request('Bearer test-token'), params);
  jest.advanceTimersByTime(15000);
  const response = await pending;
  expect(response.status).toBe(503);
  expect((fetch as jest.Mock).mock.calls[0][1].signal.aborted).toBe(true);
  expect(jest.getTimerCount()).toBe(0);
  expect(fetch).toHaveBeenCalledTimes(1);
});
