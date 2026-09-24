"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { DollarSign, TrendingUp, Info, Sparkles } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { withSubscriptionGate } from '@/components/providers/withSubscriptionGate';
import { SubscriptionPlan } from '@/types/subscription';

function TVECard() {
  const { stats, loading, error, refetch } = useGamificationStats();
  const reduceMotion = useReducedMotion();

  if (loading && !stats) {
    return (
      <Card aria-busy={loading} className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <DollarSign className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div role="status" aria-label="Loading wardrobe value" className="space-y-4">
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
            <DollarSign className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Your wardrobe value could not be loaded. Please try again.
          </p>
          <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
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
    <Card aria-busy={loading} className="bg-card dark:bg-card border border-border/60 dark:border-border/70 overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <DollarSign className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
          Total Value Extracted
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger aria-label="About wardrobe value" className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
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
          Track your estimated wardrobe value
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        {loading && <p role="status" className="mb-3 text-xs text-muted-foreground">Refreshing…</p>}
        <div className="space-y-6">
          {/* Total Value Unlocked - Big Number */}
          <div>
            <div className="flex flex-wrap items-baseline gap-2 mb-1">
              <motion.div
                initial={reduceMotion ? false : { scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, duration: reduceMotion ? 0 : undefined }}
                className="text-4xl font-display font-semibold text-[#80502F] dark:text-[#E8C8A0]"
              >
                ${totalTVE.toFixed(2)}
              </motion.div>
              <span className="text-sm text-muted-foreground">unlocked</span>
            </div>
            <p className="text-xs text-muted-foreground">
              {percentRecouped.toFixed(1)}% of your ${totalWardrobeCost.toFixed(0)} estimated wardrobe investment
            </p>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <span className="text-sm font-medium text-muted-foreground">
                Estimated Investment Recouped
              </span>
              <span className="text-sm font-bold text-[#80502F] dark:text-[#E8C8A0]">
                {percentRecouped.toFixed(1)}%
              </span>
            </div>
            <Progress aria-label="Estimated wardrobe investment recouped" aria-valuetext={`${percentRecouped.toFixed(1)} percent`} value={Math.min(percentRecouped, 100)} className="h-1" />
            {percentRecouped >= 100 && (
              <motion.div
                initial={reduceMotion ? false : { opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2 flex items-center gap-1 text-xs text-[#80502F] dark:text-[#E8C8A0]"
              >
                <Sparkles className="w-3 h-3" />
                <span className="font-medium">Estimated investment recouped! Now generating bonus value!</span>
              </motion.div>
            )}
          </div>

          {/* Annual Potential Range */}
          <motion.div
            initial={reduceMotion ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: reduceMotion ? 0 : 0.2, duration: reduceMotion ? 0 : undefined }}
            className="p-4 rounded-lg bg-secondary dark:bg-muted border border-border/60 dark:border-border/70"
          >
            <div className="flex items-start gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-[#80502F] dark:text-[#E8C8A0] mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-card-foreground mb-1">
                  Annual Potential Value
                </div>
                <div className="text-xs text-muted-foreground mb-2">
                  By wearing your wardrobe consistently, you can extract:
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-lg font-display font-semibold text-[#80502F] dark:text-[#E8C8A0]">
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

export default withSubscriptionGate(TVECard, SubscriptionPlan.PRO);

