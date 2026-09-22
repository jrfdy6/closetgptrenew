declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { savePendingQuiz } from './pendingQuizSubmission';
import type { User } from 'firebase/auth';
const user = { uid: 'owner', getIdToken: async () => 'token' } as User;
beforeEach(() => { sessionStorage.clear(); sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: [] })); global.fetch = jest.fn(); });
it.each([503, 401, 422])('keeps answers and reports failure after HTTP %s', async status => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, status, json: async () => ({ success: false }) });
  await expect(savePendingQuiz(user)).rejects.toThrow('quiz has not been saved');
  expect(sessionStorage.getItem('pendingQuizSubmission')).not.toBeNull();
});
it.each([0, 9, 10])('only skips the capsule upload when %s items reaches ten', async count => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, wardrobeCount: count }) });
  await expect(savePendingQuiz(user)).resolves.toBe(count >= 10 ? '/style-persona?from=quiz' : '/onboarding?resume=uploads');
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBeNull();
});

it('keeps the authenticated quiz gender for capsule upload guidance', async () => {
  sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: [{ question_id: 'gender', selected_option: 'Female' }] }));
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, wardrobeCount: 0 }) });
  await savePendingQuiz(user);
  expect(JSON.parse(sessionStorage.getItem('capsuleUploadContext')!)).toEqual({ userId: 'owner', gender: 'Female' });
});
