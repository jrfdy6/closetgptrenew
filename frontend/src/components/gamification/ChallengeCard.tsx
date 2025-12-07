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
import { motion } from 'framer-motion';
import { Challenge } from '@/hooks/useGamificationStats';

interface ChallengeCardProps {
  challenge: Challenge;
  onStart?: (challengeId: string) => void;
  variant?: 'active' | 'available' | 'completed';
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
  variant = 'available' 
}: ChallengeCardProps) {
  const isActive = variant === 'active';
  const isCompleted = variant === 'completed';
  const progress = challenge.progress || 0;
  const target = challenge.target || 1;
  const progressPercentage = (progress / target) * 100;

  const IconComponent = IconMap[challenge.icon || 'Target'] || Target;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card className={`relative overflow-hidden bg-card dark:bg-card border ${
        isActive ? 'border-[var(--copper-dark)]' :
        isCompleted ? 'border-border/60 dark:border-border/70 opacity-75' :
        'border-border/60 dark:border-border/70'
      }`}>
        {/* Featured Badge */}
        {challenge.featured && variant === 'available' && (
          <div className="absolute top-2 right-2">
            <Badge className="gradient-copper-gold text-white border-none">
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

        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-secondary dark:bg-muted">
              <IconComponent className="w-5 h-5 text-[var(--copper-dark)]" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-lg text-card-foreground">{challenge.title}</CardTitle>
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
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-muted-foreground">
                  Progress
                </span>
                <span className="text-sm font-bold gradient-copper-text">
                  {progress}/{target}
                </span>
              </div>
              <Progress value={progressPercentage} className="h-1" />
            </div>
          )}

          {/* Expiration (for active challenges) */}
          {isActive && challenge.expires_at && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="w-3 h-3" />
              Expires {new Date(challenge.expires_at).toLocaleDateString()}
            </div>
          )}

          {/* Rewards */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className="bg-secondary dark:bg-muted border border-border/60 dark:border-border/70 text-[var(--copper-dark)]">
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
              className="w-full gradient-copper-gold text-white hover:opacity-90"
              size="sm"
            >
              <Target className="w-4 h-4 mr-2" />
              Start Challenge
            </Button>
          )}

          {variant === 'active' && (
            <Button
              variant="outline"
              className="w-full border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary"
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

