'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion';
import { cn } from '@/lib/utils';

// Haptic feedback utility
export const hapticFeedback = {
  light: () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  },
  medium: () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(20);
    }
  },
  heavy: () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(50);
    }
  },
  success: () => {
    if ('vibrate' in navigator) {
      navigator.vibrate([10, 20, 10]);
    }
  },
  error: () => {
    if ('vibrate' in navigator) {
      navigator.vibrate([50, 20, 50]);
    }
  }
};

// Interactive button with haptic feedback
interface InteractiveButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  hapticType?: 'light' | 'medium' | 'heavy' | 'success' | 'error';
  className?: string;
  disabled?: boolean;
  variant?: 'default' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export function InteractiveButton({
  children,
  onClick,
  hapticType = 'light',
  className,
  disabled = false,
  variant = 'default',
  size = 'md'
}: InteractiveButtonProps) {
  const handleClick = () => {
    if (!disabled) {
      hapticFeedback[hapticType]();
      onClick?.();
    }
  };

  return (
    <motion.button
      onClick={handleClick}
      disabled={disabled}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        'relative overflow-hidden rounded-lg font-medium transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'active:scale-95',
        {
          'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
          'bg-transparent hover:bg-accent': variant === 'ghost',
          'border border-input bg-background hover:bg-accent': variant === 'outline',
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
          'opacity-50 cursor-not-allowed': disabled
        },
        className
      )}
    >
      {/* Ripple effect */}
      <motion.div
        className="absolute inset-0 bg-white/20 rounded-lg"
        initial={{ scale: 0, opacity: 0 }}
        whileTap={{ scale: 2, opacity: 0 }}
        transition={{ duration: 0.3 }}
      />
      {children}
    </motion.button>
  );
}

// Swipeable card component
interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
  className?: string;
}

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  className
}: SwipeableCardProps) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-100, 100], [-10, 10]);
  const opacity = useTransform(x, [-100, -50, 0, 50, 100], [0, 1, 1, 1, 0]);

  const handleDragEnd = (event: any, info: PanInfo) => {
    const { offset, velocity } = info;
    
    if (Math.abs(offset.x) > threshold || Math.abs(velocity.x) > 500) {
      if (offset.x > 0 && onSwipeRight) {
        hapticFeedback.success();
        onSwipeRight();
      } else if (offset.x < 0 && onSwipeLeft) {
        hapticFeedback.success();
        onSwipeLeft();
      }
    }
    
    if (Math.abs(offset.y) > threshold || Math.abs(velocity.y) > 500) {
      if (offset.y > 0 && onSwipeDown) {
        hapticFeedback.success();
        onSwipeDown();
      } else if (offset.y < 0 && onSwipeUp) {
        hapticFeedback.success();
        onSwipeUp();
      }
    }
    
    // Reset position
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.1}
      onDragEnd={handleDragEnd}
      style={{ x, y, rotate }}
      className={cn('cursor-grab active:cursor-grabbing', className)}
    >
      <motion.div style={{ opacity }}>
        {children}
      </motion.div>
    </motion.div>
  );
}

// Hover card with parallax effect
interface HoverCardProps {
  children: React.ReactNode;
  className?: string;
  intensity?: number;
}

export function HoverCard({ children, className, intensity = 10 }: HoverCardProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setMousePosition({ x, y });
  };

  const handleMouseLeave = () => {
    setMousePosition({ x: 0, y: 0 });
  };

  const rotateX = useTransform(
    useMotionValue(mousePosition.y), 
    [0, 300], 
    [intensity, -intensity]
  );
  const rotateY = useTransform(
    useMotionValue(mousePosition.x), 
    [0, 300], 
    [-intensity, intensity]
  );

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY }}
      className={cn(
        'perspective-1000 transition-all duration-300',
        'hover:shadow-xl hover:shadow-emerald-500/10',
        className
      )}
    >
      {children}
    </motion.div>
  );
}

// Animated progress indicator
interface AnimatedProgressProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
  animated?: boolean;
}

export function AnimatedProgress({
  value,
  max = 100,
  className,
  showLabel = true,
  animated = true
}: AnimatedProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-sm text-muted-foreground mb-2">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ 
            duration: animated ? 1 : 0,
            ease: "easeOut"
          }}
        />
      </div>
    </div>
  );
}

// Pulse animation component
interface PulseProps {
  children: React.ReactNode;
  className?: string;
  duration?: number;
}

export function Pulse({ children, className, duration = 2 }: PulseProps) {
  return (
    <motion.div
      animate={{
        scale: [1, 1.05, 1],
        opacity: [1, 0.8, 1]
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Shake animation for errors
interface ShakeProps {
  children: React.ReactNode;
  className?: string;
  trigger?: boolean;
}

export function Shake({ children, className, trigger = false }: ShakeProps) {
  return (
    <motion.div
      animate={trigger ? {
        x: [-10, 10, -10, 10, 0],
        rotate: [-2, 2, -2, 2, 0]
      } : {}}
      transition={{
        duration: 0.5,
        ease: "easeInOut"
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Bounce animation for success
interface BounceProps {
  children: React.ReactNode;
  className?: string;
  trigger?: boolean;
}

export function Bounce({ children, className, trigger = false }: BounceProps) {
  return (
    <motion.div
      animate={trigger ? {
        scale: [1, 1.2, 1],
        rotate: [0, 5, -5, 0]
      } : {}}
      transition={{
        duration: 0.6,
        ease: "easeInOut"
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Floating animation
interface FloatingProps {
  children: React.ReactNode;
  className?: string;
  duration?: number;
  distance?: number;
}

export function Floating({ 
  children, 
  className, 
  duration = 3, 
  distance = 10 
}: FloatingProps) {
  return (
    <motion.div
      animate={{
        y: [0, -distance, 0]
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Magnetic effect for buttons
interface MagneticButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  strength?: number;
}

export function MagneticButton({
  children,
  onClick,
  className,
  strength = 0.3
}: MagneticButtonProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!buttonRef.current) return;
    
    const rect = buttonRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    
    setMousePosition({ x: x * strength, y: y * strength });
  };

  const handleMouseLeave = () => {
    setMousePosition({ x: 0, y: 0 });
  };

  return (
    <motion.button
      ref={buttonRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{
        x: mousePosition.x,
        y: mousePosition.y
      }}
      transition={{ type: "spring", stiffness: 150, damping: 15 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={cn(
        'relative overflow-hidden rounded-lg transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        className
      )}
    >
      {/* Ripple effect */}
      <motion.div
        className="absolute inset-0 bg-white/20 rounded-lg"
        initial={{ scale: 0, opacity: 0 }}
        whileTap={{ scale: 2, opacity: 0 }}
        transition={{ duration: 0.3 }}
      />
      {children}
    </motion.button>
  );
}

// Gesture-based interactions
export const useSwipeGesture = (onSwipe: (direction: 'left' | 'right' | 'up' | 'down') => void) => {
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const threshold = 50;

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setStartPoint({ x: touch.clientX, y: touch.clientY });
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!startPoint) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - startPoint.x;
    const deltaY = touch.clientY - startPoint.y;

    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      if (Math.abs(deltaX) > threshold) {
        onSwipe(deltaX > 0 ? 'right' : 'left');
        hapticFeedback.light();
      }
    } else {
      if (Math.abs(deltaY) > threshold) {
        onSwipe(deltaY > 0 ? 'down' : 'up');
        hapticFeedback.light();
      }
    }

    setStartPoint(null);
  };

  return { handleTouchStart, handleTouchEnd };
}; 