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
  Clock
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
      <Card className={`relative overflow-hidden ${
        isActive ? 'border-purple-300 dark:border-purple-700' :
        isCompleted ? 'border-green-300 dark:border-green-700 opacity-75' :
        ''
      }`}>
        {/* Featured Badge */}
        {challenge.featured && variant === 'available' && (
          <div className="absolute top-2 right-2">
            <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-none">
              <Sparkles className="w-3 h-3 mr-1" />
              Featured
            </Badge>
          </div>
        )}

        {/* Completed Badge */}
        {isCompleted && (
          <div className="absolute top-2 right-2">
            <Badge className="bg-green-500 text-white border-none">
              <CheckCircle className="w-3 h-3 mr-1" />
              Completed
            </Badge>
          </div>
        )}

        <CardHeader>
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${
              isActive ? 'bg-purple-100 dark:bg-purple-900/30' :
              isCompleted ? 'bg-green-100 dark:bg-green-900/30' :
              'bg-gray-100 dark:bg-gray-800'
            }`}>
              <IconComponent className={`w-5 h-5 ${
                isActive ? 'text-purple-600 dark:text-purple-400' :
                isCompleted ? 'text-green-600 dark:text-green-400' :
                'text-gray-600 dark:text-gray-400'
              }`} />
            </div>
            <div className="flex-1">
              <CardTitle className="text-lg">{challenge.title}</CardTitle>
              <CardDescription className="mt-1 text-sm">
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
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Progress
                </span>
                <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
                  {progress}/{target}
                </span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>
          )}

          {/* Expiration (for active challenges) */}
          {isActive && challenge.expires_at && (
            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              <Clock className="w-3 h-3" />
              Expires {new Date(challenge.expires_at).toLocaleDateString()}
            </div>
          )}

          {/* Rewards */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="secondary" className="text-amber-700 dark:text-amber-400">
              <Trophy className="w-3 h-3 mr-1" />
              +{challenge.rewards?.xp || 0} XP
            </Badge>
            {challenge.rewards?.badge && (
              <Badge variant="outline" className="text-purple-700 dark:text-purple-400">
                <Award className="w-3 h-3 mr-1" />
                Badge
              </Badge>
            )}
          </div>

          {/* Action Button */}
          {variant === 'available' && onStart && (
            <Button
              onClick={() => onStart(challenge.challenge_id)}
              className="w-full"
              size="sm"
            >
              <Target className="w-4 h-4 mr-2" />
              Start Challenge
            </Button>
          )}

          {variant === 'active' && (
            <Button
              variant="outline"
              className="w-full"
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

