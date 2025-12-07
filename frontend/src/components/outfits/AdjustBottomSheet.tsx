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
import { X, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AdjustBottomSheetProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (options: {
    occasion: string;
    mood?: string;
    style?: string;
    baseItemId?: string;
  }) => void;
  weather?: {
    temperature: number;
    condition: string;
    location?: string;
  };
  occasions?: string[];
  moods?: string[];
  styles?: string[];
  baseItems?: Array<{
    id: string;
    name: string;
    imageUrl?: string;
    type: string;
  }>;
  loading?: boolean;
}

const DEFAULT_OCCASIONS = ['Business', 'Casual', 'Date', 'Gym', 'Workout'];
const DEFAULT_MOODS = ['Confident', 'Playful', 'Sophisticated', 'Relaxed', 'Bold', 'Subtle'];
const DEFAULT_STYLES = ['Minimal', 'Preppy', 'Streetwear', 'Bohemian', 'Classic', 'Edgy'];

export default function AdjustBottomSheet({
  open,
  onClose,
  onGenerate,
  weather,
  occasions = DEFAULT_OCCASIONS,
  moods = DEFAULT_MOODS,
  styles = DEFAULT_STYLES,
  baseItems = [],
  loading = false,
}: AdjustBottomSheetProps) {
  const [selectedOccasion, setSelectedOccasion] = useState<string>('');
  const [selectedMood, setSelectedMood] = useState<string>('');
  const [selectedStyle, setSelectedStyle] = useState<string>('');
  const [selectedBaseItem, setSelectedBaseItem] = useState<string>('');

  // Reset selections when sheet closes
  useEffect(() => {
    if (!open) {
      setSelectedOccasion('');
      setSelectedMood('');
      setSelectedStyle('');
      setSelectedBaseItem('');
    }
  }, [open]);

  const handleGenerate = () => {
    if (!selectedOccasion) return;
    
    onGenerate({
      occasion: selectedOccasion,
      mood: selectedMood || undefined,
      style: selectedStyle || undefined,
      baseItemId: selectedBaseItem || undefined,
    });
  };

  const canGenerate = selectedOccasion && !loading;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent
        side="bottom"
        className="h-[90vh] max-h-[90vh] bg-card border-t border-border rounded-t-3xl p-0 overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-border">
          <div className="flex-1">
            <SheetTitle className="text-xl font-display font-semibold text-card-foreground mb-1">
              Refine your look
            </SheetTitle>
            {weather && (
              <SheetDescription className="text-sm text-muted-foreground">
                AI suggestion: Smart Casual • {weather.temperature}°F, {weather.condition}
                {weather.location && ` • ${weather.location}`}
              </SheetDescription>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-11 w-11 text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
          {/* Occasion Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Occasion
            </label>
            <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
              {occasions.map((occasion) => (
                <Chip
                  key={occasion}
                  variant="default"
                  size="default"
                  selected={selectedOccasion === occasion}
                  onClick={() => setSelectedOccasion(occasion)}
                  className="flex-shrink-0"
                >
                  {occasion}
                </Chip>
              ))}
            </div>
          </div>

          {/* Mood Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Mood
            </label>
            <div className="flex flex-wrap gap-3">
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

          {/* Style Section */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Style
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

          {/* Base Item Section (Optional) */}
          {baseItems.length > 0 && (
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
                Base Item (Optional)
              </label>
              <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-2">
                {baseItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() =>
                      setSelectedBaseItem(
                        selectedBaseItem === item.id ? '' : item.id
                      )
                    }
                    className={cn(
                      'flex-shrink-0 w-15 h-15 rounded-xl overflow-hidden border-2 transition-all',
                      selectedBaseItem === item.id
                        ? 'border-primary shadow-lg shadow-primary/30'
                        : 'border-border hover:border-border/70'
                    )}
                    style={{ width: '60px', height: '60px' }}
                  >
                    {item.imageUrl ? (
                      <img
                        src={item.imageUrl}
                        alt={item.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-muted flex items-center justify-center">
                        <span className="text-xs text-muted-foreground">{item.name}</span>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sticky Generate Button */}
        <div className="px-6 pt-4 pb-6 border-t border-border bg-card">
          <Button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className={cn(
              'w-full h-14 text-base font-semibold rounded-2xl transition-all',
              canGenerate
                ? 'bg-gradient-to-r from-primary to-accent text-primary-foreground hover:shadow-lg hover:shadow-primary/30'
                : 'bg-muted text-muted-foreground cursor-not-allowed'
            )}
          >
            {loading ? (
              <>
                <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Look'
            )}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}

