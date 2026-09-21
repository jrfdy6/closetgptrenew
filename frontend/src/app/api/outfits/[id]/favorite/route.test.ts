// Keep Jest types local; Cypress also declares global test functions.
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { PUT } from './route';
import type { NextRequest } from 'next/server';

jest.mock('next/server', () => ({
  NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) },
}));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example' }));

function request(body: unknown, authenticated = true): NextRequest {
  return { headers: new Headers(authenticated ? { authorization: 'Bearer test-token' } : {}), json: async () => body } as NextRequest;
}

beforeEach(() => { global.fetch = jest.fn(); });

it.each([true, false])('forwards explicit favorite=%s once, with authentication', async isFavorite => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, id: 'look-1', isFavorite }) });
  const response = await PUT(request({ isFavorite, user_id: 'untrusted' }), { params: { id: 'look-1' } });
  expect(response.status).toBe(200);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('https://backend.example/api/outfits/look-1/favorite', expect.objectContaining({
    method: 'PUT', headers: { Authorization: 'Bearer test-token', 'Content-Type': 'application/json' },
    body: JSON.stringify({ isFavorite }),
  }));
});

it('rejects missing authentication before a backend request', async () => {
  expect((await PUT(request({ isFavorite: true }, false), { params: { id: 'look-1' } })).status).toBe(401);
  expect(fetch).not.toHaveBeenCalled();
});

it.each([{}, null, { isFavorite: 'false' }, { isFavorite: 1 }])('rejects an ambiguous favorite state %j', async body => {
  expect((await PUT(request(body), { params: { id: 'look-1' } })).status).toBe(422);
  expect(fetch).not.toHaveBeenCalled();
});

it('preserves an ownership denial', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 403, json: async () => ({ detail: 'Access denied' }) });
  expect((await PUT(request({ isFavorite: true }), { params: { id: 'look-1' } })).status).toBe(403);
});

it('does not claim success if the backend did not confirm the update', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({}) });
  expect((await PUT(request({ isFavorite: true }), { params: { id: 'look-1' } })).status).toBe(502);
});

it('returns a retryable timeout without toggling or making another request', async () => {
  const error = new Error('timeout');
  error.name = 'AbortError';
  (fetch as jest.Mock).mockRejectedValue(error);
  expect((await PUT(request({ isFavorite: true }), { params: { id: 'look-1' } })).status).toBe(504);
  expect(fetch).toHaveBeenCalledTimes(1);
});
