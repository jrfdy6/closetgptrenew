import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 [API] Health check endpoint called');
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    
    // Call the real backend
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/health`;
    console.log('🔍 [API] Backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 [API] Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ [API] Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ [API] Health check successful');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [API] Error in health check endpoint:', error);
    return NextResponse.json(
      { error: 'Health check failed' },
      { status: 500 }
    );
  }
}

