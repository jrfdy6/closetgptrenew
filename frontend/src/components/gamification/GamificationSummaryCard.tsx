"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Sparkles, TrendingUp, Award, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import Link from 'next/link';

export default function GamificationSummaryCard() {
  const { stats, loading, error } = useGamificationStats();

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Unable to load gamification stats
          </p>
        </CardContent>
      </Card>
    );
  }

  const { xp, level, badges, active_challenges_count } = stats;
  const progressPercentage = level?.progress_percentage || 0;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          Your Progress
        </CardTitle>
        <CardDescription>
          Level {level?.level || 1} {level?.tier || 'Novice'}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* XP Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Experience Points
              </span>
              <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
                {xp} XP
              </span>
            </div>
            <div className="relative">
              <Progress value={progressPercentage} className="h-3" />
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
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {level?.xp_for_next_level - xp} XP until Level {(level?.level || 1) + 1}
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
              <Award className="w-4 h-4 text-amber-500" />
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Badges</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {badges?.length || 0}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
              <Target className="w-4 h-4 text-blue-500" />
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Active</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {active_challenges_count || 0}
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <Link href="/challenges">
            <Button variant="outline" className="w-full" size="sm">
              <Target className="w-4 h-4 mr-2" />
              View All Challenges
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

