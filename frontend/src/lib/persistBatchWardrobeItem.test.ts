declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { persistBatchWardrobeItem } from './persistBatchWardrobeItem';
let originalFetch: typeof fetch;
let mockFetch: jest.Mock;
const user = { getIdToken: async () => 'upload-test-token' };
beforeEach(() => { originalFetch = global.fetch; mockFetch = jest.fn(); global.fetch = mockFetch; });
afterEach(() => { global.fetch = originalFetch; });
it('returns the persisted record rather than the staged garment', async () => {
  const saved = { id: 'persisted-id', name: 'Saved shirt', userId: 'test-user' };
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true, item: saved }) });
  expect(await persistBatchWardrobeItem({ name: 'Staged shirt' }, user)).toEqual(saved);
  expect(mockFetch).toHaveBeenCalledWith('/api/wardrobe', expect.objectContaining({ method: 'POST', headers: expect.objectContaining({ Authorization: 'Bearer upload-test-token' }) }));
});
it.each([
  { ok: false, body: { success: true, item: { id: 'not-saved' } } },
  { ok: true, body: { success: false, error: 'DB unavailable' } },
  { ok: true, body: { success: true } },
  { ok: true, body: { success: true, item: { id: '' } } },
])('rejects an unconfirmed save %j', async ({ ok, body }) => {
  mockFetch.mockResolvedValue({ ok, json: async () => body });
  await expect(persistBatchWardrobeItem({ id: 'staged-id' }, user)).rejects.toThrow('not confirmed saved');
});
