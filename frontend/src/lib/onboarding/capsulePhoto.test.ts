declare const expect: jest.Expect;
declare const it: jest.It;
import { webcrypto } from 'crypto';
import { photoHash, prepareCapsulePhoto } from './capsulePhoto';
jest.mock('heic2any', () => ({ __esModule: true, default: jest.fn() }));
import convert from 'heic2any';
it('hashes exact file bytes consistently across renamed files without network access', async () => {
  Object.defineProperty(global.crypto, 'subtle', { configurable: true, value: webcrypto.subtle });
  const first = await photoHash(new File(['photo bytes'], 'first.jpg', { type: 'image/jpeg' }));
  expect(await photoHash(new File(['photo bytes'], 'renamed.png', { type: 'image/png' }))).toBe(first);
  expect(await photoHash(new File(['different photo'], 'first.jpg', { type: 'image/jpeg' }))).not.toBe(first);
  expect(first).toMatch(/^sha256:[0-9a-f]{64}$/);
});
it('passes supported originals through without resizing or lossy recompression', async () => {
  for (const type of ['image/jpeg', 'image/png', 'image/webp']) {
    const file = new File(['original bytes'], 'photo', { type });
    expect(await prepareCapsulePhoto(file)).toBe(file);
  }
});
it('converts HEIC to a correctly named JPEG and exposes conversion failure', async () => {
  const photo = new Blob(['converted'], { type: 'image/jpeg' });
  (convert as jest.Mock).mockResolvedValueOnce(photo).mockRejectedValueOnce(new Error('decoder details'));
  const result = await prepareCapsulePhoto(new File(['heic'], 'IMG.HEIC', { type: 'image/heic' }));
  expect(result.name).toBe('IMG.jpg'); expect(result.type).toBe('image/jpeg');
  await expect(prepareCapsulePhoto(new File(['broken'], 'bad.heic', { type: 'image/heic' }))).rejects.toThrow('Export it as JPEG');
});
