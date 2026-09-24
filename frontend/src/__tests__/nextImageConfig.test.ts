/** @jest-environment node */

declare const expect: jest.Expect;
declare const it: jest.It;

import { hasRemoteMatch } from 'next/dist/shared/lib/match-remote-pattern';

const { images } = require('../../next.config');
const accepts = (url: string) => hasRemoteMatch([], images.remotePatterns, new URL(url));

it('allows optimized images in the confirmed EasyOutfit storage bucket', () => {
  expect(accepts('https://storage.googleapis.com/closetgptrenew.firebasestorage.app/thumbnails/shirt.webp')).toBe(true);
  expect(accepts('https://storage.googleapis.com/closetgptrenew.firebasestorage.app/users/test/originals/shirt.jpg?alt=media&token=example')).toBe(true);
});

it.each([
  'https://storage.googleapis.com/another-bucket/shirt.jpg',
  'https://storage.googleapis.com/closetgptrenew.firebasestorage.app-other/shirt.jpg',
  'https://storage.googleapis.com/prefix/closetgptrenew.firebasestorage.app/shirt.jpg',
  'https://storage.googleapis.com/shirt.jpg',
  'http://storage.googleapis.com/closetgptrenew.firebasestorage.app/shirt.jpg',
  'https://storage.googleapis.com:8443/closetgptrenew.firebasestorage.app/shirt.jpg',
  'https://other.storage.googleapis.com/closetgptrenew.firebasestorage.app/shirt.jpg',
  'https://storage.googleapis.com.example.com/closetgptrenew.firebasestorage.app/shirt.jpg',
])('does not broaden storage optimization to other buckets or origins: %s', url => {
  expect(accepts(url)).toBe(false);
});
