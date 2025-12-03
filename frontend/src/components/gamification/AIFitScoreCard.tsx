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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI Fit Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
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
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          AI Fit Score
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-gray-400" />
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
        <CardDescription>
          {getScoreLabel(score)}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center space-y-4">
          {/* Circular Progress */}
          <div className="relative w-24 h-24">
            <svg className="w-24 h-24 transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-gray-200 dark:text-gray-700"
              />
              {/* Progress circle */}
              <motion.circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                className={getScoreColor(score)}
                initial={{ strokeDashoffset: 251.2 }}
                animate={{ strokeDashoffset: 251.2 - (251.2 * score) / 100 }}
                transition={{ duration: 1, ease: "easeInOut" }}
                style={{
                  strokeDasharray: 251.2
                }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring" }}
                className={`text-2xl font-bold ${getScoreColor(score)}`}
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
                className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-1"
              >
                <Star className="w-3 h-3 mt-0.5 flex-shrink-0 text-amber-500" />
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
              className="w-full pt-4 border-t border-gray-200 dark:border-gray-700"
            >
              <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Next Milestone
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                {nextMilestone.message}
              </div>
              <div className="mt-2 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-blue-600"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${(nextMilestone.current / nextMilestone.target) * 100}%` 
                  }}
                  transition={{ duration: 0.8, delay: 0.7 }}
                />
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {nextMilestone.current} / {nextMilestone.target}
              </div>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

