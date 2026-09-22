import { NextResponse } from 'next/server';
import { getFirebaseAdminAuth, getFirebaseAdminDb } from '@/lib/server/firebaseAdmin';
import { parseDraft } from '@/lib/onboarding/state';
import { DraftRevisionConflict, readOnboardingState, reconcileOnboardingState, saveOnboardingDraft } from '@/lib/server/onboarding';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const maxDuration = 60;

const respond = (body: unknown, status = 200) => NextResponse.json(body, {
  status, headers: { 'Cache-Control': 'private, no-store' },
});

async function authenticate(request: Request): Promise<string | null> {
  const header = request.headers.get('authorization') || '';
  if (!header.startsWith('Bearer ') || !header.slice(7).trim()) return null;
  // No decoded-only JWT, test-token branch, client userId, or backend auth defaults.
  const auth = getFirebaseAdminAuth();
  try {
    const decoded = await auth.verifyIdToken(header.slice(7).trim(), true);
    return decoded.uid || null;
  } catch {
    return null;
  }
}

export async function GET(request: Request) {
  try {
    const userId = await authenticate(request);
    if (!userId) return respond({ success: false, error: 'Please sign in to load your progress.' }, 401);
    const state = await readOnboardingState(getFirebaseAdminDb(), userId);
    return respond({ success: true, state });
  } catch {
    return respond({ success: false, error: 'Your progress could not be loaded. Please retry.' }, 503);
  }
}

export async function POST(request: Request) {
  try {
    const userId = await authenticate(request);
    if (!userId) return respond({ success: false, error: 'Please sign in to load your progress.' }, 401);
    const state = await reconcileOnboardingState(getFirebaseAdminDb(), userId);
    return respond({ success: true, state });
  } catch {
    return respond({ success: false, error: 'Your progress could not be confirmed. Please retry.' }, 503);
  }
}

export async function PATCH(request: Request) {
  try {
    const userId = await authenticate(request);
    if (!userId) return respond({ success: false, error: 'Please sign in to save your progress.' }, 401);
    let body: any;
    try { body = await request.json(); } catch { return respond({ success: false, error: 'Invalid questionnaire draft.' }, 422); }
    const draft = parseDraft(body?.draft);
    if (!draft || !Number.isSafeInteger(body?.expectedRevision) || body.expectedRevision < 0 ||
      JSON.stringify(body).length > 128_000) {
      return respond({ success: false, error: 'Invalid questionnaire draft.' }, 422);
    }
    const state = await saveOnboardingDraft(getFirebaseAdminDb(), userId, body.expectedRevision, draft);
    return respond({ success: true, state });
  } catch (error) {
    if (error instanceof DraftRevisionConflict) {
      return respond({ success: false, code: 'revision_conflict', error: error.message, state: error.state }, 409);
    }
    return respond({ success: false, error: 'Your answers were not saved. Please retry.' }, 503);
  }
}
