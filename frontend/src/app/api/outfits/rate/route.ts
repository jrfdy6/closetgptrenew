import { NextResponse } from "next/server";
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog, serverDebugWarn } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    // Forward auth header
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const body = await request.json();
    serverDebugLog('🔍 DEBUG: Rating request received');

    const response = await fetch(`${getBackendUrl()}/api/outfits/rate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      serverDebugWarn('🔍 DEBUG: Backend rating error:', errorData);
      return NextResponse.json(
        { error: errorData?.detail || errorData?.error || 'Failed to submit rating' },
        { status: response.status }
      );
    }

    const data = await response.json();
    serverDebugLog('🔍 DEBUG: Rating submitted successfully');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in outfit rating route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
