import type { User } from 'firebase/auth';
import { fullQuizQuestions, QUIZ_QUESTIONS } from '@/lib/onboarding/questions';
import { parseDraft } from '@/lib/onboarding/state';
import type { OnboardingDraft } from '@/lib/onboarding/types';
import { auth } from '@/lib/firebase/config';

const PENDING_QUIZ_KEY = 'pendingQuizSubmission';
const GUEST_DRAFT_KEY = 'easyoutfit:onboarding:guest:v1';
const transferKey = (uid: string) => `easyoutfit:onboarding:guest-transfer:${encodeURIComponent(uid)}:v1`;
type TransferStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;
type TransferUser = Pick<User, 'uid' | 'getIdToken'>;
interface GuestTransferReceipt {
  schemaVersion: 1;
  uid: string;
  pendingSnapshot: string;
  guestSnapshot: string | null;
  name?: string;
}

function readGuestDraft(raw: string): OnboardingDraft | null {
  try { return parseDraft({ answers: JSON.parse(raw)?.answers, currentQuestionId: null }); } catch { return null; }
}

export function getPendingGuestTransfer(uid: string, storage: Pick<Storage, 'getItem'> = sessionStorage): GuestTransferReceipt | null {
  try {
    const receipt = JSON.parse(storage.getItem(transferKey(uid)) || 'null');
    if (receipt?.schemaVersion !== 1 || receipt.uid !== uid || typeof receipt.pendingSnapshot !== 'string' ||
        !(receipt.guestSnapshot === null || typeof receipt.guestSnapshot === 'string') ||
        (receipt.name !== undefined && typeof receipt.name !== 'string') || !readGuestDraft(receipt.pendingSnapshot)?.answers.length) return null;
    return receipt;
  } catch { return null; }
}

export const hasPendingGuestTransfer = (uid: string) => !!getPendingGuestTransfer(uid);

/** Call only after the auth provider has confirmed this account was just created. */
export function authorizeNewAccountGuestTransfer(user: Pick<User, 'uid'>, name?: string, storage: TransferStorage = sessionStorage): GuestTransferReceipt | null {
  if (auth.currentUser?.uid !== user.uid) throw new Error('Your signed-in account changed. Your guest answers are still saved in this browser.');
  const existing = getPendingGuestTransfer(user.uid, storage);
  if (existing) return existing;
  const pendingSnapshot = storage.getItem(PENDING_QUIZ_KEY);
  if (!pendingSnapshot) return null;
  if (!readGuestDraft(pendingSnapshot)?.answers.length) throw new Error('Your guest answers could not be read. They have been kept on this device.');
  const receipt: GuestTransferReceipt = {
    schemaVersion: 1, uid: user.uid, pendingSnapshot, guestSnapshot: storage.getItem(GUEST_DRAFT_KEY),
    ...(name ? { name } : {}),
  };
  storage.setItem(transferKey(user.uid), JSON.stringify(receipt));
  return receipt;
}

function continuationQuestion(answers: OnboardingDraft['answers']): string {
  const gender = answers.find(answer => answer.question_id === 'gender')?.selected_option;
  if (!gender || !QUIZ_QUESTIONS.find(question => question.id === 'gender')?.options.includes(gender)) return 'gender';
  const questions = fullQuizQuestions(gender);
  return questions.find(question => !answers.some(answer => answer.question_id === question.id && answer.selected_option.trim()))?.id
    ?? questions[questions.length - 1]?.id
    ?? 'gender';
}

/** Guest answers are never a completed profile and never replace an existing draft. */
export async function transferGuestDraftToNewAccount(
  user: TransferUser,
  isNewAccount: boolean,
  storage: TransferStorage = sessionStorage,
): Promise<'none' | 'saved' | 'preserved'> {
  const receipt = isNewAccount ? authorizeNewAccountGuestTransfer(user, undefined, storage) : getPendingGuestTransfer(user.uid, storage);
  if (!receipt) return isNewAccount ? 'none' : 'preserved';
  const receiptSnapshot = storage.getItem(transferKey(user.uid));
  const assertCurrentUser = () => {
    if (auth.currentUser?.uid !== user.uid) throw new Error('Your signed-in account changed. Your guest answers are still saved in this browser.');
  };
  const clearReceipt = () => {
    if (storage.getItem(transferKey(user.uid)) === receiptSnapshot) storage.removeItem(transferKey(user.uid));
  };
  const draft = readGuestDraft(receipt.pendingSnapshot);
  if (!draft?.answers.length) throw new Error('Your guest answers could not be read. They have been kept on this device.');
  draft.currentQuestionId = continuationQuestion(draft.answers);
  assertCurrentUser();
  const token = await user.getIdToken();
  assertCurrentUser();
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  const response = await fetch('/api/onboarding', { headers, cache: 'no-store' });
  if (!response.ok) throw new Error('Your account is ready, but your answers could not be saved. Please retry.');
  const loaded = await response.json();
  const state = loaded.state;
  if (loaded.success !== true || !state || !Number.isSafeInteger(state.revision)) throw new Error('Your saved progress could not be read. Please retry.');
  assertCurrentUser();
  if (state.profileComplete || state.draft?.answers?.length) { clearReceipt(); return 'preserved'; }
  const save = await fetch('/api/onboarding', { method: 'PATCH', headers, body: JSON.stringify({
    expectedRevision: state.revision,
    draft,
  }) });
  if (!save.ok) throw new Error('Your account is ready, but your answers could not be saved. Please retry.');
  const acknowledgement = await save.json();
  const persisted = acknowledgement.state;
  if (acknowledgement.success !== true || !persisted) throw new Error('Your answers have not been confirmed as saved. Please retry.');
  if (!Number.isSafeInteger(persisted.revision) || persisted.revision <= state.revision || !Array.isArray(persisted.draft?.answers) ||
      persisted.draft.currentQuestionId !== draft.currentQuestionId ||
      draft.answers.some(answer => !persisted.draft.answers.some((saved: any) => saved.question_id === answer.question_id && saved.selected_option === answer.selected_option))) {
    throw new Error('Your answers have not been confirmed as saved. Please retry.');
  }
  assertCurrentUser();
  // The acknowledged write belongs to these snapshots. A newer guest edit may
  // have replaced either copy while the request was in flight; preserve both.
  if (storage.getItem(PENDING_QUIZ_KEY) === receipt.pendingSnapshot && storage.getItem(GUEST_DRAFT_KEY) === receipt.guestSnapshot) {
    storage.removeItem(PENDING_QUIZ_KEY);
    storage.removeItem(GUEST_DRAFT_KEY);
  }
  clearReceipt();
  return 'saved';
}
