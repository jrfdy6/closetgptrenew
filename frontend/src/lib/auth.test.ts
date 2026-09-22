declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { signUp, saveSignUpName, signInWithGoogle } from './auth';
import { createUserWithEmailAndPassword, updateProfile, signInWithPopup, getAdditionalUserInfo } from 'firebase/auth';
import type { User } from 'firebase/auth';
jest.mock('./firebase/config', () => ({ auth: {} }));
jest.mock('firebase/auth', () => ({ createUserWithEmailAndPassword: jest.fn(), updateProfile: jest.fn(), signInWithPopup: jest.fn(), getAdditionalUserInfo: jest.fn(), GoogleAuthProvider: jest.fn(() => ({ addScope: jest.fn() })) }));
const user = { uid: 'new-user', email: 'alex@example.test', getIdToken: jest.fn().mockResolvedValue('refreshed-token'), providerData: [{ providerId: 'password' }] } as unknown as User;
beforeEach(() => { jest.clearAllMocks(); (createUserWithEmailAndPassword as jest.Mock).mockResolvedValue({ user }); (updateProfile as jest.Mock).mockResolvedValue(undefined); global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ userId: user.uid, name: 'Alex Example' }) }); });
it('preserves the entered full name and refreshes the token before reporting signup ready', async () => {
  const result = await signUp('alex@example.test', 'test-password', '  Alex   Example  ');
  expect(result.success).toBe(true);
  expect(updateProfile).toHaveBeenCalledWith(user, { displayName: 'Alex Example' });
  expect(user.getIdToken).toHaveBeenCalledWith(true);
  expect(fetch).toHaveBeenCalledWith('/api/user/profile', expect.objectContaining({ method: 'POST', body: JSON.stringify({ name: 'Alex Example' }) }));
});
it('retains the created identity if saving the name fails so retry cannot create another account', async () => {
  (updateProfile as jest.Mock).mockRejectedValueOnce(new Error('offline'));
  expect(await signUp('alex@example.test', 'test-password', 'Alex Example')).toMatchObject({ success: true, user, profileError: expect.any(String) });
  await saveSignUpName(user, 'Alex Example');
  expect(createUserWithEmailAndPassword).toHaveBeenCalledTimes(1);
});
it('preserves callers which do not supply a display name', async () => {
  expect((await signUp('alex@example.test', 'test-password')).success).toBe(true);
  expect(updateProfile).not.toHaveBeenCalled();
});
it.each([true, false])('returns Firebase new-account evidence for Google sign-in: %s', async isNewUser => {
  (signInWithPopup as jest.Mock).mockResolvedValue({ user });
  (getAdditionalUserInfo as jest.Mock).mockReturnValue({ isNewUser });
  expect(await signInWithGoogle()).toMatchObject({ success: true, isNewUser });
});

it.each([{ ok: false }, { ok: true, json: async () => ({}) }])('retains the new identity when profile name persistence is not acknowledged', async response => {
  (fetch as jest.Mock).mockResolvedValueOnce(response);
  expect(await signUp('alex@example.test', 'test-password', 'Alex Example')).toMatchObject({ success: true, user, profileError: expect.any(String) });
  expect(createUserWithEmailAndPassword).toHaveBeenCalledTimes(1);
});
