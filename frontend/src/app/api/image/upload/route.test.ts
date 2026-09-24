declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST } from './route';
import { proxyToBackend } from '@/lib/server/backendProxy';
jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init?: { status?: number; headers?: unknown }) => ({ status: init?.status ?? 200, headers: init?.headers, json: async () => body }) } }));
jest.mock('@/lib/server/backendProxy', () => ({ proxyToBackend: jest.fn() }));
const proxy = proxyToBackend as jest.Mock;
const form = new FormData(); form.append('file', new File(['original-bytes'], 'shirt.jpg', { type: 'image/jpeg' })); form.append('name', 'Shirt');
const request = (authorization = 'Bearer signed-token') => ({ headers: new Headers({ authorization }), formData: async () => form }) as Request;
beforeEach(() => { jest.clearAllMocks(); });
it('forwards the original multipart object without replacing bytes or filename', async () => {
  const upstream = { status: 200, json: async () => ({ success: true, image_url: 'https://assets.example/original.jpg' }) };
  proxy.mockResolvedValue(upstream);
  const input = request();
  expect(await POST(input)).toBe(upstream);
  expect(proxy).toHaveBeenCalledWith(input, '/api/image/upload', { method: 'POST', body: form, timeoutMs: 45_000 });
});
it.each([401, 403, 503, 504])('preserves failed upload response %i without substitute images', async status => {
  const upstream = { status, json: async () => ({ success: false }) }; proxy.mockResolvedValue(upstream);
  expect(await POST(request())).toBe(upstream);
});
it.each(['', 'Bearer test', 'Basic token', 'Bearer a b'])('rejects malformed bearer %s before parsing or forwarding', async authorization => {
  const input = request(authorization); input.formData = jest.fn();
  expect((await POST(input)).status).toBe(401);
  expect(input.formData).not.toHaveBeenCalled(); expect(proxy).not.toHaveBeenCalled();
});
it('reports malformed multipart without forwarding', async () => {
  const input = request(); input.formData = async () => { throw new Error('malformed'); };
  expect((await POST(input)).status).toBe(400); expect(proxy).not.toHaveBeenCalled();
});
