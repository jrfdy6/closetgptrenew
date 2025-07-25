import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:3001';
    const response = await fetch(`${backendUrl}/api/wardrobe/wardrobe-stats`, {
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