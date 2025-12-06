"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, TrendingDown, TrendingUp, Info, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function CPWCard() {
  const { stats, loading, error } = useGamificationStats();

  if (loading) {
    return (
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[#FFB84C]" />
            Cost Per Wear
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

  if (error || !stats?.cpw) {
    return (
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[#FFB84C]" />
            Cost Per Wear
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
            Set your spending ranges in settings to see CPW
          </p>
        </CardContent>
      </Card>
    );
  }

  const { cpw } = stats;
  const currentCPW = cpw.average;
  const trend = cpw.trend;
  const changePercentage = trend?.change_percentage || 0;
  const isDecreasing = changePercentage < 0;

  return (
    <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
          <DollarSign className="w-5 h-5 text-[#FFB84C]" />
          Cost Per Wear
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-[#57534E] dark:text-[#C4BCB4]" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  CPW shows how much value you're getting from your wardrobe. 
                  Lower CPW means you're maximizing your investment!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription className="text-[#57534E] dark:text-[#C4BCB4]">
          Average across your wardrobe
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Current CPW */}
          <div className="flex items-baseline gap-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="text-4xl font-display font-semibold
                bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent"
            >
              ${currentCPW?.toFixed(2) || '0.00'}
            </motion.div>
            <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">per wear</span>
          </div>

          {/* Trend Indicator */}
          {trend && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-2"
            >
              {isDecreasing ? (
                <>
                  <TrendingDown className="w-5 h-5 text-[#FFB84C]" />
                  <span className="text-sm font-medium text-[#FFB84C]">
                    {Math.abs(changePercentage).toFixed(1)}% decrease
                  </span>
                  <Badge className="bg-[#F5F0E8] dark:bg-[#262626] border border-[#FFB84C] text-[#FFB84C]">
                    Great!
                  </Badge>
                </>
              ) : changePercentage > 0 ? (
                <>
                  <TrendingUp className="w-5 h-5 text-[#FF9400]" />
                  <span className="text-sm font-medium text-[#FF9400]">
                    {changePercentage.toFixed(1)}% increase
                  </span>
                </>
              ) : (
                <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                  Stable this month
                </span>
              )}
            </motion.div>
          )}

          {/* Insight */}
          <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] pt-2 border-t border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
            {isDecreasing ? (
              <p className="flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-[#FFB84C]" />
                You're getting more value from your wardrobe!
              </p>
            ) : currentCPW && currentCPW < 10 ? (
              <p>Excellent value! Your wardrobe is working hard for you.</p>
            ) : (
              <p>Keep logging outfits to see your CPW improve!</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

