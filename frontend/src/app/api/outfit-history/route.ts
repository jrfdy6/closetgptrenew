import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const GET = (request: Request) =>
  proxyToBackend(request, '/api/outfit-history/?' + new URL(request.url).searchParams.toString());
