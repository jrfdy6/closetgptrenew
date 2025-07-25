import { useState, useEffect, useCallback } from 'react';

interface ScrollPosition {
  x: number;
  y: number;
  direction: 'up' | 'down' | 'none';
  lastY: number;
}

export const useScrollPosition = (): ScrollPosition => {
  const [scrollPosition, setScrollPosition] = useState<ScrollPosition>({
    x: 0,
    y: 0,
    direction: 'none',
    lastY: 0,
  });

  const handleScroll = useCallback(() => {
    const position = {
      x: window.scrollX,
      y: window.scrollY,
      direction: 'none' as const,
      lastY: scrollPosition.y,
    };

    if (position.y > scrollPosition.y) {
      position.direction = 'down';
    } else if (position.y < scrollPosition.y) {
      position.direction = 'up';
    }

    setScrollPosition(position);
  }, [scrollPosition.y]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  return scrollPosition;
};

// Helper function to scroll to a specific position
export const scrollTo = (
  x: number,
  y: number,
  behavior: ScrollBehavior = 'smooth'
): void => {
  window.scrollTo({
    top: y,
    left: x,
    behavior,
  });
};

// Helper function to scroll to the top of the page
export const scrollToTop = (behavior: ScrollBehavior = 'smooth'): void => {
  scrollTo(0, 0, behavior);
};

// Helper function to scroll to the bottom of the page
export const scrollToBottom = (behavior: ScrollBehavior = 'smooth'): void => {
  scrollTo(0, document.documentElement.scrollHeight, behavior);
};

// Helper function to scroll to a specific element
export const scrollToElement = (
  element: HTMLElement,
  behavior: ScrollBehavior = 'smooth',
  offset: number = 0
): void => {
  const elementPosition = element.getBoundingClientRect().top;
  const offsetPosition = elementPosition + window.pageYOffset - offset;

  scrollTo(0, offsetPosition, behavior);
};

// Helper function to check if an element is in viewport
export const isElementInViewport = (element: HTMLElement): boolean => {
  const rect = element.getBoundingClientRect();

  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
};

// Helper function to get the scroll percentage
export const getScrollPercentage = (): number => {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight;
  const winHeight = document.documentElement.clientHeight;
  const scrollPercent = scrollTop / (docHeight - winHeight);
  return scrollPercent * 100;
}; 