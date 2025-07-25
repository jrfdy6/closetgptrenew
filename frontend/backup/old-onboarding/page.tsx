"use client";

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useOnboardingStore } from '@/lib/store/onboardingStore';

export default function TestOnboardingPage() {
  const router = useRouter();
  const { resetOnboarding } = useOnboardingStore();

  const handleResetAndGo = () => {
    resetOnboarding();
    router.push('/onboarding');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Card className="p-8">
          <h1 className="text-2xl font-bold mb-4">Onboarding Test Page</h1>
          <p className="text-gray-600 mb-6">
            Use this page to easily access and test the enhanced onboarding flow.
          </p>
          
          <div className="space-y-4">
            <Button 
              onClick={() => router.push('/onboarding')}
              className="w-full"
              size="lg"
            >
              Go to Onboarding
            </Button>
            
            <Button 
              onClick={handleResetAndGo}
              variant="outline"
              className="w-full"
              size="lg"
            >
              Reset & Go to Onboarding
            </Button>
            
            <Button 
              onClick={() => router.push('/dashboard')}
              variant="ghost"
              className="w-full"
            >
              Go to Dashboard
            </Button>
          </div>
          
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">Onboarding Flow Steps:</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
              <li>Welcome & Basic Info</li>
              <li>Full Body Photo Upload (Optional)</li>
              <li>Body Type & Skin Tone</li>
              <li>Measurements & Sizes</li>
              <li>Style Filters (Choose top 3)</li>
              <li>Occasion Preferences</li>
              <li>Budget & Brands</li>
              <li>Review & Finalize</li>
            </ol>
          </div>
        </Card>
      </div>
    </div>
  );
} 