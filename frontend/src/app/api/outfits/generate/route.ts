import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  'https://closetgptrenew-backend-production.up.railway.app';

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: /api/outfits/generate called');
    
    // Forward auth header
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const body = await request.json();
    console.log('🔍 DEBUG: Generation request body:', body);

    const fullApiUrl = API_URL.startsWith('http') ? API_URL : `https://${API_URL}`;

    // Forward the request to the backend with timeout
    const response = await fetch(`${fullApiUrl}/api/outfits/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(25000), // 25 second timeout for outfit generation
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('🔍 DEBUG: Backend generation error:', errorData);
      return NextResponse.json(
        { error: errorData?.detail || errorData?.error || 'Failed to generate outfit' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('🔍 DEBUG: Outfit generated successfully:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in outfit generation route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
