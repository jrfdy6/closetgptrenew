import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from './page';
import type { OnboardingState } from '@/lib/onboarding/types';

declare const expect: jest.Expect;
declare const it: jest.It;

const mockUser = { uid: 'owner', getIdToken: jest.fn(async () => 'token') };
const mockAuth = { user: mockUser, loading: false };
const mockDashboard = jest.fn();
const mockWardrobe = { items: [] as unknown[], loading: false, error: null as string | null, refetch: jest.fn() };
const progress = (stage: OnboardingState['stage'], ready = false): OnboardingState => ({
  schemaVersion: 1, revision: 0, draft: { answers: [], currentQuestionId: null }, profileComplete: stage !== 'style', stage,
  capsule: { minimum: 10, savedCount: ready ? 10 : 0, usableCount: ready ? 10 : 0, hasCoverage: ready, missingCategories: ready ? [] : ['tops', 'bottoms', 'shoes'], ready },
  milestones: { styleCompletedAt: null, capsuleCompletedAt: null, firstOutfitId: null },
});
const mockStage = { state: progress('capsule') as OnboardingState | null, loading: false, error: null as string | null, refresh: jest.fn() };
const mockMount = jest.fn();
const mockUnmount = jest.fn();
const mockWeather = { temperature: 72, condition: 'Clear', location: 'Test' };
const mockGamification = { stats: null as { level: { level: number } } | null, loading: false, error: null as string | null };
const data = { totalItems: 10, favorites: 0, outfitsThisWeek: 0, topItems: [], styleCollections: [], totalStyleGoals: 0 };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => mockAuth }));
jest.mock('@/lib/hooks/useWardrobe', () => ({ useWardrobe: () => mockWardrobe }));
jest.mock('@/lib/hooks/useOnboardingState', () => ({ useOnboardingState: () => mockStage }));
jest.mock('@/lib/services/dashboardService', () => ({ dashboardService: { getDashboardData: (...args: unknown[]) => mockDashboard(...args) } }));
jest.mock('@/hooks/useWeather', () => ({ useAutoWeather: () => ({ weather: mockWeather, fetchWeatherByLocation: jest.fn() }) }));
jest.mock('@/hooks/useGamificationStats', () => ({ useGamificationStats: () => mockGamification }));
jest.mock('@/hooks/useSubscriptionPlan', () => ({ useSubscriptionPlan: () => ({ plan: 'free', loading: false, canAccess: () => false }) }));
jest.mock('@/components/providers/withSubscriptionGate', () => ({ withSubscriptionGate: (value: unknown) => value }));
jest.mock('@/components/Navigation', () => () => null);
jest.mock('@/components/ClientOnlyNav', () => () => null);
jest.mock('@/components/PremiumTeaser', () => () => null);
jest.mock('@/components/ui/wardrobe-insights-hub', () => () => null);
jest.mock('@/components/MissingWardrobeModal', () => function MissingWardrobeModal({ isOpen }: { isOpen: boolean }) {
  return isOpen ? <div role="dialog">Add your capsule</div> : null;
});
jest.mock('next/dynamic', () => () => function DynamicPlaceholder() { return null; });
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock('@/components/SmartWeatherOutfitGenerator', () => function Widget({ generationEnabled, onOutfitGenerated }: { generationEnabled: boolean; onOutfitGenerated: (value: unknown) => void }) {
  React.useEffect(() => {
    mockMount();
    return () => { mockUnmount(); };
  }, []);
  return <div data-testid="daily-look" data-enabled={generationEnabled}>
    <button onClick={() => onOutfitGenerated({ id: 'saved-look' })}>Complete test generation</button>
  </div>;
});

beforeEach(() => {
  sessionStorage.setItem('has-asked-for-location', 'true');
  mockDashboard.mockReset().mockResolvedValue(data);
  mockAuth.user = mockUser;
  mockAuth.loading = false;
  mockWardrobe.items = [];
  mockWardrobe.error = null;
  mockWardrobe.loading = false;
  mockStage.state = progress('capsule');
  mockStage.loading = false;
  mockStage.error = null;
  mockMount.mockClear();
  mockUnmount.mockClear();
  mockGamification.stats = null;
  mockGamification.loading = false;
  mockGamification.error = null;
});

it.each([
  { loading: true, error: null, stats: null, label: 'Loading…' },
  { loading: false, error: null, stats: null, label: 'Unavailable' },
  { loading: false, error: 'Stats unavailable', stats: { level: { level: 3 } }, label: 'Unavailable' },
])('does not invent a progress level when stats show $label', async ({ loading, error, stats, label }) => {
  Object.assign(mockGamification, { loading, error, stats });
  render(<Dashboard />);
  const card = (await screen.findByText('Your Progress')).parentElement;
  expect(card).toHaveTextContent(label);
  expect(card).not.toHaveTextContent(/Level \d/);
});

it('shows the actual progress level after a successful stats read', async () => {
  mockGamification.stats = { level: { level: 3 } };
  render(<Dashboard />);
  expect((await screen.findByText('Your Progress')).parentElement).toHaveTextContent('Level 3');
});

it('keeps automatic generation disabled on a new empty dashboard', async () => {
  render(<Dashboard />);
  expect(await screen.findByTestId('daily-look')).toHaveAttribute('data-enabled', 'false');
  expect(screen.getByRole('link', { name: /Continue my capsule/ })).toHaveAttribute('href', '/onboarding');
  expect(screen.getByText('0 of 10 pieces saved')).toBeVisible();
});

it('preserves established users after wardrobe deletion instead of forcing capsule onboarding again', async () => {
  mockStage.state = progress('complete');
  render(<Dashboard />);
  expect(await screen.findByTestId('daily-look')).toHaveAttribute('data-enabled', 'false');
  expect(screen.queryByText('Add your capsule')).not.toBeInTheDocument();
});

it('never interprets wardrobe or progress fetch failure as an empty new closet', async () => {
  mockWardrobe.error = 'Wardrobe read failed';
  mockStage.error = 'Progress read failed';
  render(<Dashboard />);
  expect(await screen.findByTestId('daily-look')).toHaveAttribute('data-enabled', 'false');
  expect(screen.queryByText('Add your capsule')).not.toBeInTheDocument();
  expect(screen.getByRole('alert')).toHaveTextContent('Progress read failed');
});

it('does not unmount the generated result while refreshing dashboard statistics', async () => {
  mockStage.state = progress('complete', true);
  mockWardrobe.items = ['shirt', 'pants', 'shoes', ...Array(7).fill('shirt')].map((type, index) => ({ id: String(index), type, imageUrl: `https://example.test/${index}.jpg` }));
  let resolveRefresh!: (value: unknown) => void;
  mockDashboard.mockResolvedValueOnce(data).mockImplementationOnce(() => new Promise(resolve => { resolveRefresh = resolve; }));
  render(<Dashboard />);
  const widget = await screen.findByTestId('daily-look');
  expect(widget).toHaveAttribute('data-enabled', 'true');
  fireEvent.click(screen.getByRole('button', { name: 'Complete test generation' }));
  await waitFor(() => expect(mockDashboard).toHaveBeenCalledTimes(2));
  expect(screen.getByTestId('daily-look')).toBe(widget);
  expect(mockMount).toHaveBeenCalledTimes(1);
  expect(mockUnmount).not.toHaveBeenCalled();
  expect(screen.getByRole('status')).toHaveTextContent('Updating your dashboard');
  expect(screen.getByText('Total items').parentElement).toHaveTextContent('10');
  await act(async () => resolveRefresh(data));
  expect(screen.getByTestId('daily-look')).toBe(widget);
});

it('shows a retryable load error instead of a zero-item wardrobe', async () => {
  mockDashboard.mockRejectedValueOnce(new Error('Failed to fetch: private server details'));
  render(<Dashboard />);
  expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load your dashboard");
  expect(screen.queryByText('Total items')).not.toBeInTheDocument();
  expect(screen.queryByText(/private server details/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Retry dashboard' }));
  expect(await screen.findByText('Total items')).toBeVisible();
  expect(screen.getByText('Total items').parentElement).toHaveTextContent('10');
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('keeps the last loaded count and generated result after a failed refresh, then recovers', async () => {
  mockDashboard.mockResolvedValueOnce(data).mockRejectedValueOnce(new Error('Network unavailable'))
    .mockResolvedValueOnce({ ...data, totalItems: 11 });
  render(<Dashboard />);
  const widget = await screen.findByTestId('daily-look');
  fireEvent.click(screen.getByRole('button', { name: 'Complete test generation' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Your last loaded dashboard is still shown');
  expect(screen.getByText('Total items').parentElement).toHaveTextContent('10');
  expect(screen.getByTestId('daily-look')).toBe(widget);
  expect(mockUnmount).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Retry dashboard' }));
  await waitFor(() => expect(screen.getByText('Total items').parentElement).toHaveTextContent('11'));
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByTestId('daily-look')).toBe(widget);
});

it('shows zero only when the dashboard successfully loads an empty wardrobe', async () => {
  mockDashboard.mockResolvedValue({ ...data, totalItems: 0 });
  render(<Dashboard />);
  expect(await screen.findByText('Total items')).toBeVisible();
  expect(screen.getByText('Total items').parentElement).toHaveTextContent('0');
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('does not let an older refresh overwrite the latest wardrobe count', async () => {
  let resolveOlder!: (value: unknown) => void;
  mockDashboard.mockResolvedValueOnce(data)
    .mockImplementationOnce(() => new Promise(resolve => { resolveOlder = resolve; }))
    .mockResolvedValueOnce({ ...data, totalItems: 12 });
  render(<Dashboard />);
  await screen.findByTestId('daily-look');
  fireEvent.click(screen.getByRole('button', { name: 'Complete test generation' }));
  fireEvent.click(screen.getByRole('button', { name: 'Complete test generation' }));
  await waitFor(() => expect(screen.getByText('Total items').parentElement).toHaveTextContent('12'));
  await act(async () => resolveOlder({ ...data, totalItems: 0 }));
  expect(screen.getByText('Total items').parentElement).toHaveTextContent('12');
});

it('does not retain another account’s dashboard when the new account fails to load', async () => {
  mockDashboard.mockResolvedValueOnce(data).mockRejectedValueOnce(new Error('New account unavailable'));
  const { rerender } = render(<Dashboard />);
  await screen.findByText('Total items');
  mockAuth.user = { ...mockUser, uid: 'other-owner' };
  rerender(<Dashboard />);
  expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load your dashboard");
  expect(screen.queryByText('Total items')).not.toBeInTheDocument();
  expect(screen.queryByText(/last loaded dashboard/)).not.toBeInTheDocument();
});

it('cancels a delayed wear refresh when the signed-in account changes', async () => {
  jest.useFakeTimers();
  try {
    mockDashboard.mockResolvedValueOnce(data).mockResolvedValueOnce({ ...data, totalItems: 12 });
    const { rerender, unmount } = render(<Dashboard />);
    await screen.findByText('Total items');
    act(() => window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn')));
    mockAuth.user = { ...mockUser, uid: 'other-owner' };
    rerender(<Dashboard />);
    await waitFor(() => expect(screen.getByText('Total items').parentElement).toHaveTextContent('12'));
    await act(async () => { jest.advanceTimersByTime(2500); });
    expect(mockDashboard).toHaveBeenCalledTimes(2);
    expect(screen.getByText('Total items').parentElement).toHaveTextContent('12');
    act(() => window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn')));
    unmount();
    await act(async () => { jest.advanceTimersByTime(2500); });
    expect(mockDashboard).toHaveBeenCalledTimes(2);
  } finally {
    jest.useRealTimers();
  }
});

it('asks a newly ready capsule to choose its first look instead of generating on dashboard arrival', async () => {
  mockStage.state = progress('first-look', true);
  mockWardrobe.items = ['shirt', 'pants', 'shoes', ...Array(7).fill('shirt')].map((type, index) => ({ id: String(index), type, imageUrl: `https://example.test/${index}.jpg` }));
  render(<Dashboard />);
  expect(await screen.findByTestId('daily-look')).toHaveAttribute('data-enabled', 'false');
  expect(screen.getByRole('link', { name: /Create my first outfit/ })).toHaveAttribute('href', '/outfits/generate?onboarding=1');
});
