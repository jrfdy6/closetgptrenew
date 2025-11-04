/**
 * Micro-Interactions System - 3-Level Hierarchy
 * 
 * Level 1: Background noise (browsing, hovering)
 * Level 2: Confirmation (actions completed)
 * Level 3: Achievement (milestones reached)
 */

// Haptic feedback (if supported)
export const triggerHaptic = (intensity: "light" | "medium" | "heavy" = "light") => {
  if (typeof window === "undefined") return;
  
  // Check if Vibration API is supported
  if (!("vibrate" in navigator)) return;
  
  const patterns = {
    light: [50],           // Single short tap (Level 2)
    medium: [100],         // Single medium tap
    heavy: [100, 50, 100, 50, 100]  // Triple tap pattern (Level 3)
  };
  
  navigator.vibrate(patterns[intensity]);
};

// Visual feedback classes for different interaction levels
export const getInteractionClasses = (level: 1 | 2 | 3) => {
  const baseClasses = "transition-all duration-200";
  
  switch (level) {
    case 1: // Background noise - subtle hover
      return `${baseClasses} hover:scale-102`;
    
    case 2: // Confirmation - clear feedback
      return `${baseClasses} active:scale-95 hover:scale-102`;
    
    case 3: // Achievement - dramatic effect
      return `${baseClasses} animate-scale-in shadow-2xl`;
    
    default:
      return baseClasses;
  }
};

// Play audio feedback (if enabled)
export const playSound = (type: "chime" | "celebration") => {
  if (typeof window === "undefined") return;
  
  // Check localStorage for sound settings
  const soundsEnabled = localStorage.getItem("soundsEnabled") === "true";
  if (!soundsEnabled) return;
  
  // Audio files would be preloaded on app init
  const audioElement = new Audio();
  
  switch (type) {
    case "chime":
      // Soft chime for outfit saves (150ms, ~300-600Hz)
      audioElement.src = "/sounds/chime.mp3";
      audioElement.volume = 0.4;
      break;
    
    case "celebration":
      // Celebration flourish for milestones (1s, rising tone)
      audioElement.src = "/sounds/celebration.mp3";
      audioElement.volume = 0.6;
      break;
  }
  
  audioElement.play().catch(() => {
    // Silently fail if audio can't play
  });
};

// Combined interaction trigger for consistency
export const triggerInteraction = (
  level: 1 | 2 | 3,
  options?: {
    haptic?: boolean;
    sound?: "chime" | "celebration";
    callback?: () => void;
  }
) => {
  const { haptic = true, sound, callback } = options || {};
  
  // Level 1: No feedback (just visual)
  if (level === 1) {
    callback?.();
    return;
  }
  
  // Level 2: Light haptic, optional chime
  if (level === 2) {
    if (haptic) triggerHaptic("light");
    if (sound) playSound(sound);
    callback?.();
    return;
  }
  
  // Level 3: Heavy haptic pattern, celebration sound
  if (level === 3) {
    if (haptic) triggerHaptic("heavy");
    if (sound) playSound(sound);
    callback?.();
    return;
  }
};

// Micro-affirmations for identity reinforcement
export const MICRO_AFFIRMATIONS = [
  "Nice. That's very 'you'.",
  "Perfect choice. You know your style.",
  "This is so you. Trust yourself.",
  "Yes! That's your vibe.",
  "Love that. Very on-brand.",
  "Exactly. That's the one.",
  "So good. You have great taste.",
  "That's it. You nailed it."
];

export const getRandomAffirmation = () => {
  return MICRO_AFFIRMATIONS[Math.floor(Math.random() * MICRO_AFFIRMATIONS.length)];
};

// Toast notification helper
export const showToast = (message: string, type: "success" | "info" | "error" = "success") => {
  if (typeof window === "undefined") return;
  
  // Custom event that can be caught by a Toast component
  const event = new CustomEvent("show-toast", {
    detail: { message, type }
  });
  
  window.dispatchEvent(event);
};

