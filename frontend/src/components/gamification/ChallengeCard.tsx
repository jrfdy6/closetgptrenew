"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Target, 
  Sparkles, 
  Trophy, 
  Calendar,
  CheckCircle,
  Clock,
  Award
} from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { Challenge } from '@/hooks/useGamificationStats';

interface ChallengeCardProps {
  challenge: Challenge;
  onStart?: (challengeId: string) => void;
  variant?: 'active' | 'available' | 'completed';
  starting?: boolean;
  startDisabled?: boolean;
}

// Map icon names to Lucide components
const IconMap: Record<string, any> = {
  'Sparkles': Sparkles,
  'Target': Target,
  'Trophy': Trophy,
  'Calendar': Calendar,
  'Upload': Target,
  'Palette': Sparkles,
};

export default function ChallengeCard({ 
  challenge, 
  onStart,
  variant = 'available',
  starting = false,
  startDisabled = false,
}: ChallengeCardProps) {
  const reduceMotion = useReducedMotion();
  const isActive = variant === 'active';
  const isCompleted = variant === 'completed';
  
  // Handle annual challenge progress structure (object) vs regular (number)
  let progress: number;
  let target: number;
  let progressDisplay: string;
  let percentage: number | undefined;
  
  if (challenge.challenge_id === 'annual_wardrobe_master') {
    // Annual challenge: progress is an object
    const progressData = typeof challenge.progress === 'object' && challenge.progress !== null
      ? challenge.progress as { total_outfits?: number; weeks_completed?: number; current_week_outfits?: number }
      : { total_outfits: 0, weeks_completed: 0 };
    progress = progressData.total_outfits || 0;
    target = 260; // 52 weeks * 5 outfits
    const weeks = progressData.weeks_completed || 0;
    progressDisplay = `${progress}/260 outfits, ${weeks}/52 weeks`;
    // Annual completion requires qualifying weeks, not just an outfit total.
    percentage = (weeks / 52) * 100;
  } else {
    // Regular challenge: progress is a number
    progress = typeof challenge.progress === 'number' ? challenge.progress : 0;
    target = typeof challenge.target === 'number' ? challenge.target : 1;
    progressDisplay = `${progress}/${target}`;
    if (challenge.challenge_id === '30_wears_challenge') {
      progressDisplay += ' items at 30 wears';
    }
  }
  
  const progressPercentage = Math.max(0, Math.min(percentage ?? (target > 0 ? (progress / target) * 100 : 0), 100));
  const expiresAt = challenge.expires_at ? new Date(challenge.expires_at) : null;
  const completedAt = challenge.completed_at ? new Date(challenge.completed_at) : null;

  const IconComponent = IconMap[challenge.icon || 'Target'] || Target;

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.3 }}
      whileHover={reduceMotion ? undefined : { scale: 1.02 }}
    >
      <Card className={`relative overflow-hidden bg-card dark:bg-card border ${
        isActive ? 'border-[var(--copper-dark)]' :
        isCompleted ? 'border-border/60 dark:border-border/70' :
        'border-border/60 dark:border-border/70'
      }`}>
        {/* Featured Badge */}
        {challenge.featured && variant === 'available' && (
          <div className="absolute top-2 right-2">
            <Badge className="bg-secondary text-card-foreground border border-border">
              <Sparkles className="w-3 h-3 mr-1" />
              Featured
            </Badge>
          </div>
        )}

        {/* Completed Badge */}
        {isCompleted && (
          <div className="absolute top-2 right-2">
            <Badge className="bg-secondary dark:bg-muted border border-border/60 dark:border-border/70 text-muted-foreground">
              <CheckCircle className="w-3 h-3 mr-1" />
              Completed
            </Badge>
          </div>
        )}

        <CardHeader className={(challenge.featured && variant === 'available') || isCompleted ? 'pt-10' : undefined}>
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-secondary dark:bg-muted">
              <IconComponent className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
            </div>
            <div className="min-w-0 flex-1">
              <CardTitle className="text-lg text-card-foreground break-words">{challenge.title}</CardTitle>
              <CardDescription className="mt-1 text-sm text-muted-foreground">
                {challenge.description}
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Progress (for active challenges) */}
          {isActive && (
            <div>
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <span className="text-sm font-medium text-muted-foreground">
                  Progress
                </span>
                <span className="text-sm font-bold text-[#80502F] dark:text-[#E8C8A0]">
                  {progressDisplay}
                </span>
              </div>
              <Progress aria-label={`${challenge.title} progress`} aria-valuetext={progressDisplay} value={progressPercentage} className="h-1" />
            </div>
          )}

          {/* Expiration (for active challenges) */}
          {isActive && expiresAt && !Number.isNaN(expiresAt.getTime()) && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="w-3 h-3" />
              Expires {expiresAt.toLocaleDateString()}
            </div>
          )}

          {isCompleted && completedAt && !Number.isNaN(completedAt.getTime()) && (
            <p className="text-xs text-muted-foreground">Completed {completedAt.toLocaleDateString()}</p>
          )}

          {/* Rewards */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className="bg-secondary dark:bg-muted border border-border/60 dark:border-border/70 text-[#80502F] dark:text-[#E8C8A0]">
              <Trophy className="w-3 h-3 mr-1" />
              +{challenge.rewards?.xp || 0} XP
            </Badge>
            {challenge.rewards?.badge && (
              <Badge className="bg-secondary dark:bg-muted border border-border/60 dark:border-border/70 text-card-foreground">
                <Award className="w-3 h-3 mr-1" />
                Badge
              </Badge>
            )}
          </div>

          {/* Action Button */}
          {variant === 'available' && onStart && (
            <Button
              onClick={() => onStart(challenge.challenge_id)}
              disabled={startDisabled}
              aria-busy={starting}
              className="min-h-11 w-full bg-none bg-[#80502F] text-white hover:bg-[#70462C] dark:bg-[#E8C8A0] dark:text-[#1A1410] dark:hover:bg-[#D4A574]"
              size="sm"
            >
              <Target className="w-4 h-4 mr-2" />
              {starting ? 'Starting…' : 'Start Challenge'}
            </Button>
          )}

          {variant === 'active' && (
            <Button
              variant="outline"
              className="min-h-11 w-full border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary"
              size="sm"
              disabled
            >
              In Progress...
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
