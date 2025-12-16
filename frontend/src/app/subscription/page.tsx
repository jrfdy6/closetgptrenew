'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { 
  subscriptionService, 
  SUBSCRIPTION_TIERS,
  type Subscription 
} from '@/lib/services/subscriptionService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Loader2, 
  Check, 
  CreditCard, 
  Sparkles, 
  Zap, 
  Shield, 
  Info,
  Calendar,
  TrendingUp,
  Crown,
  Star
} from 'lucide-react';
import UsageIndicator from '@/components/UsageIndicator';

export default function SubscriptionPage() {
  const { user, loading: authLoading } = useFirebase();
  const router = useRouter();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<'month' | 'year'>('month');

  useEffect(() => {
    if (user && !authLoading) {
      fetchSubscription();
    } else if (!authLoading && !user) {
      router.push('/signin');
    }
  }, [user, authLoading]);

  const fetchSubscription = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const sub = await subscriptionService.getCurrentSubscription(user);
      setSubscription(sub);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load subscription');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tier: string, interval: 'month' | 'year' = 'month') => {
    if (tier === 'tier1' || !user) return;
    
    setUpgrading(tier);
    setError(null);
    
    try {
      const { checkout_url } = await subscriptionService.createCheckoutSession(user, tier, interval);
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start checkout');
      setUpgrading(null);
    }
  };

  const handleManageSubscription = async () => {
    if (!user) return;
    
    try {
      const { url } = await subscriptionService.createPortalSession(user);
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open customer portal');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!user) {
    router.push('/signin');
    return null;
  }

  const currentTier = subscription?.role || 'tier1';
  const currentTierInfo = subscriptionService.getTierInfo(currentTier);
  const flatlaysRemaining = subscription?.flatlays_remaining ?? 0;
  const flatlayLimit = currentTierInfo?.limit ? parseInt(currentTierInfo.limit.split('/')[0]) : 1;
  const flatlayUsage = flatlayLimit - flatlaysRemaining;
  const flatlayPercentage = flatlayLimit > 0 ? (flatlayUsage / flatlayLimit) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      
      <div className="container mx-auto p-6 max-w-6xl mt-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Crown className="h-8 w-8 text-amber-600 dark:text-amber-400" />
            <h1 className="text-4xl font-bold">Subscription Plans</h1>
          </div>
          <p className="text-muted-foreground text-lg">
            Choose the plan that's right for you. Upgrade or downgrade anytime.
          </p>
        </div>

        {/* Usage Indicator */}
        <UsageIndicator className="mb-8" />

        {/* Current Subscription Status */}
        {subscription && (
          <Card className="mb-8 border-2 border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Star className="h-5 w-5 text-primary" />
                    Your Current Plan: {currentTierInfo?.name || 'Free'}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {subscription.is_trialing ? (
                      <span className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                        <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                        Free Trial Active • {subscription.days_remaining_in_trial || 0} days remaining
                      </span>
                    ) : subscription.status === 'active' ? (
                      <span className="flex items-center gap-2 text-green-600 dark:text-green-400">
                        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                        Active subscription
                      </span>
                    ) : (
                      <span className="text-muted-foreground">Subscription status: {subscription.status}</span>
                    )}
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="text-lg px-4 py-2">
                  {currentTierInfo?.price}/month
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Trial Countdown */}
                {subscription.is_trialing && subscription.days_remaining_in_trial !== undefined && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-blue-700 dark:text-blue-300 flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Free Trial
                      </span>
                      <Badge variant="outline" className="border-blue-300 text-blue-700 dark:text-blue-300">
                        {subscription.days_remaining_in_trial} {subscription.days_remaining_in_trial === 1 ? 'day' : 'days'} left
                      </Badge>
                    </div>
                    <p className="text-xs text-blue-600 dark:text-blue-400">
                      Your 30-day free trial ends soon. You'll be charged automatically unless you cancel.
                    </p>
                  </div>
                )}

                {/* Flat Lay Usage */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      Flat Lays This Week
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {flatlaysRemaining} of {flatlayLimit} remaining
                    </span>
                  </div>
                  <Progress value={flatlayPercentage} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {flatlayUsage} used • Resets weekly
                  </p>
                </div>

                {/* Quick Actions */}
                {subscription.role !== 'tier1' && (
                  <div className="flex gap-2 pt-2">
                    <Button 
                      onClick={handleManageSubscription} 
                      variant="outline" 
                      size="sm"
                      className="flex-1"
                    >
                      <CreditCard className="mr-2 h-4 w-4" />
                      Manage Subscription
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Subscription Tiers */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Available Plans</h2>
            
            {/* Billing Cycle Toggle */}
            <div className="flex items-center gap-4 bg-amber-100 dark:bg-amber-900/30 p-3 rounded-lg">
              <span className={`text-sm font-medium ${billingCycle === 'month' ? 'text-amber-900 dark:text-amber-100' : 'text-muted-foreground'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingCycle(billingCycle === 'month' ? 'year' : 'month')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  billingCycle === 'year' 
                    ? 'bg-amber-600' 
                    : 'bg-amber-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingCycle === 'year' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-sm font-medium ${billingCycle === 'year' ? 'text-amber-900 dark:text-amber-100' : 'text-muted-foreground'}`}>
                Yearly
              </span>
              {billingCycle === 'year' && (
                <Badge className="bg-green-600 text-white ml-2">
                  Save ~28%
                </Badge>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {SUBSCRIPTION_TIERS.map((tier) => {
              const isCurrent = currentTier === tier.id;
              const isUpgrading = upgrading === tier.id;
              const canUpgrade = !isCurrent && (tier.id > currentTier || currentTier === 'tier1');
              
              return (
                <Card 
                  key={tier.id} 
                  className={`relative transition-all hover:shadow-lg ${
                    isCurrent ? 'border-primary border-2 shadow-lg scale-105' : ''
                  } ${tier.popular ? 'border-2 border-amber-400' : ''}`}
                >
                  {tier.popular && !isCurrent && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-amber-500 text-white px-3 py-1">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Most Popular
                      </Badge>
                    </div>
                  )}
                  
                  {isCurrent && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-primary text-white px-3 py-1">
                        <Check className="h-3 w-3 mr-1" />
                        Current Plan
                      </Badge>
                    </div>
                  )}
                  
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between mb-2">
                      <CardTitle className="text-2xl">{tier.name}</CardTitle>
                      {tier.id === 'tier3' && <Crown className="h-5 w-5 text-amber-500" />}
                    </div>
                    <CardDescription>
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-bold">
                          {billingCycle === 'year' && tier.id !== 'tier1' 
                            ? tier.id === 'tier2' 
                              ? '$60'
                              : '$85'
                            : tier.price}
                        </span>
                        <span className="text-muted-foreground">
                          {billingCycle === 'year' ? '/year' : '/month'}
                        </span>
                      </div>
                      {tier.pricePerMonth > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {billingCycle === 'year' 
                            ? 'Billed yearly • Cancel anytime'
                            : 'Billed monthly • Cancel anytime'}
                        </p>
                      )}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-3 mb-6">
                      <div className="text-sm font-semibold text-muted-foreground mb-2">
                        What's included:
                      </div>
                      <ul className="space-y-2.5">
                        {tier.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start text-sm">
                            <Check className="h-4 w-4 text-primary mr-2 mt-0.5 flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {isCurrent ? (
                      <Button disabled className="w-full" variant="outline">
                        <Check className="mr-2 h-4 w-4" />
                        Current Plan
                      </Button>
                    ) : (
                      <div className="space-y-2">
                        {canUpgrade && tier.id !== 'tier1' && !subscription?.trial_used && billingCycle === 'month' && (
                          <div className="text-center">
                            <Badge variant="secondary" className="text-xs mb-2 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              <Calendar className="h-3 w-3 mr-1" />
                              30-Day Free Trial
                            </Badge>
                          </div>
                        )}
                      <Button
                        onClick={() => handleUpgrade(tier.id, billingCycle)}
                        disabled={isUpgrading || !canUpgrade}
                        className="w-full"
                        variant={tier.popular ? 'default' : 'outline'}
                        size="lg"
                      >
                        {isUpgrading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : canUpgrade ? (
                          <>
                            <Zap className="mr-2 h-4 w-4" />
                            {subscription?.trial_used 
                              ? 'Upgrade Now' 
                              : billingCycle === 'month'
                              ? 'Start Free Trial'
                              : 'Subscribe Now'}
                          </>
                        ) : (
                          'Downgrade'
                        )}
                      </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Information Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Shield className="h-5 w-5 text-blue-600" />
                Secure & Flexible
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>• Secure payment processing via Stripe</p>
              <p>• Cancel or change your plan anytime</p>
              <p>• No long-term commitments</p>
              <p>• Instant access to all features</p>
            </CardContent>
          </Card>

          <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Info className="h-5 w-5 text-green-600" />
                Need Help?
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>• Questions about billing? Use the Customer Portal</p>
              <p>• Flat lays reset weekly on your billing date</p>
              <p>• Upgrade anytime to get more features</p>
              <p>• All plans include full wardrobe management</p>
            </CardContent>
          </Card>
        </div>

        {/* Customer Portal Section */}
        {subscription && subscription.role !== 'tier1' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Manage Your Subscription
              </CardTitle>
              <CardDescription>
                Use the Customer Portal to update payment methods, view billing history, or cancel your subscription
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={handleManageSubscription} 
                variant="outline" 
                className="w-full"
                size="lg"
              >
                <CreditCard className="mr-2 h-4 w-4" />
                Open Customer Portal
              </Button>
              <p className="text-xs text-muted-foreground mt-3 text-center">
                You'll be redirected to Stripe's secure portal to manage your subscription
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <ClientOnlyNav />
    </div>
  );
}

