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
      <Card className="bg-[#2C2119] border border-[#3D2F24]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[#FFB84C]" />
            Cost Per Wear
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-12 bg-[#3D2F24] rounded animate-pulse" />
            <div className="h-4 bg-[#3D2F24] rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.cpw) {
    return (
      <Card className="bg-[#2C2119] border border-[#3D2F24]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#F8F5F1]">
            <DollarSign className="w-5 h-5 text-[#FFB84C]" />
            Cost Per Wear
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[#C4BCB4]">
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
    <Card className="bg-[#2C2119] border border-[#3D2F24] overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#F8F5F1]">
          <DollarSign className="w-5 h-5 text-[#FFB84C]" />
          Cost Per Wear
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-[#8A827A]" />
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
        <CardDescription className="text-[#C4BCB4]">
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
            <span className="text-sm text-[#8A827A]">per wear</span>
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
                  <Badge className="bg-[#3D2F24] border border-[#FFB84C] text-[#FFB84C]">
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
                <span className="text-sm text-[#8A827A]">
                  Stable this month
                </span>
              )}
            </motion.div>
          )}

          {/* Insight */}
          <div className="text-xs text-[#C4BCB4] pt-2 border-t border-[#3D2F24]">
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

