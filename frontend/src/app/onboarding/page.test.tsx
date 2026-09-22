declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen, within } from '@testing-library/react';
import Onboarding from './page';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import type { OnboardingState } from '@/lib/onboarding/types';
jest.mock('next/image', () => ({ __esModule: true, default: ({ fill, unoptimized, ...props }: { fill?: boolean; unoptimized?: boolean } & React.ImgHTMLAttributes<HTMLImageElement>) => <img {...props} /> }));
const mockUser = { uid: 'qa-user', getIdToken: jest.fn(async () => 'quiz-test-token') };
const mockRouter = { push: jest.fn(), replace: jest.fn() };
jest.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false, getIdToken: mockUser.getIdToken }) }));
jest.mock('@/components/BodyPositiveMessage', () => ({ __esModule: true, default: () => null }));
let mockOnComplete: (count: number) => void | Promise<void>;
jest.mock('@/components/GuidedUploadWizard', () => ({ __esModule: true, default: ({ targetCount, onComplete }: { targetCount: number; onComplete: (count: number) => void | Promise<void> }) => { mockOnComplete = onComplete; return <div data-testid="capsule-target">{targetCount}<button onClick={() => void onComplete(10)}>Finish capsule</button></div>; } }));
const mockWardrobe = jest.fn();
jest.mock('@/lib/services/wardrobeService', () => ({ WardrobeService: { getWardrobeItems: () => mockWardrobe() } }));
const mockPendingTransfer = jest.fn((_uid?: string) => false);
jest.mock('@/lib/guestDraftTransfer', () => ({ hasPendingGuestTransfer: (uid: string) => mockPendingTransfer(uid) }));
let state: OnboardingState;
let originalFetch: typeof fetch;
let mockFetch: jest.Mock;
let submitSuccess: boolean;
beforeEach(() => {
  jest.useFakeTimers(); window.history.replaceState({}, '', '/onboarding'); sessionStorage.clear();
  mockRouter.push.mockClear(); mockRouter.replace.mockClear();
  originalFetch = globalThis.fetch; submitSuccess = true; mockPendingTransfer.mockReturnValue(false);
  mockWardrobe.mockReset(); mockWardrobe.mockResolvedValue(Array.from({ length: 10 }, (_, index) => ({ id: `item-${index}`, userId: mockUser.uid, type: index === 0 ? 'shoes' : index === 1 ? 'pants' : 'shirt', name: `My garment ${index}`, imageUrl: `/image-${index}.jpg` })));
  state = { schemaVersion: 1, revision: 0, profileComplete: false, stage: 'style', draft: { answers: [], currentQuestionId: 'gender' }, capsule: { savedCount: 9, usableCount: 9, minimum: 10, hasCoverage: true, missingCategories: [], ready: false }, milestones: { styleCompletedAt: null, capsuleCompletedAt: null, firstOutfitId: null } };
  mockFetch = jest.fn(async (url, options) => {
    if (url === '/api/style-quiz/submit') {
      if (submitSuccess) state = { ...state, profileComplete: true, stage: 'capsule' };
      return { ok: true, json: async () => ({ success: submitSuccess }) };
    }
    if (url !== '/api/onboarding') throw new Error(`Unexpected ${url}`);
    if (options?.method === 'PATCH') state = { ...state, draft: JSON.parse(options.body).draft, revision: state.revision + 1 };
    return { ok: true, json: async () => ({ success: true, state }) };
  }); globalThis.fetch = mockFetch;
});
afterEach(() => { jest.clearAllTimers(); jest.useRealTimers(); globalThis.fetch = originalFetch; });
const renderPage = async () => { await act(async () => { render(<Onboarding />); }); };
const advanceTimer = async (ms = 300) => act(async () => { jest.advanceTimersByTime(ms); });
const choose = (name: string) => fireEvent.click(screen.getByRole('button', { name }));
const completeQuiz = async (count = 25) => {
  choose('Male'); choose('Next');
  for (let question = 2; question <= count; question += 1) {
    expect(screen.getByText(`Question ${question} of ${count}`)).toBeVisible();
    if (!screen.queryByRole('slider', { name: 'Skin tone depth' })) fireEvent.click(within(screen.getByRole('group')).getAllByRole('button')[0]);
    if (question < count) choose('Next');
  }
};
it('keeps selection until explicit Next, then focuses the requested question', async () => {
  await renderPage(); choose('Male');
  expect(screen.getByRole('button', { name: 'Male' })).toHaveAttribute('aria-pressed', 'true');
  await advanceTimer(1000); expect(screen.getByText('Getting started')).toBeVisible();
  choose('Next'); expect(screen.getByText('Question 2 of 25')).toBeVisible();
  expect(screen.getByRole('heading', { name: /Which body shape/ })).toHaveFocus();
  choose('Rectangle'); choose('Next'); await advanceTimer(1000);
  expect(screen.getByText('Question 3 of 25')).toBeVisible();
  expect(screen.getByRole('slider', { name: 'Skin tone depth' })).toBeVisible();
});
it('changing a choice exposes the current selection without skipping a question', async () => {
  await renderPage(); choose('Male'); choose('Next');
  choose('Rectangle'); choose('Oval'); await advanceTimer(1000);
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Oval' })).toHaveAttribute('aria-pressed', 'true');
  expect(screen.getByRole('button', { name: 'Rectangle' })).toHaveAttribute('aria-pressed', 'false');
  choose('Previous'); await advanceTimer(1000); expect(screen.getByText('Getting started')).toBeVisible();
});
it('restores the saved question and answer', async () => {
  state.draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }, { question_id: 'body_type_male', selected_option: 'Oval' }], currentQuestionId: 'body_type_male' };
  await renderPage(); expect(screen.getByText('Question 2 of 25')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Oval' })).toHaveAttribute('aria-pressed', 'true');
  expect(mockFetch).toHaveBeenCalledTimes(1);
});
it('starts the ten-item capsule only after persistence and authoritative readiness', async () => {
  await renderPage(); await completeQuiz();
  await act(async () => { choose('Save my style & continue'); });
  const call = mockFetch.mock.calls.find(([url]) => url === '/api/style-quiz/submit');
  expect(JSON.parse(call![1].body).answers).toHaveLength(25);
  expect(JSON.parse(call![1].body).retake).toBeUndefined();
  expect(mockFetch).not.toHaveBeenCalledWith('/api/user/profile', expect.anything());
  expect(screen.getByTestId('capsule-target')).toHaveTextContent('10');
});
it('keeps the question and real answers when submit reports failure, then allows retry', async () => {
  submitSuccess = false; await renderPage(); await completeQuiz();
  await act(async () => { choose('Save my style & continue'); });
  expect(screen.queryByTestId('capsule-target')).not.toBeInTheDocument();
  expect(screen.getByText('Question 25 of 25')).toBeVisible();
  expect(screen.getByRole('alert')).toHaveTextContent('Failed to save');
  expect(state.draft.answers).toHaveLength(25);
  submitSuccess = true;
  await act(async () => { choose('Save my style & continue'); });
  expect(screen.getByTestId('capsule-target')).toBeVisible();
});
it('never reads or writes the signed-in account during an explicit guest quiz', async () => {
  window.history.replaceState({}, '', '/onboarding?mode=guest');
  await renderPage();
  expect(screen.getByText(/finish the remaining fit and wardrobe questions/)).toBeVisible();
  await completeQuiz(13);
  await act(async () => { choose('Save my start & continue'); });
  expect(mockFetch).not.toHaveBeenCalled();
  expect(JSON.parse(sessionStorage.getItem('pendingQuizSubmission')!).answers).toHaveLength(13);
  expect(mockRouter.replace).toHaveBeenCalledWith('/finish-profile?from=quiz');
});
it('requires an explicit retake before exposing the quiz for an existing profile', async () => {
  state.profileComplete = true; state.stage = 'capsule'; await renderPage();
  expect(screen.getByText('Your style profile is saved')).toBeVisible();
  expect(screen.queryByText('What is your gender?')).not.toBeInTheDocument();
  choose('Retake my style quiz'); await completeQuiz();
  await act(async () => { choose('Save my style & continue'); });
  const call = mockFetch.mock.calls.find(([url]) => url === '/api/style-quiz/submit');
  expect(JSON.parse(call![1].body).retake).toBe(true);
});
it.each([['Male', 25], ['Female', 27], ['Non-binary', 35], ['Prefer not to say', 35]])('preserves the full %s question sequence', (gender, count) => {
  const questions = fullQuizQuestions(String(gender));
  expect(questions).toHaveLength(Number(count));
  expect(questions[0].id).toBe('gender');
  expect(questions[questions.length - 1].id).toBe('style_elements');
  expect(new Set(questions.map(question => question.id)).size).toBe(count);
});


it('holds the quiz behind a retryable loading error instead of assuming empty progress', async () => {
  mockFetch.mockRejectedValueOnce(new Error('Progress is temporarily unavailable'));
  await renderPage();
  expect(screen.getByRole('alert')).toHaveTextContent('Progress is temporarily unavailable');
  expect(screen.queryByText('What is your gender?')).not.toBeInTheDocument();
  await act(async () => { choose('Retry loading progress'); });
  expect(screen.getByText('What is your gender?')).toBeVisible();
});

it('retries next-step loading without submitting a successfully saved profile twice', async () => {
  const implementation = mockFetch.getMockImplementation()!;
  let failNextStep = true;
  mockFetch.mockImplementation(async (url, options) => {
    if (url === '/api/onboarding' && options?.method !== 'PATCH' && state.profileComplete && failNextStep) {
      failNextStep = false;
      throw new Error('Temporarily offline');
    }
    return implementation(url, options);
  });
  await renderPage(); await completeQuiz();
  await act(async () => { choose('Save my style & continue'); });
  expect(screen.queryByTestId('capsule-target')).not.toBeInTheDocument();
  expect(screen.getByText('Question 25 of 25')).toBeVisible();
  await act(async () => { choose('Save my style & continue'); });
  expect(screen.getByTestId('capsule-target')).toBeVisible();
  expect(mockFetch.mock.calls.filter(([url]) => url === '/api/style-quiz/submit')).toHaveLength(1);
});

it('shows a ready recap with actual photos and an explicit configuration link', async () => {
  state.profileComplete = true; state.stage = 'first-look'; state.capsule = { ...state.capsule, usableCount: 10, savedCount: 10, ready: true };
  state.draft.answers = [{ question_id: 'gender', selected_option: 'Male' }, { question_id: 'style_item_m_3', selected_option: 'Yes' }, { question_id: 'daily_activities', selected_option: 'Mix of everything' }];
  await renderPage();
  expect(screen.getByText('10 unique usable pieces saved')).toBeVisible();
  expect(screen.getByAltText('My garment 0')).toBeVisible();
  expect(screen.getByText('Minimalist')).toBeVisible();
  expect(screen.getByRole('link', { name: 'Create my first outfit' })).toHaveAttribute('href', '/outfits/generate?onboarding=1');
  expect(mockRouter.push).not.toHaveBeenCalled(); expect(mockRouter.replace).not.toHaveBeenCalled();
  expect(mockFetch.mock.calls.some(([url]) => String(url).includes('generate'))).toBe(false);
  expect(screen.queryByText(/plan options/i)).not.toBeInTheDocument();
});
it('keeps capsule load errors visible and recoverable without claiming zero or ready', async () => {
  state.profileComplete = true; state.stage = 'first-look'; state.capsule.ready = true;
  mockWardrobe.mockRejectedValueOnce(new Error('offline'));
  await renderPage();
  expect(screen.getByRole('alert')).toHaveTextContent('couldn’t load your saved capsule');
  expect(screen.queryByRole('link', { name: 'Create my first outfit' })).not.toBeInTheDocument();
  expect(screen.queryByText(/0 unique/)).not.toBeInTheDocument();
  await act(async () => { choose('Retry loading capsule'); });
  expect(screen.getByRole('link', { name: 'Create my first outfit' })).toBeVisible();
});
it('finishes uploads with a recap without a timed persona redirect', async () => {
  state.profileComplete = true; state.stage = 'capsule'; await renderPage(); choose('Continue my capsule');
  state.capsule = { ...state.capsule, usableCount: 10, savedCount: 10, ready: true }; state.stage = 'first-look';
  await act(async () => { choose('Finish capsule'); }); await advanceTimer(5000);
  expect(screen.getByRole('link', { name: 'Create my first outfit' })).toBeVisible();
  expect(mockRouter.replace).not.toHaveBeenCalled();
});
it('continues to completion when later guest questions are already answered', async () => {
  const questions = fullQuizQuestions('Male');
  state.draft = { answers: questions.filter(question => question.id !== 'category_spend_swimwear').map(question => ({ question_id: question.id, selected_option: question.id === 'gender' ? 'Male' : question.type === 'rgb_slider' ? 'skin_tone_50' : question.options[0] })), currentQuestionId: 'category_spend_swimwear' };
  await renderPage();
  expect(screen.getByRole('heading', { name: 'Your wardrobe habits' })).toBeVisible();
  expect(screen.getByText(/Amounts are in dollars per year/)).toBeVisible();
  choose('$0-$100'); choose('Next');
  expect(screen.getByText('Question 25 of 25')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Save my style & continue' })).toBeEnabled();
  choose('Previous'); expect(screen.getByText('Question 24 of 25')).toBeVisible();
});
it('labels optional answers and provides a privacy-preserving option', async () => {
  state.draft = { answers: [{ question_id: 'gender', selected_option: 'Female' }], currentQuestionId: 'weight' };
  await renderPage(); expect(screen.getByText(/Optional · Ranges are in pounds/)).toBeVisible();
  choose('Prefer not to specify'); expect(screen.getByRole('button', { name: 'Prefer not to specify' })).toHaveAttribute('aria-pressed', 'true');
});
it('does not enable completion before the last answer is selected', async () => {
  state.draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }], currentQuestionId: 'style_elements' };
  await renderPage(); expect(screen.getByRole('button', { name: 'Save my style & continue' })).toBeDisabled();
});
it('does not complete a partial full quiz merely because its last question has an answer', async () => {
  state.draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }, { question_id: 'style_elements', selected_option: 'Clean lines and minimal details' }], currentQuestionId: 'style_elements' };
  await renderPage(); await act(async () => { choose('Save my style & continue'); });
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  expect(screen.getByRole('alert')).toHaveTextContent('Please answer this question');
  expect(mockFetch.mock.calls.some(([url]) => url === '/api/style-quiz/submit')).toBe(false);
});
it('offers explicit recovery for a UID-bound guest transfer without importing automatically', async () => {
  mockPendingTransfer.mockReturnValue(true); await renderPage();
  expect(mockPendingTransfer).toHaveBeenCalledWith(mockUser.uid);
  expect(screen.getByRole('link', { name: 'Continue saving them' })).toHaveAttribute('href', '/signup?from=quiz');
  expect(mockFetch.mock.calls.some(([url, options]) => url === '/api/onboarding' && options?.method === 'PATCH')).toBe(false);
});
it('requires current coverage even when stored capsule progress previously passed', async () => {
  state.profileComplete = true; state.capsule.ready = true;
  mockWardrobe.mockResolvedValue(Array.from({ length: 10 }, (_, index) => ({ id: `shirt-${index}`, userId: mockUser.uid, type: 'shirt', imageUrl: `/shirt-${index}.jpg` })));
  await renderPage(); expect(screen.getByText(/Include shoes and bottom or one-piece/)).toBeVisible();
  expect(screen.queryByRole('link', { name: 'Create my first outfit' })).not.toBeInTheDocument();
});

it.each([
  ['Male', 'body_type_female', 'Hourglass', 'body_type_male', 'Athletic'],
  ['Female', 'shoe_size_male', '12', 'shoe_size_female', '6'],
])('submits only active %s answers after an identity-variant change', async (gender, oldId, oldValue, activeId, activeValue) => {
  const questions = fullQuizQuestions(gender);
  state.draft = { answers: [
    { question_id: oldId, selected_option: oldValue },
    ...questions.map(question => ({ question_id: question.id, selected_option: question.id === 'gender' ? gender : question.id === activeId ? activeValue : question.type === 'rgb_slider' ? 'skin_tone_50' : question.options[0] })),
  ], currentQuestionId: 'style_elements' };
  await renderPage(); await act(async () => { choose('Save my style & continue'); });
  const body = JSON.parse(mockFetch.mock.calls.find(([url]) => url === '/api/style-quiz/submit')![1].body);
  expect(body.answers).not.toContainEqual({ question_id: oldId, selected_option: oldValue });
  expect(body.answers).toContainEqual({ question_id: activeId, selected_option: activeValue });
  expect(body.answers).toHaveLength(questions.length);
  expect(state.draft.answers).toContainEqual({ question_id: oldId, selected_option: oldValue });
});


it('keeps the capsule screen when final confirmation fails and returns a retryable failure to its owner', async () => {
  state.profileComplete = true; await renderPage(); choose('Continue my capsule');
  mockFetch.mockRejectedValueOnce(new Error('offline'));
  await act(async () => { await expect(mockOnComplete(10)).rejects.toThrow('couldn’t confirm your next step'); });
  expect(screen.getByTestId('capsule-target')).toBeVisible();
  expect(screen.queryByRole('link', { name: 'Create my first outfit' })).not.toBeInTheDocument();
  state.capsule = { ...state.capsule, ready: true, usableCount: 10, savedCount: 10 };
  await act(async () => { await mockOnComplete(10); });
  expect(screen.getByRole('link', { name: 'Create my first outfit' })).toBeVisible();
});


it('keeps the warm introduction on the first question and focuses later screens on the active question', async () => {
  await renderPage();
  expect(screen.getByText(/First your preferences, then ten pieces/)).toBeVisible();
  expect(screen.getByText(/Build a profile around your fit/)).toBeVisible();
  choose('Male'); choose('Next');
  expect(screen.queryByText(/First your preferences, then ten pieces/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Build a profile around your fit/)).not.toBeInTheDocument();
  expect(screen.getByRole('heading', { level: 1, name: 'Let’s discover your style' })).toBeVisible();
  expect(screen.getByRole('heading', { name: /Which body shape/ })).toHaveFocus();
  choose('Previous');
  expect(screen.getByText(/First your preferences, then ten pieces/)).toBeVisible();
});
