import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export const GET = (request: Request) => proxyToBackend(request, '/api/outfit-history/today-suggestion' + (new URL(request.url).search || ''));
