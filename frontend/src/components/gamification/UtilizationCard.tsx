"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { withSubscriptionGate } from '@/components/providers/withSubscriptionGate';
import { SubscriptionPlan } from '@/types/subscription';

interface UtilizationData {
  utilization_percentage: number;
  items_worn: number;
  total_items: number;
  dormant_items: number;
  period_days: number;
}

function UtilizationCard() {
  const { user } = useAuthContext();
  const [utilization, setUtilization] = useState<UtilizationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const fetchUtilization = async () => {
      try {
        const token = await user.getIdToken();
        
        // Fetch from gamification stats (includes utilization)
        const response = await fetch('/api/gamification/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          // For now, calculate client-side or add endpoint
          // Placeholder data
          setUtilization({
            utilization_percentage: 65,
            items_worn: 45,
            total_items: 70,
            dormant_items: 25,
            period_days: 30
          });
        }
      } catch (error) {
        console.error('Error fetching utilization:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUtilization();
  }, [user]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Wardrobe Utilization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </CardContent>
      </Card>
    );
  }

  if (!utilization) {
    return null;
  }

  const percentage = utilization.utilization_percentage;
  const getUtilizationColor = (pct: number) => {
    if (pct >= 70) return 'text-green-600';
    if (pct >= 50) return 'text-blue-600';
    if (pct >= 30) return 'text-amber-600';
    return 'text-red-600';
  };

  const getUtilizationLabel = (pct: number) => {
    if (pct >= 70) return 'Excellent';
    if (pct >= 50) return 'Good';
    if (pct >= 30) return 'Fair';
    return 'Needs Attention';
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20">
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          Wardrobe Utilization
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  Shows what percentage of your wardrobe you've worn in the last 30 days.
                  Higher is better!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription>
          Last {utilization.period_days} days
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Main Percentage */}
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className={`text-5xl font-bold ${getUtilizationColor(percentage)}`}
            >
              {percentage}%
            </motion.div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {getUtilizationLabel(percentage)} Utilization
            </p>
          </div>

          {/* Progress Bar */}
          <div>
            <Progress value={percentage} className="h-3" />
            <div className="flex justify-between mt-2 text-xs text-gray-600 dark:text-gray-400">
              <span>{utilization.items_worn} worn</span>
              <span>{utilization.total_items} total</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
              <CheckCircle className="w-4 h-4 text-green-500 mx-auto mb-1" />
              <div className="text-lg font-bold text-gray-900 dark:text-white">
                {utilization.items_worn}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Items Worn
              </div>
            </div>

            <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
              <AlertCircle className="w-4 h-4 text-amber-500 mx-auto mb-1" />
              <div className="text-lg font-bold text-gray-900 dark:text-white">
                {utilization.dormant_items}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Unworn
              </div>
            </div>
          </div>

          {/* Insight */}
          <div className="text-xs text-gray-600 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            {percentage >= 70 ? (
              <p className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                Excellent! You're making great use of your wardrobe.
              </p>
            ) : percentage >= 50 ? (
              <p>Good progress! Try the Forgotten Gems challenge to boost utilization.</p>
            ) : (
              <p>Opportunity ahead! Revive dormant items to increase your score.</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default withSubscriptionGate(UtilizationCard, SubscriptionPlan.PRO);

