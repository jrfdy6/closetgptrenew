import { useState } from 'react';
import { useOnboardingStore, ColorPalette } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Check, Palette, X } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepColorPalette({ onNext, onPrevious }: StepProps) {
  const { toast } = useToast();
  const { colorPalette, setStylePreferences } = useOnboardingStore();
  const [selectedPalette, setSelectedPalette] = useState<ColorPalette>(
    colorPalette || {
      primary: [],
      secondary: [],
      accent: [],
      neutral: [],
      avoid: []
    }
  );

  const colorOptions = {
    primary: [
      { name: 'Navy Blue', hex: '#1e3a8a', category: 'primary' },
      { name: 'Forest Green', hex: '#166534', category: 'primary' },
      { name: 'Burgundy', hex: '#991b1b', category: 'primary' },
      { name: 'Charcoal', hex: '#374151', category: 'primary' },
      { name: 'Cream', hex: '#fef3c7', category: 'primary' },
      { name: 'White', hex: '#ffffff', category: 'primary' }
    ],
    secondary: [
      { name: 'Sage Green', hex: '#6b7280', category: 'secondary' },
      { name: 'Dusty Rose', hex: '#f87171', category: 'secondary' },
      { name: 'Warm Beige', hex: '#d6d3d1', category: 'secondary' },
      { name: 'Slate Blue', hex: '#475569', category: 'secondary' },
      { name: 'Taupe', hex: '#a8a29e', category: 'secondary' },
      { name: 'Muted Coral', hex: '#fb7185', category: 'secondary' }
    ],
    accent: [
      { name: 'Gold', hex: '#fbbf24', category: 'accent' },
      { name: 'Emerald', hex: '#10b981', category: 'accent' },
      { name: 'Coral', hex: '#f97316', category: 'accent' },
      { name: 'Lavender', hex: '#a78bfa', category: 'accent' },
      { name: 'Teal', hex: '#14b8a6', category: 'accent' },
      { name: 'Rose Gold', hex: '#fda4af', category: 'accent' }
    ],
    neutral: [
      { name: 'Black', hex: '#000000', category: 'neutral' },
      { name: 'White', hex: '#ffffff', category: 'neutral' },
      { name: 'Gray', hex: '#6b7280', category: 'neutral' },
      { name: 'Beige', hex: '#f5f5dc', category: 'neutral' },
      { name: 'Ivory', hex: '#fffff0', category: 'neutral' },
      { name: 'Navy', hex: '#1e3a8a', category: 'neutral' }
    ],
    avoid: [
      { name: 'Neon Pink', hex: '#ec4899', category: 'avoid' },
      { name: 'Bright Orange', hex: '#f97316', category: 'avoid' },
      { name: 'Lime Green', hex: '#84cc16', category: 'avoid' },
      { name: 'Electric Blue', hex: '#3b82f6', category: 'avoid' },
      { name: 'Hot Pink', hex: '#db2777', category: 'avoid' },
      { name: 'Bright Yellow', hex: '#eab308', category: 'avoid' }
    ]
  };

  const handleColorToggle = (color: typeof colorOptions.primary[0]) => {
    const category = color.category as keyof ColorPalette;
    setSelectedPalette(prev => ({
      ...prev,
      [category]: prev[category].includes(color.name)
        ? prev[category].filter(c => c !== color.name)
        : [...prev[category], color.name]
    }));
  };

  const handleNext = () => {
    if (selectedPalette.primary.length === 0) {
      toast({
        title: "Please select at least one primary color",
        description: "This helps us understand your color preferences.",
        variant: "destructive",
      });
      return;
    }

    setStylePreferences({ colorPalette: selectedPalette });
    onNext();
  };

  const renderColorSection = (title: string, colors: typeof colorOptions.primary, category: keyof ColorPalette) => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {colors.map((color) => (
          <div
            key={color.name}
            className={`relative cursor-pointer group ${
              selectedPalette[category].includes(color.name)
                ? 'ring-2 ring-primary'
                : ''
            }`}
            onClick={() => handleColorToggle(color)}
          >
            <div
              className="w-full aspect-square rounded-lg border-2 border-gray-200 hover:border-gray-300 transition-colors"
              style={{ backgroundColor: color.hex }}
            />
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              {selectedPalette[category].includes(color.name) ? (
                <Check className="w-5 h-5 text-white drop-shadow-lg" />
              ) : (
                <div className="w-5 h-5 bg-white/80 rounded-full" />
              )}
            </div>
            <p className="text-xs text-center mt-1 text-muted-foreground">
              {color.name}
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Palette className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="text-3xl font-bold">Choose Your Colors</h2>
        <p className="text-muted-foreground text-lg">
          Select the colors that make you feel confident and beautiful.
        </p>
      </div>

      <div className="space-y-8">
        {renderColorSection('Primary Colors (Your favorites)', colorOptions.primary, 'primary')}
        {renderColorSection('Secondary Colors (Nice to have)', colorOptions.secondary, 'secondary')}
        {renderColorSection('Accent Colors (For pops of color)', colorOptions.accent, 'accent')}
        {renderColorSection('Neutral Colors (Basics)', colorOptions.neutral, 'neutral')}
        {renderColorSection('Colors to Avoid', colorOptions.avoid, 'avoid')}
      </div>

      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={onPrevious}
          className="flex items-center"
        >
          Previous
        </Button>
        <Button
          onClick={handleNext}
          className="flex items-center"
          disabled={selectedPalette.primary.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
} 