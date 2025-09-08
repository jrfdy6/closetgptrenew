import { NextRequest, NextResponse } from 'next/server';

// Simple test route to check what's happening with outfits
export async function GET(req: NextRequest) {
  console.log("🔍 TEST: Outfits test route called");
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    console.log('🔍 TEST: Authorization header present:', !!authHeader);
    console.log('🔍 TEST: Authorization header value:', authHeader ? authHeader.substring(0, 20) + '...' : 'None');
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfits/?limit=20&offset=0`;
    console.log('🔍 TEST: Calling backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 TEST: Backend response status:', response.status);
    console.log('🔍 TEST: Backend response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 TEST: Backend error response:', errorText);
      return NextResponse.json({ 
        error: 'Backend request failed', 
        details: `Status: ${response.status} ${response.statusText}`,
        backendError: errorText
      }, { status: response.status });
    }
    
    const outfitsData = await response.json();
    console.log('🔍 TEST: Backend outfits data received:', {
      isArray: Array.isArray(outfitsData),
      length: Array.isArray(outfitsData) ? outfitsData.length : 'N/A',
      keys: Array.isArray(outfitsData) ? 'N/A' : Object.keys(outfitsData),
      firstItem: Array.isArray(outfitsData) && outfitsData.length > 0 ? outfitsData[0] : 'N/A'
    });
    
    return NextResponse.json({
      success: true,
      backendResponse: outfitsData,
      isArray: Array.isArray(outfitsData),
      length: Array.isArray(outfitsData) ? outfitsData.length : 'N/A',
      message: 'Test completed successfully'
    });
    
  } catch (err) {
    console.error('❌ TEST: /api/outfits/test failed:', err);
    return NextResponse.json({ 
      error: 'Test failed', 
      details: err instanceof Error ? err.message : 'Unknown error'
    }, { status: 500 });
  }
}
