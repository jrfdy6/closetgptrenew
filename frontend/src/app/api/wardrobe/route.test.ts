declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { GET, POST } from './route';
import { proxyToBackend } from '@/lib/server/backendProxy';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
jest.mock('@/lib/server/backendProxy', () => ({ proxyToBackend: jest.fn() }));
const proxy = proxyToBackend as jest.Mock;
const request = (body: unknown = { id: 'item-1', name: 'Shirt', imageUrl: 'https://assets.example/original.jpg', contentHash: 'photo-hash' }, authorization = 'Bearer signed-token') => ({
  headers: new Headers({ authorization }), json: async () => body, url: 'https://app.example/api/wardrobe',
}) as Request;
const item = { id: 'item-1', userId: 'owner', name: 'Saved shirt', processing_status: 'done', wearCount: 2 };
beforeEach(() => { jest.clearAllMocks(); proxy.mockResolvedValue({ ok: true, status: 200, json: async () => ({ success: true, item }) }); });

it('preserves stable id, original and metadata and returns the acknowledged saved item', async () => {
  const input = request();
  const response = await POST(input);
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ success: true, item });
  expect(proxy).toHaveBeenCalledWith(input, '/api/wardrobe/add-direct', expect.objectContaining({
    method: 'POST', headers: { 'Content-Type': 'application/json' }, timeoutMs: 45_000,
    body: JSON.stringify(await input.json()),
  }));
  expect(response.headers).toEqual({ 'Cache-Control': 'private, no-store' });
});
it('forwards owner aliases for verified backend rejection rather than silently replacing them', async () => {
  proxy.mockResolvedValue({ ok: false, status: 403 });
  const body = { id: 'item-1', userId: 'spoofed', user_id: 'other', firebase_uid: 'hostile' };
  const response = await POST(request(body));
  expect(response.status).toBe(403);
  expect(JSON.parse(proxy.mock.calls[0][2].body)).toEqual(body);
  expect((await response.json()).item).toBeUndefined();
});
it.each(['', 'Bearer ', 'Basic token', 'Bearer test', 'Bearer TEST', 'Bearer two tokens'])('does not forward malformed authorization %s', async authorization => {
  expect((await POST(request({}, authorization))).status).toBe(401);
  expect(proxy).not.toHaveBeenCalled();
});
it.each([null, [], 'bad'])('does not forward malformed body %j', async body => {
  expect((await POST(request(body))).status).toBe(400);
  expect(proxy).not.toHaveBeenCalled();
});
it.each([401, 403, 422, 500, 503, 504])('preserves backend failure %i without inventing a save', async status => {
  proxy.mockResolvedValue({ ok: false, status });
  const response = await POST(request());
  expect(response.status).toBe(status);
  expect((await response.json()).item).toBeUndefined();
});
it.each([{ success: false }, { success: true }, { success: true, item: { id: 'wrong-id', userId: 'owner' } },
  { success: true, item: { id: 'item-1', userId: '' } }, { success: true, item: { ...item, user_id: 'other' } },
  { success: true, item: { ...item, firebase_uid: 'other' } }])('rejects an unconfirmed save %j', async body => {
  proxy.mockResolvedValue({ ok: true, status: 200, json: async () => body });
  expect((await POST(request())).status).toBe(502);
});
it('rejects unreadable success data', async () => {
  proxy.mockResolvedValue({ ok: true, json: async () => { throw new Error('bad JSON'); } });
  expect((await POST(request())).status).toBe(502);
});
it('loads saved wardrobe with the exact trailing slash and preserves response errors', async () => {
  const upstream = { ok: false, status: 503, json: async () => ({ success: false }) };
  proxy.mockResolvedValue(upstream);
  const input = request();
  expect(await GET(input)).toBe(upstream);
  expect(proxy).toHaveBeenCalledWith(input, '/api/wardrobe/', { method: 'GET', timeoutMs: 45_000 });
});
it('loads count from wardrobe without the stale profile shortcut', async () => {
  const input = request();
  Object.assign(input, { url: 'https://app.example/api/wardrobe?count_only=true' });
  await GET(input);
  expect(proxy).toHaveBeenCalledTimes(1);
  expect(proxy).toHaveBeenCalledWith(input, '/api/wardrobe/?count_only=true', { method: 'GET', timeoutMs: 45_000 });
});
