// Keep Jest assertions local to this module when Cypress also contributes globals.
declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;

import { WardrobeService } from './wardrobeService';

jest.mock('@/lib/firebase/config', () => ({
  auth: { currentUser: { getIdToken: jest.fn().mockResolvedValue('test-token') } },
}));

const fetchMock = jest.fn();
const readPayload = () => JSON.parse(fetchMock.mock.calls[0][1].body);

describe('Wardrobe service update contract', () => {
  beforeEach(() => {
    global.fetch = fetchMock;
    fetchMock.mockReset().mockResolvedValue({ ok: true, json: async () => ({ success: true }) });
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });
  afterEach(() => jest.restoreAllMocks());

  it('leaves unrelated fields out of a name update', async () => {
    await WardrobeService.updateWardrobeItem('shirt-1', { name: 'Oxford shirt' });
    expect(readPayload()).toEqual({ name: 'Oxford shirt' });
  });

  it('nests only changed metadata and includes all selected materials in the scalar contract', async () => {
    await WardrobeService.updateWardrobeItem('shirt-1', { material: ['cotton', 'linen'], fit: 'slim' });
    expect(readPayload()).toEqual({ metadata: { visualAttributes: { material: 'cotton, linen', fit: 'slim' } } });
  });

  it('persists purchase price, including zero, and favorite false', async () => {
    await WardrobeService.updateWardrobeItem('shirt-1', { purchasePrice: 0, favorite: false });
    expect(readPayload()).toEqual({ purchasePrice: 0, favorite: false });
  });

  it('preserves explicit cleared description, material selection, and statement level', async () => {
    await WardrobeService.updateWardrobeItem('shirt-1', { description: '', material: [], statementLevel: 0 });
    expect(readPayload()).toEqual({ metadata: { naturalDescription: '', visualAttributes: { material: '', statementLevel: 0 } } });
  });

  it('rehydrates all materials without nesting legacy arrays and preserves explicit empty/zero values', async () => {
    fetchMock.mockResolvedValue({ ok: true, json: async () => ({ items: [
      { id: 'one', metadata: { naturalDescription: '', visualAttributes: { material: 'cotton, linen', statementLevel: 0 } },
        description: 'Old description', statementLevel: 9 },
      { id: 'two', metadata: { visualAttributes: { material: ['Cotton', 'Linen'] } } },
      { id: 'three', metadata: { visualAttributes: { material: '' } }, material: 'old wool' },
    ] }) });
    const items = await WardrobeService.getWardrobeItems();
    expect(items[0].material).toEqual(['cotton', 'linen']);
    expect(items[0].description).toBe('');
    expect(items[0].statementLevel).toBe(0);
    expect(items[1].material).toEqual(['Cotton', 'Linen']);
    expect(items[2].material).toEqual([]);
  });

  it('sends favorite independently of editor metadata', async () => {
    await WardrobeService.toggleFavorite('shirt-1', true);
    expect(readPayload()).toEqual({ favorite: true });
  });
});
