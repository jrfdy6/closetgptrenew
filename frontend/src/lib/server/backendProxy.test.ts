/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { proxyToBackend } from './backendProxy';
const originalEnv = { ...process.env };
const originalFetch = global.fetch;
const upstream = jest.fn();
beforeEach(() => { jest.clearAllMocks(); global.fetch = upstream; process.env.BACKEND_URL = 'https://railway.example'; });
afterAll(() => { global.fetch = originalFetch; process.env = originalEnv; });
const request = () => new Request('https://spoof.example/api/onboarding?url=https://evil.example', {
  method: 'POST', headers: { Authorization: 'Bearer signed-token', 'Content-Type': 'application/json',
    'X-Forwarded-Host': 'evil.example', 'X-User-Id': 'forged', 'X-Admin': 'true', Cookie: 'session=private' }, body: '{}',
});
it.each(['http://evil.example', 'https://user:password@railway.example', 'https://railway.example?target=x', 'https://railway.example/#x', 'file:///tmp/x', 'https://railway.example/path'])('fails closed on invalid configured destination %s', async url => {
  process.env.BACKEND_URL = url;
  expect((await proxyToBackend(request(), '/api/onboarding')).status).toBe(503);
  expect(upstream).not.toHaveBeenCalled();
});
it.each(['https://evil.example/api/x', '//evil.example/api/x', '/api/../private', '/api/evil\\x'])('rejects unsafe route destination %s', async path => {
  expect((await proxyToBackend(request(), path)).status).toBe(503);
  expect(upstream).not.toHaveBeenCalled();
});
it.each([301, 302, 303, 307, 308])('does not follow %s or reveal its redirect to the client', async status => {
  upstream.mockResolvedValue(new Response(null, { status, headers: { Location: 'https://evil.example/capture' } }));
  const result = await proxyToBackend(request(), '/api/onboarding');
  expect(result.status).toBe(502); expect(result.headers.get('location')).toBeNull();
  expect(upstream).toHaveBeenCalledTimes(1); expect(upstream.mock.calls[0][1].redirect).toBe('manual');
});
it('has bounded timeout with response headroom and no automatic mutation retry', async () => {
  const deadline = jest.spyOn(AbortSignal, 'timeout');
  const error = new Error('private timeout'); error.name = 'TimeoutError'; upstream.mockRejectedValue(error);
  const result = await proxyToBackend(request(), '/api/onboarding');
  expect(result.status).toBe(504); expect((await result.json()).error).toMatch(/may have been saved/);
  expect(deadline).toHaveBeenCalledWith(50_000); expect(upstream).toHaveBeenCalledTimes(1); deadline.mockRestore();
});
it('forwards only bearer and content headers to configured host', async () => {
  upstream.mockResolvedValue(Response.json({ success: true }));
  await proxyToBackend(request(), '/api/onboarding');
  expect(upstream.mock.calls[0][0]).toBe('https://railway.example/api/onboarding');
  expect(Object.fromEntries(upstream.mock.calls[0][1].headers)).toEqual({
    accept: 'application/json', authorization: 'Bearer signed-token', 'content-type': 'application/json',
  });
});
it('rejects non-JSON upstream output rather than exposing an error page', async () => {
  upstream.mockResolvedValue(new Response('private stack trace', { status: 500 }));
  const response = await proxyToBackend(request(), '/api/onboarding');
  expect(response.status).toBe(502); expect(JSON.stringify(await response.json())).not.toContain('private stack');
});
