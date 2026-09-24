import { render, screen } from '@testing-library/react';
import CPWCard from './CPWCard';
import { useGamificationStats } from '@/hooks/useGamificationStats';

jest.mock('@/hooks/useGamificationStats', () => ({ useGamificationStats: jest.fn() }));
jest.mock('@/components/providers/withSubscriptionGate', () => ({ withSubscriptionGate: (component: unknown) => component }));

it('shows unsupported CPW as unavailable instead of converting TVE or absence to zero', () => {
  jest.mocked(useGamificationStats).mockReturnValue({ stats: null, loading: false, error: null, refetch: jest.fn() });
  render(<CPWCard />);
  expect(screen.getByRole('status')).toHaveTextContent('Cost per wear is currently unavailable.');
  expect(screen.queryByText(/\$0\.00|Stable this month|Set your spending/)).not.toBeInTheDocument();
});

it('distinguishes a read error from unavailable data', () => {
  jest.mocked(useGamificationStats).mockReturnValue({ stats: null, loading: false, error: 'Failed', refetch: jest.fn() });
  render(<CPWCard />);
  expect(screen.getByRole('status')).toHaveTextContent('could not be loaded');
});
