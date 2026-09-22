import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from './page';

declare const expect: jest.Expect;
declare const it: jest.It;

const mockUser = { uid: 'owner', getIdToken: jest.fn(async () => 'token') };
const mockDashboard = jest.fn();
const mockWardrobe = { items: [] as unknown[], loading: false, error: null as string | null, refetch: jest.fn() };
const mockStage = { state: { stage: 'capsule' } as { stage: string } | null, loading: false, error: null as string | null, refresh: jest.fn() };
const mockMount = jest.fn();
const mockUnmount = jest.fn();
const mockWeather = { temperature: 72, condition: 'Clear', location: 'Test' };
const data = { totalItems: 10, favorites: 0, outfitsThisWeek: 0, topItems: [], styleCollections: [], totalStyleGoals: 0 };
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/hooks/useWardrobe', () => ({ useWardrobe: () => mockWardrobe }));
jest.mock('@/lib/hooks/useOnboardingState', () => ({ useOnboardingState: () => mockStage }));
jest.mock('@/lib/services/dashboardService', () => ({ dashboardService: { getDashboardData: (...args: unknown[]) => mockDashboard(...args) } }));
jest.mock('@/hooks/useWeather', () => ({ useAutoWeather: () => ({ weather: mockWeather, fetchWeatherByLocation: jest.fn() }) }));
jest.mock('@/hooks/useGamificationStats', () => ({ useGamificationStats: () => ({ stats: null }) }));
jest.mock('@/hooks/useSubscriptionPlan', () => ({ useSubscriptionPlan: () => ({ plan: 'free', loading: false, canAccess: () => false }) }));
jest.mock('@/components/providers/withSubscriptionGate', () => ({ withSubscriptionGate: (value: unknown) => value }));
jest.mock('@/components/Navigation', () => () => null);
jest.mock('@/components/ClientOnlyNav', () => () => null);
jest.mock('@/components/PremiumTeaser', () => () => null);
jest.mock('@/components/ui/wardrobe-insights-hub', () => () => null);
jest.mock('@/components/MissingWardrobeModal', () => ({ isOpen }: { isOpen: boolean }) => isOpen ? <div role="dialog">Add your capsule</div> : null);
jest.mock('next/dynamic', () => () => () => null);
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
  mockWardrobe.items = [];
  mockWardrobe.error = null;
  mockWardrobe.loading = false;
  mockStage.state = { stage: 'capsule' };
  mockStage.loading = false;
  mockStage.error = null;
  mockMount.mockClear();
  mockUnmount.mockClear();
});

it('keeps automatic generation disabled on a new empty dashboard', async () => {
  render(<Dashboard />);
  expect(await screen.findByTestId('daily-look')).toHaveAttribute('data-enabled', 'false');
  expect(screen.getByRole('dialog', { name: '' })).toHaveTextContent('Add your capsule');
});

it('preserves established users after wardrobe deletion instead of forcing capsule onboarding again', async () => {
  mockStage.state = { stage: 'complete' };
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
  mockStage.state = { stage: 'complete' };
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
  await act(async () => resolveRefresh(data));
  expect(screen.getByTestId('daily-look')).toBe(widget);
});
