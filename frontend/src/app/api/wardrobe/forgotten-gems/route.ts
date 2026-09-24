import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export const GET = (request: Request) => proxyToBackend(request, '/api/wardrobe-insights/insights/forgotten-gems' + (new URL(request.url).search || ''));
