import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.BACKEND_URL ||
      'https://closetgptrenew-production.up.railway.app';
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