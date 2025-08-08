import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

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

    // Normalize createdAt to seconds if present
    const createdAt = body?.createdAt;
    let normalizedCreatedAt = createdAt;
    if (typeof createdAt === 'number') {
      normalizedCreatedAt = createdAt > 1000000000000 ? Math.floor(createdAt / 1000) : createdAt;
    }

    const payload = {
      ...body,
      createdAt: normalizedCreatedAt ?? Math.floor(Date.now() / 1000),
    };

    const fullApiUrl = API_URL.startsWith('http') ? API_URL : `https://${API_URL}`;

    const response = await fetch(`${fullApiUrl}/api/outfit/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData?.detail || errorData?.error || 'Failed to create outfit' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in outfit create route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
