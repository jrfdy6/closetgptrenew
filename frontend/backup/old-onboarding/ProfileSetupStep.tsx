import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AvatarSelector } from '@/components/ui/avatar-selector';
import { useToast } from '@/components/ui/use-toast';
import { Gender, BodyType, SkinTone } from '@/lib/store/onboardingStore';

// Body type constants
const MALE_BODY_TYPES = [
  { value: "athletic", label: "Athletic" },
  { value: "ectomorph", label: "Ectomorph (Slim)" },
  { value: "mesomorph", label: "Mesomorph (Muscular)" },
  { value: "endomorph", label: "Endomorph (Stocky)" },
  { value: "inverted-triangle", label: "Inverted Triangle" },
  { value: "rectangle", label: "Rectangle" },
];

const FEMALE_BODY_TYPES = [
  { value: "hourglass", label: "Hourglass" },
  { value: "pear", label: "Pear" },
  { value: "apple", label: "Apple" },
  { value: "rectangle", label: "Rectangle" },
  { value: "inverted-triangle", label: "Inverted Triangle" },
  { value: "athletic", label: "Athletic" },
];

interface ProfileSetupStepProps {
  onComplete: () => void;
}

export function ProfileSetupStep({ onComplete }: ProfileSetupStepProps) {
  const { toast } = useToast();
  const { gender, avatarUrl, name, bodyType, skinTone, setBasicInfo } = useOnboardingStore();
  const [currentStep, setCurrentStep] = useState(1);

  const handleGenderSelect = (value: Gender) => {
    setBasicInfo({ gender: value });
  };

  const handleAvatarSelect = (url: string) => {
    setBasicInfo({ avatarUrl: url });
  };

  const handleProfileDetails = () => {
    if (!name) {
      toast({
        title: "Missing Information",
        description: "Please enter your name",
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

    onComplete();
  };

  return (
    <div className="space-y-8">
      {currentStep === 1 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Select Your Gender</h2>
          <RadioGroup
            value={gender || ''}
            onValueChange={handleGenderSelect}
            className="space-y-4"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="male" id="male" />
              <Label htmlFor="male">Male</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="female" id="female" />
              <Label htmlFor="female">Female</Label>
            </div>
          </RadioGroup>
          <div className="mt-6">
            <Button onClick={() => setCurrentStep(2)}>Next</Button>
          </div>
        </Card>
      )}

      {currentStep === 2 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Choose Your Avatar</h2>
          <AvatarSelector
            selectedUrl={avatarUrl}
            onSelect={handleAvatarSelect}
          />
          <div className="mt-6 flex justify-between">
            <Button variant="outline" onClick={() => setCurrentStep(1)}>Back</Button>
            <Button onClick={() => setCurrentStep(3)}>Next</Button>
          </div>
        </Card>
      )}

      {currentStep === 3 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Profile Details</h2>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={name || ''}
                onChange={(e) => setBasicInfo({ name: e.target.value })}
                placeholder="Enter your name"
              />
            </div>

            <div>
              <Label htmlFor="bodyType">Body Type</Label>
              <Select
                value={bodyType || ''}
                onValueChange={(value: BodyType) => setBasicInfo({ bodyType: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your body type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Athletic">Athletic</SelectItem>
                  <SelectItem value="Curvy">Curvy</SelectItem>
                  <SelectItem value="Rectangular">Rectangular</SelectItem>
                  <SelectItem value="Hourglass">Hourglass</SelectItem>
                  <SelectItem value="Pear">Pear</SelectItem>
                  <SelectItem value="Apple">Apple</SelectItem>
                  <SelectItem value="Inverted Triangle">Inverted Triangle</SelectItem>
                  <SelectItem value="Ectomorph">Ectomorph</SelectItem>
                  <SelectItem value="Mesomorph">Mesomorph</SelectItem>
                  <SelectItem value="Endomorph">Endomorph</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="skinTone">Skin Tone</Label>
              <Select
                value={skinTone || ''}
                onValueChange={(value: SkinTone) => setBasicInfo({ skinTone: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your skin tone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Warm">Warm</SelectItem>
                  <SelectItem value="Cool">Cool</SelectItem>
                  <SelectItem value="Neutral">Neutral</SelectItem>
                  <SelectItem value="Olive">Olive</SelectItem>
                  <SelectItem value="Deep">Deep</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="Fair">Fair</SelectItem>
                  <SelectItem value="Light">Light</SelectItem>
                  <SelectItem value="Medium-Light">Medium-Light</SelectItem>
                  <SelectItem value="Medium-Dark">Medium-Dark</SelectItem>
                  <SelectItem value="Dark">Dark</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="mt-6 flex justify-between">
            <Button variant="outline" onClick={() => setCurrentStep(2)}>Back</Button>
            <Button onClick={handleProfileDetails}>Complete</Button>
          </div>
        </Card>
      )}
    </div>
  );
} 