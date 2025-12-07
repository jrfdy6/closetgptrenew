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
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-12 bg-[#F5F0E8] dark:bg-[#262626] rounded animate-pulse" />
            <div className="h-4 bg-[#F5F0E8] dark:bg-[#262626] rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.tve) {
    return (
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
            Total Value Unlocked
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
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
    <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
          <DollarSign className="w-5 h-5 text-[var(--copper-dark)]" />
          Total Value Extracted
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-[#57534E] dark:text-[#C4BCB4]" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  TVE tracks value unlocked from your wardrobe. Each wear adds value when you actively rotate your items weekly!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription className="text-[#57534E] dark:text-[#C4BCB4]">
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
              <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">unlocked</span>
            </div>
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
              {percentRecouped.toFixed(1)}% of your ${totalWardrobeCost.toFixed(0)} wardrobe investment
            </p>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
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
            className="p-4 rounded-lg bg-[#F5F0E8] dark:bg-[#262626] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70"
          >
            <div className="flex items-start gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-[var(--copper-dark)] mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-[#1C1917] dark:text-[#F8F5F1] mb-1">
                  Annual Potential Value
                </div>
                <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] mb-2">
                  By wearing your wardrobe consistently, you can extract:
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-display font-semibold gradient-copper-text">
                    ${annualPotentialRange.low.toFixed(0)} - ${annualPotentialRange.high.toFixed(0)}
                  </span>
                  <span className="text-xs text-[#57534E] dark:text-[#C4BCB4]">this year</span>
                </div>
                <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">
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

