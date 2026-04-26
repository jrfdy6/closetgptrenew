import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export async function POST(request: NextRequest) {
  try {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/api/wardrobe/force-refresh-trends`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error force refreshing trends:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to force refresh trends' },
      { status: 500 }
    );
  }
} 
