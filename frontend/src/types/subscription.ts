'use client';

export enum SubscriptionPlan {
  FREE = 'FREE',
  PRO = 'PRO',
  PREMIUM = 'PREMIUM',
}

export const PLAN_HIERARCHY: Record<SubscriptionPlan, number> = {
  [SubscriptionPlan.FREE]: 0,
  [SubscriptionPlan.PRO]: 1,
  [SubscriptionPlan.PREMIUM]: 2,
};

export const hasAccess = (userPlan: string, requiredPlan: SubscriptionPlan): boolean => {
  const userLevel = PLAN_HIERARCHY[userPlan as SubscriptionPlan] ?? 0;
  const requiredLevel = PLAN_HIERARCHY[requiredPlan];
  return userLevel >= requiredLevel;
};

export const mapRoleToPlan = (role?: string): SubscriptionPlan => {
  switch ((role || '').toLowerCase()) {
    case 'tier2':
    case 'pro':
      return SubscriptionPlan.PRO;
    case 'tier3':
    case 'premium':
      return SubscriptionPlan.PREMIUM;
    default:
      return SubscriptionPlan.FREE;
  }
};

