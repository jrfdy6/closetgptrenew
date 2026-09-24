"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign } from 'lucide-react';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import { withSubscriptionGate } from '@/components/providers/withSubscriptionGate';
import { SubscriptionPlan } from '@/types/subscription';

function CPWCard() {
  const { loading, error } = useGamificationStats();

  // The stats contract exposes TVE, not cost per wear or its historical trend.
  // Do not reinterpret TVE or turn absent CPW data into a zero-dollar value.
  return (
    <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <DollarSign className="w-5 h-5 text-primary" />
          Cost Per Wear
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div role="status" aria-label="Loading cost per wear" className="space-y-4">
            <div className="h-12 bg-secondary dark:bg-muted rounded animate-pulse" />
            <div className="h-4 bg-secondary dark:bg-muted rounded animate-pulse" />
          </div>
        ) : (
          <p role="status" className="text-sm text-muted-foreground">
            {error ? 'Cost per wear could not be loaded. Please try again later.' : 'Cost per wear is currently unavailable.'}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default withSubscriptionGate(CPWCard, SubscriptionPlan.PRO);
