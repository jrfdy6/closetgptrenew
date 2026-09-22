declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import SignIn from './page';
import { signIn, signInWithGoogle } from '@/lib/auth';
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock('@/lib/auth', () => ({ signIn: jest.fn(), signInWithGoogle: jest.fn() }));
jest.mock('@/components/PasswordLinkPrompt', () => ({
  __esModule: true,
  default: ({ open, onClose, onSuccess }: { open: boolean; onClose: () => void; onSuccess: () => void }) => open ? (
    <div>
      <button onClick={onClose}>Continue without linking</button>
      <button onClick={onSuccess}>Complete password linking</button>
    </div>
  ) : null,
}));
jest.mock('@/components/PasswordLinkBanner', () => ({ __esModule: true, default: () => null }));
const user = { uid: 'existing-account', email: 'alex@example.test' };
beforeEach(() => { jest.clearAllMocks(); window.history.replaceState({}, '', '/signin?from=quiz'); sessionStorage.setItem('pendingQuizSubmission', 'guest-answers'); global.fetch = jest.fn(); });
it('signs in without submitting or clearing guest quiz answers', async () => {
  (signIn as jest.Mock).mockResolvedValue({ success: true, user });
  render(<SignIn />);
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alex@example.test' } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'test-password' } });
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(fetch).not.toHaveBeenCalled();
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBe('guest-answers');
});
it('Google sign-in cannot auto-submit guest answers either', async () => {
  (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, needsPasswordLinking: false });
  render(<SignIn />); fireEvent.click(screen.getByRole('button', { name: 'Sign in with Google' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
  expect(fetch).not.toHaveBeenCalled();
  expect(sessionStorage.getItem('pendingQuizSubmission')).toBe('guest-answers');
});

function visitSignIn(redirect?: string, fromQuiz = false) {
  const params = new URLSearchParams();
  if (redirect !== undefined) params.set('redirect', redirect);
  if (fromQuiz) params.set('from', 'quiz');
  window.history.replaceState({}, '', '/signin?' + params.toString());
  render(<SignIn />);
}

function submitEmail() {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alex@example.test' } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'test-password' } });
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
}

it('returns email sign-in to the exact requested saved outfit', async () => {
  (signIn as jest.Mock).mockResolvedValue({ success: true, user });
  visitSignIn('/outfits/outfit_83026d8df9244fa5982febd7d4c76b5b');
  submitEmail();
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/outfit_83026d8df9244fa5982febd7d4c76b5b'));
  expect(signIn).toHaveBeenCalledWith('alex@example.test', 'test-password');
  expect(fetch).not.toHaveBeenCalled();
});

it('returns Google sign-in to the requested saved outfit', async () => {
  (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, needsPasswordLinking: false });
  visitSignIn('/outfits/saved-look-123');
  fireEvent.click(screen.getByRole('button', { name: 'Sign in with Google' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/saved-look-123'));
  expect(signInWithGoogle).toHaveBeenCalledTimes(1);
});

it.each(['Complete password linking', 'Continue without linking'])(
  'preserves the saved outfit return when choosing %s after Google sign-in', async (action) => {
    (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, needsPasswordLinking: true });
    visitSignIn('/outfits/saved-look-123');
    fireEvent.click(screen.getByRole('button', { name: 'Sign in with Google' }));
    fireEvent.click(await screen.findByRole('button', { name: action }));
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/saved-look-123'));
  },
);

it.each(['email', 'Google', 'linked', 'skip'])(
  'retains quiz precedence over the saved outfit redirect for %s sign-in', async (method) => {
    (signIn as jest.Mock).mockResolvedValue({ success: true, user });
    (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, needsPasswordLinking: method === 'linked' || method === 'skip' });
    visitSignIn('/outfits/saved-look-123', true);
    if (method === 'email') submitEmail();
    else {
      fireEvent.click(screen.getByRole('button', { name: 'Sign in with Google' }));
      if (method === 'linked' || method === 'skip') {
        fireEvent.click(await screen.findByRole('button', { name: method === 'linked' ? 'Complete password linking' : 'Continue without linking' }));
      }
    }
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/onboarding'));
    expect(mockPush).not.toHaveBeenCalledWith('/outfits/saved-look-123');
    expect(fetch).not.toHaveBeenCalled();
    expect(sessionStorage.getItem('pendingQuizSubmission')).toBe('guest-answers');
  },
);

it.each(['email', 'Google'])(
  'falls back to dashboard for unsafe or non-detail redirects after %s sign-in', async (method) => {
    (signIn as jest.Mock).mockResolvedValue({ success: true, user });
    (signInWithGoogle as jest.Mock).mockResolvedValue({ success: true, user, needsPasswordLinking: false });
    const invalid = [undefined, '', 'https://outside.test/outfits/id', '//outside.test/outfits/id',
      'javascript:alert(1)', '/\\outside.test/outfits/id', '/outfits/one\\two', '/outfits/id\n',
      '/outfits/\u0000id', '/outfits/id\t', '/outfits/%2f%2foutside.test', '/outfits/%5coutside.test',
      '/outfits/../dashboard', '/outfits/..', '/outfits/id/extra', '/outfits/id?next=outside',
      '/outfits/id#fragment', '/outfits/generate', '/outfits/create', '/profile'];
    for (const redirect of invalid) {
      mockPush.mockClear();
      visitSignIn(redirect);
      if (method === 'email') submitEmail();
      else fireEvent.click(screen.getByRole('button', { name: 'Sign in with Google' }));
      await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/dashboard'));
      expect(mockPush).toHaveBeenCalledTimes(1);
      cleanup();
    }
  },
);

it('does not follow a return destination when sign-in fails', async () => {
  (signIn as jest.Mock).mockResolvedValue({ success: false, error: 'Invalid credentials' });
  visitSignIn('/outfits/saved-look-123');
  submitEmail();
  await screen.findByText('Invalid credentials');
  expect(mockPush).not.toHaveBeenCalled();
});
