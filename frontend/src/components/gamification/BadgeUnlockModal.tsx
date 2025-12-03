"use client";

import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Award, Trophy, Medal, Star, Sparkles, 
  Gem, Archive, Brain, Palette, Cloud, Target 
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface BadgeUnlockModalProps {
  isOpen: boolean;
  onClose: () => void;
  badgeId: string;
  badgeName: string;
  badgeDescription: string;
  rarity: string;
}

// Map badge IDs to icons
const BadgeIconMap: Record<string, any> = {
  'starter_closet': Archive,
  'closet_cataloger': Archive,
  'hidden_gem_hunter': Gem,
  'treasure_hunter': Trophy,
  'sustainable_style_bronze': Award,
  'sustainable_style_silver': Medal,
  'sustainable_style_gold': Trophy,
  'color_master': Palette,
  'weather_warrior': Cloud,
  'style_contributor': Star,
  'ai_trainer': Brain,
};

// Confetti component
function Confetti() {
  const confettiPieces = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.3,
    duration: 1.5 + Math.random() * 1.5,
    rotation: Math.random() * 360,
    scale: 0.5 + Math.random() * 0.5,
    color: ['#FFD700', '#FFA500', '#FF6B6B', '#4ECDC4', '#A855F7'][Math.floor(Math.random() * 5)]
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {confettiPieces.map((piece) => (
        <motion.div
          key={piece.id}
          className="absolute rounded-full"
          style={{
            left: `${piece.x}%`,
            width: `${piece.scale * 12}px`,
            height: `${piece.scale * 12}px`,
            backgroundColor: piece.color
          }}
          initial={{ y: -20, rotate: 0, opacity: 1, scale: piece.scale }}
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

export default function BadgeUnlockModal({
  isOpen,
  onClose,
  badgeId,
  badgeName,
  badgeDescription,
  rarity
}: BadgeUnlockModalProps) {
  const [showConfetti, setShowConfetti] = useState(false);
  const IconComponent = BadgeIconMap[badgeId] || Award;

  useEffect(() => {
    if (isOpen) {
      setShowConfetti(true);
      const timer = setTimeout(() => setShowConfetti(false), 2500);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'from-amber-400 to-yellow-500';
      case 'epic':
        return 'from-purple-400 to-pink-500';
      case 'rare':
        return 'from-blue-400 to-cyan-500';
      default:
        return 'from-gray-400 to-gray-500';
    }
  };

  const getRarityBg = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950 dark:to-yellow-950';
      case 'epic':
        return 'bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950';
      case 'rare':
        return 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950';
      default:
        return 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-md overflow-hidden border-none ${getRarityBg(rarity)}`}>
        {/* Confetti */}
        {showConfetti && <Confetti />}

        <div className="relative z-10 text-center py-8">
          {/* Badge Unlock Title */}
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 20
            }}
            className="mb-4"
          >
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Badge Unlocked!
            </p>
          </motion.div>

          {/* Animated Badge Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -360 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 15,
              delay: 0.2
            }}
            className="mb-6"
          >
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className={`w-32 h-32 mx-auto rounded-full bg-gradient-to-br ${getRarityColor(rarity)} 
                flex items-center justify-center shadow-2xl relative`}
            >
              {/* Glow effect */}
              <motion.div
                className="absolute inset-0 rounded-full"
                animate={{
                  boxShadow: [
                    '0 0 20px rgba(168, 85, 247, 0.5)',
                    '0 0 40px rgba(168, 85, 247, 0.8)',
                    '0 0 20px rgba(168, 85, 247, 0.5)'
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <IconComponent className="w-16 h-16 text-white relative z-10" />
            </motion.div>
          </motion.div>

          {/* Badge Name */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className={`text-3xl font-bold mb-2 bg-gradient-to-r ${getRarityColor(rarity)} bg-clip-text text-transparent`}>
              {badgeName}
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {badgeDescription}
            </p>
          </motion.div>

          {/* Rarity Badge */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ 
              delay: 0.6,
              type: "spring",
              stiffness: 300
            }}
            className="mb-8"
          >
            <Badge className={`text-sm px-4 py-1 bg-gradient-to-r ${getRarityColor(rarity)} text-white border-none`}>
              {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
            </Badge>
          </motion.div>

          {/* Sparkle Effects */}
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute"
                style={{
                  left: `${20 + (i * 10)}%`,
                  top: `${30 + ((i % 3) * 20)}%`,
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{
                  scale: [0, 1, 0],
                  opacity: [0, 1, 0],
                  rotate: [0, 180, 360]
                }}
                transition={{
                  duration: 1.5,
                  delay: 0.5 + (i * 0.1),
                  repeat: 2
                }}
              >
                <Sparkles className="w-4 h-4 text-amber-500" />
              </motion.div>
            ))}
          </div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <Button
              onClick={onClose}
              size="lg"
              className={`bg-gradient-to-r ${getRarityColor(rarity)} text-white`}
            >
              Awesome!
            </Button>
          </motion.div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

