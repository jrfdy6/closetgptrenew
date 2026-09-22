declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { transferGuestDraftToNewAccount } from './guestDraftTransfer';
const answers = [{ question_id: 'gender', selected_option: 'Male' }];
const user = { getIdToken: jest.fn().mockResolvedValue('verified-token') };
const response = (body: unknown, ok = true) => ({ ok, json: async () => body });
beforeEach(() => { sessionStorage.clear(); sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers })); global.fetch = jest.fn(); });
it('never imports or clears guest answers on an existing-account sign in', async () => {
  expect(await transferGuestDraftToNewAccount(user, false)).toBe('preserved');
  expect(fetch).not.toHaveBeenCalled();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it('saves guest answers as a draft, using the real state envelope, and only clears on acknowledged persistence', async () => {
  (fetch as jest.Mock).mockResolvedValueOnce(response({ success: true, state: { revision: 0, draft: { answers: [] }, profileComplete: false } }))
    .mockResolvedValueOnce(response({ success: true, state: { revision: 1, draft: { answers, currentQuestionId: 'gender' } } }));
  expect(await transferGuestDraftToNewAccount(user, true)).toBe('saved');
  expect(fetch).toHaveBeenLastCalledWith('/api/onboarding', expect.objectContaining({ method: 'PATCH', body: JSON.stringify({ expectedRevision: 0, draft: { answers, currentQuestionId: 'gender' } }) }));
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBeNull();
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
it('keeps guest answers on a network failure', async () => {
  (fetch as jest.Mock).mockRejectedValue(new Error('offline'));
  await expect(transferGuestDraftToNewAccount(user, true)).rejects.toThrow();
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
