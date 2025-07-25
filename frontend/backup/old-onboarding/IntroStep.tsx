import { useState, useRef } from 'react';
import { useOnboardingStore, Gender, BodyType, SkinTone } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Camera, Upload, SkipForward, Check } from 'lucide-react';
import { SkinToneSelector, SkinToneData } from './SkinToneSelector';
import { getBodyTypes } from '@/lib/utils/bodyTypeUtils';

interface IntroStepProps {
  onComplete: () => void;
}

export function IntroStep({ onComplete }: IntroStepProps) {
  const { toast } = useToast();
  const { name, gender, selfieUrl, bodyType, skinTone, setBasicInfo } = useOnboardingStore();
  const [currentStep, setCurrentStep] = useState(1);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSelfieUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast({
        title: "File too large",
        description: "Please select an image smaller than 10MB",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // Convert file to base64 for preview
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64 = e.target?.result as string;
        setBasicInfo({ selfieUrl: base64 });
        
        // Simulate AI analysis (replace with actual AI service)
        setTimeout(() => {
          // Auto-suggest based on image analysis
          const suggestedBodyType = getBodyTypes(gender || 'prefer-not-to-say')[0] as BodyType;
          const suggestedSkinTone: SkinTone = {
            depth: 'medium',
            undertone: 'neutral',
            palette: ['olive', 'taupe', 'navy'],
            id: 'medium_neutral',
            color: '#C68642'
          };
          
          setBasicInfo({ 
            bodyType: suggestedBodyType, 
            skinTone: suggestedSkinTone 
          });
          
          setIsAnalyzing(false);
          toast({
            title: "Analysis complete!",
            description: `Detected: ${suggestedBodyType} body type, ${suggestedSkinTone.depth} ${suggestedSkinTone.undertone} skin tone`,
          });
        }, 2000);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      setIsAnalyzing(false);
      toast({
        title: "Upload failed",
        description: "Please try again",
        variant: "destructive",
      });
    }
  };

  const handleComplete = () => {
    if (!name) {
      toast({
        title: "Missing Information",
        description: "Please enter your name",
        variant: "destructive",
      });
      return;
    }

    if (!gender) {
      toast({
        title: "Missing Information",
        description: "Please select your gender",
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

    if (!skinTone || !skinTone.id) {
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
    <div className="space-y-6">
      {currentStep === 1 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Welcome to ClosetGPT!</h2>
          <p className="text-muted-foreground mb-6">
            Let's get to know you better to create personalized outfit recommendations.
          </p>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">What's your name?</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setBasicInfo({ name: e.target.value })}
                placeholder="Enter your name"
                className="mt-1"
              />
            </div>

            <div>
              <Label>How do you identify?</Label>
              <RadioGroup
                value={gender || ''}
                onValueChange={(value: Gender) => setBasicInfo({ gender: value })}
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="male" id="male" />
                  <Label htmlFor="male">Male</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="female" id="female" />
                  <Label htmlFor="female">Female</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="non-binary" id="non-binary" />
                  <Label htmlFor="non-binary">Non-binary</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="prefer-not-to-say" id="prefer-not-to-say" />
                  <Label htmlFor="prefer-not-to-say">Prefer not to say</Label>
                </div>
              </RadioGroup>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <Button onClick={() => setCurrentStep(2)} disabled={!name || !gender}>
              Next
            </Button>
          </div>
        </Card>
      )}

      {currentStep === 2 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Upload a Selfie (Optional)</h2>
          <p className="text-muted-foreground mb-6">
            Upload a full-body photo to help us automatically detect your body type and skin tone.
          </p>
          
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleSelfieUpload}
                className="hidden"
              />
              
              {!selfieUrl ? (
                <div>
                  <Camera className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600 mb-4">
                    Upload a clear, full-body photo in good lighting
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isAnalyzing}
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Choose Photo
                  </Button>
                </div>
              ) : (
                <div>
                  <img
                    src={selfieUrl}
                    alt="Selfie preview"
                    className="w-32 h-32 mx-auto mb-4 rounded-lg object-cover"
                  />
                  <p className="text-sm text-green-600 mb-4">
                    Photo uploaded successfully!
                  </p>
                  {isAnalyzing && (
                    <p className="text-sm text-blue-600">
                      Analyzing your photo...
                    </p>
                  )}
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isAnalyzing}
                  >
                    Change Photo
                  </Button>
                </div>
              )}
            </div>
            
            <div className="flex justify-center">
              <Button 
                variant="ghost" 
                onClick={() => setCurrentStep(3)}
                className="text-gray-500"
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip for now
              </Button>
            </div>
          </div>
          
          <div className="mt-6 flex justify-between">
            <Button variant="outline" onClick={() => setCurrentStep(1)}>Back</Button>
            <Button onClick={() => setCurrentStep(3)}>Next</Button>
          </div>
        </Card>
      )}

      {currentStep === 3 && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Body Type & Skin Tone</h2>
          <div className="space-y-6">
            <div>
              <Label>Body Type</Label>
              <Select
                value={bodyType || ''}
                onValueChange={(value: BodyType) => setBasicInfo({ bodyType: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your body type" />
                </SelectTrigger>
                <SelectContent>
                  {getBodyTypes(gender || 'prefer-not-to-say').map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {gender && (
                <p className="text-sm text-gray-500 mt-1">
                  Showing body types specific to {gender === 'male' ? 'men' : gender === 'female' ? 'women' : 'all genders'}
                </p>
              )}
            </div>

            <div>
              <SkinToneSelector
                selectedTone={skinTone && skinTone.id ? skinTone as SkinToneData : null}
                onToneSelect={(tone: SkinToneData) => setBasicInfo({ skinTone: tone })}
                onSkip={() => setCurrentStep(4)}
              />
            </div>
          </div>

          <div className="mt-6 flex justify-between">
            <Button variant="outline" onClick={() => setCurrentStep(2)}>Back</Button>
            <Button onClick={handleComplete}>Complete</Button>
          </div>
        </Card>
      )}
    </div>
  );
} 