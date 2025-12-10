import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, Heart, Star, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EnhancedToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'favorite' | 'achievement';
  title: string;
  description?: string;
  duration?: number;
  onClose: (id: string) => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const toastVariants = {
  initial: { opacity: 0, y: 50, scale: 0.3 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, scale: 0.5, transition: { duration: 0.2 } }
};

const toastTypes = {
  success: {
    icon: CheckCircle,
    // Creme background with rosegold text
    className: 'bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 text-[#C9956F]',
    iconClassName: 'text-[#C9956F]'
  },
  error: {
    icon: AlertCircle,
    // Espresso with lighter rosegold (still warm, not red)
    className: 'bg-[#F5F0E8] dark:bg-[#1A1410] border-[#B8860B]/40 text-[#B8860B]',
    iconClassName: 'text-[#B8860B]'
  },
  warning: {
    icon: AlertCircle,
    // Creme with dark copper (warm warning, not yellow)
    className: 'bg-[#F5F0E8] dark:bg-[#251D18] border-[#B8860B]/40 text-[#B8860B]',
    iconClassName: 'text-[#B8860B]'
  },
  info: {
    icon: Info,
    // Creme background with rosegold text (no blue)
    className: 'bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 text-[#C9956F]',
    iconClassName: 'text-[#C9956F]'
  },
  favorite: {
    icon: Heart,
    // Creme with rosegold (warm, not pink)
    className: 'bg-[#F5F0E8] dark:bg-[#251D18] border-[#D4A574]/40 text-[#D4A574]',
    iconClassName: 'text-[#D4A574]'
  },
  achievement: {
    icon: Sparkles,
    // Creme background with rosegold text (no purple)
    className: 'bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/40 text-[#C9956F]',
    iconClassName: 'text-[#C9956F]'
  }
};

export function EnhancedToast({
  id,
  type,
  title,
  description,
  duration = 5000,
  onClose,
  action
}: EnhancedToastProps) {
  const toastType = toastTypes[type];
  const Icon = toastType.icon;

  React.useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  return (
    <AnimatePresence>
      <motion.div
        variants={toastVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className={cn(
          'relative overflow-hidden rounded-xl shadow-lg border-2',
          'min-w-[320px] max-w-[420px]',
          'backdrop-blur-sm',
          toastType.className
        )}
      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#C9956F]/20 rounded-full -translate-y-16 translate-x-16" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-[#C9956F]/20 rounded-full translate-y-12 -translate-x-12" />
        </div>

        <div className="relative p-4">
          <div className="flex items-start gap-3">
            {/* Icon */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className={cn(
                'flex-shrink-0 w-8 h-8 rounded-full bg-[#C9956F]/10 dark:bg-[#C9956F]/20 flex items-center justify-center',
                toastType.iconClassName
              )}
            >
              <Icon className="w-5 h-5" />
            </motion.div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <motion.h4
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="font-semibold text-sm leading-tight text-[#C9956F] dark:text-[#D4A574]"
              >
                {title}
              </motion.h4>
              
              {description && (
                <motion.p
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mt-1 text-sm opacity-80 leading-relaxed text-[#B8860B] dark:text-[#C9956F]"
                >
                  {description}
                </motion.p>
              )}

              {/* Action Button */}
              {action && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  onClick={action.onClick}
                  className="mt-3 px-3 py-1.5 bg-[#C9956F]/10 hover:bg-[#C9956F]/20 dark:bg-[#C9956F]/20 dark:hover:bg-[#C9956F]/30 rounded-lg text-sm font-medium transition-colors text-[#C9956F] dark:text-[#D4A574]"
                >
                  {action.label}
                </motion.button>
              )}
            </div>

            {/* Close Button */}
            <motion.button
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              onClick={() => onClose(id)}
              className="flex-shrink-0 w-6 h-6 rounded-full bg-[#C9956F]/10 hover:bg-[#C9956F]/20 dark:bg-[#C9956F]/20 dark:hover:bg-[#C9956F]/30 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-[#C9956F] dark:text-[#D4A574]" />
            </motion.button>
          </div>
        </div>

        {/* Progress bar */}
        <motion.div
          initial={{ scaleX: 1 }}
          animate={{ scaleX: 0 }}
          transition={{ duration: duration / 1000, ease: "linear" }}
          className="absolute bottom-0 left-0 right-0 h-1 bg-[#C9956F]/30 dark:bg-[#D4A574]/30 origin-left"
        />
      </motion.div>
    </AnimatePresence>
  );
}

// Toast container
interface ToastContainerProps {
  toasts: Array<EnhancedToastProps>;
  onClose: (id: string) => void;
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {toasts.map((toast) => (
        <EnhancedToast
          key={toast.id}
          {...toast}
          onClose={onClose}
        />
      ))}
    </div>
  );
}

// Predefined toast messages
export const toastMessages = {
  outfitWorn: {
    type: 'success' as const,
    title: '🎉 Outfit logged!',
    description: 'You\'re looking great today!'
  },
  outfitFavorited: {
    type: 'favorite' as const,
    title: '❤️ Added to favorites!',
    description: 'This outfit is now in your favorites'
  },
  itemAdded: {
    type: 'success' as const,
    title: '✅ Item added!',
    description: 'Your new item has been added to your wardrobe'
  },
  achievementUnlocked: {
    type: 'achievement' as const,
    title: '🏆 Achievement unlocked!',
    description: 'You\'ve reached a new style milestone!'
  },
  weatherUpdated: {
    type: 'info' as const,
    title: '🌤️ Weather updated!',
    description: 'Your outfit recommendations are now weather-optimized'
  },
  styleLevelUp: {
    type: 'achievement' as const,
    title: '⭐ Style level up!',
    description: 'You\'ve leveled up your style game!'
  }
}; 