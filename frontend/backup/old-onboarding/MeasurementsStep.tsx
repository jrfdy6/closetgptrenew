import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { SkipForward } from 'lucide-react';

interface MeasurementsStepProps {
  onComplete: () => void;
}

const TOP_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '2XL', '3XL'];
const BOTTOM_SIZES = ['26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '38', '40', '42', '44', '46'];
const SHOE_SIZES = ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13'];

export function MeasurementsStep({ onComplete }: MeasurementsStepProps) {
  const { toast } = useToast();
  const { 
    height, 
    weight, 
    topSize, 
    bottomSize, 
    shoeSize, 
    inseam, 
    waist, 
    chest,
    setBasicInfo,
    setMeasurements
  } = useOnboardingStore();
  
  const [feet, setFeet] = useState(Math.floor((parseInt(height) || 0) / 12));
  const [inches, setInches] = useState((parseInt(height) || 0) % 12);
  const [pounds, setPounds] = useState(weight || '');

  const handleComplete = () => {
    const totalInches = (feet * 12) + inches;
    
    setBasicInfo({
      height: totalInches.toString(),
      weight: pounds,
    });

    onComplete();
  };

  const handleSkip = () => {
    toast({
      title: "Skipped measurements",
      description: "You can always add these later in your profile settings",
    });
    onComplete();
  };

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Measurements & Sizes</h2>
        <p className="text-gray-600 mb-6">
          Help us provide better size recommendations. You can skip any fields you're unsure about.
        </p>

        <div className="space-y-6">
          {/* Height */}
          <div>
            <Label>Height</Label>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <Label htmlFor="feet" className="text-sm">Feet</Label>
                <Input
                  id="feet"
                  type="number"
                  value={feet}
                  onChange={(e) => setFeet(Number(e.target.value))}
                  placeholder="Feet"
                  min="0"
                  max="8"
                />
              </div>
              <div>
                <Label htmlFor="inches" className="text-sm">Inches</Label>
                <Input
                  id="inches"
                  type="number"
                  value={inches}
                  onChange={(e) => setInches(Number(e.target.value))}
                  placeholder="Inches"
                  min="0"
                  max="11"
                />
              </div>
            </div>
          </div>

          {/* Weight */}
          <div>
            <Label htmlFor="weight">Weight (lbs)</Label>
            <Input
              id="weight"
              type="number"
              value={pounds}
              onChange={(e) => setPounds(e.target.value)}
              placeholder="Enter your weight"
              min="50"
              max="500"
            />
          </div>

          {/* Clothing Sizes */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Top Size</Label>
              <Select
                value={topSize || ''}
                onValueChange={(value) => setMeasurements({ topSize: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {TOP_SIZES.map((size) => (
                    <SelectItem key={size} value={size}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Bottom Size</Label>
              <Select
                value={bottomSize || ''}
                onValueChange={(value) => setMeasurements({ bottomSize: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {BOTTOM_SIZES.map((size) => (
                    <SelectItem key={size} value={size}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Shoe Size</Label>
              <Select
                value={shoeSize || ''}
                onValueChange={(value) => setMeasurements({ shoeSize: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {SHOE_SIZES.map((size) => (
                    <SelectItem key={size} value={size}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Optional Measurements */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="chest">Chest (inches)</Label>
              <Input
                id="chest"
                type="number"
                value={chest || ''}
                onChange={(e) => setMeasurements({ chest: e.target.value })}
                placeholder="Optional"
                min="20"
                max="60"
              />
            </div>

            <div>
              <Label htmlFor="waist">Waist (inches)</Label>
              <Input
                id="waist"
                type="number"
                value={waist || ''}
                onChange={(e) => setMeasurements({ waist: e.target.value })}
                placeholder="Optional"
                min="20"
                max="60"
              />
            </div>

            <div>
              <Label htmlFor="inseam">Inseam (inches)</Label>
              <Input
                id="inseam"
                type="number"
                value={inseam || ''}
                onChange={(e) => setMeasurements({ inseam: e.target.value })}
                placeholder="Optional"
                min="20"
                max="40"
              />
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-between">
          <Button 
            variant="ghost" 
            onClick={handleSkip}
            className="text-gray-500"
          >
            <SkipForward className="w-4 h-4 mr-2" />
            Skip for now
          </Button>
          <Button onClick={handleComplete}>
            Continue
          </Button>
        </div>
      </Card>
    </div>
  );
} 