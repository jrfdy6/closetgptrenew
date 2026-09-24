import { z } from 'zod';

const measurement = z.union([z.string(), z.number()]).nullish();
const timestamp = z.union([z.number(), z.string(), z.date(), z.object({ seconds: z.number(), nanoseconds: z.number().optional() }).passthrough(), z.object({ _seconds: z.number(), _nanoseconds: z.number().optional() }).passthrough()]);

// Read contract only. Account authority and editable fields are enforced on Railway.
export const UserProfileSchema = z.object({
  id: z.string().nullish(),
  userId: z.string().nullish(),
  user_id: z.string().nullish(),
  name: z.string(),
  email: z.union([z.string().email(), z.literal('')]),
  // Profiles include non-binary and undisclosed responses as well as older labels.
  gender: z.string().nullish(),
  preferences: z.object({
    style: z.array(z.string()).nullish(),
    colors: z.array(z.string()).nullish(),
    occasions: z.array(z.string()).nullish(),
    formality: z.string().nullish(),
    budget: measurement,
    preferredBrands: z.array(z.string()).nullish(),
    fitPreferences: z.union([z.array(z.string()), z.record(z.unknown())]).nullish(),
  }).passthrough().nullish(),
  measurements: z.object({
    height: measurement,
    weight: measurement,
    bodyType: z.string().nullish(),
    skinTone: z.string().nullish(),
    heightFeetInches: measurement,
    topSize: measurement,
    bottomSize: measurement,
    shoeSize: measurement,
    dressSize: measurement,
    jeanWaist: measurement,
    braSize: measurement,
    inseam: measurement,
    waist: measurement,
    chest: measurement,
  }).passthrough().nullish(),
  stylePreferences: z.array(z.string()).nullish(),
  bodyType: z.string().nullish(),
  skinTone: z.string().nullish(),
  fitPreference: z.string().nullish(),
  sizePreference: z.string().nullish(),
  
  // New onboarding fields
  heightFeetInches: measurement,
  weight: measurement,
  topSize: measurement,
  bottomSize: measurement,
  shoeSize: measurement,
  dressSize: measurement,
  jeanWaist: measurement,
  braSize: measurement,
  inseam: measurement,
  waist: measurement,
  chest: measurement,
  budget: measurement,
  preferredBrands: z.array(z.string()).nullish(),
  fitPreferences: z.union([z.array(z.string()), z.record(z.unknown())]).nullish(),
  quizResponses: z.array(z.object({
    questionId: z.string(),
    answer: z.union([z.string(), z.array(z.string())]),
    confidence: z.number(),
  })).optional(),
  colorPalette: z.object({
    primary: z.array(z.string()).nullish(),
    secondary: z.array(z.string()).nullish(),
    accent: z.array(z.string()).nullish(),
    neutral: z.array(z.string()).nullish(),
    avoid: z.array(z.string()).nullish(),
  }).passthrough().nullish(),
  hybridStyleName: z.string().nullish(),
  alignmentScore: z.number().optional(),
  selfieUrl: z.string().nullish(),
  onboardingCompleted: z.boolean().optional(),
  
  createdAt: timestamp.nullish(),
  updatedAt: timestamp.nullish()
}).passthrough().refine(profile => Boolean(profile.id || profile.userId || profile.user_id), { message: 'Profile identity is required' });

export type UserProfile = z.infer<typeof UserProfileSchema>; 