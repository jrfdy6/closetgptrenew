/**
 * Usage Service
 * Handles monthly usage tracking for outfit generations and wardrobe items
 */

import { User } from 'firebase/auth';
import { performanceService } from './performanceService';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';

export interface UsageData {
  outfit_generations: {
    current: number;
    limit: number | null;
    remaining: number | null;
  };
  wardrobe_items: {
    current: number;
    limit: number | null;
    remaining: number | null;
  };
  reset_date: number;
  reset_date_str: string | null;
}

class UsageService {
  private async getAuthToken(user: User | null): Promise<string> {
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  async getCurrentUsage(user: User | null, forceRefresh: boolean = false): Promise<UsageData> {
    if (!user) {
      throw new Error('User not authenticated');
    }

    const cacheKey = performanceService.getUsageKey(user.uid);
    
    // Check cache first unless force refresh
    if (!forceRefresh) {
      const cached = performanceService.get<UsageData>(cacheKey);
      if (cached) {
        return cached;
      }
    }

    return performanceService.getUsage(user.uid, async () => {
      const token = await this.getAuthToken(user);
      
      const response = await fetch(`${API_URL}/api/payments/usage/current`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to fetch usage' }));
        throw new Error(error.detail || 'Failed to fetch usage');
      }

      return response.json();
    });
  }

  /**
   * Invalidate usage cache (call after tracking usage)
   */
  invalidateCache(userId: string): void {
    performanceService.invalidate(performanceService.getUsageKey(userId));
  }

  getUsagePercentage(current: number, limit: number | null): number {
    if (limit === null) return 0; // Unlimited
    if (limit === 0) return 100;
    return Math.min(100, (current / limit) * 100);
  }

  getUsageColor(percentage: number): string {
    if (percentage < 75) return 'text-green-600 dark:text-green-400';
    if (percentage < 90) return 'text-yellow-600 dark:text-yellow-400';
    if (percentage < 100) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  }

  getUsageBarColor(percentage: number): string {
    if (percentage < 75) return 'bg-green-500';
    if (percentage < 90) return 'bg-yellow-500';
    if (percentage < 100) return 'bg-orange-500';
    return 'bg-red-500';
  }
}

export const usageService = new UsageService();

