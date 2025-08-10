import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.BACKEND_URL ||
      'https://acceptable-wisdom-production-ac06.up.railway.app';
    const response = await fetch(`${baseUrl}/api/wardrobe/wardrobe-stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching wardrobe stats:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch wardrobe statistics' },
      { status: 500 }
    );
  }
} 