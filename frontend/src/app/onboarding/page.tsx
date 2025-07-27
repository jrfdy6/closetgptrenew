"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepWizard } from '@/components/onboarding/StepWizard';
import { StepEmailInput } from '@/components/onboarding/steps/StepEmailInput';
import { StepHeightWeightStepper } from '@/components/onboarding/steps/StepHeightWeightStepper';
import { StepBodyTypeSelector } from '@/components/onboarding/steps/StepBodyTypeSelector';
import { StepSizePicker } from '@/components/onboarding/steps/StepSizePicker';
import { StepFitPreferences } from '@/components/onboarding/steps/StepFitPreferences';
import { StepSkinToneSelector } from '@/components/onboarding/steps/StepSkinToneSelector';
import { StepOutfitStyleQuiz } from '@/components/onboarding/steps/StepOutfitStyleQuiz';
import { useToast } from '@/components/ui/use-toast';
import { StepStyleClusters } from '@/components/onboarding/steps/StepStyleClusters';
import { StepGenderSelect } from '@/components/onboarding/steps/StepGenderSelect';
import { useOnboarding } from '@/lib/hooks/useOnboarding';
import { getFirestore, doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { Sparkles } from 'lucide-react';
import { PageLoadingSkeleton } from '@/components/ui/loading-states';

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loading } = useFirebase();
  const { toast } = useToast();
  const { step, setStep, setBasicInfo } = useOnboardingStore();
  const { saveOnboardingData } = useOnboarding();

  useEffect(() => {
    if (loading) return;

    if (!user) {
              router.push('/signin');
      return;
    }

    // Pre-populate store with authenticated user data
    if (user.email && user.displayName) {
      setBasicInfo({
        name: user.displayName || '',
        email: user.email || '',
      });
    }

    // Check if user has already completed onboarding
    // This would typically check a user document in Firestore
    // For now, we'll just proceed with onboarding
  }, [user, loading, router, setBasicInfo]);

  const handleComplete = async () => {
    console.log('🎯 ONBOARDING: handleComplete called');
    try {
      // Save all onboarding data to Firebase using the useOnboarding hook
      console.log('🎯 ONBOARDING: About to call saveOnboardingData()');
      await saveOnboardingData();
      console.log('🎯 ONBOARDING: saveOnboardingData() completed successfully');
      
      toast({
        title: "Onboarding completed!",
        description: "Your profile has been saved successfully.",
      });
      
      console.log('🎯 ONBOARDING: Toast shown, redirect should happen automatically');
      // Redirect to dashboard (this is handled by saveOnboardingData)
    } catch (error) {
      console.error('🎯 ONBOARDING: Error saving onboarding data:', error);
      toast({
        title: "Error saving profile",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  // Define steps conditionally based on authentication
  const baseSteps = [
    {
      id: "gender",
      title: "Gender",
      component: StepGenderSelect,
      description: "How do you identify?"
    },
    {
      id: "height-weight",
      title: "Height & Weight",
      component: StepHeightWeightStepper,
      description: "Help us understand your proportions"
    },
    {
      id: "body-type",
      title: "Body Type",
      component: StepBodyTypeSelector,
      description: "Select your body type"
    },
    {
      id: "size-picker",
      title: "Size Picker",
      component: StepSizePicker,
      description: "What sizes do you typically wear?"
    },
    {
      id: "fit-preferences",
      title: "Fit Preferences",
      component: StepFitPreferences,
      description: "How do you like your clothes to fit?"
    },
    {
      id: "skin-tone",
      title: "Skin Tone",
      component: StepSkinToneSelector,
      description: "Choose your skin tone"
    },
    {
      id: "style-clusters",
      title: "Style Clusters",
      component: StepStyleClusters,
      description: "Discover your style by selecting the clusters that resonate with you."
    },
    {
      id: "outfit-style-quiz",
      title: "Outfit Style Quiz",
      component: StepOutfitStyleQuiz,
      description: "Refine your style by selecting the outfits that resonate with you."
    }
  ];

  // Add email step only for non-authenticated users
  const steps = user && user.email ? baseSteps : [
    {
      id: "gender",
      title: "Gender",
      component: StepGenderSelect,
      description: "How do you identify?"
    },
    {
      id: "email",
      title: "Email",
      component: StepEmailInput,
      description: "Let&apos;s stay connected"
    },
    ...baseSteps.slice(1) // Include all other steps
  ];

  // Simple bounds checking - ensure step is within valid range
  const currentStepIndex = Math.max(0, Math.min((step || 1) - 1, steps.length - 1));

  const handleStepChange = (newStepIndex: number) => {
    // Ensure the new step index is within bounds
    const boundedStepIndex = Math.max(0, Math.min(newStepIndex, steps.length - 1));
    setStep(boundedStepIndex + 1);
  };

  // Show loading state while store is initializing
  if (loading || !user) {
    return (
      <div className="min-h-screen gradient-app-bg">
        <div className="container-readable py-8">
          <PageLoadingSkeleton 
            showHero={true}
            showStats={false}
            showContent={false}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-app-bg">
      <div className="container-readable py-8">
        <div className="max-w-4xl mx-auto">
          {/* Hero Header */}
          <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8 text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-emerald-500 via-yellow-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
            </div>
            <h1 className="text-2xl sm:text-hero text-foreground mb-4">
              Welcome to Your Style Journey
            </h1>
            <p className="text-secondary text-base sm:text-lg">
              Let's create your personalized style profile in just a few minutes
            </p>
          </div>

          <StepWizard
            steps={steps}
            currentStepIndex={currentStepIndex}
            onStepChange={handleStepChange}
            onComplete={handleComplete}
            showProgress={true}
            showNavigation={true}
          />
        </div>
      </div>
    </div>
  );
} 