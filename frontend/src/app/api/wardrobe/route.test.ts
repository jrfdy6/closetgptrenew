declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import { getFirebaseAdminAuth } from '@/lib/server/firebaseAdmin';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) } }));
jest.mock('@/lib/server/firebaseAdmin', () => ({ getFirebaseAdminAuth: jest.fn() }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://api.example.test' }));
const verify = jest.fn();
const request = (body: unknown = { id: 'item-1', userId: 'spoofed', user_id: 'hostile-alias', name: 'Shirt', type: 'shirt', color: 'white' }, authenticated = true) => ({ headers: new Headers(authenticated ? { Authorization: 'Bearer test-token' } : {}), json: async () => body }) as Request;
let mockFetch: jest.Mock;
let originalFetch: typeof fetch;
beforeEach(() => { originalFetch = global.fetch; mockFetch = jest.fn(); global.fetch = mockFetch; verify.mockResolvedValue({ uid: 'owner' }); (getFirebaseAdminAuth as jest.Mock).mockReturnValue({ verifyIdToken: verify }); });
afterEach(() => { global.fetch = originalFetch; });
it('verifies ownership and passes only a real save acknowledgment through', async () => {
  const item = { id: 'item-1', userId: 'owner', name: 'Shirt' };
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true, item }) });
  const response = await POST(request());
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ success: true, item });
  expect(verify).toHaveBeenCalledWith('test-token', true);
  expect(JSON.parse(mockFetch.mock.calls[0][1].body).userId).toBe('owner');
  expect(JSON.parse(mockFetch.mock.calls[0][1].body).user_id).toBeUndefined();
});
it('does not forward unauthenticated or malformed saves', async () => {
  expect((await POST(request({}, false))).status).toBe(401);
  expect((await POST(request(null))).status).toBe(400);
  expect(mockFetch).not.toHaveBeenCalled();
});
it.each([401, 422, 500, 503])('preserves backend failure %i without inventing an item', async status => {
  mockFetch.mockResolvedValue({ ok: false, status });
  const response = await POST(request());
  expect(response.status).toBe(status);
  expect(await response.json()).toMatchObject({ success: false });
  expect((await response.json()).item).toBeUndefined();
});
it.each([{ success: false }, { success: true }, { success: true, item: { id: 'id', userId: 'other-user' } }, { success: true, item: { id: 'id', userId: 'owner', user_id: 'other-user' } }])('rejects a 200 response without an owned persisted item: %j', async body => {
  mockFetch.mockResolvedValue({ ok: true, json: async () => body });
  const response = await POST(request());
  expect(response.status).toBe(502);
  expect((await response.json()).success).toBe(false);
});
it('reports unreadable backend and network failures as failures', async () => {
  mockFetch.mockResolvedValueOnce({ ok: true, json: async () => { throw new Error('not JSON'); } }).mockRejectedValueOnce(new Error('offline'));
  expect((await POST(request())).status).toBe(502);
  expect((await POST(request())).status).toBe(503);
});
