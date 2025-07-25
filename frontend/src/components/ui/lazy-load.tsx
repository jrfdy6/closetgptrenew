'use client';

import React, { useState, useEffect, useRef, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface LazyLoadProps {
  children: ReactNode;
  className?: string;
  threshold?: number;
  rootMargin?: string;
  placeholder?: ReactNode;
  fallback?: ReactNode;
  onLoad?: () => void;
  onError?: () => void;
}

export function LazyLoad({
  children,
  className,
  threshold = 0.1,
  rootMargin = '50px',
  placeholder,
  fallback,
  onLoad,
  onError,
}: LazyLoadProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
    onError?.();
  };

  if (hasError && fallback) {
    return <div className={className}>{fallback}</div>;
  }

  if (!isVisible) {
    return (
      <div ref={ref} className={cn("min-h-[200px]", className)}>
        {placeholder || (
          <div className="w-full h-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse rounded-lg" />
        )}
      </div>
    );
  }

  return (
    <div className={className}>
      {React.cloneElement(children as React.ReactElement, {
        onLoad: handleLoad,
        onError: handleError,
      })}
      {isLoading && (
        <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse rounded-lg" />
      )}
    </div>
  );
}

// Lazy load wrapper for images
export function LazyImage({
  src,
  alt,
  className,
  ...props
}: {
  src: string;
  alt: string;
  className?: string;
  [key: string]: any;
}) {
  return (
    <LazyLoad
      className={cn("relative", className)}
      placeholder={
        <div className="w-full h-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse rounded-lg" />
      }
    >
      <img
        src={src}
        alt={alt}
        className={cn("w-full h-full object-cover", className)}
        loading="lazy"
        {...props}
      />
    </LazyLoad>
  );
}

// Lazy load wrapper for components
export function LazyComponent({
  children,
  className,
  ...props
}: {
  children: ReactNode;
  className?: string;
  [key: string]: any;
}) {
  return (
    <LazyLoad
      className={className}
      placeholder={
        <div className="w-full h-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse rounded-lg" />
      }
      {...props}
    >
      {children}
    </LazyLoad>
  );
} 