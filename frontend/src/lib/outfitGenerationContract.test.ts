import { DataValidator } from './dataValidator';
import {
  assertRequiredBaseItem,
  buildOutfitGenerationUserProfile,
} from './outfitGenerationContract';
import { ensureDefaultSkinToneAnswer, upsertQuizAnswer } from './quizAnswerContract';

describe('outfit generation contract', () => {
  it('hydrates quiz signals from the stored profile schema', () => {
    const profile = buildOutfitGenerationUserProfile(
      {
        gender: 'Non-binary',
        stylePreferences: ['Classic', 'Minimalist'],
        colorPalette: {
          primary: ['navy'],
          secondary: ['camel'],
          accent: ['burgundy'],
        },
        measurements: {
          bodyType: 'Inverted Triangle',
          skinTone: 'skin_tone_82',
          height: '6 ft 1 in',
          weight: '190 lb',
          topSize: 'L',
          bottomSize: '34',
        },
      },
      { uid: 'user-1', displayName: 'Neo', email: 'neo@example.com' }
    );

    expect(profile).toMatchObject({
      id: 'user-1',
      bodyType: 'Inverted Triangle',
      skinTone: 'skin_tone_82',
      height: '6 ft 1 in',
      weight: '190 lb',
      style_preferences: ['Classic', 'Minimalist'],
      color_preferences: ['navy', 'camel', 'burgundy'],
      size_preferences: ['L', '34'],
    });
  });

  it('enforces the required item in the returned outfit', () => {
    expect(() =>
      assertRequiredBaseItem({ baseItemId: 'shirt-1', items: [{ id: 'shirt-1' }] }, 'shirt-1')
    ).not.toThrow();

    expect(() =>
      assertRequiredBaseItem({ baseItemId: 'shirt-1', items: [{ id: 'pants-1' }] }, 'shirt-1')
    ).toThrow('did not include your selected wardrobe item');
  });

  it('preserves profile signals and rejects a base item outside the wardrobe', () => {
    const validator = DataValidator.getInstance();
    const validRequest = {
      occasion: 'Casual',
      style: 'Classic',
      mood: 'Confident',
      weather: { temperature: 72, condition: 'Clear' },
      wardrobe: [
        {
          id: 'shirt-1',
          name: 'Navy Oxford',
          type: 'SHIRT',
          color: 'navy',
        },
      ],
      user_profile: {
        id: 'user-1',
        gender: 'Non-binary',
        bodyType: 'Round/Apple',
        skinTone: 'skin_tone_82',
        stylePreferences: ['Classic'],
        style_preferences: ['Classic'],
        color_preferences: ['navy'],
      },
      baseItemId: 'shirt-1',
    };

    const validResult = validator.validateOutfitRequest(validRequest);
    expect(validResult.isValid).toBe(true);
    expect(validResult.sanitizedValue.user_profile).toMatchObject({
      gender: 'non-binary',
      bodyType: 'Round/Apple',
      skinTone: 'skin_tone_82',
      stylePreferences: ['Classic'],
    });

    const invalidResult = validator.validateOutfitRequest({
      ...validRequest,
      baseItemId: 'missing-item',
    });
    expect(invalidResult.isValid).toBe(false);
    expect(invalidResult.errors).toContain(
      'baseItemId must reference an item in the submitted wardrobe'
    );
  });

  it('commits the visible slider midpoint and preserves a custom value on return', () => {
    const defaulted = ensureDefaultSkinToneAnswer([], 'skin_tone');
    expect(defaulted).toEqual([
      { question_id: 'skin_tone', selected_option: 'skin_tone_50' },
    ]);

    const customized = upsertQuizAnswer(defaulted, 'skin_tone', 'skin_tone_82');
    const restored = ensureDefaultSkinToneAnswer(customized, 'skin_tone');

    expect(restored).toBe(customized);
    expect(restored[0].selected_option).toBe('skin_tone_82');
  });
});
