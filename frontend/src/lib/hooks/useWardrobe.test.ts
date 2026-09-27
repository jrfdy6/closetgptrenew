import { act, renderHook, waitFor } from '@testing-library/react';
import { useWardrobe, type ClothingItem } from './useWardrobe';
import { WardrobeService } from '@/lib/services/wardrobeService';
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;

let mockUser: { uid: string } | null;
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser }) }));
jest.mock('@/lib/services/wardrobeService', () => ({ WardrobeService: { getWardrobeItems: jest.fn(), addWardrobeItem: jest.fn(), updateWardrobeItem: jest.fn(), deleteWardrobeItem: jest.fn(), toggleFavorite: jest.fn(), incrementWearCount: jest.fn() } }));
const reads = WardrobeService.getWardrobeItems as jest.Mock;
const item = (owner: string, wearCount: number): ClothingItem => ({ id: 'shirt', userId: owner, name: owner + ' private shirt', wearCount, favorite: false, type: 'shirt', color: 'blue', imageUrl: '/fixture.jpg', createdAt: new Date(0), updatedAt: new Date(0) });
function deferred<T>() { let resolve!: (value: T) => void; let reject!: (reason: Error) => void; const promise = new Promise<T>((done, fail) => { resolve = done; reject = fail; }); return { promise, resolve, reject }; }
beforeEach(() => { mockUser = { uid: 'owner-a' }; jest.clearAllMocks(); Object.values(WardrobeService).forEach(value => { if (jest.isMockFunction(value)) value.mockReset(); }); });
afterEach(() => { jest.restoreAllMocks(); });

it('keeps the newer wardrobe count after an older refresh resolves last', async () => {
  const old = deferred<unknown[]>();
  reads.mockReturnValueOnce(old.promise).mockResolvedValueOnce([item('owner-a', 2)]);
  const { result } = renderHook(useWardrobe);
  await waitFor(() => expect(reads).toHaveBeenCalledTimes(1));
  await act(async () => { await result.current.refetch(); });
  expect(result.current.items[0].wearCount).toBe(2);
  await act(async () => { old.resolve([item('owner-a', 1)]); });
  expect(result.current.items[0].wearCount).toBe(2);
});

it('does not restore private rows when a pending read completes after sign-out', async () => {
  const old = deferred<unknown[]>(); reads.mockReturnValueOnce(old.promise);
  const { result, rerender } = renderHook(useWardrobe);
  await waitFor(() => expect(reads).toHaveBeenCalledTimes(1));
  mockUser = null; rerender();
  expect(result.current.items).toEqual([]);
  await act(async () => { old.resolve([item('owner-a', 1)]); });
  expect(result.current.items).toEqual([]);
});

it('does not replace the new account wardrobe with the previous account response', async () => {
  const old = deferred<unknown[]>();
  reads.mockReturnValueOnce(old.promise).mockResolvedValueOnce([item('owner-b', 3)]);
  const { result, rerender } = renderHook(useWardrobe);
  await waitFor(() => expect(reads).toHaveBeenCalledTimes(1));
  mockUser = { uid: 'owner-b' }; rerender();
  await waitFor(() => expect(result.current.items[0]?.userId).toBe('owner-b'));
  await act(async () => { old.resolve([item('owner-a', 1)]); });
  expect(result.current.items[0].userId).toBe('owner-b');
});

it('hides old rows immediately while the next account wardrobe is loading', async () => {
  const next = deferred<unknown[]>();
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockReturnValueOnce(next.promise);
  const { result, rerender } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.items).toHaveLength(1));
  mockUser = { uid: 'owner-b' }; rerender();
  expect(result.current.items).toEqual([]);
});


it('ignores an older read failure without clearing the newest loading state', async () => {
  const old = deferred<ClothingItem[]>(); const latest = deferred<ClothingItem[]>();
  reads.mockReturnValueOnce(old.promise).mockReturnValueOnce(latest.promise);
  const { result } = renderHook(useWardrobe);
  await act(async () => { void result.current.refetch(); });
  await act(async () => { old.reject(new Error('Old error')); });
  expect(result.current.error).toBeNull(); expect(result.current.loading).toBe(true);
  await act(async () => { latest.resolve([item('owner-a', 4)]); });
  expect(result.current.loading).toBe(false); expect(result.current.items[0].wearCount).toBe(4);
});

it('retains rows on a current read error and recovers on explicit refresh', async () => {
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockRejectedValueOnce(new Error('Offline')).mockResolvedValueOnce([item('owner-a', 2)]);
  const { result } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { await result.current.refetch(); });
  expect(result.current.error).toBe('Offline'); expect(result.current.items[0].wearCount).toBe(1);
  await act(async () => { await result.current.refetch(); });
  expect(result.current.error).toBeNull(); expect(result.current.items[0].wearCount).toBe(2);
});

type Hook = ReturnType<typeof useWardrobe>;
const mutations: Array<[string, keyof typeof WardrobeService, (hook: Hook) => Promise<unknown>, unknown]> = [
  ['add', 'addWardrobeItem', hook => hook.addItem(item('owner-a', 1)), { ...item('owner-a', 1), id: 'new-shirt' }],
  ['update', 'updateWardrobeItem', hook => hook.updateItem('shirt', { name: 'Changed' }), undefined],
  ['delete', 'deleteWardrobeItem', hook => hook.deleteItem('shirt'), undefined],
  ['favorite', 'toggleFavorite', hook => hook.toggleFavorite('shirt'), undefined],
  ['wear', 'incrementWearCount', hook => hook.incrementWearCount('shirt'), { newWearCount: 9, lastWorn: 1790100000000 }],
];
it.each(mutations)('ignores a late %s acknowledgement after account change', async (_name, method, invoke, acknowledgement) => {
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockResolvedValueOnce([item('owner-b', 3)]);
  const pending = deferred<unknown>(); (WardrobeService[method] as jest.Mock).mockReturnValueOnce(pending.promise);
  const { result, rerender } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  let mutation!: Promise<unknown>;
  await act(async () => { mutation = invoke(result.current); });
  mockUser = { uid: 'owner-b' }; rerender();
  await waitFor(() => expect(result.current.items[0]?.userId).toBe('owner-b'));
  await act(async () => { pending.resolve(acknowledgement); await mutation; });
  expect(result.current.items).toEqual([item('owner-b', 3)]); expect(result.current.error).toBeNull();
});

it('does not surface a prior account mutation error on the new account', async () => {
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockResolvedValueOnce([item('owner-b', 3)]);
  const pending = deferred<void>(); (WardrobeService.updateWardrobeItem as jest.Mock).mockReturnValueOnce(pending.promise);
  const { result, rerender } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  let mutation!: Promise<void>;
  await act(async () => { mutation = result.current.updateItem('shirt', { name: 'Old name' }); });
  mockUser = { uid: 'owner-b' }; rerender();
  await waitFor(() => expect(result.current.items[0]?.userId).toBe('owner-b'));
  await act(async () => { pending.reject(new Error('Old account failed')); await mutation; });
  expect(result.current.error).toBeNull(); expect(result.current.items[0].name).toBe('owner-b private shirt');
});

it('keeps acknowledged wear totals when an older read later resolves', async () => {
  const old = deferred<ClothingItem[]>();
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockReturnValueOnce(old.promise);
  (WardrobeService.incrementWearCount as jest.Mock).mockResolvedValue({ newWearCount: 4, lastWorn: 1790100000 });
  const { result } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { void result.current.refetch(); });
  await act(async () => { await result.current.incrementWearCount('shirt'); });
  expect(result.current.items[0].wearCount).toBe(4);
  expect(result.current.items[0].lastWorn?.getTime()).toBe(1790100000000);
  await act(async () => { old.resolve([item('owner-a', 1)]); });
  expect(result.current.items[0].wearCount).toBe(4); expect(result.current.loading).toBe(false);
});

it('preserves legitimate add, update, favorite and delete results', async () => {
  reads.mockResolvedValue([item('owner-a', 1)]);
  (WardrobeService.addWardrobeItem as jest.Mock).mockResolvedValue({ ...item('owner-a', 0), id: 'new-shirt' });
  const { result } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { await result.current.addItem(item('owner-a', 0)); });
  expect(result.current.items).toHaveLength(2);
  await act(async () => { await result.current.updateItem('shirt', { name: 'Updated' }); });
  expect(result.current.items[0].name).toBe('Updated');
  await act(async () => { await result.current.toggleFavorite('shirt'); });
  expect(result.current.items[0].favorite).toBe(true);
  expect(WardrobeService.toggleFavorite).toHaveBeenCalledTimes(1);
  expect(WardrobeService.toggleFavorite).toHaveBeenCalledWith('shirt', true);
  await act(async () => { await result.current.deleteItem('new-shirt'); });
  expect(result.current.items.map(row => row.id)).toEqual(['shirt']);
});

it('reports a current favorite error without claiming an unsaved change', async () => {
  reads.mockResolvedValue([item('owner-a', 1)]);
  (WardrobeService.toggleFavorite as jest.Mock).mockRejectedValue(new Error('Save failed'));
  const { result } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  await act(async () => { await expect(result.current.toggleFavorite('shirt')).rejects.toThrow('Save failed'); });
  expect(result.current.error).toBe('Save failed'); expect(result.current.items[0].favorite).toBe(false);
});

it('does not dispatch callbacks from a previous account session or after unmount', async () => {
  reads.mockResolvedValue([item('owner-a', 1)]);
  const { result, rerender, unmount } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  const old = result.current;
  mockUser = { uid: 'owner-b' }; rerender();
  await waitFor(() => expect(result.current.loading).toBe(false));
  mockUser = { uid: 'owner-a' }; rerender();
  await waitFor(() => expect(result.current.loading).toBe(false));
  const readCount = reads.mock.calls.length;
  await act(async () => { await old.refetch(); await old.updateItem('shirt', { name: 'Stale' }); });
  expect(reads).toHaveBeenCalledTimes(readCount); expect(WardrobeService.updateWardrobeItem).not.toHaveBeenCalled();
  const last = result.current; unmount();
  await act(async () => { await last.refetch(); await last.incrementWearCount('shirt'); });
  expect(reads).toHaveBeenCalledTimes(readCount); expect(WardrobeService.incrementWearCount).not.toHaveBeenCalled();
});

it('ignores reads and mutation completion after unmount', async () => {
  const read = deferred<ClothingItem[]>(); const mutation = deferred<void>();
  reads.mockResolvedValueOnce([item('owner-a', 1)]).mockReturnValueOnce(read.promise);
  (WardrobeService.updateWardrobeItem as jest.Mock).mockReturnValueOnce(mutation.promise);
  const { result, unmount } = renderHook(useWardrobe);
  await waitFor(() => expect(result.current.loading).toBe(false));
  let update!: Promise<void>;
  await act(async () => { void result.current.refetch(); update = result.current.updateItem('shirt', { name: 'After unmount' }); });
  const lastItems = result.current.items; unmount();
  await act(async () => { read.resolve([item('owner-a', 8)]); mutation.resolve(); await update; });
  expect(result.current.items).toBe(lastItems);
});
