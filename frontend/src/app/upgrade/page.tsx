'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Crown, Sparkles, Loader2, CreditCard } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import { 
  subscriptionService, 
  SUBSCRIPTION_TIERS, 
  type Subscription 
} from '@/lib/services/subscriptionService';

export default function UpgradePage() {
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
      console.error('Error fetching subscription:', err);
      setError(err instanceof Error ? err.message : 'Failed to load subscription');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (role: string) => {
    if (role === 'tier1' || !user) return;
    
    setUpgrading(role);
    setError(null);
    
    try {
      const { checkout_url } = await subscriptionService.createCheckoutSession(user, role);
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  const currentRole = subscription?.role || 'tier1';
  const currentTierInfo = subscriptionService.getTierInfo(currentRole);

  const tiers = [
    {
      id: 'tier1',
      name: 'Free',
      description: 'Everything you need to catalogue outfits and start building your personal lookbook.',
      price: '$0',
      cadence: 'Included',
      highlight: 'New wardrobe creators',
      perks: [
        '1 premium flat lay credit each week',
        'Unlimited manual outfits',
        'Wardrobe organization and tagging',
        'Mobile-friendly outfit builder'
      ],
      cta: "You're here now"
    },
    {
      id: 'tier2',
      name: 'Pro',
      description: 'Upgrade for weekly outfit visuals, priority processing, and deeper personalization.',
      price: '$7.00',
      cadence: 'per month',
      highlight: 'Style enthusiasts',
      perks: [
        '7 premium flat lay credits per week',
        'Priority flat lay rendering queue',
        'Unlimited saved outfits & notes',
        'Style persona analysis',
        'Advanced outfit filtering',
        'Early access to styling experiments'
      ],
      cta: 'Join Pro',
      popular: true
    },
    {
      id: 'tier3',
      name: 'Premium',
      description: 'For creators and teams who want premium visuals on demand and concierge support.',
      price: '$11.00',
      cadence: 'per month',
      highlight: 'Creators & stylists',
      perks: [
        '30 premium flat lay credits per week',
        'Concierge flat lay rush requests',
        'Branded export-ready visuals',
        'All Pro features',
        'Premium support',
        'Quarterly wardrobe performance review'
      ],
      cta: 'Join Premium'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <section className="text-center space-y-4">
          <Badge className="bg-amber-600 text-white rounded-full px-4 py-1 text-xs uppercase tracking-wide">
            Premium Flat Lays
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-stone-900 dark:text-stone-100">
            Choose your styling pace
          </h1>
          <p className="text-stone-600 dark:text-stone-300 text-base sm:text-lg max-w-2xl mx-auto">
            Easy Outfit caters to every type of closet. Keep your free plan for casual outfit saving or
            upgrade for magazine-ready flat lays, priority rendering, and concierge support.
          </p>
          {subscription && (
            <div className="mt-4">
              <Badge variant="secondary">
                Current Plan: {currentTierInfo?.name || 'Free'} • {subscription.flatlays_remaining} flat lays remaining
              </Badge>
            </div>
          )}
          {error && (
            <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg max-w-md mx-auto">
              {error}
            </div>
          )}
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {tiers.map((tier) => (
            <Card
              key={tier.id}
              className={`relative overflow-hidden border-2 ${
                tier.id === 'tier2'
                  ? 'border-amber-500 shadow-xl shadow-amber-500/10'
                  : 'border-transparent shadow-md'
              }`}
            >
              {tier.id === 'tier2' && (
                <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-amber-500 text-white px-4 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  Most loved
                </div>
              )}
              {tier.id === 'tier3' && (
                <div className="absolute top-4 right-4 text-amber-500">
                  <Crown className="h-6 w-6" />
                </div>
              )}

              <CardHeader className="space-y-2">
                <CardTitle className="text-2xl font-serif">{tier.name}</CardTitle>
                <p className="text-sm text-stone-600 dark:text-stone-300">{tier.description}</p>
              </CardHeader>

              <CardContent className="space-y-6">
                <div>
                  <span className="text-3xl font-bold text-stone-900 dark:text-stone-100">
                    {tier.price}
                  </span>
                  <span className="text-sm text-stone-500 dark:text-stone-400 ml-2">
                    {tier.cadence}
                  </span>
                  {tier.annual && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                      {tier.annual}
                    </p>
                  )}
                </div>

                <ul className="space-y-3 text-sm text-stone-700 dark:text-stone-200">
                  {tier.perks.map((perk) => (
                    <li key={perk} className="flex items-start gap-2">
                      <Check className="h-4 w-4 mt-0.5 text-amber-500" />
                      <span>{perk}</span>
                    </li>
                  ))}
                </ul>

                <div className="pt-2">
                  {tier.id === currentRole ? (
                    <Button disabled className="w-full" variant="outline">
                      Current Plan
                    </Button>
                  ) : tier.id === 'tier1' ? (
                    <Button disabled className="w-full bg-stone-300 text-stone-600" variant="secondary">
                      {tier.cta}
                    </Button>
                  ) : (
                    <Button 
                      onClick={() => handleUpgrade(tier.id)}
                      disabled={upgrading === tier.id}
                      className="w-full bg-stone-900 text-white hover:bg-stone-800"
                    >
                      {upgrading === tier.id ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        tier.cta
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card className="border-2 border-stone-200 dark:border-stone-700">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                What counts as a premium flat lay?
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-stone-600 dark:text-stone-300 space-y-2">
              <p>
                Every time you request a premium flat lay we stitch together your real garment photos,
                apply background removal, drop shadows, and deliver a cohesive, share-worthy visual for
                your outfit.
              </p>
              <p>
                Credits reset weekly so you can experiment with new outfits every few days without
                worrying about running out mid-month.
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-stone-200 dark:border-stone-700">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                Need more than 30 flat lays a week?
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-stone-600 dark:text-stone-300">
              <p>
                Agencies, stylists, and wardrobe teams can partner with Easy Outfit for enterprise-level
                support, custom branding, and SLA-backed turnaround times.
              </p>
              <Button asChild variant="outline" className="w-fit">
                <a href="mailto:hello@easyoutfitapp.com" target="_blank" rel="noopener noreferrer">
                  Talk with our team
                </a>
              </Button>
            </CardContent>
          </Card>
        </section>

        {/* Manage Subscription Section */}
        {subscription && subscription.role !== 'tier1' && (
          <Card className="border-2 border-stone-200 dark:border-stone-700">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                Manage Subscription
              </CardTitle>
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
      </main>

      <ClientOnlyNav />
    </div>
  );
}

