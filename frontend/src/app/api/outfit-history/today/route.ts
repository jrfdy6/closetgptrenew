import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfit-history/today`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Forward auth if needed:
        ...(request.headers.get('authorization') && {
          Authorization: request.headers.get('authorization')!,
        }),
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (err) {
    console.error('❌ Proxy GET /outfit-history/today failed:', err);
    return NextResponse.json(
      { error: 'Proxy failed to reach backend' },
      { status: 500 }
    );
  }
}
