import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

type SlidesPerViewConfig = {
  base?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;
};

interface CarouselProps {
  className?: string;
  children: React.ReactNode;
  slidesPerView?: SlidesPerViewConfig;
  spaceBetween?: number;
  showControls?: boolean;
  showIndicators?: boolean;
  autoPlay?: boolean;
  autoPlayInterval?: number;
}

const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
};

const DEFAULT_AUTOPLAY_INTERVAL = 6000;

function resolveSlidesPerView(config: SlidesPerViewConfig | undefined, width: number): number {
  const base = config?.base ?? 1;
  if (!config) {
    return base;
  }

  if (width >= BREAKPOINTS.xl && config.xl) {
    return config.xl;
  }
  if (width >= BREAKPOINTS.lg && config.lg) {
    return config.lg;
  }
  if (width >= BREAKPOINTS.md && config.md) {
    return config.md;
  }
  if (width >= BREAKPOINTS.sm && config.sm) {
    return config.sm;
  }
  return base;
}

export default function Carousel({
  className,
  children,
  slidesPerView,
  spaceBetween = 24,
  showControls = false,
  showIndicators = false,
  autoPlay = false,
  autoPlayInterval = DEFAULT_AUTOPLAY_INTERVAL,
}: CarouselProps) {
  const trackRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentSlidesPerView, setCurrentSlidesPerView] = useState(() =>
    typeof window === "undefined"
      ? slidesPerView?.base ?? 1
      : resolveSlidesPerView(slidesPerView, window.innerWidth)
  );

  const slides = useMemo(() => React.Children.toArray(children), [children]);
  const totalSlides = slides.length;

  // Create stable keys for slides by extracting keys from children
  const slideKeys = useMemo(() => {
    return slides.map((slide, idx) => {
      if (React.isValidElement(slide) && slide.key != null) {
        return String(slide.key);
      }
      // Try to find a key in the slide's children
      if (React.isValidElement(slide) && React.isValidElement(slide.props?.children)) {
        const child = slide.props.children;
        if (child && typeof child === 'object' && 'key' in child && child.key != null) {
          return String(child.key);
        }
      }
      return `slide-${idx}`;
    });
  }, [slides]);

  const maxIndex = useMemo(() => {
    const visible = Math.max(1, Math.floor(currentSlidesPerView));
    return Math.max(0, totalSlides - visible);
  }, [currentSlidesPerView, totalSlides]);

  const updateTransform = useCallback(
    (index: number) => {
      if (!trackRef.current || !containerRef.current) return;
      
      // Use pixel-based transform to account for margins properly
      requestAnimationFrame(() => {
        if (!trackRef.current || !containerRef.current) return;
        
        const containerWidth = containerRef.current.offsetWidth;
        if (containerWidth === 0) return;
        
        // Calculate slide width (percentage of container)
        const slideWidthPercent = 100 / currentSlidesPerView;
        const slideWidthPx = (containerWidth * slideWidthPercent) / 100;
        
        // Calculate offset: slide width * index + margin * index
        const offset = (slideWidthPx * index) + (spaceBetween * index);
        
        trackRef.current.style.transform = `translateX(-${offset}px)`;
      });
    },
    [currentSlidesPerView, spaceBetween]
  );

  useEffect(() => {
    const handleResize = () => {
      if (typeof window === "undefined") return;
      const nextSlidesPerView = resolveSlidesPerView(slidesPerView, window.innerWidth);
      setCurrentSlidesPerView(nextSlidesPerView);
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [slidesPerView]);

  // Reset index when slides change significantly (e.g., items removed/added)
  const prevTotalSlidesRef = useRef(totalSlides);
  useEffect(() => {
    // If items were removed and current index is now out of bounds, reset to 0
    if (prevTotalSlidesRef.current !== totalSlides) {
      const prevTotal = prevTotalSlidesRef.current;
      prevTotalSlidesRef.current = totalSlides;
      
      // Reset to 0 if items were removed or significantly changed
      if (totalSlides < prevTotal || (prevTotal > 0 && totalSlides === 0)) {
        setCurrentIndex(0);
        updateTransform(0);
        return;
      }
    }
    
    // Clamp current index to valid range
    setCurrentIndex((prev) => {
      const clamped = Math.min(prev, Math.max(0, maxIndex));
      if (clamped !== prev) {
        updateTransform(clamped);
      }
      return clamped;
    });
  }, [totalSlides, maxIndex, updateTransform]);

  // Update transform when currentIndex or slidesPerView changes
  useEffect(() => {
    updateTransform(currentIndex);
  }, [currentIndex, updateTransform]);

  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => {
      const next = prev >= maxIndex ? 0 : prev + 1;
      updateTransform(next);
      return next;
    });
  }, [maxIndex, updateTransform]);

  const handlePrev = useCallback(() => {
    setCurrentIndex((prev) => {
      const next = prev <= 0 ? maxIndex : prev - 1;
      updateTransform(next);
      return next;
    });
  }, [maxIndex, updateTransform]);

  useEffect(() => {
    if (!autoPlay || totalSlides <= Math.ceil(currentSlidesPerView)) {
      return;
    }

    const interval = window.setInterval(() => {
      handleNext();
    }, autoPlayInterval);

    return () => window.clearInterval(interval);
  }, [autoPlay, autoPlayInterval, handleNext, totalSlides, currentSlidesPerView]);

  const indicatorCount = useMemo(() => {
    const visible = Math.max(1, Math.floor(currentSlidesPerView));
    return Math.max(1, totalSlides - visible + 1);
  }, [currentSlidesPerView, totalSlides]);

  const handleIndicatorClick = (index: number) => {
    setCurrentIndex(index);
    updateTransform(index);
  };

  // Slide width as percentage - gaps are handled via margin
  const slideWidth = `${100 / currentSlidesPerView}%`;

  return (
    <div className={cn("relative", className)} ref={containerRef}>
      <div className="overflow-hidden">
        <div
          ref={trackRef}
          className="flex transition-transform duration-500 ease-out"
        >
          {slides.map((child, index) => (
            <div
              key={slideKeys[index]}
              className="flex-shrink-0"
              style={{ 
                flexBasis: slideWidth, 
                maxWidth: slideWidth, 
                minWidth: 0,
                marginRight: index < slides.length - 1 ? `${spaceBetween}px` : 0
              }}
            >
              {child}
            </div>
          ))}
        </div>
      </div>

      {showControls && totalSlides > Math.ceil(currentSlidesPerView) && (
        <>
          <button
            type="button"
            onClick={handlePrev}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 rounded-full bg-white/80 dark:bg-black/60 shadow-md hover:shadow-lg transition-all duration-200 p-2"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={handleNext}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 rounded-full bg-white/80 dark:bg-black/60 shadow-md hover:shadow-lg transition-all duration-200 p-2"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </>
      )}

      {showIndicators && indicatorCount > 1 && (
        <div className="flex justify-center mt-4 gap-2">
          {Array.from({ length: indicatorCount }).map((_, index) => {
            const isActive = index === currentIndex;
            return (
              <button
                key={index}
                type="button"
                aria-label={`Go to slide ${index + 1}`}
                onClick={() => handleIndicatorClick(index)}
                className={cn(
                  "h-2 rounded-full transition-all duration-300",
                  isActive ? "bg-amber-500 w-6" : "bg-amber-200 hover:bg-amber-300 w-2"
                )}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

