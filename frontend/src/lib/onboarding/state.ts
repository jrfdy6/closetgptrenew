import type { CapsuleReadiness, OnboardingDraft, OnboardingState } from './types';

type RecordValue = Record<string, unknown>;
export type GarmentCategory = 'top' | 'bottom' | 'one-piece' | 'shoes' | 'layer' | 'accessory' | 'unknown';

const record = (value: unknown): RecordValue => value && typeof value === 'object' && !Array.isArray(value)
  ? value as RecordValue : {};
const text = (value: unknown): string => typeof value === 'string' ? value.trim() : '';
const categories: Array<[GarmentCategory, string[]]> = [
  ['one-piece', ['dress', 'dresses', 'shirtdress', 'shirt dress', 'sundress', 'cocktail dress', 'maxi dress', 'mini dress', 'jumpsuit', 'jumpsuits', 'romper', 'rompers', 'overalls', 'one piece', 'onepiece']],
  ['layer', ['layer', 'jacket', 'jackets', 'coat', 'coats', 'blazer', 'blazers', 'cardigan', 'cardigans', 'outerwear', 'vest', 'vests']],
  ['shoes', ['dress shoes', 'shoe', 'shoes', 'sneaker', 'sneakers', 'boot', 'boots', 'sandal', 'sandals', 'heel', 'heels', 'loafer', 'loafers', 'oxford', 'oxfords', 'flat', 'flats', 'footwear']],
  ['bottom', ['bottom', 'bottoms', 'pants', 'dress pants', 'chinos', 'slacks', 'joggers', 'sweatpants', 'mini skirt', 'midi skirt', 'maxi skirt', 'pencil skirt', 'trousers', 'jeans', 'shorts', 'skirt', 'skirts', 'leggings']],
  ['top', ['dress shirt', 'crop top', 'tee', 'top', 'tops', 'shirt', 'shirts', 'tshirt', 'tshirts', 't shirt', 't shirts', 'blouse', 'blouses', 'sweater', 'sweaters', 'hoodie', 'hoodies', 'sweatshirt', 'sweatshirts', 'knitwear', 'polo', 'tank', 'tank top']],
  ['accessory', ['accessory', 'accessories', 'bag', 'bags', 'belt', 'belts', 'hat', 'hats', 'scarf', 'scarves', 'jewelry', 'watch', 'sunglasses', 'tie']],
];

/** Uses explicit classification fields, never names/brands or gender stereotypes. */
export function classifyGarment(value: unknown): GarmentCategory {
  const item = record(value);
  const analysis = record(item.analysis);
  for (const raw of [item.type, item.category, analysis.type, analysis.category]) {
    const normalized = text(raw).toLowerCase().replace(/^clothingtype\./, '').replace(/[_-]+/g, ' ').replace(/\s+/g, ' ');
    for (const [category, labels] of categories) {
      if (labels.includes(normalized)) return category;
    }
  }
  return 'unknown';
}

export function hasOutfitCoverage(items: unknown[]): boolean {
  const found = new Set(items.map(classifyGarment));
  return found.has('shoes') && (found.has('one-piece') || (found.has('top') && found.has('bottom')));
}

function imageIdentities(item: RecordValue): string[] {
  return [item.contentHash, item.imageHash, item.image_hash].map(text).filter(Boolean).map(hash => `hash:${hash}`)
    .concat([item.originalImageUrl, item.imageUrl, item.image_url].map(text).filter(Boolean).map(url => `url:${url}`));
}

/** Profiles historically used Unix seconds; protected milestones use ISO dates. */
function timestamp(value: unknown): string | null {
  if (typeof value === 'string') return text(value) || null;
  let milliseconds: number | undefined;
  if (typeof value === 'number') milliseconds = value < 1e12 ? value * 1000 : value;
  else if (value instanceof Date) milliseconds = value.getTime();
  else if (typeof record(value).seconds === 'number') milliseconds = Number(record(value).seconds) * 1000;
  return milliseconds !== undefined && Number.isFinite(milliseconds) && !Number.isNaN(new Date(milliseconds).getTime())
    ? new Date(milliseconds).toISOString() : null;
}

export function evaluateCapsule(items: readonly unknown[]): CapsuleReadiness {
  const ids = new Set<string>();
  const images = new Set<string>();
  const usable: RecordValue[] = [];
  for (const value of items) {
    const item = record(value);
    const id = text(item.id);
    if (!id || ids.has(id) || item.deleted === true || item.isDeleted === true || item.deletedAt) continue;
    ids.add(id);
    const identities = imageIdentities(item);
    const original = text(item.imageUrl) || text(item.image_url) || text(item.originalImageUrl);
    if (!original || !identities.length || classifyGarment(item) === 'unknown') continue;
    const duplicate = identities.some(identity => images.has(identity));
    identities.forEach(identity => images.add(identity));
    if (duplicate) continue;
    usable.push(item);
  }
  const found = new Set(usable.map(classifyGarment));
  const hasCoverage = hasOutfitCoverage(usable);
  const missingCategories: string[] = [];
  if (!found.has('shoes')) missingCategories.push('shoes');
  if (!found.has('one-piece')) {
    if (!found.has('top')) missingCategories.push('top or one-piece');
    if (!found.has('bottom')) missingCategories.push('bottom or one-piece');
  }
  return { savedCount: ids.size, usableCount: usable.length, minimum: 10, hasCoverage,
    missingCategories, ready: usable.length >= 10 && hasCoverage };
}

/** Inspect persisted profile evidence, not defaults injected by authentication. */
export function hasStyleProfile(value: unknown): boolean {
  const profile = record(value);
  const persona = record(profile.stylePersona);
  const preferences = record(profile.preferences);
  return Boolean(profile.styleQuizCompletedAt || text(persona.id) || text(persona.name) ||
    text(profile.stylePersona) || [profile.stylePreferences, profile.style_preferences, preferences.style]
      .some(list => Array.isArray(list) && list.some(entry => text(entry))));
}

export function ownedBy(value: unknown, userId: string): boolean {
  const item = record(value);
  const owners = [text(item.userId), text(item.user_id)].filter(Boolean);
  return owners.length > 0 && owners.every(owner => owner === userId);
}

export function emptyDraft(): OnboardingDraft {
  return { answers: [], currentQuestionId: null };
}

export function parseDraft(value: unknown): OnboardingDraft | null {
  const draft = record(value);
  if (!Array.isArray(draft.answers) || draft.answers.length > 80 ||
    !(draft.currentQuestionId === null || (typeof draft.currentQuestionId === 'string' &&
      /^[a-z0-9_]{1,100}$/.test(draft.currentQuestionId)))) return null;
  const seen = new Set<string>();
  const answers: OnboardingDraft['answers'] = [];
  for (const value of draft.answers) {
    const answer = record(value);
    if (typeof answer.question_id !== 'string' || !/^[a-z0-9_]{1,100}$/.test(answer.question_id) ||
      typeof answer.selected_option !== 'string' || answer.selected_option.length > 2000 ||
      !answer.selected_option.trim() || seen.has(answer.question_id)) return null;
    seen.add(answer.question_id);
    answers.push({ question_id: answer.question_id, selected_option: answer.selected_option });
  }
  return { answers, currentQuestionId: draft.currentQuestionId as string | null };
}

export function deriveOnboardingState(input: {
  stored?: unknown; profile?: unknown; wardrobe: RecordValue[]; outfits: RecordValue[];
}): OnboardingState {
  const stored = record(input.stored);
  const profile = record(input.profile);
  const oldMilestones = record(stored.milestones);
  const capsule = evaluateCapsule(input.wardrobe);
  const wardrobe = new Map(input.wardrobe.map(item => [text(item.id), item]));
  // A real earlier look is historical evidence; empty dashboard rows never count.
  const firstLook = input.outfits.find(outfit => Array.isArray(outfit.items) &&
    hasOutfitCoverage(outfit.items.map(raw => {
      const item = typeof raw === 'string' ? { id: raw } : record(raw);
      return { ...record(wardrobe.get(text(item.id))), ...item };
    })));
  const firstOutfitId = text(oldMilestones.firstOutfitId) || text(firstLook?.id) || null;
  const profileComplete = hasStyleProfile(profile) || Boolean(oldMilestones.styleCompletedAt);
  // Old quiz-only flags are not capsule completion. Existing real looks and protected
  // milestones remain complete even when their owner later removes wardrobe items.
  const historicallyComplete = Boolean(firstOutfitId || oldMilestones.capsuleCompletedAt);
  const stage = firstOutfitId ? 'complete' : !profileComplete && !historicallyComplete ? 'style' :
    capsule.ready || historicallyComplete ? 'first-look' : 'capsule';
  return {
    schemaVersion: 1,
    revision: Number.isSafeInteger(stored.revision) && Number(stored.revision) >= 0 ? Number(stored.revision) : 0,
    draft: parseDraft(stored.draft) || emptyDraft(),
    profileComplete,
    capsule,
    stage,
    milestones: {
      styleCompletedAt: timestamp(oldMilestones.styleCompletedAt) || timestamp(profile.styleQuizCompletedAt),
      capsuleCompletedAt: timestamp(oldMilestones.capsuleCompletedAt),
      firstOutfitId,
    },
  };
}
