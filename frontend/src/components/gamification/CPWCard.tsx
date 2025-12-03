"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, TrendingDown, TrendingUp, Info } from 'lucide-react';
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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Cost Per Wear
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

  if (error || !stats?.cpw) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Cost Per Wear
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
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
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
          Cost Per Wear
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-gray-400" />
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
        <CardDescription>
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
              className="text-4xl font-bold text-gray-900 dark:text-white"
            >
              ${currentCPW?.toFixed(2) || '0.00'}
            </motion.div>
            <span className="text-sm text-gray-500">per wear</span>
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
                  <TrendingDown className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-green-600">
                    {Math.abs(changePercentage).toFixed(1)}% decrease
                  </span>
                  <Badge variant="outline" className="text-green-700 border-green-300">
                    Great!
                  </Badge>
                </>
              ) : changePercentage > 0 ? (
                <>
                  <TrendingUp className="w-5 h-5 text-orange-600" />
                  <span className="text-sm font-medium text-orange-600">
                    {changePercentage.toFixed(1)}% increase
                  </span>
                </>
              ) : (
                <span className="text-sm text-gray-500">
                  Stable this month
                </span>
              )}
            </motion.div>
          )}

          {/* Insight */}
          <div className="text-xs text-gray-600 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            {isDecreasing ? (
              <p className="flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-500" />
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

