'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Loader2 } from 'lucide-react';
import { subscriptionService } from '@/lib/services/subscriptionService';

export default function SubscriptionSuccessPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useFirebase();
  const [loading, setLoading] = useState(true);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (sessionId && user) {
      // Wait a moment for webhook to process, then refresh subscription
      setTimeout(async () => {
        try {
          await subscriptionService.getCurrentSubscription(user);
          setLoading(false);
        } catch (error) {
          console.error('Error fetching subscription:', error);
          setLoading(false);
        }
      }, 2000);
    } else {
      setLoading(false);
    }
  }, [sessionId, user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex items-center justify-center">
        <Navigation />
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      
      <div className="container mx-auto p-6 max-w-2xl mt-12">
        <Card className="text-center">
          <CardHeader>
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <CardTitle className="text-3xl">Payment Successful!</CardTitle>
            <CardDescription>
              Your subscription has been activated
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Thank you for subscribing! You now have access to all premium features.
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => router.push('/subscription')}>
                View Subscription
              </Button>
              <Button variant="outline" onClick={() => router.push('/outfits')}>
                Start Generating Outfits
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

