import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepProps } from '@/components/onboarding/StepWizard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

export function StepFitPreferences({ onNext, onPrevious }: StepProps) {
  const { fitPreferences, setStylePreferences } = useOnboardingStore();
  const { toast } = useToast();

  const fitOptions = [
    {
      id: 'fitted',
      name: 'Fitted',
      description: 'Clothes that hug your body closely',
      examples: 'Examples: Slim-fit shirts, skinny jeans, bodycon dresses',
      icon: '👔'
    },
    {
      id: 'relaxed',
      name: 'Relaxed',
      description: 'Comfortable with some breathing room',
      examples: 'Examples: Regular-fit shirts, straight-leg pants, relaxed dresses',
      icon: '😌'
    },
    {
      id: 'oversized',
      name: 'Oversized',
      description: 'Loose and roomy for a laid-back look',
      examples: 'Examples: Oversized sweaters, baggy pants, loose dresses',
      icon: '🫂'
    },
    {
      id: 'loose',
      name: 'Loose',
      description: 'Very loose and flowy for maximum comfort',
      examples: 'Examples: Flowy tops, wide-leg pants, maxi dresses',
      icon: '🌊'
    }
  ];

  const handleFitSelect = (selectedFit: string) => {
    setStylePreferences({ fitPreferences: [selectedFit as any] });
  };

  const handleNext = () => {
    if (fitPreferences.length === 0) {
      toast({
        title: "Please select a fit preference",
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
          Fit Preferences
        </h2>
        <p className="text-lg text-gray-600">
          Choose how you like your clothes to fit.
        </p>
      </div>

      <div className="grid gap-4">
        {fitOptions.map((option) => (
          <Card
            key={option.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              fitPreferences.includes(option.id as any) ? 'ring-2 ring-purple-500 bg-purple-50' : ''
            }`}
            onClick={() => handleFitSelect(option.id)}
          >
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">{option.icon}</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold">{option.name}</h3>
                  <p className="text-gray-600 mb-2">{option.description}</p>
                  <p className="text-sm text-gray-500">{option.examples}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={fitPreferences.length === 0}>
          Next
        </Button>
      </div>
    </div>
  );
} 