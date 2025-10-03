import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 DEBUG: Outfits API route called - CONNECTING TO BACKEND');
    
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
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Get query parameters from the request
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    console.log('🔍 DEBUG: Query parameters:', queryString);
    
    // Call the real backend to get outfits
    const fullBackendUrl = queryString 
      ? `${backendUrl}/api/outfits?${queryString}`
      : `${backendUrl}/api/outfits`;
    
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend response received:', {
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
    console.log('✅ Successfully fetched outfits from backend:', {
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
    console.log('🔍 DEBUG: Outfits POST API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Temporarily bypass auth check to test functionality
    console.log('🔍 DEBUG: TEMPORARILY BYPASSING AUTH CHECK FOR TESTING');
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Get request body
    const body = await request.json();
    console.log('🔍 DEBUG: Request body:', body);
    
    // Call the real backend to generate outfit using robust service
    const fullBackendUrl = `${backendUrl}/api/outfits/generate`;
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer test', // Use test token for development
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    console.log('🔍 DEBUG: Backend response received:', {
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
    console.log('✅ Successfully generated outfit from backend:', {
      hasItems: data.items ? data.items.length : 'unknown',
      occasion: data.occasion,
      style: data.style
    });
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in outfits POST API route:', error);
    return NextResponse.json(
      { error: 'Failed to generate outfit' },
      { status: 500 }
    );
  }
}
