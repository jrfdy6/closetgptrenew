import type { Firestore } from 'firebase-admin/firestore';
import { deriveOnboardingState, ownedBy } from '@/lib/onboarding/state';
import type { OnboardingDraft, OnboardingDraftState, OnboardingState } from '@/lib/onboarding/types';

// Unlike users/{uid}, this collection is not client-writable. Draft revisions and
// milestones can only be changed through verified server requests.
export const ONBOARDING_COLLECTION = 'onboarding_states';

export class DraftRevisionConflict extends Error {
  constructor(public state: OnboardingDraftState) {
    super('Your questionnaire changed in another session. Load the newer draft before saving.');
  }
}

async function sources(db: Firestore, userId: string, read: (reference: any) => Promise<any> = reference => reference.get()) {
  const ownedRecords = async (collection: string): Promise<Array<Record<string, unknown>>> => {
    const snapshots = await Promise.all(['userId', 'user_id'].map(field =>
      read(db.collection(collection).where(field, '==', userId))));
    const rows = new Map<string, Record<string, unknown>>();
    for (const snapshot of snapshots) {
      for (const document of snapshot.docs) {
        const data = document.data();
        if (ownedBy(data, userId)) rows.set(document.id, { ...data, id: document.id });
      }
    }
    return Array.from(rows.values());
  };
  const [draft, profile, wardrobe, outfits] = await Promise.all([
    read(db.collection(ONBOARDING_COLLECTION).doc(userId)),
    read(db.collection('users').doc(userId)),
    ownedRecords('wardrobe'),
    ownedRecords('outfits'),
  ]);
  return { stored: draft.exists ? draft.data() : {}, profile: profile.exists ? profile.data() : {}, wardrobe, outfits };
}

export async function readOnboardingState(db: Firestore, userId: string): Promise<OnboardingState> {
  return deriveOnboardingState(await sources(db, userId));
}

/** Records verified progress, without accepting client-supplied counts or milestones. */
export async function reconcileOnboardingState(db: Firestore, userId: string): Promise<OnboardingState> {
  return db.runTransaction(async transaction => {
    const data = await sources(db, userId, reference => transaction.get(reference));
    const state = deriveOnboardingState(data);
    const stored = data.stored || {};
    const now = new Date().toISOString();
    const milestones = {
      ...state.milestones,
      styleCompletedAt: state.milestones.styleCompletedAt || (state.profileComplete ? now : null),
      capsuleCompletedAt: state.milestones.capsuleCompletedAt || (state.profileComplete && state.capsule.ready ? now : null),
    };
    const previous = stored.milestones || {};
    if (Object.keys(milestones).some(key => milestones[key as keyof typeof milestones] &&
      milestones[key as keyof typeof milestones] !== previous[key])) {
      transaction.set(db.collection(ONBOARDING_COLLECTION).doc(userId), {
        ...stored, schemaVersion: 1, userId, revision: state.revision, draft: state.draft, milestones, updatedAt: now,
      });
    }
    return { ...state, milestones };
  });
}

export async function saveOnboardingDraft(
  db: Firestore, userId: string, expectedRevision: number, draft: OnboardingDraft,
): Promise<OnboardingDraftState> {
  return db.runTransaction(async transaction => {
    const reference = db.collection(ONBOARDING_COLLECTION).doc(userId);
    const snapshot = await transaction.get(reference);
    const state = deriveOnboardingState({ stored: snapshot.exists ? snapshot.data() : {}, wardrobe: [], outfits: [] });
    const acknowledged = { schemaVersion: state.schemaVersion, revision: state.revision, draft: state.draft, milestones: state.milestones };
    // Recover a committed write whose response was lost without another revision.
    if (state.revision === expectedRevision + 1 && JSON.stringify(state.draft) === JSON.stringify(draft)) return acknowledged;
    if (state.revision !== expectedRevision) throw new DraftRevisionConflict(acknowledged);
    const now = new Date().toISOString();
    const next: OnboardingDraftState = {
      schemaVersion: 1,
      revision: state.revision + 1,
      draft,
      milestones: state.milestones,
    };
    transaction.set(reference, {
      schemaVersion: 1,
      userId,
      revision: next.revision,
      draft,
      milestones: next.milestones,
      updatedAt: now,
    });
    return next;
  });
}
