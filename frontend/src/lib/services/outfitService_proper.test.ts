// Keep Jest types local; Cypress also declares global test functions.
declare const beforeEach: jest.Lifecycle;
declare const describe: jest.Describe;
declare const expect: jest.Expect;
declare const it: jest.It;
import outfitService from './outfitService_proper';

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

describe('outfit server authority', () => {
  it('sends item changes to the server and uses the confirmed projection', async () => {
    const saved = { ...draft, id: 'saved-1', flat_lay_url: null, flat_lay_status: 'awaiting_consent' };
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ outfit: saved }) });
    const items = [{ ...draft.items[0], id: 'new-shirt' }];
    await expect(outfitService.updateOutfit('saved-1', { items }, 'token')).resolves.toEqual(saved);
    expect(fetch).toHaveBeenCalledWith('/api/outfits/saved-1', expect.objectContaining({
      method: 'PUT', body: JSON.stringify({ items }), headers: expect.objectContaining({ Authorization: 'Bearer token' }),
    }));
  });
  it('does not send generated projection, identity or creation fields on an edit', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ id: 'saved-1' }) });
    await outfitService.updateOutfit('saved-1', { name: 'Renamed', user_id: 'other', flat_lay_url: '/forged.png', metadata: { flatLayStatus: 'done' }, updatedAt: 1 } as any, 'token');
    expect(JSON.parse((fetch as jest.Mock).mock.calls[0][1].body)).toEqual({ name: 'Renamed' });
  });
  it('keeps the idempotency ID but excludes authority from a fallback create', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ id: 'saved-1' }) });
    await outfitService.createOutfit({ ...draft, id: 'saved-1', flatLayUrl: '/forged.png' } as any, 'token');
    const sent = JSON.parse((fetch as jest.Mock).mock.calls[0][1].body);
    expect(sent.id).toBe('saved-1');
    expect(sent).not.toHaveProperty('user_id');
    expect(sent).not.toHaveProperty('flatLayUrl');
  });
  it('keeps authorization failures visible to the editor', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 403, json: async () => ({ error: 'Access denied' }) });
    await expect(outfitService.updateOutfit('saved-1', { notes: 'Test' }, 'token')).rejects.toThrow('Access denied');
  });
});
