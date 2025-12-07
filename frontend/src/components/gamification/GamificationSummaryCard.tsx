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
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <Sparkles className="w-5 h-5 text-[var(--copper-dark)]" />
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
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <Sparkles className="w-5 h-5 text-[var(--copper-dark)]" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
            Unable to load gamification stats
          </p>
        </CardContent>
      </Card>
    );
  }

  const { xp, level, badges, active_challenges_count } = stats;
  const progressPercentage = level?.progress_percentage || 0;

  return (
    <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
          <Sparkles className="w-5 h-5 text-[#FFB84C]" />
          Your Progress
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Level Indicator - Typography-based */}
          <div className="text-center">
            <h3 className="text-xl font-display font-semibold
              gradient-copper-gold bg-clip-text text-transparent">
              Level {level?.level || 1}
            </h3>
            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] uppercase tracking-wider mt-1">
              {level?.tier || 'Novice'}
            </p>
          </div>

          {/* XP Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                Experience Points
              </span>
              <span className="text-sm font-bold gradient-copper-gold bg-clip-text text-transparent">
                {xp} XP
              </span>
            </div>
            <Progress value={progressPercentage} className="h-1" />
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">
              {level?.xp_for_next_level - xp} XP until Level {(level?.level || 1) + 1}
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-[#F5F0E8] dark:bg-[#262626]">
              <Award className="w-4 h-4 text-[var(--copper-dark)]" />
              <div>
                <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">Badges</div>
                <div className="text-lg font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                  {badges?.length || 0}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg bg-[#F5F0E8] dark:bg-[#262626]">
              <Target className="w-4 h-4 text-[var(--copper-dark)]" />
              <div>
                <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">Active</div>
                <div className="text-lg font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                  {active_challenges_count || 0}
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <Link href="/challenges">
            <Button variant="outline" className="w-full border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#262626]" size="sm">
              <Target className="w-4 h-4 mr-2" />
              View All Challenges
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

