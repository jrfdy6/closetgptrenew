"use client";

import React from 'react';
import { Card, CardContent, CardHeader } from './card';
import { cn } from '@/lib/utils';

// Enhanced Skeleton Loader with shimmer effect
export function SkeletonLoader({ 
  className, 
  variant = "default" 
}: { 
  className?: string; 
  variant?: "default" | "text" | "circular" | "rectangular";
}) {
  const baseClasses = "animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700";
  
  const variantClasses = {
    default: "rounded-lg",
    text: "rounded h-4",
    circular: "rounded-full",
    rectangular: "rounded-none"
  };

  return (
    <div 
      className={cn(
        baseClasses,
        variantClasses[variant],
        "relative overflow-hidden",
        className
      )}
    >
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
    </div>
  );
}

// Text skeleton with multiple lines
export function TextSkeleton({ 
  lines = 1, 
  className 
}: { 
  lines?: number; 
  className?: string;
}) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLoader 
          key={i} 
          variant="text" 
          className={i === lines - 1 ? "w-3/4" : "w-full"}
        />
      ))}
    </div>
  );
}

// Card skeleton for content areas
export function CardSkeleton({ 
  showHeader = true, 
  showImage = false,
  className,
  style
}: { 
  showHeader?: boolean; 
  showImage?: boolean;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <Card className={cn("overflow-hidden", className)} style={style}>
      {showImage && (
        <div className="aspect-square">
          <SkeletonLoader className="w-full h-full" variant="rectangular" />
        </div>
      )}
      {showHeader && (
        <CardHeader className="pb-3">
          <SkeletonLoader className="h-6 w-3/4 mb-2" />
          <SkeletonLoader className="h-4 w-1/2" />
        </CardHeader>
      )}
      <CardContent>
        <div className="space-y-3">
          <SkeletonLoader className="h-4 w-full" />
          <SkeletonLoader className="h-4 w-2/3" />
          <SkeletonLoader className="h-4 w-1/2" />
        </div>
      </CardContent>
    </Card>
  );
}

// Grid skeleton for multiple cards
export function GridSkeleton({ 
  count = 6, 
  columns = 3,
  showHeader = true,
  showImage = false,
  className 
}: { 
  count?: number; 
  columns?: number;
  showHeader?: boolean;
  showImage?: boolean;
  className?: string;
}) {
  return (
    <div className={cn(
      "grid gap-4 sm:gap-6",
      columns === 2 && "grid-cols-1 sm:grid-cols-2",
      columns === 3 && "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
      columns === 4 && "grid-cols-2 lg:grid-cols-4",
      className
    )}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton 
          key={i} 
          showHeader={showHeader}
          showImage={showImage}
          className="animate-fade-in"
          style={{ animationDelay: `${i * 100}ms` }}
        />
      ))}
    </div>
  );
}

// Inline loading with spinner
export function InlineLoading({ 
  message = "Loading...",
  size = "sm",
  className 
}: { 
  message?: string; 
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6", 
    lg: "h-8 w-8"
  };

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className={cn(
        "animate-spin rounded-full border-2 border-gray-300 border-t-emerald-600",
        sizeClasses[size]
      )} />
      <span className="text-sm text-muted-foreground">{message}</span>
    </div>
  );
}

// Page loading with hero skeleton
export function PageLoadingSkeleton({ 
  showHero = true,
  showStats = true,
  showContent = true,
  className 
}: { 
  showHero?: boolean;
  showStats?: boolean;
  showContent?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* Hero Skeleton */}
      {showHero && (
        <div className="gradient-hero rounded-2xl p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <SkeletonLoader className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl" variant="circular" />
                <SkeletonLoader className="h-8 w-32 sm:h-10" />
              </div>
              <SkeletonLoader className="h-5 w-48 sm:h-6" />
            </div>
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
              <SkeletonLoader className="h-10 w-full sm:w-32" />
              <SkeletonLoader className="h-10 w-full sm:w-36" />
            </div>
          </div>
        </div>
      )}

      {/* Stats Skeleton */}
      {showStats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-fade-in" style={{ animationDelay: `${i * 100}ms` }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <SkeletonLoader className="h-5 w-20" />
                <SkeletonLoader className="w-10 h-10 rounded-xl" variant="circular" />
              </CardHeader>
              <CardContent>
                <SkeletonLoader className="h-8 w-12 mb-2" />
                <SkeletonLoader className="h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Content Skeleton */}
      {showContent && (
        <div className="space-y-6">
          <div className="flex items-center space-x-3 mb-6">
            <SkeletonLoader className="w-8 h-8 rounded-lg" variant="circular" />
            <SkeletonLoader className="h-6 w-48" />
            <SkeletonLoader className="h-6 w-16" />
          </div>
          <GridSkeleton count={3} columns={3} showImage={true} />
        </div>
      )}
    </div>
  );
}

// Progress bar for multi-step processes
export function ProgressBar({ 
  progress, 
  total, 
  className 
}: { 
  progress: number; 
  total: number; 
  className?: string;
}) {
  const percentage = Math.min((progress / total) * 100, 100);

  return (
    <div className={cn("w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700", className)}>
      <div 
        className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

// Shimmer animation keyframes
const shimmerKeyframes = `
  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
`;

// Add shimmer animation to global styles
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = shimmerKeyframes;
  document.head.appendChild(style);
} 