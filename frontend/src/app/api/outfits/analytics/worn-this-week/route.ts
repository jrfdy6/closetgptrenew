// Force Vercel redeploy - analytics endpoint fix - Oct 22 2025
import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog, serverDebugWarn } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    serverDebugLog('🔍 DEBUG: Worn outfits analytics API route called');
    serverDebugLog('🔍 DEBUG: Request URL:', request.url);
    serverDebugLog('🔍 DEBUG: Request method:', request.method);
    
    // Get the authorization header - check standard location and Vercel special headers
    let authHeader = request.headers.get('authorization') || 
                     request.headers.get('Authorization') ||
                     request.headers.get('AUTHORIZATION');
    
    // Check Vercel's x-vercel-sc-headers if standard header is missing
    if (!authHeader) {
      const vercelScHeaders = request.headers.get('x-vercel-sc-headers');
      if (vercelScHeaders) {
        try {
          const parsedHeaders = JSON.parse(vercelScHeaders);
          authHeader = parsedHeaders.Authorization || parsedHeaders.authorization;
          serverDebugLog('🔍 DEBUG: Found auth in x-vercel-sc-headers');
        } catch (e) {
          serverDebugWarn('⚠️ DEBUG: Failed to parse x-vercel-sc-headers');
        }
      }
    }
    
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      serverDebugLog('🔍 DEBUG: No valid auth header - returning 401');
      return NextResponse.json(
        { error: 'Authorization header required', debug: 'API route called but no auth header provided' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = getBackendUrl();
    
    // Call the backend endpoint for worn outfits this week
    const fullBackendUrl = `${backendUrl}/api/simple-analytics/outfits-worn-this-week`;
    serverDebugLog('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    serverDebugLog('🔍 DEBUG: Using auth header from request');
    
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
    
    serverDebugLog('🔍 DEBUG: Backend response status:', response.status);
    
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
    serverDebugLog('🔍 DEBUG: Backend data received:', data);
    
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
    
    serverDebugLog('🔍 DEBUG: Normalized data:', normalizedData);
    
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
