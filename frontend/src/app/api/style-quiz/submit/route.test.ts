/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import type { NextRequest } from 'next/server';

const originalEnvironment = { ...process.env };
const mockFetch = jest.fn();

function request(body: unknown, authorization = 'Bearer verified-token') {
  return new Request('https://frontend.example/api/style-quiz/submit?backend=https://untrusted.example', {
    method: 'POST', headers: {
      Authorization: authorization, 'Content-Type': 'application/json',
      'X-User-Id': 'spoofed-owner', 'X-Forwarded-Host': 'untrusted.example', Cookie: 'private-cookie',
    }, body: JSON.stringify(body),
  }) as NextRequest;
}

beforeEach(() => {
  jest.clearAllMocks();
  process.env.BACKEND_URL = 'https://railway.example';
  delete process.env.NEXT_PUBLIC_BACKEND_URL;
  delete process.env.NEXT_PUBLIC_API_URL;
  delete process.env.FIREBASE_PRIVATE_KEY;
  delete process.env.FIREBASE_CLIENT_EMAIL;
  delete process.env.FIREBASE_PROJECT_ID;
  global.fetch = mockFetch;
});
afterAll(() => { process.env = originalEnvironment; });

it('proxies the unchanged full submission to the configured Railway host without Admin credentials', async () => {
  const submission = { userId: 'verified-owner', answers: [{ question_id: 'gender', selected_option: 'Male' }],
    colorAnalysis: { confidence: 0.875 }, spending_ranges: { tops: '$100-$250' }, retake: true };
  mockFetch.mockResolvedValue(Response.json({ success: true, persisted: true, hybridStyleName: 'The Architect' }));
  const response = await POST(request(submission));
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ success: true, persisted: true, hybridStyleName: 'The Architect' });
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(mockFetch).toHaveBeenCalledTimes(1);
  const [url, options] = mockFetch.mock.calls[0];
  expect(url).toBe('https://railway.example/api/style-quiz/submit');
  expect(options).toMatchObject({ method: 'POST', cache: 'no-store', redirect: 'manual' });
  expect(JSON.parse(new TextDecoder().decode(options.body))).toEqual(submission);
  expect(Object.fromEntries(options.headers.entries())).toEqual({
    accept: 'application/json', authorization: 'Bearer verified-token', 'content-type': 'application/json',
  });
  expect(options.signal).toBeInstanceOf(AbortSignal);
});

it.each(['', 'Basic unsigned', 'Bearer test'])('rejects malformed/test authorization %s before forwarding', async authorization => {
  const response = await POST(request({ token: 'body-token' }, authorization));
  expect(response.status).toBe(401);
  expect(mockFetch).not.toHaveBeenCalled();
});

it.each([401, 403, 409, 422, 503])('preserves Railway validation/security/commit failure status %i', async status => {
  const body = { success: false, code: 'RETAKE_REQUIRED', error: 'Profile could not be saved' };
  mockFetch.mockResolvedValue(Response.json(body, { status }));
  const response = await POST(request({ answers: [] }));
  expect(response.status).toBe(status);
  expect(await response.json()).toEqual(body);
  expect(mockFetch).toHaveBeenCalledTimes(1);
});

it('reports an unknown mutation outcome honestly and never automatically submits twice', async () => {
  mockFetch.mockRejectedValue(new TypeError('connection lost after upstream commit'));
  const response = await POST(request({ answers: [] }));
  expect(response.status).toBe(503);
  expect((await response.json()).error).toMatch(/may have been saved/i);
  expect(mockFetch).toHaveBeenCalledTimes(1);
});

it('does not forward the bearer token through a backend redirect', async () => {
  mockFetch.mockResolvedValue(new Response(null, { status: 307, headers: { Location: 'https://untrusted.example/capture' } }));
  const response = await POST(request({ answers: [] }));
  expect(response.status).toBe(502);
  expect(mockFetch).toHaveBeenCalledTimes(1);
  expect(mockFetch.mock.calls[0][1].redirect).toBe('manual');
});
