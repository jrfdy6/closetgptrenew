"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { DollarSign, TrendingUp, Info, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function TVECard() {
  const { stats, loading, error } = useGamificationStats();

  if (loading) {
    return (
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-12 bg-secondary dark:bg-muted rounded animate-pulse" />
            <div className="h-4 bg-secondary dark:bg-muted rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.tve) {
    return (
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Complete onboarding to see your value unlocked
          </p>
        </CardContent>
      </Card>
    );
  }

  const { tve } = stats;
  const totalTVE = tve.total_tve || 0;
  const totalWardrobeCost = tve.total_wardrobe_cost || 0;
  const percentRecouped = tve.percent_recouped || 0;
  const annualPotentialRange = tve.annual_potential_range || { low: 0, high: 0 };

  return (
    <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70 overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
          Total Value Extracted
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  TVE tracks value unlocked from your wardrobe. Each wear adds value when you actively rotate your items weekly!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          Track your wardrobe investment returns
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Total Value Unlocked - Big Number */}
          <div>
            <div className="flex items-baseline gap-2 mb-1">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="text-4xl font-display font-semibold gradient-copper-text"
              >
                ${totalTVE.toFixed(2)}
              </motion.div>
              <span className="text-sm text-muted-foreground">unlocked</span>
            </div>
            <p className="text-xs text-muted-foreground">
              {percentRecouped.toFixed(1)}% of your ${totalWardrobeCost.toFixed(0)} wardrobe investment
            </p>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">
                Investment Recouped
              </span>
              <span className="text-sm font-bold gradient-copper-text">
                {percentRecouped.toFixed(1)}%
              </span>
            </div>
            <Progress value={Math.min(percentRecouped, 100)} className="h-1" />
            {percentRecouped >= 100 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2 flex items-center gap-1 text-xs text-[var(--copper-dark)]"
              >
                <Sparkles className="w-3 h-3" />
                <span className="font-medium">Full investment recouped! Now generating bonus value!</span>
              </motion.div>
            )}
          </div>

          {/* Annual Potential Range */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 rounded-lg bg-secondary dark:bg-muted border border-border/60 dark:border-border/70"
          >
            <div className="flex items-start gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-[var(--copper-dark)] mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-card-foreground mb-1">
                  Annual Potential Value
                </div>
                <div className="text-xs text-muted-foreground mb-2">
                  By wearing your wardrobe consistently, you can extract:
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-display font-semibold gradient-copper-text">
                    ${annualPotentialRange.low.toFixed(0)} - ${annualPotentialRange.high.toFixed(0)}
                  </span>
                  <span className="text-xs text-muted-foreground">this year</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Based on 50-75% active rotation
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </CardContent>
    </Card>
  );
}

