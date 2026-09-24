import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export const GET = (request: Request) => proxyToBackend(request, '/api/simple-analytics/outfits-worn-this-week' + (new URL(request.url).search || ''));
