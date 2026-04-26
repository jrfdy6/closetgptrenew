import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

// DEPLOYMENT VERSION: 2025-10-11-v4-working-endpoint
// Force this route to be treated as a dynamic server route
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

// Handle CORS preflight requests
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

export async function POST(request: NextRequest) {
  try {
    serverDebugLog('🔍 DEBUG v4: Existing-data generate API route called - CONNECTING TO BACKEND');
    
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
    serverDebugLog('🔍 DEBUG: Request body keys:', Object.keys(body));
    serverDebugLog('🚨 CRITICAL: baseItemId in proxy body:', body.baseItemId);
    serverDebugLog('🚨 CRITICAL: baseItemId type:', typeof body.baseItemId);
    serverDebugLog('🚨 CRITICAL: baseItemId is undefined?', body.baseItemId === undefined);
    
    // Call the real backend generate endpoint (the one that actually exists!)
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/generate-personalized`;
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
    serverDebugLog('✅ DEBUG: Generated outfit received successfully');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in generate outfit route:', error);
    return NextResponse.json(
      { error: 'Outfit generation failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
