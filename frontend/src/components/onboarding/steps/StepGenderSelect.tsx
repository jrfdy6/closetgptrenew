import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepProps } from '@/components/onboarding/StepWizard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

export function StepGenderSelect({ onNext, onPrevious }: StepProps) {
  const { gender, setBasicInfo } = useOnboardingStore();
  const { toast } = useToast();

  const handleGenderSelect = (selectedGender: string) => {
    setBasicInfo({ gender: selectedGender as any });
  };

  const handleNext = () => {
    if (!gender) {
      toast({
        title: "Please select a gender",
        description: "This helps us provide better recommendations.",
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
          Who are we styling for?
        </h2>
        <p className="text-lg text-gray-600">
          Let&apos;s start by understanding who we&apos;re creating outfits for.
        </p>
      </div>

      <div className="grid gap-4">
        <Card 
          className={`cursor-pointer transition-all hover:shadow-lg ${
            gender === 'male' ? 'ring-2 ring-purple-500 bg-purple-50' : ''
          }`}
          onClick={() => handleGenderSelect('male')}
        >
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">👨</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold">Men</h3>
                <p className="text-gray-600">I&apos;m styling for myself (male)</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card 
          className={`cursor-pointer transition-all hover:shadow-lg ${
            gender === 'female' ? 'ring-2 ring-purple-500 bg-purple-50' : ''
          }`}
          onClick={() => handleGenderSelect('female')}
        >
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">👩</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold">Women</h3>
                <p className="text-gray-600">I&apos;m styling for myself (female)</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card 
          className={`cursor-pointer transition-all hover:shadow-lg ${
            gender === 'non-binary' ? 'ring-2 ring-purple-500 bg-purple-50' : ''
          }`}
          onClick={() => handleGenderSelect('non-binary')}
        >
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">✨</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold">Non-binary</h3>
                <p className="text-gray-600">I&apos;m styling for myself (non-binary)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={!gender}>
          Next
        </Button>
      </div>
    </div>
  );
} 