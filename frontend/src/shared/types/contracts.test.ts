import { ClothingItemSchema, OpenAIClothingAnalysisSchema, UserProfileSchema } from './index';
import { validateClothingItem } from '../utils/validation';
import { getCoreCategory } from '../utils/layering';
import { readVisualAttributes } from '../utils/garmentMetadata';

const garment = {
  id: 'fixture-shirt', userId: 'fixture-owner', name: 'Cotton shirt', type: 'shirt',
  color: 'white', season: ['spring', 'summer'], imageUrl: '/fixture.jpg',
  metadata: { visualAttributes: { material: 'cotton', futureAttribute: 'preserved' }, processingVersion: 3 },
  analysis: { legacyShape: true },
};

describe('shared runtime contracts', () => {
  it('validates garments without discarding legacy analysis or newer metadata', () => {
    const parsed = ClothingItemSchema.parse(garment);
    expect(parsed.metadata).toEqual(garment.metadata);
    expect(parsed.analysis).toEqual(garment.analysis);
    expect(parsed.season).toEqual(['spring', 'summer']);
    expect(parsed.style).toEqual([]);
    expect(ClothingItemSchema.parse({ ...garment, season: 'summer' }).season).toBe('summer');
  });

  it('rejects malformed required garment fields instead of casting arbitrary input', () => {
    expect(ClothingItemSchema.safeParse({ ...garment, name: 14 }).success).toBe(false);
    expect(ClothingItemSchema.safeParse({ ...garment, type: 'unknown-category' }).success).toBe(false);
    expect(ClothingItemSchema.safeParse(null).success).toBe(false);
  });

  it('normalizes aliases while retaining the complete category set used by layering', () => {
    expect(validateClothingItem({ ...garment, type: 'tee shirt' }).type).toBe('shirt');
    expect(validateClothingItem({ ...garment, type: 'blouse' }).type).toBe('blouse');
    expect(getCoreCategory('blouse')).toBe('top');
    expect(getCoreCategory('maxi_skirt')).toBe('bottom');
  });

  it('accepts optional profile responses without stripping persisted onboarding progress', () => {
    const profile = {
      id: 'fixture-owner', name: 'Fixture', email: 'fixture@example.com', gender: 'non-binary',
      preferences: { style: [], colors: [], occasions: [], extraPreference: 'keep' },
      measurements: { height: 0, weight: 0, bodyType: null, skinTone: null },
      stylePreferences: [], bodyType: null, skinTone: null, fitPreference: null,
      onboardingCompleted: false, onboardingProgress: { questionIndex: 3 },
      createdAt: { seconds: 1790000000, nanoseconds: 0 },
    };
    expect(UserProfileSchema.parse(profile)).toEqual(profile);
  });

  it('validates nested analysis and preserves new processing fields', () => {
    const input = { type: 'shirt', season: [], style: [], occasion: [], dominantColors: [], matchingColors: [], metadata: garment.metadata };
    expect(OpenAIClothingAnalysisSchema.parse(input).metadata).toEqual(garment.metadata);
    expect(OpenAIClothingAnalysisSchema.safeParse({ ...input, dominantColors: [false] }).success).toBe(false);
  });
});

describe('legacy metadata compatibility', () => {
  it('preserves legacy shapes of known metadata fields accepted by the backend', () => {
    const metadata = { analysisTimestamp: '2025-01-01T00:00:00Z', itemMetadata: { priceEstimate: 40 }, visualAttributes: { material: ['cotton'] } };
    const parsed = ClothingItemSchema.parse({ ...garment, metadata });
    expect(parsed.metadata).toEqual(metadata);
    expect(readVisualAttributes(parsed)).toBeUndefined();
    expect(readVisualAttributes(ClothingItemSchema.parse(garment))?.material).toBe('cotton');
  });
});

describe('saved profile compatibility with Railway', () => {
  const savedProfile = {
    userId: 'owner', user_id: 'owner', firebase_uid: 'owner', email: 'owner@example.test',
    name: 'Entered Name', gender: 'Non-binary',
    measurements: { height: '5\'8" - 5\'11"', skinTone: 'skin_tone_82' },
    stylePreferences: ['Minimalist'], stylePersona: { id: 'saved-persona' },
    styleQuizSubmissionHash: 'saved-receipt', styleQuizCompletedAt: '2026-09-21T09:00:00Z',
    subscription: { role: 'tier1', flatlays_remaining: 1 }, role: 'tier1',
    created_at: 1790000000, photos: { fullBodyPhoto: 'https://saved.test/owned' },
  };
  it('accepts the supported backend saved-profile fixture without discarding fields', () => {
    expect(UserProfileSchema.parse(savedProfile)).toEqual(savedProfile);
  });
  it.each([null, { topSize: 'M' }, { height: 170, weight: null }])('preserves partial or null measurements %p', measurements => {
    const profile = { ...savedProfile, measurements, preferences: null, fitPreferences: { tops: 'relaxed', bottoms: 'fitted' } };
    expect(UserProfileSchema.parse(profile)).toEqual(profile);
  });
  it('requires a supported identity alias and rejects malformed preference lists', () => {
    expect(UserProfileSchema.safeParse({ name: 'Fixture', email: 'fixture@example.test' }).success).toBe(false);
    expect(UserProfileSchema.safeParse({ ...savedProfile, stylePreferences: 42 }).success).toBe(false);
  });
});
