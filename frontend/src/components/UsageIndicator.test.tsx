import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import UsageIndicator from './UsageIndicator';
import { usageService } from '@/lib/services/usageService';
declare const beforeEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
jest.mock('@/lib/services/usageService', () => ({ usageService: { getCurrentUsage: jest.fn() } }));
beforeEach(() => jest.clearAllMocks());

it.each([false, true])('does not display unverified monthly zero counts, remaining quota or reset dates (compact=%s)', compact => {
  (usageService.getCurrentUsage as jest.Mock).mockResolvedValue({
    outfit_generations: { current: 0, limit: 100, remaining: 100 },
    wardrobe_items: { current: 0, limit: 100, remaining: 100 },
    reset_date_str: 'October 01, 2026',
  });
  render(<UsageIndicator compact={compact} />);
  expect(screen.getByText('Monthly usage totals are unavailable right now.')).toBeVisible();
  expect(screen.queryByText(/0\s*\/\s*100/)).not.toBeInTheDocument();
  expect(screen.queryByText(/remaining this month|resets on|limit reached/i)).not.toBeInTheDocument();
  expect(usageService.getCurrentUsage).not.toHaveBeenCalled();
});
