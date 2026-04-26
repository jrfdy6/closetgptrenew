import { NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    const authHeader =
      request.headers.get('authorization') ||
      request.headers.get('Authorization') ||
      request.headers.get('AUTHORIZATION');

    if (!authHeader) {
      return NextResponse.json(
        { success: false, error: 'Authorization header required' },
        { status: 401 }
      );
    }

    const backendUrl = getBackendUrl();

    const response = await fetch(
      `${backendUrl}/api/wardrobe/backfill-processing-status`,
      {
        method: 'POST',
        headers: {
          Authorization: authHeader,
          'Content-Type': 'application/json',
        },
      }
    );

    const responseText = await response.text();

    try {
      const data = JSON.parse(responseText);
      return NextResponse.json(data, { status: response.status });
    } catch (parseError) {
      return NextResponse.json(
        {
          success: response.ok,
          error: 'Failed to parse backend response as JSON',
          rawResponse: responseText,
        },
        { status: response.status }
      );
    }
  } catch (error) {
    console.error('❌ Error in backfill route:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to call backfill endpoint',
      },
      { status: 500 }
    );
  }
}
