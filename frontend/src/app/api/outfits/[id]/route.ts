import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';

function buildBackendUrl(path: string) {
  return `${getBackendUrl().replace(/\/$/, '')}${path}`;
}

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const headers = { 'Cache-Control': 'private, no-store' };
  const authorization = request.headers.get('authorization');
  if (!authorization || !/^Bearer \S+$/.test(authorization)) return NextResponse.json({ error: 'Sign in to view this outfit.' }, { status: 401, headers });
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(buildBackendUrl('/api/outfits/' + encodeURIComponent(params.id)), {
      headers: { Authorization: authorization }, cache: 'no-store', signal: controller.signal, redirect: 'error',
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) return NextResponse.json({ error: response.status === 404 || response.status === 403 ? 'This saved outfit is unavailable.' : 'We could not load your saved outfit. Please try again.' }, { status: response.status, headers });
    if (data?.id !== params.id || !Array.isArray(data?.items)) return NextResponse.json({ error: 'The saved outfit response could not be confirmed.' }, { status: 502, headers });
    return NextResponse.json(data, { headers });
  } catch {
    return NextResponse.json({ error: 'We could not load your saved outfit. Please try again.' }, { status: 503, headers });
  } finally { clearTimeout(timer); }
}

export const PUT = (request: Request, { params }: { params: { id: string } }) =>
  proxyToBackend(request, '/api/outfits/' + encodeURIComponent(params.id));
export const DELETE = (request: Request, { params }: { params: { id: string } }) =>
  proxyToBackend(request, '/api/outfits/' + encodeURIComponent(params.id));
