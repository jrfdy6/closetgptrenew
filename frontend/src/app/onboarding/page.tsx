"use client";

export const dynamic = 'force-dynamic';

import React, { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, ArrowRight, Check, CheckCircle2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthContext } from '@/contexts/AuthContext';
import BodyPositiveMessage from '@/components/BodyPositiveMessage';
import GuidedUploadWizard from '@/components/GuidedUploadWizard';
import OnboardingProgress from '@/components/onboarding/OnboardingProgress';
import OnboardingRecap from '@/components/onboarding/OnboardingRecap';
import { SkinToneSlider } from '@/components/onboarding/SkinToneSlider';
import { useOnboardingDraft } from '@/lib/hooks/useOnboardingDraft';
import { fullQuizQuestions, QUIZ_QUESTIONS } from '@/lib/onboarding/questions';
import { guestStylePersona } from '@/lib/onboarding/guestStylePersona';
import { quizQuestionHint, quizSection, selectedStyleNames } from '@/lib/onboarding/quizPresentation';
import { ensureDefaultSkinToneAnswer, upsertQuizAnswer } from '@/lib/quizAnswerContract';
import { hasPendingGuestTransfer } from '@/lib/guestDraftTransfer';

const ANSWER_ADVANCE_DELAY_MS = 400;

function OnboardingContent() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuthContext();
  const [flowMode, setFlowMode] = useState<string | null>(null);
  const [modeResolved, setModeResolved] = useState(false);
  const [retake, setRetake] = useState(false);
  const [uploadPhase, setUploadPhase] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [submittedThisVisit, setSubmittedThisVisit] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submissionSaved = useRef(false);
  const submissionPending = useRef(false);
  const questionHeading = useRef<HTMLHeadingElement | null>(null);
  const lastFocusedQuestion = useRef<string | null>(null);
  const answerAdvanceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigationGeneration = useRef(0);
  const cancelAnswerAdvance = useCallback(() => {
    navigationGeneration.current += 1;
    if (answerAdvanceTimer.current !== null) clearTimeout(answerAdvanceTimer.current);
    answerAdvanceTimer.current = null;
  }, []);
  const isGuestFlow = flowMode === 'guest' || flowMode === 'preauth';
  const flowIdentity = useRef<string | null>(null);
  flowIdentity.current = isGuestFlow ? 'guest' : user?.uid || null;
  const onboarding = useOnboardingDraft({ user, enabled: modeResolved && !authLoading, guest: isGuestFlow, allowProfileEdit: retake });
  const answers = onboarding.draft.answers;
  const gender = answers.find(answer => answer.question_id === 'gender')?.selected_option || null;
  const questions = React.useMemo(() => fullQuizQuestions(gender, isGuestFlow), [gender, isGuestFlow]);
  const currentIndex = Math.max(0, questions.findIndex(question => question.id === onboarding.draft.currentQuestionId));
  const question = questions[currentIndex];
  const currentAnswer = answers.find(answer => answer.question_id === question?.id);
  const profileSaved = !isGuestFlow && onboarding.state?.profileComplete && (!retake || submittedThisVisit);
  const pendingGuestTransfer = modeResolved && !isGuestFlow && user && hasPendingGuestTransfer(user.uid);
  const canNavigateQuiz = onboarding.ready && !authLoading && !profileSaved && !isSubmitting && !onboarding.conflict;
  const canNavigateQuizRef = useRef(canNavigateQuiz);
  canNavigateQuizRef.current = canNavigateQuiz;

  // A selection belongs to one visit to one question. Leaving it, switching
  // accounts, or blocking the draft must invalidate even a queued callback.
  useEffect(() => cancelAnswerAdvance, [cancelAnswerAdvance, question?.id, user?.uid, isGuestFlow, canNavigateQuiz]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setFlowMode(params.get('mode') || params.get('flow'));
    setRetake(params.get('retake') === '1');
    setModeResolved(true);
  }, []);
  useEffect(() => {
    if (!authLoading && modeResolved && !user && !isGuestFlow) router.push('/');
  }, [authLoading, modeResolved, user, isGuestFlow, router]);
  useEffect(() => {
    submissionSaved.current = false;
    submissionPending.current = false;
    setIsSubmitting(false);
    setSubmittedThisVisit(false);
    setUploadPhase(false);
    setUploadComplete(false);
    setError(null);
    lastFocusedQuestion.current = null;
  }, [user?.uid, isGuestFlow]);
  useEffect(() => {
    if (!onboarding.ready || profileSaved || question?.type !== 'rgb_slider') return;
    onboarding.updateDraft(previous => ({ ...previous, answers: ensureDefaultSkinToneAnswer(previous.answers, question.id) }));
  }, [onboarding.ready, onboarding.updateDraft, profileSaved, question?.id, question?.type]);
  useEffect(() => {
    if (!onboarding.ready || profileSaved || !question) return;
    // Keep keyboard and screen-reader context on the newly requested question.
    if (lastFocusedQuestion.current && lastFocusedQuestion.current !== question.id) questionHeading.current?.focus();
    lastFocusedQuestion.current = question.id;
  }, [onboarding.ready, profileSaved, question?.id]);

  const goToQuestion = (index: number) => {
    cancelAnswerAdvance();
    if (!canNavigateQuizRef.current) return;
    const destination = questions[index];
    if (destination) onboarding.updateDraft(previous => ({ ...previous, currentQuestionId: destination.id }));
  };
  const advanceFromQuestion = (questionId: string) => {
    // Imported guest answers stay complete. Continue to unanswered full questions;
    // use the latest draft so a new gender or rapid reselection cannot be lost.
    onboarding.updateDraft(previous => {
      if (!canNavigateQuizRef.current || !previous.answers.some(answer => answer.question_id === questionId)) return previous;
      const latestGender = previous.answers.find(answer => answer.question_id === 'gender')?.selected_option || null;
      const latestQuestions = fullQuizQuestions(latestGender, isGuestFlow);
      const visibleQuestionIndex = Math.max(0, latestQuestions.findIndex(candidate => candidate.id === previous.currentQuestionId));
      if (latestQuestions[visibleQuestionIndex].id !== questionId) return previous;
      const originIndex = latestQuestions.findIndex(candidate => candidate.id === questionId);
      if (originIndex < 0 || originIndex === latestQuestions.length - 1) return previous;
      const nextMissing = latestQuestions.findIndex((candidate, index) => index > originIndex && !previous.answers.some(answer => answer.question_id === candidate.id));
      return { ...previous, currentQuestionId: latestQuestions[nextMissing >= 0 ? nextMissing : latestQuestions.length - 1].id };
    });
  };
  const handleNext = () => {
    cancelAnswerAdvance();
    advanceFromQuestion(question.id);
  };
  const handleAnswer = (option: string) => {
    cancelAnswerAdvance();
    if (!canNavigateQuizRef.current) return;
    onboarding.updateDraft(previous => ({ ...previous, answers: upsertQuizAnswer(previous.answers, question.id, option) }));
    if (question.type === 'rgb_slider' || currentIndex === questions.length - 1) return;
    const selectedQuestionId = question.id;
    const selectedIdentity = flowIdentity.current;
    const selectedGeneration = navigationGeneration.current;
    answerAdvanceTimer.current = setTimeout(() => {
      answerAdvanceTimer.current = null;
      if (selectedGeneration !== navigationGeneration.current || selectedIdentity !== flowIdentity.current || !canNavigateQuizRef.current) return;
      advanceFromQuestion(selectedQuestionId);
    }, ANSWER_ADVANCE_DELAY_MS);
  };
  const retakeQuiz = () => {
    cancelAnswerAdvance();
    submissionSaved.current = false;
    setSubmittedThisVisit(false);
    setUploadPhase(false);
    setUploadComplete(false);
    setRetake(true);
    setError(null);
    router.replace('/onboarding?retake=1');
  };
  const submitQuiz = async () => {
    cancelAnswerAdvance();
    if (submissionPending.current) return;
    const firstMissing = questions.findIndex(candidate => !answers.some(answer => answer.question_id === candidate.id));
    if (firstMissing >= 0) {
      goToQuestion(firstMissing);
      setError('Please answer this question before continuing. Optional details have a “Prefer not to say” choice.');
      return;
    }
    const submittingIdentity = flowIdentity.current;
    submissionPending.current = true;
    setIsSubmitting(true);
    setError(null);
    // Keep draft history for review, but only the selected variant can become
    // a profile. Old gender-specific body/size/style answers must not win.
    const activeIds = new Set(questions.map(candidate => candidate.id));
    const quizAnswers = answers.filter(answer => activeIds.has(answer.question_id));
    const stylePreferences = selectedStyleNames(quizAnswers);
    const colorCounts: Record<string, number> = {};
    const colorPreferences: string[] = [];
    const likedStyles: string[] = [];
    quizAnswers.forEach(answer => {
      const source = QUIZ_QUESTIONS.find(item => item.id === answer.question_id);
      if (source?.type !== 'visual_yesno' || answer.selected_option !== 'Yes') return;
      if (source.style_name) likedStyles.push(source.style_name);
      source.colors?.forEach(color => {
        colorCounts[color] = (colorCounts[color] || 0) + 1;
        if (!colorPreferences.includes(color)) colorPreferences.push(color);
      });
    });
    const colorAnalysis = { colorCounts, likedStyles, topColors: Object.entries(colorCounts).sort(([, a], [, b]) => b - a).slice(0, 3).map(([color]) => color) };
    try {
      if (isGuestFlow) {
        if (!await onboarding.flush()) throw new Error('Your browser could not save your answers. Keep this tab open and try again.');
        if (submittingIdentity !== flowIdentity.current) return;
        sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({ answers: quizAnswers, colorAnalysis, stylePreferences, colorPreferences, persona: guestStylePersona(quizAnswers), createdAt: Date.now() }));
        router.replace('/finish-profile?from=quiz');
        return;
      }
      if (!user) throw new Error('Please sign in to complete your style profile.');
      if (!submissionSaved.current && !await onboarding.flush()) throw new Error('Your latest answers have not saved yet. Retry saving before completing the quiz.');
      if (submittingIdentity !== flowIdentity.current) return;
      if (!submissionSaved.current) {
        const token = await user.getIdToken();
        if (submittingIdentity !== flowIdentity.current) return;
        const spending_ranges = Object.fromEntries(['tops', 'pants', 'shoes', 'jackets', 'dresses', 'accessories', 'undergarments', 'swimwear'].map(category => [category, quizAnswers.find(answer => answer.question_id === `category_spend_${category}`)?.selected_option || 'unknown']));
        const response = await fetch('/api/style-quiz/submit', {
          method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ userId: user.uid, token, answers: quizAnswers, colorAnalysis, stylePreferences, colorPreferences, spending_ranges, ...(retake ? { retake: true } : {}) }),
        });
        const data = await response.json();
        if (submittingIdentity !== flowIdentity.current) return;
        if (!response.ok || data.success !== true) throw new Error(typeof data.error === 'string' ? data.error : 'Failed to save your style profile. Please try again.');
        submissionSaved.current = true;
      }
      const savedState = await onboarding.refresh();
      if (submittingIdentity !== flowIdentity.current) return;
      if (!savedState?.profileComplete) throw new Error('Your style profile saved, but we could not load your next step. Retry to continue.');
      setSubmittedThisVisit(true);
      setUploadPhase(!savedState.capsule.ready);
      setUploadComplete(savedState.capsule.ready);
    } catch (cause) {
      if (submittingIdentity === flowIdentity.current) setError(cause instanceof Error ? cause.message : 'Failed to save your style profile. Please try again.');
    } finally {
      if (submittingIdentity === flowIdentity.current) {
        submissionPending.current = false;
        setIsSubmitting(false);
      }
    }
  };

  if (authLoading || !modeResolved || (!user && !isGuestFlow)) return <LoadingProgress message="Loading your experience…" />;
  if (!onboarding.ready) return <LoadingProgress message={onboarding.error || 'Loading your saved progress…'} error={!!onboarding.error} onRetry={onboarding.error ? () => void onboarding.retry() : undefined} />;

  if (uploadPhase && !uploadComplete) return <GuidedUploadWizard
    userId={user?.uid || ''} targetCount={10} gender={gender || undefined}
    onComplete={async () => {
      const completingIdentity = flowIdentity.current;
      const saved = await onboarding.refresh();
      if (completingIdentity !== flowIdentity.current) return;
      if (!saved?.profileComplete || !saved.capsule.ready) throw new Error('Your pieces are saved, but we couldn’t confirm your next step. Please continue again.');
      setUploadComplete(true);
    }}
  />;

  if (profileSaved && (uploadComplete || onboarding.state?.capsule.ready || onboarding.state?.stage === 'complete')) return <OnboardingRecap
    key={user!.uid} userId={user!.uid} answers={answers} onRetake={retakeQuiz}
    onManageCapsule={() => { setUploadComplete(false); setUploadPhase(true); }}
    hasFirstLook={!!onboarding.state?.milestones.firstOutfitId}
  />;

  if (profileSaved) return <main className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 px-4 py-8 dark:from-stone-950 dark:via-stone-900 dark:to-amber-950"><div className="mx-auto max-w-2xl space-y-8">
    <OnboardingProgress stage="capsule" />
    <section className="rounded-3xl border border-amber-200 bg-white p-6 text-center shadow-sm dark:border-stone-700 dark:bg-stone-900 sm:p-10">
      <CheckCircle2 aria-hidden="true" className="mx-auto mb-4 h-8 w-8 text-amber-700 dark:text-amber-300" />
      <h1 className="font-serif text-3xl">Your style profile is saved</h1>
      <p className="mt-3 text-stone-600 dark:text-stone-300">Now build a capsule from the clothes you own. Start with ten pieces, including shoes and a top with bottoms or a one-piece outfit.</p>
      <p className="my-5 font-medium">{onboarding.state!.capsule.usableCount} of 10 unique usable pieces saved</p>
      <Button onClick={() => setUploadPhase(true)} className="min-h-12 rounded-2xl bg-amber-700 px-6 text-white hover:bg-amber-800">Continue my capsule<ArrowRight aria-hidden="true" className="ml-2 h-4 w-4" /></Button>
      <div className="mt-4"><button type="button" onClick={retakeQuiz} className="min-h-11 text-sm underline underline-offset-4">Retake my style quiz</button></div>
    </section>
  </div></main>;

  const section = quizSection(question);
  const hint = quizQuestionHint(question);
  const answeredCount = questions.filter(candidate => answers.some(answer => answer.question_id === candidate.id)).length;
  const sectionQuestions = questions.filter(candidate => quizSection(candidate).id === section.id);
  const sectionAnswered = sectionQuestions.filter(candidate => answers.some(answer => answer.question_id === candidate.id)).length;
  const showIntroduction = question.id === 'gender';
  const showSectionIntroduction = sectionQuestions[0]?.id === question.id;
  const isLastQuestion = currentIndex === questions.length - 1;
  const statusText = onboarding.status === 'saving' ? 'Saving your progress…' : onboarding.status === 'saved' ? (isGuestFlow ? 'Saved in this browser' : 'Progress saved to your account') : onboarding.status === 'conflict' ? 'A newer saved draft needs your review' : 'Your progress needs attention';
  return <main className={`min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 px-4 text-stone-900 dark:from-stone-950 dark:via-stone-900 dark:to-amber-950 dark:text-stone-100 ${showIntroduction ? 'py-6 sm:py-10' : 'py-3 sm:py-6'}`}>
    <div className={`mx-auto max-w-3xl ${showIntroduction ? 'space-y-6' : 'space-y-3 sm:space-y-4'}`}>
      <OnboardingProgress stage="style" />
      {pendingGuestTransfer && <p role="status" className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">Your saved guest answers are waiting. <Link href="/signup?from=quiz" className="font-semibold underline underline-offset-4">Continue saving them</Link> before starting again.</p>}
      <header className="text-center">
        {showIntroduction && <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-amber-800 dark:text-amber-300">{isGuestFlow ? 'A saved start to your profile' : 'A wardrobe that feels like you'}</p>}
        <h1 className={`font-serif ${showIntroduction ? 'text-3xl sm:text-4xl' : 'text-xl sm:text-2xl'}`}>Let’s discover your style</h1>
        {showIntroduction && <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-stone-600 dark:text-stone-300">{isGuestFlow ? 'Start with your style here. After creating an account, finish the remaining fit and wardrobe questions before adding your clothes.' : 'First your preferences, then ten pieces from your closet. We’ll use both to help you get dressed.'}</p>}
      </header>
      <section className="rounded-3xl border border-amber-200/70 bg-white/95 p-5 shadow-sm dark:border-stone-700 dark:bg-stone-900 sm:p-8" aria-label="Style questionnaire">
        <div className="flex flex-wrap justify-between gap-2 text-xs font-medium text-stone-600 dark:text-stone-300">
          <span>{question.id === 'gender' ? 'Getting started' : `Question ${currentIndex + 1} of ${questions.length}`}</span>
          {question.id !== 'gender' && <span>{answeredCount} answered</span>}
        </div>
        <progress aria-label={isGuestFlow ? 'Guest style start progress' : 'Style questionnaire progress'} value={question.id === 'gender' ? 0 : answeredCount} max={questions.length} className="mt-3 h-1.5 w-full overflow-hidden rounded-full accent-amber-700" />
        <div className="mt-3 text-xs text-stone-600 dark:text-stone-300">
          <p role="status" aria-live="polite" className="inline-flex items-center gap-1.5">{onboarding.status === 'saved' && <Check aria-hidden="true" className="h-3.5 w-3.5" />}{statusText}</p>
          {onboarding.error && <p role="alert" className="mt-2 text-red-700 dark:text-red-300">{onboarding.error}</p>}
          {onboarding.status === 'error' && <Button variant="outline" className="mt-2" onClick={() => { cancelAnswerAdvance(); void onboarding.retry(); }}>Retry saving</Button>}
          {onboarding.conflict && <Button variant="outline" className="mt-2" onClick={() => { cancelAnswerAdvance(); onboarding.reloadLatest(); }}>Load newer draft</Button>}
        </div>
        <div className="mb-4 mt-4 border-t border-stone-100 pt-4 dark:border-stone-800 sm:mb-6 sm:mt-6 sm:pt-5">
          <div className="flex flex-wrap items-baseline justify-between gap-2"><h2 className="text-sm font-semibold text-amber-900 dark:text-amber-200">{section.title}</h2><span className="text-xs text-stone-500 dark:text-stone-400">{sectionAnswered} of {sectionQuestions.length} answered in this section</span></div>
          {showSectionIntroduction && <p className="mt-1 text-sm leading-relaxed text-stone-600 dark:text-stone-300">{section.description}</p>}
        </div>
        {error && <p role="alert" className="mb-4 text-sm text-red-700 dark:text-red-300">{error}</p>}
        <h3 id="quiz-question" ref={questionHeading} tabIndex={-1} className="mb-3 font-serif text-2xl leading-snug focus:outline-none sm:text-3xl">{question.question}</h3>
        {hint && <p id="quiz-question-hint" className="mb-5 text-sm leading-relaxed text-stone-600 dark:text-stone-300">{hint}</p>}
        <p id="quiz-navigation-hint" className="mb-4 text-sm text-stone-600 dark:text-stone-300">{isLastQuestion ? 'Choose your answer, then save to continue.' : question.type === 'rgb_slider' ? 'Adjust the slider, then choose Next. Use Previous to review an answer.' : 'Choose an answer to move forward automatically. Use Previous to review an answer.'}</p>
        {question.type === 'visual' && <BodyPositiveMessage variant="profile" className="my-4" />}
        {question.type === 'visual_yesno' && question.images && <div className="mx-auto mb-5 max-w-sm overflow-hidden rounded-2xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-700 dark:bg-stone-800"><div className="relative h-[min(38vh,320px)] min-h-[180px]"><Image src={question.images[0]} alt={`${question.style_name} outfit inspiration`} fill sizes="(max-width: 640px) 80vw, 360px" className="object-contain" /></div><p className="mt-3 text-center font-medium">{question.style_name}</p><p className="mt-1 text-center text-xs capitalize text-stone-500 dark:text-stone-400">{question.colors?.join(', ')}</p></div>}
        {question.type === 'rgb_slider' ? <SkinToneSlider value={Number.parseInt(currentAnswer?.selected_option.replace('skin_tone_', '') || '50', 10)} onValueChange={value => handleAnswer(`skin_tone_${value}`)} /> : <div role="group" aria-labelledby="quiz-question" aria-describedby={hint ? 'quiz-question-hint quiz-navigation-hint' : 'quiz-navigation-hint'} className={`mt-5 grid gap-2.5 ${question.options.length >= 6 || question.type === 'visual_yesno' ? 'grid-cols-2' : 'grid-cols-1'}`}>
          {question.options.map(option => <button key={option} type="button" aria-pressed={currentAnswer?.selected_option === option} onClick={() => handleAnswer(option)} disabled={isSubmitting || !!onboarding.conflict} className={`relative flex min-h-12 items-center justify-center rounded-xl border px-4 py-3 text-center text-sm font-medium leading-snug transition-colors motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-700 disabled:opacity-60 ${currentAnswer?.selected_option === option ? 'border-amber-800 bg-amber-800 text-white shadow-sm dark:border-amber-300 dark:bg-amber-200 dark:text-stone-950' : 'border-stone-200 bg-white text-stone-800 hover:border-amber-600 hover:bg-amber-50 dark:border-stone-600 dark:bg-stone-800 dark:text-stone-100 dark:hover:border-amber-300 dark:hover:bg-stone-700'}`}><span>{option}</span>{currentAnswer?.selected_option === option && <Check aria-hidden="true" className="ml-2 h-4 w-4 shrink-0" />}</button>)}
        </div>}
        <div className="mt-7 flex items-center justify-between gap-3 border-t border-stone-200 pt-5 dark:border-stone-700">
          <Button type="button" variant="outline" onClick={() => goToQuestion(currentIndex - 1)} disabled={currentIndex === 0 || isSubmitting || !!onboarding.conflict} className="min-h-12 rounded-xl"><ArrowLeft aria-hidden="true" className="mr-1 h-4 w-4" />Previous</Button>
          <Button type="button" onClick={isLastQuestion ? () => void submitQuiz() : handleNext} disabled={!currentAnswer || isSubmitting || !!onboarding.conflict} className="h-auto min-h-12 max-w-[65%] whitespace-normal rounded-xl bg-amber-700 px-5 py-3 text-white hover:bg-amber-800">{isSubmitting ? 'Saving your style…' : isLastQuestion ? (isGuestFlow ? 'Save my start & continue' : 'Save my style & continue') : 'Next'}{!isSubmitting && <ArrowRight aria-hidden="true" className="ml-2 h-4 w-4 shrink-0" />}</Button>
        </div>
      </section>
      <p className="pb-3 text-center text-xs leading-relaxed text-stone-500 dark:text-stone-400">{isGuestFlow ? 'Your start stays in this browser until you create an account. Keep this tab to continue.' : 'Wait for “Progress saved to your account” before leaving. You can return to your saved question.'}</p>
    </div>
  </main>;
}

function LoadingProgress({ message, error = false, onRetry }: { message: string; error?: boolean; onRetry?: () => void }) {
  return <div className="flex min-h-screen items-center justify-center bg-amber-50 p-4 dark:bg-stone-950"><div className="max-w-md space-y-4 text-center"><Sparkles aria-hidden="true" className="mx-auto h-8 w-8 text-amber-700" /><p role={error ? 'alert' : 'status'}>{message}</p>{onRetry && <Button onClick={onRetry}>Retry loading progress</Button>}</div></div>;
}
export default function Onboarding() {
  return <Suspense fallback={<LoadingProgress message="Loading onboarding…" />}><OnboardingContent /></Suspense>;
}
