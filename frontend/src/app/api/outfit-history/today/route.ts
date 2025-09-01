import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  console.log("🌅 Today's outfit API route called");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfit-history/today`;
    console.log("🔗 Proxying to backend URL:", backendUrl);
    
    const authHeader = req.headers.get('authorization');
    console.log("🔍 Authorization header:", authHeader ? 'Present' : 'Missing');
    
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
      
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ Successfully fetched today's outfit from backend");
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in today outfit API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch today\'s outfit' },
      { status: 500 }
    );
  }
}
