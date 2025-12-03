"use client";

import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trophy, Sparkles, TrendingUp, Star } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface LevelUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  newLevel: number;
  tier: string;
  xp: number;
}

// Confetti component
function Confetti() {
  const confettiPieces = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.5,
    duration: 2 + Math.random() * 2,
    rotation: Math.random() * 360,
    color: ['#FFB84C', '#FF9400', '#A855F7', '#EC4899', '#10B981'][Math.floor(Math.random() * 5)]
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {confettiPieces.map((piece) => (
        <motion.div
          key={piece.id}
          className="absolute w-3 h-3 rounded-sm"
          style={{
            left: `${piece.x}%`,
            backgroundColor: piece.color
          }}
          initial={{ y: -20, rotate: 0, opacity: 1 }}
          animate={{
            y: window.innerHeight + 20,
            rotate: piece.rotation,
            opacity: 0
          }}
          transition={{
            duration: piece.duration,
            delay: piece.delay,
            ease: "easeIn"
          }}
        />
      ))}
    </div>
  );
}

export default function LevelUpModal({
  isOpen,
  onClose,
  newLevel,
  tier,
  xp
}: LevelUpModalProps) {
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShowConfetti(true);
      // Stop confetti after 3 seconds
      const timer = setTimeout(() => setShowConfetti(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'novice':
        return 'from-gray-400 to-gray-600';
      case 'stylist':
        return 'from-blue-400 to-blue-600';
      case 'curator':
        return 'from-purple-400 to-purple-600';
      case 'connoisseur':
        return 'from-amber-400 to-amber-600';
      default:
        return 'from-purple-400 to-pink-600';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'novice':
        return Star;
      case 'stylist':
        return Sparkles;
      case 'curator':
        return TrendingUp;
      case 'connoisseur':
        return Trophy;
      default:
        return Star;
    }
  };

  const TierIcon = getTierIcon(tier);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md overflow-hidden border-none bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
        {/* Confetti */}
        {showConfetti && <Confetti />}

        <div className="relative z-10 text-center py-8">
          {/* Animated Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 15,
              delay: 0.2
            }}
            className="mb-6"
          >
            <div className={`w-24 h-24 mx-auto rounded-full bg-gradient-to-br ${getTierColor(tier)} 
              flex items-center justify-center shadow-2xl`}
            >
              <TierIcon className="w-12 h-12 text-white" />
            </div>
          </motion.div>

          {/* Level Up Text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Level Up!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-4">
              You've reached Level {newLevel}
            </p>
          </motion.div>

          {/* Tier Badge */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ 
              delay: 0.6,
              type: "spring",
              stiffness: 300
            }}
            className="mb-6"
          >
            <Badge className={`text-lg px-6 py-2 bg-gradient-to-r ${getTierColor(tier)} text-white border-none`}>
              {tier}
            </Badge>
          </motion.div>

          {/* XP Display */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            className="mb-8"
          >
            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/50 dark:bg-black/30 backdrop-blur">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {xp} XP
              </span>
            </div>
          </motion.div>

          {/* Unlocked Features (if any) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="mb-6 space-y-2"
          >
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {newLevel === 5 && "Unlocked: Advanced challenge types"}
              {newLevel === 10 && "Unlocked: Curator insights & analytics"}
              {newLevel === 15 && "Unlocked: Exclusive connoisseur features"}
              {newLevel < 5 && "Keep going! More features unlock as you level up."}
            </p>
          </motion.div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
          >
            <Button
              onClick={onClose}
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700"
            >
              Continue
            </Button>
          </motion.div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

