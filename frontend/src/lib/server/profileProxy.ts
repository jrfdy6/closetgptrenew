import { NextResponse } from 'next/server';
import { getBackendUrl } from './backendUrl';

// All identity, editable-field validation and account initialization live in
// the authenticated backend. Never spread client data into an Admin SDK write.
export async function proxyProfile(request: Request, method: 'GET' | 'PUT') {
  const authorization = request.headers.get('authorization');
  if (!authorization?.startsWith('Bearer ') || !authorization.slice(7).trim()) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }
  let body: unknown;
  if (method === 'PUT') {
    try { body = await request.json(); }
    catch { return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 }); }
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return NextResponse.json({ error: 'Profile must be an object' }, { status: 422 });
    }
  }
  try {
    const response = await fetch(`${getBackendUrl().replace(/\/$/, '')}/api/auth/profile`, {
      method,
      headers: { Authorization: authorization, 'Content-Type': 'application/json' },
      ...(method === 'PUT' ? { body: JSON.stringify(body) } : {}),
      cache: 'no-store',
      signal: AbortSignal.timeout(15000),
    });
    const data = await response.json().catch(() => null);
    if (!data) return NextResponse.json({ error: 'Profile service returned an invalid response. Please retry.' }, { status: 502 });
    return NextResponse.json(data, {
      status: response.status,
      headers: { 'Cache-Control': 'private, no-store' },
    });
  } catch (error) {
    const timeout = error instanceof Error && ['AbortError', 'TimeoutError'].includes(error.name);
    return NextResponse.json({ error: 'Your profile could not be saved or loaded. Please retry.', retryable: true }, { status: timeout ? 504 : 502 });
  }
}
