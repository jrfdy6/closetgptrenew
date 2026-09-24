import '@testing-library/jest-dom';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import Page from './page';
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
const mockPush = jest.fn();
const mockUser = { uid: 'owner', email: 'owner@example.test', providerData: [], getIdToken: async () => 'token' };
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/auth', () => ({ getLinkedProviders: jest.fn(), hasPasswordLinked: () => false, linkEmailPassword: jest.fn() }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/ClientOnlyNav', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/SpendingRangesCard', () => ({ __esModule: true, default: () => null }));
jest.mock('@/lib/services/subscriptionService', () => ({ subscriptionService: { getCurrentSubscription: async () => ({ role: 'tier1', status: 'active' }) } }));
beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ userId: 'owner', name: 'Original name', email: 'owner@example.test', stylePreferences: ['Classic'], measurements: {} }) });
  Element.prototype.scrollIntoView = jest.fn();
  jest.spyOn(console, 'log').mockImplementation(() => {});
});
afterEach(() => jest.restoreAllMocks());
it('connects Favorites and Style Inspiration to the existing destinations', async () => {
  render(<Page />);
  fireEvent.click(await screen.findByRole('button', { name: /Favorite items/i }));
  expect(mockPush).toHaveBeenLastCalledWith('/wardrobe?view=favorites');
  fireEvent.click(screen.getByRole('button', { name: /Style inspiration/i }));
  expect(mockPush).toHaveBeenLastCalledWith('/style-inspiration');
});
it('opens the existing preferences editor and moves keyboard focus there without saving', async () => {
  render(<Page />);
  fireEvent.click(await screen.findByRole('button', { name: /^Preferences$/i }));
  await waitFor(() => expect(screen.getByText('Style preferences')).toHaveFocus());
  expect(screen.getByDisplayValue('Original name')).toBeVisible();
  expect((fetch as jest.Mock).mock.calls.every(([, options]) => !options.method || options.method === 'GET')).toBe(true);
});
it('shows the saved preferred style consistently in read and edit modes, not the quiz persona name', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({
    userId: 'owner', name: 'Original name', email: 'owner@example.test',
    stylePreferences: ['Cottagecore'], measurements: {}, stylePersona: { id: 'classic', name: 'The Classic' },
  }) });
  render(<Page />);
  expect(await screen.findByText('Cottagecore')).toBeVisible();
  expect(screen.queryByText('The Classic')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: /^Preferences$/i }));
  expect(screen.getByText('Cottagecore')).toBeVisible();
  expect((fetch as jest.Mock).mock.calls.every(([, options]) => !options.method || options.method === 'GET')).toBe(true);
});
