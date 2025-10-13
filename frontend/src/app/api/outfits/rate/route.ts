import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  'https://closetgptrenew-production.up.railway.app';

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
    console.log('🔍 DEBUG: Rating request body:', body);

    const fullApiUrl = API_URL.startsWith('http') ? API_URL : `https://${API_URL}`;

    const response = await fetch(`${fullApiUrl}/api/outfit/rate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('🔍 DEBUG: Backend rating error:', errorData);
      return NextResponse.json(
        { error: errorData?.detail || errorData?.error || 'Failed to submit rating' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('🔍 DEBUG: Rating submitted successfully:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in outfit rating route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
