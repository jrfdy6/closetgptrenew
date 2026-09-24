import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChallengeList from './ChallengeList';
import ChallengeCard from './ChallengeCard';
import BadgeDisplay from './BadgeDisplay';
import GamificationSummaryCard from './GamificationSummaryCard';
import AIFitScoreCard from './AIFitScoreCard';
import TVECard from './TVECard';
import XPNotification, { XPNotificationStack } from './XPNotification';
import { Progress } from '@/components/ui/progress';

declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;

const originalPointerEvent = window.PointerEvent;
const mockRefetch = jest.fn();
const mockToast = jest.fn();
const mockStart = jest.fn();
let mockStats: any;
let mockBadges: any;
let mockChallenges: any;
jest.mock('@/hooks/useGamificationStats', () => ({
  useGamificationStats: () => mockStats,
  useBadges: () => mockBadges,
  useChallenges: () => mockChallenges,
}));
jest.mock('@/components/ui/use-toast', () => ({ useToast: () => ({ toast: mockToast }) }));
jest.mock('@/components/providers/withSubscriptionGate', () => ({ withSubscriptionGate: (component: any) => component }));

const challenge = { challenge_id: 'wear-five', title: 'Wear Five Outfits', description: 'Wear five outfits this week.', progress: 2, target: 5, status: 'in_progress', rewards: { xp: 50 } };
beforeEach(() => {
  jest.clearAllMocks();
  if (!window.PointerEvent) Object.defineProperty(window, 'PointerEvent', { configurable: true, value: MouseEvent });
  mockStats = { stats: { xp: 150, level: { level: 2, tier: 'Explorer', xp_for_next_level: 300, progress_percentage: 25 }, badges: ['starter_closet'], active_challenges_count: 1 }, loading: false, error: null, refetch: mockRefetch };
  mockBadges = { badges: [], loading: false, error: null, refetch: mockRefetch };
  mockChallenges = { activeChallenges: [], availableChallenges: [], completedChallenges: [], historyError: null, loading: false, error: null, startChallenge: mockStart, refetch: mockRefetch };
});
afterEach(() => { jest.useRealTimers(); Object.defineProperty(window, 'PointerEvent', { configurable: true, value: originalPointerEvent }); });

it('exposes the real level progress and one keyboard link to existing challenges', () => {
  render(<GamificationSummaryCard />);
  const bar = screen.getByRole('progressbar', { name: 'Experience toward the next level' });
  expect(bar).toHaveAttribute('aria-valuenow', '25');
  expect(bar).toHaveAttribute('aria-valuetext', '150 XP; 150 XP until Level 3');
  expect(screen.getByRole('link', { name: 'View All Challenges' })).toHaveAttribute('href', '/challenges');
  expect(screen.queryByRole('button', { name: 'View All Challenges' })).not.toBeInTheDocument();
});

it('offers explicit progress retry without showing fabricated level or zero totals', () => {
  mockStats = { ...mockStats, stats: null, error: 'offline' };
  render(<GamificationSummaryCard />);
  expect(screen.queryByText('Level 1')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
  expect(mockRefetch).toHaveBeenCalledTimes(1);
});

it('keeps score/value transport failures distinct from onboarding or insufficient activity', () => {
  mockStats = { ...mockStats, stats: null, error: 'offline' };
  render(<><AIFitScoreCard /><TVECard /></>);
  expect(screen.getByText('Your AI Fit Score could not be loaded. Please try again.')).toBeInTheDocument();
  expect(screen.getByText('Your wardrobe value could not be loaded. Please try again.')).toBeInTheDocument();
  expect(screen.queryByText(/Complete onboarding|Rate outfits to build/)).not.toBeInTheDocument();
  expect(screen.getAllByRole('button', { name: 'Try again' })).toHaveLength(2);
});

it('shows badge errors with retry and an honest zero-earned state', () => {
  mockBadges.error = 'offline';
  const view = render(<BadgeDisplay />);
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
  expect(mockRefetch).toHaveBeenCalledTimes(1);
  mockBadges.error = null;
  view.rerender(<BadgeDisplay />);
  expect(screen.getByText(/Add clothes, log outfits/)).toBeInTheDocument();
  expect(screen.queryByText('Locked')).not.toBeInTheDocument();
});

it('supports long badge names, keyboard focus and valid modal description markup', async () => {
  mockBadges.badges = [{ id: 'annual_wardrobe_master_cycle_2', name: 'Annual Wardrobe Master — Cycle 2', description: 'Fifty-two qualifying weeks.', rarity: 'legendary', unlock_condition: 'Complete the annual challenge.' }];
  const { container } = render(<BadgeDisplay />);
  const badge = screen.getByRole('button', { name: 'View Annual Wardrobe Master — Cycle 2 badge' });
  expect(badge).toHaveClass('w-full', 'min-h-28');
  await userEvent.tab();
  expect(badge).toHaveFocus();
  await userEvent.keyboard('{Enter}');
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByText('Fifty-two qualifying weeks.')).toBeInTheDocument();
  expect(container.querySelector('p p')).toBeNull();
});

it('renders real completed challenge history in the existing tab', async () => {
  mockChallenges.completedChallenges = [{ ...challenge, instance_id: 'week-1', status: 'completed', completed_at: '2026-09-22T12:00:00Z' }];
  render(<ChallengeList />);
  await userEvent.click(screen.getByRole('tab', { name: 'Completed (1)' }));
  expect(screen.getByText(challenge.title)).toBeInTheDocument();
  expect(screen.getByText('Completed')).toBeInTheDocument();
  expect(screen.queryByText('Completed challenges will appear here. Keep going!')).not.toBeInTheDocument();
});

it('does not disguise a completed-history failure as no completed challenges', async () => {
  mockChallenges.historyError = 'Your completed challenges could not be loaded. Please try again.';
  mockChallenges.activeChallenges = [challenge];
  render(<ChallengeList />);
  expect(screen.getByText(challenge.title)).toBeInTheDocument();
  await userEvent.click(screen.getByRole('tab', { name: 'Completed' }));
  expect(screen.getByRole('status')).toHaveTextContent('could not be loaded');
  expect(screen.queryByText(/No completed challenges yet/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
  expect(mockRefetch).toHaveBeenCalledTimes(1);
});

it('locks repeated starts until the server result and then restores available actions', async () => {
  let finish!: (value: boolean) => void;
  mockStart.mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  mockChallenges.availableChallenges = [{ ...challenge, featured: true }];
  render(<ChallengeList featured />);
  const start = screen.getByRole('button', { name: 'Start Challenge' });
  fireEvent.click(start);
  fireEvent.click(start);
  expect(mockStart).toHaveBeenCalledTimes(1);
  expect(screen.getByRole('button', { name: 'Starting…' })).toBeDisabled();
  await act(async () => { finish(false); });
  expect(screen.getByRole('button', { name: 'Start Challenge' })).toBeEnabled();
  expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Could not confirm challenge start' }));
});

it('measures annual progress by qualifying weeks, with an explicit outfit and week label', () => {
  render(<ChallengeCard variant="active" challenge={{ ...challenge, challenge_id: 'annual_wardrobe_master', progress: { total_outfits: 260, weeks_completed: 2 }, expires_at: 'invalid' }} />);
  const bar = screen.getByRole('progressbar', { name: `${challenge.title} progress` });
  expect(Number(bar.getAttribute('aria-valuenow'))).toBeCloseTo(100 * 2 / 52);
  expect(bar).toHaveAttribute('aria-valuetext', '260/260 outfits, 2/52 weeks');
  expect(screen.queryByText(/Invalid Date/)).not.toBeInTheDocument();
});

it('clamps accessible progress values and preserves an explicit indeterminate state', () => {
  const view = render(<Progress aria-label="Test progress" value={140} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100');
  view.rerender(<Progress aria-label="Test progress" value={-10} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0');
  view.rerender(<Progress aria-label="Test progress" value={Number.NaN} />);
  expect(screen.getByRole('progressbar')).not.toHaveAttribute('aria-valuenow');
});

it('announces separate XP notices in normal flow and allows keyboard dismissal', async () => {
  const dismiss = jest.fn();
  render(<XPNotificationStack notifications={[{ id: 'one', xp: 10, reason: 'Outfit worn' }, { id: 'two', xp: 20, reason: 'Feedback saved', levelUp: true, newLevel: 2 }]} onDismiss={dismiss} />);
  expect(screen.getAllByRole('status')).toHaveLength(2);
  expect(screen.getByText('Level 2 reached!')).toBeInTheDocument();
  expect(screen.getByText('+10 XP').closest('.relative')).not.toHaveClass('fixed');
  await userEvent.tab();
  await userEvent.keyboard('{Enter}');
  expect(dismiss).toHaveBeenCalledWith('one');
});

it('does not extend the notice lifetime when a new dismiss callback renders', () => {
  jest.useFakeTimers();
  const first = jest.fn(); const second = jest.fn();
  const view = render(<XPNotification xp={10} reason="Outfit worn" onDismiss={first} />);
  act(() => { jest.advanceTimersByTime(2000); });
  view.rerender(<XPNotification xp={10} reason="Outfit worn" onDismiss={second} />);
  act(() => { jest.advanceTimersByTime(1500); });
  expect(first).not.toHaveBeenCalled();
  expect(second).toHaveBeenCalledTimes(1);
});

it('preserves known progress during refresh and labels it as refreshing', () => {
  mockStats.loading = true;
  render(<GamificationSummaryCard />);
  expect(screen.getByText('Level 2')).toBeInTheDocument();
  expect(screen.getByRole('status')).toHaveTextContent('Refreshing');
  expect(screen.getByRole('progressbar').closest('[aria-busy]')).toHaveAttribute('aria-busy', 'true');
  expect(screen.queryByLabelText('Loading your progress')).not.toBeInTheDocument();
});

it('labels the thirty-wears challenge as qualifying items rather than a single wear', () => {
  render(<ChallengeCard variant="active" challenge={{ ...challenge, challenge_id: '30_wears_challenge', title: 'Thirty Wears', progress: 0, target: 1 }} />);
  expect(screen.getByText('0/1 items at 30 wears')).toBeInTheDocument();
  expect(screen.getByRole('progressbar', { name: 'Thirty Wears progress' })).toHaveAttribute('aria-valuetext', '0/1 items at 30 wears');
});

it('names all rendered score and value progress bars when the subscription gate is open', () => {
  mockStats.stats.ai_fit_score = { total_score: 37, explanations: [], next_milestone: { current: 4, target: 10, message: 'Rate ten outfits.' } };
  mockStats.stats.tve = { total_tve: 42, total_wardrobe_cost: 100, percent_recouped: 42, annual_potential_range: { low: 100, high: 150 } };
  render(<><AIFitScoreCard /><TVECard /></>);
  expect(screen.getByRole('progressbar', { name: 'AI Fit Score' })).toHaveAttribute('aria-valuenow', '37');
  expect(screen.getByRole('progressbar', { name: 'AI Fit Score next milestone' })).toHaveAttribute('aria-valuetext', '4 of 10');
  expect(screen.getByRole('progressbar', { name: 'Estimated wardrobe investment recouped' })).toHaveAttribute('aria-valuenow', '42');
});
