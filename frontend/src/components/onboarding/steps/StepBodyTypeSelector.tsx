import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepProps } from '@/components/onboarding/StepWizard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

export function StepBodyTypeSelector({ onNext, onPrevious }: StepProps) {
  const { bodyType, setBasicInfo } = useOnboardingStore();
  const { toast } = useToast();

  const bodyTypes = [
    {
      id: 'Athletic',
      name: 'Athletic',
      description: 'Muscular and toned physique',
      icon: '💪'
    },
    {
      id: 'Ectomorph',
      name: 'Ectomorph',
      description: 'Naturally thin and lean',
      icon: '🏃'
    },
    {
      id: 'Mesomorph',
      name: 'Mesomorph',
      description: 'Naturally muscular build',
      icon: '🏋️'
    },
    {
      id: 'Endomorph',
      name: 'Endomorph',
      description: 'Naturally fuller build',
      icon: '🤗'
    },
    {
      id: 'Rectangular',
      name: 'Rectangular',
      description: 'Straight, balanced proportions',
      icon: '📏'
    },
    {
      id: 'Inverted Triangle',
      name: 'Inverted Triangle',
      description: 'Broader shoulders and chest',
      icon: '🔺'
    }
  ];

  const handleBodyTypeSelect = (selectedBodyType: string) => {
    setBasicInfo({ bodyType: selectedBodyType as any });
  };

  const handleNext = () => {
    if (!bodyType) {
      toast({
        title: "Please select your body type",
        description: "This helps us provide better fitting recommendations.",
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
          What&apos;s your body type?
        </h2>
        <p className="text-lg text-gray-600">
          Select your body type for better fitting recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {bodyTypes.map((type) => (
          <Card
            key={type.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              bodyType === type.id ? 'ring-2 ring-purple-500 bg-purple-50' : ''
            }`}
            onClick={() => handleBodyTypeSelect(type.id)}
          >
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">{type.icon}</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold">{type.name}</h3>
                  <p className="text-gray-600">{type.description}</p>
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
        <Button onClick={handleNext} disabled={!bodyType}>
          Next
        </Button>
      </div>
    </div>
  );
} 