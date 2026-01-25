import { NextResponse } from "next/server";
import { getApps, initializeApp, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { getFirestore, Timestamp } from "firebase-admin/firestore";
import { readFileSync } from "fs";
import { join } from "path";

// This endpoint MUST be fast/reliable. Previously it proxied to Railway and often hit Vercel's 10s limit,
// causing 504s that blocked Profile (and onboarding quick checks).
//
// We now read/write the user profile directly in Firestore via Firebase Admin.
export const dynamic = "force-dynamic";
export const maxDuration = 60;
export const runtime = "nodejs";

const profileCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL_MS = 60 * 1000; // 1 minute (best-effort on warm instances)

function initAdmin() {
  if (getApps().length) return;

  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n");
  const projectId = process.env.FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;

  // Prefer env-based credentials (recommended for production).
  if (privateKey && projectId && clientEmail) {
    initializeApp({
      credential: cert({
        projectId,
        clientEmail,
        privateKey,
      }),
    });
    return;
  }

  // Fallback: local service account JSON (useful in dev/self-host; some deployments may bundle this file).
  // NOTE: This is NOT recommended for typical Vercel deployments; prefer env vars.
  const candidates = [
    join(process.cwd(), "serviceAccountKey.json"),
    join(process.cwd(), "frontend", "serviceAccountKey.json"),
  ];
  for (const p of candidates) {
    try {
      const raw = readFileSync(p, "utf8");
      const svc = JSON.parse(raw);
      initializeApp({
        credential: cert(svc),
      });
      return;
    } catch {
      // try next candidate
    }
  }

  throw new Error("Firebase Admin not configured (missing env vars and no serviceAccountKey.json found)");
}

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

async function fetchProfileFromRailway(authHeader: string, startMs: number) {
  const backendUrl = "https://closetgptrenew-production.up.railway.app";
  const fullBackendUrl = `${backendUrl}/api/auth/profile`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8500); // keep under typical 10s serverless limit

  try {
    const res = await fetch(fullBackendUrl, {
      method: "GET",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
      signal: controller.signal,
    });

    const text = await res.text().catch(() => "");
    if (!res.ok) {
      return NextResponse.json(
        {
          error: "Backend request failed",
          details: text || `${res.status} ${res.statusText}`,
          _source: "railway",
          _duration: `${Date.now() - startMs}ms`,
        },
        { status: res.status }
      );
    }

    let data: any = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      // keep empty
    }
    return NextResponse.json({ ...data, _source: "railway", _duration: `${Date.now() - startMs}ms` });
  } catch (e: any) {
    const isTimeout = e?.name === "AbortError";
    return NextResponse.json(
      {
        error: isTimeout ? "Backend request timeout" : "Backend request failed",
        details: String(e?.message || e),
        _source: "railway",
        _duration: `${Date.now() - startMs}ms`,
      },
      { status: isTimeout ? 504 : 502 }
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function GET(request: Request) {
  const start = Date.now();

  try {
    const token = getBearerToken(request);
    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Best-effort cache (warm instance only)
    const cacheKey = token.slice(0, 32);
    const cached = profileCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      return NextResponse.json({ ...cached.data, _cached: true, _duration: `${Date.now() - start}ms` });
    }

    const authHeader = `Bearer ${token}`;

    // If Firebase Admin isn't configured in this deployment, fall back to the Railway proxy
    // instead of hard-failing with 500.
    try {
      initAdmin();
    } catch (e) {
      console.error("PROFILE API: Firebase Admin init failed; falling back to Railway.", e);
      return fetchProfileFromRailway(authHeader, start);
    }

    // If Firebase token verification fails (often due to misconfigured Firebase Admin creds on this host),
    // fall back to Railway, which is known to be configured correctly for production.
    let decoded: any;
    try {
      decoded = await getAuth().verifyIdToken(token);
    } catch (e) {
      console.error("PROFILE API: verifyIdToken failed; falling back to Railway.", e);
      return fetchProfileFromRailway(authHeader, start);
    }
    const userId = decoded.uid;

    const db = getFirestore();
    const userRef = db.collection("users").doc(userId);
    const snap = await userRef.get();

    let rawProfile: any = snap.exists ? snap.data() : null;

    // If missing, create a minimal doc so downstream flows can proceed.
    if (!rawProfile) {
      const now = Timestamp.now();
      const seed = {
        firebase_uid: userId,
        email: decoded?.email || "",
        name: decoded?.name || decoded?.email || "",
        created_at: now,
        updated_at: now,
      };
      await userRef.set(seed, { merge: true });
      rawProfile = seed;
    }

    const normalized = normalizeProfileForClient(rawProfile, decoded, userId);
    const payload = { ...normalized, _source: "firestore", _duration: `${Date.now() - start}ms` };

    profileCache.set(cacheKey, { data: payload, timestamp: Date.now() });

    return NextResponse.json(payload);
  } catch (e: any) {
    // Fail closed for auth errors, but avoid 504s from slow upstreams (we no longer depend on Railway).
    const message = String(e?.message || e);
    const isAuthError =
      message.toLowerCase().includes("token") ||
      message.toLowerCase().includes("auth") ||
      message.toLowerCase().includes("jwt") ||
      message.toLowerCase().includes("permission");

    return NextResponse.json(
      { error: "Failed to fetch user profile", details: message, _duration: `${Date.now() - start}ms` },
      { status: isAuthError ? 401 : 500 }
    );
  }
}

export async function POST(request: Request) {
  const start = Date.now();

  try {
    const token = getBearerToken(request);
    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    const authHeader = `Bearer ${token}`;

    try {
      initAdmin();
    } catch (e) {
      console.error("PROFILE API: Firebase Admin init failed on POST; falling back to Railway.", e);
      // Railway expects PUT for update
      const backendUrl = "https://closetgptrenew-production.up.railway.app";
      const fullBackendUrl = `${backendUrl}/api/auth/profile`;

      const body = await request.json().catch(() => ({}));

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8500);
      try {
        const res = await fetch(fullBackendUrl, {
          method: "PUT",
          headers: {
            Authorization: authHeader,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
        const text = await res.text().catch(() => "");
        if (!res.ok) {
          return NextResponse.json(
            {
              error: "Backend request failed",
              details: text || `${res.status} ${res.statusText}`,
              _source: "railway",
              _duration: `${Date.now() - start}ms`,
            },
            { status: res.status }
          );
        }
        let data: any = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch {}
        return NextResponse.json({ ...data, _source: "railway", _duration: `${Date.now() - start}ms` });
      } catch (err: any) {
        const isTimeout = err?.name === "AbortError";
        return NextResponse.json(
          {
            error: isTimeout ? "Backend request timeout" : "Backend request failed",
            details: String(err?.message || err),
            _source: "railway",
            _duration: `${Date.now() - start}ms`,
          },
          { status: isTimeout ? 504 : 502 }
        );
      } finally {
        clearTimeout(timeoutId);
      }
    }

    // Same as GET: if token verification fails on this host, fall back to Railway.
    let decoded: any;
    try {
      decoded = await getAuth().verifyIdToken(token);
    } catch (e) {
      console.error("PROFILE API: verifyIdToken failed on POST; falling back to Railway.", e);
      const backendUrl = "https://closetgptrenew-production.up.railway.app";
      const fullBackendUrl = `${backendUrl}/api/auth/profile`;

      const body = await request.json().catch(() => ({}));

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8500);
      try {
        const res = await fetch(fullBackendUrl, {
          method: "PUT",
          headers: {
            Authorization: authHeader,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
        const text = await res.text().catch(() => "");
        if (!res.ok) {
          return NextResponse.json(
            {
              error: "Backend request failed",
              details: text || `${res.status} ${res.statusText}`,
              _source: "railway",
              _duration: `${Date.now() - start}ms`,
            },
            { status: res.status }
          );
        }
        let data: any = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch {}
        return NextResponse.json({ ...data, _source: "railway", _duration: `${Date.now() - start}ms` });
      } catch (err: any) {
        const isTimeout = err?.name === "AbortError";
        return NextResponse.json(
          {
            error: isTimeout ? "Backend request timeout" : "Backend request failed",
            details: String(err?.message || err),
            _source: "railway",
            _duration: `${Date.now() - start}ms`,
          },
          { status: isTimeout ? 504 : 502 }
        );
      } finally {
        clearTimeout(timeoutId);
      }
    }
    const userId = decoded.uid;

    const body = await request.json().catch(() => ({}));
    const db = getFirestore();

    const userRef = db.collection("users").doc(userId);
    const now = Timestamp.now();

    const update = {
      ...body,
      firebase_uid: userId,
      email: body?.email || decoded?.email || "",
      name: body?.name || decoded?.name || decoded?.email || "",
      updated_at: now,
      // keep legacy field used elsewhere
      updatedAt: Math.floor(Date.now()),
    };

    // Ensure created_at exists
    const existing = await userRef.get();
    if (!existing.exists || !existing.data()?.created_at) {
      (update as any).created_at = now;
    }

    await userRef.set(update, { merge: true });

    // Bust cache for this token (warm instance only)
    profileCache.delete(token.slice(0, 32));

    const normalized = normalizeProfileForClient(update, decoded, userId);
    return NextResponse.json({ ...normalized, _source: "firestore", _duration: `${Date.now() - start}ms` });
  } catch (e: any) {
    return NextResponse.json(
      { error: "Failed to update user profile", details: String(e?.message || e), _duration: `${Date.now() - start}ms` },
      { status: 500 }
    );
  }
}