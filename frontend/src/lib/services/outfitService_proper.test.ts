// Keep Jest types local; Cypress also declares global test functions.
declare const beforeEach: jest.Lifecycle;
declare const describe: jest.Describe;
declare const expect: jest.Expect;
declare const it: jest.It;
import outfitService from './outfitService_proper';

jest.mock('@/lib/firebase/config', () => ({ auth: { currentUser: { uid: 'user-1' } } }));

const draft = {
  name: 'Two-piece look', occasion: 'Casual', style: 'Classic', user_id: 'user-1',
  items: [{ id: 'shirt-1', name: 'Shirt', category: 'top', style: 'Classic', color: 'blue', user_id: 'user-1' }],
  notes: 'Keep these pieces together',
};

beforeEach(() => { jest.clearAllMocks(); global.fetch = jest.fn(); });

describe('manual outfit response contract', () => {
  it('sends only editable creation fields and saved garment IDs from legacy caller payloads', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ id: 'saved-1' }) });
    await outfitService.createOutfit({
      ...draft, userId: 'other', uid: 'other', wearCount: 900, createdAt: 123,
      flat_lay_status: 'done', flat_lay_url: '/forged.png',
      metadata: { flat_lay_requested: true }, subscription: { role: 'tier3' },
    } as any, 'test-token');
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, request] = (fetch as jest.Mock).mock.calls[0];
    expect(url).toBe('/api/outfits');
    expect(request).toMatchObject({ method: 'POST', cache: 'no-store', headers: { Authorization: 'Bearer test-token' } });
    expect(JSON.parse(request.body)).toEqual({
      name: draft.name, occasion: 'Casual', style: 'Classic', notes: draft.notes,
      items: [{ id: 'shirt-1' }],
    });
  });

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

describe('canonical outfit mutations', () => {
  it('sends only editable fields and reads the confirmed saved version', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => ({ success: true, id: 'saved-1' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ ...draft, id: 'saved-1', flat_lay_url: null }) });
    const result = await outfitService.updateOutfit('saved-1', { name: 'New name', items: draft.items, flat_lay_url: '/forged.png', user_id: 'other' } as any, 'token');
    expect(fetch).toHaveBeenNthCalledWith(1, '/api/outfits/saved-1', expect.objectContaining({ method: 'PUT', body: JSON.stringify({ name: 'New name', items: draft.items }), cache: 'no-store' }));
    expect(fetch).toHaveBeenNthCalledWith(2, '/api/outfits/saved-1', expect.objectContaining({ cache: 'no-store' }));
    expect(result).toMatchObject({ id: 'saved-1', flat_lay_url: null });
  });
  it.each([{}, {success: false, id: 'saved-1'}, {success: true, id: 'other'}])('does not confirm an invalid update receipt %j', async body => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => body });
    await expect(outfitService.updateOutfit('saved-1', { name: 'New' }, 'token')).rejects.toThrow('did not confirm');
    expect(fetch).toHaveBeenCalledTimes(1);
  });
  it.each([{}, {success: true, id: 'other', deleted: true}, {success: true, id: 'saved-1'}])('does not confirm an invalid delete receipt %j', async body => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => body });
    await expect(outfitService.deleteOutfit('saved-1', 'token')).rejects.toThrow('did not confirm');
  });
  it('confirms the canonical deletion receipt', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, id: 'saved-1', deleted: true }) });
    await expect(outfitService.deleteOutfit('saved-1', 'token')).resolves.toBeUndefined();
  });
  it('preserves structured onboarding admission failures', async () => {
    (fetch as jest.Mock).mockResolvedValue({ ok: false, status: 409, json: async () => ({ detail: { code: 'onboarding_required', resume: '/onboarding' } }) });
    await expect(outfitService.createOutfit(draft, 'token')).rejects.toMatchObject({ status: 409, code: 'onboarding_required' });
  });
});
