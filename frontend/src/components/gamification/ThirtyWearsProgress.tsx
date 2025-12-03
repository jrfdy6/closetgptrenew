"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Target, Award, Medal } from 'lucide-react';
import { motion } from 'framer-motion';

interface ThirtyWearsProgressProps {
  wearCount: number;
  itemName?: string;
  targetWears?: number;
}

export default function ThirtyWearsProgress({ 
  wearCount, 
  itemName,
  targetWears = 30 
}: ThirtyWearsProgressProps) {
  const progress = (wearCount / targetWears) * 100;
  const isComplete = wearCount >= targetWears;
  const nextMilestone = wearCount < 10 ? 10 : wearCount < 20 ? 20 : 30;

  // Determine badge tier
  const getBadgeTier = (count: number) => {
    if (count >= 100) return { tier: 'Gold', icon: Trophy, color: 'text-yellow-500' };
    if (count >= 60) return { tier: 'Silver', icon: Medal, color: 'text-gray-400' };
    if (count >= 30) return { tier: 'Bronze', icon: Award, color: 'text-amber-600' };
    return { tier: 'None', icon: Target, color: 'text-gray-400' };
  };

  const badgeInfo = getBadgeTier(wearCount);
  const IconComponent = badgeInfo.icon;

  return (
    <Card className="overflow-hidden">
      <CardHeader className={`${
        isComplete 
          ? 'bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20'
          : 'bg-gray-50 dark:bg-gray-800'
      }`}>
        <CardTitle className="flex items-center gap-2 text-base">
          <IconComponent className={`w-5 h-5 ${badgeInfo.color}`} />
          30 Wears Challenge
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Progress
            </span>
            <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
              {wearCount}/{targetWears} wears
            </span>
          </div>
          <div className="relative">
            <Progress value={Math.min(progress, 100)} className="h-3" />
            
            {/* Milestone markers */}
            <div className="absolute top-0 left-1/3 w-px h-3 bg-gray-300 dark:bg-gray-600" />
            <div className="absolute top-0 left-2/3 w-px h-3 bg-gray-300 dark:bg-gray-600" />
          </div>
          
          {/* Milestone labels */}
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span className={wearCount >= 10 ? 'text-green-600 font-medium' : ''}>10</span>
            <span className={wearCount >= 20 ? 'text-green-600 font-medium' : ''}>20</span>
            <span className={wearCount >= 30 ? 'text-green-600 font-medium' : ''}>30</span>
          </div>
        </div>

        {/* Status Message */}
        <div className="text-center">
          {isComplete ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-center gap-2 text-amber-600 dark:text-amber-400">
                <Trophy className="w-5 h-5" />
                <span className="font-bold">Challenge Complete!</span>
              </div>
              <Badge className="bg-amber-500 text-white">
                Sustainable Style - {badgeInfo.tier}
              </Badge>
              
              {wearCount < 60 && (
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                  Keep going! Wear this item {60 - wearCount} more times for the Silver badge.
                </p>
              )}
              {wearCount >= 60 && wearCount < 100 && (
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                  Amazing! {100 - wearCount} more wears for the Gold badge!
                </p>
              )}
              {wearCount >= 100 && (
                <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                  Legendary sustainability! This item is a true wardrobe staple.
                </p>
              )}
            </motion.div>
          ) : (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {nextMilestone - wearCount} more wears until next milestone!
              {wearCount >= 20 && (
                <p className="text-xs mt-1 text-purple-600 dark:text-purple-400">
                  Almost there! You're {targetWears - wearCount} wears from the Bronze badge.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Upcoming Rewards */}
        {!isComplete && (
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
              Upcoming Rewards
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                <Award className="w-3 h-3 text-amber-600" />
                <span>30 wears: Bronze Badge + 100 XP</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500">
                <Medal className="w-3 h-3 text-gray-400" />
                <span>60 wears: Silver Badge + 150 XP</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500">
                <Trophy className="w-3 h-3 text-gray-400" />
                <span>100 wears: Gold Badge + 250 XP</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

