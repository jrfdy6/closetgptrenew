"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, Info, Star } from 'lucide-react';
import { motion } from 'framer-motion';
import { useGamificationStats } from '@/hooks/useGamificationStats';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function AIFitScoreCard() {
  const { stats, loading, error } = useGamificationStats();

  if (loading) {
    return (
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <Brain className="w-5 h-5 text-[#FFB84C]" />
            AI Fit Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-24 w-24 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto animate-pulse" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats?.ai_fit_score) {
    return (
      <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
            <Brain className="w-5 h-5 text-[#FFB84C]" />
            AI Fit Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
            Rate outfits to build your AI Fit Score
          </p>
        </CardContent>
      </Card>
    );
  }

  const { ai_fit_score } = stats;
  const score = ai_fit_score.total_score || 0;
  const nextMilestone = ai_fit_score.next_milestone;
  
  // Color based on score
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-blue-600';
    if (score >= 25) return 'text-amber-600';
    return 'text-gray-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 75) return 'AI Master';
    if (score >= 50) return 'AI Apprentice';
    if (score >= 25) return 'Learning';
    return 'Getting Started';
  };

  return (
    <Card className="bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
          <Brain className="w-5 h-5 text-[#FFB84C]" />
          AI Fit Score
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-[#57534E] dark:text-[#C4BCB4]" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  Shows how well the AI understands your personal style. 
                  Rate more outfits to help the AI learn!
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription className="text-[#57534E] dark:text-[#C4BCB4]">
          {getScoreLabel(score)}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center space-y-4">
          {/* Circular Progress */}
          <div className="relative w-32 h-32">
            <svg className="w-32 h-32 transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-[#F5F0E8] dark:text-[#262626]"
              />
              {/* Progress circle - Amber gradient */}
              <defs>
                <linearGradient id="amber-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFB84C" />
                  <stop offset="100%" stopColor="#FF9400" />
                </linearGradient>
              </defs>
              <motion.circle
                cx="64"
                cy="64"
                r="56"
                stroke="url(#amber-gradient)"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                initial={{ strokeDashoffset: 351.86 }}
                animate={{ strokeDashoffset: 351.86 - (351.86 * score) / 100 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                style={{
                  strokeDasharray: 351.86
                }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring" }}
                className="text-2xl font-display font-semibold
                  bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent"
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
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="text-xs text-[#57534E] dark:text-[#C4BCB4] flex items-start gap-1"
              >
                <Star className="w-3 h-3 mt-0.5 flex-shrink-0 text-[#FFB84C]" />
                <span>{explanation}</span>
              </motion.div>
            ))}
          </div>

          {/* Next Milestone */}
          {nextMilestone && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="w-full pt-4 border-t border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70"
            >
              <div className="text-xs font-medium text-[#1C1917] dark:text-[#F8F5F1] mb-1">
                Next Milestone
              </div>
              <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
                {nextMilestone.message}
              </div>
              <div className="mt-2 h-1 bg-[#F5F0E8] dark:bg-[#262626] rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400]"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${(nextMilestone.current / nextMilestone.target) * 100}%` 
                  }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                />
              </div>
              <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">
                {nextMilestone.current} / {nextMilestone.target}
              </div>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

