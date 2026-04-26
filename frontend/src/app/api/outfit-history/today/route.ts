import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  serverDebugLog("🌅 Today's outfit API route called");
  
  try {
    // Use the new suggestion endpoint instead of the old today endpoint
    const backendUrl = `${getBackendUrl()}/api/today-suggestion`;
    serverDebugLog("🔗 Proxying to backend suggestion URL:", backendUrl);
    
    const authHeader = req.headers.get('authorization');
    serverDebugLog("🔍 Authorization header:", authHeader ? 'Present' : 'Missing');
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && {
          Authorization: authHeader,
        }),
      },
    });

    if (!res.ok) {
      console.error(`❌ Backend error: ${res.status} ${res.statusText}`);
      const errorText = await res.text().catch(() => 'Unable to read error');
      console.error('❌ Backend error details:', errorText);
      
      // Return graceful fallback for today's outfit instead of propagating error
      return NextResponse.json({ 
        success: true,
        todaysOutfit: null,
        hasOutfitToday: false,
        message: `Backend temporarily unavailable (${res.status})`
      }, { status: 200 });
    }

    const data = await res.json();
    serverDebugLog("✅ Successfully fetched today's outfit from backend");
    serverDebugLog("🔍 DEBUG: Backend response data:", JSON.stringify(data, null, 2));
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in today outfit API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch today\'s outfit' },
      { status: 500 }
    );
  }
}
