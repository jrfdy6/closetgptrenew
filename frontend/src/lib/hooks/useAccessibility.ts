"use client";

import { useState, useEffect } from "react";

interface AccessibilityPreferences {
  reducedMotion: boolean;
  highContrast: boolean;
  largeText: boolean;
}

export function useAccessibility() {
  const [preferences, setPreferences] = useState<AccessibilityPreferences>({
    reducedMotion: false,
    highContrast: false,
    largeText: false
  });

  useEffect(() => {
    // Check OS-level reduce motion preference
    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPreferences(prev => ({
      ...prev,
      reducedMotion: motionQuery.matches
    }));

    // Listen for changes
    const handleMotionChange = (e: MediaQueryListEvent) => {
      setPreferences(prev => ({
        ...prev,
        reducedMotion: e.matches
      }));
    };

    motionQuery.addEventListener("change", handleMotionChange);

    // Check localStorage for user preferences
    const highContrast = localStorage.getItem("highContrast") === "true";
    const largeText = localStorage.getItem("largeText") === "true";
    
    setPreferences(prev => ({
      ...prev,
      highContrast,
      largeText
    }));

    return () => {
      motionQuery.removeEventListener("change", handleMotionChange);
    };
  }, []);

  const toggleHighContrast = () => {
    const newValue = !preferences.highContrast;
    localStorage.setItem("highContrast", String(newValue));
    setPreferences(prev => ({ ...prev, highContrast: newValue }));
    
    // Apply to document
    if (newValue) {
      document.documentElement.classList.add("high-contrast");
    } else {
      document.documentElement.classList.remove("high-contrast");
    }
  };

  const toggleLargeText = () => {
    const newValue = !preferences.largeText;
    localStorage.setItem("largeText", String(newValue));
    setPreferences(prev => ({ ...prev, largeText: newValue }));
    
    // Apply to document
    if (newValue) {
      document.documentElement.classList.add("large-text");
    } else {
      document.documentElement.classList.remove("large-text");
    }
  };

  return {
    ...preferences,
    toggleHighContrast,
    toggleLargeText
  };
}

