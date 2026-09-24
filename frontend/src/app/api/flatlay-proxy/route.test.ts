/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { GET } from './route';
const original = { ...process.env };
const originalFetch = global.fetch;
const request = (url: string) => new Request('https://easyoutfit.example/api/flatlay-proxy?url=' + encodeURIComponent(url));
const allowed = 'https://storage.googleapis.com/closetgptrenew.firebasestorage.app/flat_lays/look.png';
beforeEach(() => { process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'closetgptrenew.firebasestorage.app'; global.fetch = jest.fn(); });
afterAll(() => { process.env = original; global.fetch = originalFetch; });
it.each([
  'https://storage.googleapis.com.evil.example/closetgptrenew.firebasestorage.app/x.png',
  'https://evil.example/?storage.googleapis.com',
  'http://storage.googleapis.com/closetgptrenew.firebasestorage.app/x.png',
  'https://user:pass@storage.googleapis.com/closetgptrenew.firebasestorage.app/x.png',
  'https://storage.googleapis.com:444/closetgptrenew.firebasestorage.app/x.png',
  'https://storage.googleapis.com/other-bucket/x.png',
  'https://firebasestorage.googleapis.com/v0/b/other-bucket/o/x.png',
  'https://storage.googleapis.com/closetgptrenew.firebasestorage.app/a%2f..%2fb.png',
])('rejects an unsafe source without fetching %s', async url => {
  expect((await GET(request(url))).status).toBe(400); expect(fetch).not.toHaveBeenCalled();
});
it.each([allowed, 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/flat_lays%2Flook.png?alt=media&token=opaque'])('preserves image bytes and uses bounded private fetching for %s', async url => {
  const bytes = new Uint8Array([137, 80, 78, 71, 0, 13, 10]);
  (fetch as jest.Mock).mockResolvedValue(new Response(bytes, { headers: { 'content-type': 'image/png' } }));
  const result = await GET(request(url));
  expect(result.status).toBe(200); expect(new Uint8Array(await result.arrayBuffer())).toEqual(bytes);
  expect(result.headers.get('cache-control')).toBe('private, no-store');
  expect(fetch).toHaveBeenCalledWith(url, expect.objectContaining({ cache: 'no-store', redirect: 'error', signal: expect.any(AbortSignal) }));
});
it('does not follow redirect or expose upstream errors', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('secret upstream URL'));
  const result = await GET(request(allowed));
  expect(result.status).toBe(502); expect(await result.text()).not.toContain('secret'); expect(fetch).toHaveBeenCalledTimes(1);
});
it.each(['text/html', 'image/svg+xml'])('rejects invalid content type %s', async type => {
  (fetch as jest.Mock).mockResolvedValue(new Response('not an allowed image', { headers: { 'content-type': type } }));
  expect((await GET(request(allowed))).status).toBe(502);
});
it('enforces the byte limit without trusting Content-Length', async () => {
  (fetch as jest.Mock).mockResolvedValue(new Response(new Uint8Array(4 * 1024 * 1024 + 1), { headers: { 'content-type': 'image/png' } }));
  expect((await GET(request(allowed))).status).toBe(413);
});
it('fails closed without a configured bucket', async () => {
  delete process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET;
  expect((await GET(request(allowed))).status).toBe(503); expect(fetch).not.toHaveBeenCalled();
});
