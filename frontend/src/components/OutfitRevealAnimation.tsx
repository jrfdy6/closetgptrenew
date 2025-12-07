"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";

interface OutfitRevealAnimationProps {
  isGenerating: boolean;
  onComplete?: () => void;
}

export default function OutfitRevealAnimation({
  isGenerating,
  onComplete
}: OutfitRevealAnimationProps) {
  const [phase, setPhase] = useState<"building" | "assembling" | "revealing" | "complete">("building");
  const [itemsFloating, setItemsFloating] = useState(false);

  useEffect(() => {
    if (!isGenerating) {
      setPhase("building");
      setItemsFloating(false);
      return;
    }

    // Phase 1: Building (0-1s)
    setPhase("building");
    setItemsFloating(true);

    const timer1 = setTimeout(() => {
      // Phase 2: Assembling (1-2.5s)
      setPhase("assembling");
    }, 1000);

    const timer2 = setTimeout(() => {
      // Phase 3: Revealing (2.5-3s)
      setPhase("revealing");
    }, 2500);

    const timer3 = setTimeout(() => {
      // Phase 4: Complete (3s+)
      setPhase("complete");
      setItemsFloating(false);
      onComplete?.();
    }, 3000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [isGenerating, onComplete]);

  if (!isGenerating && phase === "building") {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-md flex items-center justify-center animate-fade-in">
      {/* Animated clothing items */}
      {itemsFloating && (
        <>
          {/* Shirt - floats from right */}
          <div
            className="absolute w-20 h-20 md:w-24 md:h-24 animate-float-in-right"
            style={{
              top: "30%",
              right: phase === "building" ? "-100px" : "45%",
              transition: "all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
              transitionDelay: "0.2s"
            }}
          >
            <div className="text-6xl md:text-7xl opacity-80">👕</div>
          </div>

          {/* Pants - floats from left */}
          <div
            className="absolute w-20 h-20 md:w-24 md:h-24 animate-float-in-left"
            style={{
              top: "50%",
              left: phase === "building" ? "-100px" : "40%",
              transition: "all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
              transitionDelay: "0.4s"
            }}
          >
            <div className="text-6xl md:text-7xl opacity-80">👖</div>
          </div>

          {/* Shoes - floats from bottom */}
          <div
            className="absolute w-20 h-20 md:w-24 md:h-24 animate-float-in-bottom"
            style={{
              bottom: phase === "building" ? "-100px" : "25%",
              left: "50%",
              transform: "translateX(-50%)",
              transition: "all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
              transitionDelay: "0.6s"
            }}
          >
            <div className="text-6xl md:text-7xl opacity-80">👟</div>
          </div>

          {/* Jacket - floats from top */}
          <div
            className="absolute w-20 h-20 md:w-24 md:h-24 animate-float-in-top"
            style={{
              top: phase === "building" ? "-100px" : "20%",
              left: "55%",
              transition: "all 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
              transitionDelay: "0.8s"
            }}
          >
            <div className="text-6xl md:text-7xl opacity-80">🧥</div>
          </div>
        </>
      )}

      {/* Center content */}
      <div className="text-center z-10">
        {/* Sparkle icon with breathing animation */}
        <div className="mb-6 flex justify-center">
          <div
            className={`w-20 h-20 rounded-full gradient-primary flex items-center justify-center shadow-2xl shadow-[#FFB84C]/50 ${
              phase === "revealing" ? "animate-scale-in" : "animate-breathe"
            }`}
          >
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>

        {/* Text with fade transitions */}
        <h2 className="heading-lg text-white mb-2 animate-fade-in">
          {phase === "building" && "Building your fit..."}
          {phase === "assembling" && "Assembling pieces..."}
          {phase === "revealing" && "✨ Almost there!"}
          {phase === "complete" && "Your look is ready!"}
        </h2>

        <p className="text-body text-white/70 animate-fade-in">
          {phase === "building" && "Analyzing your wardrobe"}
          {phase === "assembling" && "Matching colors and styles"}
          {phase === "revealing" && "Final touches"}
          {phase === "complete" && "Swipe to explore"}
        </p>

        {/* Loading bar */}
        <div className="mt-8 w-64 h-1 bg-white/20 rounded-full mx-auto overflow-hidden">
          <div
            className="h-full gradient-primary transition-all duration-300 ease-out"
            style={{
              width:
                phase === "building"
                  ? "33%"
                  : phase === "assembling"
                  ? "66%"
                  : phase === "revealing"
                  ? "90%"
                  : "100%"
            }}
          />
        </div>
      </div>

      {/* Ambient glow effect */}
      {phase === "revealing" && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse" />
        </div>
      )}
    </div>
  );
}

