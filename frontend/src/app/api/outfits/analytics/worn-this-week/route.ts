// Force Vercel redeploy - analytics endpoint fix - Oct 22 2025
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 DEBUG: Worn outfits analytics API route called');
    console.log('🔍 DEBUG: Request URL:', request.url);
    console.log('🔍 DEBUG: Request method:', request.method);
    console.log('🔍 DEBUG: All headers:', Object.fromEntries(request.headers.entries()));
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization') ||
                      request.headers.get('AUTHORIZATION');
    console.log('🔍 DEBUG: Authorization header received:', authHeader ? authHeader.substring(0, 20) + '...' : 'null');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.log('🔍 DEBUG: No valid auth header - returning 401');
      return NextResponse.json(
        { error: 'Authorization header required', debug: 'API route called but no auth header provided' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL || 
                      'https://closetgptrenew-production.up.railway.app';
    
    // Call the backend endpoint for worn outfits this week
    const fullBackendUrl = `${backendUrl}/api/simple-analytics/outfits-worn-this-week`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    console.log('🔍 DEBUG: Using auth header from request');
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
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
    
    // Normalize field names - backend returns worn_this_week, frontend expects outfits_worn_this_week
    const normalizedData = {
      success: data.success,
      outfits_worn_this_week: data.worn_this_week || data.outfits_worn_this_week || 0,
      user_id: data.user_id,
      week_start: data.week_start,
      calculated_at: data.calculated_at,
      source: 'simple_analytics',
      version: '2025-10-21',
      api_version: 'v2.0'
    };
    
    console.log('🔍 DEBUG: Normalized data:', normalizedData);
    
    // Add cache-busting headers to prevent browser/CDN caching
    return NextResponse.json(normalizedData, {
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
