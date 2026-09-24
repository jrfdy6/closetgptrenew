declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, render, screen } from '@testing-library/react';
import OnboardingRecap from './OnboardingRecap';
const mockWardrobe = jest.fn();
jest.mock('@/lib/services/wardrobeService', () => ({ WardrobeService: { getWardrobeItems: () => mockWardrobe() } }));
jest.mock('next/image', () => ({ __esModule: true, default: ({ fill, unoptimized, ...props }: { fill?: boolean; unoptimized?: boolean } & React.ImgHTMLAttributes<HTMLImageElement>) => <img {...props} /> }));
const items = (uid: string) => Array.from({ length: 10 }, (_, index) => ({ id: `${uid}-${index}`, userId: uid, type: index === 0 ? 'shoes' : index === 1 ? 'dress' : 'shirt', imageUrl: `/${uid}-${index}.jpg`, name: `${uid} garment ${index}`, processing_status: 'failed' }));
const props = { answers: [], onManageCapsule: jest.fn(), onRetake: jest.fn() };
beforeEach(() => { mockWardrobe.mockReset(); });

it('uses saved originals for a valid one-piece capsule even when cutouts fail', async () => {
  mockWardrobe.mockResolvedValue(items('a'));
  await act(async () => { render(<OnboardingRecap {...props} userId="a" />); });
  const action = screen.getByRole('link', { name: 'Create my first outfit' });
  expect(action).toBeVisible();
  expect(screen.getAllByRole('link', { name: 'Create my first outfit' })).toHaveLength(1);
  expect(action.compareDocumentPosition(screen.getByAltText('a garment 0')) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  expect(action.compareDocumentPosition(screen.getByRole('link', { name: 'View my style profile' })) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  expect(screen.getByText('10 unique usable pieces saved')).toBeVisible();
});
it('does not let duplicate images or foreign records satisfy the capsule', async () => {
  const owned = items('a').map(item => ({ ...item, imageUrl: '/same.jpg' }));
  mockWardrobe.mockResolvedValue([...owned, ...items('foreign')]);
  await act(async () => { render(<OnboardingRecap {...props} userId="a" />); });
  expect(screen.getByText('1 unique usable piece saved')).toBeVisible();
  expect(screen.queryByAltText('foreign garment 0')).not.toBeInTheDocument();
  expect(screen.queryByRole('link', { name: 'Create my first outfit' })).not.toBeInTheDocument();
});
it('masks prior-user photos immediately and ignores a late prior-user request', async () => {
  let resolveA: (value: unknown[]) => void;
  let resolveB: (value: unknown[]) => void;
  mockWardrobe.mockImplementationOnce(() => new Promise(resolve => { resolveA = resolve; })).mockImplementationOnce(() => new Promise(resolve => { resolveB = resolve; }));
  const view = render(<OnboardingRecap {...props} userId="a" />);
  view.rerender(<OnboardingRecap {...props} userId="b" />);
  await act(async () => { resolveA!(items('a')); });
  expect(screen.queryByAltText('a garment 0')).not.toBeInTheDocument();
  expect(screen.getByRole('status')).toHaveTextContent('Loading your saved pieces');
  await act(async () => { resolveB!(items('b')); });
  expect(screen.getByAltText('b garment 0')).toBeVisible();
});
