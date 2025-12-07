"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  Award, 
  Trophy, 
  Star, 
  Sparkles,
  Lock,
  Medal,
  Target,
  Palette,
  Cloud,
  Brain,
  Shirt,
  Archive,
  Gem
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useBadges } from '@/hooks/useGamificationStats';

// Map badge IDs to Lucide icons
const BadgeIconMap: Record<string, any> = {
  'starter_closet': Shirt,
  'closet_cataloger': Archive,
  'hidden_gem_hunter': Gem,
  'treasure_hunter': Trophy,
  'sustainable_style_bronze': Award,
  'sustainable_style_silver': Medal,
  'sustainable_style_gold': Trophy,
  'color_master': Palette,
  'monochrome_maven': Palette,
  'weather_warrior': Cloud,
  'transit_stylist': Target,
  'versatile_pro': Star,
  'style_contributor': Star,
  'ai_trainer': Brain,
};

// Rarity border colors (refined for "Sophisticated Gamification")
const RarityBorderColors: Record<string, string> = {
  'common': 'border-border/60 dark:border-border/70',
  'rare': 'border-border/60 dark:border-border/70',
  'epic': 'border-border/60 dark:border-border/70',
  'legendary': 'border-[var(--copper-light)]',
};

interface BadgeDisplayProps {
  compact?: boolean;
}

export default function BadgeDisplay({ compact = false }: BadgeDisplayProps) {
  const { badges, loading, error } = useBadges();

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5" />
            Badges
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return null;
  }

  if (compact) {
    // Compact view for dashboard
    return (
      <div className="flex flex-wrap gap-2">
        {badges.slice(0, 5).map((badge, index) => {
          const IconComponent = BadgeIconMap[badge.id] || Award;
          return (
            <motion.div
              key={badge.id}
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ 
                delay: index * 0.1,
                type: "spring",
                stiffness: 200
              }}
            >
              <Badge className="bg-card dark:bg-card border border-border/60 dark:border-border/70 text-card-foreground hover:border-[var(--copper-mid)]">
                <IconComponent className="w-3 h-3 mr-1 text-[var(--copper-dark)]" />
                {badge.name}
              </Badge>
            </motion.div>
          );
        })}
        {badges.length > 5 && (
          <Badge variant="outline">
            +{badges.length - 5} more
          </Badge>
        )}
      </div>
    );
  }

  // Full view with modal details
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-500" />
          Your Badges ({badges.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {badges.map((badge, index) => {
            const IconComponent = BadgeIconMap[badge.id] || Award;
            
            return (
              <Dialog key={badge.id}>
                <DialogTrigger asChild>
                  <motion.button
                    initial={{ scale: 0, rotate: -5 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ 
                      delay: index * 0.05,
                      type: "spring",
                      stiffness: 200,
                      damping: 15
                    }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`w-16 h-16 bg-card dark:bg-card border ${
                      badge.rarity === 'legendary' 
                        ? 'border-[var(--copper-light)] animate-shimmer' 
                        : 'border-border/60 dark:border-border/70'
                    } rounded-2xl
                      flex flex-col items-center justify-center gap-2 transition-all
                      hover:border-[var(--copper-mid)] cursor-pointer`}
                  >
                    <IconComponent className="w-6 h-6 text-[var(--copper-dark)]" />
                    <span className="text-xs font-medium text-center text-card-foreground">
                      {badge.name}
                    </span>
                  </motion.button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-3">
                      <div className={`p-3 rounded-lg bg-card dark:bg-card border ${RarityBorderColors[badge.rarity]}`}>
                        <IconComponent className="w-6 h-6 text-[var(--copper-dark)]" />
                      </div>
                      {badge.name}
                    </DialogTitle>
                    <DialogDescription className="space-y-2">
                      <p className="text-muted-foreground">{badge.description}</p>
                      <div className="flex items-center gap-2 pt-2">
                        <Badge className="bg-card dark:bg-card border border-border/60 dark:border-border/70 text-card-foreground">
                          {badge.rarity.charAt(0).toUpperCase() + badge.rarity.slice(1)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {badge.unlock_condition}
                        </span>
                      </div>
                    </DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
            );
          })}
          
          {/* Locked badge placeholders */}
          {badges.length < 4 && (
            Array.from({ length: Math.min(4 - badges.length, 3) }).map((_, i) => (
              <div
                key={`locked-${i}`}
                className="p-4 rounded-lg bg-gray-100 dark:bg-gray-800 
                  border-2 border-dashed border-gray-300 dark:border-gray-600
                  flex flex-col items-center gap-2 opacity-50"
              >
                <Lock className="w-8 h-8 text-gray-400" />
                <span className="text-xs font-medium text-gray-500">
                  Locked
                </span>
              </div>
            ))
          )}
        </div>

        {badges.length === 0 && (
          <div className="text-center p-8">
            <Lock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Complete challenges to earn your first badge!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

