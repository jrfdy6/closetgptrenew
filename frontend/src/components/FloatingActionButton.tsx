"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface FloatingActionButtonProps {
  onClick: () => void;
  className?: string;
  ariaLabel?: string;
}

export default function FloatingActionButton({ 
  onClick, 
  className,
  ariaLabel = "Generate outfit for today"
}: FloatingActionButtonProps) {
  const [mounted, setMounted] = useState(false);

  // Only render on client to avoid SSR issues
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        // Position
        "fixed bottom-20 right-4 z-50",
        // Size
        "w-16 h-16",
        // Design
        "rounded-full shadow-2xl",
        "flex items-center justify-center",
        // Amber gradient - brand signature
        "bg-gradient-to-br from-[#FFB84C] to-[#FF9400]",
        // Glow effect
        "shadow-[#FFB84C]/40",
        // Breathing animation
        "animate-breathe",
        // Interaction
        "active:scale-95 transition-transform duration-200",
        "hover:shadow-3xl hover:shadow-[#FFB84C]/50",
        // Accessibility
        "focus:outline-none focus:ring-2 focus:ring-[#FFB84C] focus:ring-offset-2 focus:ring-offset-background",
        className
      )}
      aria-label={ariaLabel}
      type="button"
    >
      <Sparkles className="w-7 h-7 text-white" aria-hidden="true" />
    </button>
  );
}

