// Keep Jest types local; Cypress also declares global test functions.
declare const expect: jest.Expect;
declare const it: jest.It;

import { randomOutfitConfiguration } from './randomOutfitConfiguration';

const occasions = ['Casual', 'Business', 'Party', 'Date', 'Interview', 'Weekend', 'Loungewear', 'Gym'];
const styles = [
  'Dark Academia', 'Light Academia', 'Old Money', 'Y2K', 'Coastal Grandmother', 'Clean Girl', 'Cottagecore',
  'Avant-Garde', 'Artsy', 'Maximalist', 'Colorblock', 'Business Casual', 'Classic', 'Preppy', 'Urban Professional',
  'Streetwear', 'Techwear', 'Grunge', 'Hipster', 'Romantic', 'Boho', 'French Girl', 'Pinup',
  'Minimalist', 'Modern', 'Scandinavian', 'Monochrome', 'Gothic', 'Punk', 'Cyberpunk', 'Edgy',
  'Coastal Chic', 'Athleisure', 'Casual Cool', 'Loungewear', 'Workout',
];
const moods = ['Romantic', 'Playful', 'Serene', 'Dynamic', 'Bold', 'Subtle'];
const businessStyles = ['Classic', 'Business Casual', 'Preppy', 'Urban Professional', 'Minimalist', 'Old Money'];

it('keeps every selectable random pair within its occasion and available options', () => {
  // Enumerate enough evenly spaced values to reach every entry of each pool.
  const seen = new Set<string>();
  for (let occasionIndex = 0; occasionIndex < occasions.length; occasionIndex++) {
    for (let styleIndex = 0; styleIndex < styles.length; styleIndex++) {
      for (let moodIndex = 0; moodIndex < moods.length; moodIndex++) {
        const draws = [occasionIndex / occasions.length, styleIndex / styles.length, moodIndex / moods.length];
        const result = randomOutfitConfiguration({ occasions, styles, moods }, () => draws.shift()!);
        expect(result).not.toBeNull();
        expect(result!.occasion).toBe(occasions[occasionIndex]);
        expect(styles).toContain(result!.style);
        expect(result!.mood).toBe(moods[moodIndex]);
        if (result!.style === 'Workout') expect(result!.occasion).toBe('Gym');
        if (result!.style === 'Loungewear') expect(result!.occasion).toBe('Loungewear');
        if (['Business', 'Interview'].includes(result!.occasion)) expect(businessStyles).toContain(result!.style);
        if (result!.occasion === 'Gym') expect(['Workout', 'Athleisure']).toContain(result!.style);
        if (['Party', 'Date'].includes(result!.occasion)) {
          expect(['Workout', 'Loungewear', 'Athleisure']).not.toContain(result!.style);
        }
        seen.add(result!.occasion);
      }
    }
  }
  expect([...seen]).toEqual(occasions);
});

it.each([0, 1 - Number.EPSILON])('keeps the lower/upper valid random bound %s inside all pools', draw => {
  const result = randomOutfitConfiguration({ occasions, styles, moods }, () => draw);
  expect(occasions).toContain(result!.occasion);
  expect(styles).toContain(result!.style);
  expect(moods).toContain(result!.mood);
});

it('chooses occasion before style without weighting toward larger style pools', () => {
  const draws = [0.5, 0, 0];
  expect(randomOutfitConfiguration({
    occasions: ['Casual', 'Gym'], styles: ['Classic', 'Modern', 'Minimalist', 'Workout'], moods: ['Subtle'],
  }, () => draws.shift()!)).toEqual({ occasion: 'Gym', style: 'Workout', mood: 'Subtle' });
});

it.each([
  { available: ['Workout'], expectedOccasion: 'Gym' },
  { available: ['Loungewear'], expectedOccasion: 'Loungewear' },
])('respects restricted style availability: $available', ({ available, expectedOccasion }) => {
  const result = randomOutfitConfiguration({ occasions, styles: available, moods }, () => 0);
  expect(result!.occasion).toBe(expectedOccasion);
  expect(result!.style).toBe(available[0]);
});

it.each([
  { occasions: [], styles, moods },
  { occasions, styles: [], moods },
  { occasions, styles, moods: [] },
  { occasions: ['Party'], styles: ['Workout'], moods },
  { occasions: ['Unknown'], styles, moods },
])('does not manufacture an invalid combination from unavailable options: %j', options => {
  expect(randomOutfitConfiguration(options)).toBeNull();
});
