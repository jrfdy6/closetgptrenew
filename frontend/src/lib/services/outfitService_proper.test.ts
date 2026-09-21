// Keep Jest types local; Cypress also declares global test functions.
declare const beforeEach: jest.Lifecycle;
declare const describe: jest.Describe;
declare const expect: jest.Expect;
declare const it: jest.It;
import outfitService from './outfitService_proper';
import { doc, getDoc, updateDoc } from 'firebase/firestore';

jest.mock('@/lib/firebase/config', () => ({ db: {} }));
jest.mock('firebase/firestore', () => ({ doc: jest.fn(), getDoc: jest.fn(), updateDoc: jest.fn() }));

const draft = {
  name: 'Two-piece look', occasion: 'Casual', style: 'Classic', user_id: 'user-1',
  items: [{ id: 'shirt-1', name: 'Shirt', category: 'top', style: 'Classic', color: 'blue', user_id: 'user-1' }],
  notes: 'Keep these pieces together',
};

beforeEach(() => { jest.clearAllMocks(); global.fetch = jest.fn(); });

describe('manual outfit response contract', () => {
  it.each([
    { outfit_id: 'saved-1' },
    { id: 'saved-1' },
    { outfit: { outfit_id: 'saved-1', ...draft } },
    { data: { id: 'saved-1', ...draft } },
  ])('normalizes a confirmed ID and preserves submitted fields: %j', async payload => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => payload });
    await expect(outfitService.createOutfit(draft, 'test-token')).resolves.toMatchObject({ ...draft, id: 'saved-1' });
  });

  it.each([null, {}, { success: false }, { success: false, outfit_id: 'unconfirmed' }])(
    'does not report success without confirmation: %j', async payload => {
      (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => payload });
      await expect(outfitService.createOutfit(draft, 'test-token')).rejects.toThrow('did not confirm');
    }
  );

  it('propagates a failed save instead of fabricating an outfit', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 503, json: async () => ({ error: 'Please retry later' }) });
    await expect(outfitService.createOutfit(draft, 'test-token')).rejects.toThrow('Please retry later');
  });

  it.each([true, false])('sends the requested favorite state %s in one PUT', async isFavorite => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ isFavorite }) });
    await outfitService.setOutfitFavorite('outfit-1', isFavorite, 'test-token');
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith('/api/outfits/outfit-1/favorite', expect.objectContaining({
      method: 'PUT', body: JSON.stringify({ isFavorite }),
      headers: expect.objectContaining({ Authorization: 'Bearer test-token' }),
    }));
  });
});

describe('edited outfit preview identity', () => {
  const current = { ...draft, flat_lay_status: 'done', flat_lay_url: '/old.png', metadata: { flatLayUrl: '/old.png', preserved: 'keep' } };
  function setup(data = current) {
    (doc as jest.Mock).mockReturnValue({ id: 'saved-1' });
    (getDoc as jest.Mock).mockResolvedValue({ id: 'saved-1', exists: () => true, data: () => data });
    (updateDoc as jest.Mock).mockResolvedValue(undefined);
  }
  it('clears the old preview atomically when the item set changes and preserves metadata siblings', async () => {
    setup();
    await outfitService.updateOutfit('saved-1', { items: [{ ...draft.items[0], id: 'new-shirt' }] }, 'token');
    expect(updateDoc).toHaveBeenCalledTimes(1);
    expect((updateDoc as jest.Mock).mock.calls[0][1]).toMatchObject({
      items: [expect.objectContaining({ id: 'new-shirt' })], flat_lay_url: null, flatLayUrl: null,
      'metadata.flat_lay_url': null, 'metadata.flatLayUrl': null,
      flat_lay_status: 'awaiting_consent', flat_lay_request_allowed: true,
    });
    expect((updateDoc as jest.Mock).mock.calls[0][1]).not.toHaveProperty('metadata');
  });
  it.each(['pending', 'processing'])('does not reopen or cancel an active %s job when editing items', async status => {
    setup({ ...current, flat_lay_status: status });
    await outfitService.updateOutfit('saved-1', { items: [] }, 'token');
    const update = (updateDoc as jest.Mock).mock.calls[0][1];
    expect(update.flat_lay_url).toBeNull();
    expect(update).not.toHaveProperty('flat_lay_status');
    expect(update).not.toHaveProperty('flat_lay_request_allowed');
  });
  it('preserves previews when only the outfit name changes', async () => {
    setup();
    await outfitService.updateOutfit('saved-1', { name: 'A new title', items: current.items }, 'token');
    expect((updateDoc as jest.Mock).mock.calls[0][1]).not.toHaveProperty('flat_lay_url');
  });
});
