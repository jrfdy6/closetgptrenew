import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe debug API route called');
    
    // Get backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Call the backend debug endpoint
    const response = await fetch(`${backendUrl}/api/wardrobe/debug`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend debug response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend debug response not ok:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Backend debug endpoint not available', status: response.status },
        { status: 500 }
      );
    }
    
    const debugData = await response.json();
    console.log('🔍 DEBUG: Backend debug data received:', debugData);
    
    return NextResponse.json(debugData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe debug route:', error);
    return NextResponse.json(
      { error: 'Debug endpoint failed', details: error.message },
      { status: 500 }
    );
  }
}
