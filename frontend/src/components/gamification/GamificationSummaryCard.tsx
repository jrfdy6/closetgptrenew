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
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
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
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <Sparkles className="w-5 h-5 text-[var(--copper-dark)]" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Unable to load gamification stats
          </p>
        </CardContent>
      </Card>
    );
  }

  const { xp, level, badges, active_challenges_count } = stats;
  const progressPercentage = level?.progress_percentage || 0;

  return (
    <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <Sparkles className="w-5 h-5 text-primary" />
          Your Progress
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Level Indicator - Typography-based */}
          <div className="text-center">
            <h3 className="text-xl font-display font-semibold gradient-copper-text">
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
              <span className="text-sm font-bold gradient-copper-text">
                {xp} XP
              </span>
            </div>
            <Progress value={progressPercentage} className="h-1" />
            <p className="text-xs text-muted-foreground mt-1">
              {level?.xp_for_next_level - xp} XP until Level {(level?.level || 1) + 1}
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-secondary dark:bg-muted">
              <Award className="w-4 h-4 text-[var(--copper-dark)]" />
              <div>
                <div className="text-xs text-muted-foreground">Badges</div>
                <div className="text-lg font-bold text-card-foreground">
                  {badges?.length || 0}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg bg-secondary dark:bg-muted">
              <Target className="w-4 h-4 text-[var(--copper-dark)]" />
              <div>
                <div className="text-xs text-muted-foreground">Active</div>
                <div className="text-lg font-bold text-card-foreground">
                  {active_challenges_count || 0}
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <Link href="/challenges">
            <Button variant="outline" className="w-full border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-all" size="sm">
              <Target className="w-4 h-4 mr-2" />
              View All Challenges
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

