'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from 'lucide-react';

interface UsageIndicatorProps {
  className?: string;
  showUpgradePrompt?: boolean;
  compact?: boolean;
}

export default function UsageIndicator({ className = '', compact = false }: UsageIndicatorProps) {
  // The legacy monthly ledger does not cover every save/generation path and
  // returns zero when unavailable. Do not present it as confirmed quota usage.
  // Weekly flatlay credits are displayed separately by the subscription page.
  const message = 'Monthly usage totals are unavailable right now.';

  if (compact) {
    return <p className={`text-sm text-muted-foreground ${className}`}>{message}</p>;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Monthly Usage
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  );
}
