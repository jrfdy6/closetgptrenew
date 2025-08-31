import { NextRequest, NextResponse } from 'next/server';

// Debug route to check backend outfit state
export async function GET(req: NextRequest) {
  console.log("🔍 DEBUG: /api/outfits/debug route called");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/debug`;
    console.log("🔍 DEBUG: Fetching from backend URL:", backendUrl);
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      console.error('❌ DEBUG: Backend responded with:', res.status, res.statusText);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      console.error('❌ DEBUG: Backend error details:', errorText);
      
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("🔍 DEBUG: Successfully fetched debug data from backend");
    console.log("🔍 DEBUG: Found", data.total_outfits, "outfits");
    
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ DEBUG: /api/outfits/debug proxy failed:', err);
    return NextResponse.json({ 
      error: 'Debug proxy failed', 
      details: err instanceof Error ? err.message : 'Unknown error'
    }, { status: 500 });
  }
}
