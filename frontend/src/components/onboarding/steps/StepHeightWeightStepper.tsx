'use client';

import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Ruler, Weight } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepHeightWeightStepper({ onNext, onPrevious }: StepProps) {
  const { toast } = useToast();
  const { heightFeetInches, weight, setBasicInfo } = useOnboardingStore();
  
  // Parse height from "feet'inches" format or default to 5'8"
  const parseHeight = (heightStr: string) => {
    if (!heightStr) return { feet: 5, inches: 8 };
    const match = heightStr.match(/(\d+)'(\d+)"/);
    if (match) {
      return { feet: parseInt(match[1]), inches: parseInt(match[2]) };
    }
    return { feet: 5, inches: 8 };
  };

  const { feet: initialFeet, inches: initialInches } = parseHeight(heightFeetInches);
  const [feet, setFeet] = useState(initialFeet);
  const [inches, setInches] = useState(initialInches);
  const [weightValue, setWeightValue] = useState(weight || '');

  const handleHeightChange = (newFeet: number, newInches: number) => {
    // Ensure valid ranges
    if (newFeet < 4 || newFeet > 8) return; // Reasonable height range
    if (newInches < 0 || newInches > 11) return;
    
    setFeet(newFeet);
    setInches(newInches);
    
    // Convert to "feet'inches" format and save
    const heightStr = `${newFeet}'${newInches.toString().padStart(2, '0')}"`;
    setBasicInfo({ heightFeetInches: heightStr });
  };

  const handleWeightChange = (value: string) => {
    const numValue = parseInt(value);
    if (value === '' || (numValue >= 50 && numValue <= 400)) {
      setWeightValue(value);
      setBasicInfo({ weight: value });
    }
  };

  const handleNext = () => {
    if (!heightFeetInches || !weightValue) {
      toast({
        title: "Please provide your measurements",
        description: "This helps us provide better size recommendations.",
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
          Your measurements
        </h2>
        <p className="text-lg text-gray-600">
          Help us understand your body type and size preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Height */}
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Ruler className="w-5 h-5 text-primary" />
              <Label className="text-lg font-medium">Height</Label>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Feet */}
              <div className="text-center">
                <Input
                  type="number"
                  value={feet}
                  onChange={(e) => handleHeightChange(parseInt(e.target.value) || 0, inches)}
                  className="w-16 text-center text-lg font-semibold"
                  min="4"
                  max="8"
                />
                <Label className="text-sm text-muted-foreground">ft</Label>
              </div>

              {/* Inches */}
              <div className="text-center">
                <Input
                  type="number"
                  value={inches}
                  onChange={(e) => handleHeightChange(feet, parseInt(e.target.value) || 0)}
                  className="w-16 text-center text-lg font-semibold"
                  min="0"
                  max="11"
                />
                <Label className="text-sm text-muted-foreground">in</Label>
              </div>
            </div>
            
            <p className="text-sm text-muted-foreground text-center">
              Total: {feet}'{inches.toString().padStart(2, '0')}"
            </p>
          </div>
        </Card>

        {/* Weight */}
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Weight className="w-5 h-5 text-primary" />
              <Label className="text-lg font-medium">Weight</Label>
            </div>
            
            <div className="text-center">
              <Input
                type="number"
                value={weightValue}
                onChange={(e) => handleWeightChange(e.target.value)}
                placeholder="150"
                className="w-20 text-center text-lg font-semibold"
                min="50"
                max="400"
              />
              <Label className="text-sm text-muted-foreground">lbs</Label>
            </div>
            
            <p className="text-sm text-muted-foreground text-center">
              You can also type directly in the input field
            </p>
          </div>
        </Card>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext}>
          Next
        </Button>
      </div>
    </div>
  );
} 