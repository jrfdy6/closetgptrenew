'use client';

import { Card, CardContent } from '@/components/ui/card';
import { SkeletonLoader } from './loading-states';
import { Loader2, Sparkles, Shirt, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EnhancedLoadingProps {
  type?: 'outfit' | 'wardrobe' | 'dashboard' | 'general';
  message?: string;
  showProgress?: boolean;
  progress?: number;
  className?: string;
}

const loadingConfig = {
  outfit: {
    icon: Sparkles,
    messages: [
      'Analyzing your wardrobe...',
      'Matching colors and styles...',
      'Creating the perfect outfit...',
      'Almost ready!'
    ],
    color: 'from-purple-500 to-pink-500'
  },
  wardrobe: {
    icon: Shirt,
    messages: [
      'Loading your wardrobe...',
      'Organizing items...',
      'Almost done!'
    ],
    color: 'from-blue-500 to-cyan-500'
  },
  dashboard: {
    icon: Zap,
    messages: [
      'Loading dashboard...',
      'Gathering insights...',
      'Preparing your data...'
    ],
    color: 'from-amber-500 to-orange-500'
  },
  general: {
    icon: Loader2,
    messages: ['Loading...'],
    color: 'from-gray-500 to-gray-600'
  }
};

export function EnhancedLoading({
  type = 'general',
  message,
  showProgress = false,
  progress,
  className
}: EnhancedLoadingProps) {
  const config = loadingConfig[type];
  const Icon = config.icon;
  const displayMessage = message || config.messages[0];

  return (
    <Card className={cn("border-0 shadow-lg", className)}>
      <CardContent className="p-8 text-center">
        <div className="flex flex-col items-center justify-center space-y-4">
          {/* Animated Icon */}
          <div className={cn(
            "relative w-16 h-16 rounded-full bg-gradient-to-r flex items-center justify-center",
            `bg-gradient-to-r ${config.color}`
          )}>
            <Icon className="h-8 w-8 text-white animate-spin" />
            <div className="absolute inset-0 rounded-full bg-gradient-to-r opacity-75 animate-ping" />
          </div>

          {/* Message */}
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-foreground">
              {displayMessage}
            </h3>
            {showProgress && progress !== undefined && (
              <div className="w-64 space-y-2">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={cn(
                      "h-2 rounded-full transition-all duration-300 ease-out",
                      `bg-gradient-to-r ${config.color}`
                    )}
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {Math.round(Math.min(progress, 100))}% complete
                </p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton for outfit card
 */
export function OutfitCardSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <SkeletonLoader className="w-full h-full" variant="rectangular" />
      </div>
      <CardContent className="p-4 space-y-3">
        <SkeletonLoader className="h-5 w-3/4" />
        <div className="flex gap-2">
          <SkeletonLoader className="h-4 w-16 rounded-full" />
          <SkeletonLoader className="h-4 w-20 rounded-full" />
        </div>
        <div className="flex items-center justify-between">
          <SkeletonLoader className="h-4 w-24" />
          <SkeletonLoader className="h-8 w-8 rounded-full" variant="circular" />
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton for wardrobe item card
 */
export function WardrobeItemSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
        <SkeletonLoader className="w-full h-full" variant="rectangular" />
      </div>
      <CardContent className="p-3 space-y-2">
        <SkeletonLoader className="h-4 w-2/3" />
        <SkeletonLoader className="h-3 w-1/2" />
      </CardContent>
    </Card>
  );
}

/**
 * Grid skeleton for multiple items
 */
export function GridSkeleton({
  count = 6,
  ItemSkeleton = OutfitCardSkeleton,
  className
}: {
  count?: number;
  ItemSkeleton?: React.ComponentType<{ className?: string }>;
  className?: string;
}) {
  return (
    <div className={cn("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <ItemSkeleton key={i} className="animate-fade-in" style={{ animationDelay: `${i * 50}ms` }} />
      ))}
    </div>
  );
}

/**
 * Inline loading spinner
 */
export function InlineSpinner({ size = 'sm', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <Loader2 className={cn("animate-spin text-muted-foreground", sizeClasses[size], className)} />
  );
}

