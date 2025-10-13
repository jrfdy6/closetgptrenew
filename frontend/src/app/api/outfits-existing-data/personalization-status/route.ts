import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 [API] Personalization status endpoint called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 [API] Authorization header present:', !!authHeader);
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    
    // Call the real backend
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/personalization-status`;
    console.log('🔍 [API] Backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || 'Bearer test',
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
    console.log('✅ [API] Personalization status fetched successfully');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [API] Error in personalization status endpoint:', error);
    return NextResponse.json(
      { error: 'Failed to get personalization status' },
      { status: 500 }
    );
  }
}

