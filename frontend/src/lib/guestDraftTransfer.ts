import type { User } from 'firebase/auth';

const PENDING_QUIZ_KEY = 'pendingQuizSubmission';

/** Guest answers are never a completed profile and never replace an existing draft. */
export async function transferGuestDraftToNewAccount(
  user: Pick<User, 'getIdToken'>,
  isNewAccount: boolean,
  storage: Pick<Storage, 'getItem' | 'removeItem'> = sessionStorage,
): Promise<'none' | 'saved' | 'preserved'> {
  if (!isNewAccount) return 'preserved';
  const pending = storage.getItem(PENDING_QUIZ_KEY);
  if (!pending) return 'none';
  const parsed = JSON.parse(pending);
  if (!Array.isArray(parsed.answers) || !parsed.answers.length) throw new Error('Your guest answers could not be read. They have been kept on this device.');
  const token = await user.getIdToken();
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  const response = await fetch('/api/onboarding', { headers, cache: 'no-store' });
  if (!response.ok) throw new Error('Your account is ready, but your answers could not be saved. Please retry.');
  const loaded = await response.json();
  const state = loaded.state;
  if (loaded.success !== true || !state || !Number.isSafeInteger(state.revision)) throw new Error('Your saved progress could not be read. Please retry.');
  if (state.profileComplete || state.draft?.answers?.length) return 'preserved';
  const save = await fetch('/api/onboarding', { method: 'PATCH', headers, body: JSON.stringify({
    expectedRevision: state.revision,
    draft: { answers: parsed.answers, currentQuestionId: 'gender' },
  }) });
  if (!save.ok) throw new Error('Your account is ready, but your answers could not be saved. Please retry.');
  const acknowledgement = await save.json();
  const persisted = acknowledgement.state;
  if (acknowledgement.success !== true || !persisted) throw new Error('Your answers have not been confirmed as saved. Please retry.');
  if (typeof persisted.revision !== 'number' || persisted.revision <= state.revision || !Array.isArray(persisted.draft?.answers) ||
      parsed.answers.some((answer: any) => !persisted.draft.answers.some((saved: any) => saved.question_id === answer.question_id && saved.selected_option === answer.selected_option))) {
    throw new Error('Your answers have not been confirmed as saved. Please retry.');
  }
  storage.removeItem(PENDING_QUIZ_KEY);
  storage.removeItem('easyoutfit:onboarding:guest:v1');
  return 'saved';
}
