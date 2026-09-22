import type { User } from 'firebase/auth';

export async function savePendingQuiz(user: User): Promise<string> {
  const raw = sessionStorage.getItem('pendingQuizSubmission');
  if (!raw) return '/onboarding';
  const pending = JSON.parse(raw);
  const token = await user.getIdToken();
  const response = await fetch('/api/style-quiz/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      userId: user.uid, answers: pending.answers || [],
      colorAnalysis: pending.colorAnalysis || null,
      stylePreferences: pending.stylePreferences || [],
      colorPreferences: pending.colorPreferences || [],
      spending_ranges: pending.spending_ranges,
    }),
  });
  const result = await response.json().catch(() => null);
  if (!response.ok || result?.success !== true) {
    throw new Error('You are signed in, but your quiz has not been saved. Your answers are kept here; please retry.');
  }
  // Preserve the saved quiz's upload guidance across the sign-in redirect.
  sessionStorage.setItem('capsuleUploadContext', JSON.stringify({
    userId: user.uid,
    gender: pending.answers?.find((answer: any) => answer.question_id === 'gender')?.selected_option,
  }));
  sessionStorage.removeItem('pendingQuizSubmission');
  return typeof result.wardrobeCount === 'number' && result.wardrobeCount >= 10
    ? '/style-persona?from=quiz'
    : '/onboarding?resume=uploads';
}
