import { createHash } from 'node:crypto';
import { NextResponse, type NextRequest } from 'next/server';
import { getFirebaseAdminAuth, getFirebaseAdminDb } from '@/lib/server/firebaseAdmin';
import { hasStyleProfile } from '@/lib/onboarding/state';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import { mapQuizAnswersToProfile } from '@/lib/server/quizProfile';

export const runtime = 'nodejs';

class SubmissionError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

// Hash only server-normalized input; a lost response can be retried without a second write.
function canonical(value: any): any {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  return value;
}

export async function POST(req: NextRequest) {
  const authorization = req.headers.get('authorization');
  const token = authorization?.startsWith('Bearer ') ? authorization.slice(7).trim() : '';
  if (!token) return NextResponse.json({ success: false, error: 'Please sign in to save your style profile.' }, { status: 401 });

  let identity;
  try {
    identity = await getFirebaseAdminAuth().verifyIdToken(token, true);
  } catch (error: any) {
    const status = String(error?.code || '').startsWith('auth/') ? 401 : 503;
    return NextResponse.json({ success: false, error: status === 401 ? 'Please sign in again.' : 'Profile saving is temporarily unavailable. Your answers are still available to retry.' }, { status });
  }

  try {
    const submission = await req.json();
    if (!submission || typeof submission !== 'object') throw new SubmissionError(422, 'INVALID_SUBMISSION', 'Invalid quiz submission.');
    if ([submission.guest, submission.guestMode, submission.isGuestFlow, submission.isGuest].some(value => value === true || value === 'true' || value === '1' || value === 1) || submission.mode === 'guest') {
      throw new SubmissionError(403, 'GUEST_WRITE_DENIED', 'Guest answers must remain a draft until you continue the full questionnaire.');
    }
    if ([submission.userId, submission.user_id].some(id => id !== undefined && id !== identity.uid)) {
      throw new SubmissionError(403, 'IDENTITY_MISMATCH', 'The profile does not belong to the signed-in account.');
    }
    if (!Array.isArray(submission.answers) || !submission.answers.length || submission.answers.length > 100 ||
        submission.answers.some((answer: any) => !answer || typeof answer.question_id !== 'string' || typeof answer.selected_option !== 'string' || !answer.question_id || !answer.selected_option.trim())) {
      throw new SubmissionError(422, 'INVALID_ANSWERS', 'Please complete the questionnaire before saving.');
    }
    const answers: Record<string, string> = Object.fromEntries(submission.answers.map((answer: any) => [answer.question_id, answer.selected_option]));
    if (Object.keys(answers).length !== submission.answers.length) throw new SubmissionError(422, 'INVALID_ANSWERS', 'Each question must have one answer.');
    if (!['Male', 'Female', 'Non-binary', 'Prefer not to say'].includes(answers.gender) ||
        fullQuizQuestions(answers.gender).some(question => !answers[question.id]?.trim())) {
      throw new SubmissionError(422, 'FULL_QUIZ_REQUIRED', 'Please finish the full questionnaire before saving your style profile.');
    }
    for (const field of ['stylePreferences', 'colorPreferences']) {
      if (submission[field] !== undefined && (!Array.isArray(submission[field]) || submission[field].some((value: any) => typeof value !== 'string'))) {
        throw new SubmissionError(422, 'INVALID_PREFERENCES', 'Invalid style preferences.');
      }
    }

    const submissionHash = createHash('sha256').update(JSON.stringify(canonical({
      answers, stylePreferences: submission.stylePreferences || [], colorPreferences: submission.colorPreferences || [],
      colorAnalysis: submission.colorAnalysis || null, spendingRanges: submission.spending_ranges || null,
    }))).digest('hex');
    const db = getFirebaseAdminDb();
    const ref = db.collection('users').doc(identity.uid);
    const saved = await db.runTransaction(async transaction => {
      const snap = await transaction.get(ref);
      const existing = snap.data() || {};
      if (existing.styleQuizSubmissionHash === submissionHash && hasStyleProfile(existing)) return existing;
      if (hasStyleProfile(existing) && submission.retake !== true) {
        throw new SubmissionError(409, 'RETAKE_REQUIRED', 'You already have a style profile. Choose Retake to replace it.');
      }
      const update = mapQuizAnswersToProfile(answers, submission.colorAnalysis, submission.stylePreferences || [], submission.colorPreferences || [],
        identity.name || existing.name || identity.email?.split('@')[0] || '', identity.email || existing.email || '', identity.uid, submission.spending_ranges || null);
      // Merge nested optional fields as well as the document itself.
      if (update.measurements) update.measurements = { ...(existing.measurements || {}), ...update.measurements };
      update.preferences = { ...(existing.preferences || {}), ...update.preferences };
      const now = Math.floor(Date.now() / 1000);
      update.created_at = existing.created_at ?? existing.createdAt ?? now;
      update.styleQuizCompletedAt = now;
      update.styleQuizSubmissionHash = submissionHash;
      if (submission.spending_ranges && JSON.stringify(existing.spending_ranges) !== JSON.stringify(submission.spending_ranges)) {
        update.tveRecalcStatus = 'queued';
        update.tveRecalcRequestedAt = now;
      }
      transaction.set(ref, update, { merge: true });
      return update;
    });

    return NextResponse.json({ success: true, persisted: true, message: 'Style profile saved successfully',
      hybridStyleName: saved.stylePersona.name, quizResults: { aesthetic_scores: saved.stylePersonality, color_season: answers.skin_tone || null,
        body_type: saved.bodyType || null, style_preferences: saved.stylePreferences }, colorAnalysis: submission.colorAnalysis || null });
  } catch (error) {
    if (error instanceof SubmissionError) return NextResponse.json({ success: false, code: error.code, error: error.message }, { status: error.status });
    if (error instanceof SyntaxError) return NextResponse.json({ success: false, error: 'Invalid quiz submission.' }, { status: 422 });
    // Never claim completion and never retry a write through an unverified client SDK.
    console.error('Style profile could not be persisted');
    return NextResponse.json({ success: false, error: 'Your style profile could not be saved. Your answers are still available to retry.' }, { status: 503 });
  }
}
