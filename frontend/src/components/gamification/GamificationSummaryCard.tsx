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
  const { stats, loading, error, refetch } = useGamificationStats();

  if (loading && !stats) {
    return (
      <Card aria-busy={loading} className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <Sparkles className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div role="status" aria-label="Loading your progress" className="space-y-4">
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
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <Sparkles className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Your progress could not be loaded.
          </p>
          <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
        </CardContent>
      </Card>
    );
  }

  const { xp, level, badges, active_challenges_count } = stats;
  const progressPercentage = Math.max(0, Math.min(level?.progress_percentage || 0, 100));
  const xpRemaining = Math.max(0, (level?.xp_for_next_level ?? xp) - xp);

  return (
    <Card aria-busy={loading} className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <Sparkles className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
          Your Progress
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        {loading && <p role="status" className="mb-3 text-xs text-muted-foreground">Refreshing…</p>}
        <div className="space-y-6">
          {/* Level Indicator - Typography-based */}
          <div className="text-center">
            <h3 className="text-xl font-display font-semibold text-[#80502F] dark:text-[#E8C8A0]">
              Level {level?.level || 1}
            </h3>
            <p className="text-sm text-muted-foreground uppercase tracking-wider mt-1">
              {level?.tier || 'Novice'}
            </p>
          </div>

          {/* XP Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">
                Experience Points
              </span>
              <span className="text-sm font-bold text-[#80502F] dark:text-[#E8C8A0]">
                {xp} XP
              </span>
            </div>
            <Progress aria-label="Experience toward the next level" aria-valuetext={`${xp} XP; ${xpRemaining} XP until Level ${(level?.level || 1) + 1}`} value={progressPercentage} className="h-1" />
            <p className="text-xs text-muted-foreground mt-1">
              {xpRemaining} XP until Level {(level?.level || 1) + 1}
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-secondary dark:bg-muted">
              <Award className="w-4 h-4 text-[#80502F] dark:text-[#E8C8A0]" />
              <div>
                <div className="text-xs text-muted-foreground">Badges</div>
                <div className="text-lg font-bold text-card-foreground">
                  {badges?.length || 0}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg bg-secondary dark:bg-muted">
              <Target className="w-4 h-4 text-[#80502F] dark:text-[#E8C8A0]" />
              <div>
                <div className="text-xs text-muted-foreground">Active</div>
                <div className="text-lg font-bold text-card-foreground">
                  {active_challenges_count || 0}
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <Button asChild variant="outline" className="min-h-11 w-full border-2 border-[#80502F] text-[#80502F] hover:bg-[#80502F] hover:text-white dark:border-[#E8C8A0] dark:text-[#E8C8A0] dark:hover:bg-[#E8C8A0] dark:hover:text-[#1A1410] transition-all" size="sm">
            <Link href="/challenges">
              <Target className="w-4 h-4 mr-2" />
              View All Challenges
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

