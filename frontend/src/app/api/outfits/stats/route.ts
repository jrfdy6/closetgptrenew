import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog, serverDebugWarn } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';
// Fix 405 errors - connect outfits page to working stats

export async function GET(req: NextRequest) {
  serverDebugLog('🔍 [API] /api/outfits/stats GET route called');

  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  try {
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const days = searchParams.get('days') || '7';

    const baseUrl = getBackendUrl();
    
    serverDebugLog('🔍 [API] Proxying to backend URL:', `${baseUrl}/api/outfit-stats/stats`);
    
    const controller = new AbortController();
    timeoutId = setTimeout(() => controller.abort(), 15000);

    const res = await fetch(`${baseUrl}/api/outfit-stats/stats?days=${encodeURIComponent(days)}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      serverDebugWarn('❌ [API] Backend responded with:', res.status, res.statusText);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      serverDebugWarn('❌ [API] Backend error details:', errorText);
      
      // Special handling for auth errors
      if (res.status === 403 || res.status === 401) {
        serverDebugWarn('🔐 AUTH ERROR: Token may be invalid or expired');
        serverDebugWarn('🔐 AUTH DEBUG: Auth header sent:', authHeader ? 'Yes' : 'No');
      }
      
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText,
        authHeaderSent: !!authHeader
      }, { status: res.status });
    }

    const data = await res.json();
    serverDebugLog('✅ [API] Successfully fetched stats from backend');
    return NextResponse.json(data);
  } catch (error: any) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { success: false, error: 'Backend request timeout' },
        { status: 504 }
      );
    }
    console.error('❌ [API] /api/outfits/stats proxy failed:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Proxy failed', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
}
