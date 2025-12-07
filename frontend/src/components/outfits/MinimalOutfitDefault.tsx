"use client";

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Shuffle, ChevronDown, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import AdjustBottomSheet from './AdjustBottomSheet';

interface MinimalOutfitDefaultProps {
  onShuffle: () => void;
  onExpand: (options: {
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
  suggestedOutfit?: {
    name: string;
    occasion: string;
    items?: Array<{
      name: string;
      type: string;
      imageUrl?: string;
    }>;
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
  generating?: boolean;
}

export default function MinimalOutfitDefault({
  onShuffle,
  onExpand,
  weather,
  suggestedOutfit,
  occasions,
  moods,
  styles,
  baseItems,
  generating = false,
}: MinimalOutfitDefaultProps) {
  const [sheetOpen, setSheetOpen] = useState(false);

  return (
    <>
      <div className="space-y-4">
        {/* AI Suggested Outfit Card */}
        {suggestedOutfit ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="bg-card dark:bg-card border border-border rounded-2xl overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-primary" />
                      <h3 className="text-lg font-display font-semibold text-card-foreground">
                        AI Suggested Outfit
                      </h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {suggestedOutfit.name} • {suggestedOutfit.occasion}
                    </p>
                    {weather && (
                      <p className="text-xs text-muted-foreground">
                        {weather.temperature}°F, {weather.condition}
                        {weather.location && ` • ${weather.location}`}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="bg-card dark:bg-card border border-border rounded-2xl overflow-hidden">
              <CardContent className="p-6">
                <div className="text-center py-8">
                  <Sparkles className="w-12 h-12 text-primary mx-auto mb-3 opacity-50" />
                  <p className="text-sm text-muted-foreground">
                    Generate your first outfit to see AI suggestions
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          {/* Shuffle Button */}
          <Button
            onClick={onShuffle}
            disabled={generating}
            className="h-12 bg-card dark:bg-card border border-border text-card-foreground hover:bg-muted hover:border-border active:scale-95 transition-all"
          >
            <Shuffle className="w-5 h-5 mr-2" />
            Shuffle
          </Button>

          {/* Expand Button */}
          <Button
            onClick={() => setSheetOpen(true)}
            disabled={generating}
            className="h-12 bg-gradient-to-r from-primary to-accent text-primary-foreground hover:shadow-lg hover:shadow-primary/30 active:scale-95 transition-all"
          >
            <ChevronDown className="w-5 h-5 mr-2" />
            Expand
          </Button>
        </div>
      </div>

      {/* Adjust Bottom Sheet */}
      <AdjustBottomSheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onGenerate={(options) => {
          setSheetOpen(false);
          onExpand(options);
        }}
        weather={weather}
        occasions={occasions}
        moods={moods}
        styles={styles}
        baseItems={baseItems}
        loading={generating}
      />
    </>
  );
}

