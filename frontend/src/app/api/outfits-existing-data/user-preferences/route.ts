import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    serverDebugLog('🔍 [API] User preferences endpoint called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 [API] Authorization header present:', !!authHeader);
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    
    // Call the real backend
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/user-preferences`;
    serverDebugLog('🔍 [API] Backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || 'Bearer test',
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
    serverDebugLog('✅ [API] User preferences fetched successfully');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [API] Error in user preferences endpoint:', error);
    return NextResponse.json(
      { error: 'Failed to get user preferences' },
      { status: 500 }
    );
  }
}
