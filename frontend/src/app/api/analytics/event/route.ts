import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward the analytics event to the backend
    const response = await fetch(`${getBackendUrl()}/api/analytics/event`, {
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
