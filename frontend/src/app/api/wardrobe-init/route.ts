import { NextResponse } from 'next/server';

/**
 * Initialize wardrobe count for the current user
 * This is a one-time migration endpoint
 */
export async function POST(request: Request) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    
    // Get authorization header from request
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      return NextResponse.json(
        { success: false, error: 'No authorization header' },
        { status: 401 }
      );
    }
    
    // Forward the request to the backend
    const response = await fetch(`${backendUrl}/api/wardrobe/initialize-my-wardrobe-count`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error('Error initializing wardrobe count:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to initialize wardrobe count',
        details: error.message 
      },
      { status: 500 }
    );
  }
}
