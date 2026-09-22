declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import type { NextRequest } from 'next/server';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number }) => ({ status: init?.status ?? 200, json: async () => body }) } }));
jest.mock('@/lib/server/backendUrl', () => ({ getBackendUrl: () => 'https://backend.example' }));
jest.mock('@/lib/server/debug', () => ({ serverDebugLog: jest.fn(), serverDebugWarn: jest.fn() }));
const request = (body: unknown, token = 'valid') => ({ headers: new Headers(token ? { authorization: `Bearer ${token}` } : {}), json: async () => body }) as NextRequest;
const quiz = { userId: 'owner', answers: [{ question_id: 'gender', selected_option: 'Male' }], stylePreferences: ['classic'] };

beforeEach(() => {
  global.fetch = jest.fn();
  AbortSignal.timeout = jest.fn(() => new AbortController().signal);
  (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ user_id: 'owner', email: 'owner@example.com' }) });
});
it('requires verified authentication instead of accepting decoded JWT data', async () => {
  (fetch as jest.Mock).mockReset().mockResolvedValue({ ok: false, status: 401 });
  expect((await POST(request(quiz, 'forged.jwt.token'))).status).toBe(401);
  expect(fetch).toHaveBeenCalledTimes(1);
});
it('rejects a submitted user ID belonging to another account', async () => {
  expect((await POST(request({ ...quiz, userId: 'other' }))).status).toBe(403);
  expect(fetch).toHaveBeenCalledTimes(1);
});
it('does not claim success or use a direct database fallback when saving fails', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('offline'));
  const response = await POST(request(quiz));
  expect(response.status).toBe(503);
  expect(await response.json()).toMatchObject({ success: false, retryable: true });
  expect(fetch).toHaveBeenCalledTimes(2);
});
it.each([9, 10])('preserves the ten-item capsule threshold for %s saved items', async count => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, status: 200, json: async () => ({ wardrobeCount: count }) });
  const response = await POST(request(quiz));
  expect(await response.json()).toMatchObject({ success: true, wardrobeCount: count, hasExistingWardrobe: count >= 10 });
  const payload = JSON.parse((fetch as jest.Mock).mock.calls[1][1].body);
  expect(payload.userId).toBe('owner');
  expect(payload).not.toHaveProperty('created_at');
});
