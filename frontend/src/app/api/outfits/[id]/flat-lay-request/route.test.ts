declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import type { NextRequest } from 'next/server';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) } }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example' }));
const request = (auth = 'Bearer token') => ({ headers: new Headers({ authorization: auth }), json: async () => ({ credits: 99, flat_lay_status: 'done' }) }) as NextRequest;
const params = { params: { id: 'look-1' } };
beforeEach(() => { global.fetch = jest.fn(); });
it('forwards only authenticated intent, once', async () => {
  const data = { success: true, id: 'look-1', flat_lay_status: 'pending' };
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  expect(await (await POST(request(), params)).json()).toEqual(data);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('https://backend.example/api/outfits/look-1/flat-lay-request', expect.objectContaining({ method: 'POST', body: '{}', headers: { Authorization: 'Bearer token', 'Content-Type': 'application/json' } }));
});
it.each(['', 'Bearer ', 'Basic token'])('rejects invalid auth before forwarding: %s', async auth => {
  expect((await POST(request(auth), params)).status).toBe(401);
  expect(fetch).not.toHaveBeenCalled();
});
it.each([403, 404, 409, 503])('preserves server error %s', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status, json: async () => ({ detail: 'Request needs review' }) });
  const response = await POST(request(), params);
  expect(response.status).toBe(status);
  expect(await response.json()).toEqual({ error: 'Request needs review' });
});
it.each([{}, { success: true, id: 'different', flat_lay_status: 'pending' }])('rejects an unconfirmed response %j', async data => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  expect((await POST(request(), params)).status).toBe(502);
});
it('returns an uncertain timeout without making another request', async () => {
  const error = new Error('provider details must not be exposed'); error.name = 'AbortError';
  (fetch as jest.Mock).mockRejectedValue(error);
  const response = await POST(request(), params);
  expect(response.status).toBe(504);
  expect(await response.json()).toEqual({ error: expect.stringContaining('active request will not use another credit') });
  expect(fetch).toHaveBeenCalledTimes(1);
});
