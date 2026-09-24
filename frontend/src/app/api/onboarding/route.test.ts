/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { GET, POST, PATCH } from './route';

const originalFetch = global.fetch;
const originalEnv = { ...process.env };
const upstream = jest.fn();
const draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }], currentQuestionId: 'skin_tone' };
beforeEach(() => {
  jest.clearAllMocks(); global.fetch = upstream;
  process.env.BACKEND_URL = 'https://railway.example';
  delete process.env.FIREBASE_PRIVATE_KEY;
  delete process.env.FIREBASE_CLIENT_EMAIL;
  delete process.env.FIREBASE_PROJECT_ID;
});
afterAll(() => { global.fetch = originalFetch; process.env = originalEnv; });
const request = (method: string, body?: unknown, auth = 'Bearer signed-token') => new Request('https://front.example/api/onboarding?backend=https://evil.example', {
  method, headers: { Authorization: auth, 'Content-Type': 'application/json', 'X-User-Id': 'forged', Cookie: 'private' },
  ...(body === undefined ? {} : { body: JSON.stringify(body) }),
});

it.each([['GET', GET], ['POST', POST], ['PATCH', PATCH]] as const)('forwards %s to Railway without Admin config or identity assertions', async (method, handler) => {
  upstream.mockResolvedValue(Response.json({ success: true, state: { revision: 3, draft } }));
  const response = await handler(request(method, method === 'GET' ? undefined : { expectedRevision: 2, draft }));
  expect(await response.json()).toEqual({ success: true, state: { revision: 3, draft } });
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  const [url, options] = upstream.mock.calls[0];
  expect(url).toBe('https://railway.example/api/onboarding');
  expect(options.method).toBe(method);
  expect(options.redirect).toBe('manual');
  expect(options.headers.get('x-user-id')).toBeNull();
  expect(options.headers.get('cookie')).toBeNull();
  if (method !== 'GET') expect(JSON.parse(new TextDecoder().decode(options.body))).toEqual({ expectedRevision: 2, draft });
});
it.each([401, 403, 409, 422, 503])('retains backend %s and the conflict/retry envelope', async status => {
  const body = { success: false, code: 'revision_conflict', state: { revision: 4, draft } };
  upstream.mockResolvedValue(Response.json(body, { status }));
  const response = await PATCH(request('PATCH', { expectedRevision: 2, draft }));
  expect(response.status).toBe(status); expect(await response.json()).toEqual(body);
});
it('rejects missing/test authentication before forwarding private progress', async () => {
  expect((await GET(request('GET', undefined, ''))).status).toBe(401);
  expect((await GET(request('GET', undefined, 'Bearer test'))).status).toBe(401);
  expect(upstream).not.toHaveBeenCalled();
});
it('does not retry a lost commit acknowledgement or invent empty progress', async () => {
  upstream.mockRejectedValue(new TypeError('connection lost after save'));
  const response = await PATCH(request('PATCH', { expectedRevision: 2, draft }));
  expect(response.status).toBe(503); expect((await response.json()).error).toMatch(/may have been saved/);
  expect(upstream).toHaveBeenCalledTimes(1);
});
