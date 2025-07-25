import { useOnboardingStore, Gender } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Check, User, Users, Heart, Sparkles } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepQuizLanding({ onNext }: StepProps) {
  const { toast } = useToast();
  const { gender, setBasicInfo } = useOnboardingStore();

  const handleGenderSelect = (selectedGender: Gender) => {
    setBasicInfo({ gender: selectedGender });
    // Auto-advance to next step when gender is selected
    setTimeout(() => onNext(), 500);
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Who are we styling for?
        </h2>
        <p className="text-muted-foreground text-lg">
          Let's start by understanding who we're creating personalized outfits for.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
        <Card
          className={`p-6 cursor-pointer transition-all hover:shadow-lg border-2 ${
            gender === 'male'
              ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
              : 'border-border hover:border-primary/50'
          }`}
          onClick={() => handleGenderSelect('male')}
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Male</h3>
              <p className="text-sm text-muted-foreground">
                Men's fashion and styling
              </p>
            </div>
            {gender === 'male' && (
              <Check className="w-5 h-5 text-primary" />
            )}
          </div>
        </Card>

        <Card
          className={`p-6 cursor-pointer transition-all hover:shadow-lg border-2 ${
            gender === 'female'
              ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
              : 'border-border hover:border-primary/50'
          }`}
          onClick={() => handleGenderSelect('female')}
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
              <Heart className="w-6 h-6 text-pink-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Female</h3>
              <p className="text-sm text-muted-foreground">
                Women's fashion and styling
              </p>
            </div>
            {gender === 'female' && (
              <Check className="w-5 h-5 text-primary" />
            )}
          </div>
        </Card>

        <Card
          className={`p-6 cursor-pointer transition-all hover:shadow-lg border-2 ${
            gender === 'non-binary'
              ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
              : 'border-border hover:border-primary/50'
          }`}
          onClick={() => handleGenderSelect('non-binary')}
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Non-binary</h3>
              <p className="text-sm text-muted-foreground">
                Gender-neutral fashion
              </p>
            </div>
            {gender === 'non-binary' && (
              <Check className="w-5 h-5 text-primary" />
            )}
          </div>
        </Card>

        <Card
          className={`p-6 cursor-pointer transition-all hover:shadow-lg border-2 ${
            gender === 'prefer-not-to-say'
              ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
              : 'border-border hover:border-primary/50'
          }`}
          onClick={() => handleGenderSelect('prefer-not-to-say')}
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-gray-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Prefer not to say</h3>
              <p className="text-sm text-muted-foreground">
                Keep it private
              </p>
            </div>
            {gender === 'prefer-not-to-say' && (
              <Check className="w-5 h-5 text-primary" />
            )}
          </div>
        </Card>
      </div>

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          This helps us provide more personalized recommendations
        </p>
      </div>
    </div>
  );
} 