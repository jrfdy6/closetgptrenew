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
    className: 'bg-gradient-to-r from-green-500 to-green-600 text-white border-green-400',
    iconClassName: 'text-green-100'
  },
  error: {
    icon: AlertCircle,
    className: 'bg-gradient-to-r from-red-500 to-red-600 text-white border-red-400',
    iconClassName: 'text-red-100'
  },
  warning: {
    icon: AlertCircle,
    className: 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-yellow-400',
    iconClassName: 'text-yellow-100'
  },
  info: {
    icon: Info,
    className: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white border-blue-400',
    iconClassName: 'text-blue-100'
  },
  favorite: {
    icon: Heart,
    className: 'bg-gradient-to-r from-pink-500 to-rose-600 text-white border-pink-400',
    iconClassName: 'text-pink-100'
  },
  achievement: {
    icon: Sparkles,
    className: 'bg-gradient-to-r from-purple-500 to-violet-600 text-white border-violet-400',
    iconClassName: 'text-violet-100'
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
          toastType.className
        )}
      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full -translate-y-16 translate-x-16" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/20 rounded-full translate-y-12 -translate-x-12" />
        </div>

        <div className="relative p-4">
          <div className="flex items-start gap-3">
            {/* Icon */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className={cn(
                'flex-shrink-0 w-8 h-8 rounded-full bg-white/20 flex items-center justify-center',
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
                className="font-semibold text-sm leading-tight"
              >
                {title}
              </motion.h4>
              
              {description && (
                <motion.p
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mt-1 text-sm opacity-90 leading-relaxed"
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
                  className="mt-3 px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
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
              className="flex-shrink-0 w-6 h-6 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </motion.button>
          </div>
        </div>

        {/* Progress bar */}
        <motion.div
          initial={{ scaleX: 1 }}
          animate={{ scaleX: 0 }}
          transition={{ duration: duration / 1000, ease: "linear" }}
          className="absolute bottom-0 left-0 right-0 h-1 bg-white/30 origin-left"
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