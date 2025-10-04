import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('🔍 [API] Generate personalized outfit endpoint called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 [API] Authorization header present:', !!authHeader);
    
    // Get request body
    const body = await request.json();
    console.log('🔍 [API] Request body received');
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    
    // Call the real backend
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/generate-personalized`;
    console.log('🔍 [API] Backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader || 'Bearer test',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
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
    console.log('✅ [API] Personalized outfit generated successfully');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [API] Error in generate personalized outfit endpoint:', error);
    return NextResponse.json(
      { error: 'Failed to generate personalized outfit' },
      { status: 500 }
    );
  }
}
