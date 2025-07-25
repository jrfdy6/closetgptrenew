import { z } from 'zod';

export const UserProfileSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  gender: z.enum(['male', 'female']).optional(),
  preferences: z.object({
    style: z.array(z.string()),
    colors: z.array(z.string()),
    occasions: z.array(z.string()),
    formality: z.string().optional(),
    budget: z.string().optional(),
    preferredBrands: z.array(z.string()).optional(),
    fitPreferences: z.array(z.string()).optional(),
  }),
  measurements: z.object({
    height: z.number(),
    weight: z.number(),
    bodyType: z.string(),
    skinTone: z.string().optional(),
    heightFeetInches: z.string().optional(),
    topSize: z.string().optional(),
    bottomSize: z.string().optional(),
    shoeSize: z.string().optional(),
    dressSize: z.string().optional(),
    jeanWaist: z.string().optional(),
    braSize: z.string().optional(),
    inseam: z.string().optional(),
    waist: z.string().optional(),
    chest: z.string().optional(),
  }),
  stylePreferences: z.array(z.string()),
  bodyType: z.string(),
  skinTone: z.string().optional(),
  fitPreference: z.enum(['fitted', 'relaxed', 'oversized', 'loose']).optional(),
  
  // New onboarding fields
  heightFeetInches: z.string().optional(),
  weight: z.union([z.string(), z.number()]).optional(),
  topSize: z.string().optional(),
  bottomSize: z.string().optional(),
  shoeSize: z.string().optional(),
  dressSize: z.string().optional(),
  jeanWaist: z.string().optional(),
  braSize: z.string().optional(),
  inseam: z.string().optional(),
  waist: z.string().optional(),
  chest: z.string().optional(),
  budget: z.string().optional(),
  preferredBrands: z.array(z.string()).optional(),
  fitPreferences: z.array(z.string()).optional(),
  quizResponses: z.array(z.object({
    questionId: z.string(),
    answer: z.union([z.string(), z.array(z.string())]),
    confidence: z.number(),
  })).optional(),
  colorPalette: z.object({
    primary: z.array(z.string()),
    secondary: z.array(z.string()),
    accent: z.array(z.string()),
    neutral: z.array(z.string()),
    avoid: z.array(z.string()),
  }).optional(),
  hybridStyleName: z.string().optional(),
  alignmentScore: z.number().optional(),
  selfieUrl: z.string().optional(),
  onboardingCompleted: z.boolean().optional(),
  
  createdAt: z.number(),
  updatedAt: z.number()
});

export type UserProfile = z.infer<typeof UserProfileSchema>; 