declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
it('retires the unused privileged upload endpoint without accepting an upload', async () => {
  const response = await POST();
  expect(response.status).toBe(410);
  expect(await response.json()).toEqual({ success: false, error: expect.any(String) });
  expect(response.headers).toEqual({ 'Cache-Control': 'private, no-store' });
});
