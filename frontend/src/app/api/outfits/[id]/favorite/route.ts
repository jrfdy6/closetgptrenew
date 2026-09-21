import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export const dynamic = 'force-dynamic';

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return NextResponse.json({ success: false, error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  if (typeof body?.isFavorite !== 'boolean') {
    return NextResponse.json(
      { success: false, error: 'isFavorite must be a boolean' },
      { status: 422 }
    );
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    // Forward the desired state in one write. Retrying cannot invert a favorite.
    const backendResponse = await fetch(
      `${getBackendUrl()}/api/outfits/${encodeURIComponent(params.id)}/favorite`,
      {
        method: 'PUT',
        headers: { Authorization: authHeader, 'Content-Type': 'application/json' },
        body: JSON.stringify({ isFavorite: body.isFavorite }),
        signal: controller.signal,
      }
    );
    const data = await backendResponse.json().catch(() => null);
    if (!backendResponse.ok) {
      return NextResponse.json(
        { success: false, error: data?.detail || data?.error || 'Failed to update favorite' },
        { status: backendResponse.status }
      );
    }
    if (data?.success === false || typeof data?.isFavorite !== 'boolean') {
      return NextResponse.json(
        { success: false, error: 'The server did not confirm the favorite update' },
        { status: 502 }
      );
    }
    return NextResponse.json(data);
  } catch (error) {
    const timedOut = error instanceof Error && error.name === 'AbortError';
    return NextResponse.json(
      { success: false, error: timedOut ? 'Favorite update timed out. Please try again.' : 'Failed to update favorite' },
      { status: timedOut ? 504 : 500 }
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
