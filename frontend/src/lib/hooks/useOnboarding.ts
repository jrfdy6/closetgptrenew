import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { useUserProfile } from '@/hooks/useUserProfile';
import { useFirebase } from '@/lib/firebase-context';

export function useOnboarding() {
  const router = useRouter();
  const { user } = useFirebase();
  const { updateProfile } = useUserProfile();
  const storeData = useOnboardingStore();
  const {
    name,
    email,
    height,
    heightFeetInches,
    weight,
    bodyType,
    skinTone,
    topSize,
    bottomSize,
    shoeSize,
    dressSize,
    jeanWaist,
    braSize,
    inseam,
    waist,
    chest,
    stylePreferences,
    occasions,
    preferredColors,
    formality,
    budget,
    preferredBrands,
    gender,
    selfieUrl,
    fitPreferences,
    quizResponses,
    colorPalette,
    resetOnboarding,
    hybridStyleName,
    alignmentScore,
  } = storeData;

  // Debug: Log the store data when it changes
  useEffect(() => {
    console.log('=== ONBOARDING HOOK DEBUG ===');
    console.log('Store data changed - hybridStyleName:', storeData.hybridStyleName);
    console.log('Store data changed - stylePreferences:', storeData.stylePreferences);
  }, [storeData.hybridStyleName, storeData.stylePreferences]);

  const saveOnboardingData = async () => {
    if (!user) {
      throw new Error('User must be logged in to save onboarding data');
    }

    // Get the latest store data directly to ensure we have the most recent values
    const latestStoreData = useOnboardingStore.getState();
    
    try {
      console.log('=== ONBOARDING DATA SAVE ATTEMPT ===');
      console.log('User ID:', user.uid);
      console.log('Onboarding store data (from destructured values):', {
        name,
        email,
        height,
        heightFeetInches,
        weight,
        bodyType,
        skinTone,
        stylePreferences,
        preferredColors,
        colorPalette,
        hybridStyleName,
        alignmentScore
      });
      console.log('Onboarding store data (from getState):', {
        name: latestStoreData.name,
        email: latestStoreData.email,
        height: latestStoreData.height,
        heightFeetInches: latestStoreData.heightFeetInches,
        weight: latestStoreData.weight,
        bodyType: latestStoreData.bodyType,
        skinTone: latestStoreData.skinTone,
        stylePreferences: latestStoreData.stylePreferences,
        preferredColors: latestStoreData.preferredColors,
        colorPalette: latestStoreData.colorPalette,
        hybridStyleName: latestStoreData.hybridStyleName,
        alignmentScore: latestStoreData.alignmentScore
      });
      
      // Map onboarding gender to profile gender
      const profileGender = gender === 'prefer-not-to-say' ? undefined : 
                           gender === 'non-binary' ? undefined : 
                           gender as 'male' | 'female' | undefined;
      
      // Create measurements object without undefined values
      const measurements = {
        height: height ? parseInt(height) : 0,
        heightFeetInches: heightFeetInches || '',
        weight: weight ? parseInt(weight) : 0,
        bodyType,
        topSize: topSize || '',
        bottomSize: bottomSize || '',
        shoeSize: shoeSize || '',
        dressSize: dressSize || '',
        jeanWaist: jeanWaist || '',
        braSize: braSize || '',
        inseam: inseam || '',
        waist: waist || '',
        chest: chest || '',
      };
      
      const profileData = {
        name: latestStoreData.name,
        email: latestStoreData.email,
        gender: profileGender,
        heightFeetInches: latestStoreData.heightFeetInches || '',
        weight: latestStoreData.weight || '',
        measurements,
        preferences: {
          style: latestStoreData.stylePreferences,
          colors: latestStoreData.preferredColors,
          occasions: latestStoreData.occasions,
          formality: latestStoreData.formality,
          budget: latestStoreData.budget,
          preferredBrands: latestStoreData.preferredBrands,
          fitPreferences: latestStoreData.fitPreferences,
        },
        stylePreferences: latestStoreData.stylePreferences,
        bodyType: latestStoreData.bodyType || '',
        skinTone: latestStoreData.skinTone && latestStoreData.skinTone.id ? `${latestStoreData.skinTone.depth}_${latestStoreData.skinTone.undertone}` : undefined,
        topSize: latestStoreData.topSize || '',
        bottomSize: latestStoreData.bottomSize || '',
        shoeSize: latestStoreData.shoeSize || '',
        dressSize: latestStoreData.dressSize || '',
        jeanWaist: latestStoreData.jeanWaist || '',
        braSize: latestStoreData.braSize || '',
        budget: latestStoreData.budget || 'mid-range',
        preferredBrands: latestStoreData.preferredBrands || [],
        fitPreferences: latestStoreData.fitPreferences || [],
        quizResponses: latestStoreData.quizResponses || [],
        colorPalette: latestStoreData.colorPalette || {
          primary: [],
          secondary: [],
          accent: [],
          neutral: [],
          avoid: []
        },
        hybridStyleName: latestStoreData.hybridStyleName,
        alignmentScore: latestStoreData.alignmentScore || 0,
        selfieUrl: latestStoreData.selfieUrl,
        onboardingCompleted: true,
      };
      console.log('=== PROFILE DATA TO BE SAVED ===');
      console.log('Complete profile data:', profileData);
      console.log('Key fields check:');
      console.log('- hybridStyleName (raw):', hybridStyleName);
      console.log('- hybridStyleName (in profile):', profileData.hybridStyleName);
      console.log('- colorPalette:', profileData.colorPalette);
      console.log('- heightFeetInches:', profileData.heightFeetInches);
      console.log('- weight:', profileData.weight);
      console.log('- bodyType:', profileData.bodyType);
      console.log('- stylePreferences:', profileData.stylePreferences);
      console.log('=====================================');
      
      await updateProfile(profileData);
      console.log('Profile updated successfully in Firestore');

      // Reset onboarding state
      resetOnboarding();
      
      // Redirect to dashboard after successful save
      router.push('/dashboard');
    } catch (error) {
      console.error('Failed to save onboarding data:', error);
      throw error;
    }
  };

  return {
    saveOnboardingData,
  };
} 