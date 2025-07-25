import React from 'react';
import { Button } from './button';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingActionButtonProps {
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  showLabel?: boolean;
}

export function FloatingActionButton({
  onClick,
  icon,
  label,
  variant = 'primary',
  size = 'md',
  position = 'bottom-right',
  disabled = false,
  loading = false,
  className,
  showLabel = true,
}: FloatingActionButtonProps) {
  const variantClasses = {
    primary: 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white shadow-lg hover:shadow-xl',
    success: 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white shadow-lg hover:shadow-xl',
    warning: 'bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-white shadow-lg hover:shadow-xl',
  };

  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  };

  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
    'center': 'bottom-1/2 right-6 transform translate-y-1/2',
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.8, y: 20 }}
        transition={{ 
          type: "spring", 
          stiffness: 260, 
          damping: 20,
          duration: 0.3 
        }}
        className={cn(
          'fixed z-50',
          positionClasses[position],
          className
        )}
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative"
        >
          <Button
            onClick={onClick}
            disabled={disabled || loading}
            className={cn(
              'rounded-full shadow-lg hover:shadow-xl transition-all duration-200',
              variantClasses[variant],
              sizeClasses[size],
              'flex items-center justify-center',
              'border-0',
              'focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500/50',
              'active:scale-95'
            )}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
            ) : (
              <div className="flex items-center gap-2">
                {icon}
                {showLabel && (
                  <span className="font-medium text-sm hidden sm:inline">
                    {label}
                  </span>
                )}
              </div>
            )}
          </Button>
          
          {/* Pulse animation for attention */}
          <motion.div
            className="absolute inset-0 rounded-full bg-emerald-400/30"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.7, 0, 0.7]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Specialized floating button for "Wear This Outfit"
export function WearOutfitButton({
  onClick,
  disabled = false,
  loading = false,
  outfitName,
}: {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  outfitName?: string;
}) {
  return (
    <FloatingActionButton
      onClick={onClick}
      icon={<span className="text-lg">👕</span>}
      label={outfitName ? `Wear "${outfitName}"` : "Wear This Outfit"}
      variant="success"
      size="lg"
      position="bottom-right"
      disabled={disabled}
      loading={loading}
      className="sm:bottom-8 sm:right-8"
    />
  );
}

// Floating button for quick actions
export function QuickActionButton({
  onClick,
  icon,
  label,
  variant = 'primary',
  position = 'bottom-left',
  disabled = false,
}: {
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning';
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center';
  disabled?: boolean;
}) {
  return (
    <FloatingActionButton
      onClick={onClick}
      icon={icon}
      label={label}
      variant={variant}
      size="md"
      position={position}
      disabled={disabled}
      showLabel={false}
    />
  );
} 