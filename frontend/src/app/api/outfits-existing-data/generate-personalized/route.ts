import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const POST = (request: Request) => proxyToBackend(request, '/api/outfits-existing-data/generate-personalized');
