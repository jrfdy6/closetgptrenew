'use client';

import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { usageService, type UsageData } from '@/lib/services/usageService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Shirt, Calendar, AlertCircle, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface UsageIndicatorProps {
  className?: string;
  showUpgradePrompt?: boolean;
  compact?: boolean;
}

export default function UsageIndicator({ 
  className = '', 
  showUpgradePrompt = true,
  compact = false 
}: UsageIndicatorProps) {
  const { user } = useFirebase();
  const router = useRouter();
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      fetchUsage();
    }
  }, [user]);

  const fetchUsage = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await usageService.getCurrentUsage(user);
      setUsage(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load usage');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-4">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !usage) {
    return null; // Fail silently
  }

  const outfitPercentage = usageService.getUsagePercentage(
    usage.outfit_generations.current,
    usage.outfit_generations.limit
  );
  const itemPercentage = usageService.getUsagePercentage(
    usage.wardrobe_items.current,
    usage.wardrobe_items.limit
  );

  const outfitColor = usageService.getUsageColor(outfitPercentage);
  const itemColor = usageService.getUsageColor(itemPercentage);
  const outfitBarColor = usageService.getUsageBarColor(outfitPercentage);
  const itemBarColor = usageService.getUsageBarColor(itemPercentage);

  // Check if any limit is reached
  const outfitLimitReached = usage.outfit_generations.limit !== null && 
    usage.outfit_generations.current >= usage.outfit_generations.limit;
  const itemLimitReached = usage.wardrobe_items.limit !== null && 
    usage.wardrobe_items.current >= usage.wardrobe_items.limit;

  if (compact) {
    return (
      <div className={`space-y-2 ${className}`}>
        {/* Outfit Generations */}
        {usage.outfit_generations.limit !== null && (
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                Outfits
              </span>
              <span className={outfitColor}>
                {usage.outfit_generations.current} / {usage.outfit_generations.limit}
              </span>
            </div>
            <Progress value={outfitPercentage} className="h-1.5" />
          </div>
        )}

        {/* Wardrobe Items */}
        {usage.wardrobe_items.limit !== null && (
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="flex items-center gap-1">
                <Shirt className="h-3 w-3" />
                Items
              </span>
              <span className={itemColor}>
                {usage.wardrobe_items.current} / {usage.wardrobe_items.limit}
              </span>
            </div>
            <Progress value={itemPercentage} className="h-1.5" />
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Monthly Usage
        </CardTitle>
        <CardDescription>
          Resets on {usage.reset_date_str || 'the 1st of next month'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Outfit Generations */}
        {usage.outfit_generations.limit !== null && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Outfit Generations
              </span>
              <div className="flex items-center gap-2">
                {outfitLimitReached && (
                  <Badge variant="destructive" className="text-xs">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Limit Reached
                  </Badge>
                )}
                <span className={`text-sm font-semibold ${outfitColor}`}>
                  {usage.outfit_generations.current} / {usage.outfit_generations.limit}
                </span>
              </div>
            </div>
            <Progress 
              value={outfitPercentage} 
              className="h-2"
            />
            {usage.outfit_generations.remaining !== null && (
              <p className="text-xs text-muted-foreground mt-1">
                {usage.outfit_generations.remaining} remaining this month
              </p>
            )}
          </div>
        )}

        {/* Wardrobe Items */}
        {usage.wardrobe_items.limit !== null && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Shirt className="h-4 w-4" />
                Wardrobe Items
              </span>
              <div className="flex items-center gap-2">
                {itemLimitReached && (
                  <Badge variant="destructive" className="text-xs">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Limit Reached
                  </Badge>
                )}
                <span className={`text-sm font-semibold ${itemColor}`}>
                  {usage.wardrobe_items.current} / {usage.wardrobe_items.limit}
                </span>
              </div>
            </div>
            <Progress 
              value={itemPercentage} 
              className="h-2"
            />
            {usage.wardrobe_items.remaining !== null && (
              <p className="text-xs text-muted-foreground mt-1">
                {usage.wardrobe_items.remaining} remaining this month
              </p>
            )}
          </div>
        )}

        {/* Upgrade Prompt */}
        {(outfitLimitReached || itemLimitReached) && showUpgradePrompt && (
          <div className="pt-4 border-t">
            <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <p className="text-sm text-amber-800 dark:text-amber-200 mb-2">
                You've reached your monthly limit. Upgrade for unlimited access!
              </p>
              <Button 
                asChild
                size="sm"
                className="w-full"
              >
                <Link href="/subscription">
                  <Zap className="h-4 w-4 mr-2" />
                  Upgrade to Premium
                </Link>
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

