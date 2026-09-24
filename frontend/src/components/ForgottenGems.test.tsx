import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ForgottenGems from './ForgottenGems';

declare const expect: jest.Expect;
declare const it: jest.It;

const now = Date.parse('2026-09-24T12:00:00Z');
const day = 86_400_000;
const mockUser = { uid: 'owner', getIdToken: jest.fn(async () => 'token') };
const originalFetch = global.fetch;
const mockFetch = jest.fn();
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser }) }));
jest.mock('@/components/ui/use-toast', () => ({ useToast: () => ({ toast: jest.fn() }) }));
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock('@/components/ui/carousel/Carousel', () => function Carousel({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
});

const item = {
  id: 'white-sweatshirt', name: 'White Sweatshirt', type: 'sweatshirt',
  imageUrl: 'https://example.test/sweatshirt.jpg', color: 'white', style: [],
  createdAt: Date.parse('2026-09-24T04:58:00Z'), lastWorn: null,
  daysSinceWorn: 999, usageCount: 0, favoriteScore: 0,
  suggestedOutfits: [], rediscoveryPotential: 80,
};

function respond(items: unknown[]) {
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({ data: {
    forgottenItems: items, analysis_timestamp: '2026-09-24T12:00:00Z',
  } }) });
}

beforeEach(() => {
  jest.spyOn(Date, 'now').mockReturnValue(now);
  mockFetch.mockReset();
  global.fetch = mockFetch;
});
afterEach(() => {
  jest.restoreAllMocks();
  global.fetch = originalFetch;
});

it('labels newly uploaded unworn garments accurately with both legacy and current API responses', async () => {
  respond([item, { ...item, id: 'brown-shoes', name: 'Brown Shoes', daysSinceWorn: null }]);
  render(<ForgottenGems />);
  expect(await screen.findByText('White Sweatshirt')).toBeVisible();
  expect(screen.getByText('Brown Shoes')).toBeVisible();
  expect(screen.getAllByText('Never worn • Worn 0 times')).toHaveLength(2);
  expect(screen.queryByText(/years ago/)).not.toBeInTheDocument();
});

it.each([undefined, null, NaN, Infinity, -1, 0, Date.UTC(1999, 0, 1), now + day, 'invalid'])
  ('does not invent elapsed recency for invalid lastWorn %s', async lastWorn => {
    respond([{ ...item, lastWorn, usageCount: 3 }]);
    render(<ForgottenGems />);
    expect(await screen.findByText('Last worn unknown • Worn 3 times')).toBeVisible();
    expect(screen.queryByText(/Never worn|years ago/)).not.toBeInTheDocument();
  });

it.each([
  [now, 'Today'],
  [now - day, 'Yesterday'],
  [now - 3 * day, '3 days ago'],
  [now - 14 * day, '2 weeks ago'],
  [now - 60 * day, '2 months ago'],
  [now - 365 * day, '1 year ago'],
  [(now - 14 * day) / 1000, '2 weeks ago'],
])('uses the actual timestamp %s instead of a placeholder day count', async (lastWorn, label) => {
  respond([{ ...item, lastWorn, usageCount: 3 }]);
  render(<ForgottenGems />);
  expect(await screen.findByText(`${label} • Worn 3 times`)).toBeVisible();
});
