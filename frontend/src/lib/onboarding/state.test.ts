declare const expect: jest.Expect;
declare const it: jest.It;
import { readFileSync } from 'fs';
import { join } from 'path';
import { classifyGarment, deriveOnboardingState, evaluateCapsule, hasOutfitCoverage, hasStyleProfile, ownedBy, parseDraft } from './state';

const fixtures = JSON.parse(readFileSync(join(process.cwd(), '../backend/tests/fixtures/onboarding-readiness-fixtures.json'), 'utf8'));
const item = (id: string, type: string, extra = {}) => ({ id, type, imageUrl: `https://images.invalid/${id}.jpg`, ...extra });
const capsule = [item('shirt', 'shirt'), item('pants', 'pants'), item('shoes', 'shoes'),
  ...Array.from({ length: 7 }, (_, index) => item(`extra-${index}`, 'shirt'))];

it.each(fixtures.aliases)('agrees with the backend alias contract for $type', ({ type, category }) => {
  expect(classifyGarment({ type })).toBe(category);
});

it.each(fixtures.combinations)('agrees with the backend coverage contract for $name', ({ items, hasCoverage, ready }) => {
  expect(hasOutfitCoverage(items)).toBe(hasCoverage);
  expect(evaluateCapsule(items).ready).toBe(ready);
});

it('counts persisted IDs separately from usable unique garment images', () => {
  const result = evaluateCapsule([...capsule, capsule[0], item('duplicate', 'shirt', { imageUrl: capsule[0].imageUrl }),
    item('unknown', 'other'), item('missing-image', 'shoes', { imageUrl: '' }), item('deleted', 'pants', { deleted: true })]);
  expect(result).toMatchObject({ savedCount: 13, usableCount: 10, ready: true });
});

it('deduplicates mixed hashed/unhashed photos and cutouts with the same original', () => {
  expect(evaluateCapsule([
    item('one', 'shirt', { contentHash: 'same-bytes' }),
    item('two', 'shirt', { imageUrl: 'https://images.invalid/one.jpg' }),
    item('three', 'shirt', { originalImageUrl: 'https://images.invalid/one.jpg', imageUrl: 'https://images.invalid/cutout.jpg' }),
    item('four', 'shirt', { imageUrl: 'https://images.invalid/cutout.jpg' }),
    item('five', 'shirt', { imageHash: 'same-bytes' }),
  ])).toMatchObject({ savedCount: 5, usableCount: 1 });
});

it.each([1760000000, 1760000000000, { seconds: 1760000000 }, new Date(1760000000000)])('normalizes persisted completion timestamps %j', value => {
  expect(deriveOnboardingState({ profile: { styleQuizCompletedAt: value }, wardrobe: [], outfits: [] }).milestones.styleCompletedAt)
    .toBe('2025-10-09T08:53:20.000Z');
});

it('does not block originals merely because cutout processing is pending or failed', () => {
  expect(evaluateCapsule(capsule.map(value => ({ ...value, processing_status: 'failed' }))).ready).toBe(true);
  expect(evaluateCapsule(capsule.map(value => ({ ...value, processing_status: 'pending' }))).ready).toBe(true);
});

it('requires ten usable items and actual coverage, allowing a one-piece', () => {
  expect(evaluateCapsule(capsule.slice(0, 9)).ready).toBe(false);
  expect(evaluateCapsule(capsule.map(value => ({ ...value, type: 'shirt' })))).toMatchObject({ ready: false, hasCoverage: false });
  const onePiece = [item('dress', 'maxi_dress'), item('dress-shoes', 'dress_shoes'), ...capsule.slice(2)];
  expect(evaluateCapsule(onePiece).ready).toBe(true);
});

it('uses explicit categories and nested analysis, not a garment name or guessed default', () => {
  expect(classifyGarment({ type: 'unknown', analysis: { type: 't-shirt' } })).toBe('top');
  expect(classifyGarment({ name: 'T shirt dress shoes', type: 'other' })).toBe('unknown');
  expect(hasStyleProfile({ gender: 'male', measurements: {} })).toBe(false);
  expect(hasStyleProfile({ stylePersona: { name: 'Modernist' } })).toBe(true);
});

it('resolves new, partial, ready and returning legacy stages from saved evidence', () => {
  expect(deriveOnboardingState({ wardrobe: [], outfits: [] }).stage).toBe('style');
  const profile = { stylePreferences: ['Minimalist'] };
  expect(deriveOnboardingState({ profile, wardrobe: capsule.slice(0, 9), outfits: [] }).stage).toBe('capsule');
  expect(deriveOnboardingState({ profile, wardrobe: capsule, outfits: [] }).stage).toBe('first-look');
  expect(deriveOnboardingState({ profile, wardrobe: [], outfits: [{ id: 'real-look', items: capsule.slice(0, 3) }] }).stage).toBe('complete');
  expect(deriveOnboardingState({ profile, wardrobe: [], outfits: Array.from({ length: 22 }, (_, id) => ({ id, items: [] })) }).stage).toBe('capsule');
});

it('retains historical completion when garments are later removed', () => {
  const state = deriveOnboardingState({ stored: { revision: 9, milestones: { firstOutfitId: 'earlier-look' } }, wardrobe: [], outfits: [] });
  expect(state.stage).toBe('complete');
  expect(state.capsule.ready).toBe(false);
  expect(state.milestones.firstOutfitId).toBe('earlier-look');
});

it('rejects owner aliases that disagree and validates bounded draft input', () => {
  expect(ownedBy({ userId: 'one', user_id: 'two' }, 'one')).toBe(false);
  expect(ownedBy({ user_id: 'one' }, 'one')).toBe(true);
  const answer = { question_id: 'gender', selected_option: 'Male' };
  expect(parseDraft({ answers: [answer], currentQuestionId: 'skin_tone' })).toEqual({ answers: [answer], currentQuestionId: 'skin_tone' });
  expect(parseDraft({ answers: [answer, answer], currentQuestionId: 'gender' })).toBeNull();
  expect(parseDraft({ answers: [], currentQuestionId: '../other-account' })).toBeNull();
});
