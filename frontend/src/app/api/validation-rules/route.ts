import { unavailableData } from '@/lib/server/unavailableData';

export const dynamic = 'force-dynamic';
export const GET = (request: Request) => unavailableData(request, 'Validation rules');
