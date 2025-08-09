'use client';

import { useState, useRef, useCallback } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Ruler, Weight, Plus, Minus } from 'lucide-react';
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
  const [isLongPressing, setIsLongPressing] = useState(false);
  const longPressRef = useRef<NodeJS.Timeout | null>(null);

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

  // Long press handlers
  const startLongPress = useCallback((action: () => void) => {
    longPressRef.current = setTimeout(() => {
      setIsLongPressing(true);
      const interval = setInterval(action, 100);
      longPressRef.current = setTimeout(() => {
        clearInterval(interval);
        setIsLongPressing(false);
      }, 2000) as any;
    }, 500);
  }, []);

  const stopLongPress = useCallback(() => {
    if (longPressRef.current) {
      clearTimeout(longPressRef.current);
      longPressRef.current = null;
    }
    setIsLongPressing(false);
  }, []);

  // Enhanced stepper helpers for height (feet/inches)
  const incrementFeet = (step = 1) => {
    if (feet + step <= 8) {
      handleHeightChange(feet + step, inches);
    }
  };
  const decrementFeet = (step = 1) => {
    if (feet - step >= 4) {
      handleHeightChange(feet - step, inches);
    }
  };
  const incrementInches = (step = 1) => {
    const newInches = inches + step;
    if (newInches <= 11) {
      handleHeightChange(feet, newInches);
    } else if (feet < 8) {
      const extraFeet = Math.floor(newInches / 12);
      const remainingInches = newInches % 12;
      handleHeightChange(feet + extraFeet, remainingInches);
    }
  };
  const decrementInches = (step = 1) => {
    const newInches = inches - step;
    if (newInches >= 0) {
      handleHeightChange(feet, newInches);
    } else if (feet > 4) {
      const borrowFeet = Math.ceil(Math.abs(newInches) / 12);
      const remainingInches = 12 + (newInches % 12);
      handleHeightChange(feet - borrowFeet, remainingInches);
    }
  };

  // Enhanced stepper helpers for weight (lbs)
  const incrementWeight = (step = 1) => {
    const current = parseInt(weightValue, 10);
    if (Number.isNaN(current)) {
      handleWeightChange('50');
    } else if (current + step <= 400) {
      handleWeightChange(String(current + step));
    }
  };
  const decrementWeight = (step = 1) => {
    const current = parseInt(weightValue, 10);
    if (Number.isNaN(current)) {
      return;
    }
    if (current - step >= 50) {
      handleWeightChange(String(current - step));
    }
  };

  // Click handlers with shift support
  const handleIncrementFeet = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 1 : 1;
    incrementFeet(step);
  };
  const handleDecrementFeet = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 1 : 1;
    decrementFeet(step);
  };
  const handleIncrementInches = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 1 : 1;
    incrementInches(step);
  };
  const handleDecrementInches = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 1 : 1;
    decrementInches(step);
  };
  const handleIncrementWeight = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 5 : 1;
    incrementWeight(step);
  };
  const handleDecrementWeight = (e: React.MouseEvent) => {
    const step = e.shiftKey ? 5 : 1;
    decrementWeight(step);
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
                <div className="flex items-center gap-2 justify-center">
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="h-9 w-9" 
                    aria-label="Decrease feet" 
                    onClick={handleDecrementFeet}
                    onMouseDown={() => startLongPress(() => decrementFeet(1))}
                    onMouseUp={stopLongPress}
                    onMouseLeave={stopLongPress}
                    onTouchStart={() => startLongPress(() => decrementFeet(1))}
                    onTouchEnd={stopLongPress}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  <Input
                    type="number"
                    value={feet}
                    onChange={(e) => handleHeightChange(parseInt(e.target.value) || 0, inches)}
                    className="w-16 text-center text-lg font-semibold"
                    min="4"
                    max="8"
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="h-9 w-9" 
                    aria-label="Increase feet" 
                    onClick={handleIncrementFeet}
                    onMouseDown={() => startLongPress(() => incrementFeet(1))}
                    onMouseUp={stopLongPress}
                    onMouseLeave={stopLongPress}
                    onTouchStart={() => startLongPress(() => incrementFeet(1))}
                    onTouchEnd={stopLongPress}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <Label className="text-sm text-muted-foreground">ft</Label>
              </div>

              {/* Inches */}
              <div className="text-center">
                <div className="flex items-center gap-2 justify-center">
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="h-9 w-9" 
                    aria-label="Decrease inches" 
                    onClick={handleDecrementInches}
                    onMouseDown={() => startLongPress(() => decrementInches(1))}
                    onMouseUp={stopLongPress}
                    onMouseLeave={stopLongPress}
                    onTouchStart={() => startLongPress(() => decrementInches(1))}
                    onTouchEnd={stopLongPress}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  <Input
                    type="number"
                    value={inches}
                    onChange={(e) => handleHeightChange(feet, parseInt(e.target.value) || 0)}
                    className="w-16 text-center text-lg font-semibold"
                    min="0"
                    max="11"
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="h-9 w-9" 
                    aria-label="Increase inches" 
                    onClick={handleIncrementInches}
                    onMouseDown={() => startLongPress(() => incrementInches(1))}
                    onMouseUp={stopLongPress}
                    onMouseLeave={stopLongPress}
                    onTouchStart={() => startLongPress(() => incrementInches(1))}
                    onTouchEnd={stopLongPress}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
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
              <div className="flex items-center gap-2 justify-center">
                <Button 
                  type="button" 
                  variant="outline" 
                  className="h-9 w-9" 
                  aria-label="Decrease weight" 
                  onClick={handleDecrementWeight}
                  onMouseDown={() => startLongPress(() => decrementWeight(5))}
                  onMouseUp={stopLongPress}
                  onMouseLeave={stopLongPress}
                  onTouchStart={() => startLongPress(() => decrementWeight(5))}
                  onTouchEnd={stopLongPress}
                >
                  <Minus className="h-4 w-4" />
                </Button>
                <Input
                  type="number"
                  value={weightValue}
                  onChange={(e) => handleWeightChange(e.target.value)}
                  placeholder="150"
                  className="w-20 text-center text-lg font-semibold"
                  min="50"
                  max="400"
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  className="h-9 w-9" 
                  aria-label="Increase weight" 
                  onClick={handleIncrementWeight}
                  onMouseDown={() => startLongPress(() => incrementWeight(5))}
                  onMouseUp={stopLongPress}
                  onMouseLeave={stopLongPress}
                  onTouchStart={() => startLongPress(() => incrementWeight(5))}
                  onTouchEnd={stopLongPress}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <Label className="text-sm text-muted-foreground">lbs</Label>
            </div>
            
            <p className="text-sm text-muted-foreground text-center">
              You can also type directly in the input field. Hold shift+click for larger steps.
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