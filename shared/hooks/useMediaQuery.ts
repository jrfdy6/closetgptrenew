import { useState, useEffect } from 'react';

export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [query]);

  return matches;
};

// Predefined breakpoints
export const BREAKPOINTS = {
  xs: '(max-width: 639px)',
  sm: '(min-width: 640px) and (max-width: 767px)',
  md: '(min-width: 768px) and (max-width: 1023px)',
  lg: '(min-width: 1024px) and (max-width: 1279px)',
  xl: '(min-width: 1280px) and (max-width: 1535px)',
  '2xl': '(min-width: 1536px)',
} as const;

// Predefined device types
export const DEVICE_TYPES = {
  mobile: '(max-width: 767px)',
  tablet: '(min-width: 768px) and (max-width: 1023px)',
  desktop: '(min-width: 1024px)',
} as const;

// Predefined orientation
export const ORIENTATION = {
  portrait: '(orientation: portrait)',
  landscape: '(orientation: landscape)',
} as const;

// Predefined color scheme
export const COLOR_SCHEME = {
  light: '(prefers-color-scheme: light)',
  dark: '(prefers-color-scheme: dark)',
} as const;

// Predefined reduced motion
export const REDUCED_MOTION = {
  reduce: '(prefers-reduced-motion: reduce)',
  noPreference: '(prefers-reduced-motion: no-preference)',
} as const;

// Predefined hover capability
export const HOVER = {
  hover: '(hover: hover)',
  none: '(hover: none)',
} as const;

// Predefined pointer capability
export const POINTER = {
  fine: '(pointer: fine)',
  coarse: '(pointer: coarse)',
  none: '(pointer: none)',
} as const;

// Helper function to create a media query string
export const createMediaQuery = (
  minWidth?: number,
  maxWidth?: number,
  orientation?: 'portrait' | 'landscape'
): string => {
  const conditions: string[] = [];

  if (minWidth) {
    conditions.push(`(min-width: ${minWidth}px)`);
  }

  if (maxWidth) {
    conditions.push(`(max-width: ${maxWidth}px)`);
  }

  if (orientation) {
    conditions.push(`(orientation: ${orientation})`);
  }

  return conditions.join(' and ');
};

// Helper function to check if a media query matches
export const matchesMediaQuery = (query: string): boolean => {
  if (typeof window === 'undefined') {
    return false;
  }
  return window.matchMedia(query).matches;
}; 