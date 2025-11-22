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
import { Loader2, Check, CreditCard } from 'lucide-react';

export default function SubscriptionPage() {
  const { user, loading: authLoading } = useFirebase();
  const router = useRouter();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  const handleUpgrade = async (tier: string) => {
    if (tier === 'tier1' || !user) return;
    
    setUpgrading(tier);
    setError(null);
    
    try {
      const { checkout_url } = await subscriptionService.createCheckoutSession(user, tier);
      // Redirect to Stripe checkout
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      
      <div className="container mx-auto p-6 max-w-6xl mt-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Subscription Plans</h1>
          <p className="text-muted-foreground">
            Choose the plan that's right for you
          </p>
          {subscription && (
            <div className="mt-4">
              <Badge variant="secondary">
                Current Plan: {currentTierInfo?.name || 'Free'}
                {subscription.flatlays_remaining !== undefined && (
                  <span> • {subscription.flatlays_remaining} flat lays remaining</span>
                )}
              </Badge>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {SUBSCRIPTION_TIERS.map((tier) => {
            const isCurrent = currentTier === tier.id;
            const isUpgrading = upgrading === tier.id;
            const canUpgrade = !isCurrent && (tier.id > currentTier || currentTier === 'tier1');
            
            return (
              <Card 
                key={tier.id} 
                className={`relative ${isCurrent ? 'border-primary shadow-lg' : ''} ${tier.popular ? 'border-2' : ''}`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary">Most Popular</Badge>
                  </div>
                )}
                
                <CardHeader>
                  <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  <CardDescription>
                    <span className="text-3xl font-bold">{tier.price}</span>
                    <span className="text-muted-foreground">/month</span>
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {tier.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start">
                        <Check className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  {isCurrent ? (
                    <Button disabled className="w-full" variant="outline">
                      Current Plan
                    </Button>
                  ) : (
                    <Button
                      onClick={() => handleUpgrade(tier.id)}
                      disabled={isUpgrading || !canUpgrade}
                      className="w-full"
                      variant={tier.popular ? 'default' : 'outline'}
                    >
                      {isUpgrading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : canUpgrade ? (
                        'Upgrade'
                      ) : (
                        'Downgrade'
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {subscription && subscription.role !== 'tier1' && (
          <Card>
            <CardHeader>
              <CardTitle>Manage Subscription</CardTitle>
              <CardDescription>
                Update your payment method, cancel, or change your plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleManageSubscription} variant="outline" className="w-full">
                <CreditCard className="mr-2 h-4 w-4" />
                Open Customer Portal
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      <ClientOnlyNav />
    </div>
  );
}

