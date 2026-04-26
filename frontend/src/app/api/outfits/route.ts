import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    serverDebugLog('🔍 DEBUG: Outfits API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    serverDebugLog('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Get query parameters from the request
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    serverDebugLog('🔍 DEBUG: Query parameters:', queryString);
    
    // Call the real backend to get outfits
    const fullBackendUrl = queryString 
      ? `${backendUrl}/api/outfits?${queryString}`
      : `${backendUrl}/api/outfits`;
    
    serverDebugLog('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
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
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    serverDebugLog('✅ Successfully fetched outfits from backend:', {
      count: Array.isArray(data) ? data.length : 'unknown',
      type: Array.isArray(data) ? 'array' : typeof data
    });
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in outfits API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfits' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    serverDebugLog('🔍 DEBUG: Outfits POST API route called - CONNECTING TO BACKEND');
    
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
    
    // Determine if this is a manual outfit creation (has items array) or generation request
    const isManualCreation = body.items && Array.isArray(body.items) && body.items.length > 0;
    
    // Call the appropriate backend endpoint
    // NOTE: /api/outfits/ needs trailing slash for POST (FastAPI routing)
    const endpoint = isManualCreation ? '/api/outfits/' : '/api/outfits/generate';
    const fullBackendUrl = `${backendUrl}${endpoint}`;
    
    serverDebugLog('🔍 DEBUG: Request type:', isManualCreation ? 'MANUAL CREATION' : 'GENERATION');
    serverDebugLog('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    serverDebugLog('🔍 DEBUG: Items count:', body.items ? body.items.length : 0);

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
        { error: `Backend error: ${response.status} ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    serverDebugLog(`✅ Successfully ${isManualCreation ? 'created' : 'generated'} outfit from backend:`, {
      hasItems: data.items ? data.items.length : 'unknown',
      occasion: data.occasion,
      style: data.style
    });
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in outfits POST API route:', error);
    return NextResponse.json(
      { error: 'Failed to process outfit request' },
      { status: 500 }
    );
  }
}
// Force rebuild Tue Dec  2 15:08:57 EST 2025
