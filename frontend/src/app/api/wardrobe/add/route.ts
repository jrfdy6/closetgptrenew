import { NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

// Force dynamic rendering since we use request headers
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    serverDebugLog('🔍 DEBUG: Wardrobe ADD API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get the request body
    const body = await request.json();
    serverDebugLog('🔍 DEBUG: Add wardrobe item data:', body);
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    serverDebugLog('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Call the real backend to add the item
    const fullBackendUrl = `${backendUrl}/api/wardrobe/add`;
    serverDebugLog('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    serverDebugLog('🔍 DEBUG: Backend ADD response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend ADD response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend error response body:', errorText);
      
      return NextResponse.json(
        { 
          error: `Failed to add wardrobe item`, 
          details: errorText,
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const responseData = await response.json();
    serverDebugLog('🔍 DEBUG: Backend ADD response data:', responseData);
    
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe ADD:', error);
    
    return NextResponse.json(
      { 
        error: 'Add wardrobe item failed', 
        details: String(error) 
      },
      { status: 500 }
    );
  }
}
