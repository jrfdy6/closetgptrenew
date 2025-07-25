import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { updateUserProfile } from '@/lib/firebase/userService';

export type BodyType = 
  | 'Athletic'
  | 'Curvy'
  | 'Rectangular'
  | 'Hourglass'
  | 'Pear'
  | 'Apple'
  | 'Inverted Triangle'
  | 'Ectomorph'
  | 'Mesomorph'
  | 'Endomorph';

export type SkinTone = {
  depth: 'light' | 'medium' | 'deep';
  undertone: 'cool' | 'neutral' | 'warm';
  palette: string[];
  id: string;
  color: string;
};

// Legacy skin tone for backward compatibility
export type LegacySkinTone = 
  | 'Warm'
  | 'Cool'
  | 'Neutral'
  | 'Olive'
  | 'Deep'
  | 'Medium'
  | 'Fair'
  | 'Light'
  | 'Medium-Light'
  | 'Medium-Dark'
  | 'Dark';

export type StylePreference = 
  | 'Dark Academia'
  | 'Old Money'
  | 'Streetwear'
  | 'Y2K'
  | 'Minimalist'
  | 'Boho'
  | 'Preppy'
  | 'Grunge'
  | 'Classic'
  | 'Techwear'
  | 'Androgynous'
  | 'Coastal Chic'
  | 'Business Casual'
  | 'Avant-Garde'
  | 'Cottagecore'
  | 'Edgy'
  | 'Athleisure'
  | 'Casual Cool'
  | 'Romantic'
  | 'Artsy';

export type Occasion = 'casual' | 'business' | 'formal' | 'athletic' | 'evening' | 'beach' | 'outdoor' | 'party' | 'travel' | 'home' | 'work' | 'vacation';
export type FormalityLevel = 'very_casual' | 'casual' | 'smart_casual' | 'business_casual' | 'business' | 'formal' | 'very_formal';
export type Season = 'spring' | 'summer' | 'fall' | 'winter';
export type FitPreference = 'fitted' | 'relaxed' | 'oversized' | 'loose';
export type SizePreference = 'xs' | 's' | 'm' | 'l' | 'xl' | 'xxl';
export type Gender = 'male' | 'female' | 'non-binary' | 'prefer-not-to-say';
export type BudgetRange = 'budget' | 'mid-range' | 'premium' | 'luxury';

// New types for quiz-first flow
export type QuizResponse = {
  questionId: string;
  answer: string | string[];
  confidence: number;
};
export type ColorPalette = {
  primary: string[];
  secondary: string[];
  accent: string[];
  neutral: string[];
  avoid: string[];
};

interface BasicInfo {
  name: string;
  email: string;
  gender: Gender;
  selfieUrl?: string;
  height: string;
  heightFeetInches: string;
  weight: string;
  bodyType: BodyType;
  skinTone: SkinTone;
}

interface Measurements {
  topSize: string;
  bottomSize: string;
  shoeSize: string;
  dressSize: string;
  jeanWaist: string;
  braSize: string;
  inseam?: string;
  waist?: string;
  chest?: string;
}

interface StylePreferences {
  stylePreferences: StylePreference[];
  occasions: Occasion[];
  preferredColors: string[];
  formality: FormalityLevel;
  budget: BudgetRange;
  preferredBrands: string[];
  fitPreferences: FitPreference[];
  quizResponses: QuizResponse[];
  colorPalette: ColorPalette;
  hybridStyleName?: string;
  alignmentScore?: number;
}

interface OnboardingState {
  step: number;
  name: string;
  email: string;
  gender: Gender;
  selfieUrl?: string;
  height: string;
  heightFeetInches: string;
  weight: string;
  bodyType: BodyType;
  skinTone: SkinTone;
  topSize: string;
  bottomSize: string;
  shoeSize: string;
  dressSize: string;
  jeanWaist: string;
  braSize: string;
  inseam?: string;
  waist?: string;
  chest?: string;
  stylePreferences: StylePreference[];
  occasions: Occasion[];
  preferredColors: string[];
  formality: FormalityLevel;
  budget: BudgetRange;
  preferredBrands: string[];
  fitPreferences: FitPreference[];
  quizResponses: QuizResponse[];
  colorPalette: ColorPalette;
  hybridStyleName?: string;
  alignmentScore?: number;
  setStep: (step: number) => void;
  setBasicInfo: (info: Partial<BasicInfo>) => void;
  setMeasurements: (measurements: Partial<Measurements>) => void;
  setStylePreferences: (preferences: Partial<StylePreferences>) => void;
  resetOnboarding: () => void;
  clearCache: () => void;
}

const initialState = {
  step: 1,
  name: '',
  email: '',
  gender: 'prefer-not-to-say' as Gender,
  selfieUrl: '',
  height: '',
  heightFeetInches: '',
  weight: '',
  bodyType: 'Athletic' as BodyType,
  skinTone: { depth: 'medium', undertone: 'neutral', palette: [], id: '', color: '' } as SkinTone,
  topSize: '',
  bottomSize: '',
  shoeSize: '',
  dressSize: '',
  jeanWaist: '',
  braSize: '',
  inseam: '',
  waist: '',
  chest: '',
  stylePreferences: [] as StylePreference[],
  occasions: [] as Occasion[],
  preferredColors: [] as string[],
  formality: 'casual' as FormalityLevel,
  budget: 'mid-range' as BudgetRange,
  preferredBrands: [] as string[],
  fitPreferences: [] as FitPreference[],
  quizResponses: [] as QuizResponse[],
  colorPalette: {
    primary: [],
    secondary: [],
    accent: [],
    neutral: [],
    avoid: []
  } as ColorPalette,
  hybridStyleName: undefined,
  alignmentScore: 0,
};

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      ...initialState,
      setStep: (step) => set({ step }),
      setBasicInfo: (info) =>
        set((state) => ({
          ...state,
          ...info,
        })),
      setMeasurements: (measurements) =>
        set((state) => ({
          ...state,
          ...measurements,
        })),
      setStylePreferences: (preferences) => {
        console.log('=== ONBOARDING STORE DEBUG ===');
        console.log('Setting style preferences:', preferences);
        console.log('hybridStyleName in preferences:', preferences.hybridStyleName);
        return set((state) => {
          const newState = {
            ...state,
            ...preferences,
          };
          console.log('New state hybridStyleName:', newState.hybridStyleName);
          return newState;
        });
      },
      resetOnboarding: () => set(initialState),
      clearCache: () =>
        set((state) => ({
          ...state,
          stylePreferences: [],
          occasions: [],
          preferredColors: [],
          formality: 'casual',
          budget: 'mid-range',
          preferredBrands: [],
          fitPreferences: [],
          quizResponses: [],
          colorPalette: {
            primary: [],
            secondary: [],
            accent: [],
            neutral: [],
            avoid: [],
          },
          // Preserve hybridStyleName if it exists (don't clear it)
          hybridStyleName: state.hybridStyleName,
          alignmentScore: state.alignmentScore || 0,
        })),
    }),
    {
      name: 'onboarding-storage',
    }
  )
); 