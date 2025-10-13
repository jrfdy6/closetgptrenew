import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.BACKEND_URL ||
  'https://closetgptrenew-backend-production.up.railway.app';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward the analytics event to the backend
    const response = await fetch(`${BACKEND_URL}/api/analytics/event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      console.error('Backend analytics endpoint returned error:', response.status, response.statusText);
      // Return success even if backend fails to avoid breaking frontend
      return NextResponse.json({ success: true }, { status: 200 });
    }

    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error sending analytics event:', error);
    // Return success even if backend fails to avoid breaking frontend
    return NextResponse.json({ success: true }, { status: 200 });
  }
} 