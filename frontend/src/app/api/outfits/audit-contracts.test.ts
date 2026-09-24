/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { POST } from './route';
import { GET as topWorn } from '../wardrobe/top-worn-items/route';
import { GET as coverage } from '../wardrobe/coverage/route';
const env = { ...process.env };
const originalFetch = global.fetch;
beforeEach(() => { process.env.BACKEND_URL = 'https://railway.example'; global.fetch = jest.fn(); });
afterAll(() => { process.env = env; global.fetch = originalFetch; });
it.each([{ items: [{ id: 'shirt' }] }, { occasion: 'Casual' }])('preserves structured admission errors for manual or generated creation %j', async body => {
  const detail = { code: 'onboarding_required', resume: '/onboarding', stage: 'capsule', profile_complete: true, capsule: { ready: false } };
  (fetch as jest.Mock).mockResolvedValue(Response.json({ detail }, { status: 409 }));
  const response = await POST(new Request('https://app.example/api/outfits', { method: 'POST', headers: { Authorization: 'Bearer signed-token', 'Content-Type': 'application/json' }, body: JSON.stringify(body) }));
  expect(response.status).toBe(409); expect(await response.json()).toEqual({ detail });
  expect(response.headers.get('cache-control')).toBe('private, no-store');
  expect(fetch).toHaveBeenCalledTimes(1);
});
it('does not replace a forbidden wardrobe request with mock items', async () => {
  (fetch as jest.Mock).mockResolvedValue(Response.json({ detail: 'Forbidden' }, { status: 403 }));
  const response = await topWorn(new Request('https://app.example/api/wardrobe/top-worn-items', { headers: { Authorization: 'Bearer signed-token' } }));
  expect(response.status).toBe(403); expect(await response.json()).toEqual({ detail: 'Forbidden' });
});
it('marks an unsupported insight as unavailable, never a successful empty insight', async () => {
  const response = await coverage(new Request('https://app.example/api/wardrobe/coverage', { headers: { Authorization: 'Bearer signed-token' } }));
  expect(response.status).toBe(503); expect(await response.json()).toMatchObject({ success: false, available: false });
  expect(fetch).not.toHaveBeenCalled();
});
