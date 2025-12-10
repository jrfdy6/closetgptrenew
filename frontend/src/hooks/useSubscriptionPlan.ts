'use client';

import { useEffect, useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { subscriptionService, Subscription } from '@/lib/services/subscriptionService';
import { SubscriptionPlan, mapRoleToPlan } from '@/types/subscription';

interface UseSubscriptionPlanResult {
  plan: SubscriptionPlan;
  subscription: Subscription | null;
  loading: boolean;
  error: string | null;
  isFree: boolean;
  isPro: boolean;
  isPremium: boolean;
  canAccess: (required: SubscriptionPlan) => boolean;
}

export const useSubscriptionPlan = (): UseSubscriptionPlanResult => {
  const { user, loading: authLoading } = useAuthContext();
  const [plan, setPlan] = useState<SubscriptionPlan>(SubscriptionPlan.FREE);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      if (authLoading) return;
      if (!user) {
        if (!isMounted) return;
        setPlan(SubscriptionPlan.FREE);
        setSubscription(null);
        setLoading(false);
        setError(null);
        return;
      }

      try {
        const sub = await subscriptionService.getCurrentSubscription(user);
        if (!isMounted) return;
        const mappedPlan = mapRoleToPlan(sub.role);
        setPlan(mappedPlan);
        setSubscription(sub);
        setError(null);
      } catch (err: any) {
        if (!isMounted) return;
        console.error('Failed to load subscription', err);
        setPlan(SubscriptionPlan.FREE);
        setSubscription(null);
        setError(err?.message || 'Unable to load subscription');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    load();
    return () => {
      isMounted = false;
    };
  }, [user, authLoading]);

  const canAccess = (required: SubscriptionPlan) => {
    return plan === SubscriptionPlan.PREMIUM || plan === required || (plan === SubscriptionPlan.PRO && required !== SubscriptionPlan.PREMIUM);
  };

  return {
    plan,
    subscription,
    loading,
    error,
    isFree: plan === SubscriptionPlan.FREE,
    isPro: plan === SubscriptionPlan.PRO,
    isPremium: plan === SubscriptionPlan.PREMIUM,
    canAccess,
  };
};

