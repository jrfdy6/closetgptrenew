'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { subscriptionService, type Subscription } from '@/lib/services/subscriptionService';

export default function SubscriptionSuccessPage() {
  const { user, loading: authLoading } = useFirebase();
  const [result, setResult] = useState<{ uid: string; subscription?: Subscription; error?: string } | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    setResult(null);
    if (user && !authLoading) {
      subscriptionService.getCurrentSubscription(user).then(subscription => {
        if (active) setResult({ uid: user.uid, subscription });
      }).catch(() => {
        if (active) setResult({ uid: user.uid, error: 'We could not load your subscription. Please check again.' });
      });
    }
    return () => { active = false; };
  }, [user, authLoading, revision]);

  const current = result?.uid === user?.uid ? result : null;
  const loading = authLoading || Boolean(user && !current);
  const subscription = current?.subscription;
  const paidActive = subscription && ['tier2', 'tier3'].includes(subscription.role) && ['active', 'trialing'].includes(subscription.status);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      <main className="container mx-auto p-6 max-w-2xl mt-12">
        <Card className="text-center">
          <CardHeader>
            <CardTitle className="text-3xl">Your subscription</CardTitle>
            <CardDescription>Check your account after returning from checkout.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? <p role="status" className="flex items-center justify-center gap-2"><Loader2 className="h-5 w-5 animate-spin" />Checking your subscription…</p>
              : !user ? <p>Sign in to check your subscription.</p>
              : current?.error ? <p role="alert">{current.error}</p>
              : paidActive && subscription ? <p>Your account currently has the {subscriptionService.getTierDisplayName(subscription.role)} plan{subscription.status === 'trialing' ? ' on trial' : ' active'}.</p>
              : <p>Your account does not yet show an active paid plan. If you completed checkout, the update may still be processing.</p>}
            <p className="text-sm text-muted-foreground">Returning to this page does not confirm a payment. Your account status is shown above.</p>
            <div className="flex flex-wrap gap-4 justify-center">
              {!loading && user && <Button variant="outline" onClick={() => setRevision(value => value + 1)}>Check again</Button>}
              <Button asChild><Link href={user ? '/subscription' : '/signin?redirect=%2Fsubscription-success'}>{user ? 'View subscription' : 'Sign in'}</Link></Button>
              <Button asChild variant="outline"><Link href="/outfits">My Looks</Link></Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
