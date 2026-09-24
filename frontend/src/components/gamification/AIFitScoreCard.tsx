"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Brain, Info, Star } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { withSubscriptionGate } from '@/components/providers/withSubscriptionGate';
import { SubscriptionPlan } from '@/types/subscription';

function AIFitScoreCard() {
  const { stats, loading, error, refetch } = useGamificationStats();
  const reduceMotion = useReducedMotion();

  if (loading && !stats) {
    return (
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <Brain className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            AI Fit Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div role="status" aria-label="Loading AI Fit Score" className="space-y-4">
            <div className="h-24 w-24 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto animate-pulse" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.ai_fit_score) {
    return (
      <Card className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-card-foreground">
            <Brain className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            AI Fit Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Your AI Fit Score could not be loaded. Please try again.
          </p>
          <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
        </CardContent>
      </Card>
    );
  }

  const { ai_fit_score } = stats;
  const score = Math.max(0, Math.min(ai_fit_score.total_score || 0, 100));
  const nextMilestone = ai_fit_score.next_milestone;
  
  const getScoreLabel = (score: number) => {
    if (score >= 75) return 'AI Master';
    if (score >= 50) return 'AI Apprentice';
    if (score >= 25) return 'Learning';
    return 'Getting Started';
  };

  return (
    <Card aria-busy={loading} className="bg-card dark:bg-card border border-border/60 dark:border-border/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-card-foreground">
          <Brain className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
          AI Fit Score
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger aria-label="About AI Fit Score" className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                <Info className="w-4 h-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  Reflects the feedback and wardrobe activity you have shared.
                  Rate more outfits to help the AI learn!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          {getScoreLabel(score)}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        {loading && <p role="status" className="mb-3 text-xs text-muted-foreground">Refreshing…</p>}
        <div className="flex flex-col items-center space-y-4">
          {/* Circular Progress */}
          <div role="progressbar" aria-label="AI Fit Score" aria-valuemin={0} aria-valuemax={100} aria-valuenow={score} className="relative w-32 h-32">
            <svg aria-hidden="true" className="w-32 h-32 transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-secondary dark:text-muted"
              />
              {/* Progress circle - Amber gradient */}
              <defs>
                <linearGradient id="copper-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--copper-light)" />
                  <stop offset="100%" stopColor="var(--copper-dark)" />
                </linearGradient>
              </defs>
              <motion.circle
                cx="64"
                cy="64"
                r="56"
                stroke="url(#copper-gradient)"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                initial={reduceMotion ? false : { strokeDashoffset: 351.86 }}
                animate={{ strokeDashoffset: 351.86 - (351.86 * score) / 100 }}
                transition={{ duration: reduceMotion ? 0 : 0.6, ease: "easeOut" }}
                style={{
                  strokeDasharray: 351.86
                }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                initial={reduceMotion ? false : { scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: reduceMotion ? 0 : 0.3, duration: reduceMotion ? 0 : undefined, type: "spring" }}
                className="text-2xl font-display font-semibold text-[#80502F] dark:text-[#E8C8A0]"
              >
                {Math.round(score)}
              </motion.div>
            </div>
          </div>

          {/* Explanations */}
          <div className="w-full space-y-2">
            {ai_fit_score.explanations?.slice(0, 2).map((explanation, index) => (
              <motion.div
                key={index}
                initial={reduceMotion ? false : { opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: reduceMotion ? 0 : 0.4 + index * 0.1, duration: reduceMotion ? 0 : undefined }}
                className="text-xs text-muted-foreground flex items-start gap-1"
              >
                <Star className="w-3 h-3 mt-0.5 flex-shrink-0 text-[#80502F] dark:text-[#E8C8A0]" />
                <span>{explanation}</span>
              </motion.div>
            ))}
          </div>

          {/* Next Milestone */}
          {nextMilestone && (
            <motion.div
              initial={reduceMotion ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: reduceMotion ? 0 : 0.6, duration: reduceMotion ? 0 : undefined }}
              className="w-full pt-4 border-t border-border/60 dark:border-border/70"
            >
              <div className="text-xs font-medium text-card-foreground mb-1">
                Next Milestone
              </div>
              <div className="text-xs text-muted-foreground">
                {nextMilestone.message}
              </div>
              <Progress aria-label="AI Fit Score next milestone" aria-valuetext={`${nextMilestone.current} of ${nextMilestone.target}`} value={nextMilestone.target > 0 ? (nextMilestone.current / nextMilestone.target) * 100 : 0} className="mt-2 h-1" />
              <div className="text-xs text-muted-foreground mt-1">
                {nextMilestone.current} / {nextMilestone.target}
              </div>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default withSubscriptionGate(AIFitScoreCard, SubscriptionPlan.PRO);

