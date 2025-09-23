import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 DEBUG: Worn outfits analytics API route called');
    console.log('🔍 DEBUG: All headers:', Object.fromEntries(request.headers.entries()));
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header:', authHeader);
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Extract token from "Bearer <token>" format
    const token = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : authHeader;
    console.log('🔍 DEBUG: Extracted token:', token.substring(0, 20) + '...');
    
    // Get backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL || 
                      'https://closetgptrenew-backend-production.up.railway.app';
    
    // Call the backend endpoint for worn outfits this week
    const fullBackendUrl = `${backendUrl}/api/outfits/analytics/worn-this-week`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      const errorText = await response.text().catch(() => 'Unable to read error');
      console.error('🔍 DEBUG: Backend error details:', errorText);
      
      // Return fallback data if backend is not available
      return NextResponse.json({
        success: true,
        outfits_worn_this_week: 0,
        message: `Backend temporarily unavailable (${response.status}), using fallback data`
      });
    }
    
    const data = await response.json();
    console.log('🔍 DEBUG: Backend data received:', data);
    
    // Add cache-busting headers to prevent browser/CDN caching
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Last-Modified': new Date().toUTCString(),
        'ETag': `"${Date.now()}"`
      }
    });
    
  } catch (error: any) {
    console.error('🔍 DEBUG: Error in worn outfits analytics route:', error);
    
    // Return fallback data on error with cache-busting headers
    return NextResponse.json({
      success: true,
      outfits_worn_this_week: 0,
      message: 'Error fetching data, using fallback'
    }, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Last-Modified': new Date().toUTCString(),
        'ETag': `"${Date.now()}"`
      }
    });
  }
}