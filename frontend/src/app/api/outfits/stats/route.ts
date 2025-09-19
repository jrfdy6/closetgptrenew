import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  console.log("🔍 [API] /api/outfits/stats GET route called");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfit-history/stats`;
    const authHeader = req.headers.get('authorization');
    console.log("🔍 [API] Proxying to backend URL:", backendUrl);
    console.log("🔍 [API] Authorization header:", authHeader ? `Present (${authHeader.substring(0, 20)}...)` : 'Missing');
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
    });

    if (!res.ok) {
      console.error('❌ [API] Backend responded with:', res.status, res.statusText);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      console.error('❌ [API] Backend error details:', errorText);
      
      // Special handling for auth errors
      if (res.status === 403 || res.status === 401) {
        console.error('🔐 AUTH ERROR: Token may be invalid or expired');
        console.error('🔐 AUTH DEBUG: Auth header sent:', authHeader ? 'Yes' : 'No');
      }
      
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText,
        authHeaderSent: !!authHeader
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ [API] Successfully fetched stats from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ [API] /api/outfits/stats proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
