declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { authorizeNewAccountGuestTransfer, getPendingGuestTransfer, transferGuestDraftToNewAccount } from './guestDraftTransfer';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import { auth } from '@/lib/firebase/config';
jest.mock('@/lib/firebase/config', () => ({ auth: { currentUser: null } }));
const answers = [{ question_id: 'gender', selected_option: 'Male' }];
const user = { uid: 'new-account', getIdToken: jest.fn().mockResolvedValue('verified-token') };
const mockAuth = auth as unknown as { currentUser: { uid: string } | null };
const response = (body: unknown, ok = true) => ({ ok, json: async () => body });
function acknowledgeDraft() {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] }, profileComplete: false } }))
    .mockImplementationOnce(async (_url, options) => response({ success: true, state: { revision: 1, draft: JSON.parse(options.body).draft } }));
}
const quizAnswers = (gender: string, guest = true) => fullQuizQuestions(gender, guest).map(question => ({
  question_id: question.id,
  selected_option: question.id === 'gender' ? gender : question.type === 'rgb_slider' ? 'skin_tone_50' : question.options[0],
}));
beforeEach(() => { mockAuth.currentUser = user; sessionStorage.clear(); sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers })); global.fetch = jest.fn(); });
it('never imports or clears guest answers on an existing-account sign in', async () => {
  expect(await transferGuestDraftToNewAccount(user, false)).toBe('preserved');
  expect(fetch).not.toHaveBeenCalled();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it('saves guest answers as a draft, using the real state envelope, and only clears on acknowledged persistence', async () => {
  sessionStorage.setItem('easyoutfit:onboarding:guest:v1', JSON.stringify({ draft: { answers } }));
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  expect(fetch).toHaveBeenLastCalledWith('/api/onboarding', expect.objectContaining({ method: 'PATCH', body: JSON.stringify({ expectedRevision: 0, draft: { answers, currentQuestionId: 'body_type_male' } }) }));
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBeNull();
  expect(sessionStorage.getItem('easyoutfit:onboarding:guest:v1')).toBeNull();
});
it.each(['Male', 'Female', 'Non-binary', 'Prefer not to say'])('continues a completed %s guest start at the first unanswered full question', async gender => {
  const started = quizAnswers(gender);
  sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: started }));
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  const saved = JSON.parse((fetch as jest.Mock).mock.calls[1][1].body);
  expect(saved).toEqual({ expectedRevision: 0, draft: { answers: started, currentQuestionId: 'height' } });
  expect(saved.draft.answers).toHaveLength(fullQuizQuestions(gender, true).length);
});
it('continues a partial guest draft at its first missing question without discarding later answers', async () => {
  const started = quizAnswers('Female').filter(answer => ['gender', 'body_type_female', 'style_elements'].includes(answer.question_id));
  sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: started }));
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  expect(JSON.parse((fetch as jest.Mock).mock.calls[1][1].body).draft).toEqual({ answers: started, currentQuestionId: 'skin_tone' });
});
it.each(['Male', 'Female', 'Non-binary', 'Prefer not to say'])('keeps a complete %s full draft at its final question for explicit review', async gender => {
  const completed = quizAnswers(gender, false);
  sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: completed }));
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  expect(JSON.parse((fetch as jest.Mock).mock.calls[1][1].body).draft).toEqual({ answers: completed, currentQuestionId: 'style_elements' });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect((fetch as jest.Mock).mock.calls.every(([url]) => url === '/api/onboarding')).toBe(true);
});
it.each([
  { started: [{ question_id: 'gender', selected_option: 'Unknown' }, { question_id: 'height', selected_option: 'Over 6\'3"' }] },
  { started: [{ question_id: 'height', selected_option: 'Over 6\'3"' }] },
])('returns an invalid or missing gender to its question while retaining the submitted answers', async ({ started }) => {
  sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: started }));
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  expect(JSON.parse((fetch as jest.Mock).mock.calls[1][1].body).draft).toEqual({ answers: started, currentQuestionId: 'gender' });
});
it.each([{ profileComplete: true, draft: { answers: [] } }, { profileComplete: false, draft: { answers } }])('preserves an existing style profile or draft: %j', async existing => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 3, ...existing } }));
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('preserved');
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it.each([response({}, false), response({ success: true }), response({ success: true, state: { revision: 1, draft: { answers: [] } } })])('keeps guest answers when save fails or does not acknowledge them', async failure => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] } } })).mockResolvedValueOnce(failure);
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it.each([
  { revision: 1, draft: { answers, currentQuestionId: 'gender' } },
  { revision: 0, draft: { answers, currentQuestionId: 'body_type_male' } },
  { revision: 0.5, draft: { answers, currentQuestionId: 'body_type_male' } },
])('keeps the browser copy when the save does not confirm the continuation pointer and revision: %j', async acknowledgement => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] } } }))
    .mockResolvedValueOnce(response({ success: true, state: acknowledgement }));
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow('Your answers have not been confirmed as saved');
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it.each(['not json', JSON.stringify({ answers: [{ question_id: 'gender', selected_option: null }] }), JSON.stringify({ answers: [...answers, ...answers] })])('keeps malformed guest work and does not send it: %s', async pending => {
  sessionStorage.setItem('pendingQuizSubmission', pending);
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow('Your guest answers could not be read');
  expect(fetch).not.toHaveBeenCalled();
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBe(pending);
});
it('keeps guest answers on a network failure', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('offline'));
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it('recovers an authorized transfer after a failed request using the same account, without new-account status', async () => {
  (fetch as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow('offline');
  expect(getPendingGuestTransfer(user.uid)?.uid).toBe(user.uid);
  acknowledgeDraft();
  expect(await transferGuestDraftToNewAccount(user, false)).toBe('saved');
  expect(getPendingGuestTransfer(user.uid)).toBeNull();
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBeNull();
});
it('binds recovery authorization to the newly created UID and retains it for that account', async () => {
  authorizeNewAccountGuestTransfer(user, 'Alex Example');
  const other = { ...user, uid: 'existing-account' };
  mockAuth.currentUser = other;
  expect(getPendingGuestTransfer(other.uid)).toBeNull();
  expect(await transferGuestDraftToNewAccount(other, false)).toBe('preserved');
  expect(fetch).not.toHaveBeenCalled();
  expect(getPendingGuestTransfer(user.uid)?.name).toBe('Alex Example');
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it.each(['pending', 'draft', 'both'])('preserves browser work changed in %s while the old PATCH acknowledgment is in flight', async changed => {
  const originalPending = sessionStorage.getItem('pendingQuizSubmission');
  const originalDraft = JSON.stringify({ draft: { answers } });
  sessionStorage.setItem('easyoutfit:onboarding:guest:v1', originalDraft);
  const newerAnswers = [{ question_id: 'gender', selected_option: 'Female' }];
  const nextPending = JSON.stringify({ answers: newerAnswers });
  const nextDraft = JSON.stringify({ draft: { answers: newerAnswers } });
  let acknowledge!: () => void;
  let started!: () => void;
  const patchStarted = new Promise<void>(resolve => { started = resolve; });
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] } } }))
    .mockImplementationOnce((_url, options) => new Promise(resolve => {
      acknowledge = () => resolve(response({ success: true, state: { revision: 1, draft: JSON.parse(options.body).draft } }));
      started();
    }));
  const transfer = transferGuestDraftToNewAccount(user, true);
  await patchStarted;
  if (changed !== 'draft') sessionStorage.setItem('pendingQuizSubmission', nextPending);
  if (changed !== 'pending') sessionStorage.setItem('easyoutfit:onboarding:guest:v1', nextDraft);
  acknowledge();
  expect(await transfer).toBe('saved');
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBe(changed === 'draft' ? originalPending : nextPending);
  expect(sessionStorage.getItem('easyoutfit:onboarding:guest:v1')).toBe(changed === 'pending' ? originalDraft : nextDraft);
});
it('preserves the receipt and browser work when the signed-in account changes before acknowledgment', async () => {
  let acknowledge!: () => void;
  let started!: () => void;
  const patchStarted = new Promise<void>(resolve => { started = resolve; });
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] } } }))
    .mockImplementationOnce((_url, options) => new Promise(resolve => {
      acknowledge = () => resolve(response({ success: true, state: { revision: 1, draft: JSON.parse(options.body).draft } }));
      started();
    }));
  const transfer = transferGuestDraftToNewAccount(user, true);
  await patchStarted;
  mockAuth.currentUser = { uid: 'another-account' };
  acknowledge();
  await expect(transfer).rejects.toThrow('Your signed-in account changed');
  expect(getPendingGuestTransfer(user.uid)).not.toBeNull();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
