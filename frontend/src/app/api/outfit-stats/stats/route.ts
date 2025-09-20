import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const days = searchParams.get('days') || '7';

    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // Increased to 20 seconds

    const response = await fetch(`${baseUrl}/api/outfit-stats/stats?days=${encodeURIComponent(days)}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.detail || 'Failed to fetch outfit stats' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);

  } catch (error: any) {
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { success: false, error: 'Backend request timeout' },
        { status: 504 }
      );
    }
    return NextResponse.json(
      { success: false, error: 'Failed to fetch outfit stats' },
      { status: 500 }
    );
  }
}
