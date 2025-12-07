"use client";

import { useState, useEffect } from 'react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Chip } from '@/components/ui/chip';
import { Badge } from '@/components/ui/badge';
import { X, Sparkles, Shuffle, Sun, AlertCircle, RefreshCw, Cloud, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface OutfitGenerationBottomSheetProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (options: {
    occasion: string;
    style: string;
    mood: string;
  }) => void;
  onShuffle: () => void;
  generating?: boolean;
  weather?: any;
  occasions: string[];
  styles: string[];
  moods: string[];
  baseItem?: any;
  onRemoveBaseItem?: () => void;
  userGender?: string;
}

export default function OutfitGenerationBottomSheet({
  open,
  onClose,
  onGenerate,
  onShuffle,
  generating = false,
  weather,
  occasions,
  styles,
  moods,
  baseItem,
  onRemoveBaseItem,
  userGender,
}: OutfitGenerationBottomSheetProps) {
  const [selectedOccasion, setSelectedOccasion] = useState<string>('');
  const [selectedStyle, setSelectedStyle] = useState<string>('');
  const [selectedMood, setSelectedMood] = useState<string>('');

  // Reset selections when sheet closes
  useEffect(() => {
    if (!open) {
      setSelectedOccasion('');
      setSelectedStyle('');
      setSelectedMood('');
    }
  }, [open]);

  const handleGenerate = () => {
    if (!selectedOccasion || !selectedStyle || !selectedMood) return;
    
    onGenerate({
      occasion: selectedOccasion,
      style: selectedStyle,
      mood: selectedMood,
    });
  };

  const handleShuffleInSheet = () => {
    // Auto-select random values
    const randomOccasion = occasions[Math.floor(Math.random() * occasions.length)];
    const randomStyle = styles[Math.floor(Math.random() * styles.length)];
    const randomMood = moods[Math.floor(Math.random() * moods.length)];
    
    setSelectedOccasion(randomOccasion);
    setSelectedStyle(randomStyle);
    setSelectedMood(randomMood);
    
    // Auto-trigger generation
    setTimeout(() => {
      onGenerate({
        occasion: randomOccasion,
        style: randomStyle,
        mood: randomMood,
      });
    }, 100);
  };

  const canGenerate = selectedOccasion && selectedStyle && selectedMood && !generating;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent
        side="bottom"
        className="h-[90vh] max-h-[90vh] bg-gradient-to-br from-secondary/50 via-secondary/30 to-secondary/50 dark:from-muted dark:via-muted/20 dark:to-muted/20 border-t border-border dark:border-border rounded-t-3xl p-0 overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-border dark:border-border">
          <div className="flex-1">
            <SheetTitle className="text-xl font-display font-semibold text-card-foreground mb-1">
              Generate Your Outfit
            </SheetTitle>
            {weather && (
              <SheetDescription className="text-sm text-muted-foreground flex items-center gap-2">
                <Sun className="h-4 w-4" />
                {Math.round(weather.temperature)}°F, {weather.condition}
                {weather.location && ` • ${weather.location}`}
              </SheetDescription>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-11 w-11 text-muted-foreground hover:text-foreground hover:bg-secondary"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Base Item Indicator */}
        {baseItem && (
          <div className="px-6 pt-4">
            <div className="flex items-center gap-4 p-4 bg-amber-100 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-2xl">
              <div className="w-16 h-16 bg-white dark:bg-gray-800 rounded-xl overflow-hidden flex-shrink-0 shadow-sm">
                <img
                  src={baseItem.imageUrl || baseItem.image_url || '/placeholder.jpg'}
                  alt={baseItem.name || 'Base item'}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/placeholder.jpg';
                  }}
                />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Target className="h-4 w-4 text-amber-600" />
                  <h3 className="font-semibold text-stone-900 dark:text-white text-sm">
                    Building around: {baseItem.name || 'Unknown item'}
                  </h3>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onRemoveBaseItem}
                className="text-stone-500 hover:text-stone-700"
              >
                Remove
              </Button>
            </div>
          </div>
        )}

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
          {/* Occasion Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Occasion *
            </label>
            <div className="flex flex-wrap gap-2">
              {occasions.map((occasion) => (
                <Chip
                  key={occasion}
                  variant="default"
                  size="default"
                  selected={selectedOccasion === occasion}
                  onClick={() => setSelectedOccasion(occasion)}
                >
                  {occasion}
                </Chip>
              ))}
            </div>
          </div>

          {/* Style Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Style *
            </label>
            <div className="flex flex-wrap gap-2">
              {styles.map((style) => (
                <Chip
                  key={style}
                  variant="style"
                  size="style"
                  selected={selectedStyle === style}
                  onClick={() => setSelectedStyle(style)}
                >
                  {style}
                </Chip>
              ))}
            </div>
          </div>

          {/* Mood Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Mood *
            </label>
            <div className="flex flex-wrap gap-2">
              {moods.map((mood) => (
                <Chip
                  key={mood}
                  variant="mood"
                  size="mood"
                  selected={selectedMood === mood}
                  onClick={() => setSelectedMood(mood)}
                >
                  {mood}
                </Chip>
              ))}
            </div>
          </div>

          {/* Selected Preferences Display */}
          {(selectedOccasion || selectedStyle || selectedMood) && (
            <div className="p-4 bg-white/50 dark:bg-gray-800/50 rounded-2xl border border-amber-200 dark:border-amber-800">
              <h4 className="text-sm font-medium text-stone-700 dark:text-gray-300 mb-2">Your Selections:</h4>
              <div className="flex flex-wrap gap-2">
                {selectedOccasion && (
                  <Badge variant="secondary" className="text-xs">
                    {selectedOccasion}
                  </Badge>
                )}
                {selectedStyle && (
                  <Badge variant="outline" className="text-xs">
                    {selectedStyle}
                  </Badge>
                )}
                {selectedMood && (
                  <Badge variant="outline" className="text-xs">
                    {selectedMood}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sticky Bottom Actions */}
        <div className="px-6 pt-4 pb-6 border-t border-border dark:border-border bg-gradient-to-br from-secondary/50 via-secondary/30 to-secondary/50 dark:from-muted dark:via-muted/20 dark:to-muted/20 space-y-3">
          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className={cn(
              'w-full h-14 text-base font-semibold rounded-2xl transition-all',
              canGenerate
                ? 'bg-gradient-to-r from-primary to-accent text-primary-foreground hover:shadow-lg hover:shadow-primary/30'
                : 'bg-muted dark:bg-muted text-muted-foreground cursor-not-allowed'
            )}
          >
            {generating ? (
              <>
                <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Generate Look
              </>
            )}
          </Button>

          {/* Shuffle Button */}
          <motion.div
            whileTap={{ scale: 0.98 }}
            whileHover={{ scale: 1.01 }}
          >
            <Button 
              onClick={handleShuffleInSheet}
              disabled={generating}
              variant="outline"
              className="w-full h-12 text-base font-semibold border-2 border-amber-500/50 hover:border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-all duration-200 relative overflow-hidden group"
              size="lg"
            >
              <motion.div
                animate={generating ? { rotate: 360 } : {}}
                transition={{
                  duration: 1,
                  repeat: generating ? Infinity : 0,
                  ease: "linear"
                }}
              >
                <Shuffle className="h-5 w-5 mr-2 flex-shrink-0" />
              </motion.div>
              <span>Surprise Me! (Shuffle)</span>
              <Sparkles className="h-4 w-4 ml-2 text-amber-500 group-hover:text-amber-600" />
              
              {/* Shimmer effect */}
              {!generating && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/20 to-transparent"
                  animate={{
                    x: ['-100%', '200%']
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "linear",
                    repeatDelay: 1.5
                  }}
                />
              )}
            </Button>
          </motion.div>

          {!canGenerate && !generating && (
            <p className="text-xs text-amber-600 dark:text-amber-400 text-center px-2">
              Select all options or click 'Surprise Me!' to generate
            </p>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

