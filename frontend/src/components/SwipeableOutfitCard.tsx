"use client";

import { useState, useRef, useEffect } from "react";
import { Heart, X, RefreshCw, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { triggerInteraction, getRandomAffirmation, showToast } from "@/lib/utils/interactions";

interface OutfitItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  color?: string;
}

interface Outfit {
  id: string;
  name: string;
  occasion?: string;
  mood?: string;
  items: OutfitItem[];
  imageUrl?: string;
}

interface SwipeableOutfitCardProps {
  outfit: Outfit;
  onSave: (outfit: Outfit) => void;
  onNext: () => void;
  onRemix: () => void;
  onClose: () => void;
}

export default function SwipeableOutfitCard({
  outfit,
  onSave,
  onNext,
  onRemix,
  onClose
}: SwipeableOutfitCardProps) {
  const [startX, setStartX] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [showItems, setShowItems] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartX(e.touches[0].clientX);
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    setCurrentX(e.touches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    
    const diff = currentX - startX;
    const threshold = window.innerWidth * 0.3; // 30% of screen width

    if (Math.abs(diff) > threshold) {
      if (diff < 0) {
        // Swipe left - Remix
        handleRemix();
      } else {
        // Swipe right - Next
        handleNext();
      }
    }

    setIsDragging(false);
    setCurrentX(0);
    setStartX(0);
  };

  const handleSave = () => {
    if (isSaved) return;
    
    setIsSaved(true);
    
    // Level 2 interaction - Confirmation
    triggerInteraction(2, {
      haptic: true,
      sound: "chime",
      callback: () => {
        const affirmation = getRandomAffirmation();
        showToast(affirmation, "success");
        onSave(outfit);
      }
    });
  };

  const handleNext = () => {
    // Level 1 interaction - Background
    triggerInteraction(1, {
      callback: onNext
    });
  };

  const handleRemix = () => {
    // Level 1 interaction - Background
    triggerInteraction(1, {
      callback: onRemix
    });
  };

  const dragOffset = isDragging ? currentX - startX : 0;
  const rotation = dragOffset * 0.05; // Slight rotation on drag
  const opacity = 1 - Math.abs(dragOffset) / (window.innerWidth * 0.5);

  return (
    <div className="fixed inset-0 z-[90] bg-black/75 backdrop-blur-xl flex items-center justify-center p-4 animate-fade-in">
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 z-10 w-10 h-10 bg-[#F5F0E8]/20 hover:bg-[#F5F0E8]/30 text-[#F8F5F1] rounded-full flex items-center justify-center transition-colors border border-white/20 backdrop-blur"
        aria-label="Close"
      >
        <X className="w-5 h-5" />
      </button>

      {/* Swipeable Card */}
      <div
        ref={cardRef}
        className="relative w-full max-w-md"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          transform: `translateX(${dragOffset}px) rotate(${rotation}deg)`,
          opacity,
          transition: isDragging ? "none" : "all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)"
        }}
      >
        <div className="card-surface rounded-3xl shadow-2xl overflow-hidden border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/90 dark:bg-[#1A1510]/90 backdrop-blur-xl">
          {/* Outfit Image */}
          <div className="relative aspect-[3/4] bg-[#F5F0E8] dark:bg-[#2C2119]">
            <img
              src={outfit.imageUrl || outfit.items[0]?.imageUrl || "/placeholder.jpg"}
              alt={outfit.name}
              className="w-full h-full object-cover"
            />
            
            {/* Badges */}
            <div className="absolute top-4 left-4 flex flex-col gap-2">
              {outfit.occasion && (
                <div className="px-3 py-1 bg-black/50 backdrop-blur-sm rounded-full text-white text-caption font-medium">
                  {outfit.occasion}
                </div>
              )}
              {outfit.mood && (
                <div className="px-3 py-1 bg-black/50 backdrop-blur-sm rounded-full text-white text-caption font-medium">
                  {outfit.mood}
                </div>
              )}
            </div>

            {/* Heart button */}
            <button
              onClick={handleSave}
              disabled={isSaved}
              className={cn(
                "absolute top-4 right-4 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 border border-white/40 backdrop-blur",
                isSaved
                  ? "bg-[#FF6F61] text-white scale-110"
                  : "bg-white/80 hover:bg-white hover:scale-110 text-[#1A1510]"
              )}
              aria-label={isSaved ? "Outfit saved" : "Save outfit"}
            >
              <Heart
                className={cn(
                  "w-6 h-6 transition-all duration-300",
                  isSaved ? "fill-white text-white" : "text-[#1C1917]"
                )}
              />
            </button>
          </div>

          {/* Outfit Details */}
          <div className="p-6">
            <h2 className="heading-lg mb-2 text-[#1C1917] dark:text-[#F8F5F1]">
              {outfit.name}
            </h2>

            {/* Toggle Items */}
            <button
              onClick={() => setShowItems(!showItems)}
              className="flex items-center gap-2 text-body text-[#57534E] dark:text-[#C4BCB4] mb-4"
            >
              <span>{outfit.items.length} items</span>
              <ChevronDown
                className={cn(
                  "w-4 h-4 transition-transform duration-200",
                  showItems && "rotate-180"
                )}
              />
            </button>

            {/* Items List (Collapsible) */}
            {showItems && (
              <div className="space-y-2 mb-6 animate-fade-in">
                {outfit.items.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-2 bg-[#F5F0E8]/80 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-xl"
                  >
                    <div className="w-10 h-10 bg-[#FFF7E6] dark:bg-[#3D2F24] rounded-lg overflow-hidden flex-shrink-0 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
                      <img
                        src={item.imageUrl}
                        alt={item.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-body-sm font-medium text-[#1C1917] dark:text-[#F8F5F1] truncate">
                        {item.name}
                      </div>
                      <div className="text-caption text-[#57534E] dark:text-[#C4BCB4] capitalize">
                        {item.type}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleRemix}
                className="flex-1 h-12 rounded-xl text-button font-semibold flex items-center justify-center gap-2 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-[#F5F0E8]/70 dark:bg-[#2C2119]/80 text-[#1C1917] dark:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
              >
                <RefreshCw className="w-4 h-4" />
                Remix
              </button>
              <button
                onClick={handleNext}
                className="flex-1 h-12 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white rounded-xl text-button font-semibold transition-transform hover:scale-[1.02] flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25"
              >
                Next look
              </button>
            </div>
          </div>
        </div>

        {/* Swipe indicators */}
        {!isSaved && (
          <div className="absolute -bottom-12 left-0 right-0 flex justify-between text-[#F5F0E8]/60 text-caption font-medium tracking-wide">
            <span>← Remix</span>
            <span>Next →</span>
          </div>
        )}
      </div>

      {/* Drag direction hint */}
      {isDragging && Math.abs(dragOffset) > 50 && (
        <div
          className={cn(
            "absolute top-1/2 -translate-y-1/2 text-white text-2xl font-bold opacity-50",
            dragOffset < 0 ? "right-8" : "left-8"
          )}
        >
          {dragOffset < 0 ? "🔄 REMIX" : "➡️ NEXT"}
        </div>
      )}
    </div>
  );
}

