import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepProps } from '@/components/onboarding/StepWizard';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

export interface SkinToneData {
  depth: 'light' | 'medium' | 'deep';
  undertone: 'cool' | 'neutral' | 'warm';
  palette: string[];
  id: string;
  color: string;
}

// Simplified skin tone options that align with the gradient
const SKIN_TONE_SPECTRUM: SkinToneData[] = [
  // Very light tones
  { id: 'tone_0', color: '#FFF8F0', depth: 'light', undertone: 'neutral', palette: ['ivory', 'cream', 'soft pink', 'light blue'] },
  { id: 'tone_1', color: '#FFF2E6', depth: 'light', undertone: 'warm', palette: ['peach', 'coral', 'gold', 'warm beige'] },
  { id: 'tone_2', color: '#FFE0BD', depth: 'light', undertone: 'warm', palette: ['peach', 'coral', 'gold', 'warm beige'] },
  { id: 'tone_3', color: '#F5D0A9', depth: 'light', undertone: 'warm', palette: ['peach', 'coral', 'gold', 'warm beige'] },
  { id: 'tone_4', color: '#E6C7A9', depth: 'light', undertone: 'neutral', palette: ['beige', 'cream', 'navy', 'soft pink'] },
  { id: 'tone_5', color: '#D4B483', depth: 'light', undertone: 'neutral', palette: ['beige', 'cream', 'navy', 'soft pink'] },
  // Medium tones (neutral only)
  { id: 'tone_6', color: '#A67C52', depth: 'medium', undertone: 'neutral', palette: ['olive', 'taupe', 'navy', 'terracotta'] },
  { id: 'tone_7', color: '#8B5A2B', depth: 'medium', undertone: 'neutral', palette: ['olive', 'taupe', 'navy', 'terracotta'] },
  { id: 'tone_8', color: '#8B4513', depth: 'medium', undertone: 'neutral', palette: ['olive', 'taupe', 'navy', 'terracotta'] },
  // Deep tones
  { id: 'tone_9', color: '#6B4423', depth: 'deep', undertone: 'warm', palette: ['rich brown', 'gold', 'terracotta', 'olive'] },
  { id: 'tone_10', color: '#5C4033', depth: 'deep', undertone: 'neutral', palette: ['rich brown', 'black', 'navy', 'olive'] },
  { id: 'tone_11', color: '#4A3728', depth: 'deep', undertone: 'neutral', palette: ['rich brown', 'black', 'navy', 'olive'] },
  { id: 'tone_12', color: '#3C2A21', depth: 'deep', undertone: 'warm', palette: ['rich brown', 'gold', 'terracotta', 'olive'] },
  { id: 'tone_13', color: '#2C1810', depth: 'deep', undertone: 'warm', palette: ['rich brown', 'gold', 'terracotta', 'olive'] },
  { id: 'tone_14', color: '#1A0F0A', depth: 'deep', undertone: 'neutral', palette: ['rich brown', 'black', 'navy', 'olive'] },
];

export function StepSkinToneSelector({ onNext, onPrevious }: StepProps) {
  const { skinTone, setBasicInfo } = useOnboardingStore();
  const { toast } = useToast();
  const [hoveredTone, setHoveredTone] = useState<string | null>(null);

  const getToneDescription = (tone: SkinToneData) => {
    const depthLabels = { light: 'Light', medium: 'Medium', deep: 'Deep' };
    const undertoneLabels = { cool: 'Cool', neutral: 'Neutral', warm: 'Warm' };
    return `${depthLabels[tone.depth]} ${undertoneLabels[tone.undertone]}`;
  };

  const getToneBenefits = (tone: SkinToneData) => {
    const benefits = {
      cool: 'Great with blues, purples, and cool tones',
      neutral: 'Versatile with most colors',
      warm: 'Beautiful with golds, oranges, and warm tones',
    };
    return benefits[tone.undertone];
  };

  const handleToneSelect = (tone: SkinToneData) => {
    setBasicInfo({ skinTone: tone });
  };

  const handleNext = () => {
    if (!skinTone.depth) {
      toast({
        title: "Please select your skin tone",
        description: "This helps us suggest colors that will look great on you.",
        variant: "destructive",
      });
      return;
    }
    onNext();
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          What&apos;s your skin tone?
        </h2>
        <p className="text-lg text-gray-600">
          This helps us suggest colors that will look great on you.
        </p>
      </div>

      <div className="space-y-6">
        {/* Spectrum Selector */}
        <div className="space-y-4">
          <Label className="text-sm font-medium">Choose the tone closest to yours:</Label>
          
          <div className="relative">
            {/* Gradient Bar */}
            <div 
              className="relative h-12 rounded-lg overflow-hidden"
              style={{
                background: 'linear-gradient(to right, #FFF8F0 0%, #FFF2E6 6.67%, #FFE0BD 13.33%, #F5D0A9 20%, #E6C7A9 26.67%, #D4B483 33.33%, #A67C52 40%, #8B5A2B 46.67%, #8B4513 53.33%, #6B4423 60%, #5C4033 66.67%, #4A3728 73.33%, #3C2A21 80%, #2C1810 86.67%, #1A0F0A 93.33%, #1A0F0A 100%)'
              }}
            >
              {/* Tone Markers */}
              <div className="absolute inset-0 flex">
                {SKIN_TONE_SPECTRUM.map((tone, index) => (
                  <div
                    key={tone.id}
                    className="relative flex-1 cursor-pointer group"
                    onClick={() => handleToneSelect(tone)}
                    onMouseEnter={() => setHoveredTone(tone.id)}
                    onMouseLeave={() => setHoveredTone(null)}
                  >
                    {/* Hover Effect */}
                    <div className={`absolute inset-0 transition-all duration-200 ${
                      hoveredTone === tone.id 
                        ? 'bg-white/20' 
                        : skinTone?.id === tone.id 
                        ? 'bg-white/30' 
                        : 'hover:bg-white/10'
                    }`} />
                    
                    {/* Selection Indicator */}
                    {skinTone?.id === tone.id && (
                      <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-white rounded-full border-2 border-purple-500 shadow-lg" />
                    )}
                    
                    {/* Hover Tooltip */}
                    {hoveredTone === tone.id && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10">
                        {getToneBenefits(tone)}
                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Labels */}
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>Light</span>
              <span>Medium</span>
              <span>Deep</span>
            </div>
          </div>

          {/* Selected Tone Display */}
          {skinTone && skinTone.depth && (
            <Card className="p-4 bg-purple-50 border-purple-200">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-3 mb-3">
                  <div
                    className="w-8 h-8 rounded-full border-2 border-white shadow-md"
                    style={{ backgroundColor: skinTone.color || '#C68642' }}
                  />
                  <h4 className="font-medium text-purple-800">
                    {getToneDescription(skinTone)}
                  </h4>
                </div>
                <p className="text-sm text-purple-700 mb-3">
                  {getToneBenefits(skinTone)}
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {skinTone.palette.map((color) => (
                    <span
                      key={color}
                      className="px-2 py-1 bg-white border border-gray-200 rounded-full text-xs text-gray-600"
                    >
                      {color}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={!skinTone.depth}>
          Next
        </Button>
      </div>
    </div>
  );
} 