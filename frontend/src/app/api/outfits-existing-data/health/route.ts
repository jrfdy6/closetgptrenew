import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

// Force dynamic rendering to prevent static generation during build
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    serverDebugLog('🔍 [API] Health check endpoint called');
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    
    // Call the real backend
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/health`;
    serverDebugLog('🔍 [API] Backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    serverDebugLog('🔍 [API] Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ [API] Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    serverDebugLog('✅ [API] Health check successful');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [API] Error in health check endpoint:', error);
    return NextResponse.json(
      { error: 'Health check failed' },
      { status: 500 }
    );
  }
}
