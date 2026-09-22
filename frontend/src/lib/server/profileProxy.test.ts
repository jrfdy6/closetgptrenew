declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { proxyProfile } from './profileProxy';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: any) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
jest.mock('./backendUrl', () => ({ getBackendUrl: () => 'https://backend.example' }));
const request = (token?: string, body: unknown = {}) => ({ headers: new Headers(token ? { authorization: `Bearer ${token}` } : {}), json: async () => body }) as Request;
beforeEach(() => { global.fetch = jest.fn(); AbortSignal.timeout = jest.fn(() => new AbortController().signal); });
it('rejects missing authentication before any profile access', async () => {
  expect((await proxyProfile(request(), 'GET')).status).toBe(401);
  expect(fetch).not.toHaveBeenCalled();
});
it('does not share cached profiles between tokens with the same JWT header', async () => {
  (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ name: 'One' }) }).mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ name: 'Two' }) });
  const prefix = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNhbWUifQ';
  expect(await (await proxyProfile(request(`${prefix}.one.signature`), 'GET')).json()).toEqual({ name: 'One' });
  expect(await (await proxyProfile(request(`${prefix}.two.signature`), 'GET')).json()).toEqual({ name: 'Two' });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect((fetch as jest.Mock).mock.calls[1][1].cache).toBe('no-store');
});
it('preserves backend rejection of financial fields, with no Admin fallback', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: 'Protected fields' }) });
  expect((await proxyProfile(request('token', { quotas: { flatlaysRemaining: 100 } }), 'PUT')).status).toBe(422);
  expect(fetch).toHaveBeenCalledTimes(1);
});
it('returns a retryable failure if the profile cannot be saved', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('offline'));
  const response = await proxyProfile(request('token', { name: 'Name' }), 'PUT');
  expect(response.status).toBe(502);
  expect(await response.json()).toMatchObject({ retryable: true });
});
