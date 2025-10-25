import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request headers
export const dynamic = 'force-dynamic';

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    console.log('🔍 DEBUG: Wardrobe INCREMENT-WEAR API route called for item:', id);
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Call the real backend to increment wear count
    const fullBackendUrl = `${backendUrl}/api/wardrobe/${id}/increment-wear`;
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend INCREMENT-WEAR response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend INCREMENT-WEAR response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend error response body:', errorText);
      
      return NextResponse.json(
        { 
          error: `Failed to increment wear count`, 
          details: errorText,
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const responseData = await response.json();
    console.log('🔍 DEBUG: Backend INCREMENT-WEAR response data:', responseData);
    
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe INCREMENT-WEAR:', error);
    
    return NextResponse.json(
      { 
        error: 'Increment wear count failed', 
        details: String(error) 
      },
      { status: 500 }
    );
  }
}

