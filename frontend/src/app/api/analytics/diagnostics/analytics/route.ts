import { NextRequest, NextResponse } from 'next/server';
import { authenticatedFetch } from '../../../../../lib/utils/auth';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    // Try authenticated request first, fallback to regular fetch
    let response: Response;
    try {
      response = await authenticatedFetch(
        `${backendUrl}/analytics/diagnostics/analytics?${queryString}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    } catch (authError) {
      // Fallback to regular fetch if auth fails
      console.warn('Auth failed, trying without authentication:', authError);
      response = await fetch(
        `${backendUrl}/analytics/diagnostics/analytics?${queryString}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching diagnostic analytics:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch diagnostic analytics',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 