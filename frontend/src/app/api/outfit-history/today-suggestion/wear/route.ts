import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  console.log("👕 Mark today's suggestion as worn API route called");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/today-suggestion/wear`;
    console.log("🔗 Proxying to backend URL:", backendUrl);
    
    const authHeader = req.headers.get('authorization');
    console.log("🔍 Authorization header:", authHeader ? 'Present' : 'Missing');
    
    const body = await req.json();
    console.log("📦 Request body:", body);
    
    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && {
          Authorization: authHeader,
        }),
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      console.error(`❌ Backend error: ${res.status} ${res.statusText}`);
      const errorText = await res.text().catch(() => 'Unable to read error');
      console.error('❌ Backend error details:', errorText);
      
      return NextResponse.json({ 
        success: false,
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ Successfully marked today's suggestion as worn");
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in today suggestion wear route:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to mark suggestion as worn' 
      },
      { status: 500 }
    );
  }
}
