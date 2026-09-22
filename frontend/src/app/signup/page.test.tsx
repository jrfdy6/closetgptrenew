declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import SignUp from './page';
import { signUp, signInWithGoogle, saveSignUpName } from '@/lib/auth';
import { transferGuestDraftToNewAccount } from '@/lib/guestDraftTransfer';
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock('@/lib/auth', () => ({ signUp: jest.fn(), signInWithGoogle: jest.fn(), saveSignUpName: jest.fn() }));
jest.mock('@/lib/guestDraftTransfer', () => ({ transferGuestDraftToNewAccount: jest.fn() }));
const user = { uid: 'new-account', email: 'alex@example.test' };
beforeEach(() => { jest.clearAllMocks(); window.history.replaceState({}, '', '/signup?from=quiz'); (transferGuestDraftToNewAccount as jest.Mock).mockResolvedValue('saved'); });
function fillForm() {
  fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Alex' } });
  fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Example' } });
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alex@example.test' } });
  fireEvent.change(screen.getByLabelText('Password', { exact: true }), { target: { value: 'test-password' } });
  fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'test-password' } });
}
it('passes the full entered name and continues the full questionnaire after guest draft persistence', async () => {
  (signUp as jest.Mock).mockResolvedValue({ success: true, user });
  render(<SignUp />); fillForm(); fireEvent.click(screen.getByRole('button', { name: 'Create account' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(signUp).toHaveBeenCalledWith('alex@example.test', 'test-password', 'Alex Example');
  expect(transferGuestDraftToNewAccount).toHaveBeenCalledWith(user, true);
});
it('keeps a created account retryable when draft transfer fails instead of creating it again or showing completion', async () => {
  (signUp as jest.Mock).mockResolvedValue({ success: true, user });
  (transferGuestDraftToNewAccount as jest.Mock).mockRejectedValueOnce(new Error('Your answers could not be saved. Please retry.')).mockResolvedValueOnce('saved');
  render(<SignUp />); fillForm(); fireEvent.click(screen.getByRole('button', { name: 'Create account' }));
  await screen.findByText('Your answers could not be saved. Please retry.');
  expect(mockPush).not.toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Create account' })).toBeDisabled();
  fireEvent.click(screen.getByRole('button', { name: 'Retry setup' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(signUp).toHaveBeenCalledTimes(1);
  expect(saveSignUpName).toHaveBeenCalledWith(user, 'Alex Example');
});
it('retries a failed name save on the existing new identity', async () => {
  (signUp as jest.Mock).mockResolvedValue({ success: true, user, profileError: 'Name not saved. Please retry.' });
  render(<SignUp />); fillForm(); fireEvent.click(screen.getByRole('button', { name: 'Create account' }));
  await screen.findByText('Name not saved. Please retry.');
  expect(transferGuestDraftToNewAccount).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Retry setup' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(signUp).toHaveBeenCalledTimes(1);
});
it('does not treat an existing Google account as a new account', async () => {
  (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, isNewUser: false });
  render(<SignUp />); fireEvent.click(screen.getByRole('button', { name: 'Sign up with Google' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(transferGuestDraftToNewAccount).toHaveBeenCalledWith(user, false);
});
