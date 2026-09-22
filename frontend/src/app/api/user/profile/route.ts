import { NextResponse } from 'next/server';
import { Timestamp } from 'firebase-admin/firestore';
import { getFirebaseAdminAuth, getFirebaseAdminDb } from '@/lib/server/firebaseAdmin';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;
export const runtime = 'nodejs';

function getBearerToken(request: Request): string | null {
  const raw = request.headers.get("authorization") || request.headers.get("Authorization");
  if (!raw) return null;
  if (!raw.startsWith("Bearer ")) return null;
  return raw.slice("Bearer ".length).trim();
}

function toUnixSeconds(value: any): number | null {
  if (value == null) return null;
  if (typeof value === "number") {
    // Heuristic: treat large numbers as ms, smaller as seconds.
    return value > 1_000_000_000_000 ? Math.floor(value / 1000) : Math.floor(value);
  }
  if (typeof value === "string") {
    const dt = new Date(value);
    if (!Number.isNaN(dt.getTime())) return Math.floor(dt.getTime() / 1000);
    const asNum = Number(value);
    if (!Number.isNaN(asNum)) return toUnixSeconds(asNum);
    return null;
  }
  // Firestore Timestamp (admin SDK)
  if (typeof value === "object" && typeof value.seconds === "number") {
    return Math.floor(value.seconds);
  }
  return null;
}

function normalizeProfileForClient(input: any, decoded: any, userId: string) {
  const data = input || {};

  const createdSeconds =
    toUnixSeconds(data.created_at) ??
    toUnixSeconds(data.createdAt) ??
    toUnixSeconds(decoded?.iat ? decoded.iat * 1000 : null);
  const updatedSeconds =
    toUnixSeconds(data.updated_at) ??
    toUnixSeconds(data.updatedAt) ??
    createdSeconds ??
    null;

  return {
    ...data,
    user_id: data.user_id || data.userId || userId,
    userId: data.userId || userId,
    firebase_uid: data.firebase_uid || userId,
    email: data.email || decoded?.email || "",
    name: data.name || decoded?.name || decoded?.email || "",
    created_at: createdSeconds ?? undefined,
    updated_at: updatedSeconds ?? undefined,
  };
}

class ProfileError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function verifiedIdentity(request: Request) {
  const token = getBearerToken(request);
  if (!token) throw new ProfileError(401, 'Not authenticated');
  try { return await getFirebaseAdminAuth().verifyIdToken(token, true); }
  catch (error: any) {
    if (String(error?.code || '').startsWith('auth/')) throw new ProfileError(401, 'Please sign in again.');
    throw new ProfileError(503, 'Profile access is temporarily unavailable. Please retry.');
  }
}

function failure(error: unknown) {
  if (error instanceof ProfileError) return NextResponse.json({ error: error.message }, { status: error.status });
  if (error instanceof SyntaxError) return NextResponse.json({ error: 'Invalid profile update' }, { status: 422 });
  return NextResponse.json({ error: 'Profile access is temporarily unavailable. Please retry.' }, { status: 503 });
}

export async function GET(request: Request) {
  const start = Date.now();
  try {
    // Verify every request. JWT header prefixes are shared between users and are not cache keys.
    const decoded = await verifiedIdentity(request);
    const userId = decoded.uid;
    const userRef = getFirebaseAdminDb().collection('users').doc(userId);
    const snap = await userRef.get();
    let rawProfile = snap.exists ? snap.data() : null;
    if (!rawProfile) {
      const now = Timestamp.now();
      const seed = { firebase_uid: userId, email: decoded.email || '', name: decoded.name || decoded.email || '', created_at: now, updated_at: now };
      // Read absence does not authorize replacing a profile created concurrently.
      try { await userRef.create(seed); rawProfile = seed; }
      catch (error: any) {
        if (error?.code !== 6 && error?.code !== 'already-exists') throw error;
        rawProfile = (await userRef.get()).data();
      }
    }
    return NextResponse.json({ ...normalizeProfileForClient(rawProfile, decoded, userId), _source: 'firestore', _duration: `${Date.now() - start}ms` },
      { headers: { 'Cache-Control': 'private, no-store' } });
  } catch (error) { return failure(error); }
}

export async function POST(request: Request) {
  const start = Date.now();
  try {
    const decoded = await verifiedIdentity(request);
    const userId = decoded.uid;
    const body = await request.json();
    if (!body || typeof body !== 'object' || Array.isArray(body)) throw new ProfileError(422, 'Invalid profile update');
    if ([body.userId, body.user_id, body.firebase_uid].some(id => id !== undefined && id !== userId)) throw new ProfileError(403, 'The profile does not belong to the signed-in account.');
    const userRef = getFirebaseAdminDb().collection('users').doc(userId);
    const existing = await userRef.get();
    const stored = existing.data() || {};
    const now = Timestamp.now();
    const update: Record<string, any> = {
      ...body,
      firebase_uid: userId,
      userId,
      user_id: userId,
      email: body.email || decoded.email || stored.email || '',
      name: body.name || stored.name || decoded.name || decoded.email || '',
      updated_at: now,
      updatedAt: Date.now(),
      created_at: stored.created_at || stored.createdAt || now,
    };
    // Only the verified quiz transaction can issue its completion acknowledgement.
    delete update.styleQuizSubmissionHash;
    delete update.styleQuizCompletedAt;
    await userRef.set(update, { merge: true });
    return NextResponse.json({ ...normalizeProfileForClient(update, decoded, userId), _source: 'firestore', _duration: `${Date.now() - start}ms` },
      { headers: { 'Cache-Control': 'private, no-store' } });
  } catch (error) { return failure(error); }
}
