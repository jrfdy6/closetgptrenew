"use client";

import { useEffect, useState } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function DebugOnboardingPage() {
  const { user } = useFirebase();
  const onboardingData = useOnboardingStore();
  const [firestoreData, setFirestoreData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        if (userDoc.exists()) {
          const data = userDoc.data();
          console.log('Firestore data:', data);
          setFirestoreData(data);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const testArchetypeGeneration = () => {
    const primaryStyles = ['Old Money', 'Cottagecore'];
    const style1 = primaryStyles[0];
    const style2 = primaryStyles[1];
    const key = `${style1} ${style2}`;
    const reverseKey = `${style2} ${style1}`;
    
    const archetypeMap: Record<string, string> = {
      "Old Money Cottagecore": "The Aristocratic Gardener",
      "Cottagecore Old Money": "The Aristocratic Gardener",
    };
    
    const result = archetypeMap[key] || archetypeMap[reverseKey] || `The ${style1} ${style2}`;
    console.log('Test archetype generation:', { primaryStyles, key, reverseKey, result });
    return result;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Onboarding Debug Page</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Onboarding Store Data */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Onboarding Store Data</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">Basic Info:</h3>
              <div className="text-sm space-y-1">
                <div>Name: {onboardingData.name || 'Not set'}</div>
                <div>Email: {onboardingData.email || 'Not set'}</div>
                <div>Gender: {onboardingData.gender || 'Not set'}</div>
                <div>Height: {onboardingData.heightFeetInches || 'Not set'}</div>
                <div>Weight: {onboardingData.weight || 'Not set'}</div>
                <div>Body Type: {onboardingData.bodyType || 'Not set'}</div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium">Style Data:</h3>
              <div className="text-sm space-y-1">
                <div>Style Preferences: {onboardingData.stylePreferences?.join(', ') || 'Not set'}</div>
                <div>Preferred Colors: {onboardingData.preferredColors?.join(', ') || 'Not set'}</div>
                <div>Hybrid Style Name: {onboardingData.hybridStyleName || 'Not set'}</div>
                <div>Alignment Score: {onboardingData.alignmentScore || 'Not set'}</div>
              </div>
            </div>

            {onboardingData.colorPalette && (
              <div>
                <h3 className="font-medium">Color Palette:</h3>
                <div className="text-sm space-y-1">
                  <div>Primary: {onboardingData.colorPalette.primary?.join(', ')}</div>
                  <div>Secondary: {onboardingData.colorPalette.secondary?.join(', ')}</div>
                  <div>Accent: {onboardingData.colorPalette.accent?.join(', ')}</div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Firestore Data */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Firestore Data</h2>
          {firestoreData ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium">Basic Info:</h3>
                <div className="text-sm space-y-1">
                  <div>Name: {firestoreData.name || 'Not set'}</div>
                  <div>Email: {firestoreData.email || 'Not set'}</div>
                  <div>Gender: {firestoreData.gender || 'Not set'}</div>
                  <div>Height: {firestoreData.heightFeetInches || 'Not set'}</div>
                  <div>Weight: {firestoreData.weight || 'Not set'}</div>
                  <div>Body Type: {firestoreData.bodyType || 'Not set'}</div>
                </div>
              </div>
              
              <div>
                <h3 className="font-medium">Style Data:</h3>
                <div className="text-sm space-y-1">
                  <div>Style Preferences: {firestoreData.stylePreferences?.join(', ') || 'Not set'}</div>
                  <div>Preferred Colors: {firestoreData.preferredColors?.join(', ') || 'Not set'}</div>
                  <div>Hybrid Style Name: {firestoreData.hybridStyleName || 'Not set'}</div>
                  <div>Alignment Score: {firestoreData.alignmentScore || 'Not set'}</div>
                </div>
              </div>

              {firestoreData.colorPalette && (
                <div>
                  <h3 className="font-medium">Color Palette:</h3>
                  <div className="text-sm space-y-1">
                    <div>Primary: {firestoreData.colorPalette.primary?.join(', ')}</div>
                    <div>Secondary: {firestoreData.colorPalette.secondary?.join(', ')}</div>
                    <div>Accent: {firestoreData.colorPalette.accent?.join(', ')}</div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted-foreground">No data found in Firestore</p>
          )}
        </Card>
      </div>

      <div className="mt-8 space-y-4">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Test Functions</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">Archetype Test:</h3>
              <Button 
                onClick={() => {
                  const result = testArchetypeGeneration();
                  alert(`Archetype result: ${result}`);
                }}
                className="mt-2"
              >
                Test Archetype Generation
              </Button>
            </div>
          </div>
        </Card>

        <div className="flex gap-4">
          <Button onClick={() => window.location.href = '/onboarding'}>
            Go to Onboarding
          </Button>
          <Button onClick={() => window.location.href = '/profile'}>
            Go to Profile
          </Button>
          <Button onClick={() => window.location.reload()}>
            Refresh Data
          </Button>
        </div>
      </div>
    </div>
  );
} 