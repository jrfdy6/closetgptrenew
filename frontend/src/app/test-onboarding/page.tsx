"use client";

import { useEffect, useState } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function TestOnboardingPage() {
  const { user } = useFirebase();
  const onboardingData = useOnboardingStore();
  const [firestoreData, setFirestoreData] = useState<any>(null);

  useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        if (userDoc.exists()) {
          const data = userDoc.data();
          console.log('Firestore data:', data);
          setFirestoreData(data);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [user]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Onboarding Data Test</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Onboarding Store Data */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Onboarding Store Data</h2>
          <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-96">
            {JSON.stringify(onboardingData, null, 2)}
          </pre>
        </Card>

        {/* Firestore Data */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Firestore Data</h2>
          <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-96">
            {JSON.stringify(firestoreData, null, 2)}
          </pre>
        </Card>
      </div>

      <div className="mt-8">
        <Button onClick={() => window.location.href = '/onboarding'}>
          Go to Onboarding
        </Button>
        <Button 
          onClick={() => window.location.href = '/profile'} 
          className="ml-4"
        >
          Go to Profile
        </Button>
      </div>
    </div>
  );
} 