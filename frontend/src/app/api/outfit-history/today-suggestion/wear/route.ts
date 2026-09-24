import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export const POST = (request: Request) => proxyToBackend(request, '/api/outfit-history/today-suggestion/wear' + (new URL(request.url).search || ''));
