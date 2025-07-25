import { useState, useEffect } from 'react';

interface WindowSize {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLandscape: boolean;
  isPortrait: boolean;
}

export const useWindowSize = (): WindowSize => {
  const [windowSize, setWindowSize] = useState<WindowSize>({
    width: 0,
    height: 0,
    isMobile: false,
    isTablet: false,
    isDesktop: false,
    isLandscape: false,
    isPortrait: false,
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      setWindowSize({
        width,
        height,
        isMobile: width < 768,
        isTablet: width >= 768 && width < 1024,
        isDesktop: width >= 1024,
        isLandscape: width > height,
        isPortrait: width <= height,
      });
    };

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Call handler right away so state gets updated with initial window size
    handleResize();

    // Remove event listener on cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

// Predefined breakpoints
export const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
  desktop: 1280,
  wide: 1536,
} as const;

// Helper function to check if window size is within a range
export const isWindowSizeInRange = (
  minWidth: number,
  maxWidth: number
): boolean => {
  const width = window.innerWidth;
  return width >= minWidth && width <= maxWidth;
};

// Helper function to get the current breakpoint
export const getCurrentBreakpoint = (): keyof typeof BREAKPOINTS => {
  const width = window.innerWidth;

  if (width < BREAKPOINTS.mobile) return 'mobile';
  if (width < BREAKPOINTS.tablet) return 'tablet';
  if (width < BREAKPOINTS.desktop) return 'desktop';
  return 'wide';
};

// Helper function to check if window is in landscape mode
export const isLandscape = (): boolean => {
  return window.innerWidth > window.innerHeight;
};

// Helper function to check if window is in portrait mode
export const isPortrait = (): boolean => {
  return window.innerWidth <= window.innerHeight;
};

// Helper function to get the window aspect ratio
export const getAspectRatio = (): number => {
  return window.innerWidth / window.innerHeight;
};

// Helper function to check if window is in a specific orientation
export const isOrientation = (orientation: 'landscape' | 'portrait'): boolean => {
  return orientation === 'landscape' ? isLandscape() : isPortrait();
}; 