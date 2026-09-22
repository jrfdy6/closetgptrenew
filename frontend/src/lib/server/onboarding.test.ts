declare const expect: jest.Expect;
declare const it: jest.It;
import type { Firestore } from 'firebase-admin/firestore';
import { DraftRevisionConflict, readOnboardingState, reconcileOnboardingState, saveOnboardingDraft } from './onboarding';

function database(seed: Record<string, any> = {}) {
  const records = new Map(Object.entries(seed));
  const queries: string[] = [];
  const writes: string[] = [];
  let beforeCommit: (() => void) | undefined;
  const snapshot = (path: string) => ({ id: path.split('/').pop(), exists: records.has(path), data: () => records.get(path) });
  const db = {
    collection: (collection: string) => ({
      doc: (id: string) => ({ path: `${collection}/${id}`, get: async () => snapshot(`${collection}/${id}`) }),
      where: (field: string, _operator: string, value: string) => ({
        get: async () => {
          queries.push(collection);
          return { docs: Array.from(records.entries()).filter(([path, data]) => path.startsWith(`${collection}/`) && data[field] === value).map(([path]) => snapshot(path)) };
        },
      }),
    }),
    runTransaction: async (operation: (transaction: any) => Promise<any>) => {
      for (let attempt = 0; attempt < 3; attempt += 1) {
        const pending: Array<[string, any]> = [];
        const reads = new Map<string, string | undefined>();
        const result = await operation({
          get: async (reference: { path?: string; get: () => Promise<any> }) => {
            if (reference.path) reads.set(reference.path, JSON.stringify(records.get(reference.path)));
            return reference.get();
          },
          set: (reference: { path: string }, value: any) => pending.push([reference.path, value]),
        });
        const interrupt = beforeCommit;
        beforeCommit = undefined;
        interrupt?.();
        // Model Firestore's retry when a read document changes before commit.
        if (Array.from(reads).some(([path, value]) => JSON.stringify(records.get(path)) !== value)) continue;
        for (const [path, value] of pending) { records.set(path, value); writes.push(path); }
        return result;
      }
      throw new Error('transaction contention');
    },
  } as unknown as Firestore;
  return { db, records, queries, writes, beforeNextCommit: (callback: () => void) => { beforeCommit = callback; } };
}

const draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }], currentQuestionId: 'body_type_male' };

it('saves only the verified account draft and keeps each answer transaction small', async () => {
  const store = database();
  const acknowledged = await saveOnboardingDraft(store.db, 'owner', 0, draft);
  expect(acknowledged).toMatchObject({ revision: 1, draft });
  expect(store.records.get('onboarding_states/owner')).toMatchObject({ userId: 'owner', revision: 1, draft });
  expect(store.writes).toEqual(['onboarding_states/owner']);
  expect(store.queries).toEqual([]);
  expect(acknowledged).not.toHaveProperty('capsule');
});

it('rejects a second-device stale write without overwriting the first device', async () => {
  const store = database();
  await saveOnboardingDraft(store.db, 'owner', 0, draft);
  const staleDraft = { ...draft, answers: [{ question_id: 'gender', selected_option: 'Female' }] };
  await expect(saveOnboardingDraft(store.db, 'owner', 0, staleDraft)).rejects.toBeInstanceOf(DraftRevisionConflict);
  expect(store.records.get('onboarding_states/owner').draft).toEqual(draft);
  expect(store.writes).toHaveLength(1);
});

it('recovers a lost save acknowledgment without an extra revision or write', async () => {
  const store = database();
  const first = await saveOnboardingDraft(store.db, 'owner', 0, draft);
  const retry = await saveOnboardingDraft(store.db, 'owner', 0, draft);
  expect(retry).toEqual(first);
  expect(store.writes).toHaveLength(1);
});

it('reads both legacy ownership fields but excludes conflicting/foreign records', async () => {
  const store = database({
    'users/owner': { stylePersona: { name: 'Modernist' } },
    'wardrobe/top': { userId: 'owner', type: 'shirt', imageUrl: 'https://image.invalid/top' },
    'wardrobe/bottom': { user_id: 'owner', type: 'pants', imageUrl: 'https://image.invalid/bottom' },
    'wardrobe/shoes': { userId: 'owner', user_id: 'another', type: 'shoes', imageUrl: 'https://image.invalid/shoes' },
    'wardrobe/private': { userId: 'another', type: 'shoes', imageUrl: 'https://image.invalid/private' },
    'outfits/empty': { userId: 'owner', items: [] },
  });
  const state = await readOnboardingState(store.db, 'owner');
  expect(state).toMatchObject({ profileComplete: true, stage: 'capsule', capsule: { savedCount: 2, hasCoverage: false } });
  expect(store.writes).toEqual([]);
  expect(store.records.has('onboarding_states/owner')).toBe(false);
});

it('preserves protected completion history while allowing the next draft revision', async () => {
  const store = database({ 'onboarding_states/owner': { revision: 4, draft, milestones: { firstOutfitId: 'historic' } } });
  const next = await saveOnboardingDraft(store.db, 'owner', 4, { ...draft, currentQuestionId: 'skin_tone' });
  expect(next.milestones.firstOutfitId).toBe('historic');
  expect((await readOnboardingState(store.db, 'owner')).stage).toBe('complete');
});

it('promotes verified milestones once without changing draft revision and retains them after deletion', async () => {
  const garments = Array.from({ length: 10 }, (_, index) => ({ id: `item-${index}`, userId: 'owner',
    type: index === 0 ? 'pants' : index === 1 ? 'shoes' : 'shirt', imageUrl: `https://images.invalid/${index}` }));
  const store = database({
    'users/owner': { styleQuizCompletedAt: 1760000000 },
    'onboarding_states/owner': { revision: 4, draft },
    ...Object.fromEntries(garments.map(item => [`wardrobe/${item.id}`, item])),
    'outfits/first': { userId: 'owner', items: garments.slice(0, 3) },
  });
  const first = await reconcileOnboardingState(store.db, 'owner');
  expect(first).toMatchObject({ revision: 4, stage: 'complete', draft, milestones: { firstOutfitId: 'first' } });
  expect(first.milestones.styleCompletedAt).toBe('2025-10-09T08:53:20.000Z');
  expect(first.milestones.capsuleCompletedAt).toBeTruthy();
  await reconcileOnboardingState(store.db, 'owner');
  expect(store.writes).toHaveLength(1);
  garments.forEach(item => store.records.delete(`wardrobe/${item.id}`));
  store.records.delete('outfits/first');
  store.records.delete('users/owner');
  expect(await reconcileOnboardingState(store.db, 'owner')).toMatchObject({ stage: 'complete', capsule: { ready: false }, milestones: first.milestones });
  await saveOnboardingDraft(store.db, 'owner', 4, { ...draft, currentQuestionId: 'skin_tone' });
  expect(store.records.get('onboarding_states/owner').milestones).toEqual(first.milestones);
});

it('does not record completion from fake empty looks or client quiz-only flags', async () => {
  const store = database({ 'users/owner': { onboardingCompleted: true }, 'outfits/empty': { userId: 'owner', items: [] } });
  const state = await reconcileOnboardingState(store.db, 'owner');
  expect(state.stage).toBe('style');
  expect(store.writes).toEqual([]);
});

it('cannot bypass the full questionnaire by reconciling ten garments twice', async () => {
  const store = database(Object.fromEntries(Array.from({ length: 10 }, (_, index) => [`wardrobe/item-${index}`, {
    userId: 'owner', type: index === 0 ? 'pants' : index === 1 ? 'shoes' : 'shirt', imageUrl: `https://images.invalid/${index}`,
  }])));
  for (let count = 0; count < 2; count += 1) {
    expect(await reconcileOnboardingState(store.db, 'owner')).toMatchObject({ stage: 'style', profileComplete: false,
      capsule: { ready: true }, milestones: { capsuleCompletedAt: null } });
  }
  expect(store.writes).toEqual([]);
});

it('retries reconciliation around a concurrent draft commit without losing the newer answers', async () => {
  const newerDraft = { ...draft, currentQuestionId: 'skin_tone' };
  const store = database({ 'users/owner': { styleQuizCompletedAt: 1760000000 },
    'onboarding_states/owner': { revision: 1, draft } });
  store.beforeNextCommit(() => store.records.set('onboarding_states/owner', { revision: 2, draft: newerDraft }));
  const result = await reconcileOnboardingState(store.db, 'owner');
  expect(result).toMatchObject({ revision: 2, draft: newerDraft });
  expect(store.records.get('onboarding_states/owner')).toMatchObject({ revision: 2, draft: newerDraft,
    milestones: { styleCompletedAt: '2025-10-09T08:53:20.000Z' } });
});

it('retries a draft commit around concurrent milestone promotion without losing history', async () => {
  const store = database({ 'onboarding_states/owner': { revision: 1, draft } });
  store.beforeNextCommit(() => store.records.set('onboarding_states/owner', {
    revision: 1, draft, milestones: { firstOutfitId: 'saved-look' },
  }));
  const result = await saveOnboardingDraft(store.db, 'owner', 1, { ...draft, currentQuestionId: 'skin_tone' });
  expect(result).toMatchObject({ revision: 2, milestones: { firstOutfitId: 'saved-look' } });
});
