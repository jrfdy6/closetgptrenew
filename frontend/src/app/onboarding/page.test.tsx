declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import Onboarding from './page';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import type { OnboardingState } from '@/lib/onboarding/types';
const mockUser = { uid: 'qa-user', getIdToken: jest.fn(async () => 'quiz-test-token') };
const mockRouter = { push: jest.fn(), replace: jest.fn() };
jest.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false, getIdToken: mockUser.getIdToken }) }));
jest.mock('@/components/BodyPositiveMessage', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/GuidedUploadWizard', () => ({ __esModule: true, default: ({ targetCount }: { targetCount: number }) => <div data-testid="capsule-target">{targetCount}</div> }));
let state: OnboardingState;
let originalFetch: typeof fetch;
let mockFetch: jest.Mock;
let submitSuccess: boolean;
beforeEach(() => {
  jest.useFakeTimers(); window.history.replaceState({}, '', '/onboarding'); sessionStorage.clear();
  mockRouter.push.mockClear(); mockRouter.replace.mockClear();
  originalFetch = globalThis.fetch; submitSuccess = true;
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
    if (!screen.queryByRole('slider', { name: 'Skin tone depth' })) fireEvent.click(screen.getAllByRole('button')[0]);
    if (question < count) choose('Next');
  }
};
it('manual Next advances once even after its auto timer would fire', async () => {
  await renderPage(); choose('Male'); choose('Next');
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  await advanceTimer(1000); expect(screen.getByText('Question 2 of 25')).toBeVisible();
  choose('Rectangle'); choose('Next'); await advanceTimer(1000);
  expect(screen.getByText('Question 3 of 25')).toBeVisible();
  expect(screen.getByRole('slider', { name: 'Skin tone depth' })).toBeVisible();
});
it('changing a choice replaces its timer without skipping the following question', async () => {
  await renderPage(); choose('Male'); await advanceTimer();
  choose('Rectangle'); await advanceTimer(200); choose('Oval'); await advanceTimer(100);
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  await advanceTimer(200); expect(screen.getByText('Question 3 of 25')).toBeVisible();
  await advanceTimer(1000); expect(screen.getByText('Question 3 of 25')).toBeVisible();
});
it('Previous cancels pending auto-advance from the question being left', async () => {
  await renderPage(); choose('Male'); await advanceTimer();
  choose('Rectangle'); choose('Previous'); await advanceTimer(1000);
  expect(screen.getByText('Getting started')).toBeVisible();
});
it('restores the saved question and answer', async () => {
  state.draft = { answers: [{ question_id: 'gender', selected_option: 'Male' }, { question_id: 'body_type_male', selected_option: 'Oval' }], currentQuestionId: 'body_type_male' };
  await renderPage(); expect(screen.getByText('Question 2 of 25')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Oval' })).toHaveClass('bg-gray-900');
  expect(mockFetch).toHaveBeenCalledTimes(1);
});
it('starts the ten-item capsule only after persistence and authoritative readiness', async () => {
  await renderPage(); await completeQuiz();
  await act(async () => { choose('Discover My Style'); });
  const call = mockFetch.mock.calls.find(([url]) => url === '/api/style-quiz/submit');
  expect(JSON.parse(call![1].body).answers).toHaveLength(25);
  expect(JSON.parse(call![1].body).retake).toBeUndefined();
  expect(mockFetch).not.toHaveBeenCalledWith('/api/user/profile', expect.anything());
  expect(screen.getByTestId('capsule-target')).toHaveTextContent('10');
});
it('keeps the question and real answers when submit reports failure, then allows retry', async () => {
  submitSuccess = false; await renderPage(); await completeQuiz();
  await act(async () => { choose('Discover My Style'); });
  expect(screen.queryByTestId('capsule-target')).not.toBeInTheDocument();
  expect(screen.getByText('Question 25 of 25')).toBeVisible();
  expect(screen.getByRole('alert')).toHaveTextContent('Failed to save');
  expect(state.draft.answers).toHaveLength(25);
  submitSuccess = true;
  await act(async () => { choose('Discover My Style'); });
  expect(screen.getByTestId('capsule-target')).toBeVisible();
});
it('never reads or writes the signed-in account during an explicit guest quiz', async () => {
  window.history.replaceState({}, '', '/onboarding?mode=guest');
  await renderPage(); await completeQuiz(13);
  await act(async () => { choose('Discover My Style'); });
  expect(mockFetch).not.toHaveBeenCalled();
  expect(JSON.parse(sessionStorage.getItem('pendingQuizSubmission')!).answers).toHaveLength(13);
  expect(mockRouter.replace).toHaveBeenCalledWith('/finish-profile?from=quiz');
});
it('requires an explicit retake before exposing the quiz for an existing profile', async () => {
  state.profileComplete = true; state.stage = 'capsule'; await renderPage();
  expect(screen.getByText('Your style profile is saved')).toBeVisible();
  expect(screen.queryByText('What is your gender?')).not.toBeInTheDocument();
  choose('Retake my style quiz'); await completeQuiz();
  await act(async () => { choose('Discover My Style'); });
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
  await act(async () => { choose('Discover My Style'); });
  expect(screen.queryByTestId('capsule-target')).not.toBeInTheDocument();
  expect(screen.getByText('Question 25 of 25')).toBeVisible();
  await act(async () => { choose('Discover My Style'); });
  expect(screen.getByTestId('capsule-target')).toBeVisible();
  expect(mockFetch.mock.calls.filter(([url]) => url === '/api/style-quiz/submit')).toHaveLength(1);
});
