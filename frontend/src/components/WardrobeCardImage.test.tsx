import '@testing-library/jest-dom';
declare const expect: jest.Expect;
declare const it: jest.It;

import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ImageConfigContext } from 'next/dist/shared/lib/image-config-context.shared-runtime';
import { imageConfigDefault } from 'next/dist/shared/lib/image-config';
import WardrobeCardImage from './WardrobeCardImage';

// Use Next's actual src/srcSet generation to cover the stale-srcSet regression.
jest.unmock('next/image');
const nextConfig = require('../../next.config');
const bucket = 'https://storage.googleapis.com/closetgptrenew.firebasestorage.app';
const props = {
  itemId: 'white-shirt',
  alt: 'White shirt',
  thumbnailUrl: `${bucket}/thumbnails/shirt.webp`,
  backgroundRemovedUrl: `${bucket}/cutouts/shirt.png`,
  imageUrl: `${bucket}/originals/shirt.jpg`,
};

function imageFor(nextProps = props) {
  return <ImageConfigContext.Provider value={{ ...imageConfigDefault, ...nextConfig.images }}>
    <WardrobeCardImage {...nextProps} />
  </ImageConfigContext.Provider>;
}

function expectSource(source: string) {
  const image = screen.getByRole('img', { name: props.alt });
  expect(new URL(image.getAttribute('src')!, 'https://app.test').searchParams.get('url')).toBe(source);
  for (const candidate of image.getAttribute('srcset')!.split(', ')) {
    expect(new URL(candidate.split(' ')[0], 'https://app.test').searchParams.get('url')).toBe(source);
  }
  return image;
}

it('retries failed derivatives in order and updates every optimized source to the original', () => {
  render(imageFor());
  fireEvent.error(expectSource(props.thumbnailUrl));
  fireEvent.error(expectSource(props.backgroundRemovedUrl));
  expectSource(props.imageUrl);
  expect(screen.queryByText('Image unavailable')).not.toBeInTheDocument();
});

it('does not retry identical derivative and original URLs', () => {
  render(imageFor({ ...props, backgroundRemovedUrl: props.thumbnailUrl }));
  fireEvent.error(expectSource(props.thumbnailUrl));
  fireEvent.error(expectSource(props.imageUrl));
  expect(screen.getByRole('img', { name: 'White shirt image unavailable' })).toHaveTextContent('Image unavailable');
});

it('ends with an accessible unavailable state after all sources fail, without a broken placeholder request', () => {
  const { container } = render(imageFor());
  const thumbnail = expectSource(props.thumbnailUrl);
  fireEvent.error(thumbnail);
  fireEvent.error(expectSource(props.backgroundRemovedUrl));
  fireEvent.error(expectSource(props.imageUrl));
  expect(container.querySelector('img')).toBeNull();
  expect(screen.getByRole('img', { name: 'White shirt image unavailable' })).toBeVisible();
  fireEvent.error(thumbnail);
  expect(container.querySelector('img')).toBeNull();
});

it('does not skip an available fallback when the same source reports multiple errors', () => {
  render(imageFor());
  const thumbnail = expectSource(props.thumbnailUrl);
  act(() => {
    fireEvent.error(thumbnail);
    fireEvent.error(thumbnail);
  });
  expectSource(props.backgroundRemovedUrl);
});

it('starts again when a new processed source arrives for the same garment', () => {
  const { rerender } = render(imageFor());
  fireEvent.error(expectSource(props.thumbnailUrl));
  fireEvent.error(expectSource(props.backgroundRemovedUrl));
  expectSource(props.imageUrl);
  const newThumbnail = `${bucket}/thumbnails/shirt-v2.webp`;
  rerender(imageFor({ ...props, thumbnailUrl: newThumbnail }));
  expectSource(newThumbnail);
});

it('resets the exhausted sequence for a different garment even if its URLs are the same', () => {
  const { rerender } = render(imageFor());
  fireEvent.error(expectSource(props.thumbnailUrl));
  fireEvent.error(expectSource(props.backgroundRemovedUrl));
  fireEvent.error(expectSource(props.imageUrl));
  rerender(imageFor({ ...props, itemId: 'different-shirt' }));
  expectSource(props.thumbnailUrl);
});
