"use client";

import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Award, 
  Archive, 
  Gem, 
  Trophy, 
  Medal, 
  Palette, 
  Cloud, 
  Star, 
  Brain 
} from 'lucide-react';
import { motion } from 'framer-motion';

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

// Shimmer effect component (replaces confetti)
function ShimmerEffect() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-[#FFB84C]/20 to-transparent"
        animate={{
          x: ['-100%', '200%']
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear"
        }}
      />
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
  const IconComponent = BadgeIconMap[badgeId] || Award;

  const getRarityBorder = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'border-[#FFB84C]';
      case 'epic':
        return 'border-[#3D2F24]';
      case 'rare':
        return 'border-[#3D2F24]';
      default:
        return 'border-[#3D2F24]';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md overflow-hidden bg-[#2C2119] border border-[#3D2F24]">
        {/* Shimmer Effect */}
        <ShimmerEffect />

        <div className="relative z-10 text-center py-8">
          {/* Badge Unlock Title */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.25,
              ease: "easeOut"
            }}
            className="mb-4"
          >
            <p className="text-sm font-medium text-[#C4BCB4] mb-2">
              Badge Unlocked!
            </p>
          </motion.div>

          {/* Animated Badge Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -5 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 15,
              delay: 0.1
            }}
            className="mb-6"
          >
            <motion.div
              className={`w-24 h-24 mx-auto rounded-2xl bg-[#3D2F24] border-2 ${getRarityBorder(rarity)}
                flex items-center justify-center relative animate-shimmer`}
            >
              <IconComponent className="w-12 h-12 text-[#FFB84C] relative z-10" />
            </motion.div>
          </motion.div>

          {/* Badge Name */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.25 }}
          >
            <h2 className="text-2xl font-display font-semibold mb-2
              bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
              {badgeName}
            </h2>
            <p className="text-sm text-[#C4BCB4] mb-4">
              {badgeDescription}
            </p>
          </motion.div>

          {/* Rarity Badge */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ 
              delay: 0.3,
              type: "spring",
              stiffness: 300,
              damping: 15
            }}
            className="mb-8"
          >
            <Badge className="text-sm px-4 py-1 bg-[#3D2F24] border border-[#3D2F24] text-[#F8F5F1]">
              {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
            </Badge>
          </motion.div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.25 }}
          >
            <Button
              onClick={onClose}
              size="lg"
              className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-white hover:opacity-90"
            >
              Awesome!
            </Button>
          </motion.div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

