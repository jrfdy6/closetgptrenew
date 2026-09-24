"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
import { motion, useReducedMotion } from 'framer-motion';
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
  const { badges, loading, error, refetch } = useBadges();
  const reduceMotion = useReducedMotion();

  if (loading && badges.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5" />
            Badges
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div role="status" aria-label="Loading badges" className="grid grid-cols-3 gap-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Badges</CardTitle></CardHeader>
        <CardContent>
          <p role="status" className="text-sm text-muted-foreground">Your badges could not be loaded.</p>
          <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
        </CardContent>
      </Card>
    );
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
              initial={reduceMotion ? false : { scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ 
                delay: reduceMotion ? 0 : index * 0.1,
                duration: reduceMotion ? 0 : undefined,
                type: "spring",
                stiffness: 200
              }}
            >
              <Badge className="bg-card dark:bg-card border border-border/60 dark:border-border/70 text-card-foreground hover:border-[var(--copper-mid)]">
                <IconComponent className="w-3 h-3 mr-1 text-[#80502F] dark:text-[#E8C8A0]" />
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
    <Card aria-busy={loading}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Award className="w-5 h-5 text-[#80502F] dark:text-[#E8C8A0]" />
          Your Badges ({badges.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <p role="status" className="mb-3 text-xs text-muted-foreground">Refreshing badges…</p>}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {badges.map((badge, index) => {
            const IconComponent = BadgeIconMap[badge.id] || Award;
            
            return (
              <Dialog key={badge.id}>
                <DialogTrigger asChild>
                  <motion.button
                    type="button"
                    aria-label={`View ${badge.name} badge`}
                    initial={reduceMotion ? false : { scale: 0, rotate: -5 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ 
                      delay: reduceMotion ? 0 : index * 0.05,
                      duration: reduceMotion ? 0 : undefined,
                      type: "spring",
                      stiffness: 200,
                      damping: 15
                    }}
                    whileHover={reduceMotion ? undefined : { scale: 1.03 }}
                    whileTap={reduceMotion ? undefined : { scale: 0.98 }}
                    className={`w-full min-h-28 p-3 bg-card dark:bg-card border ${
                      badge.rarity === 'legendary' 
                        ? 'border-[var(--copper-light)] motion-safe:animate-shimmer'
                        : 'border-border/60 dark:border-border/70'
                    } rounded-2xl
                      flex flex-col items-center justify-center gap-2 transition-all
                      hover:border-[var(--copper-mid)] cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`}
                  >
                    <IconComponent className="w-6 h-6 text-[#80502F] dark:text-[#E8C8A0]" />
                    <span className="text-xs font-medium text-center text-card-foreground break-words w-full">
                      {badge.name}
                    </span>
                  </motion.button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-3">
                      <div className={`p-3 rounded-lg bg-card dark:bg-card border ${RarityBorderColors[badge.rarity]}`}>
                        <IconComponent className="w-6 h-6 text-[#80502F] dark:text-[#E8C8A0]" />
                      </div>
                      {badge.name}
                    </DialogTitle>
                    <DialogDescription asChild>
                      <div className="space-y-2">
                      <p className="text-muted-foreground">{badge.description}</p>
                      <div className="flex items-center gap-2 pt-2">
                        <Badge className="bg-card dark:bg-card border border-border/60 dark:border-border/70 text-card-foreground">
                          {badge.rarity.charAt(0).toUpperCase() + badge.rarity.slice(1)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {badge.unlock_condition}
                        </span>
                      </div>
                      </div>
                    </DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
            );
          })}
        </div>

        {badges.length === 0 && (
          <div className="text-center p-8">
            <Lock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Add clothes, log outfits, and complete challenges to earn badges.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

