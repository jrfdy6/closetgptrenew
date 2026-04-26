import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    serverDebugLog('🔍 DEBUG: Debug filter API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      console.error('❌ No Authorization header provided');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    serverDebugLog('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Get request body
    const body = await request.json();
    serverDebugLog('🔍 DEBUG: Request body:', body);
    
    // Call the real backend debug endpoint
    const fullBackendUrl = `${backendUrl}/api/outfits/debug-filter`;
    serverDebugLog('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    serverDebugLog('🔍 DEBUG: Backend response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Backend error response:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    serverDebugLog('🔍 DEBUG: Debug analysis received:', data);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in debug filter route:', error);
    return NextResponse.json(
      { error: 'Debug analysis failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
