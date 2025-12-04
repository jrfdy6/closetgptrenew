"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { DollarSign, TrendingUp, Info, Sparkles, Target } from 'lucide-react';
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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Total Value Extracted
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.tve) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Total Value Extracted
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Complete onboarding to see your value extraction
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
  const lowestCategory = tve.lowest_progress_category;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
          Total Value Extracted
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  TVE shows how much value you've extracted from your wardrobe investment. 
                  Each wear adds value based on your spending habits!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription>
          Track your wardrobe investment returns
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Total Value Extracted - Big Number */}
          <div>
            <div className="flex items-baseline gap-2 mb-1">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="text-4xl font-bold text-green-600 dark:text-green-400"
              >
                ${totalTVE.toFixed(2)}
              </motion.div>
              <span className="text-sm text-gray-500">extracted</span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {percentRecouped.toFixed(1)}% of your ${totalWardrobeCost.toFixed(0)} wardrobe investment
            </p>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Investment Recouped
              </span>
              <span className="text-sm font-bold text-green-600 dark:text-green-400">
                {percentRecouped.toFixed(1)}%
              </span>
            </div>
            <div className="relative">
              <Progress value={Math.min(percentRecouped, 100)} className="h-3" />
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent"
                animate={{
                  x: ['-100%', '200%']
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear"
                }}
                style={{ mixBlendMode: 'overlay' }}
              />
            </div>
            {percentRecouped >= 100 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2 flex items-center gap-1 text-xs text-green-600 dark:text-green-400"
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
            className="p-4 rounded-lg bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border border-emerald-200 dark:border-emerald-800"
          >
            <div className="flex items-start gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  Annual Potential Value
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  By wearing your wardrobe consistently, you can extract:
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                    ${annualPotentialRange.low.toFixed(0)} - ${annualPotentialRange.high.toFixed(0)}
                  </span>
                  <span className="text-xs text-gray-500">this year</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Based on 30-50% utilization rate
                </div>
              </div>
            </div>
          </motion.div>

          {/* Lowest Progress Category (Action Item) */}
          {lowestCategory && lowestCategory.category && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="pt-4 border-t border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start gap-2">
                <Target className="w-4 h-4 text-blue-500 mt-0.5" />
                <div className="flex-1">
                  <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Next Target Category
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-blue-600 border-blue-300 capitalize">
                      {lowestCategory.category}
                    </Badge>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {lowestCategory.percent.toFixed(0)}% value extracted
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Wear your {lowestCategory.category} to boost your TVE!
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

