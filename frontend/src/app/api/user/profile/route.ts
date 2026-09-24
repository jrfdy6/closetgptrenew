import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;
export const runtime = 'nodejs';

export async function GET(request: Request) {
  return proxyToBackend(request, '/api/user/profile', { method: 'GET' });
}

export async function POST(request: Request) {
  return proxyToBackend(request, '/api/user/profile', { method: 'POST' });
}
