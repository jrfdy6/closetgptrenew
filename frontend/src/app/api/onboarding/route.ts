import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const maxDuration = 60;

export const GET = (request: Request) => proxyToBackend(request, '/api/onboarding');
export const POST = (request: Request) => proxyToBackend(request, '/api/onboarding');
export const PATCH = (request: Request) => proxyToBackend(request, '/api/onboarding');
