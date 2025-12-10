'use client';

import { SubscriptionPlan } from '@/types/subscription';

export const FLATLAY_WEEKLY_LIMITS: Record<SubscriptionPlan, number> = {
  [SubscriptionPlan.FREE]: 1,
  [SubscriptionPlan.PRO]: 5,
  [SubscriptionPlan.PREMIUM]: 9999, // effectively unlimited
};

