declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React, { useState } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import BatchImageUpload from './BatchImageUpload';
import { persistBatchWardrobeItem } from '@/lib/persistBatchWardrobeItem';
import { prepareCapsulePhoto, photoHash } from '@/lib/onboarding/capsulePhoto';
let mockOnDrop: (files: File[]) => Promise<void>;
let mockReject: () => void;
const mockUser = { uid: 'test-owner', getIdToken: jest.fn() };
jest.mock('react-dropzone', () => ({ useDropzone: ({ onDrop, onDropRejected }: any) => { mockOnDrop = onDrop; mockReject = onDropRejected; return { getRootProps: () => ({}), getInputProps: () => ({}), isDragActive: false }; } }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser }) }));
jest.mock('@/lib/publicBackendUrl', () => ({ getPublicBackendUrl: () => 'https://api.example.test' }));
jest.mock('@/lib/persistBatchWardrobeItem', () => ({ persistBatchWardrobeItem: jest.fn() }));
jest.mock('@/lib/onboarding/capsulePhoto', () => ({ prepareCapsulePhoto: jest.fn(), photoHash: jest.fn() }));
let originalFetch: typeof fetch;
let mockFetch: jest.Mock;
let analysisPending = false;
let wardrobeItems: any[] = [];
beforeEach(() => {
  mockUser.uid = 'test-owner';
  mockUser.getIdToken.mockReset().mockResolvedValue('upload-test-token');
  (prepareCapsulePhoto as jest.Mock).mockReset().mockImplementation(async (file: File) => file);
  (photoHash as jest.Mock).mockReset().mockImplementation(async (file: File) => `sha256:${file.name}`);
  originalFetch = global.fetch;
  URL.createObjectURL = jest.fn(() => 'blob:test'); URL.revokeObjectURL = jest.fn();
  let sequence = 0;
  Object.defineProperty(global.crypto, 'randomUUID', { configurable: true, value: () => `test-${++sequence}` });
  wardrobeItems = []; analysisPending = false;
  mockFetch = jest.fn(async url => ({ ok: true, json: async () => url === '/api/wardrobe' ? { success: true, items: wardrobeItems } : url.endsWith('/api/image/upload') ? { success: true, image_url: 'https://images.example.test/shirt.jpg' } : { analysis: { name: 'White shirt', type: 'shirt', color: 'white', metadata: { visualAttributes: { pattern: 'solid' } } }, ...(analysisPending ? { analysis_status: 'pending', client_item_id: 'ignored-foreign-id' } : {}) } }));
  global.fetch = mockFetch;
  (persistBatchWardrobeItem as jest.Mock).mockReset();
});
afterEach(() => { global.fetch = originalFetch; jest.restoreAllMocks(); });
const choose = async (...names: string[]) => { await act(async () => { await mockOnDrop(names.map(name => new File([name], name, { type: 'image/jpeg' }))); }); };
const start = () => fireEvent.click(screen.getByRole('button', { name: /^Save \d+ item/ }));
it.each(['normal', 'codex', 'quick'])('keeps a failed %s save out of completed garments and retries only save with stable identity', async mode => {
  analysisPending = mode === 'codex';
  (persistBatchWardrobeItem as jest.Mock).mockRejectedValueOnce(new Error('This item was not confirmed saved. Please retry.')).mockImplementation(async item => item);
  const onComplete = jest.fn();
  render(<BatchImageUpload userId="test-owner" quickMode={mode === 'quick'} onUploadComplete={onComplete} />);
  await choose('shirt.jpg'); start();
  expect(await screen.findByRole('alert')).toHaveTextContent('not confirmed saved');
  expect(onComplete).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Retry save' }));
  await waitFor(() => expect(onComplete).toHaveBeenCalledTimes(1));
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(1);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/analyze-image'))).toHaveLength(1);
  const saves = (persistBatchWardrobeItem as jest.Mock).mock.calls;
  expect(saves[0][0]).toBe(saves[1][0]);
  expect(saves[0][0].id).toBe('item-test-1');
});
it('saves one item without staging ten and retains nested analysis', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => ({ ...item, confirmed: true }));
  const complete = jest.fn();
  render(<BatchImageUpload userId="test-owner" requireStaging requiredCount={10} onUploadComplete={complete} />);
  await choose('shirt.jpg'); start();
  await waitFor(() => expect(complete).toHaveBeenCalledWith([expect.objectContaining({ confirmed: true, analysis: { name: 'White shirt', type: 'shirt', color: 'white', metadata: { visualAttributes: { pattern: 'solid' } } } })]));
});
it('partial retry never replays successful siblings or completes before all selected work resolves', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockResolvedValueOnce({ id: 'first', userId: 'test-owner' }).mockRejectedValueOnce(new Error('Not confirmed saved')).mockResolvedValueOnce({ id: 'second', userId: 'test-owner' });
  const complete = jest.fn();
  const itemSaved = jest.fn();
  render(<BatchImageUpload userId="test-owner" onUploadComplete={complete} onItemSaved={itemSaved} />);
  await choose('first.jpg', 'second.jpg'); start();
  await screen.findByRole('button', { name: 'Retry save' });
  expect(complete).not.toHaveBeenCalled();
  expect(itemSaved).toHaveBeenCalledTimes(1);
  start();
  await waitFor(() => expect(complete).toHaveBeenCalledTimes(1));
  expect(itemSaved).toHaveBeenCalledTimes(2);
  expect(complete).toHaveBeenCalledWith([{ id: 'first', userId: 'test-owner' }, { id: 'second', userId: 'test-owner' }]);
  expect(persistBatchWardrobeItem).toHaveBeenCalledTimes(3);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(2);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/analyze-image'))).toHaveLength(2);
});
it('retries failed analysis using its uploaded original', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => item);
  let analyses = 0;
  const defaultFetch = mockFetch.getMockImplementation()!;
  mockFetch.mockImplementation(async (...args) => args[0].endsWith('/analyze-image') && ++analyses === 1 ? { ok: false, json: async () => ({}) } : defaultFetch(...args));
  render(<BatchImageUpload userId="test-owner" />);
  await choose('shirt.jpg'); start();
  fireEvent.click(await screen.findByRole('button', { name: 'Retry analysis' }));
  await screen.findByText('Saved to your wardrobe');
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(1);
  expect(analyses).toBe(2);
});
it('detects exact known and same-selection duplicates without a storage write', async () => {
  wardrobeItems = [{ id: 'old', contentHash: 'sha256:old.jpg' }];
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => item);
  render(<BatchImageUpload userId="test-owner" />);
  await choose('old.jpg', 'new.jpg', 'new.jpg');
  expect(screen.getAllByText('Already added')).toHaveLength(2);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(0);
  start(); await screen.findByText('Saved to your wardrobe');
  expect(persistBatchWardrobeItem).toHaveBeenCalledTimes(1);
});
it('does not treat a failed wardrobe lookup as empty', async () => {
  mockFetch.mockResolvedValue({ ok: false, json: async () => ({ success: false, items: [] }) });
  render(<BatchImageUpload userId="test-owner" />);
  await choose('shirt.jpg');
  expect(await screen.findByRole('alert')).toHaveTextContent('could not check your saved photos');
  expect(screen.queryByText('Ready to upload')).not.toBeInTheDocument();
});
it('keeps accepted selections when an unsupported photo is rejected', async () => {
  render(<BatchImageUpload userId="test-owner" />);
  await choose('shirt.jpg');
  act(() => mockReject());
  expect(screen.getByRole('alert')).toHaveTextContent('up to 10 MB');
  expect(screen.getByText('shirt.jpg')).toBeVisible();
});
it('warns before leaving unsaved work and removes the warning after acknowledgment', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => item);
  render(<BatchImageUpload userId="test-owner" />);
  await choose('shirt.jpg');
  const unsaved = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(unsaved); expect(unsaved.defaultPrevented).toBe(true);
  start(); await screen.findByText('Saved to your wardrobe');
  const saved = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(saved); expect(saved.defaultPrevented).toBe(false);
});
it('rejects old placeholder fallback upload acknowledgments before analysis or save', async () => {
  const original = mockFetch.getMockImplementation()!;
  mockFetch.mockImplementation(async (...args) => args[0].endsWith('/api/image/upload') ? { ok: true, json: async () => ({ success: true, fallback: true, image_url: 'https://picsum.photos/placeholder' }) } : original(...args));
  render(<BatchImageUpload userId="test-owner" />);
  await choose('shirt.jpg'); start();
  expect(await screen.findByRole('alert')).toHaveTextContent('Photo upload failed');
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/analyze-image'))).toHaveLength(0);
  expect(persistBatchWardrobeItem).not.toHaveBeenCalled();
});

function ClosingUploadDialog({ complete }: { complete: jest.Mock }) {
  const [open, setOpen] = useState(true);
  return open ? <div role="dialog" aria-label="Add wardrobe items"><BatchImageUpload userId="test-owner" onUploadComplete={items => { complete(items); setOpen(false); }} /></div> : <p>Wardrobe refreshed</p>;
}
it('keeps an existing caller dialog open after the first success and closes once after the failed second item retries', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockResolvedValueOnce({ id: 'first', userId: 'test-owner' }).mockRejectedValueOnce(new Error('Not confirmed saved')).mockResolvedValueOnce({ id: 'second', userId: 'test-owner' });
  const complete = jest.fn();
  render(<ClosingUploadDialog complete={complete} />);
  await choose('first.jpg', 'second.jpg'); start();
  const retry = await screen.findByRole('button', { name: 'Retry save' });
  expect(screen.getByRole('dialog')).toBeVisible();
  expect(screen.getByText('Saved to your wardrobe')).toBeVisible();
  expect(complete).not.toHaveBeenCalled();
  fireEvent.click(retry);
  await screen.findByText('Wardrobe refreshed');
  expect(complete).toHaveBeenCalledTimes(1);
  expect(complete).toHaveBeenCalledWith([{ id: 'first', userId: 'test-owner' }, { id: 'second', userId: 'test-owner' }]);
  expect(persistBatchWardrobeItem).toHaveBeenCalledTimes(3);
});
it('completes with acknowledged items when the user removes the failed selection', async () => {
  (persistBatchWardrobeItem as jest.Mock).mockResolvedValueOnce({ id: 'first', userId: 'test-owner' }).mockRejectedValueOnce(new Error('Not confirmed saved'));
  const complete = jest.fn();
  render(<ClosingUploadDialog complete={complete} />);
  await choose('first.jpg', 'second.jpg'); start();
  await screen.findByRole('button', { name: 'Retry save' });
  fireEvent.click(screen.getByRole('button', { name: 'Remove second.jpg from this selection' }));
  await screen.findByText('Wardrobe refreshed');
  expect(complete).toHaveBeenCalledTimes(1);
  expect(complete).toHaveBeenCalledWith([{ id: 'first', userId: 'test-owner' }]);
});
it('does not start saving or upload the next photo when unmounted during analysis', async () => {
  let finishAnalysis: (response: unknown) => void = () => {};
  const original = mockFetch.getMockImplementation()!;
  mockFetch.mockImplementation(async (...args) => args[0].endsWith('/analyze-image') ? new Promise(resolve => { finishAnalysis = resolve; }) : original(...args));
  const complete = jest.fn();
  const itemSaved = jest.fn();
  const view = render(<BatchImageUpload userId="test-owner" onUploadComplete={complete} onItemSaved={itemSaved} />);
  await choose('first.jpg', 'second.jpg'); start();
  await screen.findByText('Identifying your item');
  view.unmount();
  await act(async () => { finishAnalysis({ ok: true, json: async () => ({ analysis: { type: 'shirt' } }) }); });
  expect(persistBatchWardrobeItem).not.toHaveBeenCalled();
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(1);
  expect(complete).not.toHaveBeenCalled(); expect(itemSaved).not.toHaveBeenCalled();
});
it('does not start another upload or callback after an in-flight save settles following unmount', async () => {
  let finishSave: (item: unknown) => void = () => {};
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(() => new Promise(resolve => { finishSave = resolve; }));
  const complete = jest.fn(); const itemSaved = jest.fn();
  const view = render(<BatchImageUpload userId="test-owner" onUploadComplete={complete} onItemSaved={itemSaved} />);
  await choose('first.jpg', 'second.jpg'); start();
  await screen.findByText('Saving to your wardrobe');
  view.unmount();
  await act(async () => { finishSave({ id: 'first', userId: 'test-owner' }); });
  expect(persistBatchWardrobeItem).toHaveBeenCalledTimes(1);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(1);
  expect(complete).not.toHaveBeenCalled(); expect(itemSaved).not.toHaveBeenCalled();
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((done, fail) => { resolve = done; reject = fail; });
  return { promise, resolve, reject };
}
const photo = (name: string) => new File([name], name, { type: 'image/jpeg' });

it.each(['token', 'wardrobe', 'hash', 'photo'])('protects selected photos while %s preparation is still pending', async stage => {
  const gate = deferred<unknown>();
  const file = photo('shirt.jpg');
  if (stage === 'token') mockUser.getIdToken.mockReturnValueOnce(gate.promise);
  if (stage === 'wardrobe') mockFetch.mockReturnValueOnce(gate.promise);
  if (stage === 'hash') (photoHash as jest.Mock).mockReturnValueOnce(gate.promise);
  if (stage === 'photo') (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(gate.promise);
  const pending = jest.fn();
  render(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  let selecting!: Promise<void>;
  await act(async () => { selecting = mockOnDrop([file]); });

  expect(pending).toHaveBeenLastCalledWith(true);
  expect(screen.getByText('Preparing your photos…')).toBeVisible();
  expect(screen.queryByText('Ready to upload')).not.toBeInTheDocument();
  const warning = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(warning);
  expect(warning.defaultPrevented).toBe(true);
  pending.mockClear();

  await act(async () => {
    gate.resolve(stage === 'token' ? 'upload-test-token' : stage === 'wardrobe'
      ? { ok: true, json: async () => ({ success: true, items: [] }) }
      : stage === 'hash' ? 'sha256:shirt.jpg' : file);
    await selecting;
  });
  expect(screen.getByText('Ready to upload')).toBeVisible();
  expect(pending).not.toHaveBeenCalledWith(false);
  fireEvent.click(screen.getByRole('button', { name: 'Remove shirt.jpg from this selection' }));
  expect(pending).toHaveBeenLastCalledWith(false);
});

it.each(['wardrobe', 'hash'])('clears preparation on %s failure and retains its error', async stage => {
  const gate = deferred<unknown>();
  if (stage === 'wardrobe') mockFetch.mockReturnValueOnce(gate.promise);
  else (photoHash as jest.Mock).mockReturnValueOnce(gate.promise);
  const pending = jest.fn();
  const complete = jest.fn();
  render(<BatchImageUpload userId="test-owner" onPendingChange={pending} onUploadComplete={complete} />);
  let selecting!: Promise<void>;
  await act(async () => { selecting = mockOnDrop([photo('shirt.jpg')]); });
  expect(pending).toHaveBeenLastCalledWith(true);

  await act(async () => { gate.reject(new Error('Photo check unavailable')); await selecting; });
  expect(screen.getByRole('alert')).toHaveTextContent('Photo check unavailable');
  expect(pending).toHaveBeenLastCalledWith(false);
  expect(screen.queryByText('Preparing your photos…')).not.toBeInTheDocument();
  expect(complete).not.toHaveBeenCalled();
});

it('keeps a photo preparation error pending until the failed selection is removed', async () => {
  (prepareCapsulePhoto as jest.Mock).mockRejectedValue(new Error('This HEIC photo could not be read'));
  const pending = jest.fn();
  render(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  await choose('shirt.heic');

  expect(screen.getByRole('alert')).toHaveTextContent('HEIC photo could not be read');
  expect(screen.getByText('Not saved yet')).toBeVisible();
  expect(pending).toHaveBeenLastCalledWith(true);
  fireEvent.click(screen.getByRole('button', { name: 'Remove shirt.heic from this selection' }));
  expect(pending).toHaveBeenLastCalledWith(false);
});

it('keeps pending true until every overlapping preparation resolves', async () => {
  const first = deferred<File>();
  const second = deferred<File>();
  wardrobeItems = [{ contentHash: 'sha256:first.jpg' }, { contentHash: 'sha256:second.jpg' }];
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
  const pending = jest.fn();
  render(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  let firstSelection!: Promise<void>;
  let secondSelection!: Promise<void>;
  await act(async () => { firstSelection = mockOnDrop([photo('first.jpg')]); });
  await act(async () => { secondSelection = mockOnDrop([photo('second.jpg')]); });
  pending.mockClear();

  await act(async () => { first.resolve(photo('first.jpg')); await firstSelection; });
  expect(screen.getByText('Already added')).toBeVisible();
  expect(screen.getByText('Preparing your photos…')).toBeVisible();
  expect(pending).not.toHaveBeenCalledWith(false);

  await act(async () => { second.resolve(photo('second.jpg')); await secondSelection; });
  expect(screen.getAllByText('Already added')).toHaveLength(2);
  expect(pending).toHaveBeenLastCalledWith(false);
});

it.each(['new', 'duplicate'])('does not complete an earlier save while a newer %s selection is preparing', async kind => {
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => item);
  const complete = jest.fn();
  render(<BatchImageUpload userId="test-owner" onUploadComplete={complete} />);
  await choose('first.jpg');
  const laterPhoto = deferred<File>();
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(laterPhoto.promise);
  if (kind === 'duplicate') wardrobeItems = [{ contentHash: 'sha256:second.jpg' }];
  let laterSelection!: Promise<void>;
  await act(async () => { laterSelection = mockOnDrop([photo('second.jpg')]); });
  start();
  await screen.findByText('Saved to your wardrobe');
  expect(complete).not.toHaveBeenCalled();

  await act(async () => { laterPhoto.resolve(photo('second.jpg')); await laterSelection; });
  if (kind === 'new') {
    expect(complete).not.toHaveBeenCalled();
    start();
  }
  await waitFor(() => expect(complete).toHaveBeenCalledTimes(1));
  expect(complete.mock.calls[0][0]).toHaveLength(kind === 'new' ? 2 : 1);
});

it('does not let old-owner preparation settle or append into a new-owner selection', async () => {
  const oldPhoto = deferred<File>();
  const newPhoto = deferred<File>();
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(oldPhoto.promise).mockReturnValueOnce(newPhoto.promise);
  const pending = jest.fn();
  const view = render(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  let oldSelection!: Promise<void>;
  let newSelection!: Promise<void>;
  await act(async () => { oldSelection = mockOnDrop([photo('old.jpg')]); });
  mockUser.uid = 'new-owner';
  view.rerender(<BatchImageUpload userId="new-owner" onPendingChange={pending} />);
  expect(pending).toHaveBeenLastCalledWith(false);
  await act(async () => { newSelection = mockOnDrop([photo('new.jpg')]); });
  expect(pending).toHaveBeenLastCalledWith(true);
  pending.mockClear();

  await act(async () => { oldPhoto.resolve(photo('old.jpg')); await oldSelection; });
  expect(screen.queryByText('old.jpg')).not.toBeInTheDocument();
  expect(screen.getByText('Preparing your photos…')).toBeVisible();
  expect(pending).not.toHaveBeenCalledWith(false);
  await act(async () => { newPhoto.resolve(photo('new.jpg')); await newSelection; });
  expect(screen.getByText('new.jpg')).toBeVisible();
  expect(pending).not.toHaveBeenCalledWith(false);
});

it('invalidates an old preparation even when the same owner signs back in', async () => {
  const gate = deferred<File>();
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(gate.promise);
  const view = render(<BatchImageUpload userId="test-owner" />);
  let selecting!: Promise<void>;
  await act(async () => { selecting = mockOnDrop([photo('old.jpg')]); });
  mockUser.uid = 'other-owner';
  view.rerender(<BatchImageUpload userId="other-owner" />);
  mockUser.uid = 'test-owner';
  view.rerender(<BatchImageUpload userId="test-owner" />);

  await act(async () => { gate.resolve(photo('old.jpg')); await selecting; });
  expect(screen.queryByText('old.jpg')).not.toBeInTheDocument();
  expect(screen.queryByText('Preparing your photos…')).not.toBeInTheDocument();
});

it.each(['during switch', 'after return'])('invalidates fixed-owner preparation when authentication changes and resolves %s', async when => {
  const gate = deferred<File>();
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(gate.promise);
  const pending = jest.fn();
  const view = render(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  let selecting!: Promise<void>;
  await act(async () => { selecting = mockOnDrop([photo('old.jpg')]); });
  expect(pending).toHaveBeenLastCalledWith(true);

  mockUser.uid = 'other-owner';
  view.rerender(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  if (when === 'during switch') {
    await act(async () => { gate.resolve(photo('old.jpg')); await selecting; });
  }
  mockUser.uid = 'test-owner';
  view.rerender(<BatchImageUpload userId="test-owner" onPendingChange={pending} />);
  if (when === 'after return') {
    await act(async () => { gate.resolve(photo('old.jpg')); await selecting; });
  }

  expect(screen.queryByText('old.jpg')).not.toBeInTheDocument();
  expect(screen.queryByText('Preparing your photos…')).not.toBeInTheDocument();
  expect(pending).toHaveBeenLastCalledWith(false);
  await choose('current.jpg');
  expect(screen.getByText('current.jpg')).toBeVisible();
  expect(pending).toHaveBeenLastCalledWith(true);
});

it('stages and saves only one copy when the same photo finishes two overlapping preparations', async () => {
  const first = deferred<File>();
  const second = deferred<File>();
  const file = photo('same.jpg');
  (prepareCapsulePhoto as jest.Mock).mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
  (persistBatchWardrobeItem as jest.Mock).mockImplementation(async item => item);
  const complete = jest.fn();
  render(<BatchImageUpload userId="test-owner" onUploadComplete={complete} />);
  let firstSelection!: Promise<void>;
  let secondSelection!: Promise<void>;
  await act(async () => { firstSelection = mockOnDrop([file]); });
  await act(async () => { secondSelection = mockOnDrop([file]); });
  expect(photoHash).toHaveBeenCalledTimes(2);

  await act(async () => { first.resolve(file); await firstSelection; });
  await act(async () => { second.resolve(file); await secondSelection; });
  expect(screen.getAllByText('Ready to upload')).toHaveLength(1);
  expect(screen.getByText('Already added')).toBeVisible();
  start();
  await waitFor(() => expect(complete).toHaveBeenCalledTimes(1));
  expect(persistBatchWardrobeItem).toHaveBeenCalledTimes(1);
  expect(mockFetch.mock.calls.filter(([url]) => url.endsWith('/api/image/upload'))).toHaveLength(1);
  expect(complete.mock.calls[0][0]).toHaveLength(1);
});

it('releases partial previews and pending state after unmount without callbacks from stale preparation', async () => {
  const gate = deferred<string>();
  (photoHash as jest.Mock).mockResolvedValueOnce('sha256:first.jpg').mockReturnValueOnce(gate.promise);
  const pending = jest.fn();
  const complete = jest.fn();
  const view = render(<BatchImageUpload userId="test-owner" onPendingChange={pending} onUploadComplete={complete} />);
  let selecting!: Promise<void>;
  await act(async () => { selecting = mockOnDrop([photo('first.jpg'), photo('second.jpg')]); });
  expect(URL.createObjectURL).toHaveBeenCalledTimes(1);
  expect(pending).toHaveBeenLastCalledWith(true);
  view.unmount();
  expect(pending).toHaveBeenLastCalledWith(false);
  pending.mockClear();

  await act(async () => { gate.resolve('sha256:second.jpg'); await selecting; });
  expect(URL.createObjectURL).toHaveBeenCalledTimes(1);
  expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test');
  expect(pending).not.toHaveBeenCalled();
  expect(complete).not.toHaveBeenCalled();
  const warning = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(warning);
  expect(warning.defaultPrevented).toBe(false);
});
