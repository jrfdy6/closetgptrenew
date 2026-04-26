import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${getBackendUrl()}/api/generate-fix-suggestion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error generating fix suggestion:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to generate fix suggestion' },
      { status: 500 }
    );
  }
}
