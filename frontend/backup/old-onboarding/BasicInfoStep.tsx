import { useState } from 'react';
import { useOnboardingStore, BodyType, SkinTone } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

const bodyTypeDescriptions = {
  'Athletic': 'Broad shoulders, defined muscles, and a balanced figure',
  'Curvy': 'Fuller bust and hips with a defined waist',
  'Rectangular': 'Straight figure with minimal waist definition',
  'Hourglass': 'Balanced bust and hips with a defined waist',
  'Pear': 'Narrower shoulders with wider hips',
  'Apple': 'Broader shoulders and midsection with slimmer legs',
  'Inverted Triangle': 'Broad shoulders with narrower hips',
};

const skinToneSwatches = {
  Warm: '#F5D0A9',
  Cool: '#E6C7C7',
  Neutral: '#D4C4B7',
  Olive: '#B5A642',
  Deep: '#3C2A21',
  Medium: '#C68642',
  Fair: '#FFE4C4',
};

interface BasicInfoStepProps {
  onComplete: () => void;
}

export function BasicInfoStep({ onComplete }: BasicInfoStepProps) {
  const { toast } = useToast();
  const { name, height, weight, bodyType, skinTone, setBasicInfo } = useOnboardingStore();
  const heightNum = height ? parseInt(height) : 0;
  const [feet, setFeet] = useState(Math.floor(heightNum / 12));
  const [inches, setInches] = useState(heightNum % 12);
  const [pounds, setPounds] = useState(weight || '');

  const handleComplete = () => {
    if (!name) {
      toast({
        title: "Missing Information",
        description: "Please enter your name",
        variant: "destructive",
      });
      return;
    }

    if (!feet || !inches) {
      toast({
        title: "Missing Information",
        description: "Please enter your height",
        variant: "destructive",
      });
      return;
    }

    if (!pounds) {
      toast({
        title: "Missing Information",
        description: "Please enter your weight",
        variant: "destructive",
      });
      return;
    }

    if (!bodyType) {
      toast({
        title: "Missing Information",
        description: "Please select your body type",
        variant: "destructive",
      });
      return;
    }

    if (!skinTone) {
      toast({
        title: "Missing Information",
        description: "Please select your skin tone",
        variant: "destructive",
      });
      return;
    }

    const totalInches = (feet * 12) + inches;
    setBasicInfo({
      name,
      height: totalInches.toString(),
      weight: pounds,
      bodyType,
      skinTone,
    });
    onComplete();
  };

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <div className="space-y-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setBasicInfo({ name: e.target.value })}
            placeholder="Enter your name"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="feet">Height (feet)</Label>
            <Input
              id="feet"
              type="number"
              value={feet}
              onChange={(e) => setFeet(Number(e.target.value))}
              placeholder="Feet"
              required
            />
          </div>
          <div>
            <Label htmlFor="inches">Height (inches)</Label>
            <Input
              id="inches"
              type="number"
              value={inches}
              onChange={(e) => setInches(Number(e.target.value))}
              placeholder="Inches"
              required
            />
          </div>
        </div>

        <div>
          <Label htmlFor="weight">Weight (lbs)</Label>
          <Input
            id="weight"
            type="number"
            value={pounds}
            onChange={(e) => setPounds(e.target.value)}
            placeholder="Enter your weight"
            required
          />
        </div>

        <div>
          <Label>Body Type</Label>
          <p className="text-sm text-muted-foreground mb-4">
            Select the body type that best describes your figure
          </p>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(bodyTypeDescriptions).map(([type, description]) => (
              <Card
                key={type}
                className={`p-4 cursor-pointer transition-all ${
                  bodyType === type
                    ? 'border-primary ring-2 ring-primary'
                    : 'hover:border-primary/50'
                }`}
                onClick={() => setBasicInfo({ bodyType: type as BodyType })}
              >
                <h3 className="font-medium mb-1">{type}</h3>
                <p className="text-sm text-muted-foreground">{description}</p>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <Label>Skin Tone</Label>
          <div className="grid grid-cols-4 gap-4 mt-2">
            {Object.entries(skinToneSwatches).map(([tone, color]) => (
              <div
                key={tone}
                className={`w-12 h-12 rounded-full cursor-pointer transition-all border border-gray-200 ${
                  skinTone === tone
                    ? 'ring-2 ring-primary ring-offset-2'
                    : 'hover:ring-2 hover:ring-primary/50'
                }`}
                style={{ backgroundColor: color }}
                onClick={() => {
                  console.log('Selected skin tone:', tone);
                  setBasicInfo({ skinTone: tone as SkinTone });
                }}
                title={tone}
              />
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Select the skin tone that best matches your complexion
          </p>
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleComplete}>Continue</Button>
      </div>
    </div>
  );
} 